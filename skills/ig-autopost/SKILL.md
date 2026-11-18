---
name: ig-autopost
description: >-
  The nightly content run for @vicecity_clipz (Instagram, GTA 6 niche: every
  post is about GTA 6 itself): research what is going viral in the niche, write 29 post
  ideas, pick the 5 strongest with prompts and hooks, generate the media with
  Dreamina on the cheapest model that does the job, edit it into a finished
  carousel or Reel, write a growth-and-monetisation caption, then queue a
  preview and WAIT for the owner's approval before anything goes live. Use when
  the scheduled 2 AM run fires, or when the user says "run the content
  workflow", "make tonight's post", or "do the nightly run".
---

# ig-autopost: the nightly @vicecity_clipz run

Account: Instagram **@vicecity_clipz** (Zernio account id `6ac45328d53fb57dc65f572b`).
Niche: **GTA 6, and only GTA 6.** Every post is about the game itself: news,
launch, map and regions, characters, missions, vehicles, weapons, secrets,
discoveries, comparisons with earlier GTAs, fan debates and theories. Real-world
Miami/Florida material is allowed only as a supporting angle inside a GTA 6
post (e.g. "GTA 6's Leonida Keys vs the real Keys"), never as the topic. If an
idea would still work with "GTA 6" deleted from it, it is off-niche: drop it.
Goal: views that turn into followers and money (Reels bonuses, subscriptions,
brand deals). Every post must earn a follow, not just a like.

**Hard rules (never break):**

- **Never publish without the owner's explicit approval in chat** ("approve",
  "post it", "go"). The run ends at a preview plus a Zernio *draft*. Silence is
  not approval. A previous day's approval does not carry over.
- **Credit cap: 150 Dreamina credits per run.** Quote first (`node quote`).
  If the plan would exceed 150, generate only what fits, or stop and ask.
  Never raise the cap yourself. Report credits spent and credits left.
- **Cheapest model that does the job.** Images: Seedream 5.0 Flash or Seedream 4.5
  first. Nano Banana Pro or GPT Image only when the image needs readable text or
  exact likeness of a real place. Video: Seedance 2.0 Mini or Seedance 2.5 Draft
  first, 5 s clips, 720p. Seedance 2.0/2.5 full only if the cheap tier visibly
  fails and the cap allows it. Use the live `model list` names, never guesses.
- **No made-up facts.** Every number on a slide or in a caption needs a source
  (Census via `place-stats`, a dated news article, an official Rockstar post).
  If you cannot source it, drop it or write `{{verify}}` in the preview and say so.
- **No reposting other people's footage or Rockstar's trailers and art.** Generated
  or original media only. Credit any creator whose idea or clip is referenced.
  Keep "Fan page, not affiliated with Rockstar Games."
- **5 hashtags max.** One call to action per caption.

## 0. Preflight (2 minutes)

1. `export PATH=$HOME/.local/bin:$PATH`. Check `dreamina-canvas --format json version`.
   If it's missing, reinstall: download `https://dreamina.capcut.com/canvas-cli/install.sh`,
   read it, run it, then `ln -sfn ~/.agents/skills/dreamina-canvas-cli ~/.claude/skills/dreamina-canvas-cli`.
2. `dreamina-canvas --format json auth status`. If `loggedIn` is false, run
   `auth login --no-browser`, send the owner the link and code (SendUserFile is not
   needed; a short message is enough), run `auth wait` for up to 5 minutes, and if
   it does not complete, **continue with steps 1, 2 and 5 only** and note that
   generation is waiting on sign-in.
3. Read the Dreamina Skill (`~/.claude/skills/dreamina-canvas-cli/SKILL.md`) and
   run `briefing` once. Check `auth account` for credits.
4. Check Zernio: `accounts_list` (instagram) shows `vicecity_clipz` and the
   account health is `canPost`.
5. Load history: `~/vicecity-autopost/history.json` (create if missing). It lists
   ideas already posted or rejected; never repeat them.

