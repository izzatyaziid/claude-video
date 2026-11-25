"""Shared kit for the 10 LokaDigital style previews (60 s each, 1080x1920, no VO).
Each style module defines: NAME, SLUG, BPM, PRESET, body (html), js (GSAP timeline body), cues (sfx list).
make.py turns a style into a HyperFrames project + music/SFX mix.
Brand tokens come from the approved Marketing Package sheet (lokadigital-package/package.html)."""
import os, json, shutil, wave
import numpy as np

DUR = 60.0
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))

TOKENS = """
  :root { --ink:#07040C; --p1:#46096B; --p2:#240538; --mag:#B800F0; --g:#B4FF39; --mist:#D9D0F0; --grey:#8C83A6;
          --line:rgba(255,255,255,.14); --glass:rgba(255,255,255,.045); }
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1080px; height:1920px; overflow:hidden; background:var(--ink); }
  #root { position:relative; width:1080px; height:1920px; overflow:hidden; background:var(--ink); font-family:'Inter',sans-serif; color:#fff; }
  .bgfill { position:absolute; inset:0; background:radial-gradient(120% 45% at 100% 0%, #46096B 0%, transparent 62%), radial-gradient(90% 35% at 0% 100%, #240538 0%, transparent 70%), var(--ink); }
  .grain { position:absolute; inset:0; opacity:.06; pointer-events:none; mix-blend-mode:overlay;
           background-image:repeating-radial-gradient(circle at 17% 32%, #fff 0 1px, transparent 1px 3px), repeating-radial-gradient(circle at 71% 63%, #fff 0 1px, transparent 1px 4px); }
  .vig { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse at 50% 45%, transparent 50%, rgba(0,0,0,.72) 100%); }
  .logo { position:absolute; left:96px; top:262px; width:120px; height:120px; mix-blend-mode:screen; }
  .pill { position:absolute; right:120px; top:296px; font:600 28px 'Inter'; letter-spacing:.22em; color:var(--g); border:2px solid var(--g); padding:12px 24px; border-radius:99px; }
  .lab { font:700 28px 'Inter'; letter-spacing:.28em; color:var(--mist); text-transform:uppercase; }
  .h { font:800 96px/0.98 'Inter'; letter-spacing:-.04em; }
  .gr { color:var(--g); }
  .glass { background:var(--glass); border:2px solid var(--line); border-radius:28px; box-shadow:0 40px 110px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.08); }
  .ctablock { background:var(--g); color:var(--ink); border-radius:26px; padding:34px 40px; display:flex; justify-content:space-between; align-items:center; }
  .ctablock label { display:block; font:800 26px 'Inter'; letter-spacing:.24em; }
  .ctablock small { display:block; margin-top:8px; font:600 26px 'Inter'; opacity:.75; }
  .ctablock b { font:900 50px 'Inter'; letter-spacing:-.03em; white-space:nowrap; }
"""

def head(title, css):
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{TOKENS}{css}</style>
  </head>
  <body>
"""

def page(style):
    D = DUR
    brand = "" if getattr(style, "NO_BRAND_CHROME", False) else f"""
      <img class="logo clip" id="logo" src="assets/logo.jpg" alt="LOKADIGITAL" data-start="0" data-duration="{D}" data-track-index="8">
      <div class="pill clip" id="pill" data-start="0" data-duration="{D}" data-track-index="8">{style.PILL}</div>"""
    return head(style.NAME, style.CSS) + f"""
    <div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1080" data-height="1920">
      <div class="bgfill clip" id="bgfill" data-start="0" data-duration="{D}" data-track-index="0"></div>
      {style.BODY}
      {brand}
      <div class="vig clip" id="vig" data-start="0" data-duration="{D}" data-track-index="9" data-layout-ignore></div>
      <div class="grain clip" id="grain" data-start="0" data-duration="{D}" data-track-index="9" data-layout-ignore></div>
      <audio id="mix" src="assets/mix.wav" class="clip" data-start="0" data-duration="{D}" data-track-index="10"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {style.JS}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""

