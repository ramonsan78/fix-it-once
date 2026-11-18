---
name: generate-pieces
description: Generates the visual variants for a batch's pieces from their briefs and the style bible. Use it when the owner asks to produce, generate or prepare the images or backgrounds for a batch or a piece.
---

# Generate pieces

Generate only what changes in each piece (the image or the background). Text, typography and brand come from templates, never from a generator.

## Before generating

1. Read all of `bible/style.yaml`. Note the version: every piece records it.
2. Read the briefs in `batches/<batch>/briefs/`. Validate each one:
   - title follows the naming rule in `checks/rules.json`;
   - every quote appears word for word in the source text;
   - the source files exist;
   - the emotion exists in `by_emotion`. If it doesn't, don't invent one: flag the brief and ask.
   If a brief fails, report all its failures at once and don't generate that piece.
3. Check which generation tool is connected (Runway, Krea, ComfyUI, Adobe Firefly or another MCP).

## How to build each prompt

```
<base_prompt from style.yaml>, <the emotion's treatment in by_emotion>,
<scene: two or three concrete images that appear in the piece's text>
```

- Use the images in `bible/references/approved/` as style references if the tool allows it.
- Add the `negative_prompt` where the tool accepts one.
- Short prompts, in order of priority: long prompts make results worse.
- Aspect ratio from `composition.aspect` in the bible.

## Generate

1. **Show the plan and the cost before spending.** A table: piece, prompt, number of variants (`filter.variants_per_piece`), tool and estimated credit cost. Wait for an explicit "yes" from the owner.
2. Generate and save to `batches/<batch>/candidates/<piece-id>/`, named `v01.png`, `v02.png`, and so on.
3. Save `generation.json` next to them with: exact prompt, tool, model and version, seed if available, bible version and date. It makes results repeatable and auditable.

If no tool is connected, write the prompts to `batches/<batch>/candidates/<piece-id>/prompts.md` for the owner to run by hand, and say so.

## After

Hand the batch to the `review-pieces` skill. Don't show raw candidates to the owner unless they ask.
