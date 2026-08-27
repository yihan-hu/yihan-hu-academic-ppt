# KI x Electronic Magazine — Table Grammar

Use this for native editable scientific tables in `KI x Electronic Magazine`. The table remains a real PowerPoint table.

## Defense-derived visual rule

Use the supplied Defense deck as the table color source, while Guizang controls spacing/typography:
- header: very pale KI pink-grey `#EFE8EB`;
- first body row: white;
- second body row: near-white KI pink-grey `#F7F3F5`;
- continue alternating white / near-white pink-grey;
- saturated accent `#840050` is reserved for a header rule or selective emphasis, not every border;
- internal borders are minimal and mainly horizontal; no dense four-sided spreadsheet grid. `#D9D9D9` may be used only as a hairline/separator, not broad fill.

The fills are structural only and never encode statistical significance.

## Typography inside cells

- Keep one body font size across the table.
- Emphasize an important result with **bold at the same font size**; do not enlarge one number.
- Keep effect estimate and interval in the **same cell**, e.g. `HR 0.63 (0.49–0.80)` under `HR (95% CI)`.
- Do not duplicate that estimate as a separate giant statistic unless explicitly requested.

## Default tokens

- `headerFill`: `EFE8EB`
- `stripeFill`: `F7F3F5`
- `bodyFill`: `FFFFFF`
- `gridColor`: `D9D9D9`
- `headerRule`: `840050`

These are the only default structural table colors. Do not reintroduce legacy `E6DDE2 / F3E8EE / FAF5F8 / F5EEF2 / DDD0D5 / 8F587B` variants.
