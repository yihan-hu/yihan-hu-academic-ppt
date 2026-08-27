#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';

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
  console.error('Usage: node render-pptx.mjs <deck-spec.json> <output.pptx>');
  process.exit(2);
}

const specPath = path.resolve(specArg);
const outputPath = path.resolve(outputArg);
const baseDir = path.dirname(specPath);
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));

const SLIDE_W = 13.333333;
const SLIDE_H = 7.5;
const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = spec.meta?.author || 'Guizang PPT Skill';
pptx.company = spec.meta?.company || '';
pptx.subject = spec.meta?.subject || 'Hybrid editable presentation';
pptx.title = spec.meta?.title || 'Untitled deck';
pptx.lang = spec.meta?.lang || 'zh-CN';
pptx.theme = {
  headFontFace: spec.meta?.headFontFace || 'Arial',
  bodyFontFace: spec.meta?.bodyFontFace || 'Arial',
  lang: spec.meta?.lang || 'zh-CN'
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
  const fit = img.fit || 'stretch';
  let placement = target;
  if (fit === 'contain') placement = containBox(p, target);
  if (fit === 'cover') {
    throw new Error(`fit="cover" is intentionally disabled for ${img.path}. Pre-crop the asset to the slot ratio, then use fit="stretch" to avoid PowerPoint crop inconsistencies.`);
  }
  slide.addImage({ path: p, ...placement, transparency: img.transparency ?? 0, rotate: img.rotate ?? 0 });
}

function addText(slide, el) {
  const opts = {
    ...box(el),
    fontFace: el.fontFace || spec.meta?.bodyFontFace || 'Arial',
    fontSize: el.fontSize ?? 20,
    color: hex(el.color, '000000'),
    bold: !!el.bold,
    italic: !!el.italic,
    underline: el.underline || false,
    breakLine: el.breakLine || false,
    align: el.align || 'left',
    valign: el.valign || 'mid',
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
    fill: el.fill === null ? { color: 'FFFFFF', transparency: 100 } : { color: hex(el.fill, 'FFFFFF'), transparency: el.fillTransparency ?? 0 },
    line: el.line === null ? { color: 'FFFFFF', transparency: 100 } : {
      color: hex(el.lineColor || el.line, '000000'),
      transparency: el.lineTransparency ?? 0,
      width: el.lineWidth ?? 1,
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
      color: hex(el.color, '000000'),
      transparency: el.transparency ?? 0,
      width: el.width ?? 1,
      dash: el.dash || 'solid',
      beginArrowType: el.beginArrowType,
      endArrowType: el.endArrowType
    }
  });
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

if (!Array.isArray(spec.slides) || spec.slides.length === 0) {
  throw new Error('deck-spec.json must contain a non-empty slides[] array');
}

for (const [i, slideSpec] of spec.slides.entries()) {
  const slide = pptx.addSlide();
  slide.background = { color: hex(slideSpec.backgroundColor || spec.meta?.backgroundColor || 'FFFFFF', 'FFFFFF') };
  addRaster(slide, slideSpec.rasterUnderlay, `slide ${i + 1} rasterUnderlay`);

  for (const el of slideSpec.elements || []) {
    switch (el.type) {
      case 'text': addText(slide, el); break;
      case 'shape': addShape(slide, el); break;
      case 'line': addLine(slide, el); break;
      case 'image': addImage(slide, el); break;
      default: throw new Error(`Slide ${i + 1}: unsupported element type "${el.type}"`);
    }
  }

  addRaster(slide, slideSpec.rasterOverlay, `slide ${i + 1} rasterOverlay`);
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
await pptx.writeFile({ fileName: outputPath });
console.log(`PPTX written: ${outputPath} (${spec.slides.length} slides)`);
