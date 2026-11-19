"""Create scene_<dst>.py items by affinely remapping another plan's scene items (same layout, different size):
bbox of walls of src -> bbox of walls of dst. Usage: remap_scene.py <src_key> <dst_key> -> prints python items list"""
import importlib, json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools")
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from overlay import bbox
P = "/mnt/c/Projects/3d_visual/"


def walls(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    return (a[..., 0] < 90) & (abs(a[..., 0] - a[..., 1]) < 14) & (abs(a[..., 1] - a[..., 2]) < 14)


def remap(src, dst):
    bs, bd = bbox(walls(P + f"plans_prepared/{src}_clean.png")), bbox(walls(P + f"plans_prepared/{dst}_clean.png"))
    sx, sy = (bd[2] - bd[0]) / (bs[2] - bs[0]), (bd[3] - bd[1]) / (bs[3] - bs[1])
    fx = lambda x: round(bd[0] + (x - bs[0]) * sx)
    fy = lambda y: round(bd[1] + (y - bs[1]) * sy)
    m = importlib.import_module(f"scene_{src}")
    B = lambda b: (fx(b[0]), fy(b[1]), fx(b[2]), fy(b[3]))
    items = []
    for it in m.items:
        g = dict(it)
        for k in ("box", "basin"):
            if k in g: g[k] = B(g[k])
        if "hinge" in g: g["hinge"] = (fx(g["hinge"][0]), fy(g["hinge"][1]))
        if "len" in g: g["len"] = round(g["len"] * (sx + sy) / 2)
        if "cutX" in g: g["cutX"], g["cutZ"] = fx(g["cutX"]), fy(g["cutZ"])
        if "plates" in g: g["plates"] = [(fx(p[0]), fy(p[1])) for p in g["plates"]]
        if "cushions" in g: g["cushions"] = [dict(c, box=B(c["box"])) for c in g["cushions"]]
        items.append(g)
    floors = [dict(f, box=B(f["box"])) for f in m.floors]
    return floors, items


if __name__ == "__main__":
    fl, it = remap(sys.argv[1], sys.argv[2])
    print("floors = " + repr(fl))
    print("items = [")
    for g in it: print("    " + repr(g) + ",")
    print("]")
