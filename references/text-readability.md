# Presentation Text Readability

Use this reference for academic PPTX slides intended for live presentation. The target is projector readability, not manuscript-style density.

## Default size hierarchy

Treat **14–16 pt as the default band for most audience-facing text at final PowerPoint size**.

- Slide titles: normally 26–32 pt or larger according to the parent Guizang layout.
- Main body, bullets, result labels, table cells, diagram labels: **14–16 pt by default**.
- Forest/Love plot row labels, axis labels, estimate columns, panel headings that must be read: **14–16 pt final-equivalent by default**.
- Secondary captions, model notes, minor annotations: 12–14 pt.
- Below 12 pt: exception only. Prefer shortening, wrapping, reducing rows/ticks, splitting the slide, or moving details to backup first.
- Footer/page chrome/source metadata that is not meant to be read from the back of the room may be smaller. Do not use small footer sizes as justification for shrinking actual content.

The 14–16 pt rule is a presentation default, not a rigid minimum for every text object. The important distinction is whether the audience is expected to read it during the talk.

## Density rule

When a slide does not fit at 14–16 pt:

1. shorten wording;
2. wrap deliberately;
3. remove redundant labels;
4. reduce tick density or repeated annotations;
5. enlarge the figure/table slot;
6. split the evidence across slides or move full detail to backup;
7. only then reduce selected secondary text below 14 pt.

Do not shrink the whole slide uniformly as the first response to overflow.

## Generated figure scaling

For text embedded inside PNG/SVG scientific figures, judge size by its **final on-slide equivalent**, not the source pixel number.

Approximate conversion:

`final_pt ≈ source_font_px × (placed_height_in × 72 / source_height_px)`

Therefore the required source font size depends on how large the figure is placed. For example, a 900 px-high figure placed 5.2 inches high needs roughly 34–39 px source labels to appear around 14–16 pt. Do not hard-code a 24 px label and assume it is presentation-readable.


When increasing figure fonts to meet the 14–16 pt readability target, rerun the SVG text bounding-box gate before rebuilding the deck. Larger readable fonts often create new overflows inside nodes, panels, or timeline labels; this is not caught by native PPTX font-size checks because the text is inside an image.

## QA workflow

### Native PowerPoint text

- Review the slide at 100% after Office rendering.
- Run `scripts/check-pptx-font-sizes.py <deck.pptx>` as a diagnostic report.
- Investigate audience-facing text below 14 pt.
- Text below 12 pt must be consciously justified; if many content objects fall below 12 pt, redesign the slide.

### Figure-internal text

Follow `references/figure-render-qa.md`:

- inspect the figure-only raster;
- inspect the raw PPTX slide individually;
- inspect the normalized final PPTX slide individually;
- verify that the smallest important label still reads comfortably at the final placement.

## Acceptance rule

A deck should visually read as though **most meaningful content text is 14–16 pt or larger**. A small number of 12–13 pt supporting elements is acceptable. A slide that depends on 10–11 pt content for normal reading should normally be restructured rather than accepted.
