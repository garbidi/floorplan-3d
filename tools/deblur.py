"""Repair AI-generated 'blur squares' on parquet: regions where the wood grain was smoothed away.
Each blurred patch keeps its own low-frequency light/shadow and gets the fine grain (high-pass) of the same plank
columns taken from a sharp place above/below it (planks run vertically)."""
import numpy as np, cv2


def sharpness(g, win=61):
    hp = np.abs(g - cv2.GaussianBlur(g, (0, 0), 2))
    return cv2.blur(hp, (win, win))


def parquet_mask(a):
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    return (h < 22) & (s > 30) & (s < 140) & (v > 90)


def repair(a, protect=None, pct=12, min_area=2500, grow=10, sigma=6, verbose=True):
    """a: float32/uint8 RGB. protect: bool mask of pixels never to touch. Returns float32 image."""
    a = a.astype(np.float32)
    g = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    e = sharpness(g)
    floor = parquet_mask(a)
    if protect is not None: floor &= ~protect
    thr = np.percentile(e[floor], pct)
    sharp_thr = np.percentile(e[floor], 45); busy_thr = np.percentile(e[floor], 93)
    low = ((e < thr) & floor).astype(np.uint8)
    low = cv2.morphologyEx(low, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(low)
    H, W = g.shape
    fixed = 0
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area < min_area or area < 0.35 * w * h:          # only compact, patch-like regions
            continue
        x0, y0, x1, y1 = max(0, x - grow), max(0, y - grow), min(W, x + w + grow), min(H, y + h + grow)
        hh = y1 - y0
        src = None
        ww = x1 - x0
        cands = [(0, -(hh + 8)), (0, hh + 8), (0, -2 * (hh + 8)), (0, 2 * (hh + 8)), (-(ww + 8), 0), (ww + 8, 0), (-2 * (ww + 8), 0), (2 * (ww + 8), 0)]
        for dx, dy in cands:
            sy0, sy1, sx0, sx1 = y0 + dy, y1 + dy, x0 + dx, x1 + dx
            if sy0 < 0 or sy1 > H or sx0 < 0 or sx1 > W: continue
            if floor[sy0:sy1, sx0:sx1].mean() > 0.8 and e[sy0:sy1, sx0:sx1].mean() > sharp_thr and e[sy0:sy1, sx0:sx1].max() < busy_thr:
                src = a[sy0:sy1, sx0:sx1]; break
        if src is None:                                   # any clean sharp parquet patch of the same size elsewhere
            best = None
            for sy0 in range(0, H - hh, max(20, hh // 3)):
                for sx0 in range(0, W - ww, max(20, ww // 3)):
                    fm = floor[sy0:sy0 + hh, sx0:sx0 + ww].mean()
                    if fm < 0.95: continue
                    ee = e[sy0:sy0 + hh, sx0:sx0 + ww]
                    if ee.max() >= busy_thr or ee.mean() <= sharp_thr: continue
                    d = abs(sy0 - y0) + abs(sx0 - x0)
                    if best is None or d < best[0]: best = (d, sy0, sx0)
            if best is None: continue
            src = a[best[1]:best[1] + hh, best[2]:best[2] + ww]
        tgt = a[y0:y1, x0:x1]
        detail = src - cv2.GaussianBlur(src, (0, 0), sigma)
        base = cv2.GaussianBlur(tgt, (0, 0), sigma)
        new = base + detail
        m = np.zeros((hh, x1 - x0), np.float32)
        m[(lab[y0:y1, x0:x1] == i)] = 1
        m = cv2.dilate(m, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))
        m = cv2.GaussianBlur(m, (0, 0), grow / 2) * floor[y0:y1, x0:x1]
        a[y0:y1, x0:x1] = tgt * (1 - m[..., None]) + new * m[..., None]
        fixed += 1
    if verbose: print('deblur patches fixed:', fixed, flush=True)
    return a


def protect_from_scene(scene_json, shape, planw, pad=12):
    """bool mask of all furniture / fixtures of the plan scene (plan px -> image px), dilated."""
    import json
    sc = json.load(open(scene_json)); K = shape[1] / planw
    m = np.zeros(shape[:2], bool)
    for it in sc['items']:
        b = it.get('box')
        if not b: continue
        x0, y0, x1, y1 = [int(round(v * K)) for v in b]; p = int(pad * K)
        m[max(0, y0 - p):y1 + p, max(0, x0 - p):x1 + p] = True
    return m
