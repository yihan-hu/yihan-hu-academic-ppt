# Guizang Academic PPTX — Native-First Fidelity

Use this reference whenever Academic Guizang outputs `.pptx` or `both`. It is an Academic override of the inherited Guizang hybrid baseline; do not modify the inherited `references/pptx-hybrid.md`.

## Core rule

Preserve Guizang **geometry, typography hierarchy, spacing and color-role discipline**, but keep normal PowerPoint content native/editable. For KI Editorial, override Style-A periodic dark/light rhythm with semantic dark pages. Do not use rasterization as a shortcut for ordinary layout fidelity.

### Native by default

Use PowerPoint-native elements for:

- cover/section/content titles and ordinary display text;
- body text, kicker, chrome, page number, footer and captions;
- scientific tables and editable result values;
- panels/cards, hairlines and simple decorative blocks;
- simple charts or genuinely simple diagrams when native editing is important;
- annotations and editable callouts.

For KI Editorial PPTX, use installed fonts: `Noto Serif Display`, `Noto Sans`, and `Noto Sans Mono`.

### Raster only for browser-only effects

Raster layers are allowed only for effects that PowerPoint cannot reproduce reasonably, such as WebGL, canvas, ASCII atmosphere, complex CSS masks/blends, or interactive map rendering. Declare `rasterPurpose` in the slide spec. A raster layer must not contain ordinary slide text, tables, or scientific values that could be native.

Scientific figures may remain image evidence (`type: image`, `role: evidence`) without being considered a rasterized slide layout.

### Whitelisted generated figures

Read `references/figure-generation-whitelist.md`. A whitelisted scientific figure may be one image object (`role: "generated-figure"`) even when it contains internal figure labels and result values. Quantitative forest/effect plots must be rendered deterministically from verified values. This is a figure object, not a full-slide rasterization.

### Editable explanatory figures via Canva

When the user explicitly wants to edit the internals of a **non-quantitative explanatory figure**, read `references/canva-editable-figures.md`. Canva Magic Layers may create an editable companion design from the coherent figure image. Keep these contracts separate:

- **Canva editability:** the decomposed design can be edited in Canva; record the returned design ID and source image provenance.
- **PPTX editability:** remains unverified unless a subsequent Canva PPTX export is opened and the intended internal objects are confirmed selectable/editable. Do not treat a Canva design ID as PowerPoint-native evidence.
- **Scientific fidelity:** quantitative/statistical figures and any exact evidence geometry bypass Canva decomposition entirely.

The default deliverable may therefore contain the coherent figure image in PowerPoint plus an optional editable Canva companion.

## KI Editorial color boundary

- `#4F0433` = dark editorial field / dark hero background.
- `#111111` = ordinary reading text on light pages.
- `#6F6B6D` = muted metadata/captions.
- `#840050` = selective KI accent.
- `#EFE8EB` = explicit very pale panel/header fill; `#F7F3F5` = table stripe fill; `#D9D9D9` = hairline/separator only.

Do not change the global dark-field token to black just to get neutral body text. Do not auto-fill every rectangle pale pink.
Also do not overcorrect into blank white pages. For KI Editorial sparse light pages, use a native `macro-field` shape or a large typographic anchor to restore Guizang visual mass.

## Layer order

1. slide background;
2. declared browser-only raster underlay, if any;
3. native PowerPoint elements;
4. declared browser-only raster overlay, only if it cannot cover selectable text.

`visualPlate` is not the normal Academic PPTX path. If legacy compatibility requires it, set `allowBrowserVisualPlate: true` and declare a browser-only `rasterPurpose`; it must contain no ordinary slide text.

## Logo / brand asset integrity

- Use `role: "logo"` and `fit: "contain"` for official logos.
- Never use stretch for a logo or other aspect-sensitive brand asset.
- Treat the logo rectangle as a maximum slot; preserve the intrinsic ratio inside it.
- Run `scripts/check-pptx-layout-integrity.py` on the normalized PPTX to catch repeated-logo distortion and foreground collisions.

## Visual QA

Compare the rendered PPTX against the selected Guizang parent layout. Fail the deck if:

- title scale/line breaks/left axis drift materially from the parent;
- typography falls back to Georgia/Arial/Courier New because unavailable fonts were requested;
- KI magenta becomes body ink instead of accent;
- dark KI Editorial pages become black;
- a light page becomes a field of pale-pink cards because generic rectangles were treated as panels;
- cover gains a second full-height accent sidebar/slab;
- normal slides repeat the KI logo without a deliberate reason;
- methods/results/appendix content pages are dark merely because of periodic Style-A cycling instead of a semantic reason.
