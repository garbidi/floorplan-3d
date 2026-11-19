"""Plan 33/164 (2-room 48,8). PLAN PIXELS of plans_prepared/p164_clean.png (grid display d -> plan 50+d/0.826)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1109, 904, 1539, 1454)}]
items = [
    # loggia 3,2 (L glazing)
    {"type": "glass", "box": (129, 104, 661, 159)},
    {"type": "glass", "box": (104, 135, 153, 407)},
    {"type": "armchair", "box": (219, 232, 334, 359), "rot": 30},
    {"type": "armchair", "box": (443, 334, 565, 443), "rot": 0},
    {"type": "roundtable", "box": (316, 340, 413, 437)},
    {"type": "plant", "box": (704, 226, 807, 310)},
    {"type": "glass", "box": (359, 456, 601, 498)},
    {"type": "leaf", "hinge": (764, 474), "len": 175, "angle": 90, "thick": 8},
    # bedroom 10,5
    {"type": "nightstand", "box": (201, 552, 298, 649)},
    {"type": "bed", "box": (201, 673, 680, 1055), "head": "left", "hb": 18},
    {"type": "tv", "box": (788, 740, 803, 988)},
    {"type": "glass", "box": (104, 982, 153, 1164)},
    {"type": "closet", "box": (201, 1218, 625, 1333), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (837, 1313), "len": 182, "angle": 180, "thick": 8},
    # room 9,3
    {"type": "glass", "box": (946, 104, 1363, 159)},
    {"type": "bed1", "box": (879, 238, 1327, 419), "head": "left"},
    {"type": "nightstand", "box": (879, 443, 976, 546)},
    {"type": "table", "box": (1430, 462, 1539, 722)},
    {"type": "chair", "box": (1321, 522, 1430, 661), "back": "left"},
    {"type": "closet", "box": (1091, 776, 1539, 885), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (885, 885), "len": 176, "angle": -90, "thick": 8},
    # bathroom 3,8
    {"type": "bathtub", "box": (1158, 904, 1497, 1049), "mixer": "left"},
    {"type": "vanity2", "box": (1158, 1085, 1230, 1212), "basin": (1166, 1100, 1222, 1197), "faucet": "left"},
    {"type": "washer", "box": (1436, 1055, 1533, 1188)},
    {"type": "toilet2", "box": (1158, 1279, 1261, 1364), "face": "right"},
    {"type": "shaft", "box": (1454, 1261, 1533, 1448)},
    {"type": "leaf", "hinge": (1424, 1454), "len": 157, "angle": 90, "thick": 8},
    # kitchen-living 17,2
    {"type": "glass", "box": (104, 1454, 153, 1872)},
    {"type": "table", "box": (407, 1376, 710, 1569), "plates": [(480, 1440), (640, 1440), (500, 1530), (620, 1530)]},
    {"type": "chair", "box": (341, 1418, 407, 1503), "back": "left"},
    {"type": "chair", "box": (710, 1418, 782, 1503), "back": "right"},
    {"type": "chair", "box": (450, 1569, 540, 1636), "back": "bottom"},
    {"type": "chair", "box": (571, 1569, 661, 1636), "back": "bottom"},
    {"type": "counter", "box": (546, 1872, 1406, 2017)},
    {"type": "cooktop", "box": (661, 1876, 843, 2014), "zones": 4},
    {"type": "sink", "box": (1073, 1890, 1212, 1975)},
    {"type": "console", "box": (213, 1940, 456, 1985)},
    {"type": "tv", "box": (225, 1950, 445, 1965)},
    {"type": "shaft", "box": (1406, 1830, 1563, 2017)},
    # hallway 4,8
    {"type": "closet", "box": (1454, 1466, 1902, 1606), "n": 9, "along": True, "backSide": "top"},
    {"type": "console", "box": (1575, 1878, 1654, 2023)},
    {"type": "console", "box": (1854, 1666, 1896, 1866)},
    {"type": "leaf", "hinge": (1678, 2054), "len": 212, "angle": 90, "thick": 12, "dark": True},
]

if __name__ == "__main__":
    build("p164", items, floors, sys.argv[1], pixel=True, inside=[(104, 104, 795, 455)])
    print("ok")
