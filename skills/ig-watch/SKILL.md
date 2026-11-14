---
name: ig-watch
description: >-
  Watch an Instagram video from a URL. Downloads the reel, post, IGTV or story,
  samples frames into a timestamped contact sheet, transcribes the audio, pulls
  the caption and counts, then actually looks at it and reports what happens
  on screen. Use when the user pastes an instagram.com/reel/, /p/, /tv/ or
  /stories/ link, or says "watch this reel", "what's in this Instagram video",
  "break down this reel", "transcribe this IG video", or hands over a video
  file they pulled from Instagram.
---

# ig-watch

You cannot stream video. This skill turns one into things you can read: still
frames, a contact sheet, a transcript and the post's metadata. Then you look.

```bash
python3 ~/.claude/skills/ig-watch/igwatch.py "<url>"
```

Output goes to `~/.claude/instagram/watch/<shortcode>/`:

| file | what it is |
| --- | --- |
| `video.mp4` | the download |
| `contact_sheet.jpg` | every sampled frame in one grid, each stamped with its time |
| `frames/fNN_<t>s.jpg` | the individual frames, 720px wide |
| `report.md` | caption, uploader, views/likes/comments, frame list, timed transcript |
| `report.json` | the same, structured |

## The steps

1. **Check the tools once.** `yt-dlp --version` and `ffmpeg -version`. If
   yt-dlp is missing: `pip install -U yt-dlp`. Transcripts need
   `pip install faster-whisper`. It is optional: without it you still get the
   frames.
2. **Run it** on the URL. Quote the URL, because `?igsh=` share links contain
   `&` and `?`.
3. **Read `report.md`**, then **open `contact_sheet.jpg` with the Read tool**.
   That is the watching. For anything the grid is too small to read (on-screen
   text, a product label, a face), open the single frame for that time.
4. **Need more detail on one moment?** Rerun with `--frames 24`, or grab one
   time yourself:
   `ffmpeg -ss 7.5 -i video.mp4 -frames:v 1 /tmp/t7_5.jpg`.
5. **Report** in this order unless the user asked something narrower:
   - **What it is** in one line: format (talking head, voiceover b-roll,
     skit, tutorial, slideshow), length, who posted it.
   - **The first 3 seconds**: what is on screen, the spoken line, the
     on-screen text. That is the hook, and it is most of why a reel works.
   - **Beat by beat**, with timestamps: what changes on screen and what is
     said. Merge frames where nothing changes.
   - **On-screen text**, verbatim, with times.
   - **Audio**: speech, the music or trending sound if the metadata names it,
     or silence.
   - **The caption and numbers** from the metadata, as given.

   If `/ig-reel` or `/ig-viral` is installed and the user is studying the reel
   to make their own, name the hook formula from `ig-reel/hooks.json`.

## Options

```
--frames N                  frames to sample (default ~1 per 2.5s, 6 to 16)
--model tiny|base|small     whisper size. base is the default; small for accents/noise
--no-transcribe             frames and metadata only
--cookies-from-browser X    chrome, firefox, safari, edge: for login-walled posts
--cookies cookies.txt       the same, from a Netscape cookies file
--out DIR                   parent output folder
<path/to/file.mp4>          a local file instead of a URL
```

## When it fails

- **"login required", "rate-limit", or empty results.** Instagram puts a lot
  behind a login, and more of it every year. Ask the user before you use
  their browser's cookies, then rerun with `--cookies-from-browser <browser>`.
  Never ask for their password.
- **Private accounts** need cookies from an account that follows them. If they
  do not have that, say so and stop.
- **Stories** expire after 24 hours and always need cookies.
- **Photo or carousel posts** have no video. Say so. yt-dlp can still fetch
  the images if the user wants them.
- **Network blocked** (a proxy `403`, common in sandboxes and cloud sessions):
  the host needs `instagram.com`, `www.instagram.com`, and the media CDNs
  (`scontent-*.cdninstagram.com`, `*.fbcdn.net`). Transcription also downloads
  a model from `huggingface.co` the first time. Otherwise, ask the user to
  download the file themselves and pass the path.
- **No transcript but there is speech**: faster-whisper is missing or its
  model download failed. Say it in the report. Do not guess what was said
  from the frames.

## Rules

- Report what the frames and transcript show. Between two sampled frames you
  did not see anything, so do not describe it. If a moment matters, sample it.
- Do not invent view counts, sounds or captions the metadata did not give.
- This is for viewing and studying. Do not repost someone else's video as the
  user's own, and do not scrape accounts in bulk. One link at a time, at the
  user's request, is the use this skill is built for.
