"""LokaDigital · "Macam Mana Nak Mula Bisnes Dengan RM1,000" (Education · Practical Strategy, ~60 s).
Follows the user's storyboard beat by beat. Principle: test first, then scale. No budget split shown as a formula.
Techniques: REF-001 (word-by-word headline, visuals that explain), REF-002 (3-tier layout, boxed caption, pop-out 3D),
LokaDigital package-sheet identity. Usage: python3 build.py"""
import json, os, sys, shutil, math, subprocess
import numpy as np, wave
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "previews"))
import lib, pop as P

T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
L = {l["id"]: l for l in T["lines"]}
DUR = None  # set after helpers
def s(i): return L[i]["start"]
def e(i): return L[i]["end"]
def w(i, k): return L[i]["words"][min(k, len(L[i]["words"]) - 1)]["start"]
DUR = round(T["lines"][-1]["end"] + 1.6, 2)
KEYS = {"seribu", "ringgit", "semua", "satu", "jelas.", "angle", "masalah,", "manfaat,", "offer.", "respons", "berkualiti.", "bajet", "scale", "potensi.", "meneka.", "data,", "LokaDigital."}
AVATAR = [p for p in ("neutral", "shock", "think") if os.path.exists(os.path.join(HERE, "assets", f"avatar_{p}.png"))]

