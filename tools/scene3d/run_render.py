"""Render a scene JSON with three.js in headless Chromium. Usage: run_render.py scene.json out.png [width]"""
import base64
import json
import sys

from playwright.sync_api import sync_playwright

scene_p, out_p = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
html = open(__file__.rsplit("/", 1)[0] + "/render.html", encoding="utf-8").read()
scene = json.load(open(scene_p))
scene["maskData"] = "data:image/png;base64," + base64.b64encode(open(scene["mask"], "rb").read()).decode()
inject = f"<script>window.SCENE={json.dumps(scene)};window.OUT_W={width};</script>"
html = html.replace("<body>", "<body>" + inject, 1)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 800, "height": 600})
    pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.set_content(html, wait_until="load")
    pg.wait_for_function("window.RENDER_DONE === true", timeout=600000)
    data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
    open(out_p, "wb").write(base64.b64decode(data.split(",", 1)[1]))
    b.close()
# pure white outside the apartment (post-processing can tint the background)
from PIL import Image
import numpy as np
im = Image.open(out_p).convert("RGB")
m = Image.open(scene["mask"]).convert("L").resize(im.size, Image.NEAREST)
a = np.asarray(im).copy(); bg = (np.asarray(m) == 0) & (a.min(axis=2) > 170); a[bg] = 255
Image.fromarray(a).save(out_p)
print("saved", out_p)
