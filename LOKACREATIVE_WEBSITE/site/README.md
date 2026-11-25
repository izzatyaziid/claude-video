# LokaCreative Ventures — website (draf) + admin dashboard

Status: **DRAF untuk semakan. Belum dideploy.** Mod draf memaparkan penanda TBC / CADANGAN dan menyekat enjin carian.

## Struktur
| Laluan | Isi |
|---|---|
| `src/server.js` | Express app, header keselamatan |
| `src/routes/public.js` | Laman awam: `/`, `/about`, `/brands`, `/brands/:slug`, `/news`, `/news/:slug`, `/contact`, `/privacy` |
| `src/routes/admin-api.js` | API admin JSON di `/admin/api/*` |
| `src/views.js` | Templat HTML (server-rendered, semua output di-escape) |
| `src/db.js` | Skema SQLite + seed (fakta yang disahkan sahaja) |
| `public/admin/` | Frontend dashboard di `/admin` |
| `test/security.test.js` | 42 ujian keselamatan & fungsi |

## Jalankan (development)
Perlu Node.js 22.13 atau lebih baru.
```bash
npm install
ADMIN_EMAIL=anda@domain.my ADMIN_NAME="Nama" ADMIN_PASSWORD='KataLaluan-Kuat-123!' npm run create-admin
npm start
```
Laman awam: http://localhost:3000 · Dashboard: http://localhost:3000/admin

## Production (selepas kelulusan sahaja)
```bash
NODE_ENV=production SITE_ORIGIN=https://domain-anda SITE_DRAFT=0 IP_HASH_SALT='<rentetan rawak 32+ aksara>' TRUST_PROXY=1 npm start
```
Lihat `../05_TECHNICAL_DEVELOPMENT/SECURITY_REVIEW.md` untuk senarai semak sebelum pelancaran.

## Dashboard
- **Ringkasan:** pertanyaan baru, medan TBC, kesempurnaan kandungan.
- **Pertanyaan:** borang hubungi, dengan status baru / dibaca / arkib.
- **Jenama:** register LCV-01…06 (fungsi, status fakta, warna, pautan).
- **Kandungan:** semua teks laman, dengan status Disahkan / Cadangan / TBC.
- **Berita:** tulis dan terbitkan berita.
- **Pengguna admin** dan **Log audit** (Owner sahaja), **Akaun saya** (tukar kata laluan).
