# Academic PPT Architecture

```mermaid
flowchart TD
  User[User academic presentation request] --> Entry[SKILL.md entry rules]
  Entry --> Overlay[references/academic-overlay.md]
  Entry --> Guizang[Inherited Guizang rules and assets]

  Overlay --> Brand[Brand overlays and KI presets]
  Overlay --> Figures[Figure whitelist and render QA]
  Overlay --> Native[PPTX native-first contract]

  Brand --> Outputs[HTML / PPTX / deck-spec outputs]
  Figures --> Outputs
  Native --> Outputs
  Guizang --> Outputs

  Outputs --> QA[Validation scripts and visual QA]
  QA --> Deliverables[Final HTML/PPTX artifacts]
```

## Structure

- `SKILL.md` is the runtime entrypoint. It loads Guizang first, then applies the Academic PPT overlay.
- `references/academic-overlay.md` is the main Academic policy layer for scientific fidelity, PPTX native-first behavior, and figure/table handling.
- `references/figure-generation-whitelist.md`, `references/figure-render-qa.md`, and related figure/table references define when scientific visuals may be rendered as coherent images and how they are verified.
- `references/brand-overlay.md`, `references/brand-profile.md`, `references/ki-templates.md`, and KI-specific references define frozen institutional branding overlays.
- `assets/` contains Guizang and KI templates plus brand assets.
- `scripts/` contains validators, renderers, brand-token checks, and PPTX normalization helpers.

## External boundaries

The skill may use the normal slide-generation, browser-render, filesystem, and PowerPoint/PPTX tooling required by the Guizang workflow. Figure editability remains within the native PowerPoint/deterministic figure workflow; no external decomposition path is part of the runtime.
