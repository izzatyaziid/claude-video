# LOKADIGITAL — Creative Workflow (standard siri)

> Terpakai secara automatik untuk setiap video LokaDigital. Dikemas kini setiap kali ada keputusan baharu (lihat [`CREATIVE_DECISIONS.md`](CREATIVE_DECISIONS.md)).
> Versi semasa: **2026-11-25 · Visual-first, tanpa voiceover.**

## Aliran
```
Reference Analysis → Creative Concept → On-screen Text Script → Storyboard → ✋ APPROVAL → Production → Final Review
```
**Peraturan tetap:** tiada edit, render atau generate video sebelum concept, text script dan storyboard **diluluskan secara eksplisit**.

## 1. Reference Analysis
- Dapatkan video sebenar. Jika link tak boleh diakses (contoh: Instagram disekat), minta fail di-upload. Jangan sesekali analisa berdasarkan tekaan.
- Ukur, jangan agak: scene-detect untuk cut, contact sheet 2 fps, hook pada 4 fps, loudness (LUFS) dan imbangan spektrum audio.
- Pecahkan: struktur & flow, hook 3 s, kamera, komposisi, transition, pace, typography & motion gfx, VFX, bunyi, dan **kenapa nampak premium**.
- Terangkan *pemikiran* di sebalik setiap pilihan, bukan sekadar apa yang berlaku.
- Hasilkan jadual **Ambil (prinsip) vs Tidak ambil (identiti mereka)**. Jangan tiru skrip, shot, rupa atau aset.

## 2. Creative Concept
Premis, big idea visual, objective, peta teknik reference → LokaDigital, visual world, sistem typography.
- Tiada angka, hasil atau case study rekaan. Gunakan situasi bisnes yang realistik. Contoh ilustrasi dilabel `CONTOH`.

## 3. On-screen Text Script (`VISUAL_STORYTELLING.md`)
Menggantikan skrip VO. Untuk setiap ayat: masa, teks, suara tipografi (NOISE / SIGNAL / SYSTEM), gerak, visual, dan cue muzik/SFX. Ia perlu ikut peraturan copy dalam [`EDITING_STANDARDS.md`](EDITING_STANDARDS.md).

## 4. Storyboard
Scene demi scene: tujuan cerita, visual, teks, kamera, motion gfx, transition, bunyi. Setiap scene mesti menyambung cerita.

## ✋ 5. Approval
Bentangkan 2–4 dokumen di atas. Senaraikan soalan terbuka. Tunggu kelulusan.

## 6. Production (selepas approval sahaja)
1. **Beat map:** tetapkan tempo, dan snap semua cue ke beat grid.
2. **Animatic:** low-fi, dengan teks dan timing penuh. Semak masa bacaan dan rentak.
3. **Render:** visual penuh (pipeline HTML/Canvas → Playwright → ffmpeg, seperti EP01).
4. **Sound design & mix:** muzik + SFX sahaja. −14 LUFS, true peak ≤ −1 dBTP. Simpan stems.
5. **QC:** ujian kefahaman mute, masa bacaan, zon selamat UI, kod warna, loudness, encode (H.264/AAC, 1080×1920, 30 fps).

## 7. Final Review
Hantar master + thumbnail + QC report. Kemas kini [`PROJECT_LOG.md`](PROJECT_LOG.md).

## Struktur fail per episod
```
epXX/docs/CONCEPT_EPXX.md        konsep + analisa reference + storyboard
epXX/docs/VISUAL_STORYTELLING.md copy deck + cue sheet
epXX/docs/QC_REPORT.md           selepas production
epXX/out/                        master, thumbnail
```
