"""10 DOKUMENTARI DATA — calm analyst film: thin grid, charts drawing themselves, margin annotations, slow camera.
Idea: likes, followers and views are the wrong scoreboard; track leads, cost per lead, conversion and sales."""
NAME = "LokaDigital Preview 10 · Dokumentari Data"
SLUG = "10-dokumentari-data"
PILL = "LAPORAN · CONTOH"

VANITY = [("LIKES", "↑"), ("FOLLOWERS", "↑"), ("VIEWS", "↑")]
REAL = [("01", "LEAD MASUK", "Berapa orang betul-betul bertanya"), ("02", "KOS SETIAP LEAD", "Berapa kau bayar untuk satu pertanyaan"),
        ("03", "KADAR JADI PELANGGAN", "Berapa lead yang akhirnya beli"), ("04", "JUALAN DARI IKLAN", "Duit masuk, bukan tepukan")]

CSS = """
  .grid { position:absolute; inset:0; background:
     repeating-linear-gradient(0deg, rgba(255,255,255,.04) 0 1px, transparent 1px 60px),
     repeating-linear-gradient(90deg, rgba(255,255,255,.04) 0 1px, transparent 1px 60px); }
  .mono { font-family:'IBM Plex Mono',monospace; }
  #kicker { position:absolute; left:96px; top:440px; font:600 30px 'IBM Plex Mono'; color:var(--grey); letter-spacing:.06em; }
  #h1 { position:absolute; left:96px; right:96px; top:500px; font:900 96px/0.95 'Inter'; letter-spacing:-.045em; }
  .tiles { position:absolute; left:96px; right:96px; top:760px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; }
  .tile { padding:30px 26px; border-radius:22px; background:var(--glass); border:2px solid var(--line); position:relative; }
  .tile b { display:block; font:600 26px 'IBM Plex Mono'; color:var(--mist); letter-spacing:.06em; }
  .tile span { display:block; margin-top:16px; font:900 90px 'Inter'; color:var(--lav, #C99BFF); }
  .tile i { position:absolute; left:16px; right:16px; top:50%; height:6px; background:#B800F0; transform-origin:0 50%; }
  #chart { position:absolute; left:96px; top:760px; width:888px; height:600px; overflow:visible; }
  #chart text { font:600 26px 'IBM Plex Mono'; fill:var(--grey); }
  .ann { position:absolute; font:600 30px/1.3 'IBM Plex Mono'; color:var(--mist); padding-left:22px; border-left:4px solid var(--g); opacity:0; }
  .rows { position:absolute; left:96px; right:96px; top:720px; display:flex; flex-direction:column; gap:22px; }
  .row { display:flex; gap:28px; align-items:center; padding:28px 32px; border-radius:22px; background:var(--glass); border:2px solid var(--line); opacity:0; }
  .row b { font:900 60px 'Inter'; color:var(--g); min-width:90px; } .row h3 { font:800 42px/1.05 'Inter'; letter-spacing:-.02em; }
  .row p { margin-top:8px; font:500 30px 'Inter'; color:var(--mist); }
  #bars { position:absolute; left:96px; right:96px; top:780px; }
  .bar { display:flex; align-items:center; gap:24px; margin:30px 0; }
  .bar label { width:190px; font:700 34px 'IBM Plex Mono'; }
  .bar .tr { flex:1; height:70px; background:rgba(255,255,255,.05); border-radius:12px; overflow:hidden; } .bar .tr i { display:block; height:100%; transform-origin:0 50%; }
  .bar em { font:800 34px 'Inter'; font-style:normal; width:200px; }
  .sup { position:absolute; left:96px; right:96px; top:1450px; font:900 74px/1 'Inter'; letter-spacing:-.04em; opacity:0; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

LIKES = "M40 540 C 200 500, 300 430, 420 360 S 700 180, 860 80"
SALES = "M40 520 C 200 522, 300 518, 420 521 S 700 516, 860 519"

BODY = f"""
      <div class="grid clip" id="grid" data-start="0" data-duration="60" data-track-index="1"></div>
      <div id="kicker" class="clip" data-start="0" data-duration="52" data-track-index="2">// laporan_bulanan.pdf</div>
      <div id="h1" class="clip" data-start="0" data-duration="15.6" data-track-index="2">Semua naik.<br><span class="gr">Kenapa jualan tak?</span></div>
      <div class="tiles clip" id="tiles" data-start="0" data-duration="24" data-track-index="3">
        {''.join(f'<div class="tile" id="t{i}"><b>{a}</b><span>{b}</span><i></i></div>' for i, (a, b) in enumerate(VANITY))}
      </div>
      <svg id="chart" class="clip" data-start="6.5" data-duration="17.5" data-track-index="4" viewBox="0 0 888 600">
        <line x1="40" y1="560" x2="880" y2="560" stroke="rgba(255,255,255,.3)" stroke-width="2"/>
        <path id="lk" d="{LIKES}" fill="none" stroke="#C99BFF" stroke-width="8" stroke-linecap="round"/>
        <path id="sl" d="{SALES}" fill="none" stroke="#B4FF39" stroke-width="8" stroke-linecap="round"/>
        <text x="40" y="600">JAN</text><text x="790" y="600">JUN</text><text x="640" y="60">likes</text><text x="700" y="500">jualan</text>
      </svg>
      <div class="ann clip" id="a1" data-start="9.5" data-duration="6" data-track-index="5" style="left:520px;top:1400px">ilustrasi · CONTOH<br>bukan data sebenar</div>
      <div class="sup clip" id="u1" data-start="15.8" data-duration="8" data-track-index="5" style="top:460px">Kau ukur<br><span class="gr">benda yang salah.</span></div>
      <div class="sup clip" id="u2" data-start="24.4" data-duration="20" data-track-index="5" style="top:460px;font-size:64px">Ukur ini:</div>
      <div class="rows clip" id="rows" data-start="24.4" data-duration="20" data-track-index="3">
        {''.join(f'<div class="row" id="w{i}"><b>{a}</b><div><h3>{b}</h3><p>{c}</p></div></div>' for i, (a, b, c) in enumerate(REAL))}
      </div>
      <div class="sup clip" id="u3" data-start="44.6" data-duration="7.6" data-track-index="5" style="top:460px;font-size:72px">Data yang betul =<br><span class="gr">keputusan yang betul.</span></div>
      <div id="bars" class="clip" data-start="44.6" data-duration="7.6" data-track-index="3">
        <div class="bar"><label>IKLAN A</label><div class="tr"><i id="ba" style="background:var(--g)"></i></div><em class="gr" id="ea">TAMBAH</em></div>
        <div class="bar"><label>IKLAN B</label><div class="tr"><i id="bb" style="background:#7C7396"></i></div><em style="color:var(--grey)" id="eb">TUTUP</em></div>
        <div class="ann" id="a2" style="position:relative;margin-top:30px">jualan setiap RM iklan · CONTOH</div>
      </div>
      <div id="cta" class="clip" data-start="52.4" data-duration="7.6" data-track-index="6">
        <div class="h"><span class="el">LIKES TAK</span><br><span class="el">BAYAR SEWA.</span><br><span class="el gr">JUALAN BAYAR.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>DASHBOARD & LAPORAN</label><small>Metrik yang bawa keputusan</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    A('tl.fromTo("#kicker", {opacity:0}, {opacity:1, duration:.6}, .2);')
    A('tl.fromTo("#h1", {y:30, opacity:0}, {y:0, opacity:1, duration:.8, ease:"expo.out"}, .5);')
    A('tl.fromTo(".tile", {y:40, opacity:0}, {y:0, opacity:1, duration:.6, ease:"expo.out", stagger:.3}, 1.6);')
    A('tl.set(".tile i", {scaleX:0}, 0);')
    A('tl.to("#tiles", {y:-80, scale:.7, transformOrigin:"0% 0%", opacity:.35, duration:.8, ease:"power2.inOut"}, 6);')
    A('tl.fromTo("#lk", {strokeDasharray:1100, strokeDashoffset:1100}, {strokeDashoffset:0, duration:2.4, ease:"power2.inOut"}, 6.8);')
    A('tl.fromTo("#sl", {strokeDasharray:1100, strokeDashoffset:1100}, {strokeDashoffset:0, duration:2.4, ease:"power2.inOut"}, 9.6);')
    A('tl.fromTo("#a1", {x:-20, opacity:0}, {x:0, opacity:1, duration:.5}, 9.6);')
    A('tl.to("#chart", {opacity:.25, duration:.5}, 15.6);')
    A('tl.fromTo("#u1", {y:30, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 15.9);')
    A('tl.to("#tiles", {opacity:1, y:200, scale:1, duration:.7, ease:"expo.out"}, 16.2);')
    A('tl.to(".tile i", {scaleX:1, duration:.4, ease:"power3.out", stagger:.3}, 17.6);')
    A('tl.to(".tile span", {color:"#7C7396", duration:.3, stagger:.3}, 17.6);')
    A('tl.fromTo("#u2", {opacity:0}, {opacity:1, duration:.5}, 24.5);')
    A('tl.fromTo(".row", {x:-60, opacity:0}, {x:0, opacity:1, duration:.6, ease:"expo.out", stagger:4.2}, 25.4);')
    A('tl.fromTo("#u3", {y:30, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 44.8);')
    A('tl.fromTo("#ba", {scaleX:0}, {scaleX:.82, duration:1.4, ease:"expo.out"}, 45.6);')
    A('tl.fromTo("#bb", {scaleX:0}, {scaleX:.18, duration:1.4, ease:"expo.out"}, 45.9);')
    A('tl.fromTo("#ea, #eb", {opacity:0}, {opacity:1, duration:.4, stagger:.3}, 47.4);')
    A('tl.fromTo("#a2", {opacity:0}, {opacity:1, duration:.5}, 48);')
    A('tl.to("#grid", {y:-60, duration:60, ease:"none"}, 0);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 52.6);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 53.5);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 54);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(45, [57, 64, 69, 72]), (41, [53, 60, 65, 69]), (48, [55, 64, 67, 72]), (43, [55, 62, 67, 71])]
    m.score(80, prog, kind="piano", drums="none", start=0, end=24)
    m.score(80, prog, kind="piano", drums="half", start=24.4, end=59)
    for k in range(3): m.at(m.fx, m.pop(700), 1.6 + .3 * k, .25)
    m.at(m.fx, m.whoosh(2.4), 6.8, .15); m.at(m.fx, m.whoosh(2.4), 9.6, .12)
    for k in range(3): m.at(m.fx, m.glitch(.1), 17.6 + .3 * k, .25)
    for k in range(4): m.at(m.fx, m.pop(900), 25.4 + 4.2 * k, .3)
    m.at(m.fx, m.coin(), 47.4, .3)
    m.at(m.fx, m.riser(1.6), 50.8, .25); m.at(m.fx, m.impact(), 52.45, .55)
