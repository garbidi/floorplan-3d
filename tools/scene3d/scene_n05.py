"""Plan «1кк 37,4 квм 14 литер» (n05). All coordinates in PLAN PIXELS of plans_prepared/n05_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (208, 1347, 650, 2090)}]
items = [
    # loggia (top-left)
    {"type": "glass", "box": (400, 215, 835, 272)},
    {"type": "glass", "box": (443, 570, 617, 603)},
    {"type": "leaf", "hinge": (267, 602), "len": 170, "angle": 90, "thick": 7},
    {"type": "plant", "box": (237, 300, 397, 460)},
    {"type": "roundtable", "box": (611, 453, 697, 539)},
    {"type": "nightstand", "box": (632, 474, 676, 518), "power": 0.5},   # small table lamp on the side table
    {"type": "armchair", "box": (744, 412, 858, 526), "rot": 30},
    # kitchen
    {"type": "counter", "box": (210, 800, 367, 1333)},
    {"type": "counter", "box": (367, 1173, 530, 1333)},
    {"type": "cooktop", "box": (223, 847, 350, 1027), "zones": 4},
    {"type": "sink", "box": (377, 1187, 510, 1307)},
    {"type": "fridge", "box": (530, 1173, 677, 1333)},
    {"type": "table", "box": (757, 747, 927, 973), "plates": [(843, 800), (843, 920), (795, 860)]},
    {"type": "chair", "box": (810, 677, 903, 747), "back": "top"},
    {"type": "chair", "box": (810, 973, 903, 1040), "back": "bottom"},
    {"type": "chair", "box": (683, 813, 757, 900), "back": "left"},
    {"type": "leaf", "hinge": (903, 1331), "len": 200, "angle": -146, "thick": 7},
    # bedroom
    {"type": "glass", "box": (1130, 215, 1565, 272)},
    {"type": "table", "box": (953, 307, 1040, 520)},                        # desk
    {"type": "chair", "box": (1040, 360, 1100, 467), "back": "right"},
    {"type": "plant", "box": (1545, 300, 1630, 394)},
    {"type": "nightstand", "box": (1553, 456, 1657, 567)},
    {"type": "nightstand", "box": (1553, 997, 1657, 1100)},
    {"type": "bed", "box": (1157, 587, 1657, 976), "head": "right", "hb": 18},
    {"type": "tv", "box": (978, 651, 996, 909)},
    {"type": "closet", "box": (1216, 1191, 1657, 1320), "n": 16, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (1013, 1327), "len": 189, "angle": -32, "thick": 7},
    # hallway
    {"type": "rug", "box": (1025, 1360, 1375, 1585)},
    {"type": "console", "box": (947, 1617, 1113, 1672)},                    # shoe cabinet
    {"type": "pouf", "box": (1117, 1622, 1255, 1672)},
    {"type": "closet", "box": (1508, 1340, 1658, 1675), "n": 9, "backSide": "right"},
    {"type": "leaf", "hinge": (1270, 1693), "len": 216, "angle": 34, "thick": 9, "dark": True},
    # bathroom
    {"type": "shaft", "box": (208, 1350, 640, 1445)},
    {"type": "ledge", "box": (208, 1462, 258, 1660)},
    {"type": "toilet", "box": (258, 1522, 367, 1605)},
    {"type": "vanity", "box": (213, 1660, 292, 1938)},
    {"type": "washer", "box": (488, 1733, 600, 1877)},
    {"type": "bathtub", "box": (213, 1943, 567, 2088), "mixer": "left"},
    {"type": "leaf", "hinge": (645, 1650), "len": 174, "angle": -60, "thick": 7},
]

if __name__ == "__main__":
    build("n05", items, floors, sys.argv[1], pixel=True)
    print("ok")
