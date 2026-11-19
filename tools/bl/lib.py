"""Furniture library for top-down apartment visualisations (Blender 5.x, Cycles).
Every builder: f(name, cx, cy, w, d, rot=0, **opts) -> root Empty; cx, cy in metres (world), w along local X, d along local Y, rot in degrees.
Local frame: the piece 'faces' local -Y (front), its back is at +Y (against a wall when rot puts +Y to the wall).
Modelled for a camera straight above: silhouettes, top surfaces, soft bevels, fabric folds and contact shadows matter most."""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix

ROOT = 'C:/Projects/3d_visual/'
A = ROOT + 'assets/ph/'
_M = {}
rnd = random.Random(11)


# ============================================================== materials
def _tex(nt, folder, key, mapping, non_color=False):
    files = [f for f in os.listdir(A + folder) if key in f]
    if not files: return None
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(A + folder + '/' + files[0], check_existing=True)
    if non_color: t.image.colorspace_settings.name = 'Non-Color'
    t.projection = 'BOX'; t.projection_blend = 0.25
    nt.links.new(mapping.outputs['Vector'], t.inputs['Vector']); return t


def pbr(name, folder=None, scale=1.0, color=None, rough=None, metal=0.0, nstr=0.6, rot=0.0, sheen=0.0, coat=0.0, use_diff=True, spec=0.5, hsv=None):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Metallic'].default_value = metal; b.inputs['Specular IOR Level'].default_value = spec
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen; b.inputs['Sheen Roughness'].default_value = 0.4
        if color: b.inputs['Sheen Tint'].default_value = (*[min(1, c * 1.2) for c in color], 1)
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.08
    if folder:
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (scale, scale, scale); mp.inputs['Rotation'].default_value[2] = rot
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        d = _tex(nt, folder, '_diff_', mp) if use_diff else None
        if d is not None and hsv:
            hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.inputs['Hue'].default_value = hsv[0]; hs.inputs['Saturation'].default_value = hsv[1]; hs.inputs['Value'].default_value = hsv[2]
            nt.links.new(d.outputs['Color'], hs.inputs['Color']); d = hs
        if d is not None:
            if color:
                mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1
                nt.links.new(d.outputs['Color'], mx.inputs[6]); mx.inputs[7].default_value = (*color, 1); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
            else: nt.links.new(d.outputs['Color'], b.inputs['Base Color'])
        elif color: b.inputs['Base Color'].default_value = (*color, 1)
        r = _tex(nt, folder, '_rough_', mp, True)
        if r is not None and rough is None: nt.links.new(r.outputs['Color'], b.inputs['Roughness'])
        n = _tex(nt, folder, '_nor_gl_', mp, True)
        if n is not None:
            nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr
            nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    elif color: b.inputs['Base Color'].default_value = (*color, 1)
    if rough is not None: b.inputs['Roughness'].default_value = rough
    _M[name] = m; return m


