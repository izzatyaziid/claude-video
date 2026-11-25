// LokaDigital 2D kit (ES module): palette, easing, typography, Signal Line, bloom, grain.
export const W = 1080, H = 1920;
export const C = { ink: '#05030A', p1: '#602AC8', p2: '#301270', y: '#E8FF2B', lav: '#AB94FF', mist: '#D4CAF2', grey: '#7C7396', white: '#F4F1FF' };
export function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
export const cl = x => Math.max(0, Math.min(1, x)), P = (t, a, b) => cl((t - a) / (b - a)), lerp = (a, b, u) => a + (b - a) * u;
export const eo = x => 1 - Math.pow(1 - cl(x), 3), ei = x => Math.pow(cl(x), 3), eio = x => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }, ex = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * cl(x));
export const back = x => { x = cl(x); const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
export function hexA(h, a) { const n = parseInt(h.slice(1), 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; }
export function mix(h1, h2, t) { const a = parseInt(h1.slice(1), 16), b = parseInt(h2.slice(1), 16); const f = s => Math.round(((a >> s) & 255) * (1 - t) + ((b >> s) & 255) * t); return '#' + [f(16), f(8), f(0)].map(v => v.toString(16).padStart(2, '0')).join(''); }
export function mk(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }
export const FD = (w, s) => `${w} ${s}px "Inter Display"`, FM = (w, s) => `${w} ${s}px JBM`;
export async function loadFonts() { for (const f of ['800 100px "Inter Display"', '700 100px "Inter Display"', '600 50px "Inter Display"', '500 50px "Inter Display"', '600 20px JBM', '400 20px JBM']) await document.fonts.load(f); }
export function tw(x, s, font, ls) { x.save(); x.font = font; x.letterSpacing = ls || '0px'; const m = x.measureText(s).width; x.restore(); return m; }
// words: [[text, color, glow]]; p: masked-rise in (0..1); out: exit (0..1)
export function line(x, g, words, X, Y, size, weight, o = {}) {
  const p = o.p == null ? 1 : o.p, out = o.out || 0; if (p <= 0 || out >= 1) return null;
  const font = FD(weight, size), ls = o.ls || `${-size * 0.035}px`;
  const dy = (1 - eo(p)) * size * 0.95 - eo(out) * size * 1.4, alpha = (o.alpha == null ? 1 : o.alpha) * (1 - out);
  const total = words.reduce((a, w) => a + tw(x, w[0], font, ls), 0); let cx = o.align === 'center' ? X - total / 2 : (o.align === 'right' ? X - total : X); const x0 = cx;
  for (const [s, col, glow] of words) { for (const L of glow && g ? [x, g] : [x]) { L.save(); L.font = font; L.letterSpacing = ls; L.globalAlpha = alpha;
      if (p < 1) { L.beginPath(); L.rect(cx - 40, Y - size * 1.05, 4000, size * 1.34); L.clip(); }
      L.fillStyle = col; L.fillText(s, cx, Y + dy); L.restore(); }
    cx += tw(x, s, font, ls); }
  return { x0, w: cx - x0 };
}
export function mono(x, s, X, Y, size, col, o = {}) { const p = o.p == null ? 1 : o.p; const n = Math.floor(s.length * cl(p)); if (n <= 0) return; x.save(); x.font = FM(o.w || 600, size); x.letterSpacing = o.ls || `${size * 0.22}px`; x.textAlign = o.align || 'left'; x.globalAlpha = o.alpha == null ? 1 : o.alpha; x.fillStyle = col; x.fillText(s.slice(0, n), X, Y); x.restore(); }
export function flare(x, X, Y, k, streak = true) { let gr = x.createRadialGradient(X, Y, 0, X, Y, 26 * k); gr.addColorStop(0, 'rgba(255,255,245,1)'); gr.addColorStop(.25, hexA(C.y, .9)); gr.addColorStop(1, hexA(C.y, 0)); x.fillStyle = gr; x.beginPath(); x.arc(X, Y, 26 * k, 0, 7); x.fill();
  if (!streak) return; x.save(); x.translate(X, Y); x.scale(1, .018); gr = x.createRadialGradient(0, 0, 0, 0, 0, 380 * k); gr.addColorStop(0, hexA('#FFFFF0', .9)); gr.addColorStop(.15, hexA(C.y, .45)); gr.addColorStop(1, hexA(C.y, 0)); x.fillStyle = gr; x.beginPath(); x.arc(0, 0, 380 * k, 0, 7); x.fill(); x.restore(); }
export function catmull(pts, seg) { const out = []; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)]; for (let t = 0; t < seg; t++) { const u = t / seg, u2 = u * u, u3 = u2 * u;
  out.push([.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3), .5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)]); } } out.push(pts[pts.length - 1]); return out; }
