'use strict';
/* LOKADIGITAL — EP01 "SIGNAL / NOISE"
   Deterministic canvas renderer. renderFrame(t) draws the frame at time t (seconds).
   Stateless per frame, so frames can be rendered in any order / in parallel. */

const W = 1080, H = 1920, FPS = 30, DUR = 59.0;
const cv = document.getElementById('c');
let ctx = cv.getContext('2d');

// ─── Brand palette ────────────────────────────────────────────────
const C = {
  ink: '#05030a', deep: '#10082a', plum: '#1c0e40', purple: '#4b1fa0', violet: '#7b3cf0',
  lav: '#ab94ff', mist: '#d4caf2', white: '#f6f3fc', grey: '#7c7396', dim: '#3a3152', y: '#e8ff2b'
};
const YR = '232,255,43';           // electric yellow rgb
const FD = '"Inter Display"', FT = '"Inter"';

// ─── Math / easing ────────────────────────────────────────────────
const clamp = (x, a = 0, b = 1) => x < a ? a : x > b ? b : x;
const lerp = (a, b, t) => a + (b - a) * t;
const P = (t, a, b) => clamp((t - a) / (b - a));
const E = {
  o2: x => 1 - (1 - x) * (1 - x),
  o3: x => 1 - Math.pow(1 - x, 3),
  o4: x => 1 - Math.pow(1 - x, 4),
  o5: x => 1 - Math.pow(1 - x, 5),
  ox: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
  i2: x => x * x,
  i3: x => x * x * x,
  io3: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
  iox: x => x <= 0 ? 0 : x >= 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2,
  back: x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); }
};
function mulberry(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function h3(a, b = 0, c = 0) { const s = Math.sin(a * 127.1 + b * 311.7 + c * 74.7) * 43758.5453; return s - Math.floor(s); }
function gauss(r) { return Math.sqrt(-2 * Math.log(r() + 1e-9)) * Math.cos(6.2832 * r()); }
const rgba = (rgb, a) => `rgba(${rgb},${a})`;
function mixHex(a, b, t) {
  const pa = [1, 3, 5].map(i => parseInt(a.substr(i, 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.substr(i, 2), 16));
  return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], t))).join(',')})`;
}

// ─── Typography helpers ───────────────────────────────────────────
function setFont(o) { ctx.font = `${o.w || 700} ${o.size}px ${o.f || FD}`; ctx.letterSpacing = ((o.track || 0) * o.size) + 'px'; }
function measure(s, o) { ctx.save(); setFont(o); const m = ctx.measureText(s).width - (o.track || 0) * o.size; ctx.restore(); return m; }
function fitSize(lines, maxW, o, maxSize) {
  let s = maxSize; for (const l of lines) { const m = measure(l, { ...o, size: 100 }); s = Math.min(s, maxW * 100 / m); } return Math.floor(s);
}
function txt(s, x, y, o) {
  ctx.save(); ctx.globalAlpha *= (o.a == null ? 1 : o.a); setFont(o);
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  const wdt = measure(s, o);
  let xx = x; if (o.align === 'center') xx = x - wdt / 2; else if (o.align === 'right') xx = x - wdt;
  if (o.glow) { ctx.shadowColor = o.glowCol || rgba(YR, .55); ctx.shadowBlur = o.glow; }
  if (o.stroke) { ctx.strokeStyle = o.c || C.white; ctx.lineWidth = o.stroke; ctx.lineJoin = 'round'; ctx.strokeText(s, xx, y); }
  else { ctx.fillStyle = o.c || C.white; ctx.fillText(s, xx, y); }
  ctx.restore(); return wdt;
}
// Rich line: segs = [[text, color, extra opts], ...]
function rich(segs, x, y, o) {
  const widths = segs.map(s => measure(s[0], { ...o, ...(s[2] || {}) }));
  const sp = (o.track || 0) * o.size;
  const total = widths.reduce((a, b) => a + b, 0) + sp * (segs.length - 1);
  let xx = o.align === 'center' ? x - total / 2 : o.align === 'right' ? x - total : x;
  segs.forEach((s, i) => { txt(s[0], xx, y, { ...o, ...(s[2] || {}), c: s[1], align: 'left' }); xx += widths[i] + sp; });
  return total;
}
// Masked line reveal (text rises from under a hard edge), with optional exit
function rev(content, x, y, o, pin, pout = 0) {
  if (pin <= 0 || pout >= 1) return;
  const size = o.size;
  const off = (1 - E.ox(pin)) * size * 1.15 - E.iox(pout) * size * 1.2;
  ctx.save(); ctx.beginPath(); ctx.rect(-200, y - size * 1.02, W + 400, size * 1.36); ctx.clip();
  if (Array.isArray(content)) rich(content, x, y + off, o); else txt(content, x, y + off, o);
  ctx.restore();
}
// Per-letter staggered reveal
function revLetters(s, x, y, o, lt, { st = .03, dur = .55, align = 'left', pout = 0 } = {}) {
  if (lt <= 0 || pout >= 1) return;
  ctx.save(); setFont(o);
  const total = ctx.measureText(s).width - (o.track || 0) * o.size;
  const x0 = align === 'center' ? x - total / 2 : x;
  ctx.beginPath(); ctx.rect(-50, y - o.size * 1.0, W + 100, o.size * 1.3); ctx.clip();
  ctx.fillStyle = o.c || C.white; ctx.textAlign = 'left';
  if (o.glow) { ctx.shadowColor = o.glowCol || rgba(YR, .5); ctx.shadowBlur = o.glow; }
  for (let i = 0; i < s.length; i++) {
    const pre = ctx.measureText(s.slice(0, i)).width;
    const p = E.ox(P(lt, i * st, i * st + dur));
    const q = E.iox(clamp(pout * 1.6 - i * 0.04));
    ctx.fillText(s[i], x0 + pre, y + (1 - p) * o.size * 1.1 - q * o.size * 1.2);
  }
  ctx.restore();
}
function label(s, x, y, o = {}) { return txt(s, x, y, { size: 26, w: 600, f: FT, track: .28, c: C.lav, ...o }); }

// ─── Shapes ───────────────────────────────────────────────────────
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function pill(cx, cy, text, { dot = C.lav, sc = 1, a = 1, size = 30, yellow = false } = {}) {
  if (a <= 0 || sc <= 0) return;
  ctx.save(); ctx.globalAlpha *= a; ctx.translate(cx, cy); ctx.scale(sc, sc);
  const o = { size, w: 500, f: FT, track: 0 };
  const tw = measure(text, o), w = tw + 92, h = size * 2.1;
  rr(-w / 2, -h / 2, w, h, h / 2);
  ctx.fillStyle = yellow ? 'rgba(30,30,8,.92)' : 'rgba(20,11,40,.93)'; ctx.fill();
  ctx.strokeStyle = yellow ? rgba(YR, .55) : 'rgba(255,255,255,.13)'; ctx.lineWidth = 1.5; ctx.stroke();
  ctx.beginPath(); ctx.arc(-w / 2 + 32, 0, 7, 0, 6.283); ctx.fillStyle = dot; ctx.fill();
  txt(text, -w / 2 + 54, size * .36, { ...o, c: yellow ? C.y : C.white });
  ctx.restore();
}
function heart(x, y, s, col) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.beginPath();
  ctx.moveTo(0, 6); ctx.bezierCurveTo(-14, -4, -8, -16, 0, -8); ctx.bezierCurveTo(8, -16, 14, -4, 0, 6);
  ctx.strokeStyle = col; ctx.lineWidth = 2.2 / s; ctx.stroke(); ctx.restore();
}

// ─── Pre-rendered assets ──────────────────────────────────────────
const CARD_W = 420, CARD_H = 640;
const HEADLINES = ['5 TIPS', 'POV:', 'NEW', 'SALE', 'TREND', 'WAIT', '#FYP', 'HOW TO', 'DAY 212', 'PROMO', 'VLOG', 'MENU', 'ASMR', 'OOTD', 'COLLAB', 'GRWM'];
const cards = [];
function makeCard(seed) {
  const c = document.createElement('canvas'); c.width = CARD_W; c.height = CARD_H; const g = c.getContext('2d');
  const r = mulberry(seed * 7919 + 13);
  g.beginPath(); g.roundRect(0, 0, CARD_W, CARD_H, 28);
  const bgG = g.createLinearGradient(0, 0, 0, CARD_H); bgG.addColorStop(0, '#170d2e'); bgG.addColorStop(1, '#0c0719');
  g.fillStyle = bgG; g.fill(); g.strokeStyle = 'rgba(255,255,255,.09)'; g.lineWidth = 2; g.stroke();
  // header
  const av = g.createLinearGradient(26, 30, 62, 66); av.addColorStop(0, '#8b5cf6'); av.addColorStop(1, '#3b1a80');
  g.beginPath(); g.arc(44, 48, 18, 0, 6.283); g.fillStyle = av; g.fill();
  g.fillStyle = 'rgba(255,255,255,.55)'; g.beginPath(); g.roundRect(74, 37, 110 + r() * 60, 10, 5); g.fill();
  g.fillStyle = 'rgba(255,255,255,.18)'; g.beginPath(); g.roundRect(74, 55, 60 + r() * 40, 8, 4); g.fill();
  // media
  const mx = 16, my = 88, mw = CARD_W - 32, mh = 410;
  g.save(); g.beginPath(); g.roundRect(mx, my, mw, mh, 18); g.clip();
  const hue = r();
  const mg = g.createLinearGradient(mx, my, mx + mw, my + mh);
  mg.addColorStop(0, hue < .5 ? '#2a1166' : '#1d0b45'); mg.addColorStop(1, hue < .5 ? '#0d0620' : '#3a1784');
  g.fillStyle = mg; g.fillRect(mx, my, mw, mh);
  const kind = Math.floor(r() * 4);
  if (kind === 0) { // soft orb
    const ox = mx + mw * (.3 + r() * .4), oy = my + mh * (.35 + r() * .3), orr = 120 + r() * 90;
    const og = g.createRadialGradient(ox, oy, 0, ox, oy, orr); og.addColorStop(0, 'rgba(171,148,255,.85)'); og.addColorStop(1, 'rgba(171,148,255,0)');
    g.fillStyle = og; g.fillRect(mx, my, mw, mh);
  } else if (kind === 1) { // diagonal bands
    g.globalAlpha = .35; for (let i = 0; i < 5; i++) { g.fillStyle = i % 2 ? '#7b3cf0' : '#2e1470'; g.beginPath(); const o = i * 90 - 80; g.moveTo(mx + o, my + mh); g.lineTo(mx + o + 60, my + mh); g.lineTo(mx + o + 260, my); g.lineTo(mx + o + 200, my); g.fill(); } g.globalAlpha = 1;
  } else if (kind === 2) { // product plinth
    g.fillStyle = 'rgba(255,255,255,.08)'; g.beginPath(); g.ellipse(mx + mw / 2, my + mh * .78, 130, 26, 0, 0, 6.283); g.fill();
    const pg = g.createLinearGradient(0, my + 120, 0, my + 320); pg.addColorStop(0, '#c4b2ff'); pg.addColorStop(1, '#5b2bc0');
    g.fillStyle = pg; g.beginPath(); g.roundRect(mx + mw / 2 - 60, my + 120, 120, 200, 22); g.fill();
  } else { // grid of thumbs
    for (let i = 0; i < 9; i++) { g.fillStyle = `rgba(171,148,255,${.08 + r() * .25})`; g.beginPath(); g.roundRect(mx + 14 + (i % 3) * 120, my + 40 + Math.floor(i / 3) * 120, 106, 106, 10); g.fill(); }
  }
  const acc = r() < .22;
  if (acc) { g.fillStyle = C.y; g.beginPath(); g.roundRect(mx + 22, my + mh - 70, 120, 40, 20); g.fill(); }
  g.font = `900 ${66}px ${FD}`; g.letterSpacing = '-2px'; g.fillStyle = 'rgba(255,255,255,.92)';
  g.fillText(HEADLINES[seed % HEADLINES.length], mx + 24, my + 90);
  g.restore();
  // footer
  heart(36, 534, 1.3, 'rgba(255,255,255,.75)');
  g.font = `600 22px ${FT}`; g.fillStyle = 'rgba(255,255,255,.75)';
  g.fillText((1 + r() * 9).toFixed(1) + 'k', 58, 542);
  g.beginPath(); g.arc(140, 534, 11, 0, 6.283); g.strokeStyle = 'rgba(255,255,255,.6)'; g.lineWidth = 2.2; g.stroke();
  g.fillText(String(Math.floor(r() * 300)), 160, 542);
  g.fillStyle = 'rgba(255,255,255,.3)'; g.beginPath(); g.roundRect(24, 572, 300, 9, 4); g.fill();
  g.fillStyle = 'rgba(255,255,255,.15)'; g.beginPath(); g.roundRect(24, 594, 210, 9, 4); g.fill();
  return c;
}
let grains = [], vignette, bloomC, bloomX, tmpC, tmpX, markC;
function initAssets() {
  for (let i = 0; i < 16; i++) cards.push(makeCard(i + 1));
  // film grain
  for (let k = 0; k < 6; k++) {
    const g = document.createElement('canvas'); g.width = 540; g.height = 960; const gx = g.getContext('2d');
    const id = gx.createImageData(540, 960); const r = mulberry(1000 + k);
    for (let i = 0; i < id.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 120; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    gx.putImageData(id, 0, 0); grains.push(g);
  }
  vignette = document.createElement('canvas'); vignette.width = W; vignette.height = H;
  const vx = vignette.getContext('2d');
  const vg = vx.createRadialGradient(W / 2, H / 2, H * .22, W / 2, H / 2, H * .66);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.72)'); vx.fillStyle = vg; vx.fillRect(0, 0, W, H);
  bloomC = document.createElement('canvas'); bloomC.width = 270; bloomC.height = 480; bloomX = bloomC.getContext('2d');
  tmpC = document.createElement('canvas'); tmpC.width = W; tmpC.height = H; tmpX = tmpC.getContext('2d');
  markC = document.createElement('canvas'); markC.width = W; markC.height = 400;
}

// ─── Global timeline (seconds) ────────────────────────────────────
const T = {
  slams: [0.30, 0.62, 0.90, 1.12, 1.30, 1.45, 1.58],
  count0: 1.85, storm0: 2.85, freeze: 7.60, cut: 7.85,
  stmt: [8.60, 9.30, 10.00], stmtOut: 11.55,
  chart0: 12.0, diag0: 16.6, noise0: 20.6, collapse: 23.0, sys0: 25.0,
  stages: [26.0, 28.6, 31.2, 33.6, 36.0, 38.5], stagesEnd: 41.0,
  overview: 41.0, philo: [43.1, 44.35, 45.45], viral: 47.0, system: 49.3, brand: 52.0, end: 59.0
};
const IMPACTS = [ // [time, shake, zoomKick, flash]
  [0.30, 14, .05, .30], [0.62, 10, .03, .08], [0.90, 10, .03, .06], [1.12, 8, .02, .05], [1.30, 8, .02, .05], [1.45, 8, .02, .05], [1.58, 12, .04, .12],
  [T.freeze, 10, 0, .15],
  [T.stmt[0], 10, .025, .10], [T.stmt[1], 8, .02, .06], [T.stmt[2], 14, .035, .16],
  [T.collapse + .75, 6, .02, .22],
  [T.philo[0], 6, .015, .04], [T.philo[1], 6, .015, .04], [T.philo[2], 9, .02, .08],
  [T.viral, 8, .02, .06], [T.system, 22, .07, .45], [52.6, 6, .015, .12]
];
const GLITCH = [[1.84, .10, 1.0], [T.freeze, .14, 1.2], [22.95, .10, .7], [T.cut - .05, .05, .8]];

function glowAt(t) {
  const k = [[0, 0], [0.3, 0], [1.8, .5], [3, .75], [7.6, 1], [7.849, 1], [7.85, 0], [8.6, 0], [9.2, .85], [12, .8], [20.6, .7], [23.8, 1], [25, .8],
  [41, .8], [46.6, .5], [47, .35], [49.2, .5], [49.4, 1.1], [51.6, .6], [52.2, .2], [53.4, 1.1], [58.4, 1], [59, 0]];
  for (let i = 1; i < k.length; i++) if (t <= k[i][0]) return lerp(k[i - 1][1], k[i][1], P(t, k[i - 1][0], k[i][0]));
  return 0;
}

// ─── Background ───────────────────────────────────────────────────
function background(t) {
  ctx.fillStyle = C.ink; ctx.fillRect(0, 0, W, H);
  const g = glowAt(t); if (g <= 0) return;
  const cx = W * .5 + Math.sin(t * .35) * 70, cy = H * .30 + Math.cos(t * .27) * 60;
  let gr = ctx.createRadialGradient(cx, cy, 0, cx, cy, 1150);
  gr.addColorStop(0, `rgba(96,42,200,${.40 * g})`); gr.addColorStop(.45, `rgba(48,18,112,${.22 * g})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
  const bx = W * .5 + Math.cos(t * .21) * 120;
  gr = ctx.createRadialGradient(bx, H * 1.04, 0, bx, H * 1.04, 1000);
  gr.addColorStop(0, `rgba(80,30,170,${.30 * g})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gr; ctx.fillRect(0, 0, W, H);
}
function beams(a, t) {
  if (a <= 0) return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 3; i++) {
    const cx = W * (.30 + i * .2) + Math.sin(t * .5 + i * 2) * 30;
    const gr = ctx.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, `rgba(120,70,255,${.16 * a})`); gr.addColorStop(.75, 'rgba(120,70,255,0)');
    ctx.fillStyle = gr; ctx.beginPath(); ctx.moveTo(cx - 40, -10); ctx.lineTo(cx + 40, -10); ctx.lineTo(cx + 360 - i * 160, H); ctx.lineTo(cx - 200 - i * 120, H); ctx.fill();
  }
  ctx.restore();
}
function darkCenter(a, cy = H / 2, r = 700) {
  const g = ctx.createRadialGradient(W / 2, cy, 0, W / 2, cy, r);
  g.addColorStop(0, `rgba(4,2,9,${a})`); g.addColorStop(1, 'rgba(4,2,9,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

// ═══ SCENE 01 — HOOK ═════════════════════════════════════════════
function sHook(t) {
  if (t >= 3.2) return;
  if (t < T.slams[0]) { // blinking cursor in the void
    if (Math.floor(t * 4) % 2 === 0) { ctx.fillStyle = C.y; ctx.fillRect(W / 2 - 4, H / 2 - 40, 8, 80); }
    return;
  }
  if (t < T.count0) {
    let i = 0; while (i < T.slams.length - 1 && t >= T.slams[i + 1]) i++;
    const lt = t - T.slams[i];
    const sc = 1 + .09 * Math.exp(-lt * 14);
    // flashing post cards behind (more each beat)
    const r = mulberry(100 + i);
    const n = i < 2 ? i : 2 + i;
    for (let k = 0; k < n; k++) {
      const ci = Math.floor(r() * 16), cx = 120 + r() * 840, cy = 300 + r() * 1300, s = .5 + r() * .55, rot = (r() - .5) * .3;
      ctx.save(); ctx.globalAlpha = .55 + .3 * r(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.scale(s * sc, s * sc);
      ctx.drawImage(cards[ci], -CARD_W / 2, -CARD_H / 2); ctx.restore();
    }
    if (i >= 2) darkCenter(.6, H / 2, 650);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-W / 2, -H / 2);
    const S = [
      () => txt('POST.', W / 2, H / 2 + 100, { size: 290, w: 900, track: -.04, align: 'center' }),
      () => txt('POST.', W / 2, H / 2 + 150, { size: 400, w: 900, track: -.04, align: 'center', stroke: 3, c: C.lav }),
      () => txt('POST.', 90, 760, { size: 230, w: 900, track: -.04, c: C.y, glow: 30 }),
      () => txt('POST.', W - 90, 1420, { size: 260, w: 900, track: -.04, align: 'right' }),
      () => txt('POST.', W / 2, H / 2 + 80, { size: 200, w: 900, track: -.04, align: 'center', stroke: 2.5, c: C.y }),
      () => txt('POST.', 90, 1080, { size: 330, w: 900, track: -.04 }),
      () => txt('POST.', W / 2, H / 2 + 190, { size: 560, w: 900, track: -.05, align: 'center' })
    ];
    S[i]();
    ctx.restore();
    // final stutter: full card grid flicker
    if (t > 1.70) {
      const f = Math.floor(t * FPS), r2 = mulberry(f * 31);
      for (let k = 0; k < 9; k++) { const s = .62; ctx.save(); ctx.globalAlpha = .9; ctx.translate(90 + (k % 3) * 300 + 60, 200 + Math.floor(k / 3) * 520 + 200); ctx.scale(s, s); ctx.drawImage(cards[Math.floor(r2() * 16)], -CARD_W / 2, -CARD_H / 2); ctx.restore(); }
    }
    return;
  }
  // counter
  const lt = t - T.count0;
  const a = 1 - E.i3(P(t, 2.85, 3.15));
  const zs = 1 + E.i3(P(t, 2.85, 3.15)) * .35;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, H / 2); ctx.scale(zs, zs); ctx.translate(-W / 2, -H / 2);
  rev('POSTS THIS YEAR', W / 2, 760, { size: 32, w: 600, f: FT, track: .34, c: C.lav, align: 'center' }, P(lt, .02, .4));
  const val = Math.round(lerp(1, 365, E.o4(P(t, 1.9, 2.65))));
  const numO = { size: 400, w: 900, track: -.05, align: 'center' };
  rev(String(val).padStart(3, '0'), W / 2, 1150, numO, P(lt, 0, .3));
  // progress rule
  const pw = 600 * E.o4(P(t, 1.9, 2.65));
  ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.fillRect(W / 2 - 300, 1230, 600, 3);
  ctx.fillStyle = C.y; ctx.fillRect(W / 2 - 300, 1230, pw, 3);
  ctx.beginPath(); ctx.arc(W / 2 - 300 + pw, 1231.5, 7, 0, 6.283); ctx.fill();
  rev('Every. Single. Day.', W / 2, 1330, { size: 46, w: 500, f: FT, c: C.mist, align: 'center' }, P(lt, .45, .85));
  ctx.restore();
}

// ═══ SCENE 02 — PROBLEM: the content storm ═══════════════════════
function stormPos(t) {
  const tt = Math.min(t, T.freeze), d = T.freeze - 3.0, u = clamp((tt - 3.0) / d);
  return 260 * (tt - 3.0) + 3800 * d * Math.pow(u, 3.2) / 3.2;
}
function stormVel(t) { if (t >= T.freeze) return 0; const u = clamp((t - 3.0) / (T.freeze - 3.0)); return 260 + 3800 * Math.pow(u, 2.2); }
const LAYERS = [{ sc: .40, sp: .55, a: .28, seed: 1 }, { sc: .64, sp: .85, a: .55, seed: 2 }, { sc: 1.0, sp: 1.3, a: .92, seed: 3, sparse: .6 }];
const NOTIFS = (() => {
  const r = mulberry(77), texts = ['+128 likes', 'New follower', 'Boost this post?', 'Trending sound', 'Reach -38%', 'Post #212 published', '3 new comments',
    'Story views: 412', 'Algorithm update', 'Engagement 1.2%', 'Try this trend', 'Schedule next post', 'Posting streak: 213 days', '+1 follower', 'Repost?', 'Insights ready'];
  const out = [];
  for (let k = 0; k < 30; k++) {
    const t0 = 3.05 + 4.5 * Math.pow(k / 30, .62);
    let x, y; do { x = 230 + r() * 620; y = 300 + r() * 1300; } while (y > 780 && y < 1150);
    out.push({ t0, x, y, s: texts[k % texts.length], yellow: k % 5 === 4 });
  }
  return out;
})();
function sStorm(t) {
  if (t < T.storm0 || t >= T.cut) return;
  const fa = E.o3(P(t, T.storm0, 3.15));
  const pos = stormPos(t), vel = stormVel(t);
  ctx.save(); ctx.globalAlpha = fa;
  ctx.translate(W / 2, H / 2); ctx.rotate(-.16); ctx.scale(1.05 + .1 * P(t, 3, 7.6), 1.05 + .1 * P(t, 3, 7.6)); ctx.translate(-W / 2, -H / 2);
  for (const L of LAYERS) {
    const cw = CARD_W * L.sc, ch = CARD_H * L.sc, gap = 40 * L.sc, px = cw + gap, py = ch + gap;
    const cols = Math.ceil(1900 / px) + 1, S = pos * L.sp, v = vel * L.sp;
    const ghost = v / FPS * .5;
    for (let j = 0; j < cols; j++) {
      const x = -420 + j * px;
      const SS = S + j * 173 * L.sc + (j % 2) * py * .5;
      const r0 = Math.floor(SS / py);
      for (let k = -1; k < Math.ceil(2400 / py) + 1; k++) {
        const row = r0 + k, y = -240 + row * py - SS;
        if (L.sparse && h3(row, j, L.seed) < L.sparse) continue;
        const img = cards[Math.floor(h3(row, j * 3, L.seed) * 16)];
        if (ghost > 2) {
          ctx.globalAlpha = fa * L.a * .28; ctx.drawImage(img, x, y + ghost * 2, cw, ch); ctx.drawImage(img, x, y + ghost, cw, ch);
        }
        ctx.globalAlpha = fa * L.a; ctx.drawImage(img, x, y, cw, ch);
      }
    }
  }
  ctx.restore();
  // notifications popping (frozen on freeze)
  const tn = Math.min(t, T.freeze);
  for (const n of NOTIFS) {
    const lt = tn - n.t0; if (lt < 0 || lt > 1.0) continue;
    const sc = E.back(P(lt, 0, .22)), a = 1 - P(lt, .75, 1.0);
    pill(n.x, n.y - lt * 40, n.s, { sc, a: a * fa, dot: n.yellow ? C.y : C.lav, yellow: n.yellow });
  }
  // legibility + mood
  ctx.fillStyle = 'rgba(5,3,10,.22)'; ctx.fillRect(0, 0, W, H);
  darkCenter(.82, H / 2 - 20, 640);
  // HUD
  const f = Math.floor(tn * FPS);
  label('FEED · LIVE', 80, 200, { size: 22, c: C.mist, a: fa });
  if (f % 16 < 10) { ctx.beginPath(); ctx.arc(66, 192, 6, 0, 6.283); ctx.fillStyle = C.y; ctx.fill(); }
  label('POST #' + String(Math.min(365, 212 + Math.floor(P(tn, 3, 7.6) * 153))).padStart(3, '0'), W - 80, 200, { size: 22, c: C.mist, align: 'right', a: fa });
  // supers
  const so = { size: 124, w: 700, track: -.035, align: 'center' };
  rev('Hari-hari post.', W / 2, H / 2 + 40, so, P(t, 3.2, 3.62), P(t, 4.45, 4.68));
  rev('Ikut setiap trend.', W / 2, H / 2 + 40, so, P(t, 4.68, 5.1), P(t, 5.7, 5.93));
  rev([['Tapi ', C.white], ['sales?', C.y, { glow: 34 }]], W / 2, H / 2 + 40, so, P(t, 5.93, 6.35));
  if (t >= T.freeze) { ctx.fillStyle = 'rgba(5,3,10,.35)'; ctx.fillRect(0, 0, W, H); }
}
function sStop(t) { // black beat
  if (t < T.cut || t >= T.stmt[0]) return;
  const a = E.o3(P(t, 8.0, 8.25)) * (1 - P(t, 8.42, 8.58));
  txt('Masih sama.', W / 2, H / 2 + 18, { size: 54, w: 500, f: FT, c: C.grey, align: 'center', a });
}
function sStatement(t) {
  if (t < T.stmt[0] || t >= 12.05) return;
  const lines = ['MORE CONTENT', "DOESN'T MEAN", 'MORE GROWTH.'];
  const o = { w: 900, track: -.04 };
  const size = fitSize(lines, W - 150, o, 200);
  const lh = size * 1.1, y0 = H / 2 - lh * .5;
  beams(P(t, 8.6, 9.4) * (1 - P(t, 11.6, 12.0)), t);
  const z = 1 + .055 * P(t, 8.6, 12);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
  label('THE UNCOMFORTABLE TRUTH', 78, y0 - lh - 30, { size: 24, c: C.lav, a: E.o3(P(t, 8.7, 9.1)) * (1 - P(t, 11.5, 11.7)) });
  rev(lines[0], 75, y0, { ...o, size, c: C.white }, P(t, T.stmt[0], T.stmt[0] + .5), P(t, T.stmtOut, T.stmtOut + .35));
  rev(lines[1], 75, y0 + lh, { ...o, size, c: C.lav, stroke: 2.5 }, P(t, T.stmt[1], T.stmt[1] + .5), P(t, T.stmtOut + .06, T.stmtOut + .41));
  rev(lines[2], 75, y0 + lh * 2, { ...o, size, c: C.y, glow: 40 }, P(t, T.stmt[2], T.stmt[2] + .5), P(t, T.stmtOut + .12, T.stmtOut + .47));
  ctx.restore();
}

// ═══ SCENE 03 — INSIGHT ══════════════════════════════════════════
const CH = { x0: 120, x1: 960, top: 780, bot: 1330 };
const CONTENT_PTS = [...Array(12)].map((_, i) => CH.bot - 40 - Math.pow(i / 11, 1.15) * 470 + (h3(i, 5) - .5) * 36 * (i > 0 && i < 11));
const SALES_PTS = [...Array(12)].map((_, i) => CH.bot - 70 + Math.sin(i * 1.7) * 9);
function drawSeries(pts, prog, col, wdt, dots) {
  const n = pts.length - 1, upto = prog * n, xs = i => CH.x0 + i * (CH.x1 - CH.x0) / n;
  ctx.beginPath(); ctx.moveTo(xs(0), pts[0]);
  let ex = xs(0), ey = pts[0];
  for (let i = 1; i <= Math.ceil(upto); i++) { const f = Math.min(1, upto - (i - 1)); ex = lerp(xs(i - 1), xs(i), f); ey = lerp(pts[i - 1], pts[i], f); ctx.lineTo(ex, ey); }
  ctx.strokeStyle = col; ctx.lineWidth = wdt; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke();
  if (dots) for (let i = 0; i <= Math.floor(upto); i++) { ctx.beginPath(); ctx.arc(xs(i), pts[i], 6, 0, 6.283); ctx.fillStyle = col; ctx.fill(); }
  return [ex, ey];
}
function sChart(t) {
  if (t < T.chart0 || t >= T.diag0) return;
  const out = P(t, 16.25, 16.6), oa = 1 - E.i3(out);
  ctx.save(); ctx.translate(0, -E.i3(out) * 80); ctx.globalAlpha = oa;
  // grid
  const gp = E.o4(P(t, 12.0, 12.7));
  for (let i = 0; i < 5; i++) { const y = CH.top + i * (CH.bot - CH.top) / 4; ctx.fillStyle = 'rgba(255,255,255,.07)'; ctx.fillRect(CH.x0, y, (CH.x1 - CH.x0) * gp, 2); }
  ['Q1', 'Q2', 'Q3', 'Q4'].forEach((q, i) => label(q, CH.x0 + (i + .5) * (CH.x1 - CH.x0) / 4, CH.bot + 62, { size: 22, c: C.grey, align: 'center', a: gp }));
  // gap fill
  const gf = E.o3(P(t, 14.5, 15.2));
  if (gf > 0) {
    const n = 11, xs = i => CH.x0 + i * (CH.x1 - CH.x0) / n;
    ctx.beginPath(); CONTENT_PTS.forEach((y, i) => i ? ctx.lineTo(xs(i), y) : ctx.moveTo(xs(i), y));
    for (let i = n; i >= 0; i--) ctx.lineTo(xs(i), SALES_PTS[i]);
    const g = ctx.createLinearGradient(0, CH.top, 0, CH.bot); g.addColorStop(0, `rgba(123,60,240,${.32 * gf})`); g.addColorStop(1, 'rgba(123,60,240,0)');
    ctx.fillStyle = g; ctx.fill();
    label('THE GAP', W / 2 + 90, 1130, { size: 24, c: C.mist, a: gf, align: 'center' });
  }
  const pc = E.io3(P(t, 12.35, 13.9)), ps = E.io3(P(t, 13.15, 14.6));
  ctx.save(); ctx.shadowColor = 'rgba(255,255,255,.4)'; ctx.shadowBlur = 16;
  const [cx, cy] = drawSeries(CONTENT_PTS, pc, C.white, 5, true); ctx.restore();
  const [sx, sy] = drawSeries(SALES_PTS, ps, C.lav, 5, false);
  if (pc > .02) { ctx.beginPath(); ctx.arc(cx, cy, 11, 0, 6.283); ctx.fillStyle = C.white; ctx.fill(); }
  if (ps > .02) { ctx.beginPath(); ctx.arc(sx, sy, 11, 0, 6.283); ctx.fillStyle = C.lav; ctx.fill(); }
  label('CONTENT OUTPUT ↑', CH.x1, CONTENT_PTS[11] - 34, { size: 24, c: C.white, align: 'right', a: P(t, 13.8, 14.1) });
  label('SALES →', CH.x1, SALES_PTS[11] + 52, { size: 24, c: C.lav, align: 'right', a: P(t, 14.5, 14.8) });
  ctx.restore();
  const ho = { size: 110, w: 700, track: -.035 };
  rev('Effort naik.', 100, 470, { ...ho, c: C.white }, P(t, 12.15, 12.6), out);
  rev('Sales tak gerak.', 100, 590, { ...ho, c: C.lav }, P(t, 13.25, 13.7), out);
  rev([["The problem isn't ", C.white], ['effort.', C.white, { w: 700 }]], W / 2, 1530, { size: 60, w: 500, f: FT, track: -.01, align: 'center' }, P(t, 15.0, 15.4), out);
}
function sDiag(t) {
  if (t < T.diag0 || t >= T.noise0) return;
  const out = P(t, 20.25, 20.6);
  const so = { size: 128, w: 800, track: -.04 };
  rev("It's the lack of", 92, 560, { ...so, c: C.white }, P(t, 16.65, 17.1), out);
  rev('a system.', 92, 690, { ...so, c: C.y, glow: 34 }, P(t, 16.85, 17.3), out);
  const qs = ['Siapa audience sebenar?', 'Content mana yang convert?', 'Kenapa views tak jadi sales?'];
  const qo = { w: 600, f: FT, track: -.015 };
  const qsz = fitSize(qs, 760, qo, 60);
  label('TANPA SYSTEM, TAK ADA JAWAPAN', 96, 900, { size: 22, c: C.grey, a: E.o3(P(t, 17.6, 17.9)) * (1 - out) });
  qs.forEach((q, i) => {
    const t0 = 17.75 + i * .65, y = 1030 + i * 150;
    const lw = E.o4(P(t, t0, t0 + .6)) * (1 - E.i3(out));
    ctx.fillStyle = 'rgba(255,255,255,.12)'; ctx.fillRect(96, y + 48, 888 * lw, 2);
    rev(String(i + 1).padStart(2, '0'), 96, y, { size: 30, w: 700, f: FT, track: .1, c: C.y }, P(t, t0, t0 + .4), out);
    rev(q, 190, y, { ...qo, size: qsz, c: C.white }, P(t, t0 + .05, t0 + .5), out);
  });
}
const NL = [...Array(64)].map((_, i) => { const r = mulberry(500 + i); return { y: 260 + r() * 1400, amp: 18 + r() * 95, f1: 1 + r() * 4, f2: 4 + r() * 10, ph: r() * 6.28, col: [C.lav, C.violet, C.white, C.grey, C.lav][Math.floor(r() * 5)], w: 1 + r() * 2.2, a: .22 + r() * .5, key: r() < .16 }; });
const FRAGS = ['#fyp', 'trend', 'viral?', '+1', 'boost', 'repost', 'hook?', 'algo', 'views', 'POV', 'duet', 'collab', 'reach', 'like', 'share', 'save', 'sound', 'promo'];
function sNoise(t) {
  if (t < T.noise0 || t >= 25.6) return;
  const f = Math.floor(t * FPS);
  const A = E.o3(P(t, 20.6, 21.0)) * (1 - E.io3(P(t, 23.0, 23.75)));
  const conv = E.io3(P(t, 22.95, 23.75));
  const lineA = 1 - P(t, 23.6, 23.85);
  if (lineA > 0) {
    ctx.save(); ctx.lineJoin = 'round';
    NL.forEach((L, i) => {
      ctx.beginPath();
      for (let k = 0; k <= 48; k++) {
        const x = -20 + k * (W + 40) / 48;
        const n = Math.sin(x * .004 * L.f1 + L.ph + t * 3) * .55 + Math.sin(x * .01 * L.f2 + t * 11 + L.ph) * .3 + (h3(f, i, k) - .5) * .9;
        const y = lerp(L.y, H / 2, conv) + n * L.amp * Math.max(A, 0) * (1.6 - .6 * conv);
        k ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      }
      const col = L.key ? mixHex(L.col === C.white ? '#f6f3fc' : '#ab94ff', '#e8ff2b', conv) : L.col;
      ctx.strokeStyle = col; ctx.globalAlpha = L.a * lineA * (L.key ? 1 : 1 - conv * .85) * E.o3(P(t, 20.6, 20.9)); ctx.lineWidth = L.w; ctx.stroke();
    });
    ctx.restore();
    // flickering fragments
    for (let k = 0; k < 16; k++) {
      const seed = Math.floor(f / 3) * 16 + k; if (h3(seed, 9) < .45) continue;
      const a = (.25 + h3(seed, 2) * .45) * A;
      txt(FRAGS[Math.floor(h3(seed, 3) * FRAGS.length)], 60 + h3(seed, 4) * 860, 280 + h3(seed, 5) * 1380, { size: 26 + h3(seed, 6) * 22, w: 600, f: FT, c: h3(seed, 7) < .2 ? C.y : C.lav, a });
    }
  }
  darkCenter(.85 * (1 - conv), 900, 560);
  const so = { size: 92, w: 700, track: -.035, align: 'center' };
  const out = P(t, 22.7, 22.95);
  rev('Content tanpa insight', W / 2, 870, so, P(t, 20.85, 21.25), out);
  // "noise." with chromatic jitter
  const pin = P(t, 21.25, 21.65);
  if (pin > 0 && out < 1) {
    const j = (h3(f, 77) - .5) * 14 * (1 - out);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    rev([['cuma ', C.white], ['noise.', '#ff3bd0']], W / 2 + j, 990, so, pin, out);
    rev([['cuma ', 'rgba(0,0,0,0)'], ['noise.', '#3bd7ff']], W / 2 - j, 990, so, pin, out);
    ctx.restore();
    rev([['cuma ', C.white], ['noise.', C.lav]], W / 2, 990, so, pin, out);
  }
  // the signal
  const sa = P(t, 23.55, 23.8) * (1 - P(t, 25.0, 25.05));
  if (sa > 0 && t < 25.0) {
    ctx.save(); ctx.globalAlpha = sa; ctx.shadowColor = rgba(YR, .9); ctx.shadowBlur = 26;
    ctx.fillStyle = C.y; ctx.fillRect(0, H / 2 - 2, W, 4); ctx.restore();
    const px = lerp(-150, W + 150, E.io3(P(t, 23.85, 24.85)));
    const g = ctx.createRadialGradient(px, H / 2, 0, px, H / 2, 160); g.addColorStop(0, 'rgba(255,255,230,.9)'); g.addColorStop(.25, rgba(YR, .35)); g.addColorStop(1, rgba(YR, 0));
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(px - 160, H / 2 - 160, 320, 320); ctx.restore();
    label('SIGNAL', 80, H / 2 - 36, { size: 22, c: C.y, a: P(t, 23.9, 24.2) * (1 - P(t, 24.8, 25)) });
    rev([['Insight turns noise into ', C.white], ['signal.', C.y]], W / 2, H / 2 + 120, { size: 54, w: 500, f: FT, track: -.01, align: 'center' }, P(t, 24.0, 24.4), P(t, 24.8, 25.0));
  }
}

// ═══ SCENE 04 — STRATEGY: the system ═════════════════════════════
const RAIL = { y: 330, x0: 140, x1: 940 };
const NODES = [...Array(6)].map((_, i) => RAIL.x0 + i * (RAIL.x1 - RAIL.x0) / 5);
const STAGES = [
  { name: 'AUDIT', d: ['Audience. Content. Conversion.', 'Kami baca data dulu.'] },
  { name: 'POSITION', d: ['Find the niche', 'that actually buys.'] },
  { name: 'CREATE', d: ['Content built with intent,', 'not by trend.'] },
  { name: 'TEST', d: ['Organic posts test', 'what really works.'] },
  { name: 'ADVERTISE', d: ['Budget goes behind', 'proven content only.'] },
  { name: 'SCALE', d: ["Scale what's working.", "Cut what isn't."] }
];
function stageIndex(t) { let i = -1; for (let k = 0; k < 6; k++) if (t >= T.stages[k]) i = k; return i; }
function sRail(t) {
  if (t < T.sys0 || t >= 41.4) return;
  const mp = E.io3(P(t, 25.0, 25.9));
  const ra = 1 - P(t, 41.0, 41.35);
  ctx.save(); ctx.globalAlpha = ra;
  const x0 = lerp(0, RAIL.x0, mp), x1 = lerp(W, RAIL.x1, mp), y = lerp(H / 2, RAIL.y, mp);
  const lineCol = mp < 1 ? mixHex('#e8ff2b', '#3a3152', E.i2(P(t, 25.4, 25.9))) : C.dim;
  ctx.save(); if (mp < .9) { ctx.shadowColor = rgba(YR, .8 * (1 - mp)); ctx.shadowBlur = 24; }
  ctx.fillStyle = lineCol; ctx.fillRect(x0, y - (mp < 1 ? lerp(2, 1.5, mp) : 1.5), x1 - x0, mp < 1 ? lerp(4, 3, mp) : 3); ctx.restore();
  // progress
  const si = stageIndex(t);
  if (si >= 0) {
    const prev = si > 0 ? NODES[si - 1] : NODES[0], target = NODES[si];
    const px = lerp(prev, target, E.io3(P(t, T.stages[si], T.stages[si] + .45)));
    ctx.save(); ctx.shadowColor = rgba(YR, .8); ctx.shadowBlur = 14; ctx.fillStyle = C.y; ctx.fillRect(RAIL.x0, RAIL.y - 1.5, px - RAIL.x0, 3); ctx.restore();
  }
  NODES.forEach((nx, i) => {
    const ap = E.back(P(t, 25.6 + i * .07, 25.95 + i * .07)); if (ap <= 0) return;
    const active = si === i, done = si > i;
    const pulse = active ? E.o3(P(t, T.stages[i] + .3, T.stages[i] + .6)) : 0;
    ctx.beginPath(); ctx.arc(nx, RAIL.y, (active ? 13 : 9) * ap, 0, 6.283);
    if (active || done) { ctx.fillStyle = active ? C.y : C.lav; ctx.fill(); }
    else { ctx.fillStyle = C.ink; ctx.fill(); ctx.strokeStyle = C.grey; ctx.lineWidth = 2.5; ctx.stroke(); }
    if (active) { ctx.beginPath(); ctx.arc(nx, RAIL.y, 13 + pulse * 26, 0, 6.283); ctx.strokeStyle = rgba(YR, .7 * (1 - pulse)); ctx.lineWidth = 2; ctx.stroke(); }
    label(String(i + 1).padStart(2, '0'), nx, RAIL.y + 52, { size: 20, align: 'center', c: active ? C.y : done ? C.lav : C.grey, a: ap });
  });
  label('THE LOKADIGITAL SYSTEM', W / 2, 232, { size: 24, align: 'center', c: C.mist, a: E.o3(P(t, 25.6, 26.0)) });
  ctx.restore();
}
let stageWordSize = 0;
function sStages(t) {
  if (t < T.stages[0] || t >= T.stagesEnd) return;
  const si = stageIndex(t), st = T.stages[si], en = si < 5 ? T.stages[si + 1] : T.stagesEnd, lt = t - st;
  const out = P(t, en - .32, en);
  const S = STAGES[si];
  if (!stageWordSize) stageWordSize = fitSize(STAGES.map(s => s.name), 860, { w: 900, track: -.04 }, 190);
  rev([[String(si + 1).padStart(2, '0'), C.y], [' / 06', C.grey]], 110, 470, { size: 30, w: 700, f: FT, track: .12 }, P(lt, 0, .35), out);
  revLetters(S.name, 104, 470 + stageWordSize * .98, { size: stageWordSize, w: 900, track: -.04, c: C.white }, lt, { pout: out });
  const dy = 470 + stageWordSize * .98 + 92;
  S.d.forEach((l, k) => rev(l, 110, dy + k * 58, { size: 44, w: 500, f: FT, track: -.01, c: k ? C.lav : C.mist }, P(lt, .22 + k * .08, .6 + k * .08), P(t, en - .32 + k * .04, en)));
  const va = 1 - E.i3(out);
  ctx.save(); ctx.globalAlpha = va; ctx.translate(0, -E.i3(out) * 60);
  [vAudit, vPosition, vCreate, vTest, vAdvertise, vScale][si](lt, t);
  ctx.restore();
}
const VA = { x: 140, y: 1000, w: 800, h: 560 };  // visual area
function miniTile(x, y, w, h, seed, a = 1) {
  ctx.save(); ctx.globalAlpha *= a;
  rr(x, y, w, h, 14); ctx.fillStyle = '#120a24'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.08)'; ctx.lineWidth = 1.5; ctx.stroke();
  const th = h - 28; const g = ctx.createLinearGradient(x, y, x + th, y + th); g.addColorStop(0, '#4b1fa0'); g.addColorStop(1, '#1c0e40');
  rr(x + 14, y + 14, th * .72, th, 9); ctx.fillStyle = g; ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.4)'; rr(x + 30 + th * .72, y + 26, w * .38, 9, 4); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.15)'; rr(x + 30 + th * .72, y + 46, w * .26, 8, 4); ctx.fill();
  ctx.fillStyle = 'rgba(171,148,255,.5)'; rr(x + 30 + th * .72, y + h - 34, (w * .4) * (.3 + h3(seed, 1) * .7), 8, 4); ctx.fill();
  ctx.restore();
}
function vAudit(lt) {
  const cols = 3, rows = 4, gap = 22, tw = (VA.w - gap * 2) / 3, th = 118;
  const keep = new Set([1, 5, 9]);
  const scanY = VA.y - 20 + E.io3(P(lt, .5, 1.75)) * (rows * (th + gap) + 30);
  for (let i = 0; i < 12; i++) {
    const c = i % cols, r = Math.floor(i / cols), x = VA.x + c * (tw + gap), y = VA.y + r * (th + gap);
    const ap = E.o3(P(lt, .12 + i * .025, .45 + i * .025));
    const passed = scanY > y + th / 2;
    const k = keep.has(i);
    miniTile(x, y + (1 - ap) * 30, tw, th, i, ap * (passed && !k ? .32 : 1));
    if (passed) {
      const tp = E.back(P(scanY, y + th / 2, y + th / 2 + 60));
      if (k) { ctx.save(); ctx.shadowColor = rgba(YR, .6); ctx.shadowBlur = 18; rr(x, y, tw, th, 14); ctx.strokeStyle = C.y; ctx.lineWidth = 3; ctx.stroke(); ctx.restore(); }
      label(k ? 'KEEP' : 'CUT', x + tw - 14, y + 30, { size: 18, align: 'right', c: k ? C.y : C.grey, a: tp });
    }
  }
  if (lt > .45 && lt < 1.9) {
    const sa = Math.min(P(lt, .45, .6), 1 - P(lt, 1.7, 1.9));
    const g = ctx.createLinearGradient(0, scanY - 120, 0, scanY); g.addColorStop(0, rgba(YR, 0)); g.addColorStop(1, rgba(YR, .14 * sa));
    ctx.fillStyle = g; ctx.fillRect(VA.x - 30, scanY - 120, VA.w + 60, 120);
    ctx.save(); ctx.shadowColor = rgba(YR, .9); ctx.shadowBlur = 16; ctx.fillStyle = rgba(YR, sa); ctx.fillRect(VA.x - 30, scanY - 1.5, VA.w + 60, 3); ctx.restore();
  }
}
const DOTS = (() => {
  const r = mulberry(4242), cl = [[330, 1120], [720, 1080], [420, 1440], [740, 1400]], out = [];
  for (let i = 0; i < 320; i++) {
    let x, y; if (r() < .25) { x = VA.x + r() * VA.w; y = VA.y + r() * VA.h; }
    else { const c = cl[Math.floor(r() * 4)]; x = c[0] + gauss(r) * 70; y = c[1] + gauss(r) * 55; }
    out.push({ x: clamp(x, VA.x, VA.x + VA.w), y: clamp(y, VA.y, VA.y + VA.h), ph: r() * 6.28, s: 2.5 + r() * 3 });
  }
  return out;
})();
function vPosition(lt) {
  const target = [740, 1400];
  const mp = E.io3(P(lt, .3, 1.3)), lock = E.o3(P(lt, 1.3, 1.6));
  const rx = lerp(W / 2, target[0], mp), ry = lerp(1280, target[1], mp), rad = lerp(330, 120, mp);
  DOTS.forEach((d, i) => {
    const ap = E.o3(P(lt, .05 + (i % 40) * .008, .4 + (i % 40) * .008));
    const x = d.x + Math.sin(lt * 1.3 + d.ph) * 5, y = d.y + Math.cos(lt * 1.1 + d.ph) * 5;
    const inside = Math.hypot(x - target[0], y - target[1]) < 120;
    ctx.beginPath(); ctx.arc(x, y, d.s, 0, 6.283);
    ctx.fillStyle = inside ? mixHex('#ab94ff', '#e8ff2b', lock) : C.lav;
    ctx.globalAlpha = ap * (inside ? 1 : lerp(.8, .16, lock)); ctx.fill();
  });
  ctx.globalAlpha = 1;
  // crosshair guides
  ctx.fillStyle = 'rgba(255,255,255,.07)'; ctx.fillRect(VA.x, ry, VA.w, 1.5); ctx.fillRect(rx, VA.y - 20, 1.5, VA.h + 40);
  const ra = E.o3(P(lt, .2, .45));
  ctx.save(); ctx.globalAlpha = ra; ctx.strokeStyle = lock > 0 ? C.y : C.white; ctx.lineWidth = 2.5;
  if (lock > 0) { ctx.shadowColor = rgba(YR, .7); ctx.shadowBlur = 16; }
  ctx.beginPath(); ctx.arc(rx, ry, rad, 0, 6.283); ctx.stroke();
  for (let k = 0; k < 4; k++) { const an = k * Math.PI / 2 + lt * .4 * (1 - lock); ctx.beginPath(); ctx.moveTo(rx + Math.cos(an) * (rad - 16), ry + Math.sin(an) * (rad - 16)); ctx.lineTo(rx + Math.cos(an) * (rad + 16), ry + Math.sin(an) * (rad + 16)); ctx.stroke(); }
  ctx.restore();
  if (lock > 0) {
    ctx.fillStyle = rgba(YR, .6 * lock); ctx.fillRect(target[0] - 120 - 260 * lock, target[1] - 1, 260 * lock, 2);
    label('CORE AUDIENCE', target[0] - 400, target[1] - 16, { size: 22, c: C.y, a: lock });
    label('HIGH INTENT · NICHE', target[0] - 400, target[1] + 26, { size: 18, c: C.grey, a: lock });
  }
}
function phoneFrame(cx, cy, w, h, kind, { a = 1, hi = false } = {}) {
  ctx.save(); ctx.globalAlpha *= a;
  rr(cx - w / 2, cy - h / 2, w, h, 22); ctx.fillStyle = '#100820'; ctx.fill();
  if (hi) { ctx.shadowColor = rgba(YR, .7); ctx.shadowBlur = 30; ctx.strokeStyle = C.y; ctx.lineWidth = 3.5; }
  else { ctx.strokeStyle = 'rgba(255,255,255,.2)'; ctx.lineWidth = 2; }
  ctx.stroke(); ctx.shadowBlur = 0;
  const x = cx - w / 2, y = cy - h / 2;
  const g = ctx.createLinearGradient(x, y, x, y + h); g.addColorStop(0, '#2a1166'); g.addColorStop(1, '#0d0620');
  rr(x + 12, y + 12, w - 24, h - 24, 14); ctx.fillStyle = g; ctx.fill();
  if (kind === 0) { // hook: bold headline + play
    ctx.fillStyle = C.white; rr(x + 30, y + 60, w * .7, 22, 6); ctx.fill(); rr(x + 30, y + 94, w * .5, 22, 6); ctx.fill();
    ctx.fillStyle = C.y; rr(x + 30, y + 128, w * .3, 22, 6); ctx.fill();
    ctx.beginPath(); ctx.moveTo(cx - 22, cy + 20); ctx.lineTo(cx + 30, cy + 50); ctx.lineTo(cx - 22, cy + 80); ctx.closePath(); ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.fill();
  } else if (kind === 1) { // value: mini chart
    [.35, .55, .45, .8].forEach((v, i) => { ctx.fillStyle = i === 3 ? C.lav : 'rgba(171,148,255,.4)'; const bw = (w - 90) / 4; rr(x + 30 + i * (bw + 10), y + h - 70 - v * (h * .5), bw, v * (h * .5), 6); ctx.fill(); });
    ctx.fillStyle = 'rgba(255,255,255,.7)'; rr(x + 30, y + 50, w * .6, 14, 6); ctx.fill();
  } else { // offer: product + CTA
    const og = ctx.createRadialGradient(cx, cy - 30, 0, cx, cy - 30, w * .35); og.addColorStop(0, '#c4b2ff'); og.addColorStop(1, 'rgba(91,43,192,0)');
    ctx.fillStyle = og; ctx.fillRect(x, y, w, h);
    ctx.fillStyle = C.y; rr(x + 30, y + h - 80, w - 60, 40, 20); ctx.fill();
  }
  ctx.restore();
}
function vCreate(lt) {
  const names = ['HOOK', 'VALUE', 'OFFER'];
  for (let i = 0; i < 3; i++) {
    const p = E.o4(P(lt, .2 + i * .14, .8 + i * .14));
    const cx = W / 2 + (i - 1) * 272, cy = 1260 + (1 - p) * 120;
    phoneFrame(cx, cy, 236, 420, i, { a: p });
    label(String(i + 1).padStart(2, '0') + '  ' + names[i], cx, 1520, { size: 22, align: 'center', c: i === 0 ? C.y : C.mist, a: p });
    if (i < 2) { const lp = E.o3(P(lt, .7 + i * .2, 1.0 + i * .2)); ctx.fillStyle = rgba(YR, .8); ctx.fillRect(cx + 118 + 4, 1260, 28 * lp, 2); }
  }
}
function vTest(lt) {
  const fin = [.40, .57, .94, .33], pct = [18, 27, 61, 15];
  label('ORGANIC TEST  ·  RETENTION', VA.x, 1000, { size: 22, c: C.lav, a: E.o3(P(lt, .1, .4)) });
  const win = E.o3(P(lt, 1.5, 1.8));
  for (let i = 0; i < 4; i++) {
    const y = 1080 + i * 120, ap = E.o3(P(lt, .1 + i * .06, .4 + i * .06));
    const grow = E.o3(P(lt, .25, 1.45)), wob = Math.sin(lt * 10 + i * 1.7) * .04 * (1 - P(lt, 1.1, 1.45));
    const v = clamp(fin[i] * grow + wob * grow, 0, 1);
    const isW = i === 2, dim = isW ? 1 : lerp(1, .3, win);
    txt('ABCD'[i], VA.x, y + 34, { size: 52, w: 800, c: isW && win > 0 ? mixHex('#f6f3fc', '#e8ff2b', win) : C.white, a: ap * dim });
    const bx = VA.x + 80, bw = VA.w - 80;
    rr(bx, y, bw, 40, 20); ctx.fillStyle = `rgba(255,255,255,${.06 * ap})`; ctx.fill();
    ctx.save(); ctx.globalAlpha = ap * dim;
    if (isW && win > 0) { ctx.shadowColor = rgba(YR, .7 * win); ctx.shadowBlur = 22; }
    rr(bx, y, Math.max(40, bw * v), 40, 20); ctx.fillStyle = isW ? mixHex('#7b3cf0', '#e8ff2b', win) : C.violet; ctx.fill(); ctx.restore();
    label(Math.round(pct[i] * clamp(grow + wob)) + '%', bx + Math.max(40, bw * v) - 16, y + 28, { size: 20, align: 'right', c: isW && win > .5 ? C.ink : C.white, a: ap * dim * P(lt, .4, .6) });
  }
  if (win > 0) pill(VA.x + VA.w - 90, 1080 + 2 * 120 - 46, 'WINNER', { sc: E.back(win), yellow: true, dot: C.y, size: 22 });
}
function vAdvertise(lt) {
  const cx = W / 2, cy = 1270;
  for (let k = 0; k < 5; k++) {
    const ph = ((lt - .3) * .9 + k / 5) % 1; if (lt < .3) break;
    const r = 160 + ph * 470;
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 6.283); ctx.strokeStyle = k % 2 ? rgba(YR, .45 * (1 - ph)) : `rgba(171,148,255,${.4 * (1 - ph)})`; ctx.lineWidth = 2; ctx.stroke();
  }
  const tags = [['TikTok Ads', 290, 1040], ['Meta Ads', 800, 1080], ['Retargeting', 270, 1500], ['Lookalike', 790, 1470]];
  tags.forEach((tg, i) => {
    const p = P(lt, .55 + i * .14, .85 + i * .14); if (p <= 0) return;
    ctx.strokeStyle = `rgba(171,148,255,${.35 * p})`; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(lerp(cx, tg[1], E.o3(p)), lerp(cy, tg[2], E.o3(p))); ctx.stroke();
    pill(tg[1], tg[2], tg[0], { sc: E.back(p), size: 26, dot: i < 2 ? C.y : C.lav });
  });
  const sp = E.back(P(lt, .05, .45));
  ctx.save(); ctx.translate(cx, cy); ctx.scale(sp, sp); phoneFrame(0, 0, 250, 446, 0, { hi: true }); ctx.restore();
}
function vScale(lt) {
  const x0 = VA.x + 10, x1 = VA.x + VA.w - 20, yb = 1560, ht = 560, k = 3.3;
  const fy = u => yb - (Math.exp(k * u) - 1) / (Math.exp(k) - 1) * ht;
  const ga = E.o3(P(lt, .05, .35));
  for (let i = 0; i < 4; i++) { const x = lerp(x0, x1, (i + 1) / 4); ctx.fillStyle = `rgba(255,255,255,${.06 * ga})`; ctx.fillRect(x, yb - ht - 20, 1.5, ht + 20); label(['WK 1', 'WK 4', 'WK 8', 'WK 12'][i], x, yb + 44, { size: 18, align: 'center', c: C.grey, a: ga }); }
  ctx.fillStyle = `rgba(255,255,255,${.15 * ga})`; ctx.fillRect(x0, yb, x1 - x0, 2);
  const p = E.io3(P(lt, .2, 1.5)); if (p <= 0) return;
  const N = 80, up = p;
  ctx.beginPath(); ctx.moveTo(x0, yb);
  for (let i = 0; i <= N; i++) { const u = i / N * up; ctx.lineTo(lerp(x0, x1, u), fy(u)); }
  ctx.lineTo(lerp(x0, x1, up), yb); ctx.closePath();
  const g = ctx.createLinearGradient(0, yb - ht, 0, yb); g.addColorStop(0, 'rgba(123,60,240,.45)'); g.addColorStop(1, 'rgba(123,60,240,0)'); ctx.fillStyle = g; ctx.fill();
  ctx.beginPath(); for (let i = 0; i <= N; i++) { const u = i / N * up; i ? ctx.lineTo(lerp(x0, x1, u), fy(u)) : ctx.moveTo(x0, fy(0)); }
  ctx.save(); ctx.shadowColor = rgba(YR, .8); ctx.shadowBlur = 20; ctx.strokeStyle = C.y; ctx.lineWidth = 5; ctx.lineCap = 'round'; ctx.stroke(); ctx.restore();
  const tx = lerp(x0, x1, up), ty = fy(up);
  ctx.beginPath(); ctx.arc(tx, ty, 12, 0, 6.283); ctx.fillStyle = C.y; ctx.fill();
  const pu = (lt * 1.5) % 1; ctx.beginPath(); ctx.arc(tx, ty, 12 + pu * 34, 0, 6.283); ctx.strokeStyle = rgba(YR, .6 * (1 - pu)); ctx.lineWidth = 2; ctx.stroke();
}
function sOverview(t) {
  if (t < T.overview || t >= 43.05) return;
  const out = P(t, 42.65, 43.0);
  const words = STAGES.map(s => s.name);
  const lh = 136, y0 = 560, size = 104;
  const lp = E.io3(P(t, 41.0, 41.7)) * (1 - E.i3(out));
  ctx.save(); ctx.shadowColor = rgba(YR, .8); ctx.shadowBlur = 14; ctx.fillStyle = C.y;
  ctx.fillRect(118, y0 - 70, 3, (lh * 5 + 20) * lp); ctx.restore();
  words.forEach((w, i) => {
    const t0 = 41.05 + i * .1, y = y0 + i * lh;
    const dp = E.back(P(t, t0, t0 + .3)) * (1 - out);
    if (dp > 0) { ctx.beginPath(); ctx.arc(119.5, y - 36, 9 * dp, 0, 6.283); ctx.fillStyle = i === 5 ? C.y : C.lav; ctx.fill(); }
    rev(w, 170, y, { size, w: 900, track: -.04, c: i === 5 ? C.y : C.white, glow: i === 5 ? 30 : 0 }, P(t, t0, t0 + .45), P(t, 42.65 + i * .04, 43.0));
  });
  rev('↻  REPEAT. REFINE. COMPOUND.', 170, y0 + lh * 5 + 110, { size: 28, w: 600, f: FT, track: .2, c: C.lav }, P(t, 41.8, 42.15), out);
}

// ═══ SCENE 05 — IMPACT ═══════════════════════════════════════════
function sPhilo(t) {
  if (t < 43.0 || t >= 46.65) return;
  const out = P(t, 46.3, 46.62), o = { size: 112, w: 800, track: -.04 };
  const dimA = (i) => i === 2 ? 1 : lerp(1, .3, E.o3(P(t, T.philo[i + 1], T.philo[i + 1] + .3)));
  label('THE PHILOSOPHY', 92, 560, { size: 24, c: C.lav, a: E.o3(P(t, 43.05, 43.4)) * (1 - out) });
  ctx.save(); ctx.globalAlpha = dimA(0);
  rev('Content attracts', 88, 720, { ...o, c: C.white }, P(t, T.philo[0], T.philo[0] + .45), out);
  rev('attention.', 88, 840, { ...o, c: C.white }, P(t, T.philo[0] + .12, T.philo[0] + .57), out);
  ctx.restore();
  ctx.save(); ctx.globalAlpha = dimA(1);
  rev('Organic tests.', 88, 1030, { ...o, c: C.white }, P(t, T.philo[1], T.philo[1] + .45), out);
  ctx.restore();
  rev([['Ads ', C.white], ['scale.', C.y, { glow: 36 }]], 88, 1220, o, P(t, T.philo[2], T.philo[2] + .45), out);
}
let sysLayout = null;
function sysL() {
  if (sysLayout) return sysLayout;
  const o1 = { w: 900, track: -.04 };
  const s1 = fitSize(['VIRAL IS NOT', 'A STRATEGY.'], W - 170, o1, 170);
  const s2 = fitSize(['A SYSTEM IS.'], W - 150, o1, 200);
  const w2 = measure('A SYSTEM IS', { ...o1, size: s2 });
  const x2 = (W - measure('A SYSTEM IS.', { ...o1, size: s2 })) / 2;
  const dotX = x2 + w2 + s2 * .115, dotY = 1240 - s2 * .085, dotR = s2 * .068;
  return (sysLayout = { s1, s2, x2, dotX, dotY, dotR });
}
function sViral(t) {
  if (t < 46.6 || t >= 52.0) return;
  const L = sysL(), o = { w: 900, track: -.04 };
  const fade = 1 - P(t, 51.1, 51.6);
  const up = E.io3(P(t, 48.85, 49.25));
  ctx.save(); ctx.globalAlpha = lerp(1, .22, up) * fade; ctx.translate(0, -up * 70);
  rev('VIRAL IS NOT', 85, 800, { ...o, size: L.s1, c: C.white }, P(t, T.viral, T.viral + .5));
  rev('A STRATEGY.', 85, 800 + L.s1, { ...o, size: L.s1, c: C.white }, P(t, T.viral + .25, T.viral + .75));
  ctx.restore();
  if (t >= T.system) {
    const lt = t - T.system;
    const sc = 1 + .22 * Math.exp(-lt * 9) * (lt < 2 ? 1 : 0);
    const a = E.o3(P(lt, 0, .06));
    ctx.save(); ctx.translate(W / 2, 1180); ctx.scale(sc, sc); ctx.translate(-W / 2, -1180);
    ctx.globalAlpha = a * fade;
    txt('A SYSTEM IS', L.x2, 1240, { ...o, size: L.s2, c: C.y, glow: 50 });
    ctx.restore();
    // the full stop (lives on into the brand reveal)
    if (t < 51.3) { ctx.save(); ctx.translate(W / 2, 1180); ctx.scale(sc, sc); ctx.translate(-W / 2, -1180); ctx.globalAlpha = a; ctx.beginPath(); ctx.arc(L.dotX, L.dotY, L.dotR, 0, 6.283); ctx.fillStyle = C.y; ctx.shadowColor = rgba(YR, .8); ctx.shadowBlur = 40; ctx.fill(); ctx.restore(); }
  }
}

// ═══ SCENE 06 — BRAND ════════════════════════════════════════════
const BR = { lineY: 1000, base: 960 };
let markLayout = null;
function markL() {
  if (markLayout) return markLayout;
  const oA = { w: 900, track: -.02, f: FD }, oB = { w: 300, track: -.02, f: FD };
  const sA = measure('LOKA', { ...oA, size: 100 }), sB = measure('DIGITAL', { ...oB, size: 100 });
  const size = Math.floor(800 * 100 / (sA + sB + 2));
  const chars = []; let x = (W - (sA + sB + 2) * size / 100) / 2;
  const push = (str, o) => { ctx.save(); setFont({ ...o, size }); for (let i = 0; i < str.length; i++) { const w = ctx.measureText(str[i]).width; chars.push({ ch: str[i], x, o: { ...o, size } }); x += w; } ctx.restore(); };
  push('LOKA', oA); x += size * .02; push('DIGITAL', oB);
  return (markLayout = { size, chars, cx: W / 2 });
}
function drawMark(t, a = 1, mirror = false) {
  const M = markL();
  const tr = 1 + .14 * (1 - E.o5(P(t, 52.6, 54.6)));
  M.chars.forEach((c, i) => {
    const lp = E.ox(P(t, 52.62 + i * .045, 53.25 + i * .045)); if (lp <= 0) return;
    const x = M.cx + (c.x - M.cx) * tr;
    const y = BR.base + (1 - lp) * M.size * 1.05;
    txt(c.ch, x, y, { ...c.o, track: 0, c: C.white, a });
  });
}
function sBrand(t) {
  if (t < 51.3) return;
  const L = sysL();
  // the dot travels to centre and becomes the signal line
  const mv = E.io3(P(t, 51.3, 52.1));
  const dx = lerp(L.dotX, W / 2, mv), dy = lerp(L.dotY, BR.lineY, mv);
  const ext = E.iox(P(t, 52.05, 52.75));
  const shrink = E.io3(P(t, 54.2, 54.9));
  const halfW = lerp(lerp(L.dotR, 400, ext), 45, shrink), halfH = lerp(L.dotR, 2, Math.min(1, ext * 1.4));
  // bloom light behind mark
  const bl = E.o3(P(t, 52.3, 53.6)) * (1 - P(t, 58.4, 59));
  if (bl > 0) {
    const g = ctx.createRadialGradient(W / 2, BR.lineY, 0, W / 2, BR.lineY, 900);
    g.addColorStop(0, `rgba(110,50,230,${.45 * bl})`); g.addColorStop(.5, `rgba(60,20,140,${.18 * bl})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  const fadeEnd = 1 - P(t, 58.35, 58.95);
  // wordmark (clipped above line) + reflection
  if (t >= 52.6) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, BR.lineY - 6); ctx.clip(); drawMark(t, fadeEnd); ctx.restore();
    // mirrored floor reflection, alpha-masked (no overlay band)
    tmpX.setTransform(1, 0, 0, 1, 0, 0); tmpX.globalCompositeOperation = 'source-over'; tmpX.clearRect(0, 0, W, H);
    { const sx = ctx; ctx = tmpX; ctx.save(); ctx.translate(0, BR.lineY * 2 + 6); ctx.scale(1, -1); drawMark(t, 1); ctx.restore(); ctx = sx; }
    tmpX.globalCompositeOperation = 'destination-in';
    const mg = tmpX.createLinearGradient(0, BR.lineY + 6, 0, BR.lineY + 120); mg.addColorStop(0, 'rgba(0,0,0,1)'); mg.addColorStop(1, 'rgba(0,0,0,0)');
    tmpX.fillStyle = mg; tmpX.fillRect(0, 0, W, H); tmpX.globalCompositeOperation = 'source-over'; tmpX.clearRect(0, 0, W, BR.lineY + 6);
    ctx.save(); ctx.globalAlpha = .16 * fadeEnd; ctx.drawImage(tmpC, 0, 0); ctx.restore();
    // gleam sweep across the mark
    const gp = P(t, 55.0, 56.2);
    if (gp > 0 && gp < 1) {
      tmpX.setTransform(1, 0, 0, 1, 0, 0); tmpX.clearRect(0, 0, W, H);
      const sx = ctx; ctx = tmpX; drawMark(t, 1); ctx = sx;
      tmpX.globalCompositeOperation = 'source-atop';
      const gx = lerp(-300, W + 300, E.io3(gp));
      const gg = tmpX.createLinearGradient(gx - 160, 0, gx + 160, 0); gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(.5, 'rgba(255,255,240,.95)'); gg.addColorStop(1, 'rgba(255,255,255,0)');
      tmpX.fillStyle = gg; tmpX.fillRect(0, 0, W, H); tmpX.globalCompositeOperation = 'source-over';
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, BR.lineY - 6); ctx.clip(); ctx.globalAlpha = .8; ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(tmpC, 0, 0); ctx.restore();
    }
  }
  // line / dot
  ctx.save(); ctx.globalAlpha = fadeEnd; ctx.shadowColor = rgba(YR, .9); ctx.shadowBlur = 30; ctx.fillStyle = C.y;
  if (ext <= 0) { ctx.beginPath(); ctx.arc(dx, dy, L.dotR, 0, 6.283); ctx.fill(); }
  else { rr(dx - halfW, dy - halfH, halfW * 2, halfH * 2, Math.min(halfH, 999)); ctx.fill(); }
  ctx.restore();
  // tagline
  const to = { size: 38, w: 400, f: FT, track: -.005, c: C.mist, align: 'center' };
  ctx.save(); ctx.globalAlpha = fadeEnd;
  rev('Content + Ads Strategies', W / 2, BR.lineY + 110, to, P(t, 54.6, 55.1));
  rev('Based on Niche Audience Insights and Data.', W / 2, BR.lineY + 162, to, P(t, 54.75, 55.25));
  label('VIRAL IS NOT A STRATEGY. A SYSTEM IS.', W / 2, 1600, { size: 18, align: 'center', c: C.grey, a: P(t, 56.0, 56.6) });
  ctx.restore();
}

