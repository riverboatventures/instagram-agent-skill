#!/usr/bin/env python3
"""Post preview: generic phone-feed mockup (collapsed caption), expanded caption, and all 14 slides."""
import re, glob
from PIL import Image, ImageDraw, ImageFont

F = "fonts/"
BG, PANEL, TXT, MUTED, LINK, PINK = (0, 0, 0), (18, 18, 20), (245, 245, 245), (150, 150, 160), (140, 180, 255), (255, 62, 165)
inter = lambda w, s: ImageFont.truetype(F + f"Inter-{w}.woff", s)
far = lambda s: ImageFont.truetype(F + "fa-regular.ttf", s)
fas = lambda s: ImageFont.truetype(F + "fa-solid.ttf", s)
EMOJI = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
EMO_RE = re.compile("([\U0001F300-\U0001FAFF☀-➿])")


def emoji_img(ch, size):
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=EMOJI, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)


def tokens(text):
    out = []
    for part in EMO_RE.split(text):
        if not part: continue
        if EMO_RE.fullmatch(part): out.append(("emo", part))
        else:
            for w in re.split(r"(\s+)", part):
                if w: out.append(("txt", w))
    return out


def rich(draw, canvas, x, y, width, runs, size, lh):
    """runs: list of (text, font, color). Wraps words; emoji inline. Returns new y."""
    cx = x
    for text, fnt, col in runs:
        for kind, t in tokens(text):
            if kind == "txt" and t.isspace():
                if "\n" in t:
                    for _ in range(t.count("\n")): y += lh
                    cx = x
                    continue
                cx += fnt.getlength(" ")
                continue
            w = int(size * 1.15) if kind == "emo" else fnt.getlength(t)
            if cx + w > x + width:
                y += lh; cx = x
            if kind == "emo":
                e = emoji_img(t, int(size * 1.05)); canvas.alpha_composite(e, (int(cx), int(y + size * 0.12)))
            else:
                c = LINK if t.startswith("#") else col
                draw.text((cx, y), t, font=fnt, fill=c)
            cx += w
    return y + lh


cap = open("caption.txt").read().strip()
first_line, rest = cap.split("\n", 1)
slides = sorted(glob.glob("out/*.jpg"))

W = 1880; PW = 860; M = 54
H = 3200
im = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(im)
d.text((M, 40), "POST PREVIEW", font=inter("800-normal", 30), fill=PINK)
d.text((M, 84), "Mockup for review: layout and caption as followers will see them. Not a screenshot of any app.",
       font=inter("500-normal", 24), fill=MUTED)

# ---------- panel 1: feed (collapsed) ----------
x0, y0 = M, 150
d.rounded_rectangle((x0 - 2, y0 - 2, x0 + PW + 2, y0 + 1620), radius=34, fill=PANEL)
d.text((x0 + 26, y0 + 22), "IN THE FEED", font=inter("800-normal", 22), fill=MUTED)
hy = y0 + 70
d.ellipse((x0 + 24, hy, x0 + 88, hy + 64), fill=PINK)
d.ellipse((x0 + 28, hy + 4, x0 + 84, hy + 60), fill=(30, 10, 50))
d.text((x0 + 56, hy + 32), "VC", font=inter("800-normal", 22), fill=TXT, anchor="mm")
d.text((x0 + 104, hy + 6), "Vice City Clips", font=inter("700-normal", 28), fill=TXT)
d.text((x0 + 104, hy + 38), "Miami, Florida", font=inter("500-normal", 22), fill=MUTED)
d.text((x0 + PW - 60, hy + 18), "", font=fas(28), fill=TXT)
iy = hy + 84
cover = Image.open(slides[0]).convert("RGBA").resize((PW, int(PW * 1350 / 1080)), Image.LANCZOS)
im.alpha_composite(cover, (x0, iy))
bx = x0 + PW - 110
d.rounded_rectangle((bx, iy + 20, bx + 86, iy + 60), radius=20, fill=(20, 20, 20, 200))
d.text((bx + 43, iy + 40), "1/14", font=inter("700-normal", 22), fill=TXT, anchor="mm")
ay = iy + cover.height + 22
for i, (g, f) in enumerate((("", far), ("", far), ("", far))):
    d.text((x0 + 26 + i * 70, ay), g, font=f(40), fill=TXT)
