"""Remove area numbers (tan) and the badge from a prepared plan so the model has no text to copy.
Usage: python3 clean_plan.py <key>  -> plans_prepared/<key>_clean.png"""
import re, sys
import numpy as np
from PIL import Image
from scipy import ndimage
P = '/mnt/c/Projects/3d_visual/'
key = sys.argv[1]
im = Image.open(P + f'plans_prepared/{key}.png').convert('RGB')
a = np.asarray(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
tan = (r > 150) & (g > 120) & (b < 215) & (r - b > 22)
# the badge: largest tan blob; clear its bbox plus the white/black text box beside it
lab, n = ndimage.label(ndimage.binary_dilation(tan, iterations=3))
out = a.copy()
out[ndimage.binary_dilation(tan, iterations=2)] = 255
if n:
    sizes = ndimage.sum(tan, lab, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    ys, xs = np.where(lab == big)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    h, w = y1 - y0, x1 - x0
    # the numbers box is attached to one side of the gold square; clear a generous area around it
    Y0, Y1 = max(0, y0 - int(0.15 * h)), min(a.shape[0], y1 + int(1.3 * h))
    X0, X1 = max(0, x0 - int(1.3 * w)), min(a.shape[1], x1 + int(1.3 * w))
    # clear the gold square itself
    out[y0:y1 + 1, x0:x1 + 1] = 255
    # in the surrounding zone remove only small dark components (digits, "№"), keep long lines / furniture
    region = out[Y0:Y1, X0:X1]
    dark = region.max(axis=2) < 200
    cl, cn = ndimage.label(dark)
    for i, sl in enumerate(ndimage.find_objects(cl), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if hh < 0.5 * h and ww < 0.5 * w and (hh < 0.06 * a.shape[0]):
            region[cl == i] = 255
    # the white box with the numbers next to the gold square: thin rectangular outline of about the same height
    dark = region.max(axis=2) < 200
    cl, cn = ndimage.label(dark)
    for i, sl in enumerate(ndimage.find_objects(cl), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        fill = (cl[sl] == i).mean()
        if 0.6 * h < hh < 1.4 * h and ww < 1.5 * w and fill < 0.25:
            region[sl] = 255
    out[Y0:Y1, X0:X1] = region
# faint anti-aliased remains of tan digits
rr, gg, bb = out[..., 0], out[..., 1], out[..., 2]
out[(rr - bb > 10) & (rr > 185)] = 255
Image.fromarray(out.astype(np.uint8)).save(P + f'plans_prepared/{key}_clean.png')
print(key, 'tan', int(tan.sum()), 'badge box', (X0, Y0, X1, Y1) if n else None)
