// Procedural PBR materials (canvas textures): parquet, tiles, fabrics, woods, stone, ceramic, metals.
import * as THREE from 'three';

export function rnd(seed) { let s = seed % 2147483647; if (s <= 0) s += 2147483646; return () => (s = (s * 16807) % 2147483647) / 2147483647; }

function canvas(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); return c; }
function tex(c, srgb = true) { const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 16; return t; }

// height canvas -> normal map canvas
function normalFromHeight(hc, strength) {
  const w = hc.width, h = hc.height, src = hc.getContext('2d').getImageData(0, 0, w, h).data;
  return canvas(w, h, (ctx) => {
    const img = ctx.createImageData(w, h), d = img.data, at = (x, y) => src[(((y + h) % h) * w + ((x + w) % w)) * 4] / 255;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const dx = (at(x + 1, y) - at(x - 1, y)) * strength, dy = (at(x, y + 1) - at(x, y - 1)) * strength;
      const l = Math.hypot(dx, dy, 1), i = (y * w + x) * 4;
      d[i] = (-dx / l * .5 + .5) * 255; d[i + 1] = (dy / l * .5 + .5) * 255; d[i + 2] = (1 / l * .5 + .5) * 255; d[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
  });
}

// ---------------- parquet: planks along the texture's v axis ----------------
export function parquet(opts = {}) {
  const { planks = 8, size = 2048, tone = [222, 196, 176], seed = 7, lengthVar = true } = opts;
  const r = rnd(seed), pw = size / planks;
  const col = canvas(size, size, () => {}), hgt = canvas(size, size, () => {});
  const c = col.getContext('2d'), h = hgt.getContext('2d');
  h.fillStyle = '#808080'; h.fillRect(0, 0, size, size);
  for (let i = 0; i < planks; i++) {
    const x = i * pw; let y = -r() * size;
    while (y < size) {
      const L = size * (lengthVar ? 0.45 + r() * 0.5 : 0.6);
      const k = 0.975 + r() * 0.05, hue = (r() - 0.5) * 4;
      const base = [tone[0] * k + hue, tone[1] * k, tone[2] * k - hue * 0.5];
      const g = c.createLinearGradient(x, 0, x + pw, 0);
      g.addColorStop(0, `rgb(${base.map(v => v | 0)})`); g.addColorStop(1, `rgb(${base.map(v => (v * 0.96) | 0)})`);
      c.fillStyle = g; c.fillRect(x, y, pw, L);
      // grain: long wavy streaks + a few knots
      for (let s = 0; s < 140; s++) {
        const a = 0.05 + r() * 0.12, dark = r() < 0.78;
        c.strokeStyle = dark ? `rgba(110,72,50,${a})` : `rgba(255,240,225,${a * 0.8})`;
        c.lineWidth = 0.5 + r() * 1.6; const gx = x + r() * pw, amp = 0.5 + r() * 2;
        c.beginPath(); c.moveTo(gx, y);
        for (let t = 0; t <= 1.001; t += 0.1) c.lineTo(gx + Math.sin(t * 6 + s) * amp, y + t * L);
        c.stroke();
      }
      if (r() < 0.25) { const kx = x + pw * (0.3 + r() * 0.4), ky = y + L * r(); const rg = c.createRadialGradient(kx, ky, 0, kx, ky, 10); rg.addColorStop(0, 'rgba(95,60,40,0.35)'); rg.addColorStop(1, 'rgba(95,60,40,0)'); c.fillStyle = rg; c.beginPath(); c.ellipse(kx, ky, 6, 16, 0, 0, 7); c.fill(); }
      // seams (colour + height groove)
      c.fillStyle = 'rgba(70,45,32,0.55)'; c.fillRect(x, y, 1.5, L); c.fillRect(x, y, pw, 1.5);
      h.fillStyle = '#303030'; h.fillRect(x, y, 2, L); h.fillRect(x, y, pw, 2);
      y += L;
    }
  }
  return { map: tex(col), normalMap: tex(normalFromHeight(hgt, 2.5), false) };
}

export function tiles(opts = {}) {
  const { n = 4, size = 1024, color = [226, 206, 190], seed = 11 } = opts;
  const r = rnd(seed), ts = size / n;
  const col = canvas(size, size, (c) => {
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const k = 0.96 + r() * 0.06; c.fillStyle = `rgb(${color.map(v => (v * k) | 0)})`; c.fillRect(i * ts, j * ts, ts, ts);
      for (let s = 0; s < 400; s++) { c.fillStyle = `rgba(${r() < .5 ? '255,255,255' : '150,120,100'},${r() * 0.05})`; const q = r() * 30; c.fillRect(i * ts + r() * ts, j * ts + r() * ts, q, q * 0.6); }
    }
    c.strokeStyle = 'rgba(150,130,115,0.8)'; c.lineWidth = 3;
    for (let i = 0; i <= n; i++) { c.beginPath(); c.moveTo(i * ts, 0); c.lineTo(i * ts, size); c.stroke(); c.beginPath(); c.moveTo(0, i * ts); c.lineTo(size, i * ts); c.stroke(); }
  });
  const hgt = canvas(size, size, (c) => { c.fillStyle = '#909090'; c.fillRect(0, 0, size, size); c.strokeStyle = '#303030'; c.lineWidth = 4; for (let i = 0; i <= n; i++) { c.beginPath(); c.moveTo(i * ts, 0); c.lineTo(i * ts, size); c.stroke(); c.beginPath(); c.moveTo(0, i * ts); c.lineTo(size, i * ts); c.stroke(); } });
  return { map: tex(col), normalMap: tex(normalFromHeight(hgt, 2), false) };
}

