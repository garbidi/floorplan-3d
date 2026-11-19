"""Plan 33/146 (2-room 66,3). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (700, 1060, 1150, 1355)}, {"type": "tile", "box": (1180, 1195, 1310, 1360)}]
items = [
    # loggia 4,8
    {"type": "glass", "box": (75, 95, 465, 125)}, {"type": "glass", "box": (72, 95, 100, 300)},
    {"type": "armchair", "box": (160, 225, 260, 325), "rot": 30}, {"type": "armchair", "box": (310, 295, 405, 390), "rot": -20},
    {"type": "roundtable", "box": (220, 320, 290, 385)}, {"type": "plant", "box": (500, 180, 605, 280)},
    {"type": "glass", "box": (330, 400, 445, 425)},
    L((565, 410), (565, 535)),
    # kitchen-living 18,1
    {"type": "table", "box": (140, 565, 390, 710), "plates": [(205, 600), (310, 600), (205, 678), (310, 678)]},
    {"type": "chair", "box": (170, 515, 235, 565), "back": "top"}, {"type": "chair", "box": (278, 515, 345, 565), "back": "top"},
    {"type": "chair", "box": (170, 710, 235, 760), "back": "bottom"}, {"type": "chair", "box": (278, 710, 345, 760), "back": "bottom"},
    {"type": "glass", "box": (72, 820, 100, 1110)},
    {"type": "counter", "box": (140, 840, 255, 1355)}, {"type": "counter", "box": (255, 1245, 625, 1355)},
    {"type": "cooktop", "box": (142, 930, 250, 1060), "zones": 4},
    {"type": "sink", "box": (255, 1255, 330, 1340)}, {"type": "sink", "box": (330, 1255, 410, 1340)},
    {"type": "tv", "box": (600, 540, 612, 735)},
    L((635, 1030), (565, 920)),
    # room 14,4
    {"type": "glass", "box": (730, 95, 1020, 155)},
    {"type": "closet", "box": (660, 195, 765, 525), "n": 7, "backSide": "left", "sections": 2},
    {"type": "tv", "box": (665, 540, 678, 735)},
    {"type": "table", "box": (1060, 225, 1150, 440)}, {"type": "chair", "box": (970, 280, 1060, 390), "back": "left"},
    {"type": "bed1", "box": (1010, 515, 1150, 860), "head": "bottom"},
    L((850, 870), (965, 800)),
    # bedroom 14,6
    {"type": "glass", "box": (1285, 95, 1580, 155)},
    {"type": "plant", "box": (1195, 175, 1265, 250)},
    {"type": "nightstand", "box": (1620, 220, 1700, 300)}, {"type": "nightstand", "box": (1620, 620, 1700, 700)},
    {"type": "bed", "box": (1330, 315, 1690, 605), "head": "right", "hb": 10},
    {"type": "tv", "box": (1190, 335, 1215, 580)},
    {"type": "closet", "box": (1350, 765, 1700, 860), "n": 9, "along": True, "backSide": "bottom"},
    L((1210, 870), (1320, 800)),
    # hallway 9,2
    {"type": "console", "box": (1345, 875, 1510, 915)},
    {"type": "closet", "box": (1585, 875, 1700, 1170), "n": 6, "backSide": "right", "sections": 2},
    {"type": "console", "box": (1260, 1060, 1340, 1165)},
    {"type": "washer", "box": (1155, 1065, 1245, 1160)},
    L((1360, 1185), (1490, 1265), dark=True),
    # WC 2,0
    {"type": "shaft", "box": (635, 1060, 700, 1355)},
    {"type": "vanity2", "box": (825, 1110, 885, 1185), "basin": (830, 1115, 880, 1180), "faucet": "right"},
    {"type": "ledge", "box": (715, 1320, 865, 1355)}, {"type": "toilet2", "box": (760, 1240, 825, 1320), "face": "up"},
    L((720, 1060), (820, 995)),
    # bathroom 3,2
    {"type": "bathtub", "box": (905, 1095, 1005, 1355), "mixer": "left"},
    {"type": "vanity2", "box": (1015, 1295, 1150, 1355), "basin": (1045, 1302, 1115, 1350), "faucet": "bottom"},
    {"type": "console", "box": (850, 1018, 1015, 1055)},
    L((1145, 1060), (1045, 995)),
    {"type": "shower", "box": (1185, 1200, 1305, 1355), "cutX": 1305, "cutZ": 1355},
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((100, 125, 625, 400), (75, 95, 465, 125), (72, 95, 100, 300))]

if __name__ == "__main__":
    build("p146", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
