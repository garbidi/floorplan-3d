"""Library showroom: all pieces on a floor, top-down ortho render (and optional 3/4 perspective).
run: blender -b --factory-startup --python showroom.py -- out.png samples [persp]"""
import bpy, sys, math, os, importlib
sys.path.insert(0, 'C:/Projects/3d_visual/tools/bl')
import lib; importlib.reload(lib)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 64; PERSP = len(argv) > 2 and argv[2] == 'persp'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'
pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
for d in pr.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPTIX'; sc.cycles.use_auto_tile = False
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = -0.1

floor = lib.pbr('floor', 'laminate_floor_02', 0.8, None, rot=math.pi / 2, hsv=(0.49, 0.55, 1.25))
r0 = lib._root('floor', 4.5, -3.0, 0); lib.cube(r0, 'f', -5, -4, -0.02, 5, 4, 0, floor)

L = lib
L.sofa('sofa', 1.2, -0.7, 2.2, 0.95, 0)
L.rug('rug', 1.2, -1.4, 2.4, 1.6)
L.coffee_table('ct', 1.2, -1.75, 1.0, 0.55, 0)
L.armchair('arm', 3.2, -0.9, 0.8, 0.8, 20)
L.coffee_table('ctr', 3.3, -1.9, 0.5, 0.5, 0, round_=True)
L.plant('pl', 4.2, -0.6, 0.6)
L.bed('bed', 6.0, -1.2, 1.6, 2.05, 0)
L.nightstand('ns1', 4.8, -0.35, 0.45, 0.4, 0)
L.nightstand('ns2', 7.2, -0.35, 0.45, 0.4, 0)
L.wardrobe_open('wr', 1.3, -3.0, 2.0, 0.6, 0)
L.cabinet('cab', 3.2, -3.0, 1.0, 0.5, 0)
L.shoe_cabinet('shoe', 4.2, -3.0, 0.8, 0.35, 0)
L.pouf('pouf', 4.2, -3.7, 0.5, 0.4)
L.dining_table('dt', 6.0, -3.4, 1.4, 0.8, 0)
L.chair('ch1', 5.6, -2.75, 0.45, 0.5, 0)
L.chair('ch2', 6.4, -2.75, 0.45, 0.5, 0)
L.chair('ch3', 5.6, -4.05, 0.45, 0.5, 180)
L.chair('ch4', 6.4, -4.05, 0.45, 0.5, 180)
L.desk('desk', 8.2, -3.2, 1.2, 0.6, 0)
L.kitchen_run('kit', 1.8, -5.3, 3.0, 0.6, 0, sink_at=-0.6, hob_at=0.7)
L.fridge('fr', 3.7, -5.3, 0.65, 0.65, 0)
L.washer('wash', 4.6, -5.3, 0.6, 0.6, 0)
L.bathtub('tub', 6.1, -5.3, 1.7, 0.75, 0)
L.toilet('wc', 7.6, -5.2, 0.38, 0.62, 0)
L.washbasin('wb', 8.4, -5.0, 0.55, 0.42, 0)
L.tv('tv', 8.4, -1.0, 1.2, 0, 1.0)
L.door_leaf('door', 7.8, -6.6, 0.8, 30)

sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 1.0; sun.angle = math.radians(20); sun.color = (1.0, 0.85, 0.68)
so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(15), math.radians(10), math.radians(20))
ar = bpy.data.lights.new('ar', 'AREA'); ar.shape = 'RECTANGLE'; ar.size = 12; ar.size_y = 10; ar.energy = 700; ar.color = (1.0, 0.9, 0.78)
ao = bpy.data.objects.new('ar', ar); sc.collection.objects.link(ao); ao.location = (4.5, -3.0, 6); ao.visible_glossy = False
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.50, 0.45, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
if PERSP:
    cam.lens = 30; co.location = (4.5, -12.0, 7.5); co.rotation_euler = (math.radians(58), 0, 0)
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1100
else:
    cam.type = 'ORTHO'; cam.ortho_scale = 9.6; co.location = (4.5, -3.3, 20)
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1400
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True); print('RENDERED', OUT)
