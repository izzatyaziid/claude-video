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
NODE_ENV=production SITE_ORIGIN=https://domain-anda SITE_DRAFT=0 IP_HASH_SALT='<rentetan rawak 32+ aksara>' DATA_ENC_KEY='<64 aksara hex>' TRUST_PROXY=1 npm start
```
Lihat `../05_TECHNICAL_DEVELOPMENT/SECURITY_REVIEW.md` untuk senarai semak sebelum pelancaran.

## 2FA
Semua admin **wajib** aktifkan 2FA pada log masuk pertama (Akaun saya, kemudian imbas QR dengan Google Authenticator, Microsoft Authenticator atau Authy). Simpan 10 kod pemulihan. Jika Owner tunggal hilang telefon dan kod pemulihan:
```bash
ADMIN_EMAIL=anda@domain.my ADMIN_PASSWORD='KataLaluanBaru-123!' ADMIN_RESET_2FA=1 npm run create-admin
```

## Dashboard
- **Ringkasan:** pertanyaan baru, medan TBC, kesempurnaan kandungan.
- **Pertanyaan:** borang hubungi, dengan status baru / dibaca / arkib.
- **Jenama:** register LCV-01…06 (fungsi, status fakta, warna, pautan).
- **Kandungan:** semua teks laman, dengan status Disahkan / Cadangan / TBC.
- **Berita:** tulis dan terbitkan berita.
- **Pengguna admin** dan **Log audit** (Owner sahaja), **Akaun saya** (tukar kata laluan).
