# Guizang Academic Hybrid PPTX deck-spec

The portable Academic renderer reads JSON in a 16:9 PowerPoint coordinate system in inches.

Canvas:
- width `13.333333`
- height `7.5`

This spec does **not** define a new design system. Geometry must come from the selected Guizang parent: Swiss `S01-S22` or original Style A `Layout 1-10`.

## Required visual identity

Academic defaults to Swiss. For KI or any explicit Style A request, the selected brand/profile may switch the parent family. The HTML parent template remains the visual source of truth.

```json
{
  "meta": {
    "title": "Example research talk",
    "author": "Author",
    "lang": "en-US",
    "mode": "seminar",
    "visualStyle": "guizang-swiss-academic",
    "baseStyle": "swiss",
    "designSource": "guizang-template",
    "pptxFidelity": "native-first",
    "figurePolicy": "whitelist-enforced",
    "headFontFace": "Inter Display",
    "heroFontFace": "Inter Display ExtraLight",
    "sectionFontFace": "Inter Display Light",
    "titleFontFace": "Inter Display Light",
    "bodyFontFace": "Inter",
    "monoFontFace": "JetBrains Mono",
    "labelFontFace": "JetBrains Mono",
    "cjkFontFace": "Noto Sans CJK SC",
    "backgroundColor": "FAFAF8",
    "inkColor": "0A0A0A",
    "accentColor": "002FA7",
    "grey1": "F0F0EE",
    "grey2": "D4D4D2",
    "grey3": "737373"
  },
  "slides": []
}
```

Default accent presets are those in `themes-swiss.md`: `002FA7`, `FFD500`, `C5E803`, `FF6B35`. Do not mix accents inside a deck. If and only if the user supplied an institutional/brand template and requested branding, `references/brand-overlay.md` allows replacing the Guizang accent token with a brand color actually extracted from that source.

For branded decks, prefer a fixed profile instead of repeating raw colors:

```json
{
  "meta": {
    "visualStyle": "guizang-swiss-academic",
    "designSource": "guizang-template",
    "pptxFidelity": "native-first",
    "figurePolicy": "whitelist-enforced",
    "brandProfile": "ki-swiss"
  }
}
```

A bundled profile ID resolves from `references/brands/<id>.json`; a JSON path is resolved relative to the deck spec. The renderer and validators must use the same profile. For `ki-swiss`, Swiss neutrals are locked. For `ki-editorial`, use the frozen Style A ink/paper theme block from the profile instead of Swiss neutrals.

Editorial example:

```json
{
  "meta": {
    "visualStyle": "guizang-editorial-academic",
    "baseStyle": "editorial",
    "designSource": "guizang-template",
    "pptxFidelity": "native-first",
    "figurePolicy": "whitelist-enforced",
    "brandProfile": "ki-editorial"
  }
}
```

## Required slide identity

Every body slide must declare the **real Guizang parent layout directly**:

- Swiss: `layout` is registered Guizang `S01-S22`;
- Electronic Magazine: `layout` is the original Guizang heading name `Layout 1` through `Layout 10`;
- `sourceLayout`: optional compatibility mirror of the same parent layout. If present, it **must equal** `layout`.

Example:

```json
{
  "kind": "figure",
  "layout": "S22",
  "sourceLayout": "S22",
  "takeaway": "The association attenuated after adjustment",
  "evidenceTreatment": "preserve",
  "elements": []
}
```

Swiss cover/closing may use the original registered identities directly:
- `layout: "SWISS-COVER-ASCII"`;
- `layout: "SWISS-CLOSING-ASCII"`.

Style A uses its original parent layouts directly (typically `Layout 1` for cover and the appropriate original closing/question layout) rather than inventing Swiss identities.

Do not use Academic-invented geometry IDs such as `A01-A12`, `P23`, `P24`, `CUSTOM`, or unnamed layouts. Academic semantics belong in `kind`, `takeaway`, and `evidenceTreatment`, not in a second geometry namespace.

## Slide fields

