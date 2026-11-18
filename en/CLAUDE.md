# Project: production for [CHANNEL NAME]

This repository produces the channel's content with the "Fix It Once" method. Read these rules at the start of every session.

## Rules that never break

- Every piece starts from a complete brief in `batches/<YYYY-MM>/briefs/`. If anything is missing, ask before producing.
- Everything visual is generated from `bible/style.yaml`. Never invent style rules: if something is not in the bible, ask.
- On-screen text (titles, lyrics, quotes, thumbnails) comes from templates, never from an image generator.
- No paid generation runs without first showing the prompt and the cost and getting a "yes".
- Nothing is published or delivered without `batches/<YYYY-MM>/approved.json`. The hook in `.claude/settings.json` enforces it.
- The visual judge (`.claude/agents/judge.md`) discards and ranks; it never approves. The final call belongs to the owner.
- Every rejection from the owner is logged with `log-rejection` on the spot.
- The bible changes only once a month, through `propose-rules` and the owner's approval.

## Where things live

- Style bible: `bible/`
- Each month's briefs and pieces: `batches/<YYYY-MM>/`
- Limits per format and naming rule: `checks/rules.json`
- Measurable checks: `python3 checks/checks.py batches/<YYYY-MM>/output`

## This channel's formats

<!-- Adjust to your formats. They must match checks/rules.json -->
- Main video: 2560x1440, full length
- Reel: 1080x1920, 20 s or less
- Quote: 1080x1920, 30 s or less
- Thumbnail: 1920x1080 JPG

## Delivery

<!-- Where things are delivered and who gets notified -->
- Final folder: [path or Drive folder]
- Notice: email draft to [person], sent only with the owner's OK.

## Owner

[Name]. Decides at four points: the month's list, the finalists, the final cut and publishing.
