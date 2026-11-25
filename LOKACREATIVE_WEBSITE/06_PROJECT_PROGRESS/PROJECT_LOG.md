# LOKACREATIVE_WEBSITE — Project Log

| Tarikh | Peristiwa | Rujukan |
|---|---|---|
| 2026-11-25 | Projek dimulakan sebagai **dokumentasi & perancangan sahaja**. Struktur 00–07 dicipta. Fakta yang diketahui: LokaCreative Ventures ialah syarikat induk; ekosistem LokaDigital, LokaFoodie, LokaDaily, LokaTalent, LokaCommerce, Loka Brands; positioning corporate group mesti berbeza daripada website agency LokaDigital. Semua maklumat lain = TBC. Tiada build / publish / deploy | [Dashboard](../00_WEBSITE_DASHBOARD/README.md) |
| 2026-11-25 | Audit pasif bestfood.my sebagai rujukan (REF-W01). Draf website + admin dashboard dibina dalam `site/`; 42/42 ujian keselamatan lulus, `npm audit` 0 kelemahan. Belum deploy | [REF-W01](../08_REFERENCES/REF-W01_BESTFOOD_AUDIT.md) · [Security](../05_TECHNICAL_DEVELOPMENT/SECURITY_REVIEW.md) |
| 2026-11-25 | 2FA (TOTP) wajib untuk admin. Identiti brand diambil dari Canva pemilik (deck LokaCreative, logo LokaDigital & LokaFoodie, rate card LokaFoodie); palet dan elemen rekaan dibuang. 51/51 ujian lulus | [BRAND_SOURCES](../01_BRAND_AND_BUSINESS/BRAND_SOURCES.md) |

## Keputusan direkod
| # | Tarikh | Keputusan |
|---|---|---|
| W01 | 2026-11-25 | LokaCreative Ventures = mother company. Ekosistem: LokaDigital, LokaFoodie, LokaDaily, LokaTalent, LokaCommerce, Loka Brands |
| W02 | 2026-11-25 | Website = positioning **corporate group**, berbeza daripada website agency LokaDigital |
| W03 | 2026-11-25 | Tiada fakta / angka / revenue / klien / pencapaian rekaan. Guna `TBC` |
| W04 | 2026-11-25 | Dokumentasi & perancangan dahulu. **Jangan build, publish atau deploy** tanpa approval |
| W05 | 2026-11-25 | Pemilik minta draf website + admin dashboard (backend & frontend) dengan semakan keselamatan. Dibina sebagai **draf untuk semakan**; deploy masih perlukan approval (W04 kekal untuk publish/deploy) |
| W06 | 2026-11-25 | Pemilik: tambah 2FA, dan guna logo & identiti brand sedia ada sahaja (tiada identiti rekaan). Sumber rasmi: Canva pemilik |