def stone(name, base, vein):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 12; nz.inputs['Distortion'].default_value = 2.5
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[0].color = (*base, 1)
    cr.color_ramp.elements[1].position = 0.52; cr.color_ramp.elements[1].color = (*vein, 1)
    e = cr.color_ramp.elements.new(0.6); e.color = (*base, 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.22; b.inputs['Coat Weight'].default_value = 0.3
    _M[name] = m; return m


def emit(name, color, strength):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Emission Color'].default_value = (*color, 1); b.inputs['Emission Strength'].default_value = strength
    _M[name] = m; return m


def fabric(color, kind='linen'):
    key = f'fab_{kind}_{color[0]:.2f}_{color[1]:.2f}_{color[2]:.2f}'
    if kind == 'boucle': return pbr(key, 'wool_boucle', 18.0, color, 0.95, nstr=1.0, sheen=0.6, use_diff=False, spec=0.25)
    if kind == 'velvet': return pbr(key, 'fabric_pattern_07', 6.0, color, 0.8, nstr=0.3, sheen=1.0, use_diff=False, spec=0.2)
    if kind == 'cotton': return pbr(key, 'rough_linen', 22.0, color, 0.85, nstr=0.5, sheen=0.08, use_diff=False, spec=0.25)
    if kind == 'wool': return pbr(key, 'wool_boucle', 30.0, color, 0.95, nstr=0.6, sheen=0.15, use_diff=False, spec=0.2)
    return pbr(key, 'rough_linen', 7.0, color, 0.9, nstr=0.8, sheen=0.4, use_diff=False, spec=0.3)


def M(k):
    return {
        'oak': lambda: pbr('oak', 'oak_veneer_01', 1.6, (1.0, 0.86, 0.70), coat=0.15),
        'oak_light': lambda: pbr('oak_light', 'oak_veneer_01', 1.6, (1.08, 0.97, 0.86), coat=0.1),
        'walnut': lambda: pbr('walnut', 'oak_veneer_01', 1.6, (0.45, 0.30, 0.22), coat=0.25),
        'stone': lambda: stone('stone', (0.93, 0.90, 0.86), (0.72, 0.68, 0.64)),
        'stone_dark': lambda: pbr('stone_dark', 'marble_01', 0.9, (0.25, 0.24, 0.24), 0.2, coat=0.3),
        'white': lambda: pbr('white', None, color=(0.86, 0.86, 0.84), rough=0.35),
        'white_matte': lambda: pbr('white_matte', None, color=(0.84, 0.83, 0.80), rough=0.6),
        'ceramic': lambda: pbr('ceramic', None, color=(0.92, 0.92, 0.91), rough=0.06, coat=0.6),
        'steel': lambda: pbr('steel', None, color=(0.62, 0.62, 0.63), rough=0.28, metal=1.0),
        'chrome': lambda: pbr('chrome', None, color=(0.9, 0.9, 0.9), rough=0.06, metal=1.0),
        'black': lambda: pbr('black', None, color=(0.012, 0.012, 0.013), rough=0.4),
        'black_glass': lambda: pbr('black_glass', None, color=(0.004, 0.004, 0.005), rough=0.06, coat=1.0),
        'brass': lambda: pbr('brass', None, color=(0.78, 0.58, 0.32), rough=0.25, metal=1.0),
        'glass': lambda: _glass(),
        'leather': lambda: pbr('leather', 'brown_leather', 3.0, (0.75, 0.6, 0.5), nstr=0.6),
        'shade': lambda: emit('shade', (1.0, 0.80, 0.55), 4.0),
        'led': lambda: emit('led', (1.0, 0.72, 0.42), 4.0),
        'soil': lambda: pbr('soil', None, color=(0.08, 0.06, 0.05), rough=0.95),
        'rug': lambda: pbr('rug', 'wool_boucle', 10.0, (0.80, 0.77, 0.72), 0.95, nstr=1.2, sheen=0.5, use_diff=False, spec=0.2),
    }[k]()


def _glass():
    if 'glass' in _M: return _M['glass']
    m = bpy.data.materials.new('glass'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Transmission Weight'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.02; b.inputs['Base Color'].default_value = (0.92, 0.97, 0.98, 1)
    _M['glass'] = m; return m


# ============================================================== geometry helpers
def _root(name, cx, cy, rot):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.location = (cx, cy, 0); e.rotation_euler[2] = math.radians(rot); return e


def _link(o, root):
    o.parent = root; return o


def cube(root, name, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, seg=3, sub=0):
    """local-space box (metres) under root"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.scale = (x1 - x0, y1 - y0, z1 - z0); o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    _apply_scale(o)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'NONE'
    if sub:
        s = o.modifiers.new('ss', 'SUBSURF'); s.levels = sub; s.render_levels = sub
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def cyl(root, name, x, y, r, z0, z1, mat, verts=48, bevel=0.0, sx=1.0, sy=1.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=z1 - z0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = (x, y, (z0 + z1) / 2); o.scale = (sx, sy, 1); _apply_scale(o)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL'); b.width = bevel; b.segments = 3; b.limit_method = 'ANGLE'
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def _apply_scale(o):
    me = o.data; mx = Matrix.Diagonal((*o.scale, 1.0)); me.transform(mx); o.scale = (1, 1, 1)


def _smooth(o):
    for p in o.data.polygons: p.use_smooth = True
    try: o.data.shade_smooth()
    except Exception: pass


def superprism(root, name, cx, cy, a, b, z0, z1, mat, n=4.0, seg=64):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bot, top = [], []
    for i in range(seg):
        t = 2 * math.pi * i / seg; c, s_ = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / n), c); y = b * math.copysign(abs(s_) ** (2 / n), s_)
        bot.append(bm.verts.new((x, y, z0))); top.append(bm.verts.new((x, y, z1)))
    bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(seg): bm.faces.new((bot[i], bot[(i + 1) % seg], top[(i + 1) % seg], top[i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = (cx, cy, 0)
    o.data.materials.append(mat); return _link(o, root)


def cushion(root, name, x0, y0, z0, x1, y1, z1, mat, puff=0.35, pinch=0.6, wr=0.006, seed=0):
    """soft upholstered cushion: subdivided box, edges pinched, top/bottom bulged, small wrinkles"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=10, use_grid_fill=True)
    r = random.Random(seed)
    for v in bm.verts:
        x, y, z = v.co; rr = min(1.0, (2 * x) ** 2 + (2 * y) ** 2) if False else max(abs(2 * x), abs(2 * y))
        k = 1 - rr ** 4
        v.co.z = z * (1 + puff * k) * (1 - pinch * 0.15 * (rr ** 8))
        v.co.x *= 1 - 0.04 * (abs(2 * z) ** 2); v.co.y *= 1 - 0.04 * (abs(2 * z) ** 2)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.scale = (x1 - x0, y1 - y0, z1 - z0); o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); _apply_scale(o)
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = 2
    if wr:
        t = bpy.data.textures.new('wr', 'CLOUDS'); t.noise_scale = 0.06 + r.random() * 0.03
        d = o.modifiers.new('wr', 'DISPLACE'); d.texture = t; d.strength = wr; d.texture_coords = 'OBJECT'
        hel = bpy.data.objects.new(name + '_tc', None); bpy.context.scene.collection.objects.link(hel); hel.location = (r.random() * 5, r.random() * 5, 0); d.texture_coords_object = hel
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def pillow(root, name, cx, cy, z, w, d, h, ang, mat, seed=0):
    """throw pillow lying/leaning: lens-shaped, corners pointy"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=24, y_segments=24, size=0.5)
    top = list(bm.verts)
    ret = bmesh.ops.duplicate(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:])
    bot = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
    for v in top:
        rr = max(abs(2 * v.co.x), abs(2 * v.co.y)); v.co.z = 0.5 * (1 - rr ** 2.2)
    for v in bot:
        rr = max(abs(2 * v.co.x), abs(2 * v.co.y)); v.co.z = -0.5 * (1 - rr ** 2.2)
    bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if all(v in set(bot) for v in f.verts)])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    r = random.Random(seed)
    for v in bm.verts:                                          # slight sag + pinched corners
        v.co.x *= 1 - 0.10 * (abs(2 * v.co.y) ** 3); v.co.y *= 1 - 0.10 * (abs(2 * v.co.x) ** 3)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.scale = (w, d, h); _apply_scale(o); o.location = (cx, cy, z + h / 2); o.rotation_euler[2] = math.radians(ang)
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = 2
    t = bpy.data.textures.new('wr', 'CLOUDS'); t.noise_scale = 0.05
    dd = o.modifiers.new('wr', 'DISPLACE'); dd.texture = t; dd.strength = 0.006
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def cloth(root, name, x0, y0, x1, y1, z, mat, colliders=(), frames=36, n=56, thick=0.01, mass=0.3, stiff=10, bend=0.5, pin_edge=None, fold=None):
    """drape a cloth sheet (local coords) onto colliders and freeze the result"""
    sc = bpy.context.scene
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=n, y_segments=int(n * abs(y1 - y0) / abs(x1 - x0)) or 2, size=0.5)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    o.scale = (x1 - x0, y1 - y0, 1); _apply_scale(o)
    o.parent = root; o.location = ((x0 + x1) / 2, (y0 + y1) / 2, z)
    if fold is not None:                                         # fold back the top part (turn-down)
        for v in o.data.vertices:
            if v.co.y > fold: v.co.z += 0.02; v.co.y = 2 * fold - v.co.y
    for c in colliders:
        if not any(m.type == 'COLLISION' for m in c.modifiers): c.modifiers.new('col', 'COLLISION'); c.collision.thickness_outer = 0.004
    cm = o.modifiers.new('Cloth', 'CLOTH'); st = cm.settings
    st.quality = 6; st.mass = mass; st.tension_stiffness = stiff; st.compression_stiffness = stiff; st.shear_stiffness = stiff; st.bending_stiffness = bend
    st.air_damping = 2.0
    cm.collision_settings.distance_min = 0.003; cm.collision_settings.use_self_collision = True; cm.collision_settings.self_distance_min = 0.003
    cm.point_cache.frame_start = 1; cm.point_cache.frame_end = frames
    if pin_edge is not None:
        vg = o.vertex_groups.new(name='pin'); vg.add([v.index for v in o.data.vertices if pin_edge(v.co)], 1.0, 'REPLACE'); st.vertex_group_mass = 'pin'
    sc.frame_start = 1; sc.frame_end = max(sc.frame_end, frames)
    for f in range(1, frames + 1): sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg)
    newme = bpy.data.meshes.new_from_object(ev); o.modifiers.clear(); old = o.data; o.data = newme; bpy.data.meshes.remove(old)
    sc.frame_set(1)
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = thick; so.offset = 0
    ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = 1; ss.render_levels = 2
    t = bpy.data.textures.new('cw', 'CLOUDS'); t.noise_scale = 0.18; t.noise_depth = 2
    dd = o.modifiers.new('cw', 'DISPLACE'); dd.texture = t; dd.strength = 0.05
    o.data.materials.append(mat); _smooth(o); return o


# ============================================================== living
def sofa(name, cx, cy, w, d, rot=0, color=(0.80, 0.75, 0.68), kind='boucle', pillows=((0.55, 0.47, 0.38), (0.80, 0.74, 0.66)), seats=None):
    r = _root(name, cx, cy, rot); f = fabric(color, kind); hw, hd = w / 2, d / 2
    arm = min(0.16, w * 0.08); seats = seats or max(2, min(3, round((w - 2 * arm) / 0.65)))
    cube(r, 'plinth', -hw + 0.03, -hd + 0.05, 0.0, hw - 0.03, hd - 0.04, 0.08, M('walnut'), 0.01)
    cushion(r, 'base', -hw, -hd + 0.02, 0.07, hw, hd, 0.30, f, 0.05, 0.3, 0.002, 1)
    cushion(r, 'back', -hw + 0.02, hd - 0.20, 0.30, hw - 0.02, hd, 0.78, f, 0.12, 0.5, 0.004, 2)
    for i, sx in enumerate((-1, 1)):
        cushion(r, f'arm{i}', sx * hw - arm if sx > 0 else -hw, -hd + 0.02, 0.30, hw if sx > 0 else -hw + arm, hd, 0.62, f, 0.10, 0.5, 0.003, 3 + i)
    sw = (w - 2 * arm) / seats
    for i in range(seats):
        x0 = -hw + arm + i * sw + 0.005
        cushion(r, f'seat{i}', x0, -hd + 0.04, 0.30, x0 + sw - 0.01, hd - 0.19, 0.46, f, 0.30, 0.6, 0.006, 10 + i)
        cushion(r, f'backc{i}', x0, hd - 0.36, 0.40, x0 + sw - 0.01, hd - 0.16, 0.86, f, 0.25, 0.6, 0.006, 20 + i)
    if pillows:
        for i, (px, pa, pc) in enumerate(((-hw + arm + 0.25, 18, pillows[0]), (hw - arm - 0.25, -14, pillows[1]), (hw - arm - 0.50, 6, pillows[0]))[:len(pillows) + 1]):
            pillow(r, f'pil{i}', px, hd - 0.42, 0.44, 0.46, 0.15, 0.42, pa, fabric(pc, 'velvet' if i % 2 else 'linen'), i)
    return r


def armchair(name, cx, cy, w, d, rot=0, color=(0.86, 0.82, 0.75), kind='boucle'):
    r = _root(name, cx, cy, rot); f = fabric(color, kind); hw, hd = w / 2, d / 2
    cushion(r, 'shell', -hw, -hd, 0.12, hw, hd, 0.70, f, 0.25, 0.8, 0.004, 5)
    cushion(r, 'seat', -hw + 0.12, -hd + 0.05, 0.38, hw - 0.12, hd - 0.16, 0.74, f, 0.35, 0.6, 0.006, 6)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(r, 'leg', sx * (hw - 0.07), sy * (hd - 0.07), 0.015, 0, 0.13, M('walnut'), 12)
    return r


def coffee_table(name, cx, cy, w, d, rot=0, round_=False, mat='walnut', decor=True):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; m = M(mat)
    if round_:
        cyl(r, 'top', 0, 0, min(hw, hd), 0.40, 0.44, m, 64, 0.008); cyl(r, 'stem', 0, 0, min(hw, hd) * 0.3, 0, 0.40, m, 32)
    else:
        cube(r, 'top', -hw, -hd, 0.38, hw, hd, 0.42, m, 0.012)
        cube(r, 'shelf', -hw + 0.05, -hd + 0.05, 0.10, hw - 0.05, hd - 0.05, 0.12, m, 0.006)
        for sx in (-1, 1):
            for sy in (-1, 1): cube(r, 'leg', sx * (hw - 0.04) - 0.02, sy * (hd - 0.04) - 0.02, 0, sx * (hw - 0.04) + 0.02, sy * (hd - 0.04) + 0.02, 0.38, m, 0.004)
    if decor:
        cyl(r, 'tray', w * 0.1, 0, 0.12, 0.42 if not round_ else 0.44, 0.44 if not round_ else 0.46, M('brass'), 48, 0.003)
        cyl(r, 'candle', w * 0.1, 0, 0.035, 0.44, 0.52, M('white_matte'), 24, 0.004)
        cube(r, 'book', -w * 0.2 - 0.1, -0.08, 0.42, -w * 0.2 + 0.1, 0.07, 0.46, fabric((0.55, 0.50, 0.44)), 0.004)
    return r


def dining_table(name, cx, cy, w, d, rot=0, mat='walnut', decor=True):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; m = M(mat)
    cube(r, 'top', -hw, -hd, 0.72, hw, hd, 0.75, m, 0.008)
    for sx in (-1, 1):
        for sy in (-1, 1): cube(r, 'leg', sx * (hw - 0.06) - 0.025, sy * (hd - 0.06) - 0.025, 0, sx * (hw - 0.06) + 0.025, sy * (hd - 0.06) + 0.025, 0.72, m, 0.004)
    if decor:
        cyl(r, 'vase', 0, 0, 0.06, 0.75, 0.95, M('ceramic'), 32, 0.01)
        plant_small(r, 0, 0, 0.95, 0.18)
    return r


def chair(name, cx, cy, w, d, rot=0, color=(0.82, 0.77, 0.70)):
    """upholstered dining chair, back at local +Y"""
    r = _root(name, cx, cy, rot); f = fabric(color, 'boucle'); hw, hd = w / 2, d / 2
    cushion(r, 'seat', -hw, -hd, 0.40, hw, hd - 0.04, 0.48, f, 0.25, 0.6, 0.003, 7)
    cushion(r, 'back', -hw + 0.01, hd - 0.10, 0.48, hw - 0.01, hd, 0.86, f, 0.25, 0.6, 0.003, 8)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(r, 'leg', sx * (hw - 0.04), sy * (hd - 0.05), 0.012, 0, 0.42, M('walnut'), 12)
    return r


def tv(name, cx, cy, w, rot=0, z=1.05):
    r = _root(name, cx, cy, rot)
    cube(r, 'panel', -w / 2, -0.015, z, w / 2, 0.015, z + w * 0.56, M('black_glass'), 0.004)
    cube(r, 'bezel', -w / 2 - 0.002, 0.012, z - 0.002, w / 2 + 0.002, 0.03, z + w * 0.56 + 0.002, M('black'), 0.002)
    return r


def rug(name, cx, cy, w, d, rot=0, color=(0.80, 0.77, 0.72)):
    r = _root(name, cx, cy, rot)
    cube(r, 'rug', -w / 2, -d / 2, 0, w / 2, d / 2, 0.012, pbr(f'rug_{color}', 'wool_boucle', 10.0, color, 0.95, nstr=1.2, sheen=0.5, use_diff=False, spec=0.2), 0.006)
    return r


def pouf(name, cx, cy, w, d, rot=0, color=(0.88, 0.84, 0.77), round_=False):
    r = _root(name, cx, cy, rot); f = fabric(color, 'boucle')
    if round_:
        o = cushion(r, 'pouf', -w / 2, -d / 2, 0.0, w / 2, d / 2, 0.42, f, 0.20, 0.9, 0.004, 9)
        o.modifiers.new('cast', 'CAST').factor = 0.85
    else:
        cushion(r, 'pouf', -w / 2, -d / 2, 0.0, w / 2, d / 2, 0.42, f, 0.20, 0.7, 0.004, 9)
    return r


# ============================================================== plants
_PLANT = {}


def plant_asset(root, x, y, size, aid='potted_plant_02', z=0.0, ang=0):
    if aid not in _PLANT:
        with bpy.data.libraries.load(A + aid + '/' + aid + '_1k.blend', link=False) as (src, dst): dst.objects = src.objects
        objs = [o for o in dst.objects if o is not None and o.type == 'MESH']
        coll = bpy.data.collections.new(aid)
        for o in objs: coll.objects.link(o)
        pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
        _PLANT[aid] = (coll, max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts)),
                       Vector(((max(p.x for p in pts) + min(p.x for p in pts)) / 2, (max(p.y for p in pts) + min(p.y for p in pts)) / 2, min(p.z for p in pts))))
    coll, ext, c0 = _PLANT[aid]
    inst = bpy.data.objects.new('plant', None); inst.instance_type = 'COLLECTION'; inst.instance_collection = coll
    bpy.context.scene.collection.objects.link(inst); inst.parent = root
    s = size / ext; inst.scale = (s, s, s); inst.rotation_euler[2] = math.radians(ang)
    off = Matrix.Rotation(math.radians(ang), 3, 'Z') @ (c0 * s)
    inst.location = (x - off.x, y - off.y, z - c0.z * s); return inst


def plant(name, cx, cy, size, rot=0, aid='potted_plant_02'):
    r = _root(name, cx, cy, 0); plant_asset(r, 0, 0, size, aid, ang=rot); return r


def plant_small(root, x, y, z, size):
    return plant_asset(root, x, y, size, 'potted_plant_02', z, rnd.random() * 360)


# ============================================================== bedroom
def bed(name, cx, cy, w, d, rot=0, linen=(0.86, 0.83, 0.78), throw=(0.62, 0.52, 0.42), head=(0.70, 0.62, 0.54), sim=True):
    """double bed, headboard at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    frame = cube(r, 'frame', -hw, -hd, 0.0, hw, hd - 0.06, 0.30, M('oak'), 0.012)
    cushion(r, 'headboard', -hw - 0.02, hd - 0.09, 0.25, hw + 0.02, hd, 1.10, fabric(head, 'velvet'), 0.15, 0.4, 0.002, 30)
    for i in range(1, 8):                                       # channel tufting lines
        x = -hw + i * w / 8; cube(r, 'tuft', x - 0.004, hd - 0.10, 0.28, x + 0.004, hd - 0.085, 1.06, fabric(tuple(c * 0.75 for c in head), 'velvet'))
    mat = cushion(r, 'mattress', -hw + 0.03, -hd + 0.03, 0.28, hw - 0.03, hd - 0.10, 0.52, fabric(linen), 0.06, 0.3, 0.0, 31)
    lin = fabric(linen); thr = fabric(throw, 'velvet')
    if sim:
        duv = cloth(r, 'duvet', -hw - 0.10, -hd - 0.08, hw + 0.10, hd - 0.55, 0.70, lin, (mat, frame), frames=40, n=60, thick=0.035, mass=0.45, stiff=6, bend=0.3)
        fold = cloth(r, 'turn', -hw - 0.06, hd - 0.75, hw + 0.06, hd - 0.48, 0.76, lin, (mat, duv), frames=30, n=40, thick=0.03, mass=0.3, stiff=6, bend=0.3)
        cloth(r, 'throw', -hw - 0.14, -hd * 0.62, hw + 0.14, -hd * 0.62 + 0.55, 0.85, thr, (mat, duv, frame), frames=40, n=50, thick=0.012, mass=0.3, stiff=12, bend=0.8)
    else:
        cushion(r, 'duvet', -hw, -hd, 0.52, hw, hd - 0.5, 0.62, lin, 0.2, 0.5, 0.008, 32)
    pw = (w - 0.10) / 2
    for i, sx in enumerate((-1, 1)):
        px = sx * (pw / 2 + 0.01)
        pillow(r, f'pillow{i}', px, hd - 0.30, 0.50, pw - 0.02, 0.48, 0.20, rnd.uniform(-3, 3), lin, 40 + i)
        pillow(r, f'deco{i}', px * 0.8, hd - 0.58, 0.55, 0.42, 0.14, 0.38, rnd.uniform(-8, 8), fabric(throw, 'velvet'), 50 + i)
    return r


def nightstand(name, cx, cy, w, d, rot=0, lamp=True, light=True):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd, 0.08, hw, hd, 0.52, M('oak'), 0.01)
    cube(r, 'gap', -hw + 0.01, -hd - 0.001, 0.30, hw - 0.01, -hd + 0.003, 0.305, M('black'))
    for sx in (-1, 1): cyl(r, 'leg', sx * (hw - 0.04), 0, 0.012, 0, 0.09, M('brass'), 12)
    if lamp:
        cyl(r, 'base', 0, 0.03, 0.06, 0.52, 0.72, M('ceramic'), 32, 0.02)
        cyl(r, 'shade', 0, 0.03, 0.14, 0.72, 0.92, M('shade'), 48, 0.003)
        if light:
            l = bpy.data.lights.new(name + '_l', 'POINT'); l.energy = 45; l.color = (1.0, 0.70, 0.42); l.shadow_soft_size = 0.12
            lo = bpy.data.objects.new(name + '_l', l); bpy.context.scene.collection.objects.link(lo); lo.parent = r; lo.location = (0, 0.03, 0.82)
        cube(r, 'book', -hw + 0.04, -hd + 0.04, 0.52, -hw + 0.20, -hd + 0.18, 0.55, fabric((0.48, 0.42, 0.36)), 0.004)
    return r


