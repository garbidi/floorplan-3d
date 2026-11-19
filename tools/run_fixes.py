"""Run a list of region fixes (JSON file) sequentially in Gemini; prints one line per step (flushed)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import gem  # noqa: E402
import studio  # noqa: E402

steps = json.load(open(sys.argv[1], encoding="utf-8"))
engine = studio if steps.get("engine") == "studio" else gem
R = steps["dir"]
cur = steps["start"]
for i, st in enumerate(steps["steps"]):
    out = f"{R}/{steps['prefix']}{i + 1}.jpg"
    try:
        r = engine.redraw_region(f"{R}/{cur}", st["box"], st["change"], out, inner_pct=st.get("inner"),
                              extra_files=st.get("extra", []), **({"blank_pct": st["blank"]} if st.get("blank") else {}))
    except Exception as e:  # keep going with the last good image
        r = {"error": repr(e)}
    if isinstance(r, dict) and r.get("out"):
        cur = os.path.basename(out)
        print(f"STEP {i + 1} OK {st['name']} -> {cur}", flush=True)
    else:
        print(f"STEP {i + 1} FAIL {st['name']} {r}", flush=True)
print(f"DONE last={cur}", flush=True)
