"""Render baked garments (assets/garments.blend) on a rail with real fabric materials. run: ... -- out.png mode(front|top|persp) kinds..."""
import bpy, sys, math
sys.path.insert(0, 'C:/Projects/3d_visual/tools/bl'); import lib
argv = sys.argv[sys.argv.index('--') + 1:]
OUT, MODE = argv[0], argv[1]; KINDS = argv[2:] or ['shirt']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 96
pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
for d in pr.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPTIX'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
with bpy.data.libraries.load(lib.ROOT + 'assets/garments.blend') as (src, dst): dst.objects = [n for n in src.objects]
G = {o.name[2:]: o for o in dst.objects}
G.update({k.rsplit('_', 1)[0]: v for k, v in list(G.items()) if k.endswith('_0')})
r0 = lib._root('f', 0, 0, 0)
lib.cube(r0, 'back', -1.5, 0.30, 0, 1.5, 0.32, 2.4, lib.M('oak_light'))
lib.cube(r0, 'floor', -2, -2, -0.02, 2, 2, 0, lib.M('oak_light'))
rail = lib.cyl(r0, 'rail', 0, 0, 0.011, -1.2, 1.2, lib.MM('brass'), 16); rail.rotation_euler[1] = math.radians(90); rail.location = (0, 0, 1.88)
MAT = {'shirt': ('cotton_jersey', 18, (0.93, 0.93, 0.91)), 'tee': ('cotton_jersey', 18, (0.12, 0.12, 0.13)), 'knit': ('knitted_fleece', 10, (0.72, 0.56, 0.38)),
       'jacket': ('poly_wool_herringbone', 8, (0.16, 0.18, 0.26)), 'dress': ('velour_velvet', 8, (0.52, 0.26, 0.20)), 'trousers': ('denim_fabric', 4, None)}
n = len(KINDS); xs = [(-0.5 + (i + 0.5) / n) * min(1.8, 0.16 * n) for i in range(n)]
for x, k in zip(xs, KINDS):
    src = G[k]; o = src.copy(); o.data = src.data; sc.collection.objects.link(o)
    o.location = (x, 0, 1.86); o.rotation_euler[2] = math.radians(float(__import__('os').environ.get('GROT', '0')))
    so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.0025
    ss = o.modifiers.new('ss', 'SUBSURF'); ss.levels = 1; ss.render_levels = 2
    for p in o.data.polygons: p.use_smooth = True
    folder, scl, col = MAT[k.split('_')[0]]
    m = lib.pbr(f'gm_{k.split("_")[0]}', folder, scl, lib.lin(col) if col else None, None, nstr=1.0, sheen=0.3, use_diff=(col is None), spec=0.3)
    o.data.materials.clear(); o.data.materials.append(m)
    if not __import__('os').environ.get('NOHANGER'): lib.hanger(r0, x, 1.86 - 0.021, 0.42)
ar = bpy.data.lights.new('ar', 'AREA'); ar.size = 3; ar.energy = 250; ar.color = (1, 0.92, 0.82)
ao = bpy.data.objects.new('ar', ar); sc.collection.objects.link(ao); ao.location = (-0.6, -2.0, 3.2); ao.rotation_euler = (math.radians(40), 0, math.radians(-15))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
if MODE == 'top': cam.type = 'ORTHO'; cam.ortho_scale = max(0.8, 0.18 * n + 0.4); co.location = (0, 0, 6); sc.render.resolution_x, sc.render.resolution_y = 1400, 900
elif MODE == 'side': cam.type = 'ORTHO'; cam.ortho_scale = 1.3; co.location = (3, 0, 1.3); co.rotation_euler = (math.radians(90), 0, math.radians(90)); sc.render.resolution_x, sc.render.resolution_y = 900, 1100
elif MODE == 'front': cam.lens = 40; co.location = (0, -2.6, 1.4); co.rotation_euler = (math.radians(90), 0, 0); sc.render.resolution_x, sc.render.resolution_y = 1400, 1000
else: cam.lens = 45; co.location = (1.2, -2.2, 1.9); co.rotation_euler = (math.radians(84), 0, math.radians(28)); sc.render.resolution_x, sc.render.resolution_y = 1400, 1100
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print('RENDERED')
