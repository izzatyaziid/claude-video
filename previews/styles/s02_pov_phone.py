"""02 POV TELEFON — the whole film happens on the owner's phone screen, filmed as if held in hand.
Idea: DMs answered late go cold; a response + follow-up system turns enquiries into sales."""
NAME = "LokaDigital Preview 02 · POV Telefon"
SLUG = "02-pov-telefon"
PILL = "CONTOH · F&amp;B"

# timeline (s)
T_HOOK, T_BUSY, T_INBOX, T_COLD, T_LOST, T_TURN, T_SYS, T_FU, T_WIN, T_CTA = 0, 6, 12, 19, 25, 31, 36, 43, 49, 53

MSGS = [  # incoming DMs during the busy period
    ("Aina", "Hi, ada slot untuk 10 orang Sabtu ni?", 7.0),
    ("Faiz", "Boleh delivery ke Shah Alam?", 8.2),
    ("Mei", "Set catering ada menu vegetarian?", 9.4),
    ("Ravi", "Harga set lunch berapa ya?", 10.6),
]

CSS = """
  #hand { position:absolute; left:130px; top:430px; width:820px; height:1430px; transform-style:preserve-3d; }
  .phone { position:absolute; inset:0; border-radius:90px; background:#0b0711; border:10px solid #1c1426;
           box-shadow:0 80px 160px rgba(0,0,0,.75), 0 0 0 2px rgba(255,255,255,.08), 0 0 120px rgba(123,22,184,.35); overflow:hidden; }
  .notch { position:absolute; left:50%; top:22px; width:220px; height:52px; margin-left:-110px; border-radius:26px; background:#000; z-index:20; }
  .status { position:absolute; left:60px; right:60px; top:26px; display:flex; justify-content:space-between; font:700 30px 'Inter'; color:#fff; z-index:21; }
  .scr { position:absolute; inset:0; padding:120px 44px 40px; opacity:0; }
  .apphdr { display:flex; align-items:center; gap:20px; font:800 44px 'Inter'; letter-spacing:-.02em; margin-bottom:30px; }
  .apphdr .back { width:26px; height:26px; border-left:6px solid #fff; border-bottom:6px solid #fff; transform:rotate(45deg); margin-right:8px; }
  .row { display:flex; align-items:center; gap:22px; padding:24px 10px; border-bottom:1px solid rgba(255,255,255,.08); }
  .av { width:96px; height:96px; border-radius:50%; flex:none; background:linear-gradient(135deg,var(--mag),var(--p1)); display:flex; align-items:center; justify-content:center; font:800 40px 'Inter'; }
  .row .tx { flex:1; min-width:0; }
  .row .nm { font:700 34px 'Inter'; display:flex; justify-content:space-between; }
  .row .nm i { font:500 28px 'Inter'; font-style:normal; color:var(--grey); }
  .row .ms { font:500 30px 'Inter'; color:var(--mist); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-top:6px; }
  .row .dot { width:22px; height:22px; border-radius:50%; background:var(--g); flex:none; }
  .toast { position:absolute; left:30px; right:30px; top:96px; padding:26px 30px; border-radius:36px; background:rgba(40,30,55,.92); border:1px solid rgba(255,255,255,.12);
           display:flex; gap:20px; align-items:center; box-shadow:0 30px 60px rgba(0,0,0,.5); z-index:30; opacity:0; }
  .toast .av { width:80px; height:80px; font-size:32px; }
  .toast b { display:block; font:700 30px 'Inter'; } .toast span { display:block; font:500 28px 'Inter'; color:var(--mist); margin-top:4px; }
  .busy { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
  .busy .big { font:900 120px/0.95 'Inter'; letter-spacing:-.05em; }
  .busy .lab { margin-top:30px; }
  .clock { font:900 200px 'Inter'; letter-spacing:-.06em; color:#fff; }
  .clock small { display:block; font:700 30px 'Inter'; letter-spacing:.3em; color:var(--grey); text-align:center; }
  .bubble { max-width:620px; padding:26px 32px; border-radius:36px; font:500 34px/1.3 'Inter'; margin:16px 0; }
  .in { background:#231a30; color:#fff; border-bottom-left-radius:10px; }
  .out { background:var(--g); color:var(--ink); margin-left:auto; border-bottom-right-radius:10px; font-weight:600; }
  .seen { text-align:right; font:500 26px 'Inter'; color:var(--grey); }
  .cold { margin-top:40px; text-align:center; font:800 64px 'Inter'; letter-spacing:-.03em; color:var(--grey); }
  .supers { position:absolute; left:0; right:0; top:330px; text-align:center; z-index:5; }
  .sup { position:absolute; left:90px; right:90px; font:900 88px/0.95 'Inter'; letter-spacing:-.045em; text-align:left; opacity:0; text-shadow:0 20px 60px rgba(0,0,0,.8); }
  .sysrow { display:flex; align-items:center; gap:24px; padding:30px; margin:20px 0; border-radius:30px; background:rgba(255,255,255,.05); border:2px solid rgba(255,255,255,.12); opacity:0; }
  .sysrow b { font:800 54px 'Inter'; color:var(--g); min-width:80px; }
  .sysrow p { font:700 38px/1.15 'Inter'; } .sysrow p i { display:block; font:500 28px 'Inter'; font-style:normal; color:var(--mist); margin-top:6px; }
  .tag { display:inline-block; padding:6px 16px; border-radius:99px; background:var(--g); color:var(--ink); font:800 24px 'Inter'; letter-spacing:.1em; margin-left:10px; vertical-align:middle; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; opacity:0; }
  #cta .h { font:900 116px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

def _inbox(unread=True, names=None):
    rows = []
    for n, m, _ in MSGS:
        rows.append(f'<div class="row"><div class="av">{n[0]}</div><div class="tx"><div class="nm">{n}<i>baru</i></div><div class="ms">{m}</div></div>{"<div class=dot></div>" if unread else ""}</div>')
    return "".join(rows)

BODY = f"""
      <div id="handwrap" class="clip" data-start="0" data-duration="{T_CTA:.1f}" data-track-index="1" data-layout-allow-overflow>
        <div id="hand"><div class="phone">
          <div class="notch"></div><div class="status"><span id="stime">9:41</span><span>●●● 5G</span></div>
          <section class="scr" id="s_hook"><div class="busy"><div class="big">DM MASUK.</div><div class="lab">KEDAI KAU · SABTU</div></div></section>
          <section class="scr" id="s_busy"><div class="apphdr">Mesej</div>{_inbox()}</section>
          <section class="scr" id="s_inbox"><div class="busy"><div class="clock" id="clk">3j 12m<small>MASA SEBELUM DIBALAS · CONTOH</small></div></div></section>
          <section class="scr" id="s_cold"><div class="apphdr"><span class="back"></span>Aina</div>
            <div class="bubble in">Hi, ada slot untuk 10 orang Sabtu ni?</div><div class="bubble out">Hi! Ada, boleh 😊</div><div class="seen">Dilihat</div>
            <div class="cold" id="coldtx">Tiada balasan.</div></section>
          <section class="scr" id="s_lost"><div class="busy"><div class="big" style="color:var(--grey)">Dia dah<br>tempah<br>tempat lain.</div><div class="lab">CONTOH</div></div></section>
          <section class="scr" id="s_sys"><div class="apphdr">Sistem DM <span class="tag">AKTIF</span></div>
            <div class="sysrow" id="r1"><b>01</b><p>Balasan segera<i>Soalan lazim dijawab terus</i></p></div>
            <div class="sysrow" id="r2"><b>02</b><p>Tanya keperluan<i>Tarikh, jumlah orang, bajet</i></p></div>
            <div class="sysrow" id="r3"><b>03</b><p>Follow-up berjadual<i>Lead yang senyap diingatkan</i></p></div>
            <div class="sysrow" id="r4"><b>04</b><p>Label & jejak<i>Tahu DM mana jadi jualan</i></p></div></section>
          <section class="scr" id="s_fu"><div class="apphdr"><span class="back"></span>Aina</div>
            <div class="bubble in">Hi, ada slot untuk 10 orang Sabtu ni?</div>
            <div class="bubble out">Ada! Pukul berapa ya? Nak set biasa atau set keluarga?</div>
            <div class="bubble in">Pukul 8 malam. Set keluarga.</div>
            <div class="bubble out">Dah ditempah ✓ Kami ingatkan sehari sebelum.</div></section>
          <section class="scr" id="s_win"><div class="busy"><div class="big">TEMPAHAN<br><span class="gr">SAH.</span></div><div class="lab">CONTOH</div></div></section>
          <div class="toast" id="toast0"><div class="av">A</div><div><b>Aina</b><span>{MSGS[0][1]}</span></div></div>
          <div class="toast" id="toast1"><div class="av">F</div><div><b>Faiz</b><span>{MSGS[1][1]}</span></div></div>
          <div class="toast" id="toast2"><div class="av">M</div><div><b>Mei</b><span>{MSGS[2][1]}</span></div></div>
          <div class="toast" id="toast3"><div class="av">R</div><div><b>Ravi</b><span>{MSGS[3][1]}</span></div></div>
        </div></div>
      </div>
      <div id="cta" class="clip" data-start="{T_CTA}" data-duration="{60 - T_CTA}" data-track-index="2">
        <div class="h"><span class="el">LEAD TAK</span><br><span class="el">HILANG.</span><br><span class="el gr">IA SEJUK.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>SISTEM DM & FOLLOW-UP</label><small>Untuk kedai yang sibuk</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

