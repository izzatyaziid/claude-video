"""09 GAME / LEVEL UP — an arcade game HUD: the player keeps pressing BOOST POST until GAME OVER,
then continues with a real campaign setup and collects power-ups to LEVEL CLEAR."""
NAME = "LokaDigital Preview 09 · Game Level Up"
SLUG = "09-game-level-up"
PILL = "PLAYER 1 · CONTOH"

SPRITE = [  # 10x10 pixel coffee cup, 0 empty, 1 mist, 2 lime, 3 purple
    "0000220000", "0002002000", "0000220000", "1111111100", "1333333113", "1333333101", "1333333113", "1333333100", "0111111000", "2222222220"]
COLS = {"1": "#D9D0F0", "2": "#B4FF39", "3": "#7B16B8"}
BOOSTS = [6.0, 7.6, 9.2, 10.8, 12.4]
POWERS = [("OBJEKTIF BETUL", "Mesej / jualan, bukan likes", 28.0), ("PIXEL & TRACKING", "Tahu iklan mana bawa jualan", 31.6),
          ("UJI 3 CREATIVE", "Biar data pilih yang menang", 35.2), ("AUDIENS TEPAT", "Bukan semua orang", 38.8)]

CSS = """
  .mono { font-family:'Space Mono',monospace; }
  #hud { position:absolute; left:80px; right:80px; top:430px; display:flex; justify-content:space-between; align-items:flex-start; font:700 34px 'Space Mono'; }
  #hud .lv { color:var(--g); }
  .hpw { width:420px; } .hpw small { display:block; font:700 26px 'Space Mono'; letter-spacing:.2em; color:var(--mist); margin-bottom:8px; }
  .hp { height:40px; border:4px solid #fff; padding:4px; } .hp i { display:block; height:100%; background:var(--g); transform-origin:0 50%; }
  #stars { font:700 44px 'Space Mono'; color:var(--grey); letter-spacing:.1em; text-align:right; } #stars small { display:block; font-size:26px; letter-spacing:.2em; color:var(--mist); }
  #world { position:absolute; left:0; right:0; top:620px; height:900px; overflow:hidden; }
  #ground { position:absolute; left:-200px; right:-200px; top:640px; height:260px; background:
            repeating-linear-gradient(90deg, #240538 0 60px, #46096B 60px 120px); border-top:8px solid var(--g); }
  #sky { position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(255,255,255,.03) 0 4px, transparent 4px 8px); }
  #sprite { position:absolute; left:180px; top:440px; display:grid; grid-template-columns:repeat(10,20px); }
  #sprite i { width:20px; height:20px; display:block; }
  #btn { position:absolute; left:540px; top:340px; width:420px; padding:28px 0; text-align:center; background:#B800F0; border:6px solid #fff; font:700 44px 'Space Mono'; box-shadow:0 14px 0 #46096B; }
  .float { position:absolute; font:700 40px 'Space Mono'; color:var(--grey); opacity:0; }
  #over { position:absolute; left:0; right:0; top:820px; text-align:center; font:700 130px/1 'Space Mono'; color:#B800F0; letter-spacing:-.04em; opacity:0; }
  #over small { display:block; margin-top:30px; font:700 44px 'Space Mono'; color:#fff; letter-spacing:.1em; }
  .pw { position:absolute; left:110px; right:110px; top:680px; padding:34px 40px; border:6px solid var(--g); background:#07040C; opacity:0; }
  .pw b { display:block; font:700 30px 'Space Mono'; color:var(--g); letter-spacing:.2em; } .pw h3 { margin-top:14px; font:900 70px/1 'Inter'; letter-spacing:-.04em; }
  .pw p { margin-top:14px; font:600 36px 'Inter'; color:var(--mist); }
  .coin { position:absolute; width:60px; height:60px; border-radius:50%; background:var(--g); border:6px solid #fff; opacity:0; }
  #clear { position:absolute; left:0; right:0; top:760px; text-align:center; font:700 120px/1 'Space Mono'; color:var(--g); opacity:0; }
  #clear small { display:block; margin-top:30px; font:900 64px/1.05 'Inter'; color:#fff; letter-spacing:-.03em; }
  .sup { position:absolute; left:96px; right:96px; top:1560px; font:900 72px/1 'Inter'; letter-spacing:-.04em; opacity:0; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .k { font:700 34px 'Space Mono'; color:var(--g); letter-spacing:.2em; margin-bottom:20px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; background:var(--g); margin:36px 0 40px; }
"""

