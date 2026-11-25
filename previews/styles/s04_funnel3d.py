"""04 CORONG 3D — one 3D object (a funnel built from rings in CSS 3D) in a dark studio; the camera orbits it.
Idea: traffic comes in but leaks out at each step (slow page, unclear offer, hard checkout); fix the journey."""
NAME = "LokaDigital Preview 04 · Corong 3D"
SLUG = "04-corong-3d"
PILL = "CUSTOMER JOURNEY"

RINGS = 9
LEAKS = [  # (ring index, label, appear time)
    (2, "Page lambat buka", 12.5),
    (4, "Offer tak jelas", 16.0),
    (6, "Checkout susah", 19.5),
]
FIXES = [(2, "Page laju", 33.0), (4, "Offer jelas", 36.0), (6, "Bayar 1 langkah", 39.0)]

CSS = """
  #studio { position:absolute; left:0; top:300px; width:1080px; height:1300px; perspective:1600px; perspective-origin:50% 35%; }
  #floor { position:absolute; left:-400px; top:980px; width:1880px; height:900px; border-radius:50%;
           background:radial-gradient(closest-side, rgba(123,22,184,.45), rgba(36,5,56,.2) 60%, transparent 100%); transform:rotateX(78deg); }
  #rig { position:absolute; left:540px; top:640px; width:0; height:0; transform-style:preserve-3d; }
  .ring { position:absolute; border-radius:50%; transform-style:preserve-3d; }
  .ring i { position:absolute; inset:0; border-radius:50%; border:6px solid rgba(201,155,255,.55); box-shadow:0 0 30px rgba(184,0,240,.35), inset 0 0 30px rgba(184,0,240,.25); }
  .ring.leak i { border-color:rgba(184,0,240,.95); }
  .ring.fixed i { border-color:rgba(180,255,57,.95); box-shadow:0 0 40px rgba(180,255,57,.45), inset 0 0 30px rgba(180,255,57,.2); }
  .p { position:absolute; width:22px; height:22px; margin:-11px; border-radius:50%; background:#fff; box-shadow:0 0 18px rgba(255,255,255,.9); }
  .p.g { background:var(--g); box-shadow:0 0 22px rgba(180,255,57,.9); }
  .leakl { position:absolute; padding:16px 26px; border-radius:16px; background:#1c0a24; border:2px solid rgba(184,0,240,.7); font:800 36px 'Inter'; letter-spacing:-.01em; white-space:nowrap; opacity:0; }
  .fixl { position:absolute; padding:16px 26px; border-radius:16px; background:#131a0e; border:2px solid rgba(180,255,57,.7); color:var(--g); font:800 36px 'Inter'; white-space:nowrap; opacity:0; }
  .sup { position:absolute; left:96px; right:96px; top:1470px; font:900 84px/0.96 'Inter'; letter-spacing:-.045em; opacity:0; }
  .lab2 { position:absolute; left:96px; top:420px; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
  #sales { position:absolute; left:540px; top:1180px; width:300px; margin-left:-150px; text-align:center; font:900 46px 'Inter'; letter-spacing:.06em; }
  #sales small { display:block; font:700 26px 'Inter'; letter-spacing:.3em; color:var(--grey); margin-top:8px; }
"""

def _ring_geom(i):
    r = 380 - i * 34          # radius shrinks downward
    y = -380 + i * 95         # vertical position
    return r, y

def _rings():
    out = []
    for i in range(RINGS):
        r, y = _ring_geom(i)
        out.append(f'<div class="ring" id="r{i}" style="left:{-r}px;top:{y - r}px;width:{2*r}px;height:{2*r}px"><i></i></div>')
    return "".join(out)

# particles: deterministic paths. 14 particles fall through; some leak out sideways at leak rings.
import math
PARTS = []
for k in range(16):
    ang = k * 2.4
    leak_at = [2, 4, 6, None][k % 4] if k % 3 != 0 else None
    PARTS.append((k, ang, leak_at))

def _parts():
    return "".join(f'<div class="p" id="p{k}"></div>' for k, _, _ in PARTS) + "".join(f'<div class="p g" id="q{k}"></div>' for k, _, _ in PARTS)

SUPS = [("u1", 4.0, 10.5, 'Trafik <span class="gr">masuk.</span><br>Jualan tak keluar.'),
        ("u2", 22.0, 28.5, 'Masalahnya bukan iklan.<br><span class="gr">Corong kau bocor.</span>'),
        ("u3", 42.5, 49.5, 'Tutup kebocoran.<br><span class="gr">Baru tambah trafik.</span>')]

