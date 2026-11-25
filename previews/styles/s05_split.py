"""05 SPLIT-SCREEN — two identical shops, same product, same price, side by side; only the offer and the hook differ.
Idea: the product isn't the problem; the offer and the first 3 seconds of the ad are."""
NAME = "LokaDigital Preview 05 · Split-screen"
SLUG = "05-split-screen"
PILL = "SEBELAH-MENYEBELAH"

CSS = """
  #split { position:absolute; left:0; top:420px; width:1080px; height:1160px; }
  .half { position:absolute; top:0; width:540px; height:1160px; overflow:hidden; }
  #L { left:0; } #R { left:540px; }
  .half .bgc { position:absolute; inset:0; }
  #L .bgc { background:linear-gradient(180deg,#141018,#0b0810); }
  #R .bgc { background:linear-gradient(180deg,#1b0a2a,#0b0810); }
  #divider { position:absolute; left:538px; top:420px; width:4px; height:1160px; background:var(--g); box-shadow:0 0 30px rgba(180,255,57,.7); }
  .hd { position:absolute; left:0; right:0; top:30px; text-align:center; font:800 34px 'Inter'; letter-spacing:.24em; }
  #L .hd { color:var(--grey); } #R .hd { color:var(--g); }
  .ad { position:absolute; left:40px; right:40px; top:110px; height:620px; border-radius:30px; background:#100c16; border:2px solid var(--line); overflow:hidden; }
  .ad .img { position:absolute; left:0; right:0; top:0; height:330px; }
  #L .ad .img { background:radial-gradient(60% 60% at 50% 55%, #3a2d4a, #1a1422); }
  #R .ad .img { background:radial-gradient(60% 60% at 50% 55%, #7B16B8, #240538); }
  .cup { position:absolute; left:50%; top:90px; width:150px; height:170px; margin-left:-75px; border-radius:0 0 50px 50px; background:#D9D0F0; }
  .cup:after { content:""; position:absolute; right:-46px; top:30px; width:50px; height:70px; border:14px solid #D9D0F0; border-left:none; border-radius:0 40px 40px 0; }
  .ad .cap { position:absolute; left:28px; right:28px; top:356px; font:800 40px/1.12 'Inter'; letter-spacing:-.02em; }
  .ad .px { position:absolute; left:28px; bottom:28px; font:700 30px 'Inter'; color:var(--mist); }
  .ad .btn { position:absolute; right:28px; bottom:22px; padding:12px 22px; border-radius:14px; font:800 26px 'Inter'; }
  #L .btn { background:#2a2233; color:var(--mist); } #R .btn { background:var(--g); color:var(--ink); }
  .meter { position:absolute; left:40px; right:40px; top:780px; }
  .meter .lab { font-size:24px; letter-spacing:.24em; }
  .bar { margin-top:16px; height:40px; border-radius:20px; background:rgba(255,255,255,.06); overflow:hidden; }
  .bar i { display:block; height:100%; border-radius:20px; transform-origin:0 50%; }
  #L .bar i { background:#3a2d4a; } #R .bar i { background:var(--g); }
  .people { position:absolute; left:40px; right:40px; top:900px; display:flex; flex-wrap:wrap; gap:14px; }
  .people span { width:56px; height:56px; border-radius:50%; background:#3a2d4a; opacity:0; }
  #R .people span { background:var(--g); }
  .sup { position:absolute; left:96px; right:96px; top:1610px; font:900 76px/0.98 'Inter'; letter-spacing:-.045em; opacity:0; }
  .same { position:absolute; left:0; right:0; top:1000px; text-align:center; font:900 120px/0.95 'Inter'; letter-spacing:-.05em; opacity:0; }
  .diffc { position:absolute; left:96px; right:96px; padding:34px 40px; border-radius:26px; background:var(--glass); border:2px solid var(--line); opacity:0; }
  .diffc b { font:900 84px 'Inter'; letter-spacing:-.03em; color:var(--g); } .diffc p { margin-top:18px; font:600 42px/1.25 'Inter'; color:var(--mist); }
  .diffc .vs { margin-top:34px; display:flex; flex-direction:column; gap:18px; font:800 50px/1.15 'Inter'; letter-spacing:-.02em; }
  .diffc .vs s { color:var(--grey); } .diffc .vs u { text-decoration:none; color:#fff; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

def half(side, hd, cap, btn):
    return f"""<div class="half" id="{side}"><div class="bgc"></div><div class="hd">{hd}</div>
      <div class="ad"><div class="img"><div class="cup"></div></div><div class="cap">{cap}</div><div class="px">RM12</div><div class="btn">{btn}</div></div>
      <div class="meter"><div class="lab">PELANGGAN · CONTOH</div><div class="bar"><i></i></div></div>
      <div class="people">{"<span></span>" * 12}</div></div>"""

BODY = f"""
      <div id="splitw" class="clip" data-start="0" data-duration="27" data-track-index="1" data-layout-allow-overflow>
        <div id="split">{half("L", "KEDAI A", "Kopi susu. Sedap. RM12.", "Beli")}{half("R", "KEDAI B", "Pagi kau sibuk? Kopi siap dalam 2 minit, tunggu di kaunter.", "Tempah dulu")}</div>
        <div id="divider"></div>
      </div>
      <div class="same clip" id="same" data-start="1.0" data-duration="4.5" data-track-index="2">Produk <span class="gr">sama.</span><br>Harga <span class="gr">sama.</span></div>
      <div class="sup clip" id="u1" data-start="15" data-duration="11.5" data-track-index="3">Kenapa satu <span class="gr">laku?</span></div>
      <div class="diffc clip" id="d1" data-start="27.4" data-duration="9.6" data-track-index="4" style="top:640px">
        <b>01 · OFFER</b><p>Apa pelanggan dapat, bukan apa kau jual.</p>
        <div class="vs"><s>"Kopi susu. RM12."</s><u>"Siap dalam 2 minit. Tempah dulu."</u></div></div>
      <div class="diffc clip" id="d2" data-start="37.2" data-duration="9.6" data-track-index="4" style="top:640px">
        <b>02 · HOOK</b><p>Ayat pertama cakap masalah dia, bukan nama produk.</p>
        <div class="vs"><s>"Kopi susu sedap."</s><u>"Pagi kau sibuk?"</u></div></div>
      <div class="sup clip" id="u2" data-start="47" data-duration="5.5" data-track-index="3" style="top:1000px">Jangan tukar produk.<br><span class="gr">Tukar offer & hook.</span></div>
      <div id="cta" class="clip" data-start="52.6" data-duration="7.4" data-track-index="5">
        <div class="h"><span class="el">PRODUK SAMA.</span><br><span class="el gr">JUALAN</span><br><span class="el gr">BERBEZA.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>OFFER & CREATIVE HOOK</label><small>Untuk iklan yang laku</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    A('tl.fromTo("#same", {scale:1.3, opacity:0}, {scale:1, opacity:1, duration:.6, ease:"expo.out"}, 1.1);')
    A('tl.to("#same", {opacity:0, duration:.3}, 5.1);')
    A('tl.fromTo("#L", {xPercent:-100}, {xPercent:0, duration:.8, ease:"expo.out"}, 5.4);')
    A('tl.fromTo("#R", {xPercent:100}, {xPercent:0, duration:.8, ease:"expo.out"}, 5.4);')
    A('tl.fromTo("#divider", {scaleY:0}, {scaleY:1, duration:.8, ease:"expo.inOut"}, 5.4);')
    A('tl.fromTo(".ad", {y:60, opacity:0}, {y:0, opacity:1, duration:.6, ease:"expo.out", stagger:.1}, 6.2);')
    A('tl.fromTo("#L .bar i", {scaleX:0}, {scaleX:.22, duration:6, ease:"power2.out"}, 8.5);')
    A('tl.fromTo("#R .bar i", {scaleX:0}, {scaleX:.86, duration:6, ease:"power2.out"}, 8.5);')
    A('tl.fromTo("#L .people span:nth-child(-n+3)", {scale:0, opacity:0}, {scale:1, opacity:1, duration:.3, ease:"back.out(2)", stagger:2.0}, 8.8);')
    # only first 3 of L appear within window: cap by fading the rest back
    A('tl.fromTo("#R .people span", {scale:0, opacity:0}, {scale:1, opacity:1, duration:.3, ease:"back.out(2)", stagger:.45}, 8.8);')
    A('tl.to("#split", {scale:1.06, duration:12, ease:"sine.inOut"}, 14);')
    A('tl.fromTo("#u1", {y:50, opacity:0}, {y:0, opacity:1, duration:.6, ease:"expo.out"}, 15.1);')
    A('tl.to("#L", {xPercent:-100, duration:.6, ease:"power3.in"}, 26.4);')
    A('tl.to("#R", {xPercent:100, duration:.6, ease:"power3.in"}, 26.4);')
    for d, t in (("d1", 27.4), ("d2", 37.2)):
        A(f'tl.fromTo("#{d}", {{rotationY:-50, x:-120, opacity:0, transformPerspective:1200}}, {{rotationY:0, x:0, opacity:1, duration:.8, ease:"expo.out"}}, {t + .05:.2f});')
        A(f'tl.fromTo("#{d} s", {{opacity:0}}, {{opacity:1, duration:.4}}, {t + 1.6:.2f});')
        A(f'tl.fromTo("#{d} s", {{textDecoration:"none"}}, {{textDecoration:"line-through", duration:.01}}, {t + 3.2:.2f});')
        A(f'tl.fromTo("#{d} u", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:.5, ease:"expo.out"}}, {t + 3.6:.2f});')
        A(f'tl.to("#{d}", {{rotationY:50, x:120, opacity:0, duration:.5, ease:"power3.in", transformPerspective:1200}}, {t + 9.0:.2f});')
    A('tl.fromTo("#u2", {y:50, opacity:0}, {y:0, opacity:1, duration:.6, ease:"expo.out"}, 47.1);')
    A('tl.to("#u2", {opacity:0, duration:.3}, 52.2);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 52.8);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 53.7);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 54.2);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(48, [60, 64, 67, 71]), (45, [57, 60, 64, 67]), (41, [57, 60, 65, 69]), (43, [55, 59, 62, 67])]
    m.score(110, prog, kind="pluck", drums="four", start=5.4, end=59)
    m.at(m.fx, m.thud(), 1.1, .6)
    m.at(m.fx, m.whoosh(.7), 5.3, .4); m.at(m.fx, m.whoosh(.6, False), 26.4, .4)
    for k in range(3): m.at(m.fx, m.pop(500), 8.8 + 2 * k, .2)
    for k in range(12): m.at(m.fx, m.pop(900 + 30 * k), 8.8 + .45 * k, .18)
    for t in (27.4, 37.2):
        m.at(m.fx, m.whoosh(.6), t, .35); m.at(m.fx, m.glitch(.12), t + 3.2, .3); m.at(m.fx, m.coin(), t + 3.6, .35)
    m.at(m.fx, m.riser(1.8), 50.8, .3); m.at(m.fx, m.impact(), 52.65, .6)
