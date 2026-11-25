"""07 INFINITE ZOOM — one continuous zoom, no cuts: signboard -> poster -> phone -> WhatsApp -> packaging,
then zoom back out. Idea: a brand with five different faces; one consistent identity everywhere."""
NAME = "LokaDigital Preview 07 · Infinite Zoom"
SLUG = "07-infinite-zoom"
PILL = "BRAND CHECK · CONTOH"
K = 5  # each layer is 1/5 the size of the one around it

# per layer: id, label, messy (font, colour, bg, text), clean text
LAYERS = [
    ("signboard", "SIGNBOARD", ("'Playfair Display'", "#ff4d4d", "#2a1612", "Kopi Atok"), "KOPI ATOK"),
    ("poster", "POSTER KEDAI", ("'Oswald'", "#ff9f1c", "#1b1b2f", "PROMO!!!"), "PAGI LEBIH CEPAT"),
    ("insta", "INSTAGRAM", ("'Montserrat'", "#3fa9f5", "#0f1a24", "kopiatok_official"), "@kopiatok"),
    ("wasap", "WHATSAPP", ("'League Gothic'", "#2ecc71", "#0e1d14", "KOPI ATOK ENTERPRISE"), "KOPI ATOK"),
    ("pack", "PEMBUNGKUS", ("'EB Garamond'", "#e84393", "#24121d", "~ kopi atok ~"), "KOPI ATOK"),
]
N = len(LAYERS)
T_IN = [1.5, 6, 10.5, 15, 19.5]    # arrival at each layer (zoom in)
T_OUT_START = 30.0                  # zoom back out, fixed brand
T_OUT = [30, 34, 38, 42, 46]

