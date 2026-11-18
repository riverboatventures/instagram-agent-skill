# Vice City cost-of-living carousel (example)

The 14-slide "Top 5 richest vs top 5 poorest in Vice City" carousel, built
with `place-stats` (Census + Zillow numbers) and these render scripts.

- `out/`: the finished 1080x1350 slides, in posting order.
- `caption.txt`: the caption (caption lint READY, humanizer PASS).
- `work/`: cleaned backgrounds (dark band removed, old text inpainted).
  Stored as JPG; the scripts read `work/*.png`, so convert back before re-rendering.
- `render.py` (cover, ranked, slides 3-5), `render2.py` (6, 11-14),
  `render3.py` (7-10), `render4.py` (15, follow slide: needs its background),
  `reel.py` (9:16 Reel from `out/`), `preview.py` (post mockup).
- `deband.py`, `clean.py`, `lama.py`: background repair tools (LaMa model is
  downloaded from Hugging Face `Carve/LaMa-ONNX`, not stored here).
- Fonts: Anton, Inter, Kaushan Script (SIL OFL) and Font Awesome Free (OFL/CC BY).
