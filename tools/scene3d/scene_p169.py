"""Plan 33/169 (1-room 33,9). PLAN PIXELS of plans_prepared/p169_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (220, 1460, 655, 2045)}]
items = [
    # loggia 3,1
    {"type": "glass", "box": (290, 145, 740, 215)},
    {"type": "armchair", "box": (230, 330, 380, 480), "rot": 45},
    {"type": "roundtable", "box": (420, 390, 510, 480)},
    {"type": "plant", "box": (745, 270, 840, 365)},
    {"type": "glass", "box": (375, 515, 610, 545)},
    {"type": "leaf", "hinge": (788, 540), "len": 175, "angle": 90, "thick": 8},
    # kitchen 9,3
    {"type": "table", "box": (200, 710, 525, 880), "plates": [(270, 760), (405, 760), (480, 795)]},
    {"type": "chair", "box": (235, 635, 335, 710), "back": "top"},
    {"type": "chair", "box": (370, 635, 470, 710), "back": "top"},
    {"type": "chair", "box": (525, 735, 595, 830), "back": "right"},
    {"type": "tv", "box": (835, 820, 855, 1110)},
    {"type": "counter", "box": (200, 880, 365, 1350)},
    {"type": "cooktop", "box": (205, 920, 360, 1110), "zones": 4},
    {"type": "counter", "box": (365, 1170, 670, 1350)},
    {"type": "sink", "box": (380, 1185, 515, 1330)},
    # bedroom 11,2
    {"type": "glass", "box": (1025, 145, 1480, 215)},
    {"type": "tv", "box": (980, 470, 1000, 720)},
    {"type": "nightstand", "box": (1490, 300, 1595, 405)},
    {"type": "nightstand", "box": (1490, 865, 1595, 975)},
    {"type": "bed", "box": (1110, 420, 1595, 830), "head": "right", "hb": 18},
    {"type": "closet", "box": (1170, 1025, 1595, 1185), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (1157, 1200), "len": 180, "angle": -90, "thick": 8},
    # hallway 6,5
    {"type": "closet", "box": (1030, 1555, 1170, 2035), "n": 6, "backSide": "right", "sections": 2},
    {"type": "console", "box": (690, 1440, 740, 1660)},
    {"type": "console", "box": (690, 1880, 740, 2020)},
    {"type": "leaf", "hinge": (715, 2085), "len": 235, "angle": 90, "thick": 12, "dark": True},
    # bathroom 3,8
    {"type": "bathtub", "box": (230, 1500, 645, 1660), "mixer": "left"},
    {"type": "vanity2", "box": (220, 1660, 335, 1790), "basin": (232, 1675, 322, 1775), "faucet": "left"},
    {"type": "toilet2", "box": (220, 1865, 365, 1960), "face": "right"},
    {"type": "washer", "box": (520, 1860, 655, 2010)},
    {"type": "leaf", "hinge": (668, 1680), "len": 178, "angle": 0, "thick": 8},
]

if __name__ == "__main__":
    build("p169", items, floors, sys.argv[1], pixel=True)
    print("ok")
