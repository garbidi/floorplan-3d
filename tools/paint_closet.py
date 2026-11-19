"""Procedural top-down wardrobe interior: garments on hangers seen strictly from above.

Each garment is a small height field (shoulder ridge + draped body with folds + fabric weave),
lit with a warm top light, casting a soft shadow on its neighbour. Then a wooden hanger,
chrome rail and hook go on top. Painted at SS x resolution and downsampled for anti-aliasing.

paint(w, h, dividers, seed) -> RGB uint8 array (w across the wardrobe depth, h along the rail).
"""
import numpy as np
from PIL import Image
from scipy import ndimage

SS = 3
PALETTE = [  # (base rgb, fabric kind)
    ((236, 232, 224), "shirt"), ((188, 204, 222), "shirt"), ((198, 176, 146), "knit"),
    ((58, 62, 72), "wool"), ((150, 112, 78), "coat"), ((226, 214, 192), "knit"),
    ((88, 98, 78), "wool"), ((32, 32, 36), "wool"), ((148, 146, 142), "knit"),
    ((72, 94, 128), "denim"), ((244, 240, 232), "shirt"), ((120, 72, 58), "knit"),
]


def fbm(shape, rng, scales=(4, 12, 40)):
    out = np.zeros(shape)
    for s in scales:
        small = rng.standard_normal((max(2, shape[0] // s), max(2, shape[1] // s)))
        out += ndimage.zoom(small, (shape[0] / small.shape[0], shape[1] / small.shape[1]), order=3)[: shape[0], : shape[1]] * s ** 0.5
    return out / np.abs(out).max()


def shade(h, base, light=(-0.35, -0.45, 1.0), amb=0.42, k=1.0):
    gy, gx = np.gradient(h)
    n = np.dstack([-gx * k, -gy * k, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light) / np.linalg.norm(light)
    lam = np.clip((n * L).sum(2), 0, 1)
    spec = np.clip((n * np.array([0, 0, 1.0])).sum(2), 0, 1) ** 30 * 0.08
    return np.asarray(base)[None, None, :] / 255.0 * (amb + (1 - amb) * lam)[..., None] + spec[..., None]


def garment(rng, W, T, kind):
    """Local height field (T*3 x W) and alpha for one garment. u across width, v across thickness."""
    H = int(T * 3.2)
    v, u = np.mgrid[0:H, 0:W].astype(float)
    v -= H / 2
    un = (u - W / 2) / (W / 2)                             # -1..1
    # draped body: wider than shoulders in thickness, wavy outline (vertical folds seen from above)
    fu = fbm((1, W), rng, (W // 9, W // 4))[0]
    folds = 0.16 * fu + 0.05 * np.sin(un * rng.uniform(14, 20) + rng.uniform(0, 6))
    bw = {"coat": 1.3, "knit": 1.2, "wool": 1.15, "denim": 1.12, "shirt": 1.05}[kind]
    sleeve = 0.22 * np.exp(-((np.abs(un) - 0.8) / 0.1) ** 2)            # sleeves hanging at both ends
    tb = T / 2 * bw * (1 + folds + sleeve) * np.sqrt(np.clip(1 - np.abs(un / 0.97) ** 3.2, 0, 1))
    off = rng.uniform(-0.12, 0.12) * T                     # body hangs slightly off the hanger line
    rb = np.clip(1 - ((v - off) / np.maximum(tb, 1e-3)) ** 2, 0, 1)
    hb = 0.45 * T * rb ** 0.35
    # shoulders: rounded band on the hanger line with rounded sleeve heads
    ts = T / 2 * np.sqrt(np.clip(1 - np.abs(un / 0.93) ** 6, 0, 1))
    rs = np.clip(1 - (v / np.maximum(ts, 1e-3)) ** 2, 0, 1)
    hs = 0.3 * T + 0.3 * T * rs ** 0.4
    h = np.where(rs > 0, np.maximum(hs, hb), hb)
    alpha = np.clip(np.maximum(rb, rs) * 6, 0, 1)
    # drape folds as ridges running across the thickness
    h += 0.05 * T * fbm((1, W), rng, (W // 14, W // 6))[0][None, :] * (rb > 0)
    # weave
    if kind == "knit":
        h += 0.35 * np.abs(np.sin(u * np.pi / (1.6 * SS))) + 0.25 * fbm(h.shape, rng, (2, 4))
    elif kind == "denim":
        h += 0.35 * np.sin((u + v) * np.pi / (1.2 * SS))
    elif kind in ("wool", "coat"):
        h += 0.6 * fbm(h.shape, rng, (2, 5))
    else:
        h += 0.2 * fbm(h.shape, rng, (2, 6))
    # collar / neckline at the centre of the shoulders for shirts and knits
    if kind in ("shirt", "knit", "coat"):
        g = np.exp(-(un / 0.09) ** 2 - (v / (T * 0.3)) ** 2)
        h = h - 0.22 * T * g
    return h, alpha, off


def paint(w, h, dividers=(), seed=7, n_per=11, wall=None):
    rng = np.random.default_rng(seed)
    W, Hh = w * SS, h * SS
    # wardrobe floor: dark walnut, darker towards the back wall and the partitions
    grain = fbm((Hh, W), rng, (3, 9, 30))
    img = np.zeros((Hh, W, 3))
    base = np.array([92, 60, 40]) / 255
    img[:] = base * (0.85 + 0.15 * grain[..., None])
    xx = np.linspace(0, 1, W)[None, :]
    img *= (0.55 + 0.45 * xx ** 0.6)[..., None]              # back wall (x=0) in shadow, front lit
    wall = wall or (78, 52, 36)
    th = 5 * SS
    secs, prev = [], 0
    for d in list(dividers) + [h]:
        secs.append((prev * SS + (th if prev else 0), d * SS - (th if d != h else 0)))
        prev = d
    k = 0
    rail_x = W * 0.5
    for s0, s1 in secs:
        L = s1 - s0
        n = n_per
        T = L / n * rng.uniform(0.95, 1.05)
        cur = s0 + T * 0.55
        items = []
        while cur < s1 - T * 0.45:
            col, kind = PALETTE[k % len(PALETTE)]
            k += 1
            t = T * {"coat": 1.25, "knit": 1.05, "wool": 1.0, "denim": 0.95, "shirt": 0.62}[kind]
            items.append((cur + t / 2, t, col, kind))
            cur += t * rng.uniform(0.8, 0.92)
        scale = (s1 - s0 - T * 0.4) / max(1, cur - s0)
        for y, t, col, kind in items:
            y = s0 + (y - s0) * scale
            gw = int(W * {'coat': 0.92, 'knit': 0.86, 'wool': 0.88}.get(kind, 0.84) * rng.uniform(0.96, 1.02))
            hf, al, off = garment(rng, gw, t, kind)
            ang = rng.uniform(-4, 4)
            col = np.clip(np.array(col) * rng.uniform(0.94, 1.05), 0, 255)
            rgb = shade(hf, col, k=0.6)
            # rotate the sprite slightly
            rgb = np.dstack([ndimage.rotate(rgb[..., i], ang, reshape=True, order=1) for i in range(3)])
            al = np.clip(ndimage.rotate(al, ang, reshape=True, order=1), 0, 1)
            ph, pw = al.shape
            x0 = int(rail_x - pw / 2 + rng.uniform(-2, 2) * SS)
            y0 = int(y - ph / 2)
            ya, yb, xa, xb = max(0, y0), min(Hh, y0 + ph), max(0, x0), min(W, x0 + pw)
            if yb <= ya:
                continue
            sl = (slice(ya - y0, yb - y0), slice(xa - x0, xb - x0))
            # soft shadow cast towards +y / +x (light from the upper left)
            sh = ndimage.gaussian_filter(al, 4 * SS)
            sh = ndimage.shift(sh, (5 * SS, 3 * SS), order=1)
            img[ya:yb, xa:xb] *= (1 - 0.55 * sh[sl])[..., None]
            a = al[sl][..., None]
            img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - a) + rgb[sl] * a
            # wooden hanger on the shoulder line + chrome hook over the rail
            hy = y + off * 0 - 0
            hw = gw * 0.8
            yy, xx2 = np.mgrid[ya:yb, xa:xb].astype(float)
            ca, sa = np.cos(np.radians(-ang)), np.sin(np.radians(-ang))
            lu = (xx2 - rail_x) * ca - (yy - hy) * sa
            lv = (xx2 - rail_x) * sa + (yy - hy) * ca
            bar = np.clip(0.9 * SS - np.abs(lv), 0, 1) * np.clip((hw / 2 - np.abs(lu)) / (hw * 0.25), 0, 1) * 0.85
            hr = np.clip(1 - (lv / (1.2 * SS)) ** 2, 0, 1)
            wood = np.array([150, 108, 70]) / 255 * (0.6 + 0.45 * hr)[..., None]
            img[ya:yb, xa:xb] = img[ya:yb, xa:xb] * (1 - bar[..., None]) + wood * bar[..., None]
        # chrome rail through the section
        rl = np.arange(W)[None, :] - rail_x
        prof = np.clip(1 - (rl / (1.3 * SS)) ** 2, 0, 1)
        m = np.clip(1.3 * SS - np.abs(rl), 0, 1)
        chrome = (0.35 + 0.5 * prof ** 0.5)[..., None] * np.array([0.9, 0.88, 0.85])
        img[s0:s1] = img[s0:s1] * (1 - m[..., None]) + chrome * m[..., None]
        # hooks: small chrome loops over the rail at every hanger
        for y, t, col, kind in items:
            y = s0 + (y - s0) * scale
            yy, xx2 = np.mgrid[int(y - 5 * SS):int(y + 5 * SS), int(rail_x - 5 * SS):int(rail_x + 5 * SS)].astype(float)
            r = np.hypot(xx2 - rail_x - 1.2 * SS, yy - y)
            ring = np.clip(1 - np.abs(r - 2.6 * SS) / (0.8 * SS), 0, 1) * (xx2 > rail_x - 0.5 * SS)
            ys, xs = slice(int(y - 5 * SS), int(y + 5 * SS)), slice(int(rail_x - 5 * SS), int(rail_x + 5 * SS))
            img[ys, xs] = img[ys, xs] * (1 - ring[..., None]) + np.array([0.9, 0.88, 0.85]) * ring[..., None]
        # warm LED from the front top of each section
        yy = np.linspace(0, 1, s1 - s0)[:, None]
        glow = 0.9 + 0.35 * np.exp(-((yy - 0.5) / 0.55) ** 2) * (0.6 + 0.4 * xx)
        img[s0:s1] *= glow[..., None] * np.array([1.05, 1.0, 0.9])
    # partitions (walnut)
    for d in dividers:
        yy = slice(d * SS - th, d * SS + th)
        img[yy] = np.array(wall) / 255 * (0.9 + 0.1 * grain[yy, :, None])
    img = np.clip(img, 0, 1)
    out = Image.fromarray((img * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    return np.asarray(out)


if __name__ == "__main__":
    import sys
    a = paint(225, 1242, dividers=(410, 830))
    Image.fromarray(a).save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/closet_test.png")
