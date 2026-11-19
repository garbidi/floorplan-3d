import bpy, sys, math
sys.path.insert(0, 'C:/Projects/3d_visual/tools/bl'); import lib
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 96
pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
for d in pr.devices: d.use = d.type == 'OPTIX'
sc.cycles.device = 'GPU'; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPTIX'; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
r0 = lib._root('f', 0, 0, 0); lib.cube(r0, 'f', -3, -3, -0.02, 3, 3, 0, lib.pbr('floor', 'laminate_floor_02', 0.8, None, rot=math.pi / 2, hsv=(0.49, 0.55, 1.25)))
lib.wardrobe_open('wr', 0, 0, 3.4, 0.6, 0, sections=['hang', 'shelves', 'hang', 'shoes'])
ar = bpy.data.lights.new('ar', 'AREA'); ar.size = 6; ar.energy = 500; ar.color = (1, 0.9, 0.8); ao = bpy.data.objects.new('ar', ar); sc.collection.objects.link(ao); ao.location = (0, -2, 5)
ao.rotation_euler = (math.radians(20), 0, 0)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.46, 0.42, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
cam = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co); sc.camera = co
if 'top' in sys.argv: cam.type = 'ORTHO'; cam.ortho_scale = 3.6; co.location = (0, 0, 10); sc.render.resolution_x, sc.render.resolution_y = 1600, 500
elif 'zoom' in sys.argv: cam.type = 'ORTHO'; cam.ortho_scale = 1.0; co.location = (-1.27, 0, 10); sc.render.resolution_x, sc.render.resolution_y = 1400, 900
elif 'shelf' in sys.argv: cam.lens = 50; co.location = (-0.425, -1.3, 1.25); co.rotation_euler = (math.radians(80), 0, 0); sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
elif 'shoes' in sys.argv: cam.lens = 50; co.location = (1.275, -1.2, 1.1); co.rotation_euler = (math.radians(75), 0, 0); sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
elif 'hangc' in sys.argv: cam.lens = 45; co.location = (-1.0, -1.5, 1.45); co.rotation_euler = (math.radians(85), 0, math.radians(-12)); sc.render.resolution_x, sc.render.resolution_y = 1200, 1200
else: cam.lens = 32; co.location = (0, -3.6, 1.5); co.rotation_euler = (math.radians(88), 0, 0); sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
sc.render.filepath = sys.argv[-1]
bpy.ops.render.render(write_still=True); print('RENDERED')
