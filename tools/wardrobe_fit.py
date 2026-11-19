"""Generate a wardrobe interior that fits a given target box exactly (first-time method):
3D blockout (closet.html) with the target proportions -> Gemini photoreal (top-down garments) -> crop interior.
Stored in assets as <name> (back at top). Usage from python: make(name, rail_len, depth, variant_dict)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.dirname(__file__) + "/scene3d")
import assets
from assets_gen_wardrobe import PAL, PROMPT_HANG, PROMPT_SHELF, FIX
PROMPT_TOPDOWN = """VIEWPOINT (most important): this is a FLOOR-PLAN view. The camera is on the ceiling and looks STRAIGHT DOWN (orthographic, 90 degrees, no perspective). It is NOT a front view of a wardrobe and NOT a shop display.
From straight above you see: the chrome rail as a thin straight line running along the long side of the image; each garment only as its TOP - the two shoulders and the collar of the garment lying across the rail as a narrow elongated shape perpendicular to the rail, with the wooden hanger on top of the shoulders and its hook over the rail; soft folds of fabric seen from above; the walnut floor of the wardrobe between the garments; shoes on the wardrobe floor seen from above (insoles visible). Nothing is seen from the front: no sleeves hanging towards the viewer, no vertical garments, no front of the cabinet.
IMAGE 2 is an example of exactly this top-down viewpoint - match its viewpoint and garment scale (NOT its content or colours).

