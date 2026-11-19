"""Run Gemini object-removal jobs on crops of a render. Usage: inpaint_jobs.py <render.png> <planW> <jobs.json> [names]
jobs.json: {name: {"crop": [x0,y0,x1,y1] plan px, "prompt": "..."}} -> <render dir>/inp_<name>_in.png/_out.png"""
import json, os, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import ai_inpaint, gem

src, planw, jobs = os.path.abspath(sys.argv[1]), int(sys.argv[2]), json.load(open(sys.argv[3]))
names = sys.argv[4:] or list(jobs)
a = np.asarray(Image.open(src).convert("RGB"))
K = a.shape[1] / planw
d = os.path.dirname(src) + "/"
for n in names:
    j = jobs[n]
    (cx0, cy0, cx1, cy1), asp = ai_inpaint.crop_for([int(v * K) for v in j["crop"]], a.shape)
    crop = a[cy0:cy1, cx0:cx1]
    sc = max(1.0, 1400 / crop.shape[1])
    Image.fromarray(cv2.resize(crop, None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)).save(d + f"inp_{n}_in.png")
    r = gem.generate(j["prompt"] + " Change NOTHING else; keep framing and scale identical. Strict top-down view.", [d + f"inp_{n}_in.png"], d + f"inp_{n}_out.png", aspect=asp)
    json.dump({"crop_px": [cx0, cy0, cx1, cy1]}, open(d + f"inp_{n}.json", "w"))
    print(n, asp, r, flush=True)
