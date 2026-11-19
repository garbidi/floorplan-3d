"""Draw area labels and the apartment badge deterministically (exact digits, reference style).

Reads the LABELS / BADGE lines of plans_prepared/<key>_message.txt:
  LABELS ...: "12,5" x 23, y 12; "3,8" x 75, y 12; ...
  BADGE "1 | 39,1": ... x 60–80, y 62–74 ...
Coordinates are % of the render's outer wall contour (same system as the size map).
Usage: python3 labels.py <key> <render_in> <render_out>
"""
import re
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fix  # noqa: E402

FONT = __file__.rsplit("/", 1)[0] + "/fonts/Montserrat.ttf"
TEXT = (52, 46, 44)
EDGE = (170, 165, 160)


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def parse(msg):
    msg = msg.replace("\u2212", "-")
    labels = []
    m = re.search(r"LABELS[^\n]*", msg)
    if m:
        for t, x, y in re.findall(r'"([^"]+)"[^;"]*?x (-?\d+(?:\.\d+)?), y (-?\d+(?:\.\d+)?)', m.group(0)):
            labels.append((t, float(x), float(y)))
    badge = None
    b = re.search(r'BADGE "([^"|]+)\|\s*([^"]+)"[^\n]*?x (\d+)\D+(\d+), y (\d+)\D+(\d+)', msg)
    if b:
        badge = (b.group(1).strip(), b.group(2).strip(), *map(float, b.groups()[2:]))
    return labels, badge


