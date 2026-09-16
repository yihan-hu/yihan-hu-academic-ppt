# Academic Figure Generation Whitelist

Use this reference for every Academic PPTX / HTML+PPTX deck. The default slide layout remains native PowerPoint, but **whitelisted scientific figures are image objects by default, not piles of PowerPoint primitives**.

## P0 boundary

**Text-native by default; figure-image by enforced whitelist.**

Keep native PowerPoint objects for slide title, subtitle, kicker, chrome, page number, footer, body text, takeaways, scientific tables, ordinary grouping panels, and simple annotations outside a figure.

Before drawing each slide, classify whether its dominant evidence is one of the whitelisted figure kinds below. If yes, the final PPTX must normally contain a picture object for that figure. Do not evade the rule by omitting `figureKind`.

## Whitelisted figure kinds

- `forest-plot`
- `effect-plot`
- `methods-pipeline`
- `study-design-diagram`
- `conceptual-schematic`
- `treatment-state-diagram`
- `state-transition-diagram`
- `cohort-flow`
- `estimand-diagram`
- `causal-schematic`
- `graphical-summary`

A whitelist hit is **generation-required by default**. Use one coherent `type: "image", role: "generated-figure"` object (or a preserved source figure) rather than 10–70 rectangles, lines, arrows, dots and labels.

Generated figures with embedded text must also follow `references/figure-render-qa.md`: validate text layout in a figure-only raster preview, then re-check the figure after PPTX/Office rendering. Do not accept source SVG appearance as the final QA state.

The only native exception is when the user explicitly requests full editability of that specific figure. Then set all three: `allowNativeFigure: true`, `userRequestedFullEditability: true`, and a non-empty `nativeFigureReason`.

## Quantitative figures: deterministic only

For `forest-plot` and `effect-plot`:
- render from verified source values using plotting code / SVG / HTML / canvas, or preserve a trustworthy source figure;
- preserve row labels, effect measure, point estimate, CI/CrI, null/reference line, scale and subgroup headings;
- figure-internal numerical labels may be baked into the image because they are deterministically generated from the source data;
- never use a generative image model to invent exact axes, values, intervals or statistical geometry;
- set `figureSource: "deterministic"` or `figureSource: "preserved"`.

## Methods / conceptual illustrations: image object required

For pipelines, study-design diagrams, exposure/treatment-state schematics, estimand diagrams and cohort flows:
- create one coherent illustration asset before PPTX assembly;
- use deterministic SVG/HTML/vector rendering when labels/timing/state order must be exact;
- in ChatGPT environments, actually call the image-generation tool for genuinely illustrative artwork when appropriate; do not simulate image generation with PowerPoint shapes;
- when exact scientific labels/timing must be deterministic, render SVG/HTML/vector to PNG/SVG and still insert the result as a picture object;
- preserve arrow direction, state order, timing, grouping and logical relationships;
- final PPTX must contain the illustration as a picture object, not a PowerPoint dashboard of outlined boxes.

## Required deck-spec pattern

```json
{
  "meta": {"figurePolicy": "whitelist-enforced"},
  "slides": [{
    "kind": "figure",
    "figureKind": "forest-plot",
    "layout": "Layout 7",
    "elements": [
      {"type":"text", "role":"title", "text":"Target-trial findings were stable", "x":0.7, "y":0.7, "w":11.8, "h":0.6},
      {"type":"image", "role":"generated-figure", "figureKind":"forest-plot", "figureSource":"deterministic", "path":"figures/robustness-forest.png", "fit":"contain", "x":0.8, "y":1.55, "w":11.7, "h":5.2}
    ]
  }]
}
```

## Not whitelisted

Do not image-flatten ordinary text pages, scientific tables, single key numbers, ordinary grouping panels/cards, cover title/subtitle metadata, footers, logos, page chrome, or genuinely simple 2–3 element layouts.

Final QA must run both the deck-spec hybrid validator and `scripts/check-pptx-layout-integrity.py`; the latter heuristically rejects figure-like slides that still contain many native primitives but no real figure picture.