GARMENTS = [(0.90, 0.89, 0.86), (0.55, 0.64, 0.76), (0.76, 0.66, 0.52), (0.12, 0.14, 0.22), (0.48, 0.36, 0.26), (0.80, 0.78, 0.74),
            (0.36, 0.38, 0.34), (0.64, 0.58, 0.54), (0.22, 0.19, 0.17), (0.70, 0.72, 0.76), (0.58, 0.30, 0.22), (0.40, 0.46, 0.38)]


def _garment(root, name, x, y, z_top, width, length, mat, seed):
    """garment on a hanger seen from above: shoulder profile (curved, tapered) extruded down with folds"""
    rr = random.Random(seed)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    n = 18; prof = []
    for i in range(n + 1):                                       # shoulder line: arc in X, thickness profile in Y
        t = i / n * 2 - 1; px = t * width / 2; th = 0.018 + 0.03 * (1 - t * t) ** 0.6
        prof.append((px, th))
    ring = [Vector((px, th, 0)) for px, th in prof] + [Vector((px, -th, 0)) for px, th in reversed(prof)]
    layers = 8; vs = []
    for k in range(layers + 1):
        f = k / layers; zz = -f * length
        sw = 1 + 0.12 * f + rr.uniform(-0.03, 0.03); wob = rr.uniform(-0.01, 0.01)
        vs.append([bm.verts.new((p.y * (1 + 0.6 * f) + 0.010 * math.sin(p.x * 40 + seed + k), p.x * sw + wob, zz)) for p in ring])
    m = len(ring)
    for k in range(layers):
        for i in range(m):
            bm.faces.new((vs[k][i], vs[k][(i + 1) % m], vs[k + 1][(i + 1) % m], vs[k + 1][i]))
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = (x, y, z_top)
    o.rotation_euler[2] = math.radians(rr.uniform(-6, 6))
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = 2
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def wardrobe_open(name, cx, cy, w, d, rot=0, h=2.2, fill=0.85, short=False, led=True):
    """open wardrobe, rail along local X, garments across it; back at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; t = 0.022; m = M('oak')
    cube(r, 'back', -hw, hd - 0.012, 0, hw, hd, h, m)
    for sx in (-1, 1): cube(r, 'side', sx * hw - (t if sx > 0 else 0), -hd, 0, sx * hw + (0 if sx > 0 else t), hd, h, m, 0.002)
    cube(r, 'bottom', -hw, -hd, 0, hw, hd, 0.08, m, 0.002)
    nsec = max(1, round(w / 0.9))
    for i in range(1, nsec):
        x = -hw + i * w / nsec; cube(r, 'div', x - t / 2, -hd, 0, x + t / 2, hd, h, m, 0.002)
    for i in range(nsec):
        x0 = -hw + i * w / nsec + t; x1 = -hw + (i + 1) * w / nsec - t
        rail = cyl(r, 'rail', 0, 0, 0.009, -(x1 - x0) / 2, (x1 - x0) / 2, M('chrome'), 12)
        rail.rotation_euler[1] = math.radians(90); rail.location = ((x0 + x1) / 2, 0, 1.85)
        if led:
            for xx in (x0 + 0.004, x1 - 0.004): cube(r, 'led', xx - 0.004, -hd + 0.03, 0.9, xx + 0.004, hd - 0.03, 2.0, M('led'))
        nn = int((x1 - x0) * fill / 0.055)
        xs = [x0 + 0.04 + k * (x1 - x0 - 0.08) / max(1, nn - 1) for k in range(nn)]
        for k, x in enumerate(xs):
            c = GARMENTS[(k * 7 + i * 3 + int(cx * 13)) % len(GARMENTS)]
            ln = 0.55 if short else rnd.uniform(0.75, 1.05)
            _garment(r, 'g', x, 0, 1.84, min(d - 0.10, 0.44), ln, fabric(c), int(x * 1000) + k)
            cube(r, 'hanger', x - 0.004, -min(d - 0.1, 0.19), 1.80, x + 0.004, min(d - 0.1, 0.19), 1.815, M('walnut'), 0.002)
            cyl(r, 'hook', x, 0, 0.004, 1.84, 1.87, M('chrome'), 8)
    return r


def cabinet(name, cx, cy, w, d, rot=0, h=0.9, mat='oak', doors=2, handles=True):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd, 0.0, hw, hd, h, M(mat), 0.006)
    for i in range(1, doors):
        x = -hw + i * w / doors; cube(r, 'gap', x - 0.002, -hd - 0.001, 0.02, x + 0.002, -hd + 0.004, h - 0.01, M('black'))
    cube(r, 'top_gap', -hw, -hd - 0.001, h - 0.004, hw, hd, h - 0.002, M('black'))
    if handles:
        for i in range(doors):
            x = -hw + (i + 0.5) * w / doors; cube(r, 'handle', x - 0.06, -hd - 0.02, h - 0.06, x + 0.06, -hd, h - 0.045, M('brass'), 0.003)
    return r


def shoe_cabinet(name, cx, cy, w, d, rot=0):
    r = cabinet(name, cx, cy, w, d, rot, 0.95, 'oak', max(1, round(w / 0.45)), True)
    cyl(r, 'bowl', -w * 0.2, 0, 0.09, 0.95, 0.99, M('ceramic'), 32, 0.01)
    return r


def desk(name, cx, cy, w, d, rot=0):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'top', -hw, -hd, 0.72, hw, hd, 0.75, M('walnut'), 0.006)
    for sx in (-1, 1): cube(r, 'leg', sx * hw - (0.04 if sx > 0 else 0), -hd + 0.03, 0, sx * hw + (0 if sx > 0 else 0.04), hd - 0.03, 0.72, M('walnut'), 0.004)
    cube(r, 'laptop', -0.17, -0.12, 0.75, 0.17, 0.12, 0.765, M('steel'), 0.006)
    cyl(r, 'lamp', hw - 0.15, hd - 0.12, 0.07, 0.75, 0.77, M('black'), 24)
    return r


# ============================================================== kitchen
def kitchen_run(name, cx, cy, w, d, rot=0, sink_at=None, hob_at=None, hob_w=0.6, sink_w=0.55, fridge=False):
    """base cabinets + stone countertop along local X; sink_at/hob_at = local x of centres"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'base', -hw, -hd + 0.03, 0.10, hw, hd, 0.86, M('oak_light'), 0.004)
    cube(r, 'plinth', -hw, -hd + 0.07, 0, hw, hd, 0.10, M('black'))
    ct = cube(r, 'counter', -hw, -hd, 0.86, hw, hd, 0.90, M('stone'), 0.004)
    nd = max(1, round(w / 0.6))
    for i in range(1, nd):
        x = -hw + i * w / nd; cube(r, 'gap', x - 0.0015, -hd + 0.025, 0.12, x + 0.0015, -hd + 0.032, 0.85, M('black'))
    if hob_at is not None:
        cube(r, 'hob', hob_at - hob_w / 2, -hd + 0.06, 0.90, hob_at + hob_w / 2, hd - 0.06, 0.905, M('black_glass'), 0.003)
        for (zx, zy, zr) in ((-0.15, 0.12, 0.10), (0.15, 0.12, 0.08), (-0.15, -0.12, 0.08), (0.15, -0.12, 0.10)):
            ring = cyl(r, 'zone', hob_at + zx * hob_w / 0.6, zy * (d - 0.12) / 0.48, zr, 0.905, 0.9055, pbr('zone', None, color=(0.06, 0.06, 0.06), rough=0.3), 48)
            inner = cyl(r, 'zone_i', hob_at + zx * hob_w / 0.6, zy * (d - 0.12) / 0.48, zr - 0.006, 0.904, 0.91, M('black_glass'), 48)
            m = ring.modifiers.new('cut', 'BOOLEAN'); m.object = inner; m.operation = 'DIFFERENCE'; inner.hide_render = True
        cube(r, 'touch', hob_at - 0.10, -hd + 0.065, 0.905, hob_at + 0.10, -hd + 0.085, 0.906, pbr('touch', None, color=(0.25, 0.25, 0.25), rough=0.3))
    if sink_at is not None:
        sw, sd = sink_w, d - 0.16
        rim = cube(r, 'sink_rim', sink_at - sw / 2, -hd + 0.08, 0.70, sink_at + sw / 2, -hd + 0.08 + sd, 0.902, M('steel'), 0.004)
        hole = cube(r, 'sink_hole', sink_at - sw / 2 + 0.02, -hd + 0.10, 0.72, sink_at + sw / 2 - 0.02, -hd + 0.06 + sd, 1.0, M('steel'), 0.03)
        for o, c in ((rim, hole), (ct, cube(r, 'ct_hole', sink_at - sw / 2 + 0.005, -hd + 0.085, 0.6, sink_at + sw / 2 - 0.005, -hd + 0.075 + sd, 1.0, M('steel')))):
            m = o.modifiers.new('cut', 'BOOLEAN'); m.object = c; m.operation = 'DIFFERENCE'
        hole.hide_render = True; r.children[-1].hide_render = True
        cyl(r, 'drain', sink_at, -hd + 0.08 + sd / 2, 0.025, 0.721, 0.723, M('chrome'), 24)
        fx, fy = sink_at - sw / 2 + 0.05, hd - 0.05
        cyl(r, 'faucet', fx, fy, 0.022, 0.90, 1.18, M('chrome'), 24, 0.003)
        arm = cyl(r, 'spout', 0, 0, 0.012, 0, 0.24, M('chrome'), 16); arm.rotation_euler[0] = math.radians(90); arm.location = (fx, fy - 0.12, 1.17)
    if fridge: pass
    return r


