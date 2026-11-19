"""Room-by-room photoreal pass: cut the 3D render into room tiles (with a supported aspect), let Gemini
refine each tile, then paste every tile back only inside its own paste box (feathered).

Tile spec: {"name", "box": (x0,y0,x1,y1) crop in render px, "aspect": "9:16", "paste": (x0,y0,x1,y1), "text": room description}
"""
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, __file__.rsplit("/", 1)[0])

HEADER = """IMAGE 1 is an exact top-down 3D layout of ONE ROOM of an apartment (orthographic view straight down from the ceiling), cropped from the full plan. IMAGE 2 is the style reference.
Turn IMAGE 1 into a high-end photorealistic architectural visualization in exactly the style of IMAGE 2, keeping the layout 100% identical.
STRICT RULES:
- Same canvas and framing. Do NOT move, resize, add or remove any wall, door, window or object. Every object keeps exactly its position, outline, size, orientation and count. Do not invent new rooms, walls, doors or furniture.
- Walls and shafts stay solid flat matte black; areas outside the apartment stay pure white.
- Strict orthographic top-down view, no perspective: only top surfaces are visible.
- Calm warm evening light like IMAGE 2, soft shadows, gentle ambient occlusion. No ceiling lights. No text, no labels, no watermark.
- Floor: warm natural light-oak planks with real grain (bathroom: beige stone-look tiles). Doors are real thin door leaves exactly where they are drawn.
In this room:
"""


def ratio(a):
    w, h = a.split(":")
    return int(w) / int(h)


def prep(render, tiles, outdir, up=2):
    im = Image.open(render).convert("RGB")
    for t in tiles:
        c = im.crop(t["box"])
        c = c.resize((c.size[0] * up, c.size[1] * up), Image.LANCZOS)
        c.save(f"{outdir}/tile_{t['name']}.png")
        print(t["name"], c.size, round(c.size[0] / c.size[1], 3), "target", round(ratio(t["aspect"]), 3))


def generate(tiles, outdir, names=None):
    import gem
    ref = "/mnt/c/Projects/3d_visual/reference_style_notext.png"
    for t in tiles:
        if names and t["name"] not in names:
            continue
        r = gem.generate(HEADER + t["text"], [f"{outdir}/tile_{t['name']}.png", ref], f"{outdir}/tile_{t['name']}_ai.png", aspect=t["aspect"])
        print(t["name"], r, flush=True)


def merge(base, tiles, outdir, out, scale=1, feather=12, sparkle=True):
    """Paste refined tiles into base (render px * scale). The Gemini sparkle watermark is inpainted first."""
    import cv2
    a = np.asarray(Image.open(base).convert("RGB").resize(
        (Image.open(base).size[0] * scale, Image.open(base).size[1] * scale), Image.LANCZOS)).astype(np.float32)
    for t in tiles:
        ai = cv2.imread(f"{outdir}/tile_{t['name']}_ai.png")
        if sparkle:
            h, w = ai.shape[:2]
            m = np.zeros((h, w), np.uint8)
            s = int(min(w, h) * 0.035)
            cx, cy = int(w - min(w, h) * 0.09), int(h - min(w, h) * 0.09)  # sparkle sits ~9% of short side from the corner
            m[cy - s:cy + s, cx - s:cx + s] = 255
            ai = cv2.inpaint(ai, m, 9, cv2.INPAINT_TELEA)
        ai = cv2.cvtColor(ai, cv2.COLOR_BGR2RGB)
        x0, y0, x1, y1 = [v * scale for v in t["box"]]
        ai = cv2.resize(ai, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA).astype(np.float32)
        px0, py0, px1, py1 = [v * scale for v in t["paste"]]
        f = np.zeros((y1 - y0, x1 - x0), np.float32)
        f[py0 - y0:py1 - y0, px0 - x0:px1 - x0] = 1
        f = cv2.GaussianBlur(f, (0, 0), feather)
        f[py0 - y0 + 2 * feather:py1 - y0 - 2 * feather, px0 - x0 + 2 * feather:px1 - x0 - 2 * feather] = 1
        f = np.minimum(f, (cv2.GaussianBlur((f > 0.5).astype(np.float32), (0, 0), feather / 2) > 0.01).astype(np.float32) * f)
        a[y0:y1, x0:x1] = a[y0:y1, x0:x1] * (1 - f[..., None]) + ai * f[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=96)
    return out
