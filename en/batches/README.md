# Batches

A batch is one month of production for one channel. It is built, reviewed and rendered together.

```
batches/
└── 2026-12/
    ├── briefs/           one piece.json per piece
    ├── source/           incoming audio, text and backgrounds
    ├── candidates/       generated variants, before filtering
    ├── finalists/        the 2 or 3 that pass the filters, per piece
    ├── output/           final videos and images
    ├── report.json       result of checks/checks.py
    └── approved.json     created by the owner on approval; nothing publishes without it
```

## approved.json

Written by the owner (or by Claude, when the owner says so explicitly in chat):

```json
{
  "batch": "2026-12",
  "approved_by": "Name",
  "date": "2026-12-18",
  "pieces": ["2026-12-lets-celebrate", "2026-12-christmas-at-the-door"],
  "notes": ""
}
```

The hook `checks/block-publishing.py` checks that this file exists before any publishing or delivery of the batch.
