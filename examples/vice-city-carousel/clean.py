#!/usr/bin/env python3
"""Remove baked-in text from the two source images (after deband.py).
ranked: big white headline + neon 'Vice city' script + garbled store sign;
        the diagonal neon divider is redrawn afterwards.
cover:  big white headline + garbled neon signs (Oan Drive / VICY / GCEU)."""
import numpy as np, cv2
from lama import lama
from scipy.ndimage import binary_dilation

def hsv(im): return cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(int)

def box(shape, x0, y0, x1, y1):
    m = np.zeros(shape[:2], bool); m[y0:y1, x0:x1] = True; return m

def white_text_mask(im, region, grow=9):
    h = hsv(im)
    white = (h[..., 1] < 45) & (h[..., 2] > 215) & region
    near = binary_dilation(white, iterations=grow)
    dark = (h[..., 2] < 110) & near & region                 # black outline / drop shadow
    return binary_dilation(white | dark, iterations=3)

def neon_mask(im, region, grow=7):
    h = hsv(im)
    pink = (h[..., 0] > 135) & (h[..., 0] < 175) & (h[..., 1] > 80) & (h[..., 2] > 150)
    core = (h[..., 1] < 60) & (h[..., 2] > 235)
    return binary_dilation((pink | core) & region, iterations=grow) & region

def inpaint(im, m, r=7):
    return cv2.inpaint(im, m.astype(np.uint8) * 255, r, cv2.INPAINT_TELEA)

def neon_line(im, p0, p1, color=(235, 60, 255)):
    """Glowing neon stroke (BGR color) drawn additively with a white core."""
    H, W = im.shape[:2]
    acc = np.zeros((H, W, 3), np.float32)
    for width, blur, gain in ((3, 0, 1.0), (7, 6, 0.9), (16, 18, 0.6), (30, 40, 0.35)):
        layer = np.zeros((H, W), np.float32)
        cv2.line(layer, p0, p1, 1.0, width, cv2.LINE_AA)
        if blur: layer = cv2.GaussianBlur(layer, (0, 0), blur)
        acc += layer[..., None] * np.array(color, np.float32)[None, None] * gain
    core = np.zeros((H, W), np.float32); cv2.line(core, p0, p1, 1.0, 2, cv2.LINE_AA)
    out = im.astype(np.float32) + acc
    out = out * (1 - core[..., None]) + 255 * core[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------- ranked (rich/poor split) ----------
im = cv2.imread("work/2_ranked.png")
H, W = im.shape[:2]
pts = [(50, 560), (150, 537), (250, 512), (350, 484), (450, 458), (1100, 290), (1200, 274), (1300, 242)]
a, b = np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)       # x = a*y + b
X = lambda y: int(round(a * y + b))
m = box(im.shape, 40, 560, 735, 790)                      # headline block
m |= box(im.shape, 185, 728, 655, 965)                     # neon script incl. tail + outline
# the divider passes through the text area: mask its segment there, redraw later
seg = np.zeros((H, W), np.uint8); cv2.line(seg, (X(540), 540), (X(940), 940), 255, 26)
m |= seg > 0
# garbled store sign: letters on the cream board
h = hsv(im); signr = box(im.shape, 655, 935, 768, 1030)
cream = (h[..., 1] < 85) & (h[..., 2] > 170)
m |= binary_dilation(signr & ~cream, iterations=2) & box(im.shape, 660, 940, 768, 1026)
cv2.imwrite("work/2_ranked_mask.png", m.astype(np.uint8) * 255)
im = lama(im, m)
im = neon_line(im, (X(520), 520), (X(960), 960))
cv2.imwrite("work/2_ranked_clean.png", im)
print("ranked: divider x = %.4f*y + %.1f" % (a, b))

# ---------- cover (Ocean Drive) ----------
im = cv2.imread("work/1_cover.png")
m = box(im.shape, 85, 560, 690, 772)                      # headline block
m |= neon_mask(im, box(im.shape, 690, 650, 735, 760), grow=5)           # VICY (vertical)
h = hsv(im)
teal = (h[..., 0] > 75) & (h[..., 0] < 105) & (h[..., 1] > 60) & (h[..., 2] > 180)
oan = box(im.shape, 420, 825, 530, 868)
m |= binary_dilation(((teal | ((h[..., 1] < 50) & (h[..., 2] > 230))) & oan), iterations=3) & oan
gceu = box(im.shape, 250, 765, 278, 880)
m |= binary_dilation(((h[..., 1] > 70) & (h[..., 2] > 170) | ((h[..., 1] < 50) & (h[..., 2] > 230))) & gceu, iterations=3) & gceu
cv2.imwrite("work/1_cover_mask.png", m.astype(np.uint8) * 255)
im = lama(im, m)
cv2.imwrite("work/1_cover_clean.png", im)
print("cover cleaned")
