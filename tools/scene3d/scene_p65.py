"""Plan 33/65 (studio 23,2). PLAN PIXELS of plans_prepared/p65_clean.png (pgrid labels)."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (500, 1360, 935, 1945)}]
items = [
    {"type": "glass", "box": (700, 145, 1170, 210)},
    {"type": "sofa", "box": (445, 295, 690, 765), "seats": 2, "backSide": "left", "cushions": [
        {"box": (500, 310, 580, 390), "rot": 20, "color": 0xf3eee6}, {"box": (485, 650, 570, 730), "rot": -15, "color": 0x8c6d55}]},
    {"type": "rug", "box": (690, 295, 935, 765)},
    {"type": "table", "box": (1235, 280, 1395, 640)},
    {"type": "chair", "box": (1155, 330, 1235, 430), "back": "left"}, {"type": "chair", "box": (1155, 485, 1235, 585), "back": "left"},
    {"type": "counter", "box": (1225, 700, 1395, 1395)},
    {"type": "cooktop", "box": (1230, 775, 1392, 870), "zones": 2}, {"type": "sink", "box": (1245, 1015, 1375, 1170)},
    {"type": "shaft", "box": (1240, 1395, 1395, 1590)},
    {"type": "closet", "box": (445, 1150, 840, 1300), "n": 9, "along": True, "backSide": "bottom"},
    {"type": "shaft", "box": (845, 1150, 950, 1310)},
    # bathroom
    {"type": "toilet2", "box": (505, 1440, 610, 1525), "face": "right"},
    {"type": "washer", "box": (785, 1370, 925, 1500)},
    {"type": "vanity2", "box": (500, 1610, 585, 1740), "basin": (507, 1625, 578, 1725), "faucet": "left"},
    {"type": "bathtub", "box": (515, 1745, 920, 1890), "mixer": "left"},
    L((945, 1690), (1125, 1690)),
    # hallway
    {"type": "console", "box": (960, 1775, 1010, 1895)},
    {"type": "closet", "box": (1240, 1600, 1395, 1945), "n": 5, "backSide": "right", "sections": 1},
    L((1225, 1995), (1225, 2200), dark=True),
]

if __name__ == "__main__":
    build("p65", items, floors, sys.argv[1], pixel=True)
    print("ok")
