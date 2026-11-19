"""Side-by-side region crops: reference (upscaled) vs engine render. Usage: cmp.py render.png out_prefix"""
import sys
from PIL import Image
REF = "/mnt/c/Projects/3d_visual/reference_style.png"
REG = {"loggia": (38, 30, 420, 250), "bed": (38, 250, 400, 700), "kitchen": (430, 80, 820, 500), "bath": (540, 500, 820, 870), "wardrobe": (38, 690, 420, 880)}


def main(render, prefix, names=None):
    a = Image.open(REF).convert("RGB"); b = Image.open(render).convert("RGB")
    k = b.size[0] / a.size[0]
    for n, (x0, y0, x1, y1) in REG.items():
        if names and n not in names:
            continue
        ca = a.crop((x0, y0, x1, y1)).resize((int((x1 - x0) * k), int((y1 - y0) * k)), Image.LANCZOS)
        cb = b.crop([int(v * k) for v in (x0, y0, x1, y1)])
        c = Image.new("RGB", (ca.size[0] * 2 + 10, ca.size[1]), "white"); c.paste(ca, (0, 0)); c.paste(cb, (ca.size[0] + 10, 0))
        s = min(1.0, 1400 / c.size[0]); c = c.resize((int(c.size[0] * s), int(c.size[1] * s)), Image.LANCZOS)
        c.save(f"{prefix}_{n}.jpg", quality=88)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or None)
