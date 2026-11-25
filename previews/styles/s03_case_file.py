"""03 FAIL SIASATAN — an evidence board; the camera pans from clue to clue, strings get drawn, the case gets stamped.
Idea: customers buy once and vanish; retention + remarketing brings them back."""
NAME = "LokaDigital Preview 03 · Fail Siasatan"
SLUG = "03-fail-siasatan"
PILL = "KES #03 · CONTOH"

# board-space cards: id, x, y, w, h, kind, label, title, sub
CARDS = [
    ("e1", 200, 300, 620, 420, "ev", "BUKTI A", "Beli sekali.", "Resit pertama. Tiada resit kedua."),
    ("e2", 1000, 260, 620, 420, "ev", "BUKTI B", "Senyap selepas beli.", "Tiada mesej, tiada ucapan terima kasih."),
    ("e3", 560, 900, 680, 420, "ev", "BUKTI C", "Tiada sebab datang semula.", "Tiada tawaran, tiada peringatan."),
    ("sus", 520, 1500, 760, 460, "sus", "SUSPEK", "Semua bajet untuk cari pelanggan BARU.", "Pelanggan lama dibiarkan."),
    ("s1", 160, 2150, 640, 360, "sol", "01", "Simpan senarai pembeli", "WhatsApp / CRM yang tersusun"),
    ("s2", 1000, 2150, 640, 360, "sol", "02", "Mesej selepas beli", "Terima kasih + minta ulasan"),
    ("s3", 160, 2620, 640, 360, "sol", "03", "Tawaran pelanggan setia", "Sebab untuk datang semula"),
    ("s4", 1000, 2620, 640, 360, "sol", "04", "Remarketing ads", "Iklan kepada yang pernah beli"),
]
STRINGS_RED = [("e1", "sus"), ("e2", "sus"), ("e3", "sus")]
STRINGS_G = [("s1", "s2"), ("s2", "s4"), ("s4", "s3"), ("s3", "s1")]
BW, BH = 1800, 3200

def C(cid):
    c = next(c for c in CARDS if c[0] == cid); return c[1] + c[3] / 2, c[2] + c[4] / 2

# camera stops: (t, cx, cy, scale)
CAM = [(0, 900, 700, .42), (5, 510, 510, .95), (9, 1310, 470, .95), (13, 900, 1110, .95), (17, 900, 1730, .9),
       (23, 900, 1200, .45), (28, 480, 2330, .95), (32, 1320, 2330, .95), (36, 480, 2800, .95), (40, 1320, 2800, .95),
       (44, 900, 2560, .52), (52, 900, 2560, .52)]

CSS = f"""
  #cam {{ position:absolute; left:0; top:0; width:{BW}px; height:{BH}px; transform-origin:0 0; }}
  #board {{ position:absolute; inset:0; border-radius:40px; background:
            radial-gradient(60% 40% at 30% 20%, rgba(70,9,107,.45), transparent 70%),
            repeating-linear-gradient(0deg, rgba(255,255,255,.025) 0 2px, transparent 2px 80px),
            repeating-linear-gradient(90deg, rgba(255,255,255,.025) 0 2px, transparent 2px 80px), #0c0814; border:2px solid var(--line); }}
  .cardx {{ position:absolute; padding:40px 44px; border-radius:22px; background:#151020; border:2px solid var(--line); box-shadow:0 40px 80px rgba(0,0,0,.6); }}
  .cardx .pin {{ position:absolute; left:50%; top:-18px; width:36px; height:36px; margin-left:-18px; border-radius:50%; background:var(--mag); box-shadow:0 6px 12px rgba(0,0,0,.6); }}
  .cardx .l {{ font:700 30px 'Inter'; letter-spacing:.3em; color:var(--grey); }}
  .cardx .t {{ margin-top:22px; font:800 62px/1.02 'Inter'; letter-spacing:-.035em; }}
  .cardx .s {{ margin-top:18px; font:500 34px/1.3 'Inter'; color:var(--mist); }}
  .cardx.sus {{ background:#1c0a24; border-color:rgba(184,0,240,.6); }}
  .cardx.sus .l {{ color:var(--mag); }}
  .cardx.sol {{ background:#131a0e; border-color:rgba(180,255,57,.45); }}
  .cardx.sol .l {{ font:900 64px 'Inter'; letter-spacing:-.03em; color:var(--g); }}
  .cardx.sol .t {{ font-size:50px; margin-top:12px; }}
  .cardx.sol .pin {{ background:var(--g); }}
  #strings {{ position:absolute; left:0; top:0; width:{BW}px; height:{BH}px; overflow:visible; }}
  .stamp {{ position:absolute; left:440px; top:2420px; padding:24px 50px; border:10px solid var(--g); border-radius:24px; color:var(--g);
            font:900 120px 'Inter'; letter-spacing:.02em; transform:rotate(-8deg); opacity:0; background:rgba(7,4,12,.6); }}
  #title {{ position:absolute; left:100px; top:470px; width:880px; }}
  #title .k {{ font:700 30px 'Inter'; letter-spacing:.4em; color:var(--grey); }}
  #title .h {{ margin-top:20px; font:900 120px/0.92 'Inter'; letter-spacing:-.05em; }}
  #title .tw {{ margin-top:30px; font:600 44px 'IBM Plex Mono'; color:var(--g); }}
  .sup {{ position:absolute; left:100px; right:100px; top:1480px; font:900 78px/0.98 'Inter'; letter-spacing:-.04em; text-shadow:0 20px 60px rgba(0,0,0,.9); }}
  #cta {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }}
  #cta .h {{ font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }}
  #cta .rule {{ width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }}
"""

