"""Plan 33/66 (studio 21,7). PLAN PIXELS of plans_prepared/p65_clean.png (pgrid labels)."""
import sys, math
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402
def L(h, e, **kw):
    return dict(type="leaf", hinge=h, len=math.hypot(e[0] - h[0], e[1] - h[1]), angle=math.degrees(math.atan2(e[1] - h[1], e[0] - h[0])), thick=6, **kw)

floors = [{"type": "tile", "box": (905, 1105, 1355, 1715)}]
items = [
    {"type": "glass", "box": (465, 145, 950, 215)},
    {"type": "table", "box": (450, 270, 615, 640)},
    {"type": "chair", "box": (615, 330, 695, 430), "back": "right"}, {"type": "chair", "box": (615, 490, 695, 590), "back": "right"},
    {"type": "rug", "box": (915, 280, 1160, 760)},
    {"type": "sofa", "box": (1160, 280, 1405, 760), "seats": 2, "backSide": "right", "cushions": [
        {"box": (1255, 300, 1340, 385), "rot": 20, "color": 0xf3eee6}, {"box": (1265, 615, 1350, 700), "rot": -15, "color": 0x8c6d55}]},
    {"type": "counter", "box": (450, 705, 610, 1390)},
    {"type": "cooktop", "box": (455, 770, 605, 865), "zones": 2}, {"type": "sink", "box": (470, 1020, 600, 1180)},
    {"type": "shaft", "box": (450, 1395, 605, 1600)},
    {"type": "shaft", "box": (895, 945, 1010, 1100)},
    {"type": "closet", "box": (1010, 945, 1405, 1100), "n": 9, "along": True, "backSide": "bottom"},
    # bathroom
    {"type": "washer", "box": (920, 1150, 1080, 1295)},
    {"type": "toilet2", "box": (1240, 1230, 1355, 1325), "face": "left"},
    {"type": "vanity2", "box": (1275, 1430, 1355, 1555), "basin": (1282, 1445, 1348, 1540), "faucet": "right"},
    {"type": "bathtub", "box": (925, 1585, 1350, 1715), "mixer": "right"},
    {"type": "shaft", "box": (945, 1755, 1405, 1905)},
    L((898, 1475), (718, 1475)),
    # hallway
    {"type": "closet", "box": (450, 1600, 605, 1955), "n": 5, "backSide": "left", "sections": 1},
    {"type": "console", "box": (835, 1760, 885, 1895)},
    L((610, 2005), (610, 2215), dark=True),
]

if __name__ == "__main__":
    build("p66", items, floors, sys.argv[1], pixel=True)
    print("ok")
