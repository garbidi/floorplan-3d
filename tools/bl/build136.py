"""Blender scene of plan 136 built strictly from the plan (plan px -> metres, 370 px = 1 m), top-down orthographic render.
run: blender -b --factory-startup --python build136.py -- out.png [samples]"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, Matrix

ROOT = 'C:/Projects/3d_visual/'
A = ROOT + 'assets/ph/'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else ROOT + 'tools/tmp/bl136.png'
SAMPLES = int(argv[1]) if len(argv) > 1 else 128
S = 1 / 370.0
OX, OY = 190, 305
H_WALL = 2.7
random.seed(7)


def X(px): return (px - OX) * S
def Y(py): return -(py - OY) * S


# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'; prefs.get_devices()
for d in prefs.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.use_auto_tile = False
sc.cycles.denoiser = 'OPTIX'
sc.cycles.denoising_use_gpu = True
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = 0.35


# ---------------------------------------------------------------- materials
def tex_mat(name, folder, scale=1.0, rough_mult=1.0, tint=None, rot=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; l = nt.links
    bsdf = n['Principled BSDF']
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale); mp.inputs['Rotation'].default_value[2] = rot
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    files = os.listdir(A + folder)
    def img(key, non_color):
        f = [x for x in files if key in x]
        if not f: return None
        t = n.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(A + folder + '/' + f[0])
        if non_color: t.image.colorspace_settings.name = 'Non-Color'
        t.projection = 'BOX'; t.projection_blend = 0.2
        l.new(mp.outputs['Vector'], t.inputs['Vector']); return t
    d = img('_diff_', False)
    if d:
        if tint:
            mix = n.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0
            l.new(d.outputs['Color'], mix.inputs[6]); mix.inputs[7].default_value = (*tint, 1)
            l.new(mix.outputs[2], bsdf.inputs['Base Color'])
        else:
            l.new(d.outputs['Color'], bsdf.inputs['Base Color'])
    r = img('_rough_', True)
    if r:
        mt = n.new('ShaderNodeMath'); mt.operation = 'MULTIPLY'; mt.inputs[1].default_value = rough_mult
        l.new(r.outputs['Color'], mt.inputs[0]); l.new(mt.outputs[0], bsdf.inputs['Roughness'])
    nm = img('_nor_gl_', True)
    if nm:
        nn = n.new('ShaderNodeNormalMap'); nn.inputs['Strength'].default_value = 0.6
        l.new(nm.outputs['Color'], nn.inputs['Color']); l.new(nn.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def col_mat(name, rgb, rough=0.5, metal=0.0, trans=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if rgb == (0.0, 0.0, 0.0): b.inputs['Specular IOR Level'].default_value = 0.0
    if trans: b.inputs['Transmission Weight'].default_value = trans
    if emit:
        b.inputs['Emission Color'].default_value = (*rgb, 1); b.inputs['Emission Strength'].default_value = emit
    return m


M = {
    'wall': col_mat('wall', (0.0, 0.0, 0.0), 1.0),
    'floor': tex_mat('floor', 'laminate_floor_02', 0.8, 1.0, (1.0, 0.88, 0.80), rot=math.pi / 2),
    'tile': tex_mat('tile', 'interior_tiles', 0.45, 1.0, (1.0, 0.97, 0.94), rot=math.pi / 4),
    'oak': tex_mat('oak', 'oak_veneer_01', 1.4, 1.0, (1.0, 0.82, 0.62)),
    'oak_dark': tex_mat('oak_dark', 'oak_veneer_01', 1.4, 1.0, (0.62, 0.45, 0.34)),
    'stone': tex_mat('stone', 'marble_01', 0.8, 0.6, (0.93, 0.90, 0.86)),
    'linen': col_mat('linen', (0.90, 0.87, 0.82), 0.85),
    'linen_beige': col_mat('linen_beige', (0.50, 0.40, 0.32), 0.9),
    'boucle': col_mat('boucle', (0.86, 0.82, 0.75), 0.95),
    'white': col_mat('white', (0.86, 0.86, 0.85), 0.25),
    'ceramic': col_mat('ceramic', (0.90, 0.90, 0.89), 0.08),
    'steel': col_mat('steel', (0.30, 0.30, 0.31), 0.35, 0.7),
    'black_glass': col_mat('black_glass', (0.006, 0.006, 0.007), 0.12),
    'frame': col_mat('frame', (0.24, 0.24, 0.25), 0.35, 0.6),
    'glass': col_mat('glass', (0.9, 0.95, 1.0), 0.0, 0, 1.0),
    'chrome': col_mat('chrome', (0.8, 0.8, 0.8), 0.12, 1.0),
    'sill': col_mat('sill', (0.92, 0.92, 0.9), 0.3),
    'curtain': col_mat('curtain', (0.93, 0.91, 0.87), 0.8),
    'rug': tex_mat('rug', 'rough_linen', 6.0, 1.0, (0.72, 0.68, 0.64)),
}


# ---------------------------------------------------------------- primitives
def box(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.0):
    """axis-aligned box from plan px rect and heights in metres"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    cx, cy = (X(x0) + X(x1)) / 2, (Y(y0) + Y(y1)) / 2
    o.location = (cx, cy, (z0 + z1) / 2); o.scale = (abs(X(x1) - X(x0)), abs(Y(y1) - Y(y0)), z1 - z0)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(mat)
    return o


