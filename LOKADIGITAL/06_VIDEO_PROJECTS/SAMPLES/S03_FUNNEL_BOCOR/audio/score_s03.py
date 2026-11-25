"""S03 "FUNNEL YOU BOCOR" — electronic groove + liquid/leak sound design (no voice). 110 BPM.
Flow noise follows the picture; each leak hisses until its patch clamps on; patches climb a rising arpeggio."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_engine'))
import audio_lib as A
import numpy as np
A.setup(30.0, seed=44); hz = A.hz; add = A.add; idx = A.idx; tt = A.tt; N = A.N
BEAT = 60 / 110
DIAG = [7.6, 9.6, 11.6, 13.6]; FIX = [16.4, 18.0, 19.6, 21.2]
t = tt(N)
# liquid flow bed: stronger once the funnel is sealed
flow = A.fft_filter(A.noise(N), 300, 3000) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t) ** 2)
env = 0.025 + 0.03 * np.clip((t - 16) / 6, 0, 1); env[t < 0.3] = 0
add(np.stack([flow * env, np.roll(flow, 3000) * env]), 0)
# drips into the bag (sparse before the fixes, a stream after)
r = np.random.default_rng(4)
for tc in np.arange(3.0, 16, 1.7): add(A.pop(0.05, 600 + r.integers(0, 300)), tc + r.random() * .3, pan=-0.1)
for tc in np.arange(18.5, 26, 0.18): add(A.pop(0.035, 700 + r.integers(0, 600)), tc + r.random() * .05, pan=r.uniform(-.3, .3))
# leak hiss per junction, from the zoom-out until its patch
for k in range(4):
    a, b = 5.4, FIX[k]; n = idx(b - a); h = A.fft_filter(A.noise(n), 3000, 9000) * 0.012 * np.minimum(1, tt(n) / 0.5)
    add(h, a, pan=[0.3, 0.45, 0.55, 0.65][k])
# hook stinger + "bocor" low hit
add(A.boom(0.5, 2.0, 70, 30), 0.3, rev=0.4); add(A.drop_tone(0.15, 500, 150, 0.7), 3.1)
add(A.boom(0.6, 2.5, 60, 28), 5.4, rev=0.5); add(A.glitch(0.2, 0.3), 5.45)
# diagnosis: red-alert blips
for k, td in enumerate(DIAG): add(A.tick(0.3, 900), td); add(A.ping(hz(58 - k), 0.07, 0.3), td + 0.02, rev=0.3); add(A.whoosh(0.4, 400, 2500, 0.12), td - 0.45)
# groove: minimal during diagnosis, full during fixes
b = 0
for tb in A.grid(5.4, 23.6, BEAT):
    full = tb >= 15.8
    add(A.kick(0.45 if full else 0.3, 120, 45, 0.22), tb, bus='mus')
    add(A.hat(0.05 if full else 0.03), tb + BEAT / 2, pan=0.3, bus='mus')
    if full: add(A.hat(0.03), tb + BEAT / 4, pan=-0.3, bus='mus'); add(A.bass_note(hz(38) if (b // 4) % 2 == 0 else hz(41), BEAT * .45, 0.18), tb, bus='mus')
    else: add(A.bass_note(hz(38), BEAT * .3, 0.1), tb, bus='mus')
    b += 1
# fixes: metallic clamp + rising signal arpeggio
for k, tf in enumerate(FIX):
    add(A.kick(0.4, 200, 80, 0.08), tf); add(A.coin(0.08), tf + 0.01)
    add(A.ping(hz([69, 74, 78, 81][k]), 0.12, 0.5), tf + 0.03, rev=0.5)
A.sig_ping(15.9, 0.12)
# result: bag fills -> resolve
add(A.pad(3.0, [hz(50), hz(57), hz(62), hz(66)], 0.16, 0.3, 1.0, 0.3), 23.6, bus='mus', rev=0.3); A.sig_ping(23.8, 0.18)
# CTA
add(A.pad(3.6, [hz(50), hz(57), hz(62), hz(66)], 0.12, 0.5, 1.5, 0.25), 26.4, rev=0.3)
add(A.boom(0.5, 3.0, 80, 30), 27.8, rev=0.5); A.sig_ping(27.85, 0.2)
A.master(sys.argv[1] if len(sys.argv) > 1 else 'score_s03.wav', fade_out=0.5)
