"""S01 "BOOST POST BILA SALES TURUN?" — music + SFX (no voice). Playful-premium pluck groove, 104 BPM, D minor -> D major."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_engine'))
import audio_lib as A
import numpy as np
A.setup(30.0, seed=21); hz = A.hz; add = A.add
BEAT = 60 / 104
add(A.fft_filter(A.noise(A.N), 80, 900) * 0.003, 0)
# --- hook: taps, coins
add(A.ping(hz(93), 0.03, 0.08), 0.1)
for i, tp in enumerate([0.8, 1.15, 1.45, 1.7]):
    add(A.kick(0.35, 90, 50, 0.12), tp); add(A.tick(0.3, 1500 + i * 200), tp)
    for k in range(3): add(A.coin(0.09), tp + 0.35 + k * 0.05, pan=0.3)
# groove A (problem): muted plucks, D minor
prog = [hz(50), hz(50), hz(46), hz(48)]   # D D Bb C
b = 0
for t in A.grid(0.8, 7.6, BEAT):
    root = prog[(b // 4) % 4]
    add(A.pluck(root, 0.16, 0.18, 2200), t, pan=-0.2, bus='mus')
    add(A.pluck(root * 1.5, 0.08, 0.12, 3000), t + BEAT / 2, pan=0.3, bus='mus')
    if b % 2 == 0: add(A.kick(0.3, 110, 45, 0.2), t, bus='mus')
    add(A.hat(0.04), t + BEAT / 2, bus='mus'); b += 1
# hearts: bubbly pops
r = np.random.default_rng(3)
for k in range(26): add(A.pop(0.06, 700 + r.integers(0, 900)), 2.0 + r.random() * 2.4, pan=r.uniform(-0.6, 0.6))
add(A.riser(1.2, 0.12, 400, 4000), 2.0)
# empty cart: sad descending tone; wallet drain: coins falling
add(A.drop_tone(0.16, 520, 170, 0.8), 4.5)
for k in range(7): add(A.coin(0.06), 5.8 + k * 0.22, pan=-0.4); add(A.drop_tone(0.04, 900, 400, 0.25), 5.85 + k * 0.22)
# beat of silence then head-shake whooshes + crack
for k in range(3): add(A.whoosh(0.18, 600, 2400, 0.08), 7.8 + k * 0.4, pan=(-1) ** k * 0.5)
add(A.glitch(0.25, 0.4), 8.4); add(A.boom(0.4, 1.5, 70, 30), 8.45); add(A.whoosh(0.8, 3000, 300, 0.2), 8.8)
A.sig_ping(8.85, 0.12)
# --- system: thinking -> cards
add(A.pad(1.5, [hz(62), hz(65), hz(69)], 0.1, 0.4, 0.5, 0.3), 10.8)
add(A.whoosh(0.9, 300, 5000, 0.2), 11.2)
for i, tc in enumerate([12.2, 14.4, 16.6]):
    A.sig_ping(tc, 0.12); add(A.pad(1.6, [hz(62 + i * 2), hz(66 + i * 2), hz(69 + i * 2)], 0.08, 0.05, 1.0, 0.4), tc, rev=0.4)
add(A.tick(0.2, 2000), 15.6); add(A.ping(hz(86), 0.08, 0.4), 15.62)
# groove B (system): brighter, D major, builds
b = 0
for t in A.grid(12.2, 24.8, BEAT):
    root = [hz(50), hz(55), hz(57), hz(52)][(b // 4) % 4]   # D G A E
    add(A.pluck(root, 0.14, 0.2, 3500), t, pan=-0.2, bus='mus'); add(A.pluck(root * 2, 0.07, 0.15, 5000), t + BEAT / 2, pan=0.3, bus='mus')
    add(A.kick(0.4 if t > 18.6 else 0.25, 120, 45, 0.22), t, bus='mus'); add(A.hat(0.05 if t > 18.6 else 0.03), t + BEAT / 2, bus='mus')
    if t > 20.4: add(A.hat(0.03), t + BEAT / 4, pan=0.4, bus='mus'); add(A.hat(0.03), t + 3 * BEAT / 4, pan=-0.4, bus='mus')
    b += 1
add(A.whoosh(0.6, 400, 4000, 0.18), 18.6); add(A.riser(1.6, 0.15, 300, 6000), 18.8)
for k in range(24): add(A.coin(0.05), 20.6 + k * 0.17, pan=np.sin(k) * 0.5)
for k in range(7): add(A.ping(hz(74 + (k % 4) * 3), 0.06, 0.25), 21.5 + k * 0.37)   # cart fills
A.sig_ping(21.0, 0.14)
# --- CTA
add(A.pad(5.0, [hz(50), hz(57), hz(62), hz(66)], 0.14, 0.5, 2.0, 0.25), 25.0, rev=0.3)
add(A.boom(0.5, 3.0, 80, 30), 26.9, rev=0.5); A.sig_ping(26.95, 0.2)
A.master(sys.argv[1] if len(sys.argv) > 1 else 'score_s01.wav', fade_out=0.5)
