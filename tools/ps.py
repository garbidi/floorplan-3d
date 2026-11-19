"""Photoshop 2020 (running on Windows) via COM: content-aware fill of rectangles - heals seams / small leftovers without AI.
usage from python: ps.heal(src_png, [(x0, y0, x1, y1), ...], out_png)"""
import os, subprocess, json

TMP = '/mnt/c/Projects/3d_visual/tools/tmp/'


def win(p):
    return subprocess.check_output(['wslpath', '-w', p]).decode().strip()


def ellipse(cx, cy, rx, ry, n=48):
    import math
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ring(cx, cy, r_out, r_in):
    """selection spec for an annulus (e.g. the lid circle line on a washer top)"""
    return [(ellipse(cx, cy, r_out, r_out), 'EXTEND'), (ellipse(cx, cy, r_in, r_in), 'DIMINISH')]


def heal(src, rects, out, polys=()):
    import shutil
    shutil.copy(src, TMP + 'ps_in.png'); dst = out; src = TMP + 'ps_in.png'; out = TMP + 'ps_out.png'
    if os.path.exists(out): os.remove(out)
    sel = []
    for i, (x0, y0, x1, y1) in enumerate(rects):
        sel.append(f"d.selection.select([[{x0},{y0}],[{x1},{y0}],[{x1},{y1}],[{x0},{y1}]], {'SelectionType.REPLACE' if i == 0 else 'SelectionType.EXTEND'});")
    for k, (pts, mode) in enumerate(polys):
        mode = 'REPLACE' if (k == 0 and not rects) else mode
        sel.append("d.selection.select([" + ",".join(f"[{x:.1f},{y:.1f}]" for x, y in pts) + f"], SelectionType.{mode});")
    js = f"""
app.preferences.rulerUnits = Units.PIXELS; app.displayDialogs = DialogModes.NO;
var d = app.open(new File({json.dumps(win(src).replace(chr(92), '/'))}));
{chr(10).join(sel)}
var desc = new ActionDescriptor();
desc.putEnumerated(charIDToTypeID("Usng"), charIDToTypeID("FlCn"), stringIDToTypeID("contentAware"));
desc.putUnitDouble(charIDToTypeID("Opct"), charIDToTypeID("#Prc"), 100);
desc.putEnumerated(charIDToTypeID("Md  "), charIDToTypeID("BlnM"), charIDToTypeID("Nrml"));
executeAction(charIDToTypeID("Fl  "), desc, DialogModes.NO);
d.selection.deselect();
d.saveAs(new File({json.dumps(win(out).replace(chr(92), '/'))}), new PNGSaveOptions(), true);
d.close(SaveOptions.DONOTSAVECHANGES);
"ok";
"""
    jf = TMP + 'ps_job.jsx'
    open(jf, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                        f"$ps = New-Object -ComObject Photoshop.Application; $ps.DoJavaScriptFile('{win(jf)}')"],
                       capture_output=True, timeout=600)
    msg = (r.stdout + r.stderr).decode('cp866', 'replace').strip()
    if os.path.exists(out): shutil.move(out, dst)
    else: raise RuntimeError('photoshop: ' + msg)
    return msg


def heal_in(src, ctx, rects, out, polys=()):
    """Content-aware fill restricted to the context box ctx (only its pixels are used as source), result pasted back into src."""
    from PIL import Image
    im = Image.open(src).convert('RGB'); cx0, cy0, cx1, cy1 = ctx
    im.crop(ctx).save(TMP + 'ps_ctx.png')
    heal(TMP + 'ps_ctx.png', [(x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0) for x0, y0, x1, y1 in rects], TMP + 'ps_ctx_out.png',
         [([(x - cx0, y - cy0) for x, y in pts], m) for pts, m in polys])
    im.paste(Image.open(TMP + 'ps_ctx_out.png').convert('RGB'), (cx0, cy0)); im.save(out)


def run_jsx(js):
    jf = TMP + 'ps_job.jsx'
    open(jf, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                        f"$ps = New-Object -ComObject Photoshop.Application; $ps.DoJavaScriptFile('{win(jf)}')"], capture_output=True, timeout=600)
    return (r.stdout + r.stderr).decode('cp866', 'replace').strip()


def open_work(render_png, plan_png, psd, label='plan'):
    """Open a visible working document in the user's Photoshop: layer 'render' + layer 'plan' (registered plan, 45% opacity, Screen) - saved as PSD."""
    import shutil
    shutil.copy(render_png, TMP + 'ps_w_render.png'); shutil.copy(plan_png, TMP + 'ps_w_plan.png')
    f = lambda p: json.dumps(win(p).replace(chr(92), '/'))
    return run_jsx(f"""
app.preferences.rulerUnits = Units.PIXELS; app.displayDialogs = DialogModes.NO;
var d = app.open(new File({f(TMP + 'ps_w_render.png')})); d.activeLayer.isBackgroundLayer = false; d.activeLayer.name = 'render';
var p = app.open(new File({f(TMP + 'ps_w_plan.png')})); p.activeLayer.duplicate(d, ElementPlacement.PLACEATBEGINNING); p.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument = d; var l = d.layers[0]; l.name = '{label}'; l.blendMode = BlendMode.SCREEN; l.opacity = 45;
var o = new PhotoshopSaveOptions(); o.layers = true; d.saveAs(new File({f(psd)}), o, true);
"ok";
""")


def add_layers(psd, pngs_names):
    """Add full-canvas RGBA PNGs as named layers just above 'render' in the (open or saved) PSD; plan layer stays on top; saves PSD."""
    import shutil
    f = lambda p: json.dumps(win(p).replace(chr(92), '/'))
    parts = []
    for i, (png, name) in enumerate(pngs_names):
        tmp = TMP + f'ps_layer{i}.png'; shutil.copy(png, tmp)
        parts.append(f"""var s = app.open(new File({f(tmp)})); s.activeLayer.duplicate(d, ElementPlacement.PLACEATEND); s.close(SaveOptions.DONOTSAVECHANGES);
app.activeDocument = d; var nl = d.layers[d.layers.length - 1]; nl.name = {json.dumps(name)}; nl.move(d.layers.getByName('render'), ElementPlacement.PLACEBEFORE);""")
    return run_jsx(f"""
app.preferences.rulerUnits = Units.PIXELS; app.displayDialogs = DialogModes.NO;
var d = null; var target = new File({f(psd)});
for (var k = 0; k < app.documents.length; k++) if (app.documents[k].fullName && app.documents[k].fullName.fsName == target.fsName) d = app.documents[k];
if (!d) d = app.open(target);
app.activeDocument = d;
{chr(10).join(parts)}
var o = new PhotoshopSaveOptions(); o.layers = true; d.saveAs(target, o, true);
"ok";
""")
