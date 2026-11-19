"""Wall IoU between a photoreal result and its 3D base (same framing): black-wall masks compared pixel by pixel."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage


def walls(p, size):
    a = np.asarray(Image.open(p).convert("RGB").resize(size, Image.LANCZOS)).astype(int)
    m = a.max(axis=2) < 50
    return ndimage.binary_opening(m, np.ones((5, 5)))


def iou(base, photo, W=1200):
    b = Image.open(base); size = (W, int(W * b.size[1] / b.size[0]))
    m1, m2 = walls(base, size), walls(photo, size)
    return (m1 & m2).sum() / max(1, (m1 | m2).sum())


if __name__ == "__main__":
    print(round(iou(sys.argv[1], sys.argv[2]), 3))
