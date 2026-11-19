"""Whole-apartment photoreal pass over the Blender clay render, several tries, each scored against the plan geometry (Blender walls), best kept.
usage: whole.py N tries tag   (STUDIO_RES=2K)"""
import sys, os, json, shutil; sys.path.insert(0, '/mnt/c/Projects/3d_visual/tools')
import numpy as np
from PIL import Image
from scipy import ndimage as nd
import studio
P = '/mnt/c/Projects/3d_visual/'
N, TRIES, TAG = sys.argv[1], int(sys.argv[2]), sys.argv[3]
R = P + f'renders/33 плана/{N}/code3d/'
clay = Image.open(P + f'tools/tmp/bl{N}_clay.png').convert('RGB'); W, H = clay.size
PW, PH = W, round(W * 1.5); oy = (PH - H) // 2
pad = Image.new('RGB', (PW, PH), 'white'); pad.paste(clay, (0, oy)); pad.save(R + f'{TAG}_in.png')
TXT = ("This is a RE-TEXTURING and RE-LIGHTING task, NOT a redesign. IMAGE 1 is a grey clay 3D model of a whole apartment seen strictly from directly above "
       "(orthographic). IMAGE 2 is the style reference. Output IMAGE 1 with EXACTLY the same framing, the same apartment outline and EXACTLY the same layout - "
       "every wall, opening, door leaf, window and object at exactly the same pixel position, size, shape, orientation and count as in IMAGE 1 - and only give "
       "everything photoreal materials, colours and lighting in exactly the style of IMAGE 2 (warm evening light, soft shadows and ambient occlusion, light "
       "warm-beige oak parquet with narrow planks, cream and beige fabrics with natural folds, light rugs, walnut and oak wood, glowing bedside lamps, realistic "
       "plants, solid black walls, white background outside). Take all colours from IMAGE 2, none from IMAGE 1. Do NOT move, add, remove, resize, reshape or rotate "
       "anything; do not change any wall. Appliances strictly from above; washing machine top is a plain flat lid without a round door; clothes in open wardrobes "
       "hang across the rail and are seen from above. No text, no labels, no numbers. Contents: " + open(P + f'tools/bl/p{N}_objects.txt', encoding='utf-8').read())
ref = np.asarray(Image.open(P + f'tools/tmp/bl{N}_w.png').convert('RGB')).astype(int)
wall_ref = ref.max(2) < 22
def score(img):
    a = np.asarray(img).astype(int); w = a.max(2) < 40
    near = nd.binary_dilation(wall_ref, np.ones((7, 7)))
    near_o = nd.binary_dilation(w, np.ones((7, 7)))
    prec = (w & near).sum() / max(1, w.sum()); rec = (wall_ref & near_o).sum() / max(1, wall_ref.sum())
    return 2 * prec * rec / max(1e-6, prec + rec)
best = json.load(open(R + f'{TAG}_best.json')) if os.path.exists(R + f'{TAG}_best.json') else {'score': -1}
for k in range(TRIES):
    o = R + f'{TAG}_t{k}.png'
    if not os.path.exists(o):
        print(k, studio.generate(TXT, [R + f'{TAG}_in.png', P + 'reference_style_notext.png'], o, aspect='2:3', min_size=1500), flush=True)
    if not os.path.exists(o): continue
    c = Image.open(o).convert('RGB').resize((PW, PH), Image.LANCZOS).crop((0, oy, W, oy + H)); c.save(o.replace('.png', '_c.png'))
    s = score(c); print('try', k, 'wall F1', round(s, 3), flush=True)
    if s > best['score']: best = {'score': s, 'file': o.replace('.png', '_c.png')}
json.dump(best, open(R + f'{TAG}_best.json', 'w')); print('best', best)
