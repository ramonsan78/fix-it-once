# Fix It Once

A kit for producing AI-assisted content without endless revisions. Every correction is made once, on the system, and never has to be asked for again.

Read the guide first (`docs/GUIDE.md` in the repository): it explains why each file exists.

## What's inside

```
en/
├── README.md                    this file
├── CLAUDE.md                    project instructions for Claude Code
├── bible/
│   ├── style.yaml               measurable rules, the ones the machine reads
│   ├── BIBLE.md                 the same rules explained for people
│   ├── CHANGELOG.md             which rule changed, when and why
│   └── references/
│       ├── approved/            approved pieces
│       └── rejected/            rejected pieces
│           └── reasons.csv      one row per rejection
├── brief/
│   ├── piece.json               one piece's brief, ready to copy
│   └── intake.csv               the same brief as columns, for Google Sheets
├── checks/
│   ├── rules.json               limits per format and naming rule
│   ├── checks.py                checks videos and thumbnails: duration, resolution, fps, audio and names
│   ├── block-publishing.py      hook that blocks publishing an unapproved batch
│   └── review-checklist.md      what a person reviews, and only that
├── batches/
│   └── README.md                how each batch and its approval are organized
└── .claude/
    ├── settings.json            turns on the publishing hook
    ├── agents/judge.md          the visual judge, separate from the generator
    └── skills/
        ├── generate-pieces/
        ├── review-pieces/
        ├── log-rejection/
        └── propose-rules/
```

## Getting started

1. Copy this folder's contents into a new repository (`git init`) and open it with Claude Code.
2. Fill in `bible/style.yaml` and `bible/BIBLE.md`. The sample values come from a music channel with painted illustrations; replace them with yours.
3. Put 10 to 30 approved pieces in `bible/references/approved/` and rejected ones in `bible/references/rejected/`, with their reason in `reasons.csv`.
4. Adjust `checks/rules.json` to your formats and naming rule.
5. Edit `CLAUDE.md` with your channel's name and where you deliver.
6. Ask Claude Code: "validate the briefs for batch 2026-12 and generate the variants". The skills do the rest.

## Requirements

- Claude Code.
- Python 3.9 or newer and FFmpeg (includes `ffprobe`) for the checks.
- Optional: MCP connectors for your generation tools (Runway, Krea, ComfyUI), Adobe, and your storage (Google Drive, Dropbox). Without them, the skills prepare the prompts for you to run.

## A warning

The template fixes the visual identity, never the structure or the idea of each piece. YouTube does not monetize channels whose content looks template-made or feels interchangeable from video to video: that is its "inauthentic content" policy, called "repetitious content" until July 2025 and clarified again in July 2026. Check the current version at https://support.google.com/youtube/answer/1311392

License: code under MIT, text under CC BY 4.0. See `LICENSE` and `LICENSE-DOCS.md` in the original repository: https://github.com/ramonsan78/fix-it-once