// ─── Camera, post ─────────────────────────────────────────────────
function camera(t) {
  let sx = 0, sy = 0, z = 1, rot = 0;
  for (const [ti, amp, zk] of IMPACTS) {
    const d = t - ti; if (d < 0 || d > 1.2) continue;
    const e = Math.exp(-d * 11);
    sx += Math.sin(d * 95 + ti) * amp * e; sy += Math.cos(d * 83 + ti * 2) * amp * e; z += zk * Math.exp(-d * 7); rot += Math.sin(d * 70) * .002 * amp * e;
  }
  // gentle drift
  z += .012 * Math.sin(t * .4);
  return { sx, sy, z, rot };
}
function post(t, f) {
  // bloom
  let bl = .20;
  for (const [ti, , , fl] of IMPACTS) { const d = t - ti; if (d >= 0 && d < 1.5) bl += fl * 1.2 * Math.exp(-d * 4); }
  bloomX.filter = 'blur(10px)'; bloomX.clearRect(0, 0, 270, 480); bloomX.drawImage(cv, 0, 0, 270, 480); bloomX.filter = 'none';
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = Math.min(.9, bl); ctx.drawImage(bloomC, 0, 0, W, H); ctx.restore();
  // glitch
  for (const [ti, dur, amt] of GLITCH) {
    const d = t - ti; if (d < 0 || d > dur) continue;
    tmpX.setTransform(1, 0, 0, 1, 0, 0); tmpX.globalCompositeOperation = 'source-over'; tmpX.clearRect(0, 0, W, H); tmpX.drawImage(cv, 0, 0);
    for (let k = 0; k < 14; k++) {
      const y = h3(f, k, 1) * H, hh = 8 + h3(f, k, 2) * 90, dx = (h3(f, k, 3) - .5) * 160 * amt;
      ctx.drawImage(tmpC, 0, y, W, hh, dx, y, W, hh);
    }
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = .35 * amt; ctx.drawImage(tmpC, 10 * amt, 0); ctx.restore();
    for (let k = 0; k < 4; k++) { ctx.fillStyle = k % 2 ? rgba(YR, .5) : 'rgba(123,60,240,.6)'; ctx.fillRect(h3(f, k, 5) * W, h3(f, k, 6) * H, 60 + h3(f, k, 7) * 400, 3 + h3(f, k, 8) * 8); }
  }
  // flash
  let fl = 0; for (const [ti, , , a] of IMPACTS) { const d = t - ti; if (d >= 0 && d < .5) fl += a * Math.exp(-d * 14); }
  if (fl > .005) { ctx.fillStyle = `rgba(235,225,255,${Math.min(.6, fl)})`; ctx.fillRect(0, 0, W, H); }
  ctx.drawImage(vignette, 0, 0);
  // grain
  ctx.save(); ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .16; ctx.imageSmoothingEnabled = false;
  const g = grains[f % grains.length]; const ox = h3(f, 1) * 40, oy = h3(f, 2) * 40;
  ctx.drawImage(g, -ox, -oy, W + 80, H + 80); ctx.restore();
}

// ─── Frame ────────────────────────────────────────────────────────
function renderFrame(t) {
  const f = Math.round(t * FPS);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.filter = 'none'; ctx.shadowBlur = 0;
  background(t);
  const cam = camera(t);
  ctx.save();
  ctx.translate(W / 2 + cam.sx, H / 2 + cam.sy); ctx.rotate(cam.rot); ctx.scale(cam.z, cam.z); ctx.translate(-W / 2, -H / 2);
  sHook(t); sStorm(t); sStop(t); sStatement(t);
  sChart(t); sDiag(t); sNoise(t);
  sRail(t); sStages(t); sOverview(t);
  sPhilo(t); sViral(t); sBrand(t);
  ctx.restore();
  post(t, f);
}

window.renderFrame = renderFrame;
window.READY = false;
(async () => {
  const loads = [];
  for (const w of [300, 400, 500, 600, 700, 800, 900]) { loads.push(document.fonts.load(`${w} 100px "Inter Display"`)); loads.push(document.fonts.load(`${w} 100px "Inter"`)); }
  await Promise.all(loads);
  initAssets();
  window.READY = true;
})();
