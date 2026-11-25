// LOKADIGITAL Signature Character — 2.5D rig (three.js, ES module).
// The approved likeness is a single front-facing stylised 3D render (assets/LD_character_master_1024.png).
// This rig deforms it on a dense mesh with Gaussian-weighted control points (brows, lids, irises, mouth, cheeks,
// face/hair yaw) and adds blink lids, eye direction, head tilt/bob, breathing and LokaDigital rim lighting.
//
//   const ch = await createCharacter(THREE, { texUrl, landmarks, height })
//   ch.set({ expr:{smile:1}, yaw:0.2, tilt:-0.05, blink:0, eyeX:0, eyeY:0, breathe:t, rimY:0.8, rimP:0.9 })
//   scene.add(ch.object)

export const EXPRESSIONS = {
  // displacement (px in 1024 texture space) per control point. 'skeptical' = the source likeness (zero).
  skeptical: {},
  neutral:   { browL_in:[0,-26], browL_mid:[0,-16], browL_out:[0,-6], browR_in:[0,22], browR_mid:[0,20], browR_out:[0,10], mouthL:[-2,-12], mouthR:[2,-12], lipU:[0,4], lipL:[0,-6] },
  smile:     { browL_in:[0,-28], browL_mid:[0,-20], browL_out:[0,-8], browR_in:[0,20], browR_mid:[0,16], browR_out:[0,8],
               mouthL:[-20,-34], mouthR:[20,-34], lipU:[0,6], lipL:[0,-14], cheekL:[-4,-18], cheekR:[4,-18], lidL_lo:[0,-10], lidR_lo:[0,-10], chin:[0,-4] },
  smirk:     { browL_in:[0,-16], browL_mid:[0,-10], browR_in:[0,8], browR_mid:[0,-4], mouthR:[18,-30], mouthL:[0,-6], lipU:[0,3], cheekR:[2,-14], lidR_lo:[0,-7] },
  surprised: { browL_in:[0,-46], browL_mid:[0,-36], browL_out:[0,-22], browR_in:[0,-14], browR_mid:[0,-16], browR_out:[0,-10],
               lidL_up:[0,-8], lidR_up:[0,-8], lidL_lo:[0,5], lidR_lo:[0,5], mouthL:[8,6], mouthR:[-8,6], lipL:[0,6], chin:[0,8] },
  thinking:  { browL_in:[0,-14], browL_mid:[0,-10], browR_in:[0,-6], browR_mid:[0,-12], mouthL:[4,2], mouthR:[-8,0], irisL:[12,-9], irisR:[12,-9] },
  focused:   { browL_in:[4,8], browL_mid:[0,2], browR_in:[-6,30], browR_mid:[0,26], browR_out:[0,12], lidL_up:[0,8], lidR_up:[0,10], lidL_lo:[0,-4], lidR_lo:[0,-4], mouthL:[0,2], mouthR:[0,2] },
  worried:   { browL_in:[0,-30], browL_out:[0,10], browR_in:[0,-6], browR_mid:[0,10], browR_out:[0,18], mouthL:[0,8], mouthR:[0,8] },
};

