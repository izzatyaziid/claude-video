"""01 MANIFESTO TIPOGRAFI — full-screen type only, every card cut on the beat (100 BPM).
Idea: customers don't buy features, they buy outcomes."""
NAME = "LokaDigital Preview 01 · Manifesto Tipografi"
SLUG = "01-manifesto-tipografi"
PILL = ""
NO_BRAND_CHROME = True
B = 0.84  # ~71 bpm grid; music runs at double time (143 bpm feel)

# (beat, text, look)  look: ink | lime | purple | small
SEQ = [
    (0, "BERHENTI", "ink"), (2, "JUAL", "lime"), (3, "PRODUK.", "lime"),
    (6, "PELANGGAN", "ink"), (7, "TAK BELI", "ink"), (8.5, "KOPI KAU.", "purple"),
    (11, "MEREKA BELI", "ink"), (12.5, "PAGI YANG", "lime"), (13.5, "LEBIH BAIK.", "lime"),
    (16, "CONTOH · F&B", "small"),
    (18, "IKLAN KAU", "ink"), (19, "CAKAP PASAL", "ink"), (20.5, "BAHAN.", "purple"), (21.5, "SAIZ.", "purple"), (22.5, "HARGA.", "purple"),
    (24, "PELANGGAN", "ink"), (25, "SCROLL.", "ink"),
    (28, "MEREKA TAK PEDULI", "ink"), (30, "APA PRODUK", "ink"), (31, "KAU ADA.", "purple"),
    (34, "MEREKA PEDULI", "ink"), (36, "APA HIDUP", "lime"), (37, "MEREKA JADI.", "lime"),
    (41, "JUAL HASIL.", "lime"), (43, "BUKAN CIRI.", "ink"),
    (46, "MASALAH", "purple"), (47, "→ PENYELESAIAN", "purple"), (49, "SEBELUM", "ink"), (50, "→ SELEPAS", "ink"),
    (52, "ITU YANG", "lime"), (53, "BUAT ORANG", "lime"), (54, "BELI.", "lime"),
    (57, "NAK IKLAN", "ink"), (58, "YANG JUAL", "ink"), (59, "HASIL?", "purple"),
    (62, "@END", "end"),
]
END_T = 62 * B  # ~52 s; then the brand end card

CSS = """
  .card { position:absolute; inset:0; display:flex; align-items:center; justify-content:flex-start; padding:0 90px; }
  .card.ink { background:var(--ink); color:#fff; }
  .card.lime { background:var(--g); color:var(--ink); }
  .card.purple { background:radial-gradient(120% 70% at 80% 10%, var(--mag) 0%, var(--p1) 45%, var(--p2) 100%); color:#fff; }
  .card.small { background:var(--ink); color:var(--grey); justify-content:center; }
  .card .t { font:900 150px/0.9 'Inter'; letter-spacing:-.055em; max-width:900px; }
  #vig { display:none; }
  .card.small .t { font:700 40px 'Inter'; letter-spacing:.4em; }
  .card .k { position:absolute; left:90px; bottom:460px; font:700 28px 'Inter'; letter-spacing:.3em; opacity:.6; }
  #end { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 110px; }
  #end .h { font:900 120px/0.92 'Inter'; letter-spacing:-.05em; }
  #endlogo { width:170px; height:170px; mix-blend-mode:screen; margin:0 0 30px -20px; }
  #endrule { width:200px; height:12px; border-radius:6px; background:var(--g); margin:36px 0 40px; }
  #end .ctablock { width:860px; }
"""

def _fs(txt):
    longest = max(len(w) for w in txt.split())
    return int(max(110, min(230, 900 / (0.66 * max(longest, 4)))))

def _cards():
    out = []; cut = [s for s in SEQ]
    for i, (b, txt, look) in enumerate(cut[:-1]):
        st = b * B; en = cut[i + 1][0] * B
        k = f"{i + 1:02d}"
        out.append(f'<div id="c{i}" class="card {look} clip" data-start="{st:.3f}" data-duration="{en - st:.3f}" data-track-index="1">'
                   f'<span class="t" style="font-size:{_fs(txt)}px">{txt.replace("&", "&amp;")}</span>' + (f'<span class="k">{k} / 35</span>' if look != "small" else "") + '</div>')
    return "\n      ".join(out)

