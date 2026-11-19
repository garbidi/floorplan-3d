"""Local patch editing: crop a region, (re)generate it elsewhere, paste it back with a feathered mask.
Boxes are given in 'preview' coordinates of a 1200-px-wide version of the image (scale factor applied here).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PREVIEW_W = 1200


def _box(im, box):
    k = im.size[0] / PREVIEW_W
    return tuple(int(round(v * k)) for v in box)


def crop(src, box, out):
    im = Image.open(src).convert("RGB")
    b = _box(im, box)
    im.crop(b).save(out, quality=97)
    return b


def paste(src, patch, box, out, inner=None, feather=6):
    """Paste `patch` (any size, resized to box) into `src` at `box`.
    Only the `inner` sub-box (preview coords) is replaced; its edge is feathered."""
    im = Image.open(src).convert("RGB")
    b = _box(im, box)
    p = Image.open(patch).convert("RGB").resize((b[2] - b[0], b[3] - b[1]), Image.LANCZOS)
    mask = Image.new("L", p.size, 0)
    ib = _box(im, inner) if inner else b
    k_f = int(feather * im.size[0] / PREVIEW_W)
    ImageDraw.Draw(mask).rectangle((ib[0] - b[0] + k_f, ib[1] - b[1] + k_f, ib[2] - b[0] - k_f, ib[3] - b[1] - k_f), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(k_f))
    im.paste(p, (b[0], b[1]), mask)
    im.save(out, quality=97)


def shaft(src, box, out, pipe_rel=(0.5, 0.72), pipe_r=0.32):
    """Draw a closed technical shaft: flat matte black box with a grey riser pipe seen from above."""
    im = Image.open(src).convert("RGB")
    b = _box(im, box)
    w, h = b[2] - b[0], b[3] - b[1]
    layer = np.zeros((h, w, 3), dtype=np.float32) + 17  # #111
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy, r = pipe_rel[0] * w, pipe_rel[1] * h, pipe_r * w
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring = (d <= r) & (d >= r * 0.72)
    inner = d < r * 0.72
    shade = 1 - 0.35 * ((xx - cx) + (yy - cy)) / (2 * r)  # soft light from top-left
    layer[ring] = np.stack([150 * shade, 150 * shade, 152 * shade], -1)[ring]
    layer[inner] = 38
    img = Image.fromarray(np.clip(layer, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
    im.paste(img, (b[0], b[1]))
    im.save(out, quality=97)