export function sline(x, pts, prog, o = {}) { const PP = catmull(pts, 20); const n = Math.max(2, Math.floor(PP.length * cl(prog))); const w = o.w || 3, a = o.alpha == null ? 1 : o.alpha;
  x.lineCap = 'round'; x.lineJoin = 'round'; x.strokeStyle = hexA(o.col || C.y, a); x.lineWidth = w * 1.8; x.beginPath(); for (let i = 0; i < n; i++) i ? x.lineTo(PP[i][0], PP[i][1]) : x.moveTo(PP[i][0], PP[i][1]); x.stroke();
  if (!o.noCore) { x.strokeStyle = hexA('#FFFFF0', .9 * a); x.lineWidth = w * .55; x.stroke(); }
  const h = PP[n - 1]; if (o.head !== false && prog > 0.01 && (prog < 0.999 || o.headAlways)) flare(x, h[0], h[1], o.flare || .55, o.streak !== false); return { head: h, pts: PP }; }
export function uline(x, g, X, Y, w, p) { if (p <= 0) return; const e = X + w * eo(p); for (const L of [x, g]) { L.strokeStyle = C.y; L.lineWidth = 7; L.beginPath(); L.moveTo(X, Y); L.lineTo(e, Y); L.stroke(); } if (p < 1) flare(g, e, Y, .5); }
export function rrect(x, X, Y, w, h, r) { x.beginPath(); x.moveTo(X + r, Y); x.arcTo(X + w, Y, X + w, Y + h, r); x.arcTo(X + w, Y + h, X, Y + h, r); x.arcTo(X, Y + h, X, Y, r); x.arcTo(X, Y, X + w, Y, r); x.closePath(); }
export class Post {   // bloom + vignette + grain on the output canvas
  constructor(out) { this.out = out; this.x = out.getContext('2d'); [this.GL, this.g] = mk(W, H); [this.SM, this.sm] = mk(270, 480); [this.V, this.v] = mk(W, H);
    const gr = this.v.createRadialGradient(W / 2, H * .5, H * .25, W / 2, H * .5, H * .78); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.75)'); this.v.fillStyle = gr; this.v.fillRect(0, 0, W, H);
    this.grain = []; for (let k = 0; k < 4; k++) { const [c, x] = mk(540, 960); const d = x.createImageData(540, 960); const r = rng(900 + k); for (let i = 0; i < d.data.length; i += 4) { const q = 128 + (r() + r() + r() - 1.5) * 90; d.data[i] = d.data[i + 1] = d.data[i + 2] = q; d.data[i + 3] = 255; } x.putImageData(d, 0, 0); this.grain.push(c); } }
  begin() { this.g.setTransform(1, 0, 0, 1, 0, 0); this.g.clearRect(0, 0, W, H); }
  bloom(a1 = .55, a2 = .6) { const { x, sm, SM, GL } = this; sm.clearRect(0, 0, 270, 480); sm.filter = 'blur(10px)'; sm.drawImage(GL, 0, 0, 270, 480); sm.filter = 'none';
    x.save(); x.globalCompositeOperation = 'lighter'; x.globalAlpha = a1; x.drawImage(SM, 0, 0, W, H); x.globalAlpha = 1; x.drawImage(GL, 0, 0); x.restore();
    sm.clearRect(0, 0, 270, 480); sm.filter = 'blur(3px)'; sm.drawImage(GL, 0, 0, 270, 480); sm.filter = 'none'; x.save(); x.globalCompositeOperation = 'lighter'; x.globalAlpha = a2 * .6; x.drawImage(SM, 0, 0, W, H); x.restore(); }
  finish(f, vig = 1) { const x = this.x; x.save(); x.globalAlpha = vig; x.drawImage(this.V, 0, 0); x.restore(); x.save(); x.globalCompositeOperation = 'overlay'; x.globalAlpha = .1; x.drawImage(this.grain[f % 4], 0, 0, W, H); x.restore(); }
}