def fridge(name, cx, cy, w, d, rot=0):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd + 0.03, 0, hw, hd, 1.85, M('steel'), 0.012)
    cube(r, 'door', -hw + 0.003, -hd, 0.02, hw - 0.003, -hd + 0.035, 1.84, M('steel'), 0.01)
    cube(r, 'handle', hw - 0.06, -hd - 0.035, 0.9, hw - 0.04, -hd, 1.7, M('chrome'), 0.006)
    cube(r, 'gap', -hw + 0.01, -hd + 0.034, 1.849, hw - 0.01, -hd + 0.04, 1.851, M('black'))
    return r


# ============================================================== bathroom
def washer(name, cx, cy, w, d, rot=0):
    """washing machine seen from above: plain flat lid, control strip at local -Y (front)"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd, 0, hw, hd, 0.85, M('white'), 0.015)
    cube(r, 'panel', -hw + 0.01, -hd + 0.005, 0.85, hw - 0.01, -hd + 0.10, 0.853, pbr('wpanel', None, color=(0.78, 0.78, 0.80), rough=0.25), 0.004)
    cube(r, 'display', -0.06, -hd + 0.03, 0.853, 0.06, -hd + 0.07, 0.855, M('black_glass'), 0.002)
    cyl(r, 'knob', -hw + 0.10, -hd + 0.05, 0.022, 0.853, 0.865, M('chrome'), 24, 0.003)
    cube(r, 'drawer', hw - 0.18, -hd + 0.015, 0.853, hw - 0.03, -hd + 0.085, 0.854, pbr('wdrawer', None, color=(0.70, 0.70, 0.72), rough=0.3))
    return r


def bathtub(name, cx, cy, w, d, rot=0, tap_side=1):
    """acrylic bathtub along local X, tap at local x = tap_side*(w/2)"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    tub = cube(r, 'tub', -hw, -hd, 0, hw, hd, 0.58, M('ceramic'), 0.03)
    inner = superprism(r, 'inner', 0, 0, hw - 0.08, hd - 0.07, 0.14, 1.2, M('ceramic'), 5.0)
    bvi = inner.modifiers.new('bv', 'BEVEL'); bvi.width = 0.06; bvi.segments = 6; bvi.limit_method = 'ANGLE'
    m = tub.modifiers.new('cut', 'BOOLEAN'); m.object = inner; m.operation = 'DIFFERENCE'; inner.hide_render = True
    m2 = tub.modifiers.new('ss', 'SUBSURF'); m2.levels = 1; m2.render_levels = 2
    cyl(r, 'drain', tap_side * (hw - 0.18), 0, 0.025, 0.121, 0.124, M('chrome'), 24)
    cyl(r, 'tap', tap_side * (hw - 0.03), 0, 0.02, 0.58, 0.75, M('chrome'), 24, 0.003)
    sp = cyl(r, 'spout', 0, 0, 0.012, 0, 0.12, M('chrome'), 16); sp.rotation_euler[1] = math.radians(90); sp.location = (tap_side * (hw - 0.09), 0, 0.74)
    return r


def toilet(name, cx, cy, w, d, rot=0):
    """wall-hung toilet, installation/back at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'install', -hw, hd - 0.14, 0, hw, hd, 1.15, M('white'), 0.01)
    cube(r, 'plate', -0.12, hd - 0.145, 1.0, 0.12, hd - 0.135, 1.14, M('white_matte'), 0.004)
    bowl = cyl(r, 'bowl', 0, hd - 0.14 - 0.27, 0.18, 0.25, 0.40, M('ceramic'), 48, 0.0, 1.0, 1.5)
    bowl.modifiers.new('ss', 'SUBSURF').render_levels = 2
    cyl(r, 'seat', 0, hd - 0.14 - 0.28, 0.172, 0.40, 0.43, M('ceramic'), 48, 0.0, 0.98, 1.45).modifiers.new('ss', 'SUBSURF').render_levels = 2
    cube(r, 'hinge', -0.10, hd - 0.17, 0.40, 0.10, hd - 0.14, 0.44, M('ceramic'), 0.01)
    return r


def washbasin(name, cx, cy, w, d, rot=0):
    """wall-hung basin, wall at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    top = cube(r, 'basin', -hw, -hd, 0.78, hw, hd, 0.86, M('ceramic'), 0.02)
    h = cyl(r, 'hole', 0, -0.02, min(hw, hd) * 0.75, 0.80, 1.0, M('ceramic'), 48, 0, 1.25, 1.0)
    m = top.modifiers.new('cut', 'BOOLEAN'); m.object = h; m.operation = 'DIFFERENCE'; h.hide_render = True
    cyl(r, 'drain', 0, -0.02, 0.018, 0.801, 0.803, M('chrome'), 24)
    cyl(r, 'tap', 0, hd - 0.04, 0.016, 0.86, 1.02, M('chrome'), 24, 0.003)
    sp = cyl(r, 'spout', 0, 0, 0.010, 0, 0.10, M('chrome'), 16); sp.rotation_euler[0] = math.radians(90); sp.location = (0, hd - 0.09, 1.0)
    return r


def tall_cabinet(name, cx, cy, w, d, rot=0, mat='white'):
    return cabinet(name, cx, cy, w, d, rot, 2.0, mat, 1, False)


def door_leaf(name, hx, hy, length, ang, mat='oak'):
    """door leaf hinged at (hx, hy), pointing at angle ang (deg, world)"""
    r = _root(name, hx, hy, ang)
    cube(r, 'leaf', 0, -0.02, 0, length, 0.02, 2.05, M(mat), 0.004)
    cube(r, 'handle', length - 0.12, -0.05, 1.0, length - 0.06, 0.05, 1.02, M('chrome'), 0.004)
    return r


# ============================================================== MODERN COLLECTION (2026: warm minimal / japandi, rounded "cloud" forms,
# boucle & linen, travertine, light oak, brushed brass, handleless fronts). Later definitions override the basic ones above.
def _brushed(name, color):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.32
    b.inputs['Anisotropic'].default_value = 0.6
    _M[name] = m; return m


def MM(k):
    return {
        'travertine': lambda: stone('travertine', (0.86, 0.78, 0.68), (0.74, 0.65, 0.55)),
        'quartz': lambda: stone('quartz', (0.94, 0.92, 0.89), (0.84, 0.81, 0.77)),
        'brass': lambda: _brushed('brass_b', (0.80, 0.62, 0.38)),
        'gunmetal': lambda: _brushed('gunmetal', (0.20, 0.20, 0.21)),
        'sink_steel': lambda: pbr('sink_steel', None, color=(0.58, 0.58, 0.59), rough=0.30, metal=1.0),
        'cream_front': lambda: pbr('cream_front', None, color=(0.86, 0.82, 0.76), rough=0.45),
        'sanitary': lambda: pbr('sanitary', None, color=(0.95, 0.95, 0.94), rough=0.05, coat=0.8),
        'matte_white': lambda: pbr('matte_white_s', None, color=(0.90, 0.89, 0.87), rough=0.3),
    }[k]()


def rounded_slab(root, name, cx, cy, a, b, z0, z1, mat, n=4.0, bevel=0.01, seg=96):
    o = superprism(root, name, cx, cy, a, b, z0, z1, mat, n, seg)
    if bevel:
        bv = o.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 4; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(50)
    _smooth(o); return o


def cut_with(o, cutter):
    m = o.modifiers.new('cut', 'BOOLEAN'); m.object = cutter; m.operation = 'DIFFERENCE'; m.solver = 'EXACT'
    cutter.hide_render = True; cutter.display_type = 'WIRE'
    o.modifiers.move(len(o.modifiers) - 1, 0); return o


def sofa(name, cx, cy, w, d, rot=0, color=(0.86, 0.82, 0.75), kind='boucle', pillows=((0.62, 0.50, 0.38), (0.78, 0.70, 0.60)), seats=None):
    """cloud sofa: low, deep, fat rounded cushions, rounded arms flush with the back"""
    r = _root(name, cx, cy, rot); f = fabric(color, kind); hw, hd = w / 2, d / 2
    arm = min(0.24, w * 0.11); seats = seats or (2 if w < 2.3 else 3)
    cushion(r, 'base', -hw + 0.02, -hd + 0.03, 0.02, hw - 0.02, hd - 0.02, 0.30, f, 0.10, 0.6, 0.003, 1)
    cushion(r, 'back', -hw + 0.02, hd - 0.26, 0.26, hw - 0.02, hd, 0.74, f, 0.30, 0.8, 0.005, 2)
    for i, sx in enumerate((-1, 1)):
        x0, x1 = (hw - arm, hw) if sx > 0 else (-hw, -hw + arm)
        cushion(r, f'arm{i}', x0, -hd, 0.18, x1, hd, 0.64, f, 0.35, 0.9, 0.005, 3 + i)
    sw = (w - 2 * arm) / seats
    for i in range(seats):
        x0 = -hw + arm + i * sw
        cushion(r, f'seat{i}', x0 + 0.005, -hd + 0.02, 0.28, x0 + sw - 0.005, hd - 0.22, 0.50, f, 0.45, 0.9, 0.007, 10 + i)
    for i, (px, pa, pc) in enumerate(((-hw + arm + 0.28, 12, pillows[0]), (hw - arm - 0.28, -10, pillows[1]))):
        pillow(r, f'pil{i}', px, hd - 0.36, 0.48, 0.50, 0.16, 0.46, pa, fabric(pc, 'velvet' if i else 'linen'), i)
    return r


def armchair(name, cx, cy, w, d, rot=0, color=(0.86, 0.82, 0.75), kind='boucle'):
    """rounded lounge chair: wrap-around back + arms as fat cushions, deep seat; back at local +Y"""
    r = _root(name, cx, cy, rot); f = fabric(color, kind); hw, hd = w / 2, d / 2
    cushion(r, 'base', -hw + 0.03, -hd + 0.03, 0.04, hw - 0.03, hd - 0.03, 0.30, f, 0.15, 0.8, 0.003, 4)
    cushion(r, 'back', -hw, hd - 0.22, 0.20, hw, hd, 0.72, f, 0.40, 0.95, 0.005, 5)
    for i, sx in enumerate((-1, 1)):
        cushion(r, f'arm{i}', (hw - 0.17) if sx > 0 else -hw, -hd + 0.02, 0.20, hw if sx > 0 else (-hw + 0.17), hd - 0.06, 0.60, f, 0.45, 0.95, 0.005, 12 + i)
    cushion(r, 'seat', -hw + 0.15, -hd + 0.04, 0.28, hw - 0.15, hd - 0.20, 0.47, f, 0.50, 0.95, 0.006, 6)
    pillow(r, 'pil', 0, hd - 0.28, 0.46, 0.40, 0.14, 0.34, 4, fabric((0.62, 0.50, 0.38), 'velvet'), 3)
    return r