BODY = _cards() + f"""
      <div id="end" class="clip" data-start="{END_T:.3f}" data-duration="{60 - END_T:.3f}" data-track-index="2">
        <img id="endlogo" src="assets/logo.jpg" alt="LOKADIGITAL">
        <div class="h"><span class="el">JUAL</span><br><span class="el gr">HASIL.</span><br><span class="el">BUKAN CIRI.</span></div>
        <div id="endrule"></div>
        <div class="ctablock" id="endcta"><div><label>LANGKAH SETERUSNYA</label><small>Strategi iklan berasaskan hasil</small></div><b>DM LOKADIGITAL</b></div>
      </div>"""

def _js():
    js = []
    for i, (b, txt, look) in enumerate(SEQ[:-1]):
        st = b * B; sel = f"#c{i} .t"
        v = i % 4
        if look == "small":
            js.append(f'tl.fromTo("{sel}", {{opacity:0, letterSpacing:"1.2em"}}, {{opacity:1, letterSpacing:".4em", duration:.8, ease:"expo.out"}}, {st:.3f});')
        elif v == 0:
            js.append(f'tl.fromTo("{sel}", {{scale:1.6, opacity:0}}, {{scale:1, opacity:1, duration:.28, ease:"expo.out"}}, {st:.3f});')
        elif v == 1:
            js.append(f'tl.fromTo("{sel}", {{xPercent:-30, opacity:0}}, {{xPercent:0, opacity:1, duration:.3, ease:"expo.out"}}, {st:.3f});')
        elif v == 2:
            js.append(f'tl.fromTo("{sel}", {{yPercent:80, rotationX:-70, opacity:0, transformPerspective:900}}, {{yPercent:0, rotationX:0, opacity:1, duration:.35, ease:"expo.out"}}, {st:.3f});')
        else:
            js.append(f'tl.fromTo("{sel}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:.3, ease:"power3.out"}}, {st:.3f});')
        # slow drift while held
        nxt = SEQ[i + 1][0] * B
        js.append(f'tl.to("{sel}", {{x:-24, duration:{max(.1, nxt - st - .3):.3f}, ease:"none"}}, {st + .3:.3f});')
    js.append(f'tl.fromTo("#endlogo", {{opacity:0, scale:.6}}, {{opacity:1, scale:1, duration:.6, ease:"expo.out"}}, {END_T + .2:.3f});')
    js.append(f'tl.fromTo("#end .el", {{yPercent:100, opacity:0}}, {{yPercent:0, opacity:1, duration:.6, ease:"expo.out", stagger:.18}}, {END_T + .5:.3f});')
    js.append(f'tl.fromTo("#endrule", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:.7, ease:"expo.inOut"}}, {END_T + 1.4:.3f});')
    js.append(f'tl.fromTo("#endcta", {{y:60, opacity:0}}, {{y:0, opacity:1, duration:.7, ease:"expo.out"}}, {END_T + 2.0:.3f});')
    js.append(f'tl.to("#end", {{scale:1.03, duration:{60 - END_T - 2:.3f}, ease:"none"}}, {END_T + 2:.3f});')
    return "\n      ".join(js)
JS = _js()

def sound(m):
    import lib
    prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (48, [55, 60, 64]), (43, [55, 59, 62])]
    m.score(143, prog, kind="pad", drums="four", start=0, end=END_T)
    for b, txt, look in SEQ[:-1]:
        m.at(m.fx, m.thud() if look in ("lime", "purple") else m.tick(), b * B, .55 if look != "ink" else .35)
    m.at(m.fx, m.riser(2.4), END_T - 2.4, .4); m.at(m.fx, m.impact(), END_T, .8)
    m.score(143, [(45, [57, 60, 64]), (41, [53, 57, 60])], kind="pad", drums="none", start=END_T + .5, end=59)
