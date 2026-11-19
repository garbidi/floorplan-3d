"""Deterministic fixes on a render using PLAN % coordinates (relative to the outer wall contour)."""
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from overlay import bbox  # noqa: E402


def contour(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    return bbox(a.max(axis=2) < 45)


def to_px(img, box, cb=None):
    x0, y0, x1, y1 = cb or contour(img)
    bx0, by0, bx1, by1 = box
    return (int(round(x0 + (x1 - x0) * bx0 / 100)), int(round(y0 + (y1 - y0) * by0 / 100)),
            int(round(x0 + (x1 - x0) * bx1 / 100)), int(round(y0 + (y1 - y0) * by1 / 100)))


def fill_black(src, boxes, out):
    im = Image.open(src).convert("RGB")
    cb = contour(im)
    a = np.asarray(im).copy()
    for b in boxes:
        x0, y0, x1, y1 = to_px(im, b, cb)
        a[y0:y1, x0:x1] = 0
    Image.fromarray(a).save(out, quality=97)


def crop_pct(src, box, out, pad=0):
    """Crop by plan % box (+pad %); returns pixel box."""
    im = Image.open(src).convert("RGB")
    b = to_px(im, (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
    im.crop(b).save(out, quality=97)
    return b


def paste_px(src, patch, pbox, out, inner_px=None, feather=6):
    from PIL import ImageDraw, ImageFilter
    im = Image.open(src).convert("RGB")
    p = Image.open(patch).convert("RGB").resize((pbox[2] - pbox[0], pbox[3] - pbox[1]), Image.LANCZOS)
    m = Image.new("L", p.size, 0)
    ib = inner_px or pbox
    ImageDraw.Draw(m).rectangle((ib[0] - pbox[0] + feather, ib[1] - pbox[1] + feather,
                                 ib[2] - pbox[0] - feather, ib[3] - pbox[1] - feather), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(feather))
    im.paste(p, pbox[:2], m)
    im.save(out, quality=97)


def seamless_fill(src, box_pct, out, dx_pct=2.5):
    """Fill box with pixels from the same rows shifted right by dx_pct, then correct tone with a
    per-row linear offset so the left/right edges match their neighbours (gradient-style blend)."""
    from scipy.ndimage import gaussian_filter1d
    im = Image.open(src).convert("RGB")
    cb = contour(im)
    x0, y0, x1, y1 = to_px(im, box_pct, cb)
    dx = int((cb[2] - cb[0]) * dx_pct / 100)
    a = np.asarray(im).astype(np.float32)
    patch = a[y0:y1, x0 + dx:x1 + dx].copy()
    L = a[y0:y1, x0 - 2:x0].mean(axis=1)
    R = a[y0:y1, x1:x1 + 2].mean(axis=1)
    dL = gaussian_filter1d(L - patch[:, :2].mean(axis=1), 6, axis=0)
    dR = gaussian_filter1d(R - patch[:, -2:].mean(axis=1), 6, axis=0)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]
    patch += dL[:, None, :] * (1 - t) + dR[:, None, :] * t
    a[y0:y1, x0:x1] = patch
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out, quality=97)


def poisson_patch(dst_arr, patch_arr, box_px, margin=2):
    """Blend patch into dst over box using Poisson (seamlessClone). Arrays are RGB uint8; returns new array."""
    import cv2
    x0, y0, x1, y1 = box_px
    src = dst_arr.copy()
    src[y0:y1, x0:x1] = patch_arr[:y1 - y0, :x1 - x0]
    mask = np.zeros(dst_arr.shape[:2], np.uint8)
    mask[y0 + margin:y1 - margin, x0 + margin:x1 - margin] = 255
    center = ((x0 + x1) // 2, (y0 + y1) // 2)
    out = cv2.seamlessClone(cv2.cvtColor(src, cv2.COLOR_RGB2BGR), cv2.cvtColor(dst_arr, cv2.COLOR_RGB2BGR),
                            mask, center, cv2.NORMAL_CLONE)
    return cv2.cvtColor(out, cv2.COLOR_BGR2RGB)
