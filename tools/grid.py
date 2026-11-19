"""Draw a %-grid relative to the plan's outer wall contour, to read object coordinates.
Usage: python3 grid.py <plan.png> <out.png> [x0 y0 x1 y1 (crop in %, optional)]
Prints the outer contour bbox in pixels and as % of the canvas.
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from overlay import bbox  # noqa: E402


def load_plan(p):
    src = Image.open(p).convert("RGBA")
    bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, src).convert("RGB")


def main(plan_p, out_p, crop=None):
    im = load_plan(plan_p)
    a = np.asarray(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    walls = (r < 90) & (abs(r - g) < 12) & (abs(g - b) < 12)
    x0, y0, x1, y1 = bbox(walls)
    W, H = im.size
    print(f"canvas {W}x{H}; outer contour px x {x0}-{x1}, y {y0}-{y1}; "
          f"canvas% x {100*x0/W:.1f}-{100*x1/W:.1f}, y {100*y0/H:.1f}-{100*y1/H:.1f}; "
          f"contour aspect w/h {(x1-x0)/(y1-y0):.3f}")
    if crop:
        cx0, cy0, cx1, cy1 = crop
        box = (int(x0 + (x1 - x0) * cx0 / 100), int(y0 + (y1 - y0) * cy0 / 100),
               int(x0 + (x1 - x0) * cx1 / 100), int(y0 + (y1 - y0) * cy1 / 100))
    else:
        cx0, cy0, cx1, cy1 = -3, -3, 103, 103
        box = (int(x0 + (x1 - x0) * cx0 / 100), int(y0 + (y1 - y0) * cy0 / 100),
               int(x0 + (x1 - x0) * cx1 / 100), int(y0 + (y1 - y0) * cy1 / 100))
    im = im.crop(box)
    scale = 1800 / im.size[0]
    im = im.resize((1800, int(im.size[1] * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    step = 1 if (cx1 - cx0) <= 30 else (2 if (cx1 - cx0) <= 60 else 5)
    for p in range(0, 101, step):
        X = ((x0 + (x1 - x0) * p / 100) - box[0]) * scale
        Y = ((y0 + (y1 - y0) * p / 100) - box[1]) * scale
        major = p % (5 * step if step < 5 else 10) == 0
        col = (0, 120, 255) if major else (150, 200, 255)
        if 0 <= X < im.size[0]:
            d.line([(X, 0), (X, im.size[1])], fill=col, width=2 if major else 1)
            if major:
                d.text((X + 2, 2), str(p), fill=(0, 60, 200), font=f)
        if 0 <= Y < im.size[1]:
            d.line([(0, Y), (im.size[0], Y)], fill=col, width=2 if major else 1)
            if major:
                d.text((2, Y + 2), str(p), fill=(200, 0, 0), font=f)
    im.save(out_p)


if __name__ == "__main__":
    c = [float(v) for v in sys.argv[3:7]] if len(sys.argv) >= 7 else None
    main(sys.argv[1], sys.argv[2], c)
