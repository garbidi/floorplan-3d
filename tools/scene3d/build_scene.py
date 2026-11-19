"""Build a JSON scene (walls from the plan image + furniture list) for the three.js renderer.

Coordinates: plan pixels of plans_prepared/<key>_clean.png. Furniture boxes are given in % of the
outer-contour (same system as the size maps) and converted here.
"""
import json
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools")
from grid import load_plan  # noqa: E402
from overlay import bbox  # noqa: E402

P = "/mnt/c/Projects/3d_visual/"


def wall_rects(mask, cell=3):
    """Greedy rectangle cover of the wall mask on a coarse grid."""
    h, w = mask.shape
    g = mask[: h - h % cell, : w - w % cell].reshape(h // cell, cell, w // cell, cell).mean(axis=(1, 3)) > 0.5
    used = np.zeros_like(g)
    rects = []
    H, W = g.shape
    for y in range(H):
        x = 0
        while x < W:
            if g[y, x] and not used[y, x]:
                x1 = x
                while x1 < W and g[y, x1] and not used[y, x1]:
                    x1 += 1
                y1 = y + 1
                while y1 < H and g[y1, x:x1].all() and not used[y1, x:x1].any():
                    y1 += 1
                used[y:y1, x:x1] = True
                rects.append([x * cell, y * cell, x1 * cell, y1 * cell])
                x = x1
            else:
                x += 1
    return rects


def floor_rects(interior, tile_boxes, cell=6):
    out = []
    for r in wall_rects(interior, cell):
        cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        t = "tile" if any(b[0] <= cx <= b[2] and b[1] <= cy <= b[3] for b in tile_boxes) else "wood"
        out.append({"type": t, "box": r})
    return out


def build(key, furniture, floors, out, pixel=False, inside=(), style=None):
    """inside: extra boxes (plan px) that belong to the apartment although not enclosed by walls (e.g. glazed loggias)."""
    im = load_plan(P + f"plans_prepared/{key}_clean.png")
    a = np.asarray(im).astype(int)
    walls = (a[..., 0] < 90) & (abs(a[..., 0] - a[..., 1]) < 14) & (abs(a[..., 1] - a[..., 2]) < 14)
    from scipy import ndimage
    walls = ndimage.binary_opening(walls, structure=np.ones((7, 7)))   # drop thin lines (arcs, outlines)
    x0, y0, x1, y1 = bbox(walls)
    # interior = everything not connected to the image border through free space
    import cv2
    wp = cv2.copyMakeBorder(walls.astype(np.uint8), 400, 400, 400, 400, cv2.BORDER_CONSTANT, 0)
    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 701)); k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (701, 1))
    closed = (cv2.morphologyEx(wp, cv2.MORPH_CLOSE, k1) | cv2.morphologyEx(wp, cv2.MORPH_CLOSE, k2))[400:-400, 400:-400] > 0
    interior = ndimage.binary_fill_holes(closed)
    for bx in inside:
        interior[bx[1]:bx[3], bx[0]:bx[2]] = True
    Image.fromarray((interior * 255).astype(np.uint8)).save(out.replace(".json", "_mask.png"))
    ys, xs = np.where(walls)
    ext = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]

    def px(b):
        return [x0 + (x1 - x0) * b[0] / 100, y0 + (y1 - y0) * b[1] / 100,
                x0 + (x1 - x0) * b[2] / 100, y0 + (y1 - y0) * b[3] / 100]

    def conv(f):
        g = dict(f)
        if pixel:
            return g
        if "box" in g:
            g["box"] = px(g["box"])
        if "hinge" in g:
            h = px((g["hinge"][0], g["hinge"][1], g["hinge"][0], g["hinge"][1]))
            g["hinge"] = [h[0], h[1]]
        return g

    scene = {
        "size": [im.size[0], im.size[1]],
        "mask": out.replace(".json", "_mask.png"),
        "extent": ext,
        "walls": wall_rects(walls),
        "floors": [{"type": "wood", "box": [0, 0, im.size[0], im.size[1]]}] + [{"type": f["type"], "box": (f["box"] if pixel else px(f["box"]))} for f in floors if f["type"] == "tile"],
        "outside": wall_rects(~interior, 4),
        "items": [conv(f) for f in furniture],
        "style": style,
    }
    json.dump(scene, open(out, "w"), indent=0)
    return scene
