"""Regenerate only the wardrobes of a finished render: crop each wardrobe (from the plan's 3D scene), let
AI Studio (fallback Gemini) redraw it with garments strictly from above, align and paste back the interior.
Usage: wardrobe_redo.py <key> <base_nolabels.png> <out.png>"""
import json, os, sys
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ai_inpaint
P = "/mnt/c/Projects/3d_visual/"
PROMPT = """IMAGE 1 is a crop of a photorealistic top-down (orthographic, from the ceiling) apartment render showing a built-in OPEN walnut wardrobe.
Redraw it in the same photorealistic style, keeping EXACTLY the same framing, the same walnut carcass (side panels, back panel, dividers), the same black walls and the same parquet floor around it.
Only improve the CONTENTS of the wardrobe: garments hanging on wooden hangers on a chrome rail, seen STRICTLY FROM ABOVE — you see the shoulders of each garment with a natural fabric drape and the hanger hooks over the rail, not the front of the garments; realistic varied clothes (coats, jackets, shirts, knitwear) in calm natural colours, soft warm LED light inside; optionally a few pairs of shoes on the wardrobe floor seen from above.
Do not change anything outside the wardrobe. No text, no watermark."""


def gen(img_path, out_path, aspect):
    import studio, gem
    try:
        r = studio.generate(PROMPT, [img_path], out_path, aspect=aspect, tries=1)
        if os.path.exists(out_path) and Image.open(out_path).size[0] >= 2000:
            return "studio"
    except Exception as e:
        print("studio error", e)
    r = gem.generate(PROMPT, [img_path], out_path, aspect=aspect)
    return "gemini" if r else None


def main(key, base, out):
    idx = json.load(open(P + "plans_prepared/index_new.json"))
    rdir = P + f"renders/{idx[key]['name']}/code3d/"
    sc = json.load(open(rdir + "scene.json"))
    plan_w = sc["size"][0]
    a = np.asarray(Image.open(base).convert("RGB")).astype(np.float32)
    K = a.shape[1] / plan_w
    closets = [it["box"] for it in sc["items"] if it["type"] == "closet"]
    wd = rdir + "wardrobes/"; os.makedirs(wd, exist_ok=True)
    for i, b in enumerate(closets):
        x0, y0, x1, y1 = [v * K for v in b]
        m = 0.35 * max(x1 - x0, y1 - y0) + 30 * K
        crop, asp = ai_inpaint.crop_for([int(x0 - m), int(y0 - m), int(x1 + m), int(y1 + m)], a.shape)
        cx0, cy0, cx1, cy1 = crop
        img = np.clip(a[cy0:cy1, cx0:cx1], 0, 255).astype(np.uint8)
        sc_ = max(1.0, 1600 / max(img.shape[:2]))
        inp = wd + f"w{i}_in.png"; res = wd + f"w{i}_out.png"
        Image.fromarray(cv2.resize(img, None, fx=sc_, fy=sc_, interpolation=cv2.INTER_CUBIC)).save(inp)
        if os.path.exists(res):
            os.remove(res)
        eng = gen(inp, res, asp)
        print(key, "wardrobe", i, b, eng, flush=True)
        if not eng:
            continue
        ins = 0.02 * min(x1 - x0, y1 - y0)
        try:
            ai_inpaint.paste(a, crop, [int(x0 + ins), int(y0 + ins), int(x1 - ins), int(y1 - ins)], res, feather=3, min_ncc=0.35, gain=False)
        except Exception as e:
            print(key, "wardrobe", i, "paste failed:", e, flush=True)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
    return out


if __name__ == "__main__":
    print(main(*sys.argv[1:4]))
