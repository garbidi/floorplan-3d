"""Plan «С 26 квм 14 литер» (n15). All coordinates in PLAN PIXELS of plans_prepared/n15_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1849, 669, 2255, 1212)}]
items = [
    # loggia (left)
    {"type": "glass", "box": (192, 399, 262, 843)},                     # glazing in the left wall
    {"type": "glass", "box": (563, 513, 600, 691)},                     # glazed part of the partition
    {"type": "leaf", "hinge": (589, 866), "len": 174, "angle": 0, "thick": 7},
    {"type": "armchair", "box": (408, 282, 512, 386), "rot": 30},
    {"type": "roundtable", "box": (447, 442, 535, 530)},
    {"type": "plant", "box": (291, 760, 435, 904)},
    # studio
    {"type": "sofa", "box": (669, 232, 1100, 458), "seats": 2, "arm": 42, "back": 40, "cushions": [
        {"box": (686, 282, 762, 350), "rot": 25, "color": 0xf3eee6},
        {"box": (732, 266, 806, 334), "rot": -10, "color": 0x8c6d55},
        {"box": (1000, 292, 1074, 362), "rot": 20, "color": 0xf3eee6}]},
    {"type": "rug", "box": (669, 452, 1100, 674)},
    {"type": "console", "box": (780, 896, 1041, 930)},
    {"type": "tv", "box": (790, 890, 1031, 904)},
    {"type": "closet", "box": (1169, 229, 1300, 404), "n": 7, "along": True},
    {"type": "shaft", "box": (1300, 229, 1402, 404)},
    {"type": "table", "box": (1261, 763, 1458, 932), "plates": [(1308, 840), (1410, 840)]},
    {"type": "chair", "box": (1187, 802, 1261, 902), "back": "left"},
    {"type": "chair", "box": (1458, 802, 1531, 902), "back": "right"},
    # kitchen: floor units only
    {"type": "counter", "box": (1402, 229, 1824, 390)},
    {"type": "counter", "box": (1681, 390, 1824, 643)},
    {"type": "cooktop", "box": (1458, 232, 1550, 371), "zones": 2},
    {"type": "sink", "box": (1692, 390, 1811, 532)},
    {"type": "fridge", "box": (1670, 643, 1824, 793)},
    # bathroom
    {"type": "shaft", "box": (1845, 669, 1934, 871)},
    {"type": "ledge", "box": (1943, 669, 2145, 725)},
    {"type": "toilet", "box": (2003, 725, 2085, 835)},
    {"type": "towelrail", "box": (2215, 680, 2250, 856)},
    {"type": "vanity", "box": (2165, 866, 2245, 975)},
    {"type": "shower", "box": (2078, 981, 2253, 1212), "cutX": 2161, "cutZ": 1069, "corner": "tl"},
    {"type": "washer", "box": (1934, 1100, 2078, 1212)},
    {"type": "leaf", "hinge": (1836, 1112), "len": 179, "angle": -123, "thick": 7},
    # corridor + entrance wing
    {"type": "pouf", "box": (1778, 1131, 1821, 1272)},
    {"type": "leaf", "hinge": (1851, 1300), "len": 214, "angle": 55, "thick": 9, "dark": True},
    {"type": "closet", "box": (1549, 1546, 1828, 1681), "n": 10, "along": True},
]

if __name__ == "__main__":
    build("n15", items, floors, sys.argv[1], pixel=True)
    print("ok")
