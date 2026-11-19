"""Gemini web app automation over cdp_bridge (one dedicated tab)."""
import base64
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from cdp import cdp, ev, shot  # noqa: E402

PROJ = "/mnt/c/Projects/3d_visual"
TAB = os.environ.get("GEM_TAB", "1")                      # GEM_TAB=2 -> second Gemini tab (own session, downloads and lock)
_SFX = "" if TAB == "1" else TAB
DOWNLOADS = f"/mnt/c/Projects/3d_visual/tools/tmp/dl{_SFX}"
SESSION_FILE = f"{PROJ}/tools/session{_SFX}.json"


def session():
    d = json.load(open(SESSION_FILE))
    r = cdp("Runtime.evaluate", {"expression": "1", "returnByValue": True}, session=d["session"])
    if "error" in r:
        d["session"] = cdp("Target.attachToTarget", {"targetId": d["target"], "flatten": True})["result"]["sessionId"]
        cdp("Page.enable", session=d["session"])
        cdp("Runtime.enable", session=d["session"])
        json.dump(d, open(SESSION_FILE, "w"))
    return d["session"]


def js(expr, **kw):
    return ev(session(), expr, **kw)


def screenshot(name="cur"):
    p = f"{PROJ}/tools/tmp/{name}.png"
    shot(session(), p)
    return p


def mclick_js(find_expr):
    """Real mouse click on the element returned by a JS expression (hidden tabs ignore synthetic .click())."""
    r = js("(() => { const e=" + find_expr + "; if(!e) return null; const b=e.getBoundingClientRect(); return [b.x+b.width/2,b.y+b.height/2]; })()")
    if not r or not isinstance(r, list):
        return False
    for t in ("mouseMoved", "mousePressed", "mouseReleased"):
        cdp("Input.dispatchMouseEvent", {"type": t, "x": r[0], "y": r[1], "button": "left", "clickCount": 1}, session=session())
    for _ in range(3):
        time.sleep(0.6)
        tick()
    return True


def new_image_chat():
    """Open a fresh chat and switch on the image generation tool."""
    js("location.href = 'https://gemini.google.com/app'")
    for _ in range(4):
        time.sleep(1.5)
        tick()
    for _ in range(20):
        tick()
        if js("""!!document.querySelector('button[aria-label="Загрузка и инструменты"]') && !!document.querySelector('.ql-editor')"""):
            break
        time.sleep(1)
    time.sleep(2)
    mclick_js("""document.querySelector('button[aria-label="Загрузка и инструменты"]')""")
    ok = mclick_js(r"""[...document.querySelectorAll('.cdk-overlay-container button, .cdk-overlay-container [role=menuitemcheckbox]')].find(e => (e.innerText||'').includes('Создание изображений'))""")
    r = 'ok' if ok else 'no tool'
    time.sleep(1.5)
    # dismiss promo popups if any
    js(r"""(() => { [...document.querySelectorAll('button')].filter(b => (b.innerText||'').trim()==='Не сейчас').forEach(b=>b.click()); })()""")
    return r


