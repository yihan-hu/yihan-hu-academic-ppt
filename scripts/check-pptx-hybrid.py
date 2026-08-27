#!/usr/bin/env python3
import json
import os
import re
import sys
import zipfile
from pathlib import Path

SLIDE_W = 13.333333
SLIDE_H = 7.5


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def main():
    if len(sys.argv) != 3:
        print("Usage: python check-pptx-hybrid.py <deck-spec.json> <deck.pptx>", file=sys.stderr)
        return 2

    spec_path = Path(sys.argv[1]).resolve()
    pptx_path = Path(sys.argv[2]).resolve()
    if not spec_path.exists():
        return fail(f"spec not found: {spec_path}")
    if not pptx_path.exists():
        return fail(f"pptx not found: {pptx_path}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slides = spec.get("slides") or []
    errors = []
    warnings = []

    def check_asset(raw, slide_no, label):
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            if not entry:
                continue
            p = entry if isinstance(entry, str) else entry.get("path")
            if p:
                full = Path(p) if os.path.isabs(p) else spec_path.parent / p
                if not full.exists():
                    errors.append(f"Slide {slide_no}: missing {label} asset: {p}")

    for idx, slide in enumerate(slides, 1):
        check_asset(slide.get("rasterUnderlay"), idx, "rasterUnderlay")
        check_asset(slide.get("rasterOverlay"), idx, "rasterOverlay")
        elements = slide.get("elements") or []
        native_count = 0
        text_count = 0
        for el in elements:
            typ = el.get("type")
            if typ in {"text", "shape", "line", "image"}:
                native_count += 1
            if typ == "text":
                text_count += 1
            if typ == "image":
                check_asset(el.get("path"), idx, "image")
            for key in ("x", "y", "w", "h"):
                if key not in el:
                    errors.append(f"Slide {idx}: {typ or 'element'} missing {key}")
            if all(isinstance(el.get(k), (int, float)) for k in ("x", "y", "w", "h")):
                x, y, w, h = [float(el[k]) for k in ("x", "y", "w", "h")]
                if x < -1e-6 or y < -1e-6 or w < 0 or h < 0 or x + w > SLIDE_W + 1e-4 or y + h > SLIDE_H + 1e-4:
                    errors.append(f"Slide {idx}: {typ} box out of bounds: x={x}, y={y}, w={w}, h={h}")
        if slide.get("rasterUnderlay") and native_count == 0 and not slide.get("allowRasterOnly"):
            errors.append(f"Slide {idx}: rasterUnderlay exists but there are no native editable elements. Hybrid mode must not silently become a full-slide screenshot; set allowRasterOnly only for intentionally non-editable visual pages.")
        if slide.get("rasterOverlay") and text_count:
            warnings.append(f"Slide {idx}: rasterOverlay + native text. Verify the overlay does not block text selection or duplicate text visually.")

    try:
        with zipfile.ZipFile(pptx_path) as zf:
            names = zf.namelist()
            slide_xmls = sorted(
                [n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)],
                key=lambda n: int(re.search(r"(\d+)", Path(n).name).group(1)),
            )
            if len(slide_xmls) != len(slides):
                errors.append(f"PPTX contains {len(slide_xmls)} slide XML files but spec contains {len(slides)} slides")
            for idx, slide_xml in enumerate(slide_xmls, 1):
                xml = zf.read(slide_xml).decode("utf-8", errors="ignore")
                expected_text = sum(1 for el in (slides[idx - 1].get("elements") or []) if el.get("type") == "text") if idx <= len(slides) else 0
                native_text_nodes = len(re.findall(r"<a:t(?:\s[^>]*)?>", xml))
                if expected_text > 0 and native_text_nodes == 0:
                    errors.append(f"Slide {idx}: spec has native text but PPTX slide XML has no <a:t> text nodes")
    except zipfile.BadZipFile:
        errors.append("output is not a valid PPTX/ZIP package")

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"Hybrid PPTX validation passed: {len(slides)} slide(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
