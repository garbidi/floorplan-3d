"""Plan «1кк 38 квм 14 литер» (n07). All coordinates in PLAN PIXELS of plans_prepared/n07_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (145, 1405, 605, 1900)}]
items = [
    # kitchen-living
    {"type": "glass", "box": (290, 262, 719, 340)},
    {"type": "tv", "box": (183, 371, 201, 636)},
    {"type": "table", "box": (676, 450, 854, 679), "plates": [(765, 505), (765, 625), (712, 565)]},
    {"type": "chair", "box": (726, 379, 826, 450), "back": "top"},
    {"type": "chair", "box": (726, 679, 826, 743), "back": "bottom"},
    {"type": "chair", "box": (604, 521, 676, 621), "back": "left"},
    {"type": "counter", "box": (145, 650, 311, 1171)},
    {"type": "counter", "box": (145, 1171, 469, 1321)},
    {"type": "cooktop", "box": (148, 743, 304, 921), "zones": 4},
    {"type": "sink", "box": (297, 1186, 440, 1307)},
    {"type": "fridge", "box": (469, 1171, 619, 1321)},
    {"type": "console", "box": (826, 821, 880, 1157)},
    {"type": "leaf", "hinge": (660, 1392), "len": 172, "angle": 27, "thick": 7},
    # loggia
    {"type": "glass", "box": (1014, 262, 1450, 340)},
    {"type": "glass", "box": (1143, 638, 1321, 670)},
    {"type": "leaf", "hinge": (964, 671), "len": 165, "angle": 90, "thick": 7},
    {"type": "plant", "box": (940, 364, 1090, 500)},
    {"type": "roundtable", "box": (1304, 521, 1393, 610)},
    {"type": "nightstand", "box": (1327, 544, 1370, 587), "power": 0.5},
    {"type": "armchair", "box": (1440, 462, 1570, 596), "rot": -30},
    # bedroom
    {"type": "nightstand", "box": (1500, 729, 1600, 829)},
    {"type": "nightstand", "box": (1500, 1264, 1600, 1364)},
    {"type": "bed", "box": (1107, 850, 1600, 1236), "head": "right", "hb": 18},
    {"type": "tv", "box": (930, 929, 947, 1186)},
    {"type": "closet", "box": (1150, 1420, 1603, 1552), "n": 14, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (945, 1560), "len": 190, "angle": -33, "thick": 7},
    # hallway
    {"type": "closet", "box": (1480, 1570, 1603, 1795), "n": 7, "backSide": "right"},
    {"type": "closet", "box": (1330, 1795, 1603, 1900), "n": -1, "sections": 1, "along": True, "backSide": "bottom"},
    {"type": "basket", "box": (1375, 1820, 1440, 1875)},
    {"type": "console", "box": (1160, 1850, 1330, 1900)},
    {"type": "pouf", "box": (1020, 1852, 1160, 1900)},
    {"type": "console", "box": (625, 1850, 760, 1900)},
    {"type": "leaf", "hinge": (768, 1920), "len": 225, "angle": 35, "thick": 9, "dark": True},
    # bathroom
    {"type": "shaft", "box": (145, 1370, 605, 1405)},
    {"type": "washer", "box": (460, 1405, 600, 1525)},
    {"type": "ledge", "box": (145, 1435, 205, 1635)},
    {"type": "toilet2", "box": (205, 1490, 310, 1580), "face": "right"},
    {"type": "shower", "box": (145, 1665, 330, 1900), "cutX": 245, "cutZ": 1755, "corner": "tr"},
    {"type": "vanity2", "box": (330, 1820, 600, 1900), "basin": (425, 1830, 510, 1895), "faucet": "bottom"},
    {"type": "leaf", "hinge": (610, 1750), "len": 175, "angle": -59, "thick": 7},
]

if __name__ == "__main__":
    build("n07", items, floors, sys.argv[1], pixel=True, inside=[])
    print("ok")
