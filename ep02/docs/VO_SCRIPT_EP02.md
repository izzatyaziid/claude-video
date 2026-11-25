# LOKADIGITAL — EP02 "ORANG YANG BETUL" · VO Script (ElevenLabs-ready)

> Video master dihasilkan **tanpa VO** (super-led). Skrip ini ditimed kepada picture supaya VO boleh dimasukkan kemudian tanpa ubah edit.
> Jumlah: ~150 perkataan dalam ~60 s VO aktif (≈2.5 perkataan/saat). Video 65.0 s.

## Arahan suara (voice direction)
- **Watak:** strategist yang tenang dan yakin, bercakap dengan seorang pemilik bisnes, seperti di meja mesyuarat. Bukan iklan radio, bukan motivational speaker.
- **Suara:** register rendah-sederhana, hangat, jelas. Lelaki atau wanita (pilih satu dan kekalkan untuk seluruh siri).
- **Loghat:** Bahasa Melayu **Malaysia** (bukan Indonesia). Perkataan Inggeris (content, audience, ads, strategy, scroll) disebut natural, cara orang Malaysia bercakap.
- **Tempo:** perlahan dan berjeda. Jeda ialah sebahagian daripada persembahan.
- **Sebutan:** tulis "**Loka Digital**" (dua perkataan) dalam input ElevenLabs supaya sebutan betul: *LO-ka DI-ji-tal*.

## Cadangan setting ElevenLabs (titik mula, uji dan laras)
- Model: model multilingual yang menyokong Bahasa Melayu. Uji 2–3 suara dan dengar loghat Malaysia.
- Stability ~45–55 % (cukup ekspresif, tapi tak berubah-ubah antara baris).
- Similarity ~75 %. Style rendah (~0–20 %) supaya tak teater.
- Jana **setiap scene sebagai fail berasingan** (lebih mudah dilaras timing). Export WAV 48 kHz.
- Jeda: gunakan elipsis (…) atau tag break `<break time="0.6s" />` jika model yang digunakan menyokongnya.
- Nama fail: `EP02_VO_S01.wav` … `EP02_VO_S08.wav`.

## Skrip bertimer

| Scene | Masa VO | Baris VO | Nota persembahan | Super di skrin pada masa itu |
|---|---|---|---|---|
| **S01 Hook** | 0.4–1.9 | Ramai yang nampak. | Tenang, hampir berbisik. Jangan "jual". | RAMAI YANG NAMPAK. |
| | 1.9–2.5 | *(senyap)* | Freeze: jangan isi. | — |
| | 2.5–3.9 | Tak ramai yang beli. | Lebih rendah, berat. | Tak ramai yang beli. |
| | 3.9–5.4 | Masalahnya bukan berapa ramai. | Jelas, perlahan. | Masalahnya bukan berapa ramai. |
| | 5.4–6.5 | Tapi… siapa. | Jeda sebelum "siapa". "Siapa" turun nada, muktamad. | **SIAPA.** |
| **S02 Janji** | 6.7–8.9 | Jadi, kita mula dengan tiga langkah. | Nada "mari aku tunjuk". | 01 CARI · 02 CAKAP · 03 SAMBUNG |
| **S03 Cari** | 9.2–11.4 | Langkah satu: cari. Baca data dulu. | Jeda kecil selepas "cari". | 01 CARI · Baca data dulu. |
| | 11.6–16.4 | Apa masalah mereka. Apa yang mereka risau. Bila mereka bersedia untuk beli. | Tiga ketukan sama rata (ikut 3 label). | MASALAH · KERISAUAN · MASA BELI |
| | 16.6–21.8 | Bila pola tu jelas, audience kau bukan lagi semua orang. Tapi orang yang betul. | Tekan "orang yang betul". | ~~Semua orang.~~ **Orang yang betul.** |
| **S04 Cakap** | 22.2–24.8 | Langkah dua: cakap. | | 02 CAKAP |
| | 25.0–28.4 | Content yang cuba bercakap dengan semua orang… | Sedikit sinis. | Cakap dengan semua… |
| | 28.4–30.4 | …akhirnya tak didengar sesiapa. | Datar. | = tak didengar sesiapa. |
| | 30.6–34.0 | Tulis untuk satu orang. Sebut masalah dia, dalam bahasa dia. | Hangat, intim. | (rewrite) CONTOH |
| | 34.0–35.8 | Yang betul akan berhenti scroll. | Yakin. | Tulis untuk **satu orang.** |
| **S05 Sambung** | 36.2–39.4 | Langkah tiga: sambung. Uji dulu. | | 03 SAMBUNG · UJI |
| | 39.6–42.8 | Bila jumpa yang menjadi, baru besarkan dengan ads. | Tenaga naik sedikit. | JUMPA YANG MENJADI · BESARKAN |
| | 43.2–46.8 | Bukan untuk sampai ke lebih ramai orang. | | Bukan lebih ramai. |
| | 47.0–48.8 | Tapi lebih ramai orang yang betul. | Puncak emosi, tapi masih terkawal. | Lebih ramai **yang betul.** |
| **S06 Rumusan** | 49.4–51.4 | Cari. Cakap. Sambung. | Satu perkataan, satu jeda. | 3 baris rumusan |
| | 51.6–54.9 | Itu beza antara ramai yang nampak… dan ramai yang beli. | Jeda sebelum "dan". | …ramai yang **beli.** |
| **S07 Brand** | 55.4–59.6 | Loka Digital. Content dan ads strategy, berasaskan audience insight dan data. | Rendah, profesional. | LOKA**DIGITAL** · tagline |
| **S08 CTA** | 60.4–62.4 | Follow untuk episod seterusnya. | Santai, mesra. | FOLLOW · NEXT EP03 |
| | 62.4–65.0 | *(senyap)* | Biar loop bersih. | Cover frame |

## Teks bersih untuk copy-paste ke ElevenLabs (satu blok = satu fail)

**S01**
```
Ramai yang nampak. <break time="0.6s" /> Tak ramai yang beli. Masalahnya bukan berapa ramai. Tapi… siapa.
```
**S02**
```
Jadi, kita mula dengan tiga langkah.
```
**S03**
```
Langkah satu: cari. Baca data dulu. Apa masalah mereka. Apa yang mereka risau. Bila mereka bersedia untuk beli. Bila pola tu jelas, audience kau bukan lagi semua orang. Tapi orang yang betul.
```
**S04**
```
Langkah dua: cakap. Content yang cuba bercakap dengan semua orang… akhirnya tak didengar sesiapa. Tulis untuk satu orang. Sebut masalah dia, dalam bahasa dia. Yang betul akan berhenti scroll.
```
**S05**
```
Langkah tiga: sambung. Uji dulu. Bila jumpa yang menjadi, baru besarkan dengan ads. Bukan untuk sampai ke lebih ramai orang. Tapi lebih ramai orang yang betul.
```
**S06**
```
Cari. Cakap. Sambung. Itu beza antara ramai yang nampak… dan ramai yang beli.
```
**S07**
```
Loka Digital. Content dan ads strategy, berasaskan audience insight dan data.
```
**S08**
```
Follow untuk episod seterusnya.
```

## Selepas VO siap
1. Hantar 8 fail WAV kepada aku.
2. Aku align setiap baris kepada timing di atas. Jika VO lebih panjang ±0.3 s, aku laras hold shot, bukan laju VO.
3. Muzik di-duck ~−10 dB di bawah VO, SFX kekal. Master semula −14 LUFS.
4. Super kekal (video tetap berfungsi tanpa suara).
