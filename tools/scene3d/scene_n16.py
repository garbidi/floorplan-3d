"""Plan «С 26 квм 15 литер» (n16). All coordinates in PLAN PIXELS of plans_prepared/n16_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (621, 1860, 1190, 2225)}]
items = [
    # loggia (top): corner glazing, partition with glazed panel and door
    {"type": "glass", "box": (1138, 206, 1690, 226)},
    {"type": "glass", "box": (1668, 206, 1690, 482)},
    {"type": "glass", "box": (1166, 558, 1347, 594)},
    {"type": "leaf", "hinge": (1001, 588), "len": 172, "angle": 90, "thick": 7},
    {"type": "plant", "box": (982, 297, 1104, 419)},
    {"type": "roundtable", "box": (1335, 444, 1419, 528)},
    {"type": "armchair", "box": (1474, 399, 1580, 505), "rot": -30},
    # studio
    {"type": "sofa", "box": (1393, 669, 1621, 1097), "seats": 2, "arm": 42, "back": 50, "backSide": "right", "cushions": [
        {"box": (1490, 680, 1560, 750), "rot": 20, "color": 0xf3eee6},
        {"box": (1505, 725, 1575, 795), "rot": -15, "color": 0x8c6d55},
        {"box": (1490, 995, 1560, 1065), "rot": 25, "color": 0xf3eee6}]},
    {"type": "rug", "box": (1182, 669, 1399, 1097)},
    {"type": "tv", "box": (962, 774, 980, 1030)},
    {"type": "glass", "box": (1640, 1069, 1691, 1235)},                  # small window in the right wall
    {"type": "table", "box": (940, 1222, 1100, 1350), "plates": [(1020, 1250), (1020, 1322)]},
    {"type": "chair", "box": (966, 1147, 1060, 1222), "back": "top"},
    {"type": "chair", "box": (966, 1350, 1060, 1425), "back": "bottom"},
    # kitchen: floor units only
    {"type": "shaft", "box": (1451, 1260, 1623, 1363)},
    {"type": "counter", "box": (1463, 1363, 1623, 1658)},
    {"type": "counter", "box": (1215, 1658, 1623, 1813)},
    {"type": "cooktop", "box": (1482, 1447, 1619, 1541), "zones": 2},
    {"type": "sink", "box": (1332, 1680, 1473, 1791)},
    {"type": "fridge", "box": (1068, 1658, 1213, 1813)},
    # vestibule (left wing)
    {"type": "closet", "box": (200, 1538, 334, 1812), "n": 8},
    {"type": "pouf", "box": (567, 1762, 709, 1807)},
    {"type": "leaf", "hinge": (559, 1837), "len": 221, "angle": 148, "thick": 9, "dark": True},
    # bathroom
    {"type": "shaft", "box": (565, 1860, 622, 2250)},
    {"type": "shaft", "box": (990, 1812, 1184, 1916)},
    {"type": "leaf", "hinge": (759, 1822), "len": 161, "angle": -35, "thick": 7},
    {"type": "vanity", "box": (640, 1880, 746, 2030)},
    {"type": "ledge", "box": (1134, 1916, 1188, 2085)},
    {"type": "toilet", "box": (1030, 1954, 1134, 2041)},
    {"type": "washer", "box": (1077, 2085, 1190, 2222)},
    {"type": "shower", "box": (621, 2054, 902, 2225), "cutX": 815, "cutZ": 2135, "corner": "tr"},
]

if __name__ == "__main__":
    build("n16", items, floors, sys.argv[1], pixel=True, inside=[(930, 204, 1692, 560)])
    print("ok")
