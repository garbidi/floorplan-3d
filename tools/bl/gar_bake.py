"""Bake hanging garments with real cloth simulation: sewn front/back panels from a flat pattern draped on a hanger collider.
Output: assets/garments.blend with objects G_<kind> (origin = hanger hook point, garment plane = YZ, front = -X).
run: blender -b --factory-startup --python gar_bake.py [-- kinds...]"""
import bpy, bmesh, math, sys
from mathutils import Vector

OUT = 'C:/Projects/3d_visual/assets/garments.blend'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# pattern outlines in (y, z): z=0 shoulder line top, negative downwards. Half outline for y>=0, mirrored.
PATTERNS = {
    #        body half-width, length, sleeve length, sleeve width at shoulder/cuff, sleeve angle from horizontal(deg, down), neck r (front), neck r (back)
    'shirt':  dict(bw=0.25, L=0.78, sl=0.60, sw0=0.21, sw1=0.12, ang=80, nf=0.04, nb=0.02, nw=0.042, shoulder=0.045, res=0.016),
    'tee':    dict(bw=0.25, L=0.68, sl=0.20, sw0=0.20, sw1=0.17, ang=45, nf=0.05, nb=0.022, nw=0.048, shoulder=0.04, res=0.016),
    'knit':   dict(bw=0.26, L=0.64, sl=0.58, sw0=0.23, sw1=0.11, ang=80, nf=0.05, nb=0.025, nw=0.05, shoulder=0.035, res=0.018),
    'jacket': dict(bw=0.26, L=0.76, sl=0.62, sw0=0.23, sw1=0.15, ang=82, nf=0.13, nb=0.04, nw=0.075, shoulder=0.03, res=0.018),
    'dress':  dict(bw=0.22, L=1.00, sl=0.0, sw0=0.0, sw1=0.0, ang=0, nf=0.12, nb=0.06, nw=0.09, shoulder=0.06, res=0.018, flare=0.08),
}


def outline(p):
    """closed polygon (y,z) of the flat garment piece"""
    bw, L, sl, sw0, sw1, a = p['bw'], p['L'], p['sl'], p['sw0'], p['sw1'], math.radians(p['ang'])
    fl = p.get('flare', 0.02); sh = p['shoulder']
    right = []
    right.append((0.04, 0.012))                                # neck edge (neck cut handled separately)
    if sl > 0:
        sx, sz = bw, -sh                                       # shoulder point
        dx, dz = math.cos(a), -math.sin(a)                     # sleeve direction
        nx, nz = math.sin(a), math.cos(a)                      # normal (towards up/out)
        right += [(sx, sz)]
        tip_top = (sx + dx * sl + nx * 0.0, sz + dz * sl)
        right += [(sx + dx * sl, sz + dz * sl)]
        right += [(sx + dx * sl - nx * sw1, sz + dz * sl - nz * sw1)]
        right += [(bw, sz - sw0)]                              # armpit
    else:
        right += [(bw, -sh), (bw, -0.20)]
    right += [(bw + fl, -L)]
    left = [(-y, z) for (y, z) in reversed(right)]
    return [(0.0, -L)] and right + [(0.0, -L)] + left


def inside(poly, y, z):
    c = False; n = len(poly)
    for i in range(n):
        y1, z1 = poly[i]; y2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and y < (y2 - y1) * (z - z1) / (z2 - z1 + 1e-12) + y1: c = not c
    return c


