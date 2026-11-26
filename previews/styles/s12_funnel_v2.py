"""04 v2 · CORONG 3D — strong hook + pop-out graphics.
Hook (frame 0): ad money (lime RM coins) is already pouring into a 3D funnel and leaking out the sides; caption "Bajet iklan kau bocor."
Message: the problem is a leaking funnel (slow page, unclear offer, hard checkout), not the ads; patch it, then add budget."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pop as P

NAME = "LokaDigital Preview 04 v2 · Corong 3D"
SLUG = "04v2-corong-3d"
PILL = "CUSTOMER JOURNEY"

CAPS = [
    ("c0", 0.0, 1.8, "Bajet iklan kau [bocor]."),
    ("c1", 1.8, 4.0, "Setiap [ringgit] masuk..."),
    ("c2", 4.0, 6.5, "...banyak yang [keluar] tepi."),
    ("c3", 6.5, 9.5, "Tambah bajet? Bocor makin [besar]."),
    ("c4", 9.5, 12.5, "Masalahnya bukan [iklan]."),
    ("c5", 12.5, 15.5, "Corong kau yang [bocor]."),
    ("c6", 15.5, 19.0, "Bocor 1: page [lambat]."),
    ("c7", 19.0, 22.5, "Bocor 2: offer tak [jelas]."),
    ("c8", 22.5, 26.0, "Bocor 3: checkout [susah]."),
    ("c9", 26.0, 29.5, "Dia dah nak beli. Tapi [tersangkut]."),
    ("c10", 29.5, 33.0, "Jadi, tampal [dulu]."),
    ("c11", 33.0, 37.0, "Page [laju]."),
    ("c12", 37.0, 41.0, "Offer [jelas]."),
    ("c13", 41.0, 45.0, "Bayar [1-langkah]."),
    ("c14", 45.0, 50.0, "Baru setiap ringgit [sampai]."),
    ("c15", 50.0, 60.0, "Audit corong kau: [DM] LOKADIGITAL."),
]

RINGS = 9
CX, CY = 540, 520          # rig centre in stage coords
LEAKS = [(2, "PAGE LAMBAT", "Loading 8 saat · CONTOH", 15.6, 33.2, "PAGE LAJU"),
         (4, "OFFER TAK JELAS", "Apa aku dapat?", 19.1, 37.2, "OFFER JELAS"),
         (6, "CHECKOUT SUSAH", "6 borang untuk bayar · CONTOH", 22.6, 41.2, "BAYAR 1 LANGKAH")]
NCOIN = 16

def geom(i):
    return 300 - i * 27, -300 + i * 70   # radius, y offset

CSS = P.CSS + """
  #rig { position:absolute; left:540px; top:520px; width:0; height:0; transform-style:preserve-3d; }
  .rg { position:absolute; border-radius:50%; }
  .rg i { position:absolute; inset:0; border-radius:50%; border:10px solid rgba(201,155,255,.55);
          box-shadow:0 0 36px rgba(184,0,240,.45), inset 0 0 30px rgba(184,0,240,.3); }
  .coin { position:absolute; left:-30px; top:-30px; width:60px; height:60px; border-radius:50%; background:radial-gradient(circle at 35% 30%, #e6ff9a, #B4FF39 55%, #7fb81e);
          border:4px solid #e9ffb8; box-shadow:0 0 20px rgba(180,255,57,.8); font:900 22px/52px 'Inter'; text-align:center; color:#07040C; opacity:0; }
  .coin.lk { background:radial-gradient(circle at 35% 30%, #f1b8ff, #B800F0 60%, #6c0090); border-color:#f1b8ff; box-shadow:0 0 20px rgba(184,0,240,.8); color:#fff; }
  #drips { position:absolute; left:0; top:0; width:1080px; height:1000px; overflow:visible; }
  .lc { position:absolute; width:380px; z-index:5; padding:26px 30px; }
  .lc b { display:block; font:900 50px/1 'Inter'; letter-spacing:-.03em; } .lc small { display:block; margin-top:10px; font:700 28px 'Inter'; opacity:.8; }
  #jar { position:absolute; left:340px; top:800px; width:400px; height:190px; border-radius:0 0 40px 40px; border:4px solid rgba(255,255,255,.3); border-top:none; overflow:hidden; opacity:0; }
  #jar i { position:absolute; left:0; right:0; bottom:0; height:100%; background:linear-gradient(180deg,#B4FF39,#7fb81e); transform-origin:50% 100%; }
  #jar span { position:absolute; left:0; right:0; top:60px; text-align:center; font:900 40px 'Inter'; color:#07040C; z-index:2; letter-spacing:.02em; }
  .ctab3 { position:absolute; left:90px; top:280px; width:900px; padding:56px 50px; border-radius:36px; }
  .ctab3 label { display:block; font:800 30px 'Inter'; letter-spacing:.24em; } .ctab3 h2 { margin-top:16px; font:900 120px/0.9 'Inter'; letter-spacing:-.05em; }
  .ctab3 p { margin-top:20px; font:700 34px 'Inter'; opacity:.8; }
  #flash { position:absolute; inset:0; background:#fff; opacity:0; mix-blend-mode:overlay; }
"""

def _rings():
    out = []
    for i in range(RINGS):
        r, y = geom(i)
        out.append(f'<div class="rg" id="r{i}" style="left:{-r}px;top:{y - r * .32}px;width:{2 * r}px;height:{r * .64:.0f}px"><i></i></div>')
    return "".join(out)

def _drips():
    o = []
    for k, (ri, *_r) in enumerate(LEAKS):
        r, y = geom(ri); side = -1 if k % 2 else 1
        x0, y0 = CX + side * r * .95, CY + y
        o.append(f'<path class="drip" id="dp{k}" d="M{x0:.0f} {y0:.0f} C {x0 + side * 120:.0f} {y0 - 10:.0f}, {x0 + side * 220:.0f} {y0 + 80:.0f}, {x0 + side * 260:.0f} {y0 + 330:.0f}" '
                 f'fill="none" stroke="#B800F0" stroke-width="16" stroke-linecap="round" opacity=".85"/>')
    return "".join(o)

def _cards():
    o = []
    for k, (ri, t, sub, ta, tf, fix) in enumerate(LEAKS):
        r, y = geom(ri); side = -1 if k % 2 else 1
        left = 640 if side > 0 else 60
        top = CY + y - 60
        o.append(f'<div class="c3 lc mag" id="L{k}" style="left:{left}px;top:{top:.0f}px"><b>{t}</b><small>{sub}</small><div class="shine"></div></div>')
        o.append(f'<div class="c3 lc lime" id="F{k}" style="left:{left}px;top:{top:.0f}px"><b>✓ {fix}</b><small>Tampal · CONTOH</small><div class="shine"></div></div>')
        o.append(f'<div class="ring" id="sr{k}" style="left:{CX + side * r - 130:.0f}px;top:{CY + y - 130:.0f}px;width:260px;height:260px"></div>')
    return "".join(o)

BODY = f"""
      <div class="stage3d clip" id="st" data-start="0" data-duration="60" data-track-index="2" data-layout-allow-overflow data-layout-ignore><div id="cam" style="position:absolute;inset:0;transform-style:preserve-3d">
        <svg id="drips" viewBox="0 0 1080 1000">{_drips()}</svg>
        <div id="rig">{_rings()}{''.join(f'<div class="coin" id="co{k}">RM</div>' for k in range(NCOIN))}{''.join(f'<div class="coin lk" id="cl{k}">RM</div>' for k in range(NCOIN))}{''.join(f'<div class="coin" id="cg{k}">RM</div>' for k in range(NCOIN))}{''.join(f'<div class="coin" id="ch{k}">RM</div>' for k in range(6))}</div>
        {_cards()}
        <div id="jar"><i id="jfill"></i><span>JUALAN · CONTOH</span></div>
        {P.sparks_html("sa", 14)}{P.sparks_html("sb", 14)}{P.sparks_html("sc", 14)}{P.sparks_html("sd", 18)}
        <div class="c3 ctab3 lime" id="ctab3"><label>AUDIT CUSTOMER JOURNEY</label><h2>DM<br>LOKADIGITAL</h2><p>Tampal bocor dulu. Baru scale.</p><div class="shine"></div></div>
      </div></div>
      <div id="flash" class="clip" data-start="0" data-duration="60" data-track-index="8" data-layout-ignore></div>""" + P.caps(CAPS)

def _coin_paths(j):
    A = j.append
    rt, yt = geom(0); rb, yb = geom(RINGS - 1)
    # leaky phase 0 - 30 s: coins fall, a third escape at a leak ring
    for k in range(NCOIN):
        A(f'tl.set("#co{k}, #cl{k}, #cg{k}", {{opacity:0}}, 0);')
        ang = k * 2.3
        x0 = math.cos(ang) * rt * .55
        for rep in range(5):
            st = (k * .37 + rep * 5.9) % 29.0
            leak = k % 3 == 0 and rep % 2 == 0
            sel = f"#cl{k}" if leak else f"#co{k}"
            if leak:
                li = (k // 3) % 3; ri = LEAKS[li][0]; r, y = geom(ri); side = -1 if li % 2 else 1
                A(f'tl.fromTo("{sel}", {{x:{x0:.0f}, y:{yt - 180:.0f}, opacity:1, scale:.9}}, {{x:{side * r * .9:.0f}, y:{y:.0f}, duration:{.35 + ri * .12:.2f}, ease:"power1.in", immediateRender:false}}, {st:.2f});')
                A(f'tl.to("{sel}", {{x:{side * (r + 280):.0f}, y:{y + 360:.0f}, rotation:{side * 200}, opacity:0, duration:.8, ease:"power2.in"}}, {st + .35 + ri * .12:.2f});')
            else:
                A(f'tl.fromTo("{sel}", {{x:{x0:.0f}, y:{yt - 180:.0f}, opacity:1, scale:.9}}, {{x:{math.cos(ang) * 30:.0f}, y:{yb + 60:.0f}, scale:.55, duration:1.6, ease:"power1.in", immediateRender:false}}, {st:.2f});')
                A(f'tl.to("{sel}", {{opacity:0, duration:.15}}, {st + 1.6:.2f});')
    # fixed phase 41.6 - 50 s: everything reaches the jar
    for k in range(NCOIN):
        ang = k * 2.3; x0 = math.cos(ang) * rt * .55
        for rep in range(2):
            st = 41.6 + (k * .26 + rep * 4.0) % 8.0
            A(f'tl.fromTo("#cg{k}", {{x:{x0:.0f}, y:{yt - 180:.0f}, opacity:1, scale:.9}}, {{x:{math.cos(ang) * 20:.0f}, y:{yb + 150:.0f}, scale:.5, duration:1.5, ease:"power1.in", immediateRender:false}}, {st:.2f});')
            A(f'tl.to("#cg{k}", {{opacity:0, duration:.12}}, {st + 1.5:.2f});')

def _js():
    j = []; A = j.append
    for i in range(RINGS):
        A(f'tl.set("#r{i}", {{opacity:1}}, 0);')
    A('tl.fromTo("#rig", {rotationX:14, rotationY:-18, scale:1.04}, {rotationX:8, rotationY:14, scale:1, duration:15, ease:"sine.inOut"}, 0);')
    A('tl.fromTo("#drips path", {strokeDasharray:600, strokeDashoffset:0}, {strokeDashoffset:-600, duration:2.4, ease:"none", repeat:11}, 0);')
    _coin_paths(j)
    rt, yt = geom(0)
    for k in range(6):
        x0 = (k - 2.5) * 60; y0 = yt - 260 + k * 70
        A(f'tl.set("#ch{k}", {{x:{x0:.0f}, y:{y0:.0f}, opacity:1, scale:1}}, 0);')
        A(f'tl.to("#ch{k}", {{x:{(k % 2 * 2 - 1) * 330 if k % 3 == 0 else x0 * .2:.0f}, y:{yt + 260 + k * 40:.0f}, opacity:0, duration:{.9 + k * .12:.2f}, ease:"power1.in"}}, 0);')
    # hook punch-in on the first leak
    A('tl.fromTo("#cam", {scale:1.12}, {scale:1, duration:1.8, ease:"expo.out"}, 0);')
    A(P.ring("#sr0", 0.9, .8))
    A('tl.to("#cam", {scale:1.08, duration:3, ease:"sine.inOut"}, 6.5);')
    A('tl.to("#cam", {scale:1, duration:1, ease:"expo.out"}, 9.5);')
    # leak call-outs
    for k, (ri, t, sub, ta, tf, fix) in enumerate(LEAKS):
        r, y = geom(ri); side = -1 if k % 2 else 1
        A(f'tl.to("#r{ri} i", {{borderColor:"rgba(184,0,240,1)", boxShadow:"0 0 60px rgba(184,0,240,.9)", duration:.3}}, {ta:.2f});')
        A(P.ring(f"#sr{k}", ta, .7))
        A(P.pop(f"#L{k}", ta + .1, ry=(-60 * side), z=-700, scale=.15, ease="back.out(2.4)"))
        A(P.shine(f"#L{k}", ta + .7, 500))
        A(P.floaty(f"#L{k}", ta + .7, 29.2, amp=10, rot=(5 * side)))
        A(f'tl.to("#cam", {{y:{-y * .2:.0f}, scale:1.08, duration:.6, ease:"expo.out"}}, {ta:.2f});')
        A(f'tl.to("#L{k}", {{z:50, duration:.3}}, {ta + .7:.2f});')
        A(f'tl.to("#cam", {{x:0, y:0, scale:1, duration:.8, ease:"power2.inOut"}}, {ta + 2.6:.2f});')
    A('tl.to("#L0, #L1, #L2", {opacity:.35, duration:.4}, 29.4);')
    # patches
    for k, (ri, t, sub, ta, tf, fix) in enumerate(LEAKS):
        r, y = geom(ri); side = -1 if k % 2 else 1
        A(f'tl.to("#L{k}", {{opacity:0, rotationY:{90 * side}, duration:.25, ease:"power3.in"}}, {tf - .25:.2f});')
        A(P.pop(f"#F{k}", tf, ry=(-70 * side), z=-700, scale=.15, ease="back.out(2.6)"))
        A(f'tl.to("#r{ri} i", {{borderColor:"rgba(180,255,57,1)", boxShadow:"0 0 60px rgba(180,255,57,.9)", duration:.3}}, {tf:.2f});')
        A(f'tl.to("#dp{k}", {{opacity:0, duration:.4}}, {tf:.2f});')
        A('tl.fromTo("#flash", {opacity:.4}, {opacity:0, duration:.25, immediateRender:false}, ' + f'{tf + .05:.2f});')
        j += P.burst(["sa", "sb", "sc"][k], int(CX + side * r), int(CY + y), tf + .1, n=14, r1=300)
        A(P.shine(f"#F{k}", tf + .6, 500))
        A(f'tl.to("#F{k}", {{z:50, duration:.3}}, {tf + .6:.2f});')
        A(P.floaty(f"#F{k}", tf + .6, 49.6, amp=8, rot=(4 * side)))
    for i in range(RINGS):
        A(f'tl.to("#r{i} i", {{borderColor:"rgba(180,255,57,.85)", duration:.4}}, {44.6 + i * .06:.2f});')
    # jar fills
    A(P.pop("#jar", 44.8, z=-400, scale=.4))
    A('tl.fromTo("#jfill", {scaleY:0}, {scaleY:1, duration:5, ease:"power1.inOut"}, 45.2);')
    A('tl.to("#rig, #F0, #F1, #F2, #jar, #drips", {opacity:0, z:-500, duration:.4, ease:"power3.in"}, 49.6);')
    # CTA
    A(P.pop("#ctab3", 50.1, z=-1100, rx=-60, scale=.1, ease="back.out(2.2)", dur=.8))
    A('tl.fromTo("#flash", {opacity:.5}, {opacity:0, duration:.3, immediateRender:false}, 50.3);')
    j += P.burst("sd", 540, 500, 50.4, n=18, r1=520)
    A(P.shine("#ctab3", 51.3, 1000)); A(P.shine("#ctab3", 55.0, 1000))
    A(P.floaty("#ctab3", 51.0, 59.6, amp=12, rot=5, period=2.6))
    j += P.caps_js(CAPS, frame0=True)
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    m.drone(lib.hz(31), 0, 29.5, .13)
    for k in range(24): m.at(m.fx, m.tick(), .1 + k * .35, .18)
    m.at(m.fx, m.thud(), 0.02, .5); m.at(m.fx, m.whoosh(.5, False), .9, .3)
    prog = [(45, [57, 64, 67, 72]), (41, [53, 60, 64, 69]), (43, [55, 62, 67, 71]), (40, [52, 59, 64, 67])]
    m.score(96, prog, kind="pad", drums="half", start=6.5, end=29.4)
    for ri, t, sub, ta, tf, fix in LEAKS:
        m.at(m.fx, m.glitch(.2), ta, .45); m.at(m.fx, m.pop(400), ta + .15, .45)
    m.at(m.fx, m.riser(3.2), 29.8, .25)
    m.score(96, prog, kind="pluck", drums="four", start=33.0, end=59.2)
    for ri, t, sub, ta, tf, fix in LEAKS:
        m.at(m.fx, m.impact(), tf, .5); m.at(m.fx, m.coin(), tf + .1, .45)
    for k in range(10): m.at(m.fx, m.coin(), 45.4 + k * .45, .18)
    m.at(m.fx, m.riser(1.4), 48.7, .3); m.at(m.fx, m.impact(), 50.12, .8)
    for t in (15.5, 19.0, 22.5, 26.0, 29.5): m.at(m.fx, m.tick(), t, .3)