function noiseCanvas(size, base, amp, seed, blobs = 9000, blobSize = 2) {
  const r = rnd(seed);
  return canvas(size, size, (c) => { c.fillStyle = `rgb(${base})`; c.fillRect(0, 0, size, size);
    for (let i = 0; i < blobs; i++) { c.fillStyle = `rgba(${r() < .5 ? '255,255,255' : '0,0,0'},${r() * amp})`; c.fillRect(r() * size, r() * size, blobSize, blobSize); } });
}

// bouclé: dense little loops -> strong bump
export function boucleNormal(seed = 3) {
  const r = rnd(seed);
  const hc = canvas(256, 256, (c) => { c.fillStyle = '#707070'; c.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 2600; i++) { const x = r() * 256, y = r() * 256, rad = 1.5 + r() * 2.5; const g = c.createRadialGradient(x, y, 0, x, y, rad); g.addColorStop(0, 'rgba(255,255,255,0.9)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(x - rad, y - rad, rad * 2, rad * 2); } });
  return tex(normalFromHeight(hc, 3), false);
}
export function weaveNormal(seed = 5, step = 3) {
  const hc = canvas(256, 256, (c) => { const im = c.createImageData(256, 256); const r = rnd(seed);
    for (let i = 0; i < 256 * 256; i++) { const x = i % 256, y = (i / 256) | 0; const v = 128 + 50 * Math.sin(x * Math.PI / step) * Math.sin(y * Math.PI / step) + (r() - .5) * 40; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; }
    c.putImageData(im, 0, 0); });
  return tex(normalFromHeight(hc, 1.5), false);
}

export function woodGrain(base = [120, 82, 60], seed = 5, size = 512, stripes = 220) {
  const r = rnd(seed);
  return tex(canvas(size, size, (c) => { c.fillStyle = `rgb(${base})`; c.fillRect(0, 0, size, size);
    for (let i = 0; i < stripes; i++) { const y = r() * size; c.strokeStyle = `rgba(${r() < .6 ? '40,20,10' : '255,235,215'},${r() * 0.12})`; c.lineWidth = 0.5 + r() * 2; c.beginPath(); c.moveTo(0, y); for (let x = 0; x <= size; x += 32) c.lineTo(x, y + Math.sin(x * 0.012 + i) * 3); c.stroke(); } }));
}

export function makeMaterials(S) {
  const pq = parquet(S.parquet || {});
  const tl = tiles(S.tiles || {});
  const bn = boucleNormal(), wv = weaveNormal(), lin = weaveNormal(9, 2);
  const fabric = (color, o = {}) => new THREE.MeshPhysicalMaterial({ color, roughness: o.rough ?? 0.95, normalMap: o.boucle ? bn : o.linen ? lin : wv,
    normalScale: new THREE.Vector2(o.ns ?? 0.7, o.ns ?? 0.7), sheen: 1, sheenRoughness: 0.6, sheenColor: new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.4) });
  const walnutT = woodGrain([128, 90, 70], 5), oakT = woodGrain([196, 160, 132], 8), darkT = woodGrain([88, 60, 46], 12);
  const M = {
    parquet: new THREE.MeshStandardMaterial({ map: pq.map, normalMap: pq.normalMap, normalScale: new THREE.Vector2(0.6, 0.6), roughness: 0.62 }),
    tiles: new THREE.MeshStandardMaterial({ map: tl.map, normalMap: tl.normalMap, normalScale: new THREE.Vector2(0.5, 0.5), roughness: 0.35 }),
    wall: new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 1 }),
    wallCap: new THREE.MeshBasicMaterial({ color: 0x000000 }),
    walnut: new THREE.MeshStandardMaterial({ map: walnutT, roughness: 0.55 }),
    darkwood: new THREE.MeshStandardMaterial({ map: darkT, roughness: 0.5 }),
    oak: new THREE.MeshStandardMaterial({ map: oakT, roughness: 0.55 }),
    counterTop: new THREE.MeshStandardMaterial({ map: woodGrain([176, 142, 120], 21), roughness: 0.45 }),
    white: new THREE.MeshPhysicalMaterial({ color: 0xf3f1ed, roughness: 0.4, clearcoat: 0.2 }),
    ceramic: new THREE.MeshPhysicalMaterial({ color: 0xf7f6f3, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.08 }),
    chrome: new THREE.MeshStandardMaterial({ color: 0xcfcfcf, metalness: 1, roughness: 0.25 }),
    steel: new THREE.MeshStandardMaterial({ color: 0x9d9c98, metalness: 0.55, roughness: 0.38 }),
    black: new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.35 }),
    blackGlass: new THREE.MeshPhysicalMaterial({ color: 0x1a1a1b, roughness: 0.3, clearcoat: 0.25, clearcoatRoughness: 0.3, metalness: 0.0 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xeaf3f5, transmission: 0.7, transparent: true, opacity: 0.45, roughness: 0.05 }),
    frame: new THREE.MeshStandardMaterial({ color: 0xece9e4, roughness: 0.4 }),
    stone: new THREE.MeshStandardMaterial({ color: 0xd9d2c9, roughness: 0.3 }),
    shade: new THREE.MeshStandardMaterial({ color: 0xefdcc4, emissive: 0xffc98a, emissiveIntensity: 1.6, roughness: 1, transparent: true, opacity: 0.92 }),
    bulb: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff1d6, emissiveIntensity: 8 }),
    led: new THREE.MeshStandardMaterial({ color: 0xffe9cc, emissive: 0xffc98f, emissiveIntensity: 1.2 }),
    cabGlass: new THREE.MeshPhysicalMaterial({ color: 0xeef3f2, transparent: true, opacity: 0.14, roughness: 0.05 }),
    plantPot: new THREE.MeshStandardMaterial({ color: 0x3a3a38, roughness: 0.6 }),
    fabric, linenN: lin,
  };
  M.parquetRep = S.parquetRepPx || 520; M.tilesRep = S.tilesRepPx || 240;
  return M;
}
