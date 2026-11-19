"""Plan 33/170 (2-room 59,8). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (1100, 955, 1390, 1430)}]
items = [
    # room 11,5 (top-left, L glazing)
    {"type": "glass", "box": (50, 75, 450, 100)}, {"type": "glass", "box": (50, 75, 75, 300)},
    {"type": "bed1", "box": (430, 165, 775, 305), "head": "right"},
    {"type": "nightstand", "box": (700, 320, 775, 400)},
    {"type": "closet", "box": (120, 325, 225, 635), "n": 6, "backSide": "left", "sections": 2},
    {"type": "table", "box": (320, 550, 530, 635)}, {"type": "chair", "box": (370, 460, 475, 550), "back": "top"},
    {"type": "console", "box": (810, 195, 850, 440)}, {"type": "tv", "box": (815, 220, 830, 420)},
    L((805, 485), (805, 620)),
    # bedroom 11,3
    {"type": "glass", "box": (50, 710, 75, 1025)},
    {"type": "console", "box": (145, 655, 305, 690)}, {"type": "tv", "box": (340, 672, 525, 688)},
    {"type": "bed", "box": (285, 765, 570, 1125), "head": "bottom", "hb": 10},
    {"type": "nightstand", "box": (190, 1050, 265, 1125)}, {"type": "nightstand", "box": (585, 1050, 660, 1125)},
    L((805, 820), (805, 680)),
    # living 21,3
    {"type": "glass", "box": (845, 75, 1130, 135)}, {"type": "glass", "box": (1330, 75, 1620, 135)},
    {"type": "sofa", "box": (1095, 175, 1240, 470), "seats": 2, "backSide": "right", "cushions": [
        {"box": (1160, 190, 1215, 245), "rot": 20, "color": 0xf3eee6}, {"box": (1140, 370, 1205, 430), "rot": -15, "color": 0x8c6d55}]},
    {"type": "table", "box": (1095, 795, 1330, 940), "plates": [(1165, 830), (1260, 830), (1125, 885), (1300, 885)]},
    {"type": "chair", "box": (1135, 745, 1200, 795), "back": "top"}, {"type": "chair", "box": (1225, 745, 1295, 795), "back": "top"},
    {"type": "chair", "box": (1045, 840, 1095, 905), "back": "left"}, {"type": "chair", "box": (1330, 840, 1380, 905), "back": "right"},
    {"type": "counter", "box": (1600, 410, 1705, 940)},
    {"type": "cooktop", "box": (1605, 595, 1703, 775), "zones": 4}, {"type": "sink", "box": (1610, 960, 1700, 1080)},
    {"type": "console", "box": (810, 820, 850, 940)},
    # loggia 2,8
    {"type": "plant", "box": (1295, 165, 1370, 240)},
    {"type": "armchair", "box": (1600, 150, 1690, 240), "rot": 0}, {"type": "armchair", "box": (1470, 240, 1555, 330), "rot": 0},
    {"type": "roundtable", "box": (1570, 245, 1630, 305)}, {"type": "glass", "box": (1455, 335, 1605, 355)},
    L((1328, 345), (1328, 480)),
    # dressing 3,6
    {"type": "closet", "box": (820, 955, 970, 1255), "n": 5, "backSide": "left", "sections": 2},
    {"type": "console", "box": (985, 1010, 1030, 1060)},
    {"type": "shaft", "box": (935, 1340, 1050, 1430)},
    L((805, 1095), (805, 965)),
    # bathroom 4,6
    {"type": "toilet2", "box": (1100, 1035, 1180, 1110), "face": "right"}, {"type": "ledge", "box": (1100, 1030, 1110, 1115)},
    {"type": "washer", "box": (1290, 975, 1385, 1070)}, {"type": "console", "box": (1185, 975, 1285, 1005)},
    {"type": "vanity2", "box": (1100, 1190, 1155, 1310), "basin": (1104, 1198, 1151, 1302), "faucet": "left"},
    {"type": "bathtub", "box": (1100, 1325, 1370, 1430), "mixer": "left"},
    L((1395, 1075), (1395, 1195)),
    # hallway 4,7
    {"type": "closet", "box": (1600, 1060, 1705, 1440), "n": 6, "backSide": "right", "sections": 2},
    {"type": "console", "box": (1405, 1320, 1440, 1420)},
    {"type": "shaft", "box": (1590, 950, 1700, 1050)},
    L((1440, 1460), (1440, 1615), dark=True),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((75, 100, 790, 640), (50, 75, 450, 100), (50, 75, 75, 300))]

if __name__ == "__main__":
    build("p170", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
