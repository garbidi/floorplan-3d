// Parametric furniture library. Every builder takes (ctx, item) where item.box = [x0,z0,x1,z1] in plan px
// and heights are in metres (ctx.m converts). Built to read well in a strict top-down view.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { rnd } from './materials.js';

const W = b => b[2] - b[0], D = b => b[3] - b[1];
// seeded 2D value noise + fBm (for cloth wrinkles, fabric folds)
export function makeNoise(seed = 1) {
  const r = rnd(seed), N = 256, perm = new Uint8Array(512), val = new Float32Array(N);
  for (let i = 0; i < N; i++) { perm[i] = i; val[i] = r() * 2 - 1; }
  for (let i = N - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
  for (let i = 0; i < N; i++) perm[i + N] = perm[i];
  const sm = t => t * t * (3 - 2 * t);
  const n2 = (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi, X = xi & 255, Y = yi & 255;
    const a = val[perm[X + perm[Y]]], b = val[perm[X + 1 + perm[Y]]], c = val[perm[X + perm[Y + 1]]], d = val[perm[X + 1 + perm[Y + 1]]];
    const u = sm(xf), v = sm(yf); return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v; };
  return (x, y, oct = 4) => { let s = 0, a = 0.5, f = 1; for (let o = 0; o < oct; o++) { s += a * n2(x * f, y * f); a *= 0.5; f *= 2.1; } return s; };
}
const cx = b => (b[0] + b[2]) / 2, cz = b => (b[1] + b[3]) / 2;
const inset = (b, k) => [b[0] + k, b[1] + k, b[2] - k, b[3] - k];

export function helpers(ctx) {
  const { scene, m } = ctx;
  const add = (mesh, cast = true) => { mesh.castShadow = cast; mesh.receiveShadow = true; scene.add(mesh); return mesh; };
  // rounded box from a plan rect and heights in metres
  const box = (b, y0, y1, mat, rM = 0, seg = 4) => {
    const w = W(b), d = D(b), h = m(y1 - y0), r = Math.max(0, Math.min(m(rM), w / 2 - 0.05, d / 2 - 0.05, h / 2 - 0.05));
    const g = r > 0.05 ? new RoundedBoxGeometry(w, h, d, seg, r) : new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(g, mat); mesh.position.set(cx(b), m(y0) + h / 2, cz(b)); return add(mesh);
  };
  const cyl = (x, z, rPx, y0, y1, mat, seg = 48, rTopPx) => {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(rTopPx ?? rPx, rPx, m(y1 - y0), seg), mat);
    mesh.position.set(x, m((y0 + y1) / 2), z); return add(mesh);
  };
  // "inflated" cushion: rounded box whose top bulges (pillows, seats, mattress tops)
  const cushion = (b, y0, y1, mat, bulgeM = 0.03, rM = 0.04, rot = 0) => {
    const w = W(b), d = D(b), h = m(y1 - y0), r = Math.min(m(rM), w / 2 - 0.1, d / 2 - 0.1, h / 2 - 0.1);
    const g = new RoundedBoxGeometry(w, h, d, 6, Math.max(r, 0.1)); const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y <= 0) continue; const nx = p.getX(i) / (w / 2), nz = p.getZ(i) / (d / 2);
      p.setY(i, y + m(bulgeM) * (y / (h / 2)) * Math.max(0, 1 - nx * nx) * Math.max(0, 1 - nz * nz)); }
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, mat); mesh.position.set(cx(b), m(y0) + h / 2, cz(b)); mesh.rotation.y = rot; return add(mesh);
  };
  // cloth sheet over a rect: subdivided plane with folds, draping down at the edges
  const cloth = (b, y, mat, { seed = 3, amp = 0.03, drop = 0.18, scaleM = 0.35, stretch = 2.2, dir = 'x', rough = 0.012 } = {}) => {
    const w = W(b), d = D(b), g = new THREE.PlaneGeometry(w, d, 220, 220); g.rotateX(-Math.PI / 2);
    const p = g.attributes.position, nz = makeNoise(seed), fine = makeNoise(seed + 7), edge = m(0.07), sc = m(scaleM);
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i);
      const u = dir === 'x' ? x / (sc * stretch) : x / sc, v = dir === 'x' ? z / sc : z / (sc * stretch);
      const ridge = 1 - Math.abs(nz(u, v, 4)) * 2;                     // ridged noise -> soft creases
      const hh = m(amp) * ridge + m(rough) * fine(x / m(0.08), z / m(0.08), 3);
      const ex = Math.max(0, Math.abs(x) - (w / 2 - edge)) / edge, ez = Math.max(0, Math.abs(z) - (d / 2 - edge)) / edge;
      p.setY(i, m(y) + hh * (1 - 0.6 * Math.min(1, Math.max(ex, ez))) - m(drop) * Math.min(1, Math.max(ex, ez)) ** 2); }
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, mat); mesh.position.set(cx(b), 0, cz(b)); return add(mesh);
  };
  // soft pillow: squashed sphere mapped to a squircle footprint, thinner at the corners
  const pillow = (b, y0, thickM, mat, rot = 0) => {
    const w = W(b), d = D(b), t = m(thickM), g = new THREE.SphereGeometry(1, 48, 32), p = g.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const X = Math.sign(x) * Math.abs(x) ** 0.3, Z = Math.sign(z) * Math.abs(z) ** 0.3;
      const k = 1 - 0.55 * Math.max(Math.abs(X), Math.abs(Z)) ** 6;
      p.setXYZ(i, X * w / 2, y * t / 2 * k, Z * d / 2); }
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, mat); mesh.position.set(cx(b), m(y0) + t / 2, cz(b)); mesh.rotation.y = rot; return add(mesh);
  };
  const lathe = (x, z, profileM, mat, seg = 64, y0 = 0) => {
    const pts = profileM.map(([r, y]) => new THREE.Vector2(m(r), m(y)));
    if (!mat.userData.ds) { mat.side = THREE.DoubleSide; mat.userData.ds = 1; }
    const mesh = new THREE.Mesh(new THREE.LatheGeometry(pts, seg), mat); mesh.position.set(x, m(y0), z); return add(mesh);
  };
  return { add, box, cyl, cushion, cloth, lathe, pillow };
}