def coffee_table(name, cx, cy, w, d, rot=0, round_=False, mat='travertine', decor=True):
    """oval / round travertine coffee table on a solid pedestal"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; m = MM('travertine') if mat == 'travertine' else M(mat)
    n = 2.0 if round_ else 2.4
    rounded_slab(r, 'top', 0, 0, hw, hd, 0.34, 0.40, m, n, 0.012)
    rounded_slab(r, 'pedestal', 0, 0, hw * 0.55, hd * 0.55, 0.0, 0.34, m, n, 0.008)
    if decor:
        cyl(r, 'tray', hw * 0.25, 0, min(0.13, hd * 0.6), 0.40, 0.415, MM('brass'), 48, 0.003)
        cyl(r, 'vase', hw * 0.25, 0.03, 0.045, 0.415, 0.60, pbr('vase_clay', None, color=(0.62, 0.42, 0.30), rough=0.7), 32, 0.01)
        cube(r, 'book1', -hw * 0.45 - 0.11, -0.08, 0.40, -hw * 0.45 + 0.11, 0.08, 0.425, fabric((0.80, 0.76, 0.70)), 0.004)
        cube(r, 'book2', -hw * 0.45 - 0.09, -0.06, 0.425, -hw * 0.45 + 0.09, 0.07, 0.445, fabric((0.45, 0.36, 0.28)), 0.004)
    return r


def dining_table(name, cx, cy, w, d, rot=0, mat='oak', decor=True):
    """oval light-oak dining table on two slab legs"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; m = M(mat)
    rounded_slab(r, 'top', 0, 0, hw, hd, 0.72, 0.755, m, 2.3, 0.008)
    for sx in (-1, 1): rounded_slab(r, 'leg', sx * hw * 0.55, 0, 0.05, hd * 0.55, 0.0, 0.72, m, 4, 0.01)
    if decor:
        cyl(r, 'bowl', -0.12, 0, 0.13, 0.755, 0.80, MM('travertine'), 48, 0.02)
        cyl(r, 'vase', 0.18, 0.02, 0.05, 0.755, 0.98, pbr('vase_glass', None, color=(0.85, 0.80, 0.72), rough=0.2), 32, 0.01)
        plant_small(r, 0.18, 0.02, 0.98, 0.16)
    return r


def chair(name, cx, cy, w, d, rot=0, color=(0.80, 0.74, 0.66)):
    """curved shell dining chair in boucle on thin oak legs, back at local +Y"""
    r = _root(name, cx, cy, rot); f = fabric(color, 'boucle'); hw, hd = w / 2, d / 2
    cushion(r, 'seat', -hw, -hd, 0.42, hw, hd - 0.02, 0.49, f, 0.30, 0.8, 0.003, 7)
    cushion(r, 'back', -hw + 0.01, hd - 0.09, 0.46, hw - 0.01, hd, 0.82, f, 0.40, 0.95, 0.003, 8)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(r, 'leg', sx * (hw - 0.05), sy * (hd - 0.06), 0.013, 0, 0.43, M('oak'), 12)
    return r


def bed(name, cx, cy, w, d, rot=0, linen=(0.90, 0.87, 0.82), throw=(0.66, 0.55, 0.44), head=(0.82, 0.76, 0.68), sim=True):
    """upholstered bed with a soft rounded frame and a wide channel headboard, crumpled linen, throw, pillows; headboard at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; hf = fabric(head, 'boucle')
    frame = cushion(r, 'frame', -hw - 0.04, -hd - 0.04, 0.05, hw + 0.04, hd - 0.04, 0.34, hf, 0.12, 0.7, 0.003, 29)
    nch = 7; cw = (w + 0.30) / nch
    for i in range(nch):
        x0 = -hw - 0.15 + i * cw
        cushion(r, f'head{i}', x0 + 0.004, hd - 0.12, 0.30, x0 + cw - 0.004, hd, 1.15, hf, 0.35, 0.7, 0.003, 70 + i)
    mat = cushion(r, 'mattress', -hw + 0.02, -hd + 0.02, 0.30, hw - 0.02, hd - 0.12, 0.54, fabric(linen), 0.08, 0.3, 0.0, 31)
    lin = fabric(linen); thr = fabric(throw, 'velvet')
    if sim:
        duv = cloth(r, 'duvet', -hw - 0.12, -hd - 0.10, hw + 0.12, hd - 0.55, 0.72, lin, (mat, frame), frames=45, n=70, thick=0.04, mass=0.5, stiff=5, bend=0.2)
        t = bpy.data.textures.new('fold', 'WOOD'); t.wood_type = 'BANDNOISE'; t.noise_scale = 0.35; t.turbulence = 8
        dd = duv.modifiers.new('fold', 'DISPLACE'); dd.texture = t; dd.strength = 0.025
        cloth(r, 'turn', -hw - 0.08, hd - 0.78, hw + 0.08, hd - 0.50, 0.80, lin, (mat, duv), frames=30, n=44, thick=0.035, mass=0.3, stiff=5, bend=0.2)
        cloth(r, 'throw', -hw - 0.16, -hd * 0.70, hw + 0.16, -hd * 0.70 + 0.50, 0.90, thr, (mat, duv, frame), frames=45, n=56, thick=0.014, mass=0.35, stiff=10, bend=0.6)
    pw = (w - 0.12) / 2
    for i, sx in enumerate((-1, 1)):
        px = sx * (pw / 2 + 0.02)
        pillow(r, f'pillow{i}', px, hd - 0.30, 0.52, pw - 0.03, 0.50, 0.22, rnd.uniform(-4, 4), lin, 40 + i)
        pillow(r, f'pillowb{i}', px * 0.95, hd - 0.42, 0.62, pw - 0.10, 0.18, 0.44, rnd.uniform(-4, 4), lin, 44 + i)
        pillow(r, f'deco{i}', px * 0.7, hd - 0.62, 0.58, 0.40, 0.15, 0.36, rnd.uniform(-10, 10), thr, 50 + i)
    return r


def nightstand(name, cx, cy, w, d, rot=0, lamp=True, light=True):
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    rounded_slab(r, 'body', 0, 0, hw, hd, 0.0, 0.50, M('oak'), 4.5, 0.012)
    cube(r, 'gap', -hw + 0.02, -hd - 0.001, 0.25, hw - 0.02, -hd + 0.004, 0.254, M('black'))
    if lamp:
        cyl(r, 'base', 0.02, 0.03, 0.07, 0.50, 0.60, pbr('lamp_base', None, color=(0.70, 0.55, 0.42), rough=0.6), 48, 0.03)
        o = cushion(r, 'shade', 0.02 - 0.11, 0.03 - 0.11, 0.60, 0.02 + 0.11, 0.03 + 0.11, 0.80, M('shade'), 0.5, 0.95, 0.0, 77)
        o.modifiers.new('cast', 'CAST').factor = 1.0
        if light:
            l = bpy.data.lights.new(name + '_l', 'POINT'); l.energy = 40; l.color = (1.0, 0.70, 0.42); l.shadow_soft_size = 0.15
            lo = bpy.data.objects.new(name + '_l', l); bpy.context.scene.collection.objects.link(lo); lo.parent = r; lo.location = (0.02, 0.03, 0.74)
        cube(r, 'book', -hw + 0.04, -hd + 0.05, 0.50, -hw + 0.21, -hd + 0.20, 0.53, fabric((0.48, 0.42, 0.36)), 0.004)
    return r


SHIRT = [(0.93, 0.92, 0.89), (0.62, 0.71, 0.82), (0.86, 0.79, 0.68), (0.16, 0.18, 0.26), (0.52, 0.40, 0.30), (0.74, 0.74, 0.72),
         (0.38, 0.42, 0.36), (0.80, 0.70, 0.62), (0.26, 0.22, 0.20), (0.90, 0.86, 0.80), (0.55, 0.32, 0.24), (0.44, 0.52, 0.62)]


def _garment(root, name, x, y, z_top, width, length, mat, seed):
    """garment on a hanger seen from above: soft shoulder 'pillow' + body falling down with gentle folds (thin in X, wide in Y)"""
    rr = random.Random(seed)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    n = 20; ring = []
    for i in range(n):
        t = i / (n - 1) * 2 - 1; ring.append((t, 1.0))
    prof = [(t * width / 2, 0.012 + 0.030 * (1 - t * t) ** 0.5) for t, _ in ring]
    loop = [(th, px) for px, th in prof] + [(-th, px) for px, th in reversed(prof)]
    layers = 10; vs = []
    for k in range(layers + 1):
        f = k / layers; zz = -f * length - 0.06 * (f ** 0.5)
        drop = 1.0 - 0.10 * math.exp(-((f - 0.05) / 0.05) ** 2)          # shoulder slope
        sw = (0.92 + 0.14 * f) * drop
        vs.append([bm.verts.new((tx * (1 + 0.8 * f) + 0.008 * math.sin(py * 30 + seed * 0.7 + k * 0.9) * f, py * sw, zz)) for tx, py in loop])
    m = len(loop)
    for k in range(layers):
        for i in range(m): bm.faces.new((vs[k][i], vs[k][(i + 1) % m], vs[k + 1][(i + 1) % m], vs[k + 1][i]))
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = (x, y, z_top)
    o.rotation_euler[2] = math.radians(rr.uniform(-4, 4)); o.rotation_euler[1] = math.radians(rr.uniform(-2, 2))
    s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = 2
    o.data.materials.append(mat); _smooth(o); return _link(o, root)


def wardrobe_open(name, cx, cy, w, d, rot=0, h=2.2, fill=0.8, short=False, led=True):
    """open wardrobe: light-oak carcass, brushed brass rail, wooden hangers, mixed garments across the rail; back at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; t = 0.022; m = M('oak_light')
    cube(r, 'back', -hw, hd - 0.012, 0, hw, hd, h, m)
    for sx in (-1, 1): cube(r, 'side', sx * hw - (t if sx > 0 else 0), -hd, 0, sx * hw + (0 if sx > 0 else t), hd, h, m, 0.003)
    cube(r, 'bottom', -hw, -hd, 0, hw, hd, 0.06, m, 0.002)
    nsec = max(1, round(w / 0.9))
    for i in range(1, nsec):
        x = -hw + i * w / nsec; cube(r, 'div', x - t / 2, -hd, 0, x + t / 2, hd, h, m, 0.003)
    for i in range(nsec):
        x0 = -hw + i * w / nsec + t; x1 = -hw + (i + 1) * w / nsec - t
        rail = cyl(r, 'rail', 0, 0, 0.010, -(x1 - x0) / 2, (x1 - x0) / 2, MM('brass'), 16)
        rail.rotation_euler[1] = math.radians(90); rail.location = ((x0 + x1) / 2, 0, 1.86)
        if led:
            for xx in (x0 + 0.004, x1 - 0.004): cube(r, 'led', xx - 0.004, -hd + 0.03, 0.9, xx + 0.004, hd - 0.03, 2.0, M('led'))
        nn = int((x1 - x0) * fill / 0.06)
        xs = [x0 + 0.05 + k * (x1 - x0 - 0.10) / max(1, nn - 1) for k in range(nn)]
        for k, x in enumerate(xs):
            c = SHIRT[(k * 5 + i * 7 + int(abs(cx) * 31)) % len(SHIRT)]
            kind = 'velvet' if (k + i) % 4 == 0 else 'linen'
            ln = 0.55 if short else rnd.uniform(0.70, 1.05)
            gw = min(d - 0.08, 0.46) * rnd.uniform(0.92, 1.0)
            _garment(r, 'g', x + rnd.uniform(-0.006, 0.006), 0, 1.835, gw, ln, fabric(c, kind), int(x * 1000) + k * 13)
            hg = cyl(r, 'hanger', 0, 0, 0.008, -gw * 0.42, gw * 0.42, M('walnut'), 8); hg.rotation_euler[0] = math.radians(90); hg.location = (x, 0, 1.845)
            cyl(r, 'hook', x, 0, 0.0035, 1.845, 1.875, MM('brass'), 8)
    return r


