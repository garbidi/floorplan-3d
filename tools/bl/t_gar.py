import bpy, sys, math
sys.path.insert(0, 'C:/Projects/3d_visual/tools/bl'); import lib
bpy.ops.wm.read_factory_settings(use_empty=True)
m = lib.fabric((0.2, 0.22, 0.3))
b = m.node_tree.nodes['Principled BSDF']
print('BASE', tuple(b.inputs['Base Color'].default_value), [l.from_node.type for l in b.inputs['Base Color'].links])
print('MATS', [x.name for x in bpy.data.materials])
