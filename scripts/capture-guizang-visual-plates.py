#!/usr/bin/env python3
"""Capture Guizang visual plates and optional full HTML references.

Fidelity plates contain only:
  - [data-pptx-fidelity]
  - [data-pptx-raster]
  - .ascii-bg
  - [data-pptx-raster-global] only for an actually transparent `.slide.hero`

Normal scientific content is hidden in the plate. The source HTML is made self-contained
and loaded once with Playwright `page.set_content()`, avoiding file:// / localhost policy
restrictions and avoiding repeated browser startup. Original deck scripts are stripped for
capture stability; deterministic static canvas fallbacks reproduce the Guizang grid/ASCII
atmosphere for the static PPTX frame.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import http.server
import mimetypes
import os
from pathlib import Path
import re
import shutil
import socketserver
import subprocess
import sys
import threading
import uuid

CAPTURE_STYLE = r"""
<style id="guizang-pptx-capture-style">
html,body{margin:0!important;width:100%!important;height:100%!important;overflow:hidden!important}
html{background:transparent!important}
body.guizang-pptx-plate{background:transparent!important}
body.guizang-pptx-plate #nav,body.guizang-pptx-plate #hint,body.guizang-pptx-plate #overview,
body.guizang-pptx-reference #nav,body.guizang-pptx-reference #hint,body.guizang-pptx-reference #overview{display:none!important}
body.guizang-pptx-plate #deck,body.guizang-pptx-reference #deck{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;transform:none!important;transition:none!important;overflow:hidden!important}
body.guizang-pptx-plate #deck{background:transparent!important}
body.guizang-pptx-plate #deck .slide,body.guizang-pptx-reference #deck .slide{display:none!important;position:absolute!important;inset:0!important;width:100vw!important;height:100vh!important;transform:none!important;transition:none!important}
body.guizang-pptx-plate #deck .slide{visibility:hidden!important;background:transparent!important;box-shadow:none!important}
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"],body.guizang-pptx-reference #deck .slide[data-pptx-active="1"]{display:flex!important}
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"]{visibility:visible!important}
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] *{visibility:hidden!important}
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] [data-pptx-fidelity],
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] [data-pptx-fidelity] *,
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] [data-pptx-raster],
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] [data-pptx-raster] *,
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] .ascii-bg,
body.guizang-pptx-plate #deck .slide[data-pptx-active="1"] .ascii-bg *{visibility:visible!important}
body.guizang-pptx-plate [data-pptx-raster-global]{visibility:hidden!important}
body.guizang-pptx-reference [data-pptx-raster-global]{visibility:visible!important}
body.guizang-pptx-plate [data-pptx-fidelity],body.guizang-pptx-plate [data-pptx-raster],body.guizang-pptx-plate .ascii-bg{opacity:1!important}
body.guizang-pptx-plate [data-anim],body.guizang-pptx-plate [data-animate],
body.guizang-pptx-reference [data-anim],body.guizang-pptx-reference [data-animate]{animation:none!important;transition:none!important;opacity:1!important;transform:none!important}
</style>
"""

CONTROLLER = r"""
<script id="guizang-pptx-capture-controller">
(() => {
  const slides=[...document.querySelectorAll('#deck .slide')];
  const drawAscii=(c)=>{
    const r=c.getBoundingClientRect(); if(r.width<4||r.height<4) return;
    c.width=Math.round(r.width); c.height=Math.round(r.height);
    const ctx=c.getContext('2d'); ctx.clearRect(0,0,c.width,c.height);
    ctx.font='500 13px "JetBrains Mono", monospace'; ctx.textBaseline='top';
    const chars='   ...:::---+++***◦◦••▢▣', cell=16, cols=Math.ceil(r.width/cell), rows=Math.ceil(r.height/cell), t=.72;
    for(let y=0;y<rows;y++) for(let x=0;x<cols;x++){
      const n=(Math.sin(x*.18+t)+Math.sin(y*.24-t*.7)+Math.sin((x+y)*.12+t*.45)+Math.sin(Math.hypot(x-cols*.5,y-rows*.5)*.16-t*.55))/4;
      const v=(n+1)/2; if(v<.22) continue; const ch=chars[Math.min(chars.length-1,Math.floor(v*chars.length))]; if(ch===' ') continue;
      const a=.08+(v-.22)*.55; ctx.fillStyle=`rgba(255,255,255,${a.toFixed(3)})`; ctx.fillText(ch,x*cell,y*cell);
    }
  };
  const drawGrid=(c)=>{
    const r=c.getBoundingClientRect(); if(r.width<4||r.height<4) return;
    c.width=Math.round(r.width); c.height=Math.round(r.height);
    const ctx=c.getContext('2d'); ctx.clearRect(0,0,c.width,c.height); ctx.lineWidth=1;
    for(let x=0;x<c.width;x+=64){ctx.strokeStyle=(x%256===0)?'rgba(10,10,10,.10)':'rgba(10,10,10,.035)';ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}
    for(let y=0;y<c.height;y+=64){ctx.strokeStyle=(y%256===0)?'rgba(10,10,10,.10)':'rgba(10,10,10,.035)';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}
  };
  window.__setGuizangCapture=(target,mode)=>{
    document.body.classList.remove('guizang-pptx-plate','guizang-pptx-reference');
    document.body.classList.add(mode==='plate'?'guizang-pptx-plate':'guizang-pptx-reference');
    slides.forEach((s,i)=>s.setAttribute('data-pptx-active',i===target?'1':'0'));
    document.querySelectorAll('[data-anim],[data-animate]').forEach(el=>{el.style.opacity='1';el.style.transform='none';el.style.animation='none';el.style.transition='none';});
    const active=slides[target]; active?.querySelectorAll('canvas.ascii-bg').forEach(drawAscii);
    const global=document.querySelector('[data-pptx-raster-global]');
    if(global){global.style.visibility=(active?.classList.contains('hero'))?'visible':'hidden';if(active?.classList.contains('hero'))drawGrid(global);}
    window.__currentSlideIndex=target; return true;
  };
  window.__GuizangCaptureReady=true;
})();
</script>
"""


def maybe_reexec_with_playwright() -> None:
    if os.environ.get('GUIZANG_PLAYWRIGHT_REEXEC') == '1': return
    try:
        import playwright.sync_api  # noqa
        return
    except Exception:
        pass
    exe=shutil.which('playwright')
    if not exe: return
    d=Path(exe).resolve().parent
    for name in ('python','python3'):
        cand=d/name
        if cand.exists() and Path(sys.executable).resolve()!=cand.resolve():
            env=dict(os.environ); env['GUIZANG_PLAYWRIGHT_REEXEC']='1'
            os.execve(str(cand),[str(cand),str(Path(__file__).resolve()),*sys.argv[1:]],env)


def browser_executable(explicit: str|None) -> str:
    if explicit:
        p=shutil.which(explicit) or (explicit if Path(explicit).exists() else None)
        if p: return str(p)
        raise SystemExit(f'Browser executable not found: {explicit}')
    for name in ('chromium','chromium-browser','google-chrome','google-chrome-stable','microsoft-edge','msedge'):
        p=shutil.which(name)
        if p: return p
    raise SystemExit('No Chromium/Chrome/Edge executable found.')


def inline_local_assets(html: str, base_dir: Path) -> str:
    def local(raw): return not (re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',raw.strip()) or raw.strip().startswith('//') or raw.strip().startswith('#'))
    def fp(raw):
        raw=raw.split('?',1)[0].split('#',1)[0]; q=Path(raw); return q if q.is_absolute() else (base_dir/q).resolve()
    def uri(p):
        mime=mimetypes.guess_type(p.name)[0] or 'application/octet-stream'; return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode('ascii')}"
    # original scripts are stripped for capture stability
    html=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',html,flags=re.I)
    def link(m):
        attrs=(m.group(1)+' '+m.group(3)).lower(); raw=m.group(2)
        if 'stylesheet' not in attrs or not local(raw) or not fp(raw).exists(): return m.group(0)
        return '<style>\n'+fp(raw).read_text(encoding='utf-8',errors='ignore')+'\n</style>'
    html=re.sub(r'<link\b([^>]*?)\bhref=["\']([^"\']+)["\']([^>]*)>',link,html,flags=re.I)
    def attr(m):
        raw=m.group(2); p=fp(raw) if local(raw) else None
        return f'{m.group(1)}="{uri(p)}"' if p and p.exists() and p.is_file() else m.group(0)
    html=re.sub(r'\b(src|poster)=["\']([^"\']+)["\']',attr,html,flags=re.I)
    def cssurl(m):
        raw=m.group(1).strip().strip('"\''); p=fp(raw) if local(raw) else None
        return f'url("{uri(p)}")' if p and p.exists() and p.is_file() else m.group(0)
    html=re.sub(r'url\(([^)]+)\)',cssurl,html,flags=re.I)
    return html


def inject_controller(html: str) -> str:
    html=html.replace('</head>',CAPTURE_STYLE+'\n</head>',1) if '</head>' in html else CAPTURE_STYLE+'\n'+html
    html=html.replace('</body>',CONTROLLER+'\n</body>',1) if '</body>' in html else html+'\n'+CONTROLLER
    return html


def capture_playwright(html_content, browser_path, count, out, ref_out, width, height, settle_ms):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=browser_path,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        page.set_content(html_content,wait_until='domcontentloaded',timeout=30000)
        page.wait_for_function('window.__GuizangCaptureReady === true',timeout=10000)
        for i in range(count):
            page.evaluate('(x)=>window.__setGuizangCapture(x[0],x[1])',[i,'plate']); page.wait_for_timeout(settle_ms)
            dest=out/f'slide-{i+1:02d}-visual.png'; page.screenshot(path=str(dest),omit_background=True,animations='disabled'); print(dest)
            if ref_out:
                page.evaluate('(x)=>window.__setGuizangCapture(x[0],x[1])',[i,'reference']); page.wait_for_timeout(settle_ms)
                ref=ref_out/f'slide-{i+1}.png'; page.screenshot(path=str(ref),omit_background=False,animations='disabled'); print(ref)
        browser.close()


def main():
    maybe_reexec_with_playwright()
    ap=argparse.ArgumentParser(); ap.add_argument('html'); ap.add_argument('output_dir'); ap.add_argument('--reference-dir'); ap.add_argument('--width',type=int,default=2560); ap.add_argument('--height',type=int,default=1440); ap.add_argument('--browser'); ap.add_argument('--settle-ms',type=int,default=40)
    a=ap.parse_args(); src=Path(a.html).resolve(); out=Path(a.output_dir).resolve(); ref=Path(a.reference_dir).resolve() if a.reference_dir else None
    if not src.exists(): raise SystemExit(f'HTML not found: {src}')
    if abs(a.width/a.height-16/9)>.01: raise SystemExit('Capture must be 16:9')
    raw=src.read_text(encoding='utf-8'); count=len(re.findall(r'<section\b[^>]*\bclass=["\'][^"\']*\bslide\b',raw,flags=re.I))
    if not count: raise SystemExit('No <section class="slide ..."> elements found')
    out.mkdir(parents=True,exist_ok=True); ref and ref.mkdir(parents=True,exist_ok=True)
    html=inject_controller(inline_local_assets(raw,src.parent)); browser=browser_executable(a.browser)
    try:
        import playwright.sync_api  # noqa
    except ImportError:
        raise SystemExit('Playwright is required for reliable fidelity capture. Install Python Playwright or run in an environment that provides it.')
    capture_playwright(html,browser,count,out,ref,a.width,a.height,a.settle_ms)
    print(f'Captured {count} Guizang visual plate(s) at {a.width}x{a.height}.')
    if ref: print(f'Captured {count} full HTML reference slide(s).')
    return 0

if __name__=='__main__': raise SystemExit(main())
