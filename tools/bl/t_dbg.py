import bpy, sys, bmesh, math
sys.argv = ['x']
src = open('C:/Projects/3d_visual/tools/bl/gar_bake.py').read().split("kinds = argv")[0]
exec(src)
o = build_garment('shirt')
bm = bmesh.new(); bm.from_mesh(o.data)
bnd = [e for e in bm.edges if e.is_boundary]
import collections
pts = sorted(set((round(v.co.y, 2), round(v.co.z, 2)) for e in bnd for v in e.verts))
print('DBG nbound edges', len(bnd))
# group boundary loops
loops = []
seen = set()
for e in bnd:
    if e in seen: continue
    loop = [e]; seen.add(e); stack = [e]
    while stack:
        cur = stack.pop()
        for v in cur.verts:
            for e2 in v.link_edges:
                if e2.is_boundary and e2 not in seen: seen.add(e2); loop.append(e2); stack.append(e2)
    ys = [v.co.y for ee in loop for v in ee.verts]; zs = [v.co.z for ee in loop for v in ee.verts]
    loops.append((len(loop), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)))
print('DBG loops', loops)
