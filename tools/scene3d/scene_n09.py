"""Plan «2 кк 53 квм 15 литер» (n09). All coordinates in PLAN PIXELS of plans_prepared/n09_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1632, 935, 1985, 1330)}, {"type": "tile", "box": (1192, 1125, 1557, 1330)}]
items = [
    # loggia
    {"type": "glass", "box": (270, 152, 616, 200)},
    {"type": "glass", "box": (375, 447, 520, 474)},
    {"type": "leaf", "hinge": (660, 474), "len": 138, "angle": 90, "thick": 7},
    {"type": "armchair", "box": (160, 302, 286, 423), "rot": -30},
    {"type": "roundtable", "box": (310, 350, 391, 431)},
    {"type": "nightstand", "box": (330, 370, 371, 411), "power": 0.5},
    {"type": "plant", "box": (560, 221, 689, 350)},
    # kitchen-living
    {"type": "tv", "box": (158, 511, 176, 729)},
    {"type": "table", "box": (455, 705, 734, 866), "plates": [(539, 745), (661, 745), (539, 826), (661, 826)]},
    {"type": "chair", "box": (499, 645, 579, 705), "back": "top"},
    {"type": "chair", "box": (621, 645, 702, 705), "back": "top"},
    {"type": "chair", "box": (499, 866, 579, 915), "back": "bottom"},
    {"type": "chair", "box": (621, 866, 702, 915), "back": "bottom"},
    {"type": "counter", "box": (141, 871, 266, 1213)},
    {"type": "counter", "box": (141, 1213, 541, 1329)},
    {"type": "cooktop", "box": (144, 939, 263, 1084), "zones": 4},
    {"type": "sink", "box": (270, 1220, 440, 1322)},
    {"type": "fridge", "box": (541, 1213, 660, 1329)},
    {"type": "leaf", "hinge": (737, 1100), "len": 152, "angle": -122, "thick": 7},
    {"type": "shaft", "box": (660, 1156, 754, 1329)},
    # middle bedroom
    {"type": "glass", "box": (890, 152, 1240, 200)},
    {"type": "nightstand", "box": (752, 261, 829, 374)},
    {"type": "bed", "box": (756, 377, 1156, 697), "head": "left", "hb": 16},
    {"type": "plant", "box": (1256, 229, 1345, 310)},
    {"type": "tv", "box": (1321, 439, 1340, 640)},
    {"type": "closet", "box": (752, 806, 1123, 915), "n": 14, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (1321, 918), "len": 155, "angle": -152, "thick": 7},
    # right bedroom (children's)
    {"type": "glass", "box": (1485, 152, 1840, 200)},
    {"type": "closet", "box": (1396, 237, 1509, 479), "n": 7, "backSide": "left"},
    {"type": "table", "box": (1888, 245, 1985, 479)},
    {"type": "chair", "box": (1783, 306, 1888, 415), "back": "left"},
    {"type": "bed1", "box": (1832, 527, 1985, 906), "head": "bottom"},
    {"type": "nightstand", "box": (1727, 826, 1807, 906)},
    {"type": "leaf", "hinge": (1436, 918), "len": 150, "angle": -36, "thick": 7},
    # hallway
    {"type": "console", "box": (826, 931, 1152, 971)},
    {"type": "closet", "box": (1044, 1124, 1168, 1334), "n": 7, "backSide": "right"},
    {"type": "pouf", "box": (756, 1125, 790, 1260)},
    {"type": "leaf", "hinge": (1006, 1340), "len": 196, "angle": 150, "thick": 9, "dark": True},
    # WC
    {"type": "vanity2", "box": (1194, 1189, 1250, 1261), "basin": (1199, 1196, 1245, 1254), "faucet": "left"},
    {"type": "ledge", "box": (1509, 1150, 1557, 1300)},
    {"type": "toilet2", "box": (1420, 1197, 1509, 1277), "face": "left"},
    {"type": "shaft", "box": (1557, 1132, 1630, 1261)},
    {"type": "leaf", "hinge": (1300, 1125), "len": 150, "angle": -33, "thick": 7},
    # bathroom
    {"type": "washer", "box": (1893, 935, 1985, 1052)},
    {"type": "vanity2", "box": (1925, 1052, 1985, 1161), "basin": (1931, 1062, 1979, 1151), "faucet": "right"},
    {"type": "bathtub", "box": (1678, 1210, 1977, 1326), "mixer": "right"},
    {"type": "leaf", "hinge": (1632, 1112), "len": 135, "angle": -132, "thick": 7},
]

if __name__ == "__main__":
    build("n09", items, floors, sys.argv[1], pixel=True)
    print("ok")