def kitchen_run(name, cx, cy, w, d, rot=0, sink_at=None, hob_at=None, hob_w=0.6, sink_w=0.60, fridge=False):
    """handleless kitchen: warm-cream fronts with shadow gaps, light quartzite top, flush hob, undermount steel sink, gunmetal arc faucet"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'base', -hw, -hd + 0.03, 0.10, hw, hd, 0.85, MM('cream_front'), 0.003)
    cube(r, 'plinth', -hw, -hd + 0.08, 0, hw, hd, 0.10, M('black'))
    cube(r, 'jgroove', -hw, -hd + 0.025, 0.80, hw, -hd + 0.06, 0.83, M('black'))
    ct = cube(r, 'counter', -hw, -hd, 0.85, hw, hd, 0.89, MM('quartz'), 0.003)
    nd = max(1, round(w / 0.6))
    for i in range(1, nd):
        x = -hw + i * w / nd; cube(r, 'gap', x - 0.0015, -hd + 0.025, 0.11, x + 0.0015, -hd + 0.032, 0.80, M('black'))
    if hob_at is not None:
        cube(r, 'hob', hob_at - hob_w / 2, -hd + 0.05, 0.885, hob_at + hob_w / 2, hd - 0.05, 0.893, M('black_glass'), 0.002)
        zm = pbr('zone2', None, color=(0.10, 0.10, 0.10), rough=0.35)
        for (zx, zy, zr) in ((-0.15, 0.11, 0.10), (0.15, 0.11, 0.085), (-0.15, -0.12, 0.085), (0.15, -0.12, 0.10)):
            ring_o = cyl(r, 'zone', hob_at + zx * hob_w / 0.6, zy * (d - 0.10) / 0.5, zr, 0.8930, 0.8935, zm, 64)
            inner = cyl(r, 'zone_i', hob_at + zx * hob_w / 0.6, zy * (d - 0.10) / 0.5, zr - 0.004, 0.892, 0.90, zm, 64); cut_with(ring_o, inner)
        cube(r, 'slider', hob_at - 0.12, -hd + 0.065, 0.8935, hob_at + 0.12, -hd + 0.075, 0.894, pbr('touch2', None, color=(0.30, 0.30, 0.30), rough=0.3))
    if sink_at is not None:
        sd = d - 0.20; cyy = -hd + 0.09 + sd / 2
        rim = rounded_slab(r, 'sink', sink_at, cyy, sink_w / 2, sd / 2, 0.66, 0.875, MM('sink_steel'), 8.0, 0.0)
        hole = rounded_slab(r, 'sink_hole', sink_at, cyy, sink_w / 2 - 0.015, sd / 2 - 0.015, 0.68, 1.0, MM('sink_steel'), 8.0, 0.0)
        cut_with(rim, hole)
        cth = rounded_slab(r, 'ct_hole', sink_at, cyy, sink_w / 2 - 0.012, sd / 2 - 0.012, 0.6, 1.0, MM('quartz'), 8.0, 0.0); cut_with(ct, cth)
        cyl(r, 'drain', sink_at + sink_w * 0.25, cyy, 0.03, 0.681, 0.683, MM('sink_steel'), 32)
        fx, fy = sink_at, hd - 0.06
        cyl(r, 'faucet_b', fx, fy, 0.025, 0.89, 0.92, MM('gunmetal'), 32, 0.004)
        cyl(r, 'faucet', fx, fy, 0.014, 0.92, 1.22, MM('gunmetal'), 24)
        arc = bpy.data.curves.new('arc', 'CURVE'); arc.dimensions = '3D'; arc.bevel_depth = 0.013; arc.bevel_resolution = 4
        sp = arc.splines.new('BEZIER'); sp.bezier_points.add(1)
        sp.bezier_points[0].co = (0, 0, 1.22); sp.bezier_points[0].handle_left = (0, 0.05, 1.10); sp.bezier_points[0].handle_right = (0, -0.0, 1.34)
        sp.bezier_points[1].co = (0, -0.22, 1.10); sp.bezier_points[1].handle_left = (0, -0.22, 1.30); sp.bezier_points[1].handle_right = (0, -0.22, 1.00)
        ao = bpy.data.objects.new('spout', arc); bpy.context.scene.collection.objects.link(ao); ao.location = (fx, fy, 0); ao.data.materials.append(MM('gunmetal')); _link(ao, r)
        cyl(r, 'lever', fx + 0.035, fy, 0.006, 1.0, 1.08, MM('gunmetal'), 12)
        cyl(r, 'soap', fx + 0.22, fy - 0.01, 0.03, 0.89, 1.06, pbr('soap', None, color=(0.75, 0.70, 0.62), rough=0.4), 32, 0.008)
        cube(r, 'board', -hw + 0.08, -hd + 0.10, 0.89, -hw + 0.42, -hd + 0.36, 0.91, M('oak'), 0.006)
    return r


def fridge(name, cx, cy, w, d, rot=0):
    """freestanding fridge, satin stainless, recessed handle groove"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd + 0.03, 0, hw, hd, 1.86, MM('sink_steel'), 0.015)
    cube(r, 'door', -hw + 0.003, -hd, 0.02, hw - 0.003, -hd + 0.04, 1.85, MM('sink_steel'), 0.012)
    cube(r, 'groove', -hw + 0.01, -hd - 0.002, 1.80, hw - 0.01, -hd + 0.02, 1.83, M('black'))
    cube(r, 'gap', -hw + 0.01, -hd + 0.038, 1.859, hw - 0.01, -hd + 0.044, 1.861, M('black'))
    return r


def washer(name, cx, cy, w, d, rot=0):
    """front-loader seen from above: plain flat white lid, control strip with display and dial at the front edge"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'body', -hw, -hd, 0, hw, hd, 0.85, MM('matte_white'), 0.018)
    cube(r, 'strip', -hw + 0.012, -hd + 0.004, 0.85, hw - 0.012, -hd + 0.085, 0.852, pbr('wstrip', None, color=(0.93, 0.93, 0.93), rough=0.15, coat=0.5), 0.004)
    cube(r, 'display', -0.05, -hd + 0.025, 0.852, 0.07, -hd + 0.06, 0.8535, M('black_glass'), 0.002)
    cyl(r, 'dial', -hw + 0.11, -hd + 0.045, 0.025, 0.852, 0.866, MM('sink_steel'), 32, 0.004)
    cube(r, 'drawer', hw - 0.20, -hd + 0.012, 0.852, hw - 0.04, -hd + 0.078, 0.853, pbr('wdrawer2', None, color=(0.88, 0.88, 0.88), rough=0.3))
    return r


def bathtub(name, cx, cy, w, d, rot=0, tap_side=1):
    """built-in rectangular tub: slim rim, soft deep basin, brushed brass deck tap"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    tub = cube(r, 'tub', -hw, -hd, 0, hw, hd, 0.58, MM('sanitary'), 0.012)
    inner = rounded_slab(r, 'basin', -tap_side * 0.02, 0, hw - 0.07, hd - 0.06, 0.10, 1.2, MM('sanitary'), 3.2, 0.0)
    bv = inner.modifiers.new('bv', 'BEVEL'); bv.width = 0.08; bv.segments = 8; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(60)
    cut_with(tub, inner)
    cyl(r, 'drain', tap_side * (hw - 0.22), 0, 0.03, 0.101, 0.104, MM('brass'), 32)
    cyl(r, 'tap_b', tap_side * (hw - 0.035), 0, 0.022, 0.58, 0.60, MM('brass'), 32)
    sp = cyl(r, 'spout', 0, 0, 0.011, 0, 0.14, MM('brass'), 16); sp.rotation_euler[1] = math.radians(90); sp.location = (tap_side * (hw - 0.10), 0, 0.68)
    cyl(r, 'tap', tap_side * (hw - 0.035), 0, 0.012, 0.60, 0.69, MM('brass'), 16)
    for dy in (-0.07, 0.07): cyl(r, 'knob', tap_side * (hw - 0.035), dy, 0.016, 0.58, 0.63, MM('brass'), 24, 0.003)
    return r