def rbox(name, cx, cy, w, d, z0, z1, ang, mat, bevel=0.0):
    """rotated box: centre in plan px, size in metres, angle deg (ccw in plan view)"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = (w, d, z1 - z0); bpy.ops.object.transform_apply(scale=True)
    o.location = (X(cx), Y(cy), (z0 + z1) / 2); o.rotation_euler[2] = math.radians(ang)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = 3
    o.data.materials.append(mat)
    return o


def cyl(name, cx, cy, r, z0, z1, mat, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, vertices=verts, location=(X(cx), Y(cy), (z0 + z1) / 2))
    o = bpy.context.active_object; o.name = name; o.data.materials.append(mat); return o


def soft(o, w=0.03, seg=4):
    b = o.modifiers.new('bv', 'BEVEL'); b.width = w; b.segments = seg
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 2; s.render_levels = 2
    return o


def wrinkle(o, strength=0.012, size=0.08, lv=3):
    t = bpy.data.textures.new('wr', 'CLOUDS'); t.noise_scale = size
    if lv:
        sub = o.modifiers.new('ss0', 'SUBSURF'); sub.levels = lv; sub.render_levels = lv; sub.subdivision_type = 'SIMPLE'
    d = o.modifiers.new('disp', 'DISPLACE'); d.texture = t; d.strength = strength; d.mid_level = 0.5
    return o


def cloth_drape(name, x0, y0, x1, y1, z, mat, frames=45, n=64, thick=0.012, mass=0.25, stiff=12):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=n, y_subdivisions=n, size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = (abs(X(x1) - X(x0)), abs(Y(y1) - Y(y0)), 1); bpy.ops.object.transform_apply(scale=True)
    o.location = ((X(x0) + X(x1)) / 2, (Y(y0) + Y(y1)) / 2, z)
    c = o.modifiers.new('Cloth', 'CLOTH'); st = c.settings
    st.quality = 6; st.mass = mass; st.tension_stiffness = stiff; st.compression_stiffness = stiff; st.bending_stiffness = 0.6
    c.collision_settings.distance_min = 0.004; c.collision_settings.use_self_collision = True; c.collision_settings.self_distance_min = 0.004
    c.point_cache.frame_end = frames
    sc.frame_start = 1; sc.frame_end = frames
    for f in range(1, frames + 1): sc.frame_set(f)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Cloth')
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = thick
    ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = 1; ss.render_levels = 2
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat); sc.frame_set(1)
    return o


def collider(o, d=0.004):
    m = o.modifiers.new('col', 'COLLISION'); o.collision.thickness_outer = d; return o


def cut(o, cutter):
    m = o.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutter; m.solver = 'EXACT'
    cutter.hide_render = True; cutter.display_type = 'WIRE'
    return o


def load_asset(aid):
    path = A + aid + '/' + aid + '_1k.blend'
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = src.objects
    objs = [o for o in dst.objects if o is not None]
    for o in objs: bpy.context.scene.collection.objects.link(o)
    return objs


def place_asset(aid, x0, y0, x1, y1, ang=0.0, keep_aspect=True, z=0.0):
    """fit asset footprint (after rotation ang deg about z) into plan rect"""
    objs = load_asset(aid)
    meshes = [o for o in objs if o.type == 'MESH']
    root = bpy.data.objects.new(aid + '_root', None); bpy.context.scene.collection.objects.link(root)
    for o in objs:
        if o.parent is None: o.parent = root
    bpy.context.view_layer.update()
    root.rotation_euler[2] = math.radians(ang); bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    mnx = min(p.x for p in pts); mxx = max(p.x for p in pts); mny = min(p.y for p in pts); mxy = max(p.y for p in pts); mnz = min(p.z for p in pts)
    tw, td = abs(X(x1) - X(x0)), abs(Y(y1) - Y(y0))
    sx, sy = tw / (mxx - mnx), td / (mxy - mny)
    s = min(sx, sy) if keep_aspect else None
    root.scale = (s, s, s) if keep_aspect else (sx, sy, (sx + sy) / 2)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2; cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    mnz = min(p.z for p in pts)
    root.location += Vector(((X(x0) + X(x1)) / 2 - cx, (Y(y0) + Y(y1)) / 2 - cy, z - mnz))
    return root


# ---------------------------------------------------------------- architecture
geo = json.load(open(ROOT + 'tools/bl/p136_geo.json'))
for i, (x0, y0, x1, y1) in enumerate(geo['walls']):
    box(f'wall{i}', x0, y0, x1, y1, 0, H_WALL, M['wall'])

# floors (plan interior rects) - wood everywhere, tile in the bathroom
for i, (x0, y0, x1, y1) in enumerate(geo['floor']):
    box(f'floor{i}', x0, y0, x1, y1, -0.02, 0.0, M['floor'])
box('floor_bath', 1744, 2820, 2526, 3727, 0.0, 0.004, M['tile'])

# windows: sill wall, white sill, frame + glass, light curtains at the sides
def window(x0, x1, y0, y1, depth_dir=1):
    box('win_low', x0, y0, x1, y1, 0, 0.85, M['wall'])
    my = (y0 + y1) / 2
    box('win_sill', x0, y1 - 4, x1, y1 + 28 * depth_dir, 0.85, 0.89, M['sill'], 0.004)
    box('win_frame_a', x0, my - 9, x1, my - 4, 0.89, 2.3, M['frame'])
    box('win_glass', x0, my - 4, x1, my + 4, 0.89, 2.3, M['glass'])
    n = max(2, round((x1 - x0) / 330))
    for k in range(n + 1):
        xx = x0 + (x1 - x0) * k / n
        box(f'win_mull{k}', xx - 6, my - 12, xx + 6, my + 12, 0.89, 2.3, M['frame'])
    for side in (0, 1):                                    # curtains bunched at both ends
        cxx = x0 + 60 if side == 0 else x1 - 60
        for j in range(7):
            o = cyl('curt', cxx - 45 + j * 15, y1 + 30, 0.035, 0.05, 2.5, M['curtain'], 16)

window(462, 1150, 305, 406)
window(1600, 2286, 305, 406)
# glazed partition loggia / bedroom (plan y880-920, x1505-2070) with an open door at its left end
box('gp_low', 1505, 880, 2070, 920, 0, 0.05, M['frame'])
box('gp_glass', 1680, 896, 2070, 904, 0.05, 2.4, M['glass'])
for xx in (1680, 1875, 2068):
    box('gp_mull', xx - 5, 890, xx + 5, 910, 0.05, 2.4, M['frame'])


# doors (leaves 0.04 m thick), hinge in plan px, length m, angle deg (plan view ccw from +x)
def leaf(hx, hy, length, ang):
    cx = hx + math.cos(math.radians(ang)) * length / 2 / S
    cy = hy - math.sin(math.radians(ang)) * length / 2 / S
    rbox('door', cx, cy, length, 0.04, 0.0, 2.1, ang, M['oak_dark'], 0.004)

leaf(1373, 2350, 0.8, 145)        # kitchen-living door, opened into the hall
leaf(1487, 2350, 0.8, 35)         # bedroom door
leaf(1744, 2810, 0.7, 125)        # bathroom door, opened into the hall (plan)
leaf(1440, 3190, 0.9, -130)       # entrance door, opened out
gx, gy = 1510, 905                                         # glazed loggia door: frame leaf opened into the bedroom (plan arc)
for k, (dx, dy) in enumerate(((0, 0),)):
    rbox('gp_door', gx + 0.33 / S * math.cos(math.radians(-75)), gy - 0.33 / S * math.sin(math.radians(-75)), 0.66, 0.035, 0.0, 2.2, -75, M['frame'])

# ---------------------------------------------------------------- kitchen-living 17,0
# sofa (plan 265-572 x 491-1111): back along the left wall, arms top/bottom, 2 seat cushions, pillows
box('sofa_base', 268, 495, 568, 1107, 0.0, 0.40, M['boucle'], 0.03)
soft(box('sofa_back', 268, 495, 340, 1107, 0.40, 0.78, M['boucle'], 0.04), 0.05)
soft(box('sofa_arm1', 268, 495, 568, 560, 0.40, 0.62, M['boucle'], 0.04), 0.05)
soft(box('sofa_arm2', 268, 1042, 568, 1107, 0.40, 0.62, M['boucle'], 0.04), 0.05)
soft(box('cush1', 342, 562, 566, 798, 0.40, 0.52, M['boucle'], 0.05), 0.06)
soft(box('cush2', 342, 802, 566, 1040, 0.40, 0.52, M['boucle'], 0.05), 0.06)
for (cx, cy, a) in ((380, 610, 25), (375, 960, -20), (395, 1010, 10)):
    soft(rbox('pillow_s', cx, cy, 0.42, 0.14, 0.52, 0.92, a, M['linen_beige'], 0.04), 0.05)
box('rug_liv', 560, 520, 1110, 1080, 0.0, 0.012, M['rug'], 0.004)
# coffee table (plan 745-919 x 680-954): walnut top + 4 legs
box('ct_top', 748, 683, 916, 951, 0.40, 0.44, M['oak_dark'], 0.006)
for cx, cy in ((765, 700), (899, 700), (765, 934), (899, 934)):
    box('ct_leg', cx - 6, cy - 6, cx + 6, cy + 6, 0, 0.40, M['oak_dark'])
box('tv', 1338, 615, 1362, 1021, 1.0, 1.62, M['black_glass'], 0.004)
place_asset('potted_plant_02', 1180, 1110, 1365, 1300)
# fridge (plan box), stainless top
box('fridge', 265, 1254, 515, 1490, 0, 1.85, M['steel'], 0.01)
box('fridge_gap', 509, 1258, 515, 1486, 1.8, 1.86, M['black_glass'])
# countertop L: left run + bottom run, 0.9 m high, oak
box('counter_l', 265, 1490, 515, 2370, 0, 0.9, M['oak'], 0.006)
box('counter_b', 265, 2370, 790, 2560, 0, 0.9, M['oak'], 0.006)
box('cooktop', 290, 1625, 495, 1895, 0.9, 0.906, M['black_glass'], 0.004)
for cx, cy, r in ((345, 1690, 0.085), (445, 1690, 0.07), (345, 1830, 0.07), (445, 1830, 0.085)):
    o = cyl('zone', cx, cy, r, 0.906, 0.907, col_mat('zone', (0.05, 0.05, 0.05), 0.2)); o.scale = (1, 1, 1)
sk = box('sink_rim', 298, 2118, 492, 2340, 0.70, 0.905, M['steel'], 0.004)
cut(sk, box('sink_hole', 318, 2140, 472, 2318, 0.72, 1.0, M['steel']))
cut(bpy.data.objects['counter_l'], box('ct_hole', 300, 2120, 490, 2338, 0.6, 1.0, M['steel']))
cyl('faucet', 300 + 12, 2150, 0.018, 0.9, 1.15, M['chrome'], 16)
rbox('faucet_arm', 330, 2170, 0.2, 0.02, 1.13, 1.15, -40, M['chrome'])
# dining table + 2 chairs
box('dt_top', 1115, 1495, 1365, 1802, 0.72, 0.75, M['oak_dark'], 0.005)
for cx, cy in ((1135, 1515), (1345, 1515), (1135, 1782), (1345, 1782)):
    box('dt_leg', cx - 10, cy - 10, cx + 10, cy + 10, 0, 0.72, M['oak_dark'])
for cy, back in ((1450, 1405), (1850, 1895)):                     # upholstered chairs (plan)
    soft(box('chair_seat', 1172, cy - 45, 1298, cy + 45, 0.42, 0.48, M['boucle'], 0.02), 0.03)
    soft(box('chair_back', 1172, min(back, back - 18 if back > cy else back), 1298, (back + 18) if back < cy else back, 0.48, 0.85, M['boucle'], 0.02), 0.03)

# ---------------------------------------------------------------- bedroom 11,6
box('rug_bed', 1700, 1130, 2440, 1960, 0.0, 0.012, M['rug'], 0.004)
box('bed_frame', 1751, 1215, 2525, 1872, 0, 0.32, M['oak'], 0.01)
soft(box('headboard', 2490, 1210, 2525, 1877, 0.3, 1.1, M['linen_beige'], 0.03), 0.04)
mt = soft(box('mattress', 1765, 1228, 2492, 1859, 0.32, 0.55, M['linen'], 0.05), 0.05)
collider(mt); collider(bpy.data.objects['bed_frame'])
duv = cloth_drape('duvet', 1740, 1190, 2265, 1897, 0.75, M['linen'], frames=40, thick=0.03, mass=0.4, stiff=8)
wrinkle(duv, 0.012, 0.12, 0); collider(duv, 0.006)
throw = cloth_drape('throw', 1835, 1180, 2010, 1910, 0.95, M['linen_beige'], frames=40, n=48, thick=0.012, mass=0.3, stiff=15)
wrinkle(throw, 0.015, 0.05, 0)
for py in (1400, 1700):
    wrinkle(soft(box('pillow', 2300, py - 135, 2475, py + 135, 0.55, 0.74, M['linen'], 0.06), 0.06), 0.008)
    wrinkle(soft(rbox('pillow2', 2275, py, 0.30, 0.48, 0.60, 0.80, 4 if py < 1500 else -5, M['linen_beige'], 0.05), 0.05), 0.008)
for y0, y1 in ((1041, 1201), (1885, 2044)):
    box('nightstand', 2370, y0, 2525, y1, 0, 0.5, M['oak'], 0.006)
    cyl('lamp_base', 2447, (y0 + y1) / 2, 0.05, 0.5, 0.75, M['ceramic'])
    cyl('lamp_shade', 2447, (y0 + y1) / 2, 0.12, 0.75, 0.95, col_mat('shade', (1.0, 0.82, 0.58), 0.6, emit=6.0))
    bpy.ops.object.light_add(type='POINT', location=(X(2447), Y((y0 + y1) / 2), 1.1)); lp = bpy.context.active_object
    lp.data.energy = 60; lp.data.color = (1.0, 0.72, 0.42); lp.data.shadow_soft_size = 0.15
box('tv_bed', 1436, 1354, 1456, 1760, 1.0, 1.6, M['black_glass'], 0.004)

# ---------------------------------------------------------------- loggia 3,8
place_asset('coffee_table_round_01', 1884, 691, 2030, 841)
place_asset('modern_arm_chair_01', 2064, 608, 2281, 832, ang=-120)
place_asset('potted_plant_02', 2264, 441, 2525, 655)
place_asset('potted_plant_02', 1080, 420, 1340, 640)

# ---------------------------------------------------------------- wardrobes (open, garments across the rail)
GAR = [(0.85, 0.85, 0.83), (0.62, 0.70, 0.80), (0.75, 0.66, 0.55), (0.18, 0.20, 0.28), (0.55, 0.45, 0.35), (0.90, 0.88, 0.84), (0.42, 0.44, 0.40)]
def wardrobe(x0, y0, x1, y1, axis='x'):
    t = 0.02 / S
    box('wr_back', x0, y0, x1, y1, 0, 0.02, M['oak'])
    for sx0, sy0, sx1, sy1 in ((x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1)):
        box('wr_side', sx0, sy0, sx1, sy1, 0, 2.2, M['oak'], 0.002)
    led = box('wr_led', x0 + t, y0 + t, x1 - t, y0 + t + 6, 2.12, 2.13, col_mat('led', (1.0, 0.75, 0.45), 0.5, emit=8.0))
    if axis == 'x':
        my = (y0 + y1) / 2; box('rail', x0 + t, my - 4, x1 - t, my + 4, 1.85, 1.87, M['chrome'])
        n = int((X(x1) - X(x0)) / 0.055); xs = [x0 + t + 15 + i * (x1 - x0 - 2 * t - 30) / max(1, n - 1) for i in range(n)]
        for xx in xs:
            c = random.choice(GAR); w = (y1 - y0) * S * 0.8
            g = rbox('garment', xx, my, 0.05, w, 0.9 + random.random() * 0.3, 1.86, 0, col_mat('g', c, 0.9), 0.012); soft(g, 0.012, 2)
            rbox('hanger', xx, my, 0.012, w * 0.9, 1.84, 1.87, 0, M['oak_dark'])
    else:
        mx = (x0 + x1) / 2; box('rail', mx - 4, y0 + t, mx + 4, y1 - t, 1.85, 1.87, M['chrome'])
        n = int((Y(y0) - Y(y1)) / 0.055); ys = [y0 + t + 15 + i * (y1 - y0 - 2 * t - 30) / max(1, n - 1) for i in range(n)]
        for yy in ys:
            c = random.choice(GAR); w = (x1 - x0) * S * 0.8
            g = rbox('garment', mx, yy, w, 0.05, 0.9 + random.random() * 0.3, 1.86, 0, col_mat('g', c, 0.9), 0.012); soft(g, 0.012, 2)
            rbox('hanger', mx, yy, w * 0.9, 0.012, 1.84, 1.87, 0, M['oak_dark'])

wardrobe(1826, 2166, 2525, 2341)                     # bedroom wardrobe (plan)
wardrobe(1833, 2372, 2525, 2520)                     # hall wardrobe (plan)
box('hall_cab', 2290, 2520, 2525, 2799, 0, 0.9, M['oak'], 0.006)   # closed cabinet of the L (plan)
# hall: shoe cabinet + pouf, boiler; bathroom tall cabinet
box('shoe_cab', 1014, 2668, 1095, 2930, 0, 0.95, M['oak'], 0.006)
soft(box('pouf', 1018, 2945, 1084, 3145, 0, 0.42, M['boucle'], 0.03), 0.03)
box('boiler', 1645, 2863, 1711, 3158, 0.0, 1.9, M['white'], 0.01)
box('bath_cab', 1745, 2863, 1808, 3158, 0.0, 2.0, M['white'], 0.006)

# ---------------------------------------------------------------- bathroom 4,8
box('wc_install', 2470, 2980, 2525, 3288, 0, 1.1, M['white'], 0.01)
wc = cyl('wc_bowl', 2385, 3134, 0.18, 0.25, 0.40, M['ceramic'], 48); wc.scale = (1.45, 1.0, 1.0)
soft(wc, 0.03, 3)
seat = cyl('wc_seat', 2380, 3134, 0.165, 0.40, 0.43, M['ceramic'], 48); seat.scale = (1.42, 1.0, 1.0); soft(seat, 0.01, 2)
wb = box('wb', 2406, 3315, 2523, 3468, 0.78, 0.86, M['ceramic'], 0.015)
wbh = cyl('wb_hole', 2458, 3392, 0.11, 0.80, 1.0, M['ceramic']); wbh.scale = (0.75, 1.0, 1.0); cut(wb, wbh)
cyl('wb_tap', 2510, 3392, 0.015, 0.86, 1.0, M['chrome'], 16)
box('washer', 1744, 3493, 1950, 3726, 0, 0.85, M['white'], 0.015)
box('washer_panel', 1744, 3493, 1950, 3530, 0.85, 0.853, col_mat('wp', (0.7, 0.7, 0.72), 0.3))
tub = box('tub', 1955, 3488, 2523, 3727, 0, 0.58, M['ceramic'], 0.02)
tin = box('tub_in', 1990, 3518, 2490, 3697, 0.15, 1.0, M['ceramic']); soft(tin, 0.08)
cut(tub, tin)
cyl('tub_tap', 2505, 3608, 0.02, 0.58, 0.75, M['chrome'], 16)

# ---------------------------------------------------------------- lights + camera
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object; sun.data.energy = 1.2; sun.data.angle = math.radians(25)
sun.rotation_euler = (math.radians(22), math.radians(-12), math.radians(10)); sun.data.color = (1.0, 0.82, 0.64)
W, Hh = X(2597), -Y(3802)
bpy.ops.object.light_add(type='AREA', location=(W / 2, -Hh / 2, 6.0))
ar = bpy.context.active_object; ar.data.shape = 'RECTANGLE'; ar.data.size = W * 1.2; ar.data.size_y = Hh * 1.2; ar.data.energy = 700; ar.data.color = (1.0, 0.86, 0.72); ar.visible_glossy = False
world = bpy.data.worlds.new('w'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.50, 0.45, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25

# camera: same framing as the current render (render px = 119 + (px-190)*0.6442), isotropic -> resized to 2562 high afterwards
SX = 0.6442
cw = 1800 / SX                                      # plan px across the image
cx_px = 190 + (900 - 119) / SX
ch_iso = round(2562 * SX / 0.6356)
cy_px = 305 + (1281 - 196) / 0.6356
cam = bpy.data.cameras.new('cam'); cam.type = 'ORTHO'; cam.ortho_scale = max(cw, ch_iso / SX) * S
co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
co.location = (X(cx_px), Y(cy_px), 20); co.rotation_euler = (0, 0, 0)
cam.clip_end = 100
sc.render.resolution_x = 1800; sc.render.resolution_y = ch_iso; sc.render.resolution_percentage = int(os.environ.get('BLPCT', '100'))
sc.render.film_transparent = True
sc.render.filepath = OUT
if os.environ.get('BLBORDER'):
    b = [float(v) for v in os.environ['BLBORDER'].split(',')]
    sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = b
if not os.environ.get('BLBORDER'): bpy.ops.wm.save_as_mainfile(filepath=ROOT + 'tools/bl/p136.blend')
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT, ch_iso)
