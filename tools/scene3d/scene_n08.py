"""Plan «2 кк 53 квм 14 литер» (n08). All coordinates in PLAN PIXELS of plans_prepared/n08_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (185, 1097, 555, 1522)}, {"type": "tile", "box": (596, 1312, 1035, 1528)}]
items = [
    # kitchen-living
    {"type": "glass", "box": (230, 153, 603, 227)},
    {"type": "tv", "box": (206, 257, 223, 473)},
    {"type": "table", "box": (494, 347, 777, 507), "plates": [(572, 395), (693, 395), (572, 460), (693, 460)]},
    {"type": "chair", "box": (533, 289, 610, 347), "back": "top"},
    {"type": "chair", "box": (653, 289, 733, 347), "back": "top"},
    {"type": "chair", "box": (533, 507, 610, 573), "back": "bottom"},
    {"type": "chair", "box": (653, 507, 733, 573), "back": "bottom"},
    {"type": "counter", "box": (185, 489, 317, 920)},
    {"type": "counter", "box": (185, 920, 463, 1047)},
    {"type": "cooktop", "box": (188, 567, 314, 720), "zones": 4},
    {"type": "sink", "box": (262, 940, 355, 1045)},
    {"type": "sink", "box": (355, 940, 437, 1045)},
    {"type": "fridge", "box": (463, 920, 590, 1047)},
    {"type": "leaf", "hinge": (770, 1060), "len": 171, "angle": -149, "thick": 7},
    # middle bedroom
    {"type": "glass", "box": (873, 153, 1233, 227)},
    {"type": "closet", "box": (813, 273, 927, 644), "n": 8, "backSide": "left"},
    {"type": "bed1", "box": (813, 663, 973, 1047)},
    {"type": "nightstand", "box": (991, 964, 1076, 1047)},
    {"type": "table", "box": (1300, 276, 1400, 516)},
    {"type": "chair", "box": (1196, 333, 1300, 467), "back": "left"},
    {"type": "console", "box": (1356, 540, 1400, 827)},
    {"type": "tv", "box": (1370, 580, 1386, 790)},
    {"type": "leaf", "hinge": (1353, 1060), "len": 174, "angle": -149, "thick": 7},
    # loggia
    {"type": "glass", "box": (1507, 154, 1879, 233)},
    {"type": "glass", "box": (1643, 478, 1793, 502)},
    {"type": "leaf", "hinge": (1500, 502), "len": 143, "angle": 90, "thick": 7},
    {"type": "plant", "box": (1486, 247, 1621, 376)},
    {"type": "roundtable", "box": (1793, 376, 1879, 461)},
    {"type": "nightstand", "box": (1815, 398, 1857, 440), "power": 0.5},
    {"type": "armchair", "box": (1897, 330, 2025, 447), "rot": -30},
    # right bedroom
    {"type": "nightstand", "box": (1943, 554, 2029, 640)},
    {"type": "nightstand", "box": (1943, 1004, 2029, 1090)},
    {"type": "bed", "box": (1614, 654, 2029, 997), "head": "right", "hb": 18},
    {"type": "tv", "box": (1440, 719, 1458, 933)},
    {"type": "closet", "box": (1650, 1154, 2029, 1261), "n": 12, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (1407, 1250), "len": 166, "angle": -56, "thick": 7},
    # hallway
    {"type": "closet", "box": (1304, 1251, 1404, 1543), "n": 7, "backSide": "right"},
    {"type": "pouf", "box": (1038, 1340, 1078, 1515)},
    {"type": "console", "box": (830, 1068, 1112, 1105)},
    {"type": "leaf", "hinge": (1082, 1572), "len": 180, "angle": 30, "thick": 9, "dark": True},
    # bathroom
    {"type": "shaft", "box": (185, 1047, 565, 1097)},
    {"type": "shaft", "box": (185, 1522, 555, 1574)},
    {"type": "washer", "box": (188, 1128, 304, 1220)},
    {"type": "vanity2", "box": (322, 1100, 447, 1192), "basin": (337, 1110, 432, 1180), "faucet": "top"},
    {"type": "bathtub", "box": (188, 1351, 488, 1474), "mixer": "left"},
    {"type": "leaf", "hinge": (553, 1300), "len": 146, "angle": -57, "thick": 7},
    # WC
    {"type": "shaft", "box": (555, 1312, 596, 1528)},
    {"type": "ledge", "box": (596, 1350, 673, 1520)},
    {"type": "toilet2", "box": (673, 1397, 765, 1489), "face": "right"},
    {"type": "vanity2", "box": (945, 1380, 1033, 1480), "basin": (955, 1390, 1023, 1470), "faucet": "right"},
    {"type": "leaf", "hinge": (781, 1322), "len": 145, "angle": -32, "thick": 7},
]

if __name__ == "__main__":
    build("n08", items, floors, sys.argv[1], pixel=True)
    print("ok")
