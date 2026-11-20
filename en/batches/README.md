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

Written by the owner, by hand. Claude can show the content to paste, but it never creates or edits this file: the hook blocks it.

```json
{
  "batch": "2026-12",
  "approved_by": "Name",
  "date": "2026-12-18",
  "pieces": ["2026-12-morning-light", "2026-12-long-way-home"],
  "notes": ""
}
```

Before any publishing or delivery of the batch, the hook `checks/block-publishing.py` checks that this file exists and is complete: `batch` matches the folder, `approved_by` is filled in, `date` is YYYY-MM-DD and `pieces` lists at least one piece. The hook doesn't check which piece each command delivers: that is still the owner's call.