# ---------------------------------------------------------------- audio
SR = 48000
def _t(n): return np.arange(n) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def _env(n, a=.005, d=.3):
    t = _t(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def _lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[f > fc] *= np.exp(-(f[f > fc] - fc) / (fc * .3)); return np.fft.irfft(X, len(x))
def _hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[f < fc] *= (f[f < fc] / fc) ** 2; return np.fft.irfft(X, len(x))

class Mix:
    def __init__(self, seed=1):
        self.N = int(SR * DUR); self.bed = np.zeros(self.N); self.fx = np.zeros(self.N); self.rng = np.random.default_rng(seed)
    def at(self, buf, sig, t, g=1.0):
        i = int(t * SR); j = min(self.N, i + len(sig))
        if 0 <= i < self.N: buf[i:j] += sig[: j - i] * g
    # instruments
    def kick(self, hard=False):
        n = int(.4 * SR); t = _t(n); f = 42 + (140 if hard else 90) * np.exp(-t / .035)
        return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .001, .2 if hard else .15) * (2.2 if hard else 1.2))
    def clap(self):
        n = int(.25 * SR); x = _hp(self.rng.standard_normal(n), 900); e = sum(_env(n, .001, .012) * (np.arange(n) >= int(k * SR)) for k in (0, .012, .024)) + _env(n, .001, .09) * .6
        return x * e * .5
    def hat(self, open_=False):
        n = int((.25 if open_ else .05) * SR); return _hp(self.rng.standard_normal(n), 7000) * _env(n, .0005, .08 if open_ else .012)
    def tone(self, f, d, kind="sine", a=.01, dec=None):
        n = int(d * SR); t = _t(n)
        if kind == "sine": x = np.sin(2 * np.pi * f * t)
        elif kind == "saw": x = _lp(2 * ((f * t) % 1) - 1, 2400)
        elif kind == "square": x = np.sign(np.sin(2 * np.pi * f * t)) * .5
        elif kind == "piano": x = sum(np.sin(2 * np.pi * f * k * t) * (.6 ** (k - 1)) for k in (1, 2, 3, 4))
        elif kind == "pluck": x = _lp(np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t), 3000)
        env = np.minimum(1, t / a) * (np.exp(-t / dec) if dec else np.minimum(1, (d - t) / .15).clip(0, 1))
        return x * env
    # sfx
    def whoosh(self, d=.45, up=True):
        n = int(d * SR); t = _t(n); x = self.rng.standard_normal(n)
        lo, hi = (_lp(x, 1200), _lp(x, 6000))
        mixw = t / d if up else 1 - t / d
        return (lo * (1 - mixw) + hi * mixw) * np.sin(np.pi * t / d) ** 2 * .8
    def pop(self, f=900):
        n = int(.09 * SR); t = _t(n); return np.sin(2 * np.pi * f * t * (1 + .6 * np.exp(-t / .01))) * _env(n, .001, .03)
    def tick(self):
        n = int(.03 * SR); return _lp(self.rng.standard_normal(n), 6000) * _env(n, .0005, .005)
    def thud(self):
        n = int(.7 * SR); t = _t(n); f = 40 + 70 * np.exp(-t / .05); return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .001, .25)
    def riser(self, d):
        n = int(d * SR); t = _t(n); return _lp(self.rng.standard_normal(n), 6000) * (t / d) ** 2.2 * .5 + np.sin(2 * np.pi * np.cumsum(200 + 700 * (t / d) ** 2) / SR) * (t / d) ** 2 * .2
    def impact(self):
        n = int(1.8 * SR); t = _t(n); f = 36 + 64 * np.exp(-t / .06)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .001, .55) + _lp(self.rng.standard_normal(n), 1500) * _env(n, .001, .09) * .45
    def notif(self):
        return np.concatenate([self.tone(hz(84), .09, "sine", .002, .05), self.tone(hz(91), .2, "sine", .002, .08)]) * .6
    def stamp(self):
        n = int(.35 * SR); return _lp(self.rng.standard_normal(n), 2500) * _env(n, .001, .03) + self.thud()[:n] * .7
    def type_(self):
        n = int(.04 * SR); return _hp(self.rng.standard_normal(n), 2000) * _env(n, .0005, .006)
    def glitch(self, d=.15):
        n = int(d * SR); x = np.sign(self.rng.standard_normal(n // 200 + 1)).repeat(200)[:n]; return x * .3
    def coin(self):
        return np.concatenate([self.tone(hz(83), .07, "square", .001, .05), self.tone(hz(88), .25, "square", .001, .12)]) * .4
    def paper(self):
        n = int(.22 * SR); return _hp(self.rng.standard_normal(n), 1500) * (self.rng.random(n) > .7) * _env(n, .002, .08) * .8

    def score(self, bpm, prog, kind="pad", drums="four", start=0.0, end=None, lead=None, swing=0.0):
        """prog: list of (root_midi, [chord midis]) per bar. drums: four|half|trap|none|chip"""
        end = end or DUR - 1.0; B = 60 / bpm; bar = 4 * B; t0 = start; k = 0
        while t0 < end:
            r, ch = prog[k % len(prog)]
            if kind == "pad":
                n = int(bar * SR); t = _t(n)
                pad = sum(np.sin(2 * np.pi * hz(m) * t + .3 * np.sin(2 * np.pi * .4 * t)) for m in ch) / len(ch)
                self.at(self.bed, _lp(pad * np.minimum(1, t / .8) * np.minimum(1, (bar - t) / .6), 1800), t0, .12)
            elif kind in ("piano", "pluck", "square"):
                for b in range(4):
                    for i, m in enumerate(ch):
                        self.at(self.bed, self.tone(hz(m + 12 * (kind == "pluck")), B * 1.2, kind, .003, .5 if kind == "piano" else .18), t0 + b * B + i * .012 + (swing * B if b % 2 else 0), .07 if kind != "square" else .05)
            self.at(self.bed, self.tone(hz(r - 24), bar, "sine", .02), t0, .2)
            for b in range(8 if drums != "half" else 4):
                tb = t0 + b * (B / 2 if drums != "half" else B) + (swing * B / 2 if b % 2 else 0)
                if drums in ("four", "chip") and b % 2 == 0: self.at(self.bed, self.kick(drums == "four"), tb, .5)
                if drums == "half" and b % 2 == 0: self.at(self.bed, self.kick(), tb, .45)
                if drums == "trap" and b in (0, 3, 6): self.at(self.bed, self.kick(True), tb, .5)
                if drums in ("four", "trap", "chip") and b in (2, 6): self.at(self.bed, self.clap(), tb, .35)
                if drums != "none": self.at(self.bed, self.hat(b % 4 == 3), tb + (B / 4 if drums == "half" else 0), .06)
            if lead:
                for b, m in enumerate(lead[k % len(lead)]):
                    if m: self.at(self.bed, self.tone(hz(m), B * .9, "square" if drums == "chip" else "pluck", .003, .2), t0 + b * B, .06)
            t0 += bar; k += 1

    def drone(self, f, start, end, g=.1):
        n = int((end - start) * SR); t = _t(n)
        x = sum(np.sin(2 * np.pi * f * m * t + np.sin(2 * np.pi * .2 * m * t)) / m for m in (1, 1.5, 2, 3))
        self.at(self.bed, _lp(x, 900) * np.minimum(1, t / 2) * np.minimum(1, (n / SR - t) / 1.5), start, g)

    def write(self, path):
        fade = np.ones(self.N); e0 = int((DUR - 1.5) * SR); fade[e0:] = np.linspace(1, 0, self.N - e0) ** 2
        x = self.bed * fade + self.fx * .9
        x = x / (np.abs(x).max() + 1e-9) * .89
        st = np.stack([x, x], 1)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
