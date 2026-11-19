"""Plan 33/67 (2-room 48,1). PLAN PIXELS of plans_prepared/p65_clean.png (pgrid labels)."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

# coordinates in DISPLAY px of the pgrid image (crop 50,50, scale 0.826) -> plan px via _sc
floors = [{"type": "tile", "box": (880, 895, 1195, 1300)}]
items = [
    # loggia 3,0 (L glazing)
    {"type": "glass", "box": (40, 75, 470, 100)}, {"type": "glass", "box": (35, 75, 60, 300)},
    {"type": "armchair", "box": (320, 245, 420, 340), "rot": 0}, {"type": "armchair", "box": (465, 155, 570, 260), "rot": 25},
    {"type": "roundtable", "box": (430, 255, 500, 325)}, {"type": "glass", "box": (295, 350, 490, 380)},
    L((155, 375), (155, 510)),
    # bedroom 10,5
    {"type": "glass", "box": (35, 495, 60, 645)}, {"type": "tv", "box": (125, 580, 140, 790)},
    {"type": "nightstand", "box": (525, 425, 605, 510)},
    {"type": "bed", "box": (210, 530, 605, 840), "head": "right", "hb": 10},
    {"type": "closet", "box": (100, 990, 395, 1085), "n": 8, "along": True, "backSide": "bottom"},
    L((612, 1075), (462, 1075)),
    # room 12,4
    {"type": "glass", "box": (705, 65, 1050, 135)},
    {"type": "closet", "box": (622, 170, 725, 495), "n": 7, "backSide": "left", "sections": 2},
    {"type": "tv", "box": (640, 505, 655, 715)},
    {"type": "table", "box": (1100, 210, 1195, 425)}, {"type": "chair", "box": (1010, 255, 1100, 380), "back": "left"},
    {"type": "bed1", "box": (1045, 500, 1195, 875), "head": "bottom"},
    {"type": "nightstand", "box": (945, 795, 1030, 875)},
    L((652, 880), (652, 735)),
    # bathroom 3,8
    {"type": "bathtub", "box": (885, 895, 1160, 1005), "mixer": "left"},
    {"type": "vanity2", "box": (880, 1010, 945, 1145), "basin": (886, 1040, 939, 1115), "faucet": "left"},
    {"type": "washer", "box": (1110, 1015, 1195, 1120)},
    {"type": "toilet2", "box": (880, 1180, 970, 1260), "face": "right"},
    L((1130, 1305), (1130, 1440)),
    # kitchen-living 11,5
    {"type": "glass", "box": (25, 1145, 60, 1490)},
    {"type": "table", "box": (270, 1120, 525, 1275), "plates": [(300, 1170), (490, 1170), (345, 1240), (445, 1240)]},
    {"type": "chair", "box": (210, 1145, 270, 1225), "back": "left"}, {"type": "chair", "box": (525, 1145, 585, 1225), "back": "right"},
    {"type": "chair", "box": (305, 1275, 385, 1330), "back": "bottom"}, {"type": "chair", "box": (405, 1275, 485, 1330), "back": "bottom"},
    {"type": "counter", "box": (95, 1495, 685, 1620)},
    {"type": "cooktop", "box": (150, 1500, 295, 1615), "zones": 4}, {"type": "sink", "box": (405, 1510, 520, 1610)},
    {"type": "shaft", "box": (690, 1505, 825, 1620)},
    # hallway 6,9
    {"type": "closet", "box": (825, 1505, 1200, 1620), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (1285, 1195, 1510, 1340), "n": 6, "along": True, "backSide": "top"},
    {"type": "shaft", "box": (1195, 1195, 1285, 1310)},
    {"type": "console", "box": (1200, 1535, 1310, 1620)},
    L((1320, 1645), (1320, 1825), dark=True),
]
K, O = 1 / 0.8260869565217391, 50
def _sc(d):
    d = dict(d)
    for k in ("box", "basin", "hinge"):
        if k in d: d[k] = tuple(O + v * K for v in d[k])
    if "len" in d: d["len"] *= K
    return d
items = [_sc(i) for i in items]; floors = [_sc(f) for f in floors]

if __name__ == "__main__":
    build("p67", items, floors, sys.argv[1], pixel=True, inside=[tuple(int(50 + v / 0.826) for v in (35, 75, 590, 360))])
    print("ok")
