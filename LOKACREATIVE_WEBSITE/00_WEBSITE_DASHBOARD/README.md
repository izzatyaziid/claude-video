# 🌐 LOKACREATIVE_WEBSITE — Website Dashboard
> Corporate Website Planning & Documentation · **single source of truth**
> Kemas kini terakhir: **2026-11-25** · Branch kerja: `claude/optimistic-heisenberg-8mmyaf`
> **Peraturan:** tiada fakta rekaan. `TBC` = belum disahkan. **CADANGAN** = perlu approval.

## 🎯 Tujuan
Merancang website korporat **LokaCreative Ventures**, syarikat induk kepada **LokaDigital, LokaFoodie, LokaDaily, LokaTalent, LokaCommerce dan Loka Brands**. Website ini mempunyai **positioning corporate group** yang berbeza daripada website agency LokaDigital.

## 🚦 Status semasa
**Fasa: 1 — Draf website + admin dashboard dibina untuk semakan (W05).** 🔴 **Belum publish atau deploy.**

| Bahagian | Status |
|---|---|
| 01 Brand & business | 🟥 Kebanyakan TBC: perlukan input kau |
| 02 Strategi | 🟨 Cadangan sedia, menunggu keputusan |
| 03 Design & UI/UX | 🟨 Draf ikut identiti deck Canva pemilik (hitam #171717, lime #D6FF3F). Font rasmi TBC |
| 04 Kandungan | 🟥 Struktur sahaja; teks bergantung pada maklumat TBC |
| 05 Teknikal | 🟨 Draf: Node.js + Express + SQLite, admin dashboard, 51/51 ujian keselamatan lulus, 2FA wajib ([`SECURITY_REVIEW.md`](../05_TECHNICAL_DEVELOPMENT/SECURITY_REVIEW.md)) |
| 08 Rujukan | 🟩 Audit bestfood.my siap ([`REF-W01`](../08_REFERENCES/REF-W01_BESTFOOD_AUDIT.md)) |
| 07 Aset | 🟥 Tiada logo / foto lagi |

**Fasa seterusnya (selepas approval):** 1) kunci strategi & sitemap → 2) design direction → 3) kandungan → 4) wireframe → 5) build (preview) → 6) review → 7) deploy.

## 🆕 Kemas kini terkini
- **2026-11-25 (W07):** Semua logo diganti dengan fail yang dibekalkan pemilik (LokaCreative, LokaDigital, LokaFoodie, LokaDaily, **Lokatrication**). Hanya jenama yang ada logo dipaparkan; LokaTalent, LokaCommerce, Loka Brands disembunyikan buat masa ini. Fungsi LokaDaily & Lokatrication: TBC.
- **2026-11-25 (W06):** **2FA wajib** untuk semua admin (TOTP + kod pemulihan). Website ditukar kepada **identiti brand sebenar** dari deck Canva (hitam/lime) dengan logo LokaDigital dan LokaFoodie; identiti rekaan dibuang. 51/51 ujian lulus. ⚠️ 4 percanggahan perlu keputusan: [`BRAND_SOURCES.md`](../01_BRAND_AND_BUSINESS/BRAND_SOURCES.md).
- **2026-11-25 (W05):** Atas permintaan pemilik: audit rujukan bestfood.my, draf website dan admin dashboard (backend + frontend) dibina dalam [`site/`](../site/README.md) dengan semakan keselamatan. Semua fakta belum disahkan kekal TBC. Belum deploy.
- **2026-11-25:** Projek dimulakan. Struktur dokumentasi 00–07 dicipta dengan maklumat sedia ada dan TBC untuk semua yang belum disahkan.

## ✋ Keputusan & maklumat diperlukan daripada kau
**Percanggahan brand (baru, W06)**
0. Deck Canva sebut LokaCreative ialah *digital marketing agency*, tapi W02 kata *corporate group*. Mana satu? Emel rasmi kumpulan? ([`BRAND_SOURCES.md`](../01_BRAND_AND_BUSINESS/BRAND_SOURCES.md))

**Perniagaan (paling penting: ia menentukan semua yang lain)**
1. Fungsi ringkas (1 ayat) untuk **LokaFoodie, LokaDaily, LokaTalent, LokaCommerce, Loka Brands**.
2. Struktur: setiap jenama ialah subsidiari, divisyen atau jenama dagangan? Jenama mana dipaparkan semasa pelancaran?
3. Profil syarikat: nama entiti berdaftar, tahun, pengasas/kepimpinan, lokasi, visi & misi (jika ada).
4. Objektif utama website ([`WEBSITE_OBJECTIVES.md`](../02_WEBSITE_STRATEGY/WEBSITE_OBJECTIVES.md), O1–O5) dan CTA utama.