BODY = f"""
      <div id="studiow" class="clip" data-start="0" data-duration="51" data-track-index="1" data-layout-allow-overflow data-layout-ignore>
        <div id="studio"><div id="floor"></div><div id="rig">{_rings()}{_parts()}</div>
          {''.join(f'<div class="leakl" id="L{i}">{t}</div>' for i, (_, t, _) in enumerate(LEAKS))}
          {''.join(f'<div class="fixl" id="F{i}">{t}</div>' for i, (_, t, _) in enumerate(FIXES))}
        </div>
      </div>
      <div class="lab lab2 clip" id="lab2" data-start="0" data-duration="51" data-track-index="2">CORONG JUALAN · CONTOH</div>
      {''.join(f'<div class="sup clip" id="{i}" data-start="{a}" data-duration="{b - a:.1f}" data-track-index="3">{t}</div>' for i, a, b, t in SUPS)}
      <div id="cta" class="clip" data-start="51" data-duration="9" data-track-index="4">
        <div class="h"><span class="el">BAIKI</span><br><span class="el">CORONG.</span><br><span class="el gr">BUKAN BAJET.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>AUDIT CUSTOMER JOURNEY</label><small>Page, offer & checkout</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    # rings: lie flat (rotateX 72) and build in
    for i in range(RINGS):
        A(f'tl.set("#r{i}", {{rotationX:72}}, 0);')
    A('tl.fromTo(".ring", {z:-600, opacity:0}, {z:0, opacity:1, duration:.9, ease:"expo.out", stagger:.12}, .2);')
    # camera orbit: rotate the whole rig
    A('tl.fromTo("#rig", {rotationY:-35, rotationX:8, scale:.8}, {rotationY:0, rotationX:0, scale:1, duration:4, ease:"expo.out"}, 0);')
    A('tl.to("#rig", {rotationY:25, duration:18, ease:"sine.inOut"}, 4);')
    A('tl.to("#rig", {rotationY:-20, rotationX:6, duration:20, ease:"sine.inOut"}, 22);')
    A('tl.to("#rig", {rotationY:0, rotationX:0, scale:1.08, duration:9, ease:"sine.inOut"}, 42);')
    # particles: two waves (leaky 4.5-28, fixed 30-50)
    for wave, cls, t0, t1, leaky in (("p", "p", 4.5, 28, True), ("q", "g", 30, 50, False)):
        for k, ang, leak_at in PARTS:
            for rep in range(3):
                st = t0 + (k * .45 + rep * 7.2) % (t1 - t0 - 3)
                r0, y0 = _ring_geom(0); x0 = math.cos(ang) * r0 * .55; z0 = math.sin(ang) * r0 * .3
                sel = f"#{wave}{k}"
                if leaky and leak_at is not None:
                    rl, yl = _ring_geom(leak_at)
                    A(f'tl.fromTo("{sel}", {{x:{x0:.0f}, y:{y0 - 120:.0f}, z:{z0:.0f}, opacity:1}}, {{x:{math.cos(ang) * rl * .5:.0f}, y:{yl:.0f}, z:0, duration:{.25 * leak_at + .5:.2f}, ease:"power1.in"}}, {st:.2f});')
                    A(f'tl.to("{sel}", {{x:{math.cos(ang) * 700:.0f}, y:{yl + 260:.0f}, opacity:0, duration:.7, ease:"power2.out"}}, {st + .25 * leak_at + .5:.2f});')
                else:
                    rb, yb = _ring_geom(RINGS - 1)
                    A(f'tl.fromTo("{sel}", {{x:{x0:.0f}, y:{y0 - 120:.0f}, z:{z0:.0f}, opacity:1}}, {{x:0, y:{yb + 260:.0f}, z:0, duration:2.4, ease:"power1.in"}}, {st:.2f});')
                    A(f'tl.to("{sel}", {{opacity:0, duration:.2}}, {st + 2.4:.2f});')
            A(f'tl.set("#{wave}{k}", {{opacity:0}}, 0);')
    for i, (ri, t, ta) in enumerate(LEAKS):
        r, y = _ring_geom(ri)
        A(f'tl.to("#r{ri} i", {{borderColor:"rgba(184,0,240,.95)", duration:.3}}, {ta:.2f});')
        A(f'tl.set("#L{i}", {{left:{(min(540 + r + 20, 600) if i % 2 == 0 else 110):.0f}, top:{640 + y - 30:.0f}}}, 0);')
        A(f'tl.fromTo("#L{i}", {{opacity:0, x:{-40 if i % 2 == 0 else 40}}}, {{opacity:1, x:0, duration:.5, ease:"expo.out"}}, {ta:.2f});')
        A(f'tl.to("#L{i}", {{opacity:0, duration:.3}}, 29.5);')
    for i, (ri, t, ta) in enumerate(FIXES):
        r, y = _ring_geom(ri)
        A(f'tl.to("#r{ri} i", {{borderColor:"rgba(180,255,57,.95)", boxShadow:"0 0 40px rgba(180,255,57,.5)", duration:.3}}, {ta:.2f});')
        A(f'tl.set("#F{i}", {{left:{(min(540 + r + 20, 640) if i % 2 == 0 else 110):.0f}, top:{640 + y - 30:.0f}}}, 0);')
        A(f'tl.fromTo("#F{i}", {{opacity:0, scale:.7}}, {{opacity:1, scale:1, duration:.45, ease:"back.out(2)"}}, {ta:.2f});')
    for i, a, b, t in SUPS:
        A(f'tl.fromTo("#{i}", {{y:50, opacity:0}}, {{y:0, opacity:1, duration:.6, ease:"expo.out"}}, {a + .1:.2f});')
        A(f'tl.to("#{i}", {{opacity:0, duration:.3}}, {b - .3:.2f});')
    A('tl.to("#studiow", {opacity:0, duration:.5}, 50.5);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 51.2);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 52.1);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 52.6);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    m.drone(lib.hz(33), 0, 30, .12)
    prog = [(45, [57, 64, 67, 72]), (41, [53, 60, 64, 69]), (43, [55, 62, 67, 71]), (40, [52, 59, 64, 67])]
    m.score(90, prog, kind="pad", drums="half", start=4, end=29)
    m.score(90, prog, kind="pluck", drums="four", start=30, end=59)
    for i in range(RINGS): m.at(m.fx, m.pop(300 + 40 * i), .3 + .12 * i, .25)
    for _, _, ta in LEAKS: m.at(m.fx, m.glitch(.2), ta, .4); m.at(m.fx, m.whoosh(.6, False), ta + .1, .2)
    for _, _, ta in FIXES: m.at(m.fx, m.coin(), ta, .35)
    m.at(m.fx, m.riser(2), 49, .3); m.at(m.fx, m.impact(), 51.05, .6)
