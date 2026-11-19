"""Plan 33/149 (1-room 43,3). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (135, 175, 585, 510)}]
items = [
    # bathroom 4,3
    {"type": "glass", "box": (265, 100, 390, 140)},
    {"type": "bathtub", "box": (140, 185, 260, 480), "mixer": "left"},
    {"type": "vanity2", "box": (270, 180, 400, 240), "basin": (295, 188, 375, 232), "faucet": "top"},
    {"type": "ledge", "box": (400, 180, 575, 220)}, {"type": "toilet2", "box": (450, 220, 525, 310), "face": "down"},
    {"type": "washer", "box": (485, 390, 580, 505)}, {"type": "shaft", "box": (585, 175, 700, 510)},
    L((325, 515), (440, 590)),
    # hallway 7,2
    {"type": "closet", "box": (135, 520, 245, 845), "n": 6, "backSide": "left", "sections": 2},
    {"type": "console", "box": (140, 845, 205, 965)},
    L((405, 985), (260, 1080), dark=True),
    # dressing 2,2
    {"type": "closet", "box": (470, 1190, 630, 1310), "n": 4, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (470, 985, 560, 1190), "n": 4, "backSide": "left", "sections": 1},
    {"type": "console", "box": (635, 1050, 688, 1105)},
    L((620, 975), (510, 900)),
    # kitchen-living 15,2
    {"type": "glass", "box": (1445, 100, 1690, 140)}, {"type": "glass", "box": (1650, 100, 1690, 645)},
    {"type": "counter", "box": (705, 175, 1265, 305)}, {"type": "counter", "box": (705, 305, 830, 540)},
    {"type": "sink", "box": (825, 195, 940, 290)}, {"type": "cooktop", "box": (1045, 180, 1200, 300), "zones": 4},
    {"type": "tv", "box": (1280, 195, 1500, 212)},
    {"type": "table", "box": (1325, 440, 1495, 725), "plates": [(1365, 530), (1455, 530), (1365, 650), (1455, 650)]},
    {"type": "chair", "box": (1265, 490, 1325, 570), "back": "left"}, {"type": "chair", "box": (1265, 615, 1325, 695), "back": "left"},
    {"type": "chair", "box": (1495, 490, 1555, 570), "back": "right"}, {"type": "chair", "box": (1495, 615, 1555, 695), "back": "right"},
    L((697, 695), (780, 575)),
    # bedroom 10,6
    {"type": "tv", "box": (930, 785, 1155, 800)},
    {"type": "bed", "box": (870, 885, 1210, 1305), "head": "bottom", "hb": 10},
    {"type": "nightstand", "box": (1230, 1225, 1320, 1310)},
    {"type": "closet", "box": (705, 960, 815, 1310), "n": 7, "backSide": "left", "sections": 2},
    L((697, 790), (780, 915)),
    # loggia 3,8
    {"type": "glass", "box": (1650, 880, 1690, 1220)},
    {"type": "plant", "box": (1475, 795, 1595, 925)}, {"type": "roundtable", "box": (1405, 1075, 1475, 1150)},
    {"type": "armchair", "box": (1435, 1175, 1555, 1300), "rot": 30},
    {"type": "glass", "box": (1355, 945, 1385, 1085)},
    L((1360, 808), (1228, 808)),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((705, 140, 1655, 760), (1445, 100, 1690, 140), (1650, 100, 1690, 645), (1385, 775, 1650, 1310), (1650, 880, 1690, 1220))]

if __name__ == "__main__":
    build("p149", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
