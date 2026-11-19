"""Plan 33/132 (2-room 58,3). PLAN PIXELS of plans_prepared/p65_clean.png (pgrid labels)."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

# coordinates in DISPLAY px of the pgrid image -> plan px via _sc
floors = []
items = [
    # bedroom 13,0
    {"type": "glass", "box": (625, 75, 880, 120)},
    {"type": "closet", "box": (500, 120, 595, 510), "n": 7, "backSide": "left", "sections": 2},
    {"type": "tv", "box": (890, 140, 1085, 155)},
    {"type": "bed", "box": (820, 275, 1120, 645), "head": "bottom", "hb": 10},
    {"type": "nightstand", "box": (735, 765, 815, 845)}, {"type": "nightstand", "box": (1135, 765, 1215, 845)},
    L((720, 655), (655, 570)),
    # loggia 3,8 (L glazing)
    {"type": "glass", "box": (1325, 55, 1550, 85)}, {"type": "glass", "box": (1520, 55, 1550, 455)},
    {"type": "plant", "box": (1355, 155, 1465, 265)},
    {"type": "armchair", "box": (1280, 400, 1370, 490), "rot": 0}, {"type": "armchair", "box": (1385, 535, 1475, 625), "rot": 0},
    {"type": "roundtable", "box": (1310, 510, 1370, 570)},
    {"type": "glass", "box": (1245, 300, 1270, 430)},
    L((1250, 170), (1120, 170)),
    # hallway 6,6
    {"type": "closet", "box": (500, 660, 540, 1150), "n": 7, "backSide": "left", "sections": 3},
    # room 12,9
    {"type": "bed1", "box": (755, 660, 1110, 800), "head": "left"},
    {"type": "nightstand", "box": (755, 815, 835, 890)},
    {"type": "table", "box": (1210, 675, 1425, 765)}, {"type": "chair", "box": (1265, 765, 1365, 860), "back": "bottom"},
    {"type": "glass", "box": (1520, 740, 1555, 1055)},
    {"type": "console", "box": (860, 1455, 1105, 1495)}, {"type": "tv", "box": (885, 1468, 1080, 1480)},
    {"type": "closet", "box": (1120, 1395, 1450, 1495), "n": 8, "along": True, "backSide": "bottom"},
    L((750, 1030), (830, 1165)),
    # dressing 4,1
    {"type": "closet", "box": (100, 1165, 485, 1265), "n": 8, "along": True, "backSide": "top"},
    {"type": "console", "box": (105, 1375, 140, 1475)},
    L((135, 1500), (165, 1590), dark=True),
    # kitchen-living 13,7
    {"type": "glass", "box": (1520, 1300, 1555, 1555)},
    {"type": "table", "box": (1195, 1235, 1345, 1480), "plates": [(1230, 1270), (1310, 1270), (1230, 1395), (1310, 1395)]},
    {"type": "chair", "box": (1140, 1260, 1195, 1330), "back": "left"}, {"type": "chair", "box": (1140, 1370, 1195, 1440), "back": "left"},
    {"type": "chair", "box": (1345, 1260, 1400, 1330), "back": "right"}, {"type": "chair", "box": (1345, 1370, 1400, 1440), "back": "right"},
]
K, O = 1 / 0.8260869565217391, 50  # p71: s computed below
def _sc(d):
    d = dict(d)
    for k in ("box", "basin", "hinge"):
        if k in d: d[k] = tuple(O + v * K for v in d[k])
    if "len" in d: d["len"] *= K
    return d
def _fy(d):
    d = dict(d); f = lambda y: (y - 50) * 0.8260869565217391
    for k in ("box", "basin"):
        if k in d: b = d[k]; d[k] = (b[0], f(b[1]), b[2], f(b[3]))
    if "hinge" in d: h = d["hinge"]; d["hinge"] = (h[0], f(h[1]))
    return d
def _needs(d):
    b = d.get("box") or (d["hinge"][0], d["hinge"][1], 0, d["hinge"][1])
    return b[1] >= 1390 and not (d.get("type") == "glass" or d.get("type") in ("table", "chair") or (d.get("type") == "closet" and b[0] < 200) or (d.get("type") == "console" and b[0] < 200))
items = [_sc(_fy(i) if _needs(i) else i) for i in items]
def LP(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=7, **kw)
# kitchen + bathroom: PLAN px (labels)
floors = [{"type": "tile", "box": (450, 1836, 952, 2223)}]
items += [
    {"type": "shaft", "box": (952, 1836, 1037, 2223)},
    {"type": "counter", "box": (1037, 1836, 1176, 2223)}, {"type": "counter", "box": (1176, 2108, 1569, 2223)},
    {"type": "sink", "box": (1050, 1990, 1165, 2100)}, {"type": "cooktop", "box": (1340, 2112, 1503, 2220), "zones": 4},
    {"type": "tv", "box": (1600, 2195, 1835, 2210)},
    {"type": "bathtub", "box": (480, 1854, 607, 2217), "mixer": "left"},
    {"type": "washer", "box": (843, 1854, 946, 1963)},
    {"type": "vanity2", "box": (637, 2163, 728, 2223), "basin": (647, 2168, 718, 2218), "faucet": "bottom"},
    {"type": "toilet2", "box": (795, 2108, 879, 2211), "face": "up"},
    LP((825, 1842), (698, 1763)),
]

if __name__ == "__main__":
    build("p132", items, floors, sys.argv[1], pixel=True, inside=[tuple(int(50 + v / 0.826) for v in (1270, 85, 1525, 640))])
    print("ok")
