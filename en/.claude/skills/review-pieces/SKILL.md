---
name: review-pieces
description: Filters a batch before the owner sees it. Runs the measurable checks and the visual judge, and leaves 2 or 3 finalists per piece in a gallery. Use it after generating variants or rendering, and always before asking for approval.
---

# Review pieces

The owner should only see what needs their judgment. This skill discards everything else.

## Candidate images

1. For each piece with candidates in `batches/<batch>/candidates/<piece-id>/`, launch the `judge` agent (`.claude/agents/judge.md`) with that folder and the brief. Always a different agent from the one that generated.
2. Copy the finalists to `batches/<batch>/finalists/<piece-id>/` with their `verdict.md`.
3. If the judge left no finalist for a piece, don't show it: report which rule failed and propose regenerating with one specific adjustment.

## Rendered videos

1. Run `python3 checks/checks.py batches/<batch>/output --json batches/<batch>/report.json`.
2. If anything fails, fix it before showing anything. Only if you can't fix it, explain the failure to the owner in one line per file.

## The gallery

Build a single page for the batch (a Claude artifact or an HTML file at `batches/<batch>/gallery.html`) with:

- one row per piece: title, emotion and its 2 or 3 finalists side by side, in the judge's order;
- under each finalist, the judge's line;
- a place for the owner to mark the chosen one and write one sentence for each rejection.

Then ask for the review in a single message: how many pieces, how many finalists and which decisions are needed. Don't ask piece by piece.

## When the owner answers

- Chosen pieces: move them to `batches/<batch>/chosen/`.
- Each rejection with a reason: hand it to the `log-rejection` skill right away.
