"""Small deterministic painters: door leaf seen from above, washer top facing any side."""
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw

import paint_fridge


def door_leaf(a, hinge, length, angle, thick, color=(128, 86, 58), shadow=True):
    """walnut door leaf (px units) from hinge along angle (deg, 0 = +x, 90 = +y/down), with a soft floor shadow."""
    hx, hy = hinge
    an = math.radians(angle)
    ex, ey = hx + math.cos(an) * length, hy + math.sin(an) * length
    nx, ny = -math.sin(an) * thick / 2, math.cos(an) * thick / 2
    poly = [(hx + nx, hy + ny), (ex + nx, ey + ny), (ex - nx, ey - ny), (hx - nx, hy - ny)]
    h, w = a.shape[:2]
    out = a.astype(np.float32)
    if shadow:
        m = Image.new("L", (w, h), 0)
        off = thick * 0.9
        ImageDraw.Draw(m).polygon([(x + off * 0.6, y + off) for x, y in poly], fill=255)
        sh = cv2.GaussianBlur(np.asarray(m).astype(np.float32) / 255, (0, 0), thick * 0.8)
        out *= (1 - 0.45 * sh)[..., None]
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in poly], fill=255)
    f = np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    # shading across the leaf thickness (light edge on one side)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = ((xx - hx) * -math.sin(an) + (yy - hy) * math.cos(an)) / max(thick / 2, 1)
    shade = np.clip(1.0 - 0.18 * t, 0.75, 1.15)
    col = np.array(color, np.float32)[None, None, :] * shade[..., None]
    out = out * (1 - f[..., None]) + col * f[..., None]
    a[...] = np.clip(out, 0, 255).astype(a.dtype)
    return a


def washer_top(a, box, front="down"):
    """front: side where the machine's door/drawer is (towards the room)."""
    x0, y0, x1, y1 = box
    pad = 40
    X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(a.shape[1], x1 + pad), min(a.shape[0], y1 + pad)
    sub = np.ascontiguousarray(a[Y0:Y1, X0:X1])
    k = {"up": 0, "left": 1, "down": 2, "right": 3}[front]
    r = np.ascontiguousarray(np.rot90(sub, k))
    # box inside the rotated sub-image
    bx = np.array([[x0 - X0, y0 - Y0], [x1 - X0, y1 - Y0]], np.float32)
    H, W = sub.shape[:2]
    for _ in range(k):  # rotate coordinates CCW 90: (x, y) -> (y, W - x)
        bx = np.array([[p[1], W - p[0]] for p in bx], np.float32); H, W = W, H
    bx0, by0 = int(bx[:, 0].min()), int(bx[:, 1].min()); bx1, by1 = int(bx[:, 0].max()), int(bx[:, 1].max())
    paint_fridge.paint_washer_top(r, (bx0, by0, bx1, by1), front="up")
    a[Y0:Y1, X0:X1] = np.rot90(r, -k)
    return a


