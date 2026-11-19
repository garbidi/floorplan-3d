"""Region redraw guided by the matching crop of the 2D plan (IMAGE 1 = plan crop, IMAGE 2 = render crop)."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import fix  # noqa: E402
import studio  # noqa: E402
from grid import load_plan  # noqa: E402
from overlay import bbox  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

PROJ = "/mnt/c/Projects/3d_visual"


def run(render, plan, pct_box, inner_pct, change, out, extra=(), res="2K", gen_name="pg_gen.jpg"):
    im = Image.open(render).convert("RGB")
    cb = fix.contour(im)
    x0, y0, x1, y1 = fix.to_px(im, pct_box, cb)
    w, h = x1 - x0, y1 - y0
    name, r = min(studio.RATIOS.items(), key=lambda kv: abs(kv[1] - w / h))
    if w / h < r:
        nw = int(h * r); x0 -= (nw - w) // 2; x1 = x0 + nw
    else:
        nh = int(w / r); y0 -= (nh - h) // 2; y1 = y0 + nh
    # same box in % of contour -> plan pixels
    pct = [(x0 - cb[0]) / (cb[2] - cb[0]) * 100, (y0 - cb[1]) / (cb[3] - cb[1]) * 100,
           (x1 - cb[0]) / (cb[2] - cb[0]) * 100, (y1 - cb[1]) / (cb[3] - cb[1]) * 100]
    pl = load_plan(plan)
    a = np.asarray(pl).astype(int)
    walls = (a[..., 0] < 90) & (abs(a[..., 0] - a[..., 1]) < 12) & (abs(a[..., 1] - a[..., 2]) < 12)
    pc = bbox(walls)
    pbox = fix.to_px(pl, pct, pc)
    pl.crop(pbox).resize((x1 - x0, y1 - y0), Image.LANCZOS).save(PROJ + "/tools/tmp/pg_plan.png")
    im.crop((x0, y0, x1, y1)).save(PROJ + "/tools/tmp/pg_render.jpg", quality=97)
    prompt = ("IMAGE 1 is a fragment of the 2D architectural floor plan. IMAGE 2 is exactly the same fragment of the "
              "photorealistic top-down render of this apartment (same framing, same scale). " + change +
              " Output a redrawn IMAGE 2 with exactly the same framing, scale, walls, floor and lighting; strict "
              "orthographic top-down view from the ceiling. No borders, no text.")
    for _ in range(3):
        studio.js("location.href = 'https://aistudio.google.com/prompts/new_chat?model=gemini-3-pro-image'")
        for _ in range(6):
            time.sleep(1.5); studio.tick()
        studio.set_selects(name, res)
        studio.send(prompt, [PROJ + "/tools/tmp/pg_plan.png", PROJ + "/tools/tmp/pg_render.jpg", *extra])
        if studio.wait_turn(2) == "ok" and studio.last_size() > 500:
            break
    gen = PROJ + "/tools/tmp/" + gen_name
    studio.save_last_image(gen)
    fix.paste_px(render, gen, (x0, y0, x1, y1), out, inner_px=fix.to_px(im, inner_pct, cb), feather=5)
    return {"ratio": name, "out": out}
