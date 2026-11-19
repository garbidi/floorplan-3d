"""Build a mirrored twin plan from a finished one: flip the photoreal render (without labels) horizontally,
fit it onto the twin plan's wall bbox, mirror the 3D scene JSON (for label placement), draw the twin's labels.
Usage: mirror_plan.py <src_key> <dst_key> <src_render_nolabels.png>"""
import json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from overlay import bbox
import labels
P = "/mnt/c/Projects/3d_visual/"


def walls(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    return (a[..., 0] < 90) & (abs(a[..., 0] - a[..., 1]) < 14) & (abs(a[..., 1] - a[..., 2]) < 14)


def main(src, dst, render):
    idx = json.load(open(P + "plans_prepared/index_new.json"))
    ws, wd = walls(P + f"plans_prepared/{src}_clean.png"), walls(P + f"plans_prepared/{dst}_clean.png")
    Ws = ws.shape[1]
    bs, bd = bbox(ws[:, ::-1]), bbox(wd)
    sx, sy = (bd[2] - bd[0]) / (bs[2] - bs[0]), (bd[3] - bd[1]) / (bs[3] - bs[1])
    fx = lambda x: bd[0] + ((Ws - x) - bs[0]) * sx
    fy = lambda y: bd[1] + (y - bs[1]) * sy
    # render
    im = Image.open(render).convert("RGB")
    K = im.size[0] / Ws
    Hd, Wd = wd.shape
    Kd = K
    flip = im.transpose(Image.FLIP_LEFT_RIGHT)
    # affine: dst pixel (u,v) in Kd-space -> plan dst (u/Kd, v/Kd) -> plan src-flipped -> src px
    inv_x = lambda u: ((u / Kd - bd[0]) / sx + bs[0]) * K
    inv_y = lambda v: ((v / Kd - bd[1]) / sy + bs[1]) * K
    a0, c0 = inv_x(0), inv_y(0)
    coeffs = (1 / sx, 0, a0, 0, 1 / sy, c0)
    out = flip.transform((int(Wd * Kd), int(Hd * Kd)), Image.AFFINE, coeffs, resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    rdir = P + f"renders/{idx[dst]['name']}/code3d/"
    os.makedirs(rdir, exist_ok=True)
    out.save(rdir + "mirror_nolabels.png")
    # scene json
    sc = json.load(open(P + f"renders/{idx[src]['name']}/code3d/scene.json"))
    def box(b):
        x0, x1 = sorted((fx(b[0]), fx(b[2]))); return [x0, fy(b[1]), x1, fy(b[3])]
    sc["size"] = [Wd, Hd]
    for k in ("walls", "outside"):
        sc[k] = [box(r) for r in sc.get(k, [])]
    for it in sc["items"]:
        if "box" in it:
            it["box"] = box(it["box"])
        if "hinge" in it:
            it["hinge"] = [fx(it["hinge"][0]), fy(it["hinge"][1])]
            it["angle"] = 180 - it.get("angle", 0)
    json.dump(sc, open(rdir + "scene.json", "w"))
    final = P + f"final/{idx[dst]['name']}.jpg"
    labels.draw_plan(dst, rdir + "mirror_nolabels.png", final)
    return final


if __name__ == "__main__":
    print(main(*sys.argv[1:4]))
