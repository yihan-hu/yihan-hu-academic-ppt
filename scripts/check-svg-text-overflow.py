#!/usr/bin/env python3
"""Hard-gate bounded text in generated figures.

Usage:
  python check-svg-text-overflow.py spec.json

The spec JSON is a list of figure checks or a dict with key "figures".
Each figure item supports:
  {
    "name": "registry-flow",
    "font": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "items": [
      {"text": "HbA1c · BMI", "font_size": 22, "box": [0,0,220,24]},
      {"lines": ["Follow-up", "up to", "1800 d"], "font_size": 24, "line_height": 21, "box": [0,0,165,68]}
    ]
  }

The script measures text with Pillow. If any item exceeds its declared box,
it exits non-zero and prints each failing item.
"""
import argparse, json, sys
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image

DEFAULT_FONT = '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf'


def load_spec(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and 'figures' in data:
        return data['figures']
    if isinstance(data, list):
        return data
    raise SystemExit('Spec must be a list or an object with key "figures"')


def text_width(draw, font, text):
    if not text:
        return 0
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def line_height(draw, font):
    bbox = draw.textbbox((0,0), 'Ag', font=font)
    return bbox[3] - bbox[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec_json')
    args = ap.parse_args()

    draw = ImageDraw.Draw(Image.new('RGB', (10, 10), 'white'))
    figures = load_spec(args.spec_json)
    failures = []

    for fig in figures:
        name = fig.get('name', 'unnamed-figure')
        font_path = fig.get('font', DEFAULT_FONT)
        for idx, item in enumerate(fig.get('items', []), start=1):
            box = item.get('box')
            if not box or len(box) != 4:
                failures.append(f'{name} item {idx}: missing 4-number box')
                continue
            _, _, bw, bh = box
            fsize = int(item.get('font_size', 24))
            font = ImageFont.truetype(font_path, fsize)
            lines = item.get('lines') or [item.get('text', '')]
            lh = int(item.get('line_height') or line_height(draw, font))
            maxw = max(text_width(draw, font, line) for line in lines)
            totalh = lh * len(lines)
            if maxw > bw or totalh > bh:
                failures.append(
                    f'{name} item {idx} overflow: text={lines!r} measured {maxw}x{totalh} exceeds box {bw}x{bh}'
                )

    if failures:
        print('FAIL: bounded text overflow detected', file=sys.stderr)
        for f in failures:
            print(f'- {f}', file=sys.stderr)
        raise SystemExit(2)
    print('PASS: all bounded text items fit declared boxes')


if __name__ == '__main__':
    main()
