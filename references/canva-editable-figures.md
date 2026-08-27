# Canva Magic Layers for Editable Academic Figures

Use this reference only when the user explicitly asks to edit the internals of a generated scientific/explanatory figure and the Canva connector exposes Magic Layers / `image-to-design`.

## Purpose

Magic Layers converts a flat PNG/JPEG/WEBP into a new Canva design whose text, shapes, and image regions may be separated into editable elements. Treat that result as an **editable Canva companion**, not as proof that the same figure is natively editable in PowerPoint.

The Academic PPT source of truth remains the Guizang deck spec and the original figure asset. Canva is an optional post-processing/editability surface for suitable explanatory artwork.

## Eligibility gate

### Allowed

Use Magic Layers for non-quantitative explanatory figures when editability is useful:

- `methods-pipeline`
- `study-design-diagram`
- `conceptual-schematic`
- `treatment-state-diagram`
- `state-transition-diagram`
- `cohort-flow`
- `estimand-diagram`
- `causal-schematic`
- `graphical-summary`

The source should be visually flat and semantically simple: clean blocks, arrows, monoline icons, short labels, restrained fills, limited texture, and no decorative effects that would make layer decomposition unstable.

### Forbidden

Do not use Magic Layers to reconstruct quantitative/statistical evidence or exact scientific geometry, including:

- `forest-plot`
- `effect-plot`
- Kaplan-Meier/survival curves
- Love/balance plots
- exact axes, tick positions, scales, point locations, CI/CrI lengths, reference lines, risk tables, or numerical geometry
- any figure where a small visual displacement could change the scientific interpretation

Those figures remain deterministic/preserved. If the user requires PowerPoint-native editability, rebuild them deterministically with native chart/vector primitives rather than decomposing a bitmap.

## Workflow

1. **Classify first.** Confirm the figure is an allowed explanatory kind under `references/figure-generation-whitelist.md`.
2. **Create the canonical figure asset.** Generate/render the figure at high quality and validate labels, arrows, timing/state order, and brand treatment before any Canva conversion.
3. **Preserve the canonical asset.** Keep the original source image used in the deck; do not replace it with an unverified Canva export automatically.
4. **Invoke Canva Magic Layers.** Use Canva `image-to-design` with the exact platform file reference when available. If there is no file reference or supported public URL, open the Magic Layers upload tile and have the user provide the image there; do not relay image bytes through model text.
5. **Record the result.** After conversion, store the returned Canva design ID and the exact source-image provenance in the project/deck spec.
6. **Optional Canva edits.** If further edits are requested, use Canva's editing transaction workflow and commit the transaction after applying changes.
7. **PowerPoint claim gate.** If a Canva-exported PPTX is used, open/inspect the exported file and verify that the intended internal objects are selectable/editable before setting `powerPointEditabilityVerified: true`.
8. **Scientific QA again.** After any Canva edit/export, re-check labels, arrows, state order, timing, colors, and semantics against the canonical figure. Never accept visual layer decomposition as evidence of scientific fidelity by itself.

## Deck-spec provenance

When this path is actually used, record fields such as:

```json
{
  "figureKind": "study-design-diagram",
  "editableFigureWorkflow": "canva-magic-layers",
  "editableFigureSource": "figures/study-design.png",
  "canvaDesignId": "D...",
  "powerPointEditabilityVerified": false
}
```

`canvaDesignId` proves only that an editable Canva design was created. It does not prove the final `.pptx` contains native PowerPoint shapes/text.

## Output contract

Prefer one of these explicit deliverable descriptions:

- **PPTX + editable Canva companion** — default when Magic Layers is used successfully; PowerPoint may still contain the coherent image.
- **Verified native-editable PPTX** — only after exported/internal elements are actually inspected in the final PowerPoint file.
- **PPTX image figure only** — when Canva is unavailable, conversion fails, or the figure is ineligible.

Do not silently degrade from a requested editable companion to a flat image. State the limitation and keep the scientifically validated canonical figure.

## Design-for-decomposition guidance

If Magic Layers is planned from the start, make the source figure easier to decompose:

- prefer flat fills, sharp boundaries, monoline icons, and short text labels;
- avoid photorealism, glassmorphism, heavy shadows, complex gradients, textured backgrounds, and tiny decorative fragments;
- keep text large enough for reliable recognition and keep labels separated from arrows/edges;
- keep important scientific relationships explicit rather than implied by decorative proximity;
- preserve the selected Guizang/KI color-role grammar, but do not bake slide title/footer/page chrome into the figure.
