"""Google AI Studio (Nano Banana Pro) automation over cdp_bridge — one dedicated tab."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from cdp import cdp, ev, shot  # noqa: E402

PROJ = "/mnt/c/Projects/3d_visual"
RES = os.environ.get("STUDIO_RES", "4K")
SESSION_FILE = f"{PROJ}/tools/session_studio.json"


def session():
    d = json.load(open(SESSION_FILE))
    r = cdp("Runtime.evaluate", {"expression": "1", "returnByValue": True}, session=d["session"])
    if "error" in r:  # bridge restarted -> re-attach to the same tab
        d["session"] = cdp("Target.attachToTarget", {"targetId": d["target"], "flatten": True})["result"]["sessionId"]
        cdp("Page.enable", session=d["session"])
        cdp("Runtime.enable", session=d["session"])
        json.dump(d, open(SESSION_FILE, "w"))
    return d["session"]


def js(expr, **kw):
    return ev(session(), expr, **kw)


def screenshot(name="studio"):
    p = f"{PROJ}/tools/tmp/{name}.png"
    shot(session(), p)
    return p


def tick():
    try:
        screenshot("_sframe")
    except Exception:
        pass


def busy():
    return js(r"""!![...document.querySelectorAll('button')].find(b => /^Stop/.test((b.innerText||'').trim()))""")


def n_images():
    return js(r"""[...document.querySelectorAll('ms-chat-turn img, .chat-turn-container img')].filter(i => i.naturalWidth > 500).length""")


def wait_done(timeout=900):
    t0 = time.time()
    time.sleep(15)
    while time.time() - t0 < timeout:
        if not busy():
            time.sleep(3)
            return {"done": True, "images": n_images(), "secs": int(time.time() - t0)}
        time.sleep(10)
    return {"timeout": True}


def last_error():
    return js(r"""(() => { const t=[...document.querySelectorAll('ms-chat-turn')].pop(); return t ? (t.innerText||'').slice(-600) : ''; })()""")


def save_last_image(dest):
    """Fetch the last generated image (data:/blob:/https) inside the page and save it at full resolution."""
    expr = r"""(async () => {
      const imgs = [...document.querySelectorAll('ms-chat-turn img, .chat-turn-container img')].filter(i => i.naturalWidth > 500);
      const img = imgs.pop();
      if (!img) return 'NOIMG';
      if (img.src.startsWith('data:')) return img.src;
      const blob = await (await fetch(img.src)).blob();
      return await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
    })()"""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    return ev(session(), expr, timeout_ms=180000, save_b64_to=dest)


def send(text, files=()):
    s = session()
    if files:
        cdp("Page.setInterceptFileChooserDialog", {"enabled": True}, session=s)
        root = cdp("DOM.getDocument", {"depth": 0}, session=s)["result"]["root"]["nodeId"]
        nid = cdp("DOM.querySelector", {"nodeId": root, "selector": "input[type=file]"}, session=s)["result"]["nodeId"]
        win = [f.replace(PROJ, r"C:\Projects\3d_visual").replace("/", "\\") for f in files]
        cdp("DOM.setFileInputFiles", {"nodeId": nid, "files": win}, session=s)
        cdp("Page.setInterceptFileChooserDialog", {"enabled": False}, session=s)
        time.sleep(4)
    tick()
    js(r"""document.querySelector('textarea[aria-label="Enter a prompt"]').focus()""")
    cdp("Input.insertText", {"text": text}, session=s)
    tick()
    time.sleep(1.5)
    RUN = r"""(() => { const b=[...document.querySelectorAll('button')].find(b => /^Run/.test((b.innerText||'').trim())); return !!b && !b.disabled && b.getAttribute('aria-disabled') !== 'true'; })()"""
    for _ in range(60):          # Run becomes active only after every attachment has finished uploading
        if js(RUN):
            break
        time.sleep(3)
        tick()
    return js(r"""(() => { const b=[...document.querySelectorAll('button')].find(b => /^Run/.test((b.innerText||'').trim())); if (!b || b.disabled) return 'run disabled'; b.click(); return 'run'; })()""")


def setup(system_text, aspect="4:5", resolution="4K"):
    """Fill System instructions, aspect ratio and resolution; report current state."""
    js(r"""(() => { const b=[...document.querySelectorAll('button')].find(b => (b.getAttribute('aria-label')||b.innerText||'').trim().startsWith('System instructions')); b.click(); })()""")
    time.sleep(2)
    js(r"""(() => { const t=document.querySelector('textarea[aria-label="System instructions"]'); t.focus(); t.select(); })()""")
    cdp("Input.insertText", {"text": system_text}, session=session())
    time.sleep(1.5)
    si = js(r"""document.querySelector('textarea[aria-label="System instructions"]').value.length""")
    js(r"""[...document.querySelectorAll('button')].filter(b => (b.getAttribute('aria-label')||'').match(/close/i) && b.getBoundingClientRect().x > 1800).forEach(b=>b.click())""")
    time.sleep(1.5)
    for label, value in (("Aspect ratio", aspect), ("Resolution", resolution)):
        js(f"""document.querySelector('[aria-label="{label}"]').click()""")
        time.sleep(1.2)
        js(f"""(() => {{ const o=[...document.querySelectorAll('mat-option, [role=option]')].find(o => (o.innerText||'').trim().split('\\n')[0].trim()==='{value}'); if(o) o.click(); }})()""")
        time.sleep(1)
    state = js(r"""[...document.querySelectorAll('[role=combobox]')].map(c => c.getAttribute('aria-label') + '=' + (c.innerText||'').trim()).join(', ')""")
    return {"system_len": si, "state": state}


def set_selects(aspect="4:5", resolution="4K", tries=6):
    """set aspect + resolution and VERIFY (the page may still be loading and reset them to Auto/1K)."""
    st = ""
    for _ in range(tries):
        st = _set_selects_once(aspect, resolution)
        if isinstance(st, str) and f"Aspect ratio={aspect}" in st and f"Resolution={resolution}" in st:
            return st
        time.sleep(2.5)
    return "NOT SET: " + str(st)


def _set_selects_once(aspect="4:5", resolution="4K"):
    for label, value in (("Aspect ratio", aspect), ("Resolution", resolution)):
        js(f"""document.querySelector('[aria-label="{label}"]').click()""")
        time.sleep(1.2)
        js(f"""(() => {{ const o=[...document.querySelectorAll('mat-option, [role=option]')].find(o => (o.innerText||'').trim().split('\\n')[0].trim()==='{value}'); if(o) o.click(); }})()""")
        time.sleep(1)
    return js(r"""[...document.querySelectorAll('[role=combobox]')].map(c => c.getAttribute('aria-label') + '=' + (c.innerText||'').trim()).join(', ')""")


def new_chat(aspect="4:5"):
    js("location.href = 'https://aistudio.google.com/prompts/new_chat?model=gemini-3-pro-image'")
    for _ in range(6):
        time.sleep(1.5)
        tick()
    return set_selects(aspect, RES)


def wait_turn(min_turns, timeout=900):
    """Wait until generation ends. Returns 'ok', 'reset' (page reloaded to empty chat) or 'timeout'."""
    t0 = time.time()
    for _ in range(8):
        time.sleep(2)
        tick()
    while time.time() - t0 < timeout:
        tick()
        st = js(r"""(() => ({busy: !![...document.querySelectorAll('button')].find(b => /Stop/.test((b.innerText||'').trim())), turns: document.querySelectorAll('ms-chat-turn').length}))()""")
        if isinstance(st, dict) and "turns" in st:
            if st["turns"] == 0 and not st["busy"]:
                return "reset"
            if not st["busy"] and st["turns"] >= min_turns:
                time.sleep(3)
                return "ok"
        time.sleep(6)
    return "timeout"


def expand_thoughts():
    """Images sometimes appear only inside the collapsed 'model thoughts' block: open all of them."""
    n = js(r"""(() => { let n=0; document.querySelectorAll('ms-chat-turn button, ms-chat-turn [role=button], ms-chat-turn mat-expansion-panel-header').forEach(b => { const t=(b.innerText||b.getAttribute('aria-label')||''); if (/Expand to view model thoughts|model thoughts|Thoughts/i.test(t) && !/Collapse/i.test(t)) { b.click(); n++; } }); return n; })()""")
    time.sleep(3)
    tick()
    return n


def last_size():
    expand_thoughts()
    return js(r"""(() => { const i=[...document.querySelectorAll('ms-chat-turn img')].filter(i=>i.naturalWidth>500).pop(); return i ? i.naturalWidth : 0; })()""")


def _generate_unlocked(text, files, dest, first=True, tries=3, aspect="4:5", min_size=3000):
    """Send a message (new chat if first) and save the resulting image; retries page resets and non-4K results."""
    reset_before = False
    for attempt in range(tries):
        if first and not reset_before:
            print("new chat:", new_chat(aspect))
        elif reset_before:             # page reloaded by itself: do NOT navigate again, just re-apply settings and resend here
            for _ in range(4):
                time.sleep(1.5); tick()
            print("same page:", js("location.href"), set_selects(aspect, RES))
        n0 = js("document.querySelectorAll('ms-chat-turn').length") or 0
        print("send:", send(text, files if (first or reset_before) else ()))
        r = wait_turn(n0 + 2)
        print("wait:", r, "size:", last_size())
        if r == "reset":
            reset_before = True
            continue
        if r == "ok" and last_size() >= min_size:
            return save_last_image(dest)
        if r == "ok":  # low-res result: rerun the same turn
            js(r"""(() => { const t=[...document.querySelectorAll('ms-chat-turn')].pop(); const b=[...t.querySelectorAll('button')].find(b => /Rerun/.test(b.getAttribute('aria-label')||'')); if(b) b.click(); })()""")
            r = wait_turn(n0 + 2)
            if last_size() >= min_size:
                return save_last_image(dest)
    return {"error": "failed", "size": last_size()}


RATIOS = {"1:1": 1, "9:16": 9/16, "16:9": 16/9, "3:4": 3/4, "4:3": 4/3, "3:2": 3/2, "2:3": 2/3,
          "5:4": 5/4, "4:5": 4/5, "21:9": 21/9}


def redraw_region(src, pct_box, change, out, inner_pct=None, feather=5, extra_files=(), blank_pct=None):
    """Crop a region (plan % box, expanded to the nearest supported aspect), let Nano Banana Pro redraw it
    with ONE change, paste the inner part back with feathering. Returns output path."""
    sys.path.insert(0, os.path.dirname(__file__))
    import fix
    from PIL import Image
    im = Image.open(src).convert("RGB")
    cb = fix.contour(im)
    x0, y0, x1, y1 = fix.to_px(im, pct_box, cb)
    w, h = x1 - x0, y1 - y0
    name, r = min(RATIOS.items(), key=lambda kv: abs(kv[1] - w / h))
    if w / h < r:
        nw = int(h * r); x0 -= (nw - w) // 2; x1 = x0 + nw
    else:
        nh = int(w / r); y0 -= (nh - h) // 2; y1 = y0 + nh
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(im.size[0], x1), min(im.size[1], y1)
    crop_path = PROJ + "/tools/tmp/region.jpg"
    crop_img = im.crop((x0, y0, x1, y1))
    if blank_pct:
        from PIL import ImageDraw
        bx0, by0, bx1, by1 = fix.to_px(im, blank_pct, cb)
        ImageDraw.Draw(crop_img).rectangle((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0), fill=(128, 128, 128))
    crop_img.save(crop_path, quality=97)
    prompt = ("IMAGE 1 is a small crop of a photorealistic top-down (orthographic, camera looking straight down) "
              "apartment interior render. Redraw IMAGE 1 with exactly the same framing, and with the same outlines, "
              "positions, sizes, colors and lighting of everything, making ONLY this change:\n" + change +
              "\nEverything is seen strictly from above. Output only the redrawn crop, with no borders and no text.")
    for attempt in range(3):
        js("location.href = 'https://aistudio.google.com/prompts/new_chat?model=gemini-3-pro-image'")
        for _ in range(6):
            time.sleep(1.5)
            tick()
        set_selects(name, "2K")
        send(prompt, [crop_path, *extra_files])
        if wait_turn(2) == "ok" and last_size() > 500:
            break
    gen = PROJ + "/tools/tmp/region_gen.jpg"
    save_last_image(gen)
    inner = fix.to_px(im, inner_pct, cb) if inner_pct else (x0, y0, x1, y1)
    fix.paste_px(src, gen, (x0, y0, x1, y1), out, inner_px=inner, feather=feather)
    return {"ratio": name, "box": (x0, y0, x1, y1), "out": out}


def generate(*args, **kw):
    """serialised: only one generation at a time across processes (the Gemini / AI Studio tabs are shared)"""
    import fcntl
    with open("/mnt/c/Projects/3d_visual/tools/tmp/studio.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            return _generate_unlocked(*args, **kw)
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)
