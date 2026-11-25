"""Build two HyperFrames projects from one timeline (timing.json):
  A/ = avatar host + VO + music + SFX (mouth driven by the VO envelope)
  B/ = same film with no VO: silent avatar gestures, on-screen supers, music + SFX
Usage: python3 build.py   (needs timing.json, assets/vo.wav, assets/mix_A.wav, assets/mix_B.wav)
DRAFT SAMPLE. Copy from approved EP02 lines; F&B example labelled CONTOH; no invented numbers."""
import json, os, shutil, wave, html
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
DUR = round(T["duration"], 2)
LINES = T["lines"]
FPS = 30

# ---------- scenes: contiguous spans from the first to the last line of each scene ----------
scenes = []
for ln in LINES:
    if scenes and scenes[-1]["id"] == ln["scene"]:
        scenes[-1]["lines"].append(ln)
    else:
        scenes.append({"id": ln["scene"], "lines": [ln]})
for i, s in enumerate(scenes):
    s["start"] = 0.0 if i == 0 else round(s["lines"][0]["start"] - 0.25, 3)
for i, s in enumerate(scenes):
    s["end"] = DUR if i == len(scenes) - 1 else scenes[i + 1]["start"]
    s["dur"] = round(s["end"] - s["start"], 3)

GESTURE = {"posts": "point", "shop": "open", "views": "point", "budget": "open", "crowd": "chin",
           "cari": "point", "cakap": "open", "sambung": "point", "cta": "wave"}

