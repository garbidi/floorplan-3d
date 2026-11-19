"""Plan «1кк 37 квм 15 литер» (n04). All coordinates in PLAN PIXELS of plans_prepared/n04_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (233, 1485, 660, 2114)}]
items = [
    # loggia (top-left): L-shaped corner glazing
    {"type": "glass", "box": (133, 273, 707, 313)},
    {"type": "glass", "box": (133, 273, 180, 567)},
    {"type": "glass", "box": (460, 642, 633, 678)},
    {"type": "leaf", "hinge": (293, 672), "len": 168, "angle": 90, "thick": 7},
    {"type": "plant", "box": (247, 380, 400, 520)},
    {"type": "roundtable", "box": (624, 540, 713, 633)},
    {"type": "nightstand", "box": (647, 564, 690, 607), "power": 0.5},
    {"type": "armchair", "box": (752, 478, 888, 614), "rot": 30},
    # kitchen
    {"type": "counter", "box": (233, 853, 380, 1213)},
    {"type": "counter", "box": (233, 1213, 544, 1353)},
    {"type": "cooktop", "box": (236, 907, 377, 1073), "zones": 4},
    {"type": "sink", "box": (387, 1227, 533, 1350)},
    {"type": "fridge", "box": (544, 1213, 693, 1353)},
    {"type": "table", "box": (767, 787, 940, 1013), "plates": [(853, 845), (853, 955), (800, 900)]},
    {"type": "chair", "box": (820, 720, 907, 787), "back": "top"},
    {"type": "chair", "box": (820, 1013, 907, 1093), "back": "bottom"},
    {"type": "chair", "box": (696, 853, 767, 947), "back": "left"},
    {"type": "leaf", "hinge": (893, 1375), "len": 197, "angle": -147, "thick": 7},
    # bedroom
    {"type": "glass", "box": (1080, 267, 1513, 353)},
    {"type": "table", "box": (960, 387, 1047, 600)},
    {"type": "chair", "box": (1047, 440, 1107, 547), "back": "right"},
    {"type": "plant", "box": (1533, 393, 1640, 487)},
    {"type": "nightstand", "box": (1547, 520, 1647, 620)},
    {"type": "nightstand", "box": (1547, 1047, 1647, 1153)},
    {"type": "bed", "box": (1153, 640, 1647, 1047), "head": "right", "hb": 18},
    {"type": "tv", "box": (984, 727, 1003, 987)},
    {"type": "closet", "box": (1200, 1233, 1650, 1363), "n": 16, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (993, 1375), "len": 192, "angle": -33, "thick": 7},
    # hallway
    {"type": "closet", "box": (1515, 1390, 1648, 1703), "n": 9, "backSide": "right"},
    {"type": "console", "box": (951, 1646, 1112, 1700)},
    {"type": "pouf", "box": (1120, 1650, 1257, 1700)},
    {"type": "leaf", "hinge": (1297, 1728), "len": 208, "angle": 35, "thick": 9, "dark": True},
    # bathroom
    {"type": "shaft", "box": (233, 1413, 652, 1485)},
    {"type": "glass", "box": (136, 1646, 225, 1800)},
    {"type": "ledge", "box": (233, 1485, 281, 1687)},
    {"type": "toilet2", "box": (281, 1542, 386, 1630), "face": "right"},
    {"type": "washer", "box": (499, 1751, 620, 1888)},
    {"type": "vanity2", "box": (233, 1800, 305, 1961), "basin": (241, 1830, 297, 1930), "faucet": "left"},
    {"type": "bathtub", "box": (233, 1969, 604, 2114), "mixer": "left"},
    {"type": "leaf", "hinge": (652, 1690), "len": 175, "angle": -56, "thick": 7},
]

if __name__ == "__main__":
    build("n04", items, floors, sys.argv[1], pixel=True, inside=[(180, 313, 707, 640)])
    print("ok")
