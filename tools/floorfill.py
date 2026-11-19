"""Remove an object from a parquet floor with vertical planks by rebuilding the floor plank column by plank column.

For every plank column that crosses the object box:
  * the cut rows are real plank joints of that column found above and below the box (so no artificial edge appears),
  * the segment between the joints is copied from another plank column of the same rows (offset by a whole number of
    planks) that contains only clean floor (no dark or saturated pixels) and whose brightness matches best,
  * a linear gain along the column blends the copied segment into the light just above and below the cuts.

fill(a, box, pitch, ...) works in pixel coordinates of the image array a (float32, modified in place)."""
import cv2
import numpy as np


def plank_edges(a, x0, x1, y0, y1, pitch):
    """x positions of the vertical plank seams between x0 and x1, estimated on rows y0..y1 (clean floor rows)."""
    g = cv2.GaussianBlur(a[y0:y1].mean(axis=2), (0, 0), 1.2)
    gx = np.abs(np.diff(g, axis=1)).mean(axis=0)
    # phase of the seam grid: maximise the gradient energy on a comb with the given pitch
    best = max(np.arange(0, pitch, 0.5), key=lambda ph: sum(gx[int(round(p))] for p in np.arange(ph + x0 - x0 % 1, x1, pitch) if 0 <= int(round(p)) < len(gx)))
    return [p for p in np.arange(best, gx.shape[0] if False else x1 + pitch, pitch)]


def joints(col, y_from, y_to, step):
    """rows of horizontal plank joints (dark lines) in a column strip between y_from and y_to (step = search direction)."""
    prof = col.mean(axis=(1, 2))
    base = cv2.GaussianBlur(prof.reshape(-1, 1), (1, 0), sigmaX=0.1, sigmaY=6).ravel()
    dip = base - prof
    rng = range(y_from, y_to, step)
    for y in rng:
        if 0 < y < len(prof) - 1 and dip[y] > 9 and dip[y] >= dip[y - 1] and dip[y] >= dip[y + 1]:
            return y
    return None


def fill(a, box, pitch, clean=None, max_reach=None, offsets=range(-12, 13), dark=70, avoid=(), ylim=None, xlim=None):
    """box = (x0, y0, x1, y1) px of the object (with its shadow); pitch = plank width px; avoid = boxes (px) that
    must not be used as a source (other objects)."""
    x0, y0, x1, y1 = box
    max_reach = max_reach or int(pitch * 6)
    src = a.copy()
    ok = src.max(axis=2) > dark
    hsv = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    for bx in avoid:
        ok[bx[1]:bx[3], bx[0]:bx[2]] = False
    ok[y0:y1, x0:x1] = False
    # seams: detect on the rows just above the box
    ref_rows = (max(0, y0 - int(pitch * 3)), max(1, y0 - 4))
    g = cv2.GaussianBlur(src[ref_rows[0]:ref_rows[1]].mean(axis=2), (0, 0), 1.0)
    gx = np.abs(np.diff(g, axis=1)).mean(axis=0)
    phases = np.arange(0, pitch, 0.5)
    def energy(ph):
        ps = np.arange(x0 - pitch * 2 + ((ph - (x0 - pitch * 2)) % pitch), x1 + pitch * 2, pitch)
        return sum(gx[int(round(p))] for p in ps if 0 <= int(round(p)) < len(gx))
    ph = max(phases, key=energy)
    first = x0 - pitch * 2 + ((ph - (x0 - pitch * 2)) % pitch)
    seams = [p for p in np.arange(first, x1 + pitch * 2, pitch)]
    cols = [(s0, s1) for s0, s1 in zip(seams[:-1], seams[1:]) if s1 > x0 and s0 < x1]
    for s0, s1 in cols:
        c0, c1 = int(round(s0)) + 1, int(round(s1)) - 1
        if xlim:
            c0, c1 = max(c0, xlim[0]), min(c1, xlim[1])
            if c1 - c0 < 3:
                continue
        strip = src[:, c0:c1]
        top = joints(strip, y0 - 8, max(0, y0 - max_reach), -1)
        bot = joints(strip, y1 + 8, min(a.shape[0] - 1, y1 + max_reach), 1)
        top = top if top is not None else y0 - 2
        bot = bot if bot is not None else y1 + 2
        t, b = top + 2, bot - 1                               # keep the target's joint lines themselves
        top_free, bot_free = True, True
        if ylim:
            if t < ylim[0]: t, top_free = ylim[0], False
            if b > ylim[1]: b, bot_free = ylim[1], False
        best, best_err = None, 1e18
        for k in offsets:
            if k == 0:
                continue
            dx = int(round(k * pitch))
            if c0 + dx < 0 or c1 + dx > a.shape[1]:
                continue
            if not ok[t:b, c0 + dx:c1 + dx].all():
                continue
            seg = src[t:b, c0 + dx:c1 + dx]
            if int(hsv[t:b, c0 + dx:c1 + dx, 1].max()) > int(hsv[max(0, t - 30):t, c0:c1, 1].max()) + 40:
                continue
            above = src[max(0, t - 8):t, c0:c1].mean(axis=(0, 1))
            below = src[b:b + 8, c0:c1].mean(axis=(0, 1))
            err = np.abs(seg[:8].mean(axis=(0, 1)) - above).sum() + np.abs(seg[-8:].mean(axis=(0, 1)) - below).sum()
            if err < best_err:
                best, best_err = dx, err
        if best is None:
            continue
        seg = src[t:b, c0 + best:c1 + best].copy()
        above = src[max(0, t - 8):t, c0:c1].mean(axis=(0, 1))
        below = src[b:b + 8, c0:c1].mean(axis=(0, 1))
        g_top = above / np.maximum(seg[:8].mean(axis=(0, 1)), 1)
        g_bot = below / np.maximum(seg[-8:].mean(axis=(0, 1)), 1)
        if not bot_free: g_bot = g_top
        if not top_free: g_top = g_bot
        w = np.linspace(0, 1, b - t)[:, None, None]
        # strip the source column's own shading (cast shadows of other objects) and give it the target's shading:
        # a straight blend between the light just above and just below the cut
        # 2D low-pass inside the column (shadows are soft, grain is fine) -> keep only the grain
        prof = cv2.GaussianBlur(seg, (0, 0), max(3, pitch * 0.45), borderType=cv2.BORDER_REFLECT)
        detail = seg / np.maximum(prof, 1)
        detail = detail * (1 + 0.04 * (np.random.default_rng(c0).random() - 0.5))   # slight per-plank tone
        tgt = above[None, None, :] * (1 - w) + below[None, None, :] * w
        if not bot_free: tgt = np.broadcast_to(above[None, None, :], tgt.shape)
        if not top_free: tgt = np.broadcast_to(below[None, None, :], tgt.shape)
        a[t:b, c0:c1] = detail * tgt
        # seams themselves (1-2 px between columns) inside the box: copy from the same offset
        for sx in (int(round(s0)) - 1, int(round(s0)), int(round(s0)) + 1):
            if x0 - 2 <= sx <= x1 + 2 and (not xlim or xlim[0] <= sx < xlim[1]):
                sc = src[t:b, sx + best]
                pr = cv2.GaussianBlur(sc.reshape(-1, 1, 3), (1, 0), sigmaX=0.1, sigmaY=max(4, pitch * 0.8)).reshape(-1, 3)
                a[t:b, sx] = sc / np.maximum(pr, 1) * tgt[:, 0] * 0.93
    return a
