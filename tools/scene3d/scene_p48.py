"""Plan 33/48 (3-room 82,3). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (685, 88, 1180, 292)}]
items = [
    # loggia 3,8 (left, L glazing)
    {"type": "glass", "box": (45, 42, 195, 60)}, {"type": "glass", "box": (45, 42, 65, 320)},
    {"type": "armchair", "box": (145, 95, 215, 165), "rot": 30}, {"type": "roundtable", "box": (170, 180, 220, 225)},
    {"type": "plant", "box": (95, 330, 170, 405)}, {"type": "glass", "box": (228, 155, 245, 290)},
    L((240, 375), (320, 375)),
    # bedroom 13,6
    {"type": "nightstand", "box": (272, 90, 325, 140)}, {"type": "nightstand", "box": (540, 90, 595, 140)},
    {"type": "bed", "box": (330, 90, 530, 335), "head": "top", "hb": 12},
    {"type": "closet", "box": (612, 90, 665, 300), "n": 7, "backSide": "right", "sections": 1},
    {"type": "console", "box": (365, 398, 495, 414)}, {"type": "tv", "box": (370, 402, 490, 408)},
    L((890, 408), (842, 322)),
    # bathroom 3,2
    {"type": "shower", "box": (690, 90, 775, 205), "cutX": 740, "cutZ": 170},
    {"type": "vanity2", "box": (690, 225, 730, 290), "basin": (694, 232, 726, 284), "faucet": "left"},
    {"type": "toilet2", "box": (815, 108, 860, 165), "face": "down"},
    {"type": "shaft", "box": (900, 90, 935, 220)},
    L((835, 297), (762, 340)),
    # bathroom 4,1
    {"type": "toilet2", "box": (975, 108, 1018, 165), "face": "down"},
    {"type": "vanity2", "box": (1048, 90, 1100, 128), "basin": (1055, 94, 1093, 122), "faucet": "top"},
    {"type": "bathtub", "box": (1100, 90, 1175, 272), "mixer": "left"},
    {"type": "washer", "box": (900, 228, 960, 290)},
    L((1088, 297), (1015, 340)),
    # living 14,3 (top-right, L glazing)
    {"type": "glass", "box": (1605, 42, 1755, 60)}, {"type": "glass", "box": (1735, 42, 1755, 320)},
    {"type": "sofa", "box": (1275, 90, 1605, 190), "seats": 3, "backSide": "top", "cushions": [
        {"box": (1295, 110, 1340, 155), "rot": 20, "color": 0xf3eee6}, {"box": (1530, 105, 1575, 150), "rot": -15, "color": 0x8c6d55}]},
    {"type": "table", "box": (1395, 228, 1480, 282)},
    {"type": "console", "box": (1350, 405, 1550, 435)}, {"type": "tv", "box": (1360, 418, 1540, 424)},
    {"type": "plant", "box": (1625, 345, 1695, 410)},
    L((1185, 410), (1235, 340)),
    # room 14,0
    {"type": "console", "box": (1290, 445, 1450, 468)}, {"type": "tv", "box": (1295, 452, 1445, 458)},
    {"type": "closet", "box": (1465, 445, 1680, 515), "n": 8, "along": True, "backSide": "top"},
    {"type": "glass", "box": (1715, 500, 1755, 710)},
    {"type": "bed1", "box": (1200, 680, 1435, 775), "head": "left"},
    {"type": "nightstand", "box": (1200, 620, 1250, 670)},
    {"type": "table", "box": (1505, 715, 1650, 775)}, {"type": "chair", "box": (1540, 655, 1610, 715), "back": "top"},
    L((1185, 458), (1232, 545)),
    # hallway 10,2
    {"type": "closet", "box": (820, 445, 895, 635), "n": 6, "backSide": "left", "sections": 2},
    {"type": "console", "box": (1155, 580, 1178, 740)},
    L((1020, 642), (930, 700), dark=True),
    L((1065, 780), (1150, 830)),
    # kitchen-living 14,9
    {"type": "table", "box": (1305, 785, 1405, 950), "plates": [(1330, 830), (1380, 830), (1330, 900), (1380, 900)]},
    {"type": "chair", "box": (1270, 800, 1305, 850), "back": "left"}, {"type": "chair", "box": (1270, 875, 1305, 925), "back": "left"},
    {"type": "chair", "box": (1405, 800, 1440, 850), "back": "right"}, {"type": "chair", "box": (1405, 875, 1440, 925), "back": "right"},
    {"type": "counter", "box": (1060, 1085, 1410, 1175)}, {"type": "counter", "box": (1060, 990, 1130, 1085)},
    {"type": "sink", "box": (1090, 1095, 1145, 1150)}, {"type": "sink", "box": (1145, 1095, 1200, 1150)},
    {"type": "cooktop", "box": (1285, 1088, 1395, 1170), "zones": 4},
    {"type": "shaft", "box": (1060, 920, 1110, 990)},
    {"type": "console", "box": (1415, 1140, 1550, 1162)}, {"type": "tv", "box": (1420, 1148, 1545, 1153)},
    # loggia 4,2 (bottom-right)
    {"type": "glass", "box": (1715, 860, 1755, 1070)}, {"type": "plant", "box": (1640, 810, 1705, 880)},
    {"type": "armchair", "box": (1580, 975, 1640, 1030), "rot": 0}, {"type": "armchair", "box": (1635, 1085, 1705, 1150), "rot": -30},
    {"type": "roundtable", "box": (1595, 1045, 1640, 1090)},
    {"type": "glass", "box": (1555, 915, 1565, 1025)},
    L((1560, 830), (1480, 830)),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((65, 60, 230, 430), (1605, 60, 1735, 430), (1565, 805, 1715, 1175))]

if __name__ == "__main__":
    build("p48", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
