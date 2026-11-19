"""Procedural top-down wardrobe drawing (used as an exact layout guide for photoreal redraw).

draw_long(w, h, n, seed): open wardrobe seen from the ceiling, back wall at the BOTTOM edge, opening at the top,
    one horizontal rail, n garments hanging on it (each a narrow sliver across the rail).
draw_folded(w, h, stacks, seed): open shelf unit seen from above with stacks of folded clothes.
All sizes in pixels; images are rendered at 3x and downscaled for antialiasing.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PALETTE = [(222, 210, 190), (196, 170, 138), (240, 234, 222), (150, 142, 134), (178, 140, 104),
           (92, 88, 86), (205, 190, 168), (132, 110, 94), (60, 58, 60), (214, 200, 176), (170, 160, 150)]
OAK = (196, 160, 122)
OAK_DARK = (150, 116, 84)


def _noise(h, w, seed, scale=1.0):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h, w)).astype(np.float32)
    img = Image.fromarray(np.clip(128 + n * 40, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(scale))
    return (np.asarray(img).astype(np.float32) - 128) / 40


def _wood(h, w, seed, base=OAK):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, w)[None, :]
    y = np.linspace(0, 1, h)[:, None]
    grain = np.sin((x * 60 + np.sin(y * 7 + rng.uniform(0, 6)) * 0.8) * np.pi) * 0.5 + 0.5
    n = _noise(h, w, seed + 1, 2)
    v = 1 + (grain - 0.5) * 0.08 + n * 0.03
    return np.clip(np.array(base, np.float32)[None, None, :] * v[..., None], 0, 255)


def draw_long(w, h, n=18, seed=1):
    S = 3
    W, H = w * S, h * S
    rng = np.random.default_rng(seed)
    frame = int(0.06 * H)
    img = _wood(H, W, seed)                                  # carcass top edges
    inner = _wood(H - 2 * frame, W - 2 * frame, seed + 7, OAK_DARK)
    # interior lighting: soft LED glow brighter towards the opening (top)
    yy = np.linspace(1.12, 0.8, inner.shape[0])[:, None, None]
    img[frame:H - frame, frame:W - frame] = np.clip(inner * yy * np.array([1.04, 1.0, 0.95]), 0, 255)
    im = Image.fromarray(img.astype(np.uint8)).convert("RGBA")

    rail_y = frame + int((H - 2 * frame) * 0.46)
    usable = W - 2 * frame - 4 * S
    pitch = usable / n
    shadow = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shadow)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i in range(n):
        cx = frame + 2 * S + pitch * (i + 0.5) + rng.uniform(-0.12, 0.12) * pitch
        t = pitch * rng.uniform(0.72, 0.95)                  # garment thickness seen from above
        L = (H - 2 * frame) * rng.uniform(0.74, 0.84)        # shoulder width (along depth)
        top = rail_y - L * 0.5
        col = np.array(PALETTE[rng.integers(len(PALETTE))], np.float32)
        gw, gh = int(t * 1.25) + 2, int(L) + 2
        g = np.zeros((gh, gw, 4), np.float32)
        ys = np.linspace(-1, 1, gh)[:, None]
        xs = np.linspace(-1, 1, gw)[None, :]
        # silhouette: rounded ends (shoulders), slight bulge at the collar in the middle
        half = 0.78 + 0.18 * np.exp(-(ys / 0.18) ** 2) - 0.10 * (np.abs(ys) ** 6)
        mask = (np.abs(xs) <= half) & (np.abs(ys) <= 0.985)
        shade = 0.72 + 0.34 * np.sqrt(np.clip(1 - (xs / np.maximum(half, 1e-3)) ** 2, 0, 1))
        shade = shade * (1 - 0.10 * np.abs(ys))
        tex = 1 + _noise(gh, gw, seed * 100 + i, 0.6) * 0.06
        rgb = col[None, None, :] * (shade * tex)[..., None]
        g[..., :3] = np.clip(rgb, 0, 255)
        g[..., 3] = mask * 255
        gi = Image.fromarray(g.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(0.8 * S / 3))
        ang = rng.uniform(-3, 3)
        gi = gi.rotate(ang, resample=Image.BICUBIC, expand=True)
        px, py = int(cx - gi.width / 2), int(top - (gi.height - gh) / 2)
        sd.rounded_rectangle((px + 3 * S, py + 4 * S, px + gi.width + 3 * S, py + gi.height + 5 * S),
                             radius=int(t / 2), fill=150)
        layer.alpha_composite(gi, (max(px, 0), max(py, 0)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5 * S))
    dark = Image.new("RGBA", (W, H), (40, 28, 20, 255))
    dark.putalpha(shadow.point(lambda v: int(v * 0.55)))
    im.alpha_composite(dark)
    # rail under the garments' hooks is hidden; show it only in gaps
    d = ImageDraw.Draw(im)
    d.line([(frame, rail_y), (W - frame, rail_y)], fill=(185, 180, 172, 255), width=max(2, int(0.012 * H)))
    im.alpha_composite(layer)
    # hanger hooks: small metallic arcs over the rail at each garment
    d = ImageDraw.Draw(im)
    rng2 = np.random.default_rng(seed)
    for i in range(n):
        cx = frame + 2 * S + pitch * (i + 0.5)
        r = int(0.025 * H)
        d.arc((cx - r, rail_y - r, cx + r, rail_y + r), 200, 340, fill=(205, 200, 190, 255), width=max(2, S))
    return im.convert("RGB").resize((w, h), Image.LANCZOS)


def draw_folded(w, h, stacks=3, seed=5):
    S = 3
    W, H = w * S, h * S
    rng = np.random.default_rng(seed)
    frame = int(0.1 * W)
    img = _wood(H, W, seed)
    inner = _wood(H - 2 * frame, W - 2 * frame, seed + 3, OAK_DARK)
    img[frame:H - frame, frame:W - frame] = inner * 1.05
    im = Image.fromarray(img.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(im)
    ih = (H - 2 * frame) / stacks
    for k in range(stacks):
        y0 = frame + ih * k + ih * 0.08
        y1 = frame + ih * (k + 1) - ih * 0.08
        x0 = frame + (W - 2 * frame) * 0.08
        x1 = W - frame - (W - 2 * frame) * 0.08
        col = np.array(PALETTE[rng.integers(len(PALETTE))], np.float32)
        sh = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sh).rounded_rectangle((x0 + 4 * S, y0 + 5 * S, x1 + 4 * S, y1 + 5 * S), radius=6 * S, fill=160)
        sh = sh.filter(ImageFilter.GaussianBlur(4 * S))
        dk = Image.new("RGBA", (W, H), (40, 28, 20, 255)); dk.putalpha(sh.point(lambda v: int(v * 0.5)))
        im.alpha_composite(dk)
        gw, gh = int(x1 - x0), int(y1 - y0)
        ys = np.linspace(-1, 1, gh)[:, None]; xs = np.linspace(-1, 1, gw)[None, :]
        shade = 0.9 + 0.12 * (1 - xs ** 2) - 0.05 * np.abs(ys)
        rib = 1 + 0.05 * np.sin(xs * 60)                        # knit ribs
        tex = 1 + _noise(gh, gw, seed + k * 11, 0.7) * 0.05
        rgb = np.clip(col[None, None, :] * (shade * rib * tex)[..., None], 0, 255).astype(np.uint8)
        g = Image.fromarray(rgb).convert("RGBA")
        m = Image.new("L", (gw, gh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, gw - 1, gh - 1), radius=6 * S, fill=255)
        g.putalpha(m)
        im.alpha_composite(g, (int(x0), int(y0)))
        # fold edge lines of the stacked layers
        for j in range(1, 4):
            yy = y0 + gh * (0.18 + 0.2 * j)
            d.line([(x0 + 6 * S, yy), (x1 - 6 * S, yy)], fill=tuple(int(c * 0.82) for c in col) + (255,), width=S)
    return im.convert("RGB").resize((w, h), Image.LANCZOS)
