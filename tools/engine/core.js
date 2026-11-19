// Core of the floor-plan render engine: renderer, orthographic top-down camera, lighting rig, post-processing.
// World units = plan pixels. Heights are given in metres and converted with S.pxm (plan px per metre).
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export function createCore(S, OUT_W) {
  const [PW, PH] = S.size;
  const OUT_H = Math.round(OUT_W * PH / PW);
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(OUT_W, OUT_H);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = S.exposure || 1.0;
  document.body.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  renderer.setClearColor(0xffffff, 1);
  // image-based lighting: neutral room environment gives soft fill + reflections on glossy materials
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  // orthographic camera looking straight down: plan x -> screen x, plan y -> screen y
  const cam = new THREE.OrthographicCamera(0, PW, 0, -PH, 1, 20000);
  cam.position.set(0, 5000, 0);
  cam.rotation.set(-Math.PI / 2, 0, 0);
  cam.updateProjectionMatrix();

  const m = v => v * S.pxm;             // metres -> plan px
  return { THREE, renderer, scene, cam, PW, PH, OUT_W, OUT_H, m, S };
}

export function addLights(core, S) {
  const { THREE, scene, PW, PH, m } = core;
  // sky fill (warm top, darker bounce from the floor)
  scene.add(new THREE.HemisphereLight(0xfff6ee, 0x7a6a60, S.hemi ?? 0.55));
  // main key: soft evening daylight coming in from the windows (top-left of the plan), long soft shadows
  const key = new THREE.DirectionalLight(0xfff1e4, S.key ?? 1.6);
  const dir = S.keyDir || [-0.45, 1.0, -0.6];                      // x, up, z (plan down = +z)
  key.position.set(PW / 2 + dir[0] * m(20), m(20) * dir[1], PH / 2 + dir[2] * m(20));
  key.target.position.set(PW / 2, 0, PH / 2); scene.add(key.target);
  key.castShadow = true;
  key.shadow.mapSize.set(4096, 4096);
  const R = Math.max(PW, PH);
  Object.assign(key.shadow.camera, { left: -R, right: R, top: R, bottom: -R, near: 1, far: m(60) });
  key.shadow.radius = S.shadowSoft ?? 14; key.shadow.blurSamples = 24;
  key.shadow.bias = -0.0004; key.shadow.normalBias = 0.8;
  scene.add(key);
  return key;
}

// warm practical light (table/floor lamp): small point light with soft shadows
export function lampLight(core, x, z, hM, power = 1, rangeM = 5) {
  const { THREE, scene, m } = core;
  const l = new THREE.PointLight(0xffc98f, power * (core.S?.lampScale ?? 1) * m(1) * m(1) * 0.35, m(rangeM), 2);
  l.position.set(x, m(hM), z);
  l.castShadow = true; l.shadow.mapSize.set(1024, 1024); l.shadow.radius = 10; l.shadow.bias = -0.002;
  scene.add(l);
  return l;
}

const GradeShader = {
  uniforms: { tDiffuse: { value: null }, vignette: { value: 0.28 }, warmth: { value: 0.03 }, contrast: { value: 1.06 }, sat: { value: 0.92 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `uniform sampler2D tDiffuse; uniform float vignette, warmth, contrast, sat; varying vec2 vUv;
    void main(){ vec4 c = texture2D(tDiffuse, vUv); vec3 col = c.rgb;
      float l = dot(col, vec3(0.299,0.587,0.114)); col = mix(vec3(l), col, sat);
      col = (col - 0.5) * contrast + 0.5; col += vec3(warmth, warmth*0.4, -warmth*0.6);
      vec2 d = vUv - 0.5; float v = 1.0 - vignette * dot(d, d) * 2.2; col *= v;
      gl_FragColor = vec4(clamp(col,0.0,1.0), c.a); }`,
};

export function renderFinal(core, S) {
  const { THREE, renderer, scene, cam, OUT_W, OUT_H } = core;
  // r160 has no scene.environmentIntensity: scale image-based light per material
  const ei = S.envIntensity ?? 0.35;
  scene.traverse(o => { if (o.isMesh) for (const mt of [].concat(o.material)) if ('envMapIntensity' in mt) mt.envMapIntensity = ei; });
  const composer = new EffectComposer(renderer);
  composer.setSize(OUT_W, OUT_H);
  composer.addPass(new RenderPass(scene, cam));
  const ao = new GTAOPass(scene, cam, OUT_W, OUT_H);
  ao.updateGtaoMaterial({ radius: core.m(S.aoRadiusM ?? 0.45), distanceExponent: 1.3, thickness: core.m(0.25), scale: 1.4, samples: 24 });
  ao.blendIntensity = S.aoIntensity ?? 1.0;
  composer.addPass(ao);
  if (S.bloom !== 0) composer.addPass(new UnrealBloomPass(new THREE.Vector2(OUT_W, OUT_H), S.bloom ?? 0.45, 0.35, S.bloomThreshold ?? 5.0));
  composer.addPass(new OutputPass());
  const grade = new ShaderPass(GradeShader);
  grade.uniforms.vignette.value = 0.0;          // vignette is applied later inside the apartment only
  composer.addPass(grade);
  composer.render();
}