Recommended:
- `kind`: cover, question, methods, result, table, figure, definition, discussion, conclusion, section, closing;
- `layout`: Swiss `S01-S22` / registered Swiss cover-closing IDs, or original Style A `Layout 1-10`;
- `sourceLayout`: optional compatibility mirror of `layout`; when present it must be identical;
- `takeaway`: scientific claim/question;
- `evidenceTreatment`: preserve, relayout, redraw, annotate, expand-zoom;
- `figureKind`: **required whenever the slide contains a whitelisted scientific figure**; omission is not an escape hatch. Read `references/figure-generation-whitelist.md`;
- `allowNativeFigure`: exceptional native-PowerPoint escape hatch only when the user explicitly requested full PowerPoint editability; also require `userRequestedFullEditability: true` and a non-empty `nativeFigureReason`;
- `editableFigureWorkflow`: optional figure editability route. Use `"canva-magic-layers"` only for non-quantitative explanatory figures and only when an editable Canva companion is actually created; use `"native-pptx"` for the native exception above;
- `editableFigureSource`: path or stable asset reference for the exact image sent to Canva Magic Layers;
- `canvaDesignId`: record only after `image-to-design` returns the created editable Canva design; this proves Canva editability, **not** PowerPoint-native editability;
- `powerPointEditabilityVerified`: boolean; set `true` only after the final exported PPTX has been inspected and the intended figure internals are selectable/editable as native PowerPoint elements. A Canva design alone does not satisfy this field;
- `backgroundColor`;
- `elements`;
- `tone`: optional `light` / `dark`; for KI Editorial, `dark` resolves to the deep-purple editorial field, never black. `dark` is allowed by semantic kind only (`cover`, `section`, `transition`, `synthesis`, `conclusion`, `closing`) unless `allowDarkContent:true` with a clear `darkReason`;
- `rasterUnderlay` / `rasterOverlay`: browser-only effects only, with `rasterPurpose`;
- `visualPlate`: legacy compatibility only; do not use it for ordinary Academic slide text/layout;
- `notes`;
- `sources`.

## Figure classification gate

For every slide, classify the dominant evidence **before** drawing it. If the content is a forest/effect plot, methods pipeline, study-design/conceptual/treatment-state/state-transition/cohort/estimand/causal schematic, or graphical summary, set the matching `figureKind` and generate/preserve one figure picture. `meta.figurePolicy` must be `whitelist-enforced`. The validators also infer likely whitelist hits from labels/estimate patterns and primitive counts, so omitting `figureKind` will fail rather than silently reverting to PowerPoint boxes.

When the user asks for figure editability, read `references/canva-editable-figures.md` before choosing a route. `editableFigureWorkflow: "canva-magic-layers"` means an editable **Canva companion design** exists while the PPTX may still contain the original coherent image. Never use that workflow for quantitative/statistical evidence or as proof of native PowerPoint editability.

## Text roles

**Native-first rule:** ordinary display text stays native PowerPoint text. Do not rasterize `hero`, `section`, `title`, kicker, chrome, body copy, table text, result values or captions.

The Academic renderer provides family-aware editable defaults. Swiss uses the installed Inter family. KI Editorial PPTX uses `Noto Serif Display` for display text, `Noto Sans` for body, and `Noto Sans Mono` for mono/meta so Office does not fall back to Georgia / Arial / Courier New.

For KI Editorial on light pages, normal text defaults to `presentationTokens.readingInk`; secondary text defaults to neutral grey `presentationTokens.mutedInk`; on dark pages it defaults to the paper/light text color. `statistic` may use the KI accent on light pages. Normal methods/results/appendix slides default to light; do not inherit Style-A periodic dark pages.

Chinese text defaults to `Noto Sans CJK SC`. Explicit font overrides are allowed only for language/runtime compatibility, not to invent another visual theme.

### Explicit color provenance

Avoid explicit colors when a role can use Guizang tokens automatically. If an explicit non-token color is scientifically necessary, mark the element:

```json
{
  "type": "line",
  "role": "scientific",
  "color": "1F77B4",
  "colorSource": "scientific-data",
  "x": 1.0, "y": 2.0, "w": 3.0, "h": 0
}
```

For a secondary institution color, `colorSource: "institution-template"` is allowed only when the active brand profile lists that color in `approvedSecondary`.

Example:

```json
{
  "type": "text",
  "role": "body",
  "text": "Primary estimand: within-person change in EDSS after infection",
  "x": 0.67, "y": 1.72, "w": 5.8, "h": 0.52
}
```

Keep the Guizang title and this scientific copy as native PowerPoint text; match the parent layout through geometry and font hierarchy rather than rasterization.

## Scientific image

Use `fit: "contain"` for evidence by default. Read `references/figure-generation-whitelist.md` before building forest/effect plots or clearly illustrative study-design/methods/conceptual/state/cohort diagrams.

```json
{
  "type": "image",
  "role": "evidence",
  "path": "images/forest-plot.png",
  "x": 0.72, "y": 1.35, "w": 11.85, "h": 5.35,
  "fit": "contain"
}
```

Never crop away axes, legends, risk tables, panel labels, CI/CrI, reference lines, or scientifically meaningful whitespace.

Whitelisted generated figure example:

```json
{
  "type": "image",
  "role": "generated-figure",
  "figureKind": "forest-plot",
  "figureSource": "deterministic",
  "path": "figures/robustness-forest.png",
  "fit": "contain",
  "x": 0.72, "y": 1.35, "w": 11.85, "h": 5.35
}
```

For quantitative `forest-plot` / `effect-plot`, `figureSource` must be `deterministic` or `preserved`; never use generative image output for exact statistical geometry or values.

Brand logo example:

```json
{
  "type": "image",
  "role": "logo",
  "path": "assets/brands/ki-logo-accent.png",
  "fit": "contain",
  "x": 11.1, "y": 0.45, "w": 1.45, "h": 0.55
}
```