def _cards():
    out = []
    for cid, x, y, w, h, kind, l, t, s in CARDS:
        out.append(f'<div class="cardx {kind}" id="{cid}" style="left:{x}px;top:{y}px;width:{w}px;min-height:{h}px"><div class="pin"></div><div class="l">{l}</div><div class="t">{t}</div><div class="s">{s}</div></div>')
    return "".join(out)

def _strings():
    o = []
    for i, (a, b) in enumerate(STRINGS_RED):
        (x1, y1), (x2, y2) = C(a), C(b)
        o.append(f'<path class="sr" id="sr{i}" d="M{x1:.0f} {y1:.0f} Q {(x1+x2)/2:.0f} {(y1+y2)/2+80:.0f} {x2:.0f} {y2:.0f}" fill="none" stroke="#B800F0" stroke-width="8" stroke-linecap="round"/>')
    for i, (a, b) in enumerate(STRINGS_G):
        (x1, y1), (x2, y2) = C(a), C(b)
        o.append(f'<path class="sg" id="sg{i}" d="M{x1:.0f} {y1:.0f} L {x2:.0f} {y2:.0f}" fill="none" stroke="#B4FF39" stroke-width="10" stroke-linecap="round"/>')
    return "".join(o)

SUPS = [("sp1", 23.3, 27.8, 'Pelanggan lama <span class="gr">dah kenal kau.</span>'),
        ("sp2", 44.6, 51.6, 'Jual semula biasanya <span class="gr">lebih murah</span> daripada cari orang baru.')]

