#!/usr/bin/env python3
"""Screenshot a built clinic site (local files, local fonts). Usage: screenshot.py <slug> <outdir>"""
import sys, glob, os, threading, http.server, functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
FONTS = glob.glob("/tmp/claude-0/-home-claude/*/scratchpad/fonts/node_modules/@fontsource/ibm-plex-sans*/files/*.woff2")

def main(slug, outdir):
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT/"public"))
    h.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h); port = srv.server_port
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    fontcss = []
    for f in FONTS:
        n = os.path.basename(f)  # ibm-plex-sans-latin-400-normal.woff2
        fam = "IBM Plex Sans Arabic" if "arabic" in n else "IBM Plex Sans"
        if "-latin-ext" in n or "cyrillic" in n or "vietnamese" in n or "greek" in n or "hebrew" in n or "devanagari" in n or "thai" in n: continue
        w = n.split("-")[-2]
        fontcss.append((n, fam, w))
    shots = [("desktop-top", dict(width=1440,height=900), "", False),
             ("desktop-full", dict(width=1440,height=900), "", True),
             ("mobile-top", dict(width=390,height=844), "", False),
             ("mobile-ar", dict(width=390,height=844), "?lang=ar", False)]
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, vp, qs, full in shots:
            ctx = b.new_context(viewport=vp, device_scale_factor=2 if vp["width"]<800 else 1)
            pg = ctx.new_page()
            def route(r):
                u = r.request.url
                if "fonts.googleapis.com" in u:
                    css = "".join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('http://fonts.local/{n}') format('woff2')}}" for n,fam,w in fontcss)
                    r.fulfill(body=css, content_type="text/css")
                elif "fonts.local" in u:
                    n = u.rsplit("/",1)[1]; r.fulfill(path=[f for f in FONTS if f.endswith(n)][0], content_type="font/woff2")
                elif "google.com/maps" in u or "fonts.gstatic" in u:
                    r.fulfill(body="", content_type="text/html")
                else: r.continue_()
            pg.route("**/*", route)
            pg.goto(f"http://127.0.0.1:{port}/{slug}/index.html{qs}", wait_until="load")
            pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
            pg.wait_for_timeout(1200)
            pg.screenshot(path=str(out/f"{slug}-{name}.png"), full_page=full)
            ctx.close()
        b.close()
    print("ok", list(out.iterdir()))
main(sys.argv[1], sys.argv[2])
