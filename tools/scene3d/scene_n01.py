"""Plan «1 кк 39 квм 15 литер (зеркалка)» (n01). All coordinates in PLAN PIXELS of plans_prepared/n01_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (207, 1300, 633, 1900)}]
items = [
    # bedroom
    {"type": "glass", "box": (336, 243, 771, 331)},
    {"type": "nightstand", "box": (207, 421, 314, 521)},
    {"type": "nightstand", "box": (207, 964, 314, 1064)},
    {"type": "bed", "box": (210, 543, 714, 940), "head": "left", "hb": 18},
    {"type": "plant", "box": (786, 386, 893, 479)},
    {"type": "tv", "box": (864, 614, 884, 871)},
    {"type": "closet", "box": (207, 1150, 657, 1286), "n": 16, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (879, 1280), "len": 196, "angle": -151, "thick": 7},
    # loggia
    {"type": "glass", "box": (1066, 243, 1494, 331)},
    {"type": "glass", "box": (1244, 626, 1423, 660)},
    {"type": "leaf", "hinge": (1587, 664), "len": 165, "angle": 90, "thick": 7},
    {"type": "armchair", "box": (973, 450, 1116, 586), "rot": 30},
    {"type": "roundtable", "box": (1151, 500, 1251, 600)},
    {"type": "nightstand", "box": (1177, 526, 1225, 574), "power": 0.5},
    {"type": "plant", "box": (1451, 350, 1630, 493)},
    # kitchen-living
    {"type": "table", "box": (951, 829, 1101, 1150), "plates": [(1026, 880), (1026, 1100), (1060, 935), (1060, 1045)]},
    {"type": "chair", "box": (987, 757, 1073, 829), "back": "top"},
    {"type": "chair", "box": (987, 1150, 1073, 1221), "back": "bottom"},
    {"type": "chair", "box": (1101, 886, 1166, 979), "back": "right"},
    {"type": "chair", "box": (1101, 1000, 1166, 1093), "back": "right"},
    {"type": "tv", "box": (1611, 900, 1630, 1157)},
    {"type": "counter", "box": (1497, 1186, 1651, 1762)},
    {"type": "counter", "box": (1330, 1762, 1651, 1900)},
    {"type": "cooktop", "box": (1508, 1330, 1648, 1495), "zones": 4},
    {"type": "sink", "box": (1367, 1770, 1508, 1893)},
    {"type": "fridge", "box": (1183, 1762, 1330, 1900)},
    # shafts
    {"type": "shaft", "box": (1092, 1603, 1183, 1900)},
    {"type": "shaft", "box": (908, 1603, 1183, 1622)},
    {"type": "shaft", "box": (207, 1300, 470, 1385)},
    # hallway
    {"type": "closet", "box": (933, 1622, 1092, 1900), "n": 8, "backSide": "right"},
    {"type": "pouf", "box": (658, 1720, 695, 1855)},
    {"type": "leaf", "hinge": (900, 1905), "len": 238, "angle": 151, "thick": 9, "dark": True},
    # bathroom
    {"type": "washer", "box": (493, 1307, 623, 1414)},
    {"type": "ledge", "box": (207, 1395, 255, 1587)},
    {"type": "toilet2", "box": (255, 1450, 370, 1555), "face": "right"},
    {"type": "vanity2", "box": (207, 1612, 292, 1720), "basin": (214, 1625, 285, 1707), "faucet": "left"},
    {"type": "bathtub", "box": (207, 1745, 600, 1895), "mixer": "left"},
    {"type": "leaf", "hinge": (633, 1712), "len": 188, "angle": -58, "thick": 7},
]

if __name__ == "__main__":
    build("n01", items, floors, sys.argv[1], pixel=True)
    print("ok")