def _sprite():
    return "".join(f'<i style="background:{COLS.get(c, "transparent")}"></i>' for row in SPRITE for c in row)

BODY = f"""
      <div id="hud" class="clip" data-start="0" data-duration="52" data-track-index="2">
        <div class="hpw"><small id="lvl" class="lv">LEVEL 1 · BAJET IKLAN</small><div class="hp"><i id="hpbar"></i></div></div>
        <div id="stars">☆☆☆☆<small>PELANGGAN</small></div>
      </div>
      <div id="world" class="clip" data-start="0" data-duration="52" data-track-index="1">
        <div id="sky"></div><div id="ground"></div><div id="sprite">{_sprite()}</div>
        <div id="btn">BOOST POST</div>
        {''.join(f'<div class="float" id="fl{i}" style="left:{560 + (i % 2) * 140}px;top:260px">+ likes</div>' for i in range(len(BOOSTS)))}
        {''.join(f'<div class="coin" id="cn{i}" style="left:{620 + i * 70}px;top:470px"></div>' for i in range(4))}
      </div>
      <div class="sup clip" id="u0" data-start="0.4" data-duration="5.4" data-track-index="3">Strategi iklan kau:<br><span class="gr">tekan butang ni.</span></div>
      <div id="over" class="clip" data-start="14.2" data-duration="8.8" data-track-index="4">GAME<br>OVER<small>BAJET HABIS · PELANGGAN 0</small></div>
      <div class="sup clip" id="u1" data-start="17.6" data-duration="5.4" data-track-index="3">Boost post = engagement.<br><span class="gr">Bukan jualan.</span></div>
      <div class="sup clip" id="u2" data-start="23.2" data-duration="4.6" data-track-index="3" style="top:860px;text-align:center;font-family:'Space Mono';font-weight:700;color:var(--g)">CONTINUE? ▶ YA</div>
      {''.join(f'<div class="pw clip" id="pw{i}" data-start="{t:.1f}" data-duration="3.4" data-track-index="4"><b>POWER-UP {i + 1}/4</b><h3>{a}</h3><p>{b}</p></div>' for i, (a, b, t) in enumerate(POWERS))}
      <div id="clear" class="clip" data-start="42.6" data-duration="9.4" data-track-index="4">LEVEL<br>CLEAR<small>Iklan yang dibina,<br><span class="gr">bukan ditekan.</span></small></div>
      <div id="cta" class="clip" data-start="52.2" data-duration="7.8" data-track-index="5">
        <div class="k">PLAYER 2 MASUK?</div>
        <div class="h"><span class="el">STOP</span><br><span class="el">BOOST.</span><br><span class="el gr">MULA KEMPEN.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>META & TIKTOK ADS SETUP</label><small>Objektif, pixel & testing</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    A('tl.fromTo("#u0", {opacity:0}, {opacity:1, duration:.2, ease:"steps(2)"}, .5);')
    A('tl.fromTo("#sprite", {y:-300}, {y:0, duration:.6, ease:"bounce.out"}, .4);')
    A('tl.to("#ground", {x:-240, duration:52, ease:"none"}, 0);')
    for i, t in enumerate(BOOSTS):
        A(f'tl.to("#btn", {{y:12, duration:.08, yoyo:true, repeat:1}}, {t:.2f});')
        A(f'tl.to("#hpbar", {{scaleX:{1 - (i + 1) / len(BOOSTS):.2f}, duration:.3, ease:"steps(3)"}}, {t + .1:.2f});')
        A(f'tl.fromTo("#fl{i}", {{y:0, opacity:1}}, {{y:-140, opacity:0, duration:1.2, ease:"power1.out", immediateRender:false}}, {t + .1:.2f});')
        A(f'tl.to("#sprite", {{y:-60, duration:.15, yoyo:true, repeat:1, ease:"power2.out"}}, {t:.2f});')
    A('tl.to("#hpbar", {backgroundColor:"#B800F0", duration:.1}, 11);')
    A('tl.to("#sprite", {rotation:90, y:60, duration:.4, ease:"steps(4)"}, 13.6);')
    A('tl.to("#world", {opacity:.2, duration:.3}, 14.1); tl.set("#btn", {opacity:0}, 14.1);')
    A('tl.fromTo("#over", {scale:2, opacity:0}, {scale:1, opacity:1, duration:.3, ease:"steps(4)"}, 14.2);')
    A('tl.fromTo("#u1", {opacity:0}, {opacity:1, duration:.2, ease:"steps(2)"}, 17.7);')
    A('tl.to("#over", {opacity:0, duration:.2}, 22.8);')
    A('tl.fromTo("#u2", {opacity:0}, {opacity:1, duration:.2, ease:"steps(2)", repeat:4, yoyo:true}, 23.3);')
    A('tl.set("#lvl", {textContent:"LEVEL 2 · KEMPEN"}, 27.6); tl.set("#hpbar", {scaleX:1, backgroundColor:"#B4FF39"}, 27.6);')
    A('tl.to("#world", {opacity:1, duration:.3}, 27.6); tl.set("#sprite", {rotation:0, y:0}, 27.6); tl.set("#btn", {opacity:0}, 27.6);')
    stars = ["★☆☆☆", "★★☆☆", "★★★☆", "★★★★"]
    for i, (a, b, t) in enumerate(POWERS):
        A(f'tl.fromTo("#pw{i}", {{x:-200, opacity:0}}, {{x:0, opacity:1, duration:.3, ease:"steps(4)"}}, {t:.2f});')
        A(f'tl.to("#pw{i}", {{x:200, opacity:0, duration:.25, ease:"steps(3)"}}, {t + 3.1:.2f});')
        A(f'tl.fromTo("#cn{i}", {{opacity:1, y:0}}, {{y:-200, opacity:0, duration:.6, ease:"power2.out", immediateRender:false}}, {t + .2:.2f});')
        A(f'tl.to("#sprite", {{y:-120, duration:.2, yoyo:true, repeat:1, ease:"power2.out"}}, {t + .1:.2f});')
        A(f'tl.set("#stars", {{color:"#B4FF39"}}, {t + .3:.2f}); tl.set("#stars", {{innerHTML:"{stars[i]}<small>PELANGGAN</small>"}}, {t + .3:.2f});')
    A('tl.to("#world", {opacity:.25, duration:.3}, 42.4);')
    A('tl.fromTo("#clear", {scale:2, opacity:0}, {scale:1, opacity:1, duration:.35, ease:"steps(5)"}, 42.6);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.4, ease:"steps(5)", stagger:.18}, 52.6);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.5, ease:"steps(6)"}, 53.5);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.4, ease:"steps(5)"}, 54);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(45, [69, 72, 76]), (41, [65, 69, 72]), (43, [67, 71, 74]), (40, [64, 67, 71])]
    lead = [[81, 0, 79, 76, 0, 76, 79, 0], [77, 0, 76, 72, 0, 72, 74, 0], [79, 0, 77, 74, 0, 74, 76, 0], [76, 0, 74, 71, 0, 71, 72, 0]]
    lead = [l[:4] for l in lead]
    m.score(128, prog, kind="square", drums="chip", start=0, end=13.8, lead=lead)
    for t in BOOSTS: m.at(m.fx, m.pop(1200), t, .35); m.at(m.fx, m.tone(lib.hz(60), .25, "square", .002, .1), t + .1, .2)
    m.at(m.fx, m.tone(lib.hz(55), .25, "square", .002, .2), 14.2, .4); m.at(m.fx, m.tone(lib.hz(50), .3, "square", .002, .2), 14.45, .4); m.at(m.fx, m.tone(lib.hz(43), .7, "square", .002, .4), 14.75, .4)
    for k in range(6): m.at(m.fx, m.tick(), 23.3 + k * .4, .4)
    m.score(140, prog, kind="square", drums="chip", start=27.6, end=59, lead=lead)
    for a, b, t in POWERS: m.at(m.fx, m.coin(), t + .2, .5)
    m.at(m.fx, m.riser(1.2), 41.4, .3); m.at(m.fx, m.impact(), 42.65, .5)