CSS = P.CSS + """
  .hdrline { position:absolute; left:96px; right:96px; top:420px; display:flex; justify-content:space-between; padding-bottom:14px; border-bottom:2px solid rgba(255,255,255,.12); font:600 26px 'IBM Plex Mono'; letter-spacing:.12em; color:var(--grey); }
  .hl { position:absolute; left:96px; right:96px; top:476px; font:900 62px/1.06 'Inter'; letter-spacing:-.035em; color:#fff; opacity:0; }
  .hl span { display:inline-block; opacity:.16; } .hl span.kk { color:var(--g); }
  #hook { position:absolute; left:96px; right:96px; top:476px; font:900 70px/1.0 'Inter'; letter-spacing:-.045em; }
  #hook em { font-style:normal; color:var(--g); }
  .stage3d { top:660px; height:620px; }
  .note { position:absolute; width:250px; height:130px; border-radius:18px; background:linear-gradient(150deg,#d4ff7a,#B4FF39 55%,#86c522);
          box-shadow:0 30px 60px rgba(0,0,0,.55), 0 0 50px rgba(180,255,57,.35), inset 0 2px 0 rgba(255,255,255,.6); color:var(--ink); opacity:0; }
  .note b { position:absolute; left:20px; top:14px; font:900 46px 'Inter'; letter-spacing:-.03em; } .note i { position:absolute; right:18px; bottom:12px; width:58px; height:58px; border-radius:50%; border:5px solid rgba(7,4,12,.3); }
  .note small { position:absolute; left:20px; bottom:14px; font:800 16px 'Inter'; letter-spacing:.2em; opacity:.6; }
  #tot { position:absolute; left:270px; top:520px; padding:16px 30px; border-radius:99px; font:900 46px 'Inter'; letter-spacing:-.02em; }
  .prod { position:absolute; left:70px; top:120px; width:300px; height:360px; border-radius:30px; padding:24px; }
  .box3 { position:absolute; left:60px; top:70px; width:180px; height:180px; border-radius:24px; background:linear-gradient(150deg,#C99BFF,#7B16B8); box-shadow:0 20px 40px rgba(0,0,0,.5), inset 0 2px 0 rgba(255,255,255,.4); }
  .box3:after { content:""; position:absolute; left:70px; top:-18px; width:40px; height:36px; border-radius:10px; background:var(--g); }
  .prod small { position:absolute; left:24px; bottom:24px; font:800 22px 'Inter'; letter-spacing:.2em; color:var(--mist); }
  #crowd { position:absolute; left:400px; top:40px; width:620px; height:520px; overflow:visible; }
  #crowd .dot { fill:#8C83A6; }
  .aud { position:absolute; left:460px; top:390px; width:520px; padding:22px 28px; border-radius:22px; }
  .aud b { display:block; font:800 24px 'Inter'; letter-spacing:.2em; } .aud p { margin-top:8px; font:800 38px/1.1 'Inter'; letter-spacing:-.02em; }
  .no { position:absolute; left:470px; top:70px; padding:14px 24px; border-radius:16px; font:900 40px 'Inter'; transform:rotate(-5deg); }
  .phone { position:absolute; left:80px; top:40px; width:330px; height:560px; border-radius:46px; background:#0b0711; border:6px solid #2a2036; overflow:hidden; box-shadow:0 40px 90px rgba(0,0,0,.6); }
  .phone .vf { position:absolute; inset:14px; border-radius:36px; background:radial-gradient(70% 55% at 50% 45%, #3a1a5c, #120a1d); overflow:hidden; }
  .phone .grid { position:absolute; inset:0; background:linear-gradient(90deg, transparent 33%, rgba(255,255,255,.15) 33.3%, transparent 33.6%, transparent 66.4%, rgba(255,255,255,.15) 66.6%, transparent 67%),
                 linear-gradient(0deg, transparent 33%, rgba(255,255,255,.15) 33.3%, transparent 33.6%, transparent 66.4%, rgba(255,255,255,.15) 66.6%, transparent 67%); }
  .phone .box3 { left:70px; top:160px; width:160px; height:160px; }
  .rec { position:absolute; left:50%; bottom:26px; width:70px; height:70px; margin-left:-35px; border-radius:50%; border:6px solid #fff; }
  .rec i { position:absolute; inset:8px; border-radius:50%; background:#ff3b5c; }
  .recdot { position:absolute; left:26px; top:26px; font:800 22px 'Inter'; color:#fff; } .recdot i { display:inline-block; width:14px; height:14px; border-radius:50%; background:#ff3b5c; margin-right:8px; }
  .ang { position:absolute; left:470px; width:520px; padding:24px 28px; border-radius:22px; display:flex; gap:20px; align-items:center; }
  .ang b { font:900 54px 'Inter'; color:var(--g); min-width:80px; } .ang p { font:800 40px/1.05 'Inter'; letter-spacing:-.02em; } .ang p i { display:block; margin-top:6px; font:600 26px 'Inter'; font-style:normal; color:var(--mist); }
  .vid { position:absolute; top:40px; width:290px; height:520px; border-radius:26px; padding:20px; }
  .vid .th { height:250px; border-radius:16px; background:radial-gradient(70% 60% at 50% 45%, #46096B, #160c22); position:relative; }
  .vid .th .box3 { left:65px; top:45px; width:120px; height:120px; }
  .vid h4 { margin-top:16px; font:900 34px 'Inter'; letter-spacing:-.02em; }
  .met { margin-top:12px; } .met label { display:flex; justify-content:space-between; font:700 20px 'Inter'; letter-spacing:.12em; color:var(--mist); }
  .met .tr { margin-top:6px; height:16px; border-radius:8px; background:rgba(255,255,255,.08); overflow:hidden; } .met .tr i { display:block; height:100%; border-radius:8px; background:var(--lav, #C99BFF); transform-origin:0 50%; }
  .vid.win { border-color:rgba(180,255,57,.8); }
  .crown { position:absolute; left:50%; top:12px; margin-left:-90px; width:180px; padding:10px 0; text-align:center; border-radius:99px; font:900 26px 'Inter'; letter-spacing:.14em; opacity:0; }
  #wallet { position:absolute; left:60px; top:330px; width:300px; height:200px; border-radius:30px; padding:26px; }
  #wallet b { display:block; font:800 24px 'Inter'; letter-spacing:.2em; } #wallet h3 { margin-top:12px; font:900 64px 'Inter'; letter-spacing:-.04em; }
  .coin { position:absolute; width:56px; height:56px; border-radius:50%; background:radial-gradient(circle at 35% 30%, #e6ff9a, #B4FF39 55%, #7fb81e); border:4px solid #e9ffb8;
          box-shadow:0 0 22px rgba(180,255,57,.8); font:900 20px/48px 'Inter'; text-align:center; color:#07040C; opacity:0; }
  #big { position:absolute; left:470px; top:40px; width:520px; height:540px; border-radius:30px; padding:26px; }
  #big .th { height:300px; border-radius:18px; background:radial-gradient(70% 60% at 50% 45%, #7B16B8, #160c22); position:relative; }
  #big .th .box3 { left:170px; top:70px; width:150px; height:150px; }
  #big h4 { margin-top:20px; font:900 52px 'Inter'; letter-spacing:-.03em; } #big p { margin-top:8px; font:700 28px 'Inter'; color:var(--mist); }
  .scale { position:absolute; right:30px; top:30px; padding:10px 20px; border-radius:99px; font:900 26px 'Inter'; letter-spacing:.16em; }
  .ghost { position:absolute; left:470px; width:240px; height:120px; border-radius:20px; border:3px dashed rgba(255,255,255,.2); font:800 22px/120px 'Inter'; text-align:center; letter-spacing:.14em; color:var(--grey); opacity:0; }
  .q { position:absolute; font:900 120px 'Inter'; color:var(--grey); opacity:0; }
  .big2 { position:absolute; left:80px; right:80px; top:120px; font:900 110px/0.92 'Inter'; letter-spacing:-.05em; opacity:0; }
  .big2 s { text-decoration:none; color:var(--grey); } .big2 em { font-style:normal; color:var(--g); }
  #reveal { position:absolute; left:0; right:0; top:760px; text-align:center; opacity:0; }
  #reveal img { width:300px; height:300px; }
  #reveal h2 { margin-top:10px; font:900 100px/0.9 'Inter'; letter-spacing:-.05em; } #reveal h2 em { font-style:normal; color:var(--g); }
  .ctab3 { position:absolute; left:90px; top:120px; width:900px; padding:56px 50px; border-radius:36px; }
  .ctab3 label { display:block; font:800 30px 'Inter'; letter-spacing:.24em; } .ctab3 h2 { margin-top:16px; font:900 120px/0.9 'Inter'; letter-spacing:-.05em; } .ctab3 p { margin-top:20px; font:700 34px 'Inter'; opacity:.8; }
  #av { position:absolute; left:560px; top:1300px; width:500px; height:620px; }
  #av img { position:absolute; left:0; bottom:0; width:500px; opacity:0; filter:drop-shadow(0 24px 34px rgba(0,0,0,.55)); }
  #avglow { position:absolute; left:520px; top:1330px; width:620px; height:620px; border-radius:50%; background:none; display:none; }
  .capband { top:1300px; } .cap { left:70px; right:520px; text-align:left; font-size:60px; }
  #flash { position:absolute; inset:0; background:#fff; opacity:0; mix-blend-mode:overlay; }
"""

