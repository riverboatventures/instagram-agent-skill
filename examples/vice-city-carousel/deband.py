#!/usr/bin/env python3
"""Remove Nano Banana's semi-transparent dark band (x=49..383).
The band is a tone change, not a single multiplier, so per channel we learn a
curve true = h(darkened) from pixel pairs straddling both band edges on smooth
rows (cubic, forced monotone), apply it as a LUT inside the band, then inpaint
the 5px seams."""
import sys, numpy as np, cv2
src, dst = sys.argv[1:3]
im = cv2.imread(src).astype(np.float32)
H, W = im.shape[:2]
L0, R0 = 49, 383
lum = im.mean(2)
g = np.abs(np.diff(lum, axis=1))
xs_, ys_ = [], []
for xo, xi, a, b in ((range(L0 - 6, L0 - 2), range(L0 + 2, L0 + 6), L0 - 7, L0 + 7),
                     (range(R0 + 3, R0 + 7), range(R0 - 5, R0 - 1), R0 - 6, R0 + 8)):
    smooth = np.concatenate([g[:, a:min(a, b) + 5], g[:, b - 5:b]], 1).max(1) < 5
    for dx in range(4):
        xs_.append(im[smooth, list(xo)[dx]]); ys_.append(im[smooth, list(xi)[dx]])
X, Y = np.concatenate(xs_), np.concatenate(ys_)     # X true (outside), Y darkened (inside)
fix = im.copy()
band = im[:, L0:R0 + 1]
for c in range(3):
    x, y = X[:, c], Y[:, c]
    keep = np.ones(len(x), bool)
    for _ in range(6):                       # trimmed least squares (drop worst 20%)
        k, b0 = np.polyfit(y[keep], x[keep], 1)
        res = np.abs(x - (k * y + b0)); keep = res < np.percentile(res[keep], 80)
    if not (1.3 < k < 2.6):                   # implausible (busy edges) -> pure gain
        k, b0 = np.median(x[keep] / np.maximum(y[keep], 1)), 0.0
    fix[:, L0:R0 + 1, c] = band[..., c] * k + b0
    print(f"ch{c}: true = {k:.3f}*dark + {b0:+.1f}")
# seam-matching pass: per-row residual step at each edge, robustly smoothed in y,
# blended linearly across the band so both edges join with no visible step
from scipy.ndimage import median_filter, gaussian_filter1d
for _ in range(2):
    dL = fix[:, L0 - 6:L0 - 2].mean(1) - fix[:, L0 + 2:L0 + 6].mean(1)
    dR = fix[:, R0 + 3:R0 + 7].mean(1) - fix[:, R0 - 5:R0 - 1].mean(1)
    def clean(d):
        bad = np.abs(d).max(1) > 18            # an object crosses the edge here, not a band step
        if bad.all(): return np.zeros_like(d)
        idx = np.arange(len(d))
        for c in range(3):
            d[bad, c] = np.interp(idx[bad], idx[~bad], d[~bad, c])
        return gaussian_filter1d(median_filter(d, size=(61, 1)), 12, axis=0)
    dL, dR = clean(dL), clean(dR)
    t = np.linspace(0, 1, R0 - L0 + 1)[None, :, None]
    fix[:, L0:R0 + 1] += dL[:, None, :] * (1 - t) + dR[:, None, :] * t
fix = np.clip(fix, 0, 255).astype(np.uint8)
m = np.zeros((H, W), np.uint8); m[:, L0 - 2:L0 + 3] = 255; m[:, R0 - 2:R0 + 3] = 255
fix = cv2.inpaint(fix, m, 3, cv2.INPAINT_TELEA)
cv2.imwrite(dst, fix, [cv2.IMWRITE_PNG_COMPRESSION, 3])
