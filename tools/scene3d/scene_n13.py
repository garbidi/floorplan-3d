"""Plan «3кк 79 квм 14 литер» (n13). All coordinates in PLAN PIXELS of plans_prepared/n13_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (244, 1160, 595, 1790)}, {"type": "tile", "box": (607, 1395, 905, 1790)}]
items = [
    # bedroom (left)
    {"type": "glass", "box": (440, 130, 800, 185)},
    {"type": "nightstand", "box": (244, 318, 325, 409)},
    {"type": "nightstand", "box": (244, 782, 325, 882)},
    {"type": "bed", "box": (250, 427, 680, 773), "head": "left", "hb": 18},
    {"type": "table", "box": (780, 218, 862, 400)},
    {"type": "chair", "box": (725, 262, 780, 355), "back": "left"},
    {"type": "tv", "box": (835, 473, 852, 709)},
    {"type": "closet", "box": (244, 1027, 635, 1155), "n": 14, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (690, 1150), "len": 135, "angle": -62, "thick": 7},
    # children's room
    {"type": "glass", "box": (1110, 130, 1480, 185)},
    {"type": "table", "box": (898, 263, 998, 518)},
    {"type": "chair", "box": (998, 327, 1107, 454), "back": "right"},
    {"type": "console", "box": (898, 573, 944, 864)},
    {"type": "closet", "box": (1395, 236, 1516, 682), "n": 9, "backSide": "right"},
    {"type": "bed1", "box": (1344, 727, 1516, 1127), "head": "bottom"},
    {"type": "nightstand", "box": (1234, 1045, 1298, 1127)},
    {"type": "leaf", "hinge": (915, 1150), "len": 140, "angle": -32, "thick": 7},
    # living room
    {"type": "glass", "box": (1705, 130, 2100, 185)},
    {"type": "glass", "box": (2718, 364, 2755, 755)},
    {"type": "sofa", "box": (2080, 218, 2665, 390), "seats": 3, "arm": 40, "back": 50, "cushions": [
        {"box": (2130, 240, 2215, 320), "rot": 20, "color": 0xf3eee6},
        {"box": (2180, 250, 2260, 330), "rot": -10, "color": 0x8c6d55},
        {"box": (2560, 245, 2640, 325), "rot": 25, "color": 0xf3eee6}]},
    {"type": "table", "box": (2295, 445, 2455, 555)},
    {"type": "console", "box": (2200, 776, 2564, 827)},
    {"type": "tv", "box": (2220, 785, 2545, 800)},
    {"type": "table", "box": (1718, 367, 1918, 718), "plates": [(1785, 445), (1855, 445), (1785, 615), (1855, 615), (1818, 690)]},
    {"type": "chair", "box": (1655, 430, 1718, 515), "back": "left"},
    {"type": "chair", "box": (1655, 555, 1718, 640), "back": "left"},
    {"type": "chair", "box": (1918, 430, 1981, 515), "back": "right"},
    {"type": "chair", "box": (1918, 555, 1981, 640), "back": "right"},
    {"type": "chair", "box": (1778, 718, 1860, 790), "back": "bottom"},
    # kitchen (bottom run)
    {"type": "shaft", "box": (1536, 1363, 1636, 1482)},
    {"type": "counter", "box": (1636, 1363, 2400, 1482)},
    {"type": "fridge", "box": (1645, 1366, 1773, 1480)},
    {"type": "sink", "box": (1873, 1375, 1968, 1475)},
    {"type": "sink", "box": (1968, 1375, 2064, 1475)},
    {"type": "cooktop", "box": (2209, 1370, 2391, 1478), "zones": 4},
    {"type": "leaf", "hinge": (1560, 1180), "len": 160, "angle": 115, "thick": 7},
    # loggia
    {"type": "glass", "box": (2403, 1082, 2430, 1300)},
    {"type": "glass", "box": (2736, 1009, 2773, 1391)},
    {"type": "leaf", "hinge": (2400, 927), "len": 145, "angle": 180, "thick": 7},
    {"type": "plant", "box": (2555, 909, 2680, 1055)},
    {"type": "roundtable", "box": (2455, 1227, 2545, 1309)},
    {"type": "nightstand", "box": (2480, 1248, 2520, 1288), "power": 0.5},
    {"type": "armchair", "box": (2463, 1336, 2610, 1464), "rot": 30},
    # bathroom
    {"type": "washer", "box": (244, 1164, 353, 1280)},
    {"type": "washer", "box": (244, 1284, 353, 1391)},
    {"type": "vanity2", "box": (244, 1400, 307, 1525), "basin": (250, 1415, 301, 1510), "faucet": "left"},
    {"type": "vanity2", "box": (244, 1529, 307, 1645), "basin": (250, 1542, 301, 1632), "faucet": "left"},
    {"type": "bathtub", "box": (244, 1655, 562, 1782), "mixer": "left"},
    {"type": "leaf", "hinge": (603, 1372), "len": 170, "angle": -75, "thick": 7},
    # WC
    {"type": "vanity2", "box": (616, 1482, 680, 1582), "basin": (622, 1492, 674, 1572), "faucet": "left"},
    {"type": "shaft", "box": (607, 1618, 671, 1764)},
    {"type": "ledge", "box": (707, 1736, 871, 1782)},
    {"type": "toilet2", "box": (740, 1630, 838, 1736), "face": "up"},
    {"type": "leaf", "hinge": (735, 1395), "len": 125, "angle": -35, "thick": 7},
    # hallway
    {"type": "pouf", "box": (916, 1527, 962, 1645)},
    {"type": "console", "box": (916, 1380, 962, 1518)},
    {"type": "closet", "box": (1162, 1382, 1300, 1790), "n": 9, "backSide": "left"},
    {"type": "leaf", "hinge": (925, 1792), "len": 190, "angle": 30, "thick": 9, "dark": True},
]

if __name__ == "__main__":
    build("n13", items, floors, sys.argv[1], pixel=True)
    print("ok")
