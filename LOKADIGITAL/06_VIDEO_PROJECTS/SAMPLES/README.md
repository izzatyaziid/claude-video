# LOKADIGITAL — Production Test: 3 Sample Videos

> **Status:** 🟡 Untuk semakan kau. Dipilih dari [pelan content Disember](../../08_MONTHLY_CONTENT/MONTHLY_CONTENT_PLAN_2026-12.md).
> Semua: 1080×1920 · 30 fps · 30 s · H.264 / AAC 48 kHz · −14 LUFS · **tiada voiceover** · muzik + SFX dijana khas.

| Sample | Rawatan | Video | Sumber |
|---|---|---|---|
| **S01 · Boost Post Bila Sales Turun?** | Character-led (Signature Character) | [`S01_BOOST_POST/out/…mp4`](S01_BOOST_POST/out/LOKADIGITAL_S01_BOOST_POST_1080x1920.mp4) | [`src/s01.html`](S01_BOOST_POST/src/s01.html) · [`audio/score_s01.py`](S01_BOOST_POST/audio/score_s01.py) |
| **S02 · Viral Macam Bunga Api** | Cinematic 3D metaphor (three.js) | [`S02_BUNGA_API/out/…mp4`](S02_BUNGA_API/out/LOKADIGITAL_S02_BUNGA_API_1080x1920.mp4) | [`src/s02.html`](S02_BUNGA_API/src/s02.html) · [`audio/score_s02.py`](S02_BUNGA_API/audio/score_s02.py) |
| **S03 · Funnel You Bocor** | Motion graphics + infographic | [`S03_FUNNEL_BOCOR/out/…mp4`](S03_FUNNEL_BOCOR/out/LOKADIGITAL_S03_FUNNEL_BOCOR_1080x1920.mp4) | [`src/s03.html`](S03_FUNNEL_BOCOR/src/s03.html) · [`audio/score_s03.py`](S03_FUNNEL_BOCOR/audio/score_s03.py) |

## Workflow & tools
1. **Idea** (pelan bulanan) → **cerita & beat** (dalam komen timeline setiap `src/*.html`) → **look** (bahasa visual EP02: ink + ungu, kuning hanya untuk makna, Inter Display + JetBrains Mono, Signal Line).
2. **Render picture:** HTML5 Canvas 2D + **three.js WebGL** (SwiftShader, CPU) dalam Chromium headless (Playwright) → JPG per frame. Setiap frame ialah fungsi masa (*stateless*), jadi boleh dirender selari. [`_engine/render.js`](_engine/render.js)
3. **Watak:** rig 2.5D Signature Character ([`07_SIGNATURE_CHARACTER`](../../07_SIGNATURE_CHARACTER/README.md)).
4. **Audio:** muzik + SFX disintesis dengan Python/numpy ([`_engine/audio_lib.py`](_engine/audio_lib.py)). **Tiada suara.**
5. **Mux:** ffmpeg, normalisasi kenyaringan EBU R128 dua laluan ke −14 LUFS ([`_engine/mux.sh`](_engine/mux.sh)).

## Jana semula
```bash
cd LOKADIGITAL/06_VIDEO_PROJECTS/SAMPLES
node _engine/render.js S01_BOOST_POST/src/s01.html /tmp/s01 30 4
python3 S01_BOOST_POST/audio/score_s01.py /tmp/s01.wav
_engine/mux.sh /tmp/s01 /tmp/s01.wav S01_BOOST_POST/out/LOKADIGITAL_S01_BOOST_POST_1080x1920.mp4 "LOKADIGITAL S01"
```
