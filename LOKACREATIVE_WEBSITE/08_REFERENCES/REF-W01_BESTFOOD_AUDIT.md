# REF-W01 — Audit rujukan: bestfood.my
> Disemak: **2026-11-25** · Kaedah: **audit pasif sahaja**. Kami baca HTML awam laman utama, header HTTP dan `robots.txt`. Tiada login, tiada imbasan endpoint, tiada ujian penembusan: laman ini bukan milik kita.
> Tujuan: belajar struktur dan strategi untuk website **LokaCreative Ventures** tanpa meniru.

## 1. Ringkasan
| Perkara | Penemuan |
|---|---|
| Jenis laman | Website korporat syarikat **media food & lifestyle** yang menjual reach kepada jenama (B2B) |
| Platform | WordPress 7.1.5, tema custom `bestfood-theme`, plugin AIOSEO 4.9.10 dan plugin terjemahan |
| Hosting | Hostinger (hPanel), cache LiteSpeed, CDN `hcdn`, HTTP/2 + HTTP/3 |
| Bahasa | `en-GB` (Inggeris), dan ada nama channel Cina (吃玩大马) |
| Font | Bricolage Grotesque (display), Inter (body), Newsreader (serif) |
| Navigasi | Home · The Network · Work With Us · News · Contact Us · **WhatsApp Us** |

## 2. Struktur laman utama (mengikut susunan)
1. **Hero:** "We make brands stand out", subteks kategori, dan bukti segera (No. 1 di Instagram, 7M+ followers, sejak 2022). CTA: *Work with us* · *See the network*.
2. **Chip kategori:** Food, Travel & places, Home & living, Beauty, Consumer tech, FMCG & retail.
3. **About:** cerita penubuhan (2022), misi, siapa kami, dan apa yang kami buat untuk partner.
4. **Reach (angka):** No.1, 7M+, 500M monthly views, 20M monthly engagement.
5. **The Network:** *flagship* (Best Food Malaysia, dengan pecahan setiap platform) kemudian channel **bahasa**, **negeri**, **minat** dan **baharu**.
6. **Audience:** jantina, umur, minat.
7. **Servis untuk jenama:** Video, Photo, Social posting, Cross-posting. CTA: *Request a media kit & rates*.
8. **Campaigns that moved:** kerja contoh, iaitu embed reel IG/TikTok.
9. **Latest news:** 4 artikel.
10. **Logo wall:** "The brands Malaysians eat".
11. **CTA penutup:** "Let's make something Malaysia talks about" + sosial.

## 3. Apa yang patut kita pelajari (dan cara guna untuk LokaCreative)
| Teknik bestfood.my | Kenapa berkesan | Cara guna untuk LokaCreative |
|---|---|---|
| Model **flagship + network** | Pelawat faham hierarki dalam 5 saat | Halaman **Ekosistem**: LokaCreative di tengah, 6 jenama sebagai "register" dengan kod, status dan saluran |
| **Bukti di hero** | Kredibiliti sebelum scroll | Guna **hanya fakta disahkan**. Buat masa ini: "6 jenama · 1 kumpulan". Angka lain **TBC** dan disembunyikan sehingga disahkan |
| Laluan audiens jelas ("For brands & agencies") | Setiap pelawat tahu pintu mana nak masuk | Tiga pintu: **Rakan kongsi korporat · Jenama & klien · Talent** |
| Satu CTA dominan | Fokus kepada satu tindakan | "Bincang kerjasama", dengan borang yang direkod dalam dashboard |
| Seksyen berita | Tanda syarikat aktif | Seksyen **Berita**, diurus dari admin dashboard |
| Logo wall klien | Bukti sosial | **Hanya** dengan izin bertulis klien (peraturan W03) |

