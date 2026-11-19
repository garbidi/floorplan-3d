"""Plan 33/44 (1-room 38,8). PLAN PIXELS of plans_prepared/p44_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1430, 1795, 1950, 2420)}]
items = [
    # loggia 3,8
    {"type": "glass", "box": (340, 425, 870, 505)},
    {"type": "armchair", "box": (220, 650, 400, 820), "rot": 45},
    {"type": "roundtable", "box": (445, 730, 575, 860)},
    {"type": "plant", "box": (820, 540, 1010, 720)},
    {"type": "glass", "box": (530, 875, 740, 912)},
    {"type": "leaf", "hinge": (958, 900), "len": 205, "angle": 90, "thick": 8},
    # bedroom 14,0
    {"type": "nightstand", "box": (195, 985, 320, 1115)},
    {"type": "nightstand", "box": (195, 1665, 320, 1800)},
    {"type": "bed", "box": (205, 1145, 820, 1640), "head": "left", "hb": 20},
    {"type": "tv", "box": (990, 1230, 1015, 1570)},
    {"type": "closet", "box": (192, 1930, 330, 2180), "n": 5, "backSide": "left", "sections": 1},
    {"type": "closet", "box": (192, 2180, 705, 2330), "n": 11, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (570, 2080, 705, 2180), "n": 3, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (730, 2100, 900, 2415), "n": 6, "backSide": "left", "sections": 2},
    {"type": "pouf", "box": (912, 2355, 1092, 2415)},
    {"type": "leaf", "hinge": (1053, 2020), "len": 242, "angle": -122, "thick": 8},
    # kitchen-living 12,5
    {"type": "glass", "box": (1270, 415, 1790, 505)},
    {"type": "console", "box": (1880, 535, 1945, 870)},
    {"type": "tv", "box": (1895, 560, 1915, 845)},
    {"type": "table", "box": (1100, 670, 1303, 1057), "plates": [(1200, 750), (1200, 900), (1200, 1000)]},
    {"type": "chair", "box": (1303, 710, 1385, 830), "back": "right"},
    {"type": "chair", "box": (1303, 855, 1385, 980), "back": "right"},
    {"type": "chair", "box": (1135, 1057, 1255, 1150), "back": "bottom"},
    {"type": "counter", "box": (1755, 885, 1950, 1475)},
    {"type": "cooktop", "box": (1775, 1015, 1948, 1245), "zones": 4},
    {"type": "counter", "box": (1570, 1475, 1950, 1670)},
    {"type": "sink", "box": (1585, 1500, 1770, 1650)},
    {"type": "fridge", "box": (1380, 1478, 1570, 1668)},
    {"type": "leaf", "hinge": (1130, 1675), "len": 236, "angle": -30, "thick": 8},
    # hallway 4,4
    {"type": "console", "box": (1355, 2215, 1420, 2400)},
    {"type": "leaf", "hinge": (1105, 2447), "len": 281, "angle": 31, "thick": 12, "dark": True},
    # bathroom 4,1
    {"type": "washer", "box": (1445, 1805, 1610, 1950)},
    {"type": "ledge", "box": (1885, 1800, 1950, 2195)},
    {"type": "toilet2", "box": (1745, 1955, 1885, 2070), "face": "left"},
    {"type": "shower", "box": (1650, 2195, 1950, 2420), "cutX": 1765, "cutZ": 2310, "corner": "tl"},
    {"type": "vanity2", "box": (1435, 2310, 1650, 2420), "basin": (1490, 2335, 1600, 2405), "faucet": "bottom"},
    {"type": "leaf", "hinge": (1421, 2185), "len": 218, "angle": -123, "thick": 8},
]

if __name__ == "__main__":
    build("p44", items, floors, sys.argv[1], pixel=True)
    print("ok")
