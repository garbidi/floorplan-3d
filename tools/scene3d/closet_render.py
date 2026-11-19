"""Render the 3D wardrobe interior (closet.html) to PNG. Usage: from closet_render import render; render(cfg, out)."""
import base64
import json

from playwright.sync_api import sync_playwright

DEFAULT = {
    "ss": 3, "seed": 5, "exposure": 1.1, "wallH": 700, "th": 6, "shelfY": 420, "led": 60000,
    "palette": [["#ecE8e0", "shirt"], ["#bccde0", "shirt"], ["#c9b08e", "knit"], ["#3b3f49", "wool"],
                ["#9a6e48", "coat"], ["#e3d6c0", "knit"], ["#5a6450", "wool"], ["#222326", "coat"],
                ["#949290", "knit"], ["#48607f", "denim"], ["#f4f0e8", "shirt"], ["#7a4a3a", "knit"]],
    "stackPal": [["#e6ddcf", "knit"], ["#8e9aa8", "plain"], ["#b89a78", "knit"], ["#f1eee8", "plain"]],
}


def render(cfg, out):
    c = dict(DEFAULT); c.update(cfg)
    html = open(__file__.rsplit("/", 1)[0] + "/closet.html", encoding="utf-8").read()
    html = html.replace("<body>", f"<body><script>window.CFG={json.dumps(c)};</script>", 1)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 400, "height": 400})
        pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.set_content(html, wait_until="load")
        pg.wait_for_function("window.RENDER_DONE === true", timeout=900000)
        data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
        open(out, "wb").write(base64.b64decode(data.split(",", 1)[1]))
        b.close()
