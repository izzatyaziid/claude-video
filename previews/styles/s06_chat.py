"""06 DRAMA CHAT — a story told in message bubbles, edited like a thriller: typing dots, silences, read receipts.
Idea: when the first answer is only the price, the chat dies; build value and trust before the price."""
NAME = "LokaDigital Preview 06 · Drama Chat"
SLUG = "06-drama-chat"
PILL = "CONTOH · KEDAI KEK"

# (time, side, text, kind)  side: in|out ; kind: msg|typing|seen|sys
ACT1 = [
    (1.2, "in", "Kek coklat 1kg berapa?", "msg"),
    (3.0, "out", "", "typing"),
    (4.4, "out", "RM90.", "msg"),
    (5.6, "out", "Dilihat", "seen"),
]
ACT2 = [
    (30.0, "in", "Kek coklat 1kg berapa?", "msg"),
    (31.8, "out", "", "typing"),
    (33.0, "out", "Untuk majlis apa ya? Birthday anak? 🎂", "msg"),
    (35.6, "in", "Ha'ah, anak umur 6.", "msg"),
    (37.6, "out", "Kek coklat lembap, tulis nama dia free. Ramai mak ayah ambil yang ni untuk birthday.", "msg"),
    (40.6, "out", "[ gambar 3 kek birthday · CONTOH ]", "img"),
    (42.6, "out", "1kg RM90, siap dalam 2 hari. Nak saya lock tarikh?", "msg"),
    (45.4, "in", "Ok nak! Sabtu boleh?", "msg"),
]

CSS = """
  #chat { position:absolute; left:60px; right:60px; top:420px; height:1180px; overflow:hidden; }
  #feed1 { position:absolute; left:0; right:0; bottom:0; display:flex; flex-direction:column; gap:22px; }
  #feed2 { position:absolute; left:0; right:0; top:150px; display:flex; flex-direction:column; gap:22px; }
  .b { max-width:760px; padding:30px 36px; border-radius:40px; font:600 44px/1.25 'Inter'; letter-spacing:-.01em; opacity:0; }
  .b.in { background:#221a2e; color:#fff; border-bottom-left-radius:12px; align-self:flex-start; }
  .b.out { background:var(--g); color:var(--ink); border-bottom-right-radius:12px; align-self:flex-end; }
  .b.img { background:linear-gradient(135deg,#7B16B8,#240538); color:var(--mist); height:300px; display:flex; align-items:center; justify-content:center; font:700 32px 'Inter'; letter-spacing:.08em; align-self:flex-end; width:560px; }
  .b.typing { padding:28px 34px; align-self:flex-end; background:#2b2238; display:flex; gap:12px; }
  .b.typing i { width:18px; height:18px; border-radius:50%; background:var(--mist); display:block; }
  .b.seen { padding:0; background:none; align-self:flex-end; font:600 30px 'Inter'; color:var(--grey); }
  .hdr { position:absolute; left:60px; right:60px; top:420px; display:flex; align-items:center; gap:22px; padding-bottom:26px; border-bottom:1px solid var(--line); }
  .hdr .av { width:84px; height:84px; border-radius:50%; background:linear-gradient(135deg,var(--mag),var(--p1)); }
  .hdr b { font:800 40px 'Inter'; } .hdr small { display:block; font:500 28px 'Inter'; color:var(--grey); }
  .big { position:absolute; left:96px; right:96px; font:900 110px/0.94 'Inter'; letter-spacing:-.05em; opacity:0; }
  .cntr { position:absolute; left:0; right:0; top:900px; text-align:center; font:900 220px 'Inter'; letter-spacing:-.06em; color:var(--grey); opacity:0; }
  .rules { position:absolute; left:96px; right:96px; top:700px; display:flex; flex-direction:column; gap:26px; }
  .rule1 { display:flex; gap:28px; align-items:center; padding:30px 36px; border-radius:26px; background:var(--glass); border:2px solid var(--line); opacity:0; }
  .rule1 b { font:900 70px 'Inter'; color:var(--g); min-width:110px; } .rule1 p { font:800 46px/1.1 'Inter'; letter-spacing:-.02em; }
  #cta { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #cta .h { font:900 112px/0.92 'Inter'; letter-spacing:-.05em; }
  #cta .rule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
"""

def bub(i, side, text, kind, pre):
    if kind == "typing": return f'<div class="b typing" id="{pre}{i}"><i></i><i></i><i></i></div>'
    if kind == "seen": return f'<div class="b seen" id="{pre}{i}">{text}</div>'
    if kind == "img": return f'<div class="b img" id="{pre}{i}">{text}</div>'
    return f'<div class="b {side}" id="{pre}{i}">{text}</div>'

