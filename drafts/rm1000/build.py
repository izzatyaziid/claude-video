"""LokaDigital · "Ke mana RM1,000 iklan kau pergi?" — avatar explainer (REF-001 + REF-002 techniques, LokaDigital identity).
Reads timing.json (VO line + word times) and writes project/index.html. Avatar images: assets/avatar_<pose>.png (optional).
Usage: python3 build.py"""
import json, os, sys, shutil, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "previews"))
import lib, pop as P

T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
L = {l["id"]: l for l in T["lines"]}
DUR = round(T["duration"] + 1.4, 2)
def s(i): return L[i]["start"]
def e(i): return L[i]["end"]
def w(i, k): return L[i]["words"][k]["start"]

KEYS = {"seribu", "ringgit", "tiga", "tempahan", "Kenapa?", "sepuluh", "blok.", "likes", "views.", "tanya.", "DM.", "esok.", "harga.", "senyap.",
        "satu", "bajet.", "sistem.", "mesej.", "minit,", "nilai,", "sama.", "LokaDigital."}
AVATAR = [p for p in ("point", "shock", "think", "thumb", "wave", "neutral") if os.path.exists(os.path.join(HERE, "assets", f"avatar_{p}.png"))]

BLOCKS = 10
GX, GY, BW, BH, GAP = 70, 250, 172, 120, 16   # block grid in stage coords (5 x 2)
def bpos(i): return GX + (i % 5) * (BW + GAP), GY + (i // 5) * (BH + GAP)

CSS = P.CSS + """
  #root { background:var(--ink); }
  .hdrline { position:absolute; left:96px; right:96px; top:420px; display:flex; justify-content:space-between; padding-bottom:14px; border-bottom:2px solid rgba(255,255,255,.12); font:600 26px 'IBM Plex Mono'; letter-spacing:.12em; color:var(--grey); }
  .hl { position:absolute; left:96px; right:96px; top:476px; font:900 64px/1.06 'Inter'; letter-spacing:-.035em; color:#fff; opacity:0; }
  .hl span { display:inline-block; opacity:.16; margin-right:14px; }
  .hl span.kk { color:var(--g); }
  .stage3d { top:640px; height:640px; }
  .blk { position:absolute; width:172px; height:120px; border-radius:18px; background:linear-gradient(160deg,#c9ff6a,#B4FF39 60%,#8fd12a); color:var(--ink);
         box-shadow:0 24px 50px rgba(0,0,0,.55), 0 0 40px rgba(180,255,57,.35), inset 0 2px 0 rgba(255,255,255,.6); font:900 40px/120px 'Inter'; letter-spacing:-.03em; text-align:center; opacity:0; }
  .blk small { position:absolute; left:0; right:0; top:10px; font:800 18px/1 'Inter'; letter-spacing:.2em; opacity:.6; }
  .big { position:absolute; left:140px; top:120px; width:800px; padding:44px 50px; border-radius:36px; }
  .big b { display:block; font:900 170px/0.9 'Inter'; letter-spacing:-.06em; } .big small { display:block; font:800 30px 'Inter'; letter-spacing:.24em; margin-bottom:10px; }
  .three { position:absolute; left:250px; top:120px; width:580px; padding:40px; border-radius:36px; text-align:center; }
  .three b { display:block; font:900 200px/0.9 'Inter'; letter-spacing:-.06em; } .three small { display:block; font:800 34px 'Inter'; letter-spacing:.2em; }
  .bin { position:absolute; width:300px; height:190px; border-radius:26px; border:3px dashed rgba(255,255,255,.25); padding:20px; }
  .bin b { display:block; font:800 26px 'Inter'; letter-spacing:.16em; color:var(--mist); }
  .bin i { position:absolute; left:20px; bottom:16px; font:900 44px 'Inter'; font-style:normal; color:#fff; }
  .stamp2 { position:absolute; padding:12px 20px; border-radius:14px; font:900 32px 'Inter'; letter-spacing:-.02em; transform:rotate(-6deg); }
  .kenapa { position:absolute; left:0; right:0; top:150px; text-align:center; font:900 200px/1 'Inter'; letter-spacing:-.06em; color:#fff; opacity:0; text-shadow:0 0 60px rgba(184,0,240,.8); }
  .sys { position:absolute; left:90px; top:110px; width:900px; text-align:center; }
  .sys s { display:block; font:900 110px/1 'Inter'; color:var(--grey); letter-spacing:-.05em; text-decoration:none; opacity:0; }
  .sys b { display:block; margin-top:20px; font:900 190px/0.9 'Inter'; letter-spacing:-.06em; color:var(--g); opacity:0; text-shadow:0 0 80px rgba(180,255,57,.5); }
  .step { position:absolute; left:90px; width:900px; padding:28px 34px; display:flex; gap:28px; align-items:center; }
  .step b { font:900 70px 'Inter'; color:var(--g); min-width:110px; } .step p { font:800 46px/1.05 'Inter'; letter-spacing:-.02em; } .step p i { display:block; margin-top:8px; font:600 30px 'Inter'; font-style:normal; color:var(--mist); }
  #flashm { position:absolute; inset:0; background:radial-gradient(120% 70% at 80% 10%, #B800F0 0%, #46096B 55%, #240538 100%); opacity:0; }
  #flashm span { position:absolute; left:96px; top:880px; font:900 120px/0.9 'Inter'; letter-spacing:-.05em; }
  #flashm small { position:absolute; left:96px; top:820px; font:700 30px 'IBM Plex Mono'; letter-spacing:.2em; color:var(--g); }
  #av { position:absolute; left:560px; top:1300px; width:500px; height:620px; }
  #av img { position:absolute; left:0; bottom:0; width:500px; opacity:0; filter:drop-shadow(0 24px 34px rgba(0,0,0,.55)); }
  #avglow { position:absolute; left:520px; top:1330px; width:620px; height:620px; border-radius:50%; background:none; display:none; }
  .capband { top:1300px; } .cap { left:70px; right:520px; text-align:left; font-size:60px; }
  #flash { position:absolute; inset:0; background:#fff; opacity:0; mix-blend-mode:overlay; }
  .ctab3 { position:absolute; left:90px; top:120px; width:900px; padding:56px 50px; border-radius:36px; }
  .ctab3 label { display:block; font:800 30px 'Inter'; letter-spacing:.24em; } .ctab3 h2 { margin-top:16px; font:900 120px/0.9 'Inter'; letter-spacing:-.05em; } .ctab3 p { margin-top:20px; font:700 34px 'Inter'; opacity:.8; }
"""

def headline(lid):
    l = L[lid]
    spans = " ".join(f'<span class="{"kk" if wd["text"] in KEYS or wd["text"].strip(".,?") in KEYS else ""}" id="{lid}w{k}">{wd["text"]}</span>' for k, wd in enumerate(l["words"]))
    return f'<div class="hl clip" id="hl_{lid}" data-start="{max(0, l["start"] - .05):.2f}" data-duration="{l["end"] - l["start"] + l["gap"] + .05:.2f}" data-track-index="3">{spans}</div>'

CAPS = [("k1", 0.0, s("l4"), "Dapat [3] tempahan je."), ("k2", s("l4"), s("l6"), "Ikut setiap [ringgit]."),
        ("k3", s("l6"), s("l8"), "4 blok: [likes]."), ("k4", s("l8"), s("l10"), "3 blok: DM [lambat]."),
        ("k5", s("l10"), s("l12"), "2 blok: [harga] je."), ("k6", s("l12"), s("l13"), "1 blok [sampai]."),
        ("k7", s("l13"), s("l15"), "Bukan bajet. [Sistem]."), ("k8", s("l15"), s("l18"), "3 [langkah]."),
        ("k9", s("l18"), s("l19"), "Bajet [sama]."), ("k10", s("l19"), DUR, "[DM] LokaDigital.")]

def body():
    blocks = "".join(f'<div class="blk" id="b{i}"><small>BLOK {i + 1}</small>RM100</div>' for i in range(BLOCKS))
    av = '<div id="avbob" style="position:absolute;inset:0">' + "".join(f'<img id="av_{p}" src="assets/avatar_{p}.png" alt="host">' for p in AVATAR) + '</div>'
    return f"""
      <div class="hdrline clip" id="hdr" data-start="0" data-duration="{DUR}" data-track-index="2"><span id="hdrl">KE MANA RM1,000?</span><span id="hdrr">BAB 01 / 02 · CONTOH</span></div>
      {''.join(headline(f"l{i}") for i in range(1, 21))}
      <div class="stage3d clip" id="st" data-start="0" data-duration="{DUR}" data-track-index="4" data-layout-allow-overflow data-layout-ignore><div id="cam" style="position:absolute;inset:0;transform-style:preserve-3d">
        <div class="c3 big lime" id="bigc"><small>BAJET IKLAN · CONTOH</small><b>RM1,000</b><div class="shine"></div></div>
        <div class="c3 three mag" id="tri"><b>3</b><small>TEMPAHAN</small><div class="shine"></div></div>
        <div class="kenapa" id="kn">Kenapa?</div>
        {blocks}
        <div class="bin" id="bin1" style="left:70px;top:20px;opacity:0"><b>LIKES & VIEWS</b><i>♥ 👁</i></div>
        <div class="bin" id="bin2" style="left:390px;top:20px;opacity:0"><b>DM · DIBALAS ESOK</b><i>💬</i></div>
        <div class="bin" id="bin3" style="left:710px;top:20px;opacity:0"><b>TANYA HARGA</b><i>RM90?</i></div>
        <div class="c3 stamp2 mag" id="stA" style="left:80px;top:226px">Tiada yang tanya</div>
        <div class="c3 stamp2 mag" id="stB" style="left:400px;top:226px">Beli tempat lain</div>
        <div class="c3 stamp2 mag" id="stC" style="left:740px;top:226px">Senyap</div>
        <div class="sys" id="sys"><s id="sy1">BAJET</s><b id="sy2">SISTEM.</b></div>
        <div class="c3 step" id="p1" style="top:10px"><b>01</b><p>Objektif: mesej<i>Bukan likes</i></p><div class="shine"></div></div>
        <div class="c3 step" id="p2" style="top:10px"><b>02</b><p>Balas DM cepat<i>Dalam minit, bukan esok</i></p><div class="shine"></div></div>
        <div class="c3 step" id="p3" style="top:10px"><b>03</b><p>Tanya → nilai → harga<i>Baru sebut RM90</i></p><div class="shine"></div></div>
        <div class="c3 ctab3 lime" id="cta"><label>AUDIT BAJET IKLAN</label><h2>DM<br>LOKADIGITAL</h2><p>Tahu ke mana setiap ringgit pergi.</p><div class="shine"></div></div>
        {P.sparks_html("sa", 14)}{P.sparks_html("sb", 16)}{P.sparks_html("sc", 18)}
        <div class="ring" id="rg1" style="left:300px;top:20px;width:480px;height:480px"></div>
        <div class="ring" id="rg2" style="left:330px;top:120px;width:420px;height:420px"></div>
      </div></div>
      <div id="flashm" class="clip" data-start="{s('l13') - .1:.2f}" data-duration="{s('l15') - s('l13') + .1:.2f}" data-track-index="6"><small>BAB 02 / 02</small><span>Masalahnya<br>bukan bajet.</span></div>
      <div id="avglow" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5" data-layout-ignore></div>
      <div id="av" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5" data-layout-ignore>{av}</div>
      {P.caps(CAPS)}
      <div id="flash" class="clip" data-start="0" data-duration="{DUR}" data-track-index="8" data-layout-ignore></div>
      <audio id="vo" src="assets/vo.wav" class="clip" data-start="0" data-duration="{DUR}" data-track-index="11"></audio>"""

POSES = [(0, "point"), (s("l3"), "shock"), (s("l5"), "point"), (s("l7"), "think"), (s("l9"), "shock"), (s("l11"), "think"),
         (s("l12"), "point"), (s("l14"), "shock"), (s("l15"), "point"), (s("l18"), "thumb"), (s("l19"), "wave")]

def js():
    j = []; A = j.append
    # headline word-by-word (REF-001) + key words
    for i in range(1, 21):
        lid = f"l{i}"; l = L[lid]
        A(f'tl.set("#hl_{lid}", {{opacity:1}}, {max(0, l["start"] - .05):.2f});')
        for k, wd in enumerate(l["words"]):
            A(f'tl.to("#{lid}w{k}", {{opacity:1, duration:.08}}, {wd["start"]:.2f});')
    # ---- HOOK: frame 0 = RM1,000 card already popped
    A(P.pop("#bigc", 0, frame0=True)); A('tl.fromTo("#bigc", {scale:1.12, rotationX:12}, {scale:1, rotationX:0, duration:.7, ease:"expo.out"}, 0);')
    A(P.shine("#bigc", .3, 900)); A(P.floaty("#bigc", .8, s("l2"), amp=10, rot=4))
    t2 = w("l2", 1)
    A(f'tl.to("#bigc", {{y:-60, scale:.7, x:-200, opacity:.5, duration:.35, ease:"power3.inOut"}}, {t2 - .1:.2f});')
    A(P.pop("#tri", t2, z=-900, scale=.1, ease="back.out(2.8)"))
    A(f'tl.fromTo("#flash", {{opacity:.55}}, {{opacity:0, duration:.25, immediateRender:false}}, {t2 + .02:.2f});')
    j += P.burst("sa", 540, 280, t2 + .05, n=14, r1=420)
    tk = s("l3")
    A(f'tl.to("#bigc, #tri", {{opacity:0, scale:.5, z:-400, duration:.25, ease:"power3.in"}}, {tk - .05:.2f});')
    A(f'tl.fromTo("#kn", {{opacity:0, scale:2.2}}, {{opacity:1, scale:1, duration:.3, ease:"back.out(2)"}}, {tk:.2f});')
    A(f'tl.to("#cam", {{x:14, duration:.04, yoyo:true, repeat:7, ease:"none"}}, {tk:.2f});')
    A(P.ring("#rg1", tk + .05, .8))
    A(f'tl.to("#kn", {{opacity:0, y:-60, duration:.3}}, {s("l4") + .3:.2f});')
    # ---- 10 blocks
    t5 = s("l5")
    A(f'tl.set("#bigc", {{x:0, y:0, scale:1, opacity:1, z:0}}, {s("l4") + .2:.2f});')
    A(f'tl.fromTo("#bigc", {{opacity:0, z:-500}}, {{opacity:1, z:0, duration:.5, ease:"expo.out", immediateRender:false}}, {s("l4") + .3:.2f});')
    A(f'tl.to("#bigc", {{opacity:0, scale:1.3, duration:.25}}, {w("l5", 5) - .1:.2f});')
    for i in range(BLOCKS):
        x, y = bpos(i)
        A(f'tl.set("#b{i}", {{left:{x}, top:{y}}}, 0);')
        A(P.pop(f"#b{i}", w("l5", 5) + i * .07, z=-600, rx=-60, scale=.2, ease="back.out(2.4)"))
    j += P.burst("sb", 540, 310, w("l5", 5), n=16, r1=480)
    # 4 -> likes bin
    t6 = s("l6"); A(f'tl.fromTo("#bin1", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {t6:.2f});')
    for n, i in enumerate((0, 1, 2, 3)):
        A(f'tl.to("#b{i}", {{left:{90 + (n % 2) * 120}, top:{75 + (n // 2) * 60}, scale:.55, rotation:{(-8, 6, -4, 9)[n]}, duration:.45, ease:"back.inOut(1.4)"}}, {w("l6", 1) + n * .1:.2f});')
    A(f'tl.to("#b0, #b1, #b2, #b3", {{filter:"grayscale(1) brightness(.55)", duration:.4}}, {w("l7", 4):.2f});')
    A(P.pop("#stA", w("l7", 4), z=-500, scale=.2, ease="back.out(3)"))
    # 3 -> DM bin
    t8 = s("l8"); A(f'tl.fromTo("#bin2", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {t8:.2f});')
    for n, i in enumerate((4, 5, 6)):
        A(f'tl.to("#b{i}", {{left:{410 + (n % 2) * 120}, top:{75 + (n // 2) * 60}, scale:.55, rotation:{(5, -7, 4)[n]}, duration:.45, ease:"back.inOut(1.4)"}}, {w("l8", 1) + n * .1:.2f});')
    A(f'tl.to("#b4, #b5, #b6", {{filter:"grayscale(1) brightness(.55)", duration:.4}}, {w("l9", 3):.2f});')
    A(P.pop("#stB", w("l9", 6), z=-500, scale=.2, ease="back.out(3)"))
    # 2 -> price
    t10 = s("l10"); A(f'tl.fromTo("#bin3", {{opacity:0, y:-30}}, {{opacity:1, y:0, duration:.3}}, {t10:.2f});')
    for n, i in enumerate((7, 8)):
        A(f'tl.to("#b{i}", {{left:{730 + n * 120}, top:75, scale:.55, rotation:{(-6, 7)[n]}, duration:.45, ease:"back.inOut(1.4)"}}, {w("l10", 1) + n * .1:.2f});')
    A(f'tl.to("#b7, #b8", {{filter:"grayscale(1) brightness(.55)", duration:.4}}, {w("l11", 5):.2f});')
    A(P.pop("#stC", w("l11", 5), z=-500, scale=.2, ease="back.out(3)"))
    # 1 left: glow + spotlight
    t12 = s("l12")
    A(f'tl.to("#b9", {{left:454, top:330, scale:1.5, z:120, duration:.6, ease:"expo.inOut"}}, {t12:.2f});')
    A(P.ring("#rg2", t12 + .5, .9)); A(P.shine("#b9", t12 + .6, 200))
    A(f'tl.to("#bin1, #bin2, #bin3, #stA, #stB, #stC, #b0, #b1, #b2, #b3, #b4, #b5, #b6, #b7, #b8", {{opacity:.25, duration:.4}}, {t12 + .2:.2f});')
    # chapter flash (REF-001 red-card cut, LokaDigital purple)
    A(f'tl.fromTo("#flashm", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:.35, ease:"expo.inOut"}}, {s("l13") - .1:.2f});')
    A(f'tl.fromTo("#flashm span", {{yPercent:60, opacity:0}}, {{yPercent:0, opacity:1, duration:.45, ease:"expo.out"}}, {s("l13") + .1:.2f});')
    A(f'tl.set("#hdrr", {{textContent:"BAB 02 / 02 · CONTOH"}}, {s("l13"):.2f});')
    A(f'tl.to("#flashm", {{clipPath:"inset(100% 0 0 0)", duration:.35, ease:"expo.inOut"}}, {s("l14") - .2:.2f});')
    A(f'tl.to("#bin1, #bin2, #bin3, #stA, #stB, #stC, #b0, #b1, #b2, #b3, #b4, #b5, #b6, #b7, #b8, #b9", {{opacity:0, duration:.2}}, {s("l13"):.2f});')
    A(f'tl.fromTo("#sy1", {{opacity:0}}, {{opacity:.6, duration:.2}}, {s("l14") - .1:.2f});')
    A(f'tl.fromTo("#sy2", {{opacity:0, scale:2, z:-200}}, {{opacity:1, scale:1, z:0, duration:.45, ease:"back.out(2.6)"}}, {w("l14", 1):.2f});')
    A(f'tl.fromTo("#flash", {{opacity:.5}}, {{opacity:0, duration:.25, immediateRender:false}}, {w("l14", 1) + .02:.2f});')
    j += P.burst("sc", 540, 280, w("l14", 1) + .05, n=18, r1=500)
    A(f'tl.to("#sys", {{opacity:0, duration:.25}}, {s("l15") - .1:.2f});')
    # three steps; blocks recover to lime as each step lands
    for n, (pid, lid) in enumerate((("#p1", "l15"), ("#p2", "l16"), ("#p3", "l17"))):
        t = s(lid)
        A(f'tl.set("{pid}", {{top:{10 + n * 170}}}, 0);')
        A(P.pop(pid, t + .05, ry=-50, z=-700, scale=.2, ease="back.out(2.4)"))
        A(P.shine(pid, t + .6, 900))
    for i in range(BLOCKS):
        x, y = bpos(i)
        A(f'tl.set("#b{i}", {{left:{x}, top:{380 + (i // 5) * 100}, scale:.72, rotation:0, z:0, filter:"grayscale(1) brightness(.55)", opacity:0}}, {s("l15") - .05:.2f});')
    A(f'tl.to("#b0, #b1, #b2, #b3, #b4, #b5, #b6, #b7, #b8, #b9", {{opacity:1, duration:.3, stagger:.04}}, {s("l15") + .4:.2f});')
    rec = [(s("l15") + 1.6, (0, 1, 2)), (s("l16") + 1.6, (4, 5)), (s("l17") + 1.8, (7, 8)), (s("l18") + .6, (9, 6))]
    for t, ids in rec:
        for n, i in enumerate(ids):
            A(f'tl.to("#b{i}", {{filter:"grayscale(0) brightness(1)", scale:.8, duration:.3, ease:"back.out(3)"}}, {t + n * .12:.2f});')
    A(f'tl.to("#p1, #p2, #p3", {{opacity:.35, duration:.3}}, {s("l18"):.2f});')
    A(f'tl.to("#cam", {{z:80, duration:3, ease:"sine.inOut"}}, {s("l18"):.2f});')
    # CTA
    tc = s("l19")
    A(f'tl.to("#p1, #p2, #p3, #b0, #b1, #b2, #b3, #b4, #b5, #b6, #b7, #b8, #b9", {{opacity:0, z:-400, duration:.3, ease:"power3.in"}}, {tc - .1:.2f});')
    A(f'tl.to("#cam", {{z:0, duration:.4}}, {tc:.2f});')
    A(P.pop("#cta", tc + .1, z=-1100, rx=-60, scale=.1, ease="back.out(2.2)", dur=.8))
    A(P.shine("#cta", tc + 1.0, 1000)); A(P.shine("#cta", s("l20") + .6, 1000))
    A(P.floaty("#cta", tc + 1.0, DUR - .2, amp=10, rot=4, period=2.4))
    # avatar: expression swaps that follow the VO + continuous smooth motion (sway, talk bob per word, pops on swaps)
    if AVATAR:
        A('tl.set("#av img", {transformOrigin:"50% 100%"}, 0);')
        A('tl.fromTo("#av", {y:520}, {y:0, duration:.9, ease:"expo.out"}, 0);')
        n = int(DUR / 3.4)
        A(f'tl.fromTo("#av", {{rotation:-1.8, transformOrigin:"50% 100%"}}, {{rotation:1.8, duration:1.7, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}}}, 0);')
        A(f'tl.to("#avglow", {{scale:1.1, opacity:.85, duration:1.7, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}}}, 0);')
        EXPR = [(0, "neutral"), (s("l2"), "shock"), (s("l4"), "think"), (s("l6"), "neutral"), (w("l7", 3), "think"),
                (s("l8"), "neutral"), (w("l9", 3), "shock"), (s("l10"), "neutral"), (w("l11", 5), "think"),
                (s("l12"), "neutral"), (s("l13"), "think"), (w("l14", 1), "shock"), (s("l15"), "neutral"),
                (s("l18"), "neutral"), (s("l19"), "neutral")]
        prev = None
        for t, p in EXPR:
            p = p if p in AVATAR else "neutral"
            if p == prev: continue
            A(f'tl.set("#av img", {{opacity:0}}, {t:.2f}); tl.set("#av_{p}", {{opacity:1}}, {t:.2f});')
            A(f'tl.fromTo("#av_{p}", {{scale:.94, y:30}}, {{scale:1, y:0, duration:.45, ease:"back.out(2.2)", immediateRender:false}}, {t:.2f});')
            prev = p
        for i in range(1, 21):
            l = L[f"l{i}"]
            for k, wd in enumerate(l["words"]):
                amp = 9 if k % 3 == 0 else 5
                A(f'tl.to("#avbob", {{y:-{amp}, duration:.11, ease:"sine.out", yoyo:true, repeat:1}}, {wd["start"]:.2f});')
    j += P.caps_js(CAPS, frame0=True)
    return "\n      ".join(j)

class Style:
    NAME = "LokaDigital · Ke mana RM1,000?"; PILL = "CONTOH · KEDAI KEK"; CSS = CSS
Style.BODY = body(); Style.JS = js()

def sound():
    m = lib.Mix(seed=7)
    lib.DUR = DUR; m.N = int(lib.SR * DUR); m.bed = m.bed[:m.N] if len(m.bed) >= m.N else __import__("numpy").zeros(m.N); m.fx = __import__("numpy").zeros(m.N)
    prog = [(45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])]
    m.score(100, prog, kind="pluck", drums="half", start=0, end=s("l13"))
    m.score(100, prog, kind="pad", drums="four", start=s("l14"), end=DUR - .5)
    m.at(m.fx, m.thud(), .02, .5)
    m.at(m.fx, m.impact(), w("l2", 1), .55); m.at(m.fx, m.glitch(.25), s("l3"), .4)
    for i in range(BLOCKS): m.at(m.fx, m.pop(600 + 40 * i), w("l5", 5) + i * .07 + .05, .25)
    for lid in ("l6", "l8", "l10"): m.at(m.fx, m.whoosh(.5), w(lid, 1), .25)
    for lid, k in (("l7", 4), ("l9", 6), ("l11", 5)): m.at(m.fx, m.stamp(), w(lid, k) + .05, .35)
    m.at(m.fx, m.coin(), s("l12") + .5, .35)
    m.at(m.fx, m.whoosh(.5), s("l13") - .1, .4); m.at(m.fx, m.impact(), w("l14", 1), .55)
    for lid in ("l15", "l16", "l17"): m.at(m.fx, m.pop(900), s(lid) + .1, .3)
    for t, ids in [(s("l15") + 1.6, 3), (s("l16") + 1.6, 2), (s("l17") + 1.8, 2), (s("l18") + .6, 2)]:
        for n in range(ids): m.at(m.fx, m.coin(), t + n * .12, .2)
    m.at(m.fx, m.riser(1.2), s("l19") - 1.1, .25); m.at(m.fx, m.impact(), s("l19") + .12, .6)
    import numpy as np, wave
    with wave.open(os.path.join(HERE, "assets", "vo.wav")) as wv:
        vo = np.frombuffer(wv.readframes(wv.getnframes()), np.int16) / 32768.0
    vo = np.pad(vo, (0, max(0, m.N - len(vo))))[: m.N]
    env = np.convolve(np.abs(vo), np.ones(4800) / 4800, "same"); duck = 1 - .6 * np.clip(env / (env.max() * .25), 0, 1)
    fade = np.ones(m.N); e0 = int((DUR - 1.2) * lib.SR); fade[e0:] = np.linspace(1, 0, m.N - e0) ** 2
    x = (m.bed * duck * .32 + m.fx * .45) * fade
    x = x / (np.abs(x).max() + 1e-9) * .5
    st = np.stack([x, x], 1)
    with wave.open(os.path.join(HERE, "assets", "bed.wav"), "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(lib.SR); wv.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    lib.DUR = DUR
    d = os.path.join(HERE, "project"); os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    sc = os.path.join(HERE, "..", "..", "hf-lab", "lab-test")
    for f in ("hyperframes.json", "package.json"): shutil.copy(os.path.join(sc, f), d)
    json.dump({"id": "rm1000", "name": "Ke mana RM1,000"}, open(os.path.join(d, "meta.json"), "w"))
    shutil.copy(os.path.join(HERE, "..", "ref002-samples", "assets", "logo.jpg"), os.path.join(d, "assets"))
    for p in AVATAR: shutil.copy(os.path.join(HERE, "assets", f"avatar_{p}.png"), os.path.join(d, "assets"))
    sound()
    import subprocess
    # final mix: VO (-16 LUFS) + bed, normalised to -14 LUFS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "assets", "vo.wav"), "-i", os.path.join(HERE, "assets", "bed.wav"),
                    "-filter_complex", "[0]aformat=channel_layouts=stereo,apad[v];[v][1]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
                    "-map", "[o]", "-ar", "48000", "-t", str(DUR), os.path.join(d, "assets", "mix.wav")], check=True)
    html = lib.page(Style).replace('<audio id="mix" src="assets/mix.wav" class="clip" data-start="0" data-duration="60.0"', f'<audio id="mix" src="assets/mix.wav" class="clip" data-start="0" data-duration="{DUR}"')
    html = html.replace(f'<audio id="vo" src="assets/vo.wav" class="clip" data-start="0" data-duration="{DUR}" data-track-index="11"></audio>', "")
    html = html.replace('data-duration="60.0"', f'data-duration="{DUR}"')
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    print("built", DUR, "s · avatar poses:", AVATAR or "none")