def toilet(name, cx, cy, w, d, rot=0):
    """rimless wall-hung toilet, compact rounded-rectangle bowl, slim seat, brushed brass flush plate on the installation; wall at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'install', -hw, hd - 0.12, 0, hw, hd, 1.10, MM('matte_white'), 0.01)
    rounded_slab(r, 'plate', 0, hd - 0.122, 0.11, 0.004, 0.96, 1.08, MM('brass'), 6, 0.0)
    bl = 0.54; bwid = min(0.36, w * 0.95)
    bowl = rounded_slab(r, 'bowl', 0, hd - 0.12 - bl / 2, bwid / 2, bl / 2, 0.20, 0.39, MM('sanitary'), 2.6, 0.0)
    s = bowl.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = 2
    lid = rounded_slab(r, 'lid', 0, hd - 0.12 - bl / 2 - 0.005, bwid / 2 - 0.004, bl / 2 - 0.01, 0.39, 0.42, MM('sanitary'), 2.6, 0.01)
    cube(r, 'lidline', -bwid / 2 + 0.03, hd - 0.15, 0.419, bwid / 2 - 0.03, hd - 0.145, 0.421, pbr('lidline', None, color=(0.75, 0.75, 0.75), rough=0.3))
    return r


def washbasin(name, cx, cy, w, d, rot=0):
    """floating light-oak vanity with an integrated soft rectangular basin and a wall-mounted brushed brass spout; wall at local +Y"""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2
    cube(r, 'vanity', -hw, -hd + 0.02, 0.42, hw, hd, 0.68, M('oak_light'), 0.006)
    top = cube(r, 'top', -hw, -hd, 0.68, hw, hd, 0.84, MM('sanitary'), 0.008)
    bas = rounded_slab(r, 'basin', 0, -0.01, hw * 0.72, hd * 0.62, 0.74, 1.0, MM('sanitary'), 3.0, 0.0)
    bv = bas.modifiers.new('bv', 'BEVEL'); bv.width = 0.03; bv.segments = 6; bv.limit_method = 'ANGLE'
    cut_with(top, bas)
    cyl(r, 'drain', 0, -0.01, 0.018, 0.741, 0.743, MM('brass'), 24)
    sp = cyl(r, 'spout', 0, 0, 0.010, 0, 0.16, MM('brass'), 16); sp.rotation_euler[0] = math.radians(90); sp.location = (0, hd - 0.08, 1.02)
    cyl(r, 'rose', 0, hd - 0.003, 0.03, 1.0, 1.04, MM('brass'), 24).rotation_euler[0] = math.radians(90)
    cyl(r, 'dispenser', hw - 0.08, hd - 0.06, 0.028, 0.84, 1.00, pbr('disp', None, color=(0.55, 0.45, 0.36), rough=0.5), 32, 0.008)
    return r


def pouf(name, cx, cy, w, d, rot=0, color=(0.88, 0.84, 0.77), round_=True):
    r = _root(name, cx, cy, rot); f = fabric(color, 'boucle')
    o = cushion(r, 'pouf', -w / 2, -d / 2, 0.0, w / 2, d / 2, 0.40, f, 0.35, 0.95, 0.004, 9)
    if round_: o.modifiers.new('cast', 'CAST').factor = 0.9
    return r


# ============================================================== WARDROBE v3: detailed garments, folded stacks, shoes, configurable sections
def lin(c):
    """palette colours below are written in sRGB (as a designer picks them) -> linear for the shader"""
    return tuple(x ** 2.2 for x in c)


def _bm_obj(root, name, bm, mat, sub=2, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if sub:
        s = o.modifiers.new('ss', 'SUBSURF'); s.levels = 1; s.render_levels = sub
    o.data.materials.append(mat)
    if smooth: _smooth(o)
    return _link(o, root)


def _tube(bm, pts, radii, seg=12, flat=1.0):
    """tube along a polyline of 3D points (vertical-ish), elliptical section (flat = x/y ratio)"""
    rings = []
    for k, (p, r) in enumerate(zip(pts, radii)):
        p = Vector(p)
        d = (Vector(pts[min(k + 1, len(pts) - 1)]) - Vector(pts[max(k - 1, 0)])).normalized()
        a = d.orthogonal().normalized(); b = d.cross(a).normalized()
        rings.append([bm.verts.new(p + a * math.cos(2 * math.pi * i / seg) * r * flat + b * math.sin(2 * math.pi * i / seg) * r) for i in range(seg)])
    for k in range(len(rings) - 1):
        for i in range(seg): bm.faces.new((rings[k][i], rings[k][(i + 1) % seg], rings[k + 1][(i + 1) % seg], rings[k + 1][i]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])


def _torso(bm, width, length, thick, shoulder_drop, flare=0.06, hem_wave=0.006, seed=0, vneck=0.0):
    """hanging garment body: lofted rounded-rect sections; garment plane = local YZ, thickness along X"""
    rr = random.Random(seed); nU = 28; nV = 14; rings = []
    for k in range(nV + 1):
        f = k / nV
        z = -f * length
        hw = width / 2 * (1 + flare * f) * (0.94 + 0.06 * min(1, f * 6))
        th = thick * (0.85 + 0.15 * min(1, f * 5)) * (1 - 0.2 * f)
        ring = []
        for i in range(nU):
            t = 2 * math.pi * i / nU; c, s = math.cos(t), math.sin(t)
            y = hw * math.copysign(abs(c) ** 0.35, c); x = th / 2 * math.copysign(abs(s) ** 0.8, s)
            zz = z
            if k == 0: zz -= shoulder_drop * (abs(y) / (width / 2)) ** 1.5           # sloped shoulders
            if k == nV: zz += hem_wave * math.sin(y * 40 + seed)
            x += 0.004 * math.sin(y * 25 + k + seed) * f                                 # soft vertical folds
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    for k in range(nV):
        for i in range(nU): bm.faces.new((rings[k][i], rings[k][(i + 1) % nU], rings[k + 1][(i + 1) % nU], rings[k + 1][i]))
    top_c = bm.verts.new((0, 0, 0.012)); bot_c = bm.verts.new((0, 0, -length))     # domed shoulders, closed hem (fans -> clean subsurf)
    for i in range(nU):
        bm.faces.new((rings[0][(i + 1) % nU], rings[0][i], top_c)); bm.faces.new((rings[-1][i], rings[-1][(i + 1) % nU], bot_c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def hanger(root, x, z, width, mat=None):
    """wooden hanger (curved bar following the shoulders) + brass hook"""
    mat = mat or M('walnut')
    cu = bpy.data.curves.new('hg', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.007; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    for p, (yy, zz) in zip(sp.bezier_points, ((-width / 2, z - 0.045), (0, z), (width / 2, z - 0.045))):
        p.co = (0, yy, zz); p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('hanger', cu); bpy.context.scene.collection.objects.link(o); o.location = (x, 0, 0); o.data.materials.append(mat); _link(o, root)
    o.visible_camera = not getattr(bpy.context.scene, '_hide_hangers', False)
    hk = bpy.data.curves.new('hook', 'CURVE'); hk.dimensions = '3D'; hk.bevel_depth = 0.0025
    s2 = hk.splines.new('BEZIER'); s2.bezier_points.add(2)
    for p, (yy, zz) in zip(s2.bezier_points, ((0, z), (0, z + 0.075), (0.018, z + 0.09))):
        p.co = (0, yy, zz); p.handle_left_type = p.handle_right_type = 'AUTO'
    o2 = bpy.data.objects.new('hook', hk); bpy.context.scene.collection.objects.link(o2); o2.location = (x, 0, 0); o2.data.materials.append(MM('brass')); _link(o2, root)


def garment(root, kind, x, z_top, color, seed=0, width=0.44):
    """kind: shirt | tee | knit | jacket | dress | trousers. Plane YZ (across the rail), front faces -X."""
    rr = random.Random(seed); color = lin(color)
    if kind == 'trousers':
        bm = bmesh.new(); L = 0.42
        for side in (-1, 1):                                                   # folded over the hanger bar
            _tube(bm, [(side * 0.012, 0, z_top - 0.05 - f * L) for f in (0, .3, .6, 1)], [0.012] * 4, 8)
        o = _bm_obj(root, 'trousers', bm, fabric(color, 'cotton'), 2)
        for side in (-1, 1):
            leg = bmesh.new(); _torso(leg, 0.30, L, 0.022, 0.0, 0.0, 0.0, seed)
            lo = _bm_obj(root, 'leg', leg, fabric(color, 'cotton'), 2); lo.location = (x + side * 0.012, 0, z_top - 0.05)
        o.location = (x, 0, 0); hanger(root, x, z_top, 0.34); return
    fab = fabric(color, 'wool' if kind == 'knit' else 'cotton')
    th = {'shirt': 0.055, 'tee': 0.05, 'knit': 0.085, 'jacket': 0.10, 'dress': 0.05}[kind]
    L = {'shirt': 0.78, 'tee': 0.66, 'knit': 0.62, 'jacket': 0.80, 'dress': 1.05}[kind] * rr.uniform(0.95, 1.05)
    fl = {'shirt': 0.04, 'tee': 0.02, 'knit': 0.0, 'jacket': 0.03, 'dress': 0.35}[kind]
    w = width * {'shirt': 1.0, 'tee': 0.98, 'knit': 1.02, 'jacket': 1.06, 'dress': 0.90}[kind]
    bm = bmesh.new(); _torso(bm, w, L, th, 0.05, fl, 0.006, seed)
    body = _bm_obj(root, kind, bm, fab, 2); body.location = (x, 0, z_top - 0.02)
    if kind != 'dress':                                                        # sleeves hanging at the sides, slightly to the front
        sl = {'shirt': 0.60, 'tee': 0.20, 'knit': 0.58, 'jacket': 0.62}[kind]
        for side in (-1, 1):
            sb = bmesh.new(); y0 = side * (w / 2 - 0.075)
            pts = [(-th * 0.05, y0, -0.09), (-th * 0.30, y0 + side * 0.01, -0.09 - sl * 0.35), (-th * 0.45, y0 + side * 0.005, -0.09 - sl * 0.75), (-th * 0.42, y0, -0.09 - sl)]
            r0 = 0.038 if kind != 'jacket' else 0.048
            _tube(sb, pts, [r0, r0 * 0.9, r0 * 0.75, r0 * 0.7], 12, 0.7)
            so = _bm_obj(root, 'sleeve', sb, fab, 2); so.location = (x, 0, z_top - 0.02)
    # neck / collar
    if kind == 'shirt':
        cb = bmesh.new(); bmesh.ops.create_cone(cb, cap_ends=False, segments=24, radius1=0.042, radius2=0.046, depth=0.03)
        co = _bm_obj(root, 'collar', cb, fab, 2); co.location = (x - th * 0.1, 0, z_top - 0.005); co.scale = (0.55, 1, 1)
        so = co.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.006
        ins = cyl(root, 'neck_in', 0, 0, 0.05, -0.002, 0.0, fabric(tuple(c * 0.55 for c in color)), 24); ins.scale = (0.5, 1, 1); ins.location = (x - th * 0.1, 0, z_top - 0.012)
        for side in (-1, 1):
            cp = bmesh.new(); vv = [cp.verts.new(p) for p in ((0, side * 0.012, 0), (0, side * 0.045, 0.004), (-0.03, side * 0.02, -0.035))]; cp.faces.new(vv)
            cpo = _bm_obj(root, 'collar_pt', cp, fab, 1); cpo.location = (x - th * 0.25, 0, z_top - 0.01); cpo.modifiers.new('sol', 'SOLIDIFY').thickness = 0.004
        pl = bmesh.new(); bmesh.ops.create_cube(pl, size=1)
        po = _bm_obj(root, 'placket', pl, fab, 0); po.scale = (0.004, 0.026, L * 0.85); po.location = (x - th / 2 - 0.001, 0, z_top - 0.06 - L * 0.42)
        for k in range(6):
            bt = cyl(root, 'btn', 0, 0, 0.0055, -0.0015, 0.0015, M('white'), 12); bt.rotation_euler[1] = math.radians(90); bt.location = (x - th / 2 - 0.004, 0, z_top - 0.10 - k * L * 0.14)
    elif kind in ('tee', 'knit'):
        tb = bmesh.new(); bmesh.ops.create_cone(tb, cap_ends=False, segments=24, radius1=0.045, radius2=0.047, depth=0.014)
        to = _bm_obj(root, 'neck', tb, fabric(tuple(c * 0.85 for c in color), 'wool' if kind == 'knit' else 'cotton'), 2)
        to.location = (x, 0, z_top - 0.01); to.scale = (0.6, 1, 1); to.modifiers.new('sol', 'SOLIDIFY').thickness = 0.008
        if kind == 'knit':                                                     # ribbed hem + cuffs
            rb = bmesh.new(); _tube(rb, [(0, -w / 2, z_top - 0.02 - L + 0.03), (0, w / 2, z_top - 0.02 - L + 0.03)], [0.018, 0.018], 12, th / 0.036)
            _bm_obj(root, 'rib', rb, fabric(tuple(c * 0.88 for c in color), 'wool'), 2).location = (x, 0, 0)
    elif kind == 'jacket':                                                     # lapels (V) + pocket flaps
        for side in (-1, 1):
            lb = bmesh.new()
            v = [lb.verts.new(p) for p in ((0, side * 0.02, 0), (0, side * 0.10, 0), (0, side * 0.03, -0.30))]
            lb.faces.new(v)
            lo = _bm_obj(root, 'lapel', lb, fabric(tuple(c * 0.8 for c in color), 'cotton'), 1); lo.location = (x - th * 0.42, 0, z_top - 0.03)
            lo.modifiers.new('sol', 'SOLIDIFY').thickness = 0.006

    hanger(root, x, z_top - 0.035, min(0.40, w * 0.85))


def folded_stack(root, x0, x1, y0, y1, z, n, colors, seed=0):
    """stack of folded sweaters/tees: soft slabs with a fold roll at the front edge, slight offsets"""
    rr = random.Random(seed); h = 0.045
    for k in range(n):
        c = lin(colors[(k + seed) % len(colors)]); f = fabric(c, 'wool' if k % 2 == 0 else 'cotton')
        dx, dy = rr.uniform(-0.01, 0.01), rr.uniform(-0.008, 0.008)
        cushion(root, 'fold', x0 + dx, y0 + dy, z + k * h, x1 + dx, y1 + dy, z + (k + 1) * h - 0.003, f, 0.25, 0.7, 0.002, seed * 10 + k)
        roll = cyl(root, 'roll', 0, 0, h * 0.45, -(x1 - x0) / 2 + 0.01, (x1 - x0) / 2 - 0.01, f, 16)
        roll.rotation_euler[1] = math.radians(90); roll.location = ((x0 + x1) / 2 + dx, y0 + dy + 0.01, z + k * h + h * 0.45)


def shoe_pair(root, x, y, z, color, kind='sneaker', ang=0, seed=0):
    """pair of shoes on a shelf, toes to the front (-Y): egg-shaped sole, tapered upper with opening and heel"""
    for side in (-1, 1):
        sx = x + side * 0.058; rot = math.radians(ang + side * 4)
        e = bpy.data.objects.new('shoe', None); bpy.context.scene.collection.objects.link(e); _link(e, root); e.location = (sx, y, z); e.rotation_euler[2] = rot
        sole_m = MM('matte_white') if kind == 'sneaker' else pbr('sole_dark', None, color=(0.08, 0.07, 0.06), rough=0.6)
        bm = bmesh.new(); seg = 40; pts = []
        for i in range(seg):
            t = 2 * math.pi * i / seg; yy = 0.135 * math.sin(t); ww = 0.046 * (1 - 0.25 * (yy / 0.135)) ** 1.0
            pts.append((ww * math.cos(t), yy))
        def slab(z0, z1, sc_, name, mat, sub):
            b = bmesh.new(); lo = [b.verts.new((px * sc_, py * sc_, z0)) for px, py in pts]; hi = [b.verts.new((px * sc_, py * sc_, z1)) for px, py in pts]
            b.faces.new(lo[::-1]); b.faces.new(hi)
            for i in range(seg): b.faces.new((lo[i], lo[(i + 1) % seg], hi[(i + 1) % seg], hi[i]))
            o = _bm_obj(e, name, b, mat, sub); bv = o.modifiers.new('bv', 'BEVEL'); bv.width = 0.006; bv.segments = 3; o.modifiers.move(1, 0); return o
        slab(0.0, 0.022, 1.0, 'sole', sole_m, 1)
        hgt = {'sneaker': 0.075, 'loafer': 0.05, 'boot': 0.16}[kind]
        up = slab(0.02, hgt, 0.93, 'upper', fabric(lin(color), 'linen' if kind == 'sneaker' else 'velvet'), 2)
        for v_ in up.data.vertices:                                     # toe slopes down to the front
            if v_.co.z > 0.03: v_.co.z -= (hgt - 0.035) * max(0, -v_.co.y / 0.125) ** 1.6
        op = cyl(e, 'opening', 0, 0.045, 0.030, hgt - 0.012, hgt + 0.001, pbr('shoe_in', None, color=(0.15, 0.13, 0.12), rough=0.8), 24, 0, 0.95, 1.5)
        if kind == 'sneaker':
            for k_ in range(4): cube(e, 'lace', -0.02, -0.035 + k_ * 0.018, hgt - 0.012 - (3 - k_) * 0.006, 0.02, -0.029 + k_ * 0.018, hgt - 0.006 - (3 - k_) * 0.006, MM('matte_white'), 0.002)


KNITS = [(0.84, 0.76, 0.62), (0.48, 0.34, 0.24), (0.92, 0.90, 0.86), (0.32, 0.36, 0.28), (0.66, 0.56, 0.48), (0.16, 0.18, 0.26), (0.62, 0.30, 0.22), (0.50, 0.58, 0.68)]
HANG = [('shirt', (0.93, 0.93, 0.91)), ('jacket', (0.14, 0.16, 0.24)), ('knit', (0.72, 0.56, 0.38)), ('shirt', (0.50, 0.62, 0.78)),
        ('tee', (0.10, 0.10, 0.11)), ('dress', (0.52, 0.28, 0.20)), ('knit', (0.36, 0.40, 0.30)), ('shirt', (0.88, 0.84, 0.76)),
        ('jacket', (0.58, 0.46, 0.34)), ('trousers', (0.24, 0.22, 0.20)), ('tee', (0.84, 0.84, 0.82)), ('knit', (0.20, 0.26, 0.40)),
        ('shirt', (0.70, 0.36, 0.28)), ('dress', (0.16, 0.16, 0.17))]


def wardrobe_open(name, cx, cy, w, d, rot=0, h=2.2, sections=None, led=True, fill=0.65, seed=0):
    """open wardrobe, back at local +Y. sections: list of 'hang' | 'shelves' | 'shoes' | 'hang_short' (default all 'hang').
    Hanging garments sparse (premium boutique look), each detailed."""
    r = _root(name, cx, cy, rot); hw, hd = w / 2, d / 2; t = 0.022; m = M('oak_light')
    nsec = max(1, round(w / 0.85)); sections = (sections or ['hang'] * nsec)[:nsec] + ['hang'] * max(0, nsec - len(sections or []))
    cube(r, 'back', -hw, hd - 0.012, 0, hw, hd, h, m)
    for sx in (-1, 1): cube(r, 'side', sx * hw - (t if sx > 0 else 0), -hd, 0, sx * hw + (0 if sx > 0 else t), hd, h, m, 0.003)
    cube(r, 'bottom', -hw, -hd, 0, hw, hd, 0.06, m, 0.002)
    for i in range(1, nsec):
        x = -hw + i * w / nsec; cube(r, 'div', x - t / 2, -hd, 0, x + t / 2, hd, h, m, 0.003)
    rr = random.Random(seed + int(abs(cx) * 100))
    for i, kind in enumerate(sections):
        x0 = -hw + i * w / nsec + t / 2 + (t / 2 if i == 0 else 0); x1 = -hw + (i + 1) * w / nsec - t / 2 - (t / 2 if i == nsec - 1 else 0)
        if led:
            for xx in (x0 + 0.004, x1 - 0.004): cube(r, 'led', xx - 0.003, -hd + 0.03, 0.10, xx + 0.003, -hd + 0.045, h - 0.05, M('led'))
        if kind.startswith('hang'):
            zr = 1.88 if kind == 'hang' else 1.10
            rail = cyl(r, 'rail', 0, 0, 0.011, -(x1 - x0) / 2, (x1 - x0) / 2, MM('brass'), 16)
            rail.rotation_euler[1] = math.radians(90); rail.location = ((x0 + x1) / 2, 0, zr)
            nn = max(3, int((x1 - x0) * fill / 0.075)); step = (x1 - x0 - 0.12) / max(1, nn - 1)
            for k in range(nn):
                kd, col = HANG[(k * 5 + i * 3 + seed) % len(HANG)]
                if kind == 'hang_short' and kd == 'dress': kd = 'shirt'
                garment(r, kd, x0 + 0.06 + k * step + rr.uniform(-0.01, 0.01), zr - 0.015, col, seed * 100 + i * 10 + k, min(d - 0.10, 0.46))
            if kind == 'hang_short':
                cube(r, 'shelf_low', x0, -hd + 0.02, 0.40, x1, hd - 0.012, 0.42, m, 0.002)
                folded_stack(r, x0 + 0.04, (x0 + x1) / 2 - 0.02, -hd + 0.06, hd - 0.06, 0.42, 4, KNITS, i + seed)
        elif kind == 'shelves':
            levels = [0.40, 0.78, 1.16, 1.54, 1.92]
            for zz in levels: cube(r, 'shelf', x0, -hd + 0.02, zz - 0.02, x1, hd - 0.012, zz, m, 0.002)
            for li, zz in enumerate(levels):
                nst = 2 if (x1 - x0) > 0.55 else 1; sw = (x1 - x0 - 0.08) / nst
                for s_ in range(nst):
                    folded_stack(r, x0 + 0.04 + s_ * sw, x0 + 0.04 + (s_ + 1) * sw - 0.04, -hd + 0.07, hd - 0.07, zz, rr.randint(3, 5), KNITS, li * 3 + s_ + i)
        elif kind == 'shoes':
            levels = [0.08, 0.36, 0.64, 0.92, 1.20]
            for zz in levels[1:]: cube(r, 'shelf', x0, -hd + 0.02, zz - 0.02, x1, hd - 0.012, zz, m, 0.002)
            cube(r, 'shelf_top', x0, -hd + 0.02, 1.48, x1, hd - 0.012, 1.50, m, 0.002)
            folded_stack(r, x0 + 0.05, x1 - 0.05, -hd + 0.07, hd - 0.07, 1.50, 5, KNITS, i + 7)
            kinds = ['sneaker', 'loafer', 'sneaker', 'boot', 'loafer']; cols = [(0.94, 0.93, 0.90), (0.40, 0.26, 0.18), (0.20, 0.20, 0.22), (0.55, 0.42, 0.30), (0.12, 0.12, 0.12)]
            for li, zz in enumerate(levels):
                npair = max(1, int((x1 - x0) / 0.26))
                for p in range(npair):
                    shoe_pair(r, x0 + (p + 0.5) * (x1 - x0) / npair, 0, zz, cols[(li + p) % 5], kinds[(li + p) % 5], 0, li * 7 + p)
    return r


# ============================================================== WARDROBE v4: cloth-simulated garments (assets/garments.blend, baked by gar_bake.py)
_GAR = {}
FAB = {'shirt': ('waffle_pique_cotton', 9), 'tee': ('cotton_jersey', 9), 'knit': ('knitted_fleece', 5), 'jacket': ('poly_wool_herringbone', 4),
       'dress': ('velour_velvet', 6), 'trousers': ('denim_fabric', 3)}


def _garments():
    if not _GAR:
        with bpy.data.libraries.load(ROOT + 'assets/garments.blend') as (src, dst): dst.meshes = [n for n in src.meshes if n.startswith('G_')]
        for m in dst.meshes:
            if m is not None: _GAR[m.name[2:]] = m
    return _GAR


def garment_mat(kind, color):
    folder, scl = FAB[kind]
    key = f'gar_{kind}_{color[0]:.2f}_{color[1]:.2f}_{color[2]:.2f}'
    if kind == 'trousers' and color is None: return pbr(key, folder, scl, None, None, nstr=1.0, sheen=0.2, spec=0.3)
    return pbr(key, folder, scl, lin(color), None, nstr=2.2, sheen=0.45, use_diff=False, spec=0.25)


def garment(root, kind, x, z_top, color, seed=0, width=0.44):
    """cloth-simulated garment on a hidden wooden hanger with a brass hook; plane YZ across the rail"""
    G = _garments(); rr = random.Random(seed)
    me = G.get(f'{kind}_{seed % 2}') or G.get(f'{kind}_0')
    o = bpy.data.objects.new(kind, me); bpy.context.scene.collection.objects.link(o); _link(o, root)
    o.location = (x, 0, z_top + 0.02); o.rotation_euler[2] = math.radians(rr.uniform(-5, 5) + (180 if rr.random() < 0.5 else 0))
    s_ = width / 0.44 * rr.uniform(0.96, 1.03); o.scale = (1, s_, rr.uniform(0.97, 1.03))
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.0025
    ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = 1; ss.render_levels = 2
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.clear() if o.data.users <= 1 else None
    mat = garment_mat(kind, color if kind != 'trousers' or rr.random() < 0.5 else None)
    o.material_slots and None
    if not o.data.materials: o.data.materials.append(mat)
    else:
        o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = mat
    hanger(root, x, z_top + 0.02 - 0.034, 0.36 * width / 0.44)


def folded_stack(root, x0, x1, y0, y1, z, n, colors, seed=0):
    """stack of folded knits/tees (cloth-baked G_folded meshes), each with its own fabric, slightly uneven"""
    G = _garments(); rr = random.Random(seed); h = 0.046
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; sx, sy = (x1 - x0) / 0.33, (y1 - y0) / 0.29
    for k in range(n):
        c = colors[(k + seed) % len(colors)]; kind = 'knit' if (k + seed) % 3 else 'shirt'
        me = G.get(f'folded_{(k + seed) % 2}') or G.get('folded_0')
        o = bpy.data.objects.new('fold', me); bpy.context.scene.collection.objects.link(o); _link(o, root)
        o.location = (cx + rr.uniform(-0.01, 0.01), cy + rr.uniform(-0.008, 0.008), z + k * h); o.hide_render = False; o.rotation_euler[2] = math.radians(rr.uniform(-3, 3) + (180 if rr.random() < 0.5 else 0))
        o.scale = (sx, sy, 1.0)
        ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = 1; ss.render_levels = 1
        sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.003
        for p in o.data.polygons: p.use_smooth = True
        mat = garment_mat(kind, c)
        if not o.data.materials: o.data.materials.append(mat)
        o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = mat
        for (a_, b_) in ((-0.13, -0.035), (-0.033, 0.13)):                     # fold crease 1/3 from the front edge
            core = cushion(root, 'fold_core', -0.15, a_, -0.016, 0.15, b_, 0.017, mat, 0.08, 0.7, 0.0015, seed + k)
            core.parent = o; core.matrix_parent_inverse.identity(); core.location = (0, 0, 0.018)
