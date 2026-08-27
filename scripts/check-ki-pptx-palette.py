#!/usr/bin/env python3
"""Final PPTX palette and fill-budget audit for bundled KI presets.

The audit is intentionally pragmatic:
- PPTX XML is checked for forbidden legacy tokens and unexpected explicit colors.
- Rendered slide images, when provided, are checked for excessive pale KI fill and
  unexpected saturated raster colors. This catches generated figures and macro-fields,
  not just native PowerPoint shapes.
"""
from __future__ import annotations

import argparse
import collections
import colorsys
import math
import re
import sys
import zipfile
from pathlib import Path

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

LEGACY_EDITORIAL = {
    '870052': 'old assumed KI accent',
    'F1F3F5': 'old Indigo-Porcelain paper',
    'E4E8EC': 'old Indigo-Porcelain paper tint',
    'E6DDE2': 'legacy pink grid',
    'F3E8EE': 'legacy pink header fill',
    'FAF5F8': 'legacy pink stripe fill',
    'F5EEF2': 'legacy pink panel fill',
    'DDD0D5': 'over-heavy plum-grey fill from rejected palette iteration',
    '8F587B': 'dusty mauve used as default secondary text in rejected palette iteration',
}

EXPECTED_EDITORIAL = {
    'FFFFFF', '4F0433', '111111', '840050', '6F6B6D', 'EFE8EB', 'F7F3F5',
    'D9D9D9', 'FD8169', '000000'
}
PALE_EDITORIAL = {'EFE8EB', 'F7F3F5'}
PPTX_XML_COLOR_RE = re.compile(r'<a:srgbClr\s+val="([0-9A-Fa-f]{6})"')
SLIDE_RE = re.compile(r'ppt/slides/slide(\d+)\.xml')


def rgb(hex_color: str):
    hex_color = hex_color.replace('#', '').upper()
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def dist(a, b):
    return math.sqrt(sum((int(x) - int(y)) ** 2 for x, y in zip(a, b)))


EXPECTED_RGB = [rgb(c) for c in EXPECTED_EDITORIAL]
PALE_RGB = [rgb(c) for c in PALE_EDITORIAL]


def is_neutral_gray_hex(c: str) -> bool:
    r, g, b = rgb(c)
    return max(r, g, b) - min(r, g, b) <= 5


def is_near_expected_hex(c: str) -> bool:
    rc = rgb(c)
    return any(dist(rc, x) <= 10 for x in EXPECTED_RGB)


def count_slide_colors(path: Path):
    counter = collections.Counter()
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not SLIDE_RE.fullmatch(name):
                continue
            xml = zf.read(name).decode('utf-8', errors='ignore')
            for color in PPTX_XML_COLOR_RE.findall(xml):
                counter[color.upper()] += 1
    return counter


def slide_backgrounds(path: Path):
    bgs = []
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(
            [n for n in zf.namelist() if SLIDE_RE.fullmatch(n)],
            key=lambda n: int(SLIDE_RE.fullmatch(n).group(1))
        )
        for name in slide_names:
            xml = zf.read(name).decode('utf-8', errors='ignore')
            m = re.search(r'<p:bg>.*?<a:srgbClr\s+val="([0-9A-Fa-f]{6})"', xml, flags=re.S)
            bgs.append(m.group(1).upper() if m else None)
    return bgs


def slide_count(path: Path) -> int:
    with zipfile.ZipFile(path) as zf:
        return sum(1 for n in zf.namelist() if SLIDE_RE.fullmatch(n))


def find_rendered_slides(render_dir: Path):
    if not render_dir or not render_dir.exists():
        return []
    files = []
    for p in render_dir.iterdir():
        if p.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
            continue
        m = re.search(r'(?:slide[-_ ]?|page[-_ ]?)(\d+)', p.stem, flags=re.I)
        if m:
            files.append((int(m.group(1)), p))
    return [p for _, p in sorted(files)]


def pixel_allowed(r, g, b):
    # Very wide tolerance for antialiasing and office renderer variation.
    if max(r, g, b) - min(r, g, b) <= 35:
        return True  # neutral grey/black/white
    if any(dist((r, g, b), x) <= 55 for x in EXPECTED_RGB):
        return True
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    hue = h * 360
    # KI plum/magenta family, including antialiased variants of 4F0433/840050.
    if (295 <= hue <= 340 or hue >= 345) and s >= 0.20:
        return True
    # Coral semantic result highlight family.
    if 5 <= hue <= 24 and s >= 0.35 and r > g and r > b:
        return True
    return False