def build_garment(kind):
    p = PATTERNS[kind]; poly = outline(p); r = p['res']
    ys = [i * r for i in range(int(-1.0 / r), int(1.0 / r) + 1)]
    zs = [-i * r for i in range(0, int((p['L'] + 0.6) / r) + 1)]
    bm = bmesh.new(); grid = {}
    def keep(y, z):
        if not inside(poly, y, z): return False
        neck = (y / 0.10) ** 2 + (z / p['nf']) ** 2 < 1.0       # front neck scoop (applied to both, back gets a shallower one below)
        return not neck
    panels = {}
    for side, x in (('f', -0.004), ('b', 0.004)):
        vmap = {}
        for i, y in enumerate(ys):
            for j, z in enumerate(zs):
                yy = y; zz = z
                ok = inside(poly, yy, zz) and not ((yy / p.get('nw', 0.068)) ** 2 + (zz / (p['nf'] if side == 'f' else p['nb'])) ** 2 < 1.0)
                if ok: vmap[(i, j)] = bm.verts.new((x, yy, zz))
        for (i, j), v in vmap.items():
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if all(k in vmap for k in q): bm.faces.new([vmap[k] for k in q])
        panels[side] = vmap
    bm.verts.ensure_lookup_table()
    # snap staircase boundary verts onto the true outline (smooth seams/edges)
    segs = [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
    def nearest(y, z):
        best = None
        for (y1, z1), (y2, z2) in segs:
            dy, dz = y2 - y1, z2 - z1; L2 = dy * dy + dz * dz or 1e-9
            t = max(0, min(1, ((y - y1) * dy + (z - z1) * dz) / L2)); py, pz = y1 + t * dy, z1 + t * dz
            d = (py - y) ** 2 + (pz - z) ** 2
            if best is None or d < best[0]: best = (d, py, pz)
        return best
    for v in bm.verts:
        if not v.is_boundary: continue
        d, py, pz = nearest(v.co.y, v.co.z)
        if d < (2.2 * r) ** 2: v.co.y, v.co.z = py, pz
    # weld seams: boundary verts of front & back at the same (i,j) except neck, hem, sleeve cuffs
    hemz = -p['L'] + r * 1.5
    weld = {}
    for k, vf in panels['f'].items():
        vb = panels['b'].get(k)
        if vb is None: continue
        if not (vf.is_boundary and vb.is_boundary): continue
        y, z = vf.co.y, vf.co.z
        if z < hemz: continue                                                   # hem stays open
        if abs(y) < p.get('nw', 0.068) + 0.02 and z > -(p['nf'] + 0.02): continue    # neck stays open
        if p['sl'] > 0:
            a = math.radians(p['ang']); sx, sz = p['bw'], -p['shoulder']
            t = (abs(y) - sx) * math.cos(a) - (z - sz) * math.sin(a)          # distance along the sleeve axis
            if t > p['sl'] - r * 1.5: continue                                  # cuff stays open
        weld[vb] = vf; vf.co.x = 0.0
    bmesh.ops.weld_verts(bm, targetmap=weld)
    hcol = {'shirt': 0.035, 'tee': 0.014, 'knit': 0.022, 'jacket': 0.0, 'dress': 0.0}[kind]
    if hcol:
        neck = [e for e in bm.edges if e.is_boundary and all(abs(v.co.y) < p.get('nw', 0.068) + 0.025 and v.co.z > -(p['nf'] + 0.03) for v in e.verts)]
        ret = bmesh.ops.extrude_edge_only(bm, edges=neck)
        nv = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
        for v in nv:
            v.co.z += hcol; v.co.y *= 1.03; v.co.x *= (1.2 if kind == 'shirt' else 1.0)
    me = bpy.data.meshes.new(kind); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('G_' + kind, me); sc.collection.objects.link(o)
    return o


def hanger_collider(width=0.42):
    cu = bpy.data.curves.new('hc', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.012; cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for pt, (y, z) in zip(sp.bezier_points, ((-width / 2, -0.06), (0, -0.015), (width / 2, -0.06))):
        pt.co = (0, y, z); pt.handle_left_type = pt.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('hanger_col', cu); sc.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target='MESH'); o.select_set(False)
    o.modifiers.new('col', 'COLLISION'); o.collision.thickness_outer = 0.004; o.collision.cloth_friction = 20
    return o


def simulate(o, frames, mass=0.25, stiff=15, bend=0.05, pin_top=True, shrink=0.0):
    c = o.modifiers.new('Cloth', 'CLOTH'); st = c.settings
    st.quality = 7; st.mass = mass; st.tension_stiffness = stiff; st.compression_stiffness = stiff; st.shear_stiffness = stiff * 0.5
    st.bending_stiffness = bend; st.air_damping = 4.0; st.shrink_min = shrink
    cs = c.collision_settings; cs.distance_min = 0.003; cs.use_self_collision = True; cs.self_distance_min = 0.0025; cs.collision_quality = 4
    if pin_top:
        vg = o.vertex_groups.new(name='pin')
        ids = [v.index for v in o.data.vertices if v.co.z > -0.035 and 0.07 < abs(v.co.y) < 0.20]
        vg.add(ids, 1.0, 'REPLACE'); st.vertex_group_mass = 'pin'; st.pin_stiffness = 0.6
    c.point_cache.frame_start = 1; c.point_cache.frame_end = frames
    sc.frame_start = 1; sc.frame_end = frames
    for f in range(1, frames + 1): sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev); o.modifiers.clear(); old = o.data; o.data = me; bpy.data.meshes.remove(old)
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
    sc.frame_set(1)
    sm = o.modifiers.new('sm', 'CORRECTIVE_SMOOTH'); sm.factor = 0.6; sm.iterations = 6; sm.smooth_type = 'LENGTH_WEIGHTED'; sm.use_only_smooth = True
    dg = bpy.context.evaluated_depsgraph_get(); me2 = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); old = o.data; o.data = me2; bpy.data.meshes.remove(old)


