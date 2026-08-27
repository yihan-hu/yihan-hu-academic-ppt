# PPTX Hybrid Mode

Use this reference whenever the requested output is `.pptx` or `both` (HTML + PPTX).

## Goal

Keep the existing HTML visual language, but make the PowerPoint version genuinely editable:

- **Native PPTX**: titles, body text, numbers, cards, hairlines, simple diagrams, basic charts, image frames.
- **Raster layer**: WebGL/canvas backgrounds, complex CSS filters, dense decorative SVG/CSS, maps, browser-only composites.
- **Never** solve hybrid mode by placing a full-slide screenshot over the whole slide when the slide contains text that should remain editable.

The PPTX should remain useful in Microsoft PowerPoint, Keynote, and WPS even if browser-only animation is absent.

## Output modes

Resolve output mode before implementation:

- `html` — existing single-file web deck only.
- `pptx` — hybrid editable PowerPoint only. HTML may be generated temporarily to rasterize browser-only layers, but it is not required as a final deliverable.
- `both` — produce `index.html`, `deck-spec.json`, and `deck.pptx` from the same content plan.

If the user says only “PPT” and does not specify a format, prefer `pptx` when editability/collaboration is important; otherwise preserve the existing HTML behavior. If they explicitly ask for PowerPoint/PPTX, use hybrid mode.

## Folder contract

Recommended project layout:

```text
project/ppt/
├── index.html                 # html/both only
├── deck-spec.json             # canonical PPTX content + geometry
├── deck.pptx                  # pptx/both
├── images/                    # photos, screenshots, diagrams
└── raster/
    ├── slide-01-raster.png    # browser-only layer, transparent where possible
    └── ...
```

Use `deck-spec.json` as the canonical source for **content, slide order, editable text, geometry, and PPTX-only element types**. HTML remains the canonical source for browser behavior and motion.

## Render order

For each PPTX slide, render in this order:

1. Native slide background color.
2. `rasterUnderlay` browser-only layer, if present.
3. Native editable elements in `elements[]`, in array order.
4. `rasterOverlay` only when an effect truly needs to sit above native content.

Prefer underlays. Overlays can make native elements difficult to select and can accidentally cover text.

## Native vs raster decision table

| Content | PPTX representation | Rule |
|---|---|---|
| title / subtitle / body / caption / KPI | native text box | always editable |
| cards / blocks / keylines / dividers | native shapes/lines | always editable |
| simple bars / timelines / matrices | native shapes + text | editable |
| photos / screenshots | native PowerPoint image | editable position/crop; pre-crop to the target ratio |
| WebGL / animated canvas | raster PNG | capture final static state |
| CSS blur / blend / shader / complex mask | raster PNG | only the effect layer, not the text |
| MapLibre map / dense browser map | raster PNG + native title/labels when practical | map itself can be raster |
| generated infographic with embedded text | image only if source is already a bitmap | prefer rebuilding important labels as native text when feasible |
| Motion One transitions | omit or approximate with PowerPoint animation only if explicitly requested | static final state is the default |

## HTML annotations for raster capture

When generating HTML that will also feed a PPTX, annotate browser-only layers:

```html
<div data-pptx-raster>
  <!-- complex CSS / SVG / map / visual effect only -->
</div>
```

Global browser-only canvases may use:

```html
<canvas data-pptx-raster-global ...></canvas>
```

Do **not** put editable title/body text inside `data-pptx-raster` containers. The raster capture tool intentionally hides normal slide content.

The rasterizer also preserves `.ascii-bg` automatically because Swiss cover/closing ASCII fields are browser-only decoration.

## deck-spec.json

Use 16:9 wide slide coordinates in **inches**: width `13.333333`, height `7.5`.

Minimal structure:

```json
{
  "meta": {
    "title": "Deck title",
    "style": "B",
    "theme": "ikb",
    "lang": "zh-CN"
  },
  "slides": [
    {
      "id": "01",
      "layout": "SWISS-COVER-ASCII",
      "backgroundColor": "143CFF",
      "rasterUnderlay": "raster/slide-01-raster.png",
      "elements": [
        {
          "type": "text",
          "text": "一种新的工作方式",
          "x": 0.72,
          "y": 1.25,
          "w": 10.8,
          "h": 1.35,
          "fontFace": "Arial",
          "fontSize": 48,
          "color": "FFFFFF",
          "bold": false,
          "margin": 0
        }
      ]
    }
  ]
}
```

### Supported native elements

`scripts/render-pptx.mjs` supports:

