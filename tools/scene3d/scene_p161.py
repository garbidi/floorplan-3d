"""Plan 33/161 (2-room 62,1). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (65, 545, 260, 865)}, {"type": "tile", "box": (65, 905, 390, 1160)}]
items = [
    # bedroom 13,3
    {"type": "glass", "box": (155, 65, 375, 115)},
    {"type": "nightstand", "box": (65, 130, 125, 195)}, {"type": "nightstand", "box": (65, 450, 125, 510)},
    {"type": "bed", "box": (65, 205, 355, 440), "head": "left", "hb": 10},
    {"type": "tv", "box": (450, 245, 462, 425)},
    {"type": "table", "box": (430, 555, 480, 680)}, {"type": "chair", "box": (390, 590, 430, 645), "back": "left"},
    {"type": "closet", "box": (320, 810, 480, 900), "n": 5, "along": True, "backSide": "bottom"},
    L((482, 525), (372, 525)),
    # WC 2,9
    {"type": "shower", "box": (80, 555, 250, 655), "cutX": 250, "cutZ": 655},
    {"type": "vanity2", "box": (80, 680, 125, 755), "basin": (84, 688, 121, 748), "faucet": "left"},
    {"type": "toilet2", "box": (160, 805, 215, 865), "face": "up"},
    L((258, 670), (355, 670)),
    # bathroom 4,3
    {"type": "bathtub", "box": (70, 945, 150, 1150), "mixer": "left"},
    {"type": "vanity2", "box": (155, 1100, 250, 1155), "basin": (178, 1110, 232, 1150), "faucet": "bottom"},
    {"type": "toilet2", "box": (300, 1090, 350, 1155), "face": "up"},
    {"type": "washer", "box": (305, 915, 380, 975)}, {"type": "shaft", "box": (395, 905, 485, 965)},
    L((395, 990), (395, 1080)),
    # living 19,9
    {"type": "glass", "box": (530, 60, 745, 115)}, {"type": "glass", "box": (905, 60, 1120, 115)},
    {"type": "console", "box": (508, 200, 540, 375)}, {"type": "tv", "box": (515, 215, 528, 360)},
    {"type": "sofa", "box": (670, 185, 785, 415), "seats": 2, "backSide": "left", "cushions": [
        {"box": (720, 195, 770, 245), "rot": 20, "color": 0xf3eee6}, {"box": (705, 340, 760, 390), "rot": -15, "color": 0x8c6d55}]},
    {"type": "table", "box": (805, 245, 1005, 360), "plates": [(865, 270), (945, 270), (865, 330), (945, 330)]},
    {"type": "chair", "box": (835, 205, 890, 245), "back": "top"}, {"type": "chair", "box": (920, 205, 975, 245), "back": "top"},
    {"type": "chair", "box": (835, 360, 890, 400), "back": "bottom"}, {"type": "chair", "box": (920, 360, 975, 400), "back": "bottom"},
    {"type": "counter", "box": (635, 575, 1070, 665)},
    {"type": "sink", "box": (755, 585, 835, 655)}, {"type": "cooktop", "box": (965, 580, 1068, 662), "zones": 4},
    {"type": "shaft", "box": (635, 665, 755, 760)},
    # hallway 7,3
    {"type": "closet", "box": (640, 760, 740, 1210), "n": 7, "backSide": "right", "sections": 2},
    {"type": "console", "box": (410, 1140, 495, 1190)},
    L((510, 1210), (510, 1335), dark=True),
    # loggia 3,8
    {"type": "glass", "box": (1435, 60, 1750, 80)}, {"type": "glass", "box": (1735, 60, 1755, 240)},
    {"type": "armchair", "box": (1450, 175, 1515, 245), "rot": 0}, {"type": "armchair", "box": (1605, 155, 1685, 235), "rot": -30},
    {"type": "roundtable", "box": (1535, 190, 1590, 240)},
    L((1180, 145), (1080, 145)),
    # room 10,6
    {"type": "tv", "box": (1320, 300, 1475, 312)},
    {"type": "table", "box": (1495, 285, 1665, 345)}, {"type": "chair", "box": (1540, 345, 1620, 420), "back": "bottom"},
    {"type": "bed1", "box": (1185, 555, 1455, 660), "head": "left"},
    {"type": "closet", "box": (1470, 580, 1670, 660), "n": 7, "along": True, "backSide": "bottom"},
    {"type": "glass", "box": (1735, 345, 1755, 545)},
    L((1180, 485), (1180, 375)),
]

def _sc(d):
    d = dict(d)
    if "box" in d: d["box"] = tuple(O + v * K for v in d["box"])
    if "basin" in d: d["basin"] = tuple(O + v * K for v in d["basin"])
    if "hinge" in d: d["hinge"] = tuple(O + v * K for v in d["hinge"])
    if "len" in d: d["len"] *= K
    if "cutX" in d: d["cutX"] = O + d["cutX"] * K; d["cutZ"] = O + d["cutZ"] * K
    if "cushions" in d: d["cushions"] = [dict(c, box=tuple(O + v * K for v in c["box"])) for c in d["cushions"]]
    return d
items = [_sc(i) for i in items]; floors = [_sc(f) for f in floors]
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((1180, 60, 1755, 255),)]

if __name__ == "__main__":
    build("p161", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
