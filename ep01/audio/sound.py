"""LOKADIGITAL EP01 — original score + sound design, synthesised from scratch (numpy only).
Every cue is locked to the same timeline constants as render/scene.js.
Usage: python3 sound.py out.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 59.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N); R = np.zeros(N)          # dry bus
RL = np.zeros(N); RR = np.zeros(N)        # reverb send
MUS_L = np.zeros(N); MUS_R = np.zeros(N)  # music bus (gets tape-stop + ducking)

def idx(t): return int(round(t * SR))
def tt(n): return np.arange(n) / SR

def add(sig, t0, gain=1.0, pan=0.0, rev=0.0, bus='fx'):
    """Mix mono or (2,n) signal at t0. pan -1..1 (equal power)."""
    i = idx(t0)
    if sig.ndim == 1: sl, sr_ = sig, sig
    else: sl, sr_ = sig[0], sig[1]
    n = len(sl)
    if i >= N or i + n <= 0: return
    a, b = max(0, i), min(N, i + n)
    s0 = a - i
    th = (pan + 1) * np.pi / 4
    gl, gr = np.cos(th) * gain * 1.414, np.sin(th) * gain * 1.414
    if bus == 'mus':
        MUS_L[a:b] += sl[s0:s0 + b - a] * gl; MUS_R[a:b] += sr_[s0:s0 + b - a] * gr
    else:
        L[a:b] += sl[s0:s0 + b - a] * gl; R[a:b] += sr_[s0:s0 + b - a] * gr
    if rev:
        RL[a:b] += sl[s0:s0 + b - a] * gl * rev; RR[a:b] += sr_[s0:s0 + b - a] * gr * rev

def fft_filter(x, lo=0, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))

def noise(n): return rng.standard_normal(n)

def sweep_noise(dur, f0, f1, q=0.5, curve=1.0):
    """Band-pass noise whose centre sweeps f0->f1 (overlap-add STFT filtering)."""
    n = idx(dur); x = noise(n + 4096); out = np.zeros(n + 4096)
    hop, win = 512, 2048; w = np.hanning(win)
    f = np.fft.rfftfreq(win, 1 / SR)
    for s in range(0, n, hop):
        p = (s / n) ** curve
        fc = f0 * (f1 / f0) ** p
        bw = fc * q
        m = np.exp(-0.5 * ((f - fc) / bw) ** 2)
        seg = x[s:s + win] * w
        out[s:s + win] += np.fft.irfft(np.fft.rfft(seg) * m, win) * w
    return out[:n] / (np.max(np.abs(out[:n])) + 1e-9)

def env_ad(n, a, d, shape=1.0):
    t = tt(n); e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
    return e ** shape

# ─── Instruments ───────────────────────────────────────────────
def kick(amp=1.0, f0=130, f1=42, dec=0.32):
    n = idx(0.6); t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / dec)
    click = fft_filter(noise(n), 1500, 6000) * np.exp(-t * 300) * 0.25
    return np.tanh((s + click) * 1.6) * amp

def boom(amp=1.0, dur=3.5, f0=90, f1=30):
    n = idx(dur); t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dur * 0.33))
    body = fft_filter(noise(n), 30, 400) * np.exp(-t * 9) * 0.5
    snap = fft_filter(noise(n), 800, 9000) * np.exp(-t * 60) * 0.35
    return np.tanh((s * 1.2 + body + snap) * 1.4) * amp

def hat(amp=0.2, dec=0.03):
    n = idx(0.12); t = tt(n)
    return fft_filter(noise(n), 7000) * np.exp(-t / dec) * amp

def tick(amp=0.3, f=2400):
    n = idx(0.05); t = tt(n)
    return (np.sin(2 * np.pi * f * t) * 0.6 + fft_filter(noise(n), 3000) * 0.4) * np.exp(-t * 160) * amp

def ping(f, amp=0.25, dec=0.7):
    n = idx(dec * 4); t = tt(n)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.003 * t) + 0.12 * np.sin(2 * np.pi * f * 3.01 * t)
    return s * env_ad(n, 0.004, dec) * amp

def whoosh(dur=0.6, f0=300, f1=4000, amp=0.4, rev=False):
    s = sweep_noise(dur, f0, f1, 0.6, 0.8)
    n = len(s); e = np.sin(np.pi * np.minimum(1, np.arange(n) / n)) ** 1.5
    s = s * e * amp
    return s[::-1] if rev else s

def riser(dur, amp=0.4, f0=200, f1=6000):
    n = idx(dur); t = tt(n)
    s = sweep_noise(dur, f0, f1, 0.35, 1.6) * (t / dur) ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(110 * (1 + 3 * (t / dur) ** 2)) / SR) * (t / dur) ** 3 * 0.25
    return (s + tone) * amp

def glitch(dur=0.15, amp=0.5):
    n = idx(dur); x = noise(n)
    hold = rng.integers(8, 60)
    x = np.repeat(x[::hold], hold)[:n]
    x = np.round(x * 3) / 3
    gate = (np.sin(2 * np.pi * rng.uniform(30, 80) * tt(n)) > 0).astype(float)
    return fft_filter(x, 200) * gate * amp

def pad(dur, freqs, amp=0.15, att=1.5, rel=1.5, bright=0.35):
    n = idx(dur); t = tt(n); out = np.zeros((2, n))
    for ch, det in ((0, -1), (1, 1)):
        s = np.zeros(n)
        for f in freqs:
            for k, (hm, ha) in enumerate(((1, 1), (2, bright), (3, bright * 0.5), (4, bright * 0.25))):
                ff = f * hm * (1 + det * 0.0018 * (k + 1))
                s += ha * np.sin(2 * np.pi * ff * t + rng.uniform(0, 6.28))
        lfo = 1 + 0.12 * np.sin(2 * np.pi * 0.17 * t + ch)
        s *= lfo
        out[ch] = s
    e = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel)
    return out * np.clip(e, 0, 1) * amp / len(freqs)

def bass_note(f, dur, amp=0.35):
    n = idx(dur); t = tt(n)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)
    e = np.minimum(1, t / 0.008) * np.exp(-t / (dur * 0.8))
    return np.tanh(s * e * 1.3) * amp

def hz(m): return 440 * 2 ** ((m - 69) / 12)
D1, F1, A1, C2, Bb1, D2 = hz(26), hz(29), hz(33), hz(36), hz(34), hz(38)

# ─── Timeline (mirrors scene.js) ───────────────────────────────
SLAMS = [0.30, 0.62, 0.90, 1.12, 1.30, 1.45, 1.58]
FREEZE, CUT = 7.60, 7.85
STMT = [8.60, 9.30, 10.00]
STAGES = [26.0, 28.6, 31.2, 33.6, 36.0, 38.5]
PHILO = [43.1, 44.35, 45.45]
VIRAL, SYSTEM = 47.0, 49.3
BEAT = 0.5  # 120 bpm

# room tone
add(fft_filter(noise(N), 80, 900) * 0.004, 0)

# ── 01 HOOK ──
add(ping(hz(86), 0.05, 0.05), 0.0); add(ping(hz(86), 0.05, 0.05), 0.25)  # cursor blips
for i, s in enumerate(SLAMS):
    add(kick(0.9 if i in (0, 6) else 0.7, 150, 40, 0.35), s)
    add(fft_filter(noise(idx(0.25)), 1200, 8000) * env_ad(idx(0.25), 0.001, 0.05) * 0.35, s, pan=(-1) ** i * 0.3)
    add(glitch(0.06, 0.15), s + 0.02, pan=(-1) ** (i + 1) * 0.5)
add(boom(0.6, 2.0), SLAMS[0], rev=0.4)
add(boom(0.8, 2.2), SLAMS[6], rev=0.5)
add(glitch(0.12, 0.35), 1.72); add(glitch(0.1, 0.3), 1.80, pan=0.4)
# counter ticks follow the number roll (ease-out quart)
last = -1
for k in range(0, idx(0.8), idx(1 / 240)):
    u = min(1, k / idx(0.75)); v = int(1 + 364 * (1 - (1 - u) ** 4))
    if v // 6 != last: last = v // 6; add(tick(0.18, 2600 + v * 3), 1.9 + k / SR, pan=0.15)
add(ping(hz(81), 0.18, 0.5), 2.65, rev=0.6)
add(riser(1.3, 0.25, 300, 5000), 1.85)
add(whoosh(0.5, 3000, 300, 0.35), 2.85)

# ── 02 PROBLEM — the storm (music bus so it can tape-stop) ──
t0 = 3.0
add(pad(5.0, [D2 * 2, A1 * 2, F1 * 4], 0.22, 0.6, 0.3, 0.5), t0, bus='mus')
b = 0
t = t0
while t < FREEZE:
    u = (t - t0) / (FREEZE - t0)
    add(kick(0.55 + 0.25 * u, 120, 45, 0.25), t, bus='mus')
    add(bass_note(D1 * 2 if (b // 4) % 2 == 0 else F1 * 2, BEAT * 0.9, 0.22), t, bus='mus')
    for h in range(2 if u < 0.4 else 4):
        add(hat(0.08 + 0.08 * u), t + h * BEAT / (2 if u < 0.4 else 4), pan=0.3 * (-1) ** h, bus='mus')
    t += BEAT; b += 1
add(riser(FREEZE - 3.1, 0.45, 150, 7000), 3.1, bus='mus')
# notification blips (pentatonic) — same seeds/timing as the visual pills
penta = [74, 76, 79, 81, 83, 86, 88]
for k in range(30):
    tk = 3.05 + 4.5 * (k / 30) ** 0.62
    if tk < FREEZE:
        add(ping(hz(penta[(k * 3) % 7]), 0.07, 0.12), tk, pan=np.sin(k * 2.1) * 0.7, rev=0.3)
for s in (3.2, 4.68, 5.93):
    add(whoosh(0.45, 400, 5000, 0.22), s - 0.12, pan=-0.2)
add(kick(0.5), 5.93); add(ping(hz(62), 0.12, 0.6), 5.95, rev=0.5)
# hard stop
add(glitch(0.16, 0.6), FREEZE); add(boom(0.35, 1.2, 60, 25), FREEZE, rev=0.2)
add(fft_filter(noise(idx(0.06)), 2000) * 0.3, CUT - 0.02)

# ── statement ──
for i, s in enumerate(STMT):
    add(boom([0.85, 0.75, 1.0][i], 3.5), s, rev=0.55)
    add(fft_filter(noise(idx(0.4)), 2000, 12000) * env_ad(idx(0.4), 0.001, 0.08) * 0.25, s, rev=0.6)
add(pad(3.4, [D1 * 2, A1, D2], 0.18, 0.2, 0.8, 0.2), 8.6)
add(whoosh(0.5, 4000, 500, 0.25), 11.5)

# ── 03 INSIGHT ──
add(pad(8.8, [D2 * 2, F1 * 4, A1 * 4, C2 * 4], 0.16, 1.0, 1.0, 0.25), 12.0, bus='mus')
t = 12.0
while t < 20.5:
    add(bass_note(D1 * 2, BEAT * 1.8, 0.18), t, bus='mus')
    add(hat(0.05), t + BEAT, bus='mus'); add(tick(0.05, 3200), t + BEAT * 1.5, pan=0.5, bus='mus')
    t += BEAT * 2
# chart line tones
n = idx(1.55); tl = tt(n)
add(np.sin(2 * np.pi * np.cumsum(hz(67) * (1 + 0.5 * tl / 1.55)) / SR) * np.sin(np.pi * tl / 1.55) * 0.05, 12.35, pan=-0.3, rev=0.4)
n = idx(1.45); tl = tt(n)
add(np.sin(2 * np.pi * hz(62) * tl) * np.sin(np.pi * tl / 1.45) * 0.045, 13.15, pan=0.3, rev=0.4)
for s in (12.15, 13.25, 15.0):
    add(whoosh(0.35, 600, 4500, 0.15), s - 0.08)
add(boom(0.45, 2.5), 16.65, rev=0.5); add(ping(hz(74), 0.12, 0.8), 16.85, rev=0.6)
for i in range(3):
    add(tick(0.25, 1900), 17.75 + i * 0.65); add(ping(hz([69, 72, 76][i]), 0.08, 0.3), 17.77 + i * 0.65, rev=0.4)
add(whoosh(0.4, 5000, 400, 0.2), 20.25)
# noise section
n = idx(2.5); crackle = np.zeros(n)
for k in range(220):
    p = rng.integers(0, n - 400); crackle[p:p + 400] += noise(400) * np.exp(-np.arange(400) / 60) * rng.uniform(0.2, 1)
add(crackle * 0.12, 20.6, pan=0.2)
for k in range(10):
    add(glitch(rng.uniform(0.04, 0.12), 0.12), 20.7 + k * 0.23, pan=rng.uniform(-0.8, 0.8))
dis = pad(2.6, [hz(62), hz(63), hz(68), hz(69)], 0.1, 0.4, 0.3, 0.6)
add(dis, 20.6)
add(fft_filter(noise(idx(2.4)), 300, 6000) * np.linspace(0.02, 0.09, idx(2.4)), 20.6)
# collapse: reverse swell -> SIGNAL
add(whoosh(0.8, 200, 6000, 0.45, rev=True), 22.95)
add(boom(0.6, 3.0, 70, 30), 23.75, rev=0.5)
add(pad(2.0, [hz(74), hz(81), hz(86)], 0.11, 0.01, 1.2, 0.15), 23.75, rev=0.35)
add(whoosh(1.0, 800, 7000, 0.2), 23.85, pan=-0.6); add(whoosh(1.0, 7000, 800, 0.2), 24.35, pan=0.6)

# ── 04 STRATEGY — groove ──
add(whoosh(0.9, 300, 3000, 0.3), 25.0)
add(pad(16.2, [D2 * 2, A1 * 2, F1 * 4], 0.13, 1.0, 0.3, 0.3), 25.0, bus='mus')
prog = [D1, D1, Bb1 / 2 * 2, C2 / 2 * 2]   # Dm  Dm  Bb  C (bass roots)
t = 26.0; b = 0
while t < 42.95 - 1e-6:
    root = prog[(b // 8) % 4] * 2
    if t >= 41.0:
        add(kick(0.45, 125, 45, 0.28), t, bus='mus'); add(hat(0.06), t + BEAT / 2, bus='mus'); add(hat(0.05), t + BEAT / 4, bus='mus'); add(hat(0.05), t + BEAT * .75, bus='mus')
        t += BEAT; b += 1; continue
    add(kick(0.6, 125, 45, 0.28), t, bus='mus')
    add(bass_note(root, BEAT * 0.45, 0.22), t, bus='mus'); add(bass_note(root * (2 if b % 2 else 1), BEAT * 0.4, 0.14), t + BEAT / 2, bus='mus')
    add(hat(0.07), t + BEAT / 2, pan=0.35, bus='mus'); add(hat(0.035), t + BEAT * 0.75, pan=-0.35, bus='mus')
    if b % 2 == 1: add(fft_filter(noise(idx(0.18)), 900, 7000) * env_ad(idx(0.18), 0.001, 0.05) * 0.18, t, rev=0.3, bus='mus')
    t += BEAT; b += 1
stage_notes = [74, 76, 79, 81, 84, 86]
for i, s in enumerate(STAGES):
    add(whoosh(0.4, 500, 6000, 0.25), s - 0.15, pan=-0.3)
    add(ping(hz(stage_notes[i]), 0.16, 0.6), s + 0.05, rev=0.6)
    add(tick(0.2, 2200), s + 0.3)
# per-stage FX
add(sweep_noise(1.25, 600, 5000, 0.2) * np.hanning(idx(1.25)) * 0.12, 26.5)            # audit scan
for k in (1, 5, 9): add(tick(0.15, 3000), 26.5 + (k // 3 + 0.5) / 4.2 * 1.25)
add(tick(0.35, 1400), 28.6 + 1.3); add(ping(hz(86), 0.12, 0.3), 28.6 + 1.32, rev=0.5)      # lock
for i in range(3): add(whoosh(0.3, 800, 3000, 0.12), 31.2 + 0.2 + i * 0.14, pan=(i - 1) * 0.6)
n = idx(1.2); tl = tt(n)
add(np.sin(2 * np.pi * np.cumsum(hz(60) * (1 + tl)) / SR) * np.sin(np.pi * tl / 1.2) * 0.05, 33.85)
add(ping(hz(86), 0.2, 0.6), 33.6 + 1.5, rev=0.6); add(ping(hz(91), 0.12, 0.5), 33.6 + 1.55, rev=0.6)
for k in range(3): add(kick(0.25, 70, 38, 0.5), 36.3 + k * 1.11, rev=0.3)                # ad pulses
add(riser(1.4, 0.22, 300, 6000), 38.7)
# overview build
add(riser(2.0, 0.35, 200, 8000), 41.0)
for i in range(6): add(tick(0.22, 1800 + i * 250), 41.05 + i * 0.1)
for k in range(8): add(fft_filter(noise(idx(0.1)), 900, 6000) * env_ad(idx(0.1), 0.001, 0.03) * (0.06 + k * 0.02), 42.0 + k * 0.125)

# ── 05 IMPACT ──
add(pad(3.6, [D1 * 2, A1, D2, F1 * 2], 0.16, 0.05, 0.4, 0.3), 43.0, bus='mus')
for i, s in enumerate(PHILO):
    add(boom([0.55, 0.6, 0.8][i], 2.5), s, rev=0.45)
    add(ping(hz([74, 77, 81][i]), 0.12, 0.6), s + 0.02, rev=0.6)
add(whoosh(0.4, 5000, 400, 0.22), 46.3)
add(pad(2.4, [D1 * 2, A1 * 2], 0.12, 0.6, 0.6, 0.1), 46.6)
add(boom(0.5, 2.5), VIRAL, rev=0.45); add(kick(0.3), VIRAL + 0.25)
add(whoosh(0.55, 200, 7000, 0.5, rev=True), SYSTEM - 0.55)
add(riser(1.8, 0.2, 100, 3000), SYSTEM - 1.8)
add(boom(1.0, 4.0, 110, 28), SYSTEM, rev=0.7)
add(fft_filter(noise(idx(1.0)), 1500, 14000) * env_ad(idx(1.0), 0.001, 0.15) * 0.35, SYSTEM, rev=0.7)
add(pad(2.6, [hz(62), hz(69), hz(74), hz(77)], 0.13, 0.01, 1.4, 0.5), SYSTEM, rev=0.3)

# ── 06 BRAND ──
add(whoosh(0.8, 400, 2500, 0.15), 51.3)
n = idx(0.7); tl = tt(n)
add(np.sin(2 * np.pi * np.cumsum(hz(74) * (1 + 0.5 * tl / 0.7)) / SR) * np.sin(np.pi * tl / 0.7) * 0.06, 52.05, rev=0.6)
add(whoosh(0.7, 1500, 9000, 0.18), 52.05)
add(boom(0.7, 4.5, 80, 28), 52.6, rev=0.6)
add(pad(6.4, [hz(38), hz(50), hz(57), hz(62), hz(66)], 0.2, 0.8, 2.5, 0.25), 52.6, rev=0.25)   # D major resolve
for i in range(11): add(tick(0.06, 3000 + i * 120), 52.62 + i * 0.045, pan=(i - 5) / 6)
n = idx(1.2); tl = tt(n)
shim = sum(np.sin(2 * np.pi * f * tl) for f in (hz(98), hz(105), hz(110))) * np.sin(np.pi * tl / 1.2) ** 2 * 0.025
add(shim, 55.0, rev=0.7)
add(ping(hz(86), 0.07, 0.8), 54.65, rev=0.7)

# ─── Music bus processing: tape-stop at the freeze + sidechain-ish ducking under impacts ───
i0, i1 = idx(FREEZE), idx(CUT)
for bus in (MUS_L, MUS_R):
    seg_len = i1 - i0
    rate = np.linspace(1, 0, seg_len) ** 1.3
    pos = i0 + np.cumsum(rate)
    bus[i0:i1] = np.interp(pos, np.arange(N), bus) * np.linspace(1, 0.2, seg_len)
    bus[i1:idx(8.6)] = 0
duck = np.ones(N)
for s in SLAMS + STMT + PHILO + [VIRAL, SYSTEM, 52.6, 23.75]:
    a = idx(s); n = min(idx(0.6), N - a); duck[a:a + n] = np.minimum(duck[a:a + n], 1 - 0.55 * np.exp(-tt(n) * 6))
L += MUS_L * duck; R += MUS_R * duck
RL += MUS_L * duck * 0.15; RR += MUS_R * duck * 0.15

# ─── Reverb (stereo convolution with decaying noise IR) ───
def ir(seed, dur=2.8):
    g = np.random.default_rng(seed); n = idx(dur); t = tt(n)
    x = g.standard_normal(n) * np.exp(-t / 0.75)
    return fft_filter(x, 150, 7000) * 0.06
def conv(x, h):
    m = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)]
L += conv(RL, ir(1)); R += conv(RR, ir(2))

# ─── Master ───
mix = np.stack([L, R])
mix = fft_filter(mix[0], 22), fft_filter(mix[1], 22)
mix = np.stack(mix)
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
fade = np.ones(N); fn = idx(0.6); fade[-fn:] = np.linspace(1, 0, fn) ** 2
mix *= fade
mix *= 0.7 / np.max(np.abs(mix))
out = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('wrote', len(out) / SR, 's')
