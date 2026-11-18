#!/usr/bin/env python3
"""Batch 2: Golden Beach, Brownsville, Medley, Opa-locka, The Gap."""
from render import *          # noqa: F401,F403  (shared helpers + info_slide)


def gap(src, y0, out):
    c = base(src, y0)
    c.alpha_composite(gradient((W, H), [(0, 225), (0.45, 170), (0.62, 40), (0.75, 0), (1, 0)], "x"))
    c.alpha_composite(gradient((W, H), [(0, 130), (0.12, 0), (0.80, 0), (1, 220)], "y"))
    brand(c)
    pill(c, "THE GAP", (60, 52), INTER("800-normal", 24))
    y = 250
    num = ANTON(124)
    for place, value in (("FISHER ISLAND \u00b7 MEDIAN HOUSEHOLD INCOME", "$250,001+"), (None, None), ("OPA-LOCKA \u00b7 MEDIAN HOUSEHOLD INCOME", "$37,532")):
        if place is None:
            vs = text_layer("vs", SCRIPT(84), fill=PINK + (255,), stroke=3, stroke_fill=(30, 0, 30))
            paste_shadow(c, vs, (70, y - 18), blur=10, offset=(0, 5), opacity=0.8); y += vs.height - 30
            continue
        pw, ph = pill(c, place, (60, y), INTER("800-normal", 22), fill=(255, 255, 255), color=DEEP + (255,))
        y += ph + 4
        l = text_layer(value, num, stroke=4, stroke_fill=(10, 0, 20))
        paste_shadow(c, l, (54, y), blur=14, offset=(0, 10), opacity=0.85); y += l.height - 6
    sub = INTER("700-normal", 36)
    y += 14
    for ln in wrap("Same county. Same sunset. 6.7× the income.", sub, 620):
        l = text_layer(ln, sub); paste_shadow(c, l, (62, y), blur=8, offset=(0, 3), opacity=0.95); y += 48
    y += 10
    pv = INTER("500-normal", 29)
    for ln in wrap("Poverty rate: 3.8% on Fisher Island vs 29.7% in Opa-locka.", pv, 640):
        l = text_layer(ln, pv, fill=(255, 255, 255, 235)); paste_shadow(c, l, (62, y), blur=6, offset=(0, 2), opacity=0.95); y += 40
    # CTA box
    y = y + 22
    bw, bh = 640, 140
    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=36, fill=PINK + (255,))
    paste_shadow(c, box, (60, y), blur=16, offset=(0, 8), opacity=0.55)
    q = text_layer("Which list are you on?", INTER("700-normal", 32)); c.alpha_composite(q, (96, y + 18))
    cta = text_layer("COMMENT RICH OR REAL", fit_font("COMMENT RICH OR REAL", ANTON, bw - 120, 62))
    c.alpha_composite(cta, (94, y + 58))
    arrow = text_layer("", ICON(46)); c.alpha_composite(arrow, (60 + bw - 74, y + 68))
    foot = INTER("500-normal", 19)
    f1 = text_layer("Sources: U.S. Census Bureau ACS 2020–2024 · Zillow Home Value Index, Oct 2026", foot, fill=(255, 255, 255, 200))
    f2 = text_layer("Fan page, not affiliated with Rockstar Games.", foot, fill=(255, 255, 255, 200))
    paste_shadow(c, f1, (60, H - 78), blur=5, offset=(0, 2), opacity=0.9)
    paste_shadow(c, f2, (60, H - 50), blur=5, offset=(0, 2), opacity=0.9)
    print("gap: CTA box bottom at", y + bh)
    c.convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    info_slide("work/6_golden_beach.png", 150, "THE RICHEST  ·  #2", "2. GOLDEN BEACH",
               "Oceanfront mansions, a residents-only beach, 691 residents",
               [("money", "Median household income:", "$236,250/year"),
                ("house", "Typical home value:", "$7,700,183"),
                ("pct", "Poverty rate:", "7.1%")],
               "MAXIMUM", "Private beach", "out/06_golden_beach.jpg")
    info_slide("work/11_brownsville.png", 200, "THE POOREST  ·  #3", "3. BROWNSVILLE",
               "Historic neighbourhood, Metrorail station, community roots",
               [("money", "Median household income:", "$40,795/year"),
                ("house", "Typical home value:", "$433,143"),
                ("key", "Median rent:", "$1,252/month")],
               "LOW", "Brownsville Metrorail station", "out/11_brownsville.jpg")
    info_slide("work/12_medley.png", 150, "THE POOREST  ·  #2", "2. MEDLEY",
               "Warehouses, rock quarries and trucking. 988 residents, far more loading docks.",
               [("money", "Median household income:", "$40,735/year"),
                ("house", "Median home value:", "$87,300"),
                ("key", "Median rent:", "$1,320/month")],
               "LOW", "A loading dock", "out/12_medley.jpg")
    info_slide("work/13_opa_locka.png", 120, "THE POOREST  ·  #1", "1. OPA-LOCKA",
               "The largest collection of Moorish Revival architecture in the Western Hemisphere",
               [("money", "Median household income:", "$37,532/year"),
                ("house", "Typical home value:", "$479,423"),
                ("key", "Median rent:", "$1,351/month")],
               "LOW", "City Hall's domes and minarets", "out/13_opa_locka.jpg")
    gap("work/14_gap.png", 60, "out/14_the_gap.jpg")
    print("done")
