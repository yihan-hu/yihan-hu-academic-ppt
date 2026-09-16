# Academic PPT Quality Checklist

**This checklist is additive. First complete the inherited `references/checklist.md` using the active Guizang family: shared rules + Style A rules for Electronic Magazine, or shared rules + Style B/Swiss rules for Swiss. Do not silently skip Style A QA when `ki-editorial` is active. Then run the scientific checks below.**

## Scientific fidelity

- Every core claim is supported by the supplied source material or clearly marked as external context.
- n and denominators are preserved where relevant.
- Units and effect measures are visible.
- CI/CrI/error bars are preserved when part of the source result.
- Null/reference values are not removed.
- Data-group colors remain semantically consistent.
- Redrawn visuals use supplied/recoverable values only.
- Hypotheses are visually distinguished from established findings.

## Figures

- Evidence figures are not stretched.
- Read `references/figure-generation-whitelist.md`; a whitelist hit is **image-required by default**. Omitting `figureKind` does not permit native reconstruction.
- For KI Editorial, dark pages are semantic only; ordinary methods/results/appendix pages must remain light unless explicitly justified.
- Check palette roles: secondary text should be neutral grey, panel/table fill should be very pale, and `#D9D9D9` should not become a broad card color.
- Forest/effect plots generated from data are deterministic and preserve every plotted estimate/interval/reference line/label.
- Methods/study-design/conceptual/state/cohort illustrations may be single generated figures; slide title/body/footer remain native.
- A whitelisted figure is not assembled from dozens of PowerPoint primitives unless the user explicitly requested full editability and the spec records the exception.
- Final `scripts/check-pptx-layout-integrity.py` must reject likely forest/effect/methods/state illustrations that still have many native primitives but no real figure picture.
- No axis, legend, risk table, panel label, or meaningful annotation is cropped.
- Labels are readable on a projector.
- Most audience-facing text is approximately **14–16 pt at final slide size**; titles are larger, while supporting annotations may be 12–14 pt.
- Audience-facing text below 12 pt is exceptional and requires a density justification plus individual-slide visual review; prefer shortening, wrapping, splitting, or moving detail to backup before shrinking further.
- Generated figure text is judged by final on-slide equivalent size, not source SVG/PNG pixel size; read `references/text-readability.md` and `references/figure-render-qa.md`.
- Run `scripts/check-pptx-font-sizes.py <deck.pptx>` as a diagnostic for native text; investigate non-footer content below 14 pt and treat widespread sub-12-pt content as a redesign signal.
- Figure-internal text must be checked for clipping, overlap, and label collisions after the final raster/export step; if any axis label, tick label, legend entry, CI label, or annotation is crowded, the figure must be regenerated with fewer rows/ticks, larger margins, or a split layout rather than accepted as-is.
- Read `references/figure-render-qa.md` for any generated figure containing embedded text. A source SVG that looks correct is not sufficient evidence of final correctness.
- SVG `<text>` must never be assumed to auto-wrap or fit a bounded box. Long labels require deliberate line breaks / `<tspan>` layout and internal padding.
- For deterministic SVG figures with labels inside boxes/nodes/panels, run `scripts/check-svg-text-bounds.py` before rasterization/embedding; any `data-bbox` overflow is a hard failure, and font-size changes require rerunning this check.
- Every generated figure must pass **two visual checks**: figure-only raster preview before PPTX assembly, then individual-slide inspection after Office/PPTX rendering. A montage alone is not an acceptance test for small figure text.
- Repeat figure-slide inspection on the normalized final PPTX after Office open/resave. Any later mutation invalidates the visual certification.
- If a target Office environment has shown blank embedded SVGs, scientific figures must be rasterized to validated high-resolution PNG before embedding; use `scripts/check-pptx-figure-media.py <deck.pptx> --fail-on-svg` as a compatibility gate.
- Deterministic epidemiology result figures (forest plots, Love plots, balance plots, KM-style effect summaries) should default to conventional epidemiology styling: neutral text/axes, minimal accent use, clear null/reference lines, and standard CI/point encodings. KI branding may appear in surrounding slide chrome, but should not force decorative restyling of core statistical figures.
- Dense figures use overview -> focus when necessary.
- Annotation directs attention without covering evidence.

## Tables

- Values match the source.
- Decimal precision is consistent within comparable columns.
- Intervals use consistent notation.
- Units appear in headers or footnotes.
- Highlighting does not hide non-highlighted results.
- Font size is appropriate for the room and density.

## Methods

- Study design and analytic population are clear.
- Time windows and matching ratios are visible where important.
- Model class and estimand are not conflated.
- Key adjustment variables and interactions are retained when interpretation depends on them.
- Assumptions and sensitivity analyses are not omitted solely for aesthetics.

## Presentation hierarchy

- Slide title is a claim or question, not a generic label when possible.
- Evidence is the dominant visual element on result slides.
- Repeated result layouts are consistent.
- Navigation is stable only when the current deck genuinely needs persistent navigation; single-study decks should not invent Study I-IV chrome.
- Decorative elements do not compete with scientific evidence.

## PPTX quality

