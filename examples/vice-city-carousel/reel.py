#!/usr/bin/env python3
"""Turn the carousel slides into a 9:16 Reel (1080x1920, 30fps).
Each slide sits full-width on a blurred, darkened copy of itself, with a slow
push-in; slides change with a quick swipe-left (like swiping the carousel).
No audio track: add a trending sound in Instagram's editor."""
import glob, subprocess, sys
from pathlib import Path

OUT = Path("reel"); OUT.mkdir(exist_ok=True)
slides = sorted(glob.glob("out/*.jpg"))
FPS, T = 30, 0.35                                      # swipe duration


def dur(name):
    if name.startswith("01"): return 2.8              # hook: give it a beat
    if name.startswith("02"): return 2.6
    if name.startswith("14"): return 3.4              # the gap: big numbers
    if name.startswith("15"): return 3.2              # follow slide
    return 2.1


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-1500:])


segs = []
for s in slides:
    name = Path(s).name; d = dur(name); n = int(round(d * FPS)) + 1
    out = OUT / (Path(s).stem + ".mp4")
    filt = (f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"gblur=sigma=40,eq=brightness=-0.18:saturation=1.15[bg];"
            f"[0:v]scale=2160:2700,zoompan=z='1+0.035*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={n}:s=1080x1350:fps={FPS}[fg];"
            f"[bg][fg]overlay=0:285:shortest=1,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS), "-t", f"{d:.2f}", "-i", s,
         "-filter_complex", filt, "-map", "[v]", "-t", f"{d:.2f}", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", str(out)])
    segs.append((out, d))

# chain swipe transitions
inputs, chain, off, last = [], [], 0.0, "0:v"
for i, (p, d) in enumerate(segs):
    inputs += ["-i", str(p)]
for i in range(1, len(segs)):
    off += segs[i - 1][1] - T
    tag = f"x{i}"
    chain.append(f"[{last}][{i}:v]xfade=transition=slideleft:duration={T}:offset={off:.3f}[{tag}]")
    last = tag
total = sum(d for _, d in segs) - T * (len(segs) - 1)
run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain) + f";[{last}]format=yuv420p[v]",
     "-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", str(FPS),
     "-movflags", "+faststart", "reel_vice_city.mp4"])
print(f"{len(segs)} slides, {total:.1f}s -> reel_vice_city.mp4")