def attach(paths):
    """Attach local files by a CDP drag-and-drop onto the prompt editor; waits for the previews."""
    s = session()
    files = [p.replace(PROJ, r"C:\Projects\3d_visual").replace("/", "\\") for p in paths]
    count = lambda: js("""document.querySelectorAll('button[aria-label="закрыть прикрепленный файл"]').length""") or 0
    for _ in range(10):
        if not count():
            break
        js("""document.querySelector('button[aria-label="закрыть прикрепленный файл"]').click()""")
        time.sleep(0.8)
    n0 = count()
    for _ in range(3):
        js("document.querySelector('.cdk-overlay-backdrop')?.click()")
        cdp("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27}, session=s)
        cdp("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27}, session=s)
        time.sleep(0.5)
    time.sleep(2)
    screenshot("_frame")  # forces a fresh layout in the background tab
    xy = None
    for _ in range(15):
        tick()
        xy = js("""(() => { const e=document.querySelector('.ql-editor'); if(!e) return null; const b=e.getBoundingClientRect(); return [b.x+b.width/2, b.y+b.height/2]; })()""")
        if isinstance(xy, list):
            break
        time.sleep(1)
    x, y = xy
    data = {"items": [], "files": files, "dragOperationsMask": 1}
    for t in ("dragEnter", "dragOver", "drop"):
        cdp("Input.dispatchDragEvent", {"type": t, "x": x, "y": y, "data": data}, session=s)
        time.sleep(0.4)
    for _ in range(30):
        time.sleep(2)
        n = count()
        if n - n0 >= len(paths):
            time.sleep(3)
            return {"attached": n}
    return {"attached": count(), "error": "attach failed"}


def type_prompt(text):
    js("document.querySelector('.ql-editor').focus()")
    return cdp("Input.insertText", {"text": text}, session=session())


def tick():
    """Background tabs are not rendered; a screenshot forces a frame so the app keeps working."""
    try:
        screenshot("_frame")
    except Exception:
        pass


def send():
    tick()
    return js(r"""(() => { const b = [...document.querySelectorAll('button')].find(b => /Отправить/.test(b.getAttribute('aria-label')||'')); if(!b) return 'no send'; if (b.disabled || b.getAttribute('aria-disabled')==='true') return 'disabled'; b.click(); return 'sent'; })()""")


def count_images():
    return js(r"""document.querySelectorAll('model-response img, generated-image img, single-image img').length""")


def response_state():
    return js(r"""(() => {
      const rs = document.querySelectorAll('model-response');
      const last = rs[rs.length-1];
      if (!last) return {n:0};
      const imgs = [...last.querySelectorAll('img')].filter(i => i.naturalWidth > 300);
      const stop = !![...document.querySelectorAll('button')].find(b => /Остановить/.test(b.getAttribute('aria-label')||''));
      return {n: rs.length, imgs: imgs.length, busy: stop, text: (last.innerText||'').slice(0,300)};
    })()""")


def wait_result(timeout=600):
    t0 = time.time()
    for _ in range(5):
        time.sleep(2)
        tick()
    while time.time() - t0 < timeout:
        tick()
        st = response_state()
        if isinstance(st, dict) and not st.get("busy") and (st.get("imgs") or st.get("text")):
            time.sleep(3)
            return st
        time.sleep(4)
    return {"timeout": True}


def download_last(dest):
    """serialised across tabs: one download at a time, so the new file in the download dirs belongs to this tab"""
    import fcntl
    with open("/mnt/c/Projects/3d_visual/tools/tmp/download.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            return _download_last(dest)
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)


def _download_last(dest):
    """Click the full-size download button of the last generated image and move the file to dest."""
    cdp("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": r"C:\Projects\3d_visual\tools\tmp\dl" + _SFX}, session=session())
    DIRS = ["/mnt/c/Projects/3d_visual/tools/tmp/dl", "/mnt/c/Projects/3d_visual/tools/tmp/dl2", "/mnt/c/Users/user/Downloads"]
    listing = lambda: set(f for d in DIRS for f in glob.glob(f"{d}/*"))
    before = listing()
    r = js(r"""(async () => {
      const rs = document.querySelectorAll('model-response');
      const last = rs[rs.length-1];
      const img = [...last.querySelectorAll('img')].filter(i => i.naturalWidth > 300).pop();
      if (!img) return 'no image';
      img.scrollIntoView(); img.dispatchEvent(new MouseEvent('mouseover', {bubbles:true}));
      await new Promise(r => setTimeout(r, 800));
      const btn = [...last.querySelectorAll('button')].find(b => /Скачать|Download/i.test((b.getAttribute('aria-label')||'') + (b.innerText||'')));
      if (!btn) return 'no download button';
      btn.click(); return 'clicked';
    })()""")
    if r != "clicked":
        return r
    for _ in range(90):
        time.sleep(2)
        tick()
        new = [f for f in listing() - before if not f.endswith((".crdownload", ".tmp")) and os.path.basename(f).lower().startswith(("gemini_generated", "generated image"))]
        if new:
            f = max(new, key=os.path.getmtime)
            time.sleep(2)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            import shutil; shutil.copy(f, dest)
            return dest
    return "download timeout"


RATIOS = {"1:1": 1, "9:16": 9 / 16, "3:4": 3 / 4, "4:3": 4 / 3, "16:9": 16 / 9}


def set_aspect(name):
    mclick_js(r"""[...document.querySelectorAll('button')].find(b => /Соотношение сторон|^\d+:\d+$/.test((b.getAttribute('aria-label')||'') + '|' + (b.innerText||'').trim()) && b.getBoundingClientRect().y > 250)""")
    ok = mclick_js(f"""[...document.querySelectorAll('.cdk-overlay-container button, .cdk-overlay-container [role=menuitem], .cdk-overlay-container [role=menuitemradio]')].find(e => (e.innerText||'').trim()==='{name}')""")
    return 'ok' if ok else 'nf'

def _generate_unlocked(text, files, dest, aspect="4:3", tries=2):
    """New Gemini chat with image tool, attach files, send prompt, download full-size result."""
    for attempt in range(tries):
        print("chat:", new_image_chat(), "aspect:", set_aspect(aspect))
        time.sleep(1)
        if files:
            a = attach(files)
            print("attach:", a)
            if a.get("error"):
                continue
        type_prompt(text)
        time.sleep(1.5)
        print("send:", send())
        st = wait_result(timeout=600)
        print("result:", st)
        for _ in range(30):
            if isinstance(st, dict) and st.get("imgs"):
                break
            time.sleep(3)
            tick()
            st = response_state()
        if isinstance(st, dict) and st.get("imgs"):
            time.sleep(3)
            r = grab_last_image(dest)
            print("download:", r)
            # full-size original via the Download button (the cached preview is only ~1024 px)
            try:
                full = download_last(dest + ".full.png")
                if isinstance(full, str) and os.path.exists(full):
                    from PIL import Image as _I
                    if r != dest or _I.open(full).size[0] > _I.open(dest).size[0]:
                        os.replace(full, dest); r = dest
                    print("full size:", _I.open(dest).size)
            except Exception as e:
                print("full download failed:", e)
            if r == dest:
                return dest
    return None


def edit(text, dest):
    """Follow-up edit in the current chat."""
    type_prompt(text)
    time.sleep(1.5)
    print("send:", send())
    st = wait_result(timeout=600)
    if isinstance(st, dict) and st.get("imgs"):
        return download_last(dest)
    return st


def redraw_region(src, pct_box, change, out, inner_pct=None, feather=5, extra_files=()):
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
    crop_path = PROJ + "/tools/tmp/region.png"
    im.crop((x0, y0, x1, y1)).save(crop_path)
    prompt = ("IMAGE 1 is a small crop of a photorealistic top-down (orthographic, camera looking straight down) "
              "apartment interior render. Redraw IMAGE 1 with exactly the same framing, and with the same outlines, "
              "positions, sizes, colors and lighting of everything, making ONLY this change:\n" + change +
              "\nEverything is seen strictly from above. Output only the redrawn crop, with no borders and no text.")
    gen = PROJ + "/tools/tmp/region_gen.png"
    if os.path.exists(gen):
        os.remove(gen)
    res = generate(prompt, [crop_path, *extra_files], gen, aspect=name)
    if not res:
        return {"error": "generation failed"}
    remove_sparkle(gen)
    inner = fix.to_px(im, inner_pct, cb) if inner_pct else (x0, y0, x1, y1)
    fix.paste_px(src, gen, (x0, y0, x1, y1), out, inner_px=inner, feather=feather)
    return {"ratio": name, "box": (x0, y0, x1, y1), "out": out}


def remove_sparkle(path):
    """Gemini stamps a small sparkle watermark in the bottom-right corner; inpaint that corner."""
    import cv2
    import numpy as np
    a = cv2.imread(path)
    h, w = a.shape[:2]
    m = np.zeros((h, w), np.uint8)
    m[int(h * 0.93):, int(w * 0.93):] = 255
    cv2.imwrite(path, cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA))


def grab_last_image(dest):
    """Save the last generated image from its blob/https URL via the browser cache (no UI overlays)."""
    import base64
    sess = session()
    src = js(r"""(() => { const rs=document.querySelectorAll('model-response'); const l=rs[rs.length-1];
      const i=[...l.querySelectorAll('img')].filter(i=>i.naturalWidth>300).pop(); return i ? i.src : null; })()""")
    if not src:
        return "no image"
    fid = cdp("Page.getFrameTree", session=sess)["result"]["frameTree"]["frame"]["id"]
    r = cdp("Page.getResourceContent", {"frameId": fid, "url": src}, session=sess, timeout_ms=120000)
    if "result" not in r:
        return "no content"
    c = r["result"]["content"]
    open(dest, "wb").write(base64.b64decode(c) if r["result"]["base64Encoded"] else c.encode())
    return dest


def generate(*args, **kw):
    """serialised: only one generation at a time across processes (the Gemini / AI Studio tabs are shared)"""
    import fcntl
    with open(f"/mnt/c/Projects/3d_visual/tools/tmp/browser{_SFX}.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            return _generate_unlocked(*args, **kw)
        finally:
            fcntl.flock(lk, fcntl.LOCK_UN)
