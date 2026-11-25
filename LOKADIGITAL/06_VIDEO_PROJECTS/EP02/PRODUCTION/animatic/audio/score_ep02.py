"""LOKADIGITAL EP02 — ANIMATIC temp score + sound design (music + SFX only, NO voiceover).
Synthesised from scratch with numpy; instruments reused from ep01/audio/sound.py.
Every cue time comes from ../beatmap.json (same source as the animatic picture).
Usage: python3 score_ep02.py out.wav
"""
import sys, wave, json, os
import numpy as np

BM = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'beatmap.json')))
E = BM['events']; BEAT = BM['beat']; ORIGIN = BM['origin']
SR = 48000
DUR = BM['dur']
N = int(SR * DUR)
rng = np.random.default_rng(11)

L = np.zeros(N); R = np.zeros(N)
RL = np.zeros(N); RR = np.zeros(N)
MUS_L = np.zeros(N); MUS_R = np.zeros(N)

def idx(t): return int(round(t * SR))
def tt(n): return np.arange(n) / SR

def add(sig, t0, gain=1.0, pan=0.0, rev=0.0, bus='fx'):
    i = idx(t0)
    if sig.ndim == 1: sl, sr_ = sig, sig
    else: sl, sr_ = sig[0], sig[1]
    n = len(sl)
    if i >= N or i + n <= 0: return
    a, b = max(0, i), min(N, i + n); s0 = a - i
    th = (pan + 1) * np.pi / 4; gl, gr = np.cos(th) * gain * 1.414, np.sin(th) * gain * 1.414
    if bus == 'mus': MUS_L[a:b] += sl[s0:s0 + b - a] * gl; MUS_R[a:b] += sr_[s0:s0 + b - a] * gr
    else: L[a:b] += sl[s0:s0 + b - a] * gl; R[a:b] += sr_[s0:s0 + b - a] * gr
    if rev: RL[a:b] += sl[s0:s0 + b - a] * gl * rev; RR[a:b] += sr_[s0:s0 + b - a] * gr * rev

def fft_filter(x, lo=0, hi=None):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))

def noise(n): return rng.standard_normal(n)

def sweep_noise(dur, f0, f1, q=0.5, curve=1.0):
    n = idx(dur); x = noise(n + 4096); out = np.zeros(n + 4096)
    hop, win = 512, 2048; w = np.hanning(win); f = np.fft.rfftfreq(win, 1 / SR)
    for s in range(0, n, hop):
        p = (s / n) ** curve; fc = f0 * (f1 / f0) ** p; bw = fc * q
        m = np.exp(-0.5 * ((f - fc) / bw) ** 2); seg = x[s:s + win] * w
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

# ─── EP02 helpers ──────────────────────────────────────────────
def sig_ping(t, amp=0.16, rev=0.6):
    """Series sonic motif: 'signal ping' = two clean notes (A5 -> E6)."""
    add(ping(hz(81), amp, 0.55), t, rev=rev); add(ping(hz(88), amp * 0.8, 0.7), t + 0.08, rev=rev)

def sand(dur, amp=0.08):
    n = idx(dur); t = tt(n)
    return fft_filter(noise(n), 3500, 12000) * np.sin(np.pi * t / dur) ** 1.5 * amp

def megaphone(dur, f=220, amp=0.18):
    n = idx(dur); t = tt(n)
    saw = 2 * ((f * t + 0.3 * np.sin(2 * np.pi * 5 * t)) % 1) - 1
    x = fft_filter(np.tanh(saw * 3) + 0.4 * noise(n), 500, 2600) * (0.6 + 0.4 * (np.sin(2 * np.pi * 7 * t) > 0))
    e = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.2)
    return np.tanh(x * 2) * e * amp

def thud(amp=0.4):
    n = idx(0.5); t = tt(n)
    return fft_filter(np.sin(2 * np.pi * 55 * t) * np.exp(-t * 12) + noise(n) * np.exp(-t * 40) * 0.3, 30, 600) * amp

def grid(t0, t1, step):
    k = np.ceil((t0 - ORIGIN) / step - 1e-6); t = ORIGIN + k * step
    while t < t1 - 1e-6: yield t; t += step

ARP = [hz(62), hz(65), hz(69), hz(74), hz(76), hz(74), hz(69), hz(65)]   # D F A D E D A F
PROG = [D1, Bb1 / 2 * 2, F1, C2 / 2 * 2]                                  # Dm  Bb  F  C (roots)

