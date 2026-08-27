#!/usr/bin/env python3
"""Validate frozen Guizang brand tokens and reject unauthorized slide-level colors."""

import argparse
import json
import re
from pathlib import Path

SWISS_NEUTRALS = {'FAFAF8', '0A0A0A', 'F0F0EE', 'D4D4D2', '737373', 'FFFFFF'}
GUIZANG_PRESETS = {'002FA7', 'FFD500', 'C5E803', 'FF6B35'}
COLOR_KEYS = {'color', 'fill', 'line', 'lineColor', 'borderColor', 'headerFill', 'backgroundColor'}


def norm(v):
    if not isinstance(v, str):
        return None
    v = v.replace('#', '').upper()
    return v if re.fullmatch(r'[0-9A-F]{6}', v) else None


def walk_colors(node, inherited_source=None, path='root'):
    found = []
    if isinstance(node, dict):
        source = node.get('colorSource', inherited_source)
        for k, v in node.items():
            if k in COLOR_KEYS:
                if isinstance(v, str):
                    c = norm(v)
                    if c:
                        found.append((path + '.' + k, c, source))
                elif isinstance(v, dict):
                    c = norm(v.get('color'))
                    if c:
                        found.append((path + '.' + k + '.color', c, v.get('colorSource', source)))
            if k not in COLOR_KEYS:
                found.extend(walk_colors(v, source, path + '.' + str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found.extend(walk_colors(v, inherited_source, f'{path}[{i}]'))
    return found


def resolve_profile(spec_path, meta):
    raw = meta.get('brandProfile')
    if not raw:
        return None, None
    value = str(raw)
    if '/' in value or '\\' in value or value.lower().endswith('.json'):
        p = Path(value)
        p = p if p.is_absolute() else (spec_path.parent / p)
    else:
        root = Path(__file__).resolve().parents[1]
        p = root / 'references' / 'brands' / f'{value}.json'
    if not p.exists():
        raise FileNotFoundError(f'brandProfile not found: {raw}')
    return p, json.loads(p.read_text(encoding='utf-8'))


def validate_swiss(meta, profile, colors, errors):
    if profile.get('neutralPolicy') != 'inherit-guizang':
        errors.append('Swiss brand profile must use neutralPolicy=inherit-guizang')
    accent = norm(profile.get('accent'))
    accent_on = norm(profile.get('accentOn') or 'FFFFFF')
    if norm(meta.get('accentColor') or accent) != accent:
        errors.append(f'meta.accentColor must equal brand profile accent {accent}')
    expected = {
        'backgroundColor': 'FAFAF8', 'inkColor': '0A0A0A', 'grey1': 'F0F0EE',
        'grey2': 'D4D4D2', 'grey3': '737373'
    }
    for key, value in expected.items():
        actual = norm(meta.get(key) or value)
        if actual != value:
            errors.append(f'meta.{key} must remain Guizang neutral {value}; got {actual}')
    approved = {norm(x.get('color')) for x in (profile.get('approvedSecondary') or []) if norm(x.get('color'))}
    allowed = SWISS_NEUTRALS | {accent, accent_on}
    for pth, color, source in colors:
        if color in allowed or source == 'scientific-data':
            continue
        if source == 'institution-template' and color in approved:
            continue
        errors.append(f'unauthorized explicit color {color} at {pth}')
    if accent != '002FA7':
        for pth, color, source in colors:
            if color == '002FA7' and source != 'scientific-data':
                errors.append(f'residual IKB color at {pth} while brand accent is {accent}')
    return accent


def validate_editorial(meta, profile, colors, errors):
    if profile.get('neutralPolicy') != 'style-a-theme-block':
        errors.append('Editorial brand profile must use neutralPolicy=style-a-theme-block')
    t = profile.get('themeTokens') or {}
    p = profile.get('presentationTokens') or {}
    expected_tokens = {
        'backgroundColor': norm(t.get('paper')),
        'paperTint': norm(t.get('paperTint')),
        'inkTint': norm(t.get('inkTint')),
        'inkColor': norm(p.get('readingInk') or t.get('ink')),
    }
    for key, value in expected_tokens.items():
        if not value:
            errors.append(f'Editorial profile missing token for {key}')
            continue
        if key in meta and norm(meta.get(key)) != value:
            errors.append(f'meta.{key} must match editorial profile role {value}; got {norm(meta.get(key))}')
    accent = norm(profile.get('accent') or t.get('inkTint'))
    accent_on = norm(profile.get('accentOn') or 'FFFFFF')
    approved = {norm(x.get('color')) for x in (profile.get('approvedSecondary') or []) if norm(x.get('color'))}
    table_tokens = profile.get('tableTokens') or {}
    presentation_tokens = profile.get('presentationTokens') or {}
    allowed = {norm(v) for v in [t.get('ink'), t.get('paper'), t.get('paperTint'), t.get('inkTint'), accent, accent_on, 'FFFFFF', *table_tokens.values(), *presentation_tokens.values()] if norm(v)}
    for pth, color, source in colors:
        if color in allowed or source == 'scientific-data':
            continue
        if source == 'institution-template' and color in approved:
            continue
        errors.append(f'unauthorized explicit color {color} at {pth} for editorial brand profile')
    if profile.get('id') == 'ki-editorial':
        legacy = {'870052','F1F3F5','E4E8EC','E6DDE2','F3E8EE','FAF5F8','F5EEF2','DDD0D5','8F587B'}
        for pth, color, source in colors:
            if color in legacy and source != 'scientific-data':
                errors.append(f'legacy KI-editorial color {color} at {pth}; use the Defense-derived frozen palette')
    return accent



def validate_ki_editorial_usage(spec, profile, errors):
    if profile.get('id') != 'ki-editorial':
        return
    t = profile.get('themeTokens') or {}
    p = profile.get('presentationTokens') or {}
    accent = norm(profile.get('accent') or t.get('inkTint')) or '840050'
    dark_field = norm(t.get('ink')) or '4F0433'
    paper = norm(t.get('paper')) or 'FFFFFF'
    reading = norm(p.get('readingInk')) or '111111'
    title_color = norm(p.get('slideTitle')) or accent
    semantic_label = norm(p.get('semanticLabel')) or accent
    peer_panel = norm(p.get('peerPanelFill')) or 'F7F3F5'
    grouping_fill = norm(p.get('groupingFill') or p.get('panelFill')) or 'EFE8EB'
    panel = norm(p.get('panelFill')) or grouping_fill
    semantic_band = norm(p.get('semanticBandFill')) or dark_field
    semantic_band_on = norm(p.get('semanticBandOn')) or paper
    max_semantic_bands = int(p.get('semanticBandMaxPerLightSlide') or 1)
    max_semantic_band_coverage = float(p.get('semanticBandCoverageMax') or 0.18)
    max_peer_panels_without_macro = int(p.get('maxSmallPeerPanelsWithoutMacroField') or 3)
    allowed_logo_kinds = {'cover', 'closing', 'section'}
    semantic_dark_kinds = set((p.get('semanticDarkKinds') or ['cover','section','transition','synthesis','conclusion','closing']))
    dark_count = 0
    slides = spec.get('slides') or []

    for si, slide in enumerate(slides, start=1):
        kind = str(slide.get('kind') or '').lower()
        tone = str(slide.get('tone') or '').lower()
        bg = norm(slide.get('backgroundColor'))
        is_dark = tone == 'dark' or bg == dark_field
        if tone == 'dark' and bg and bg != dark_field:
            errors.append(f'Slide {si}: KI editorial dark tone must use deep-purple field {dark_field}; got {bg}')
        if bg in {'000000', '111111'} and kind in {'cover', 'section', 'closing'}:
            errors.append(f'Slide {si}: KI editorial hero/section background may not default to black/reading-ink {bg}; use deep-purple field {dark_field} or light paper')
        if is_dark:
            dark_count += 1
            if kind not in semantic_dark_kinds and not slide.get('allowDarkContent'):
                errors.append(f'Slide {si}: KI editorial dark page is semantic-only; kind={kind!r} is not allowed to inherit periodic Style-A dark rhythm')
            if slide.get('allowDarkContent') and not str(slide.get('darkReason') or '').strip():
                errors.append(f'Slide {si}: allowDarkContent requires a non-empty darkReason')

        accent_nonsemantic_text = 0
        macro_fields = []
        small_panels = []
        peer_panels = []
        semantic_bands = []
        peer_groups = 0
        has_central_table_or_figure = False
        for el0 in (slide.get('elements') or []):
            if not isinstance(el0, dict):
                continue
            if el0.get('type') == 'table' or el0.get('role') in {'generated-figure','figure'} or el0.get('figureKind'):
                try:
                    w0 = float(el0.get('w', 0)); h0 = float(el0.get('h', 0))
                    if w0 * h0 >= 18:
                        has_central_table_or_figure = True
                except Exception:
                    has_central_table_or_figure = True
            if el0.get('role') in {'peer-group','design-group'}:
                peer_groups += 1
        for ei, el in enumerate(slide.get('elements') or [], start=1):
            if not isinstance(el, dict):
                continue
            typ = el.get('type')
            if typ == 'text':
                c = norm(el.get('color'))
                role = str(el.get('role') or 'body')
                if tone != 'dark' and role == 'title' and c and c != title_color:
                    errors.append(f'Slide {si} element {ei}: KI editorial light-page title must use slideTitle {title_color}; got {c}')
                if tone != 'dark' and role in {'body', 'annotation'} and c == accent:
                    errors.append(f'Slide {si} element {ei}: KI magenta {accent} may not be ordinary {role} text; use readingInk {reading}')
                if c == accent and role not in {'title','semantic-label','statistic','navigation'}:
                    accent_nonsemantic_text += 1
                if c == dark_field and tone != 'dark' and role in {'body', 'title', 'hero', 'section', 'annotation'}:
                    errors.append(f'Slide {si} element {ei}: deep-purple dark-field token {dark_field} used as ordinary light-page text; use readingInk {reading}')
                if role == 'semantic-label' and c and c != semantic_label and tone != 'dark':
                    errors.append(f'Slide {si} element {ei}: semantic-label should use {semantic_label}; got {c}')
                if role == 'semantic-band-text' and c and c != semantic_band_on and tone != 'dark':
                    errors.append(f'Slide {si} element {ei}: semantic-band-text must use semanticBandOn {semantic_band_on}; got {c}')
            elif typ == 'shape':
                shape = str(el.get('shape') or 'rect')
                fill = norm(el.get('fill'))
                role = str(el.get('role') or '')
                if role == 'macro-field':
                    try:
                        x, y, w, h = [float(el.get(k, 0)) for k in ('x','y','w','h')]
                        macro_fields.append((x, y, w, h, fill))
                        if w * h < 12.0:
                            errors.append(f'Slide {si} element {ei}: macro-field is too small to act as Guizang visual mass; enlarge it or use role=panel')
                    except Exception:
                        macro_fields.append((0,0,0,0,fill))
                if role == 'panel':
                    try:
                        x, y, w, h = [float(el.get(k, 0)) for k in ('x','y','w','h')]
                        if fill == panel and w * h < 8.0:
                            small_panels.append((x, y, w, h))
                    except Exception:
                        pass
                    if fill and fill != grouping_fill:
                        errors.append(f'Slide {si} element {ei}: grouping panel must use groupingFill {grouping_fill}; got {fill}')
                if role == 'peer-panel':
                    try:
                        x, y, w, h = [float(el.get(k, 0)) for k in ('x','y','w','h')]
                        peer_panels.append((x, y, w, h, fill))
                    except Exception:
                        peer_panels.append((0,0,0,0,fill))
                    if fill and fill != peer_panel:
                        errors.append(f'Slide {si} element {ei}: peer-panel must use peerPanelFill {peer_panel}; got {fill}')
                if role == 'semantic-band':
                    try:
                        x, y, w, h = [float(el.get(k, 0)) for k in ('x','y','w','h')]
                        semantic_bands.append((x, y, w, h, fill))
                        coverage = (w * h) / (13.333333 * 7.5)
                        if coverage > max_semantic_band_coverage + 1e-9:
                            errors.append(f'Slide {si} element {ei}: semantic-band covers {coverage:.1%}; limit is {max_semantic_band_coverage:.0%} on a light slide')
                    except Exception:
                        semantic_bands.append((0,0,0,0,fill))
                    if tone == 'dark':
                        errors.append(f'Slide {si} element {ei}: semantic-band is a light-page treatment; use the normal dark field on dark slides')
                    if fill and fill != semantic_band:
                        errors.append(f'Slide {si} element {ei}: semantic-band must use semanticBandFill {semantic_band}; got {fill}')
                if tone != 'dark' and fill == dark_field and role != 'semantic-band' and el.get('colorSource') != 'scientific-data':
                    errors.append(f'Slide {si} element {ei}: deep-plum {dark_field} on a light slide requires role=semantic-band')
                if role in {'panel','peer-panel'} and fill in {paper, 'FFFFFF'}:
                    expected = peer_panel if role == 'peer-panel' else grouping_fill
                    errors.append(f'Slide {si} element {ei}: explicit {role} fill matches the light page; use {expected} or omit fill so the renderer applies its role token')
                if kind == 'cover' and shape == 'rect' and fill == accent:
                    try:
                        x, y, w, h = [float(el.get(k, 0)) for k in ('x','y','w','h')]
                        if h >= 6.0 and 1.3 <= w <= 5.5:
                            errors.append(f'Slide {si}: KI editorial cover contains a full-height magenta sidebar/slab; remove it')
                    except Exception:
                        pass
            elif typ == 'image':
                path = str(el.get('path') or '').lower()
                if 'ki-logo' in path and kind not in allowed_logo_kinds and not slide.get('allowLogo'):
                    errors.append(f'Slide {si}: KI logo repeated on ordinary content slide; reserve logo for cover/closing/rare section pages')
        if accent_nonsemantic_text > 2 and not slide.get('allowAccentTextHeavy'):
            errors.append(f'Slide {si}: {accent_nonsemantic_text} non-semantic text elements use KI magenta; reserve accent for title/semantic labels/navigation, not body ink')
        if tone != 'dark' and len(semantic_bands) > max_semantic_bands:
            errors.append(f'Slide {si}: {len(semantic_bands)} semantic bands exceed the light-page limit of {max_semantic_bands}')
        if tone != 'dark' and len(peer_panels) > max_peer_panels_without_macro and not macro_fields:
            errors.append(f'Slide {si}: {len(peer_panels)} peer panels exceed the no-macro-field limit of {max_peer_panels_without_macro}')
        if tone != 'dark' and kind not in {'cover','section','closing','appendix'}:
            lt = str(slide.get('layoutTreatment') or '')
            # Macro-fields are optional.  Do not require fill simply because a slide has
            # several peer groups; require an anchor only when the author explicitly marks the
            # page as unanchored/sparse.  This prevents overcorrection into a pale-filled deck.
            if slide.get('needsVisualAnchor') and not macro_fields and lt not in {'big-type-anchor','large-figure','central-table'} and not has_central_table_or_figure:
                errors.append(f'Slide {si}: needsVisualAnchor=true but the light page has no macro-field/big-type/figure/table anchor; use references/ki-editorial-macro-fields.md')
            if peer_groups >= 3 and macro_fields:
                placement = str(slide.get('macroFieldPlacement') or '').lower()
                # A three-peer overview should not color the rightmost/leftmost peer by default;
                # that reads as an unintended emphasis.  Use a middle field unless the slide
                # explicitly declares a semantic side split.
                for (x, y, w, h, fill) in macro_fields:
                    center_x = x + w / 2
                    if placement not in {'middle','center','centre','right','left'}:
                        errors.append(f'Slide {si}: three-peer macro-field requires macroFieldPlacement; default should be "middle"')
                    if center_x > 8.0 and not slide.get('asymmetricSemanticSplit'):
                        errors.append(f'Slide {si}: right-side macro-field on a three-peer overview implies unintended emphasis; use macroFieldPlacement="middle" or set asymmetricSemanticSplit=true with a reason')
                    if center_x < 5.3 and center_x > 0 and placement in {'right','left'} and not slide.get('asymmetricSemanticSplit'):
                        # left side fields are also semantic, but allow very wide figure/table grounds by area exceptions elsewhere
                        errors.append(f'Slide {si}: side macro-field on a three-peer overview requires asymmetricSemanticSplit=true')
            if slide.get('asymmetricSemanticSplit'):
                reason = str(slide.get('semanticSplitReason') or '').strip()
                if not reason:
                    errors.append(f'Slide {si}: asymmetricSemanticSplit requires semanticSplitReason')
                elif not reason.lower().startswith(('source:', 'story:', 'user:')):
                    errors.append(f'Slide {si}: semanticSplitReason must start with source:, story:, or user: so side macro-fields cannot be self-approved without provenance')
            if len(macro_fields) > 2 and not slide.get('allowMultipleMacroFields'):
                errors.append(f'Slide {si}: too many macro-fields ({len(macro_fields)}); use one dominant field rather than many filled regions')

    dark_limit = max(2, int((len(slides) * float(p.get('maxDarkSlideRatio') or 0.20)) + 0.999))
    if dark_count > dark_limit and not spec.get('meta', {}).get('allowMoreDarkSlides'):
        errors.append(f'KI editorial uses {dark_count}/{len(slides)} dark pages; limit is {dark_limit}. Use dark fields semantically, not as periodic Style-A cycling.')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck_spec')
    args = ap.parse_args()
    spec_path = Path(args.deck_spec).resolve()
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    meta = spec.get('meta') or {}
    errors = []
    _, profile = resolve_profile(spec_path, meta)
    colors = walk_colors(spec.get('slides') or [], path='slides')
    if profile is not None:
        style = profile.get('baseStyle') or 'swiss'
        if meta.get('designSource') != 'guizang-template':
            errors.append('meta.designSource must be guizang-template in brand mode')
        if style == 'swiss':
            accent = validate_swiss(meta, profile, colors, errors)
        elif style == 'editorial':
            accent = validate_editorial(meta, profile, colors, errors)
            validate_ki_editorial_usage(spec, profile, errors)
        else:
            errors.append(f'unsupported profile baseStyle: {style}')
            accent = norm(profile.get('accent'))
    else:
        accent = norm(meta.get('accentColor') or '002FA7')
        if accent not in GUIZANG_PRESETS:
            errors.append(f'non-brand Swiss deck accent {accent} is not an original Guizang preset')
        style = 'swiss'
    if errors:
        for e in errors:
            print('ERROR:', e)
        return 1
    profile_id = profile.get('id') if profile else 'none'
    print(f'Brand token lock passed: profile={profile_id} style={style} accent={accent}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
