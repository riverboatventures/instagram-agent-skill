#!/usr/bin/env python3
"""Lay out the Vice City carousel slides (1080x1350, 4:5) over the cleaned art."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np

W, H = 1080, 1350
F = "fonts/"
PINK = (255, 62, 165)
DEEP = (24, 8, 44)
WHITE = (255, 255, 255)

def font(name, size): return ImageFont.truetype(F + name, size)
ANTON = lambda s: font("Anton.woff", s)
INTER = lambda w, s: font(f"Inter-{w}.woff", s)
SCRIPT = lambda s: font("Kaushan.woff", s)
ICON = lambda s: font("fa-solid.ttf", s)
IC = dict(money="", house="", key="", pct="", wallet="", pin="", palm="")


def base(path, y0, scale_from=768):
    im = Image.open(path).convert("RGB")
    s = W / scale_from
    crop = im.crop((0, y0, scale_from, y0 + int(round(H / s))))
    out = crop.resize((W, H), Image.LANCZOS)
    return out.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2)).convert("RGBA")


def gradient(size, stops, axis):
    """stops: list of (pos 0..1, alpha 0..255); axis 'x' or 'y'."""
    w, h = size; n = w if axis == "x" else h
    t = np.linspace(0, 1, n)
    a = np.interp(t, [p for p, _ in stops], [v for _, v in stops])
    a = np.tile(a[None, :], (h, 1)) if axis == "x" else np.tile(a[:, None], (1, w))
    layer = np.zeros((h, w, 4), np.uint8); layer[..., :3] = DEEP; layer[..., 3] = a.astype(np.uint8)
    return Image.fromarray(layer, "RGBA")


def text_layer(txt, fnt, fill=WHITE, stroke=0, stroke_fill=(0, 0, 0), spacing=0):
    if spacing:
        widths = [fnt.getlength(c) for c in txt]
        w = int(sum(widths) + spacing * (len(txt) - 1)) + 2 * stroke + 4
    else:
        w = int(fnt.getlength(txt)) + 2 * stroke + 4
    asc, desc = fnt.getmetrics()
    h = asc + desc + 2 * stroke + 4
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if spacing:
        x = stroke + 2
        for c, cw in zip(txt, widths):
            d.text((x, stroke + 2), c, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += cw + spacing
    else:
        d.text((stroke + 2, stroke + 2), txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return lay


def paste_shadow(canvas, lay, xy, blur=10, offset=(0, 6), opacity=0.8):
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").point(lambda v: int(v * opacity)))
    pad = blur * 3
    big = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad), (0, 0, 0, 0))
    big.paste(sh, (pad, pad)); big = big.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(big, (xy[0] - pad + offset[0], xy[1] - pad + offset[1]))
    canvas.alpha_composite(lay, xy)


def neon(canvas, txt, fnt, center, color=PINK, glow=(6, 16, 36)):
    lay = text_layer(txt, fnt, fill=WHITE)
    x = int(center[0] - lay.width / 2); y = int(center[1] - lay.height / 2)
    pad = max(glow) * 3
    a = Image.new("L", (lay.width + 2 * pad, lay.height + 2 * pad), 0); a.paste(lay.getchannel("A"), (pad, pad))
    acc = np.zeros((a.height, a.width, 3), np.float32)
    for r, g in zip(glow, (1.0, 0.8, 0.55)):
        b = np.asarray(a.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255
        acc += b[..., None] * np.array(color, np.float32) * g * 1.6
    region = canvas.crop((x - pad, y - pad, x - pad + a.width, y - pad + a.height)).convert("RGB")
    lit = np.clip(np.asarray(region, np.float32) + acc, 0, 255).astype(np.uint8)
    canvas.paste(Image.fromarray(lit).convert("RGBA"), (x - pad, y - pad))
    # coloured tube with a hot white core
    tube = text_layer(txt, fnt, fill=color + (255,), stroke=3, stroke_fill=color)
    canvas.alpha_composite(tube, (x - 3, y - 3))
    core = text_layer(txt, fnt, fill=(255, 235, 250, 255))
    canvas.alpha_composite(core, (x, y))


def fit_font(txt, maker, max_w, start):
    s = start
    while maker(s).getlength(txt) > max_w and s > 20: s -= 2
    return maker(s)


def wrap(txt, fnt, max_w):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= max_w: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines


def pill(canvas, txt, xy, fnt, fill=PINK, color=WHITE, padx=26, pady=12, spacing=3, anchor="l"):
    lay = text_layer(txt, fnt, fill=color, spacing=spacing)
    w, h = lay.width + 2 * padx, lay.height + 2 * pady - 8
    x = xy[0] - (w // 2 if anchor == "c" else 0); y = xy[1]
    p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=fill)
    paste_shadow(canvas, p, (x, y), blur=8, offset=(0, 4), opacity=0.5)
    canvas.alpha_composite(lay, (x + padx, y + pady - 6))
    return w, h


def brand(canvas):
    lay = text_layer("VICE CITY CLIPS", INTER("800-normal", 22), fill=(255, 255, 255, 215), spacing=4)
    paste_shadow(canvas, lay, (W - lay.width - 56, 60), blur=6, offset=(0, 2), opacity=0.7)


def swipe(canvas, xy=None):
    t = text_layer("SWIPE", INTER("800-normal", 26), fill=PINK + (255,), spacing=3)
    a = text_layer("", ICON(24), fill=PINK + (255,))
    lay = Image.new("RGBA", (t.width + a.width + 10, max(t.height, a.height)), (0, 0, 0, 0))
    lay.alpha_composite(t, (0, 0)); lay.alpha_composite(a, (t.width + 10, (t.height - a.height) // 2 + 2))
    xy = xy or (W - lay.width - 56, H - 74)
    paste_shadow(canvas, lay, xy, blur=6, offset=(0, 2), opacity=0.8)


# --------------------------------------------------------------------------
def info_slide(src, y0, tag, title, best_for, stats, wallet, spawn, out):
    c = base(src, y0)
    c.alpha_composite(gradient((W, H), [(0, 215), (0.42, 150), (0.72, 0), (1, 0)], "x"))
    c.alpha_composite(gradient((W, H), [(0, 120), (0.12, 0), (0.78, 0), (1, 200)], "y"))
    brand(c)
    pill(c, tag, (60, 52), INTER("800-normal", 24))

    hf = fit_font(title, ANTON, 960, 150)
    lay = text_layer(title, hf, stroke=4, stroke_fill=(10, 0, 20))
    n_bf = len(wrap("Best for: " + best_for, INTER("600-italic", 38), 760))
    y = 330 - max(0, n_bf - 2) * 70          # long "best for" -> start higher, keep box clear of footer
    paste_shadow(c, lay, (54, y), blur=14, offset=(0, 10), opacity=0.85)
    y += lay.height + 6

    bf = INTER("600-italic", 38)
    lines = wrap("Best for: " + best_for, bf, 760)
    for ln in lines:
        l = text_layer(ln, bf); paste_shadow(c, l, (62, y), blur=8, offset=(0, 3), opacity=0.9); y += 50
    y += 34

    # stat rows with pink rule
    top = y
    lf, vf, icf = INTER("500-normal", 29), ANTON(50), ICON(44)
    for icon, label, value in stats:
        il = text_layer(IC[icon], icf); paste_shadow(c, il, (100, y + 18), blur=6, offset=(0, 2), opacity=0.7)
        l = text_layer(label, lf, fill=(255, 255, 255, 230)); paste_shadow(c, l, (172, y), blur=6, offset=(0, 2), opacity=0.9)
        v = text_layer(value, vf); paste_shadow(c, v, (170, y + 34), blur=8, offset=(0, 3), opacity=0.9)
        y += 118
    bar = Image.new("RGBA", (7, y - top - 22), PINK + (255,))
    c.alpha_composite(bar, (66, top + 6))
    y += 8

    # pink box
    bx, by, bw, bh = 60, y, 840, 186
    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
    d.rounded_rectangle((2, 2, bw - 3, bh - 3), radius=38, fill=DEEP + (170,), outline=PINK + (255,), width=5)
    paste_shadow(c, box, (bx, by), blur=12, offset=(0, 6), opacity=0.5)
    rows = [("wallet", "Wallet damage:", wallet, PINK), ("pin", "Spawn point:", spawn, WHITE)]
    ry = by + 30
    for icon, label, value, col in rows:
        il = text_layer(IC[icon], ICON(38)); c.alpha_composite(il, (bx + 34, ry + 4))
        l = text_layer(label, INTER("500-normal", 31)); c.alpha_composite(l, (bx + 96, ry + 8))
        vfnt = fit_font(value, ANTON, bw - 120 - int(INTER("500-normal", 31).getlength(label)) - 40, 42)
        v = text_layer(value, vfnt, fill=col + (255,)); c.alpha_composite(v, (bx + 96 + l.width + 12, ry + 2 + (42 - vfnt.size) // 2))
        ry += 70

    src_l = text_layer("Source: U.S. Census Bureau ACS 2020–2024 · Zillow Home Value Index, Oct 2026",
                       INTER("500-normal", 21), fill=(255, 255, 255, 190))
    paste_shadow(c, src_l, (60, H - 70), blur=5, offset=(0, 2), opacity=0.9)
    swipe(c, (W - 170, H - 76))
    c.convert("RGB").save(out, quality=95)


def cover(out):
    c = base("work/1_cover_clean.png", 300)
    c.alpha_composite(gradient((W, H), [(0, 150), (0.16, 40), (0.26, 120), (0.5, 175), (0.66, 60), (0.78, 0), (0.86, 90), (1, 230)], "y"))
    brand(c)
    pill(c, "THE IRL COST OF LIVING IN MIAMI", (W // 2, 120), INTER("800-normal", 28), anchor="c")
    y = 300
    for txt in ("TOP 5 RICHEST",):
        f = fit_font(txt, ANTON, 980, 170); l = text_layer(txt, f, stroke=5, stroke_fill=(10, 0, 20))
        paste_shadow(c, l, ((W - l.width) // 2, y), blur=16, offset=(0, 10), opacity=0.9); y += l.height - 8
    vs = text_layer("vs", SCRIPT(92), fill=PINK + (255,), stroke=3, stroke_fill=(30, 0, 30))
    paste_shadow(c, vs, ((W - vs.width) // 2, y - 6), blur=10, offset=(0, 5), opacity=0.8); y += vs.height - 20
    f = fit_font("TOP 5 POOREST", ANTON, 980, 170); l = text_layer("TOP 5 POOREST", f, stroke=5, stroke_fill=(10, 0, 20))
    paste_shadow(c, l, ((W - l.width) // 2, y), blur=16, offset=(0, 10), opacity=0.9); y += l.height
    neon(c, "Vice City", SCRIPT(200), (W // 2, y + 95))
    bl = text_layer("Same county. Same sunset. 6.7× the income.", INTER("700-normal", 38))
    paste_shadow(c, bl, ((W - bl.width) // 2, H - 168), blur=8, offset=(0, 3), opacity=0.95)
    swipe(c, ((W - 150) // 2, H - 92))
    c.convert("RGB").save(out, quality=95)


def ranked(out):
    y0 = 80
    im = Image.open("work/2_ranked_clean.png").convert("RGB")
    # hand-letter the blank store sign (in source coords, before cropping)
    d = ImageDraw.Draw(im)
    f = ANTON(31); d.text((667, 950), "BODEGA", font=f, fill=(196, 52, 46))
    d.text((668, 994), "CAFECITO", font=INTER("800-normal", 14), fill=(40, 110, 110))
    im.save("work/2_ranked_signed.png")
    c = base("work/2_ranked_signed.png", y0)
    c.alpha_composite(gradient((W, H), [(0, 120), (0.14, 0), (0.85, 0), (1, 150)], "y"))
    brand(c)
    pill(c, "HOW WE RANKED IT", (60, 52), INTER("800-normal", 24))
    # frosted glass card
    cx0, cy0, cx1, cy1 = 70, 440, 1010, 1100
    region = c.crop((cx0, cy0, cx1, cy1)).filter(ImageFilter.GaussianBlur(14))
    mask = Image.new("L", region.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, region.width - 1, region.height - 1), radius=44, fill=255)
    c.paste(region, (cx0, cy0), mask)
    card = Image.new("RGBA", region.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((2, 2, region.width - 3, region.height - 3), radius=44, fill=DEEP + (178,), outline=PINK + (255,), width=5)
    paste_shadow(c, card, (cx0, cy0), blur=18, offset=(0, 10), opacity=0.45)
    x = cx0 + 60; y = cy0 + 50
    t = text_layer("HOW WE RANKED IT", ANTON(104)); c.alpha_composite(t, (x, y)); y += t.height + 10
    c.alpha_composite(Image.new("RGBA", (150, 8), PINK + (255,)), (x + 2, y)); y += 40
    body = INTER("600-normal", 38)
    for para in ["All 68 cities and towns in Miami-Dade, ranked by median household income.",
                 "Half the households earn more, half earn less."]:
        for ln in wrap(para, body, cx1 - cx0 - 120):
            l = text_layer(ln, body); c.alpha_composite(l, (x, y)); y += 52
        y += 22
    y += 6
    fn = INTER("500-normal", 27)
    for ln in wrap("Source: U.S. Census Bureau, ACS 2020–2024. $250,001 is the highest number the Census will publish.", fn, cx1 - cx0 - 120):
        l = text_layer(ln, fn, fill=(255, 255, 255, 200)); c.alpha_composite(l, (x, y)); y += 38
    swipe(c, (60, H - 92))
    c.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    import os; os.makedirs("out", exist_ok=True)
    cover("out/01_cover.jpg")
    ranked("out/02_how_we_ranked.jpg")
    info_slide("work/3_miami_shores.png", 250, "THE RICHEST  ·  #5", "5. MIAMI SHORES",
               "1920s and 30s homes, tree-lined streets, Barry University",
               [("money", "Median household income:", "$144,050/year"),
                ("house", "Typical home value:", "$761,476"),
                ("key", "Median rent:", "$2,657/month")],
               "HIGH", "Miami Shores Country Club", "out/03_miami_shores.jpg")
    info_slide("work/4_key_biscayne.png", 200, "THE RICHEST  ·  #4", "4. KEY BISCAYNE",
               "Island life, beaches, the Cape Florida Lighthouse",
               [("money", "Median household income:", "$181,505/year"),
                ("house", "Typical home value:", "$1,731,887"),
                ("key", "Median rent:", "$3,501+/month (Census max)")],
               "EXTREME", "Rickenbacker Causeway", "out/04_key_biscayne.jpg")
    info_slide("work/5_pinecrest.png", 250, "THE RICHEST  ·  #3", "3. PINECREST",
               "Big lots, banyan-lined streets, quiet estates",
               [("money", "Median household income:", "$206,417/year"),
                ("house", "Typical home value:", "$2,278,941"),
                ("pct", "Poverty rate:", "4.3%")],
               "EXTREME", "Pinecrest Gardens", "out/05_pinecrest.jpg")
    print("done")
