"""Plan 33/162 (1-room 37,1). PLAN PIXELS of plans_prepared/p162_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (205, 1500, 795, 1920)}]
items = [
    # loggia 3,1
    {"type": "glass", "box": (245, 140, 700, 215)},
    {"type": "armchair", "box": (255, 340, 405, 490), "rot": 45},
    {"type": "roundtable", "box": (445, 385, 540, 490)},
    {"type": "plant", "box": (755, 245, 855, 355)},
    {"type": "glass", "box": (285, 515, 575, 558)},
    {"type": "leaf", "hinge": (752, 552), "len": 180, "angle": 90, "thick": 8},
    # bedroom 10,0
    {"type": "nightstand", "box": (207, 640, 310, 750)},
    {"type": "bed", "box": (210, 770, 720, 1180), "head": "left", "hb": 18},
    {"type": "tv", "box": (840, 830, 860, 1105)},
    {"type": "closet", "box": (207, 1290, 665, 1435), "n": 10, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (888, 1392), "len": 188, "angle": 180, "thick": 8},
    # kitchen-living 14,1
    {"type": "glass", "box": (1020, 140, 1465, 215)},
    {"type": "sofa", "box": (943, 265, 1148, 680), "seats": 2, "backSide": "left", "cushions": [
        {"box": (970, 290, 1050, 370), "rot": 20, "color": 0xf3eee6}, {"box": (970, 560, 1050, 640), "rot": -15, "color": 0x8c6d55}]},
    {"type": "console", "box": (1570, 305, 1625, 625)},
    {"type": "tv", "box": (1585, 330, 1605, 600)},
    {"type": "table", "box": (905, 830, 1265, 1035), "plates": [(995, 880), (1150, 880), (995, 985), (1150, 985)]},
    {"type": "chair", "box": (945, 760, 1045, 830), "back": "top"},
    {"type": "chair", "box": (1100, 760, 1195, 830), "back": "top"},
    {"type": "chair", "box": (945, 1035, 1045, 1115), "back": "bottom"},
    {"type": "chair", "box": (1100, 1035, 1195, 1115), "back": "bottom"},
    {"type": "counter", "box": (1460, 715, 1625, 1440)},
    {"type": "cooktop", "box": (1475, 760, 1622, 950), "zones": 4},
    {"type": "sink", "box": (1480, 1135, 1600, 1280)},
    {"type": "counter", "box": (1360, 1270, 1625, 1440)},
    {"type": "fridge", "box": (1205, 1270, 1360, 1440)},
    # hallway 6,0
    {"type": "console", "box": (1570, 1630, 1625, 1760)},
    {"type": "console", "box": (1570, 1760, 1625, 1910)},
    {"type": "leaf", "hinge": (1600, 1995), "len": 215, "angle": 90, "thick": 12, "dark": True},
    # bathroom 3,9
    {"type": "bathtub", "box": (215, 1525, 355, 1890), "mixer": "left"},
    {"type": "washer", "box": (365, 1500, 515, 1610)},
    {"type": "vanity2", "box": (365, 1825, 545, 1920), "basin": (400, 1838, 505, 1905), "faucet": "bottom"},
    {"type": "toilet2", "box": (625, 1765, 720, 1920), "face": "up"},
    {"type": "leaf", "hinge": (808, 1588), "len": 170, "angle": 0, "thick": 8},
]

if __name__ == "__main__":
    build("p162", items, floors, sys.argv[1], pixel=True)
    print("ok")
