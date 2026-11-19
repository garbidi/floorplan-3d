"""Blender render (exact plan geometry) -> AI Studio photoreal pass in the accepted style. usage: hybrid.py N src.png tag"""
import sys, os; sys.path.insert(0, '/mnt/c/Projects/3d_visual/tools')
from PIL import Image
import studio
P = '/mnt/c/Projects/3d_visual/'
N, SRC, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
R = P + f'renders/33 плана/{N}/code3d/'
im = Image.open(SRC).convert('RGB'); W, H = im.size
PW, PH = W, round(W * 1.5); oy = (PH - H) // 2                     # pad to 2:3
pad = Image.new('RGB', (PW, PH), 'white'); pad.paste(im, (0, oy)); pad.save(R + f'{TAG}_in.png')
TXT = ("IMAGE 1 is a neutral GREY CLAY layout model of an apartment seen strictly from directly above (orthographic top view). It defines ONLY the geometry: "
       "the exact position, size, orientation and count of every wall, opening, door leaf, window and piece of furniture. It has no colours on purpose. "
       "IMAGE 2 is the STYLE REFERENCE. Produce a finished photoreal top-down architectural visualization that looks exactly like IMAGE 2: the same warm "
       "evening light and colour grading, soft shadows and ambient occlusion, the same light warm-beige oak parquet with narrow planks, the same cream and "
       "beige fabrics, light rugs, bedding with natural folds, glowing bedside lamps, realistic green plants, wardrobes with clothes hanging across the rail "
       "seen from above with a warm LED glow, the same kitchen and bathroom materials, solid black walls. Take all colours and materials from IMAGE 2, none from IMAGE 1. "
       + open(P + f'tools/bl/p{N}_objects.txt', encoding='utf-8').read() +
       " STRICT GEOMETRY: every item stays exactly where it is in IMAGE 1 - do not add, remove, move, resize, rotate or reshape anything; wall lines straight "
       "and identical. Appliances strictly from above; washing machine top is a plain flat lid without a round door. No text, no labels, no numbers. "
       "Same framing as IMAGE 1, white background outside the apartment.")
out = R + f'{TAG}_out.png'
print(studio.generate(TXT, [R + f'{TAG}_in.png', P + 'reference_style_notext.png'], out, aspect='2:3', min_size=3000), flush=True)
o = Image.open(out).convert('RGB').resize((PW, PH), Image.LANCZOS).crop((0, oy, W, oy + H)); o.save(R + f'{TAG}_c.png'); print('done', R + f'{TAG}_c.png')
