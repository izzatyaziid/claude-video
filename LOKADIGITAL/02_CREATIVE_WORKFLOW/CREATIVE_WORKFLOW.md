# LOKADIGITAL — Creative Workflow (standard siri)

> Terpakai secara automatik untuk setiap video LokaDigital. Dikemas kini setiap kali ada keputusan baharu (lihat [`CREATIVE_DECISIONS.md`](../04_CREATIVE_DECISIONS/CREATIVE_DECISIONS.md)).
> Versi semasa: **2026-11-25 · Visual-first, tanpa voiceover.**

## Aliran
```
Reference Analysis → Creative Concept → On-screen Text Script → Storyboard → ✋ APPROVAL → Production → Final Review
```
**Peraturan tetap:** tiada edit, render atau generate video sebelum concept, text script dan storyboard **diluluskan secara eksplisit**.

**Sebelum bertanya apa-apa:** semak [`CREATIVE_DECISIONS.md`](../04_CREATIVE_DECISIONS/CREATIVE_DECISIONS.md). Keputusan yang dah direkod **tidak ditanya semula**. Tanya hanya jika maklumat baharu benar-benar diperlukan; jika tidak, guna keputusan sedia ada dan teruskan.

## 1. Reference Analysis
- Dapatkan video sebenar. Jika link tak boleh diakses (contoh: Instagram disekat), minta fail di-upload. Jangan sesekali analisa berdasarkan tekaan.
- Ukur, jangan agak: scene-detect untuk cut, contact sheet 2 fps, hook pada 4 fps, loudness (LUFS) dan imbangan spektrum audio.
- Pecahkan: struktur & flow, hook 3 s, kamera, komposisi, transition, pace, typography & motion gfx, VFX, bunyi, dan **kenapa nampak premium**.
- Terangkan *pemikiran* di sebalik setiap pilihan, bukan sekadar apa yang berlaku.
- Hasilkan jadual **Ambil (prinsip) vs Tidak ambil (identiti mereka)**. Jangan tiru skrip, shot, rupa atau aset.

## 2. Creative Concept
Premis, big idea visual, objective, peta teknik reference → LokaDigital, visual world, sistem typography.
- Tiada angka, hasil atau case study rekaan. Gunakan situasi bisnes yang realistik. Contoh ilustrasi dilabel `CONTOH`.

## 3. On-screen Text Script (`SCRIPT/VISUAL_STORYTELLING_EPxx.md`)
Menggantikan skrip VO. Untuk setiap ayat: masa, teks, suara tipografi (NOISE / SIGNAL / SYSTEM), gerak, visual, dan cue muzik/SFX. Ia perlu ikut peraturan copy dalam [`EDITING_STANDARDS.md`](EDITING_STANDARDS.md).

## 4. Storyboard
Scene demi scene: tujuan cerita, visual, teks, kamera, motion gfx, transition, bunyi. Setiap scene mesti menyambung cerita.

## ✋ 5. Approval
Bentangkan dokumen di atas. Senaraikan hanya soalan yang benar-benar baharu (bukan yang sudah ada dalam CREATIVE_DECISIONS). Tunggu kelulusan.

## 6. Production (selepas approval sahaja)
1. **Beat map:** tetapkan tempo, dan snap semua cue ke beat grid.
2. **Animatic:** low-fi, dengan teks dan timing penuh. Semak masa bacaan dan rentak.
3. **Render:** visual penuh (pipeline HTML/Canvas → Playwright → ffmpeg, seperti EP01).
4. **Sound design & mix:** muzik + SFX sahaja. −14 LUFS, true peak ≤ −1 dBTP. Simpan stems.
5. **QC:** ujian kefahaman mute, masa bacaan, zon selamat UI, kod warna, loudness, encode (H.264/AAC, 1080×1920, 30 fps).

## 7. Final Review
Hantar master + thumbnail + QC report. Kemas kini [`PROJECT_LOG.md`](../05_PROJECT_LOG/PROJECT_LOG.md) dan [dashboard](../00_PROJECT_DASHBOARD/README.md).

## Struktur fail per episod
```
LOKADIGITAL/06_VIDEO_PROJECTS/EPxx/
├── README.md                          status episod
├── CONCEPT/CONCEPT_EPxx.md            premis, big idea, visual world, typography, bunyi
├── SCRIPT/VISUAL_STORYTELLING_EPxx.md skrip teks di skrin + cue sheet muzik/SFX
├── STORYBOARD/STORYBOARD_EPxx.md      scene demi scene + "Faham tanpa suara"
├── ASSETS/                            muzik, SFX, font, imej (atau ASSET_LIST.md)
├── PRODUCTION/                        kod render, beat map, animatic
└── FINAL_OUTPUT/                      master, thumbnail, QC_REPORT_EPxx.md
```
Analisa reference disimpan dalam [`REFERENCE_LIBRARY.md`](../03_REFERENCE_LIBRARY/REFERENCE_LIBRARY.md) (satu ID setiap reference, contoh REF-001), bukan dalam folder episod.
Pengecualian sejarah: kod & master EP01 kekal di `ep01/` (root repo) kerana `ep01/build.sh` dan branch default bergantung padanya.

