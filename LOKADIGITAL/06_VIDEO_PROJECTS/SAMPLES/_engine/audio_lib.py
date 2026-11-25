"""LokaDigital shared audio library (numpy only): instruments + mixer. Music and SFX only — never voice.
Usage in a score:  import audio_lib as A;  A.setup(duration);  A.add(A.kick(), t) ... ;  A.master('out.wav')
Instruments reused from ep01/audio/sound.py and EP02 animatic score."""
import wave
import numpy as np
SR = 48000

def setup(dur, seed=11):
    global N, rng, L, R, RL, RR, MUS_L, MUS_R, DUR
    DUR = dur; N = int(SR * dur); rng = np.random.default_rng(seed)
    L = np.zeros(N); R = np.zeros(N); RL = np.zeros(N); RR = np.zeros(N); MUS_L = np.zeros(N); MUS_R = np.zeros(N)


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

def grid(t0, t1, step, origin=0.0):
    k = np.ceil((t0 - origin) / step - 1e-6); t = origin + k * step
    while t < t1 - 1e-6: yield t; t += step


def pluck(f, amp=0.2, dec=0.25, bright=4000):
    n = idx(dec * 4); t = tt(n)
    saw = 2 * ((f * t) % 1) - 1
    return fft_filter(saw, 60, bright) * np.exp(-t / dec) * np.minimum(1, t / 0.003) * amp

def coin(amp=0.15):
    n = idx(0.5); t = tt(n)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((2650, 9), (3970, 12), (5310, 16)))
    return s * np.minimum(1, t / 0.002) * amp

def pop(amp=0.15, f=900):
    n = idx(0.12); t = tt(n)
    return np.sin(2 * np.pi * (f + 900 * np.exp(-t * 60)) * t) * np.exp(-t * 40) * amp

def drop_tone(amp=0.2, f0=420, f1=140, dur=0.6):
    n = idx(dur); t = tt(n); f = f1 + (f0 - f1) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * amp

def sig_ping(t, amp=0.16, rev=0.6):
    add(ping(hz(81), amp, 0.55), t, rev=rev); add(ping(hz(88), amp * 0.8, 0.7), t + 0.08, rev=rev)

def master(path, gates=(), fade_out=0.6):
    """Mix buses, reverb, soft-clip, optional hard-silence gates [(t0,t1)], write 16-bit WAV."""
    global L, R
    Lm = L + MUS_L * 0.95; Rm = R + MUS_R * 0.95
    def ir(seed, dur=2.4):
        g = np.random.default_rng(seed); n = idx(dur); t = tt(n)
        return fft_filter(g.standard_normal(n) * np.exp(-t / 0.65), 150, 7000) * 0.06
    def conv(x, h):
        m = 1 << int(np.ceil(np.log2(len(x) + len(h)))); return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[:len(x)]
    Lm = Lm + conv(RL + MUS_L * 0.1, ir(1)); Rm = Rm + conv(RR + MUS_R * 0.1, ir(2))
    mix = np.stack([fft_filter(Lm, 22), fft_filter(Rm, 22)]); mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    gate = np.ones(N)
    for a, b in gates: gate[idx(a):idx(b)] = 0
    fn = idx(fade_out); gate[-fn:] *= np.linspace(1, 0, fn) ** 2
    mix *= gate; mix *= 0.7 / (np.max(np.abs(mix)) + 1e-9)
    out = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
    print('wrote', len(out) / SR, 's ->', path)