"""
D = "/mnt/c/Projects/3d_visual/assets/wardrobe/src/"
RAT = {"16:9": 16 / 9, "3:2": 1.5, "4:3": 4 / 3, "5:4": 1.25, "1:1": 1, "4:5": .8, "3:4": .75, "2:3": 2 / 3, "9:16": 9 / 16}


def make(name, rail_len, depth, v, seed=7, scale=2.2, reuse=False, engine='gemini'):
    from closet_render import render
    import gem
    L, Dp = int(rail_len * scale), int(depth * scale)
    keys = list(dict.fromkeys(v.get("hang", [])))
    cfg = {"w": Dp, "h": L, "dividers": [], "seed": seed, "modes": [v["mode"]], "wallH": 700,
           "palette": [PAL[k] for k in keys] or [PAL["wshirt"]],
           "hang": [[keys.index(k) for k in v.get("hang", [])]], "shoes": [v.get("shoes", [])], "stacks": [v.get("stacks", [])]}
    render(cfg, D + f"{name}_block.png")
    im = Image.open(D + f"{name}_block.png").convert("RGB").rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)
    # canvas with walnut frame, padded to the nearest supported aspect
    iw, ih = 1100, int(1100 * im.size[1] / im.size[0])
    if ih > 1100:
        ih, iw = 1100, int(1100 * im.size[0] / im.size[1])
    FR = 40
    MG = int(0.13 * max(iw, ih))          # dark outer margin: Gemini's sparkle lands there, not on the clothes
    cw, ch = iw + 2 * FR + 2 * MG, ih + 2 * FR + 2 * MG
    rats = dict(RAT, **({'21:9': 21 / 9} if engine == 'studio' else {}))
    asp = min(rats, key=lambda k: abs(np.log(rats[k] / (cw / ch))))
    r = rats[asp]
    W, H = (cw, int(round(cw / r))) if cw / ch > r else (int(round(ch * r)), ch)
    W, H = max(W, cw), max(H, ch)
    canvas = Image.new("RGB", (W, H), (20, 20, 20))
    ox, oy = (W - cw) // 2 + MG, (H - ch) // 2 + MG
    cw, ch = cw - 2 * MG, ch - 2 * MG
    ImageDraw.Draw(canvas).rectangle((ox, oy, ox + cw - 1, oy + ch - 1), fill=(92, 58, 38))
    canvas.paste(im.resize((iw, ih), Image.LANCZOS), (ox + FR, oy + FR))
    ImageDraw.Draw(canvas).rectangle((ox + FR - 4, oy + FR - 4, ox + FR + iw + 3, oy + FR + ih + 3), outline=(52, 32, 20), width=4)
    canvas.save(D + f"{name}_in.png")
    txt = (PROMPT_SHELF if v["mode"] == "shelf" else PROMPT_HANG).replace(
        "Keep the strip of parquet and the black border exactly as in the image.", "Keep the dark border outside the wardrobe exactly as in the image.") + FIX
    out = D + f"{name}_ai.png"
    if not (reuse and os.path.exists(out)):
        ok = False
        if engine == 'studio':
            import studio
            ex = "/mnt/c/Projects/3d_visual/assets/wardrobe/wardrobe_fit_n03_a.png"
            studio.generate(PROMPT_TOPDOWN + txt, [D + f"{name}_in.png", ex], out, aspect=asp, tries=3)
            ok = os.path.exists(out) and Image.open(out).size[0] >= 2000
            if not ok: print('studio failed -> gemini', flush=True)
        if not ok and not gem.generate(txt, [D + f"{name}_in.png"], out, aspect=asp if asp in RAT else '16:9'):
            raise RuntimeError("generation failed")
    import ai_inpaint
    res = np.asarray(Image.open(out).convert("RGB"))
    # find the wardrobe on the dark canvas: bbox of the non-dark area, then step inside the carcass frame
    g = res.astype(np.float32).mean(axis=2)
    rows = np.where((g > 45).mean(axis=1) > 0.3)[0]; cols = np.where((g > 45).mean(axis=0) > 0.3)[0]
    y0, y1, x0, x1 = rows.min(), rows.max(), cols.min(), cols.max()
    fy = FR / (ih + 2 * FR) * (y1 - y0) * 1.1; fx = FR / (iw + 2 * FR) * (x1 - x0) * 1.1
    inner = res[int(y0 + fy): int(y1 - fy), int(x0 + fx): int(x1 - fx)]
    assets.add(name, inner, "wardrobe", back="top", tags=["fit"], note=f"fitted {rail_len}x{depth}")
    return name


def make_outer(name, Lout, Dout, frame, v, pxm, seed=7, scale=2.2, tries=2, dry=False, carcass=(104, 68, 46), extra=""):
    """Whole wardrobe INCLUDING its carcass, generated at the exact outer proportions of its place on the render.
    Lout x Dout: outer size along the rail x depth (plan px), frame: carcass thickness (plan px), pxm: plan px per metre.
    Garments/shoes have fixed real-world sizes (so every wardrobe of every plan shows the same garment scale).
    Stored in assets (back wall at the top); paste it into the OUTER box so no old layer can show."""
    from closet_render import render
    import gem
    L, Dp = Lout - 2 * frame, Dout - 2 * frame
    bpm = pxm * scale                                    # blockout px per metre
    keys = list(dict.fromkeys(v.get("hang", [])))
    cfg = {"w": int(Dp * scale), "h": int(L * scale), "dividers": [], "seed": seed, "modes": [v["mode"]], "wallH": 700,
           "palette": [PAL[k] for k in keys] or [PAL["wshirt"]], "hang": [[keys.index(k) for k in v.get("hang", [])]],
           "shoes": [v.get("shoes", [])], "stacks": [v.get("stacks", [])],
           "gw": 0.46 * bpm, "shoeL": 0.28 * bpm, "tk": bpm / 455.0}
    render(cfg, D + f"{name}_block.png")
    im = Image.open(D + f"{name}_block.png").convert("RGB").rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)
    iw = 1150; ih = int(round(iw * Dp / L))
    FR = max(6, int(round(frame * iw / L)))
    cw, ch = iw + 2 * FR, ih + 2 * FR
    MG = int(0.12 * cw)
    tw, th = cw + 2 * MG, ch + 2 * MG
    asp = min(RAT, key=lambda k: abs(np.log(RAT[k] / (tw / th))))
    r = RAT[asp]
    W, H = (tw, int(round(tw / r))) if tw / th > r else (int(round(th * r)), th)
    canvas = Image.new("RGB", (W, H), (20, 20, 20))
    ox, oy = (W - cw) // 2, (H - ch) // 2
    d = ImageDraw.Draw(canvas)
    d.rectangle((ox, oy, ox + cw - 1, oy + ch - 1), fill=tuple(carcass))
    d.rectangle((ox, oy, ox + cw - 1, oy + ch - 1), outline=(150, 112, 86), width=3)
    canvas.paste(im.resize((iw, ih), Image.LANCZOS), (ox + FR, oy + FR))
    d.rectangle((ox + FR - 2, oy + FR - 2, ox + FR + iw + 1, oy + FR + ih + 1), outline=(60, 38, 26), width=2)
    canvas.save(D + f"{name}_in.png")
    if dry:
        return D + f"{name}_in.png"
    base = (PROMPT_SHELF if v["mode"] == "shelf" else PROMPT_HANG).replace(
        "Keep the strip of parquet and the black border exactly as in the image.", "")
    # the generic shoe line lists three kinds -> Gemini tried to show all of them and added lone shoes; describe exactly what is in the blockout
    KIND = {"sneaker": "white sneakers with laces", "loafer": "brown leather loafers", "boot": "black leather ankle boots"}
    sh = v.get("shoes", [])
    shoe_txt = ("Shoes on the wardrobe floor: EXACTLY " + str(len(sh)) + " pair" + ("s" if len(sh) != 1 else "") + " ("
                + ", ".join("one pair of " + KIND.get(k, k) for _, k in sh) + ") exactly where the pairs are in image 1, seen strictly from above with the insole visible. "
                "NO other shoes: no single shoe, no third shoe, no extra pair. The empty part of the wardrobe floor stays EMPTY walnut.") if sh else \
               "There are NO shoes in this wardrobe. The wardrobe floor stays empty walnut."
    base = base.replace("Shoes on the wardrobe floor: real shoes seen strictly from above (white sneakers with laces, brown leather loafers, black leather ankle boots) with the insole visible inside.", shoe_txt)
    txt = base + FIX + ("\nThe light walnut rectangle framing the wardrobe is its carcass seen from above (side panels, back panel, "
                        "front edge): keep it exactly, same thickness, same position. Everything outside it stays plain dark. "
                        "Keep every garment and every shoe fully INSIDE the carcass, nothing crosses the frame, nothing is cut off. "
                        "Keep the number, order, size and spacing of the garments exactly as in image 1. Shoes always come in PAIRS: every pair = a left AND a right shoe side by side, both fully visible." + (" The carcass is LIGHT OAK wood." if sum(carcass) > 450 else "") + (" " + extra if extra else ""))
    out = D + f"{name}_ai.png"
    exp = cw / ch
    for t in range(tries):
        if os.path.exists(out):
            os.remove(out)
        if os.environ.get('ENGINE') == 'studio':
            import studio
            asp_s = min(studio.RATIOS, key=lambda k: abs(np.log(studio.RATIOS[k] / (tw / th))))
            ok = studio.generate(txt, [D + f"{name}_in.png"], out, aspect=asp_s, min_size=1500)
            ok = os.path.exists(out)
        else:
            ok = gem.generate(txt, [D + f"{name}_in.png"], out, aspect=asp)
        if not ok:
            continue
        res = np.asarray(Image.open(out).convert("RGB"))
        g = res.astype(np.float32).mean(axis=2)
        rows = np.where((g > 45).mean(axis=1) > 0.25)[0]; cols = np.where((g > 45).mean(axis=0) > 0.25)[0]
        y0, y1, x0, x1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
        got = (x1 - x0) / (y1 - y0)
        print(name, "aspect expected", round(exp, 3), "got", round(got, 3), flush=True)
        if abs(np.log(got / exp)) < 0.06:
            assets.add(name, res[y0:y1, x0:x1], "wardrobe", back="top", tags=["fit", "outer"], note=f"outer {Lout}x{Dout} f{frame}")
            return name
    raise RuntimeError("no generation with correct proportions")
