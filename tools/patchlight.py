"""Light matching for copied floor patches: the smooth shading inside a patched box is replaced by a membrane
(harmonic) interpolation of the shading of the untouched floor around it, so a copied patch takes over the local
light gradient (wall shadows, lamp glow) and no rectangle is visible. Dark pixels (walls, door leaves) are ignored."""
import cv2
import numpy as np


def nconv(img, w, s):
    return cv2.GaussianBlur(img * w[..., None], (0, 0), s) / np.maximum(cv2.GaussianBlur(w, (0, 0), s), 1e-4)[..., None]


def match(a, orig, box_px, s=10, pad=60, dark=60):
    """a: patched float image (modified in place); orig: image before patching; box_px: (x0,y0,x1,y1) in px."""
    x0, y0, x1, y1 = box_px
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(a.shape[1], x1 + pad), min(a.shape[0], y1 + pad)
    reg, org = a[Y0:Y1, X0:X1], orig[Y0:Y1, X0:X1]
    inside = np.zeros(reg.shape[:2], np.float32); inside[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = 1
    floor_new = (reg.max(axis=2) > dark).astype(np.float32)
    floor_old = (org.max(axis=2) > dark).astype(np.float32)
    cur = nconv(reg, inside * floor_new, s)                       # smooth shading of the patch itself
    sur = nconv(org, (1 - inside) * floor_old, s)                 # smooth shading of the surrounding floor
    # membrane fill of the surrounding shading into the box (inpaint on a low-res copy, per channel)
    q = 0.25
    small = cv2.resize(sur, None, fx=q, fy=q, interpolation=cv2.INTER_AREA)
    m = cv2.resize(inside, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    m = cv2.dilate((m > 0).astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
    lo, hi = small.min(), small.max()
    s8 = ((small - lo) / max(hi - lo, 1) * 255).astype(np.uint8)
    fill = np.dstack([cv2.inpaint(s8[..., c], m, 6, cv2.INPAINT_NS) for c in range(3)]).astype(np.float32) / 255 * (hi - lo) + lo
    fill = cv2.GaussianBlur(cv2.resize(fill, (reg.shape[1], reg.shape[0]), interpolation=cv2.INTER_CUBIC), (0, 0), s / 2)
    g = np.clip(fill / np.maximum(cur, 1), 0.6, 1.6)
    f = cv2.GaussianBlur(inside, (0, 0), 3)[..., None] * floor_new[..., None]
    reg[:] = reg * (1 - f) + reg * g * f


def match_sides(a, box_px, sides=("l", "r", "t", "b"), strip=8, smooth=15):
    """Gain field for a copied patch from its borders: on each used side, gain = (floor just outside) / (patch just
    inside), smoothed along the side; inside the box the side gains are blended with inverse-distance weights.
    Use only sides that touch plain floor (not walls or furniture)."""
    x0, y0, x1, y1 = box_px
    reg = a[y0:y1, x0:x1]
    h, w = reg.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    num = np.zeros((h, w, 3), np.float32); den = np.zeros((h, w, 1), np.float32)

    def sm(v):
        return cv2.GaussianBlur(v.reshape(-1, 1, 3).astype(np.float32), (1, 0), sigmaX=0.1, sigmaY=smooth).reshape(-1, 3)
    for sd in sides:
        if sd == "l":
            g = sm(a[y0:y1, x0 - strip:x0].mean(1) / np.maximum(reg[:, :strip].mean(1), 1)); d = xx; G = g[:, None, :]
        elif sd == "r":
            g = sm(a[y0:y1, x1:x1 + strip].mean(1) / np.maximum(reg[:, -strip:].mean(1), 1)); d = w - 1 - xx; G = g[:, None, :]
        elif sd == "t":
            g = sm(a[y0 - strip:y0, x0:x1].mean(0) / np.maximum(reg[:strip].mean(0), 1)); d = yy; G = g[None, :, :]
        else:
            g = sm(a[y1:y1 + strip, x0:x1].mean(0) / np.maximum(reg[-strip:].mean(0), 1)); d = h - 1 - yy; G = g[None, :, :]
        wgt = 1.0 / (d + 3) ** 2
        num += G * wgt[..., None]; den += wgt[..., None]
    gain = np.clip(num / den, 0.6, 1.6)
    reg[:] = reg * gain
