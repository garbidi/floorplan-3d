"""Plan 33/130 (3-room 74,9). PLAN PIXELS of plans_prepared/p130_clean.png (pgrid labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (4137, 2321, 4851, 3179)}, {"type": "tile", "box": (2684, 2393, 3253, 3107)}]
items = [
    # loggia 4,6 (top-left, L glazing)
    {"type": "glass", "box": (310, 145, 795, 205)},
    {"type": "glass", "box": (310, 145, 365, 1000)},
    {"type": "glass", "box": (1100, 790, 1130, 905)},
    {"type": "armchair", "box": (650, 330, 860, 560), "rot": 20},
    {"type": "roundtable", "box": (880, 440, 1020, 575)},
    {"type": "nightstand", "box": (920, 480, 980, 540), "power": 0.5},
    {"type": "armchair", "box": (900, 610, 1100, 810), "rot": -95},
    {"type": "plant", "box": (490, 940, 720, 1160)},
    {"type": "leaf", "hinge": (1115, 1172), "len": 255, "angle": 180, "thick": 8},
    # kitchen 9,4
    {"type": "glass", "box": (1240, 160, 1600, 330)},
    {"type": "counter", "box": (1185, 330, 2275, 575)},
    {"type": "counter", "box": (2270, 330, 2500, 1262)},
    {"type": "cooktop", "box": (1620, 335, 1900, 560), "zones": 4},
    {"type": "sink", "box": (2290, 590, 2478, 760)},
    {"type": "sink", "box": (2290, 765, 2478, 925)},
    # living 16,2
    {"type": "glass", "box": (315, 1500, 462, 2170)},
    {"type": "console", "box": (545, 1265, 1185, 1360)},
    {"type": "tv", "box": (600, 1290, 1130, 1310)},
    {"type": "table", "box": (770, 1700, 1050, 1880)},
    {"type": "sofa", "box": (560, 2050, 1300, 2360), "seats": 2, "backSide": "bottom", "cushions": [
        {"box": (620, 2140, 730, 2250), "rot": 20, "color": 0xf3eee6}, {"box": (1080, 2150, 1190, 2260), "rot": -10, "color": 0x8c6d55},
        {"box": (1170, 2140, 1270, 2240), "rot": 25, "color": 0xf3eee6}]},
    {"type": "table", "box": (1580, 1265, 1930, 1810), "plates": [(1690, 1395), (1810, 1395), (1690, 1650), (1810, 1650)]},
    {"type": "chair", "box": (1465, 1340, 1580, 1480), "back": "left"},
    {"type": "chair", "box": (1465, 1590, 1580, 1730), "back": "left"},
    {"type": "chair", "box": (1930, 1340, 2045, 1480), "back": "right"},
    {"type": "chair", "box": (1930, 1590, 2045, 1730), "back": "right"},
    {"type": "console", "box": (1500, 2280, 2020, 2360)},
    {"type": "leaf", "hinge": (2530, 2295), "len": 330, "angle": -123, "thick": 8},
    # room 12,9
    {"type": "glass", "box": (2805, 160, 3490, 300)},
    {"type": "table", "box": (2650, 467, 2757, 920)},
    {"type": "chair", "box": (2757, 580, 2957, 807), "back": "right"},
    {"type": "closet", "box": (3450, 427, 3672, 1120), "n": 9, "backSide": "right"},
    {"type": "console", "box": (3590, 1140, 3672, 1653)},
    {"type": "bed1", "box": (2580, 1160, 2870, 1890), "head": "bottom"},
    {"type": "nightstand", "box": (2905, 1735, 3073, 1888)},
    {"type": "leaf", "hinge": (3580, 1905), "len": 300, "angle": -147, "thick": 8},
    # bedroom 14,3
    {"type": "glass", "box": (3960, 170, 4630, 300)},
    {"type": "table", "box": (3743, 380, 3877, 713)},
    {"type": "chair", "box": (3877, 473, 3970, 627), "back": "right"},
    {"type": "tv", "box": (3757, 863, 3787, 1273)},
    {"type": "bed", "box": (4057, 767, 4817, 1380), "head": "right", "hb": 22},
    {"type": "nightstand", "box": (4700, 570, 4830, 740)},
    {"type": "nightstand", "box": (4700, 1415, 4830, 1600)},
    {"type": "plant", "box": (4650, 360, 4790, 520)},
    {"type": "closet", "box": (4137, 1925, 4851, 2150), "n": 14, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (3762, 1905), "len": 300, "angle": -34, "thick": 8},
    # hallway 10,1
    {"type": "console", "box": (2648, 1933, 3172, 2005)},
    {"type": "closet", "box": (3280, 2363, 3460, 3188), "n": 10, "backSide": "left"},
    {"type": "console", "box": (3480, 3107, 3685, 3188)},
    {"type": "console", "box": (4020, 2620, 4101, 3107)},
    {"type": "leaf", "hinge": (3710, 3215), "len": 350, "angle": 34, "thick": 12, "dark": True},
    # WC 2,6
    {"type": "console", "box": (2684, 2411, 2757, 2718)},
    {"type": "vanity2", "box": (3127, 2465, 3244, 2628), "basin": (3140, 2480, 3230, 2615), "faucet": "right"},
    {"type": "ledge", "box": (2765, 3034, 3082, 3107)},
    {"type": "toilet2", "box": (2856, 2863, 2991, 3034), "face": "up"},
    {"type": "leaf", "hinge": (2785, 2385), "len": 285, "angle": -35, "thick": 8},
    # bathroom 4,8
    {"type": "ledge", "box": (4760, 2340, 4851, 2650)},
    {"type": "toilet2", "box": (4589, 2430, 4760, 2565), "face": "left"},
    {"type": "vanity2", "box": (4715, 2727, 4832, 2881), "basin": (4725, 2740, 4820, 2868), "faucet": "right"},
    {"type": "washer", "box": (4146, 2718, 4345, 2926)},
    {"type": "bathtub", "box": (4255, 2944, 4832, 3160), "mixer": "right"},
    {"type": "leaf", "hinge": (4110, 2605), "len": 275, "angle": -119, "thick": 8},
]

if __name__ == "__main__":
    build("p130", items, floors, sys.argv[1], pixel=True, inside=[(365, 205, 1120, 1200)])
    print("ok")
