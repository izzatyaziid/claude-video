# LOKA — Documentation & Production Repository

Repository ini mengandungi dua sistem dokumentasi (single source of truth) dan kod production video.

| Sistem | Tujuan | Dashboard |
|---|---|---|
| [`LOKADIGITAL/`](LOKADIGITAL/) | Creative & video production LokaDigital (siri video, brand, workflow, keputusan) | [📊 Project Dashboard](LOKADIGITAL/00_PROJECT_DASHBOARD/README.md) |
| [`LOKACREATIVE_WEBSITE/`](LOKACREATIVE_WEBSITE/) | Perancangan website korporat LokaCreative Ventures (syarikat induk) | [🌐 Website Dashboard](LOKACREATIVE_WEBSITE/00_WEBSITE_DASHBOARD/README.md) |

## Status ringkas
| Projek | Status |
|---|---|
| LokaDigital EP01 "SIGNAL / NOISE" | ✅ Siap: [`ep01/out/LOKADIGITAL_EP01_SignalNoise_1080x1920.mp4`](ep01/out/LOKADIGITAL_EP01_SignalNoise_1080x1920.mp4) |
| LokaDigital EP02 "ORANG YANG BETUL" | ✅ Style frames v2 · 🟡 Animatic v1 menunggu approval |
| LokaDigital EP03 "VIRAL IS NOT A STRATEGY" | 📝 Brief |
| LokaCreative Ventures website | 📝 Perancangan (tiada build / deploy) |

## Struktur
```
LOKADIGITAL/            dokumentasi creative & video LokaDigital
LOKACREATIVE_WEBSITE/   dokumentasi & perancangan website LokaCreative Ventures
ep01/                   kod production + master EP01 (build: ./ep01/build.sh)
```
`ep01/` kekal di root kerana `ep01/build.sh` dan branch default repo bergantung pada lokasinya. Dokumen EP01 kini dalam [`LOKADIGITAL/06_VIDEO_PROJECTS/EP01/`](LOKADIGITAL/06_VIDEO_PROJECTS/EP01/README.md).
