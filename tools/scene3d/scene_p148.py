"""Plan 33/148 (2-room 56,0). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (960, 1035, 1290, 1210)}, {"type": "tile", "box": (1360, 840, 1660, 1210)}]
items = [
    # loggia 3,8
    {"type": "glass", "box": (210, 95, 510, 130)},
    {"type": "armchair", "box": (125, 215, 230, 325), "rot": 40}, {"type": "roundtable", "box": (245, 275, 320, 345)},
    {"type": "plant", "box": (460, 170, 580, 275)}, {"type": "glass", "box": (315, 365, 440, 390)},
    L((565, 385), (565, 505)),
    # kitchen-living 14,8
    {"type": "console", "box": (120, 420, 165, 615)}, {"type": "tv", "box": (128, 440, 138, 595)},
    {"type": "table", "box": (370, 580, 625, 730), "plates": [(440, 615), (550, 615), (440, 695), (550, 695)]},
    {"type": "chair", "box": (405, 525, 475, 580), "back": "top"}, {"type": "chair", "box": (515, 525, 585, 580), "back": "top"},
    {"type": "chair", "box": (405, 730, 475, 785), "back": "bottom"}, {"type": "chair", "box": (515, 730, 585, 785), "back": "bottom"},
    {"type": "counter", "box": (115, 630, 230, 1210)}, {"type": "counter", "box": (230, 1095, 560, 1210)},
    {"type": "cooktop", "box": (118, 770, 225, 905), "zones": 4},
    {"type": "sink", "box": (170, 1110, 250, 1195)}, {"type": "sink", "box": (250, 1110, 335, 1195)},
    {"type": "shaft", "box": (565, 1025, 625, 1170)},
    L((635, 995), (560, 880)),
    # room 12,2
    {"type": "glass", "box": (720, 95, 1030, 155)},
    {"type": "table", "box": (640, 205, 730, 430)}, {"type": "chair", "box": (730, 265, 825, 375), "back": "right"},
    {"type": "closet", "box": (1025, 205, 1130, 445), "n": 5, "backSide": "right", "sections": 1},
    {"type": "tv", "box": (1100, 460, 1115, 660)},
    {"type": "bed1", "box": (640, 470, 785, 825), "head": "bottom"}, {"type": "nightstand", "box": (800, 750, 885, 830)},
    L((1085, 835), (965, 765)),
    # bedroom 12,5
    {"type": "glass", "box": (1240, 95, 1725, 130)}, {"type": "glass", "box": (1700, 95, 1725, 310)},
    {"type": "glass", "box": (1660, 585, 1725, 700)},
    {"type": "plant", "box": (1575, 180, 1645, 255)},
    {"type": "nightstand", "box": (1165, 200, 1245, 280)}, {"type": "nightstand", "box": (1165, 615, 1245, 695)},
    {"type": "bed", "box": (1165, 300, 1550, 605), "head": "left", "hb": 10},
    {"type": "tv", "box": (1625, 350, 1640, 550)},
    {"type": "closet", "box": (1315, 730, 1660, 830), "n": 8, "along": True, "backSide": "bottom"},
    L((1170, 835), (1285, 765)),
    # hallway 6,8
    {"type": "console", "box": (770, 840, 940, 885)}, {"type": "console", "box": (640, 1000, 675, 1110)},
    {"type": "closet", "box": (845, 1030, 955, 1205), "n": 4, "backSide": "right", "sections": 1},
    L((805, 1225), (670, 1310), dark=True),
    # WC 1,9
    {"type": "vanity2", "box": (968, 1085, 1025, 1165), "basin": (973, 1092, 1020, 1158), "faucet": "left"},
    {"type": "ledge", "box": (1250, 1050, 1290, 1205)}, {"type": "toilet2", "box": (1165, 1095, 1250, 1165), "face": "left"},
    {"type": "shaft", "box": (1290, 1035, 1360, 1205)},
    L((1160, 1035), (1055, 970)),
    # bathroom 4,0
    {"type": "washer", "box": (1560, 845, 1650, 945)},
    {"type": "vanity2", "box": (1600, 985, 1655, 1055), "basin": (1605, 990, 1650, 1050), "faucet": "right"},
    {"type": "bathtub", "box": (1385, 1095, 1655, 1205), "mixer": "right"},
    {"type": "console", "box": (1360, 840, 1455, 875)},
    {"type": "glass", "box": (1660, 970, 1725, 1085)},
    L((1355, 1000), (1290, 890)),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((1165, 130, 1700, 830), (1240, 95, 1725, 130), (1700, 95, 1725, 310))]

if __name__ == "__main__":
    build("p148", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
