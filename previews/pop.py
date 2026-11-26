"""Pop-out motion kit (v2): 3D cards that burst toward camera, shine sweeps, particle bursts, floating idle,
and a REF-002 style caption band with a lime keyword box. All deterministic (no random at runtime)."""
import math

CSS = """
  .stage3d { position:absolute; left:0; right:0; top:400px; height:1000px; perspective:1300px; perspective-origin:50% 45%; }
  .c3 { position:absolute; border-radius:28px; background:linear-gradient(160deg, rgba(255,255,255,.10), rgba(255,255,255,.03)); border:2px solid rgba(255,255,255,.16);
        box-shadow:0 50px 100px rgba(0,0,0,.65), 0 0 60px rgba(123,22,184,.35), inset 0 1px 0 rgba(255,255,255,.2); overflow:hidden; transform-style:preserve-3d; opacity:0; }
  .c3.lime { background:var(--g); color:var(--ink); border-color:rgba(255,255,255,.5); box-shadow:0 50px 100px rgba(0,0,0,.6), 0 0 80px rgba(180,255,57,.45); }
  .c3.mag { background:linear-gradient(160deg,#B800F0,#46096B); border-color:rgba(255,255,255,.3); box-shadow:0 50px 100px rgba(0,0,0,.6), 0 0 80px rgba(184,0,240,.5); }
  .shine { position:absolute; top:-20%; bottom:-20%; width:120px; left:-200px; transform:skewX(-20deg);
           background:linear-gradient(90deg, transparent, rgba(255,255,255,.55), transparent); pointer-events:none; }
  .spark { position:absolute; width:18px; height:18px; border-radius:50%; background:var(--g); box-shadow:0 0 16px rgba(180,255,57,.9); opacity:0; }
  .spark.m { background:#B800F0; box-shadow:0 0 16px rgba(184,0,240,.9); }
  .spark.w { background:#fff; box-shadow:0 0 16px rgba(255,255,255,.9); width:12px; height:12px; }
  .ring { position:absolute; border-radius:50%; border:6px solid var(--g); box-shadow:0 0 40px rgba(180,255,57,.6), inset 0 0 30px rgba(180,255,57,.3); opacity:0; }
  .capband { position:absolute; left:0; right:0; top:1420px; height:220px; }
  .cap { position:absolute; left:80px; right:80px; top:0; text-align:center; font:900 74px/1.08 'Inter'; letter-spacing:-.04em; color:#fff; opacity:0;
         text-shadow:0 10px 40px rgba(0,0,0,.8); }
  .cap .w { display:inline-block; }
  .cap .k { position:relative; display:inline-block; padding:0 14px; margin:0 4px; color:var(--ink); isolation:isolate; }
  .cap .k b { position:absolute; inset:-2px 0 -6px; background:var(--g); border-radius:14px; z-index:-1; transform-origin:0 50%; }
"""

def caps(items, track=7):
    """items: (id, start, end, text) ; text marks the keyword as [word]."""
    out = []
    for cid, a, b, t in items:
        html = ""
        for w in t.split(" "):
            if w.startswith("[") and "]" in w:
                core, rest = w[1:].split("]", 1)
                html += f'<span class="k"><b></b>{core}</span>{rest} '
            else:
                html += f'<span class="w">{w}</span> '
        out.append(f'<div class="cap clip" id="{cid}" data-start="{a:.2f}" data-duration="{b - a:.2f}" data-track-index="{track}">{html.strip()}</div>')
    return "<div class=\"capband\">" + "".join(out) + "</div>"

def caps_js(items, frame0=False):
    j = []
    for n, (cid, a, b, t) in enumerate(items):
        if frame0 and n == 0:
            j.append(f'tl.set("#{cid}", {{opacity:1}}, 0);')
            j.append(f'tl.set("#{cid} .k b", {{scaleX:1}}, 0);')
        else:
            j.append(f'tl.fromTo("#{cid}", {{opacity:0, y:30, scale:.92}}, {{opacity:1, y:0, scale:1, duration:.22, ease:"back.out(2.5)"}}, {a:.2f});')
            j.append(f'tl.fromTo("#{cid} .k b", {{scaleX:0}}, {{scaleX:1, duration:.25, ease:"expo.out"}}, {a + .12:.2f});')
            j.append(f'tl.fromTo("#{cid} .k", {{scale:1.25}}, {{scale:1, duration:.3, ease:"back.out(3)"}}, {a + .12:.2f});')
        j.append(f'tl.to("#{cid}", {{opacity:0, y:-20, duration:.15, ease:"power2.in"}}, {b - .15:.2f});')
    return j

def pop(sel, t, z=-500, rx=-40, ry=0, y=120, scale=.25, dur=.6, ease="back.out(2)", frame0=False):
    if frame0:
        return f'tl.set("{sel}", {{opacity:1, scale:1, z:0, rotationX:0, rotationY:0, y:0}}, 0);'
    return (f'tl.fromTo("{sel}", {{opacity:0, scale:{scale}, z:{z}, rotationX:{rx}, rotationY:{ry}, y:{y}}}, '
            f'{{opacity:1, scale:1, z:0, rotationX:0, rotationY:0, y:0, duration:{dur}, ease:"{ease}"}}, {t:.2f});')

def out(sel, t, dur=.35, z=-400):
    return f'tl.to("{sel}", {{opacity:0, scale:.6, z:{z}, duration:{dur}, ease:"power3.in"}}, {t:.2f});'

def floaty(sel, t0, t1, amp=14, rot=4, period=2.2):
    n = max(1, int((t1 - t0) / period))
    return f'tl.to("{sel}", {{y:"-={amp}", rotationY:{rot}, duration:{period / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:{2 * n - 1}}}, {t0:.2f});'

def shine(sel, t, w=900):
    return f'tl.fromTo("{sel} .shine", {{x:0}}, {{x:{w + 400}, duration:.7, ease:"power2.inOut"}}, {t:.2f});'

def sparks_html(prefix, n=14, cls=""):
    return "".join(f'<div class="spark {["", "m", "w"][i % 3] if not cls else cls}" id="{prefix}{i}"></div>' for i in range(n))

def burst(prefix, cx, cy, t, n=14, r0=40, r1=360, dur=.8):
    """sparks fly out from (cx, cy). Each spark id may be used by only one burst."""
    j = []
    for i in range(n):
        a = i / n * 2 * math.pi + (i % 3) * .2
        r = r1 * (.65 + .35 * ((i * 7) % 5) / 4)
        j.append(f'tl.set("#{prefix}{i}", {{left:{cx}, top:{cy}, opacity:0}}, 0);')
        j.append(f'tl.fromTo("#{prefix}{i}", {{x:{math.cos(a) * r0:.0f}, y:{math.sin(a) * r0:.0f}, opacity:1, scale:1.2}}, '
                 f'{{x:{math.cos(a) * r:.0f}, y:{math.sin(a) * r:.0f}, opacity:0, scale:.3, duration:{dur}, ease:"power3.out", immediateRender:false}}, {t:.2f});')
    return j

def ring(sel, t, dur=.7):
    return f'tl.fromTo("{sel}", {{opacity:1, scale:.3}}, {{opacity:0, scale:1.6, duration:{dur}, ease:"expo.out", immediateRender:false}}, {t:.2f});'