The logo slot is a maximum box. Preserve the intrinsic image ratio inside it; do not stretch the artwork to `w × h`.

## Native scientific table

```json
{
  "type": "table",
  "role": "evidence",
  "x": 0.72, "y": 1.55, "w": 11.85, "h": 4.85,
  "fontSize": 16,
  "headerRows": 1,
  "colW": [3.1, 2.0, 2.0, 2.75, 2.0],
  "rows": [
    ["Outcome", "Group A", "Group B", "HR (95% CI)", "P"],
    ["Hospital-treated infection", "12.38", "25.74", "2.27 (1.39–3.69)", "0.001"]
  ]
}
```

Cells can be objects with `options` for subtle Guizang emphasis. Keep borders light, straight, and rectangular. Do not use arbitrary decorative striping.

For `brandProfile: "ki-editorial"`, tables default to `tableStyle: "ki-editorial-banded"`: header uses the profile header tint, the **first body row is white**, the next body row uses the pale KI stripe tint, and subsequent rows alternate. This is structural banding, not significance encoding. Important effect cells may be bold, but their font size must remain equal to the other body cells. Keep an effect estimate and its interval in one cell.

```json
{
  "type": "table",
  "role": "evidence",
  "tableStyle": "ki-editorial-banded",
  "fontSize": 16,
  "headerRows": 1,
  "rows": [
    ["Stratum", "Outcome", "HR (95% CI)", "Interpretation"],
    ["Prior infection", "Seizure, 5-year", {"text":"HR 0.63 (0.49–0.80)", "options":{"bold":true}}, "Concentrated benefit"],
    ["No prior infection", "Seizure, 5-year", "HR 0.92 (0.82–1.04)", "Weaker evidence"]
  ]
}
```

Do not add a native `role: "statistic"` repeating the same table estimate on a KI editorial table slide unless `allowDuplicateStatistic: true` is explicitly justified.

## Cover / closing treatment

Keep cover/closing typography and metadata native/editable. Browser-only ASCII/WebGL/canvas atmosphere may be a declared raster underlay. Do not put the title into that raster.

For `ki-editorial`, preserve the original Style-A cover rhythm: a dark cover is a single full deep-purple field with light text; a light hero uses white `#FFFFFF`. Do not add a separate full-height KI-magenta sidebar/slab.

## Collision / overlap contract

By default, foreground content boxes must not overlap. The Academic validator checks text-text, text-table, text-logo and text-figure collisions. It also checks the normalized PPTX itself for severe text-box overlaps.

Panels/background shapes may sit behind text when they are explicit underlays. Do not solve a collision by shrinking everything; first move the conflicting objects, switch to the correct Guizang layout, or convert a whitelisted diagram/forest plot into one generated figure.

## Intentional overlaps

By default, content boxes must not overlap.

If an Sxx skeleton intentionally overlays text on an image or a highlight shape sits under text, mark the specific element:

```json
{"allowOverlap": true}
```

Use this only after visual review. Do not use it to silence an unknown collision.

## Layer order

1. background;
2. declared browser-only raster underlay, if any;
3. native editable PowerPoint elements;
4. declared browser-only raster overlay, only if it cannot cover selectable text.

If any raster layer is used, set `rasterPurpose` to one of `webgl`, `canvas`, `ascii`, `map`, `complex-css`, or `browser-effect`. `visualPlate` is legacy-only and requires `allowBrowserVisualPlate: true`; it must not contain ordinary slide text.

### Explicit panel role

For KI Editorial, use `role: "panel"` when a rectangle is truly a grouping panel. If `fill` is omitted, the Academic renderer may use the profile `panelFill` (`#EFE8EB`). Generic rectangles keep the normal page/background behavior and are **not** automatically tinted.

```json
{
  "type": "shape",
  "shape": "rect",
  "role": "panel",
  "x": 0.8, "y": 4.1, "w": 5.6, "h": 1.3
}
```

### KI Editorial macro-field role

For `brandProfile: "ki-editorial"`, use `role: "macro-field"` when a pale field is meant to solve page balance or group a major region. This is different from `role: "panel"`: a macro-field is large, continuous, and usually sits behind multiple elements. Use `layoutTreatment: "macro-field"` or `"big-type-anchor"` when the slide intentionally uses this solution.

A light content slide with three or more peer groups should have a visual anchor: big type, a central whitelisted figure, a central table, or a selective macro-field when whitespace is genuinely unbalanced. Do not require a macro-field if the slide already has adequate visual mass. Do not leave a three-column peer slide as mostly blank white, and do not create a wall of small filled cards.

```json
{
  "layoutTreatment": "macro-field",
  "elements": [
    {"type": "shape", "shape": "rect", "role": "macro-field", "fill": "EFE8EB", "x": 4.75, "y": 1.55, "w": 3.65, "h": 4.9}
  ]
}
```
