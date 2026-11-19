"""Remove an object from a render with Gemini on a small crop, then paste back only the object area.
The crop is upscaled to the nearest supported aspect; the result is aligned back to the crop with ECC
(translation+scale) so plank seams line up, colour-matched on a ring around the mask and feather-pasted."""
import sys
import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, __file__.rsplit("/", 1)[0])
RATIOS = {"1:1": 1, "4:3": 4 / 3, "3:4": 3 / 4, "3:2": 1.5, "2:3": 2 / 3, "5:4": 1.25, "4:5": 0.8, "16:9": 16 / 9, "9:16": 9 / 16}


def remove_sparkle(res):
    """Gemini's 4-point star sits at about (0.90 w, 0.86 h): a small blob brighter than its surroundings.
    Search that window for the brightest compact blob relative to a median background and inpaint it."""
    h, w = res.shape[:2]
    y0, y1, x0, x1 = int(h * 0.76), int(h * 0.95), int(w * 0.84), int(w * 0.96)
    g = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY).astype(np.float32)
    reg = g[y0:y1, x0:x1]
    bg = cv2.medianBlur(res[y0:y1, x0:x1], 31)
    bg = cv2.cvtColor(bg, cv2.COLOR_RGB2GRAY).astype(np.float32)
    pos = np.clip(reg - bg, 0, None)
    s = max(6, int(min(w, h) * 0.022))
    k = cv2.boxFilter(pos, -1, (s, s))
    cy, cx = np.unravel_index(np.argmax(k), k.shape)
    r = int(s * 1.4)
    m = np.zeros((h, w), np.uint8)
    m[max(0, y0 + cy - r):y0 + cy + r, max(0, x0 + cx - r):x0 + cx + r] = 255
    return cv2.inpaint(res, m, 9, cv2.INPAINT_TELEA)


def crop_for(box, shape, pad=0):
    """expand box (px) to the nearest supported aspect, inside the image."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    name, r = min(RATIOS.items(), key=lambda kv: abs(np.log(kv[1] / (w / h))))
    if w / h < r:
        nw = int(h * r); x0 -= (nw - w) // 2; x1 = x0 + nw
    else:
        nh = int(w / r); y0 -= (nh - h) // 2; y1 = y0 + nh
    dx = max(0, -x0) - max(0, x1 - shape[1]); dy = max(0, -y0) - max(0, y1 - shape[0])
    return (x0 + dx, y0 + dy, x1 + dx, y1 + dy), name


def run(a, crop_box, mask_box, prompt, work, feather=8):
    import gem
    (cx0, cy0, cx1, cy1), asp = crop_for(crop_box, a.shape)
    crop = np.clip(a[cy0:cy1, cx0:cx1], 0, 255).astype(np.uint8)
    up = cv2.resize(crop, None, fx=max(1, 1400 / crop.shape[1]), fy=max(1, 1400 / crop.shape[1]), interpolation=cv2.INTER_CUBIC)
    Image.fromarray(up).save(work + "_in.png")
    r = gem.generate(prompt, [work + "_in.png"], work + "_out.png", aspect=asp)
    if not r:
        raise RuntimeError("gemini failed")
    return paste(a, crop_box=(cx0, cy0, cx1, cy1), mask_box=mask_box, out_png=work + "_out.png", feather=feather)


def paste(a, crop_box, mask_box, out_png, feather=8, min_ncc=0.35, gain=True, ignore_box=None):
    cx0, cy0, cx1, cy1 = crop_box
    crop = np.clip(a[cy0:cy1, cx0:cx1], 0, 255).astype(np.uint8)
    res = cv2.cvtColor(cv2.imread(out_png), cv2.COLOR_BGR2RGB)
    res = remove_sparkle(res)
    res = cv2.resize(res, (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_AREA)
    mx0, my0, mx1, my1 = [v - o for v, o in zip(mask_box, (cx0, cy0, cx0, cy0))]
    # align res to crop using everything outside the mask
    g1 = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY).astype(np.float32); g2 = cv2.cvtColor(res, cv2.COLOR_RGB2GRAY).astype(np.float32)
    wm = np.full(g1.shape, 255, np.uint8); wm[max(0, my0 - 20):my1 + 20, max(0, mx0 - 20):mx1 + 20] = 0
    if ignore_box is not None:                 # areas that changed on purpose (e.g. a removed object) are not used for alignment
        ix0, iy0, ix1, iy1 = [v - o for v, o in zip(ignore_box, (cx0, cy0, cx0, cy0))]
        wm[max(0, iy0):max(0, iy1), max(0, ix0):max(0, ix1)] = 0
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        _, warp = cv2.findTransformECC(g1, g2, warp, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), wm, 5)
        res = cv2.warpAffine(res, warp, (crop.shape[1], crop.shape[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    except cv2.error as e:
        print("ECC failed:", e)
    # alignment quality outside the mask (normalised cross-correlation of gradients)
    ga = cv2.Sobel(g1, cv2.CV_32F, 1, 1, ksize=3); gb = cv2.Sobel(cv2.cvtColor(res, cv2.COLOR_RGB2GRAY).astype(np.float32), cv2.CV_32F, 1, 1, ksize=3)
    sel = wm > 0
    ncc = float(np.corrcoef(ga[sel].ravel(), gb[sel].ravel())[0, 1])
    print("inpaint alignment ncc:", round(ncc, 3))
    if ncc < min_ncc:
        raise ValueError(f"bad alignment ({ncc:.2f})")
    res = res.astype(np.float32)
    # colour match on a ring around the mask
    ring = np.zeros(g1.shape, bool); ring[max(0, my0 - 25):my1 + 25, max(0, mx0 - 25):mx1 + 25] = True
    ring[max(0, my0):my1, max(0, mx0):mx1] = False
    gain_v = crop[ring].astype(np.float32).mean(0) / np.maximum(res[ring].mean(0), 1)
    if gain is True:
        res *= gain_v
    f = np.zeros(g1.shape, np.float32); f[max(0, my0):my1, max(0, mx0):mx1] = 1
    f = cv2.GaussianBlur(f, (0, 0), feather)[..., None]
    f = np.maximum(f, 0) * (cv2.GaussianBlur((np.pad(np.ones((max(1, my1 - my0), max(1, mx1 - mx0))), 0)), (0, 0), 1).mean() > 0)
    a[cy0:cy1, cx0:cx1] = a[cy0:cy1, cx0:cx1] * (1 - f) + res * f
    return warp
