# V1 "Yang Paling Bising" — foley-led score. Noise wall (paper slaps + crowd megaphones) -> hard cut to room tone ->
# marker scratch + warm Karplus-Strong guitar motif -> pins, stamp. Music & SFX only, no voice.
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../SAMPLES/_engine'))
import audio_lib as A
A.setup(25.0, seed=21); SR = A.SR; N = lambda d: A.idx(d); tt = A.tt

def ks(f, dur=2.5, amp=.2, bright=.5, seed=0):     # Karplus-Strong plucked nylon string
    n = N(dur); p = int(SR / f); g = np.random.default_rng(seed); buf = g.uniform(-1, 1, p) * amp
    buf = A.fft_filter(np.concatenate([buf, np.zeros(4096)]), 0, 2500 + bright * 4000)[:p]
    out = np.zeros(n); d = .996
    for i in range(n): out[i] = buf[i % p]; buf[i % p] = d * .5 * (buf[i % p] + buf[(i + 1) % p])
    return out * np.minimum(1, tt(n) / .002)
def ksfast(f, dur=2.5, amp=.2, bright=.5, seed=0):   # vectorised approximation: decaying harmonic series + pick noise
    n = N(dur); t = tt(n); s = np.zeros(n)
    for k in range(1, 12): s += np.sin(2*np.pi*f*k*t*(1+.0004*k)) * np.exp(-t*(1.2+k*k*.35*(1.3-bright))) / k**1.1
    pk = A.fft_filter(np.random.default_rng(seed).standard_normal(n) * np.exp(-t*90), 800, 6000) * .25
    return (s + pk) * amp * np.minimum(1, t/.002)
def slap(amp=.5, seed=0):                            # paper sheet slapped onto a wall
    g = np.random.default_rng(seed); n = N(.35); t = tt(n)
    crack = A.fft_filter(g.standard_normal(n), 900, 7000) * np.exp(-t*55)
    body = A.fft_filter(g.standard_normal(n), 80, 700) * np.exp(-t*22) * .8
    return (crack + body + np.sin(2*np.pi*95*t)*np.exp(-t*30)*.6) * amp
def rustle(dur, amp=.15, seed=0):
    g = np.random.default_rng(seed); n = N(dur); t = tt(n)
    x = A.fft_filter(g.standard_normal(n), 1500, 9000) * (np.abs(A.fft_filter(g.standard_normal(n), 0, 12)) * 6)
    return x * np.sin(np.pi * t / dur) ** .7 * amp
def scratch(dur, amp=.06, seed=0):                    # felt marker on paper
    g = np.random.default_rng(seed); n = N(dur); t = tt(n)
    strokes = (np.sin(2*np.pi*(5+3*np.sin(t*7))*t) > -.2).astype(float); strokes = A.fft_filter(strokes, 0, 40)
    return A.fft_filter(g.standard_normal(n), 2500, 8000) * strokes * np.minimum(1, t/.02) * np.minimum(1, (dur-t)/.05) * amp
def room(dur, amp=.012):
    n = N(dur); return A.fft_filter(A.noise(n), 60, 900) * amp

# 1 · THE WALL (0–5.6 s): every poster lands with its own slap; crowd of megaphones swells underneath
for i in range(14):
    tp = .15 + i * .19 * (1 - i * .025); tl = np.ceil((tp + .25) * 12) / 12 - .02
    A.add(slap(.55 + .03 * i, i), tl, pan=np.sin(i * 2.3) * .6, rev=.15)
for k, (f, p) in enumerate([(220, -.5), (247, .5), (196, -.2), (262, .3), (233, .7), (208, -.7)]):
    st = .6 + k * .55; A.add(A.megaphone(5.4 - st, f, .10 + k * .012), st, pan=p, rev=.25)
