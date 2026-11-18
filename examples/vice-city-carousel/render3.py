#!/usr/bin/env python3
"""Batch 3: Fisher Island, Indian Creek (bonus), Gladeview, Leisure City.
Sources are 3:4 Runway renders, normalised to 768 px wide in work/ by prep()."""
import sys
from PIL import Image
from render import *          # noqa: F401,F403
IC["users"] = "\uf0c0"


import render as _r
_orig_base = _r.base
def _base_native(path, y0, scale_from=None):        # crop at the source's own width (no 768 downscale)
    return _orig_base(path, y0, Image.open(path).width)
_r.base = _base_native


def prep(src, dst):
    im = Image.open(src).convert("RGB")
    im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS).save(dst)


if __name__ == "__main__":
    for n in ("7_fisher_island", "8_indian_creek", "9_gladeview", "10_leisure_city"):
        prep(f"src/{n}.png", f"work/{n}.png")
    y0 = {k: int(v) for k, v in (a.split("=") for a in sys.argv[1:])}
    info_slide("work/7_fisher_island.png", y0.get("7", 48), "THE RICHEST  ·  #1", "1. FISHER ISLAND",
               "An island you can only reach by ferry or boat, superyacht marina, 1,026 residents",
               [("money", "Median household income:", "$250,001+/year (Census max)"),
                ("house", "Typical home value:", "$7,062,683"),
                ("pct", "Poverty rate:", "3.8%")],
               "OFF THE CHARTS", "Private ferry dock", "out/07_fisher_island.jpg")
    info_slide("work/8_indian_creek.png", y0.get("8", 48), "BONUS  ·  NR (NOT RANKED)", "NR. INDIAN CREEK",
               "An island village with its own police force and one guarded bridge",
               [("house", "Median home value:", "$2,000,001+ (Census max)"),
                ("money", "Median household income:", "Not published, too few homes"),
                ("users", "Population:", "39 people")],
               "DON'T ASK", "The guard gate", "out/08_indian_creek.jpg")
    info_slide("work/9_gladeview.png", y0.get("9", 48), "THE POOREST  ·  #5", "5. GLADEVIEW",
               "Metrorail access, right next to Liberty City",
               [("money", "Median household income:", "$47,469/year"),
                ("house", "Typical home value:", "$417,760"),
                ("key", "Median rent:", "$1,341/month")],
               "MODERATE", "NW 62nd Street", "out/09_gladeview.jpg")
    info_slide("work/10_leisure_city.png", y0.get("10", 48), "THE POOREST  ·  #4", "4. LEISURE CITY",
               "Affordable South Dade, close to Homestead and the Everglades",
               [("money", "Median household income:", "$41,977/year"),
                ("house", "Median home value:", "$375,100"),
                ("key", "Median rent:", "$1,723/month")],
               "MODERATE", "South Dixie Highway", "out/10_leisure_city.jpg")
    print("done")
