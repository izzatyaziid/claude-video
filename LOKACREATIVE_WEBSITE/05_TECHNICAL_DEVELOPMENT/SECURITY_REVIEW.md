# Security Review — draf website & admin dashboard
> Tarikh: **2026-11-25** · Skop: kod dalam `LOKACREATIVE_WEBSITE/site/` · Status: **draf, belum dideploy**

## Ringkasan
| Perkara | Keputusan |
|---|---|
| Ujian keselamatan automatik (`npm test`) | **42 / 42 lulus** |
| `npm audit` (3 dependency terus: express, helmet, express-rate-limit) | **0 kelemahan** |
| Ralat CSP dalam pelayar (Playwright, desktop + mudah alih) | Tiada |

## Kawalan yang dilaksanakan
| Ancaman (OWASP) | Kawalan | Diuji |
|---|---|---|
| Broken access control (A01) | Peranan **Owner / Editor**; urusan admin, log audit dan padam pertanyaan hanya untuk Owner; Owner tidak boleh nyahaktif diri sendiri | ✅ |
| Cryptographic failures (A02) | Kata laluan **scrypt** (N=16384) + salt; ID sesi disimpan sebagai **SHA-256** (cookie dicuri dari DB tidak boleh diguna semula); IP pelawat di-hash dengan salt (PDPA) | ✅ |
| Injection (A03) | Semua SQL guna **parameterised statements**; slug, warna dan URL divalidasi ketat | ✅ |
| XSS (A03) | Semua output server melalui `esc()`; dashboard guna `textContent` sahaja; **CSP tanpa `unsafe-inline`**; isi berita ialah teks biasa | ✅ |
| CSRF | Token CSRF per-sesi (header `X-CSRF-Token`, perbandingan timing-safe) + semakan **Origin** + API hanya terima JSON + cookie `SameSite=Strict` | ✅ |
| Auth failures (A07) | Had kadar login (10 / 15 min / IP); **akaun dikunci 15 min** selepas 5 gagal; mesej ralat generik (tiada user enumeration); masa respons seragam (hash dummy); sesi baru setiap login (anti session-fixation); tamat sesi 30 min idle / 8 jam maksimum; tukar kata laluan menamatkan sesi lain | ✅ |
| Security misconfiguration (A05) | Helmet: CSP, `frame-ancestors 'none'` (anti-clickjacking), `nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS (production), tiada `X-Powered-By`; `noindex` dalam mod draf; konfigurasi production wajib (`SITE_ORIGIN`, `IP_HASH_SALT`) atau server enggan mula | ✅ |
| Logging (A09) | Log audit: login, gagal login, kunci akaun, semua perubahan kandungan dan akaun | ✅ |
| Spam / abuse | Borang hubungi: honeypot, had 5 / jam / IP, had saiz badan 10 KB, validasi server | ✅ |
| Cookie | `HttpOnly`, `SameSite=Strict`, `Secure` + awalan `__Host-` dalam production | ✅ |
| Default credentials | **Tiada** kata laluan lalai. Admin dicipta melalui `npm run create-admin` dengan polisi kata laluan (12+ aksara, 3 jenis) | ✅ |

## Risiko baki & tindakan sebelum production
| # | Perkara | Tindakan |
|---|---|---|
| R1 | Tiada **2FA** untuk admin | CADANGAN: tambah TOTP sebelum pelancaran awam |
| R2 | `node:sqlite` masih *experimental* dalam Node 22 | Kunci versi Node; backup DB harian; pertimbang Postgres jika trafik tinggi |
| R3 | Had kadar disimpan dalam memori (reset bila restart, tidak dikongsi antara instance) | Cukup untuk satu instance. Guna store kongsi jika berbilang server |
| R4 | Tiada notifikasi emel bila pertanyaan baru masuk | Integrasi emel transaksi (TBC servis) |
| R5 | Dasar privasi ialah **templat draf** | Wajib disemak penasihat undang-undang (PDPA 2010) |
| R6 | HTTPS & domain | Deploy di belakang TLS; tetapkan `NODE_ENV=production`, `SITE_ORIGIN`, `IP_HASH_SALT`, `TRUST_PROXY=1` jika di belakang proxy |
| R7 | Tiada polisi retensi data pertanyaan | Putuskan tempoh simpanan (contoh 12 bulan) dan padam berkala |

## Cara ulang semakan
```bash
cd LOKACREATIVE_WEBSITE/site && npm install && npm test && npm audit
```
