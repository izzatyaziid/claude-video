# EP02 · Animatic v1

> **Status:** ⏸️ **Ditangguhkan** (2026-11-25). Dinilai semula sebagai terlalu bergantung pada headline dan zarah berulang; lihat [Creative Direction v2 (cadangan)](../../CONCEPT/CREATIVE_DIRECTION_v2_PROPOSAL.md). Disimpan sebagai rekod v1.
> Visual: berdasarkan [style frames v2](../../ASSETS/STYLE_FRAMES/README.md) (benchmark rasmi). Timing: [`BEAT_MAP_EP02.md`](../BEAT_MAP_EP02.md). **Tiada voiceover**: audio ialah muzik + SFX sahaja.

| Fail | Butiran |
|---|---|
| [`out/LOKADIGITAL_EP02_ANIMATIC_v1_1080x1920.mp4`](out/LOKADIGITAL_EP02_ANIMATIC_v1_1080x1920.mp4) | 1080×1920 · 30 fps · 67.5 s · H.264 / AAC 48 kHz · −13.9 LUFS |
| [`out/ANIMATIC_v1_contact_sheet_1fps.jpg`](out/ANIMATIC_v1_contact_sheet_1fps.jpg) | Satu frame setiap saat (72 frame), untuk semakan pantas |

**Overlay semakan:** di bawah kiri setiap frame ada label kecil `ANIMATIC v1 · scene · beat · masa`, supaya komen boleh merujuk beat yang tepat (contoh "B24"). Label ini akan dibuang dalam production.

## Apa yang animatic ini tunjukkan
- Flow cerita penuh: 8 scene, 42 beat.
- Timing setiap scene dan ayat, dengan masa bacaan disemak automatik.
- Gerak kamera maya: dolly, push-through tajuk 3D, rack focus/orbit, push-in/pull-back, tracking laju, crane-out.
- Typography: masked rise, underline dilukis, strike, typewriter, huruf hanyut, morph "Ramai yang nampak → Cari yang beli".
- Zarah manusia: ledakan, freeze, siluet terbentuk, tapisan, kelompok F&B berpaling, gelombang penyalaan kuning.
- Signal Line: titik → garis → rail → pengimbas → pancaran → cabang uji → laluan pemenang → underline logo → CTA.
- Transition, serta penempatan muzik dan SFX, termasuk senyap 0.65 s selepas freeze dan 0.8 s di hujung.

## Had animatic (bukan kualiti akhir)
- Kedalaman zarah dan bloom dipermudahkan supaya render pantas: 1× resolusi, bloom kecil, tiada DOF fizikal sebenar. Style frames v2 kekal sebagai standard rupa akhir.
- Skor ialah **muzik sementara** yang dijana secara prosedur. Strukturnya (tempo 92 BPM, build, drop 44.5 s, resolve) dah betul, tetapi bunyi akhir akan diperhalusi dalam production.
- Sample peak −0.6 dBFS. Limiter true-peak −1 dBTP akan digunakan semasa mastering akhir.

## Jana semula
```bash
cd LOKADIGITAL/06_VIDEO_PROJECTS/EP02/PRODUCTION/animatic
python3 beatmap.py                                   # beatmap.json + ../BEAT_MAP_EP02.md
node render/render.js /tmp/ep02_frames 4             # 2,025 frame (≈65 s)
python3 audio/score_ep02.py /tmp/ep02_score.wav      # muzik + SFX
ffmpeg -framerate 30 -i /tmp/ep02_frames/f%05d.jpg -i /tmp/ep02_score.wav -c:v libx264 -crf 25 -pix_fmt yuv420p \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -shortest out/LOKADIGITAL_EP02_ANIMATIC_v1_1080x1920.mp4
```
Instrumen audio diguna semula daripada `ep01/audio/sound.py`. Font: Inter Display (sistem) dan JetBrains Mono (OFL, dalam `ASSETS/STYLE_FRAMES/src/fonts/`).
