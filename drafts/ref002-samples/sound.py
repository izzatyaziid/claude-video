"""Music bed + SFX for the REF-002 drafts, synthesised with numpy (LokaDigital default: procedural score, no licensed music).
Writes assets/mix_A.wav (VO + ducked bed + SFX) and assets/mix_B.wav (bed + SFX, no VO), pre-loudness.
Usage: python -I sound.py <project_dir>   then loudness-normalise with ffmpeg (see make.sh)."""
import sys, os, json, wave
import numpy as np

root = sys.argv[1]
sys.path.insert(0, root)
from build import scenes, LINES, DUR  # same timeline as the picture

SR = 48000; N = int(SR * DUR) + SR
rng = np.random.default_rng(3)
def T(n): return np.arange(n) / SR
def at(buf, sig, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[: j - i] * g
def env(n, a=0.005, d=0.3):
    t = T(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[f > fc] *= np.exp(-(f[f > fc] - fc) / (fc * .3)); return np.fft.irfft(X, len(x))
def hz(m): return 440 * 2 ** ((m - 69) / 12)

bed = np.zeros(N); fx = np.zeros(N)
BPM = 96; B = 60 / BPM
# chord loop (A minor -> F -> C -> G), pads + sub
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [52, 55, 60]), (55, [55, 59, 62])]
bar = 4 * B; t0 = 0.0; k = 0
while t0 < DUR:
    root_n, ch = prog[k % 4]; n = int(bar * SR); t = T(n)
    pad = sum(np.sin(2 * np.pi * hz(m) * t + .3 * np.sin(2 * np.pi * .4 * t)) for m in ch) / 3
    pad = lp(pad * np.minimum(1, t / .8) * np.minimum(1, (bar - t) / .6), 1800)
    at(bed, pad, t0, .10)
    sub = np.sin(2 * np.pi * hz(root_n - 24) * t) * np.minimum(1, t / .05) * np.exp(-t / 2.5)
    at(bed, sub, t0, .22)
    t0 += bar; k += 1
# pulse: kick on 1 and 3 after the hook, soft hats on 8ths
def kick():
    n = int(.35 * SR); t = T(n); f = 45 + 90 * np.exp(-t / .04); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .16)
def hat():
    n = int(.05 * SR); return lp(rng.standard_normal(n), 9000) * env(n, .0005, .012)
start_pulse = scenes[1]["start"]
t = start_pulse
while t < DUR - 1.0:
    beat = round((t - start_pulse) / B)
    if beat % 2 == 0: at(bed, kick(), t, .45)
    at(bed, hat(), t + B / 2, .05)
    t += B
# SFX
def whoosh(d=.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n); tt = T(n)
    fc = np.linspace(300, 5000, n) if up else np.linspace(5000, 300, n)
    y = np.zeros(n); a = 0
    for i in range(0, n, 256):
        c = fc[i]; al = 1 - np.exp(-2 * np.pi * c / SR)
        seg = x[i:i + 256]; o = np.empty_like(seg)
        for j, v in enumerate(seg): a += al * (v - a); o[j] = a
        y[i:i + 256] = o
    return y * np.sin(np.pi * tt / d) ** 2
def pop(f=900):
    n = int(.09 * SR); t = T(n); return np.sin(2 * np.pi * f * t * (1 + .6 * np.exp(-t / .01))) * env(n, .001, .03)
def tick():
    n = int(.03 * SR); return lp(rng.standard_normal(n), 6000) * env(n, .0005, .005)
def ping(f):
    n = int(.6 * SR); t = T(n); return (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .002, .18)
def riser(d):
    n = int(d * SR); t = T(n); return lp(rng.standard_normal(n), 6000) * (t / d) ** 2.2 * .6 + np.sin(2 * np.pi * np.cumsum(200 + 600 * (t / d) ** 2) / SR) * (t / d) ** 2 * .25
def impact():
    n = int(1.6 * SR); t = T(n); f = 38 + 60 * np.exp(-t / .06); return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .5) + lp(rng.standard_normal(n), 1200) * env(n, .001, .08) * .4
W = [whoosh(.42, True), whoosh(.5, True), whoosh(.38, False)]
sc = {s["id"]: s for s in scenes}
for i, s in enumerate(scenes[1:]):
    at(fx, W[i % 3], s["start"] - .2, .35)
p = sc["posts"]["start"] + .25
for i in range(9): at(fx, pop(700 + 40 * i), p + .09 * i + .01, .18)
s = sc["shop"]
tt = s["start"] + .2
while tt < s["end"] - .3: at(fx, tick(), tt, .25); tt += .5
for i in range(8): at(fx, pop(500 + 60 * i), sc["views"]["start"] + .3 + .08 * i + .02, .14)
l4 = next(l for l in LINES if l["id"] == "s4"); at(fx, pop(300), l4["start"] + .22, .35)
for i in range(5): at(fx, pop(420), sc["budget"]["start"] + .3 + .06 * i, .1)
at(fx, whoosh(.9, False), sc["budget"]["start"] + .4, .18)
for i in range(30): at(fx, pop(1200 + 25 * (i % 9)), sc["crowd"]["start"] + .2 + .028 * i, .05)
k = sc["cari"]["start"]
at(fx, whoosh(.9, True), k + .6, .2); at(fx, whoosh(.6, False), k + 1.55, .15)
for i in range(8): at(fx, ping(hz(76 + [0, 3, 7, 10, 12, 15, 19, 22][i])), k + 1.6 + .05 * i + .02, .08)
at(fx, whoosh(.6, True), sc["cakap"]["start"], .2)
tt = sc["cakap"]["start"] + .35
for i in range(12): at(fx, tick(), tt + i * .085, .2)
for i in range(3): at(fx, pop(600 + 200 * i), sc["sambung"]["start"] + .15 + .28 * i + .02, .3)
cta = sc["cta"]["start"]
at(fx, riser(1.4), cta - 1.4, .35); at(fx, impact(), cta + .03, .7)
# end: fade bed on a bar line
fade = np.ones(N); e0 = int((DUR - 1.4) * SR); fade[e0:] = np.linspace(1, 0, N - e0) ** 2
bed *= fade

def write(path, x):
    x = x[: int(DUR * SR)]; x = x / (np.abs(x).max() + 1e-9) * .89
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())

# A: VO + ducked bed
with wave.open(os.path.join(root, "assets", "vo.wav")) as w:
    vo = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
venv = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); duck = 1 - .55 * np.clip(venv / (venv.max() * .3), 0, 1)
write(os.path.join(root, "assets", "mix_A_raw.wav"), vo * 1.0 + bed * duck * .55 + fx * .7)
write(os.path.join(root, "assets", "mix_B_raw.wav"), bed * 1.0 + fx * .9)
print("ok", DUR)
