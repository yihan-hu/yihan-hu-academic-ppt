# KI Preset Templates

The Academic PPT skill contains two first-class KI presets. Both are derivative Guizang templates, not newly designed KI layouts.

## 1. KI x Swiss

- Preset ID: `ki-swiss`
- Template: `assets/template-ki-swiss.html`
- Parent: `assets/template-swiss.html`
- Layout source: original Guizang Swiss S01-S22 only
- Token change: Guizang `--accent` IKB is replaced by the dominant presentation accent extracted from the supplied Defense deck, `#840050`
- Locked Guizang neutrals: `#FAFAF8`, `#0A0A0A`, `#F0F0EE`, `#D4D4D2`, `#737373`
- Logo: KI white/accent logo on cover, section, or closing pages only unless the user asks otherwise

This preset must read as Guizang Swiss first and KI second. Do not keep IKB as a second slide-level accent.

## 2. KI x Electronic Magazine

- Preset ID: `ki-editorial`
- Template: `assets/template-ki-editorial.html`
- Parent: `assets/template.html`
- Layout source: original Guizang Style A layouts only
- Theme source: Guizang Style A geometry/typography with the supplied Defense deck as the KI color source
- Approved theme block:
  - `--ink: #4F0433` (KI deep purple)
  - `--ink-rgb: 79,4,51`
  - `--paper: #FFFFFF`
  - `--paper-rgb: 255,255,255`
  - `--paper-tint: #EFE8EB`
  - `--ink-tint: #840050`
- Logo: KI white logo on dark editorial fields; KI accent logo on light pages when needed

This is not Swiss recolored into purple. It keeps the original Style A serif-display, editorial chrome, magazine framing, WebGL atmosphere, and layout vocabulary. For KI Academic, the original Style-A automatic dark/light page cycling is **overridden**: dark slides are semantic, not periodic.

### KI Editorial color roles

Keep the original Style-A geometry and typography, but replace automatic Style-A color cycling with the supplied Defense palette. Read `references/ki-editorial-visual-grammar.md` and separate **dark field**, **light-page title**, and **reading ink**:

- deep KI purple `#4F0433` = semantic dark editorial field / dark hero background; on a light slide it may also appear once as a bounded `semantic-band` for a cohort, population, study phase, source, or major takeaway;
- Defense-derived KI magenta `#840050` = default light-page slide-title color and the single compact accent for semantic labels, numbering, monoline icons/arrows and key navigation cues;
- neutral `#111111` = ordinary body copy, explanations and table reading text on light pages; never turn paragraphs magenta;
- neutral grey `#6F6B6D` = secondary text/caption;
- near-white KI pink-grey `#F7F3F5` = subtle equal peer-panel surface and table body stripe;
- very pale KI pink-grey `#EFE8EB` = stronger explicit grouping/header/macro-field fill;
- neutral grey `#D9D9D9` = hairline/separator only, not a broad fill;
- coral `#FD8169` = rare semantic result/risk highlight only.

A light slide may therefore read as **white ground + magenta title/cues + black body + restrained pale grouping**. Three genuinely equal peer groups may each use a `#F7F3F5` peer panel. `#4F0433` on a light slide must be a semantic band, not a decorative block. `#D9D9D9` is a line/separator, not a card fill. **Ordinary rectangles do not receive any fill automatically.**

### Light-page macro-field rule

Do not equate “restrained fill” with “mostly empty white,” but also do not overcorrect into every page having a pale field. On sparse light pages, follow `references/ki-editorial-macro-fields.md`: create visual mass with oversized type, a central figure/table ground, three subtle equal peer panels when the content is truly parallel, or **one selective** continuous macro-field. Use `#EFE8EB` as a minority rhythm for stronger grouping, not as a required default fill and not as repeated small decorative header bands.

### Cover rule

Default to a semantic dark cover or light cover. For KI, a dark cover uses **one full deep-purple field** (`#4F0433`) with light text; a light hero uses white `#FFFFFF`. Do not add a second full-height KI-magenta sidebar/slab. Do not use black as the default KI Editorial hero field. Normal methods/results/appendix content pages default to light pages; use dark only for cover, section/transition, synthesis/conclusion, or closing.

### Logo cadence and geometry

Use the KI logo on cover / closing and, when useful, rare section dividers. Do not repeat the logo on every normal content slide.

For PPTX, every KI logo image must use `role: "logo"` and `fit: "contain"`. The supplied logo asset ratio is authoritative: treat x/y/w/h as a maximum slot, never stretch the bitmap to the slot. Do not squeeze the logo to make it fit beside page numbers or titles; move/resize the slot while preserving aspect ratio.
The logo artwork keeps its intrinsic supplied brand color; do not recolor the bitmap merely to force an exact match with the `#840050` presentation accent token.

### Native table rule

When a `KI x Electronic Magazine` slide contains a native editable scientific table, also read `references/ki-editorial-tables.md`. Keep it as a real table, but default to the Defense-derived filled editorial banding: very pale pink-grey header, then body rows alternating **white first** and near-white pink-grey. Do not default to a publication three-line table or a line-only table. Keep effect estimate + CI in one cell and emphasize important results with same-size bold, never enlargement.

## Selection rule

When the user asks for a KI deck and does not specify a Guizang family, ask them to choose one of:

- `KI x Swiss`
- `KI x Electronic Magazine`

If the current conversation already makes the choice explicit, do not ask again.

## Hard inheritance rule

The two KI template assets must remain Guizang-locked. KI Swiss normalizes only approved theme-token values; KI Editorial additionally normalizes the single approved `reading-ink` light-page color-role override. Do not add CSS that forces periodic dark slides for KI Academic; dark-page cadence is controlled by deck semantics and QA. Run:

```bash
python <SKILL_ROOT>/scripts/check-ki-template-lock.py
```

Any other difference is a regression. `template-ki-editorial.html` has one additionally whitelisted color-role override: `--reading-ink:#111111` and the light-slide text-color binding to that token. Do not add new cards, geometry, font rules, spacing, shadows, or layout CSS to the KI template files.

## PPTX rule

For Academic PPTX output, keep `meta.designSource: "guizang-template"`, `meta.figurePolicy: "whitelist-enforced"`, and use the selected Guizang layout geometry. Keep ordinary slide text, tables, panels, hairlines and ordinary layout native. For scientific figures, follow `references/figure-generation-whitelist.md`: forest/effect plots and clearly illustrative methods/study-design/conceptual/state/cohort figures **must be one coherent generated/preserved picture by default**; native reconstruction is allowed only when the user explicitly requests full editability. Browser raster layers remain limited to genuine browser-only effects. Do not rasterize ordinary titles/body/chrome.
