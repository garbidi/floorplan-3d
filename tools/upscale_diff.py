"""Find objects added/removed by an 'upscale' pass: compare source and result at low resolution (blurred),
report blobs where they differ strongly. Usage: upscale_diff.py <src> <result> <out_vis.png>"""
import sys
import cv2
import numpy as np
from PIL import Image


def diff(src, res, vis=None, W=600):
    a = Image.open(src).convert("RGB"); b = Image.open(res).convert("RGB")
    H = int(W * a.size[1] / a.size[0])
    A = cv2.GaussianBlur(np.asarray(a.resize((W, H), Image.LANCZOS)).astype(np.float32), (0, 0), 3)
    B = cv2.GaussianBlur(np.asarray(b.resize((W, H), Image.LANCZOS)).astype(np.float32), (0, 0), 3)
    d = np.abs(A - B).mean(axis=2)
    m = (d > 28).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    blobs = [tuple(int(v * a.size[0] / W) for v in (s[0], s[1], s[0] + s[2], s[1] + s[3])) for s in st[1:] if s[4] > 40]
    if vis:
        v = np.asarray(b.resize((W, H))).copy()
        for x0, y0, x1, y1 in blobs:
            k = W / a.size[0]
            cv2.rectangle(v, (int(x0 * k), int(y0 * k)), (int(x1 * k), int(y1 * k)), (255, 0, 0), 2)
        Image.fromarray(v).save(vis)
    return blobs


if __name__ == "__main__":
    print(diff(*sys.argv[1:4]))