SCREENS = [("s_hook", T_HOOK, T_BUSY), ("s_busy", T_BUSY, T_INBOX), ("s_inbox", T_INBOX, T_COLD), ("s_cold", T_COLD, T_LOST),
           ("s_lost", T_LOST, T_TURN), ("s_sys", T_TURN, T_FU), ("s_fu", T_FU, T_WIN), ("s_win", T_WIN, T_CTA)]

def _js():
    j = []
    A = j.append
    # handheld camera: slow drift + tilt, a punch-in on key beats
    A(f'tl.fromTo("#hand", {{rotationX:16, rotationY:-14, rotationZ:-3, y:120, scale:.86}}, {{rotationX:6, rotationY:6, rotationZ:1.5, y:0, scale:1, duration:6, ease:"expo.out"}}, 0);')
    A(f'tl.to("#hand", {{rotationY:-5, rotationX:3, rotationZ:-1, duration:{T_CTA - 6:.1f}, ease:"sine.inOut"}}, 6);')
    for i, (sid, a, b) in enumerate(SCREENS):
        A(f'tl.fromTo("#{sid}", {{opacity:0, x:{60 if i % 2 else -60}}}, {{opacity:1, x:0, duration:.35, ease:"expo.out"}}, {a + .02:.2f});')
        A(f'tl.to("#{sid}", {{opacity:0, duration:.2, ease:"power2.in"}}, {b - .2:.2f});')
    A(f'tl.fromTo("#s_hook .big", {{scale:1.5, opacity:0}}, {{scale:1, opacity:1, duration:.5, ease:"expo.out"}}, .2);')
    for k, (n, msg, t) in enumerate(MSGS):
        A(f'tl.fromTo("#toast{k}", {{y:-160, opacity:0}}, {{y:0, opacity:1, duration:.4, ease:"back.out(1.6)"}}, {t:.2f});')
        A(f'tl.to("#toast{k}", {{y:-160, opacity:0, duration:.3, ease:"power2.in"}}, {t + 1.0:.2f});')
    A(f'tl.fromTo("#s_busy .row", {{x:80, opacity:0}}, {{x:0, opacity:1, duration:.4, ease:"expo.out", stagger:1.2}}, {T_BUSY + 1.1:.2f});')
    A(f'tl.fromTo("#clk", {{scale:.6, opacity:0}}, {{scale:1, opacity:1, duration:.6, ease:"expo.out"}}, {T_INBOX + .2:.2f});')
    A(f'tl.to("#hand", {{scale:1.1, duration:5, ease:"power1.inOut"}}, {T_INBOX:.2f});')
    A(f'tl.to("#hand", {{scale:1, duration:.6, ease:"expo.out"}}, {T_COLD:.2f});')
    A(f'tl.fromTo("#s_cold .bubble, #s_cold .seen", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:.4, ease:"expo.out", stagger:1.0}}, {T_COLD + .4:.2f});')
    A(f'tl.fromTo("#coldtx", {{opacity:0}}, {{opacity:1, duration:1.2, ease:"power1.in"}}, {T_COLD + 3.4:.2f});')
    A(f'tl.fromTo("#s_lost .big", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:.8, ease:"expo.out"}}, {T_LOST + .3:.2f});')
    A(f'tl.fromTo(".sysrow", {{x:90, opacity:0}}, {{x:0, opacity:1, duration:.5, ease:"expo.out", stagger:1.3}}, {T_TURN + .6:.2f});')
    A(f'tl.fromTo("#s_fu .bubble", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:.4, ease:"expo.out", stagger:1.25}}, {T_FU + .4:.2f});')
    A(f'tl.fromTo("#s_win .big", {{scale:1.4, opacity:0}}, {{scale:1, opacity:1, duration:.5, ease:"expo.out"}}, {T_WIN + .2:.2f});')
    A(f'tl.to("#hand", {{y:-1600, rotationX:30, duration:.7, ease:"power3.in"}}, {T_CTA - .7:.2f});')
    A(f'tl.fromTo("#cta", {{opacity:0}}, {{opacity:1, duration:.3}}, {T_CTA:.2f});')
    A(f'tl.fromTo("#cta .el", {{yPercent:100, opacity:0}}, {{yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}}, {T_CTA + .2:.2f});')
    A(f'tl.fromTo("#ctarule", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:.7, ease:"expo.inOut"}}, {T_CTA + 1.1:.2f});')
    A(f'tl.fromTo("#ctab", {{y:60, opacity:0}}, {{y:0, opacity:1, duration:.7, ease:"expo.out"}}, {T_CTA + 1.6:.2f});')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(50, [62, 65, 69, 72]), (46, [58, 62, 65, 69]), (43, [55, 58, 62, 65]), (45, [57, 61, 64, 67])]
    m.score(84, prog, kind="piano", drums="half", start=0, end=T_LOST, swing=.12)
    m.drone(lib.hz(38), T_LOST, T_TURN + .5, .12)
    m.score(84, prog, kind="piano", drums="half", start=T_TURN, end=59, swing=.12)
    for _, _, t in MSGS: m.at(m.fx, m.notif(), t, .5)
    for k in range(4): m.at(m.fx, m.tick(), T_BUSY + 1.1 + 1.2 * k, .3)
    tt = T_INBOX + .2
    while tt < T_COLD - .3: m.at(m.fx, m.tick(), tt, .25); tt += 1.0
    for k in range(3): m.at(m.fx, m.pop(700), T_COLD + .4 + k, .3)
    for k in range(4): m.at(m.fx, m.pop(900 + 80 * k), T_TURN + .6 + 1.3 * k, .3)
    for k in range(4): m.at(m.fx, m.pop(800), T_FU + .4 + 1.25 * k, .3)
    m.at(m.fx, m.riser(1.6), T_WIN - 1.6, .3); m.at(m.fx, m.impact(), T_WIN + .2, .6)
    m.at(m.fx, m.whoosh(.6), T_CTA - .7, .4)
