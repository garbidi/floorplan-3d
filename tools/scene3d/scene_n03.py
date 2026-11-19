"""Plan «1кк 36 квм 15 литер» (n03). All coordinates in PLAN PIXELS of plans_prepared/n03_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1228, 1140, 1685, 1602)}]
items = [
    # loggia (top-left)
    {"type": "glass", "box": (340, 200, 760, 254)},
    {"type": "glass", "box": (487, 543, 662, 578)},
    {"type": "leaf", "hinge": (831, 578), "len": 160, "angle": 90, "thick": 7},
    {"type": "armchair", "box": (257, 385, 367, 495), "rot": 30},
    {"type": "roundtable", "box": (421, 428, 503, 510)},
    {"type": "nightstand", "box": (441, 448, 483, 490), "power": 0.5},     # small lamp on the side table
    {"type": "plant", "box": (719, 272, 869, 422)},
    # bedroom
    {"type": "nightstand", "box": (202, 625, 302, 727)},
    {"type": "nightstand", "box": (202, 1152, 302, 1257)},
    {"type": "bed", "box": (202, 750, 696, 1132), "head": "left", "hb": 18},
    {"type": "tv", "box": (867, 812, 885, 1068)},
    {"type": "rug", "box": (375, 1205, 700, 1449)},
    # L-shaped open wardrobe: narrow part on the left wall (with a basket of folded clothes) + the run along the bottom wall
    {"type": "closet", "box": (203, 1332, 311, 1462), "n": -1, "sections": 1, "backSide": "left"},
    {"type": "basket", "box": (226, 1365, 280, 1427)},
    {"type": "closet", "box": (203, 1458, 753, 1600), "n": 16, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (912, 1305), "len": 160, "angle": -120, "thick": 7},
    # kitchen-living
    {"type": "glass", "box": (1085, 200, 1500, 254)},
    {"type": "table", "box": (931, 387, 1260, 579), "plates": [(1025, 440), (1165, 440), (1025, 525), (1165, 525)]},
    {"type": "chair", "box": (981, 312, 1069, 387), "back": "top"},
    {"type": "chair", "box": (1121, 312, 1209, 387), "back": "top"},
    {"type": "chair", "box": (981, 579, 1069, 644), "back": "bottom"},
    {"type": "chair", "box": (1121, 579, 1209, 644), "back": "bottom"},
    {"type": "tv", "box": (1644, 281, 1662, 531)},
    {"type": "counter", "box": (1535, 550, 1685, 915)},
    {"type": "counter", "box": (1350, 915, 1685, 1044)},
    {"type": "cooktop", "box": (1550, 615, 1682, 785), "zones": 4},
    {"type": "sink", "box": (1375, 927, 1521, 1040)},
    {"type": "fridge", "box": (1204, 915, 1350, 1044)},
    {"type": "leaf", "hinge": (956, 1069), "len": 196, "angle": -31, "thick": 7},
    # shafts above the bathroom
    {"type": "shaft", "box": (1204, 1048, 1685, 1140)},
    # hallway
    {"type": "closet", "box": (775, 1374, 910, 1599), "n": 8},
    {"type": "pouf", "box": (1159, 1465, 1204, 1600)},
    {"type": "leaf", "hinge": (937, 1627), "len": 219, "angle": 31, "thick": 9, "dark": True},
    # bathroom
    {"type": "washer", "box": (1225, 1142, 1365, 1262)},
    {"type": "ledge", "box": (1365, 1142, 1522, 1178)},                   # wall shelf with toiletries
    {"type": "ledge", "box": (1637, 1184, 1685, 1384)},
    {"type": "toilet2", "box": (1527, 1242, 1637, 1328), "face": "left"},
    {"type": "shower", "box": (1456, 1427, 1685, 1602), "cutX": 1544, "cutZ": 1509, "corner": "tl"},
    {"type": "vanity2", "box": (1228, 1522, 1452, 1601), "basin": (1294, 1530, 1382, 1592), "faucet": "bottom"},
    {"type": "leaf", "hinge": (1212, 1437), "len": 171, "angle": -121, "thick": 7},
]

if __name__ == "__main__":
    build("n03", items, floors, sys.argv[1], pixel=True)
    print("ok")