def headline(lid):
    l = L[lid]
    spans = " ".join(f'<span class="{"kk" if wd["text"] in KEYS else ""}" id="{lid}w{k}">{wd["text"]}</span>' for k, wd in enumerate(l["words"]))
    return f'<div class="hl clip" id="hl_{lid}" data-start="{max(0, l["start"] - .05):.2f}" data-duration="{l["end"] - l["start"] + l["gap"] + .05:.2f}" data-track-index="3">{spans}</div>'

CAPS = [("k0", 0.0, s("l2"), "Ada [RM1,000]?"), ("k1", s("l2"), s("l4"), "1. Pilih [satu] audience."), ("k2", s("l4"), s("l6"), "2. Test [3] angle."),
        ("k3", s("l6"), s("l7"), "3. Ukur [respons]."), ("k4", s("l7"), s("l8"), "Baru [scale]."), ("k5", s("l8"), s("l10"), "Data, bukan [teka]."), ("k6", s("l10"), DUR, "[DM] LokaDigital.")]

NOTES = [(110, 190, -8), (400, 150, 6), (680, 200, -4), (230, 360, 10), (540, 350, -6)]
DOTS = []
rng = np.random.default_rng(5)
for i in range(70):
    DOTS.append((rng.uniform(20, 600), rng.uniform(20, 340), rng.uniform(9, 14), i % 9 == 4))
VIDS = [("MASALAH", ".35,.20,.30", False), ("MANFAAT", ".55,.40,.45", False), ("OFFER", ".85,.80,.75", True)]

