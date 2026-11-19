"""Plan 33/163 (1-room 35,2). PLAN PIXELS of plans_prepared/p163_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1215, 1100, 1555, 1660)}]
items = [
    # loggia 3,1
    {"type": "glass", "box": (295, 140, 755, 215)},
    {"type": "armchair", "box": (245, 345, 395, 495), "rot": 45},
    {"type": "roundtable", "box": (430, 390, 525, 490)},
    {"type": "plant", "box": (760, 260, 875, 375)},
    {"type": "glass", "box": (285, 525, 570, 560)},
    {"type": "leaf", "hinge": (752, 560), "len": 180, "angle": 90, "thick": 8},
    # kitchen-living 15,5
    {"type": "table", "box": (205, 760, 550, 975), "plates": [(290, 815), (435, 815), (290, 920), (435, 920)]},
    {"type": "chair", "box": (245, 680, 335, 760), "back": "top"},
    {"type": "chair", "box": (395, 680, 495, 760), "back": "top"},
    {"type": "chair", "box": (245, 975, 335, 1050), "back": "bottom"},
    {"type": "chair", "box": (395, 975, 495, 1050), "back": "bottom"},
    {"type": "console", "box": (835, 680, 895, 1015)},
    {"type": "tv", "box": (850, 700, 868, 990)},
    {"type": "counter", "box": (205, 1185, 395, 1945)},
    {"type": "cooktop", "box": (210, 1260, 380, 1450), "zones": 4},
    {"type": "sink", "box": (230, 1690, 375, 1840)},
    {"type": "counter", "box": (395, 1795, 575, 1945)},
    {"type": "closet", "box": (685, 1555, 820, 1945), "n": 5, "backSide": "left", "sections": 1},
    # bedroom 10,0
    {"type": "glass", "box": (1075, 140, 1525, 215)},
    {"type": "tv", "box": (980, 450, 998, 735)},
    {"type": "nightstand", "box": (1495, 245, 1555, 360)},
    {"type": "bed", "box": (1095, 380, 1555, 815), "head": "right", "hb": 18},
    {"type": "closet", "box": (1150, 945, 1555, 1100), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (998, 1105), "len": 168, "angle": -90, "thick": 8},
    # hallway 3,0
    {"type": "console", "box": (1035, 1610, 1085, 1725)},
    {"type": "console", "box": (1035, 1745, 1085, 1880)},
    {"type": "leaf", "hinge": (1095, 1995), "len": 230, "angle": 92, "thick": 12, "dark": True},
    # bathroom 3,6
    {"type": "bathtub", "box": (1230, 1135, 1555, 1290), "mixer": "right"},
    {"type": "vanity2", "box": (1460, 1300, 1555, 1435), "basin": (1470, 1335, 1545, 1420), "faucet": "right"},
    {"type": "washer", "box": (1215, 1505, 1360, 1640)},
    {"type": "toilet2", "box": (1390, 1505, 1490, 1640), "face": "up"},
    {"type": "leaf", "hinge": (1195, 1475), "len": 170, "angle": 180, "thick": 8},
]

if __name__ == "__main__":
    build("p163", items, floors, sys.argv[1], pixel=True)
    print("ok")