def draw(key, src, out):
    P = "/mnt/c/Projects/3d_visual/"
    msg = open(P + f"plans_prepared/{key}_message.txt", encoding="utf-8").read()
    labels, badge = parse(msg)
    im = Image.open(src).convert("RGB")
    cb = fix.contour(im)
    W = cb[2] - cb[0]
    size = max(16, int(W * 0.0145))          # label text height relative to apartment width
    d = ImageDraw.Draw(im)
    f = font(size)
    for t, x, y in labels:
        cx, cy, _, _ = fix.to_px(im, (x, y, x, y), cb)
        tw = d.textlength(t, font=f)
        pw, ph = int(size * 0.55), int(size * 0.42)
        box = (int(cx - tw / 2 - pw), int(cy - size / 2 - ph), int(cx + tw / 2 + pw), int(cy + size / 2 + ph))
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).rectangle((box[0] + 2, box[1] + 3, box[2] + 2, box[3] + 3), fill=70)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(4)))
        d = ImageDraw.Draw(im)
        d.rectangle(box, fill=(250, 249, 247), outline=EDGE, width=max(1, size // 22))
        d.text((cx, cy), t, font=f, fill=TEXT, anchor="mm")
    if badge:
        n, total, x0, x1, y0, y1 = badge
        bx0, by0, bx1, by1 = fix.to_px(im, (x0, y0, x1, y1), cb)
        cxm = (bx0 + bx1) // 2
        cy = (by0 + by1) // 2
        big = font(int(size * 2.1), 450)
        small = font(int(size * 1.1), 450)
        lw = d.textlength(n, font=big) + size * 1.4
        rw = d.textlength(total, font=small) + size * 1.4
        hh = int(size * 1.6)
        box = (int(cxm - (lw + rw) / 2), cy - hh, int(cxm + (lw + rw) / 2), cy + hh)
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).rectangle((box[0] + 2, box[1] + 3, box[2] + 2, box[3] + 3), fill=70)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(4)))
        d = ImageDraw.Draw(im)
        d.rectangle(box, fill=(250, 249, 247), outline=EDGE, width=max(1, size // 20))
        mid = int(box[0] + lw)
        d.line([(mid, box[1] + 4), (mid, box[3] - 4)], fill=EDGE, width=max(1, size // 20))
        d.text(((box[0] + mid) / 2, cy), n, font=big, fill=TEXT, anchor="mm")
        d.text(((mid + box[2]) / 2, cy), total, font=small, fill=TEXT, anchor="mm")
    im.save(out, quality=97)


def plan_marks(key):
    """Find the tan area numbers and the tan badge square on the original plan (plans_prepared/<key>.png).
    Returns (labels, badge): labels = [(cx, cy, digit_h)], badge = (x0, y0, x1, y1) in plan px."""
    import numpy as np
    from scipy import ndimage
    P = "/mnt/c/Projects/3d_visual/"
    a = np.asarray(Image.open(P + f"plans_prepared/{key}.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r - b > 45) & (r > 140) & (g > 100)
    lab, _ = ndimage.label(ndimage.binary_dilation(m, np.ones((9, 25))))
    boxes = []
    badge = None
    for sl in ndimage.find_objects(lab):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if (y1 - y0) * (x1 - x0) < 200:
            continue
        if m[sl].mean() > 0.5 and (y1 - y0) > 100:          # filled tan square = badge
            badge = [x0 + 4, y0 + 4, x1 - 12, y1 - 4]
            continue
        boxes.append([x0 + 12, y0 + 4, x1 - 12, y1 - 4])
    # merge pieces of one number that lie on the same line close to each other
    merged = []
    for bx in sorted(boxes):
        for mb in merged:
            horiz = abs((mb[1] + mb[3]) / 2 - (bx[1] + bx[3]) / 2) < 12 and -10 < bx[0] - mb[2] < 45
            vert = abs((mb[0] + mb[2]) / 2 - (bx[0] + bx[2]) / 2) < 12 and -10 < bx[1] - mb[3] < 45
            if horiz or vert:
                mb[:] = [min(mb[0], bx[0]), min(mb[1], bx[1]), max(mb[2], bx[2]), max(mb[3], bx[3])]
                break
        else:
            merged.append(list(bx))
    changed = True
    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                a_, b_ = merged[i], merged[j]
                if abs((a_[0] + a_[2]) / 2 - (b_[0] + b_[2]) / 2) < 12 and (-10 < b_[1] - a_[3] < 45 or -10 < a_[1] - b_[3] < 45):
                    merged[i] = [min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[2], b_[2]), max(a_[3], b_[3])]
                    del merged[j]; changed = True; break
            if changed:
                break
    # digit height = short side of the number box (numbers may be rotated on the plan)
    labels = [((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2, min(bx[3] - bx[1], bx[2] - bx[0])) for bx in merged]
    if labels:   # all area numbers on a plan have one size: use the largest detected digit height for all
        hmax = float(max(l[2] for l in labels))
        labels = [(l[0], l[1], hmax) for l in labels]
    if badge:   # the white cell with the totals sits right of the tan square: follow its dark border line
        best = None
        for yy in range(badge[1] - 6, badge[1] + 20):
            row = a[yy, badge[2]:badge[2] + int((badge[2] - badge[0]) * 1.2)].sum(axis=1) < 500
            run = int(np.argmin(row)) if not row.all() else len(row)
            if run > 20 and (best is None or run > best):
                best = run
        badge[2] = badge[2] + (best if best else int((badge[2] - badge[0]) * 0.65))
    return labels, badge


TAN = (162, 116, 78)


def _tan(im, box, h):
    """designer reference: translucent creamy tan plate (light top-left -> darker bottom-right), thin white frame, soft shadow.
    mask and frame drawn at 4x and downscaled -> anti-aliased rounded corners."""
    import numpy as _np
    x0, y0, x1, y1 = [int(v) for v in box]; r = max(4, int(h * 0.07)); fw = max(2, h // 110)
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((x0 + 2, y0 + 4, x1 + 2, y1 + 5), r, fill=60)
    im.paste((40, 20, 5), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(3, h // 12))))
    w_, h_ = x1 - x0 + 1, y1 - y0 + 1; S = 4
    big = Image.new("L", (w_ * S, h_ * S), 0); ImageDraw.Draw(big).rounded_rectangle((0, 0, w_ * S - 1, h_ * S - 1), r * S, fill=255)
    fill = _np.asarray(big.resize((w_, h_), Image.LANCZOS), _np.float32) / 255
    big = Image.new("L", (w_ * S, h_ * S), 0); ImageDraw.Draw(big).rounded_rectangle((0, 0, w_ * S - 1, h_ * S - 1), r * S, outline=255, width=fw * S)
    frame = _np.asarray(big.resize((w_, h_), Image.LANCZOS), _np.float32) / 255
    t = (_np.linspace(0, 1, w_)[None, :] * 0.55 + _np.linspace(0, 1, h_)[:, None] * 0.45)
    col = _np.array([186, 134, 90], _np.float32)[None, None] * (1.1 - 0.3 * t)[..., None]
    bg = _np.asarray(im.crop((x0, y0, x0 + w_, y0 + h_)), _np.float32)
    al = (fill * 0.76)[..., None]
    out = bg * (1 - al) + col * al
    fr = frame[..., None]; out = out * (1 - fr) + 255 * fr
    im.paste(Image.fromarray(out.clip(0, 255).astype(_np.uint8)), (x0, y0))
    return ImageDraw.Draw(im)


def dfont(size, weight=600):
    """DIN-like font of the designer's reference plates (Bahnschrift: axes weight, width)."""
    f = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/bahnschrift.ttf", size)
    try:
        f.set_variation_by_axes([weight, 100])
    except Exception:
        pass
    return f


# ---- Figma spec of the designer's plate (Frame 29 / Frame 32, file "Untitled", page 3) ----
FIG = dict(H=247.1, W1=389.0, pad_x=36.69, pad_y=17.3, gap=36.69, radius=15.0, border=2.0, grad_angle=137.6,
           c0=(172, 111, 54), c1=(70, 45, 22), s0=0.2387, s1=1.3883, alpha=0.7, shadow=(0, 4, 4, 0.25),
           num=122.33, word=38.01, word_shadow=(0, 2.19, 2.19, 0.25), area=69.3, uline_w=95.52, uline_t=4.0, gap_v=6.92,
           vline_len=186.89, vline_t=5.0, small_h=133.61)


def mfont(size, weight=700):
    f = ImageFont.truetype(__file__.rsplit("/", 1)[0] + "/fonts/Manrope.ttf", max(1, int(round(size))))
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def _fig_shadow(im, paint, u, spec):
    """Figma drop shadow: paint(draw, fill) is drawn into a mask, offset (x, y), gaussian sigma = blur/2, black at alpha."""
    x, y, blur, a = spec
    sh = Image.new("L", im.size, 0); paint(ImageDraw.Draw(sh), 255)
    sh = sh.transform(im.size, Image.AFFINE, (1, 0, -x * u, 0, 1, -y * u)).filter(ImageFilter.GaussianBlur(max(0.6, blur * u / 2)))
    sh = sh.point(lambda v: int(v * a))
    im.paste((0, 0, 0), (0, 0), sh)


def fig_plate(im, box, u):
    """plate: shadow, 70% linear gradient 137.6deg (#AC6F36 23.87% -> #462D16 138.83%), 2px inner white border, radius 15 (anti-aliased)."""
    import numpy as _np, math as _m
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    w_, h_ = x1 - x0, y1 - y0; r = FIG["radius"] * u; bw = FIG["border"] * u; S = 4
    before = _np.asarray(im.crop((x0, y0, x1, y1)), _np.float32)          # Figma: shadow not shown behind the translucent fill
    _fig_shadow(im, lambda dd, c: dd.rounded_rectangle((x0, y0, x1 - 1, y1 - 1), r, fill=c), u, FIG["shadow"])
    big = Image.new("L", (w_ * S, h_ * S), 0); ImageDraw.Draw(big).rounded_rectangle((0, 0, w_ * S - 1, h_ * S - 1), r * S, fill=255)
    fill = _np.asarray(big.resize((w_, h_), Image.LANCZOS), _np.float32) / 255
    big = Image.new("L", (w_ * S, h_ * S), 0); ImageDraw.Draw(big).rounded_rectangle((0, 0, w_ * S - 1, h_ * S - 1), r * S, outline=255, width=max(1, int(round(bw * S))))
    frame = _np.asarray(big.resize((w_, h_), Image.LANCZOS), _np.float32) / 255
    a = _m.radians(FIG["grad_angle"]); dx, dy = _m.sin(a), -_m.cos(a)          # CSS: 0deg = to top, clockwise
    L = abs(w_ * dx) + abs(h_ * dy)
    yy, xx = _np.mgrid[0:h_, 0:w_].astype(_np.float32)
    t = ((xx - w_ / 2) * dx + (yy - h_ / 2) * dy) / L + 0.5
    t = _np.clip((t - FIG["s0"]) / (FIG["s1"] - FIG["s0"]), 0, 1)[..., None]
    col = _np.array(FIG["c0"], _np.float32) * (1 - t) + _np.array(FIG["c1"], _np.float32) * t
    shadowed = _np.asarray(im.crop((x0, y0, x1, y1)), _np.float32)
    fm = fill[..., None]; bg = before * fm + shadowed * (1 - fm)
    al = (fill * FIG["alpha"])[..., None]
    out = bg * (1 - al) + col * al
    fr = frame[..., None]; out = out * (1 - fr) + 255 * fr
    im.paste(Image.fromarray(out.clip(0, 255).astype(_np.uint8)), (x0, y0))


def fig_text(im, xy, t, f, u, spec=None, anchor="mm"):
    _fig_shadow(im, lambda dd, c: dd.text(xy, t, font=f, fill=c, anchor=anchor), u, spec or FIG["shadow"])
    ImageDraw.Draw(im).text(xy, t, font=f, fill=(255, 255, 255), anchor=anchor)


def fig_line(im, p0, p1, wdt, u):
    _fig_shadow(im, lambda dd, c: dd.line([p0, p1], fill=c, width=max(1, int(round(wdt)))), u, FIG["shadow"])
    ImageDraw.Draw(im).line([p0, p1], fill=(255, 255, 255), width=max(1, int(round(wdt))))


def _wpaint(im, paint, h):
    """white elements with the reference's soft drop shadow: paint(draw, colour) draws them."""
    sh = Image.new("L", im.size, 0); paint(ImageDraw.Draw(sh), 160)
    off = max(1, h // 60)
    sh = sh.transform(im.size, Image.AFFINE, (1, 0, -off, 0, 1, -int(off * 1.6))).filter(ImageFilter.GaussianBlur(max(1.5, h / 45)))
    im.paste((55, 30, 10), (0, 0), sh)
    paint(ImageDraw.Draw(im), (255, 255, 255))


def _wtext(im, xy, t, f, h, anchor="mm"):
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).text((xy[0] + 1, xy[1] + 2), t, font=f, fill=110, anchor=anchor)
    im.paste((60, 35, 20), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(1, h // 40))))
    ImageDraw.Draw(im).text(xy, t, font=f, fill=(255, 255, 255), anchor=anchor)


def _box(d, im, box, size):
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rectangle((box[0] + 3, box[1] + 4, box[2] + 3, box[3] + 4), fill=70)
    im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(3, size // 8))))
    d = ImageDraw.Draw(im)
    d.rectangle(box, fill=(250, 249, 247), outline=EDGE, width=max(1, size // 22))
    return d


def occupancy(key, size):
    """cost map in plan px from the 3D scene of the plan: walls/shafts 10, furniture 1, rugs 0.3 (0 = free floor)."""
    import json
    import numpy as np
    P = "/mnt/c/Projects/3d_visual/"
    name = json.load(open(P + "plans_prepared/index_new.json"))[key]["name"]
    sc = json.load(open(P + f"renders/{name}/code3d/scene.json"))
    occ = np.zeros((size[1], size[0]), np.float32)
    for r in sc["walls"]:
        occ[int(r[1]):int(r[3]), int(r[0]):int(r[2])] = 10
    for r in sc.get("outside", []):
        occ[int(r[1]):int(r[3]), int(r[0]):int(r[2])] = 10
    import cv2, math
    for it in sc["items"]:
        if it["type"] == "leaf":
            hx, hz = it["hinge"]; an = math.radians(it.get("angle", 0))
            cv2.line(occ, (int(hx), int(hz)), (int(hx + math.cos(an) * it["len"]), int(hz + math.sin(an) * it["len"])), 3.0, 40)
            continue
        if "box" not in it:
            continue
        b = [int(v) for v in it["box"]]
        c = {"shaft": 10, "glass": 10}.get(it["type"], 1.0)
        occ[b[1]:b[3], b[0]:b[2]] = np.maximum(occ[b[1]:b[3], b[0]:b[2]], c)
    # keep a small gap to walls and furniture (the photoreal render is not pixel-exact)
    occ = cv2.dilate(occ, np.ones((25, 25), np.uint8))
    # soft penalty near anything (objects in the photoreal render are drawn a bit larger than in the plan)
    free = (occ == 0).astype(np.uint8)
    dt = cv2.distanceTransform(free, cv2.DIST_L2, 5)
    occ = occ + 0.35 * np.clip(1 - dt / 70.0, 0, 1) * free
    return occ


def place(occ, box, taken, radius, step=4, dist_w=0.02):
    """shift box (plan px) to the nearest spot with the least overlap with objects/walls and other labels."""
    import numpy as np
    x0, y0, x1, y1 = box
    ii = occ.cumsum(0).cumsum(1)
    def cost_at(dx, dy):
        a0, b0, a1, b1 = int(x0 + dx), int(y0 + dy), int(x1 + dx), int(y1 + dy)
        if a0 < 1 or b0 < 1 or a1 >= occ.shape[1] or b1 >= occ.shape[0]:
            return 1e9
        c = ii[b1, a1] - ii[b0 - 1, a1] - ii[b1, a0 - 1] + ii[b0 - 1, a0 - 1]
        for t in taken:
            ox = max(0, min(a1, t[2]) - max(a0, t[0])); oy = max(0, min(b1, t[3]) - max(b0, t[1]))
            c += ox * oy * 20
        return c + dist_w * (dx * dx + dy * dy)
    best = min(((dx, dy) for dx in range(-radius, radius + 1, step) for dy in range(-radius, radius + 1, step)), key=lambda d: cost_at(*d))
    return (x0 + best[0], y0 + best[1], x1 + best[0], y1 + best[1])

BADGE_VARIANTS = ("matte", "glass", "dark", "split", "card", "outline", "glass_r", "dark_r", "clear_r", "real1", "real2", "real3")
TAN = (176, 138, 98)
WHITE = (255, 255, 255)


def panel(im, box, var, s, mid=None):
    """Background + frame of a badge (mid = x of the vertical divider) or of a room-area label (mid=None) in style var.
    s = stroke scale (badge height), so frames, glows and shadows match between the badge and the labels.
    Returns (left text colour, right text colour, divider colour, text needs a shadow)."""
    import numpy as np
    from PIL import ImageChops, ImageEnhance
    x0, y0, x1, y1 = box
    h = y1 - y0
    fr = max(2, int(s) // 40)
    rounded = var in ("glass_r", "dark_r", "clear_r", "real1", "real2", "real3")
    rad = int(min(s * 0.13, h * 0.3)) if rounded else 0
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, rad, fill=255)

    def shadow(alpha, blur, dx=0, dy=0):
        sh = Image.new("L", im.size, 0)
        ImageDraw.Draw(sh).rounded_rectangle((x0 + dx, y0 + dy, x1 + dx, y1 + dy), rad, fill=alpha)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(2, blur))))

    def fill(col, alpha, part=None):
        m = mask if part is None else ImageChops.multiply(mask, _rect_mask(im.size, (part[0], y0, part[1], y1 + 1)))
        im.paste(col, (0, 0), m.point(lambda v: int(v * alpha)))

    def blurred(r, bright=1.0, tint=None, tint_a=0.0):
        pad = int(s)
        reg = im.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).filter(ImageFilter.GaussianBlur(max(1, int(r))))
        if bright != 1.0:
            reg = ImageEnhance.Brightness(reg).enhance(bright)
        if tint:
            reg = Image.blend(reg, Image.new("RGB", reg.size, tint), tint_a)
        g = Image.new("RGB", im.size); g.paste(reg, (x0 - pad, y0 - pad))
        return g

    def frame(col, width, alpha=255):
        fl = Image.new("L", im.size, 0)
        ImageDraw.Draw(fl).rounded_rectangle(box, rad, outline=alpha, width=width)
        im.paste(col, (0, 0), fl)

    def top_light():
        yy, xx = np.mgrid[0:h, 0:x1 - x0]
        tl = Image.fromarray((255 * np.clip(1.15 - (yy / h * 0.8 + xx / max(1, x1 - x0) * 0.5), 0.25, 1)).astype("uint8"))
        lit = Image.new("L", im.size, 0); lit.paste(tl, (x0, y0))
        return tl, lit

    if var in ("real1", "real2", "real3"):
        # realistic clear glass: light blur, faint tint, edge glow lit from the top-left, white text with a shadow
        blur_r, tint_a, bright = {"real1": (s / 16, 0.14, 1.06), "real2": (s / 40, 0.08, 1.04), "real3": (s / 10, 0.2, 1.08)}[var]
        shadow(45, s / 14, int(s) // 60, int(s) // 25)
        im.paste(blurred(blur_r, bright, WHITE, tint_a), (0, 0), mask)
        ew = max(3, int(s) // 18)
        edge = Image.new("L", im.size, 0)
        ImageDraw.Draw(edge).rounded_rectangle(box, rad, outline=255, width=ew)
        edge = ImageChops.multiply(edge.filter(ImageFilter.GaussianBlur(ew / 2)), mask)
        tl, lit = top_light()
        im.paste(WHITE, (0, 0), ImageChops.multiply(edge, lit).point(lambda v: int(v * 0.85)))
        dark = Image.new("L", im.size, 0); dark.paste(ImageChops.invert(tl).point(lambda v: int(v * 0.35)), (x0, y0))
        im.paste((0, 0, 0), (0, 0), ImageChops.multiply(edge, dark))
        rim = Image.new("L", im.size, 0)
        ImageDraw.Draw(rim).rounded_rectangle(box, rad, outline=255, width=max(2, fr // 2))
        im.paste(WHITE, (0, 0), ImageChops.multiply(rim, lit).point(lambda v: int(v * 0.95)))
        return WHITE, WHITE, WHITE, True
    if var in ("glass_r", "dark_r", "clear_r"):
        # rounded glass: blurred floor under a tint, white frame, soft drop shadow and a light top sheen
        shadow(70, s / 12, 0, int(s) // 30)
        tint, alpha, col = {"glass_r": (WHITE, 0.5, TEXT), "dark_r": ((38, 34, 32), 0.5, WHITE), "clear_r": (WHITE, 0.28, WHITE)}[var]
        g = blurred(s / 7, 1.0, tint, alpha)
        sh = Image.new("L", (1, h)); sh.putdata([int(60 * max(0, 1 - i / (h * 0.55))) for i in range(h)])
        sheen = Image.new("L", im.size, 0); sheen.paste(sh.resize((x1 - x0, h)), (x0, y0))
        g.paste(WHITE, (0, 0), sheen)
        im.paste(g, (0, 0), mask)
        frame(WHITE, fr, 230)
        return col, col, col, var == "clear_r"
    if var == "matte":
        shadow(60, s / 14, 0, int(s) // 40)
        fill(WHITE, 0.86)
        frame(WHITE, fr)
        return TEXT, TEXT, TEXT, False
    if var in ("glass", "dark"):
        shadow(55, s / 12, 0, int(s) // 40)
        tint, a = (WHITE, 0.55) if var == "glass" else ((38, 34, 32), 0.55)
        im.paste(blurred(s / 8, 1.0, tint, a), (0, 0), mask)
        frame(WHITE, fr)
        c = TEXT if var == "glass" else WHITE
        return c, c, c, False
    if var == "split":
        # badge: tan left part with white text + white right part; room labels: tan with white text
        shadow(70, s / 14, 0, int(s) // 40)
        if mid is None:
            fill(TAN, 1.0)
        else:
            fill(TAN, 1.0, (x0, mid)); fill(WHITE, 1.0, (mid, x1 + 1))
        frame(WHITE, fr)
        return WHITE, (WHITE if mid is None else TEXT), None, False
    if var == "card":
        shadow(90, s / 10, int(s) // 50, int(s) // 25)
        fill(WHITE, 1.0)
        frame((225, 222, 218), max(1, fr // 2))
        return TEXT, TEXT, EDGE, False
    if var == "outline":
        frame(WHITE, fr)
        return WHITE, WHITE, WHITE, True
    raise ValueError(var)


def _rect_mask(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rectangle(r, fill=255)
    return m


def shadowed(im, paint, cols, need_shadow, s):
    """paint(draw, cols) draws text strokes; with need_shadow a blurred dark copy goes under them first."""
    if need_shadow:
        sh = Image.new("L", im.size, 0)
        paint(ImageDraw.Draw(sh), tuple(150 if c is not None else None for c in cols))
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(2, int(s) // 35))))
    paint(ImageDraw.Draw(im), cols)


def badge_variant(im, box, mid, n, word, total, fonts, var):
    """Badge: big letter/number, horizontal line, word under it | vertical line | area in bold; look = panel(var)."""
    x0, y0, x1, y1 = box
    bh = y1 - y0
    fb, fw, fa = fonts
    fr = max(3, bh // 40)
    lc = (x0 + mid) / 2
    if var == "outline":   # the frame of the outline badge also gets the shadow
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rectangle(box, outline=200, width=fr)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(3, bh // 30))))
    lcol, rcol, linecol, need = panel(im, box, var, bh, mid)

    def paint(dd, cols):
        l, r, ln = cols
        ul = max(dd.textlength(n, font=fb), dd.textlength(word, font=fw)) * 0.7
        dd.text((lc, y0 + bh * 0.37), n, font=fb, fill=l, anchor="mm")
        dd.line([(lc - ul / 2, y0 + bh * 0.645), (lc + ul / 2, y0 + bh * 0.645)], fill=l, width=fr)
        dd.text((lc, y0 + bh * 0.79), word, font=fw, fill=l, anchor="mm")
        dd.text(((mid + x1) / 2, (y0 + y1) / 2), total, font=fa, fill=r, anchor="mm")
        if ln is not None:
            dd.line([(mid, y0 + bh * 0.18), (mid, y1 - bh * 0.18)], fill=ln, width=fr)
    shadowed(im, paint, (lcol, rcol, linecol), need, bh)
    return im


def label_variant(im, box, t, f, var, s):
    """Room-area label in the same look as the badge of style var (s = badge height for matching strokes)."""
    x0, y0, x1, y1 = box
    if var == "outline":
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rectangle(box, outline=200, width=max(2, int(s) // 40))
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(3, int(s) // 30))))
    col, _, _, need = panel(im, box, var, s)
    def paint(dd, cols):
        dd.text(((x0 + x1) / 2, (y0 + y1) / 2), t, font=f, fill=cols[0], anchor="mm")
    shadowed(im, paint, (col,), need, s)
    return im


PREMIUM = ("p1", "p2", "p3", "p4")
CHAMPAGNE = (214, 190, 150)
GRAPHITE = (44, 40, 38)


def _text_shadowed(im, items, col, s, shadow=150):
    """items = [(xy, text, font, anchor)] or [("line", pts, width)]; white/colour text with a soft dark shadow under it."""
    def paint(dd, c):
        for it in items:
            if it[0] == "line":
                dd.line(it[1], fill=c, width=it[2])
            elif it[0] == "rect":
                dd.rectangle(it[1], outline=c, width=it[2])
            else:
                dd.text(it[0], it[1], font=it[2], fill=c, anchor=it[3])
    if shadow:
        sh = Image.new("L", im.size, 0); paint(ImageDraw.Draw(sh), shadow)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(2, int(s) // 30))))
    paint(ImageDraw.Draw(im), col)


def premium_label_lines(t, name, size, style):
    """fonts + lines of a premium room label: p1/p3 = "15,3 м²" only, p2/p4 = NAME (small caps) over the area."""
    fa = font(size, 500)
    if style in ("p2", "p4") and name:
        fn = font(int(size * 0.5), 500)
        return [(name.upper(), fn, int(size * 0.5)), (t + " м²", fa, size)]
    return [(t + " м²", fa, size)]


def premium_label(im, cx, cy, lines, style, s):
    d = ImageDraw.Draw(im)
    gap = lines[-1][2] * 0.28
    H = sum(l[2] for l in lines) + gap * (len(lines) - 1)
    y = cy - H / 2
    items = []
    for i, (txt, f, h) in enumerate(lines):
        if i == 0 and len(lines) > 1:     # spaced small caps
            sp = h * 0.16
            w = sum(d.textlength(ch, font=f) for ch in txt) + sp * (len(txt) - 1)
            x = cx - w / 2
            for ch in txt:
                items.append(((x, y + h / 2), ch, f, "lm")); x += d.textlength(ch, font=f) + sp
        else:
            items.append(((cx, y + h / 2), txt, f, "mm"))
        y += h + gap
    if style == "p4":
        w = max(d.textlength(l[0], font=l[1]) * (1.2 if len(lines) > 1 and l is lines[0] else 1) for l in lines)
        box = (int(cx - w / 2 - lines[-1][2] * 0.55), int(cy - H / 2 - lines[-1][2] * 0.4), int(cx + w / 2 + lines[-1][2] * 0.55), int(cy + H / 2 + lines[-1][2] * 0.4))
        panel(im, box, "dark_r", s)
        name_items = [it for it in items if it[3] == "lm"]
        _text_shadowed(im, name_items, CHAMPAGNE, s, 0)
        _text_shadowed(im, [it for it in items if it[3] != "lm"], WHITE, s, 0)
    else:
        _text_shadowed(im, items, WHITE, s)
    return im


def premium_badge(im, box, n, word, total, style):
    """p1/p2: thin white frame, light letter, line + word, area with м²; p4: dark rounded glass, champagne letter.
    p3 is drawn outside the apartment by premium_info()."""
    x0, y0, x1, y1 = box
    bh = y1 - y0
    fb, fw, fa, fu = font(int(bh * 0.46), 300), font(int(bh * 0.15), 500), font(int(bh * 0.27), 500), font(int(bh * 0.15), 500)
    d = ImageDraw.Draw(im)
    lw = max(d.textlength(n, font=fb), d.textlength(word, font=fw) * 1.25) + bh * 0.5
    tw = d.textlength(total, font=fa) + d.textlength(" м²", font=fu)
    rw = tw + bh * 0.55
    cxm = (x0 + x1) / 2
    x0, x1 = int(cxm - (lw + rw) / 2), int(cxm + (lw + rw) / 2)
    mid = x0 + lw; lc = (x0 + mid) / 2
    fr = max(2, bh // 60)
    ul = max(d.textlength(n, font=fb), d.textlength(word, font=fw)) * 0.75
    sp = bh * 0.025
    ww = sum(d.textlength(ch, font=fw) for ch in word) + sp * (len(word) - 1)
    wi = []; x = lc - ww / 2
    for ch in word:
        wi.append(((x, y0 + bh * 0.8), ch, fw, "lm")); x += d.textlength(ch, font=fw) + sp
    ax = (mid + x1) / 2 - tw / 2
    left = [((lc, y0 + bh * 0.38), n, fb, "mm"), ("line", [(lc - ul / 2, y0 + bh * 0.655), (lc + ul / 2, y0 + bh * 0.655)], fr)] + wi
    right = [((ax, (y0 + y1) / 2), total, fa, "lm"), ((ax + d.textlength(total, font=fa), (y0 + y1) / 2 - bh * 0.06), " м²", fu, "lm")]
    div = ("line", [(mid, y0 + bh * 0.2), (mid, y1 - bh * 0.2)], fr)
    if style == "p4":
        panel(im, (x0, y0, x1, y1), "dark_r", bh)
        _text_shadowed(im, left, CHAMPAGNE, bh, 0)
        _text_shadowed(im, right + [div], WHITE, bh, 0)
    else:
        _text_shadowed(im, [("rect", (x0, y0, x1, y1), fr)] + left + right + [div], WHITE, bh)
    return im


def premium_info(im, n, word, total, bh0):
    """p3: the badge leaves the apartment and becomes a typographic block on the white margin (graphite + tan lines).
    Tries big to small sizes and puts the block in the middle of the largest free white area."""
    import numpy as np
    from scipy import ndimage
    d = ImageDraw.Draw(im)
    a = np.asarray(im.convert("L")) < 238
    a[:3, :] = a[-3:, :] = True; a[:, :3] = a[:, -3:] = True     # image borders count as obstacles too
    far = ndimage.distance_transform_edt(~a)
    for scale in (1.6, 1.4, 1.2, 1.0, 0.85, 0.7, 0.6):
        bh = int(bh0 * scale)
        fb, fw, fa, fu = font(int(bh * 0.6), 300), font(int(bh * 0.15), 500), font(int(bh * 0.36), 400), font(int(bh * 0.2), 400)
        fl = font(int(bh * 0.11), 500)
        sp = bh * 0.03
        ww = sum(d.textlength(ch, font=fw) for ch in word.upper()) + sp * (len(word) - 1)
        lw = max(d.textlength(n, font=fb), ww) + bh * 0.35
        tw = max(d.textlength(total, font=fa) + d.textlength(" м²", font=fu), d.textlength("ОБЩАЯ ПЛОЩАДЬ", font=fl))
        W, H = int(lw + bh * 0.3 + tw), bh
        pad = bh * 0.45
        best = None
        st = max(8, H // 8)
        for yy in range(0, im.size[1] - H, st):
            for xx in range(0, im.size[0] - W, st):
                m = far[yy:yy + H:6, xx:xx + W:6].min()
                if m > pad and (best is None or m > best[0]):
                    best = (m, xx, yy)
        if best:
            break
    if best is None:
        print("no free margin for the info block"); return im
    _, x0, y0 = best
    lc = x0 + (lw - bh * 0.35) / 2
    d.text((lc, y0 + H * 0.4), n, font=fb, fill=GRAPHITE, anchor="mm")
    ul = max(d.textlength(n, font=fb), ww) * 0.8
    d.line([(lc - ul / 2, y0 + H * 0.74), (lc + ul / 2, y0 + H * 0.74)], fill=TAN, width=max(2, bh // 45))
    x = lc - ww / 2
    for ch in word.upper():
        d.text((x, y0 + H * 0.9), ch, font=fw, fill=GRAPHITE, anchor="lm"); x += d.textlength(ch, font=fw) + sp
    mx = x0 + lw
    d.line([(mx, y0 + H * 0.12), (mx, y0 + H * 0.95)], fill=TAN, width=max(2, bh // 45))
    ax = mx + bh * 0.3
    d.text((ax, y0 + H * 0.58), total, font=fa, fill=GRAPHITE, anchor="lm")
    d.text((ax + d.textlength(total, font=fa), y0 + H * 0.5), " м²", font=fu, fill=GRAPHITE, anchor="lm")
    d.text((ax, y0 + H * 0.22), "ОБЩАЯ ПЛОЩАДЬ", font=fl, fill=(140, 128, 118), anchor="lm")
    return im


INTL = ("f1", "f2", "f3", "f4")
SERIF = __file__.rsplit("/", 1)[0] + "/fonts/Cormorant.ttf"
GOLD = (184, 151, 90)
GREIGE = (236, 232, 225)


def serif(size, weight=400):
    f = ImageFont.truetype(SERIF, size, layout_engine=ImageFont.Layout.RAQM)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


LN = ["lnum"]


def _spaced(d, x, y, txt, f, sp, anchor="l"):
    """letter-spaced caps; returns items for _paint and the total width. anchor l/m = x is left/centre."""
    w = sum(d.textlength(ch, font=f) for ch in txt) + sp * (len(txt) - 1)
    if anchor == "m":
        x -= w / 2
    items = []
    for ch in txt:
        items.append(((x, y), ch, f, "lm")); x += d.textlength(ch, font=f) + sp
    return items, w


def _paint(im, items, col, shadow=0, blur=4):
    def go(dd, c):
        for it in items:
            if it[0] == "line":
                dd.line(it[1], fill=c, width=it[2])
            elif it[0] == "rect":
                dd.rectangle(it[1], outline=c, width=it[2])
            elif it[0] == "circle":
                dd.ellipse(it[1], outline=c, width=it[2])
            else:
                dd.text(it[0], it[1], font=it[2], fill=c, anchor=it[3], features=LN)
    if shadow:
        sh = Image.new("L", im.size, 0); go(ImageDraw.Draw(sh), shadow)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))
    go(ImageDraw.Draw(im), col)


def intl_label_size(d, t, size, style):
    fa, fu = serif(int(size * 1.25), 500), serif(int(size * 0.78), 500)
    w = d.textlength(t, font=fa, features=LN) + d.textlength("\u2009м²", font=fu, features=LN)
    if style == "f3":
        r = max(w * 0.62, size * 1.15)
        return 2 * r, 2 * r
    return w, size * 1.6


def intl_label(im, cx, cy, t, size, style, s):
    d = ImageDraw.Draw(im)
    fa, fu = serif(int(size * 1.25), 500), serif(int(size * 0.78), 500)
    wa = d.textlength(t, font=fa, features=LN); w = wa + d.textlength("\u2009м²", font=fu, features=LN)
    x = cx - w / 2
    hl = max(2, int(s) // 70)
    txt = [((x, cy), t, fa, "lm"), ((x + wa, cy - size * 0.22), "\u2009м²", fu, "lm")]
    blur = max(2, int(s) // 30)
    if style == "f3":
        r = max(w * 0.62, size * 1.15)
        box = (int(cx - r), int(cy - r), int(cx + r), int(cy + r))
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse(box, fill=255)
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).ellipse((box[0], box[1] + r * 0.08, box[2], box[3] + r * 0.08), fill=60)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(r * 0.15)))
        pad = int(r)
        reg = im.crop((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)).filter(ImageFilter.GaussianBlur(max(2, int(r * 0.12))))
        reg = Image.blend(reg, Image.new("RGB", reg.size, (40, 34, 30)), 0.35)
        gl = Image.new("RGB", im.size); gl.paste(reg, (box[0] - pad, box[1] - pad))
        im.paste(gl, (0, 0), m)
        _paint(im, [("circle", box, hl), ("circle", (box[0] + hl * 3, box[1] + hl * 3, box[2] - hl * 3, box[3] - hl * 3), max(1, hl // 2))], WHITE)
        _paint(im, txt, WHITE)
        return im
    ul = w * 0.35
    line = ("line", [(cx - ul / 2, cy + size * 0.95), (cx + ul / 2, cy + size * 0.95)], hl)
    _paint(im, txt + ([line] if style != "f4" else []), WHITE, 150, blur)
    if style == "f4":
        _paint(im, [line], GOLD)
    return im


def intl_badge(im, box, n, word, total, style):
    """f1/f3: double white hairline frame, serif letter, hairline, spaced caps word | serif area;
    f4: solid gold card with a white inset frame. (f2 = spec strip, see intl_strip)."""
    x0, y0, x1, y1 = box
    bh = y1 - y0
    d = ImageDraw.Draw(im)
    fb, fa, fu = serif(int(bh * 0.62), 400), serif(int(bh * 0.4), 500), serif(int(bh * 0.2), 500)
    fw = font(int(bh * 0.12), 500); sp = bh * 0.03
    ww = sum(d.textlength(ch, font=fw) for ch in word.upper()) + sp * (len(word) - 1)
    lw = max(d.textlength(n, font=fb, features=LN), ww) + bh * 0.55
    wa = d.textlength(total, font=fa, features=LN); tw = wa + d.textlength("\u2009м²", font=fu, features=LN)
    rw = tw + bh * 0.6
    cxm = (x0 + x1) / 2
    x0, x1 = int(cxm - (lw + rw) / 2), int(cxm + (lw + rw) / 2)
    mid = x0 + lw; lc = (x0 + mid) / 2
    hl = max(2, bh // 70); ins = int(bh * 0.06)
    ul = max(d.textlength(n, font=fb, features=LN), ww) * 0.7
    wi, _ = _spaced(d, lc, y0 + bh * 0.8, word.upper(), fw, sp, "m")
    ax = (mid + x1) / 2 - tw / 2
    items = [((lc, y0 + bh * 0.4), n, fb, "mm"), ("line", [(lc - ul / 2, y0 + bh * 0.67), (lc + ul / 2, y0 + bh * 0.67)], hl)] + wi
    items += [("line", [(mid, y0 + bh * 0.22), (mid, y1 - bh * 0.22)], hl), ((ax, (y0 + y1) / 2), total, fa, "lm"), ((ax + wa, (y0 + y1) / 2 - bh * 0.1), "\u2009м²", fu, "lm")]
    frames = [("rect", (x0, y0, x1, y1), hl), ("rect", (x0 + ins, y0 + ins, x1 - ins, y1 - ins), max(1, hl // 2))]
    if style == "f4":
        sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rectangle((x0, y0 + bh // 30, x1, y1 + bh // 30), fill=90)
        im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(bh // 12)))
        ImageDraw.Draw(im).rectangle((x0, y0, x1, y1), fill=GOLD)
        _paint(im, [frames[1]] + items, WHITE)
    else:
        _paint(im, frames + items, WHITE, 150, max(3, bh // 30))
    return im


def intl_strip(im, n, word, total, bh):
    """f2: Bulgari / ANWA style spec strip added under the image: greige band, serif letter + spaced caps, columns."""
    W, H = im.size
    sh = int(bh * 1.5)
    out = Image.new("RGB", (W, H + sh), WHITE); out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    m = int(W * 0.06)
    y0, y1 = H + int(sh * 0.12), H + sh - int(sh * 0.18)
    d.rectangle((m, y0, W - m, y1), fill=GREIGE)
    hh = y1 - y0; cy = (y0 + y1) / 2
    fb = serif(int(hh * 0.62), 400); fw = font(int(hh * 0.105), 600); fv = serif(int(hh * 0.36), 500); fu = serif(int(hh * 0.18), 500)
    sp = hh * 0.035
    x = m + hh * 0.45
    lw = max(d.textlength(n, font=fb, features=LN), 1)
    items = [((x + lw / 2, y0 + hh * 0.4), n, fb, "mm")]
    ul = lw * 1.4
    items.append(("line", [(x + lw / 2 - ul / 2, y0 + hh * 0.7), (x + lw / 2 + ul / 2, y0 + hh * 0.7)], max(2, hh // 80)))
    wi, ww = _spaced(d, x + lw / 2, y0 + hh * 0.83, word.upper(), fw, sp, "m")
    items += wi
    x = x + max(lw, ww) / 2 + lw / 2 + hh * 0.5
    cols = [("ТИП КВАРТИРЫ", "Студия" if word.startswith("студ") else f"{n}-комнатная", None), ("ОБЩАЯ ПЛОЩАДЬ", total, " м²")]
    for title, val, unit in cols:
        items.append(("line", [(x, y0 + hh * 0.2), (x, y1 - hh * 0.2)], max(1, hh // 110)))
        x += hh * 0.4
        ti, tw_ = _spaced(d, x, y0 + hh * 0.33, title, fw, sp)
        items += ti
        items.append(((x, y0 + hh * 0.64), val, fv, "lm"))
        vw = d.textlength(val, font=fv, features=LN)
        if unit:
            items.append(((x + vw, y0 + hh * 0.58), unit, fu, "lm")); vw += d.textlength(unit, font=fu, features=LN)
        x += max(tw_, vw) + hh * 0.6
    _paint(out, items, GRAPHITE)
    return out


import luxe  # noqa: E402


def _shift(items, ox, oy):
    out = []
    for it in items:
        if it[0] == "line":
            out.append(("line", [(x + ox, y + oy) for x, y in it[1]], it[2]))
        elif it[0] in ("rect", "circle"):
            b = it[1]; out.append((it[0], (b[0] + ox, b[1] + oy, b[2] + ox, b[3] + oy), it[2]))
        else:
            out.append(((it[0][0] + ox, it[0][1] + oy),) + tuple(it[1:]))
    return out


def _mask_items(dd, items):
    for it in items:
        if it[0] == "line":
            dd.line(it[1], fill=255, width=it[2])
        else:
            dd.text(it[0], it[1], font=it[2], fill=255, anchor=it[3], features=LN)


def luxe_badge(im, box, n, word, total, style, placer=None):
    """l1..l5: material card (marble / lacquer / deco veil / velvet / ivory) with foil frame and foil serif content."""
    x0, y0, x1, y1 = box
    bh = int((y1 - y0) * 1.12)
    cy0 = (y0 + y1) / 2
    y0, y1 = int(cy0 - bh / 2), int(cy0 + bh / 2)
    d = ImageDraw.Draw(im)
    fb, fa, fu = serif(int(bh * 0.56), 500), serif(int(bh * 0.36), 600), serif(int(bh * 0.19), 600)
    fw = font(int(bh * 0.105), 600); sp = bh * 0.035
    ww = sum(d.textlength(ch, font=fw) for ch in word.upper()) + sp * (len(word) - 1)
    orn = style in ("l2", "l3", "l4")
    side = bh * (0.75 if orn else 0.55)
    lw = max(d.textlength(n, font=fb, features=LN), ww) + side
    wa = d.textlength(total, font=fa, features=LN); tw = wa + d.textlength("\u2009м²", font=fu, features=LN)
    rw = tw + side * 1.1
    cxm = (x0 + x1) / 2
    x0, x1 = int(cxm - (lw + rw) / 2), int(cxm + (lw + rw) / 2)
    if placer:      # find a free spot for the FINAL (bigger) card, with a margin for its shadow
        mg = int(bh * 0.12)
        nb = placer((x0 - mg, y0 - mg, x1 + mg, y1 + mg))
        x0, y0, x1, y1 = nb[0] + mg, nb[1] + mg, nb[2] - mg, nb[3] - mg
    mid = x0 + lw; lc = (x0 + mid) / 2
    hl = max(2, bh // 60)
    ul = max(d.textlength(n, font=fb, features=LN), ww) * 0.7
    wi, _ = _spaced(d, lc, y0 + bh * 0.79, word.upper(), fw, sp, "m")
    ax = (mid + x1) / 2 - tw / 2
    items = [((lc, y0 + bh * 0.41), n, fb, "mm"), ("line", [(lc - ul / 2, y0 + bh * 0.665), (lc + ul / 2, y0 + bh * 0.665)], hl)] + wi
    items += [("line", [(mid, y0 + bh * 0.24), (mid, y1 - bh * 0.24)], hl), ((ax, (y0 + y1) / 2), total, fa, "lm"), ((ax + wa, (y0 + y1) / 2 - bh * 0.09), "\u2009м²", fu, "lm")]
    rad = int(bh * 0.06) if style == "l5" else 0
    return luxe.card(im, (x0, y0, x1, y1), style, bh, lambda dd, ox, oy: _mask_items(dd, _shift(items, ox, oy)), ornaments=orn, radius=rad)


def luxe_label_size(d, t, size, style):
    fa, fu = serif(int(size * 1.2), 600), serif(int(size * 0.72), 600)
    w = d.textlength(t, font=fa, features=LN) + d.textlength("\u2009м²", font=fu, features=LN)
    if style == "l3":
        return w, size * 1.9
    return w + size * 1.3, size * 1.75


def luxe_label(im, cx, cy, t, size, style, s):
    d = ImageDraw.Draw(im)
    fa, fu = serif(int(size * 1.2), 600), serif(int(size * 0.72), 600)
    wa = d.textlength(t, font=fa, features=LN); w = wa + d.textlength("\u2009м²", font=fu, features=LN)
    if style == "l3":    # gold foil numbers on a soft dark veil, deco rule with a diamond underneath
        bw, bh = w + size * 1.3, size * 1.95
        box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        def fn(dd, ox, oy):
            X, Y = cx + ox, cy + oy - size * 0.12
            _mask_items(dd, [((X - w / 2, Y), t, fa, "lm"), ((X - w / 2 + wa, Y - size * 0.24), "\u2009м²", fu, "lm")])
            hl = max(2, int(size) // 14); yl = Y + size * 0.72; L = w * 0.55
            dd.line([(X - L, yl), (X - size * 0.22, yl)], fill=255, width=hl); dd.line([(X + size * 0.22, yl), (X + L, yl)], fill=255, width=hl)
            dd.regular_polygon((X, yl, size * 0.13), 4, rotation=45, fill=255)
        return luxe.card(im, box, style, size * 2.6, fn, frame=False)
    bw, bh = w + size * 1.3, size * 1.75
    box = (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
    def fn(dd, ox, oy):
        X, Y = cx + ox, cy + oy
        _mask_items(dd, [((X - w / 2, Y), t, fa, "lm"), ((X - w / 2 + wa, Y - size * 0.24), "\u2009м²", fu, "lm")])
    return luxe.card(im, box, style, size * 2.6, fn, radius=int(size * 0.18) if style == "l5" else 0)


LABEL_AT = {"p149": {"2,2": (780, 1470)}, "p170": {"3,6": (1230, 1420)}}   # client: area label centre in RENDER px (placement search skipped)
BADGE_AT = {"n05": (1200, 1452), "p220": (955, 1080), "p161": (830, 690)}          # client: badge position (plan px centre), placement search skipped


def draw_plan(key, src, out, badge_style="v1", badge_word=None, room_names=None):
    """Labels and badge at the positions and sizes of the tan numbers / badge of the original plan.
    Texts come from the LABELS / BADGE lines of the message (matched to the nearest tan number)."""
    import numpy as np
    P = "/mnt/c/Projects/3d_visual/"
    msg = open(P + f"plans_prepared/{key}_message.txt", encoding="utf-8").read()
    texts, btxt = parse(msg)
    marks, badge = plan_marks(key)
    plan = Image.open(P + f"plans_prepared/{key}_clean.png")
    pa = np.asarray(plan.convert("RGB")).astype(int)
    wm = (pa[..., 0] < 90) & (abs(pa[..., 0] - pa[..., 1]) < 14) & (abs(pa[..., 1] - pa[..., 2]) < 14)
    from scipy import ndimage as _nd
    wm = _nd.binary_opening(wm, structure=np.ones((7, 7)))
    ys_, xs_ = np.where(wm)
    pcb = (xs_.min(), ys_.min(), xs_.max(), ys_.max())     # full outer wall extent
    im = Image.open(src).convert("RGB")
    k = im.size[0] / plan.size[0]
    d = ImageDraw.Draw(im)
    try:
        occ = occupancy(key, plan.size)
    except Exception as e:
        print("no occupancy:", e); occ = None
    taken = []
    strip_args = None
    fixed_badge = badge_style == "fig" and badge and key in BADGE_AT
    if fixed_badge:
        bw_, bh_ = 1.575 * (badge[3] - badge[1]) / 2, (badge[3] - badge[1]) / 2; bcx, bcy = BADGE_AT[key]
        badge = [bcx - bw_, bcy - bh_, bcx + bw_, bcy + bh_]
    if badge_style == "fig" and badge and (badge[3] - badge[1]) < 0.075 * plan.size[0]:    # big apartments: plate not smaller than 7.5% of the plan width
        sc_ = 0.075 * plan.size[0] / (badge[3] - badge[1]); bcx, bcy = (badge[0] + badge[2]) / 2, (badge[1] + badge[3]) / 2
        badge = [bcx + (badge[0] - bcx) * sc_, bcy + (badge[1] - bcy) * sc_, bcx + (badge[2] - bcx) * sc_, bcy + (badge[3] - bcy) * sc_]
    if btxt and badge and occ is not None and not fixed_badge:
        badge = list(place(occ, badge, taken, int((badge[3] - badge[1]) * 7.0), step=10, dist_w=0.0015))
    if badge:
        taken.append(badge)
    from scipy.optimize import linear_sum_assignment
    pts = [(pcb[0] + (pcb[2] - pcb[0]) * x / 100, pcb[1] + (pcb[3] - pcb[1]) * y / 100) for _, x, y in texts]
    med_h = float(np.median([m[2] for m in marks])) if marks else 40.0
    assign = {}
    if marks:
        cost = np.array([[((m[0] - px) ** 2 + (m[1] - py) ** 2) ** 0.5 for m in marks] for px, py in pts])
        ri, ci = linear_sum_assignment(cost)
        lim = max(220, 0.15 * (pcb[2] - pcb[0]))
        assign = {r: c for r, c in zip(ri, ci) if cost[r, c] <= lim}
        # same count of texts and plan numbers: trust the global assignment even for far points
        if len(marks) == len(pts):
            assign = {r: c for r, c in zip(ri, ci)}
    for ti, (t, x, y) in enumerate(texts):
        if ti in assign:
            cx, cy, h = marks[assign[ti]]
        else:
            (cx, cy), h = pts[ti], med_h        # no tan number near the message position: use it with the usual size
        size = int(h / 0.92 * k)
        f = font(size, 450)
        if badge_style == "fig":
            bhf = (badge[3] - badge[1]) * k if badge else size * 3.0
            uf = bhf / FIG["H"]; f = mfont(FIG["area"] * uf, 700); size = int(FIG["area"] * uf)
        tw = d.textlength(t, font=f)
        pw, ph = int(size * 0.4), int(size * 0.26)
        th = size
        if badge_style == "fig":                                         # reserve the real plate size (+ a gap) for placement
            pw, ph = int(FIG["pad_x"] * uf), int((FIG["small_h"] * uf - size) / 2)
        if badge_style in luxe.LUXE:
            tw, th = luxe_label_size(d, t, size, badge_style)
            pw, ph = int(size * 0.2), int(size * 0.15)
        if badge_style in INTL:
            tw, th = intl_label_size(d, t, size, badge_style)
            pw, ph = int(size * 0.3), int(size * 0.2)
        if badge_style in PREMIUM:
            size = int(size * 0.9)
            plines = premium_label_lines(t, (room_names or [None] * len(texts))[ti], size, badge_style)
            tw = max(d.textlength(l[0], font=l[1]) * (1.25 if len(plines) > 1 and l is plines[0] else 1) for l in plines)
            th = sum(l[2] for l in plines) + plines[-1][2] * 0.28 * (len(plines) - 1)
        pb = ((cx * k - tw / 2 - pw) / k, (cy * k - th * 0.5 - ph) / k, (cx * k + tw / 2 + pw) / k, (cy * k + th * 0.5 + ph) / k)
        fixed = LABEL_AT.get(key, {}).get(t)
        if fixed:
            fx, fy = fixed[0] / k, fixed[1] / k; hw_, hh_ = (pb[2] - pb[0]) / 2, (pb[3] - pb[1]) / 2; pb = (fx - hw_, fy - hh_, fx + hw_, fy + hh_)
        elif occ is not None:
            pb = place(occ, pb, taken, int(h * 5))
        taken.append(pb)
        cx, cy = (pb[0] + pb[2]) / 2 * k, (pb[1] + pb[3]) / 2 * k
        box = (int(cx - tw / 2 - pw), int(cy - size * 0.5 - ph), int(cx + tw / 2 + pw), int(cy + size * 0.5 + ph))
        if badge_style in luxe.LUXE:
            im = luxe_label(im, cx, cy, t, size, badge_style, 0)
            d = ImageDraw.Draw(im)
        elif badge_style in INTL:
            im = intl_label(im, cx, cy, t, size, badge_style, (badge[3] - badge[1]) * k if badge else size * 2.6)
            d = ImageDraw.Draw(im)
        elif badge_style in PREMIUM:
            im = premium_label(im, cx, cy, plines, badge_style, (badge[3] - badge[1]) * k if badge else size * 2.6)
            d = ImageDraw.Draw(im)
        elif badge_style in BADGE_VARIANTS:
            sb = (badge[3] - badge[1]) * k if badge else size * 2.6
            f = font(size, 600 if badge_style in ("outline", "real1", "real2", "real3", "clear_r", "dark", "dark_r", "split") else 500)
            im = label_variant(im, box, t, f, badge_style, sb)
            d = ImageDraw.Draw(im)
        elif badge_style == "fig":
            tb = d.textbbox((0, 0), t, font=f, anchor="mm")
            pw_ = (tb[2] - tb[0]) + 2 * FIG["pad_x"] * uf; ph_ = FIG["small_h"] * uf
            box = (int(cx - pw_ / 2), int(cy - ph_ / 2), int(cx + pw_ / 2), int(cy + ph_ / 2))
            fig_plate(im, box, uf); fig_text(im, (cx, cy), t, f, uf); d = ImageDraw.Draw(im)
        elif badge_style == "ref":
            bh_ = box[3] - box[1]; e = int(bh_ * 0.12)
            box = (box[0] - e, box[1] - e, box[2] + e, box[3] + e)
            _tan(im, box, box[3] - box[1])
            _wpaint(im, lambda dd, c: dd.text((cx, cy), t, font=f, fill=c, anchor="mm"), box[3] - box[1]); d = ImageDraw.Draw(im)
        else:
            d = _box(d, im, box, size)
            d.text((cx, cy), t, font=f, fill=TEXT, anchor="mm")
    if btxt and badge:
        n, total = btxt[0], btxt[1]
        x0, y0, x1, y1 = [int(v * k) for v in badge]
        bh = y1 - y0
        mid = x0 + int((x1 - x0) * 0.6)
        if badge_style in luxe.LUXE:
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн.")
            placer = None
            if occ is not None:
                others = [t for t in taken if t is not badge]
                def placer(b):
                    nb = place(occ, (b[0] / k, b[1] / k, b[2] / k, b[3] / k), others, int(bh / k * 6), step=8, dist_w=0.001)
                    return [int(v * k) for v in nb]
            im = luxe_badge(im, (x0, y0, x1, y1), n, word, total, badge_style, placer)
        elif badge_style in INTL:
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн.")
            if badge_style == "f2":
                strip_args = (n, word, total, bh)       # added after whiten_outside (it would bleach the band)
            else:
                if occ is not None:
                    nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                    x0, y0, x1, y1 = [int(v * k) for v in nb]
                im = intl_badge(im, (x0, y0, x1, y1), n, word, total, badge_style)
        elif badge_style in PREMIUM:
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн.")
            if badge_style == "p3":
                im = premium_info(im, n, word, total, bh)
            else:
                if occ is not None:
                    nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                    x0, y0, x1, y1 = [int(v * k) for v in nb]
                im = premium_badge(im, (x0, y0, x1, y1), n, word, total, badge_style)
        elif badge_style == "fig":
            # layout measured on the designer's plate (fractions of the plate height H; plate W = 1.575 H)
            u = bh / FIG["H"]; Hh = bh
            word = (badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн")).lower()   # Figma: lowercase "комн" (Manrope's Cyrillic lowercase reads as small caps)
            def fit_cap(txt, cap, w=700):
                f = mfont(cap * 1.4, w); bb = d.textbbox((0, 0), txt, font=f, anchor="ls")
                return mfont(cap * 1.4 * cap / max(1, bb[3] - bb[1] if txt.strip("1") == "" else (d.textbbox((0, 0), "Н", font=f, anchor="ls")[3] - d.textbbox((0, 0), "Н", font=f, anchor="ls")[1])), w)
            fb = fit_cap(n, 0.356 * Hh); fa = fit_cap("8", 0.208 * Hh); fw = mfont(FIG["word"] * 0.081 * Hh / (d.textbbox((0, 0), "н", font=mfont(FIG["word"]), anchor="ls")[3] - d.textbbox((0, 0), "н", font=mfont(FIG["word"]), anchor="ls")[1]), 700)
            track = 0
            ww = sum(d.textlength(ch, font=fw) for ch in word) + track * (len(word) - 1)
            colw = max(0.385 * Hh, ww + 0.004 * Hh)
            lcx = 0.345 * Hh + max(0, colw - 0.385 * Hh) / 2                   # column centre from the plate's left edge
            vxr = lcx + colw / 2 + 0.161 * Hh                                  # vertical line centre
            aw = d.textlength(total, font=fa)
            W = max(1.575 * Hh, vxr + 0.15 * Hh + aw + 0.17 * Hh)
            cxm = (x0 + x1) / 2
            x0, x1 = int(cxm - W / 2), int(cxm + W / 2); y1 = y0 + int(Hh)
            if occ is not None and not fixed_badge:
                mg = 0.08 * Hh / k
                nb = place(occ, (x0 / k - mg, y0 / k - mg, x1 / k + mg, y1 / k + mg), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                x0, y0, x1, y1 = [int(v * k) for v in (nb[0] + mg, nb[1] + mg, nb[2] - mg, nb[3] - mg)]
            fig_plate(im, (x0, y0, x1, y1), u)
            def glyph(txt, f, cx, top):                                        # place by the ink box: centre x, top y
                bb = d.textbbox((0, 0), txt, font=f, anchor="ls")
                return (cx - (bb[0] + bb[2]) / 2, top - bb[1])
            fig_text(im, glyph(n, fb, x0 + 0.329 * Hh + (lcx - 0.345 * Hh), y0 + 0.191 * Hh), n, fb, u, anchor="ls")
            ly = y0 + 0.629 * Hh
            fig_line(im, (x0 + lcx - colw / 2, ly), (x0 + lcx + colw / 2, ly), 0.0145 * Hh, u)
            cx_ = x0 + lcx - ww / 2; base = y0 + 0.831 * Hh
            for ch in word:                                                     # letter-spaced word
                fig_text(im, (cx_, base), ch, fw, u, FIG["word_shadow"], anchor="ls"); cx_ += d.textlength(ch, font=fw) + track
            vx = x0 + vxr
            fig_line(im, (vx, y0 + 0.124 * Hh), (vx, y0 + 0.880 * Hh), 0.018 * Hh, u)
            bb = d.textbbox((0, 0), total, font=fa, anchor="ls")
            fig_text(im, (vx + 0.15 * Hh - bb[0], y0 + 0.612 * Hh), total, fa, u, anchor="ls")
            d = ImageDraw.Draw(im)
        elif badge_style == "ref":
            # designer's reference: tan translucent rounded plate, white "1" bold, short line, "КОМН" caps | vertical line | area
            word = badge_word or ("СТУДИЯ" if n.strip().upper() in ("С", "C") else "КОМН")
            fb, fw, fa = dfont(int(bh * 0.6), 600), dfont(int(bh * 0.15), 700), dfont(int(bh * 0.36), 600)
            lw = max(d.textlength(n, font=fb), d.textlength(word, font=fw)) + bh * 0.6
            rw = d.textlength(total, font=fa) + bh * 0.6
            cxm = (x0 + x1) / 2; W = lw + rw
            x0, x1 = int(cxm - W / 2), int(cxm + W / 2)
            if occ is not None:
                nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                x0, y0, x1, y1 = [int(v * k) for v in nb]
            _tan(im, (x0, y0, x1, y1), bh)
            mid = int(x0 + lw); lc = (x0 + mid) / 2; fr = max(2, bh // 50)
            ul = max(d.textlength(n, font=fb) * 2.3, d.textlength(word, font=fw) * 1.05)
            def paint(dd, c):
                dd.text((lc, y0 + bh * 0.37), n, font=fb, fill=c, anchor="mm")
                dd.line([(lc - ul / 2, y0 + bh * 0.63), (lc + ul / 2, y0 + bh * 0.63)], fill=c, width=fr)
                dd.text((lc, y0 + bh * 0.8), word, font=fw, fill=c, anchor="mm")
                dd.line([(mid, y0 + bh * 0.13), (mid, y1 - bh * 0.13)], fill=c, width=fr)
                dd.text(((mid + x1) / 2, (y0 + y1) / 2), total, font=fa, fill=c, anchor="mm")
            _wpaint(im, paint, bh)
            d = ImageDraw.Draw(im)
        elif badge_style == "v3":
            # transparent badge: white frame, big letter/number with a horizontal line and the word under it | vertical line | area in bold; all white with a soft shadow
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн.")
            fb, fw, fa = font(int(bh * 0.44), 450), font(int(bh * 0.15), 450), font(int(bh * 0.25), 700)
            lw = max(d.textlength(n, font=fb), d.textlength(word, font=fw)) + bh * 0.55
            rw = d.textlength(total, font=fa) + bh * 0.6
            cxm = (x0 + x1) / 2; W = lw + rw
            x0, x1 = int(cxm - W / 2), int(cxm + W / 2)
            if occ is not None:
                nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                x0, y0, x1, y1 = [int(v * k) for v in nb]
            mid = int(x0 + lw); lc = (x0 + mid) / 2; fr = max(3, bh // 38)
            ul = max(d.textlength(n, font=fb), d.textlength(word, font=fw)) * 0.62
            def strokes(dd, col):
                dd.rectangle((x0, y0, x1, y1), outline=col, width=fr)
                dd.line([(mid, y0 + bh * 0.16), (mid, y1 - bh * 0.16)], fill=col, width=fr)
                dd.text((lc, y0 + bh * 0.38), n, font=fb, fill=col, anchor="mm")
                dd.line([(lc - ul / 2, y0 + bh * 0.66), (lc + ul / 2, y0 + bh * 0.66)], fill=col, width=fr)
                dd.text((lc, y0 + bh * 0.8), word, font=fw, fill=col, anchor="mm")
                dd.text(((mid + x1) / 2, (y0 + y1) / 2), total, font=fa, fill=col, anchor="mm")
            sh = Image.new("L", im.size, 0); strokes(ImageDraw.Draw(sh), 150)
            im.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(max(3, bh // 40))))
            d = ImageDraw.Draw(im); strokes(d, (255, 255, 255))
        elif badge_style in BADGE_VARIANTS:
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "комн.")
            fb, fw, fa = font(int(bh * 0.46), 500), font(int(bh * 0.165), 500), font(int(bh * 0.28), 700)
            lw = max(d.textlength(n, font=fb), d.textlength(word, font=fw)) + bh * 0.5
            rw = d.textlength(total, font=fa) + bh * 0.55
            cxm = (x0 + x1) / 2; W = lw + rw
            x0, x1 = int(cxm - W / 2), int(cxm + W / 2)
            if occ is not None:
                nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                x0, y0, x1, y1 = [int(v * k) for v in nb]
            im = badge_variant(im, (x0, y0, x1, y1), int(x0 + lw), n, word, total, (fb, fw, fa), badge_style)
        elif badge_style == "v2":
            # new badge: transparent background + frame, big letter/number | line | word over the area in bold
            word = badge_word or ("студия" if n.strip().upper() in ("С", "C") else "")
            fb, fw, fa = font(int(bh * 0.5), 500), font(int(bh * 0.17), 450), font(int(bh * 0.24), 700)
            lw = max(d.textlength(n, font=fb) + bh * 0.5, (x1 - x0) * 0.38)
            rw = max(d.textlength(word, font=fw), d.textlength(total, font=fa)) + bh * 0.5
            cxm = (x0 + x1) / 2; W = lw + rw
            x0, x1 = int(cxm - W / 2), int(cxm + W / 2)
            if W > (badge[2] - badge[0]) * k * 1.05 and occ is not None:           # wider than the original badge: find a free spot again
                nb = place(occ, (x0 / k, y0 / k, x1 / k, y1 / k), [t for t in taken if t is not badge], int(bh / k * 6), step=8, dist_w=0.001)
                x0, y0, x1, y1 = [int(v * k) for v in nb]
            mid = int(x0 + lw)
            fr = max(2, bh // 45)
            d.rectangle((x0, y0, x1, y1), outline=TEXT, width=fr)
            d.line([(mid, y0 + bh * 0.16), (mid, y1 - bh * 0.16)], fill=TEXT, width=fr)
            d.text(((x0 + mid) / 2, (y0 + y1) / 2), n, font=fb, fill=TEXT, anchor="mm")
            rc = (mid + x1) / 2
            d.text((rc, y0 + bh * 0.36), word, font=fw, fill=TEXT, anchor="mm")
            d.text((rc, y0 + bh * 0.66), total, font=fa, fill=TEXT, anchor="mm")
        else:
            d = _box(d, im, (x0, y0, x1, y1), bh // 4)
            d.line([(mid, y0 + bh * 0.12), (mid, y1 - bh * 0.12)], fill=EDGE, width=max(1, bh // 90))
            d.text(((x0 + mid) / 2, (y0 + y1) / 2), n, font=font(int(bh * 0.5), 450), fill=TEXT, anchor="mm")
            d.text(((mid + x1) / 2, (y0 + y1) / 2), total, font=font(int(bh * 0.2), 450), fill=TEXT, anchor="mm")
    im.save(out, quality=97)
    try:
        import whiten_outside
        whiten_outside.whiten(key, out)
    except Exception as e:
        print("whiten skipped:", e)
    if strip_args:
        intl_strip(Image.open(out).convert("RGB"), *strip_args).save(out, quality=97)


if __name__ == "__main__":
    draw(*sys.argv[1:4])