A.add(A.fft_filter(A.noise(N(5.0)), 300, 3000) * np.linspace(0, 1, N(5.0)) ** 2 * .05, .5, rev=.3)   # crowd wash
A.add(scratch(1.0, .09, 3), 3.2); A.add(scratch(.4, .08, 4), 4.1)                                  # "Semua menjerit." + circle
# hard cut at 5.6: the note slides in — whoosh of paper, then a quiet room
A.add(rustle(.5, .25, 9), 5.45); A.add(slap(.25, 40), 6.0)
A.add(room(19.4), 5.6, bus='mus')
# 2 · THE NOTE: marker writes each line
for i, (t0, L) in enumerate([(6.3, 8), (6.85, 17), (7.7, 13), (8.3, 16), (9.1, 14)]): A.add(scratch(L * .045, .07, 10 + i), t0, pan=-.1)
# warm motif (D major, nylon), enters as the note is written; voice-leading kept simple and human
D = A.hz
mot = [(6.4, 62), (6.9, 66), (7.4, 69), (8.2, 71), (8.6, 69), (9.4, 66), (10.2, 64), (10.6, 66), (11.4, 62)]
for t0, m in mot: A.add(ksfast(D(m), 2.6, .16, .55, int(t0*10)), t0, pan=.15, rev=.35, bus='mus')
A.add(A.pad(7, [D(50), D(57), D(62), D(66)], .05, 2.5, 2.5, .2), 6.2, rev=.5, bus='mus')
# 3 · walls come down (12.4–15): paper rustles, falls
for k in range(7): A.add(rustle(.9, .14, 50 + k), 12.4 + k * .3, pan=np.sin(k) * .7, rev=.2)
A.add(A.whoosh(.9, 2000, 300, .12), 12.8)
# insight highlighter (14.8) — a marker swipe
A.add(scratch(.6, .10, 70), 14.8)
# 4 · groove under the method (13.2–21): soft brush + upright bass, plucked chords
for b, t0 in enumerate(A.grid(13.2, 21.2, .5, 13.2)):
    A.add(A.fft_filter(A.noise(N(.12)), 3000, 11000) * np.exp(-tt(N(.12))*40) * (.05 if b % 2 else .03), t0 + (.02 if b % 2 else 0), pan=.3)
    if b % 4 == 0: A.add(A.thud(.18), t0)
prog = [(13.2, [50, 57, 62, 66]), (15.2, [47, 54, 59, 62]), (17.2, [43, 50, 55, 59]), (19.2, [45, 52, 57, 61])]
for t0, ch in prog:
    A.add(A.bass_note(D(ch[0] - 12), 1.9, .22), t0, bus='mus')
    for j, m in enumerate(ch[1:]): A.add(ksfast(D(m + 12), 2.0, .07, .45, j), t0 + j * .03, pan=-.2 + j * .2, rev=.3, bus='mus')
    for j, m in enumerate(ch[1:][::-1]): A.add(ksfast(D(m + 12), 1.5, .05, .45, j + 9), t0 + 1.0 + j * .03, pan=.2, rev=.3, bus='mus')
# cards pinned (17.2 + .55 i): pin tap + pen tick
for i in range(3):
    A.add(A.pop(.10, 1400), 17.2 + i * .55 + .3); A.add(slap(.12, 80 + i), 17.2 + i * .55 + .28)
    A.add(scratch(.25, .08, 90 + i), 17.2 + i * .55 + .5)
# 5 · CTA: music resolves, rubber stamp lands
A.add(A.pad(3.8, [D(50), D(57), D(62), D(66), D(69)], .06, .4, 2.5, .3), 21.2, rev=.6, bus='mus')
for t0, m in [(21.3, 74), (21.6, 69), (21.9, 66), (22.25, 62)]: A.add(ksfast(D(m), 2.8, .14, .6, int(t0*7)), t0, rev=.4, bus='mus')
A.add(A.thud(.6), 22.6); A.add(slap(.7, 99), 22.6, rev=.3)
A.add(rustle(.4, .12, 123), 23.1); A.add(ksfast(D(74), 3, .10, .7, 5), 23.3, rev=.6, bus='mus')
A.master(os.path.join(os.path.dirname(__file__), 'score_v1.wav'), fade_out=.5)
