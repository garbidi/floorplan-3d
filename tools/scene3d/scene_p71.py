"""Plan 33/71 (1-room 34,8). PLAN PIXELS of plans_prepared/p65_clean.png (pgrid labels)."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

# coordinates in DISPLAY px of the pgrid image -> plan px via _sc
floors = [{"type": "tile", "box": (1005, 1070, 1375, 1595)}]
items = [
    # loggia 3,0
    {"type": "glass", "box": (215, 100, 615, 185)},
    {"type": "armchair", "box": (180, 280, 305, 405), "rot": 40}, {"type": "roundtable", "box": (340, 320, 420, 400)},
    {"type": "plant", "box": (600, 205, 690, 300)}, {"type": "glass", "box": (250, 440, 470, 465)},
    L((630, 470), (630, 620)),
    # kitchen-living 12,1
    {"type": "table", "box": (140, 645, 430, 805), "plates": [(210, 685), (325, 685), (395, 725)]},
    {"type": "chair", "box": (170, 580, 255, 645), "back": "top"}, {"type": "chair", "box": (290, 580, 375, 645), "back": "top"},
    {"type": "chair", "box": (430, 685, 495, 770), "back": "right"},
    {"type": "tv", "box": (705, 680, 718, 920)},
    {"type": "counter", "box": (140, 860, 285, 1470)}, {"type": "counter", "box": (285, 1330, 460, 1470)},
    {"type": "cooktop", "box": (145, 870, 280, 1025), "zones": 4}, {"type": "sink", "box": (160, 1180, 270, 1310)},
    {"type": "shaft", "box": (465, 1325, 570, 1460)},
    {"type": "shaft", "box": (95, 1480, 525, 1600)},
    # bedroom 11,6
    {"type": "glass", "box": (895, 100, 1295, 185)},
    {"type": "tv", "box": (800, 440, 815, 685)},
    {"type": "nightstand", "box": (1300, 260, 1395, 355)},
    {"type": "bed", "box": (935, 375, 1395, 740), "head": "right", "hb": 10},
    {"type": "closet", "box": (975, 910, 1395, 1050), "n": 9, "along": True, "backSide": "bottom"},
    L((790, 1060), (790, 890)),
    # hallway 4,1
    {"type": "closet", "box": (575, 1325, 715, 1645), "n": 6, "backSide": "left", "sections": 2},
    {"type": "console", "box": (945, 1515, 990, 1645)},
    L((730, 1680), (730, 1880), dark=True),
    # bathroom 4,0
    {"type": "bathtub", "box": (1010, 1080, 1375, 1205), "mixer": "right"},
    {"type": "vanity2", "box": (1305, 1215, 1375, 1365), "basin": (1312, 1250, 1368, 1330), "faucet": "right"},
    {"type": "console", "box": (1005, 1415, 1050, 1500)},
    {"type": "toilet2", "box": (1130, 1500, 1210, 1595), "face": "up"},
    {"type": "washer", "box": (1245, 1500, 1370, 1595)},
    L((1000, 1405), (845, 1405)),
]
K, O = 1 / 0.8260869565217391, 50  # p71: s computed below
def _sc(d):
    d = dict(d)
    for k in ("box", "basin", "hinge"):
        if k in d: d[k] = tuple(O + v * K for v in d[k])
    if "len" in d: d["len"] *= K
    return d
items = [_sc(i) for i in items]; floors = [_sc(f) for f in floors]

if __name__ == "__main__":
    build("p71", items, floors, sys.argv[1], pixel=True)
    print("ok")