**Brand & design**
5. Logo LokaCreative Ventures dan logo setiap jenama (fail).
6. Arah reka bentuk: A Neutral corporate · B Dark premium · C Masterbrand system ([`DESIGN_DIRECTION.md`](../03_DESIGN_AND_UI_UX/DESIGN_DIRECTION.md)).

**Teknikal & operasi**
7. Domain (dan siapa pemegang akaun DNS).
8. Siapa akan kemas kini kandungan selepas pelancaran (menentukan tech stack).
9. Bahasa: BM, EN atau dwibahasa.
10. Emel / telefon / alamat rasmi dan penerima pertanyaan borang.

## 📋 Tugasan tertunda
- [ ] Terima jawapan 1–10 di atas
- [ ] Kunci objektif, audiens, positioning, sitemap
- [ ] Pilih design direction → colour & typography
- [ ] Tulis kandungan setiap halaman
- [ ] Pilih tech stack → architecture final
- [ ] Kumpul aset (logo, foto)

## ⏭️ Langkah seterusnya
Bila kau beri maklumat perniagaan (1–4), aku kemas kini semua dokumen berkaitan, tukar TBC kepada fakta yang disahkan, dan cadangkan sitemap + kandungan Home versi pertama untuk approval.

## 📚 Semua dokumentasi
| # | Bahagian | Dokumen |
|---|---|---|
| 01 | Brand & business | [`BRAND_GUIDELINES.md`](../01_BRAND_AND_BUSINESS/BRAND_GUIDELINES.md) · [`COMPANY_PROFILE.md`](../01_BRAND_AND_BUSINESS/COMPANY_PROFILE.md) · [`BUSINESS_STRUCTURE.md`](../01_BRAND_AND_BUSINESS/BUSINESS_STRUCTURE.md) |
| 02 | Strategi | [`WEBSITE_OBJECTIVES.md`](../02_WEBSITE_STRATEGY/WEBSITE_OBJECTIVES.md) · [`TARGET_AUDIENCE.md`](../02_WEBSITE_STRATEGY/TARGET_AUDIENCE.md) · [`WEBSITE_POSITIONING.md`](../02_WEBSITE_STRATEGY/WEBSITE_POSITIONING.md) · [`SITEMAP.md`](../02_WEBSITE_STRATEGY/SITEMAP.md) |
| 03 | Design & UI/UX | [`DESIGN_DIRECTION.md`](../03_DESIGN_AND_UI_UX/DESIGN_DIRECTION.md) · [`COLOUR_TYPOGRAPHY.md`](../03_DESIGN_AND_UI_UX/COLOUR_TYPOGRAPHY.md) · [`UI_UX_GUIDELINES.md`](../03_DESIGN_AND_UI_UX/UI_UX_GUIDELINES.md) |
| 04 | Kandungan | [`HOMEPAGE.md`](../04_WEBSITE_CONTENT/HOMEPAGE.md) · [`ABOUT_US.md`](../04_WEBSITE_CONTENT/ABOUT_US.md) · [`OUR_BRANDS.md`](../04_WEBSITE_CONTENT/OUR_BRANDS.md) · [`OUR_SERVICES.md`](../04_WEBSITE_CONTENT/OUR_SERVICES.md) · [`CONTACT.md`](../04_WEBSITE_CONTENT/CONTACT.md) |
| 05 | Teknikal | [`TECH_STACK.md`](../05_TECHNICAL_DEVELOPMENT/TECH_STACK.md) · [`WEBSITE_ARCHITECTURE.md`](../05_TECHNICAL_DEVELOPMENT/WEBSITE_ARCHITECTURE.md) · [`SEO_STRATEGY.md`](../05_TECHNICAL_DEVELOPMENT/SEO_STRATEGY.md) · [`INTEGRATIONS.md`](../05_TECHNICAL_DEVELOPMENT/INTEGRATIONS.md) |
| 06 | Log & keputusan | [`PROJECT_LOG.md`](../06_PROJECT_PROGRESS/PROJECT_LOG.md) (W01–W04) |
| 07 | Aset | [`ASSET_LIBRARY.md`](../07_ASSETS/ASSET_LIBRARY.md) |
| 08 | Rujukan | [`REF-W01_BESTFOOD_AUDIT.md`](../08_REFERENCES/REF-W01_BESTFOOD_AUDIT.md) |
| — | Kod draf | [`site/README.md`](../site/README.md) · [`SECURITY_REVIEW.md`](../05_TECHNICAL_DEVELOPMENT/SECURITY_REVIEW.md) |
| — | Projek berkaitan | [LOKADIGITAL dashboard](../../LOKADIGITAL/00_PROJECT_DASHBOARD/README.md) (identiti & video LokaDigital) |
