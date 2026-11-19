"""Room-by-room photoreal pass over the Blender clay render of a plan, then exact Blender walls on top.
usage: rooms.py N gen [names] | compose     (render px mapping of the 33-batch: rx = 119 + (px-190)*0.6442, ry = 196 + (py-305)*0.6356)"""
import sys, os, json; sys.path.insert(0, '/mnt/c/Projects/3d_visual/tools')
import numpy as np
from PIL import Image
P = '/mnt/c/Projects/3d_visual/'
N, MODE = sys.argv[1], sys.argv[2]
R = P + f'renders/33 плана/{N}/code3d/'
CLAY = P + f'tools/tmp/bl{N}_clay.png'
COL = P + f'tools/tmp/bl{N}_w.png'
def rx(px): return round(119 + (px - 190) * 0.6442)
def ry(py): return round(196 + (py - 305) * 0.6356)
# room: (plan box incl. its walls, objects text)
ROOMS = json.load(open(P + f'tools/bl/p{N}_rooms.json', encoding='utf-8'))
RAT = {"1:1": 1, "3:4": .75, "4:3": 4 / 3, "4:5": .8, "5:4": 1.25, "2:3": 2 / 3, "3:2": 1.5, "9:16": 9 / 16, "16:9": 16 / 9}
HEAD = ("This is a RE-TEXTURING and RE-LIGHTING task, NOT a redesign. IMAGE 1 is a grey clay 3D model of ONE room of an apartment, seen strictly from directly "
        "above (orthographic). IMAGE 2 is the style reference. Output IMAGE 1 with EXACTLY the same framing and EXACTLY the same layout - every wall, door, window "
        "and object at exactly the same pixel position, size, shape, orientation and count as in IMAGE 1 - only give everything photoreal materials, colours and "
        "lighting in exactly the style of IMAGE 2 (warm evening light, soft shadows and ambient occlusion, light warm-beige oak parquet with narrow planks, cream and "
        "beige fabrics with natural folds, light rugs, walnut and oak wood, glowing lamps, realistic plants, solid black walls). Do NOT move, add, remove, resize, "
        "reshape or rotate anything. Appliances strictly from above; a washing machine top is a plain flat lid without a round door. No text. Room contents: ")


def crop_box(r):
    x0, y0, x1, y1 = r['box']
    return rx(x0), ry(y0), rx(x1), ry(y1)


if MODE == 'gen':
    import studio
    clay = Image.open(CLAY).convert('RGB')
    for name, r in ROOMS.items():
        if sys.argv[3:] and name not in sys.argv[3:]: continue
        x0, y0, x1, y1 = crop_box(r); c = clay.crop((x0, y0, x1, y1)); W, H = c.size
        asp = min(RAT, key=lambda k: abs(RAT[k] - W / H)); ar = RAT[asp]
        PW, PH = (round(H * ar), H) if W / H < ar else (W, round(W / ar))
        pad = Image.new('RGB', (PW, PH), 'white'); ox, oy = (PW - W) // 2, (PH - H) // 2; pad.paste(c, (ox, oy))
        sc = 1600 / max(PW, PH); pad = pad.resize((round(PW * sc), round(PH * sc)), Image.LANCZOS); pad.save(R + f'room_{name}_in.png')
        json.dump({'crop': [x0, y0, x1, y1], 'pad': [PW, PH, ox, oy]}, open(R + f'room_{name}.json', 'w'))
        out = R + f'room_{name}_out.png'
        print(name, asp, studio.generate(HEAD + r['objects'], [R + f'room_{name}_in.png', P + 'reference_style_notext.png'], out, aspect=asp, min_size=1500), flush=True)
else:
    base = np.asarray(Image.open(COL).convert('RGB')).astype(np.float32)
    acc = base.copy()
    for name, r in ROOMS.items():
        if not os.path.exists(R + f'room_{name}_out.png'): continue
        j = json.load(open(R + f'room_{name}.json')); x0, y0, x1, y1 = j['crop']; PW, PH, ox, oy = j['pad']
        o = Image.open(R + f'room_{name}_out.png').convert('RGB').resize((PW, PH), Image.LANCZOS).crop((ox, oy, ox + x1 - x0, oy + y1 - y0))
        acc[y0:y1, x0:x1] = np.asarray(o, np.float32)
    # exact walls + outside from the Blender render (black walls, white outside)
    b = base.astype(np.int32)
    wall = b.max(2) < 22
    out_white = b.min(2) > 250
    acc[wall] = (3, 1, 2); acc[out_white] = 255
    Image.fromarray(acc.clip(0, 255).astype(np.uint8)).save(R + 'rooms_compose.png'); print('composed', R + 'rooms_compose.png')
