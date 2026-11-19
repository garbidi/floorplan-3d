"""Engine scene from an existing plan scene (tools/scene3d build_scene output) + reference look.
Usage: from_plan.py <plan scene.json> <out engine_scene.json> [pxm]"""
import json, sys
src, out = sys.argv[1], sys.argv[2]
pxm = float(sys.argv[3]) if len(sys.argv) > 3 else 205
sc = json.load(open(src))
for it in sc["items"]:
    if it["type"] == "glass":
        b = it["box"]
        ext = b[1] < sc["extent"][1] + 60 or b[0] < sc["extent"][0] + 60 or b[2] > sc["extent"][2] - 60 or b[3] > sc["extent"][3] - 60
        it["type"] = "window" if ext else "partition"; it["curtain"] = bool(ext)
    if it["type"] == "toilet":
        it["type"] = "toilet2"
    if it["type"] == "bed1":
        it["type"] = "bed"; it["single"] = True; it.setdefault("hb", 12)
    if it["type"] == "sink" and any(c["type"] == "counter" and c["box"][0] <= it["box"][0] and c["box"][2] >= it["box"][2]
                                    and c["box"][1] <= it["box"][1] + 5 and c["box"][3] >= it["box"][3] - 5 for c in sc["items"]):
        it["kitchen"] = True
sc.update({"pxm": pxm, "parquet": {"planks": 12, "tone": [200, 164, 142]}, "parquetRepPx": int(pxm * 1.55), "tilesRepPx": int(pxm * 1.2),
           "tiles": {"n": 4, "color": [226, 200, 182]}, "exposure": 0.92, "keyDir": [-0.2, 1.0, -0.3], "key": 0.55, "hemi": 0.75,
           "envIntensity": 0.3, "lampScale": 5, "shadowSoft": 40, "aoRadiusM": 0.9, "aoIntensity": 1.0, "vignette": 0.35,
           "gradeRef": "/mnt/c/Projects/3d_visual/reference_style_notext.png"})
json.dump(sc, open(out, "w"))
print("ok", len(sc["items"]), "items")
