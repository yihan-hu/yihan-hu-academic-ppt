#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let PptxGenJS;
try {
  PptxGenJS = require('pptxgenjs');
} catch (err) {
  console.error('Missing dependency: pptxgenjs. Install it in the current Node environment.');
  process.exit(2);
}

let imageSizeFn = null;
try {
  const imageSizePkg = require('image-size');
  imageSizeFn = imageSizePkg.imageSize || imageSizePkg.default || imageSizePkg;
} catch (_) {
  // contain mode will fail with an actionable message if used.
}

const [specArg, outputArg] = process.argv.slice(2);
if (!specArg || !outputArg) {
  console.error('Usage: node render-academic-pptx.mjs <deck-spec.json> <output.pptx>');
  process.exit(2);
}

const specPath = path.resolve(specArg);
const outputPath = path.resolve(outputArg);
const baseDir = path.dirname(specPath);
const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const meta = spec.meta || {};

const SLIDE_W = 13.333333;
const SLIDE_H = 7.5;
const GUIZANG_NEUTRALS = { backgroundColor: 'FAFAF8', inkColor: '0A0A0A', grey1: 'F0F0EE', grey2: 'D4D4D2', grey3: '737373' };

function normalizeHex(v) {
  const raw = String(v || '').replace(/^#/, '').toUpperCase();
  return /^[0-9A-F]{6}$/.test(raw) ? raw : null;
}

function resolveBrandProfile(raw) {
  if (!raw) return { path: null, profile: null };
  const value = String(raw);
  let p;
  if (value.includes('/') || value.includes('\\') || value.toLowerCase().endsWith('.json')) {
    p = path.isAbsolute(value) ? value : path.resolve(baseDir, value);
  } else {
    p = path.resolve(skillRoot, 'references', 'brands', `${value}.json`);
  }
  if (!fs.existsSync(p)) throw new Error(`brandProfile not found: ${raw}`);
  return { path: p, profile: JSON.parse(fs.readFileSync(p, 'utf8')) };
}

const brand = resolveBrandProfile(meta.brandProfile);
if ((meta.designSource || '') !== 'guizang-template') {
  throw new Error('meta.designSource must be "guizang-template". Academic PPTX is rendered from Guizang HTML/template geometry, not an independent PowerPoint design.');
}

const baseStyle = brand.profile?.baseStyle || meta.baseStyle || 'swiss';
let visual;
if (baseStyle === 'editorial') {
  if (!brand.profile) throw new Error('Editorial Academic PPTX currently requires an explicit style-aware brand profile.');
  if (brand.profile.neutralPolicy !== 'style-a-theme-block') throw new Error('Editorial brand profile must use neutralPolicy="style-a-theme-block".');
  const t = brand.profile.themeTokens || {};
  const p = brand.profile.presentationTokens || {};
  const paper = normalizeHex(t.paper);
  const darkField = normalizeHex(t.ink);
  const paperTint = normalizeHex(t.paperTint);
  const inkTint = normalizeHex(t.inkTint);
  const readingInk = normalizeHex(p.readingInk) || darkField;
  const mutedInk = normalizeHex(p.mutedInk) || readingInk;
  const slideTitle = normalizeHex(p.slideTitle) || normalizeHex(brand.profile.accent) || inkTint;
  const semanticLabel = normalizeHex(p.semanticLabel) || normalizeHex(brand.profile.accent) || inkTint;
  const iconStroke = normalizeHex(p.iconStroke) || semanticLabel;
  const arrowStroke = normalizeHex(p.arrowStroke) || semanticLabel;
  const peerPanelFill = normalizeHex(p.peerPanelFill) || normalizeHex(p.tableStripeFill) || paperTint;
  const groupingFill = normalizeHex(p.groupingFill) || normalizeHex(p.panelFill) || paperTint;
  const panelFill = normalizeHex(p.panelFill) || groupingFill;
  const semanticBandFill = normalizeHex(p.semanticBandFill) || darkField;
  const semanticBandOn = normalizeHex(p.semanticBandOn) || paper;
  if (!paper || !darkField || !paperTint || !inkTint) throw new Error('Editorial brand profile is missing required Style A themeTokens.');
  for (const [key, expected] of Object.entries({ backgroundColor: paper, paperTint, inkTint })) {
    if (meta[key] && normalizeHex(meta[key]) !== expected) throw new Error(`Editorial brand mode locks meta.${key} to ${expected}; got ${normalizeHex(meta[key])}`);
  }
  if (meta.inkColor && normalizeHex(meta.inkColor) !== readingInk) throw new Error(`Editorial native reading ink must be ${readingInk}; got ${normalizeHex(meta.inkColor)}`);
  visual = {
    paper,
    ink: readingInk,
    darkField,
    panel: panelFill,
    groupingFill,
    peerPanel: peerPanelFill,
    semanticBand: semanticBandFill,
    semanticBandOn,
    titleAccent: slideTitle,
    semanticLabel,
    iconStroke,
    arrowStroke,
    grey1: paperTint,
    grey2: paperTint,
    grey3: mutedInk,
    accent: normalizeHex(brand.profile.accent) || inkTint,
    head: meta.headFontFace || 'Noto Serif Display',
    hero: meta.heroFontFace || 'Noto Serif Display',
    section: meta.sectionFontFace || 'Noto Serif Display',
    title: meta.titleFontFace || 'Noto Serif Display',
    body: meta.bodyFontFace || 'Noto Sans',
    mono: meta.monoFontFace || 'Noto Sans Mono',
    label: meta.labelFontFace || meta.monoFontFace || 'Noto Sans Mono',
    cjk: meta.cjkFontFace || 'Noto Sans CJK SC'
  };
} else if (baseStyle === 'swiss') {
  if (brand.profile) {
    if (brand.profile.neutralPolicy !== 'inherit-guizang') throw new Error('Swiss brand profile must use neutralPolicy="inherit-guizang".');
    for (const [key, expected] of Object.entries(GUIZANG_NEUTRALS)) {
      const actual = normalizeHex(meta[key] || expected);
      if (actual !== expected) throw new Error(`Swiss brand mode locks meta.${key} to Guizang ${expected}; got ${actual}`);
    }
    const profileAccent = normalizeHex(brand.profile.accent);
    if (!profileAccent) throw new Error('Brand profile accent must be a six-digit RGB value.');
    if (meta.accentColor && normalizeHex(meta.accentColor) !== profileAccent) {
      throw new Error(`meta.accentColor must equal brand profile accent ${profileAccent}`);
    }
  }
  visual = {
    paper: GUIZANG_NEUTRALS.backgroundColor,
    ink: GUIZANG_NEUTRALS.inkColor,
    darkField: GUIZANG_NEUTRALS.inkColor,
    panel: GUIZANG_NEUTRALS.grey1,
    grey1: GUIZANG_NEUTRALS.grey1,
    grey2: GUIZANG_NEUTRALS.grey2,
    grey3: GUIZANG_NEUTRALS.grey3,
    accent: normalizeHex(brand.profile?.accent) || meta.accentColor || '002FA7',
    head: meta.headFontFace || 'Inter Display',
    hero: meta.heroFontFace || 'Inter Display ExtraLight',
    section: meta.sectionFontFace || 'Inter Display Light',
    title: meta.titleFontFace || 'Inter Display Light',
    body: meta.bodyFontFace || 'Inter',
    mono: meta.monoFontFace || 'JetBrains Mono',
    label: meta.labelFontFace || meta.monoFontFace || 'JetBrains Mono',
    cjk: meta.cjkFontFace || 'Noto Sans CJK SC'
  };
} else {
  throw new Error(`Unsupported baseStyle: ${baseStyle}`);
}

const profileTableTokens = brand.profile?.tableTokens || {};
const tableTokens = {
  headerFill: normalizeHex(profileTableTokens.headerFill) || (baseStyle === 'editorial' ? 'EFE8EB' : visual.grey1),
  stripeFill: normalizeHex(profileTableTokens.stripeFill) || (baseStyle === 'editorial' ? 'F7F3F5' : visual.grey1),
  bodyFill: normalizeHex(profileTableTokens.bodyFill) || 'FFFFFF',
  gridColor: normalizeHex(profileTableTokens.gridColor) || visual.grey2,
  headerRule: normalizeHex(profileTableTokens.headerRule) || visual.accent
};

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = meta.author || 'Academic PPT';
pptx.company = meta.company || '';
pptx.subject = meta.subject || `Guizang ${baseStyle} academic presentation`;
pptx.title = meta.title || 'Untitled academic deck';
pptx.lang = meta.lang || 'en-US';
pptx.theme = {
  headFontFace: visual.head,
  bodyFontFace: visual.body,
  lang: meta.lang || 'en-US'
};

function absAsset(p) {
  if (!p) return null;
  return path.isAbsolute(p) ? p : path.resolve(baseDir, p);
}

function ensureAsset(p, label) {
  const resolved = absAsset(p);
  if (!resolved || !fs.existsSync(resolved)) {
    throw new Error(`${label} not found: ${p}`);
  }
  return resolved;
}

function hex(v, fallback = '000000') {
  if (!v) return fallback;
  return String(v).replace(/^#/, '').toUpperCase();
}

function finite(n, label) {
  if (typeof n !== 'number' || !Number.isFinite(n)) throw new Error(`${label} must be a finite number`);
  return n;
}

function box(el) {
  return {
    x: finite(el.x, 'x'),
    y: finite(el.y, 'y'),
    w: finite(el.w, 'w'),
    h: finite(el.h, 'h')
  };
}

let activeSlideTone = 'light';

function hasCjk(text) {
  return /[\u3400-\u9FFF\uF900-\uFAFF]/.test(String(text || ''));
}

function roleStyle(role, text) {
  const cjk = hasCjk(text);
  const cjkFace = visual.cjk;
  const onDark = activeSlideTone === 'dark';
  const main = onDark ? visual.paper : visual.ink;
  const muted = onDark ? visual.paper : visual.grey3;
  const accent = onDark ? visual.paper : visual.accent;
  const titleColor = onDark ? visual.paper : (baseStyle === 'editorial' ? (visual.titleAccent || visual.accent) : main);
  const semanticColor = onDark ? visual.paper : (visual.semanticLabel || visual.accent);
  const styles = {
    hero:       { fontFace: cjk ? cjkFace : visual.hero, fontSize: 72, color: main, bold: false, valign: 'top' },
    section:    { fontFace: cjk ? cjkFace : visual.section, fontSize: 50, color: main, bold: false, valign: 'top' },
    title:      { fontFace: cjk ? cjkFace : visual.title, fontSize: 32, color: titleColor, bold: false, valign: 'top' },
    body:       { fontFace: cjk ? cjkFace : visual.body, fontSize: 19, color: main, bold: false, valign: 'top' },
    label:      { fontFace: cjk ? cjkFace : visual.label, fontSize: 12.5, color: muted, bold: cjk, valign: 'mid' },
    'semantic-label': { fontFace: cjk ? cjkFace : visual.label, fontSize: 12.5, color: semanticColor, bold: cjk, valign: 'mid' },
    'semantic-band-text': { fontFace: cjk ? cjkFace : visual.body, fontSize: 16, color: onDark ? visual.paper : (visual.semanticBandOn || visual.paper), bold: false, valign: 'mid' },
    meta:       { fontFace: cjk ? cjkFace : visual.label, fontSize: 11.5, color: muted, bold: cjk, valign: 'mid' },
    annotation: { fontFace: cjk ? cjkFace : visual.body, fontSize: 16, color: main, bold: false, valign: 'top' },
    citation:   { fontFace: cjk ? cjkFace : visual.body, fontSize: 10.5, color: muted, bold: false, valign: 'mid' },
    statistic:  { fontFace: cjk ? cjkFace : visual.section, fontSize: 54, color: accent, bold: false, valign: 'mid' },
    navigation: { fontFace: cjk ? cjkFace : visual.label, fontSize: 10.5, color: muted, bold: cjk, valign: 'mid' }
  };
  return styles[role] || styles.body;
}

function containBox(imgPath, target) {
  if (!imageSizeFn) throw new Error('image-size is required for fit="contain". Install image-size or pre-size the asset and use fit="stretch".');
  const data = fs.readFileSync(imgPath);
  const dims = imageSizeFn(data);
  if (!dims?.width || !dims?.height) throw new Error(`Cannot read image dimensions: ${imgPath}`);
  const src = dims.width / dims.height;
  const dst = target.w / target.h;
  let w = target.w, h = target.h, x = target.x, y = target.y;
  if (src > dst) {
    h = w / src;
    y += (target.h - h) / 2;
  } else {
    w = h * src;
    x += (target.w - w) / 2;
  }
  return { x, y, w, h };
}

function addImage(slide, img) {
  const p = ensureAsset(img.path, 'image');
  const target = box(img);
  const lowerPath = String(img.path || '').toLowerCase();
  const isLogo = img.role === 'logo' || lowerPath.includes('ki-logo') || lowerPath.includes('/logo') || lowerPath.includes('\\logo');
  const isFigure = img.role === 'evidence' || img.role === 'generated-figure';
  if (isLogo && img.fit && img.fit !== 'contain') {
    throw new Error(`Logo images must use fit="contain" to preserve aspect ratio: ${img.path}`);
  }
  const fit = (isLogo || isFigure) ? 'contain' : (img.fit || 'stretch');
  let placement = target;
  if (fit === 'contain') placement = containBox(p, target);
  if (fit === 'cover') {
    throw new Error(`fit="cover" is intentionally disabled for ${img.path}. Pre-crop ordinary assets to the slot ratio; for scientific evidence use fit="contain".`);
  }
  slide.addImage({ path: p, ...placement, transparency: img.transparency ?? 0, rotate: img.rotate ?? 0 });
}

function addText(slide, el) {
  const joinedText = el.runs ? el.runs.map(r => r.text || '').join('') : (el.text || '');
  const base = roleStyle(el.role || 'body', joinedText);
  const opts = {
    ...box(el),
    fontFace: el.fontFace || base.fontFace,
    fontSize: el.fontSize ?? base.fontSize,
    color: hex(el.color || base.color, visual.ink),
    bold: el.bold ?? base.bold,
    italic: !!el.italic,
    underline: el.underline || false,
    breakLine: el.breakLine || false,
    align: el.align || 'left',
    valign: el.valign || base.valign || 'mid',
    margin: el.margin ?? 0,
    fit: el.fit || 'shrink',
    paraSpaceAfterPt: el.paraSpaceAfterPt ?? 0,
    lineSpacingMultiple: el.lineSpacingMultiple,
    isTextBox: true
  };
  if (el.charSpacing !== undefined) opts.charSpacing = el.charSpacing;
  if (el.transparency !== undefined) opts.transparency = el.transparency;
  if (el.rotate !== undefined) opts.rotate = el.rotate;
  if (el.isTextBox !== undefined) opts.isTextBox = el.isTextBox;
  if (el.bullet) opts.bullet = el.bullet;
  if (el.rtlMode !== undefined) opts.rtlMode = el.rtlMode;
  if (el.runs) slide.addText(el.runs, opts);
  else slide.addText(el.text ?? '', opts);
}

function addShape(slide, el) {
  const shapeName = el.shape || 'rect';
  const shapeType = pptx.ShapeType?.[shapeName];
  if (!shapeType) throw new Error(`Unknown PptxGenJS shape type: ${shapeName}`);
  const opts = {
    ...box(el),
    fill: el.fill === null ? { color: 'FFFFFF', transparency: 100 } : { color: hex(el.fill,
      baseStyle === 'editorial' && el.role === 'peer-panel' ? visual.peerPanel :
      baseStyle === 'editorial' && el.role === 'semantic-band' ? visual.semanticBand :
      baseStyle === 'editorial' && (el.role === 'panel' || el.role === 'macro-field') ? visual.groupingFill :
      visual.paper), transparency: el.fillTransparency ?? 0 },
    line: el.line === null ? { color: 'FFFFFF', transparency: 100 } : {
      color: hex(el.lineColor || el.line, baseStyle === 'editorial' && el.role === 'icon-stroke' ? visual.iconStroke : visual.grey2),
      transparency: el.lineTransparency ?? 0,
      width: el.lineWidth ?? 0.8,
      dash: el.dash || 'solid'
    },
    rotate: el.rotate ?? 0
  };
  slide.addShape(shapeType, opts);
}

function addLine(slide, el) {
  const x = finite(el.x, 'line.x');
  const y = finite(el.y, 'line.y');
  const w = finite(el.w, 'line.w');
  const h = finite(el.h, 'line.h');
  slide.addShape(pptx.ShapeType.line, {
    x, y, w, h,
    line: {
      color: hex(el.color, baseStyle === 'editorial' && ['semantic-arrow','semantic-line'].includes(el.role) ? visual.arrowStroke : visual.grey2),
      transparency: el.transparency ?? 0,
      width: el.width ?? 0.8,
      dash: el.dash || 'solid',
      beginArrowType: el.beginArrowType,
      endArrowType: el.endArrowType
    }
  });
}

function normalizeFill(fill, fallback = visual.paper) {
  if (fill === null) return undefined;
  if (!fill) return { color: fallback };
  if (typeof fill === 'string') return { color: hex(fill, fallback) };
  const out = { ...fill };
  if (out.color) out.color = hex(out.color, fallback);
  return out;
}

function normalizeRichRuns(runs, fontSize) {
  return runs.map((run) => {
    const options = { ...(run?.options || {}) };
    // KI editorial table emphasis changes weight, not size.
    options.fontSize = fontSize;
    if (options.color) options.color = hex(options.color, visual.ink);
    return { text: String(run?.text ?? ''), options };
  });
}

function editorialBorder(isHeader) {
  const none = { type: 'solid', color: tableTokens.gridColor, pt: 0.1, transparency: 100 };
  const bodyBottom = { type: 'solid', color: tableTokens.gridColor, pt: 0.25 };
  const headerBottom = { type: 'solid', color: tableTokens.headerRule, pt: 0.8 };
  // top / right / bottom / left: hierarchy comes from fills, not a spreadsheet grid.
  return [none, none, isHeader ? headerBottom : bodyBottom, none];
}

function normalizeCell(cell, isHeader, el, rowIndex, tableStyle, headerRows) {
  const bodyFontSize = el.fontSize ?? 16;
  const headerFontSize = el.headerFontSize ?? bodyFontSize;
  const targetFontSize = isHeader ? headerFontSize : bodyFontSize;
  const bodyIndex = rowIndex - headerRows;
  const isEditorialBanded = tableStyle === 'ki-editorial-banded';

  const structuralOptions = {};
  if (isEditorialBanded) {
    structuralOptions.fill = {
      color: isHeader
        ? tableTokens.headerFill
        : (bodyIndex % 2 === 0 ? tableTokens.bodyFill : tableTokens.stripeFill)
    };
    structuralOptions.border = editorialBorder(isHeader);
    structuralOptions.fontSize = targetFontSize;
  } else if (isHeader) {
    structuralOptions.bold = true;
    structuralOptions.fill = { color: hex(el.headerFill || visual.grey1) };
  }
  if (isHeader && structuralOptions.bold === undefined) structuralOptions.bold = true;

  if (cell && typeof cell === 'object' && !Array.isArray(cell)) {
    const options = { ...structuralOptions, ...(cell.options || {}) };
    if (options.fill !== undefined) options.fill = normalizeFill(options.fill, isEditorialBanded ? tableTokens.bodyFill : visual.grey1);
    if (options.color) options.color = hex(options.color, visual.ink);
    // Never allow isolated font enlargement in the KI editorial banded table.
    if (isEditorialBanded) options.fontSize = targetFontSize;
    if (isHeader && options.bold === undefined) options.bold = true;
    if (isEditorialBanded) {
      // Structural fills/borders are profile-owned and may not be overridden cell-by-cell.
      options.fill = structuralOptions.fill;
      options.border = structuralOptions.border;
    } else if (isHeader && options.fill === undefined) {
      options.fill = { color: hex(el.headerFill || visual.grey1) };
    }

    const rawRuns = Array.isArray(cell.runs) ? cell.runs : (Array.isArray(cell.text) ? cell.text : null);
    if (rawRuns) {
      return { text: normalizeRichRuns(rawRuns, targetFontSize), options };
    }
    return { text: String(cell.text ?? ''), options };
  }

  return { text: String(cell ?? ''), options: structuralOptions };
}

function addTable(slide, el) {
  box(el);
  if (!Array.isArray(el.rows) || el.rows.length === 0) throw new Error('table element requires non-empty rows[]');
  const headerRows = Number.isInteger(el.headerRows) ? el.headerRows : 1;
  const defaultEditorialStyle = baseStyle === 'editorial' && brand.profile?.id === 'ki-editorial';
  const tableStyle = el.tableStyle || (defaultEditorialStyle ? 'ki-editorial-banded' : 'default');
  if (tableStyle === 'ki-editorial-banded' && !defaultEditorialStyle) {
    throw new Error('tableStyle="ki-editorial-banded" requires brandProfile="ki-editorial"');
  }
  const rows = el.rows.map((row, rIdx) => {
    if (!Array.isArray(row)) throw new Error(`table row ${rIdx + 1} must be an array`);
    return row.map(cell => normalizeCell(cell, rIdx < headerRows, el, rIdx, tableStyle, headerRows));
  });
  const isEditorialBanded = tableStyle === 'ki-editorial-banded';
  const opts = {
    ...box(el),
    fontFace: el.fontFace || visual.body,
    fontSize: el.fontSize ?? 16,
    color: hex(el.color, visual.ink),
    margin: el.margin ?? 0.06,
    border: isEditorialBanded
      ? { type: 'solid', color: tableTokens.gridColor, pt: 0.1, transparency: 100 }
      : (el.border ?? { type: 'solid', color: hex(el.borderColor || visual.grey2), pt: el.borderPt ?? 0.6 }),
    fill: isEditorialBanded ? { color: tableTokens.bodyFill } : normalizeFill(el.fill, visual.paper),
    valign: el.valign || 'mid',
    autoFit: false,
    breakLine: false
  };
  if (el.colW) opts.colW = el.colW;
  if (el.rowH) opts.rowH = el.rowH;
  if (el.bold !== undefined) opts.bold = !!el.bold;
  if (el.align) opts.align = el.align;
  slide.addTable(rows, opts);
}

function addRaster(slide, raster, label) {
  if (!raster) return;
  const entries = Array.isArray(raster) ? raster : [raster];
  for (const entry of entries) {
    if (typeof entry === 'string') {
      const p = ensureAsset(entry, label);
      slide.addImage({ path: p, x: 0, y: 0, w: SLIDE_W, h: SLIDE_H });
    } else {
      addImage(slide, { fit: 'stretch', x: 0, y: 0, w: SLIDE_W, h: SLIDE_H, ...entry });
    }
  }
}

function addNotes(slide, slideSpec) {
  const parts = [];
  if (slideSpec.notes) parts.push(String(slideSpec.notes).trim());
  if (Array.isArray(slideSpec.sources) && slideSpec.sources.length > 0) {
    parts.push(`[Sources]\n${slideSpec.sources.map(s => `- ${String(s)}`).join('\n')}`);
  }
  if (parts.length > 0) slide.addNotes(parts.join('\n\n'));
}

if (!Array.isArray(spec.slides) || spec.slides.length === 0) {
  throw new Error('deck-spec.json must contain a non-empty slides[] array');
}

function addElement(slide, el, slideNo) {
  switch (el.type) {
    case 'text': addText(slide, el); break;
    case 'shape': addShape(slide, el); break;
    case 'line': addLine(slide, el); break;
    case 'image': addImage(slide, el); break;
    case 'table': addTable(slide, el); break;
    default: throw new Error(`Slide ${slideNo}: unsupported element type "${el.type}"`);
  }
}

for (const [i, slideSpec] of spec.slides.entries()) {
  const slide = pptx.addSlide();
  const explicitBg = normalizeHex(slideSpec.backgroundColor);
  const inferredDark = explicitBg && normalizeHex(visual.darkField) && explicitBg === normalizeHex(visual.darkField);
  activeSlideTone = slideSpec.tone === 'dark' || inferredDark ? 'dark' : 'light';
  const defaultBg = activeSlideTone === 'dark' ? (visual.darkField || visual.ink) : visual.paper;
  slide.background = { color: hex(slideSpec.backgroundColor || defaultBg, defaultBg) };

  // Native-first hybrid order: browser-only underlay -> native elements -> optional browser-only overlay.
  // background -> browser effects -> native media underlay -> Guizang visual plate
  // -> editable scientific content -> rare top-most raster effect.
  addRaster(slide, slideSpec.rasterUnderlay, `slide ${i + 1} rasterUnderlay`);

  const elements = slideSpec.elements || [];
  for (const el of elements.filter(e => e.layer === 'underlay')) addElement(slide, el, i + 1);

  addRaster(slide, slideSpec.visualPlate, `slide ${i + 1} visualPlate`);

  for (const el of elements.filter(e => e.layer !== 'underlay')) addElement(slide, el, i + 1);

  addRaster(slide, slideSpec.rasterOverlay, `slide ${i + 1} rasterOverlay`);
  addNotes(slide, slideSpec);
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
await pptx.writeFile({ fileName: outputPath });
console.log(`Academic PPTX written: ${outputPath} (${spec.slides.length} slides)`);