## 1. Research and 29 ideas

- Search the web (WebSearch, several queries in one turn) for what is working
  **this week** in GTA 6: news, patches, discoveries, easter eggs, records,
  viral GTA 6 Reels and carousels, fan theories, comparisons, trending formats (POV, "rating", "real vs game", countdowns,
  myth checks). Prefer sources from the last 7 days.
- If a specific viral Reel URL turns up, view it with `/ig-watch` and note the
  hook formula (see `/ig-viral` for ranking by outlier multiple).
- Check what our own posts did with Zernio analytics when available
  (`analytics_get_analytics` / `posts_list`) and lean into what worked.
- Write **29 ideas**. For each: one-line concept, format (Reel / carousel /
  single image), why it should travel (search demand, debate, saves, shares),
  and the monetisation angle (follow driver, series potential, brand fit).

## 2. Pick the top 5 and write the table

Score each idea 1-5 on: timeliness, share/debate potential, save value,
follow potential (series), production cost (cheaper scores higher), and
fact-risk (lower risk scores higher). Pick the top 5 and output a markdown table:

| # | Idea | Format | Hook (first 3 s / cover line) | Dreamina prompt(s) | Caption angle + CTA | Est. credits |

Hooks: score them with `python3 skills/ig-reel/hookscore.py` and keep the
strongest. Save the 29 ideas and the table to
`~/vicecity-autopost/YYYY-MM-DD/ideas.md`.

## 3. Generate with Dreamina (idea #1; more only if the cap allows)

Produce the **#1 idea** as a finished post. If credits remain under the cap,
pre-generate assets for #2. Follow the Dreamina Skill exactly: create or reuse
a canvas, send its link, save nodes, `node quote`, then run within the cap.
Use one node per output. Inspect every output (look at the images and frames)
and regenerate only what misses. Style anchor: stylized illustrated
video-game key art, bold ink outlines, cel shading, magenta/violet/gold dusk,
and always append "no text, no letters, no logos, no watermark, no borders,
no dark bands, no overlays".

## 4. Edit into a finished post

- Carousel: 1080x1350, reuse the layout code in
  `examples/vice-city-carousel/render*.py` (pink pills, Anton headlines,
  @VICECITY_CLIPZ mark, source footer, SWIPE prompt). Last slide = follow CTA
  for the next part of the series.
- Reel: 1080x1920, 15-30 s. Hook on screen in the first second, cuts every
  1.5-2.5 s, captions/text overlays readable in the safe zone (keep the bottom
  ~300 px clear), original synthesized score (no copyrighted music). Reuse
  `examples/vice-city-carousel/reel.py` patterns and the trailer score generator.
- Look at the result (contact sheet, a few frames) before calling it done.

## 5. Caption for growth and money

Write it with `/ig-caption` rules, then check it:
`python3 skills/ig-caption/caption.py caption.txt --keywords "gta 6,vice city"`
must say READY, and `python3 skills/ig-human/detect.py caption.txt` must PASS.
Structure: hook in the first 125 characters, one concrete payoff, one CTA
(comment keyword for reach, or follow for the series), source line, fan-page
line, 5 hashtags. Add a suggested pinned comment.

## 6. Preview and wait

1. Upload media with Zernio presigned URLs, run `validate_post`, then create the
   post as a **draft** (`posts_create` with `is_draft=true`). Never `publish_now`
   and never schedule without approval.
2. Build a preview image (feed mockup + caption + all slides, like
   `examples/vice-city-carousel/preview.py`) and send the owner, with
   `status: proactive`: the preview, the finished media, the top-5 table, credits
   spent / left, and the Zernio draft id.
3. Ask for approval in one line: "Reply **approve** to post now, **approve 7pm**
   to schedule, or tell me what to change."
4. Record the run in `history.json` (date, ideas, chosen idea, draft id, status
   `awaiting_approval`). **Stop.** When the owner approves, publish or schedule
   that exact draft, confirm it went live with `posts_get`, and update history.