# ─── S01 HOOK ──────────────────────────────────────────────────
add(fft_filter(noise(N), 80, 900) * 0.003, 0)                                       # room tone
n = idx(E['freeze']); tl = tt(n)
add(np.sin(2 * np.pi * D1 * tl) * np.minimum(1, tl / 0.08) * 0.22, 0)              # sub drone from frame 0
add(ping(hz(93), 0.03, 0.08), 0.0)
add(boom(1.0, 2.2), E['impact'], rev=0.5); add(kick(0.9, 150, 40, 0.35), E['impact'])
add(fft_filter(noise(idx(1.2)), 2000, 14000) * env_ad(idx(1.2), 0.002, 0.35) * 0.28, E['impact'], rev=0.6)
add(pad(E['freeze'] - E['impact'], [D2, A1 * 2, F1 * 4, hz(64)], 0.22, 0.05, 0.05, 0.5), E['impact'], bus='mus')
add(riser(E['freeze'] - E['impact'] - 0.1, 0.18, 300, 5000), E['impact'] + 0.1)
for i in range(4):
    add(tick(0.22, 2200 + i * 260), E['chips'] + i * 0.163, pan=[-0.5, 0.6, -0.2, 0.4][i])
    add(ping(hz([76, 79, 81, 83][i]), 0.05, 0.12), E['chips'] + i * 0.163, rev=0.3)
for k in range(3): add(tick(0.12, 1800), E['beli_alone'] + 0.1 + k * 0.16)
add(fft_filter(noise(idx(0.03)), 200, 2500) * 0.5, E['freeze'] - 0.12)               # dead, dry click
add(fft_filter(noise(idx(2.6)), 120, 1500) * np.sin(np.pi * tt(idx(2.6)) / 2.6) ** 2 * 0.05, E['push'])   # low air
for t in grid(E['line_masalah'], E['siapa'], BEAT):                                 # heartbeat sub
    add(kick(0.35, 70, 38, 0.25), t); add(kick(0.22, 65, 36, 0.2), t + 0.16)
sig_ping(E['siapa'], 0.2); add(boom(0.7, 2.5, 80, 30), E['siapa'], rev=0.5)
add(whoosh(0.5, 300, 5000, 0.3), E['s02'] - 0.45)

# ─── S02 MAP ───────────────────────────────────────────────────
for i, k in enumerate(('node_cari', 'node_cakap', 'node_sambung')):
    add(tick(0.25, 1800 + i * 400), E[k]); add(ping(hz([74, 79, 86][i]), 0.07, 0.25), E[k] + 0.01, rev=0.4)
add(tick(0.3, 1400), E['rail_lock'])
add(whoosh(0.35, 4000, 400, 0.2), E['s03'] - 0.3)

# ─── S03 CARI ──────────────────────────────────────────────────
add(whoosh(0.6, 200, 6000, 0.35), E['s03'] - 0.1); add(kick(0.7), E['s03'])
b = 0
for t in grid(E['s03'], E['s04'], BEAT):
    add(kick(0.42, 120, 45, 0.25), t, bus='mus')
    if b % 4 == 0: add(bass_note(D1 * 2, BEAT * 3.6, 0.2), t, bus='mus')
    if t >= E['q1']: add(hat(0.05), t + BEAT / 2, pan=0.3, bus='mus')
    b += 1
add(sweep_noise(1.6, 500, 6000, 0.25) * np.hanning(idx(1.6)) * 0.12, E['hud_research'])
for k in ('q1', 'q2', 'q3'): add(tick(0.3, 1500), E[k]); add(ping(hz(62), 0.08, 0.2), E[k] + 0.01)
add(pad(E['s04'] - E['cluster'], [D2, F1 * 2, A1 * 2, hz(64)], 0.2, 0.6, 0.8, 0.3), E['cluster'], bus='mus', rev=0.3)
sig_ping(E['cluster'] + 0.1, 0.1)
cr = np.zeros(idx(1.0))
for _ in range(90):
    p = rng.integers(0, len(cr) - 400); cr[p:p + 400] += noise(400) * np.exp(-np.arange(400) / 60) * rng.uniform(0.2, 1)
add(cr * 0.1, E['semua_orang'], pan=0.2)
add(glitch(0.14, 0.4), E['strike1']); sig_ping(E['orang_betul'], 0.15)
add(whoosh(0.4, 600, 4500, 0.18), E['to_rail1'])

