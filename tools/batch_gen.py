"""Generate N variants for a prepared plan in AI Studio, pick best by wall IoU. Usage: batch_gen.py key [n]"""
import json, subprocess, sys, time, re
sys.path.insert(0, '/mnt/c/Projects/3d_visual/tools')
import studio
from build_prompt import build
P = '/mnt/c/Projects/3d_visual/'
key = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
idx = json.load(open(P + 'plans_prepared/index_new.json'))
build(P + f'plans_prepared/{key}_message.txt', P + f'plans_prepared/{key}_full.txt')
import os; RD = P + 'renders/' + idx[key]['name'] + '/'; os.makedirs(RD, exist_ok=True)
text = open(P + f'plans_prepared/{key}_full.txt', encoding='utf-8').read()
jr = P + f'tools/tmp/judge_reports/{key}.txt'
if os.path.exists(jr):
    text += '\n\nMUST FIX — a previous attempt of this exact plan was rejected by the reviewer for these errors; avoid ALL of them (coordinates in % of the outer contour):\n' + open(jr, encoding='utf-8').read()
plan_img = P + f'plans_prepared/{key}_clean.png' if os.path.exists(P + f'plans_prepared/{key}_clean.png') else P + f'plans_prepared/{key}.png'
best = (-1, None)
t0 = time.time()
for i in range(n):
    out = RD + f'v{i+1}.jpg'
    r = studio.generate(text, [plan_img, P + 'reference_style_notext.png'], out, aspect=idx[key]['aspect'])
    if isinstance(r, dict) and r.get('saved'):
        o = subprocess.run(['python3', P + 'tools/overlay.py', P + f'plans_prepared/{key}.png', out, P + f'tools/tmp/ov_{key}_{i+1}.jpg'], capture_output=True, text=True).stdout
        iou = float(re.search(r'IoU=([\d.]+)', o).group(1)); print(key, i + 1, o.strip(), flush=True)
        if iou > best[0]: best = (iou, out)
print(f'BEST {key} {best} {int(time.time()-t0)}s', flush=True)
