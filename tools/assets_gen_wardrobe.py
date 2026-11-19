"""Generate wardrobe-section assets: 3D blockout (closet.html) -> Gemini photoreal -> interior crop into assets/.
Each variant is one wardrobe section seen from above, rail horizontal, BACK WALL AT THE TOP of the image.
Usage: python3 tools/assets_gen_wardrobe.py blockout|gen [names...]"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__) + "/scene3d")
P = "/mnt/c/Projects/3d_visual/"
D = P + "assets/wardrobe/src/"

PAL = {  # colour, kind
    "wshirt": ["#f2efe8", "shirt"], "bshirt": ["#b9cbe0", "shirt"], "pshirt": ["#e8d3d0", "shirt"], "sshirt": ["#cfd6c4", "shirt"],
    "camel": ["#a57648", "coat"], "black": ["#1f2024", "coat"], "grey": ["#6d6e72", "coat"], "navy": ["#2a3448", "wool"],
    "cream": ["#e6dac4", "knit"], "oat": ["#c9b394", "knit"], "rust": ["#8a4a32", "knit"], "sage": ["#8d9a7e", "knit"],
    "olive": ["#5a6246", "wool"], "denim": ["#4a6384", "denim"], "lightdenim": ["#8aa3be", "denim"], "charcoal": ["#3a3b3f", "wool"],
    "terracotta": ["#b0654a", "knit"], "beige": ["#d8c7a8", "wool"], "burgundy": ["#5e2630", "knit"], "white": ["#f5f3ee", "knit"],
}
VARIANTS = {
    "shirts_light": dict(mode="hang_shoes", hang=["wshirt", "bshirt", "wshirt", "pshirt", "sshirt", "wshirt", "bshirt", "cream"], shoes=[["#f3f1ec", "sneaker"], ["#caa27a", "loafer"]]),
    "coats_dark": dict(mode="hang_shoes", hang=["black", "charcoal", "camel", "grey", "navy"], shoes=[["#1a1817", "boot"], ["#3b2a20", "boot"]]),
    "knits_warm": dict(mode="hang", hang=["oat", "rust", "cream", "terracotta", "sage", "burgundy", "white"]),
    "mixed_denim": dict(mode="hang_shoes", hang=["denim", "wshirt", "lightdenim", "olive", "denim", "bshirt", "charcoal"], shoes=[["#8a6446", "loafer"], ["#f1eee8", "sneaker"]]),
    "suits": dict(mode="hang_shoes", hang=["navy", "wshirt", "charcoal", "bshirt", "grey", "wshirt"], shoes=[["#1c1a19", "loafer"], ["#5a3a26", "loafer"]]),
    "stacks_neutral": dict(mode="shelf", stacks=[5, 6, 4], stackPal=[["#e9e4da", "knit"], ["#a9b2bb", "plain"], ["#c7ab86", "knit"]]),
    "stacks_color": dict(mode="shelf", stacks=[6, 4, 5], stackPal=[["#2f3a4f", "knit"], ["#b86a4e", "knit"], ["#8d9a7e", "plain"]]),
    "coats_light": dict(mode="hang_shoes", hang=["beige", "camel", "cream", "oat", "grey"], shoes=[["#e8e2d6", "sneaker"], ["#1a1817", "boot"]]),
    "casual": dict(mode="hang", hang=["sage", "wshirt", "denim", "oat", "bshirt", "black", "terracotta", "lightdenim"]),
    "stacks_mixed": dict(mode="shelf", stacks=[4, 5, 6], stackPal=[["#f2efe8", "plain"], ["#4a6384", "twill"], ["#e6dac4", "knit"]]),
}
L, DEPTH = 398, 224          # section length (rail) x depth, blockout px


def blockout(name, seed):
    from closet_render import render
    v = VARIANTS[name]
    keys = list(dict.fromkeys(v.get("hang", [])))
    cfg = {"w": DEPTH, "h": L, "dividers": [], "seed": seed, "modes": [v["mode"]],
           "palette": [PAL[k] for k in keys] or [PAL["wshirt"]],
           "hang": [[keys.index(k) for k in v.get("hang", [])]], "shoes": [v.get("shoes", [])],
           "stacks": [v.get("stacks", [])]}
    if "stackPal" in v:
        cfg["stackPal"] = v["stackPal"]
    out = D + f"{name}_block.png"
    render(cfg, out)
    im = Image.open(out).convert("RGB").rotate(90, expand=True)     # rail horizontal, back wall (x=0) -> bottom
    im = im.transpose(Image.FLIP_TOP_BOTTOM)                           # back wall at the top
    w, h = im.size                                                     # ~ 1194 x 672 (16:9)
    FR = 40                                                            # walnut carcass frame, px of the 1456x816 input
    inner = im.resize((1456 - 2 * FR, 816 - 2 * FR), Image.LANCZOS)
    canvas = Image.new("RGB", (1456, 816), (92, 58, 38))
    canvas.paste(inner, (FR, FR))
    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    d.rectangle((FR - 4, FR - 4, 1456 - FR + 3, 816 - FR + 3), outline=(52, 32, 20), width=4)
    canvas.save(D + f"{name}_in.png")


PROMPT_HANG = open(P + "tools/tmp/closet_prompt_hang.txt").read()
PROMPT_SHELF = open(P + "tools/tmp/closet_prompt_shelf.txt").read()
FIX = ("\nThe back wall of the wardrobe is at the TOP edge of the image, the open front at the BOTTOM edge. "
       "The walnut carcass frames the image on all sides exactly as in image 1.")


def gen(name):
    import gem
    v = VARIANTS[name]
    txt = (PROMPT_SHELF if v["mode"] == "shelf" else PROMPT_HANG).replace("Keep the strip of parquet and the black border exactly as in the image.", "") + FIX
    return gem.generate(txt, [D + f"{name}_in.png"], D + f"{name}_ai.png", aspect="16:9")


if __name__ == "__main__":
    cmd, names = sys.argv[1], sys.argv[2:] or list(VARIANTS)
    for i, n in enumerate(names):
        if cmd == "blockout":
            blockout(n, 11 + i * 7); print("block", n, flush=True)
        else:
            print("gen", n, gen(n), flush=True)