## 4. Kelemahan yang kami jumpa (jangan ulang)
| # | Isu | Bukti (pasif) | Kesan |
|---|---|---|---|
| K1 | **PHP 7.4.33 terdedah dalam header** `x-powered-by` | Header respons | PHP 7.4 tamat sokongan (EOL) pada **28 Nov 2022**, jadi tiada patch keselamatan lagi. Mendedahkan versi juga memudahkan penyerang |
| K2 | **Header keselamatan tiada:** HSTS, `X-Content-Type-Options`, `X-Frame-Options` / `frame-ancestors`, `Referrer-Policy` | Header respons | Risiko clickjacking dan MIME sniffing. CSP hanya `upgrade-insecure-requests` |
| K3 | Versi WordPress terdedah dalam `<meta name="generator">` | HTML | Memudahkan penyerang memadankan kelemahan |
| K4 | **Tiada borang pertanyaan**: hanya `mailto:` dan WhatsApp | HTML (0 `<form>`) | Lead tidak direkod atau diukur. Tiada pipeline |
| K5 | **Tiada pautan dasar privasi atau notis cookie** | HTML | Risiko pematuhan **PDPA 2010** bila data dikumpul (contohnya WhatsApp) |
| K6 | Tiada analitik dikesan dalam HTML | HTML | Mungkin tidak dapat mengukur prestasi CTA (mungkin juga dipasang di tempat lain; tidak disahkan) |
| K7 | H1 tercantum: "We make**brands** stand out" | HTML | Pembaca skrin dan SEO membaca "makebrands" |
| K8 | `<title>` dan OG ("Food Reviews & Hidden Gems") bercanggah dengan positioning B2B di hero | Meta | Mesej SEO dan perkongsian sosial tidak selari |
| K9 | "All stories →" dan "Press Release" memaut ke **satu artikel**, bukan indeks berita | HTML | Jalan mati dalam navigasi |
| K10 | 78 imej, **0 WebP/AVIF**, 46 lazy-load | HTML | Peluang prestasi (LCP) di mudah alih |
| K11 | Emoji sebagai ikon servis (🎬 📸 📣 🔁) | HTML | Kurang premium untuk positioning korporat |
| K12 | Angka besar (500M, 20M) **tanpa tarikh atau sumber** | Teks | Kredibiliti: rakan kongsi korporat mahu "setakat bila, sumber apa" |
| K13 | `sitemap.xml` tidak memulangkan entri `<loc>` semasa semakan kami | Fetch | **Perlu disahkan.** Mungkin format indeks lain. Kami tidak buat kesimpulan |

## 5. Apa yang website LokaCreative tambah baik (sudah dibina dalam draf)
| Kelemahan rujukan | Penyelesaian kita |
|---|---|
| K1–K3 | Node/Express tanpa header versi; header CSP ketat, HSTS (production), `frame-ancestors 'none'`, `nosniff`, `Referrer-Policy`, `Permissions-Policy` |
| K4 | Borang pertanyaan dengan pengesahan server, honeypot dan had kadar, direkod dalam **admin dashboard** |
| K5 | Halaman privasi (draf, perlu semakan undang-undang) dan kotak persetujuan PDPA pada borang. IP disimpan sebagai hash sahaja |
| K7–K9 | Satu H1 bersih setiap halaman; meta dan OG dari kandungan; indeks berita sebenar `/news` |
| K11 | Tiada emoji. Kod register (LCV-01…06) dan ikon geometri |
| K12 | Sistem status kandungan **confirmed / cadangan / TBC**. Tiada angka dipaparkan tanpa disahkan |

## 6. Yang masih kurang pada website kita (perlu input pemilik)
- Fungsi 5 jenama, profil syarikat, visi dan misi, logo, domain, bahasa: semuanya **TBC** (soalan 1–10 dalam dashboard).
- Angka atau bukti yang boleh disahkan, untuk menggantikan seksyen "Reach" bestfood.
- Gambar sebenar pasukan atau kerja (bestfood kuat sebab kandungan visual sebenar).
- Analitik pilihan (contohnya Plausible / GA4) dan semakan undang-undang dasar privasi.