def audit_rendered_palette(render_dir: Path, total_slides: int):
    if Image is None:
        return [f'Pillow is unavailable; cannot run raster palette/pale-fill audit for {render_dir}'], []
    errors = []
    stats = []
    slide_paths = find_rendered_slides(render_dir)
    if not slide_paths:
        return [f'no rendered slide images found in {render_dir}'], []
    high_pale = []
    for idx, path in enumerate(slide_paths, start=1):
        im = Image.open(path).convert('RGB')
        if im.width > 900:
            ratio = 900 / im.width
            im = im.resize((900, max(1, int(im.height * ratio))))
        pix = list(im.getdata())
        n = len(pix)
        pale = 0
        unexpected = 0
        sampled = 0
        for (r, g, b) in pix:
            # Skip nearly white paper for unexpected-color calculation.
            if dist((r, g, b), rgb('FFFFFF')) <= 18:
                continue
            sampled += 1
            if any(dist((r, g, b), x) <= 28 for x in PALE_RGB):
                pale += 1
            if not pixel_allowed(r, g, b):
                # Count only saturated-ish off-palette colors.
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                if s > 0.22 and v > 0.20:
                    unexpected += 1
        pale_ratio = pale / n
        unexpected_ratio = unexpected / max(1, sampled)
        stats.append((idx, pale_ratio, unexpected_ratio))
        if pale_ratio > 0.15:
            high_pale.append((idx, pale_ratio))
        if pale_ratio > 0.32:
            errors.append(f'slide {idx}: pale KI fill covers {pale_ratio:.1%} of rendered slide; limit is 32%. Use less macro-field or larger typography/figure/table instead.')
        if unexpected_ratio > 0.030:
            errors.append(f'slide {idx}: {unexpected_ratio:.1%} of non-paper pixels are saturated off-palette colors in rendered output; raster figures must follow KI palette.')
    deck_limit = max(3, math.ceil((total_slides or len(slide_paths)) * 0.35))
    if len(high_pale) > deck_limit:
        detail = ', '.join(f'{i}:{r:.0%}' for i, r in high_pale[:10])
        errors.append(f'pale KI fill is overused on {len(high_pale)}/{total_slides or len(slide_paths)} slides (limit {deck_limit}; high slides {detail}). Macro-fields should be a minority rhythm, not the deck default.')
    return errors, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx', type=Path)
    ap.add_argument('--profile', default='ki-editorial', choices=['ki-editorial', 'ki-swiss'])
    ap.add_argument('--render-dir', type=Path, default=None, help='Optional directory with rendered slide PNGs for raster/pale-fill area audit')
    args = ap.parse_args()
    path = args.pptx.resolve()
    if not path.exists():
        print(f'ERROR: not found: {path}', file=sys.stderr)
        return 2
    colors = count_slide_colors(path)
    if args.profile == 'ki-editorial':
        bad = [(c, colors[c], why) for c, why in LEGACY_EDITORIAL.items() if colors[c] > 0]
        if bad:
            for c, n, why in bad:
                print(f'ERROR: legacy KI-editorial color {c} appears {n} time(s): {why}', file=sys.stderr)
            return 1
        unexpected = []
        for c, n in colors.items():
            if c in EXPECTED_EDITORIAL or is_neutral_gray_hex(c) or is_near_expected_hex(c):
                continue
            unexpected.append((c, n))
        if unexpected:
            for c, n in sorted(unexpected, key=lambda x: (-x[1], x[0]))[:20]:
                print(f'ERROR: unexpected KI-editorial explicit XML color {c} appears {n} time(s); add it to the profile with provenance or map it to an approved token.', file=sys.stderr)
            return 1
        bgs = slide_backgrounds(path)
        dark_count = sum(1 for c in bgs if c == '4F0433')
        dark_limit = max(2, int((len(bgs) * 0.20) + 0.999))
        if dark_count > dark_limit:
            print(f'ERROR: KI-editorial dark field appears as slide background {dark_count}/{len(bgs)} time(s); limit is {dark_limit}. Use dark pages semantically, not periodic Style-A cycling.', file=sys.stderr)
            return 1
        if args.render_dir:
            render_errors, stats = audit_rendered_palette(args.render_dir, len(bgs))
            if render_errors:
                for e in render_errors:
                    print('ERROR:', e, file=sys.stderr)
                return 1
            if stats:
                high = ', '.join(f'{i}:{p:.0%}' for i, p, _ in stats if p > 0.10)
                if high:
                    print(f'Rendered pale-fill ratios >10%: {high}')
        print('KI Editorial final palette audit passed.')
        print('Most used slide XML colors:', ', '.join(f'{c}:{n}' for c, n in colors.most_common(12)))
        return 0
    if colors['002FA7'] > 0:
        print(f'ERROR: residual IKB 002FA7 appears {colors["002FA7"]} time(s) in KI Swiss deck', file=sys.stderr)
        return 1
    print('KI Swiss final palette audit passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
