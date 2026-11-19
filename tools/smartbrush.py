"""'Smart brush' for AI blur squares on parquet: every blurred patch is re-rendered by Gemini inside a crop of its
own surroundings (so plank joints, grain direction, light and shadows continue naturally), then only the patch area
is pasted back (ECC-aligned, feathered).
usage (python): boxes = find(img, protect); jobs = plan_crops(boxes, shape); run(src_png, jobs, out_png, tag)"""
import json, os, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import deblur

PROMPT = ("This is a top-down photoreal render of an apartment floor (oak parquet planks). Some rectangular areas of the parquet are BLURRED / smeared "
          "(the wood grain and plank joints are missing there). Repaint ONLY those blurred areas: continue the oak planks exactly as they run around them "
          "(same plank width, same direction, joints staggered naturally, same colour and grain), and keep the light, shadows and reflections exactly as they are. "
          "Do NOT change anything else: walls, furniture, door leaves, rugs and everything that is sharp stays exactly identical. Keep framing and scale identical. "
          "Strict top-down orthographic view, no text, no watermark.")


def find(a, protect=None, pct=12, min_area=2500):
    g = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    e = deblur.sharpness(g)
    floor = deblur.parquet_mask(a)
    if protect is not None: floor &= ~protect
    low = ((e < np.percentile(e[floor], pct)) & floor).astype(np.uint8)
    low = cv2.morphologyEx(low, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(low)
    out = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area >= min_area and area >= 0.35 * w * h:
            out.append((x, y, x + w, y + h))
    return out


def plan_crops(boxes, shape, ctx=0.8, maxside=1400):
    """one crop per patch (merged when crops overlap a lot): crop = patch box grown by ctx*size on every side."""
    H, W = shape[:2]; jobs = []
    for (x0, y0, x1, y1) in boxes:
        w, h = x1 - x0, y1 - y0; gx, gy = int(max(w, 120) * ctx), int(max(h, 120) * ctx)
        c = [max(0, x0 - gx), max(0, y0 - gy), min(W, x1 + gx), min(H, y1 + gy)]
        merged = False
        for j in jobs:
            cc = j['crop']
            ix = max(0, min(cc[2], c[2]) - max(cc[0], c[0])); iy = max(0, min(cc[3], c[3]) - max(cc[1], c[1]))
            if ix * iy > 0.3 * (c[2] - c[0]) * (c[3] - c[1]):
                nc = [min(cc[0], c[0]), min(cc[1], c[1]), max(cc[2], c[2]), max(cc[3], c[3])]
                if max(nc[2] - nc[0], nc[3] - nc[1]) <= maxside:
                    j['crop'] = nc; j['boxes'].append((x0, y0, x1, y1)); merged = True; break
        if not merged:
            jobs.append({'crop': c, 'boxes': [(x0, y0, x1, y1)]})
    return jobs


def run(src_png, jobs, out_png, tag, gen=True, grow=14):
    import gem, ai_inpaint
    a = np.asarray(Image.open(src_png).convert('RGB')).astype(np.float32)
    d = os.path.dirname(out_png) + '/'
    for k, j in enumerate(jobs):
        name = f'{tag}{k}'
        (cx0, cy0, cx1, cy1), asp = ai_inpaint.crop_for(j['crop'], a.shape)
        if gen and not os.path.exists(d + f'sb_{name}.json'):
            c = Image.fromarray(np.clip(a[cy0:cy1, cx0:cx1], 0, 255).astype(np.uint8)); sc = max(1.0, 1400 / c.width)
            c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS).save(d + f'sb_{name}_in.png')
            r = gem.generate(PROMPT, [d + f'sb_{name}_in.png'], d + f'sb_{name}_out.png', aspect=asp)
            json.dump({'crop_px': [int(cx0), int(cy0), int(cx1), int(cy1)], 'boxes': [list(map(int, b)) for b in j['boxes']]}, open(d + f'sb_{name}.json', 'w'))
            print(name, r, flush=True)
    for k, j in enumerate(jobs):
        name = f'{tag}{k}'
        if not os.path.exists(d + f'sb_{name}.json'): continue
        meta = json.load(open(d + f'sb_{name}.json'))
        for b in meta['boxes']:
            mb = [b[0] - grow, b[1] - grow, b[2] + grow, b[3] + grow]
            try:
                ai_inpaint.paste(a, meta['crop_px'], mb, d + f'sb_{name}_out.png', feather=grow // 2, min_ncc=0.25,
                                 ignore_box=mb)
            except ValueError as e:
                print(name, 'skip', e, flush=True)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out_png)
    return out_png
