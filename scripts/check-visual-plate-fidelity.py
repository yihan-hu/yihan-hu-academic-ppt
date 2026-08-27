#!/usr/bin/env python3
"""Verify that opaque Guizang visual-plate pixels survive PPTX rendering.

Run after rendering deck.pptx to slide-1.png, slide-2.png, ... . The checker masks
native element rectangles because scientific content is expected to sit above the plate.
It compares high-alpha visual-plate pixels against the rendered PPTX and can also
compare the full HTML reference outside native scientific rectangles. The second check
catches missing slide backgrounds / split blocks that a transparent plate-only check cannot see.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

try:
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except Exception:
    print('ERROR: Pillow is required for visual fidelity checking.', file=sys.stderr)
    raise SystemExit(2)

SLIDE_W = 13.333333
SLIDE_H = 7.5


def resolve(base: Path, p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else base / q


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('rendered_dir')
    ap.add_argument('--alpha', type=int, default=245, help='Only compare plate pixels at or above this alpha')
    ap.add_argument('--mae', type=float, default=18.0, help='Maximum mean absolute RGB error on compared pixels')
    ap.add_argument('--min-pixels', type=int, default=1500)
    ap.add_argument('--reference-dir', help='Directory containing full HTML reference slide-1.png, slide-2.png, ...')
    ap.add_argument('--reference-mae', type=float, default=10.0, help='Maximum RGB MAE outside native scientific rectangles')
    args = ap.parse_args()

    spec_path = Path(args.spec).resolve()
    rendered_dir = Path(args.rendered_dir).resolve()
    reference_dir = Path(args.reference_dir).resolve() if args.reference_dir else None
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    slides = spec.get('slides') or []
    errors = []
    warnings = []

    for idx, slide in enumerate(slides, 1):
        vp = slide.get('visualPlate')
        if not vp:
            if not slide.get('allowNativeVisualSkin'):
                errors.append(f'Slide {idx}: no visualPlate')
            continue
        if isinstance(vp, list):
            warnings.append(f'Slide {idx}: multiple visualPlate entries; fidelity checker uses the first one')
            vp = vp[0]
        if isinstance(vp, dict):
            vp = vp.get('path')
        if not vp:
            errors.append(f'Slide {idx}: invalid visualPlate entry')
            continue

        plate_path = resolve(spec_path.parent, vp)
        render_path = rendered_dir / f'slide-{idx}.png'
        if not render_path.exists():
            # also support zero-padded names
            render_path = rendered_dir / f'slide-{idx:02d}.png'
        if not plate_path.exists() or not render_path.exists():
            errors.append(f'Slide {idx}: missing plate/render ({plate_path.name}, {render_path.name})')
            continue

        plate = Image.open(plate_path).convert('RGBA')
        rendered = Image.open(render_path).convert('RGB')
        if plate.size != rendered.size:
            plate = plate.resize(rendered.size, Image.Resampling.LANCZOS)
        w, h = rendered.size

        # high-alpha plate mask
        alpha = plate.getchannel('A')
        mask = alpha.point(lambda a: 255 if a >= args.alpha else 0)

        # Exclude native element rectangles; they are expected to cover the plate.
        # Keep a reusable native mask for the optional full-reference skeleton check.
        native_mask = Image.new('L', (w, h), 255)
        native_draw = ImageDraw.Draw(native_mask)
        draw = ImageDraw.Draw(mask)
        for el in slide.get('elements') or []:
            if not all(isinstance(el.get(k), (int, float)) for k in ('x','y','w','h')):
                continue
            pad = 8
            x0 = int(max(0, el['x'] / SLIDE_W * w - pad))
            y0 = int(max(0, el['y'] / SLIDE_H * h - pad))
            x1 = int(min(w, (el['x'] + el['w']) / SLIDE_W * w + pad))
            y1 = int(min(h, (el['y'] + el['h']) / SLIDE_H * h + pad))
            draw.rectangle((x0, y0, x1, y1), fill=0)
            native_draw.rectangle((x0, y0, x1, y1), fill=0)

        compared = mask.histogram()[255]
        if compared < args.min_pixels:
            warnings.append(f'Slide {idx}: only {compared} opaque plate pixels available for comparison')
            continue

        plate_rgb = plate.convert('RGB')
        diff = ImageChops.difference(plate_rgb, rendered)
        # mask diff and compute mean over active pixels only
        channels = diff.split()
        total = 0.0
        for ch in channels:
            stat = ImageStat.Stat(ch, mask=mask)
            total += stat.mean[0]
        mae = total / 3.0
        print(f'Slide {idx}: visual-plate opaque-pixel MAE={mae:.2f} over {compared} px')
        if mae > args.mae:
            errors.append(f'Slide {idx}: visual plate fidelity MAE {mae:.2f} exceeds {args.mae:.2f}')

        if reference_dir:
            reference_path = reference_dir / f'slide-{idx}.png'
            if not reference_path.exists():
                reference_path = reference_dir / f'slide-{idx:02d}.png'
            if not reference_path.exists():
                errors.append(f'Slide {idx}: missing full HTML reference in {reference_dir}')
            else:
                reference = Image.open(reference_path).convert('RGB')
                if reference.size != rendered.size:
                    reference = reference.resize(rendered.size, Image.Resampling.LANCZOS)
                ref_diff = ImageChops.difference(reference, rendered)
                active = native_mask.histogram()[255]
                if active < args.min_pixels:
                    warnings.append(f'Slide {idx}: only {active} reference skeleton pixels available for comparison')
                else:
                    ref_total = 0.0
                    for ch in ref_diff.split():
                        ref_total += ImageStat.Stat(ch, mask=native_mask).mean[0]
                    ref_mae = ref_total / 3.0
                    print(f'Slide {idx}: reference skeleton MAE={ref_mae:.2f} over {active} px')
                    if ref_mae > args.reference_mae:
                        errors.append(f'Slide {idx}: reference skeleton MAE {ref_mae:.2f} exceeds {args.reference_mae:.2f}; check slide background / split blocks / Guizang chrome')

    for w in warnings:
        print(f'WARNING: {w}')
    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        return 1
    print(f'Visual-plate fidelity check passed: {len(slides)} slide(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
