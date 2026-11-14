#!/usr/bin/env python3
"""igwatch: turn an Instagram video URL into something Claude can watch.

Downloads the reel/post/story with yt-dlp, pulls evenly spaced frames and a
contact sheet with ffmpeg, transcribes the audio with faster-whisper when it is
installed, and writes report.md + report.json next to the media.

    python3 igwatch.py https://www.instagram.com/reel/XXXX/
    python3 igwatch.py URL --frames 16 --out ~/ig-watch
    python3 igwatch.py URL --cookies-from-browser chrome   # private / login-walled
    python3 igwatch.py ./local.mp4                          # already downloaded

Needs: yt-dlp, ffmpeg/ffprobe. Optional: faster-whisper.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def die(msg):
    sys.exit(f"igwatch: {msg}")


def slug_for(src):
    m = re.search(r"instagram\.com/(?:[^/]+/)?(?:reel|reels|p|tv|stories/[^/]+)/([A-Za-z0-9_-]+)", src)
    if m:
        return m.group(1)
    return re.sub(r"[^A-Za-z0-9_-]+", "_", Path(src).stem)[:60] or "video"


def download(url, outdir, args):
    if not shutil.which("yt-dlp"):
        die("yt-dlp not found. Install it: pip install -U yt-dlp")
    cmd = ["yt-dlp", "--no-playlist", "--no-warnings", "--write-info-json",
           "-f", "bv*+ba/b", "--merge-output-format", "mp4",
           "-o", str(outdir / "video.%(ext)s"), url]
    if args.cookies:
        cmd += ["--cookies", args.cookies]
    if args.cookies_from_browser:
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    r = run(cmd)
    if r.returncode != 0:
        err = (r.stderr or r.stdout).strip().splitlines()
        tail = "\n".join(err[-5:])
        hint = ""
        if "403" in tail and "proxy" in tail.lower():
            hint = ("\nThe network blocked instagram.com. Allow instagram.com, "
                    "www.instagram.com and the *.cdninstagram.com / *.fbcdn.net "
                    "media hosts, or download the file yourself and pass the path.")
        elif re.search(r"login|rate.?limit|private|cookies", tail, re.I):
            hint = ("\nInstagram wants a logged-in session for this one. Retry with "
                    "--cookies-from-browser chrome (or firefox/safari) or --cookies cookies.txt.")
        die(f"download failed:\n{tail}{hint}")
    vids = sorted(p for p in outdir.glob("video.*") if p.suffix not in (".json", ".part"))
    if not vids:
        die("yt-dlp finished but no video file was written (photo post?)")
    info = {}
    j = outdir / "video.info.json"
    if j.exists():
        info = json.loads(j.read_text())
    return vids[0], info


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", str(path)])
    if r.returncode != 0:
        die(f"ffprobe failed on {path}: {r.stderr.strip()}")
    d = json.loads(r.stdout)
    dur = float(d.get("format", {}).get("duration") or 0)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    has_audio = any(s.get("codec_type") == "audio" for s in d.get("streams", []))
    return dur, v.get("width"), v.get("height"), has_audio


def extract_frames(video, outdir, dur, n):
    fdir = outdir / "frames"
    fdir.mkdir(exist_ok=True)
    for old in fdir.glob("*.jpg"):
        old.unlink()
    n = max(1, n)
    times = [dur * (i + 0.5) / n for i in range(n)] if dur > 0 else [0.0]
    frames = []
    for i, t in enumerate(times, 1):
        f = fdir / f"f{i:02d}_{t:06.2f}s.jpg"
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video),
             "-frames:v", "1", "-vf", "scale='min(720,iw)':-2", "-q:v", "3", str(f)])
        if f.exists():
            frames.append((t, f))
    return frames


def contact_sheet(frames, outdir):
    if not frames:
        return None
    cols = 4 if len(frames) > 6 else min(3, len(frames))
    rows = -(-len(frames) // cols)
    sheet = outdir / "contact_sheet.jpg"
    inputs = []
    for _, f in frames:
        inputs += ["-i", str(f)]
    labels = "".join(
        f"[{i}:v]scale=360:-2,drawtext=text='{t:.1f}s':x=8:y=8:fontsize=22:"
        f"fontcolor=white:box=1:boxcolor=black@0.6[v{i}];"
        for i, (t, _) in enumerate(frames))
    pads = "".join(f"[v{i}]" for i in range(len(frames)))
    layout = "|".join(
        "_".join([("+".join(["w0"] * c) if c else "0"), ("+".join(["h0"] * r) if r else "0")])
        for i in range(len(frames)) for c, r in [(i % cols, i // cols)])
    filt = labels + f"{pads}xstack=inputs={len(frames)}:layout={layout}:fill=black[out]"
    r = run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt,
             "-map", "[out]", "-q:v", "3", str(sheet)])
    if r.returncode != 0 and len(frames) > 1:
        # drawtext may be missing (no fontconfig); retry without labels
        filt = "".join(f"[{i}:v]scale=360:-2[v{i}];" for i in range(len(frames))) + \
               f"{pads}xstack=inputs={len(frames)}:layout={layout}:fill=black[out]"
        r = run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt,
                 "-map", "[out]", "-q:v", "3", str(sheet)])
    if len(frames) == 1:
        shutil.copy(frames[0][1], sheet)
    return sheet if sheet.exists() else None


def transcribe(video, outdir, model_name):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, "faster-whisper not installed (pip install faster-whisper)"
    audio = outdir / "audio.wav"
    r = run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vn",
             "-ac", "1", "-ar", "16000", str(audio)])
    if r.returncode != 0:
        return None, f"audio extract failed: {r.stderr.strip()}"
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
        segs, info = model.transcribe(str(audio), vad_filter=True)
        out = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
               for s in segs]
        return {"language": info.language, "segments": out}, None
    except Exception as e:  # model download blocked, etc.
        return None, f"transcription failed: {e}"
    finally:
        audio.unlink(missing_ok=True)


def fmt_ts(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="Instagram URL (reel, post, tv, story) or a local video path")
    ap.add_argument("--out", default=os.path.expanduser("~/.claude/instagram/watch"),
                    help="parent output dir (default ~/.claude/instagram/watch)")
    ap.add_argument("--frames", type=int, default=0,
                    help="frames to sample (default: ~1 per 2.5s, 6 to 16)")
    ap.add_argument("--model", default="base", help="whisper model (tiny/base/small/...)")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--cookies", help="Netscape cookies.txt for login-walled posts")
    ap.add_argument("--cookies-from-browser", help="chrome, firefox, safari, edge...")
    args = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        die("ffmpeg/ffprobe not found")

    outdir = Path(args.out).expanduser() / slug_for(args.src)
    outdir.mkdir(parents=True, exist_ok=True)

    if re.match(r"https?://", args.src):
        video, info = download(args.src, outdir, args)
    else:
        video, info = Path(args.src).expanduser().resolve(), {}
        if not video.exists():
            die(f"no such file: {video}")

    dur, w, h, has_audio = probe(video)
    n = args.frames or max(6, min(16, round(dur / 2.5)))
    frames = extract_frames(video, outdir, dur, n)
    sheet = contact_sheet(frames, outdir)

    tr, tr_err = (None, "skipped (--no-transcribe)") if args.no_transcribe else \
                 (None, "no audio track") if not has_audio else \
                 transcribe(video, outdir, args.model)

    meta = {k: info.get(k) for k in (
        "title", "uploader", "uploader_id", "channel", "timestamp", "upload_date",
        "view_count", "like_count", "comment_count", "description", "webpage_url")
        if info.get(k) is not None}
    report = {
        "source": args.src, "video": str(video), "duration_s": round(dur, 2),
        "resolution": f"{w}x{h}", "has_audio": has_audio, "metadata": meta,
        "contact_sheet": str(sheet) if sheet else None,
        "frames": [{"t": round(t, 2), "path": str(f)} for t, f in frames],
        "transcript": tr, "transcript_note": tr_err,
    }
    (outdir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    L = [f"# Instagram video: {slug_for(args.src)}", "",
         f"- source: {args.src}", f"- file: {video}",
         f"- duration: {dur:.1f}s  ·  {w}x{h}  ·  audio: {'yes' if has_audio else 'no'}"]
    for k in ("uploader", "uploader_id", "upload_date", "view_count", "like_count", "comment_count"):
        if k in meta:
            L.append(f"- {k}: {meta[k]}")
    if meta.get("description"):
        L += ["", "## Caption", "", meta["description"]]
    L += ["", "## Look at these", ""]
    if sheet:
        L.append(f"- contact sheet: {sheet}")
    L += [f"- {fmt_ts(t)}  {f}" for t, f in frames]
    L += ["", "## Transcript", ""]
    if tr and tr["segments"]:
        L.append(f"(language: {tr['language']})")
        L += [f"- [{fmt_ts(s['start'])}-{fmt_ts(s['end'])}] {s['text']}" for s in tr["segments"]]
    else:
        L.append(f"_none: {tr_err or 'no speech detected'}_")
    (outdir / "report.md").write_text("\n".join(L) + "\n")

    print("\n".join(L))
    print(f"\nreport: {outdir / 'report.md'}")


if __name__ == "__main__":
    main()
