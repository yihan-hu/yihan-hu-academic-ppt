#!/usr/bin/env python3
"""Audit PPTX media for SVG figure compatibility risk.

Lists SVG media files and the slide relationships that reference them.
Use --fail-on-svg to return exit code 2 when SVG media is present.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def norm_target(base: PurePosixPath, target: str) -> str:
    parts = list(base.parts)
    for piece in target.split('/'):
        if piece in ('', '.'):
            continue
        if piece == '..':
            if parts:
                parts.pop()
        else:
            parts.append(piece)
    return '/'.join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('--fail-on-svg', action='store_true')
    args = ap.parse_args()

    with zipfile.ZipFile(args.pptx) as zf:
        names = set(zf.namelist())
        svg_media = sorted(n for n in names if n.startswith('ppt/media/') and n.lower().endswith('.svg'))
        refs: dict[str, list[str]] = {m: [] for m in svg_media}

        slide_re = re.compile(r'^ppt/slides/_rels/slide(\d+)\.xml\.rels$')
        for rel_name in names:
            m = slide_re.match(rel_name)
            if not m:
                continue
            slide_num = m.group(1)
            root = ET.fromstring(zf.read(rel_name))
            rel_base = PurePosixPath('ppt/slides')
            for rel in root.findall(f'{{{REL_NS}}}Relationship'):
                target = rel.attrib.get('Target', '')
                resolved = norm_target(rel_base, target)
                if resolved in refs:
                    refs[resolved].append(f'slide {slide_num}')

    if not svg_media:
        print('PASS: no embedded SVG media found.')
        return 0

    print(f'WARNING: found {len(svg_media)} embedded SVG media file(s).')
    for media in svg_media:
        used = ', '.join(refs.get(media, [])) or 'no slide relationship found'
        print(f'- {media}: {used}')
    print('If the target Office environment has shown blank SVGs, rasterize deterministic figures to high-resolution PNG before embedding.')
    return 2 if args.fail_on_svg else 0


if __name__ == '__main__':
    sys.exit(main())