BODY = f"""
      <div id="camwrap" class="clip" data-start="0" data-duration="52" data-track-index="1" data-layout-allow-overflow data-layout-ignore>
        <div id="cam"><div id="board"></div><svg id="strings" viewBox="0 0 {BW} {BH}">{_strings()}</svg>{_cards()}<div class="stamp" id="stamp">KES SELESAI</div></div>
      </div>
      <div id="title" class="clip" data-start="0" data-duration="4.6" data-track-index="2">
        <div class="k">FAIL KES #03</div><div class="h">PELANGGAN<br>YANG <span class="gr">HILANG.</span></div><div class="tw" id="tw">status: belum selesai_</div>
      </div>
      {''.join(f'<div class="sup clip" id="{i}" data-start="{a}" data-duration="{b - a:.1f}" data-track-index="3">{t}</div>' for i, a, b, t in SUPS)}
      <div id="cta" class="clip" data-start="52" data-duration="8" data-track-index="4">
        <div class="h"><span class="el">JANGAN BIAR</span><br><span class="el">PELANGGAN</span><br><span class="el gr">HILANG.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>RETENTION & REMARKETING</label><small>Sistem pelanggan setia</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _cam(cx, cy, s):  # board point (cx,cy) to screen centre (540,1020)
    return 540 - cx * s, 1020 - cy * s

def _js():
    j = []; A = j.append
    x0, y0 = _cam(*CAM[0][1:3], CAM[0][3])
    A(f'tl.set("#cam", {{x:{x0:.0f}, y:{y0:.0f}, scale:{CAM[0][3]}, transformOrigin:"0 0"}}, 0);')
    for (t0, *_), (t1, cx, cy, s) in zip(CAM, CAM[1:]):
        x, y = _cam(cx, cy, s)
        A(f'tl.to("#cam", {{x:{x:.0f}, y:{y:.0f}, scale:{s}, duration:1.3, ease:"power3.inOut"}}, {t0 + (t1 - t0) - 1.3 if t1 - t0 > 1.3 else t0:.2f});')
    A('tl.fromTo("#title .h", {yPercent:30, opacity:0}, {yPercent:0, opacity:1, duration:.7, ease:"expo.out"}, .2);')
    A('tl.fromTo("#tw", {clipPath:"inset(0 100% 0 0)"}, {clipPath:"inset(0 0% 0 0)", duration:1.4, ease:"steps(24)"}, 1.2);')
    for cid, t in [("e1", 4.4), ("e2", 8.4), ("e3", 12.4), ("sus", 16.4), ("s1", 27.4), ("s2", 31.4), ("s3", 35.4), ("s4", 39.4)]:
        A(f'tl.fromTo("#{cid}", {{y:-80, rotation:{-6 if hash(cid) % 2 else 5}, opacity:0}}, {{y:0, rotation:{-1.5 if hash(cid) % 2 else 1.2}, opacity:1, duration:.55, ease:"back.out(1.6)"}}, {t:.2f});')
    for i in range(3):
        A(f'tl.fromTo("#sr{i}", {{strokeDasharray:1600, strokeDashoffset:1600}}, {{strokeDashoffset:0, duration:.9, ease:"power2.inOut"}}, {19 + i * .6:.2f});')
    for i in range(4):
        A(f'tl.fromTo("#sg{i}", {{strokeDasharray:1000, strokeDashoffset:1000}}, {{strokeDashoffset:0, duration:.8, ease:"power2.inOut"}}, {41 + i * .6:.2f});')
    A('tl.to(".sr", {opacity:.15, duration:.6}, 27);')
    A('tl.fromTo("#stamp", {scale:2.2, opacity:0}, {scale:1, opacity:1, duration:.35, ease:"power4.in"}, 47.2);')
    for i, a, b, t in SUPS:
        A(f'tl.fromTo("#{i}", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:.6, ease:"expo.out"}}, {a + .1:.2f});')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 52.2);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 53.1);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 53.6);')
    A('tl.to("#camwrap", {opacity:0, duration:.4}, 51.6);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    prog = [(40, [52, 55, 59]), (36, [48, 52, 55]), (38, [50, 53, 57]), (35, [47, 50, 54])]
    m.drone(lib.hz(28), 0, 26, .14)
    m.score(70, prog, kind="piano", drums="half", start=4, end=26)
    m.score(96, [(45, [57, 60, 64, 67]), (41, [53, 57, 60, 64]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])], kind="pluck", drums="four", start=27, end=59)
    for k in range(14): m.at(m.fx, m.type_(), 1.2 + k * .1, .4)
    for t in (4.4, 8.4, 12.4, 16.4, 27.4, 31.4, 35.4, 39.4): m.at(m.fx, m.pop(500), t + .3, .35)
    for (t0, *_), (t1, *_r) in zip(CAM, CAM[1:]):
        m.at(m.fx, m.whoosh(.9), t1 - 1.3, .2)
    for i in range(3): m.at(m.fx, m.whoosh(.8, False), 19 + i * .6, .15)
    m.at(m.fx, m.stamp(), 47.55, .9); m.at(m.fx, m.riser(1.5), 50.5, .25); m.at(m.fx, m.impact(), 52.05, .6)
