#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

SLIDE_W = 13.333333
SLIDE_H = 7.5

GENERATED_FIGURE_KINDS = {
    'forest-plot', 'effect-plot', 'methods-pipeline', 'study-design-diagram',
    'conceptual-schematic', 'treatment-state-diagram', 'state-transition-diagram',
    'cohort-flow', 'estimand-diagram', 'causal-schematic', 'graphical-summary'
}
QUANTITATIVE_GENERATED_FIGURES = {'forest-plot', 'effect-plot'}


ESTIMATE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*\(\s*\d+(?:\.\d+)?\s*[–-]\s*\d+(?:\.\d+)?\s*\)")


def _slide_text_for_figure(slide):
    parts = [str(slide.get('takeaway') or ''), str(slide.get('title') or '')]
    for el in slide.get('elements') or []:
        if not isinstance(el, dict):
            continue
        if el.get('type') == 'text':
            if isinstance(el.get('runs'), list):
                parts.extend(str(r.get('text') or '') for r in el.get('runs') if isinstance(r, dict))
            else:
                parts.append(str(el.get('text') or ''))
        elif el.get('type') == 'table':
            for row in el.get('rows') or []:
                if isinstance(row, list):
                    for cell in row:
                        if isinstance(cell, dict):
                            parts.append(str(cell.get('text') or ''))
                        else:
                            parts.append(str(cell))
    return ' '.join(parts)


def infer_whitelisted_figure(slide):
    """Infer likely whitelist hits so omission of figureKind cannot bypass policy."""
    elements = slide.get('elements') or []
    primitive_count = sum(1 for el in elements if isinstance(el, dict) and el.get('type') in {'shape', 'line'})
    text = _slide_text_for_figure(slide)
    low = text.lower()
    estimate_count = len(ESTIMATE_RE.findall(text))

    if primitive_count >= 6 and estimate_count >= 4:
        return 'effect-plot'

    state_terms = sum(term in low for term in ['current use', 'non-use', 'no use', 'discontinuation', 'three-state', 'two-state'])
    if primitive_count >= 8 and state_terms >= 5:
        return 'treatment-state-diagram'

    trial_terms = sum(term in low for term in ['trial', 'eligible visit', 'time zero', 'clone', 'grace period', 'censor', 'ipcw', 'follow-up'])
    if primitive_count >= 15 and trial_terms >= 4:
        return 'study-design-diagram'

    pipeline_terms = sum(term in low for term in ['pipeline', 'workflow', 'step', 'sequence', 'stage', 'cohort flow'])
    if primitive_count >= 10 and pipeline_terms >= 2:
        return 'methods-pipeline'

    concept_terms = sum(term in low for term in ['estimand', 'causal', 'mechanism', 'conceptual', 'exposure state', 'treatment state'])
    if primitive_count >= 8 and concept_terms >= 2:
        return 'conceptual-schematic'

    return None

try:
    from PIL import Image
except Exception:
    Image = None


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def entries_count(raw):
    if not raw:
        return 0
    return len(raw) if isinstance(raw, list) else 1


def rect_of(el):
    if not all(isinstance(el.get(k), (int, float)) for k in ('x', 'y', 'w', 'h')):
        return None
    return tuple(float(el[k]) for k in ('x', 'y', 'w', 'h'))


