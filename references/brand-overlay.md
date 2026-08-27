# Institutional Brand Overlay

Use this when the user supplies an institutional/brand template or explicitly selects a bundled brand profile.

The institutional source is a **brand source**, not a second layout source. Guizang remains the design source of truth.

## Ownership

**Guizang owns**
- the selected parent family: Style A Electronic Magazine or Style B Swiss;
- the parent layout geometry and registered layout vocabulary;
- grid, spacing, whitespace, asymmetry, typography hierarchy, chrome and motion;
- the theme-token architecture of the selected family;
- HTML visual-plate geometry.

**Institution template owns**
- official logo assets and variants;
- supported brand colors that are frozen into a profile;
- institution/department naming;
- narrowly approved secondary colors only when truly required.

**Scientific source owns**
- data colors inside figures;
- quantitative values and uncertainty;
- scientific terminology and labels.

## P0 brand workflow

### 1. Analyze the supplied template

```bash
python <SKILL_ROOT>/scripts/inspect-brand-template.py source-template.pptx brand-analysis.json
```

Do not trust `ppt/theme/theme1.xml` alone. Many institutional decks keep a default Office theme and apply brand colors directly in slide/master XML or logo artwork.

### 2. Freeze a style-aware profile

Read `references/brand-profile.md`. The same profile must drive HTML, PPTX native elements, logo selection and QA. Do not hand-pick colors after the profile is frozen.

### 3. Apply the profile mechanically

```bash
python <SKILL_ROOT>/scripts/apply-brand-profile.py index.guizang.html <profile-id-or-json> index.html
```

The script detects the Guizang family and refuses a profile/template mismatch.

- Swiss: preserve the Guizang neutral system and replace only the accent family.
- Electronic Magazine: replace only the original six-variable Style A theme block (`ink`, `ink-rgb`, `paper`, `paper-rgb`, `paper-tint`, `ink-tint`).

Do not recolor individual components.

### 4. Use the same profile in deck-spec

```json
{
  "meta": {
    "designSource": "guizang-template",
    "pptxFidelity": "native-first",
    "brandProfile": "ki-swiss"
  }
}
```

For Style A use the matching editorial profile, e.g. `ki-editorial`. Do not independently restyle the PPTX renderer.

### 5. Validate token lock

```bash
python <SKILL_ROOT>/scripts/check-brand-token-lock.py deck-spec.json
```

## Swiss token model

With `baseStyle: "swiss"` and `neutralPolicy: "inherit-guizang"`, keep:

- paper `#FAFAF8`
- ink `#0A0A0A`
- grey-1 `#F0F0EE`
- grey-2 `#D4D4D2`
- grey-3 `#737373`

The institutional primary replaces Guizang `--accent`; it does not sit next to the old accent.

Correct: `Guizang IKB -> institution accent`

Wrong: `Guizang IKB + institution accent + another highlight color`

## Electronic Magazine token model

Style A does not use the Swiss accent/grey system. It is themed through its original ink/paper block. A branded Style A preset may replace that block **as one atomic theme operation** while keeping every other geometry/layout rule unchanged.

Do not apply the Swiss neutral lock to Style A. Doing so destroys the original Editorial theme system. For KI Editorial specifically, `themeTokens.ink` remains the deep-purple dark field, while `presentationTokens.readingInk` supplies neutral reading text on light pages. Do not turn the global `ink` token black to fix light-page text.

On light KI Editorial pages, use the pale panel fill only for explicit grouping panels. A generic rectangle is not automatically a panel.
If a light page has large unanchored white space, do not respond with many small panels. First try Guizang-style visual mass through large type or a figure/table ground; use a pale macro-field selectively, not by default. For three comparable peers, if a pale field is needed, the default field is the middle peer, not the rightmost peer; side macro-fields require a declared source/story semantic split. See `references/ki-editorial-macro-fields.md`.

## Color provenance

Explicit deck-spec colors must be one of:

- tokens from the active profile;
- enabled `approvedSecondary` with `colorSource: "institution-template"`;
- scientifically meaningful colors with `colorSource: "scientific-data"`.

If a color has no provenance, remove it rather than inventing a justification.

## Logo rule

- Cover / section / closing may use the logo clearly.
- Normal methods/results slides usually express brand identity through the active theme and chrome, not a repeated large logo.
- Keep official logo proportions and transparency.
- Do not squeeze parent layout geometry to make room for a logo.
- Use white logo on dark/accent fields and accent logo on light fields when contrast is sufficient.

## What not to inherit by default

Unless the user explicitly asks to preserve institutional layout, do not inherit:

- title coordinates;
- Study I/II/III/IV navigation;
- default PowerPoint fonts;
- source table/card geometry;
- rounded boxes/dashboard UI;
- source footer/date/page chrome;
- source whitespace/typographic scale.

## KI bundled presets

Read `references/ki-templates.md`.

- `ki-swiss`: exact Guizang Swiss derivative with IKB replaced by KI `#840050`; all Guizang Swiss neutrals remain unchanged.
- `ki-editorial`: Guizang Style A geometry/typography with the supplied Defense deck as the color source. Use white light pages, `#4F0433` semantic dark editorial fields, neutral `#111111` reading text, and `#840050` as the selective presentation accent; `#EFE8EB / #F7F3F5` provide restrained panel/table fills, `#D9D9D9` is hairline-only, and dark pages are semantic rather than periodic.
- `ki` remains a backward-compatible alias of `ki-swiss`.

Run:

```bash
python <SKILL_ROOT>/scripts/check-ki-template-lock.py
```

Any difference outside the approved theme tokens and the single whitelisted KI Editorial `reading-ink` color-role override is a regression.

## Acceptance criterion

Compare the branded result against the original Guizang parent first and the institution source second.

**First impression: Guizang -> second impression: institution identity.**
