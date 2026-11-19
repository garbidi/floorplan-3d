"""Plan «2кк 51 квм 14 литер» (n11). All coordinates in PLAN PIXELS of plans_prepared/n11_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (1658, 975, 2025, 1370)}, {"type": "tile", "box": (1198, 1195, 1583, 1400)}]
items = [
    # loggia
    {"type": "glass", "box": (308, 150, 675, 223)},
    {"type": "glass", "box": (425, 470, 573, 507)},
    {"type": "leaf", "hinge": (717, 507), "len": 143, "angle": 90, "thick": 7},
    {"type": "armchair", "box": (212, 320, 337, 445), "rot": 30},
    {"type": "roundtable", "box": (362, 378, 445, 462)},
    {"type": "nightstand", "box": (383, 399, 424, 441), "power": 0.5},
    {"type": "plant", "box": (620, 245, 753, 370)},
    # bedroom (left)
    {"type": "nightstand", "box": (187, 553, 267, 687)},
    {"type": "nightstand", "box": (187, 1003, 267, 1145)},
    {"type": "bed", "box": (190, 662, 603, 995), "head": "left", "hb": 16},
    {"type": "tv", "box": (737, 703, 757, 887)},
    {"type": "console", "box": (187, 1170, 273, 1278)},
    {"type": "closet", "box": (187, 1278, 778, 1400), "n": 18, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (778, 1187), "len": 179, "angle": -118, "thick": 7},
    # middle room (children's)
    {"type": "glass", "box": (920, 150, 1290, 223)},
    {"type": "table", "box": (803, 262, 907, 503)},
    {"type": "chair", "box": (907, 320, 1015, 445), "back": "right"},
    {"type": "bed1", "box": (803, 520, 948, 912), "head": "bottom"},
    {"type": "nightstand", "box": (965, 820, 1057, 907)},
    {"type": "closet", "box": (1290, 262, 1407, 520), "n": 7, "backSide": "right"},
    {"type": "console", "box": (1353, 528, 1407, 803)},
    {"type": "leaf", "hinge": (1340, 925), "len": 167, "angle": -148, "thick": 7},
    # kitchen (right)
    {"type": "glass", "box": (1538, 150, 1900, 223)},
    {"type": "table", "box": (1433, 337, 1717, 500), "plates": [(1516, 380), (1641, 380), (1516, 458), (1641, 458)]},
    {"type": "chair", "box": (1475, 278, 1558, 337), "back": "top"},
    {"type": "chair", "box": (1600, 278, 1683, 337), "back": "top"},
    {"type": "chair", "box": (1475, 500, 1558, 562), "back": "bottom"},
    {"type": "chair", "box": (1600, 500, 1683, 562), "back": "bottom"},
    {"type": "tv", "box": (1995, 233, 2013, 453)},
    {"type": "counter", "box": (1897, 462, 2025, 787)},
    {"type": "counter", "box": (1750, 787, 2025, 912)},
    {"type": "cooktop", "box": (1900, 503, 2022, 670), "zones": 4},
    {"type": "sink", "box": (1753, 795, 1892, 903)},
    {"type": "fridge", "box": (1622, 787, 1750, 912)},
    {"type": "leaf", "hinge": (1450, 912), "len": 153, "angle": -29, "thick": 7},
    # hallway
    {"type": "console", "box": (790, 937, 1065, 970)},
    {"type": "pouf", "box": (790, 1190, 828, 1395)},
    {"type": "closet", "box": (1010, 1195, 1182, 1400), "n": 7, "backSide": "right"},
    {"type": "leaf", "hinge": (873, 1410), "len": 190, "angle": 35, "thick": 9, "dark": True},
    # shafts
    {"type": "shaft", "box": (1667, 920, 2025, 975)},
    {"type": "shaft", "box": (1583, 1187, 1658, 1320)},
    # WC
    {"type": "vanity2", "box": (1198, 1253, 1273, 1353), "basin": (1205, 1262, 1266, 1344), "faucet": "left"},
    {"type": "ledge", "box": (1542, 1210, 1583, 1350)},
    {"type": "toilet2", "box": (1442, 1253, 1542, 1345), "face": "left"},
    {"type": "leaf", "hinge": (1432, 1187), "len": 150, "angle": -146, "thick": 7},
    # bathroom
    {"type": "washer", "box": (1900, 987, 2025, 1103)},
    {"type": "bathtub", "box": (1667, 1203, 2025, 1337), "mixer": "right"},
    {"type": "leaf", "hinge": (1663, 1162), "len": 152, "angle": -118, "thick": 7},
]

if __name__ == "__main__":
    build("n11", items, floors, sys.argv[1], pixel=True)
    print("ok")
