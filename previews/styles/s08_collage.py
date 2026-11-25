"""08 KOLAJ KERTAS — cut paper, ransom-note letters, stepped 12 fps motion, torn sheets.
Idea: chasing every trend buries the brand; content pillars keep it recognisable."""
NAME = "LokaDigital Preview 08 · Kolaj Kertas"
SLUG = "08-kolaj-kertas"
PILL = "CONTENT PILLARS"

TITLE = "IKUT TREND?"
FONTS = ["'Archivo Black'", "'Playfair Display'", "'Oswald'", "'Space Mono'", "'League Gothic'", "'EB Garamond'", "'Montserrat'"]
PAPERS = ["#D9D0F0", "#B4FF39", "#C99BFF", "#ffffff", "#B800F0", "#e9e4f7"]
STICKERS = [("Dance trend", 7.0, -14, 140, 640), ("Filter popular", 8.3, 9, 520, 760), ("Audio trending", 9.6, -6, 160, 940),
            ("Meme minggu ni", 10.9, 12, 470, 1100), ("Challenge baru", 12.2, -10, 220, 1240), ("Format orang lain", 13.5, 7, 420, 700)]
PILLARS = [("01", "AJAR", "Tips yang berguna"), ("02", "TUNJUK", "Proses & belakang tabir"), ("03", "BUKTI", "Ulasan & hasil sebenar"), ("04", "JUAL", "Offer yang jelas")]

CSS = """
  .paperbg { position:absolute; inset:0; background:
     repeating-linear-gradient(0deg, rgba(255,255,255,.018) 0 1px, transparent 1px 5px),
     radial-gradient(120% 45% at 100% 0%, #46096B 0%, transparent 62%), #120c18; }
  .rn { position:absolute; left:60px; right:60px; top:640px; display:flex; flex-wrap:wrap; gap:8px; justify-content:center; }
  .rn span { display:inline-block; padding:8px 12px; font-size:96px; line-height:1; color:#07040C; box-shadow:6px 8px 0 rgba(0,0,0,.45); }
  .stk { position:absolute; padding:26px 34px; font:900 54px 'Inter'; letter-spacing:-.02em; color:#07040C; box-shadow:8px 10px 0 rgba(0,0,0,.5);
         clip-path:polygon(0 4%, 6% 0, 40% 3%, 72% 0, 100% 5%, 98% 50%, 100% 96%, 60% 100%, 30% 97%, 2% 100%, 0 55%); }
  #brandcard { position:absolute; left:300px; top:880px; width:480px; padding:40px; background:#07040C; border:4px solid var(--g); text-align:center; font:900 64px 'Inter'; letter-spacing:-.03em; color:var(--g); }
  #brandcard small { display:block; font:700 26px 'Inter'; letter-spacing:.3em; color:var(--mist); margin-top:10px; }
  .q { position:absolute; left:96px; right:96px; top:1420px; font:900 96px/0.94 'Inter'; letter-spacing:-.05em; opacity:0; }
  .tearL, .tearR { position:absolute; top:420px; width:540px; height:1200px; background:#D9D0F0; }
  .tearL { left:0; clip-path:polygon(0 0, 100% 0, 92% 10%, 100% 22%, 90% 35%, 100% 48%, 91% 62%, 100% 75%, 92% 88%, 100% 100%, 0 100%); }
  .tearR { left:540px; clip-path:polygon(8% 0, 100% 0, 100% 100%, 8% 100%, 0 88%, 8% 75%, -1% 62%, 9% 48%, 0 35%, 10% 22%, 0 10%); background:#c9bfe6; }
  .tear-t { position:absolute; left:110px; right:110px; top:800px; font:900 100px/0.94 'Inter'; letter-spacing:-.05em; color:#07040C; text-align:center; }
  .pil { position:absolute; top:520px; width:200px; height:880px; padding:30px 18px; color:#07040C; box-shadow:10px 12px 0 rgba(0,0,0,.5);
         clip-path:polygon(0 1%, 50% 0, 100% 1.5%, 99% 99%, 50% 100%, 1% 98.5%); }
  .pil b { display:block; font:900 64px 'Inter'; letter-spacing:-.04em; }
  .pil h3 { margin-top:30px; font:900 56px/1 'Inter'; letter-spacing:-.04em; writing-mode:vertical-rl; transform:rotate(180deg); height:420px; }
  .pil p { position:absolute; left:18px; right:18px; bottom:30px; font:700 28px/1.2 'Inter'; }
  .rule2 { position:absolute; left:96px; right:96px; top:1450px; font:900 70px/1 'Inter'; letter-spacing:-.04em; opacity:0; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

def _title():
    out = []
    for i, ch in enumerate(TITLE):
        if ch == " ": out.append('<span style="background:none;box-shadow:none;width:30px"></span>'); continue
        out.append(f'<span class="ltr" id="lt{i}" style="font-family:{FONTS[i % len(FONTS)]};background:{PAPERS[i % len(PAPERS)]};transform:rotate({(-7, 5, -3, 8, -5, 4, -8)[i % 7]}deg)">{ch}</span>')
    return "".join(out)

BODY = f"""
      <div class="paperbg clip" id="pbg" data-start="0" data-duration="60" data-track-index="1"></div>
      <div class="rn clip" id="rn" data-start="0" data-duration="6.6" data-track-index="2">{_title()}</div>
      <div id="brandcard" class="clip" data-start="6.4" data-duration="11.6" data-track-index="2">KEDAI KAU<small>BRAND · CONTOH</small></div>
      {''.join(f'<div class="stk clip" id="sk{i}" data-start="{t:.1f}" data-duration="{18 - t:.1f}" data-track-index="3" style="left:{x}px;top:{y}px;background:{PAPERS[i % len(PAPERS)]}">{n}</div>' for i, (n, t, r, x, y) in enumerate(STICKERS))}
      <div class="q clip" id="q1" data-start="15" data-duration="3" data-track-index="4">Brand kau <span class="gr">mana?</span></div>
      <div class="clip" id="tear" data-start="18" data-duration="6.2" data-track-index="5"><div class="tearL"></div><div class="tearR"></div><div class="tear-t" id="tt">Orang ingat trend.<br>Bukan kau.</div></div>
      <div class="clip" id="pills" data-start="24.4" data-duration="27.6" data-track-index="2">
        {''.join(f'<div class="pil" id="pl{i}" style="left:{86 + i * 232}px;background:{["#B4FF39", "#D9D0F0", "#C99BFF", "#ffffff"][i]}"><b>{a}</b><h3>{b}</h3><p>{c}</p></div>' for i, (a, b, c) in enumerate(PILLARS))}
      </div>
      <div class="rule2 clip" id="r1" data-start="36" data-duration="7.8" data-track-index="4">Trend boleh.<br><span class="gr">Kalau masuk tiang kau.</span></div>
      <div class="rule2 clip" id="r2" data-start="44" data-duration="8" data-track-index="4">4 tiang. Setiap minggu.<br><span class="gr">Orang mula kenal kau.</span></div>
      <div id="cta" class="clip" data-start="52.2" data-duration="7.8" data-track-index="6">
        <div class="h"><span class="el">KONSISTEN</span><br><span class="el gr">LEBIH KUAT</span><br><span class="el">DARI IKUT-IKUT.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>CONTENT PILLARS & PLAN</label><small>Pelan content bulanan</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _boil(sel, t0, t1, amp=1.2):
    # stop-motion "boil": small stepped rotation flips while the paper sits there
    n = max(1, int((t1 - t0) / .25))
    return f'tl.to("{sel}", {{rotation:"+={amp}", duration:.125, ease:"steps(1)", yoyo:true, repeat:{2 * n - 1}}}, {t0:.2f});'