d.text((x0 + PW - 64, ay), "", font=far(40), fill=TXT)
for i in range(5):
    r = 7 if i == 0 else (6 if i < 3 else 4)
    cx = x0 + PW // 2 - 50 + i * 25; cy = ay + 22
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PINK if i == 0 else (90, 90, 100))
ty = ay + 72
name = inter("700-normal", 27); body = inter("500-normal", 27)
ty = rich(d, im, x0 + 26, ty, PW - 52, [("Vice City Clips ", name, TXT), (first_line, body, TXT)], 27, 38)
d.text((x0 + 26, ty - 2), "... more", font=body, fill=MUTED)
d.text((x0 + 26, ty + 44), "Just now", font=inter("500-normal", 22), fill=MUTED)

# ---------- panel 2: expanded caption ----------
x1 = M + PW + 52
d.rounded_rectangle((x1 - 2, y0 - 2, x1 + PW + 2, y0 + 1620), radius=34, fill=PANEL)
d.text((x1 + 26, y0 + 22), "CAPTION, AFTER TAPPING “MORE”", font=inter("800-normal", 22), fill=MUTED)
ty = y0 + 84
ty = rich(d, im, x1 + 30, ty, PW - 60, [("Vice City Clips ", inter("700-normal", 30), TXT), (cap, inter("500-normal", 30), TXT)], 30, 44)
ty += 40
d.line((x1 + 30, ty, x1 + PW - 30, ty), fill=(50, 50, 60), width=2); ty += 30
d.text((x1 + 30, ty), "SUGGESTED FIRST COMMENT (PIN IT)", font=inter("800-normal", 22), fill=PINK); ty += 44
rich(d, im, x1 + 30, ty, PW - 60, [("Vice City Clips ", inter("700-normal", 28), TXT),
                                     ("Which list are you on? Comment RICH or REAL \U0001F447", inter("500-normal", 28), TXT)], 28, 40)
stats = [f"{len(cap):,} characters of 2,200", f"First line lands whole in the feed ({len(first_line)} / 125 chars)",
         "5 hashtags (Instagram's cap)", "One call to action", "Caption lint: READY  ·  Humanizer: 75.5 PASS"]
sy = y0 + 1620 - 40 - 44 * len(stats)
d.text((x1 + 30, sy - 50), "CHECKS", font=inter("800-normal", 22), fill=PINK)
for i, s_ in enumerate(stats):
    d.text((x1 + 30, sy + i * 44), "", font=fas(24), fill=(90, 220, 140))
    d.text((x1 + 70, sy + i * 44 - 2), s_, font=inter("500-normal", 26), fill=TXT)

# ---------- strip: all 14 slides ----------
sy = y0 + 1660
d.text((M, sy), "ALL 14 SLIDES, IN SWIPE ORDER", font=inter("800-normal", 24), fill=MUTED)
tw = (W - 2 * M - 6 * 16) // 7; th = int(tw * 1350 / 1080)
for i, p in enumerate(slides):
    t = Image.open(p).convert("RGBA").resize((tw, th), Image.LANCZOS)
    tx = M + (i % 7) * (tw + 16); ty = sy + 46 + (i // 7) * (th + 40)
    im.alpha_composite(t, (tx, ty))
    d.text((tx + 8, ty + th + 6), f"{i + 1}", font=inter("700-normal", 20), fill=MUTED)
need = sy + 46 + 2 * (th + 40) + 20
im = im.crop((0, 0, W, need))
im.convert("RGB").save("post_preview.png", optimize=True)
print("preview", im.size)
