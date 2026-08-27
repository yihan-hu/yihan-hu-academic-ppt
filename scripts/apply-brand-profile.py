#!/usr/bin/env python3
"""Apply a frozen brand profile to the matching Guizang HTML theme tokens only."""

import argparse
import json
import re
from pathlib import Path

SWISS_NEUTRALS = {
    'paper': 'FAFAF8',
    'paper-rgb': '250,250,248',
    'ink': '0A0A0A',
    'ink-rgb': '10,10,10',
    'grey-1': 'F0F0EE',
    'grey-2': 'D4D4D2',
    'grey-3': '737373',
}


def norm(v):
    return str(v or '').replace('#', '').upper()


def rgb_triplet(v):
    v = norm(v)
    if not re.fullmatch(r'[0-9A-F]{6}', v):
        raise ValueError(f'Invalid RGB color: {v}')
    return ','.join(str(int(v[i:i+2], 16)) for i in (0, 2, 4))


def replace_var(html, name, value):
    pat = re.compile(r'(--' + re.escape(name) + r'\s*:\s*)([^;]+)(;)')
    html2, count = pat.subn(lambda m: m.group(1) + value + m.group(3), html, count=1)
    if count != 1:
        raise ValueError(f'Could not find unique --{name} token in HTML')
    return html2


def resolve_profile(raw):
    if '/' in raw or '\\' in raw or raw.lower().endswith('.json'):
        p = Path(raw).resolve()
    else:
        p = Path(__file__).resolve().parents[1] / 'references' / 'brands' / f'{raw}.json'
    if not p.exists():
        raise SystemExit(f'Brand profile not found: {raw}')
    return p, json.loads(p.read_text(encoding='utf-8'))


def detect_style(html):
    if '--accent:' in html and '--grey-1:' in html:
        return 'swiss'
    if '--paper-tint:' in html and '--ink-tint:' in html:
        return 'editorial'
    raise SystemExit('Could not detect Guizang template family from theme tokens.')


def apply_swiss(html, profile):
    if profile.get('neutralPolicy') != 'inherit-guizang':
        raise SystemExit('Swiss brand profile must use neutralPolicy=inherit-guizang.')
    accent = norm(profile.get('accent'))
    accent_on = norm(profile.get('accentOn') or 'FFFFFF')
    if not re.fullmatch(r'[0-9A-F]{6}', accent) or not re.fullmatch(r'[0-9A-F]{6}', accent_on):
        raise SystemExit('Brand profile accent/accentOn must be six-digit RGB values.')
    for key, value in SWISS_NEUTRALS.items():
        html = replace_var(html, key, '#' + value.lower() if key not in {'paper-rgb', 'ink-rgb'} else value)
    html = replace_var(html, 'accent', '#' + accent.lower())
    html = replace_var(html, 'accent-rgb', rgb_triplet(accent))
    html = replace_var(html, 'accent-on', '#' + accent_on.lower())
    if '--accent-bright' in html:
        html = replace_var(html, 'accent-bright', '#' + accent.lower())
    return html


def apply_editorial(html, profile):
    if profile.get('neutralPolicy') != 'style-a-theme-block':
        raise SystemExit('Editorial brand profile must use neutralPolicy=style-a-theme-block.')
    t = profile.get('themeTokens') or {}
    required = ['ink', 'inkRgb', 'paper', 'paperRgb', 'paperTint', 'inkTint']
    missing = [k for k in required if not t.get(k)]
    if missing:
        raise SystemExit('Editorial profile missing themeTokens: ' + ', '.join(missing))
    mapping = {
        'ink': '#' + norm(t['ink']).lower(),
        'ink-rgb': str(t['inkRgb']),
        'paper': '#' + norm(t['paper']).lower(),
        'paper-rgb': str(t['paperRgb']),
        'paper-tint': '#' + norm(t['paperTint']).lower(),
        'ink-tint': '#' + norm(t['inkTint']).lower(),
    }
    for key, value in mapping.items():
        html = replace_var(html, key, value)

    presentation = profile.get('presentationTokens') or {}
    reading = norm(presentation.get('readingInk'))
    if reading:
        if not re.fullmatch(r'[0-9A-F]{6}', reading):
            raise SystemExit('presentationTokens.readingInk must be a six-digit RGB value.')
        reading_line = '    --reading-ink:#' + reading.lower() + ';\n'
        if '--reading-ink:' in html:
            html = replace_var(html, 'reading-ink', '#' + reading.lower())
        else:
            anchor = re.search(r'(^\s*--ink-tint\s*:[^;]+;\n)', html, flags=re.M)
            if not anchor:
                raise SystemExit('Could not insert --reading-ink after --ink-tint.')
            html = html[:anchor.end()] + reading_line + html[anchor.end():]
        old_rule = '.slide.light{color:var(--ink);background:var(--paper)}'
        if old_rule in html:
            html = html.replace(old_rule, '.slide.light{color:var(--reading-ink);background:var(--paper)}', 1)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_html')
    ap.add_argument('brand_profile')
    ap.add_argument('output_html')
    args = ap.parse_args()
    src = Path(args.input_html).resolve()
    out = Path(args.output_html).resolve()
    _, profile = resolve_profile(str(args.brand_profile))
    html = src.read_text(encoding='utf-8')
    detected = detect_style(html)
    declared = profile.get('baseStyle') or 'swiss'
    if detected != declared:
        raise SystemExit(f'Profile baseStyle={declared} does not match input template style={detected}.')
    if detected == 'swiss':
        html = apply_swiss(html, profile)
    else:
        html = apply_editorial(html, profile)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f'Branded Guizang HTML written: {out} profile={profile.get("id")} style={detected}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
