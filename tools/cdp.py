"""WSL-side helper: sends requests to cdp_bridge.js (running on Windows) via cdpc.js."""
import json
import subprocess
import sys
import uuid

PROJ_WSL = "/mnt/c/Projects/3d_visual"
PROJ_WIN = r"C:\Projects\3d_visual"


def win(p):
    """WSL path under the project -> Windows path."""
    return p.replace(PROJ_WSL, PROJ_WIN).replace("/", "\\")


def call(req, timeout=300):
    name = f"req_{uuid.uuid4().hex[:8]}.json"
    wsl_path = f"{PROJ_WSL}/tools/tmp/{name}"
    import os
    os.makedirs(f"{PROJ_WSL}/tools/tmp", exist_ok=True)
    with open(wsl_path, "w", encoding="utf-8") as f:
        json.dump(req, f)
    out = subprocess.run(
        ["cmd.exe", "/c", "node", PROJ_WIN + r"\tools\cdpc.js", PROJ_WIN + r"\tools\tmp" + "\\" + name],
        capture_output=True, timeout=timeout, cwd=PROJ_WSL,
    ).stdout.decode("utf-8", "replace")
    os.remove(wsl_path)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": out}


def cdp(method, params=None, session=None, timeout_ms=60000):
    return call({"op": "cdp", "method": method, "params": params or {}, "sessionId": session, "timeoutMs": timeout_ms})


def ev(session, expression, timeout_ms=120000, save_b64_to=None):
    req = {"op": "eval", "sessionId": session, "expression": expression, "timeoutMs": timeout_ms}
    if save_b64_to:
        req["saveBase64To"] = win(save_b64_to)
    r = call(req, timeout=timeout_ms / 1000 + 30)
    if save_b64_to:
        return r
    res = r.get("result", {})
    if "exceptionDetails" in res:
        return {"exception": res["exceptionDetails"].get("exception", {}).get("description") or res["exceptionDetails"]}
    return res.get("result", {}).get("value", r)


def shot(session, path):
    return call({"op": "screenshot", "sessionId": session, "path": win(path)})


if __name__ == "__main__":
    print(json.dumps(call(json.loads(sys.argv[1])), ensure_ascii=False, indent=1)[:4000])