def _js():
    j = []; A = j.append
    for i, ch in enumerate(TITLE):
        if ch == " ": continue
        A(f'tl.fromTo("#lt{i}", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:.25, ease:"steps(3)"}}, {.3 + i * .22:.2f});')
    A(_boil("#rn", 2.8, 6.2, 1.0))
    A('tl.to("#rn", {y:-900, rotation:-8, duration:.5, ease:"steps(6)"}, 6.1);')
    A('tl.fromTo("#brandcard", {scale:0, rotation:-10}, {scale:1, rotation:-2, duration:.4, ease:"steps(5)"}, 6.4);')
    for i, (n, t, r, x, y) in enumerate(STICKERS):
        A(f'tl.fromTo("#sk{i}", {{scale:2.2, rotation:{r * 2}, opacity:0}}, {{scale:1, rotation:{r}, opacity:1, duration:.3, ease:"steps(4)"}}, {t:.2f});')
        A(_boil(f"#sk{i}", t + .3, 17.8, .8))
    A('tl.fromTo("#q1", {opacity:0}, {opacity:1, duration:.3, ease:"steps(3)"}, 15.1);')
    A('tl.fromTo(".tearL, .tearR", {opacity:0}, {opacity:1, duration:.2, ease:"steps(2)"}, 18);')
    A('tl.fromTo("#tt", {opacity:0}, {opacity:1, duration:.3, ease:"steps(3)"}, 18.6);')
    A('tl.to(".tearL", {x:-620, rotation:-6, duration:.7, ease:"steps(8)"}, 23.4);')
    A('tl.to(".tearR", {x:620, rotation:6, duration:.7, ease:"steps(8)"}, 23.4);')
    A('tl.to("#tt", {opacity:0, duration:.2}, 23.4);')
    for i in range(4):
        t = 24.8 + i * 2.6
        A(f'tl.fromTo("#pl{i}", {{y:1300, rotation:{(-8, 6, -5, 7)[i]}}}, {{y:0, rotation:{(-1.5, 1, -1, 1.5)[i]}, duration:.5, ease:"steps(6)"}}, {t:.2f});')
        A(_boil(f"#pl{i}", t + .5, 51.5, .6))
    A('tl.fromTo("#r1", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, ease:"steps(3)"}, 36.1);')
    A('tl.fromTo("#r2", {opacity:0, y:30}, {opacity:1, y:0, duration:.3, ease:"steps(3)"}, 44.1);')
    A('tl.to("#pills", {scale:.9, y:-60, duration:8, ease:"none"}, 44);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.4, ease:"steps(5)", stagger:.18}, 52.4);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.5, ease:"steps(6)"}, 53.3);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.4, ease:"steps(5)"}, 53.8);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(45, [57, 60, 64, 67]), (50, [62, 65, 69, 72]), (43, [55, 59, 62, 67]), (48, [60, 64, 67, 71])]
    m.score(96, prog, kind="piano", drums="half", start=0, end=18, swing=.18)
    m.drone(lib.hz(40), 18, 24.4, .1)
    m.score(96, prog, kind="pluck", drums="four", start=24.4, end=59, swing=.18)
    for i, ch in enumerate(TITLE):
        if ch != " ": m.at(m.fx, m.paper(), .3 + i * .22, .5)
    for n, t, *_ in STICKERS: m.at(m.fx, m.paper(), t, .5); m.at(m.fx, m.pop(400), t + .05, .2)
    m.at(m.fx, m.whoosh(.7), 23.3, .4); m.at(m.fx, m.paper(), 23.4, .8)
    for i in range(4): m.at(m.fx, m.thud(), 24.8 + i * 2.6 + .45, .4)
    m.at(m.fx, m.impact(), 52.25, .55)
