# KI-template — Neutral Ivory Academic

This is the user-approved Karolinska academic PPT design language from the October 2026 ALS serology talk, generalized into an **editable, study-neutral** 16:9 starter.

## Use

1. Choose the exact preset `KI-template` (brand profile: `references/brands/ki-template.json`).
2. Run `/usr/bin/python3 scripts/build-ki-template.py` to regenerate `assets/templates/KI-template-starter.pptx`.
3. Duplicate the relevant starter slide and replace placeholders with the new study's source-grounded content.
4. Keep logos and source data separate. The starter uses the existing official KI white logo asset; do not stretch or recolor it.
5. Render and review final presentation after editing.

## Fixed palette

| Purpose | RGB |
| --- | --- |
| Cover field | `#4F0433` |
| Content slide canvas | `#FAFAF8` |
| Selected grouping panel | `#F7F0F4` |
| High-contrast neutral peer panel | `#FFFFFF` |
| Semantic accent | `#870052` |
| Reading text | `#302A30` |
| Heading text | `#302330` |
| Caption | `#736A73` |
| Rules | `#E7E3E6` |

## Visual grammar

Use no repeated decorative network/dot graphic. Content slides have a left accent tick, a horizontal separation beneath the title, generous whitespace, and a quiet footer. The cover has deep KI plum full bleed, an unmodified white KI logo at upper-right, large left title, subtitle, and byline, without a duration label.

Supported editable archetypes: Cover, prior evidence vs study objective, study population/methods, baseline table, single effect-size hero, forest plot, take-home messages. The starter deliberately uses generic placeholders rather than ALS research data.

Scientific chart values and credible/confidence intervals must always be replaced with source-verified values. Avoid duplicating the same statistic in two panels. Use one magenta accent for featured associations and grey for comparison marks.

## Compatibility

`KI-template` is an **independent native PowerPoint preset**, not a Guizang derivative. Existing locked `ki-swiss` and `ki-editorial` remain unchanged. The `assets/templates/KI-template-starter.pptx` sample is a generic blank starter and should not be treated as an ALS paper source.

## Validation

```bash
/usr/bin/python3 scripts/build-ki-template.py
/usr/bin/python3 - <<'PY'
from pptx import Presentation
p=Presentation('assets/templates/KI-template-starter.pptx')
assert len(p.slides)==7
print('KI-template slides:', len(p.slides))
PY
python3 scripts/check-ki-template-lock.py
```
