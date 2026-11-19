"""Plan 33/145 (2-room 68,7). Coordinates read in DISPLAY px of the pgrid image (crop 50,50; s=0.7826) -> plan px via _sc."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
K, O = 1 / 0.7826, 50

def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (640, 100, 795, 320)}, {"type": "tile", "box": (855, 100, 1080, 320)}]
items = [
    # bedroom 15,8 (left, L glazing)
    {"type": "glass", "box": (40, 55, 200, 72)}, {"type": "glass", "box": (40, 55, 62, 405)},
    {"type": "console", "box": (230, 100, 410, 130)}, {"type": "tv", "box": (240, 108, 400, 114)},
    {"type": "plant", "box": (105, 120, 165, 175)},
    {"type": "bed", "box": (220, 245, 440, 525), "head": "bottom", "hb": 10},
    {"type": "nightstand", "box": (150, 470, 210, 525)}, {"type": "nightstand", "box": (450, 470, 510, 525)},
    {"type": "closet", "box": (548, 100, 620, 330), "n": 7, "backSide": "right", "sections": 1},
    L((637, 455), (590, 372)),
    # WC 2,5
    {"type": "ledge", "box": (660, 100, 770, 128)}, {"type": "toilet2", "box": (690, 128, 740, 190), "face": "down"},
    {"type": "vanity2", "box": (645, 240, 690, 298), "basin": (650, 246, 685, 292), "faucet": "left"},
    L((680, 322), (760, 370)),
    # bathroom 3,4
    {"type": "shaft", "box": (798, 100, 850, 225)},
    {"type": "washer", "box": (858, 105, 928, 165)},
    {"type": "vanity2", "box": (935, 100, 990, 145), "basin": (942, 104, 983, 140), "faucet": "top"},
    {"type": "bathtub", "box": (998, 105, 1075, 300), "mixer": "left"},
    L((865, 322), (945, 372)),
    # room 15,3 (top-right, L glazing)
    {"type": "glass", "box": (1590, 52, 1745, 72)}, {"type": "glass", "box": (1725, 52, 1750, 365)},
    {"type": "glass", "box": (1370, 65, 1450, 100)},
    {"type": "bed1", "box": (1105, 105, 1365, 210), "head": "left"},
    {"type": "nightstand", "box": (1105, 220, 1160, 280)},
    {"type": "table", "box": (1605, 125, 1700, 285)}, {"type": "chair", "box": (1530, 170, 1605, 250), "back": "left"},
    {"type": "closet", "box": (1470, 385, 1665, 460), "n": 7, "along": True, "backSide": "bottom"},
    {"type": "console", "box": (1215, 445, 1395, 470)}, {"type": "tv", "box": (1225, 452, 1385, 458)},
    {"type": "plant", "box": (1405, 410, 1460, 465)},
    L((1097, 462), (1150, 372)),
    # kitchen-living 17,1
    {"type": "glass", "box": (665, 52, 745, 100)}, {"type": "glass", "box": (885, 52, 965, 100)}, {"type": "glass", "box": (445, 52, 525, 100)},
    {"type": "table", "box": (1080, 505, 1290, 580), "plates": [(1130, 540), (1240, 540)]},
    {"type": "chair", "box": (1045, 505, 1080, 555), "back": "left"}, {"type": "chair", "box": (1290, 505, 1325, 555), "back": "right"},
    {"type": "chair", "box": (1115, 580, 1165, 615), "back": "bottom"}, {"type": "chair", "box": (1175, 580, 1220, 615), "back": "bottom"},
    {"type": "tv", "box": (1315, 495, 1460, 503)},
    {"type": "table", "box": (1335, 610, 1435, 665)},
    {"type": "sofa", "box": (1275, 735, 1495, 840), "seats": 2, "backSide": "bottom", "cushions": [
        {"box": (1290, 765, 1335, 810), "rot": 20, "color": 0xf3eee6}, {"box": (1440, 775, 1485, 820), "rot": -15, "color": 0x8c6d55}]},
    {"type": "counter", "box": (835, 575, 915, 840)}, {"type": "counter", "box": (915, 755, 1205, 840)},
    {"type": "sink", "box": (840, 675, 905, 745)}, {"type": "sink", "box": (840, 745, 905, 800)},
    {"type": "cooktop", "box": (1065, 760, 1165, 838), "zones": 4},
    {"type": "shaft", "box": (825, 480, 890, 575)},
    L((940, 478), (1020, 535)),
    # loggia 3,8 (bottom-right)
    {"type": "glass", "box": (1725, 515, 1750, 695)},
    {"type": "plant", "box": (1615, 505, 1690, 585)}, {"type": "roundtable", "box": (1560, 690, 1610, 735)},
    {"type": "armchair", "box": (1585, 755, 1665, 835), "rot": 30},
    {"type": "glass", "box": (1535, 600, 1550, 760)},
    L((1535, 515), (1450, 515)),
    # hallway 5,5
    {"type": "closet", "box": (555, 535, 640, 845), "n": 6, "backSide": "left", "sections": 2},
    {"type": "console", "box": (790, 670, 825, 765)}, {"type": "console", "box": (795, 765, 820, 840)},
    L((770, 855), (665, 915), dark=True),
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
INSIDE = [tuple(int(O + v * K) for v in b) for b in ((62, 72, 640, 530), (40, 55, 200, 72), (40, 55, 62, 405), (1100, 72, 1725, 470), (1590, 52, 1750, 72), (1725, 52, 1750, 365), (1550, 505, 1725, 850), (1725, 515, 1750, 695))]

if __name__ == "__main__":
    build("p145", items, floors, sys.argv[1], pixel=True, inside=INSIDE)
    print("ok")
