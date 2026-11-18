---
name: propose-rules
description: Once a month, reviews the logged rejections and proposes changes to the style bible, the CHANGELOG and the checks, so the owner can approve them in one sitting. Use it at the end of each month or when the owner asks to update the bible.
---

# Propose rules

The bible changes once a month, never mid-week. This skill prepares that change so the owner can decide it in ten minutes.

## Steps

1. **Read the month's rejections** in `bible/references/rejected/reasons.csv` (filter by date) and the suggestions in the judge's `verdict.md` files under `batches/<batch>/finalists/`.
2. **Group by pattern.** A pattern is the same reason, in other words, across two or more pieces.
3. **Decide what each pattern proposes:**
   - **repeated defect** → a new check in `checks/rules.json` or `checks/checks.py`, or new examples for the judge;
   - **repeated preference** → a new or adjusted rule in `style.yaml` and its explanation in `BIBLE.md`;
   - **whims** → propose nothing. Mention them only if they repeat three times or more.
4. **Write the proposal** under "Pending" in `bible/CHANGELOG.md`, one line per change with its origin:
   ```
   - Text zone grows from 25% to 30% of the height.
     Origin: 4 rejections for lyrics over dense vegetation (1104, 1111, 1118, 1125).
   ```
5. **Show the owner** a short table: change, origin, file it touches. Ask for a yes or no per row.

## When the owner approves

1. Apply each approved change to `style.yaml` and `BIBLE.md` at the same time, so they never disagree.
2. Bump the version (1.0 → 1.1) in `style.yaml` and move the changes from "Pending" to a new dated `CHANGELOG` entry.
3. Rejected changes are removed from "Pending" and not proposed again unless new rejections appear.
4. If the change is large (another palette, another technique), suggest retraining the style model, if there is one, and testing it separately before using it.