def body():
    notes = "".join(f'<div class="note" id="n{i}" style="left:{x}px;top:{y}px"><b>RM</b><small>BAJET MARKETING</small><i></i></div>' for i, (x, y, r) in enumerate(NOTES))
    dots = "".join(f'<circle class="dot{" hit" if h else ""}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>' for x, y, r, h in DOTS)
    vids = ""
    for i, (lab, vals, win) in enumerate(VIDS):
        a, b, c = vals.split(",")
        vids += (f'<div class="c3 vid{" win" if win else ""}" id="v{i}" style="left:{40 + i * 340}px"><div class="th"><div class="box3"></div></div><h4>{lab}</h4>'
                 f'<div class="met"><label>DM MASUK</label><div class="tr"><i data-v="{a}"></i></div></div>'
                 f'<div class="met"><label>SIMPAN</label><div class="tr"><i data-v="{b}"></i></div></div>'
                 f'<div class="met"><label>KLIK</label><div class="tr"><i data-v="{c}"></i></div></div>'
                 + ('<div class="crown lime c3" id="crown" style="position:absolute">PEMENANG</div>' if win else "") + '<div class="shine"></div></div>')
    coins = "".join(f'<div class="coin" id="co{i}">RM</div>' for i in range(10))
    av = '<div id="avbob" style="position:absolute;inset:0">' + "".join(f'<img id="av_{p}" src="assets/avatar_{p}.png" alt="host">' for p in AVATAR) + '</div>'
    return f"""
      <div class="hdrline clip" id="hdr" data-start="0" data-duration="{DUR}" data-track-index="2"><span id="hdrl">MULA BISNES · RM1,000</span><span id="hdrr">EDUCATION · CONTOH</span></div>
      <div id="hook" class="clip" data-start="0" data-duration="{s('l2') - .1:.2f}" data-track-index="3"><span class="hw">Kalau</span> <span class="hw">aku</span> <span class="hw">ada</span> <span class="hw"><em>RM1,000,</em></span> <span class="hw">bisnes</span> <span class="hw">apa</span> <span class="hw">aku</span> <span class="hw">boleh</span> <span class="hw"><em>mula?</em></span></div>
      {''.join(headline(f"l{i}") for i in range(2, 11))}
      <div class="stage3d clip" id="st" data-start="0" data-duration="{DUR}" data-track-index="4" data-layout-allow-overflow data-layout-ignore><div id="cam" style="position:absolute;inset:0;transform-style:preserve-3d">
        {notes}<div class="c3 lime" id="tot">RM1,000 · CONTOH<div class="shine"></div></div>
        <div class="c3 prod" id="prod"><div class="box3"></div><small>PRODUK KAU</small><div class="shine"></div></div>
        <svg id="crowd" viewBox="0 0 620 520">{dots}<circle id="spot" cx="0" cy="0" r="120" fill="none" stroke="#B4FF39" stroke-width="7" opacity="0"/></svg>
        <div class="c3 mag no" id="no">✕ SEMUA ORANG</div>
        <div class="c3 aud lime" id="aud"><b>AUDIENCE · CONTOH</b><p>Ibu bekerja, 25–35, sibuk, beli online</p><div class="shine"></div></div>
        <div class="phone" id="ph"><div class="vf"><div class="grid"></div><div class="box3"></div><div class="recdot"><i></i>REC</div><div class="rec"><i></i></div></div></div>
        <div class="c3 ang" id="a1" style="top:60px"><b>01</b><p>Masalah<i>"Tak sempat masak?"</i></p></div>
        <div class="c3 ang" id="a2" style="top:230px"><b>02</b><p>Manfaat<i>"Siap dalam 5 minit"</i></p></div>
        <div class="c3 ang" id="a3" style="top:400px"><b>03</b><p>Offer<i>"Beli 2, percuma 1"</i></p></div>
        {vids}
        <div class="c3" id="wallet"><b>BAJET · CONTOH</b><h3>RM</h3></div>
        <div class="c3" id="big"><div class="th"><div class="box3"></div></div><h4>OFFER</h4><p>Content yang dah terbukti</p><div class="c3 lime scale" id="sc">SCALE ↑</div><div class="shine"></div></div>
        
        {coins}
        <div class="q" id="q1" style="left:160px;top:120px">?</div><div class="q" id="q2" style="left:480px;top:40px">?</div><div class="q" id="q3" style="left:800px;top:160px">?</div>
        <div class="big2" id="b1"><s>Jangan</s><br><s>meneka.</s></div>
        <div class="big2" id="b2">Guna<br><em>data.</em></div>
        
        <div class="c3 ctab3 lime" id="cta"><label>MULA DENGAN BETUL</label><h2>DM<br>LOKADIGITAL</h2><p>Test dulu. Baru scale.</p><div class="shine"></div></div>
        {P.sparks_html("sa", 14)}{P.sparks_html("sb", 16)}{P.sparks_html("sc", 18)}
        <div class="ring" id="rg1" style="left:690px;top:120px;width:360px;height:360px"></div>
      </div></div>
      <div id="reveal" class="clip" data-start="{e('l9') + .25:.2f}" data-duration="{max(.6, s('l10') - e('l9') - .15):.2f}" data-track-index="6"><img src="assets/logo_t.png" alt="LOKADIGITAL"><h2>LOKA<em>DIGITAL</em></h2></div>
      <div id="avglow" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5" data-layout-ignore></div>
      <div id="av" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5" data-layout-ignore>{av}</div>
      {P.caps(CAPS)}
      <div id="flash" class="clip" data-start="0" data-duration="{DUR}" data-track-index="8" data-layout-ignore></div>"""

