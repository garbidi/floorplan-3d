"""Plan 33/72 (2-room 48,7). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (990, 880, 1400, 1170)}]
items = [
    # loggia 3,1
    {"type": "glass", "box": (70, 85, 490, 120)}, {"type": "glass", "box": (68, 85, 100, 315)},
    {"type": "plant", "box": (150, 175, 230, 245)}, {"type": "armchair", "box": (490, 180, 590, 280), "rot": -30},
    {"type": "roundtable", "box": (445, 270, 510, 330)}, {"type": "glass", "box": (375, 360, 555, 385)},
    L((243, 370), (243, 505)),
    # bedroom 12,7
    {"type": "closet", "box": (145, 390, 235, 735), "n": 8, "backSide": "left", "sections": 2},
    {"type": "glass", "box": (70, 935, 100, 1070)}, {"type": "tv", "box": (168, 805, 182, 1000)},
    {"type": "bed", "box": (260, 755, 625, 1050), "head": "right", "hb": 10},
    {"type": "nightstand", "box": (560, 660, 635, 735)}, {"type": "nightstand", "box": (560, 1065, 635, 1145)},
    L((650, 488), (790, 488)),
    # kitchen-living 15,6
    {"type": "glass", "box": (720, 85, 995, 120)}, {"type": "glass", "box": (1225, 85, 1545, 120)},
    {"type": "console", "box": (655, 210, 695, 465)}, {"type": "tv", "box": (662, 235, 672, 440)},
    {"type": "table", "box": (890, 265, 1145, 410), "plates": [(965, 300), (1070, 300), (965, 375), (1070, 375)]},
    {"type": "chair", "box": (925, 215, 995, 265), "back": "top"}, {"type": "chair", "box": (1035, 215, 1105, 265), "back": "top"},
    {"type": "chair", "box": (925, 410, 995, 465), "back": "bottom"}, {"type": "chair", "box": (1035, 410, 1105, 465), "back": "bottom"},
    {"type": "counter", "box": (655, 635, 770, 1115)}, {"type": "counter", "box": (770, 1000, 975, 1115)},
    {"type": "cooktop", "box": (660, 670, 768, 795), "zones": 4}, {"type": "sink", "box": (665, 905, 755, 1015)},
    {"type": "console", "box": (1070, 825, 1315, 858)},
    # room 8,7
    {"type": "bed1", "box": (1180, 190, 1535, 330), "head": "left"},
    {"type": "nightstand", "box": (1180, 350, 1260, 430)}, {"type": "tv", "box": (1675, 170, 1690, 365)},
    {"type": "table", "box": (1620, 395, 1710, 600)}, {"type": "chair", "box": (1540, 440, 1620, 550), "back": "left"},
    {"type": "closet", "box": (1160, 435, 1260, 655), "n": 5, "backSide": "left", "sections": 1},
    L((1290, 660), (1290, 515)),
    # bathroom 3,6
    {"type": "bathtub", "box": (995, 900, 1105, 1170), "mixer": "left"},
    {"type": "washer", "box": (1115, 880, 1215, 955)},
    {"type": "vanity2", "box": (1115, 1080, 1235, 1135), "basin": (1135, 1088, 1210, 1130), "faucet": "bottom"},
    {"type": "toilet2", "box": (1285, 1060, 1350, 1135), "face": "up"},
    L((1405, 1025), (1530, 1025)),
    # hallway 5,0
    {"type": "closet", "box": (1615, 665, 1710, 1070), "n": 7, "backSide": "right", "sections": 2},
    {"type": "console", "box": (1635, 1075, 1710, 1175)},
    L((1432, 1205), (1432, 1375), dark=True),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((68, 85, 610, 355),)]

if __name__ == "__main__":
    build("p72", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
