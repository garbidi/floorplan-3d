"""Render a scene JSON with the engine. Usage: run.py scene.json out.png [width] [key=value overrides...]"""
import base64, functools, http.server, json, sys, threading
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

HERE = __file__.rsplit("/", 1)[0]


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=HERE)
    h.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def render(scene_p, out_p, width=2000, overrides=None):
    scene = json.load(open(scene_p))
    scene.update(overrides or {})
    srv = serve()
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 800, "height": 600})
        pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: print("pageerror:", e))
        pg.add_init_script(f"window.SCENE={json.dumps(scene)};window.OUT_W={width};")
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html")
        pg.wait_for_function("window.RENDER_DONE === true", timeout=900000)
        data = pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
        open(out_p, "wb").write(base64.b64decode(data.split(",", 1)[1]))
        b.close()
    srv.shutdown()
    im = Image.open(out_p).convert("RGB")
    msk = Image.open(scene["mask"]).convert("L").resize(im.size, Image.NEAREST)
    a = np.asarray(im).astype(np.float32)
    inside = np.asarray(msk) > 0
    vg = scene.get("vignette", 0.3)
    if vg:   # darken towards the edges of the apartment (not the white page)
        import cv2
        dist = cv2.distanceTransform(inside.astype(np.uint8), cv2.DIST_L2, 5)
        k = np.clip(dist / (0.08 * max(a.shape[:2])), 0, 1)
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        rad = ((xx / a.shape[1] - .5) ** 2 + (yy / a.shape[0] - .5) ** 2)
        f = (1 - vg * 0.5 * (1 - k)) * (1 - vg * rad)
        a[inside] *= f[inside][:, None]
    gref = scene.get("gradeRef")
    if gref:   # LAB grading of the interior to the reference look: L by histogram, a/b by mean+std
        import cv2
        ra = np.asarray(Image.open(gref).convert("RGB"))
        rsel = (ra.max(axis=2) > 40) & ~(ra.min(axis=2) > 235)
        sel = inside & (a.max(axis=2) > 40)
        la = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        lr = cv2.cvtColor(ra, cv2.COLOR_RGB2LAB).astype(np.float32)
        mix = scene.get("gradeMix", 0.8)
        qs = np.linspace(0, 100, 257)
        sp = np.percentile(la[..., 0][sel], qs); rp = np.percentile(lr[..., 0][rsel], qs)
        L2 = np.interp(la[..., 0], sp, rp)
        la[..., 0] = np.where(sel, la[..., 0] * (1 - mix) + L2 * mix, la[..., 0])
        for c in (1, 2):
            ms, ss = la[..., c][sel].mean(), la[..., c][sel].std() + 1e-3
            mr, sr = lr[..., c][rsel].mean(), lr[..., c][rsel].std()
            v = (la[..., c] - ms) * (1 + (sr / ss - 1) * 0.5) + mr
            la[..., c] = np.where(sel, la[..., c] * (1 - mix) + v * mix, la[..., c])
        a = cv2.cvtColor(np.clip(la, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
    bg = (~inside) & (a.min(axis=2) > 140); a[bg] = 255
    a = np.clip(a, 0, 255).astype(np.uint8)
    Image.fromarray(a).save(out_p)
    return out_p


if __name__ == "__main__":
    ov = {}
    for kv in sys.argv[4:]:
        k, v = kv.split("=", 1); ov[k] = json.loads(v)
    print(render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2000, ov))
