"""Reference apartment (reference_style.png, 877x970 px) for the engine. Coordinates in reference px."""
import json, sys
sys.path.insert(0, "/mnt/c/Projects/3d_visual/tools/scene3d")
from build_scene import build  # noqa: E402

PXM = 128            # reference px per metre (from the room areas)
floors = [{"type": "tile", "box": (590, 560, 820, 862)}]
items = [
    {"type": "window", "box": (135, 36, 355, 80), "room": "bottom"},
    {"type": "window", "box": (455, 36, 705, 84), "room": "bottom"},
    # loggia
    {"type": "armchair", "box": (58, 112, 152, 205), "rot": 60},
    {"type": "floorlamp", "box": (147, 82, 202, 137)},
    {"type": "roundtable", "box": (150, 180, 200, 230)},
    {"type": "plant", "box": (292, 88, 418, 232)},
    # bedroom
    {"type": "nightstand", "box": (40, 290, 100, 350)},
    {"type": "nightstand", "box": (42, 602, 100, 667)},
    {"type": "bed", "box": (38, 352, 330, 595), "head": "left"},
    {"type": "tv", "box": (372, 256, 386, 355)},
    {"type": "closet", "box": (38, 700, 104, 875), "backSide": "left", "fill": "shelf", "glass": True, "stackM": 0.24, "stackColors": [0xe9e2d8, 0xd6ccc0, 0xece6de, 0xcfc4b8, 0xe2dad0]},
    {"type": "closet", "box": (104, 790, 318, 875), "backSide": "bottom", "sections": 3, "glass": True},
    {"type": "closet", "box": (328, 725, 415, 875), "backSide": "right", "fill": "shelf", "glass": True, "stackM": 0.14},
    {"type": "leaf", "hinge": (372, 580), "len": 118, "angle": 58},
    # kitchen
    {"type": "table", "box": (460, 150, 550, 290), "plates": [(485, 175), (520, 220), (485, 262)], "candle": (452, 222)},
    {"type": "chair", "box": (462, 110, 515, 150), "back": "top"},
    {"type": "chair", "box": (550, 197, 592, 257), "back": "right", "color": 0xe4dbd2},
    {"type": "chair", "box": (462, 290, 517, 334), "back": "bottom"},
    {"type": "counter", "box": (712, 86, 818, 500)},
    {"type": "counter", "box": (520, 415, 712, 500)},
    {"type": "cooktop", "box": (735, 131, 812, 232), "zones": 4},
    {"type": "kettle", "box": (770, 250, 805, 287)},
    {"type": "cup", "box": (785, 300, 807, 322)},
    {"type": "sink", "box": (734, 337, 812, 420), "faucet": "right"},
    {"type": "cabinet", "box": (555, 412, 642, 500), "hM": 0.95, "color": 0xbdbab6},
    {"type": "appliance", "box": (740, 440, 790, 492)},
    {"type": "leaf", "hinge": (537, 447), "len": 112, "angle": 152},
    # hallway
    {"type": "console", "box": (540, 510, 580, 630)},
    {"type": "console", "box": (547, 735, 580, 875), "hM": 1.0},
    {"type": "leaf", "hinge": (580, 740), "len": 108, "angle": -118},
    {"type": "leaf", "hinge": (400, 880), "len": 118, "angle": 35, "dark": True},
    # bathroom
    {"type": "cabinet", "box": (592, 565, 667, 629)},
    {"type": "ledge", "box": (772, 565, 815, 680)},
    {"type": "toilet", "box": (716, 602, 772, 646), "face": "left"},
    {"type": "basin", "box": (752, 690, 815, 757), "wall": "right"},
    {"type": "bathtub", "box": (592, 760, 818, 860), "mixer": "right"},
]

if __name__ == "__main__":
    out = sys.argv[1]
    sc = build("ref", items, floors, out, pixel=True, inside=[(38, 78, 420, 250)])
    sc.update({"pxm": PXM, "parquet": {"planks": 12, "tone": [200, 164, 142]}, "exposure": 0.92, "gradeRef": "/mnt/c/Projects/3d_visual/reference_style_notext.png", "parquetRepPx": 200, "keyDir": [-0.2, 1.0, -0.3], "key": 0.55, "hemi": 0.75, "envIntensity": 0.3, "lampScale": 9, "shadowSoft": 40, "aoRadiusM": 0.9, "aoIntensity": 1.0, "vignette": 0.35, "tilesRepPx": 240, "tiles": {"n": 4, "color": [226, 200, 182]}})
    json.dump(sc, open(out, "w"))
    print("ok")