const VERT = `
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
const FRAG = `
uniform sampler2D map; uniform float blink; uniform vec2 eyeL; uniform vec2 eyeR; uniform vec2 eyeRL; uniform vec2 eyeRR;
uniform vec3 skin; uniform float rimY; uniform float rimP; uniform float opacity; uniform float exposure; uniform vec3 tint;
varying vec2 vUv;
float lid(vec2 uv, vec2 c, vec2 r){                  // 0..1 coverage of the closing upper lid inside one eye ellipse
  vec2 d = (uv - c) / (r * 1.08); float rr = dot(d,d); if (rr > 1.0) return 0.0;
  float feather = smoothstep(1.0, 0.82, rr);           // soft lid boundary
  float top = sqrt(max(0.0, 1.0 - d.x*d.x));           // uv y grows upward: lid starts at +top
  float edge = mix(top, -top * 0.85, blink);           // lid edge travels down with blink
  return smoothstep(edge - 0.05, edge + 0.03, d.y) * feather;
}
void main(){
  vec4 c = texture2D(map, vUv);
  if (c.a < 0.01) discard;
  vec3 col = c.rgb;  // raw sRGB
  // blink lids (skin + lash line), in texture space so they follow the deformation
  if (blink > 0.001){
    float lL = lid(vUv, eyeL, eyeRL), lR = lid(vUv, eyeR, eyeRR); float l = max(lL, lR);
    vec2 e = lL > lR ? eyeL : eyeR; vec2 er = lL > lR ? eyeRL : eyeRR;
    // lid = the real skin texture just above the eye, pulled down; shaded darker toward the lash line
    vec3 lidc = texture2D(map, vec2(e.x + (vUv.x - e.x) * 0.6, e.y - er.y * 1.9)).rgb;   // skin just below the eye
    lidc *= 0.80 + 0.20 * smoothstep(-er.y, er.y, vUv.y - e.y);                          // crease shadow toward the top
    col = mix(col, lidc, l);
    float lash = max(lid(vUv, eyeL, eyeRL) - lid(vUv - vec2(0.0,0.006), eyeL, eyeRL), lid(vUv, eyeR, eyeRR) - lid(vUv - vec2(0.0,0.006), eyeR, eyeRR));
    col = mix(col, vec3(0.12,0.07,0.07), clamp(lash*1.6,0.0,1.0) * step(0.6, blink));
  }
  // grade: lift shadows toward LokaDigital purple, keep skin warm
  float lum = dot(col, vec3(0.299,0.587,0.114));
  col = mix(col, col * vec3(0.90,0.84,1.08) + vec3(0.02,0.0,0.05), (1.0 - smoothstep(0.12,0.5,lum)) * 0.45);
  col *= exposure; col *= tint;
  // rim lights: purple from the left, electric yellow (the Signal Line) from the right
  float o = 0.006;
  float rimR = clamp(c.a - texture2D(map, vUv + vec2(o, 0.0)).a, 0.0, 1.0) + 0.6*clamp(c.a - texture2D(map, vUv + vec2(2.0*o, 0.0)).a, 0.0, 1.0);
  float rimL = clamp(c.a - texture2D(map, vUv - vec2(o, 0.0)).a, 0.0, 1.0) + 0.6*clamp(c.a - texture2D(map, vUv - vec2(2.0*o, 0.0)).a, 0.0, 1.0);
  float rimT = clamp(c.a - texture2D(map, vUv + vec2(0.0, o)).a, 0.0, 1.0);
  col += vec3(0.91,1.0,0.17) * rimR * rimY * 0.85;
  col += vec3(0.56,0.42,1.0) * (rimL * 0.9 + rimT * 0.5) * rimP;
  gl_FragColor = vec4(col, c.a * opacity);
}`;

export async function createCharacter(THREE, opt) {
  const lm = opt.landmarks; const S = lm.size; const SEG = opt.seg || 160;
  const tex = await new THREE.TextureLoader().loadAsync(opt.texUrl);
  tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 4;   // raw sRGB in, raw sRGB out (ShaderMaterial does no conversion)
  const h = opt.height || 1; const geo = new THREE.PlaneGeometry(h, h, SEG, SEG);
  const pos = geo.attributes.position; const base = Float32Array.from(pos.array);
  const names = Object.keys(lm.points); const nP = names.length, nV = pos.count;
  // per-vertex Gaussian weights for each control point
  const W = new Float32Array(nV * nP);
  for (let v = 0; v < nV; v++) {
    const px = (base[v*3] / h + 0.5) * S, py = (0.5 - base[v*3+1] / h) * S;
    for (let k = 0; k < nP; k++) { const [x, y, r] = lm.points[names[k]]; const d2 = (px-x)*(px-x) + (py-y)*(py-y); W[v*nP+k] = Math.exp(-d2 / (2*r*r)); }
  }
  const ex = lm.eyes, uvE = e => new THREE.Vector2(e.c[0]/S, 1 - e.c[1]/S), rE = e => new THREE.Vector2(e.rx/S, e.ry/S);
  const mat = new THREE.ShaderMaterial({ vertexShader: VERT, fragmentShader: FRAG, transparent: true, depthWrite: false,
    uniforms: { map: { value: tex }, blink: { value: 0 }, eyeL: { value: uvE(ex.L) }, eyeR: { value: uvE(ex.R) }, eyeRL: { value: rE(ex.L) }, eyeRR: { value: rE(ex.R) },
      skin: { value: new THREE.Vector3(...lm.skin_rgb.map(v => v/255)) }, rimY: { value: 0.8 }, rimP: { value: 0.9 }, opacity: { value: 1 }, exposure: { value: 1 }, tint: { value: new THREE.Vector3(1,1,1) } } });
  const mesh = new THREE.Mesh(geo, mat);
  const pivot = new THREE.Group(); pivot.add(mesh); mesh.position.y = h * 0.5 - h * 0.86;   // pivot at the neck (y≈0.86 of the image)
  const root = new THREE.Group(); root.add(pivot); root.position.y = h * 0.86 - h * 0.5;
  const D = new Float32Array(nP * 2);
  function set(p = {}) {
    D.fill(0);
    const ex_ = p.expr || {};
    for (const [name, w] of Object.entries(ex_)) { const e = EXPRESSIONS[name]; if (!e || !w) continue;
      for (const [pt, [dx, dy]] of Object.entries(e)) { const k = names.indexOf(pt); if (k >= 0) { D[k*2] += dx * w; D[k*2+1] += dy * w; } } }
    const add = (pt, dx, dy) => { const k = names.indexOf(pt); if (k >= 0) { D[k*2] += dx; D[k*2+1] += dy; } };
    const yaw = p.yaw || 0, ey = p.eyeX || 0, eyy = p.eyeY || 0;
    add('face', yaw * 30, 0); add('nose', yaw * 18, 0); add('mouthL', yaw * 10, 0); add('mouthR', yaw * 10, 0); add('hair', yaw * 12, 0);
    add('irisL', yaw * 8 + ey * 14, eyy * 10); add('irisR', yaw * 8 + ey * 14, eyy * 10);
    const arr = pos.array, sc = h / S;
    for (let v = 0; v < nV; v++) { let dx = 0, dy = 0; const o = v * nP;
      for (let k = 0; k < nP; k++) { const w = W[o+k]; if (w > 0.002) { dx += D[k*2] * w; dy += D[k*2+1] * w; } }
      arr[v*3] = base[v*3] + dx * sc; arr[v*3+1] = base[v*3+1] - dy * sc; }
    pos.needsUpdate = true;
    pivot.rotation.z = p.tilt || 0;
    const b = p.breathe || 0; pivot.scale.set(1 + 0.004 * Math.sin(b * 1.7), 1 + 0.007 * Math.sin(b * 1.7), 1);
    mat.uniforms.blink.value = p.blink || 0;
    if (p.rimY != null) mat.uniforms.rimY.value = p.rimY; if (p.rimP != null) mat.uniforms.rimP.value = p.rimP;
    if (p.opacity != null) mat.uniforms.opacity.value = p.opacity; if (p.exposure != null) mat.uniforms.exposure.value = p.exposure;
  }
  set({});
  return { object: root, set, material: mat };
}