BODY = f"""
      <div class="hdr clip" id="hdr" data-start="0" data-duration="49" data-track-index="1"><div class="av"></div><div><b>Kedai Kek (contoh)</b><small>Business · biasanya balas dalam 1 jam</small></div></div>
      <div id="chatw" class="clip" data-start="0" data-duration="49" data-track-index="2"><div id="chat">
        <div id="feed1">{''.join(bub(i, a[1], a[2], a[3], "a") for i, a in enumerate(ACT1))}</div>
        <div id="feed2">{''.join(bub(i, a[1], a[2], a[3], "b") for i, a in enumerate(ACT2))}</div>
      </div></div>
      <div class="cntr clip" id="cntr" data-start="7" data-duration="6" data-track-index="3"><span id="cn">1 jam</span></div>
      <div class="big clip" id="big1" data-start="13" data-duration="5.6" data-track-index="3" style="top:820px">Senyap.<br><span style="color:var(--grey)">Selamanya.</span></div>
      <div class="big clip" id="big2" data-start="18.8" data-duration="10.6" data-track-index="3" style="top:520px;font-size:96px">Harga je,<br>tanpa nilai,<br><span class="gr">orang banding</span><br><span class="gr">harga je.</span></div>
      <div class="big clip" id="big3" data-start="25.4" data-duration="4" data-track-index="4" style="top:1300px;font-size:64px;color:var(--mist)">Cuba sekali lagi.</div>
      <div class="rules clip" id="rules" data-start="49" data-duration="4.8" data-track-index="3">
        <div class="rule1"><b>01</b><p>Tanya dulu, <span class="gr">kenal dia.</span></p></div>
        <div class="rule1"><b>02</b><p>Tunjuk bukti & cerita.</p></div>
        <div class="rule1"><b>03</b><p>Harga datang <span class="gr">selepas nilai.</span></p></div>
      </div>
      <div id="cta" class="clip" data-start="53.8" data-duration="6.2" data-track-index="5">
        <div class="h"><span class="el">NILAI DULU.</span><br><span class="el gr">HARGA</span><br><span class="el gr">KEMUDIAN.</span></div>
        <div class="rule" id="ctarule"></div>
        <div class="ctablock" id="ctab"><div><label>SKRIP DM & SALES</label><small>Chat yang jadi tempahan</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    j = []; A = j.append
    A('tl.fromTo("#hdr", {y:-40, opacity:0}, {y:0, opacity:1, duration:.5, ease:"expo.out"}, .2);')
    for pre, acts in (("a", ACT1), ("b", ACT2)):
        for i, (t, side, text, kind) in enumerate(acts):
            sel = f"#{pre}{i}"
            if kind == "typing":
                A(f'tl.fromTo("{sel}", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.25, ease:"back.out(2)"}}, {t:.2f});')
                A(f'tl.fromTo("{sel} i", {{y:0}}, {{y:-10, duration:.2, yoyo:true, repeat:5, stagger:.1, ease:"sine.inOut"}}, {t:.2f});')
                nxt = acts[i + 1][0]
                A(f'tl.to("{sel}", {{opacity:0, height:0, padding:0, duration:.15}}, {nxt - .15:.2f});')
            else:
                A(f'tl.fromTo("{sel}", {{opacity:0, y:40, scale:.9, transformOrigin:"{"0% 100%" if side == "in" else "100% 100%"}"}}, {{opacity:1, y:0, scale:1, duration:.35, ease:"back.out(1.7)"}}, {t:.2f});')
    A('tl.set("#feed2", {opacity:0}, 0); tl.set("#feed2", {opacity:1}, 29.6);')
    A('tl.to("#feed1", {opacity:0, duration:.4}, 29.2);')
    A('tl.to("#chat", {y:-40, duration:1, ease:"power2.out"}, 6.2);')
    A('tl.to("#feed2", {y:-300, duration:1.2, ease:"power2.inOut"}, 40.2);')
    A('tl.fromTo("#cntr", {opacity:0, scale:.7}, {opacity:1, scale:1, duration:.5, ease:"expo.out"}, 7.1);')
    A('tl.to("#chatw", {opacity:.25, duration:.6}, 7);')
    A('tl.to("#chatw", {opacity:1, duration:.4}, 29.4);')
    A('tl.to("#chatw", {opacity:.15, duration:.4}, 13);')
    for k, word in enumerate(["3 jam", "1 hari", "3 hari"]):
        A(f'tl.set("#cn", {{textContent:"{word}"}}, {8.6 + k * 1.4:.2f});')
    A('tl.fromTo("#big1", {y:50, opacity:0}, {y:0, opacity:1, duration:.6, ease:"expo.out"}, 13.1);')
    A('tl.fromTo("#big2", {y:50, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 18.9);')
    A('tl.fromTo("#big3", {opacity:0}, {opacity:1, duration:.5}, 25.6);')
    A('tl.to("#chatw", {opacity:.2, duration:.4}, 48.4);')
    A('tl.fromTo(".rule1", {x:-100, opacity:0}, {x:0, opacity:1, duration:.5, ease:"expo.out", stagger:.5}, 49.1);')
    A('tl.fromTo("#cta .el", {yPercent:100, opacity:0}, {yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}, 54);')
    A('tl.fromTo("#ctarule", {scaleX:0, transformOrigin:"0% 50%"}, {scaleX:1, duration:.7, ease:"expo.inOut"}, 54.9);')
    A('tl.fromTo("#ctab", {y:60, opacity:0}, {y:0, opacity:1, duration:.7, ease:"expo.out"}, 55.4);')
    return "\n      ".join(j)
JS = _js()

def sound(m):
    import lib
    m.score(92, [(50, [62, 65, 69]), (46, [58, 62, 65])], kind="pluck", drums="half", start=0, end=6.5)
    m.drone(lib.hz(36), 6.5, 29, .1)
    for k in range(4): m.at(m.fx, m.tick(), 8.6 + k * 1.4 - 1.4, .4)
    m.at(m.fx, m.thud(), 13.1, .5)
    prog = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
    m.score(92, prog, kind="pluck", drums="four", start=29.6, end=59)
    for t, side, text, kind in ACT1 + ACT2:
        if kind in ("msg", "img"): m.at(m.fx, m.pop(1000 if side == "out" else 650), t, .35)
        if kind == "typing":
            for k in range(6): m.at(m.fx, m.type_(), t + k * .2, .3)
    for k in range(3): m.at(m.fx, m.pop(800), 49.1 + .5 * k, .35)
    m.at(m.fx, m.riser(1.6), 52.2, .3); m.at(m.fx, m.impact(), 53.85, .6)
