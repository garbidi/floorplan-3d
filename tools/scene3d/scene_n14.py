"""Plan «С 25 квм 15 литер» (n14). All coordinates in PLAN PIXELS of plans_prepared/n14_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (262, 240, 798, 716)}]
items = [
    # bathroom
    {"type": "shaft", "box": (798, 236, 951, 740)},
    {"type": "shower", "box": (262, 240, 453, 500), "cutX": 369, "cutZ": 403},
    {"type": "ledge", "box": (489, 240, 719, 290)},
    {"type": "toilet", "box": (552, 290, 651, 416)},
    {"type": "vanity", "box": (262, 500, 352, 716)},
    {"type": "washer", "box": (672, 556, 798, 716)},
    {"type": "towelrail", "box": (755, 372, 798, 556)},
    {"type": "leaf", "hinge": (472, 726), "len": 193, "angle": 34, "thick": 7},
    # kitchen (floor units only)
    {"type": "counter", "box": (951, 240, 1480, 416)},
    {"type": "counter", "box": (951, 416, 1123, 570)},
    {"type": "sink", "box": (967, 386, 1104, 547)},
    {"type": "cooktop", "box": (1319, 244, 1421, 412), "zones": 2},
    {"type": "fridge", "box": (951, 570, 1123, 740)},
    # living
    {"type": "sofa", "box": (1559, 240, 2049, 499), "seats": 2, "arm": 55, "back": 52, "cushions": [
        {"box": (1575, 285, 1680, 395), "rot": 25, "color": 0xf3eee6},
        {"box": (1890, 280, 1990, 380), "rot": -15, "color": 0xf3eee6},
        {"box": (1935, 300, 2030, 395), "rot": 20, "color": 0x8c6d55}]},
    {"type": "rug", "box": (1559, 499, 2049, 745)},
    {"type": "table", "box": (1220, 834, 1446, 1032), "plates": []},
    {"type": "chair", "box": (1142, 888, 1222, 997), "back": "left"},
    {"type": "chair", "box": (1446, 888, 1530, 997), "back": "right"},
    {"type": "console", "box": (1574, 971, 1949, 1030)},
    {"type": "tv", "box": (1612, 997, 1911, 1017)},
    # loggia partition: glass + door
    {"type": "glass", "box": (2141, 553, 2187, 754)},
    {"type": "leaf", "hinge": (2163, 958), "len": 205, "angle": 180, "thick": 7},
    # loggia
    {"type": "armchair", "box": (2240, 290, 2380, 435), "rot": -35},
    {"type": "roundtable", "box": (2222, 492, 2320, 590)},
    {"type": "plant", "box": (2333, 830, 2494, 1004)},
    {"type": "glass", "box": (2516, 441, 2619, 932)},
    # corridor + entrance wing
    {"type": "closet", "box": (262, 740, 391, 1387), "n": 24, "sections": 3},
    {"type": "pouf", "box": (628, 1070, 681, 1231)},
    {"type": "leaf", "hinge": (648, 1417), "len": 248, "angle": 149, "thick": 9, "dark": True},
]

if __name__ == "__main__":
    build("n14", items, floors, sys.argv[1], pixel=True)
    print("ok")
