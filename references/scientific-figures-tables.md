# Scientific Figures and Tables

## General rule

Theme the slide, not the data.

For Academic PPTX, also read `references/figure-generation-whitelist.md`. Ordinary slide layout remains native, while specific figure classes may be rendered as one coherent figure image.

The deck may use a restrained accent color, but figures retain their scientifically meaningful color encoding unless the underlying data is redrawn deliberately and the mapping is preserved.

## Publication figures

Prefer preserve + annotate when:
- source data is unavailable;
- the figure contains complex panels;
- exact scales and labels matter;
- the figure is already publication quality.

Use `fit: contain` for evidence figures. Never crop away an axis, legend, risk table, panel label, confidence band, or reference line.

If a publication figure has tiny labels, use one of:
- enlarge it;
- split it across slides;
- overview -> focus;
- redraw only if exact source data is available.

## Statistical plots

### Forest plots

Preserve:
- reference line;
- effect measure and direction;
- interval;
- row labels;
- subgroup headings;
- values when present.

Good redesign options:
- increase row spacing;
- align numbers in a separate right column;
- highlight 1-3 rows while leaving all rows visible;
- use repeated panels for different control groups or outcomes.

### Kaplan-Meier / cumulative incidence / event curves

Preserve:
- axis scale;
- time unit;
- censor marks if relevant;
- risk table when present;
- group legend;
- confidence bands if shown;
- analysis population and event definition.

Do not replace curves with a single endpoint number unless the full curve is retained elsewhere.

### Scatter / box / violin / distribution plots

Preserve:
- group sample structure;
- thresholds;
- visible spread;
- outliers unless the analysis intentionally excludes them;
- statistical annotation.

Do not remove points merely to make a box plot cleaner.

### Longitudinal trajectories

Preserve:
- time origin;
- treatment or event switching points;
- uncertainty bands;
- group color mapping;
- non-linear shape when it is the result.

Avoid straightening a non-linear model for visual simplicity.

## Tables

Tables are often the most faithful way to present dense scientific results.

### Re-typeset when values are available

Use native PowerPoint tables and:
- align decimals;
- use en-dashes for intervals;
- keep units in headers;
- keep effect estimate and CI/CrI together in one cell when they form one reported measure, e.g. `HR 0.63 (0.49–0.80)` under `HR (95% CI)`;
- use consistent precision;
- avoid vertical borders unless they improve grouping;
- use subtle structural fills or row tinting when the selected Guizang family supports them;
- use **14–16 pt body text by default** for live-presentation tables; use 12–14 pt only when density genuinely requires it, and prefer splitting before going below 12 pt;
- split across slides only when the audience cannot read the table.

For `KI x Electronic Magazine`, do not default to a paper-style three-line table. Read `references/ki-editorial-tables.md`: use a pale KI header fill, then start body zebra banding with **white on the first body row**, alternating with a very pale KI-pink tint.

### Highlight without deleting

Preferred emphasis:
- same-size bold on an important estimate cell;
- 5-10% tint on a key row when scientific emphasis is actually intended;
- a restrained border/rule around a key column only when needed;
- small callout outside the table only when it does not duplicate the same result as a second hero statistic.

Avoid:
- giant colored arrows covering values;
- deleting non-significant rows;
- replacing a full table with only statistically significant values.

## Scientific diagrams

Redraw diagrams when their purpose is conceptual rather than empirical.

Good candidates:
- data linkage;
- cohort matching;
- treatment pathway;
- time windows;
- causal model;
- biomarker mechanism at a high level;
- statistical workflow.

When the diagram matches the generation whitelist, prefer one coherent SVG/HTML/vector-rendered figure over many PowerPoint boxes/connectors. The figure may include its internal scientific labels. Use native shapes only for genuinely simple diagrams or when the user explicitly requires full editability. Keep arrow direction, timing, state order and logical relationships exact.

For anatomical or molecular illustrations, use trusted source imagery or user-supplied figures unless a schematic abstraction is sufficient. Do not use generative imagery for exact anatomical labels or quantitative biological mechanisms without source verification.

## Figure annotation vocabulary

Use short labels:
- "higher after treatment";
- "no clear separation";
- "attenuated after adjustment";
- "signal concentrated in subgroup";
- "peak near switching";
- "similar final level".

Keep interpretation separate from raw labels already inside the figure.

## Epidemiology result-figure default

For conventional epidemiology/statistical result figures — including forest plots, Love plots, balance diagnostics, and similar estimate displays — prefer a standard scientific visual grammar unless the user explicitly asks for a branded figure style. This means:

- neutral black/grey axes and labels;
- clear but minimal accent usage;
- standard point + CI encodings;
- readable numeric estimate columns;
- restrained tick density that avoids collisions;
- no decorative KI restyling that makes the figure look less like a normal epidemiology figure.

Brand identity should live mainly in slide typography, spacing, titles, and page-level fields, not in over-designed statistical graphics.

## Figure text QA

For the full construction and render-review loop, read `references/figure-render-qa.md`. In particular, do not rely on SVG text auto-wrapping or source-SVG appearance; validate the rasterized figure and the Office-rendered slide separately.

Before finalizing any generated figure image, explicitly check for:

- text crossing box boundaries;
- overlapping labels or tick marks;
- truncated legend/title/caption text;
- numeric columns colliding with the plotting area;
- row labels that become unreadable at projected viewing distance.

If a figure fails any of these checks, regenerate or split it. Do not accept small-font crowding as the default solution.
