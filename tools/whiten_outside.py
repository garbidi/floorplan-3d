"""Make everything outside the apartment pure white (removes Gemini sparkle / grey ghosts on the background),
keeping dark things outside such as entrance door leaves. Uses the 3D scene interior mask (plan px)."""
import json, sys
import cv2
import numpy as np
from PIL import Image
P = "/mnt/c/Projects/3d_visual/"


def whiten(key, path, out=None):
    name = json.load(open(P + "plans_prepared/index_new.json"))[key]["name"]
    m = np.asarray(Image.open(P + f"renders/{name}/code3d/scene_mask.png").convert("L")) > 0
    im = np.asarray(Image.open(path).convert("RGB")).copy()
    m = cv2.resize(m.astype(np.uint8), (im.shape[1], im.shape[0]), interpolation=cv2.INTER_NEAREST)
    k = max(3, im.shape[1] // 250)
    inside = cv2.dilate(m, np.ones((k, k), np.uint8)) > 0
    # the scene mask can miss parts of the real render (132: hall corner got bleached) -> keep everything not reachable from the image border
    # through near-white background pixels
    from scipy import ndimage as nd
    # through background pixels: near-white, or the light neutral grey of a vignetted backdrop (163)
    lo, hi = im.min(axis=2).astype(int), im.max(axis=2).astype(int)
    lab, _ = nd.label((lo >= 238) | ((hi - lo < 14) & (lo > 150)))
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    inside |= ~np.isin(lab, list(border))
    light = im.min(axis=2) > 150
    im[(~inside) & light] = 255
    Image.fromarray(im).save(out or path, quality=97)


if __name__ == "__main__":
    whiten(sys.argv[1], sys.argv[2])
