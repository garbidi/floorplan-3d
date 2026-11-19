"""Plan 33/64 (2-room 54,8). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (105, 578, 275, 885)}, {"type": "tile", "box": (305, 578, 530, 855)}]
items = [
    # bedroom 11,1
    {"type": "glass", "box": (185, 70, 390, 105)},
    {"type": "bed", "box": (80, 145, 360, 370), "head": "left", "hb": 10},
    {"type": "nightstand", "box": (80, 385, 130, 445)},
    {"type": "tv", "box": (493, 180, 503, 330)},
    {"type": "closet", "box": (275, 485, 480, 570), "n": 8, "along": True, "backSide": "bottom"},
    L((530, 465), (430, 465)),
    # WC/bath 3,0
    L((172, 575), (172, 478)),
    {"type": "vanity2", "box": (105, 580, 150, 675), "basin": (110, 590, 145, 665), "faucet": "left"},
    {"type": "toilet2", "box": (105, 700, 165, 755), "face": "right"},
    {"type": "shower", "box": (105, 785, 275, 885), "cutX": 275, "cutZ": 885},
    # bath 3,6
    {"type": "bathtub", "box": (310, 580, 505, 665), "mixer": "left"},
    {"type": "vanity2", "box": (305, 665, 345, 745), "basin": (309, 675, 341, 735), "faucet": "left"},
    {"type": "washer", "box": (305, 775, 365, 855)},
    {"type": "toilet2", "box": (450, 795, 500, 855), "face": "up"},
    L((540, 778), (635, 778)),
    # living 19,8
    {"type": "glass", "box": (570, 70, 780, 105)}, {"type": "glass", "box": (938, 70, 1145, 105)},
    {"type": "console", "box": (545, 155, 575, 350)}, {"type": "tv", "box": (552, 180, 562, 330)},
    {"type": "sofa", "box": (705, 145, 820, 370), "seats": 2, "backSide": "left", "cushions": [
        {"box": (755, 160, 800, 205), "rot": 20, "color": 0xf3eee6}, {"box": (740, 300, 790, 345), "rot": -15, "color": 0x8c6d55}]},
    {"type": "table", "box": (835, 205, 1030, 315), "plates": [(895, 230), (975, 230), (895, 290), (975, 290)]},
    {"type": "chair", "box": (870, 165, 920, 205), "back": "top"}, {"type": "chair", "box": (955, 165, 1005, 205), "back": "top"},
    {"type": "chair", "box": (870, 315, 920, 355), "back": "bottom"}, {"type": "chair", "box": (955, 315, 1005, 355), "back": "bottom"},
    {"type": "counter", "box": (710, 560, 1110, 640)},
    {"type": "sink", "box": (825, 570, 905, 635)},
    {"type": "cooktop", "box": (1005, 565, 1105, 638), "zones": 4},
    {"type": "shaft", "box": (710, 645, 820, 740)},
    # hallway 2,9
    {"type": "closet", "box": (720, 745, 800, 890), "n": 4, "backSide": "right", "sections": 1},
    {"type": "console", "box": (545, 810, 585, 885)},
    L((590, 910), (590, 1035), dark=True),
    # loggia 3,8
    {"type": "glass", "box": (1465, 50, 1765, 70)}, {"type": "glass", "box": (1755, 50, 1775, 230)},
    {"type": "armchair", "box": (1485, 165, 1550, 230), "rot": 0}, {"type": "armchair", "box": (1635, 140, 1710, 220), "rot": -30},
    {"type": "roundtable", "box": (1570, 180, 1620, 225)},
    L((1215, 132), (1120, 132)),
    # room 10,6
    {"type": "tv", "box": (1365, 285, 1515, 295)},
    {"type": "table", "box": (1530, 270, 1700, 335)}, {"type": "chair", "box": (1575, 335, 1660, 405), "back": "bottom"},
    {"type": "bed1", "box": (1225, 535, 1495, 645), "head": "left"},
    {"type": "closet", "box": (1505, 560, 1700, 645), "n": 7, "along": True, "backSide": "bottom"},
    {"type": "glass", "box": (1755, 365, 1775, 610)},
    L((1218, 465), (1218, 360)),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((1215, 50, 1775, 235),)]

if __name__ == "__main__":
    build("p64", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
