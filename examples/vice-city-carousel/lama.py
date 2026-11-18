#!/usr/bin/env python3
"""LaMa (ONNX) inpainting for large masks. Crops a square around the mask,
runs at 512x512, scales back and composites only masked pixels (feathered)."""
import numpy as np, cv2, onnxruntime as ort
_S = None

def lama(img_bgr, mask, pad=40):
    global _S
    if _S is None:
        _S = ort.InferenceSession("models/lama_fp32.onnx", providers=["CPUExecutionProvider"])
    H, W = mask.shape
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min() - pad, ys.max() + pad, xs.min() - pad, xs.max() + pad
    side = max(y1 - y0, x1 - x0)
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    side = min(side, H, W)
    y0 = int(np.clip(cy - side // 2, 0, H - side)); x0 = int(np.clip(cx - side // 2, 0, W - side))
    crop = img_bgr[y0:y0 + side, x0:x0 + side]; mc = mask[y0:y0 + side, x0:x0 + side].astype(np.uint8)
    rgb = cv2.cvtColor(cv2.resize(crop, (512, 512), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
    mm = (cv2.resize(mc, (512, 512), interpolation=cv2.INTER_NEAREST) > 0).astype(np.float32)
    out = _S.run(None, {"image": (rgb.transpose(2, 0, 1)[None] / 255.0).astype(np.float32),
                        "mask": mm[None, None]})[0][0].transpose(1, 2, 0)
    if out.max() <= 1.5: out = out * 255
    out = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    out = cv2.resize(out, (side, side), interpolation=cv2.INTER_CUBIC)
    a = cv2.GaussianBlur(mc.astype(np.float32), (0, 0), 2)[..., None]
    a = np.clip(a * 1.5, 0, 1)
    res = img_bgr.copy()
    res[y0:y0 + side, x0:x0 + side] = (crop * (1 - a) + out * a).astype(np.uint8)
    return res
