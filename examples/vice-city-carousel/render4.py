#!/usr/bin/env python3
"""Slide 15: follow slide teasing Part 2 (Broward County).
usage: python3 render4.py [background.png] [y0]"""
import sys
from PIL import Image
import render as _r
from render import *          # noqa: F401,F403
IC["userplus"] = ""

_orig_base = _r.base
def base_native(path, y0):
    return _orig_base(path, y0, Image.open(path).width)


def follow_slide(src, y0, out):
    c = base_native(src, y0)
    c.alpha_composite(gradient((W, H), [(0, 225), (0.5, 170), (0.7, 60), (0.85, 0), (1, 0)], "x"))
    c.alpha_composite(gradient((W, H), [(0, 130), (0.14, 0), (0.70, 40), (1, 230)], "y"))
    brand(c)
    pill(c, "UP NEXT  ·  PART 2", (60, 52), INTER("800-normal", 24))
    y = 290
    k = text_layer("RICHEST vs POOREST", INTER("800-normal", 34), fill=PINK + (255,), spacing=4)
    paste_shadow(c, k, (64, y), blur=8, offset=(0, 3), opacity=0.9); y += 58
    for i, ln in enumerate(("BROWARD", "COUNTY")):
        l = text_layer(ln, ANTON(168), stroke=5, stroke_fill=(10, 0, 20))
        paste_shadow(c, l, (54, y), blur=16, offset=(0, 10), opacity=0.9)
        y += 168 if i == 0 else l.height - 22
    y += 28
    sub = INTER("600-italic", 40)
    for ln in wrap("Fort Lauderdale edition. Same Census data, all 36 cities and towns.", sub, 820):
        l = text_layer(ln, sub); paste_shadow(c, l, (62, y), blur=8, offset=(0, 3), opacity=0.95); y += 54
    y += 30
    # teaser card
    tw, th = 860, 150
    card = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((2, 2, tw - 3, th - 3), radius=34, fill=DEEP + (180,), outline=PINK + (255,), width=4)
    paste_shadow(c, card, (60, y), blur=12, offset=(0, 6), opacity=0.5)
    t1 = text_layer("SPOILER", INTER("800-normal", 24), fill=PINK + (255,), spacing=4); c.alpha_composite(t1, (96, y + 24))
    t2 = text_layer("Broward's richest town has only 466 residents.", fit_font("Broward's richest town has only 466 residents.", lambda s: INTER("700-normal", s), tw - 80, 36))
    c.alpha_composite(t2, (96, y + 66)); y += th + 60
    # follow button
    bw, bh = 640, 124
    btn = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(btn).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=bh // 2, fill=PINK + (255,))
    paste_shadow(c, btn, (60, y), blur=18, offset=(0, 10), opacity=0.6)
    ic = text_layer(IC["userplus"], ICON(48)); c.alpha_composite(ic, (108, y + 34))
    ft = text_layer("FOLLOW FOR PART 2", ANTON(64)); c.alpha_composite(ft, (186, y + (bh - ft.height) // 2 + 4))
    foot = text_layer("Data: U.S. Census Bureau ACS 2020–2024 · Fan page, not affiliated with Rockstar Games.",
                      INTER("500-normal", 21), fill=(255, 255, 255, 190))
    paste_shadow(c, foot, (60, H - 70), blur=5, offset=(0, 2), opacity=0.9)
    print("follow button bottom at", y + bh)
    c.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "work/7_fisher_island.png"
    y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    out = sys.argv[3] if len(sys.argv) > 3 else "out/15_follow_part2.jpg"
    follow_slide(src, y0, out)
