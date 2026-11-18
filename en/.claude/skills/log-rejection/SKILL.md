---
name: log-rejection
description: Logs an owner rejection in bible/references/rejected/reasons.csv, with its category, so it doesn't happen again. Use it every time the owner rejects a piece, a take, a frame or a thumbnail and says why.
---

# Log a rejection

A rejection that isn't written down comes back. This skill turns the owner's sentence into a useful row.

## Steps

1. **Copy the rejected piece** to `bible/references/rejected/` named `no_<short-reason>_<MMDD>.png` (or its format). Example: `no_unreadable-lyrics_1204.png`.
2. **Categorize the reason** as one of three:
   - **defect**: an objective error anyone would see (deformed face, cut-off text, off-palette color, overlong duration);
   - **preference**: the owner's taste that can become a rule (sky too cold for a joyful song);
   - **whim**: a one-off rejection with no pattern ("I don't like the angle").
   If you're unsure between preference and whim, ask the owner in one line.
3. **Link it to a rule** in `bible/style.yaml` if one exists (for example `composition.text_zone`). If none does, leave the column empty: it's a candidate for a new rule.
4. **Add the row** to `bible/references/rejected/reasons.csv`:
   ```
   file,reason,category,date,related_rule
   ```
   The reason goes in the owner's own words, not reinterpreted.
5. **If it's a measurable defect** (duration, resolution, name, color), propose in one line adding it to `checks/rules.json` or `checks/checks.py`.

## What you don't do

- You don't change `style.yaml` or `BIBLE.md`. New rules are proposed once a month with `propose-rules`.
- You don't argue with the rejection. It's logged as is.
