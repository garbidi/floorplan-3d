"""Plan 33/147 (1-room 39,0). PLAN PIXELS of plans_prepared/p147_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1475, 1385, 1975, 2030)}]
items = [
    # loggia 3,8
    {"type": "glass", "box": (365, 220, 870, 305)},
    {"type": "plant", "box": (230, 360, 405, 540)},
    {"type": "roundtable", "box": (610, 505, 730, 630)},
    {"type": "armchair", "box": (780, 420, 960, 600), "rot": -40},
    {"type": "glass", "box": (480, 655, 685, 695)},
    {"type": "leaf", "hinge": (280, 692), "len": 200, "angle": 90, "thick": 8},
    # kitchen-living 13,9
    {"type": "tv", "box": (245, 900, 270, 1225)},
    {"type": "table", "box": (610, 870, 1025, 1115), "plates": [(725, 935), (910, 935), (725, 1050), (910, 1050)]},
    {"type": "chair", "box": (665, 785, 785, 870), "back": "top"},
    {"type": "chair", "box": (850, 785, 970, 870), "back": "top"},
    {"type": "chair", "box": (665, 1115, 785, 1205), "back": "bottom"},
    {"type": "chair", "box": (850, 1115, 970, 1205), "back": "bottom"},
    {"type": "counter", "box": (212, 1270, 410, 2030)},
    {"type": "cooktop", "box": (215, 1390, 405, 1615), "zones": 4},
    {"type": "counter", "box": (410, 1850, 615, 2030)},
    {"type": "sink", "box": (405, 1860, 580, 2010)},
    {"type": "fridge", "box": (615, 1850, 800, 2030)},
    {"type": "console", "box": (830, 1635, 1110, 1700)},
    {"type": "closet", "box": (935, 1710, 1130, 2030), "n": 5, "backSide": "left", "sections": 1},
    # bedroom 13,3
    {"type": "glass", "box": (1270, 220, 1770, 305)},
    {"type": "tv", "box": (1085, 700, 1105, 1030)},
    {"type": "table", "box": (1108, 350, 1185, 620)},
    {"type": "chair", "box": (1185, 420, 1260, 550), "back": "right"},
    {"type": "nightstand", "box": (1855, 435, 1975, 565)},
    {"type": "bed", "box": (1350, 595, 1975, 1080), "head": "right", "hb": 20},
    {"type": "closet", "box": (1380, 1210, 1975, 1375), "n": 12, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (1148, 1380), "len": 212, "angle": -30, "thick": 8},
    # hallway 4,2
    {"type": "console", "box": (1405, 1820, 1465, 1990)},
    {"type": "leaf", "hinge": (1421, 2065), "len": 258, "angle": 149, "thick": 12, "dark": True},
    # bathroom 3,8
    {"type": "washer", "box": (1495, 1395, 1665, 1550)},
    {"type": "ledge", "box": (1915, 1530, 1975, 1800)},
    {"type": "toilet2", "box": (1780, 1600, 1915, 1730), "face": "left"},
    {"type": "shower", "box": (1690, 1810, 1975, 2030), "cutX": 1790, "cutZ": 1910, "corner": "tl"},
    {"type": "vanity2", "box": (1495, 1930, 1690, 2030), "basin": (1535, 1945, 1645, 2010), "faucet": "bottom"},
    {"type": "leaf", "hinge": (1481, 1810), "len": 204, "angle": -123, "thick": 8},
]

if __name__ == "__main__":
    build("p147", items, floors, sys.argv[1], pixel=True)
    print("ok")