def js():
    j = []; A = j.append
    # word-by-word headline
    for i in range(2, 11):
        lid = f"l{i}"; l = L[lid]
        A(f'tl.set("#hl_{lid}", {{opacity:1}}, {max(0, l["start"] - .05):.2f});')
        for k, wd in enumerate(l["words"]):
            A(f'tl.to("#{lid}w{k}", {{opacity:1, duration:.1}}, {wd["start"]:.2f});')
    # ---- 0-4 s HOOK: hook text + 3D floating money already on screen at frame 0
    A('tl.set("#hook .hw", {opacity:1}, 0);')
    A('tl.fromTo("#hook .hw", {yPercent:60, opacity:0}, {yPercent:0, opacity:1, duration:.35, ease:"back.out(2)", stagger:.06, immediateRender:false}, 0.05);')
    for i, (x, y, r) in enumerate(NOTES):
        A(P.pop(f"#n{i}", 0, frame0=True))
        A(f'tl.fromTo("#n{i}", {{rotationZ:{r}, rotationY:{-25 + i * 12}, rotationX:18, z:{-80 + i * 40}}}, {{rotationZ:{-r}, rotationY:{25 - i * 12}, rotationX:-10, z:{60 - i * 30}, y:-30, duration:{s("l2"):.2f}, ease:"sine.inOut"}}, 0);')
    A(P.pop("#tot", .5, z=-600, scale=.2, ease="back.out(2.6)"))
    A(P.shine("#tot", .9, 500))
    A(f'tl.fromTo("#cam", {{scale:1.12, rotationX:8}}, {{scale:1, rotationX:0, duration:{min(2.5, s("l2")):.2f}, ease:"expo.out"}}, 0);')
    A(f'tl.to("#n0, #n1, #n2, #n3, #n4, #tot", {{opacity:0, z:-500, duration:.3, ease:"power3.in"}}, {s("l2") - .3:.2f});')
    # ---- 4-12 s product + one niche audience
    A(P.pop("#prod", s("l2") + .05, ry=40, z=-700, scale=.2)); A(P.shine("#prod", s("l2") + .5, 400)); A(P.floaty("#prod", s("l2") + .6, s("l4") - .4, amp=10, rot=-5))
    A(f'tl.fromTo("#crowd .dot", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:.3, ease:"back.out(2)", stagger:{{each:.008, from:"random"}}}}, {s("l2") + .2:.2f});')
    A(P.pop("#no", w("l2", 4), z=-500, scale=.2, ease="back.out(3)"))
    A(f'tl.to("#no", {{opacity:0, duration:.3}}, {s("l3"):.2f});')
    hx, hy = [(x, y) for x, y, r, h in DOTS if h][2]
    A(f'tl.set("#spot", {{attr:{{cx:{hx:.0f}, cy:{hy:.0f}}}}}, 0);')
    A(f'tl.fromTo("#spot", {{opacity:0, scale:2.5, transformOrigin:"{hx:.0f}px {hy:.0f}px"}}, {{opacity:1, scale:1, duration:.5, ease:"expo.out", immediateRender:false}}, {s("l3"):.2f});')
    A(f'tl.to("#crowd .dot", {{opacity:.15, duration:.4}}, {s("l3") + .2:.2f});')
    A(f'tl.to("#crowd .hit", {{opacity:1, fill:"#B4FF39", duration:.3, stagger:.05}}, {s("l3") + .3:.2f});')
    A(P.pop("#aud", w("l3", 3), z=-600, scale=.2, ease="back.out(2.4)")); A(P.shine("#aud", w("l3", 3) + .5, 600))
    A(f'tl.to("#prod, #crowd, #aud", {{opacity:0, z:-400, duration:.3, ease:"power3.in"}}, {s("l4") - .3:.2f});')
    # ---- 12-22 s smartphone shoot + 3 angles
    A(P.pop("#ph", s("l4") + .05, ry=-35, z=-800, scale=.2, ease="back.out(2)"))
    A(f'tl.fromTo("#ph .recdot i", {{opacity:1}}, {{opacity:.2, duration:.4, yoyo:true, repeat:{int((s("l6") - s("l4")) / .4)}, ease:"steps(1)"}}, {s("l4") + .3:.2f});')
    A(f'tl.fromTo("#ph .box3", {{rotation:-6, scale:.9}}, {{rotation:6, scale:1.05, duration:{(s("l6") - s("l4")) / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, {s("l4") + .3:.2f});')
    for n, (a_id, wk) in enumerate((("#a1", ("l5", 1)), ("#a2", ("l5", 2)), ("#a3", ("l5", 4)))):
        t = w(*wk) if n else w("l5", 1)
        A(P.pop(a_id, t - .05, ry=-60, z=-600, scale=.2, ease="back.out(2.4)"))
        A(f'tl.fromTo("#flash", {{opacity:.35}}, {{opacity:0, duration:.2, immediateRender:false}}, {t:.2f});')
        A(P.floaty(a_id, t + .6, s("l6") - .4, amp=8, rot=(4 if n % 2 else -4)))
    A(f'tl.to("#ph, #a1, #a2, #a3", {{opacity:0, z:-400, duration:.3, ease:"power3.in"}}, {s("l6") - .3:.2f});')
    # ---- 22-32 s three videos with metrics; one wins
    for i in range(3):
        A(P.pop(f"#v{i}", s("l6") + .05 + i * .2, rx=-50, z=-700, scale=.2, ease="back.out(2)"))
        A(P.floaty(f"#v{i}", s("l6") + .8 + i * .2, e("l6") - .1, amp=8, rot=(3 if i % 2 else -3)))
    vals = [v.split(",") for _, v, _ in VIDS]
    for i in range(3):
        for k in range(3):
            A(f'tl.fromTo("#v{i} .met:nth-of-type({k + 1}) .tr i", {{scaleX:0}}, {{scaleX:{vals[i][k]}, duration:1.0, ease:"expo.out"}}, {s("l6") + .7 + k * .2:.2f});')
    A(f'tl.to("#v2 .tr i", {{backgroundColor:"#B4FF39", duration:.3}}, {e("l6") - .2:.2f});')
    A(f'tl.to("#v0, #v1", {{opacity:.35, scale:.92, duration:.5}}, {e("l6"):.2f});')
    A(f'tl.to("#v2", {{scale:1.1, z:120, duration:.6, ease:"back.out(2)"}}, {e("l6"):.2f});')
    A(f'tl.fromTo("#crown", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.4, ease:"back.out(3)"}}, {e("l6") + .2:.2f});')
    j += P.burst("sa", 900, 120, e("l6") + .25, n=14, r1=320)
    A(P.shine("#v2", e("l6") + .5, 400))
    A(P.ring("#rg1", e("l6") + .25))
    A(f'tl.to("#v0, #v1, #v2", {{opacity:0, z:-400, duration:.3, ease:"power3.in"}}, {s("l7") - .3:.2f});')
    # ---- 32-43 s budget flows to the winning creative (no fixed split shown)
    A(P.pop("#wallet", s("l7") + .05, ry=40, z=-700, scale=.2)); A(P.pop("#big", s("l7") + .25, ry=-40, z=-700, scale=.2))
    for i in range(10):
        st = s("l7") + .8 + i * .22
        A(f'tl.set("#co{i}", {{left:180, top:400}}, 0);')
        A(f'tl.fromTo("#co{i}", {{x:0, y:0, opacity:1, scale:.6}}, {{x:{560 + (i % 3) * 40}, y:{-260 + (i % 4) * 30}, scale:1, opacity:1, duration:.7, ease:"power2.inOut", immediateRender:false}}, {st:.2f});')
        A(f'tl.to("#co{i}", {{opacity:0, scale:.3, duration:.15}}, {st + .7:.2f});')
    A(f'tl.to("#big", {{scale:1.12, duration:{e("l7") - s("l7"):.2f}, ease:"sine.inOut"}}, {s("l7") + .8:.2f});')
    A(P.pop("#sc", s("l7") + 1.6, z=-400, scale=.2, ease="back.out(3)"))
    A(P.shine("#big", s("l7") + 2.0, 600))
    A(f'tl.to("#wallet, #big", {{opacity:0, z:-400, duration:.3, ease:"power3.in"}}, {s("l8") - .3:.2f});')
    # ---- 43-52 s message, 52-60 brand reveal + CTA
    for i, q in enumerate(("#q1", "#q2", "#q3")):
        A(f'tl.fromTo("{q}", {{opacity:0, scale:.4, rotation:{(-20, 10, 25)[i]}}}, {{opacity:.5, scale:1, duration:.35, ease:"back.out(2)"}}, {s("l8") + .05 + i * .12:.2f});')
    A(P.pop("#b1", s("l8") + .05, z=-500, scale=.3))
    A(f'tl.to("#q1, #q2, #q3, #b1", {{opacity:0, duration:.3}}, {s("l9") - .2:.2f});')
    A(P.pop("#b2", s("l9"), z=-700, scale=.2, ease="back.out(2.6)"))
    A(f'tl.fromTo("#flash", {{opacity:.5}}, {{opacity:0, duration:.25, immediateRender:false}}, {w("l9", 1):.2f});')
    j += P.burst("sb", 300, 300, w("l9", 1), n=16, r1=420)
    A(f'tl.to("#b2", {{opacity:0, duration:.25}}, {e("l9") + .2:.2f});')
    A(f'tl.fromTo("#reveal", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.5, ease:"expo.out"}}, {e("l9") + .3:.2f});')
    A(f'tl.to("#reveal", {{opacity:0, y:-80, duration:.35}}, {s("l10") - .1:.2f});')
    A(P.pop("#cta", s("l10"), z=-1100, rx=-60, scale=.1, ease="back.out(2.2)", dur=.8))
    j += P.burst("sc", 540, 400, s("l10") + .2, n=18, r1=520)
    A(P.shine("#cta", s("l10") + 1.0, 1000)); A(P.floaty("#cta", s("l10") + 1.0, DUR - .2, amp=10, rot=4, period=2.4))
    # avatar
    if AVATAR:
        A('tl.set("#av img", {transformOrigin:"50% 100%"}, 0);')
        A('tl.fromTo("#av", {y:520}, {y:0, duration:.9, ease:"expo.out"}, 0);')
        n = int(DUR / 3.4)
        A(f'tl.fromTo("#av", {{rotation:-1.8, transformOrigin:"50% 100%"}}, {{rotation:1.8, duration:1.7, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}}}, 0);')
        A(f'tl.to("#avglow", {{scale:1.1, opacity:.85, duration:1.7, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}}}, 0);')
        EXPR = [(0, "shock"), (s("l2"), "neutral"), (s("l3"), "think"), (s("l4"), "neutral"), (s("l6"), "think"), (e("l6"), "shock"),
                (s("l7"), "neutral"), (s("l8"), "think"), (s("l9"), "neutral")]
        prev = None
        for t, p in EXPR:
            p = p if p in AVATAR else "neutral"
            if p == prev: continue
            A(f'tl.set("#av img", {{opacity:0}}, {t:.2f}); tl.set("#av_{p}", {{opacity:1}}, {t:.2f});')
            A(f'tl.fromTo("#av_{p}", {{scale:.94, y:30}}, {{scale:1, y:0, duration:.45, ease:"back.out(2.2)", immediateRender:false}}, {t:.2f});')
            prev = p
        for i in range(1, 11):
            for k, wd in enumerate(L[f"l{i}"]["words"]):
                A(f'tl.to("#avbob", {{y:-{9 if k % 3 == 0 else 5}, duration:.11, ease:"sine.out", yoyo:true, repeat:1}}, {wd["start"]:.2f});')
    j += P.caps_js(CAPS, frame0=True)
    return "\n      ".join(j)