def folded(rr):
    """folded knit/tee: cloth sheet relaxed over a thin core slab -> soft rounded fold edges and wrinkles on top. footprint 0.30 x 0.26, height ~0.045"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.018)); core = bpy.context.active_object
    core.scale = (0.28, 0.24, 0.03); bpy.ops.object.transform_apply(scale=True)
    bv = core.modifiers.new('bv', 'BEVEL'); bv.width = 0.012; bv.segments = 4
    core.modifiers.new('col', 'COLLISION'); core.collision.thickness_outer = 0.002; core.collision.cloth_friction = 30
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=52, size=1, location=(0, 0, 0.045)); o = bpy.context.active_object; o.name = 'G_folded'
    o.scale = (0.33, 0.29, 1); bpy.ops.object.transform_apply(scale=True)
    ph = rr.uniform(0, 6.28)
    for v in o.data.vertices: v.co.z += 0.004 * math.sin(v.co.x * 30 + ph) * math.cos(v.co.y * 22 + ph)
    c = o.modifiers.new('Cloth', 'CLOTH'); st = c.settings; st.quality = 6; st.mass = 0.2; st.tension_stiffness = 10; st.bending_stiffness = 0.5; st.shrink_min = 0.03
    c.collision_settings.distance_min = 0.002; c.point_cache.frame_end = 40; sc.frame_end = 40
    for f in range(1, 41): sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = me
    for v in o.data.vertices: v.co.z = max(v.co.z, 0.0)
    bpy.data.objects.remove(core); sc.frame_set(1)
    return o


def trousers():
    """trousers folded over the hanger bar: sheet pre-bent over a horizontal bar into two hanging halves, then relaxed"""
    bm = bmesh.new(); W = 0.34; L = 0.50; r = 0.017; nW = 20; nL = 32; nA = 8
    rows = []
    for k in range(-nL, nL + nA + 1):
        if k < 0: x, z = -0.016, -0.08 + (k / nL) * L                     # front half going down
        elif k > nA: x, z = 0.016, -0.08 - ((k - nA) / nL) * L               # back half going down
        else:
            a = math.pi * k / nA; x, z = -0.016 * math.cos(a), -0.08 + 0.016 * math.sin(a)
        rows.append([bm.verts.new((x, -W / 2 + W * i / nW, z)) for i in range(nW + 1)])
    for a_, b_ in zip(rows[:-1], rows[1:]):
        for i in range(nW): bm.faces.new((a_[i], a_[i + 1], b_[i + 1], b_[i]))
    me = bpy.data.meshes.new('trousers'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('G_trousers', me); sc.collection.objects.link(o)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=0.44, location=(0, 0, -0.08), rotation=(math.radians(90), 0, 0))
    bar = bpy.context.active_object; bar.modifiers.new('col', 'COLLISION'); bar.collision.cloth_friction = 40; bar.collision.thickness_outer = 0.004
    c = o.modifiers.new('Cloth', 'CLOTH'); st = c.settings; st.quality = 7; st.mass = 0.4; st.tension_stiffness = 25; st.bending_stiffness = 0.3
    c.collision_settings.use_self_collision = True; c.collision_settings.self_distance_min = 0.003; c.collision_settings.distance_min = 0.003
    c.point_cache.frame_end = 40; sc.frame_end = 40
    for f in range(1, 41): sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = me
    bpy.data.objects.remove(bar); sc.frame_set(1)
    return o


import random
kinds = argv or ['shirt', 'tee', 'knit', 'jacket', 'dress', 'trousers', 'folded']
NV = 2
hc = hanger_collider()
done = []
for k, vi in [(k, vi) for k in kinds for vi in range(NV)]:
    rr = random.Random(hash((k, vi)) & 0xffff)
    if k == 'folded':
        o = folded(rr)
    elif k == 'trousers':
        o = trousers()
    else:
        o = build_garment(k)
        ph = rr.uniform(0, 6.28); sy = 1 + rr.uniform(-0.04, 0.04) * (vi > 0)
        for v in o.data.vertices: v.co.x += 0.002 * math.sin(v.co.z * 9 + v.co.y * 5 + ph); v.co.y *= sy
        simulate(o, 150, mass={'jacket': 0.5, 'knit': 0.35}.get(k, 0.25), stiff={'jacket': 40, 'knit': 8}.get(k, 15),
                 bend={'jacket': 2.0, 'knit': 0.02}.get(k, 0.06))
    # soft-clamp the footprint seen from above: thickness (X) and width (Y) - hanging clothes in a wardrobe are compact
    if k == 'folded':
        o.location.x = 0; o.name = f'G_{k}_{vi}'; o.data.name = o.name; done.append(o.name); print('BAKED', o.name, flush=True); continue
    p_ = PATTERNS.get(k, dict(bw=0.2)); hw = p_['bw'] + 0.04; tx = {'jacket': 0.06, 'knit': 0.055}.get(k, 0.045)
    for v in o.data.vertices:
        v.co.x = tx * math.tanh(v.co.x / tx)
        if abs(v.co.y) > hw * 0.8: v.co.y = math.copysign(hw * 0.8 + 0.2 * hw * math.tanh((abs(v.co.y) - hw * 0.8) / (0.2 * hw)), v.co.y)
    o.location.x = 0; o.name = f'G_{k}_{vi}'; o.data.name = o.name
    done.append(o.name); print('BAKED', o.name, len(o.data.vertices), flush=True)
bpy.data.objects.remove(hc)
for o in bpy.data.objects:
    if not o.name.startswith('G_'): bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT, done)