# ---------- mouth levels from the VO envelope (A only) ----------
def mouth_track():
    with wave.open(os.path.join(HERE, "assets", "vo.wav")) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768.0
    hop = sr // FPS; n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)])
    ref = np.percentile(rms[rms > 0.01], 90) if np.any(rms > 0.01) else 1
    lv = np.digitize(rms / ref, [0.12, 0.35, 0.65, 0.95])  # 0 rest .. 4 wide
    # vary vowel shape a little so it doesn't flap: alternate open/round on long holds
    out, prev = [], -1
    for i, v in enumerate(lv):
        v = int(v)
        if v == 3 and (i // 4) % 3 == 2: v = 5      # "O" shape now and then
        if v != prev: out.append((round(i / FPS, 3), v)); prev = v
    return out

# ---------- helpers ----------
def esc(s): return html.escape(s, quote=True)

def caption_markup(mode):
    parts = []
    for ln in LINES:
        words = []
        for k, w in enumerate(ln["words"]):
            core = w["text"].strip(".,?!")
            is_key = core.lower() == ln["key"].lower()
            cls = "w key" if is_key else "w"
            words.append(f'<span class="{cls}" id="{ln["id"]}w{k}"><span class="wt">{esc(w["text"])}</span>'
                         + ('<i class="kb"><b></b><b></b><b></b><b></b></i>' if is_key else "") + "</span>")
        st = max(0.05, ln["start"] - (0.08 if mode == "A" else 0.18))
        en = ln["end"] + ln["gap"] * (0.55 if mode == "A" else 0.85)
        parts.append(f'<div id="cap_{ln["id"]}" class="cap clip" data-start="{st:.3f}" data-duration="{en - st:.3f}" '
                     f'data-track-index="3" data-layout-allow-overflow>{" ".join(words)}</div>')
    return "\n      ".join(parts)

def dots_markup(n=96, seed=11):
    rng = np.random.default_rng(seed); out = []
    for i in range(n):
        x, y = rng.uniform(70, 830), rng.uniform(40, 560); r = rng.uniform(7, 13)
        out.append(f'<circle class="dot{" hit" if i % 12 == 5 else ""}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>')
    return "".join(out)

def grid_tiles():
    cols = ["#3a1f7a", "#4b2a9a", "#2c1760", "#5a36b5", "#352070", "#462790", "#2f1a66", "#56339f", "#3d2382"]
    return "".join(f'<div class="tile" style="background:{c}"><span></span></div>' for c in cols)

AVATAR = """
<svg id="av" viewBox="0 0 700 640" width="700" height="640" aria-label="host">
  <defs>
    <linearGradient id="jk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#241640"/><stop offset="1" stop-color="#0d0818"/></linearGradient>
    <linearGradient id="sk" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E2AE8A"/><stop offset="1" stop-color="#B97E5C"/></linearGradient>
    <radialGradient id="rim" cx=".2" cy=".3" r=".9"><stop offset="0" stop-color="#AB94FF" stop-opacity=".55"/><stop offset=".6" stop-color="#602AC8" stop-opacity="0"/></radialGradient>
  </defs>
  <g id="body">
    <path d="M110 640 C120 520 190 455 270 440 L430 440 C510 455 580 520 590 640 Z" fill="url(#jk)" stroke="#6b4fd0" stroke-width="3"/>
    <path d="M300 440 L350 520 L400 440 Z" fill="#D4CAF2"/>
    <path d="M285 444 L350 545 L415 444" fill="none" stroke="#3b2770" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="455" cy="515" r="9" fill="#E8FF2B"/>
    <rect x="318" y="385" width="64" height="70" rx="22" fill="#B97E5C"/>
  </g>
  <g id="arm_down">
    <path d="M150 560 C150 600 160 630 170 640" stroke="#6b4fd0" stroke-width="78" stroke-linecap="round" fill="none"/><path d="M150 560 C150 600 160 630 170 640" stroke="#241640" stroke-width="70" stroke-linecap="round" fill="none"/>
    <path d="M550 560 C550 600 540 630 530 640" stroke="#6b4fd0" stroke-width="78" stroke-linecap="round" fill="none"/><path d="M550 560 C550 600 540 630 530 640" stroke="#241640" stroke-width="70" stroke-linecap="round" fill="none"/>
  </g>
  <g id="arm_point" opacity="0">
    <path d="M160 560 C150 600 160 630 170 640" stroke="#6b4fd0" stroke-width="78" stroke-linecap="round" fill="none"/><path d="M160 560 C150 600 160 630 170 640" stroke="#241640" stroke-width="70" stroke-linecap="round" fill="none"/>
    <path d="M545 560 C600 520 610 440 590 380" stroke="#6b4fd0" stroke-width="74" stroke-linecap="round" fill="none"/><path d="M545 560 C600 520 610 440 590 380" stroke="#241640" stroke-width="66" stroke-linecap="round" fill="none"/>
    <g transform="translate(590 345)"><rect x="-30" y="-10" width="60" height="62" rx="24" fill="url(#sk)"/><rect x="-10" y="-78" width="22" height="80" rx="11" fill="url(#sk)"/><rect x="-36" y="0" width="18" height="34" rx="9" fill="#B97E5C"/></g>
  </g>
  <g id="arm_open" opacity="0">
    <path d="M155 560 C100 520 95 450 120 410" stroke="#6b4fd0" stroke-width="74" stroke-linecap="round" fill="none"/><path d="M155 560 C100 520 95 450 120 410" stroke="#241640" stroke-width="66" stroke-linecap="round" fill="none"/>
    <path d="M545 560 C600 520 605 450 580 410" stroke="#6b4fd0" stroke-width="74" stroke-linecap="round" fill="none"/><path d="M545 560 C600 520 605 450 580 410" stroke="#241640" stroke-width="66" stroke-linecap="round" fill="none"/>
    <g transform="translate(118 368) rotate(-14)"><rect x="-38" y="-30" width="76" height="66" rx="26" fill="url(#sk)"/><rect x="-36" y="-64" width="14" height="44" rx="7" fill="url(#sk)"/><rect x="-18" y="-74" width="14" height="52" rx="7" fill="url(#sk)"/><rect x="0" y="-72" width="14" height="50" rx="7" fill="url(#sk)"/><rect x="18" y="-62" width="14" height="42" rx="7" fill="url(#sk)"/></g>
    <g transform="translate(582 368) rotate(14)"><rect x="-38" y="-30" width="76" height="66" rx="26" fill="url(#sk)"/><rect x="-32" y="-62" width="14" height="42" rx="7" fill="url(#sk)"/><rect x="-14" y="-72" width="14" height="50" rx="7" fill="url(#sk)"/><rect x="4" y="-74" width="14" height="52" rx="7" fill="url(#sk)"/><rect x="22" y="-64" width="14" height="44" rx="7" fill="url(#sk)"/></g>
  </g>
  <g id="arm_chin" opacity="0">
    <path d="M160 560 C150 600 160 630 170 640" stroke="#6b4fd0" stroke-width="78" stroke-linecap="round" fill="none"/><path d="M160 560 C150 600 160 630 170 640" stroke="#241640" stroke-width="70" stroke-linecap="round" fill="none"/>
    <path d="M545 580 C520 520 470 470 420 430" stroke="#6b4fd0" stroke-width="72" stroke-linecap="round" fill="none"/><path d="M545 580 C520 520 470 470 420 430" stroke="#241640" stroke-width="64" stroke-linecap="round" fill="none"/>
    <g transform="translate(392 402) rotate(-30)"><rect x="-30" y="-26" width="62" height="54" rx="24" fill="url(#sk)"/><rect x="-14" y="-52" width="20" height="40" rx="10" fill="url(#sk)"/></g>
  </g>
  <g id="arm_wave" opacity="0">
    <path d="M160 560 C150 600 160 630 170 640" stroke="#6b4fd0" stroke-width="78" stroke-linecap="round" fill="none"/><path d="M160 560 C150 600 160 630 170 640" stroke="#241640" stroke-width="70" stroke-linecap="round" fill="none"/>
    <path d="M545 560 C610 520 630 430 615 360" stroke="#6b4fd0" stroke-width="74" stroke-linecap="round" fill="none"/><path d="M545 560 C610 520 630 430 615 360" stroke="#241640" stroke-width="66" stroke-linecap="round" fill="none"/>
    <g id="wavehand" transform="translate(615 318)"><g transform="rotate(10)"><rect x="-38" y="-30" width="76" height="66" rx="26" fill="url(#sk)"/><rect x="-36" y="-64" width="14" height="44" rx="7" fill="url(#sk)"/><rect x="-18" y="-76" width="14" height="54" rx="7" fill="url(#sk)"/><rect x="0" y="-74" width="14" height="52" rx="7" fill="url(#sk)"/><rect x="18" y="-62" width="14" height="42" rx="7" fill="url(#sk)"/><rect x="34" y="-6" width="30" height="16" rx="8" fill="url(#sk)"/></g></g>
  </g>
  <g id="head">
    <ellipse cx="350" cy="250" rx="138" ry="158" fill="url(#sk)"/>
    <ellipse cx="214" cy="262" rx="22" ry="34" fill="#C48A67"/><ellipse cx="486" cy="262" rx="22" ry="34" fill="#C48A67"/>
    <path d="M208 230 C200 120 270 72 352 72 C440 72 505 122 494 232 C478 175 450 150 400 140 C350 175 270 168 228 160 C214 185 210 205 208 230 Z" fill="#1B1424"/>
    <ellipse cx="350" cy="250" rx="138" ry="158" fill="url(#rim)"/>
    <g id="brows"><rect x="268" y="196" width="58" height="12" rx="6" fill="#1B1424"/><rect x="376" y="196" width="58" height="12" rx="6" fill="#1B1424"/></g>
    <g id="eyes">
      <g class="eye"><ellipse cx="298" cy="246" rx="21" ry="24" fill="#F4F1FA"/><circle cx="301" cy="249" r="12" fill="#1B1424"/><circle cx="305" cy="244" r="4" fill="#fff"/></g>
      <g class="eye"><ellipse cx="404" cy="246" rx="21" ry="24" fill="#F4F1FA"/><circle cx="407" cy="249" r="12" fill="#1B1424"/><circle cx="411" cy="244" r="4" fill="#fff"/></g>
    </g>
    <path d="M346 262 C340 290 336 300 352 304" fill="none" stroke="#A86F50" stroke-width="5" stroke-linecap="round"/>
    <ellipse cx="270" cy="306" rx="24" ry="12" fill="#E07A7A" opacity=".18"/><ellipse cx="432" cy="306" rx="24" ry="12" fill="#E07A7A" opacity=".18"/>
    <g id="mouth" transform="translate(350 340)">
      <path class="m m0" d="M-34 0 C-14 14 14 14 34 0" fill="none" stroke="#5a2a2a" stroke-width="7" stroke-linecap="round"/>
      <path class="m m1" opacity="0" d="M-30 -2 C-12 14 12 14 30 -2 C12 4 -12 4 -30 -2 Z" fill="#4a1e22"/>
      <path class="m m2" opacity="0" d="M-32 -6 C-14 22 14 22 32 -6 C12 0 -12 0 -32 -6 Z" fill="#4a1e22"/>
      <g class="m m3" opacity="0"><path d="M-34 -10 C-16 34 16 34 34 -10 C12 -4 -12 -4 -34 -10 Z" fill="#4a1e22"/><path d="M-20 16 C-8 26 8 26 20 16 C8 12 -8 12 -20 16 Z" fill="#d46a6a"/></g>
      <g class="m m4" opacity="0"><path d="M-40 -12 C-18 42 18 42 40 -12 C14 -6 -14 -6 -40 -12 Z" fill="#4a1e22"/><path d="M-30 -8 L30 -8 L26 0 L-26 0 Z" fill="#F4F1FA"/><path d="M-22 22 C-8 32 8 32 22 22 C8 16 -8 16 -22 22 Z" fill="#d46a6a"/></g>
      <ellipse class="m m5" opacity="0" cx="0" cy="8" rx="17" ry="22" fill="#4a1e22"/>
    </g>
  </g>
</svg>"""

STAGE = """
<div id="stage">
  <section id="sc_posts" class="scene">
    <div class="phone"><div class="ph-top"><span></span><b>@kedaikopi.contoh</b></div><div class="grid">__TILES__</div></div>
  </section>
  <section id="sc_shop" class="scene">
    <svg viewBox="0 0 900 640" class="ill">
      <g id="awning">__AWNING__</g>
      <rect x="120" y="150" width="660" height="18" fill="#2a1a52"/>
      <rect x="160" y="380" width="580" height="150" rx="14" fill="#1a1033" stroke="#4b2a9a" stroke-width="3"/>
      <rect x="190" y="340" width="90" height="40" rx="8" fill="#2c1760"/><rect x="620" y="330" width="80" height="50" rx="8" fill="#2c1760"/>
      <g class="chair" transform="translate(180 560)"><rect x="0" y="0" width="70" height="12" rx="6" fill="#3a2770"/><rect x="8" y="12" width="8" height="50" fill="#3a2770"/><rect x="54" y="12" width="8" height="50" fill="#3a2770"/></g>
      <g class="chair" transform="translate(400 560)"><rect x="0" y="0" width="70" height="12" rx="6" fill="#3a2770"/><rect x="8" y="12" width="8" height="50" fill="#3a2770"/><rect x="54" y="12" width="8" height="50" fill="#3a2770"/></g>
      <g class="chair" transform="translate(620 560)"><rect x="0" y="0" width="70" height="12" rx="6" fill="#3a2770"/><rect x="8" y="12" width="8" height="50" fill="#3a2770"/><rect x="54" y="12" width="8" height="50" fill="#3a2770"/></g>
      <g id="clock" transform="translate(450 250)"><circle r="56" fill="#120b24" stroke="#AB94FF" stroke-width="5"/><rect id="hand_m" x="-3" y="-44" width="6" height="46" rx="3" fill="#D4CAF2"/><rect id="hand_h" x="-4" y="-28" width="8" height="30" rx="4" fill="#AB94FF"/><circle r="7" fill="#E8FF2B"/></g>
    </svg>
  </section>
  <section id="sc_views" class="scene">
    <svg viewBox="0 0 900 640" class="ill">
      <g id="eye" transform="translate(250 230)"><path d="M-150 0 C-80 -95 80 -95 150 0 C80 95 -80 95 -150 0 Z" fill="#160d2c" stroke="#AB94FF" stroke-width="6"/><circle r="52" fill="#602AC8"/><circle r="24" fill="#05030A"/></g>
      <g id="bars" transform="translate(110 560)">__BARS__</g>
      <g id="bag" transform="translate(680 330)"><rect x="-90" y="-70" width="180" height="190" rx="22" fill="#160d2c" stroke="#7C7396" stroke-width="5"/><path d="M-45 -70 C-45 -130 45 -130 45 -70" fill="none" stroke="#7C7396" stroke-width="8"/><g id="bagx" opacity="0"><path d="M-35 0 L35 70 M35 0 L-35 70" stroke="#7C7396" stroke-width="10" stroke-linecap="round"/></g></g>
    </svg>
  </section>
  <section id="sc_budget" class="scene">
    <div class="meter"><div class="mlabel">BAJET IKLAN</div><div class="track"><div id="fill"></div></div></div>
    <div class="people">__PEOPLE__</div>
    <div class="plabel">PELANGGAN</div>
  </section>
  <section id="sc_crowd" class="scene"><svg viewBox="0 0 900 600" class="ill" id="crowd">__DOTS__</svg></section>
  <section id="sc_cari" class="scene">
    <svg viewBox="0 0 900 600" class="ill"><g id="crowd2">__DOTS2__</g>
      <g id="ring"><circle r="92" fill="none" stroke="#E8FF2B" stroke-width="6"/><circle r="104" fill="none" stroke="#E8FF2B" stroke-opacity=".25" stroke-width="16"/></g></svg>
  </section>
  <section id="sc_cakap" class="scene">
    <div class="adcard"><div class="adtag">CONTOH IKLAN · F&amp;B</div>
      <div class="adhead"><span class="avatar-dot"></span><b>Kedai Kopi (contoh)</b><i>Ditaja</i></div>
      <p id="adtext">Post content setiap hari, tapi pelanggan tetap tak datang?</p>
      <div class="adbtn">Hantar Mesej</div></div>
  </section>
  <section id="sc_sambung" class="scene">
    <svg viewBox="0 0 900 640" class="ill">
      <path id="sigpath" d="M150 470 L450 170 L750 470" fill="none" stroke="#E8FF2B" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
      <g class="node" id="n1" transform="translate(150 470)"><circle r="78" fill="#160d2c" stroke="#AB94FF" stroke-width="5"/><text y="12">CARI</text></g>
      <g class="node" id="n2" transform="translate(450 170)"><circle r="78" fill="#160d2c" stroke="#AB94FF" stroke-width="5"/><text y="12">CAKAP</text></g>
      <g class="node" id="n3" transform="translate(750 470)"><circle r="78" fill="#160d2c" stroke="#E8FF2B" stroke-width="5"/><text y="12">SAMBUNG</text></g>
    </svg>
  </section>
  <section id="sc_cta" class="scene">
    <div class="wordmark"><span>LOKA</span><span>DIGITAL</span></div>
    <div id="ctaline"></div>
    <div class="ctasub">DATA-LED AUDIENCE RESEARCH</div>
  </section>
</div>"""

def stage_html():
    s = STAGE.replace("__TILES__", grid_tiles())
    s = s.replace("__AWNING__", "".join(f'<rect x="{120 + i*66}" y="60" width="66" height="90" fill="{"#602AC8" if i % 2 else "#2c1760"}"/>' for i in range(10)))
    s = s.replace("__BARS__", "".join(f'<rect class="bar" x="{i*70}" y="-{60 + i*38}" width="46" height="{60 + i*38}" rx="8" fill="#AB94FF" opacity="{.35 + i*.07:.2f}"/>' for i in range(8)))
    s = s.replace("__PEOPLE__", "".join('<div class="person"><span></span><b></b></div>' for _ in range(5)))
    s = s.replace("__DOTS__", dots_markup()).replace("__DOTS2__", dots_markup())
    return s

# ---------- timeline JS ----------
def timeline_js(mode, mouth):
    js = []
    A = js.append
    A('const tl = gsap.timeline({ paused: true });')
    # ambient
    A(f'tl.fromTo("#glow", {{x:-120, y:0, scale:.9}}, {{x:140, y:-80, scale:1.15, duration:{DUR}, ease:"sine.inOut"}}, 0);')
    A(f'tl.fromTo("#glow2", {{x:80, y:0}}, {{x:-120, y:60, duration:{DUR}, ease:"sine.inOut"}}, 0);')
    # scenes: in / out + slow push
    for i, s in enumerate(scenes):
        sel = f'#sc_{s["id"]}'
        st, en = s["start"], s["end"]
        A(f'tl.set("{sel}", {{opacity:0}}, 0);')
        A(f'tl.fromTo("{sel}", {{opacity:0, y:70, scale:.94, filter:"blur(14px)"}}, {{opacity:1, y:0, scale:1, filter:"blur(0px)", duration:.55, ease:"expo.out"}}, {st:.3f});')
        push_end = en - .4 if i < len(scenes) - 1 else en
        A(f'tl.to("{sel}", {{scale:1.04, duration:{max(.2, push_end - st - .55):.3f}, ease:"none"}}, {st + .55:.3f});')
        if i < len(scenes) - 1:
            A(f'tl.to("{sel}", {{opacity:0, y:-60, scale:1.08, filter:"blur(12px)", duration:.4, ease:"power3.in"}}, {en - .4:.3f});')
        # gesture
        g = GESTURE[s["id"]]
        for other in ["down", "point", "open", "chin", "wave"]:
            A(f'tl.to("#arm_{other}", {{opacity:{1 if other == g else 0}, duration:.18, ease:"power2.out"}}, {st + .05:.3f});')
        A(f'tl.to("#avbob", {{y:-14, duration:.22, ease:"power2.out", yoyo:true, repeat:1}}, {st + .05:.3f});')
    A('tl.fromTo("#avwrap", {y:420}, {y:0, duration:.7, ease:"expo.out"}, 0.0);')
    # per-scene details
    def sc(name): return next(s for s in scenes if s["id"] == name)
    p = sc("posts")["start"]
    A(f'tl.fromTo("#sc_posts .tile", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:.32, ease:"back.out(2)", stagger:.09}}, {p + .25:.3f});')
    s = sc("shop")["start"]; d = sc("shop")["dur"]
    A(f'tl.fromTo("#hand_m", {{rotation:0, svgOrigin:"0 0"}}, {{rotation:720, svgOrigin:"0 0", duration:{d:.3f}, ease:"none"}}, {s:.3f});')
    A(f'tl.fromTo("#hand_h", {{rotation:20, svgOrigin:"0 0"}}, {{rotation:80, svgOrigin:"0 0", duration:{d:.3f}, ease:"none"}}, {s:.3f});')
    A(f'tl.fromTo(".chair", {{y:30, opacity:0}}, {{y:0, opacity:1, duration:.4, ease:"expo.out", stagger:.12}}, {s + .3:.3f});')
    v = sc("views"); A(f'tl.fromTo(".bar", {{scaleY:0, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:.5, ease:"expo.out", stagger:.08}}, {v["start"] + .3:.3f});')
    l4 = next(l for l in LINES if l["id"] == "s4")
    A(f'tl.fromTo("#bagx", {{opacity:0, scale:.4, svgOrigin:"0 35"}}, {{opacity:1, scale:1, svgOrigin:"0 35", duration:.3, ease:"back.out(3)"}}, {l4["start"] + .2:.3f});')
    A(f'tl.fromTo("#eye", {{scaleY:1}}, {{scaleY:.1, duration:.08, yoyo:true, repeat:1, svgOrigin:"250 230"}}, {v["start"] + 1.2:.3f});')
    b = sc("budget"); l6 = next(l for l in LINES if l["id"] == "s6")
    A(f'tl.fromTo("#fill", {{scaleX:1, transformOrigin:"0% 50%"}}, {{scaleX:0.02, duration:{l6["start"] - b["start"]:.3f}, ease:"power2.in"}}, {b["start"] + .2:.3f});')
    A(f'tl.fromTo(".person", {{opacity:0, y:30}}, {{opacity:.55, y:0, duration:.4, stagger:.06, ease:"expo.out"}}, {b["start"] + .3:.3f});')
    A(f'tl.to(".person", {{y:-10, duration:.15, yoyo:true, repeat:1, stagger:.05}}, {l6["start"] + .3:.3f});')
    c = sc("crowd"); A(f'tl.fromTo("#crowd .dot", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:.35, ease:"back.out(2)", stagger:{{each:.008, from:"random"}}}}, {c["start"] + .2:.3f});')
    A(f'tl.to("#crowd", {{x:-30, duration:{c["dur"]:.3f}, ease:"none"}}, {c["start"]:.3f});')
    k = sc("cari")
    A(f'tl.fromTo("#ring", {{x:160, y:150, scale:.4, opacity:0}}, {{x:160, y:150, scale:1, opacity:1, duration:.35, ease:"expo.out"}}, {k["start"] + .2:.3f});')
    A(f'tl.to("#ring", {{x:640, y:430, duration:.9, ease:"power3.inOut"}}, {k["start"] + .6:.3f});')
    A(f'tl.to("#ring", {{x:470, y:260, duration:.6, ease:"power3.inOut"}}, {k["start"] + 1.55:.3f});')
    A(f'tl.to("#crowd2 .dot", {{opacity:.18, duration:.3}}, {k["start"] + .5:.3f});')
    A(f'tl.to("#crowd2 .hit", {{opacity:1, fill:"#E8FF2B", duration:.25, stagger:.05}}, {k["start"] + 1.6:.3f});')
    ck = sc("cakap")
    A(f'tl.fromTo(".adcard", {{rotationX:30, y:80}}, {{rotationX:0, y:0, duration:.7, ease:"expo.out"}}, {ck["start"]:.3f});')
    A(f'tl.fromTo("#adtext", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:1.0, ease:"none"}}, {ck["start"] + .35:.3f});')
    sb = sc("sambung")
    A(f'tl.fromTo(".node", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:.4, ease:"back.out(2)", stagger:.28}}, {sb["start"] + .15:.3f});')
    A(f'tl.fromTo("#sigpath", {{strokeDashoffset:900, strokeDasharray:900}}, {{strokeDashoffset:0, strokeDasharray:900, duration:1.0, ease:"expo.inOut"}}, {sb["start"] + .5:.3f});')
    ct = sc("cta")
    A(f'tl.fromTo(".wordmark span", {{yPercent:110}}, {{yPercent:0, duration:.7, ease:"expo.out", stagger:.12}}, {ct["start"] + .1:.3f});')
    A(f'tl.fromTo("#ctaline", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:.8, ease:"expo.inOut"}}, {ct["start"] + .6:.3f});')
    A(f'tl.fromTo(".ctasub", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:.5, ease:"power3.out"}}, {ct["start"] + 1.2:.3f});')
    A(f'tl.fromTo("#wavehand", {{rotation:-12, svgOrigin:"615 360"}}, {{rotation:12, svgOrigin:"615 360", duration:.28, ease:"sine.inOut", yoyo:true, repeat:5}}, {ct["start"] + .2:.3f});')
    # blinks (deterministic)
    t = 1.7
    while t < DUR - .3:
        A(f'tl.to("#eyes", {{scaleY:.08, svgOrigin:"350 246", duration:.06, yoyo:true, repeat:1}}, {t:.2f});')
        t += 2.9 if int(t * 10) % 2 else 3.6
    # head life: tilt per line
    for i, ln in enumerate(LINES):
        A(f'tl.to("#head", {{rotation:{(-4 if i % 2 else 3)}, svgOrigin:"350 400", duration:.5, ease:"sine.inOut"}}, {ln["start"]:.3f});')
        A(f'tl.to("#brows", {{y:{-8 if i % 3 == 0 else 0}, duration:.2, ease:"power2.out"}}, {ln["start"]:.3f});')
    A(f'tl.to("#body", {{scaleY:1.012, svgOrigin:"350 640", duration:1.6, ease:"sine.inOut", yoyo:true, repeat:{int(DUR / 1.6)}}}, 0);')
    # mouth
    if mode == "A":
        for tm, lv in mouth:
            for m in range(6):
                A(f'tl.set("#mouth .m{m}", {{opacity:{1 if m == lv else 0}}}, {tm});')
    # captions
    for ln in LINES:
        cap = f'#cap_{ln["id"]}'
        st = max(0.05, ln["start"] - (0.08 if mode == "A" else 0.18))
        en = ln["end"] + ln["gap"] * (0.55 if mode == "A" else 0.85)
        if mode == "A":
            A(f'tl.fromTo("{cap}", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:.14, ease:"power2.out"}}, {st:.3f});')
            for k, w in enumerate(ln["words"]):
                A(f'tl.fromTo("#{ln["id"]}w{k} .wt", {{opacity:.28}}, {{opacity:1, duration:.08}}, {w["start"]:.3f});')
        else:
            A(f'tl.fromTo("{cap} .wt", {{yPercent:105, opacity:0}}, {{yPercent:0, opacity:1, duration:.5, ease:"expo.out", stagger:.06}}, {st:.3f});')
        kw = [k for k, w in enumerate(ln["words"]) if w["text"].strip(".,?!").lower() == ln["key"].lower()]
        if kw:
            k0 = kw[0]; kt = ln["words"][k0]["start"] if mode == "A" else st + .35
            A(f'tl.fromTo("#{ln["id"]}w{k0} .kb", {{opacity:0, scale:1.25}}, {{opacity:1, scale:1, duration:.22, ease:"back.out(2.5)"}}, {kt:.3f});')
            A(f'tl.to("#{ln["id"]}w{k0} .wt", {{color:"#E8FF2B", duration:.12}}, {kt:.3f});')
        A(f'tl.to("{cap}", {{opacity:0, duration:.12, ease:"power2.in"}}, {en - .12:.3f});')
    A('window.__timelines["main"] = tl;')
    A('tl.seek(0);')
    return "\n      ".join(js)

CSS = """
      :root { --ink:#05030A; --p1:#602AC8; --p2:#301270; --y:#E8FF2B; --lav:#AB94FF; --mist:#D4CAF2; --grey:#7C7396; }
      * { margin:0; padding:0; box-sizing:border-box; }
      html, body { width:1080px; height:1920px; overflow:hidden; background:var(--ink); }
      #root { position:relative; width:1080px; height:1920px; overflow:hidden; background:var(--ink); font-family:'Inter',sans-serif; color:var(--mist); }
      #bg { position:absolute; inset:0; }
      #glow { position:absolute; left:-200px; top:180px; width:1200px; height:1200px; border-radius:50%; background:radial-gradient(circle, rgba(96,42,200,.55) 0%, rgba(48,18,112,.25) 45%, transparent 70%); }
      #glow2 { position:absolute; left:300px; top:1150px; width:900px; height:900px; border-radius:50%; background:radial-gradient(circle, rgba(96,42,200,.35) 0%, transparent 65%); }
      #vig { position:absolute; inset:0; background:radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(0,0,0,.75) 100%); }
      #grain { position:absolute; inset:0; opacity:.07; background-image:repeating-radial-gradient(circle at 17% 32%, #fff 0 1px, transparent 1px 3px), repeating-radial-gradient(circle at 71% 63%, #fff 0 1px, transparent 1px 4px); mix-blend-mode:overlay; }
      #meta { position:absolute; left:120px; top:300px; font:400 28px 'Space Mono',monospace; letter-spacing:.3em; color:var(--grey); }
      #meta b { color:var(--y); font-weight:400; }
      #stage { position:absolute; left:90px; top:360px; width:900px; height:700px; perspective:1200px; }
      .scene { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; opacity:0; }
      .ill { width:900px; height:640px; overflow:visible; }
      .phone { width:440px; height:660px; border-radius:46px; background:#0d0818; border:4px solid #3b2770; padding:26px 22px; box-shadow:0 0 80px rgba(96,42,200,.45); }
      .ph-top { display:flex; align-items:center; gap:14px; margin-bottom:22px; font:600 28px 'Inter'; color:var(--mist); }
      .ph-top span { width:46px; height:46px; border-radius:50%; background:var(--p1); }
      .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
      .tile { aspect-ratio:1; border-radius:10px; position:relative; }
      .tile span { position:absolute; inset:28%; border-radius:50%; border:4px solid rgba(212,202,242,.35); }
      .meter { width:760px; }
      .mlabel, .plabel { font:400 28px 'Space Mono',monospace; letter-spacing:.3em; color:var(--grey); margin-bottom:22px; }
      .plabel { margin-top:24px; margin-bottom:0; }
      .track { height:64px; border-radius:32px; background:#160d2c; border:3px solid #3b2770; padding:8px; }
      #fill { height:100%; border-radius:26px; background:linear-gradient(90deg, var(--p1), var(--lav)); }
      .people { display:flex; gap:44px; margin-top:110px; }
      .person { display:flex; flex-direction:column; align-items:center; gap:10px; }
      .person span { width:56px; height:56px; border-radius:50%; background:var(--grey); }
      .person b { width:96px; height:70px; border-radius:48px 48px 12px 12px; background:var(--grey); }
      #crowd .dot, #crowd2 .dot { fill:#7C7396; }
      .adcard { width:760px; border-radius:30px; background:#0f0920; border:3px solid #4b2a9a; padding:40px; box-shadow:0 30px 90px rgba(0,0,0,.6), 0 0 70px rgba(96,42,200,.35); }
      .adtag { font:400 28px 'Space Mono',monospace; letter-spacing:.24em; color:var(--grey); margin-bottom:28px; }
      .adhead { display:flex; align-items:center; gap:16px; font:700 32px 'Inter'; color:var(--mist); }
      .adhead i { margin-left:auto; font:400 28px 'Inter'; color:var(--grey); font-style:normal; }
      .avatar-dot { width:58px; height:58px; border-radius:50%; background:var(--p1); }
      #adtext { margin:34px 0; font:700 50px/1.15 'Inter'; color:#fff; }
      .adbtn { display:inline-block; padding:18px 34px; border-radius:16px; background:var(--y); color:#05030A; font:700 32px 'Inter'; }
      .node text { font:400 34px 'Archivo Black'; fill:var(--mist); text-anchor:middle; letter-spacing:.02em; }
      .wordmark { display:flex; flex-direction:column; align-items:flex-start; width:760px; font:400 150px/0.95 'Archivo Black'; letter-spacing:-.04em; color:#fff; }
      .wordmark span { display:block; }
      #ctaline { width:760px; height:10px; margin-top:34px; background:var(--y); box-shadow:0 0 30px rgba(232,255,43,.7); }
      .ctasub { width:760px; margin-top:26px; font:400 34px 'Space Mono',monospace; letter-spacing:.3em; color:var(--y); }
      .cap { position:absolute; left:0; width:1080px; top:1070px; padding:0 150px; text-align:center; font:800 60px/1.18 'Inter'; color:var(--mist); letter-spacing:-.02em; overflow:visible; }
      .B .cap { font:400 64px/1.12 'Archivo Black'; color:#fff; letter-spacing:-.03em; text-transform:uppercase; }
      .w { position:relative; display:inline-block; overflow:visible; }
      .w.key { margin:0 16px; }
      .B .w { overflow:hidden; vertical-align:top; padding:0 4px; }
      .wt { display:inline-block; }
      .kb { position:absolute; left:-12px; right:-12px; top:-4px; bottom:-6px; border:3px solid var(--y); border-radius:6px; box-shadow:0 0 22px rgba(232,255,43,.45); opacity:0; }
      .kb b { position:absolute; width:12px; height:12px; background:var(--y); border-radius:2px; }
      .kb b:nth-child(1){left:-7px;top:-7px} .kb b:nth-child(2){right:-7px;top:-7px} .kb b:nth-child(3){left:-7px;bottom:-7px} .kb b:nth-child(4){right:-7px;bottom:-7px}
      #avwrap { position:absolute; left:190px; top:1280px; width:700px; height:640px; }
      #avglow { position:absolute; left:140px; top:1200px; width:800px; height:800px; border-radius:50%; background:radial-gradient(circle, rgba(171,148,255,.22) 0%, transparent 60%); }
      #tag { position:absolute; right:110px; top:300px; font:400 28px 'Space Mono',monospace; letter-spacing:.3em; color:var(--grey); }
"""

def page(mode, mouth):
    label = "A · AVATAR + VO" if mode == "A" else "B · TANPA VO"
    audio = f'<audio id="mix" src="assets/mix_{mode}.wav" class="clip" data-start="0" data-duration="{DUR}" data-track-index="9"></audio>'
    return f"""<!doctype html>
<html lang="ms">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>{CSS}</style>
  </head>
  <body>
    <div id="root" class="{mode}" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
      <div id="bg" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0"><div id="glow"></div><div id="glow2"></div></div>
      <div id="meta" class="clip" data-start="0" data-duration="{DUR}" data-track-index="1">CONTOH · F&amp;B</div>
      <div id="tag" class="clip" data-start="0" data-duration="{DUR}" data-track-index="1" data-layout-ignore>DRAFT {mode}</div>
      <div id="stagewrap" class="clip" data-start="0" data-duration="{DUR}" data-track-index="2" data-layout-allow-overlap>{stage_html()}</div>
      {caption_markup(mode)}
      <div id="avglow" class="clip" data-start="0" data-duration="{DUR}" data-track-index="4"></div>
      <div id="avwrap" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5" data-layout-allow-overflow data-layout-ignore><div id="avbob">{AVATAR}</div></div>
      <div id="vig" class="clip" data-start="0" data-duration="{DUR}" data-track-index="6" data-layout-ignore></div>
      <div id="grain" class="clip" data-start="0" data-duration="{DUR}" data-track-index="7" data-layout-ignore></div>
      {audio}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      {timeline_js(mode, mouth)}
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    mouth = mouth_track()
    scaffold = os.path.join(HERE, "..", "..", "hf-lab", "lab-test")
    for mode in "AB":
        d = os.path.join(HERE, mode); os.makedirs(os.path.join(d, "assets"), exist_ok=True)
        for f in ["hyperframes.json", "package.json"]:
            shutil.copy(os.path.join(scaffold, f), d)
        json.dump({"id": f"ref002-draft-{mode.lower()}", "name": f"REF-002 draft {mode}"}, open(os.path.join(d, "meta.json"), "w"))
        shutil.copy(os.path.join(HERE, "assets", f"mix_{mode}.wav"), os.path.join(d, "assets"))
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page(mode, mouth))
    print("scenes", [(s["id"], s["start"], s["dur"]) for s in scenes], "dur", DUR, "mouth keys", len(mouth))
