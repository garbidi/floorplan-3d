"""Plan «2кк 67 квм литер» (n12). All coordinates in PLAN PIXELS of plans_prepared/n12_clean.png, measured on a grid."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (850, 180, 1125, 480)}, {"type": "tile", "box": (1203, 180, 1540, 480)}]
items = [
    # left loggia
    {"type": "glass", "box": (70, 320, 125, 610)},
    {"type": "glass", "box": (345, 230, 375, 460)},
    {"type": "leaf", "hinge": (380, 715), "len": 100, "angle": 0, "thick": 7},
    {"type": "armchair", "box": (140, 190, 240, 290), "rot": 20},
    {"type": "roundtable", "box": (210, 262, 280, 330)},
    {"type": "nightstand", "box": (227, 279, 263, 313), "power": 0.5},
    {"type": "armchair", "box": (205, 332, 300, 430), "rot": -90},
    {"type": "plant", "box": (140, 795, 262, 895)},
    # left bedroom
    {"type": "nightstand", "box": (405, 185, 490, 255)},
    {"type": "nightstand", "box": (720, 185, 800, 255)},
    {"type": "bed", "box": (485, 185, 740, 522), "head": "top", "hb": 16},
    {"type": "tv", "box": (495, 870, 710, 888)},
    {"type": "closet", "box": (772, 785, 965, 893), "n": 8, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (948, 690), "len": 160, "angle": -118, "thick": 7},
    # WC (left of the pair)
    {"type": "shower", "box": (850, 180, 988, 330), "cutX": 935, "cutZ": 290, "corner": "br"},
    {"type": "ledge", "box": (988, 180, 1125, 225)},
    {"type": "toilet2", "box": (1015, 225, 1098, 310), "face": "down"},
    {"type": "vanity2", "box": (1015, 400, 1112, 480), "basin": (1030, 410, 1098, 470), "faucet": "bottom"},
    {"type": "leaf", "hinge": (880, 488), "len": 115, "angle": -25, "thick": 7},
    {"type": "shaft", "box": (1125, 180, 1203, 480)},
    # bathroom
    {"type": "ledge", "box": (1203, 180, 1400, 225)},
    {"type": "toilet2", "box": (1238, 225, 1318, 310), "face": "down"},
    {"type": "vanity2", "box": (1340, 190, 1428, 250), "basin": (1352, 198, 1416, 244), "faucet": "top"},
    {"type": "washer", "box": (1210, 380, 1310, 480)},
    {"type": "bathtub", "box": (1440, 185, 1535, 440), "mixer": "left"},
    {"type": "leaf", "hinge": (1520, 490), "len": 120, "angle": 155, "thick": 7},
    # right bedroom (children's)
    {"type": "bed1", "box": (1605, 185, 1880, 290), "head": "left"},
    {"type": "nightstand", "box": (1605, 300, 1680, 355)},
    {"type": "closet", "box": (1920, 185, 2230, 290), "n": 10, "along": True, "backSide": "top"},
    {"type": "glass", "box": (2255, 300, 2310, 610)},
    {"type": "table", "box": (2060, 600, 2240, 690)},
    {"type": "chair", "box": (2090, 510, 2200, 600), "back": "top"},
    {"type": "console", "box": (1755, 648, 1995, 688)},
    {"type": "leaf", "hinge": (1605, 685), "len": 130, "angle": -60, "thick": 7},
    # hallway
    {"type": "console", "box": (1000, 500, 1320, 530)},
    {"type": "leaf", "hinge": (1022, 898), "len": 165, "angle": 117, "thick": 9, "dark": True},
    {"type": "pouf", "box": (1047, 1068, 1080, 1150)},
    {"type": "closet", "box": (1215, 910, 1300, 1192), "n": 8, "backSide": "right"},
    # kitchen-living
    {"type": "shaft", "box": (1310, 692, 1402, 782)},
    {"type": "counter", "box": (1310, 782, 1410, 1195)},
    {"type": "counter", "box": (1410, 1072, 1672, 1195)},
    {"type": "fridge", "box": (1310, 790, 1405, 890)},
    {"type": "sink", "box": (1320, 900, 1405, 1062)},
    {"type": "cooktop", "box": (1548, 1075, 1668, 1190), "zones": 4},
    {"type": "console", "box": (1650, 700, 1845, 727)},
    {"type": "tv", "box": (1665, 703, 1830, 716)},
    {"type": "table", "box": (1830, 950, 1970, 1195), "plates": [(1875, 1010), (1925, 1010), (1875, 1135), (1925, 1135)]},
    {"type": "chair", "box": (1780, 990, 1830, 1065), "back": "left"},
    {"type": "chair", "box": (1780, 1090, 1830, 1165), "back": "left"},
    {"type": "chair", "box": (1970, 990, 2020, 1065), "back": "right"},
    {"type": "chair", "box": (1970, 1090, 2020, 1165), "back": "right"},
    {"type": "leaf", "hinge": (1418, 695), "len": 145, "angle": 30, "thick": 7},
    # right loggia
    {"type": "glass", "box": (2290, 840, 2330, 1130)},
    {"type": "glass", "box": (2058, 855, 2078, 985)},
    {"type": "leaf", "hinge": (2062, 737), "len": 108, "angle": 180, "thick": 7},
    {"type": "plant", "box": (2130, 715, 2245, 825)},
    {"type": "roundtable", "box": (2108, 975, 2172, 1040)},
    {"type": "nightstand", "box": (2124, 991, 2156, 1024), "power": 0.5},
    {"type": "armchair", "box": (2108, 1068, 2205, 1165), "rot": 30},
]

if __name__ == "__main__":
    build("n12", items, floors, sys.argv[1], pixel=True)
    print("ok")
