"""Prepare a plan from plans/33 плана/<N>.png: transparent -> white, scaled to ~2400 px long side, key p<N> in index_new.json
(name '33 плана/<N>' => renders/33 плана/<N>/, final/33 плана/<N>.jpg), then clean_plan. usage: prep33.py N [N...]"""
import json, sys, subprocess
import numpy as np
from PIL import Image
P = '/mnt/c/Projects/3d_visual/'
RAT = {"1:1": 1, "3:4": .75, "4:3": 4 / 3, "4:5": .8, "5:4": 1.25, "2:3": 2 / 3, "3:2": 1.5, "9:16": 9 / 16, "16:9": 16 / 9}
idx = json.load(open(P + 'plans_prepared/index_new.json'))
for n in sys.argv[1:]:
    im = Image.open(P + f'plans/33 плана/{n}.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
    s = 2400 / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    key = f'p{n}'; im.save(P + f'plans_prepared/{key}.png')
    a = np.asarray(im).astype(int); wm = (a.max(2) < 90)
    ys, xs = np.nonzero(wm); W, H = im.size
    asp = min(RAT, key=lambda r: abs(RAT[r] - W / H))
    idx[key] = {'src': f'33 плана/{n}.png', 'aspect': asp,
                'canvas_pct': [round(100 * xs.min() / W, 1), round(100 * xs.max() / W, 1), round(100 * ys.min() / H, 1), round(100 * ys.max() / H, 1)],
                'contour_aspect': round((xs.max() - xs.min()) / (ys.max() - ys.min()), 3), 'name': f'33 плана/{n}'}
    subprocess.run(['python3', P + 'tools/clean_plan.py', key], check=True)
    print(key, im.size, idx[key])
json.dump(idx, open(P + 'plans_prepared/index_new.json', 'w'), ensure_ascii=False, indent=1)