- `text` — native PowerPoint text. `runs` may be used instead of `text` for mixed emphasis.
- `shape` — native rectangle, ellipse, chevron, etc. Use a PptxGenJS shape name such as `rect`, `ellipse`, `chevron`.
- `line` — native line.
- `image` — native image placement. Use `fit: "contain"` for screenshots that must not crop; otherwise use `fit: "stretch"` only with assets already prepared to the slot ratio.

All geometry fields are inches. Colors are six-digit hex **without** `#`.

Example rich text:

```json
{
  "type": "text",
  "runs": [
    {"text": "72%", "options": {"bold": true}},
    {"text": "  faster", "options": {"italic": true}}
  ],
  "x": 0.8, "y": 1.0, "w": 5.0, "h": 0.8,
  "fontFace": "Arial", "fontSize": 30, "color": "111111", "margin": 0
}
```

## Style A mapping

Preserve the editorial/e-ink hierarchy:

- Main title: native serif text whenever the target machine has an appropriate Chinese serif font. Otherwise choose a stable local serif and document the substitution.
- Body: native sans-serif.
- Metadata/kicker: native monospace or a stable sans-serif fallback.
- WebGL fluid/contour/dispersive background: raster underlay.
- Photos: native images.
- Hairlines, stat cards, pipeline steps: native shapes + text.

Do not rasterize a whole editorial slide just because the background is complex.

## Style B mapping

Swiss locked mode still applies. `S01-S22` / registered cover and closing layouts remain the layout source of truth.

- All typography: native sans-serif text.
- Hairlines, grids, bars, timeline axes, matrix cells, KPI blocks: native lines/shapes/text.
- One accent color only.
- No gradient, shadow, or rounded rectangles.
- ASCII cover/closing field and browser-only grid canvas: raster underlay.
- S22 photo: native image, pre-cropped to 21:9.
- S08 MapLibre map: raster map panel is allowed; title, labels outside the map, and comparison copy should stay native.

For PPTX, interpret the HTML “large type / light weight” rule in PowerPoint points rather than vw/vh. Preserve hierarchy visually; do not mechanically convert CSS units.

## Workflow

1. Finish narrative, style, theme, slide count, and layout assignment exactly as in the HTML workflow.
2. Decide output mode: `html`, `pptx`, or `both`.
3. For `pptx`/`both`, create `deck-spec.json` **before** writing the final PPTX renderer output.
4. Keep all user-editable text and simple geometry in `elements[]`.
5. If browser-only visuals exist, mark them with `data-pptx-raster` / `data-pptx-raster-global`, then prepare per-slide capture sources:

```bash
python <SKILL_ROOT>/scripts/prepare-pptx-raster-html.py path/to/index.html path/to/raster-source
```

6. Use the host environment’s browser screenshot capability to render each prepared HTML file at 16:9 (recommended 1600×900), with transparent background when supported, into `raster/slide-XX-raster.png`. Do not use OCR or recreate native text inside the bitmap.
7. Set each slide’s `rasterUnderlay` to the corresponding PNG where useful.
8. Render PPTX:

```bash
node <SKILL_ROOT>/scripts/render-pptx.mjs path/to/deck-spec.json path/to/deck.pptx
```

9. Validate structure/editability:

```bash
python <SKILL_ROOT>/scripts/check-pptx-hybrid.py path/to/deck-spec.json path/to/deck.pptx
```

10. Render the PPTX to images using the environment’s available PowerPoint/LibreOffice/rendering tool and visually compare it with the HTML/reference layout.
11. Fix all visible overflow, overlap, font substitution, crop, and raster/native duplication problems before delivery.

## Quality gates

A hybrid PPTX is not complete until all are true:

- Important text is selectable/editable in PowerPoint.
- Simple charts/lines/cards are native, not baked into a screenshot.
- Browser-only effects appear as raster layers without duplicating native text.
- No raster overlay unintentionally blocks native text.
- Photos/screenshots use standard ratios and do not look stretched.
- Slide count/order matches the HTML/content plan.
- The PPTX opens without repair warnings.
- A rendered visual comparison preserves the chosen Style A or Style B character.

## Environment notes

- Prefer PptxGenJS for PPTX creation.
- In OpenAI slide environments, follow the installed `slides` skill and use its PptxGenJS helpers and render/overflow validation tools when available.
- In other local agent environments, `scripts/render-pptx.mjs` requires `pptxgenjs`; `image-size` is used for non-distorting `contain` placement.
- `prepare-pptx-raster-html.py` has no browser dependency; it only creates isolated capture sources. Use the environment’s available browser screenshot tool for the actual PNG capture.