def ledge(a, box, side="left", items=True, seed=2):
    """installation ledge behind a wall-hung toilet: light stone top with bevel, soft shadow on the floor,
    a few toiletries (small bottles / jar) on it. side = wall the ledge stands against."""
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = [int(v) for v in box]
    out = a.astype(np.float32)
    w, h = x1 - x0, y1 - y0
    sh = np.zeros(out.shape[:2], np.float32)
    d = max(4, min(w, h) // 5)
    dx, dy = {"left": (d, d // 2), "right": (-d, d // 2), "top": (d // 2, d), "bottom": (d // 2, -d)}[side]
    sh[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = 1
    out *= (1 - 0.35 * cv2.GaussianBlur(sh, (0, 0), d))[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = np.array([226, 220, 210], np.float32)
    g = 0.95 + 0.05 * (1 - xx / w) + 0.01 * cv2.GaussianBlur(rng.standard_normal((h, w)).astype(np.float32), (0, 0), 2)
    top = base[None, None, :] * g[..., None]
    b = max(2, min(w, h) // 12)
    edge = np.maximum(np.clip(1 - (w - 1 - xx) / b, 0, 1), np.clip(1 - (h - 1 - yy) / b, 0, 1))
    top *= (1 - 0.18 * edge)[..., None]
    out[y0:y1, x0:x1] = top
    if items:
        along_y = h > w
        L = h if along_y else w
        for k, (col, r) in enumerate([((70, 88, 72), 0.26), ((236, 232, 226), 0.22), ((150, 120, 92), 0.2)]):
            c = 0.2 + 0.15 * k
            cx, cy = (x0 + w / 2, y0 + L * c) if along_y else (x0 + L * c, y0 + h / 2)
            rr = min(w, h) * r
            m = Image.new("L", (out.shape[1], out.shape[0]), 0)
            ImageDraw.Draw(m).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255)
            f = cv2.GaussianBlur(np.asarray(m).astype(np.float32) / 255, (0, 0), 0.8)
            s2 = cv2.GaussianBlur(np.roll(np.roll(f, int(rr * 0.5), 0), int(rr * 0.4), 1), (0, 0), rr * 0.4)
            out *= (1 - 0.3 * s2)[..., None]
            shade = np.clip(1.1 - 0.35 * np.hypot(xx.mean() * 0 + (np.mgrid[0:out.shape[0], 0:out.shape[1]][1] - cx + rr * 0.3), (np.mgrid[0:out.shape[0], 0:out.shape[1]][0] - cy + rr * 0.3)) / max(rr, 1), 0.6, 1.15)
            out = out * (1 - f[..., None]) + (np.array(col, np.float32)[None, None, :] * shade[..., None]) * f[..., None]
    a[...] = np.clip(out, 0, 255).astype(a.dtype)
    return a


def redo_entrance(a, erase_box, thr_box, hinge, angle, length, thick):
    """remove a wrongly drawn entrance door leaf (outside the apartment on white) and draw the right one.
    erase_box: area outside the wall to paint white; thr_box: strip of the opening inside the wall line that the
    old leaf crossed -> refilled with the floor rows just above it."""
    x0, y0, x1, y1 = [int(v) for v in erase_box]
    a[y0:y1, x0:x1] = 255
    tx0, ty0, tx1, ty1 = [int(v) for v in thr_box]
    h = ty1 - ty0
    a[ty0:ty1, tx0:tx1] = a[ty0 - h:ty0, tx0:tx1]
    door_leaf(a, hinge, length, angle, thick, color=(44, 40, 38))
    return a


def match_wood(arr, target_rgb, sat_min=0.28):
    """shift the wood (warm, saturated) pixels of an asset towards a target mean colour; fabrics stay as they are."""
    import colorsys
    a = arr.astype(np.float32)
    hsv = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s = hsv[..., 0] * 2, hsv[..., 1] / 255
    wood = ((h < 40) | (h > 340)) & (s > sat_min) & (hsv[..., 2] > 40)
    m = cv2.GaussianBlur(wood.astype(np.float32), (0, 0), 2)[..., None]
    gain = np.array(target_rgb, np.float32) / np.maximum(a[wood].mean(0), 1)
    out = a * (1 - m) + np.clip(a * gain, 0, 255) * m
    arr[...] = out.astype(arr.dtype)
    return arr


def metal_door(a, hinge, length, angle, thick, color=(46, 42, 40), handle=True):
    """entrance door seen from above: dark metal leaf with a lighter top edge line, rounded ends, chrome lever handle
    near the free end on both faces, soft contact shadow."""
    hx, hy = hinge
    an = math.radians(angle)
    ux, uy = math.cos(an), math.sin(an)            # along the leaf
    nx, ny = -uy, ux                               # across the leaf
    h, w = a.shape[:2]
    out = a.astype(np.float32)
    ex, ey = hx + ux * length, hy + uy * length
    # soft shadow (light from the upper left)
    sh = Image.new("L", (w, h), 0)
    off = thick * 0.8
    ImageDraw.Draw(sh).line([(hx + off, hy + off), (ex + off, ey + off)], fill=255, width=int(thick * 1.1))
    shm = cv2.GaussianBlur(np.asarray(sh).astype(np.float32) / 255, (0, 0), thick * 0.9)
    out *= (1 - 0.35 * shm)[..., None]
    # leaf body with shading across the thickness
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx - hx) * ux + (yy - hy) * uy
    v = (xx - hx) * nx + (yy - hy) * ny
    body = np.clip(np.minimum(thick / 2 - np.abs(v), np.minimum(u, length - u)) + 0.5, 0, 1)
    tv = v / (thick / 2)
    shade = 0.78 + 0.3 * (1 - tv) / 2 + 0.55 * np.exp(-((tv + 0.6) / 0.1) ** 2)   # bevel highlight line near one face
    col = np.array(color, np.float32)[None, None, :] * shade[..., None]
    out = out * (1 - body[..., None]) + col * body[..., None]
    if handle:
        hw = max(3, int(thick * 0.3))
        for side in (-1, 1):
            bx = hx + ux * (length - thick * 1.4); by = hy + uy * (length - thick * 1.4)          # rose on the leaf face
            fx, fy = bx + nx * side * thick / 2, by + ny * side * thick / 2
            px_, py_ = fx + nx * side * thick * 0.35, fy + ny * side * thick * 0.35            # lever off the face
            hm = Image.new("L", (w, h), 0); dr = ImageDraw.Draw(hm)
            dr.line([(fx, fy), (px_, py_)], fill=255, width=hw)                                # connector
            dr.line([(px_, py_), (px_ - ux * thick * 2.0, py_ - uy * thick * 2.0)], fill=255, width=hw)   # lever along the leaf
            hmf = cv2.GaussianBlur(np.asarray(hm).astype(np.float32) / 255, (0, 0), 0.8)[..., None]
            out = out * (1 - hmf) + np.array([128, 127, 124], np.float32) * hmf
    a[...] = np.clip(out, 0, 255).astype(a.dtype)
    return a
