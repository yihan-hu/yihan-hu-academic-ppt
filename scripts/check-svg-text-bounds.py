#!/usr/bin/env python3
"""Check text marked with data-bbox in deterministic SVG figures.

SVG text does not auto-fit. This script is a hard gate for figure labels that
must remain inside a known region after larger live-presentation font sizes.

Expected SVG pattern:
  <text data-bbox="x,y,w,h" data-bbox-name="node label" font-size="28" ...>
    <tspan ...>Line 1</tspan><tspan ...>Line 2</tspan>
  </text>

The script measures each line with PIL using Noto Sans fallbacks and fails if
any line or multiline block exceeds the declared bbox, allowing configurable
padding.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    from PIL import ImageFont
except Exception as e:  # pragma: no cover
    print(f"ERROR: Pillow/PIL is required: {e}", file=sys.stderr)
    sys.exit(2)

FONT_DIRS = [
    Path("/usr/share/fonts/truetype/noto"),
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/share/fonts/truetype/liberation2"),
]

FONT_CANDIDATES = {
    "sans": {
        "regular": ["NotoSans-Regular.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
        "bold": ["NotoSans-Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    },
    "mono": {
        "regular": ["NotoSansMono-Regular.ttf", "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"],
        "bold": ["NotoSansMono-Bold.ttf", "DejaVuSansMono-Bold.ttf", "LiberationMono-Bold.ttf"],
    },
    "serif": {
        "regular": ["NotoSerif-Regular.ttf", "DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"],
        "bold": ["NotoSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"],
    },
}


def find_font(family: str, weight: str) -> str:
    fam = (family or "").lower()
    group = "mono" if "mono" in fam else ("serif" if "serif" in fam else "sans")
    wt = "bold" if str(weight).lower() in {"bold", "700", "800", "900", "600"} else "regular"
    for name in FONT_CANDIDATES[group][wt]:
        for d in FONT_DIRS:
            p = d / name
            if p.exists():
                return str(p)
    # last resort
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def parse_len(value: Optional[str], default: float = 0.0) -> float:
    if value is None:
        return default
    m = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(m.group(0)) if m else default


def parse_bbox(s: str) -> Tuple[float, float, float, float]:
    parts = [float(x) for x in re.split(r"[,\s]+", s.strip()) if x]
    if len(parts) != 4:
        raise ValueError(f"data-bbox must have 4 numbers, got: {s!r}")
    return tuple(parts)  # type: ignore


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def inherited_attr(el: ET.Element, name: str, default: str = "") -> str:
    return el.attrib.get(name, default)


def text_lines(el: ET.Element) -> List[str]:
    tspans = [child for child in list(el) if local_name(child.tag) == "tspan"]
    if tspans:
        lines = []
        for t in tspans:
            # Capture tspan text plus any nested tail text in a conservative way.
            txt = "".join(t.itertext())
            if txt.strip() or len(tspans) == 1:
                lines.append(txt.strip())
        return lines
    txt = "".join(el.itertext()).strip()
    return [txt] if txt else []


def text_width(font: ImageFont.FreeTypeFont, txt: str) -> float:
    if not txt:
        return 0.0
    # textlength is more accurate when available; bbox is a fallback.
    try:
        return float(font.getlength(txt))
    except Exception:
        box = font.getbbox(txt)
        return float(box[2] - box[0])


def line_height(font: ImageFont.FreeTypeFont, font_size: float, explicit: Optional[float]) -> float:
    if explicit and explicit > 0:
        return explicit
    ascent, descent = font.getmetrics()
    return max(font_size * 1.20, ascent + descent)


def check_file(path: Path, *, default_padding: float, require_bbox: bool, verbose: bool) -> int:
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        print(f"ERROR: cannot parse {path}: {e}", file=sys.stderr)
        return 2

    errors: List[str] = []
    checked = 0
    text_elems = [el for el in root.iter() if local_name(el.tag) == "text"]
    for idx, el in enumerate(text_elems, 1):
        bbox_s = el.attrib.get("data-bbox")
        if not bbox_s:
            if require_bbox:
                txt = " / ".join(text_lines(el))[:80]
                errors.append(f"{path.name}: untagged <text> #{idx}: {txt!r}")
            continue
        try:
            x, y, w, h = parse_bbox(bbox_s)
        except Exception as e:
            errors.append(f"{path.name}: invalid bbox on text #{idx}: {e}")
            continue
        name = el.attrib.get("data-bbox-name", f"text #{idx}")
        pad = parse_len(el.attrib.get("data-bbox-padding"), default_padding)
        family = inherited_attr(el, "font-family", "Noto Sans")
        weight = inherited_attr(el, "font-weight", "")
        font_size = parse_len(inherited_attr(el, "font-size", "16"), 16)
        lh = parse_len(el.attrib.get("data-line-height"), 0)
        font_path = find_font(family, weight)
        try:
            font = ImageFont.truetype(font_path, max(1, int(round(font_size))))
        except Exception as e:
            errors.append(f"{path.name}: cannot load font for {name}: {e}")
            continue
        lines = text_lines(el)
        if not lines:
            continue
        max_w = max(text_width(font, line) for line in lines)
        eff_lh = line_height(font, font_size, lh)
        total_h = font_size if len(lines) == 1 else font_size + (len(lines) - 1) * eff_lh
        avail_w = max(0, w - 2 * pad)
        avail_h = max(0, h - 2 * pad)
        checked += 1
        if max_w > avail_w + 0.5:
            errors.append(
                f"{path.name}: {name} width overflow: text {max_w:.1f}px > box {avail_w:.1f}px; lines={lines!r}; bbox={bbox_s}"
            )
        if total_h > avail_h + 0.5:
            errors.append(
                f"{path.name}: {name} height overflow: text {total_h:.1f}px > box {avail_h:.1f}px; lines={lines!r}; bbox={bbox_s}"
            )
    if verbose:
        print(f"{path}: checked {checked} tagged text boxes")
    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail if SVG data-bbox text exceeds its bounding region.")
    ap.add_argument("svg", nargs="+", help="SVG file(s) to check")
    ap.add_argument("--padding", type=float, default=4.0, help="default bbox padding in SVG px")
    ap.add_argument("--require-bbox", action="store_true", help="fail if any <text> lacks data-bbox")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    rc = 0
    for f in args.svg:
        code = check_file(Path(f), default_padding=args.padding, require_bbox=args.require_bbox, verbose=args.verbose)
        rc = max(rc, code)
    return rc


if __name__ == "__main__":
    sys.exit(main())
