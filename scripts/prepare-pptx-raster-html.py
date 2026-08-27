#!/usr/bin/env python3
"""Prepare one HTML capture source per slide for PPTX hybrid raster layers.

This script does not launch a browser. It injects capture-only CSS/JS that hides normal
slide content and keeps only elements explicitly marked data-pptx-raster, global
browser-only layers marked data-pptx-raster-global, and Swiss .ascii-bg canvases.
Use the host environment's browser screenshot tool to render the generated files.
"""

import re
import sys
from pathlib import Path

CAPTURE_STYLE = r"""
<style id="pptx-raster-capture-style">
html,body{background:transparent!important;overflow:hidden!important}
body.pptx-raster-capture #nav,
body.pptx-raster-capture #hint,
body.pptx-raster-capture #overview{display:none!important}
body.pptx-raster-capture > *{visibility:hidden!important}
body.pptx-raster-capture #deck,
body.pptx-raster-capture [data-pptx-raster-global]{visibility:visible!important}
body.pptx-raster-capture #deck .slide{background:transparent!important;box-shadow:none!important}
body.pptx-raster-capture #deck .slide *{visibility:hidden!important}
body.pptx-raster-capture #deck .slide [data-pptx-raster],
body.pptx-raster-capture #deck .slide [data-pptx-raster] *,
body.pptx-raster-capture #deck .slide .ascii-bg{visibility:visible!important}
body.pptx-raster-capture #deck .slide [data-pptx-raster]{opacity:1!important}
body.pptx-raster-capture #deck .slide .ascii-bg{opacity:.92!important}
body.pptx-raster-capture [data-anim],
body.pptx-raster-capture [data-animate]{animation:none!important;transition:none!important}
</style>
"""

SCRIPT_TEMPLATE = r"""
<script id="pptx-raster-capture-script">
(() => {
  const target = __TARGET_SLIDE__;
  const run = () => {
    document.body.classList.add('pptx-raster-capture');
    const deck = document.getElementById('deck');
    const slides = [...document.querySelectorAll('.slide')];
    if (deck) {
      deck.style.transition = 'none';
      deck.style.transform = `translateX(${-target * 100}vw)`;
    }
    window.__currentSlideIndex = target;
    slides.forEach((s, i) => s.setAttribute('data-pptx-active', i === target ? '1' : '0'));
    document.querySelectorAll('[data-anim],[data-animate]').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, {once:true});
  else run();
})();
</script>
"""


def inject(html: str, target: int) -> str:
    style = CAPTURE_STYLE
    script = SCRIPT_TEMPLATE.replace('__TARGET_SLIDE__', str(target))
    if '</head>' in html:
        html = html.replace('</head>', style + '\n</head>', 1)
    else:
        html = style + '\n' + html
    if '</body>' in html:
        html = html.replace('</body>', script + '\n</body>', 1)
    else:
        html += '\n' + script
    return html


def main():
    if len(sys.argv) != 3:
        print('Usage: python prepare-pptx-raster-html.py <index.html> <output-dir>', file=sys.stderr)
        return 2
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if not src.exists():
        print(f'HTML not found: {src}', file=sys.stderr)
        return 1
    html = src.read_text(encoding='utf-8')
    # Both bundled templates use <section class="slide ...">.
    count = len(re.findall(r'<section\b[^>]*\bclass=["\'][^"\']*\bslide\b', html, flags=re.I))
    if count == 0:
        print('No <section class="slide ..."> elements found.', file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        dest = out / f'slide-{i + 1:02d}.html'
        dest.write_text(inject(html, i), encoding='utf-8')
        print(dest)
    print(f'Prepared {count} raster capture HTML file(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