CSS = """
  #zoomw { position:absolute; inset:0; overflow:hidden; }
  #zoom { position:absolute; left:0; top:0; width:1080px; height:1920px; }
  .lay { position:absolute; left:0; top:0; width:1080px; height:1920px; overflow:hidden; }
  .lay .bgm, .lay .bgc { position:absolute; inset:0; }
  .lay .bgc { background:radial-gradient(120% 45% at 100% 0%, #46096B 0%, transparent 62%), #0d0816; opacity:0; }
  .hole { position:absolute; left:432px; top:768px; width:216px; height:384px; border-radius:6px; box-shadow:0 0 0 6px rgba(255,255,255,.18); }
  .tm, .tc { position:absolute; left:80px; right:80px; top:500px; text-align:center; line-height:1; }
  .tm { font-size:104px; }
  .tc { font:900 140px/0.92 'Inter'; letter-spacing:-.05em; color:#fff; opacity:0; }
  .tc em { font-style:normal; color:var(--g); }
  .tag2 { position:absolute; left:0; right:0; top:1300px; text-align:center; font:700 40px 'Inter'; letter-spacing:.3em; color:rgba(255,255,255,.75); }
  .stripe { position:absolute; left:0; right:0; height:40px; }
  .sup { position:absolute; left:96px; right:96px; top:1500px; font:900 84px/0.96 'Inter'; letter-spacing:-.045em; opacity:0; text-shadow:0 20px 60px rgba(0,0,0,.9); }
  .x { position:absolute; left:96px; right:96px; top:560px; display:grid; grid-template-columns:1fr 1fr; gap:16px; opacity:0; }
  .x div { padding:28px; border-radius:20px; font-size:60px; text-align:center; background:rgba(255,255,255,.04); border:2px solid var(--line); }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

def _layers():
    out = []
    for i, (lid, lab, (font, col, bg, txt), clean) in enumerate(LAYERS):
        hole = '<div class="hole"></div>' if i < N - 1 else ""
        out.append(f'''<div class="lay" id="L{i}">
          <div class="bgm" style="background:{bg}"></div><div class="bgc"></div>
          <div class="stripe" style="top:0;background:{col};opacity:.9" id="st{i}"></div>
          <div class="tm" id="tm{i}" style="font-family:{font};color:{col}">{txt}</div>
          <div class="tc" id="tc{i}">{clean.replace("ATOK", "<em>ATOK</em>") if "ATOK" in clean else clean}</div>
          {hole}<div class="tag2">{lab}</div></div>''')
    return "".join(out)

BODY = f"""
      <div id="zoomw" class="clip" data-start="0" data-duration="50" data-track-index="1" data-layout-allow-overflow data-layout-ignore><div id="zoom">{_layers()}</div></div>
      <div class="x clip" id="xgrid" data-start="24" data-duration="6" data-track-index="2">
        {''.join(f'<div style="font-family:{f};color:{c}">{t.split()[0]}</div>' for _, _, (f, c, _, t), _ in LAYERS[:4])}
      </div>
      <div class="sup clip" id="u1" data-start="24" data-duration="6" data-track-index="3">Satu kedai.<br><span class="gr">Lima muka berbeza.</span></div>
      <div class="sup clip" id="u2" data-start="46.5" data-duration="4" data-track-index="3">Satu brand.<br><span class="gr">Satu muka. Semua tempat.</span></div>
      <div id="cta" class="clip" data-start="50.5" data-duration="9.5" data-track-index="4">
        <div class="h"><span class="el">ORANG INGAT</span><br><span class="el">YANG</span><br><span class="el gr">KONSISTEN.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>BRAND IDENTITY SYSTEM</label><small>Logo, warna & font yang seragam</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    for i in range(N):
        A(f'tl.set("#L{i}", {{scale:{1 / K ** i}, transformOrigin:"50% 50%"}}, 0);')
    A('tl.set("#zoom", {scale:1, transformOrigin:"50% 50%"}, 0);')
    # zoom in: segment by segment
    prev = 0.0
    for i in range(1, N):
        A(f'tl.to("#zoom", {{scale:{K ** i}, duration:{T_IN[i] - T_IN[i - 1]:.2f}, ease:"power2.inOut"}}, {T_IN[i - 1]:.2f});')
        A(f'tl.to("#L{i - 1}", {{opacity:0, duration:.3}}, {T_IN[i] - .1:.2f});')
    # hold inside, show the mess
    A('tl.to("#zoomw", {opacity:.18, duration:.5}, 23.6);')
    A('tl.fromTo("#xgrid", {opacity:0, y:40}, {opacity:1, y:0, duration:.6, ease:"expo.out"}, 24.1);')
    A('tl.fromTo("#u1", {opacity:0, y:40}, {opacity:1, y:0, duration:.6, ease:"expo.out"}, 24.3);')
    A('tl.to("#zoomw", {opacity:1, duration:.5}, 29.6);')
    # switch every layer to the clean brand, then zoom back out
    for i in range(N):
        A(f'tl.to("#L{i} .bgc", {{opacity:1, duration:.6}}, {29.6 + .1 * i:.2f});')
        A(f'tl.to("#tm{i}", {{opacity:0, duration:.3}}, {29.6 + .1 * i:.2f});')
        A(f'tl.fromTo("#tc{i}", {{opacity:0, scale:1.2}}, {{opacity:1, scale:1, duration:.6, ease:"expo.out"}}, {29.8 + .1 * i:.2f});')
        A(f'tl.to("#st{i}", {{backgroundColor:"#B4FF39", duration:.4}}, {29.6 + .1 * i:.2f});')
    for i in range(N - 1, 0, -1):
        t0 = T_OUT[N - 1 - i]
        A(f'tl.set("#L{i - 1}", {{opacity:1}}, {t0:.2f});')
        A(f'tl.to("#zoom", {{scale:{K ** (i - 1)}, duration:4, ease:"power2.inOut"}}, {t0:.2f});')
    A('tl.fromTo("#u2", {opacity:0, y:40}, {opacity:1, y:0, duration:.6, ease:"expo.out"}, 46.6);')
    A('tl.to("#zoomw", {opacity:0, duration:.5}, 50);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 50.7);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 51.6);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 52.1);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    m.drone(lib.hz(36), 0, 30, .1)
    for i in range(1, N): m.at(m.fx, m.riser(T_IN[i] - T_IN[i - 1] - .2), T_IN[i - 1] + .2, .22); m.at(m.fx, m.thud(), T_IN[i], .45)
    m.at(m.fx, m.glitch(.3), 24.1, .4)
    prog = [(48, [60, 64, 67, 72]), (43, [55, 59, 62, 67]), (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65])]
    m.score(120, prog, kind="pad", drums="four", start=29.6, end=59)
    for i in range(N): m.at(m.fx, m.pop(800 + 60 * i), 29.8 + .1 * i, .3)
    for t in T_OUT[:4]: m.at(m.fx, m.whoosh(1.2, False), t + .3, .25)
    m.at(m.fx, m.impact(), 50.55, .6)
