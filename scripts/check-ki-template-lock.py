#!/usr/bin/env python3
"""Ensure KI derivatives stay Guizang-locked, with only approved token/color-role changes."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def token_value(text, name):
    m = re.search(r'--' + re.escape(name) + r'\s*:\s*([^;]+);', text)
    if not m:
        raise ValueError(f'missing --{name}')
    return m.group(1).strip()

def replace_token(text, name, value):
    pat = re.compile(r'(--' + re.escape(name) + r'\s*:\s*)([^;]+)(;)')
    out, n = pat.subn(lambda m: m.group(1) + value + m.group(3), text, count=1)
    if n != 1:
        raise ValueError(f'missing or duplicate --{name}')
    return out

def compare_swiss(profile):
    parent = (ROOT/'assets/template-swiss.html').read_text(encoding='utf-8')
    child = (ROOT/'assets/template-ki-swiss.html').read_text(encoding='utf-8')
    expected={'accent':'840050','accent-rgb':'132,0,80','accent-on':'FFFFFF','accent-bright':'840050'}
    normalized=child
    for name, exp in expected.items():
        actual=token_value(child,name).replace('#','').upper()
        if actual != exp.replace('#','').upper():
            raise AssertionError(f'ki-swiss --{name} expected {exp} got {token_value(child,name)}')
        normalized=replace_token(normalized,name,token_value(parent,name))
    if normalized != parent:
        raise AssertionError('template-ki-swiss.html contains differences outside approved Swiss theme tokens')
    if profile.get('templateAsset') != 'assets/template-ki-swiss.html':
        raise AssertionError('ki-swiss templateAsset mismatch')

def compare_editorial(profile):
    parent = (ROOT/'assets/template.html').read_text(encoding='utf-8')
    child = (ROOT/'assets/template-ki-editorial.html').read_text(encoding='utf-8')
    t=profile['themeTokens']
    expected={'ink':t['ink'],'ink-rgb':t['inkRgb'],'paper':t['paper'],'paper-rgb':t['paperRgb'],'paper-tint':t['paperTint'],'ink-tint':t['inkTint']}
    normalized=child
    for name, exp in expected.items():
        actual=token_value(child,name).replace('#','').upper()
        if actual != str(exp).replace('#','').upper():
            raise AssertionError(f'ki-editorial --{name} expected {exp} got {token_value(child,name)}')
        normalized=replace_token(normalized,name,token_value(parent,name))
    reading=(profile.get('presentationTokens') or {}).get('readingInk','111111').replace('#','').upper()
    actual_reading=token_value(child,'reading-ink').replace('#','').upper()
    if actual_reading != reading:
        raise AssertionError(f'ki-editorial --reading-ink expected {reading} got {actual_reading}')
    normalized=re.sub(r'^\s*--reading-ink\s*:[^;]+;\n', '', normalized, count=1, flags=re.M)
    normalized=normalized.replace('.slide.light{color:var(--reading-ink);background:var(--paper)}', '.slide.light{color:var(--ink);background:var(--paper)}', 1)
    if normalized != parent:
        raise AssertionError('template-ki-editorial.html contains differences outside approved theme tokens + reading-ink role override')
    if profile.get('templateAsset') != 'assets/template-ki-editorial.html':
        raise AssertionError('ki-editorial templateAsset mismatch')

def main():
    swiss=json.loads((ROOT/'references/brands/ki-swiss.json').read_text(encoding='utf-8'))
    editorial=json.loads((ROOT/'references/brands/ki-editorial.json').read_text(encoding='utf-8'))
    compare_swiss(swiss)
    compare_editorial(editorial)
    print('KI template lock passed: Swiss token-only; Editorial token-only plus one reading-ink color-role override.')
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as e:
        print('ERROR:', e)
        raise SystemExit(1)