- Important text and tables are editable.
- Full-slide screenshots are avoided except for intentionally preserved non-editable pages.
- Raster layers do not cover editable text.
- No unintended overlap or out-of-bounds elements.
- Renderer output is kept as `deck.raw.pptx` and is **never** delivered directly.
- `scripts/finalize-pptx.py deck.raw.pptx deck.pptx --brand-profile <active-profile-id>` has passed after the final package mutation; this now includes final layout/figure QA and KI palette QA when applicable.
- ZIP CRC, XML parsing, internal relationships and required OOXML parts all pass.
- A real office engine has opened and re-saved the deck; the normalized deck preserves slide count, slide size and notes.
- The normalized deck has been rendered to PDF by the office engine with no error.
- The **normalized final deck**, not the raw deck, has been rendered to slide images and visually reviewed.
- The normalized final deck opens without repair warnings.

## Guizang Academic PPTX native-first checks

- `meta.pptxFidelity` is `native-first`.
- Ordinary title/body/kicker/chrome/table/result text remains native PowerPoint text.
- Browser raster layers are used only for declared WebGL/canvas/ASCII/map/complex-CSS effects and contain no ordinary slide text.
- KI Editorial visible text runs use installed `Noto Serif Display / Noto Sans / Noto Sans Mono`; ignore empty paragraph end-marker defaults inserted by Office, but no visible run may fall back to Georgia / Courier New / unavailable Playfair or IBM Plex.
- KI Editorial light-page background is `#FFFFFF`; light-page slide titles default to `#840050`, ordinary body/explanation text remains `#111111`, and compact semantic labels/icons/arrows may use `#840050` without turning paragraphs magenta.
- KI Editorial does not use the old Indigo-Porcelain `#F1F3F5` paper or the legacy pink stack `#E6DDE2 / #F3E8EE / #FAF5F8 / #F5EEF2`.
- KI Editorial dark pages use the deep-purple field, not black. A light page may use at most one bounded `#4F0433` `semantic-band` with white text when it encodes cohort/population/study phase/source/takeaway semantics.
- Generic rectangles are not automatically tinted. `#F7F3F5` is the subtle equal-peer panel surface; `#EFE8EB` is the stronger grouping/header/macro fill; `#D9D9D9` is the neutral hairline/separator.
- Three genuinely equal peer groups may use three matching `#F7F3F5` peer panels without a macro-field. Light KI Editorial pages must not read as empty white paper, but macro-fields remain selective; use `references/ki-editorial-macro-fields.md` and `references/ki-editorial-visual-grammar.md` before adding stronger fill.
- A KI Editorial cover does not contain a second full-height magenta sidebar/slab.
- KI logo is not repeated on ordinary content slides by default.
- Every brand logo preserves its intrinsic aspect ratio; `role: "logo"` uses `fit: "contain"`, never stretch.
- Run `scripts/check-pptx-layout-integrity.py` on the normalized final PPTX; severe text-text overlaps, logo/text collisions, repeated-small-image aspect distortion and out-of-bounds shapes are failures.
- For KI presets, run `scripts/check-ki-pptx-palette.py deck.pptx --profile ki-editorial|ki-swiss` on the normalized final PPTX; any legacy KI Editorial palette token, unexpected non-token color, or excessive pale-fill area is a failure. Use `--render-dir` when slide renders are available so raster figures are included in the audit.


## Template-first / brand overlay

- Every body slide names a real Guizang Sxx (or original Style A layout when explicitly selected); no Axx geometry exists.
- Slide construction started from the Guizang template/layout skeleton rather than a newly designed PowerPoint arrangement.
- If an institutional template was provided, only supported brand tokens/logo were inherited unless the user explicitly requested its layout.
- After branding, the deck still reads visually as Guizang first and institution second.
- Institution accent does not replace scientific data colors inside figures.

## Brand token lock

- A supplied institutional template was analyzed with `scripts/inspect-brand-template.py`; the Office theme was not assumed to be authoritative.
- A fixed brand profile is recorded before slide construction.
- Swiss brand mode keeps Guizang neutrals `FAFAF8 / 0A0A0A / F0F0EE / D4D4D2 / 737373` and replaces only the single accent family.
- Electronic Magazine brand mode keeps the exact frozen Style A six-variable ink/paper theme block; KI Editorial separates dark-field ink from light-page reading ink through `presentationTokens` rather than turning the global ink token black.
- In Swiss brand mode, the institution accent replaces the Guizang accent; the old IKB does not remain as a second slide-level accent.
- No manual component-by-component palette was invented after the profile was frozen.
- Every non-token explicit color has provenance: `institution-template` or `scientific-data`.
- `scripts/check-brand-token-lock.py deck-spec.json` passes.
- `meta.designSource` is `guizang-template`.
- The branded deck still reads as Guizang before it reads as the institution.

## KI preset regression

When using a built-in KI preset:

- run `scripts/check-ki-template-lock.py`;
- confirm `ki-swiss` contains only Swiss theme-token changes from `template-swiss.html`;
- confirm `ki-editorial` contains only Style A theme-token changes from `template.html`;
- confirm the selected `brandProfile` matches the selected parent family;
- treat any extra KI-specific layout CSS as a failure.

## KI x Electronic Magazine tables

- Native table uses `ki-editorial-banded` unless a publication-style table is explicitly requested.
- Header is tinted; the first body row is white; subsequent body rows alternate pale KI tint / white.
- Important estimate emphasis uses bold at the same body font size; no enlarged cell text.
- Effect measure and 95% CI/CrI stay in the same cell.
- No duplicate giant statistic repeats a value already emphasized inside the table unless explicitly requested.
