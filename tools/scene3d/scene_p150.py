"""Plan 33/150 (1-room 35,8). PLAN PIXELS of plans_prepared/p150_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1395, 1300, 1900, 1950)}]
items = [
    # loggia 3,8
    {"type": "glass", "box": (380, 230, 870, 300)},
    {"type": "armchair", "box": (270, 390, 420, 560), "rot": 45},
    {"type": "roundtable", "box": (460, 510, 570, 630)},
    {"type": "plant", "box": (830, 330, 1020, 510)},
    {"type": "glass", "box": (560, 660, 760, 690)},
    {"type": "leaf", "hinge": (965, 690), "len": 190, "angle": 90, "thick": 8},
    # bedroom 13,5
    {"type": "nightstand", "box": (222, 750, 345, 880)},
    {"type": "nightstand", "box": (222, 1440, 345, 1570)},
    {"type": "bed", "box": (230, 910, 850, 1415), "head": "left", "hb": 20},
    {"type": "tv", "box": (990, 1000, 1012, 1320)},
    {"type": "console", "box": (222, 1645, 360, 1815)},
    {"type": "closet", "box": (222, 1820, 818, 2015), "n": 12, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (845, 1700, 1060, 2015), "n": 5, "backSide": "left", "sections": 1},
    {"type": "leaf", "hinge": (1048, 1595), "len": 230, "angle": -118, "thick": 8},
    # kitchen 10,0
    {"type": "glass", "box": (1215, 230, 1715, 300)},
    {"type": "table", "box": (1100, 440, 1320, 740), "plates": [(1195, 505), (1195, 675), (1275, 590)]},
    {"type": "chair", "box": (1130, 370, 1260, 440), "back": "top"},
    {"type": "chair", "box": (1130, 740, 1260, 830), "back": "bottom"},
    {"type": "chair", "box": (1320, 545, 1410, 660), "back": "right"},
    {"type": "counter", "box": (1700, 300, 1915, 1060)},
    {"type": "cooktop", "box": (1705, 400, 1912, 630), "zones": 4},
    {"type": "sink", "box": (1720, 840, 1890, 1030)},
    {"type": "counter", "box": (1520, 1015, 1915, 1205)},
    {"type": "fridge", "box": (1335, 1015, 1520, 1205)},
    {"type": "leaf", "hinge": (1106, 1205), "len": 207, "angle": -25, "thick": 8},
    # hallway 4,4
    {"type": "console", "box": (1325, 1720, 1385, 1890)},
    {"type": "leaf", "hinge": (1062, 2030), "len": 270, "angle": 32, "thick": 12, "dark": True},
    # bathroom 4,1
    {"type": "washer", "box": (1410, 1330, 1590, 1460)},
    {"type": "ledge", "box": (1842, 1360, 1900, 1600)},
    {"type": "toilet2", "box": (1700, 1420, 1842, 1530), "face": "left"},
    {"type": "vanity2", "box": (1800, 1620, 1900, 1750), "basin": (1812, 1635, 1890, 1735), "faucet": "right"},
    {"type": "bathtub", "box": (1430, 1755, 1890, 1940), "mixer": "right"},
    {"type": "glass", "box": (1440, 1960, 1900, 2050)},
    {"type": "leaf", "hinge": (1395, 1715), "len": 213, "angle": -120, "thick": 8},
]

if __name__ == "__main__":
    build("p150", items, floors, sys.argv[1], pixel=True)
    print("ok")
