# Scientific Figure Render QA

Use this reference for any generated scientific figure that contains embedded text, especially deterministic SVG/HTML/vector figures, forest plots, Love plots, balance plots, methods diagrams, study-design diagrams, timelines, and treatment-state schematics.

## Why this needs a separate QA pass

A figure can be logically correct and still fail visually after export. In particular:

- SVG `<text>` does not automatically wrap to fit a box.
- Browser, SVG, LibreOffice, and PowerPoint font metrics can differ.
- Font fallback can make a label wider or taller than it was during authoring.
- `fit: contain` can shrink a dense figure until labels are technically present but unreadable.
- A figure may look fine as source SVG but become crowded after rasterization or Office re-rendering.
- A montage is useful for deck rhythm, but it is not sufficient to validate small figure text.

Treat figure rendering as a two-stage problem: first make the figure internally valid, then verify it again inside the final slide.

## Figure construction rules

### 1. Never rely on automatic text fitting inside generated figures

For every label placed inside a bounded region:

- reserve an explicit text area;
- manually wrap long text into multiple lines;
- use SVG `<tspan>` or multiple text elements for deterministic line breaks;
- keep a visible padding margin between text and the box edge;
- do not assume changing `font-size` alone will fix overflow.

If a label is too long, prefer shortening or wrapping before reducing font size.

### 2. Use stable fonts and explicit metrics

- Prefer installed fonts used by the deck, such as `Noto Sans` for scientific figure labels.
- Avoid relying on browser-only or unavailable fonts inside figures.
- Keep most audience-facing figure text visually equivalent to approximately **14–16 pt at the final slide placement**. This includes row labels, axis labels, numeric estimate columns, and diagram labels that must be read during the talk.
- Secondary ticks, captions, and minor annotations may use roughly 12–14 pt final-equivalent. Below 12 pt is an exception, not the default.
- Derive source pixel font size from the final figure slot rather than hard-coding a px value. Approximate conversion: `final_pt ≈ source_font_px × (placed_height_in × 72 / source_height_px)`. For example, a 900 px-high figure placed 5.2 inches high needs roughly 34–39 px source text to appear around 14–16 pt.
- If the figure cannot fit at these sizes, shorten/wrap labels, reduce tick density, enlarge the figure slot, split panels, or move full detail to backup before shrinking primary text.

### 3. Reserve bands for labels instead of placing text on top of geometry

For timelines, pipelines, and state diagrams:

- reserve separate vertical bands for top labels, the main line/boxes, and bottom labels;
- keep arrow labels away from arrowheads and node labels;
- do not place two different annotations in the same horizontal band unless their bounding regions are explicitly separated;
- use leader lines when a label cannot fit cleanly next to its node.

### 4. Use conventional epidemiology styling for result figures

For forest plots, Love plots, balance plots, and similar statistical figures:

- theme the slide, not the statistical geometry;
- default to neutral black/grey axes and labels;
- use standard point + CI encodings;
- keep null/reference lines obvious;
- use restrained tick density;
- align numeric estimates in a separate column when present;
- use KI or other institutional accent only sparingly, if at all, inside the result figure.

A result figure should look like a normal epidemiology/statistics figure embedded in a branded slide, not like a branded infographic.

### 5. Prefer deterministic PNG embedding when SVG compatibility is uncertain

For figures whose labels and geometry have already been deterministically laid out:

1. author in SVG/HTML/vector form if convenient;
2. rasterize to a high-resolution PNG after the figure itself passes QA;
3. embed the PNG in PowerPoint using `fit: contain`;
4. retain the editable source figure separately for regeneration.

Do not use PNG as a way to hide a bad SVG layout. The source figure must be correct first.

If the target PowerPoint environment has shown blank or unreliable SVG rendering, treat embedded SVG media as a compatibility risk and prefer PNG for scientific figure objects.


### 6. Use a machine-checkable bbox gate for deterministic SVG text

For deterministic SVG/HTML/vector figures that contain labels inside boxes, nodes, panels, timeline bands, or reserved label regions:

