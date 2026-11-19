"""Plan 33/168 (studio 24,9). PLAN PIXELS of plans_prepared/p168_clean.png (read on tools/tmp/pgrid.py labels)."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (718, 1720, 1352, 2575)}]
items = [
    {"type": "glass", "box": (1155, 300, 1850, 392)},
    {"type": "rug", "box": (1000, 455, 1340, 1140)},
    {"type": "sofa", "box": (637, 455, 1000, 1140), "seats": 2, "backSide": "left", "cushions": [
        {"box": (705, 470, 800, 570), "rot": 20, "color": 0xf3eee6}, {"box": (700, 1020, 800, 1120), "rot": -15, "color": 0x8c6d55}]},
    {"type": "console", "box": (2025, 520, 2105, 1045)},
    {"type": "tv", "box": (2062, 575, 2092, 990)},
    {"type": "table", "box": (1610, 1235, 2105, 1480)},
    {"type": "chair", "box": (1680, 1120, 1830, 1235), "back": "top"},
    {"type": "chair", "box": (1915, 1120, 2065, 1235), "back": "top"},
    {"type": "closet", "box": (637, 1470, 1155, 1692), "n": 12, "along": True, "backSide": "bottom"},
    {"type": "shaft", "box": (1155, 1470, 1380, 1700)},
    # kitchen run along the right wall
    {"type": "counter", "box": (1865, 1480, 2105, 2468)},
    {"type": "cooktop", "box": (1895, 1548, 2100, 1690), "zones": 2},
    {"type": "sink", "box": (1905, 1930, 2085, 2145)},
    # bathroom
    {"type": "bathtub", "box": (735, 1738, 1278, 1930), "mixer": "left"},
    {"type": "vanity2", "box": (718, 1965, 840, 2195), "basin": (732, 2010, 828, 2145), "faucet": "left"},
    {"type": "ledge", "box": (718, 2320, 745, 2500)},
    {"type": "toilet2", "box": (745, 2340, 890, 2480), "face": "right"},
    {"type": "washer", "box": (1125, 2352, 1350, 2570)},
    {"type": "leaf", "hinge": (1378, 2282), "len": 250, "angle": -10, "thick": 8},
    # hallway
    {"type": "console", "box": (1382, 2320, 1455, 2630)},
    {"type": "console", "box": (1382, 2900, 1455, 3125)},
    {"type": "closet", "box": (1890, 2742, 2105, 3145), "n": 7, "backSide": "right", "sections": 2},
    {"type": "leaf", "hinge": (1452, 3215), "len": 330, "angle": 92, "thick": 12, "dark": True},
]

if __name__ == "__main__":
    build("p168", items, floors, sys.argv[1], pixel=True)
    print("ok")
