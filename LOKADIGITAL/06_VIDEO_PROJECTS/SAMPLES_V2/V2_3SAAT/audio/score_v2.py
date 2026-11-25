# V2 "3 Saat" — lo-fi feed loop (muffled, bored) -> tape-stop on the hook -> breakdown hits -> clean beat returns -> CTA.
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../SAMPLES/_engine'))
import audio_lib as A
A.setup(24.0, seed=33); SR = A.SR; N = A.idx; tt = A.tt; hz = A.hz
T = dict(s1=2.55, s2=4.85, flick=6.55, hook=8.35, line2=9.6, smirk=10.4, freeze=11.9, big=12.2, anat=14.6, rule=18.3, cta=20.3)
BPM = 84; beat = 60 / BPM
def ep(f, dur, amp=.12):   # electric-piano-ish tone
    n = N(dur); t = tt(n); s = np.sin(2*np.pi*f*t + 1.2*np.sin(2*np.pi*f*2*t)*np.exp(-t*3)) * np.exp(-t*1.6)
    return s * np.minimum(1, t/.004) * amp
def loop(t0, t1, muffle=900, gain=1.0, origin=0.0):
    """lo-fi groove; rendered into a temp bus then filtered as one (muffled = 'heard through boredom')"""
    n = N(t1 - t0); buf = np.zeros(n)
    def put(sig, tt0, g=1.0):
        i = N(tt0 - t0); 
        if i >= n or i < 0: return
        m = min(len(sig), n - i); buf[i:i+m] += sig[:m] * g
    chords = [[62, 65, 69, 72], [60, 64, 67, 71], [58, 62, 65, 69], [57, 60, 64, 67]]
    for k, tb in enumerate(A.grid(t0, t1, beat, origin)):
        bi = int(round((tb - origin) / beat))
        if bi % 4 in (0, 2): put(A.kick(.6, 110, 45, .25), tb)
        if bi % 4 in (1, 3): put(A.fft_filter(A.noise(N(.2)), 900, 7000) * np.exp(-tt(N(.2))*22) * .35, tb + .012)
        put(A.hat(.10), tb + beat/2 + .02)
        if bi % 4 == 0:
            ch = chords[(bi // 4) % 4]
            for j, m in enumerate(ch): put(ep(hz(m), beat*4, .07), tb + j*.012)
            put(A.bass_note(hz(ch[0]-24), beat*3.5, .3), tb)
    buf = A.fft_filter(buf, 30, muffle) if muffle else buf
    buf += A.fft_filter(A.noise(n), 2000, 9000) * .006          # vinyl hiss
    return buf * gain
# 1 · bored scroll (muffled loop)
A.add(loop(0, T['hook'], 850, 1.0), 0, bus='mus')
A.add(A.fft_filter(A.noise(N(24)), 50, 500) * .01, 0)          # room tone
for s in (T['s1'], T['s2']):
    A.add(A.whoosh(.35, 1500, 400, .16), s - .03, pan=.2); A.add(A.tick(.10, 3000), s + .38)
# flick: fast ticks decelerating
ts = T['flick']; k = 0
while ts < T['hook']:
    A.add(A.tick(.07, 2600 + k * 40), ts, pan=np.sin(k) * .3); ts += .05 + k * .012; k += 1
A.add(A.whoosh(1.6, 4000, 300, .14), T['flick'])
# 2 · THE STOP: tape-stop of the loop's last half second + impact
tail = loop(T['hook'] - .6, T['hook'] + .2, 850, 1.0)
n = len(tail); rate = np.linspace(1, .05, n); pos = np.cumsum(rate); pos = pos[pos < n - 1]
stop = np.interp(pos, np.arange(n), tail) * np.linspace(1, 0, len(pos)) ** .5
A.add(stop, T['hook'] - .05, bus='mus')
A.add(A.kick(1.0, 160, 38, .5), T['hook']); A.add(A.boom(.55, 3.0), T['hook'], rev=.4)
A.add(A.fft_filter(A.noise(N(.08)), 2000, 12000) * np.exp(-tt(N(.08))*50) * .5, T['hook'])
# the three hook words slam (spring) — small punches
for i in range(3): A.add(A.thud(.25), T['hook'] + i * .12)
# held breath: heartbeat + high tone
for k in range(3): A.add(A.kick(.35, 70, 40, .2), T['hook'] + .9 + k * .75); A.add(A.kick(.22, 70, 40, .2), T['hook'] + 1.08 + k * .75)
A.add(A.pad(3.5, [hz(74), hz(81)], .03, 1, 1.5, .5), T['hook'] + .4, rev=.6, bus='mus')
A.add(A.pluck(hz(69), .16, .5), T['line2'], rev=.5); A.add(A.pluck(hz(74), .12, .5), T['line2'] + .12, rev=.5)
A.add(A.pop(.14, 1100), T['smirk'] + .9)
# 3 · breakdown
A.add(A.fft_filter(A.noise(N(.06)), 1500, 9000) * np.exp(-tt(N(.06))*60) * .6, T['freeze'])   # shutter
A.add(A.tick(.2, 1800), T['freeze'] + .05)
A.add(A.pad(8.4, [hz(50), hz(57), hz(62)], .06, .8, 1.5, .25), T['freeze'], rev=.5, bus='mus')
A.add(A.kick(.9, 140, 40, .45), T['big'] + .5); A.add(A.boom(.45, 2.5), T['big'] + .5, rev=.3); A.add(A.riser(.5, .10), T['big'])
for i in range(3): A.add(A.ping(hz(76 + [0, 3, 7][i]), .14, .5), T['anat'] + i * 1.1, rev=.4); A.add(A.whoosh(.3, 800, 3000, .07), T['anat'] + i * 1.1 - .1)
A.add(A.riser(1.2, .12), T['rule'] - 1.2)
# 4 · clean groove back (the lesson lands) through CTA
A.add(A.kick(.9, 150, 40, .4), T['rule'])
A.add(loop(T['rule'], 24.0, None, .85, origin=T['rule']), T['rule'], bus='mus')
A.add(A.whoosh(.5, 400, 2500, .15), T['cta'] - .05); A.add(A.tick(.12, 3000), T['cta'] + .5)
A.add(A.pop(.16, 900), T['cta'] + 1.4); A.add(A.coin(.10), T['cta'] + 1.45)
for k, m in enumerate([74, 77, 81]): A.add(A.ping(hz(m), .10, .8), T['cta'] + 2.2 + k * .14, rev=.5)
A.master(os.path.join(os.path.dirname(__file__), 'score_v2.wav'), fade_out=.6)