- add `data-bbox="x,y,w,h"` to every bounded `<text>` element;
- add `data-bbox-name` for readable error messages;
- add `data-line-height` for multiline labels when line height is not obvious;
- run `scripts/check-svg-text-bounds.py figure.svg` before rasterizing or embedding;
- treat any width/height overflow as a hard failure;
- if a global font-size/readability pass changes figure font sizes, rerun this bbox check before rebuilding PPTX.

This check does not replace visual review, but it catches the class of errors where a label is wider than its node or panel even before Office rendering.

## Mandatory figure QA workflow

Run this loop for every figure-containing slide.

### Stage A — figure-only QA before PPTX assembly

1. Generate the figure source at its intended aspect ratio.
2. If the source is SVG with bounded labels, run `scripts/check-svg-text-bounds.py figure.svg` and stop on failure.
3. Rasterize the figure alone to PNG using the intended export path.
4. Open the figure PNG by itself at 100% scale.
5. Check all of the following:
   - no text crosses a box boundary;
   - no labels overlap each other;
   - no label collides with a line, marker, CI, arrow, or node;
   - no title, legend, tick label, or numeric column is clipped;
   - all long labels have deliberate wrapping;
   - axis ticks are sparse enough to read;
   - the smallest important label is still presentation-readable.
6. If any check fails, regenerate the figure source. Do not defer the problem to PowerPoint layout.

### Stage B — raw PPTX QA

1. Insert the figure as one coherent figure image object.
2. Render the raw PPTX through an Office-compatible engine to PDF/PNG.
3. Open every slide that contains a generated figure individually, not only in a montage.
4. Check:
   - the entire figure is visible with `contain` behavior;
   - the slide title/body does not collide with the figure;
   - the figure has not been scaled so small that labels become unreadable;
   - no Office font/rendering change created new clipping or overlap;
   - no figure is blank or missing.
5. If a slide fails, fix the source figure or the figure slot. Do not cover the error with another shape.

### Stage C — normalized final PPTX QA

After finalization / Office open-resave:

1. render the normalized final PPTX again;
2. inspect all figure slides again individually;
3. run the deck-level layout, palette, and figure-media checks;
4. only deliver after the normalized final render still matches the reviewed raw render.

Any mutation after finalization invalidates this QA and requires another finalization + render pass.

## Figure-specific checks

### Forest plots

- row labels do not collide with plotting area;
- CIs remain visible and are not clipped at the plot boundary without an arrow/indicator;
- null line is visible;
- subgroup headings are separated from estimate rows;
- right-side numeric estimate column has enough width;
- axis ticks do not overlap;
- point size does not obscure short CIs.

### Love plots / balance diagnostics

- variable labels are readable;
- before/after symbols are distinguishable without excessive branding;
- the SMD threshold is clearly marked;
- shared legends do not overlap panel headings;
- paired panels use comparable scales unless scientifically justified otherwise.

### Timelines / study-design / treatment-state figures

- labels do not sit directly on top of arrows or event markers;
- long state names use deliberate line breaks;
- arrowheads do not enter text boxes;
- time labels have their own band;
- repeated labels are omitted rather than stacked.

### Registry / data-source diagrams

- source names and descriptions fit inside their boxes;
- multi-line descriptions use explicit line breaks;
- all peer boxes share a consistent internal padding system;
- arrows between boxes do not run through text.

## Fail-fast conditions

A figure is not ready for delivery if any of the following is true:

- any text exceeds a box or figure boundary;
- any two figure labels visibly overlap;
- figure text is only readable by zooming in;
- a result figure has been decoratively restyled at the expense of standard statistical readability;
- the source SVG looks correct but the rasterized/Office-rendered version does not;
- an SVG figure renders blank in the target Office pipeline;
- the montage looks acceptable but the individual slide fails close inspection.

## Practical review rule

For decks with many figures, create two review artifacts:

- a montage for overall deck rhythm;
- individual slide renders for every figure slide.

The montage is a screening tool. Individual-slide inspection is the acceptance test for scientific figures.
