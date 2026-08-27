# KI Editorial Visual Grammar

Use this reference whenever `brandProfile: "ki-editorial"` is active. It defines color-role treatments derived from the KI academic references while Guizang continues to own layout geometry, typography hierarchy, spacing, and slide rhythm.

## Core light-slide grammar

A normal KI Editorial content slide should read as:

**white ground + KI-magenta title/cues + neutral-black reading text + restrained pale grouping**.

Role tokens:

- page ground: `#FFFFFF`;
- light-page slide title: `#840050`;
- ordinary body/explanation/table reading text: `#111111`;
- secondary text/caption: `#6F6B6D`;
- compact semantic label, number, monoline icon/arrow: `#840050`;
- subtle equal peer panel: `#F7F3F5`;
- stronger grouping/header/macro field: `#EFE8EB`;
- bounded semantic band: `#4F0433` with `#FFFFFF` text;
- hairline/separator: `#D9D9D9`;
- rare result/risk highlight: `#FD8169`.

Do not use magenta as paragraph ink. Do not use deep plum as decoration. Do not inherit the source KI slide's coordinates, fonts, rounded-card geometry, or footer placement.

## Treatment A — Peer overview

Use for Aim, design variants, outcomes, subgroups, or other genuinely equal categories.

- Keep the page white.
- Set the main slide title in `#840050`.
- Two or three equal groups may use matching `role: "peer-panel"` surfaces in `#F7F3F5`.
- Use `#840050` for a compact number badge, monoline icon, or short group heading.
- Keep descriptions in `#111111`.
- Use no shadow and no heavy border; hairlines, when needed, use `#D9D9D9`.
- Do not add an `#EFE8EB` macro-field merely because three peer panels exist.

## Treatment B — Longitudinal study / registry linkage

Use for follow-up timelines, registry linkage, study-entry diagrams, and similar methods stories.

- Keep the page white and the main title `#840050`.
- Render stage icons, short stage labels, and directional arrows in `#840050`.
- Keep explanatory text in `#111111`.
- A cohort/population/study-phase/source statement may use one bounded `role: "semantic-band"` in `#4F0433` with white text.
- Keep the semantic band below the main title hierarchy and within 18% of total slide area.
- Use at most one semantic band on a light slide.
- Registry/source icons beneath the band may use the same magenta monoline treatment.

If the timeline/study-design object meets the Academic figure whitelist, render the scientific diagram as one coherent figure image. The slide title, footer, and ordinary explanatory text remain native PowerPoint objects.

## Treatment C — Figure or table evidence

Use when the main visual is a scientific figure or editable table.

- Keep the surrounding slide white unless the slide is explicitly semantic-dark.
- Keep the slide title `#840050`.
- Preserve scientific data colors inside the figure; theme colors do not overwrite evidence encoding.
- Use `#EFE8EB` only when a stronger grouping/header/table ground is needed.
- Tables keep the KI Editorial banding rule: `#EFE8EB` header, white first body row, `#F7F3F5` next row, then alternate.
- Keep effect estimates and intervals scientifically intact; color treatment never implies significance by itself.

## Dark pages

Use full `#4F0433` dark fields only for cover, section, transition, synthesis, conclusion, or closing semantics. Light text is used on the dark field. Do not reintroduce periodic Style-A dark/light cycling and do not default to black.

## Deck-spec roles

Prefer these semantic roles instead of free-form colors:

- `title` → light-page default `slideTitle`;
- `semantic-label` → `semanticLabel`;
- `peer-panel` → `peerPanelFill`;
- `panel` / `macro-field` → `groupingFill`;
- `semantic-band` → `semanticBandFill`;
- `semantic-band-text` → `semanticBandOn`;
- `semantic-arrow` / `semantic-line` → `arrowStroke`;
- `icon-stroke` → `iconStroke`.

Explicit colors should match the active role token. Omitted colors may be filled by the Academic renderer's role defaults.

## QA

Reject a KI Editorial light slide when:

- an explicit `title` color is not `#840050`;
- ordinary `body` or `annotation` text is magenta;
- deep plum appears as an ordinary light-page shape instead of a `semantic-band`;
- more than one semantic band appears on a light slide;
- a semantic band exceeds 18% of slide area;
- a `peer-panel` uses a stronger fill than `#F7F3F5` without a semantic reason;
- more than three peer panels are used without a macro-field or layout rethink;
- the institutional reference has silently replaced Guizang geometry/typography/spacing.
