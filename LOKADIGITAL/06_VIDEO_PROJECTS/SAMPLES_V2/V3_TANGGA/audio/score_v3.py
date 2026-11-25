# V3 "Viral ≠ Strategi" — cinematic: sub drone, stone groan, five heavy impacts (times match the in-scene rigid-body
# simulation), grinding stone steps each locking with an ascending tone, climb swell, major-key resolve at the CTA.
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../SAMPLES/_engine'))
import audio_lib as A
A.setup(22.0, seed=55); N = A.idx; tt = A.tt; hz = A.hz
HITS = [5.885, 6.185, 6.415, 6.595, 6.735]; BOUNCE = [h + .198 for h in HITS]
STEP0, GAP = 7.3, .78
def grind(dur, amp=.25, seed=0):
    g = np.random.default_rng(seed); n = N(dur); t = tt(n)
    gr = A.fft_filter(g.standard_normal(n), 60, 1400) * (0.6 + 0.4 * np.abs(A.fft_filter(g.standard_normal(n), 0, 25)) * 4)
    rum = np.sin(2 * np.pi * 38 * t + np.sin(t * 9)) * .5
    return (gr + rum) * np.sin(np.pi * np.minimum(1, t / dur)) ** .6 * amp
def debris(amp=.25, seed=0):
    g = np.random.default_rng(seed); out = np.zeros(N(1.2))
    for k in range(18):
        i = N(g.uniform(0, .9) ** 2); n = N(.05); s = A.fft_filter(g.standard_normal(n), 1500, 9000) * np.exp(-tt(n) * 80) * g.uniform(.2, 1)
        out[i:i + n] += s[:len(out) - i]
    return out * amp
def bell(f, dur=3.0, amp=.12):
    n = N(dur); t = tt(n); s = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) * a for r, d, a in ((1, 1.2, 1), (2.01, 2.5, .4), (3.0, 4, .2), (4.17, 6, .12)))
    return s * np.minimum(1, t / .003) * amp
# drone bed: D1 + A1, slow filter breathe
n = N(22); t = tt(n)
drone = (np.sin(2 * np.pi * hz(26) * t) * .5 + np.sin(2 * np.pi * hz(33) * t) * .25 + A.fft_filter(A.noise(n), 40, 220) * .4) * (0.7 + 0.3 * np.sin(t * .6))
drone *= np.minimum(1, t / 2.5) * (1 - 0.5 * ((t > 7.3) & (t < 11)))
A.add(drone * .10, 0, bus='mus')
# 1 · tension: low pulse every 1.2 s, groan as the letters wobble
for k, tp in enumerate(A.grid(.6, 4.6, 1.2)): A.add(A.kick(.35 + k * .05, 60, 36, .35), tp)
A.add(A.fft_filter(A.noise(N(1.6)), 70, 300) * np.sin(np.pi * tt(N(1.6)) / 1.6) * .2, 4.0)   # stone groan
A.add(A.riser(1.8, .09, 100, 1500), 4.1)
# 2 · five impacts (heavy) + bounces + debris; brief silence before the first
for i, h in enumerate(HITS):
    A.add(A.kick(1.0, 120, 30, .5), h, pan=(i - 2) * .25); A.add(A.boom(.5 + i * .05, 3.0), h, rev=.5)
    A.add(debris(.3, i), h + .01, pan=(i - 2) * .3, rev=.3); A.add(A.thud(.3), BOUNCE[i], pan=(i - 2) * .25)
A.add(A.fft_filter(A.noise(N(3)), 100, 1200) * np.exp(-tt(N(3)) * 1.2) * .08, 6.75, rev=.6)   # dust settle
# 3 · steps grind up, each locks with a rising bell (D minor → lifts to D major on SCALE)
notes = [62, 65, 69, 72, 78]
for i in range(5):
    t0 = STEP0 + i * GAP; A.add(grind(.62, .22 + i * .02, i), t0, pan=.1); A.add(A.thud(.45), t0 + .6); A.add(A.kick(.5, 90, 40, .3), t0 + .6)
    A.add(bell(hz(notes[i]), 3.2, .10 + i * .01), t0 + .6, rev=.5, bus='mus')
A.add(A.pad(4.5, [hz(50), hz(57), hz(62), hz(65)], .05, 1.2, 1.5, .25), 7.4, rev=.5, bus='mus')
# 4 · climb: pulse in eighths + swell
for k, tp in enumerate(A.grid(11.4, 15.0, .3)): A.add(A.kick(.25 + .02 * (k % 4 == 0), 70, 40, .2), tp); A.add(A.hat(.04 + .002 * k), tp + .15)
for k, tp in enumerate(A.grid(11.4, 15.0, 1.2)): A.add(A.bass_note(hz(38 + [0, 3, 5][k % 3]), 1.15, .25), tp, bus='mus')
A.add(A.pad(3.8, [hz(62), hz(66), hz(69), hz(74)], .05, 2.5, .6, .4), 11.4, rev=.5, bus='mus')
A.add(A.riser(2.2, .14, 200, 8000), 12.8); A.add(A.whoosh(1.8, 300, 3000, .12), 15.0)
# 5 · crane reveal + CTA: D major resolve
A.add(A.boom(.55, 4.0, 70, 28), 15.1, rev=.5); A.add(A.kick(.8, 110, 34, .5), 15.1)
A.add(A.pad(6.8, [hz(38), hz(50), hz(57), hz(62), hz(66), hz(69)], .09, .8, 2.5, .35), 15.1, rev=.6, bus='mus')
for k, m in enumerate([74, 78, 81, 86]): A.add(bell(hz(m), 3.0, .07), 17.5 + k * .18, rev=.6, bus='mus')
A.add(A.pop(.14, 900), 18.9); A.add(A.coin(.08), 18.95)
A.add(bell(hz(74), 3.5, .09), 19.7, rev=.7, bus='mus')
A.master(os.path.join(os.path.dirname(__file__), 'score_v3.wav'), fade_out=.8)