// orientation helper: map local (u along length, v across depth from the wall) to plan rect for a given wall side
function sideRect(b, side, u0, u1, v0, v1) {
  // u in [0,1] along the wall, v in [0,1] from the wall into the room
  if (side === 'top') return [b[0] + W(b) * u0, b[1] + D(b) * v0, b[0] + W(b) * u1, b[1] + D(b) * v1];
  if (side === 'bottom') return [b[0] + W(b) * u0, b[3] - D(b) * v1, b[0] + W(b) * u1, b[3] - D(b) * v0];
  if (side === 'left') return [b[0] + W(b) * v0, b[1] + D(b) * u0, b[0] + W(b) * v1, b[1] + D(b) * u1];
  return [b[2] - W(b) * v1, b[1] + D(b) * u0, b[2] - W(b) * v0, b[1] + D(b) * u1];
}

export function buildItems(ctx, items, lampLight) {
  const { M, m } = ctx; const H = helpers(ctx); const { box, cyl, cushion, cloth, lathe, add, pillow } = H;
  const B = {};

  B.window = (it) => {                    // glazing in a wall opening: sill, frame, glass, sheer curtains on the room side
    const b = it.box, vert = D(b) > W(b), side = it.room || (vert ? 'right' : 'bottom');
    box(b, 0, 0.9, M.frame);                                    // sill / lower wall part in light colour
    box(b, 0.9, 0.95, M.frame);
    const g = inset(b, 1); box(g, 0.95, 2.5, M.glass);
    if (it.curtain !== false) {             // sheer curtains gathered at both ends, wavy footprint (seen from above)
      const L = vert ? D(b) : W(b), panel = m(it.curtainM ?? 0.6), amp = m(0.04), th = m(0.02);
      for (const end of [0, 1]) {
        const pts = [], n = 40;
        for (let k = 0; k <= n; k++) { const t = k / n * panel; pts.push([t, Math.sin(t / m(0.05) * Math.PI) * amp]); }
        const sh = new THREE.Shape(); sh.moveTo(pts[0][0], pts[0][1] + th); pts.forEach(([u, v]) => sh.lineTo(u, v + th)); [...pts].reverse().forEach(([u, v]) => sh.lineTo(u, v - th));
        const g = new THREE.ExtrudeGeometry(sh, { depth: m(2.4), bevelEnabled: false }); g.rotateX(Math.PI / 2); g.translate(0, m(2.45), 0);
        const mesh = new THREE.Mesh(g, M.fabric(0xf4efe9, { linen: true, ns: 0.2 })); mesh.material.transparent = true; mesh.material.opacity = 0.9;
        const off = amp + m(0.03), u0 = end ? L - panel - m(0.02) : m(0.02);
        if (!vert) { mesh.position.set(b[0] + u0, 0, side === 'bottom' ? b[3] + off : b[1] - off); }
        else { mesh.rotation.y = -Math.PI / 2; mesh.position.set(side === 'right' ? b[2] + off : b[0] - off, 0, b[1] + u0); }
        add(mesh);
      }
    }
  };
  B.partition = (it) => {                  // interior glazed partition: low wall + dark thin frame + clear glass
    const b = it.box; box(b, 0, 0.1, M.wall); box(inset(b, 0.5), 0.1, 2.5, new THREE.MeshPhysicalMaterial({ color: 0xe3eeef, transparent: true, opacity: 0.22, roughness: 0.03 }));
    const vert = D(b) > W(b), t = Math.min(W(b), D(b));
    if (vert) { box([b[0], b[1], b[2], b[1] + t * 0.6], 0, 2.5, M.black); box([b[0], b[3] - t * 0.6, b[2], b[3]], 0, 2.5, M.black); }
    else { box([b[0], b[1], b[0] + t * 0.6, b[3]], 0, 2.5, M.black); box([b[2] - t * 0.6, b[1], b[2], b[3]], 0, 2.5, M.black); }
    box(vert ? [cx(b) - 0.8, b[1], cx(b) + 0.8, b[3]] : [b[0], cz(b) - 0.8, b[2], cz(b) + 0.8], 2.45, 2.5, M.black);
  };
  B.glass = B.window;

  B.armchair = (it) => {                  // upholstered armchair: rounded back + arms + soft seat; back towards local -z
    const b = it.box, w = W(b), d = D(b), fab = M.fabric(it.color || 0xcdbeb7, { boucle: true, ns: 0.9 }), g = new THREE.Group();
    const part = (x0, z0, x1, z1, y0, y1, rM, bulge) => { const geo = new RoundedBoxGeometry(x1 - x0, m(y1 - y0), z1 - z0, 8, Math.min(m(rM), (x1 - x0) / 2 - .1, (z1 - z0) / 2 - .1, m(y1 - y0) / 2 - .1));
      const p = geo.attributes.position; for (let i = 0; i < p.count; i++) { const y = p.getY(i); if (y > 0) { const nx = p.getX(i) / ((x1 - x0) / 2), nz = p.getZ(i) / ((z1 - z0) / 2); p.setY(i, y + m(bulge) * Math.max(0, 1 - nx * nx) * Math.max(0, 1 - nz * nz)); } }
      geo.computeVertexNormals(); const mm = new THREE.Mesh(geo, fab); mm.position.set((x0 + x1) / 2 - w / 2, m((y0 + y1) / 2), (z0 + z1) / 2 - d / 2); mm.castShadow = mm.receiveShadow = true; g.add(mm); };
    part(0.02 * w, 0.02 * d, 0.98 * w, 0.98 * d, 0.1, 0.4, 0.1, 0);        // base
    part(0, 0, w, d * 0.3, 0.3, 0.82, 0.14, 0.04);                          // back, rounded
    part(0, 0.05 * d, w * 0.2, d, 0.3, 0.64, 0.1, 0.04);                    // arms
    part(w * 0.8, 0.05 * d, w, d, 0.3, 0.64, 0.1, 0.04);
    part(w * 0.18, d * 0.26, w * 0.82, d * 0.99, 0.38, 0.5, 0.1, 0.05);     // seat cushion
    for (const [fx, fz] of [[0.12, 0.1], [0.88, 0.1], [0.12, 0.9], [0.88, 0.9]]) { const l = new THREE.Mesh(new THREE.CylinderGeometry(m(0.015), m(0.01), m(0.1), 8), M.darkwood); l.position.set((fx - 0.5) * w, m(0.05), (fz - 0.5) * d); g.add(l); }
    g.position.set(cx(b), 0, cz(b)); g.rotation.y = -(it.rot || 0) * Math.PI / 180; ctx.scene.add(g);
  };

  B.floorlamp = (it) => {
    const b = it.box, x = cx(b), z = cz(b), r = Math.min(W(b), D(b)) / 2;
    cyl(x + r * 0.35, z + r * 0.9, m(0.012), 0, 1.45, M.black, 12);                 // stem (offset -> visible)
    cyl(x + r * 0.35, z + r * 0.9, m(0.14), 0, 0.02, M.black, 32);                  // base
    lathe(x, z, [[r / m(1) * 0.8, 1.72], [r / m(1) * 0.82, 1.71], [r / m(1), 1.45], [r / m(1) * 1.01, 1.445]], M.shade, 64).castShadow = false;
    const ribs = 12; for (let k = 0; k < ribs; k++) { const a = k / ribs * Math.PI * 2; const s = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, r * 0.95, 4), M.frame); s.position.set(x + Math.cos(a) * r * 0.75, m(1.6), z + Math.sin(a) * r * 0.75); s.rotation.z = Math.PI / 2; s.rotation.y = -a; ctx.scene.add(s); }
    cyl(x, z, r * 0.12, 1.5, 1.72, M.bulb, 16).castShadow = false;
    lampLight(x, z, 1.25, it.power ?? 1.2, 4.5);
  };

  B.roundtable = (it) => { const b = it.box, r = Math.min(W(b), D(b)) / 2;
    cyl(cx(b), cz(b), r, 0.5, 0.53, M.oak, 64); cyl(cx(b), cz(b), m(0.02), 0, 0.5, M.black, 12); cyl(cx(b), cz(b), r * 0.5, 0, 0.015, M.black, 32); };

  B.plant = (it) => {                    // monstera: dark pot + 7-9 large glossy leaves with edge slits
    const b = it.box, x = cx(b), z = cz(b), R = Math.min(W(b), D(b)) / 2, r = rnd(Math.round(x * 7 + z));
    lathe(x, z, [[0.001, 0], [0.15, 0], [0.19, 0.4], [0.2, 0.42], [0.17, 0.42], [0.17, 0.39]].map(([a, y]) => [a * R / m(0.62), y]), M.plantPot, 48);
    cyl(x, z, R * 0.27, 0.36, 0.39, new THREE.MeshStandardMaterial({ color: 0x2e2218, roughness: 1 }), 24);
    const n = it.leaves || 8;
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2 + (r() - 0.5) * 0.5, L = R * (0.72 + r() * 0.25), Wd = L * 0.95;
      // heart-shaped outline with slits cut from the edge towards the midrib
      const pts = [], N = 90, slits = [0.28, 0.42, 0.56, 0.7];
      for (let k = 0; k <= N; k++) { const t = k / N * Math.PI * 2; // param around the leaf
        const u = (1 - Math.cos(t)) / 2, side = Math.sin(t) >= 0 ? 1 : -1;
        let half = Wd / 2 * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.02)), 0.75) * (u < 0.12 ? 0.6 + u * 3.3 : 1);
        for (const sl of slits) if (Math.abs(u - sl) < 0.022) half *= 0.28;          // slit
        pts.push(new THREE.Vector2(u * L, side * half)); }
      const geo = new THREE.ShapeGeometry(new THREE.Shape(pts), 1); geo.rotateX(-Math.PI / 2);
      const p = geo.attributes.position; for (let k = 0; k < p.count; k++) { const u = p.getX(k) / L, v = p.getZ(k) / (Wd / 2); p.setY(k, m(0.08) * Math.sin(u * Math.PI) - m(0.04) * v * v * u); }
      geo.computeVertexNormals();
      const mat = new THREE.MeshPhysicalMaterial({ color: new THREE.Color().setHSL(0.25 + r() * 0.03, 0.42, 0.2 + r() * 0.07), roughness: 0.38, clearcoat: 0.3, side: THREE.DoubleSide });
      const leaf = new THREE.Mesh(geo, mat); leaf.position.set(x + Math.cos(a) * R * 0.12, m(0.6 + r() * 0.35), z + Math.sin(a) * R * 0.12); leaf.rotation.y = -a;
      leaf.castShadow = true; leaf.receiveShadow = true; ctx.scene.add(leaf);
      const st = new THREE.Mesh(new THREE.CylinderGeometry(m(0.006), m(0.009), R * 0.45, 6), mat); st.position.set(x + Math.cos(a) * R * 0.15, m(0.55), z + Math.sin(a) * R * 0.15); st.rotation.z = Math.PI / 2; st.rotation.y = -a; ctx.scene.add(st);
    }
  };

  B.nightstand = (it) => { const b = it.box; box(b, 0, 0.5, M.walnut, 0.01); box(inset(b, 1.5), 0.5, 0.52, M.oak, 0.005);
    const x = cx(b), z = cz(b), r = Math.min(W(b), D(b)) * 0.36, R1 = r / m(1);
    lathe(x, z, [[0.001, 0.52], [0.06, 0.52], [0.07, 0.6], [0.05, 0.72], [0.015, 0.78]].map(([a, y]) => [a * r / m(0.2), y]), M.ceramic, 32);
    lathe(x, z, [[R1 * 0.62, 0.99], [R1 * 0.64, 0.98], [R1, 0.78], [R1 * 1.01, 0.775]], M.shade, 64).castShadow = false;   // open shade
    const bl = new THREE.Mesh(new THREE.SphereGeometry(r * 0.2, 24, 16), M.bulb); bl.position.set(x, m(0.9), z); ctx.scene.add(bl);
    lampLight(x, z, 0.92, it.power ?? 0.55, 3.2); };

  B.bed = (it) => {
    const b = it.box, side = it.head || 'top';
    const hb = m(it.hbM ?? 0.1);
    const R = (u0, u1, v0, v1) => sideRect(b, side, u0, u1, v0, v1);     // u across the bed width, v from the headboard
    const len = (side === 'left' || side === 'right') ? W(b) : D(b), vk = hb / len;
    box(R(0.005, 0.995, vk, 1), 0, 0.3, M.fabric(it.hbColor || 0x8f8886, { linen: true }), 0.03);        // upholstered base
    cushion(R(0, 1, 0, vk), 0, 1.0, M.fabric(it.hbColor || 0x8f8886, { linen: true }), 0.02, 0.05);        // headboard
    cushion(R(0.02, 0.98, vk, 0.99), 0.3, 0.5, M.fabric(0xe9e4e1, { linen: true, ns: 0.4 }), 0.02, 0.06);   // mattress
    const pc = it.pillowColor || [0xa9a2a3, 0x9b9395];
    const pairs = it.single ? [[0.06, 0.94]] : [[0.03, 0.49], [0.51, 0.97]];
    const pm = M.fabric(pc[0], { linen: true, ns: 0.5 }), pm2 = M.fabric(pc[1], { linen: true, ns: 0.5 });
    const rot = (side === 'left' || side === 'right') ? Math.PI / 2 : 0;
    for (const [u0, u1] of pairs) {
      pillow(R(u0, u1, vk + 0.01, vk + 0.22), 0.5, 0.15, pm);
      if (!it.single) pillow(R(u0 + 0.1, u1 - 0.1, vk + 0.19, vk + 0.29), 0.55, 0.12, pm2);
    }
    const duv = new THREE.MeshPhysicalMaterial({ color: it.duvet || 0xc3bdbd, roughness: 0.55, sheen: 0.8, sheenRoughness: 0.35, sheenColor: new THREE.Color(0xffffff) });
    const dir = (side === 'left' || side === 'right') ? 'x' : 'z';
    cloth(R(-0.03, 1.03, vk + 0.28, 1.02), 0.6, duv, { seed: 11, amp: 0.07, drop: 0.32, scaleM: 0.42, stretch: 1.8, dir, rough: 0.003 });
    if (it.fold !== false) cloth(R(-0.03, 1.03, vk + 0.24, vk + 0.36), 0.66, duv, { seed: 5, amp: 0.03, drop: 0.3, scaleM: 0.3, stretch: 2.5, dir: dir === 'x' ? 'z' : 'x', rough: 0.002 });
  };

  B.tv = (it) => { const b = it.box; box(b, 1.0, 1.08, M.blackGlass, 0.004); };

  B.closet = (it) => {                      // wardrobe: carcass, optional glass fronts, rail + garments or folded stacks, warm LED
    const b = it.box, side = it.backSide || 'left', along = side === 'top' || side === 'bottom';
    const th = m(0.02), car = it.carcass === 'light' ? M.oak : M.walnut;
    const R = (u0, u1, v0, v1) => sideRect(b, side, u0, u1, v0, v1);
    const L = along ? W(b) : D(b), Dp = along ? D(b) : W(b), fv = 1 - th / Dp;     // fv: front edge (v)
    const Hc = it.hM ?? 2.2;
    box(R(0, 1, 0, 0.03), 0, Hc, car); box(R(0, th / L, 0, 1), 0, Hc, car); box(R(1 - th / L, 1, 0, 1), 0, Hc, car);
    box(R(0, 1, 0, 1), 0, 0.03, M.darkwood);
    const inner = new THREE.MeshStandardMaterial({ map: M.walnut.map, color: 0xcdb6a4, roughness: 0.6 });
    box(R(th / L, 1 - th / L, 0.03, fv), 0, 0.05, inner);                                  // light inner floor
    const secs = it.sections || 1; for (let k = 1; k < secs; k++) box(R(k / secs - th / L / 2, k / secs + th / L / 2, 0, 1), 0, Hc, car);
    const kind = it.fill || 'hang', r = rnd(Math.round(cx(b) * 3 + cz(b)));
    const cols = it.colors || [0xf1ece4, 0xe6ddd1, 0xd9cdbd, 0xece6dd, 0xcfc3b4, 0xf6f2ec];
    for (let s = 0; s < secs; s++) {
      const u0 = s / secs + th / L * 1.5, u1 = (s + 1) / secs - th / L * 1.5;
      if (kind === 'shelf') {                 // folded items on shelves, stacked along the length
        const n = Math.max(1, Math.round((u1 - u0) * L / m(it.stackM ?? 0.2)));
        for (let k = 0; k < n; k++) { const a = u0 + (u1 - u0) * (k + 0.06) / n, e = u0 + (u1 - u0) * (k + 0.94) / n;
          const c = (it.stackColors || [0x6b5b53, 0x8a7a70, 0x5c4f49, 0x9b8b80, 0x75665e])[k % 5];
          cushion(R(a, e, 0.08 + r() * 0.03, 0.9 - r() * 0.03), 1.0 + (k % 2) * 0.02, 1.08 + (k % 2) * 0.02, M.fabric(c, { linen: true, ns: 0.5 }), 0.02, 0.025); }
      } else {
        box(R(u0, u1, 0.49, 0.51), 1.9, 1.92, M.chrome);                  // rail
        const n = Math.max(2, Math.round((u1 - u0) * L / m(it.pitchM ?? 0.09)));
        for (let k = 0; k < n; k++) {
          const t = u0 + (u1 - u0) * (k + 0.5 + (r() - 0.5) * 0.3) / n, tw = (u1 - u0) / n * (0.35 + r() * 0.3);
          const col = cols[Math.floor(r() * cols.length)];
          // garment seen from above: narrow body with rounded shoulders, hanging from the rail
          cushion(R(t - tw / 2, t + tw / 2, 0.12 + r() * 0.06, 0.88 - r() * 0.06), 1.0 + r() * 0.3, 1.86, M.fabric(col, { linen: true, ns: 0.4 }), 0.03, 0.05);
          box(R(t - 0.003, t + 0.003, 0.44, 0.56), 1.86, 1.9, M.oak);     // hanger
        }
      }
      // warm LED strip along the front top of the section + its light
      box(R(u0, u1, fv - 0.05, fv - 0.03), Hc - 0.05, Hc - 0.04, M.led);
      const lr = R((u0 + u1) / 2, (u0 + u1) / 2 + 0.001, 0.5, 0.501);
      const led = new THREE.PointLight(0xffc98f, m(1) * m(1) * 0.08 * (ctx.S.lampScale ?? 1), m(0.9), 2); led.position.set(lr[0], m(Hc - 0.4), lr[1]); ctx.scene.add(led);
    }
    if (it.glass) {                          // glass fronts with a thin frame and a centre mullion per section
      box(R(0, 1, fv, 1), 0.05, Hc - 0.03, M.cabGlass);
      box(R(0, 1, fv, 1), Hc - 0.03, Hc, car);
      for (let s = 0; s <= secs; s++) { const u = Math.min(1 - th / L, Math.max(0, s / secs - th / L / 2)); box(R(u, u + th / L, fv - 0.01, 1), 0.05, Hc, car); }
      for (let s = 0; s < secs; s++) { const u = (s + 0.5) / secs; box(R(u - 0.003, u + 0.003, fv, 1), 0.05, Hc, M.frame); }
    }
  };

  B.leaf = (it) => {                        // door leaf with handle
    const [hx, hz] = it.hinge, a = (it.angle || 0) * Math.PI / 180, L = it.len, th = it.thick || m(0.04);
    const mat = it.dark ? new THREE.MeshStandardMaterial({ color: 0x2c2724, roughness: 0.35, metalness: 0.5 }) : M.walnut;
    const g = new RoundedBoxGeometry(L, m(2.05), th, 3, Math.min(th / 2 - 0.05, 1.5));
    const mesh = new THREE.Mesh(g, mat); mesh.position.set(hx + Math.cos(a) * L / 2, m(1.025), hz + Math.sin(a) * L / 2); mesh.rotation.y = -a; add(mesh);
    const hd = new THREE.Mesh(new THREE.BoxGeometry(m(0.12), m(0.02), th + m(0.05)), M.chrome); hd.position.set(hx + Math.cos(a) * (L - m(0.08)), m(2.06), hz + Math.sin(a) * (L - m(0.08))); hd.rotation.y = -a; ctx.scene.add(hd);
  };

  B.table = (it) => { const b = it.box; box(b, 0.72, 0.75, M.walnut, 0.008);
    for (const [x, z] of [[b[0] + m(0.05), b[1] + m(0.05)], [b[2] - m(0.05), b[1] + m(0.05)], [b[0] + m(0.05), b[3] - m(0.05)], [b[2] - m(0.05), b[3] - m(0.05)]]) cyl(x, z, m(0.02), 0, 0.72, M.walnut, 12);
    for (const p of it.plates || []) { const r = m(0.12); lathe(p[0], p[1], [[0.001, 0.75], [0.09, 0.752], [0.12, 0.765], [0.125, 0.77]].map(([a, y]) => [a * r / m(0.125), y]), M.ceramic, 48);
      lathe(p[0], p[1], [[0.001, 0.77], [0.06, 0.77], [0.08, 0.785]].map(([a, y]) => [a * r / m(0.125), y]), M.ceramic, 48);
      box([p[0] + r * 1.15, p[1] - r * 0.7, p[0] + r * 1.2, p[1] + r * 0.7], 0.75, 0.755, M.chrome); box([p[0] - r * 1.2, p[1] - r * 0.7, p[0] - r * 1.15, p[1] + r * 0.7], 0.75, 0.755, M.chrome); }
    if (it.candle) { const [x, z] = it.candle; lathe(x, z, [[0.001, 0.75], [0.04, 0.75], [0.045, 0.83], [0.03, 0.84]], M.glass, 32); lampLight(x, z, 0.82, 0.18, 1.5); }
  };

  B.chair = (it) => { const b = it.box, back = it.back || 'left', fab = M.fabric(it.color || 0x9e928c, { boucle: true, ns: 0.8 });
    const R = (u0, u1, v0, v1) => sideRect(b, back, u0, u1, v0, v1);
    for (const [u, v] of [[0.15, 0.2], [0.85, 0.2], [0.15, 0.85], [0.85, 0.85]]) { const q = R(u - 0.02, u + 0.02, v - 0.02, v + 0.02); cyl(cx(q), cz(q), m(0.012), 0, 0.45, M.black, 8); }
    cushion(R(0.04, 0.96, 0.12, 0.98), 0.42, 0.5, fab, 0.035, 0.09);                     // seat, soft rounded
    cushion(R(0.0, 1.0, 0.0, 0.2), 0.45, 0.82, fab, 0.03, 0.08);                          // curved back
    cushion(R(0.0, 0.14, 0.0, 0.6), 0.45, 0.68, fab, 0.02, 0.06); cushion(R(0.86, 1.0, 0.0, 0.6), 0.45, 0.68, fab, 0.02, 0.06); };

  B.counter = (it) => { const b = it.box; box(b, 0, 0.86, M.walnut, 0.003);
    box(inset(b, -0.5), 0.86, 0.9, it.top === 'stone' ? M.stone : M.counterTop, 0.004); };
  B.cooktop = (it) => { const b = it.box; box(inset(b, 1), 0.9, 0.905, M.blackGlass, 0.004);
    const zones = it.zones || 4, rr = Math.min(W(b), D(b)) * 0.2;
    const pos = zones === 4 ? [[.27, .27], [.73, .27], [.27, .73], [.73, .73]] : [[.5, .28], [.5, .72]];
    for (const [fx, fz] of pos) { const ring = new THREE.Mesh(new THREE.RingGeometry(rr * 0.88, rr, 64), new THREE.MeshBasicMaterial({ color: 0x5c5c5c })); ring.rotation.x = -Math.PI / 2; ring.position.set(b[0] + W(b) * fx, m(0.906), b[1] + D(b) * fz); ctx.scene.add(ring); } };
  B.sink = (it) => { const b = it.box; const steel = it.kitchen; box(inset(b, 1), 0.9, 0.915, steel ? M.steel : M.ceramic, 0.01);
    const k = Math.min(W(b), D(b)) * 0.1, bowlMat = steel ? new THREE.MeshStandardMaterial({ color: 0x8d8c88, metalness: 0.6, roughness: 0.3, side: THREE.BackSide }) : new THREE.MeshPhysicalMaterial({ color: 0xf1f0ec, roughness: 0.15, clearcoat: 1, side: THREE.BackSide });
    if (it.split) { const xs = b[0] + k + (W(b) - 2 * k) * it.split; box([b[0] + k, b[1] + k, xs - k / 3, b[3] - k], 0.72, 0.9155, bowlMat, 0.03); box([xs + k / 3, b[1] + k, b[2] - k, b[3] - k], 0.72, 0.9155, bowlMat, 0.03); }
    else box(inset(b, k), 0.72, 0.9155, bowlMat, 0.03);
    const f = it.faucet || 'right'; const fx = f === 'right' ? b[2] - W(b) * 0.1 : f === 'left' ? b[0] + W(b) * 0.1 : cx(b), fz = f === 'top' ? b[1] + D(b) * 0.1 : f === 'bottom' ? b[3] - D(b) * 0.1 : cz(b);
    cyl(fx, fz, m(0.02), 0.9, 1.15, M.chrome, 16); const sp = new THREE.Mesh(new THREE.CylinderGeometry(m(0.012), m(0.012), m(0.2), 12), M.chrome); sp.rotation.z = Math.PI / 2; sp.position.set(fx - (f === 'right' ? m(0.1) : -m(0.1)), m(1.15), fz); if (f === 'top' || f === 'bottom') { sp.rotation.set(Math.PI / 2, 0, 0); sp.position.set(fx, m(1.15), fz + (f === 'top' ? m(0.1) : -m(0.1))); } ctx.scene.add(sp); };
  B.fridge = (it) => { const b = it.box; box(b, 0, 0.86, M.steel, 0.01); box(inset(b, 2), 0.86, 0.87, M.steel, 0.01); };
  B.dishwasher = B.fridge;
  B.kettle = (it) => { const b = it.box, r = Math.min(W(b), D(b)) / 2; lathe(cx(b), cz(b), [[0.001, 0.9], [0.08, 0.9], [0.09, 0.95], [0.075, 1.08], [0.03, 1.1], [0.001, 1.1]].map(([a, y]) => [a * r / m(0.09), y]), M.steel, 48); };
  B.cup = (it) => { const b = it.box, r = Math.min(W(b), D(b)) / 2; lathe(cx(b), cz(b), [[0.001, 0.9], [0.04, 0.9], [0.045, 0.99], [0.04, 0.99], [0.035, 0.91]].map(([a, y]) => [a * r / m(0.045), y]), M.ceramic, 32); };
  B.console = (it) => { const b = it.box; box(b, 0.05, it.hM ?? 0.9, M.walnut, 0.01); box(inset(b, 1), (it.hM ?? 0.9), (it.hM ?? 0.9) + 0.02, M.oak, 0.005); };
  B.washer = (it) => { const b = it.box; box(b, 0, 0.85, M.white, 0.02); box(inset(b, 2), 0.85, 0.86, M.white, 0.01); };
  B.cabinet = (it) => { const b = it.box; box(b, 0, it.hM ?? 0.85, new THREE.MeshStandardMaterial({ color: it.color || 0xeadfd3, roughness: 0.45 }), 0.01); };
  B.appliance = (it) => { const b = it.box; box(b, 0.9, 1.2, M.steel, 0.02); box(inset(b, W(b) * 0.2), 1.2, 1.21, M.black, 0.01); };

  B.ledge = (it) => { const b = it.box; box(b, 0, 1.1, M.oak, 0.005); const along = W(b) > D(b), Lp = along ? W(b) : D(b);
    const at = (t) => along ? [b[0] + W(b) * t, cz(b)] : [cx(b), b[1] + D(b) * t];
    const rr = Math.min(W(b), D(b)) * 0.3;
    [[0.12, 0xf1ece4, 0.18], [0.3, 0xa27d62, 0.14], [0.47, 0xe8e2d8, 0.2]].forEach(([t, col, h]) => { const [x, z] = at(t);
      lathe(x, z, [[0.001, 1.1], [0.1, 1.1], [0.1, 1.1 + h], [0.05, 1.12 + h], [0.02, 1.16 + h], [0.001, 1.16 + h]].map(([a, y]) => [a * rr / m(0.1), y]), new THREE.MeshPhysicalMaterial({ color: col, roughness: 0.3, clearcoat: 0.6 }), 32); });
    const t0 = 0.6, t1 = 0.85; const tb = along ? [b[0] + W(b) * t0, b[1] + D(b) * 0.1, b[0] + W(b) * t1, b[3] - D(b) * 0.1] : [b[0] + W(b) * 0.1, b[1] + D(b) * t0, b[2] - W(b) * 0.1, b[1] + D(b) * t1];
    cushion(tb, 1.1, 1.18, M.fabric(0xd9d3cc, { ns: 0.8 }), 0.02, 0.03); };

  B.toilet = (it) => {                     // wall-hung WC seen from above: D-shaped bowl + seat + lid gap
    const b = it.box, face = it.face || 'down', vert = face === 'up' || face === 'down';
    const L = vert ? D(b) : W(b), Wd = vert ? W(b) : D(b);
    const shp = (l, w, k) => { const s = new THREE.Shape(); s.moveTo(0, -w / 2); s.lineTo(l * k, -w / 2); s.absellipse(l * k, 0, l * (1 - k), w / 2, -Math.PI / 2, Math.PI / 2, false); s.lineTo(0, w / 2); s.lineTo(0, -w / 2); return s; };
    const g = new THREE.Group();
    const body = new THREE.Mesh(new THREE.ExtrudeGeometry(shp(L, Wd, 0.4), { depth: m(0.3), bevelEnabled: true, bevelThickness: m(0.03), bevelSize: m(0.03), bevelSegments: 6, curveSegments: 48 }), M.ceramic);
    body.rotation.x = -Math.PI / 2; body.position.y = m(0.1); g.add(body);
    const seat = new THREE.Mesh(new THREE.ExtrudeGeometry(shp(L * 0.9, Wd * 0.9, 0.35), { depth: m(0.02), bevelEnabled: true, bevelThickness: m(0.01), bevelSize: m(0.012), bevelSegments: 4, curveSegments: 48 }), M.ceramic);
    seat.rotation.x = -Math.PI / 2; seat.position.set(L * 0.06, m(0.43), 0); g.add(seat);
    g.traverse(o => { if (o.isMesh) o.castShadow = o.receiveShadow = true; });
    g.position.set(face === 'left' ? b[2] : face === 'right' ? b[0] : cx(b), 0, face === 'up' ? b[3] : face === 'down' ? b[1] : cz(b));
    g.rotation.y = { right: 0, left: Math.PI, down: -Math.PI / 2, up: Math.PI / 2 }[face]; ctx.scene.add(g);
  };
  B.toilet2 = B.toilet;

  B.basin = (it) => {                      // round washbasin on the wall + round mirror strip
    const b = it.box, r = Math.min(W(b), D(b)) / 2, x = cx(b), z = cz(b);
    lathe(x, z, [[0.001, 0.72], [0.1, 0.72], [0.19, 0.78], [0.22, 0.86], [0.225, 0.87], [0.2, 0.87], [0.17, 0.8], [0.06, 0.78], [0.001, 0.78]].map(([a, y]) => [a * r / m(0.225), y]), M.ceramic, 64);
    const wall = it.wall || 'right'; const fx = wall === 'right' ? b[2] - m(0.03) : wall === 'left' ? b[0] + m(0.03) : x, fz = wall === 'top' ? b[1] + m(0.03) : wall === 'bottom' ? b[3] - m(0.03) : z;
    cyl(fx, fz, m(0.015), 0.87, 1.0, M.chrome, 16);
  };
  B.vanity2 = (it) => B.basin({ ...it, box: it.basin || it.box, wall: it.faucet });

  B.bathtub = (it) => {                    // acrylic tub: hollow rounded rim + deep concave basin + mixer
    const b = it.box, w = W(b), d = D(b);
    const rr = (sh, x0, y0, x1, y1, r) => { sh.moveTo(x0 + r, y0); sh.lineTo(x1 - r, y0); sh.quadraticCurveTo(x1, y0, x1, y0 + r); sh.lineTo(x1, y1 - r); sh.quadraticCurveTo(x1, y1, x1 - r, y1); sh.lineTo(x0 + r, y1); sh.quadraticCurveTo(x0, y1, x0, y1 - r); sh.lineTo(x0, y0 + r); sh.quadraticCurveTo(x0, y0, x0 + r, y0); return sh; };
    const k = Math.min(w, d) * 0.08, outer = rr(new THREE.Shape(), -w / 2, -d / 2, w / 2, d / 2, m(0.05));
    outer.holes.push(rr(new THREE.Path(), -w / 2 + k, -d / 2 + k, w / 2 - k, d / 2 - k, Math.min(w, d) * 0.32));
    const g = new THREE.ExtrudeGeometry(outer, { depth: m(0.56), bevelEnabled: true, bevelThickness: m(0.015), bevelSize: m(0.015), bevelSegments: 4, curveSegments: 24 });
    g.rotateX(-Math.PI / 2); const rim = new THREE.Mesh(g, M.ceramic); rim.position.set(cx(b), 0, cz(b)); add(rim);
    // basin: shallow dish whose centre is lowest -> reads as depth from above
    const bw = w - 2 * k, bd = d - 2 * k, bg = new THREE.PlaneGeometry(bw, bd, 80, 40); bg.rotateX(-Math.PI / 2);
    const p = bg.attributes.position;
    for (let q = 0; q < p.count; q++) { const nx = Math.abs(p.getX(q)) / (bw / 2), nz = Math.abs(p.getZ(q)) / (bd / 2); const e = Math.max(nx ** 4, nz ** 2.5); p.setY(q, m(0.2) + m(0.36) * Math.min(1, e) ** 1.5); }
    bg.computeVertexNormals();
    const basin = new THREE.Mesh(bg, new THREE.MeshPhysicalMaterial({ color: 0xeef0f0, roughness: 0.14, clearcoat: 1, side: THREE.DoubleSide })); basin.position.set(cx(b), 0, cz(b)); add(basin);
    const drain = side => 0; void drain;
    const side = it.mixer || 'right', mx = side === 'left' ? b[0] + w * 0.05 : b[2] - w * 0.05;
    cyl(side === 'left' ? b[0] + w * 0.16 : b[2] - w * 0.16, cz(b), m(0.022), 0.2, 0.215, M.chrome, 24);
    cyl(mx, cz(b), m(0.02), 0.58, 0.72, M.chrome, 16);
    const sp = new THREE.Mesh(new THREE.CylinderGeometry(m(0.012), m(0.012), m(0.14), 12), M.chrome); sp.rotation.z = Math.PI / 2; sp.position.set(mx + (side === 'left' ? m(0.07) : -m(0.07)), m(0.72), cz(b)); ctx.scene.add(sp);
  };

  B.shower = (it) => {                      // pentagonal tray (corner cut: it.corner tl/tr/br) + frameless glass on the open sides + rain head
    const b = it.box, cxp = it.cutX, czp = it.cutZ, corner = it.corner || 'br';
    const P = corner === 'tr' ? [[b[0], b[1]], [cxp, b[1]], [b[2], czp], [b[2], b[3]], [b[0], b[3]]] :
              corner === 'tl' ? [[cxp, b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]], [b[0], czp]] :
                                [[b[0], b[1]], [b[2], b[1]], [b[2], czp], [cxp, b[3]], [b[0], b[3]]];
    const sh = new THREE.Shape(); sh.moveTo(P[0][0], P[0][1]); P.slice(1).forEach(q => sh.lineTo(q[0], q[1])); sh.lineTo(P[0][0], P[0][1]);
    const g = new THREE.ExtrudeGeometry(sh, { depth: m(0.05), bevelEnabled: true, bevelThickness: m(0.01), bevelSize: m(0.01), bevelSegments: 3 });
    g.rotateX(Math.PI / 2); const tray = new THREE.Mesh(g, M.ceramic); tray.position.y = m(0.05); add(tray);
    const drain = corner === 'tr' ? [b[0] + W(b) * 0.3, b[3] - D(b) * 0.3] : corner === 'tl' ? [b[2] - W(b) * 0.3, b[3] - D(b) * 0.3] : [b[0] + W(b) * 0.3, b[1] + D(b) * 0.3];
    cyl(drain[0], drain[1], m(0.04), 0.05, 0.056, M.chrome, 32);
    const open = corner === 'tr' ? [[P[0], P[1]], [P[1], P[2]], [P[2], P[3]]] : corner === 'tl' ? [[P[4], P[0]], [P[0], P[1]], [P[3], P[4]]] : [[P[1], P[2]], [P[2], P[3]], [P[3], P[4]]];
    const gm = new THREE.MeshPhysicalMaterial({ color: 0xe6f1f2, transparent: true, opacity: 0.28, roughness: 0.03, metalness: 0.1 });
    for (const [p0, p1] of open) { const L = Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), a = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
      const gl = new THREE.Mesh(new THREE.BoxGeometry(L, m(2.0), m(0.01)), gm); gl.position.set((p0[0] + p1[0]) / 2, m(1.05), (p0[1] + p1[1]) / 2); gl.rotation.y = -a; ctx.scene.add(gl);
      const tr = new THREE.Mesh(new THREE.BoxGeometry(L, m(0.012), m(0.02)), M.chrome); tr.position.set((p0[0] + p1[0]) / 2, m(2.05), (p0[1] + p1[1]) / 2); tr.rotation.y = -a; ctx.scene.add(tr); }
    const head = corner === 'tr' ? [b[0] + W(b) * 0.15, b[3] - D(b) * 0.45] : corner === 'tl' ? [b[2] - W(b) * 0.15, b[3] - D(b) * 0.45] : [b[0] + W(b) * 0.35, b[1] + D(b) * 0.12];
    cyl(head[0], head[1], m(0.12), 2.1, 2.12, M.chrome, 48);
  };
  B.pouf = (it) => {                         // rectangular tufted boucle pouf on thin legs
    const b = it.box, fab = M.fabric(it.color || 0xe9e2d8, { boucle: true, ns: 0.9 });
    for (const [fx, fz] of [[0.1, 0.12], [0.9, 0.12], [0.1, 0.88], [0.9, 0.88]]) cyl(b[0] + W(b) * fx, b[1] + D(b) * fz, m(0.012), 0, 0.08, M.darkwood, 8);
    cushion(b, 0.08, 0.44, fab, 0.03, 0.06);
    const along = W(b) > D(b), n = Math.max(2, Math.round((along ? W(b) : D(b)) / m(0.25)));
    for (let k = 1; k < n; k++) { const t = k / n; cyl(along ? b[0] + W(b) * t : cx(b), along ? cz(b) : b[1] + D(b) * t, m(0.012), 0.44, 0.47, M.fabric(0xd6cdc0, { ns: 0.3 }), 16); }
  };
  B.basket = (it) => { const b = it.box, r = Math.min(W(b), D(b)) / 2;
    lathe(cx(b), cz(b), [[0.001, 0], [0.9, 0], [1, 0.9], [0.97, 0.92], [0.88, 0.9]].map(([a, y]) => [a * r / m(1), y * 0.35]), new THREE.MeshStandardMaterial({ map: M.oak.map, color: 0xd9b88f, roughness: 0.9 }), 48);
    cushion(inset(b, r * 0.25), 0.2, 0.33, M.fabric(0xe7e0d4, { linen: true }), 0.02, 0.03); };
  B.rug = (it) => { const b = it.box; box(b, 0.002, 0.015, M.fabric(it.color || 0xcfc6bb, { ns: 1 }), 0.01); };
  B.shaft = (it) => { box(it.box, 0, 2.7, M.wall); };

  for (const it of items) { const f = B[it.type]; if (f) f(it); else console.warn('no builder for', it.type); }
}
