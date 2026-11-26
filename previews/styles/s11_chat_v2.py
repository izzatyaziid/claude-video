"""06 v2 · DRAMA CHAT — rebuilt for a strong hook and pop-out 3D graphics.
Hook (frame 0): the customer's price question is already on screen; by 1.7 s the owner answers "RM90.", by 3.4 s the customer vanishes.
Message: answering with only the price makes customers compare and leave; ask, show value, then price + invite."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pop as P

NAME = "LokaDigital Preview 06 v2 · Drama Chat"
SLUG = "06v2-drama-chat"
PILL = "CONTOH · KEDAI KEK"

CAPS = [
    ("c0", 0.0, 1.7, "Pelanggan tanya [harga]."),
    ("c1", 1.7, 3.4, "Kau jawab [RM90.]"),
    ("c2", 3.4, 5.6, "Lepas tu dia [hilang]."),
    ("c3", 5.6, 9.0, "Sebab kau buat dia [banding]."),
    ("c4", 9.0, 12.5, "Yang paling [murah] menang."),
    ("c5", 12.5, 15.5, "Owner yang laku buat [ni:]"),
    ("c6", 15.5, 19.5, "Satu: [tanya] dulu."),
    ("c7", 19.5, 24.0, "[Kenal] dia sebelum sebut harga."),
    ("c8", 24.0, 28.5, "Dua: tunjuk [nilai]."),
    ("c9", 28.5, 33.0, "Bagi dia sebab untuk [pilih] kau."),
    ("c10", 33.0, 37.5, "Tiga: harga + [ajak]."),
    ("c11", 37.5, 42.0, "Dia tak banding. Dia [tempah]."),
    ("c12", 42.0, 46.5, "Produk sama. Harga [sama]."),
    ("c13", 46.5, 51.0, "Bezanya: [cara] kau jawab."),
    ("c14", 51.0, 60.0, "Nak skrip DM yang [jual?]"),
]

TAGS = [("RM85", 120, 60), ("RM79", 700, 40), ("RM95", 60, 520), ("RM88", 760, 500), ("RM92", 420, 700)]

CSS = P.CSS + """
  .bub { position:absolute; padding:34px 42px; border-radius:46px; font:700 56px/1.18 'Inter'; letter-spacing:-.02em; opacity:0; }
  .bub.in { background:#2a2036; color:#fff; border-bottom-left-radius:14px; box-shadow:0 40px 90px rgba(0,0,0,.6); }
  .bub.out { background:var(--g); color:var(--ink); border-bottom-right-radius:14px; box-shadow:0 40px 90px rgba(0,0,0,.55), 0 0 70px rgba(180,255,57,.4); }
  .seen { position:absolute; font:700 34px 'Inter'; color:var(--grey); opacity:0; }
  .tag { position:absolute; padding:22px 34px; border-radius:20px; font:900 64px 'Inter'; letter-spacing:-.03em; }
  .tag small { display:block; font:700 22px 'Inter'; letter-spacing:.24em; opacity:.7; }
  .hdr3 { position:absolute; left:80px; top:10px; padding:16px 30px; border-radius:99px; font:800 34px 'Inter'; letter-spacing:.12em; }
  .chip { position:absolute; padding:24px 34px; border-radius:24px; font:800 46px 'Inter'; letter-spacing:-.02em; }
  .photo { position:absolute; left:60px; top:130px; width:430px; height:460px; border-radius:30px;
           background:radial-gradient(60% 55% at 50% 45%, #B800F0, #46096B 60%, #240538); display:flex; align-items:flex-end; padding:26px; font:700 26px 'Inter'; letter-spacing:.2em; color:var(--mist); }
  .cake { position:absolute; left:105px; top:140px; width:220px; height:150px; border-radius:20px 20px 30px 30px; background:#D9D0F0; box-shadow:0 -24px 0 -6px #B4FF39 inset; }
  .stamp { position:absolute; left:190px; top:600px; width:700px; padding:40px; border-radius:34px; text-align:center; font:900 96px/0.95 'Inter'; letter-spacing:-.04em; }
  .stamp small { display:block; margin-top:14px; font:800 30px 'Inter'; letter-spacing:.24em; }
  .vs { position:absolute; top:220px; width:440px; height:520px; padding:40px 34px; }
  .vs b { display:block; font:800 30px 'Inter'; letter-spacing:.2em; } .vs h3 { margin-top:26px; font:900 72px/0.95 'Inter'; letter-spacing:-.04em; }
  .vs p { margin-top:24px; font:700 40px/1.2 'Inter'; }
  .ctab3 { position:absolute; left:90px; top:300px; width:900px; padding:56px 50px; border-radius:36px; }
  .ctab3 label { display:block; font:800 30px 'Inter'; letter-spacing:.24em; } .ctab3 h2 { margin-top:16px; font:900 120px/0.9 'Inter'; letter-spacing:-.05em; }
  .ctab3 p { margin-top:20px; font:700 34px 'Inter'; opacity:.8; }
  #flash { position:absolute; inset:0; background:#fff; opacity:0; mix-blend-mode:overlay; }
"""

def _stage():
    tags = "".join(f'<div class="c3 tag {"mag" if i % 2 else ""}" id="tg{i}" style="left:{x}px;top:{y}px">{t}<small>KEDAI LAIN · CONTOH</small><div class="shine"></div></div>' for i, (t, x, y) in enumerate(TAGS))
    return f"""
      <div class="stage3d clip" id="st" data-start="0" data-duration="60" data-track-index="2" data-layout-allow-overflow data-layout-ignore><div id="cam" style="position:absolute;inset:0;transform-style:preserve-3d">
        <!-- hook -->
        <div class="bub in" id="q" style="left:70px;top:200px;width:900px;font-size:70px">Kak, kek coklat 1kg berapa?</div>
        <div class="bub out c3" id="a" style="left:420px;top:480px;font-size:130px;padding:30px 60px">RM90.<div class="shine"></div></div>
        <div class="seen" id="seen" style="left:460px;top:740px">Dilihat ✓✓ · 3 hari lalu</div>
        <div class="c3 tag lime" id="tgc" style="left:380px;top:330px">RM90<small>KEDAI KAU</small><div class="shine"></div></div>
        {tags}
        {P.sparks_html("sa", 14)}{P.sparks_html("sb", 16)}{P.sparks_html("sc", 18)}
        <div class="ring" id="rg1" style="left:340px;top:240px;width:400px;height:400px"></div>
        <div class="ring" id="rg2" style="left:290px;top:520px;width:500px;height:500px"></div>
        <!-- three steps -->
        <div class="c3 hdr3 mag" id="h1">01 · TANYA DULU</div>
        <div class="c3 hdr3 mag" id="h2">02 · TUNJUK NILAI</div>
        <div class="c3 hdr3 lime" id="h3">03 · HARGA + AJAK</div>
        <div class="bub out" id="s1a" style="left:300px;top:130px">Untuk majlis apa ya?</div>
        <div class="bub in" id="s1b" style="left:70px;top:320px">Birthday anak, umur 6.</div>
        <div class="c3 chip" id="k1" style="left:90px;top:560px">Birthday</div>
        <div class="c3 chip" id="k2" style="left:400px;top:600px">Sabtu</div>
        <div class="c3 chip lime" id="k3" style="left:640px;top:540px">6 tahun</div>
        <div class="c3 photo" id="ph"><div class="cake"></div>GAMBAR KEK · CONTOH<div class="shine"></div></div>
        <div class="c3 chip lime" id="v1" style="left:540px;top:150px;max-width:480px">Lembap sampai esok</div>
        <div class="c3 chip" id="v2" style="left:540px;top:360px;max-width:480px">Tulis nama free</div>
        <div class="c3 chip mag" id="v3" style="left:540px;top:540px;max-width:480px">Siap 2 hari</div>
        <div class="bub out" id="s3a" style="left:170px;top:120px;width:820px">1kg RM90. Nak saya lock Sabtu?</div>
        <div class="bub in" id="s3b" style="left:70px;top:360px">Ok lock!</div>
        <div class="c3 stamp lime" id="stp">✓ DITEMPAH<small>SABTU · 8 MALAM · CONTOH</small><div class="shine"></div></div>
        <!-- recap -->
        <div class="c3 vs" id="vl" style="left:80px"><b style="color:var(--grey)">HARGA JE</b><h3 style="color:var(--grey)">“RM90.”</h3><p style="color:var(--grey)">→ Dilihat.<br>→ Senyap.</p></div>
        <div class="c3 vs lime" id="vr" style="left:560px"><b>NILAI DULU</b><h3>“Untuk majlis apa?”</h3><p>→ Ditempah.<br>→ Datang lagi.</p><div class="shine"></div></div>
        <!-- cta -->
        <div class="c3 ctab3 lime" id="ctab3"><label>SKRIP DM & SALES</label><h2>DM<br>LOKADIGITAL</h2><p>Chat yang jadi tempahan.</p><div class="shine"></div></div>
        {P.sparks_html("sd", 18)}
      </div></div>
      <div id="flash" class="clip" data-start="0" data-duration="60" data-track-index="8" data-layout-ignore></div>"""

BODY = _stage() + P.caps(CAPS)

def _js():
    j = []; A = j.append
    # ---- HOOK: frame 0 already shows the question + caption
    A(P.pop("#q", 0, frame0=True))
    A('tl.fromTo("#q", {scale:1.08}, {scale:1, duration:.5, ease:"expo.out"}, 0);')
    A(P.pop("#a", 1.7, z=-700, scale=.2, ease="back.out(2.6)"))
    A('tl.fromTo("#flash", {opacity:.5}, {opacity:0, duration:.25, immediateRender:false}, 1.75);')
    A(P.shine("#a", 2.0, 500))
    A('tl.fromTo("#seen", {opacity:0, x:-20}, {opacity:1, x:0, duration:.3}, 2.6);')
    A('tl.to("#q", {opacity:.12, z:-600, rotationY:25, y:-60, filter:"blur(6px)", duration:1.2, ease:"power2.in"}, 3.4);')
    A('tl.to("#a", {rotation:-6, y:30, duration:.4, ease:"back.in(2)"}, 3.5);')
    A('tl.to("#cam", {z:-120, duration:2, ease:"power2.out"}, 3.4);')
    A('tl.to("#a, #seen, #q", {opacity:0, duration:.3}, 5.5);')
    # ---- comparison: price tags burst around
    A('tl.to("#cam", {z:0, duration:.6, ease:"expo.out"}, 5.6);')
    A(P.pop("#tgc", 5.6, z=-900, scale=.1, ease="back.out(2.4)"))
    j += P.burst("sa", 540, 430, 5.75, n=14)
    A(P.ring("#rg1", 5.75))
    for i in range(len(TAGS)):
        A(P.pop(f"#tg{i}", 6.0 + i * .28, z=-600, rx=-30, ry=(-40 if i % 2 else 40), scale=.2))
        A(P.floaty(f"#tg{i}", 6.6 + i * .28, 12.2, amp=16, rot=(6 if i % 2 else -6)))
    A(P.floaty("#tgc", 6.2, 9.0, amp=10, rot=4))
    # cheapest wins: RM79 grows and glows, ours falls
    A('tl.to("#tg1", {scale:1.45, x:-330, y:330, z:150, backgroundColor:"#B4FF39", color:"#07040C", duration:.6, ease:"back.out(2)"}, 9.1);')
    A('tl.to("#tgc", {y:420, rotation:14, opacity:.25, duration:.6, ease:"power3.in"}, 9.2);')
    A('tl.to("#tg0, #tg2, #tg3, #tg4", {opacity:.2, z:-300, duration:.5}, 9.2);')
    A(P.shine("#tg1", 9.6, 300))
    A('tl.to("#tg0, #tg1, #tg2, #tg3, #tg4, #tgc", {opacity:0, scale:.5, z:-500, duration:.35, ease:"power3.in"}, 12.2);')
    # ---- "owner yang laku buat ni": three headers flip in as a preview
    for i, h in enumerate(("#h1", "#h2", "#h3")):
        A(f'tl.fromTo("{h}", {{opacity:0, rotationX:-90, y:{120 + i * 150}, x:{100 + i * 40}}}, {{opacity:1, rotationX:0, y:{120 + i * 150}, x:{100 + i * 40}, duration:.45, ease:"back.out(2)"}}, {12.7 + i * .35:.2f});')
    A('tl.to("#h2, #h3", {opacity:0, duration:.25}, 15.2);')
    A('tl.to("#h1", {x:0, y:0, duration:.5, ease:"expo.inOut"}, 15.2);')
    # ---- step 1
    A(P.pop("#s1a", 15.8, ry=-30))
    A(P.pop("#s1b", 17.3, ry=30))
    for i, k in enumerate(("#k1", "#k2", "#k3")):
        A(P.pop(k, 19.6 + i * .4, z=-700, rx=-60, scale=.1, ease="back.out(3)"))
        A(P.floaty(k, 20.2 + i * .4, 23.6, amp=12, rot=(5 if i % 2 else -5)))
    j += P.burst("sb", 540, 640, 20.0, n=16, r1=420)
    A('tl.to("#h1, #s1a, #s1b, #k1, #k2, #k3", {opacity:0, z:-400, duration:.35, ease:"power3.in"}, 23.7);')
    # ---- step 2
    A('tl.fromTo("#h2", {opacity:0, rotationX:-90, x:0, y:0}, {opacity:1, rotationX:0, x:0, y:0, duration:.45, ease:"back.out(2)", immediateRender:false}, 24.0);')
    A(P.pop("#ph", 24.4, ry=-35, z=-800, scale=.2))
    A(P.shine("#ph", 25.2, 600))
    A(P.floaty("#ph", 25.0, 32.6, amp=10, rot=-5))
    for i, v in enumerate(("#v1", "#v2", "#v3")):
        A(P.pop(v, 26.0 + i * .9, ry=-70, z=-500, scale=.2, ease="back.out(2.4)"))
        A(P.floaty(v, 26.6 + i * .9, 32.6, amp=12, rot=(6 if i % 2 else -6)))
    A('tl.to("#h2, #ph, #v1, #v2, #v3", {opacity:0, z:-400, duration:.35, ease:"power3.in"}, 32.7);')
    # ---- step 3
    A('tl.fromTo("#h3", {opacity:0, rotationX:-90, x:0, y:0}, {opacity:1, rotationX:0, x:0, y:0, duration:.45, ease:"back.out(2)", immediateRender:false}, 33.0);')
    A(P.pop("#s3a", 33.4, ry=-30))
    A(P.pop("#s3b", 35.4, ry=30))
    A(P.pop("#stp", 37.6, z=-1000, scale=.1, rx=-70, ease="back.out(2.8)"))
    A('tl.fromTo("#flash", {opacity:.6}, {opacity:0, duration:.3, immediateRender:false}, 37.7);')
    j += P.burst("sc", 540, 760, 37.7, n=18, r1=480)
    A(P.ring("#rg2", 37.7, .9))
    A(P.shine("#stp", 38.3, 800))
    A(P.floaty("#stp", 38.3, 41.6, amp=10, rot=4))
    A('tl.to("#h3, #s3a, #s3b, #stp", {opacity:0, z:-400, duration:.35, ease:"power3.in"}, 41.7);')
    # ---- recap
    A(P.pop("#vl", 42.2, ry=50, z=-600, scale=.3))
    A(P.pop("#vr", 42.7, ry=-50, z=-600, scale=.3))
    A('tl.to("#vl", {rotationY:18, z:-120, opacity:.6, duration:1.2, ease:"power2.inOut"}, 46.5);')
    A('tl.to("#vr", {rotationY:-10, z:120, scale:1.06, duration:1.2, ease:"power2.inOut"}, 46.5);')
    A(P.shine("#vr", 47.4, 500))
    A('tl.to("#vl, #vr", {opacity:0, z:-400, duration:.35, ease:"power3.in"}, 50.6);')
    # ---- CTA
    A(P.pop("#ctab3", 51.0, z=-1100, rx=-60, scale=.1, ease="back.out(2.2)", dur=.8))
    j += P.burst("sd", 540, 500, 51.3, n=18, r1=520)
    A('tl.fromTo("#flash", {opacity:.5}, {opacity:0, duration:.3, immediateRender:false}, 51.2);')
    A(P.shine("#ctab3", 52.2, 1000)); A(P.shine("#ctab3", 55.5, 1000))
    A(P.floaty("#ctab3", 52.0, 59.6, amp=12, rot=5, period=2.6))
    # caption band
    j += P.caps_js(CAPS, frame0=True)
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    m.at(m.fx, m.pop(700), 0.02, .5)
    m.at(m.fx, m.impact(), 1.72, .7)
    m.at(m.fx, m.tick(), 2.6, .5); m.at(m.fx, m.tick(), 2.75, .5)
    m.drone(lib.hz(33), 3.2, 9.0, .14)
    m.at(m.fx, m.whoosh(1.2, False), 3.4, .4)
    m.at(m.fx, m.thud(), 5.6, .6)
    for i in range(len(TAGS)): m.at(m.fx, m.pop(500 + 90 * i), 6.0 + i * .28 + .05, .35)
    m.at(m.fx, m.coin(), 9.1, .4); m.at(m.fx, m.whoosh(.5, False), 9.2, .3)
    prog = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
    m.score(100, prog, kind="pluck", drums="four", start=12.4, end=59.2)
    for i in range(3): m.at(m.fx, m.whoosh(.35), 12.7 + i * .35, .25)
    for t in (15.8, 17.3, 33.4, 35.4): m.at(m.fx, m.pop(1000), t + .05, .4)
    for i in range(3): m.at(m.fx, m.pop(800 + 120 * i), 19.6 + i * .4 + .05, .4)
    m.at(m.fx, m.whoosh(.6), 24.4, .35)
    for i in range(3): m.at(m.fx, m.pop(700 + 100 * i), 26.0 + i * .9 + .05, .4)
    m.at(m.fx, m.riser(1.6), 36.0, .3); m.at(m.fx, m.impact(), 37.62, .7)
    m.at(m.fx, m.whoosh(.6), 42.2, .3); m.at(m.fx, m.whoosh(.6), 42.7, .3)
    m.at(m.fx, m.riser(2.0), 49.0, .35); m.at(m.fx, m.impact(), 51.02, .8)
    for t in (15.5, 19.5, 24.0, 28.5, 33.0, 37.5, 42.0, 46.5): m.at(m.fx, m.tick(), t, .3)
