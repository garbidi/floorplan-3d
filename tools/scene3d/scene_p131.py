"""Plan 33/131 (1-room 41,0). PLAN PIXELS of plans_prepared/p131_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (224, 1540, 633, 2108)}]
items = [
    # bedroom 14,1
    {"type": "glass", "box": (372, 147, 825, 207)},
    {"type": "plant", "box": (248, 242, 343, 349)},
    {"type": "nightstand", "box": (224, 381, 327, 489)},
    {"type": "nightstand", "box": (224, 939, 327, 1048)},
    {"type": "bed", "box": (224, 509, 740, 915), "head": "left", "hb": 18},
    {"type": "table", "box": (858, 254, 945, 474)},
    {"type": "chair", "box": (797, 313, 858, 414), "back": "left"},
    {"type": "tv", "box": (896, 586, 915, 858)},
    {"type": "closet", "box": (224, 1139, 333, 1273), "n": 3, "backSide": "left", "sections": 1},
    {"type": "closet", "box": (224, 1273, 633, 1421), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (896, 1265), "len": 203, "angle": -146, "thick": 8},
    # loggia 3,8
    {"type": "glass", "box": (1158, 124, 1613, 207)},
    {"type": "plant", "box": (1042, 236, 1202, 384)},
    {"type": "roundtable", "box": (1409, 406, 1504, 497)},
    {"type": "armchair", "box": (1540, 349, 1688, 491), "rot": -40},
    {"type": "glass", "box": (1231, 524, 1421, 550)},
    {"type": "leaf", "hinge": (1048, 548), "len": 168, "angle": 90, "thick": 8},
    # kitchen-living 13,1
    {"type": "counter", "box": (1560, 556, 1720, 1516)},
    {"type": "cooktop", "box": (1565, 680, 1718, 864), "zones": 4},
    {"type": "sink", "box": (1579, 1081, 1700, 1228)},
    {"type": "table", "box": (968, 941, 1314, 1145), "plates": [(1067, 995), (1215, 995), (1067, 1095), (1215, 1095)]},
    {"type": "chair", "box": (1018, 873, 1115, 941), "back": "top"},
    {"type": "chair", "box": (1172, 873, 1267, 941), "back": "top"},
    {"type": "chair", "box": (1018, 1145, 1115, 1220), "back": "bottom"},
    {"type": "chair", "box": (1172, 1145, 1267, 1220), "back": "bottom"},
    {"type": "console", "box": (1220, 1567, 1442, 1628)},
    {"type": "leaf", "hinge": (953, 1540), "len": 202, "angle": -55, "thick": 8},
    # hallway 5,8
    {"type": "closet", "box": (1022, 1646, 1172, 2108), "n": 6, "backSide": "right", "sections": 2},
    {"type": "console", "box": (654, 1294, 704, 1522)},
    {"type": "console", "box": (657, 1782, 704, 1913)},
    {"type": "console", "box": (657, 1960, 702, 2102)},
    {"type": "leaf", "hinge": (698, 2132), "len": 224, "angle": 32, "thick": 12, "dark": True},
    # bathroom 4,2
    {"type": "ledge", "box": (224, 1551, 272, 1759)},
    {"type": "toilet2", "box": (272, 1610, 384, 1700), "face": "right"},
    {"type": "vanity2", "box": (224, 1803, 304, 1907), "basin": (232, 1815, 296, 1895), "faucet": "left"},
    {"type": "washer", "box": (495, 1803, 630, 1942)},
    {"type": "bathtub", "box": (230, 1954, 609, 2102), "mixer": "left"},
    {"type": "leaf", "hinge": (639, 1723), "len": 179, "angle": -56, "thick": 8},
]

if __name__ == "__main__":
    build("p131", items, floors, sys.argv[1], pixel=True)
    print("ok")
