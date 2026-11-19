"""Top-down stainless-steel fridge painted into a render: brushed top, bevelled edges, door gap,
bar handle on the door side and a soft drop shadow (the fridge is taller than the counters).

paint_into(arr, box, front='right') modifies arr (H x W x 3 uint8) in place.
"""
import numpy as np
from scipy import ndimage

SS = 3


def paint_into(arr, box, front="right", seed=3, back_rgb=(24, 24, 24)):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # drop shadow on the floor (light from upper left): darken a blurred offset rectangle
    pad = 60
    ya, yb, xa, xb = max(0, y0 - pad), min(arr.shape[0], y1 + pad), max(0, x0 - pad), min(arr.shape[1], x1 + pad)
    m = np.zeros((yb - ya, xb - xa))
    m[y0 - ya + 10:y1 - ya + 16, x0 - xa + 12:x1 - xa + 20] = 1
    m = ndimage.gaussian_filter(m, 12)
    reg = arr[ya:yb, xa:xb].astype(float)
    reg *= (1 - 0.6 * m)[..., None]
    arr[ya:yb, xa:xb] = np.clip(reg, 0, 255).astype(np.uint8)

    W, H = w * SS, h * SS
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    # brushed steel: fine streaks along the depth axis (perpendicular to the front)
    along_x = front in ("right", "left")
    n = rng.standard_normal(W if not along_x else H)
    streak = ndimage.gaussian_filter1d(n, 0.8) * 0.5 + ndimage.gaussian_filter1d(rng.standard_normal(n.size), 6) * 1.2
    streak = streak[None, :] if not along_x else streak[:, None]
    base = np.array([204, 198, 188]) / 255.0
    # soft reflection gradient across the top + streaks
    g = 0.84 + 0.2 * (1 - xx / W) * (1 - yy / H) + 0.018 * streak
    img = base * g[..., None]
    # bevel: light on top/left edges, dark on bottom/right
    b = 5 * SS
    e_l, e_t = np.clip(1 - xx / b, 0, 1), np.clip(1 - yy / b, 0, 1)
    e_r, e_b = np.clip(1 - (W - 1 - xx) / b, 0, 1), np.clip(1 - (H - 1 - yy) / b, 0, 1)
    img *= (1 + 0.12 * np.maximum(e_l, e_t) - 0.28 * np.maximum(e_r, e_b))[..., None]
    # dark ventilation strip at the back, door gap near the front
    if front == "right":
        img[:, 2 * SS:12 * SS] *= 0.85
        for k in range(4 * SS, H - 4 * SS, 5 * SS):
            img[k:k + 2 * SS, 3 * SS:11 * SS] = np.array(back_rgb) / 255.0
        gx = W - 16 * SS
        img[:, gx:gx + SS] *= 0.35
        img[:, gx + SS:gx + 2 * SS] *= 1.15
        # bar handle standing off the door: two stand-offs + round bar with highlight
        hx = W + 0  # handle drawn outside the box, see below
    img = np.clip(img, 0, 1)
    from PIL import Image
    top = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS))
    arr[y0:y1, x0:x1] = top
    if front == "right":
        hy0, hy1 = y0 + int(h * 0.18), y1 - int(h * 0.18)
        hx = x1 + 6
        # handle shadow
        sh = np.zeros((hy1 - hy0 + 40, 40))
        sh[20:-12, 12:22] = 1
        sh = ndimage.gaussian_filter(sh, 5)
        reg = arr[hy0 - 14:hy1 + 26, hx - 8:hx + 32].astype(float)
        reg *= (1 - 0.5 * sh[: reg.shape[0], : reg.shape[1]])[..., None]
        arr[hy0 - 14:hy1 + 26, hx - 8:hx + 32] = reg.astype(np.uint8)
        # stand-offs
        for yy_ in (hy0 + 6, hy1 - 12):
            arr[yy_:yy_ + 8, x1 - 1:hx + 2] = (150, 150, 148)
        # bar: cylinder shading across its width
        bw = 9
        prof = np.clip(1 - ((np.arange(bw) - bw * 0.35) / (bw * 0.6)) ** 2, 0, 1)
        col = (110 + 140 * prof)[None, :, None] * np.array([1, 1, 0.98])
        arr[hy0:hy1, hx:hx + bw] = np.clip(col, 0, 255).astype(np.uint8)
    return arr


def paint_washer_top(arr, box, front="up", seed=4):
    """Front-loading washing machine seen strictly from above: white enamel top with a soft sheen,
    rounded edges, a thin seam of the top panel and a hint of the detergent drawer on the front edge."""
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    pad = 30
    ya, yb, xa, xb = max(0, y0 - pad), min(arr.shape[0], y1 + pad), max(0, x0 - pad), min(arr.shape[1], x1 + pad)
    m = np.zeros((yb - ya, xb - xa)); m[y0 - ya + 4:y1 - ya + 6, x0 - xa + 5:x1 - xa + 8] = 1
    m = ndimage.gaussian_filter(m, 6)
    reg = arr[ya:yb, xa:xb].astype(float); reg *= (1 - 0.45 * m)[..., None]
    arr[ya:yb, xa:xb] = np.clip(reg, 0, 255).astype(np.uint8)
    W, H = w * SS, h * SS
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = np.array([238, 236, 231]) / 255.0
    g = 0.9 + 0.1 * (1 - xx / W) * (1 - yy / H) + 0.004 * ndimage.gaussian_filter(rng.standard_normal((H, W)), 2)
    img = base * g[..., None]
    b = 4 * SS
    e_l, e_t = np.clip(1 - xx / b, 0, 1), np.clip(1 - yy / b, 0, 1)
    e_r, e_b = np.clip(1 - (W - 1 - xx) / b, 0, 1), np.clip(1 - (H - 1 - yy) / b, 0, 1)
    img *= (1 + 0.06 * np.maximum(e_l, e_t) - 0.22 * np.maximum(e_r, e_b))[..., None]
    if front == "up":   # seam of the top panel near the front edge + detergent drawer outline at front-left
        sy = int(H * 0.1)
        img[sy:sy + SS] *= 0.8
        img[sy + SS:sy + 2 * SS] *= 1.03
        dx0, dx1 = int(W * 0.06), int(W * 0.38)
        img[b:sy - SS, dx0:dx0 + SS] *= 0.85; img[b:sy - SS, dx1:dx1 + SS] *= 0.85
    img = np.clip(img, 0, 1)
    from PIL import Image
    arr[y0:y1, x0:x1] = np.asarray(Image.fromarray((img * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS))
    return arr
