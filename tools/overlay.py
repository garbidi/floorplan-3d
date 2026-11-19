"""Geometry check: overlay the floor plan's line art (red) and walls on top of a render.

Usage: python3 overlay.py <plan.png> <render.jpg> <out.jpg>
Both images are normalized by the bounding box of their walls, so different margins don't matter.
Prints wall IoU (1.0 = walls match exactly).
"""
import sys

import numpy as np
from PIL import Image


def bbox(mask):
    """Outer wall contour: rows/cols that contain a substantial amount of wall pixels
    (ignores thin dark objects such as door leaves outside the apartment)."""
    cols = mask.sum(axis=0)
    rows = mask.sum(axis=1)
    xs = np.where(cols > 0.25 * cols.max())[0]
    ys = np.where(rows > 0.25 * rows.max())[0]
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def main(plan_p, render_p, out_p, flip=False):
    src = Image.open(plan_p).convert("RGBA")
    bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    plan = np.asarray(Image.alpha_composite(bg, src).convert("RGB")).astype(int)
    rend_img = Image.open(render_p).convert("RGB")
    rend = np.asarray(rend_img).astype(int)

    # plan walls: dark neutral grey fill; plan lines: any darker pixel
    pr, pg, pb = plan[..., 0], plan[..., 1], plan[..., 2]
    plan_walls = (pr < 90) & (abs(pr - pg) < 12) & (abs(pg - pb) < 12)
    plan_lines = (pr + pg + pb) / 3 < 170
    # render walls: near black
    rend_walls = rend.max(axis=2) < 45

    px0, py0, px1, py1 = bbox(plan_walls)
    rx0, ry0, rx1, ry1 = bbox(rend_walls)

    W, H = 1400, int(1400 * (py1 - py0) / (px1 - px0))
    def norm(img_arr_or_mask, box, is_mask):
        x0, y0, x1, y1 = box
        crop = img_arr_or_mask[y0:y1, x0:x1]
        im = Image.fromarray((crop * 255).astype(np.uint8) if is_mask else crop.astype(np.uint8))
        return np.asarray(im.resize((W, H), Image.NEAREST if is_mask else Image.LANCZOS))

    pw = norm(plan_walls, (px0, py0, px1, py1), True) > 127
    pl = norm(plan_lines, (px0, py0, px1, py1), True) > 127
    rw = norm(rend_walls, (rx0, ry0, rx1, ry1), True) > 127
    rimg = norm(rend, (rx0, ry0, rx1, ry1), False)

    iou = (pw & rw).sum() / max((pw | rw).sum(), 1)
    out = (rimg * 0.55).astype(np.uint8)
    out[pl] = [255, 40, 40]            # plan lines in red
    out[rw & ~pw] = [0, 170, 255]      # walls in render but not in plan: blue
    Image.fromarray(out).save(out_p, quality=92)
    print(f"wall IoU={iou:.3f}  plan bbox aspect={(px1-px0)/(py1-py0):.3f}  render bbox aspect={(rx1-rx0)/(ry1-ry0):.3f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