def overlap_ratio(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    iw = max(0.0, min(ax + aw, bx + bw) - max(ax, bx))
    ih = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    inter = iw * ih
    if inter <= 0:
        return 0.0
    denom = min(max(aw * ah, 1e-9), max(bw * bh, 1e-9))
    return inter / denom


def main():
    if len(sys.argv) != 3:
        print("Usage: python check-academic-pptx-hybrid.py <deck-spec.json> <deck.pptx>", file=sys.stderr)
        return 2

    spec_path = Path(sys.argv[1]).resolve()
    pptx_path = Path(sys.argv[2]).resolve()
    if not spec_path.exists():
        return fail(f"spec not found: {spec_path}")
    if not pptx_path.exists():
        return fail(f"pptx not found: {pptx_path}")

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slides = spec.get("slides") or []
    meta = spec.get("meta") or {}
    errors = []
    warnings = []

    if meta.get('designSource') != 'guizang-template':
        errors.append('meta.designSource must be guizang-template; independent PPTX visual design is not allowed')
    profile_style = 'swiss'
    profile_id = None
    raw_profile = meta.get('brandProfile')
    if raw_profile:
        try:
            value = str(raw_profile)
            if '/' in value or '\\' in value or value.lower().endswith('.json'):
                pp = Path(value) if Path(value).is_absolute() else spec_path.parent / value
            else:
                pp = Path(__file__).resolve().parents[1] / 'references' / 'brands' / f'{value}.json'
            profile_data = json.loads(pp.read_text(encoding='utf-8'))
            profile_style = profile_data.get('baseStyle') or 'swiss'
            profile_id = profile_data.get('id')
        except Exception as exc:
            errors.append(f'could not resolve brand profile style: {exc}')
    else:
        profile_style = meta.get('baseStyle') or 'swiss'
        profile_id = None
    expected_visual = 'guizang-editorial-academic' if profile_style == 'editorial' else 'guizang-swiss-academic'
    if meta.get('visualStyle') != expected_visual:
        errors.append(f'meta.visualStyle must be {expected_visual} for baseStyle={profile_style}')
    if str(meta.get('pptxFidelity') or '') != 'native-first':
        errors.append('meta.pptxFidelity must be native-first for Academic PPTX')
    if str(meta.get('figurePolicy') or '') != 'whitelist-enforced':
        errors.append('meta.figurePolicy must be whitelist-enforced so figureKind omission cannot bypass the generation whitelist')

    token_checker = Path(__file__).resolve().parent / 'check-brand-token-lock.py'
    if token_checker.exists():
        proc = subprocess.run([sys.executable, str(token_checker), str(spec_path)], capture_output=True, text=True)
        if proc.returncode != 0:
            errors.append('brand token lock failed: ' + (proc.stdout + proc.stderr).strip().replace('\n', ' | '))
        elif proc.stdout.strip():
            print(proc.stdout.strip())

    def resolve_asset(raw):
        return Path(raw) if os.path.isabs(raw) else spec_path.parent / raw

    def check_asset(raw, slide_no, label, require_alpha=False):
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            if not entry:
                continue
            p = entry if isinstance(entry, str) else entry.get("path")
            if not p:
                continue
            full = resolve_asset(p)
            if not full.exists():
                errors.append(f"Slide {slide_no}: missing {label} asset: {p}")
                continue
            if require_alpha and Image is not None:
                try:
                    im = Image.open(full)
                    has_alpha = im.mode in {"RGBA", "LA"} or "transparency" in im.info
                    if not has_alpha:
                        errors.append(f"Slide {slide_no}: {label} must be transparent; image has mode={im.mode}: {p}")
                except Exception as exc:
                    warnings.append(f"Slide {slide_no}: could not inspect {label} alpha ({p}): {exc}")

    fidelity_mode = str(meta.get("pptxFidelity") or "native-first")

    if profile_style == 'editorial':
        valid_body_layouts = {f'Layout {i}' for i in range(1, 11)}
        valid_special = set()
    else:
        valid_body_layouts = {f'S{i:02d}' for i in range(1, 23)}
        valid_special = {'SWISS-COVER-ASCII', 'SWISS-CLOSING-ASCII'}

    def cell_text(cell):
        if isinstance(cell, dict):
            if isinstance(cell.get('runs'), list):
                return ''.join(str(r.get('text', '')) for r in cell.get('runs') if isinstance(r, dict))
            if isinstance(cell.get('text'), list):
                return ''.join(str(r.get('text', '')) for r in cell.get('text') if isinstance(r, dict))
            return str(cell.get('text', ''))
        return str(cell)

    def check_editorial_table_rules(el, slide_no):
        table_style = el.get('tableStyle') or 'ki-editorial-banded'
        if table_style == 'publication':
            return
        if table_style != 'ki-editorial-banded':
            errors.append(f'Slide {slide_no}: KI editorial native table must use tableStyle="ki-editorial-banded" unless explicitly set to publication')
            return
        rows = el.get('rows') or []
        header_rows = el.get('headerRows', 1)
        body_font = el.get('fontSize', 16)
        if not isinstance(header_rows, int) or header_rows < 1:
            errors.append(f'Slide {slide_no}: KI editorial banded table requires at least one header row')
            return
        if rows and isinstance(rows[0], list):
            headers = [cell_text(c).strip() for c in rows[0]]
            has_bare_effect = any(re.fullmatch(r'(HR|OR|RR|IRR|MD|SMD|BETA|β)', h, re.I) for h in headers)
            has_interval_header = any(re.search(r'(95\s*%?\s*(CI|CrI)|CI|CrI)', h, re.I) for h in headers)
            if has_bare_effect and has_interval_header:
                errors.append(f'Slide {slide_no}: effect estimate and CI/CrI must share one table column/cell (e.g. "HR (95% CI)"), not separate columns')
        for r_idx, row in enumerate(rows):
            if r_idx < header_rows or not isinstance(row, list):
                continue
            for c_idx, cell in enumerate(row):
                if not isinstance(cell, dict):
                    continue
                opts = cell.get('options') or {}
                if 'fontSize' in opts and float(opts.get('fontSize')) != float(body_font):
                    errors.append(f'Slide {slide_no}: KI editorial table body cell r{r_idx+1}c{c_idx+1} changes font size; emphasize with bold at the same size')
                runs = cell.get('runs') if isinstance(cell.get('runs'), list) else (cell.get('text') if isinstance(cell.get('text'), list) else [])
                for run in runs:
                    if isinstance(run, dict) and isinstance(run.get('options'), dict) and 'fontSize' in run.get('options') and float(run['options']['fontSize']) != float(body_font):
                        errors.append(f'Slide {slide_no}: KI editorial table rich-text run r{r_idx+1}c{c_idx+1} changes font size; use weight only')

    for idx, slide in enumerate(slides, 1):
        layout = slide.get('layout')
        if layout not in valid_body_layouts | valid_special:
            family = 'Style A Layout 1-10' if profile_style == 'editorial' else 'Swiss S01-S22 or registered cover/closing'
            errors.append(f'Slide {idx}: layout must be an original Guizang {family}; got {layout!r}')
        if slide.get('sourceLayout') is not None and slide.get('sourceLayout') != layout:
            errors.append(f'Slide {idx}: sourceLayout must equal layout; got {slide.get("sourceLayout")!r} vs {layout!r}')
        check_asset(slide.get("rasterUnderlay"), idx, "rasterUnderlay")
        check_asset(slide.get("visualPlate"), idx, "visualPlate", require_alpha=True)
        check_asset(slide.get("rasterOverlay"), idx, "rasterOverlay")
        raster_present = bool(slide.get("rasterUnderlay") or slide.get("visualPlate") or slide.get("rasterOverlay"))
        if raster_present:
            purpose = str(slide.get('rasterPurpose') or '')
            allowed_purposes = {'webgl', 'canvas', 'ascii', 'map', 'complex-css', 'browser-effect'}
            if purpose not in allowed_purposes:
                errors.append(f'Slide {idx}: raster layer requires browser-only rasterPurpose; got {purpose!r}')
        if slide.get('visualPlate') and not slide.get('allowBrowserVisualPlate'):
            errors.append(f'Slide {idx}: visualPlate is not the normal native-first path; use only for browser-only effects with allowBrowserVisualPlate=true')

        elements = slide.get("elements") or []
        if profile_id == 'ki-editorial':
            editorial_tables = [el for el in elements if el.get('type') == 'table']
            if editorial_tables:
                for table_el in editorial_tables:
                    check_editorial_table_rules(table_el, idx)
                duplicate_stats = [el for el in elements if el.get('type') == 'text' and el.get('role') == 'statistic']
                if duplicate_stats and not slide.get('allowDuplicateStatistic'):
                    errors.append(f'Slide {idx}: KI editorial table slide contains a separate role=statistic; keep the emphasized estimate inside the table unless allowDuplicateStatistic is explicitly justified')
        native_count = 0
        text_count = 0
        scientific_native_count = 0
        native_image_count = 0
        foreground_collision = []
        shape_line_count = sum(1 for el in elements if el.get('type') in {'shape', 'line'})
        generated_figures = [el for el in elements if el.get('type') == 'image' and el.get('role') == 'generated-figure']
        declared_figure_kind = slide.get('figureKind')
        inferred_figure_kind = infer_whitelisted_figure(slide)
        if declared_figure_kind and declared_figure_kind not in GENERATED_FIGURE_KINDS:
            errors.append(f'Slide {idx}: unsupported figureKind {declared_figure_kind!r}; use the figure-generation whitelist')
        if inferred_figure_kind and not declared_figure_kind:
            errors.append(f'Slide {idx}: content heuristics indicate whitelist figure {inferred_figure_kind!r}, but figureKind is omitted. Classify before drawing; omission is not a native escape hatch.')
        effective_figure_kind = declared_figure_kind or inferred_figure_kind
        native_exception = bool(slide.get('allowNativeFigure'))
        if native_exception:
            if slide.get('userRequestedFullEditability') is not True:
                errors.append(f'Slide {idx}: allowNativeFigure requires userRequestedFullEditability=true')
            if not str(slide.get('nativeFigureReason') or '').strip():
                errors.append(f'Slide {idx}: allowNativeFigure requires a non-empty nativeFigureReason')
        if effective_figure_kind in GENERATED_FIGURE_KINDS and not generated_figures and not native_exception:
            errors.append(f'Slide {idx}: whitelist figure {effective_figure_kind} must be a generated/preserved picture object by default; found {shape_line_count} native shape/line primitives and no role=generated-figure image')

        for el in elements:
            typ = el.get("type")
            if typ in {"text", "shape", "line", "image", "table"}:
                native_count += 1
            if typ == "text":
                text_count += 1
            if typ == "image":
                native_image_count += 1
                check_asset(el.get("path"), idx, "image")
                path_text = str(el.get('path') or '').lower()
                is_logo = el.get('role') == 'logo' or 'ki-logo' in path_text or '/logo' in path_text or '\\logo' in path_text
                if is_logo:
                    if el.get('role') != 'logo':
                        errors.append(f'Slide {idx}: brand logo image must declare role="logo": {el.get("path")}')
                    if el.get('fit') not in (None, 'contain'):
                        errors.append(f'Slide {idx}: logo must use fit="contain"; got {el.get("fit")!r}')
                if el.get('role') == 'generated-figure':
                    fk = el.get('figureKind') or declared_figure_kind
                    if fk not in GENERATED_FIGURE_KINDS:
                        errors.append(f'Slide {idx}: generated-figure requires whitelisted figureKind; got {fk!r}')
                    if el.get('fit') not in (None, 'contain'):
                        errors.append(f'Slide {idx}: generated-figure must use fit="contain"; got {el.get("fit")!r}')
                    source = el.get('figureSource')
                    if source not in {'deterministic', 'preserved', 'image-gen'}:
                        errors.append(f'Slide {idx}: generated-figure must declare figureSource as deterministic, preserved, or image-gen; got {source!r}')
                    if fk in QUANTITATIVE_GENERATED_FIGURES and source not in {'deterministic', 'preserved'}:
                        errors.append(f'Slide {idx}: quantitative {fk} must use figureSource="deterministic" or "preserved"; got {source!r}')
            if (
                typ in {"text", "table"}
                or (typ == "image" and el.get("role") in {"evidence", "generated-figure"})
                or (typ in {"shape", "line"} and el.get("role") in {"annotation", "evidence", "scientific"})
            ):
                scientific_native_count += 1
            if typ in {'text', 'table', 'image'} and el.get('layer') != 'underlay':
                foreground_collision.append(el)
            for key in ("x", "y", "w", "h"):
                if key not in el:
                    errors.append(f"Slide {idx}: {typ or 'element'} missing {key}")
            if all(isinstance(el.get(k), (int, float)) for k in ("x", "y", "w", "h")):
                x, y, w, h = [float(el[k]) for k in ("x", "y", "w", "h")]
                if x < -1e-6 or y < -1e-6 or w < 0 or h < 0 or x + w > SLIDE_W + 1e-4 or y + h > SLIDE_H + 1e-4:
                    errors.append(f"Slide {idx}: {typ} box out of bounds: x={x}, y={y}, w={w}, h={h}")

        # Foreground collision check: text-text and text/table/image collisions are not decorative overlaps.
        for a_i in range(len(foreground_collision)):
            a = foreground_collision[a_i]
            ra = rect_of(a)
            if ra is None:
                continue
            for b_i in range(a_i + 1, len(foreground_collision)):
                b = foreground_collision[b_i]
                rb = rect_of(b)
                if rb is None:
                    continue
                if a.get('allowOverlap') or b.get('allowOverlap'):
                    continue
                if a.get('overlapGroup') and a.get('overlapGroup') == b.get('overlapGroup'):
                    continue
                # image-image overlaps are allowed for composed figures; every other foreground pair is checked.
                if a.get('type') == 'image' and b.get('type') == 'image':
                    continue
                ratio = overlap_ratio(ra, rb)
                threshold = 0.12 if a.get('type') == b.get('type') == 'text' else 0.06
                if ratio > threshold:
                    def desc(el):
                        if el.get('type') == 'text':
                            s = str(el.get('text') or '')
                            return f'text:{s[:42]!r}'
                        if el.get('type') == 'image':
                            return f'image:{el.get("role") or "image"}:{el.get("path")}'
                        return str(el.get('type'))
                    errors.append(f'Slide {idx}: foreground collision ratio={ratio:.2f} between {desc(a)} and {desc(b)}; move/reflow or mark only a truly intentional overlap')

        if (slide.get("rasterUnderlay") or slide.get("visualPlate")) and native_count == 0 and not slide.get("allowRasterOnly"):
            errors.append(f"Slide {idx}: visual/raster layers exist but there are no native editable elements; set allowRasterOnly only for an intentionally non-editable visual page")
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
                slide_spec = slides[idx - 1] if idx <= len(slides) else {}
                elements = slide_spec.get("elements") or []
                expected_text = sum(1 for el in elements if el.get("type") == "text")
                expected_tables = sum(1 for el in elements if el.get("type") == "table")
                expected_pics = (
                    sum(1 for el in elements if el.get("type") == "image")
                    + entries_count(slide_spec.get("rasterUnderlay"))
                    + entries_count(slide_spec.get("visualPlate"))
                    + entries_count(slide_spec.get("rasterOverlay"))
                )
                native_text_nodes = len(re.findall(r"<a:t(?:\s[^>]*)?>", xml))
                native_tables = len(re.findall(r"<a:tbl(?:\s[^>]*)?>", xml))
                pic_nodes = len(re.findall(r"<p:pic(?:\s[^>]*)?>", xml))
                if profile_id == 'ki-editorial':
                    try:
                        root_xml = ET.fromstring(xml)
                        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
                        bad_visible_fonts = {'Georgia', 'Courier New', 'Playfair Display', 'IBM Plex Mono'}
                        for run in root_xml.findall('.//a:r', ns):
                            txt = run.find('a:t', ns)
                            if txt is None or not (txt.text or '').strip():
                                continue
                            rpr = run.find('a:rPr', ns)
                            latin = rpr.find('a:latin', ns) if rpr is not None else None
                            face = latin.get('typeface') if latin is not None else ''
                            if face in bad_visible_fonts:
                                errors.append(f'Slide {idx}: visible KI Editorial text run fell back to {face!r}; use installed Noto Serif Display / Noto Sans / Noto Sans Mono')
                    except Exception as exc:
                        warnings.append(f'Slide {idx}: could not inspect visible text fonts: {exc}')
                if expected_text > 0 and native_text_nodes == 0:
                    errors.append(f"Slide {idx}: spec has native text but PPTX slide XML has no <a:t> text nodes")
                if expected_tables > 0 and native_tables == 0:
                    errors.append(f"Slide {idx}: spec has native table but PPTX slide XML has no <a:tbl> table node")
                if expected_pics > 0 and pic_nodes < expected_pics:
                    errors.append(f"Slide {idx}: expected at least {expected_pics} image layer(s) but PPTX has {pic_nodes} <p:pic> node(s)")

            expected_notes = sum(1 for s in slides if s.get("notes") or s.get("sources"))
            note_xmls = [n for n in names if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n)]
            if expected_notes > 0 and len(note_xmls) == 0:
                warnings.append("Spec contains notes/sources but PPTX package has no notesSlides; verify renderer support in the current PptxGenJS version.")
    except zipfile.BadZipFile:
        errors.append("output is not a valid PPTX/ZIP package")

    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"Academic native-first hybrid PPTX validation passed: {len(slides)} slide(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