class Style:
    NAME = "LokaDigital · Mula Bisnes RM1,000"; PILL = "EDUCATION · STRATEGI"; CSS = CSS
Style.BODY = body(); Style.JS = js()

def sound():
    lib.DUR = DUR; m = lib.Mix(seed=11); m.N = int(lib.SR * DUR); m.bed = np.zeros(m.N); m.fx = np.zeros(m.N)
    prog = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
    m.score(118, prog, kind="pluck", drums="four", start=0, end=s("l8"))
    m.score(118, prog, kind="pad", drums="four", start=s("l8"), end=DUR - .5)
    m.at(m.fx, m.thud(), .02, .5); m.at(m.fx, m.whoosh(.8), .1, .3); m.at(m.fx, m.impact(), .52, .45)
    for t in (s("l2"), s("l4"), s("l6"), s("l7")): m.at(m.fx, m.whoosh(.5), t - .2, .3)
    m.at(m.fx, m.stamp(), w("l2", 4) + .05, .35); m.at(m.fx, m.coin(), s("l3") + .3, .3)
    for n in range(3): m.at(m.fx, m.pop(800 + 150 * n), (w("l5", 1), w("l5", 2), w("l5", 4))[n], .35)
    for k in range(int((s("l6") - s("l4")) / .4)): m.at(m.fx, m.tick(), s("l4") + .3 + k * .4, .12)
    m.at(m.fx, m.impact(), e("l6") + .02, .5); m.at(m.fx, m.coin(), e("l6") + .2, .35)
    for i in range(10): m.at(m.fx, m.coin(), s("l7") + .8 + i * .22 + .65, .16)
    m.at(m.fx, m.thud(), s("l8") + .05, .5); m.at(m.fx, m.impact(), w("l9", 1), .55)
    m.at(m.fx, m.riser(1.4), s("l10") - 1.4, .25); m.at(m.fx, m.impact(), s("l10") + .02, .6)
    with wave.open(os.path.join(HERE, "assets", "vo.wav")) as wv:
        vo = np.frombuffer(wv.readframes(wv.getnframes()), np.int16) / 32768.0
    vo = np.pad(vo, (0, max(0, m.N - len(vo))))[: m.N]
    env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); duck = 1 - .6 * np.clip(env / (env.max() * .25), 0, 1)
    fade = np.ones(m.N); e0 = int((DUR - 1.2) * lib.SR); fade[e0:] = np.linspace(1, 0, m.N - e0) ** 2
    x = (m.bed * duck * .34 + m.fx * .45) * fade; x = x / (np.abs(x).max() + 1e-9) * .5
    with wave.open(os.path.join(HERE, "assets", "bed.wav"), "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(lib.SR); wv.writeframes((np.stack([x, x], 1) * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    lib.DUR = DUR
    d = os.path.join(HERE, "project"); os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    sc = os.path.join(HERE, "..", "..", "hf-lab", "lab-test")
    for f in ("hyperframes.json", "package.json"): shutil.copy(os.path.join(sc, f), d)
    json.dump({"id": "mula1000", "name": "Mula Bisnes RM1,000"}, open(os.path.join(d, "meta.json"), "w"))
    shutil.copy(os.path.join(HERE, "..", "ref002-samples", "assets", "logo.jpg"), os.path.join(d, "assets")); shutil.copy(os.path.join(HERE, "assets", "logo_t.png"), os.path.join(d, "assets"))
    for p in AVATAR: shutil.copy(os.path.join(HERE, "assets", f"avatar_{p}.png"), os.path.join(d, "assets"))
    sound()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "assets", "vo.wav"), "-i", os.path.join(HERE, "assets", "bed.wav"),
                    "-filter_complex", "[0]aformat=channel_layouts=stereo,apad[v];[v][1]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
                    "-map", "[o]", "-ar", "48000", "-t", str(DUR), os.path.join(d, "assets", "mix.wav")], check=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(lib.page(Style))
    print("built", DUR, "s · avatar:", AVATAR)
