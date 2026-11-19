"""Library of ready-made top-down pieces for fixing renders (wardrobe interiors, poufs, washer tops, ...).

assets/index.json:  {name: {"file": "wardrobe/xxx.png", "kind": "wardrobe|pouf|...", "back": "top",
                            "tags": [...], "aspect": w/h}}
  * "back" = the side of the piece that touches the wall (wardrobe back wall, pouf/cabinet back); pieces are stored
    with the back at the TOP. place() rotates the piece so its back faces the requested side.
  * files are already cropped to the content (wardrobe = interior between the carcass panels).

Usage:
    import assets
    assets.names("wardrobe")                                   # names
    assets.place(arr, "wardrobe_coats_dark", box_px, back="left")   # arr float/uint8 HxWx3, modified in place
    assets.place(arr, "pouf_rect", box_px, back="right", mask="round", shadow=True)
    assets.pick("wardrobe", avoid=[...], seed=k)             # a varied choice for the next wardrobe
"""
import json
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = "/mnt/c/Projects/3d_visual/assets/"
INDEX = ROOT + "index.json"
ROT = {"top": 0, "left": 1, "bottom": 2, "right": 3}          # number of 90° CCW turns to bring the back there


def index():
    return json.load(open(INDEX)) if os.path.exists(INDEX) else {}


def add(name, img, kind, back="top", tags=(), note=""):
    """store an RGB array (already cropped, back at `back`) under assets/<kind>/<name>.png, normalised to back=top."""
    idx = index()
    arr = np.asarray(img)[..., :3]
    arr = np.rot90(arr, -ROT[back])                          # bring the back to the top
    os.makedirs(ROOT + kind, exist_ok=True)
    rel = f"{kind}/{name}.png"
    Image.fromarray(np.ascontiguousarray(arr).astype(np.uint8)).save(ROOT + rel)
    idx[name] = {"file": rel, "kind": kind, "back": "top", "tags": list(tags), "note": note,
                 "aspect": round(arr.shape[1] / arr.shape[0], 3)}
    json.dump(idx, open(INDEX, "w"), indent=1, ensure_ascii=False)
    return rel


def names(kind=None):
    return [k for k, v in index().items() if kind is None or v["kind"] == kind]


def get(name, back="top"):
    e = index()[name]
    arr = np.asarray(Image.open(ROOT + e["file"]).convert("RGB"))
    return np.ascontiguousarray(np.rot90(arr, ROT[back]))


def pick(kind, avoid=(), seed=0, aspect=None):
    """a name of the given kind, not in `avoid`; with `aspect` prefers pieces whose (rotated) aspect fits."""
    cand = [n for n in names(kind) if n not in avoid] or names(kind)
    rng = np.random.default_rng(seed)
    if aspect:
        idx = index()
        cand.sort(key=lambda n: abs(np.log(max(idx[n]["aspect"], 1 / idx[n]["aspect"]) / max(aspect, 1 / aspect))))
        cand = cand[: max(3, len(cand) // 2)]
    return cand[int(rng.integers(len(cand)))]


def place(arr, name, box, back="top", mask=None, shadow=False, feather=1, crop_len=True):
    """paste asset `name` into box (x0,y0,x1,y1 px) with its back to `back`.
    crop_len: for long pieces (wardrobes) cut a window of the right proportion along the rail instead of squashing."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    w, h = x1 - x0, y1 - y0
    p = get(name, back).astype(np.float32)
    if crop_len and index()[name]["kind"] == "wardrobe" and "fit" not in index()[name].get("tags", []):
        along_x = back in ("top", "bottom")
        ph, pw = p.shape[:2]
        # choose the window so that both cut lines run through empty back panel (low detail), not through clothes
        g = cv2.cvtColor(p.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
        det = np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0 if along_x else 0, ksize=3)) + np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3))
        prof = det.mean(axis=0) if along_x else det.mean(axis=1)
        prof = np.convolve(prof, np.ones(9) / 9, mode="same")
        L = p.shape[1] if along_x else p.shape[0]
        need = int((p.shape[0] * w / h) if along_x else (p.shape[1] * h / w))
        if need < L:
            best = min(range(0, L - need + 1, 2), key=lambda o: prof[o] + prof[min(L - 1, o + need - 1)] + 0.02 * abs(o - (L - need) / 2))
            p = p[:, best:best + need] if along_x else p[best:best + need]
    p = cv2.resize(p, (w, h), interpolation=cv2.INTER_AREA)
    if mask == "round":
        m = Image.new("L", (w * 2, h * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle((3, 3, w * 2 - 3, h * 2 - 3), radius=int(min(w, h) * 0.7), fill=255)
        f = np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    elif mask == "ellipse":
        m = Image.new("L", (w * 2, h * 2), 0)
        ImageDraw.Draw(m).ellipse((3, 3, w * 2 - 3, h * 2 - 3), fill=255)
        f = np.asarray(m.resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    else:
        f = np.ones((h, w), np.float32)
        if feather:
            for j in range(feather):
                v = (j + 1) / (feather + 1); f[j] *= v; f[-1 - j] *= v; f[:, j] *= v; f[:, -1 - j] *= v
    out = arr.astype(np.float32)
    if shadow:
        sh = np.zeros(out.shape[:2], np.float32)
        d = max(4, min(w, h) // 8)
        sh[y0 + d:y1 + d, x0 + d // 2:x1 + d // 2] = 1
        sh = cv2.GaussianBlur(sh, (0, 0), d)
        out *= (1 - 0.35 * sh)[..., None]
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - f[..., None]) + p * f[..., None]
    arr[...] = out.astype(arr.dtype)
    return arr
