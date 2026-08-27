# Scientific Fidelity

## Principle

Preserve scientific information. Reduce visual competition.

A slide can be dense and still be well designed. The objective is not maximum whitespace; it is fast orientation, faithful evidence, and controlled attention.

## Three-layer review

Before redesigning a slide, score it on three dimensions.

### 1. Data fidelity

Ask whether exact values or visual encodings carry scientific meaning.

High data-fidelity content includes:
- effect estimates and uncertainty intervals;
- survival curves and risk tables;
- forest plots;
- scatterplots, distributions, and trajectories;
- heatmaps and imaging;
- model coefficients;
- sample sizes and denominators;
- tables with multiple estimates;
- sensitivity analyses.

High data-fidelity content should usually be preserved, relaid out, or redrawn only from reliable source values.

### 2. Semantic fidelity

Ask whether the structure itself carries meaning.

Examples:
- cohort inclusion/exclusion flow;
- temporal relationship between exposure, treatment, and outcome;
- causal or mediation model;
- repeated measures structure;
- hierarchical model;
- subgroup or interaction logic;
- definitions such as PIRA, relapse windows, or confirmation periods.

Semantic structure may be redrawn if the relationships and labels are known exactly.

### 3. Visual flexibility

Ask how much freedom exists to change appearance without changing the science.

High flexibility:
- title hierarchy;
- spacing;
- grouping;
- line weight;
- table typography;
- panel order when order is not meaningful;
- annotation placement.

Low flexibility:
- axis range;
- data colors that encode groups;
- uncertainty;
- reference lines;
- statistical significance markings;
- clinically meaningful thresholds;
- temporal order.

## Treatment decision

### Preserve

Choose when the original scientific visual is already legible, values are unavailable, or exact reconstruction would be risky.

Improve:
- slide title;
- figure size;
- surrounding whitespace;
- takeaway annotation;
- source line;
- crop only if no scientific content is removed.

### Relayout

Choose when all content is correct but hierarchy is weak.

Typical operations:
- move the takeaway above the figure;
- group model details into a secondary column;
- align multiple figures to a common grid;
- convert prose into labeled blocks without deleting details;
- rebuild a table with better typography.

### Redraw

Choose only when exact information is available from data, vector source, or clearly readable values.

Good redraw candidates:
- study-design diagrams;
- cohort flow;
- treatment timelines;
- causal diagrams;
- simple forest plots from supplied estimates;
- simple trajectory schematics;
- tables.

Do not redraw complex publication plots from a low-resolution screenshot if exact values cannot be recovered.
For Academic PPTX, redraw output may be a single generated figure image only when its figure class is allowed by `references/figure-generation-whitelist.md`; quantitative plots must be deterministic from verified values.

### Annotate

Use to direct attention without modifying the evidence.

Preferred annotation styles:
- a thin accent outline around one row or panel;
- a short arrow and 3-8 word label;
- a translucent region highlight;
- a small takeaway line above the figure;
- a single emphasized estimate while all other values remain visible.

### Expand / Zoom

Use for dense evidence that must remain complete.

Recommended sequence:
1. full evidence overview;
2. focused crop or re-render of the relevant panel;
3. interpretation or mechanism slide if needed.

Do not use zooming as a way to hide contradictory or inconvenient results.

## Information classification

Use three tiers.

### Essential

Removing it would change interpretation, credibility, or reproducibility.

Examples:
- n;
- comparison group;
- estimate + uncertainty;
- units;
- model name when multiple models are compared;
- inclusion criteria that explain sample selection;
- definition of a non-standard outcome.

### Supporting

Useful but can be visually secondary.

Examples:
- full covariate list after the model class is established;
- secondary subgroup labels;
- journal and year;
- detailed data-source notes.

### Redundant

Can often be removed.

Examples:
- repeated sentences that restate the chart title;
- decorative boxes with no grouping function;
- duplicate labels already present in a figure;
- repeated institution/date footer on every internal slide unless required.

## Scientific emphasis

Visual emphasis must not imply stronger evidence than the analysis supports.

Avoid:
- giant red numbers for weak or non-significant results;
- hiding intervals while highlighting point estimates;
- using green/red as good/bad when colors merely encode groups;
- fading null or contradictory results until they are effectively invisible.

Prefer language such as:
- "consistent with";
- "suggests";
- "no clear difference";
- "association attenuated after adjustment";
when supported by the source material.