# ─── S04 CAKAP ─────────────────────────────────────────────────
add(whoosh(0.6, 200, 6000, 0.35), E['s04'] - 0.1)
b = 0
for t in grid(E['s04'], E['s05'], BEAT):
    root = PROG[(b // 4) % 4] * 2
    add(kick(0.48, 125, 45, 0.27), t, bus='mus')
    add(bass_note(root, BEAT * 0.45, 0.2), t, bus='mus'); add(bass_note(root * 2, BEAT * 0.35, 0.1), t + BEAT / 2, bus='mus')
    add(hat(0.06), t + BEAT / 2, pan=0.35, bus='mus'); add(hat(0.03), t + BEAT * 0.75, pan=-0.35, bus='mus')
    b += 1
add(megaphone(E['diri_sendiri'] - E['ad_shout'], 220, 0.16), E['ad_shout'], pan=-0.1)
for k in range(6): add(whoosh(0.5, 300, 1500, 0.08), E['ad_shout'] + k * 0.38, pan=(-1) ** k * 0.5)
cr = np.zeros(idx(1.5))
for _ in range(120):
    p = rng.integers(0, len(cr) - 400); cr[p:p + 400] += noise(400) * np.exp(-np.arange(400) / 60) * rng.uniform(0.2, 1)
add(cr * 0.09, E['diri_sendiri'], pan=-0.2)
add(sand(E['strike2'] - E['tiada_peduli'], 0.1), E['tiada_peduli'], pan=0.3)
add(glitch(0.18, 0.5), E['strike2']); add(boom(0.35, 1.2, 70, 30), E['strike2'])
l1, l2 = len('Post content setiap hari,'), len('tapi pelanggan tetap tak datang?')
for i in range(l1): add(tick(0.07 + 0.03 * rng.random(), 2600 + rng.integers(-300, 300)), E['type1'] + (E['type2'] - E['type1']) * i / l1, pan=0.1)
for i in range(l2): add(tick(0.07 + 0.03 * rng.random(), 2600 + rng.integers(-300, 300)), E['type2'] + 1.15 * i / l2, pan=0.1)
n = idx(1.8); tl = tt(n)
add(sum(np.sin(2 * np.pi * f * tl) for f in (hz(93), hz(98), hz(100))) * np.sin(np.pi * tl / 1.8) ** 2 * 0.02, E['type2'] + 0.6, rev=0.7)
sig_ping(E['masalah_dia'], 0.17)
for k, t in enumerate(grid(E['masalah_dia'], E['s05'], BEAT / 4)):
    add(ping(ARP[k % 8] * 2, 0.045, 0.12), t, pan=np.sin(k) * 0.4, rev=0.3, bus='mus')
add(whoosh(0.35, 800, 4500, 0.18), E['to_rail2'])

# ─── S05 SAMBUNG ───────────────────────────────────────────────
add(whoosh(0.6, 200, 6000, 0.35), E['s05'] - 0.1)
for t in grid(E['s05'], E['drop'] - BEAT / 4, BEAT):
    add(kick(0.5, 125, 45, 0.27), t, bus='mus'); add(bass_note(D1 * 2, BEAT * 0.8, 0.18), t, bus='mus')
for i in range(3): add(tick(0.25, 1700 + i * 300), E['uji'] + 0.3 + i * 0.15)
add(thud(0.35), E['branch_die1']); add(thud(0.35), E['branch_die2'])
sig_ping(E['menjadi'], 0.12)
for t in grid(E['besarkan'], E['drop'] - BEAT / 4, BEAT / 4): add(hat(0.05 + 0.05 * (t - E['besarkan']) / (E['drop'] - E['besarkan'])), t, pan=0.25, bus='mus')
add(riser(E['drop'] - E['besarkan'] - BEAT / 4, 0.4, 150, 8000), E['besarkan'], bus='mus')
# DROP
add(boom(1.0, 4.0, 110, 28), E['drop'], rev=0.6); add(kick(1.0), E['drop'])
add(fft_filter(noise(idx(1.5)), 1500, 14000) * env_ad(idx(1.5), 0.001, 0.3) * 0.3, E['drop'], rev=0.6)
b = 0
for t in grid(E['drop'], E['sweep'], BEAT):
    root = PROG[(b // 4) % 4] * 2
    add(kick(0.6, 125, 45, 0.28), t, bus='mus'); add(bass_note(root, BEAT * 0.45, 0.22), t, bus='mus'); add(bass_note(root * 2, BEAT * 0.35, 0.12), t + BEAT / 2, bus='mus')
    add(hat(0.07), t + BEAT / 2, pan=0.35, bus='mus'); add(hat(0.04), t + BEAT / 4, pan=-0.3, bus='mus'); add(hat(0.04), t + BEAT * 0.75, pan=0.3, bus='mus')
    if b % 2: add(fft_filter(noise(idx(0.18)), 900, 7000) * env_ad(idx(0.18), 0.001, 0.05) * 0.16, t, rev=0.3, bus='mus')
    b += 1
add(pad(E['sweep'] - E['drop'], [D2 * 2, A1 * 2, F1 * 4, hz(76)], 0.17, 0.3, 0.4, 0.4), E['drop'], bus='mus')
add(whoosh(0.6, 200, 8000, 0.45), E['sweep'] - 0.4)

# ─── S06 RUMUSAN ───────────────────────────────────────────────
add(pad(E['s07'] - E['s06'], [hz(50), hz(57), hz(62), hz(66), hz(69)], 0.2, 0.4, 0.8, 0.25), E['s06'], rev=0.3)   # D major resolve
for i in range(3): add(tick(0.2, 2000 + i * 300), E['s06'] + 0.2 + i * 0.2); add(ping(hz([74, 78, 81][i]), 0.06, 0.25), E['s06'] + 0.21 + i * 0.2, rev=0.4)
add(glitch(0.5, 0.3), E['morph']); add(glitch(0.2, 0.2), E['morph'] + 0.2, pan=0.4)
sig_ping(E['cari_beli'], 0.26, 0.7); add(boom(0.45, 2.0, 80, 30), E['cari_beli'], rev=0.5)

# ─── S07 BRAND ─────────────────────────────────────────────────
add(boom(0.7, 4.0, 80, 28), E['s07'], rev=0.6)
n = idx(1.4); tl = tt(n)
add(sum(np.sin(2 * np.pi * f * tl) for f in (hz(98), hz(105), hz(110))) * np.sin(np.pi * tl / 1.4) ** 2 * 0.025, E['s07'] + 0.1, rev=0.7)
sig_ping(E['s07'] + 0.25, 0.14)
add(pad(E['fade_out'] - E['s07'], [hz(50), hz(57), hz(62), hz(64)], 0.12, 1.2, 1.5, 0.2), E['s07'], bus='mus')

# ─── S08 CTA ───────────────────────────────────────────────────
sig_ping(E['dm'], 0.2); add(kick(0.35, 70, 36, 0.5), E['dm'], rev=0.3)
add(tick(0.15, 2400), E['follow_save']); add(tick(0.15, 2700), E['follow_save'] + 0.12)
add(whoosh(0.5, 400, 5000, 0.25), E['next'] - 0.05, pan=0.5)
add(ping(hz(74), 0.06, 0.8), E['cover'], rev=0.6)

# ─── bus processing ────────────────────────────────────────────
duck = np.ones(N)
for k in ('impact', 'siapa', 'strike2', 'drop', 'cari_beli', 's07', 'dm'):
    a = idx(E[k]); n = min(idx(0.6), N - a); duck[a:a + n] = np.minimum(duck[a:a + n], 1 - 0.5 * np.exp(-tt(n) * 6))
L += MUS_L * duck; R += MUS_R * duck
RL += MUS_L * duck * 0.12; RR += MUS_R * duck * 0.12

def ir(seed, dur=2.6):
    g = np.random.default_rng(seed); n = idx(dur); t = tt(n)
    return fft_filter(g.standard_normal(n) * np.exp(-t / 0.7), 150, 7000) * 0.06
def conv(x, h):
    m = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)]
L += conv(RL, ir(1)); R += conv(RR, ir(2))

mix = np.stack([fft_filter(L, 22), fft_filter(R, 22)])
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
# hard silences (the storyboard uses silence as a weapon): freeze gap and the loop tail
gate = np.ones(N)
a, b = idx(E['freeze']), idx(E['push']); gate[a:b] = 0; gate[b:b + idx(0.05)] = np.linspace(0, 1, idx(0.05))
a = idx(E['fade_out']); gate[a - idx(0.3):a] = np.minimum(gate[a - idx(0.3):a], np.linspace(1, 0, idx(0.3)) ** 2); gate[a:] = 0
mix *= gate
mix *= 0.7 / np.max(np.abs(mix))
out = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('wrote', len(out) / SR, 's')
