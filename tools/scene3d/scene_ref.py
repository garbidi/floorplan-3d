"""Reference visualization (reference_style.png, 877x970) rebuilt as a 3D scene. Coordinates in reference px."""
import sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

floors = [{"type": "tile", "box": (590, 560, 820, 862)}]
items = [
    # windows
    {"type": "glass", "box": (135, 36, 355, 80)},
    {"type": "glass", "box": (455, 36, 705, 84)},
    # loggia
    {"type": "armchair", "box": (52, 107, 155, 210), "rot": -25},
    {"type": "floorlamp", "box": (147, 82, 202, 137), "power": 0.9},
    {"type": "roundtable", "box": (150, 180, 200, 230)},
    {"type": "plant", "box": (295, 90, 415, 230)},
    # bedroom
    {"type": "nightstand", "box": (40, 290, 100, 350)},
    {"type": "nightstand", "box": (42, 602, 100, 667)},
    {"type": "bed", "box": (38, 352, 330, 595), "head": "left", "hb": 16},
    {"type": "tv", "box": (372, 256, 386, 355)},
    {"type": "closet", "box": (38, 700, 100, 875), "n": -1, "sections": 1, "backSide": "left"},
    {"type": "closet", "box": (100, 790, 315, 875), "n": 12, "along": True, "backSide": "bottom"},
    {"type": "closet", "box": (328, 725, 415, 875), "n": -1, "sections": 1, "along": True, "backSide": "bottom"},
    {"type": "leaf", "hinge": (372, 580), "len": 118, "angle": 58, "thick": 5},
    # kitchen
    {"type": "table", "box": (460, 150, 550, 290), "plates": [(485, 175), (520, 220), (485, 262)]},
    {"type": "chair", "box": (462, 110, 515, 150), "back": "top"},
    {"type": "chair", "box": (550, 197, 592, 257), "back": "right"},
    {"type": "chair", "box": (462, 290, 517, 334), "back": "bottom"},
    {"type": "counter", "box": (712, 86, 818, 500), "top": "oak"},
    {"type": "counter", "box": (520, 415, 712, 500), "top": "oak"},
    {"type": "cooktop", "box": (735, 131, 812, 232), "zones": 4},
    {"type": "sink", "box": (734, 337, 812, 420)},
    {"type": "fridge", "box": (555, 415, 642, 500)},
    {"type": "leaf", "hinge": (537, 447), "len": 112, "angle": 152, "thick": 5},
    # hallway
    {"type": "console", "box": (540, 510, 580, 630)},
    {"type": "console", "box": (547, 735, 580, 875)},
    {"type": "leaf", "hinge": (580, 740), "len": 108, "angle": -118, "thick": 5},
    {"type": "leaf", "hinge": (400, 880), "len": 118, "angle": 35, "thick": 8, "dark": True},
    # bathroom
    {"type": "washer", "box": (592, 565, 667, 629)},
    {"type": "ledge", "box": (770, 565, 815, 680)},
    {"type": "toilet2", "box": (716, 602, 770, 644), "face": "left"},
    {"type": "vanity2", "box": (752, 690, 815, 757), "basin": (755, 694, 810, 753), "faucet": "right"},
    {"type": "bathtub", "box": (592, 760, 818, 860), "mixer": "right"},
]


def _x2(v):
    if isinstance(v, (int, float)): return v * 2
    if isinstance(v, (list, tuple)): return type(v)(_x2(x) for x in v)
    if isinstance(v, dict): return {k: (_x2(x) if k in ("box", "hinge", "len", "thick", "plates", "basin", "arm", "back", "hb") and not isinstance(x, str) else x) for k, x in v.items()}
    return v



if __name__ == "__main__":
    build("ref", items, floors, sys.argv[1], pixel=True, inside=[(38, 78, 420, 250)], style="ref")
    print("ok")
