# KI Editorial Macro-Field and Peer-Panel Rule

Use this file whenever `brandProfile: "ki-editorial"` is active and a light content page feels too empty, too card-like, or visually unbalanced.

## Core rule

Do not solve light-page emptiness by either leaving most of the slide as unanchored white paper or filling every concept with a heavy pale card. Choose the lightest structural treatment that gives the page visual mass.

Three genuinely equal peers are a supported exception: they may use three subtle `#F7F3F5` peer panels without a macro-field. This is the preferred KI-reference treatment when the source content is truly parallel. Keep the panels flat, border-light or borderless, without shadow, and keep ordinary body text `#111111`.

## Treatment hierarchy

Use these in order of increasing visual mass:

1. **No fill** when a large heading, figure, table, or number already anchors the slide.
2. **Peer panels** (`role: "peer-panel"`, `#F7F3F5`) for two or three genuinely equal groups.
3. **Grouping field** (`role: "panel"`, `#EFE8EB`) when one bounded group needs stronger containment.
4. **Macro-field** (`role: "macro-field"`, `#EFE8EB`) for a large continuous visual anchor covering roughly 20–40% of the content area.
5. **Semantic band** (`role: "semantic-band"`, `#4F0433`) only when the band encodes a cohort, population, study phase, source, or major takeaway; use white text and at most one on a light slide.

Do not use fill simply because a slide has whitespace. Guizang whitespace is intentional when paired with oversized type, a strong figure/table ground, or a clear asymmetrical grid.

## Equal peers

For three comparable designs, aims, cohorts, outcomes, or subgroups:

- keep the three groups visibly peer-like;
- allow all three to use the same `#F7F3F5` peer-panel surface;
- use `#840050` only for the page title, compact number/icon/semantic label, or a short cue;
- keep descriptive copy `#111111`;
- avoid a second macro-field unless the page is still genuinely unanchored;
- do not tint only the leftmost or rightmost peer unless the narrative explicitly makes it different.

Deck-spec sketch:

```json
{
  "layoutTreatment": "peer-panels",
  "elements": [
    {"type":"shape", "role":"peer-panel", "fill":"F7F3F5", "x":0.8, "y":2.0, "w":3.7, "h":3.7},
    {"type":"shape", "role":"peer-panel", "fill":"F7F3F5", "x":4.8, "y":2.0, "w":3.7, "h":3.7},
    {"type":"shape", "role":"peer-panel", "fill":"F7F3F5", "x":8.8, "y":2.0, "w":3.7, "h":3.7}
  ]
}
```

## Macro-fields remain optional

A macro-field is a large background structure, not a card. Use it when a sparse page still lacks visual mass after trying type, figure/table ground, or equal peer panels.

If one macro-field is used behind three comparable peers, place it behind the **middle** peer by default so it does not imply left/right priority. A left/right 2+1 macro-field is allowed only when the source/story explicitly contains that asymmetry; set `asymmetricSemanticSplit: true` plus a provenance-bearing `semanticSplitReason`.

Examples of valid macro-fields:

- a right-side or left-side vertical field covering roughly 25–40% of content width;
- a bottom/top horizontal field covering roughly 20–35% of content height;
- a large pale index/word field acting as a graphic anchor;
- a wide figure/table ground;
- an asymmetric split that is semantically justified.

## Avoid

- `#EFE8EB` behind every small card or heading;
- three equal peer concepts receiving three **strong** `#EFE8EB` cards when `#F7F3F5` is sufficient;
- white content boxes relying only on hairline borders;
- a left/right-only fill that accidentally implies emphasis;
- multiple deep-plum bands on one light page;
- deep plum used as generic decoration;
- combining three peer panels with a large macro-field unless there is a real visual-balance need.

## QA

A KI Editorial light slide should avoid both extremes: unanchored white emptiness and a pink-grey card wall. Accept any of these anchors when semantically appropriate:

- `layoutTreatment: "peer-panels"` with up to three equal `#F7F3F5` panels;
- `role: "macro-field"`;
- `layoutTreatment: "big-type-anchor"`;
- a whitelisted generated figure occupying the visual center;
- a native table occupying the visual center.

Deck-level rule: macro-fields should remain a minority rhythm. If many light pages use >15% `#EFE8EB` coverage, return to typography, figure/table grounds, peer panels, and whitespace rather than adding more fill.
