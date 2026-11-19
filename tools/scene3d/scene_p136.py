"""Plan 33/136 (1-room 43,9). PLAN PIXELS of plans_prepared/p136_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1010, 1730, 1500, 2280)}]
items = [
    # kitchen-living 17,0
    {"type": "glass", "box": (280, 160, 680, 240)},
    {"type": "sofa", "box": (157, 190, 342, 563), "seats": 2, "backSide": "left", "cushions": [
        {"box": (200, 225, 290, 315), "rot": 20, "color": 0xf3eee6}, {"box": (185, 430, 260, 500), "rot": -10, "color": 0x8c6d55},
        {"box": (180, 495, 260, 555), "rot": 25, "color": 0xf3eee6}]},
    {"type": "table", "box": (443, 303, 548, 470)},
    {"type": "tv", "box": (800, 360, 818, 600)},
    {"type": "plant", "box": (700, 670, 810, 790)},
    {"type": "table", "box": (660, 880, 830, 1070), "plates": [(745, 935), (745, 1015)]},
    {"type": "chair", "box": (700, 820, 795, 880), "back": "top"},
    {"type": "chair", "box": (700, 1070, 795, 1140), "back": "bottom"},
    {"type": "counter", "box": (157, 645, 308, 1415)},
    {"type": "cooktop", "box": (160, 860, 295, 1030), "zones": 4},
    {"type": "sink", "box": (180, 1260, 292, 1395)},
    {"type": "counter", "box": (308, 1300, 430, 1415)},
    {"type": "leaf", "hinge": (800, 1386), "len": 182, "angle": -149, "thick": 8},
    # loggia 3,8
    {"type": "glass", "box": (955, 160, 1370, 240)},
    {"type": "plant", "box": (1350, 265, 1490, 390)},
    {"type": "roundtable", "box": (1090, 410, 1180, 500)},
    {"type": "armchair", "box": (1195, 380, 1340, 520), "rot": -40},
    {"type": "glass", "box": (1070, 515, 1265, 545)},
    {"type": "leaf", "hinge": (893, 530), "len": 180, "angle": 90, "thick": 8},
    # bedroom 11,6
    {"type": "tv", "box": (880, 810, 900, 1070)},
    {"type": "nightstand", "box": (1395, 630, 1490, 730)},
    {"type": "nightstand", "box": (1395, 1105, 1490, 1210)},
    {"type": "bed", "box": (1040, 745, 1490, 1100), "head": "right", "hb": 18},
    {"type": "closet", "box": (1095, 1260, 1490, 1385), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (881, 1386), "len": 177, "angle": -32, "thick": 8},
    # hallway 6,7
    {"type": "closet", "box": (1095, 1400, 1490, 1520), "n": 8, "along": True, "backSide": "top"},
    {"type": "console", "box": (1340, 1545, 1415, 1640)},
    {"type": "console", "box": (640, 1600, 690, 1880)},
    {"type": "console", "box": (980, 1720, 1030, 1890)},
    {"type": "leaf", "hinge": (945, 1905), "len": 201, "angle": 146, "thick": 12, "dark": True},
    {"type": "leaf", "hinge": (1224, 1665), "len": 164, "angle": -148, "thick": 8},
    # bathroom 4,8
    {"type": "ledge", "box": (1445, 1760, 1500, 1965)},
    {"type": "toilet2", "box": (1310, 1820, 1445, 1925), "face": "left"},
    {"type": "vanity2", "box": (1415, 1985, 1500, 2080), "basin": (1425, 1995, 1490, 2070), "faucet": "right"},
    {"type": "washer", "box": (1020, 2110, 1140, 2240)},
    {"type": "bathtub", "box": (1145, 2100, 1500, 2240), "mixer": "right"},
]

if __name__ == "__main__":
    build("p136", items, floors, sys.argv[1], pixel=True)
    print("ok")
