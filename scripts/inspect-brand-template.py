#!/usr/bin/env python3
"""Inspect a PPTX for brand-token candidates without treating the Office theme as authoritative."""

import argparse
import collections
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from PIL import Image
except Exception:
    Image = None

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


def rgb(v):
    if not v:
        return None
    v = str(v).replace('#', '').upper()
    return v if re.fullmatch(r'[0-9A-F]{6}', v) else None


def image_info(data, name):
    info = {'name': name, 'sizeBytes': len(data)}
    suffix = Path(name).suffix.lower()
    if suffix == '.svg':
        text = data.decode('utf-8', errors='ignore')
        colors = collections.Counter(c.upper() for c in re.findall(r'#[0-9A-Fa-f]{6}', text))
        info['svgColors'] = [{'color': c[1:], 'count': n} for c, n in colors.most_common(8)]
        return info
    if Image is None:
        return info
    try:
        from io import BytesIO
        im = Image.open(BytesIO(data)).convert('RGBA')
        info['width'], info['height'] = im.size
        thumb = im.copy()
        thumb.thumbnail((320, 320))
        colors = collections.Counter()
        chromatic = collections.Counter()
        for r, g, b, a in thumb.getdata():
            if a < 32:
                continue
            q = (round(r / 8) * 8, round(g / 8) * 8, round(b / 8) * 8)
            q = tuple(max(0, min(255, x)) for x in q)
            h = ''.join(f'{x:02X}' for x in q)
            colors[h] += 1
            if max(q) - min(q) > 18 and 20 < sum(q) / 3 < 235:
                chromatic[h] += 1
        info['dominantColors'] = [{'color': c, 'count': n} for c, n in colors.most_common(6)]
        info['dominantChromatic'] = [{'color': c, 'count': n} for c, n in chromatic.most_common(6)]
    except Exception as exc:
        info['imageWarning'] = str(exc)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('output_json')
    args = ap.parse_args()
    pptx = Path(args.pptx).resolve()
    out = Path(args.output_json).resolve()
    if not pptx.exists():
        raise SystemExit(f'PPTX not found: {pptx}')

    explicit = collections.Counter()
    scheme = collections.Counter()
    theme = {}
    media_usage = collections.Counter()
    media_info = {}

    with zipfile.ZipFile(pptx) as zf:
        names = set(zf.namelist())
        theme_name = 'ppt/theme/theme1.xml'
        if theme_name in names:
            root = ET.fromstring(zf.read(theme_name))
            clr_scheme = root.find('.//a:clrScheme', NS)
            if clr_scheme is not None:
                for child in list(clr_scheme):
                    key = child.tag.rsplit('}', 1)[-1]
                    leaf = next(iter(list(child)), None)
                    if leaf is None:
                        continue
                    value = leaf.attrib.get('val') or leaf.attrib.get('lastClr')
                    value = rgb(value)
                    if value:
                        theme[key] = value

        xml_targets = [n for n in names if (n.startswith('ppt/slides/') or n.startswith('ppt/slideMasters/') or n.startswith('ppt/slideLayouts/')) and n.endswith('.xml')]
        for name in xml_targets:
            text = zf.read(name).decode('utf-8', errors='ignore')
            for c in re.findall(r'<a:srgbClr\b[^>]*\bval="([0-9A-Fa-f]{6})"', text):
                explicit[c.upper()] += 1
            for c in re.findall(r'<a:schemeClr\b[^>]*\bval="([A-Za-z0-9]+)"', text):
                scheme[c] += 1

        for name in names:
            if not name.startswith('ppt/slides/_rels/slide') or not name.endswith('.xml.rels'):
                continue
            text = zf.read(name).decode('utf-8', errors='ignore')
            for target in re.findall(r'Target="\.\./media/([^"?]+)"', text):
                media_usage[target] += 1

        for media_name, usage in media_usage.items():
            full = f'ppt/media/{media_name}'
            if full in names:
                rec = image_info(zf.read(full), media_name)
                rec['usageCount'] = usage
                media_info[media_name] = rec

    report = {
        'source': str(pptx),
        'warning': 'Do not treat theme colors as the brand palette automatically. Prefer repeated explicit colors and repeated logo artwork, then confirm visually.',
        'themeColors': theme,
        'explicitColors': [{'color': c, 'count': n} for c, n in explicit.most_common(30)],
        'schemeColorUsage': [{'name': c, 'count': n} for c, n in scheme.most_common(20)],
        'mediaCandidates': sorted(media_info.values(), key=lambda x: (-x.get('usageCount', 0), x.get('name', ''))),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Brand inspection written: {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
