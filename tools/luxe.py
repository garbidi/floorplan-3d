"""Luxury material badges and area tags for labels.draw_plan (styles l1..l5).

l1 marble + brass, l2 black lacquer + gold foil, l3 art deco gold (no tags), l4 emerald velvet + gold, l5 ivory letterpress + gold.
Everything is drawn on a local canvas around the badge / tag and pasted back; foil = metallic gradient + fine
brushed noise + bevel from the glyph mask."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

LUXE = ("l1", "l2", "l3", "l4", "l5")

GOLD = [(0.0, (122, 92, 42)), (0.22, (226, 196, 120)), (0.38, (176, 136, 62)), (0.55, (246, 226, 160)),
        (0.72, (168, 128, 58)), (0.88, (222, 190, 112)), (1.0, (130, 98, 46))]
GOLD_DEEP = [(0.0, (96, 70, 30)), (0.25, (184, 148, 80)), (0.45, (128, 96, 42)), (0.6, (206, 172, 100)),
             (0.8, (120, 90, 40)), (1.0, (170, 134, 70))]
BRASS = [(0.0, (110, 84, 44)), (0.3, (200, 168, 104)), (0.5, (140, 108, 58)), (0.7, (214, 186, 124)), (1.0, (118, 90, 48))]


def _rng(seed=7):
    return np.random.default_rng(seed)


def _noise(w, h, blur, seed):
    n = _rng(seed).standard_normal((h, w)).astype(np.float32)
    img = Image.fromarray(((n - n.min()) / (np.ptp(n) + 1e-6) * 255).astype(np.uint8))
    a = np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)


def metal(w, h, stops=GOLD, angle=0.6, seed=3):
    """metallic foil texture: multi-stop gradient along a diagonal + brushed streaks."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx * np.cos(angle) + yy * np.sin(angle))
    t = (t - t.min()) / (np.ptp(t) + 1e-6)
    t = np.clip(t + 0.035 * _noise(w, h, max(2, h / 6), seed), 0, 1)
    ps = np.array([s[0] for s in stops]); cs = np.array([s[1] for s in stops], np.float32)
    out = np.stack([np.interp(t, ps, cs[:, c]) for c in range(3)], -1)
    streak = _rng(seed + 1).standard_normal((1, w)).astype(np.float32)
    streak = np.asarray(Image.fromarray(((streak - streak.min()) / (np.ptp(streak) + 1e-6) * 255).astype(np.uint8)).resize((w, h)).filter(ImageFilter.GaussianBlur(1))).astype(np.float32) / 255 - 0.5
    out = out * (1 + 0.06 * streak[..., None])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def bevel_paste(canvas, mask, tex, depth):
    """paste tex through mask with an emboss: light from top-left, dark rim bottom-right, soft drop shadow."""
    d = max(1, int(depth))
    sh = mask.filter(ImageFilter.GaussianBlur(d * 1.2))
    canvas.paste((0, 0, 0), (d // 2 + 1, d), sh.point(lambda v: int(v * 0.45)))
    canvas.paste(tex, (0, 0), mask)
    m = np.asarray(mask).astype(np.float32) / 255
    mb = np.asarray(mask.filter(ImageFilter.GaussianBlur(max(1, d * 0.6)))).astype(np.float32) / 255
    sx = np.roll(mb, d, axis=1); sy = np.roll(mb, d, axis=0)
    hi = np.clip((mb - (sx + sy) / 2) * 2.2, 0, 1) * m
    lo = np.clip(((sx + sy) / 2 - mb) * 2.2, 0, 1) * m
    canvas.paste((255, 250, 225), (0, 0), Image.fromarray((hi * 200).astype(np.uint8)))
    canvas.paste((40, 26, 8), (0, 0), Image.fromarray((lo * 150).astype(np.uint8)))


def marble(w, h, seed=11):
    """Calacatta-like: warm white base, soft clouding, a few organic domain-warped grey-gold veins."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    S = max(w, h)
    wx = _noise(w, h, S / 6, seed) * 0.9 + _noise(w, h, S / 18, seed + 1) * 0.35
    wy = _noise(w, h, S / 6, seed + 2) * 0.9 + _noise(w, h, S / 18, seed + 3) * 0.35
    u = (xx + wx * S * 0.12) / S; v = (yy + wy * S * 0.12) / S
    f = np.sin((u * 0.8 + v * 1.6) * 7.0 + wx * 2.0)
    vein = np.clip(1 - np.abs(f) / 0.09, 0, 1) ** 1.6
    f2 = np.sin((u * 1.7 - v * 0.6) * 13.0 + wy * 3.0)
    vein2 = np.clip(1 - np.abs(f2) / 0.025, 0, 1) ** 2 * 0.45
    cloud = _noise(w, h, S / 8, seed + 4)
    base = np.array([246, 243, 237], np.float32) + (3.5 * cloud)[..., None] + 1.2 * _noise(w, h, 0.8, seed + 5)[..., None]
    veins = np.asarray(Image.fromarray((np.clip(vein + vein2, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, S / 500)))).astype(np.float32) / 255
    col = base - veins[..., None] * np.array([62, 64, 68], np.float32) * 1.1
    col = col - (np.clip(cloud, 0, None) * 4)[..., None] * np.array([1, 1, 1.4])
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def lacquer(w, h, base=(18, 16, 15), seed=5):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = (xx / w * 0.6 + yy / h * 0.4)
    spec = np.exp(-((xx / w - 0.25) ** 2 * 6 + (yy / h - 0.0) ** 2 * 3)) * 26
    col = np.array(base, np.float32) + (g * 10 + spec)[..., None] + 1.5 * _noise(w, h, 1.5, seed)[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def velvet(w, h, base=(14, 58, 46), seed=9):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx / w - 0.4) * 1.3) ** 2 + ((yy / h - 0.35)) ** 2)
    sheen = np.clip(1 - r * 1.5, 0, 1) * 30
    pile = 6 * _noise(w, h, 0.8, seed) + 5 * _noise(w, h, max(3, w / 25), seed + 1)
    col = np.array(base, np.float32) + (sheen + pile)[..., None] * np.array([0.7, 1.0, 0.9])
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


def ivory(w, h, seed=13):
    col = np.array([246, 240, 228], np.float32) + 3 * _noise(w, h, 0.7, seed)[..., None] + 3 * _noise(w, h, max(3, w / 30), seed + 1)[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))


MATERIAL = {"l1": marble, "l2": lacquer, "l4": velvet, "l5": ivory}
INK = {"l1": GOLD_DEEP, "l2": GOLD, "l3": GOLD, "l4": GOLD, "l5": GOLD_DEEP}
FRAME = {"l1": BRASS, "l2": GOLD, "l3": GOLD, "l4": GOLD, "l5": GOLD_DEEP}


def deco_corners(dd, box, s, w, fill=255):
    """art-deco stepped corner ornaments inside box."""
    x0, y0, x1, y1 = box
    for sx, sy, cx, cy in ((1, 1, x0, y0), (-1, 1, x1, y0), (1, -1, x0, y1), (-1, -1, x1, y1)):
        for i, L in enumerate((s, s * 0.62, s * 0.3)):
            o = i * s * 0.16
            dd.line([(cx + sx * o, cy + sy * (o + L)), (cx + sx * o, cy + sy * o), (cx + sx * (o + L), cy + sy * o)], fill=fill, width=w)
        dd.regular_polygon((cx + sx * s * 0.62, cy + sy * s * 0.62, max(2, s * 0.07)), 4, rotation=45, fill=fill)


def card(im, box, style, s, items_fn, frame=True, ornaments=False, radius=0):
    """material card at box (image px) with foil frame and foil content drawn by items_fn(draw, ox, oy)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    m = int(s * 0.5)
    R = (x0 - m, y0 - m, x1 + m, y1 + m)
    loc = im.crop(R)
    w, h = x1 - x0, y1 - y0
    bx = (m, m, m + w, m + h)
    hl = max(2, int(s) // 60)
    if style != "l3":
        sh = Image.new("L", loc.size, 0)
        ImageDraw.Draw(sh).rounded_rectangle((bx[0] + s * 0.02, bx[1] + s * 0.06, bx[2] + s * 0.02, bx[3] + s * 0.06), radius, fill=150)
        loc.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(s * 0.08)))
        cm = Image.new("L", loc.size, 0); ImageDraw.Draw(cm).rounded_rectangle(bx, radius, fill=255)
        mat = Image.new("RGB", loc.size); mat.paste(MATERIAL[style](w, h), (m, m))
        loc.paste(mat, (0, 0), cm)
        if style == "l5":     # paper edge: faint inner shade
            e = Image.new("L", loc.size, 0); ImageDraw.Draw(e).rounded_rectangle(bx, radius, outline=60, width=max(2, int(s) // 25))
            loc.paste((120, 100, 70), (0, 0), ImageChops.multiply(e.filter(ImageFilter.GaussianBlur(s * 0.03)), cm))
    else:   # art deco on the floor: a dark translucent veil so the gold reads on wood
        cm = Image.new("L", loc.size, 0); ImageDraw.Draw(cm).rectangle(bx, fill=255)
        veil = loc.filter(ImageFilter.GaussianBlur(s * 0.06))
        veil = Image.blend(veil, Image.new("RGB", loc.size, (20, 16, 12)), 0.55)
        loc.paste(veil, (0, 0), cm)
    fm = Image.new("L", loc.size, 0); fd = ImageDraw.Draw(fm)
    if frame:
        ins = s * 0.07
        fd.rounded_rectangle(bx, radius, outline=255, width=hl * 2)
        fd.rounded_rectangle((bx[0] + ins, bx[1] + ins, bx[2] - ins, bx[3] - ins), max(0, radius - ins), outline=255, width=max(1, hl))
        if ornaments:
            deco_corners(fd, (bx[0] + ins * 1.9, bx[1] + ins * 1.9, bx[2] - ins * 1.9, bx[3] - ins * 1.9), s * 0.16, max(1, hl), 255)
    tm = Image.new("L", loc.size, 0)
    items_fn(ImageDraw.Draw(tm), m - x0, m - y0)
    tex = metal(loc.size[0], loc.size[1], FRAME[style], seed=4)
    bevel_paste(loc, fm, tex, s / 90)
    tex = metal(loc.size[0], loc.size[1], INK[style], angle=0.9, seed=6)
    if style == "l5":      # letterpress: pressed-in shade before the foil
        loc.paste((90, 70, 40), (0, 0), tm.filter(ImageFilter.GaussianBlur(max(1, s / 120))).point(lambda v: int(v * 0.35)))
    bevel_paste(loc, tm, tex, s / 110)
    im.paste(loc, R[:2])
    return im
