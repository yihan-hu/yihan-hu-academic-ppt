# Brand Profile Contract

A brand profile is a small, explicit contract between a supplied institutional template and Guizang. It does not define layout.

## Purpose

Use the profile to make branding deterministic. The same profile must drive:

1. the Guizang HTML CSS variables;
2. the Academic PPTX renderer native colors;
3. brand-token validation;
4. logo asset selection.

Do not hand-pick colors again after the profile is approved.

Brand logo assets are also geometry-locked: preserve their intrinsic aspect ratio, use `role: "logo"`, and place them with `fit: "contain"`. A brand profile supplies the artwork; it does not authorize stretching or squeezing it.

## Required fields

```json
{
  "id": "example-brand",
  "name": "Example Institution",
  "source": "user-supplied template.pptx",
  "accent": "840050",
  "accentOn": "FFFFFF",
  "neutralPolicy": "inherit-guizang",
  "logos": {
    "light": "assets/brands/example-logo-white.png",
    "accent": "assets/brands/example-logo-accent.png"
  },
  "approvedSecondary": [],
  "observedSecondary": [],
  "doNotInherit": []
}
```

Colors are six-digit uppercase RGB without `#`.

## Neutral lock

With `neutralPolicy: "inherit-guizang"`, these values are immutable:

- paper `FAFAF8`
- ink `0A0A0A`
- grey1 `F0F0EE`
- grey2 `D4D4D2`
- grey3 `737373`

Institution branding normally replaces only the Guizang accent token and accent-on token. Do not convert paper to pure white or ink to pure black.

## Secondary colors

`observedSecondary` records colors seen in the institutional source but does not authorize their use. `approvedSecondary` is opt-in and should usually remain empty for Guizang Swiss.

If a secondary color is truly required by the user, record a narrow semantic use. Never use a secondary brand color merely to make a slide more colorful.

## Color provenance

Explicit colors in `deck-spec.json` must be one of:

- a Guizang neutral;
- the active profile accent/accentOn;
- an enabled approved secondary with `colorSource: "institution-template"`;
- a scientifically meaningful color with `colorSource: "scientific-data"`.

Any other explicit color is a validation error.

## Template-analysis warning

Do not trust `ppt/theme/theme1.xml` alone. Many real institutional decks keep the default Office theme while applying brand colors directly as `srgbClr` values in slide/master XML or in logo artwork. Run `scripts/inspect-brand-template.py`, inspect repeated explicit colors and repeated logo assets, then create or select the profile.

## Style-aware profiles

A profile should declare `baseStyle` and `templateAsset` when it is tied to a Guizang family.

- `baseStyle: "swiss"`: use the Swiss accent model; `neutralPolicy` is normally `inherit-guizang`.
- `baseStyle: "editorial"`: use the original Style A theme-block model; store exact `themeTokens` for `ink`, `inkRgb`, `paper`, `paperRgb`, `paperTint`, and `inkTint`.

Bundled KI profiles:

- `references/brands/ki-swiss.json`
- `references/brands/ki-editorial.json`
- `references/brands/ki.json` is a backward-compatible alias of `ki-swiss`.

Never infer that an editorial profile should obey Swiss neutral values. Validate it against its own frozen Style A theme block.

## KI Editorial role separation

For `ki-editorial`, keep the original Style-A geometry and dark-field token, but override automatic periodic dark/light cycling. Apply `presentationTokens` by role:

- `themeTokens.ink` (`#4F0433`) = **dark editorial field** and the bounded light-page `semanticBandFill`, not ordinary body ink;
- `presentationTokens.slideTitle` (`#840050`) = default title color on light content slides;
- `presentationTokens.readingInk` (`#111111`) = normal light-page body/explanation/cell text;
- `presentationTokens.semanticLabel / iconStroke / arrowStroke` (`#840050`) = compact semantic cues, not paragraph ink;
- `presentationTokens.mutedInk` (`#6F6B6D`) = metadata/captions;
- `presentationTokens.peerPanelFill` (`#F7F3F5`) = subtle equal-peer panel surface; up to three equal peers may use it without a macro-field;
- `presentationTokens.groupingFill / panelFill` (`#EFE8EB`) = stronger explicit grouping/macro fill, never the default fill for every rectangle;
- `presentationTokens.tableStripeFill` (`#F7F3F5`) = table/body stripe;
- `#D9D9D9` = hairline/separator only, not card fill.

Do not solve purple-text overuse by changing the global Style-A `ink` token to black. That token also controls dark editorial fields and would turn Guizang dark pages into black pages. Do not solve dark-page overuse by deleting dark fields either; instead use semantic dark pages only.
