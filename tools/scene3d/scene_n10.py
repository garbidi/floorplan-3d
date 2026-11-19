"""Plan «2 кк 54 квм 15 литер» (n10): same layout as n08, items remapped from scene_n08 (remap_scene.py) and checked on the overlay."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{'type': 'tile', 'box': (192, 1076, 558, 1498)}, {'type': 'tile', 'box': (598, 1290, 1033, 1504)}]
items = [
    {'type': 'glass', 'box': (236, 139, 605, 212)},
    {'type': 'tv', 'box': (212, 242, 229, 457)},
    {'type': 'table', 'box': (497, 332, 777, 491), 'plates': [(575, 379), (694, 379), (575, 444), (694, 444)]},
    {'type': 'chair', 'box': (536, 274, 612, 332), 'back': 'top'},
    {'type': 'chair', 'box': (655, 274, 734, 332), 'back': 'top'},
    {'type': 'chair', 'box': (536, 491, 612, 556), 'back': 'bottom'},
    {'type': 'chair', 'box': (655, 491, 734, 556), 'back': 'bottom'},
    {'type': 'counter', 'box': (192, 473, 322, 901)},
    {'type': 'counter', 'box': (192, 901, 467, 1027)},
    {'type': 'cooktop', 'box': (195, 550, 319, 702), 'zones': 4},
    {'type': 'sink', 'box': (268, 920, 360, 1025)},
    {'type': 'sink', 'box': (360, 920, 441, 1025)},
    {'type': 'fridge', 'box': (467, 901, 592, 1027)},
    {'type': 'leaf', 'hinge': (771, 1040), 'len': 170, 'angle': -149, 'thick': 7},
    {'type': 'glass', 'box': (872, 139, 1229, 212)},
    {'type': 'closet', 'box': (813, 258, 926, 627), 'n': 8, 'backSide': 'left'},
    {'type': 'bed1', 'box': (813, 645, 971, 1027)},
    {'type': 'nightstand', 'box': (989, 944, 1073, 1027)},
    {'type': 'table', 'box': (1295, 261, 1394, 499)},
    {'type': 'chair', 'box': (1192, 318, 1295, 451), 'back': 'left'},
    {'type': 'console', 'box': (1350, 523, 1394, 808)},
    {'type': 'tv', 'box': (1364, 563, 1380, 772)},
    {'type': 'leaf', 'hinge': (1347, 1040), 'len': 172, 'angle': -149, 'thick': 7},
    {'type': 'glass', 'box': (1500, 140, 1868, 218)},
    {'type': 'glass', 'box': (1634, 462, 1783, 486)},
    {'type': 'leaf', 'hinge': (1493, 486), 'len': 142, 'angle': 90, 'thick': 7},
    {'type': 'plant', 'box': (1479, 232, 1613, 360)},
    {'type': 'roundtable', 'box': (1783, 360, 1868, 445)},
    {'type': 'nightstand', 'box': (1805, 382, 1846, 424), 'power': 0.5},
    {'type': 'armchair', 'box': (1886, 315, 2012, 431), 'rot': -30},
    {'type': 'nightstand', 'box': (1931, 537, 2016, 623)},
    {'type': 'nightstand', 'box': (1931, 984, 2016, 1069)},
    {'type': 'bed', 'box': (1606, 636, 2016, 977), 'head': 'right', 'hb': 18},
    {'type': 'tv', 'box': (1434, 701, 1451, 914)},
    {'type': 'closet', 'box': (1641, 1133, 2016, 1239), 'n': 12, 'along': True, 'backSide': 'bottom'},
    {'type': 'leaf', 'hinge': (1401, 1228), 'len': 165, 'angle': -56, 'thick': 7},
    {'type': 'closet', 'box': (1299, 1229, 1398, 1519), 'n': 7, 'backSide': 'right'},
    {'type': 'pouf', 'box': (1036, 1318, 1075, 1491)},
    {'type': 'console', 'box': (830, 1048, 1109, 1084)},
    {'type': 'leaf', 'hinge': (1079, 1548), 'len': 178, 'angle': 30, 'thick': 9, 'dark': True},
    {'type': 'shaft', 'box': (192, 1027, 568, 1076)},
    {'type': 'washer', 'box': (195, 1107, 309, 1199)},
    {'type': 'vanity2', 'box': (199, 1227, 262, 1347), 'basin': (205, 1240, 256, 1334), 'faucet': 'left'},
    {'type': 'bathtub', 'box': (197, 1398, 488, 1500), 'mixer': 'left'},
    {'type': 'leaf', 'hinge': (556, 1278), 'len': 145, 'angle': -57, 'thick': 7},
    {'type': 'shaft', 'box': (558, 1290, 598, 1504)},
    {'type': 'ledge', 'box': (598, 1328, 675, 1496)},
    {'type': 'toilet2', 'box': (675, 1374, 766, 1466), 'face': 'right'},
    {'type': 'vanity2', 'box': (944, 1357, 1031, 1457), 'basin': (954, 1367, 1021, 1447), 'faucet': 'right'},
    {'type': 'leaf', 'hinge': (781, 1300), 'len': 144, 'angle': -32, 'thick': 7},
]


if __name__ == "__main__":
    build("n10", items, floors, sys.argv[1], pixel=True)
    print("ok")
