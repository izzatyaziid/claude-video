"""S02 "VIRAL MACAM BUNGA API" — cinematic ambient score + SFX (no voice). Sea wash, firework whistles/booms/crackle,
silence after the fireworks, lighthouse ignition hum, steady beam pulses, D major swell at the harbour, CTA sting."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_engine'))
import audio_lib as A
import numpy as np
A.setup(30.0, seed=33); hz = A.hz; add = A.add; idx = A.idx; tt = A.tt
N = A.N; t = tt(N)
# sea wash: band-limited noise with slow swell (whole piece)
wash = A.fft_filter(A.noise(N), 120, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t) ** 2) * 0.035
add(np.stack([wash, np.roll(wash, 4000)]), 0)
# low drone (D) for the night
add(A.pad(10.0, [hz(26), hz(38), hz(45)], 0.16, 0.5, 2.0, 0.15), 0.0, bus='mus')
# fireworks
for t0, tb in [(0.4, 1.3), (2.6, 3.4), (4.2, 4.9)]:
    n = idx(tb - t0); tl = tt(n); f = 900 + 1600 * tl / (tb - t0)
    add(np.sin(2 * np.pi * np.cumsum(f) / A.SR) * np.sin(np.pi * tl / (tb - t0)) * 0.05, t0, pan=-0.2)          # whistle
    add(A.boom(0.8, 3.0, 70, 26), tb, rev=0.6); add(A.fft_filter(A.noise(idx(0.4)), 1500, 12000) * A.env_ad(idx(0.4), 0.001, 0.08) * 0.25, tb, rev=0.5)
    cr = np.zeros(idx(2.2)); r = np.random.default_rng(int(tb * 10))
    for _ in range(160):
        p = r.integers(0, len(cr) - 300); cr[p:p + 300] += A.noise(300) * np.exp(-np.arange(300) / 40) * r.uniform(0.2, 1) * (1 - p / len(cr))
    add(cr * 0.08, tb + 0.2, pan=r.uniform(-0.5, 0.5), rev=0.4)
add(A.pad(4.6, [hz(62), hz(69), hz(74)], 0.1, 0.3, 1.5, 0.5), 1.3, bus='mus')            # bright but short
# after: near silence, a lonely low note
add(A.ping(hz(50), 0.07, 1.5), 8.2, rev=0.7)
# lighthouse ignition + steady beam pulse (the "every day" heartbeat)
add(A.boom(0.6, 3.0, 60, 28), 11.0, rev=0.5); n = idx(4.0); tl = tt(n)
add(np.sin(2 * np.pi * hz(38) * tl) * np.minimum(1, tl / 0.8) * 0.06, 11.0)
A.sig_ping(11.05, 0.16)
for tp in np.arange(11.5, 24.5, 60 / 80):
    add(A.kick(0.22, 70, 40, 0.3), tp, bus='mus')
# warm swell: strategy = constant light (D major), building to the harbour
add(A.pad(8.5, [hz(50), hz(57), hz(62), hz(66)], 0.16, 2.0, 1.5, 0.3), 12.5, bus='mus', rev=0.3)
for k, tc in enumerate([13.4, 14.9, 15.9]): add(A.ping(hz([69, 74, 78][k]), 0.06, 0.6), tc, rev=0.6)
add(A.pad(6.0, [hz(50), hz(57), hz(62), hz(66), hz(69)], 0.2, 1.0, 1.5, 0.35), 19.5, bus='mus', rev=0.4)
for k in range(10): add(A.ping(hz(74 + (k % 5) * 2), 0.04, 0.4), 20.0 + k * 0.45, pan=np.sin(k) * 0.5, rev=0.5)   # harbour windows
# CTA
add(A.pad(5.0, [hz(50), hz(57), hz(62), hz(66)], 0.14, 0.5, 2.0, 0.25), 25.0, rev=0.3)
add(A.boom(0.5, 3.0, 80, 30), 27.0, rev=0.5); A.sig_ping(27.05, 0.2)
A.master(sys.argv[1] if len(sys.argv) > 1 else 'score_s02.wav', fade_out=0.6)
