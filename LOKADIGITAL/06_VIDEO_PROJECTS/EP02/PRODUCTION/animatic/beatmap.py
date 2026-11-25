"""EP02 "ORANG YANG BETUL" — beat map (single source of timing).

Every cue time comes from storyboard v5 FINAL / VISUAL_STORYTELLING_EP02.md and is snapped to the
92 BPM half-beat grid (grid origin = 0.15 s, the hook impact). Outputs:
  beatmap.json                                  -> read by the animatic renderer and the score
  ../BEAT_MAP_EP02.md                           -> human-readable beat map
Usage: python3 beatmap.py
"""
import json, os

BPM = 92
BEAT = 60 / BPM            # 0.6522 s
HALF = BEAT / 2            # 0.3261 s
ORIGIN = 0.15              # bar 1, beat 1 = the hook impact
DUR = 67.5

def snap(t):
    return round(ORIGIN + round((t - ORIGIN) / HALF) * HALF, 3)

# ---- raw storyboard times (seconds) -------------------------------------------------------
RAW = {
    # S01 hook
    'impact': 0.15, 'chips': 0.5, 'beli_alone': 1.5, 'freeze': 2.1, 'push': 2.7, 'hero_form': 2.7,
    'line_masalah': 4.2, 'siapa': 5.8, 's02': 7.0,
    # S02 map
    'node_cari': 7.3, 'node_cakap': 7.75, 'node_sambung': 8.2, 'rail_lock': 8.6,
    # S03 CARI
    's03': 9.0, 'baca_data': 10.4, 'hud_research': 10.6, 'q1': 12.4, 'q2': 13.8, 'q3': 15.2,
    'cluster': 16.6, 'semua_orang': 18.6, 'strike1': 19.8, 'orang_betul': 20.1, 'to_rail1': 21.6,
    # S04 CAKAP
    's04': 22.3, 'ad_shout': 23.6, 'diri_sendiri': 25.8, 'tiada_peduli': 27.4, 'strike2': 28.9,
    'type1': 29.3, 'type2': 30.1, 'masalah_dia': 33.6, 'to_rail2': 35.7,
    # S05 SAMBUNG
    's05': 36.0, 'uji': 37.4, 'branch_die1': 38.8, 'branch_die2': 39.3, 'menjadi': 39.8,
    'besarkan': 41.2, 'bukan_ramai': 43.0, 'drop': 44.4, 'yang_betul': 46.6, 'sweep': 49.0,
    # S06 recap
    's06': 49.0, 'ramai_nampak': 51.0, 'morph': 52.4, 'cari_beli': 52.9,
    # S07 brand
    's07': 55.0, 'tagline': 56.2,
    # S08 CTA
    's08': 58.1, 'dm': 59.8, 'follow_save': 60.6, 'next': 62.4, 'cover': 64.8, 'fade_out': 66.7, 'end': 67.5,
}
# Deliberate adjustments (beyond grid snapping) so every line meets the reading-time rule.
ADJ = {
    'line_masalah': (4.25, 'Tak ramai yang beli. perlu 1.6 s'),
    'siapa': (6.0, 'Masalahnya bukan berapa ramai. perlu 1.6 s'),
    's02': (7.6, 'SIAPA. (kuning) perlu 1.5 s; hook jadi 7.5 s, S02 dipendekkan ke 1.3 s (cukup untuk 3 perkataan)'),
    'node_cari': (7.7, 'ikut S02 baharu'), 'node_cakap': (7.95, 'ikut S02 baharu'), 'node_sambung': (8.25, 'ikut S02 baharu'),
    'strike1': (19.9, 'Semua orang. perlu 1.0 s'), 'orang_betul': (20.3, 'ikut strike1'),
    'masalah_dia': (33.5, 'Cakap pasal masalah dia. perlu 2.1 s (ayat F&B masih 3.26 s)'),
    'bukan_ramai': (43.2, 'BESARKAN DENGAN ADS. perlu 1.8 s'),
    'next': (62.38, 'NEXT perlu 2.4 s; DM kekal ≈2.6 s (K3). Transition visual, tidak disnap'),
    'cover': (64.8, 'cover perlu 2.7 s. Transition visual, tidak disnap'),
}
FIXED = {'end', 's06', 'next', 'cover'}   # 's06' == 'sweep'; end is the file length
SRC = {k: (ADJ[k][0] if k in ADJ else v) for k, v in RAW.items()}
EV = {k: (v if k in FIXED else snap(v)) for k, v in SRC.items()}
EV['s06'] = EV['sweep']

# ---- on-screen text cues (for reading-time QC) ------------------------------------------
# (start_event, end_event, text, words, has_yellow)
TEXT = [
    ('impact', 'freeze', 'RAMAI YANG NAMPAK.', 3, False),
    ('push', 'line_masalah', 'Tak ramai yang beli.', 4, False),
    ('line_masalah', 'siapa', 'Masalahnya bukan berapa ramai.', 4, False),
    ('siapa', 's02', 'SIAPA.', 1, True),
    ('s02', 's03', 'CARI · CAKAP · SAMBUNG', 3, False),
    ('baca_data', 'q1', 'Baca data dulu.', 3, True),
    ('q1', 'q2', 'APA MASALAH DIA?', 3, False),
    ('q2', 'q3', 'APA DIA RISAU?', 3, False),
    ('q3', 'cluster', 'BILA DIA BELI?', 3, False),
    ('cluster', 'semua_orang', 'CONTOH · PEMILIK F&B · RESTORAN · CAFE', 5, False),
    ('semua_orang', 'strike1', 'Semua orang.', 2, False),
    ('orang_betul', 's04', 'Orang yang betul.', 3, True),
    ('ad_shout', 'diri_sendiri', 'KAMI YANG TERBAIK! HUBUNGI KAMI SEKARANG!', 6, False),
    ('diri_sendiri', 'tiada_peduli', 'Cakap pasal diri sendiri…', 4, False),
    ('tiada_peduli', 'strike2', '…tiada siapa peduli.', 3, False),
    ('type2', 'masalah_dia', '"Post content setiap hari, / tapi pelanggan tetap tak datang?" (selepas lengkap)', 9, False),
    ('masalah_dia', 'to_rail2', 'Cakap pasal masalah dia.', 4, True),
    ('menjadi', 'besarkan', 'YANG MENJADI', 2, False),
    ('besarkan', 'bukan_ramai', 'BESARKAN DENGAN ADS.', 3, True),
    ('bukan_ramai', 'drop', 'Bukan lebih ramai.', 3, False),
    ('yang_betul', 'sweep', 'Lebih ramai yang betul.', 4, True),
    ('s06', 'ramai_nampak', 'CARI. CAKAP. SAMBUNG.', 3, False),
    ('ramai_nampak', 'morph', 'Ramai yang nampak.', 3, False),
    ('cari_beli', 's07', 'Cari yang beli.', 3, True),
    ('tagline', 's08', 'CONTENT & ADS STRATEGY · DATA-LED', 5, False),
    ('s08', 'dm', 'Nak orang yang betul?', 4, False),
    ('dm', 'next', 'DM LOKADIGITAL', 2, True),
    ('next', 'cover', 'NEXT · EP03 — Viral is not a strategy.', 5, True),
    ('cover', 'end', 'Ramai nampak. Kenapa tak ramai beli?', 6, True),
]

def need(words, yellow):
    return max(1.0, 0.4 + 0.3 * words) + (0.5 if yellow else 0)

# ---- beats (human-readable beat map) ------------------------------------------------------
# keys: id, start(event), end(event), scene, action, cam, type, part, line, audio, trans
B = []
def beat(i, s, e, scene, action, cam, typ, part, line, audio, trans):
    B.append(dict(id=i, start=s, end=e, scene=scene, action=action, cam=cam, type=typ, part=part, line=line, audio=audio, trans=trans))

S1, S2, S3, S4, S5, S6, S7, S8 = ('S01 HOOK', 'S02 PETA', 'S03 CARI', 'S04 CAKAP', 'S05 SAMBUNG', 'S06 RUMUSAN', 'S07 BRAND', 'S08 CTA')
beat('B01', None, 'impact', S1, 'Frame 0: titik kuning berdenyut di depan lautan samar (tiada frame hitam)', 'Statik, drift 0.2 %', '—', 'Lautan lavender samar, drift perlahan', 'Titik kuning berdenyut (signal)', 'Sub drone D1 masuk', 'Potong terus ke ledakan')
beat('B02', 'impact', 'chips', S1, 'LEDAKAN: zarah-manusia meletup dari titik pusat ke kedudukan masing-masing', 'Shake halus 0.4 s + punch-in 4 %', 'NOISE slam "RAMAI YANG NAMPAK." (skala 1.25→1, expo-out)', 'Semua titik terbang keluar dari pusat (expo-out 1.2 s)', 'Titik kekal di pusat', 'IMPACT + boom + swell (downbeat bar 1)', '—')
beat('B03', 'chips', 'beli_alone', S1, 'Chip VIEW · LIKE · KLIK · SHARE pop di celah orang ramai', 'Drift', 'Chip mono pop (scale 0.6→1)', 'Orang ramai bernafas (micro-drift)', '—', 'Tick setiap chip (1/8 beat)', '—')
beat('B04', 'beli_alone', 'freeze', S1, 'Chip lain hilang; BELI sendirian di tengah, berkelip, MATI', 'Statik', 'Chip BELI flicker 3× lalu padam', '—', '—', 'Klik "mati" kering', 'Hard cut ke freeze')
beat('B05', 'freeze', 'push', S1, 'FREEZE: semua berhenti, warna jadi kelabu', 'Statik total', 'Semua teks hilang', 'Beku, desaturate ke kelabu', '—', 'SENYAP TOTAL 0.6 s', '—')
beat('B06', 'push', 'line_masalah', S1, 'Dolly-in menembus orang ramai; satu zarah dekat terbentuk jadi SILUET MANUSIA (benchmark SF1)', 'Dolly-in perlahan (expo-in), rack focus ke siluet', 'SIGNAL "Tak ramai yang beli." masked rise', 'Titik berkumpul jadi siluet (0.7 s)', '—', 'Nafas udara rendah', '—')
beat('B07', 'line_masalah', 'siapa', S1, 'Kamera terus mendekat', 'Dolly-in berterusan', 'SIGNAL "Masalahnya bukan berapa ramai." masuk; ayat sebelum keluar ke atas + kabur', 'Orang ramai beku berlapis', 'Titik kuning di paras kepala siluet', 'Nadi sub (heartbeat) ikut beat', '—')
beat('B08', 'siapa', 's02', S1, 'SIAPA. (frame benchmark SF1 pada ≈6.2 s)', 'Dolly perlahan, kemudian roll 90° pada 6.7', 'SIGNAL kuning 250 px "SIAPA." + underline dilukis L→R 0.3 s', 'Siluet kekal', 'Titik kuning memanjang jadi garis pendek, kemudian merentas frame', 'SIGNAL PING + sub hit', 'Roll 90° mengikut Signal Line')
beat('B09', 's02', 'rail_lock', S2, 'Signal Line meluncur melepasi 3 kelompok dan menulis CARI · CAKAP · SAMBUNG', 'Pan sisi ikut hujung garis', 'Perkataan ditulis oleh garis (stroke reveal)', '3 kelompok samar', 'Garis = penulis', 'Whoosh + 3 tick pitch naik', '—')
beat('B10', 'rail_lock', 's03', S2, 'Garis + perkataan mengecut ke atas jadi SIGNAL RAIL (y220–290)', 'Tilt ke atas', 'Perkataan mengecil jadi label mono', '—', 'Garis jadi rail HUD', 'Tick kunci', 'Kamera jatuh ke dalam lautan')
beat('B11', 's03', 'baca_data', S3, 'Tajuk 3D "01 CARI" dan kamera menembusinya', 'Push-through (tajuk membesar melepasi kamera)', 'Tajuk 3D Inter Display', 'Lautan kelabu-ungu', 'Rail: nod 01 berdenyut', 'KICK pertama, whoosh-through', 'Push-through')
beat('B12', 'baca_data', 'q1', S3, 'Signal Line menyelam; grid imbasan muncul', 'Dolly ke depan', 'SIGNAL "Baca data dulu." ("data" kuning + underline) + HUD "DATA-LED AUDIENCE RESEARCH"', 'Garis imbasan melintas orang ramai', 'Menyelam, menjadi pengimbas', 'Sweep imbasan + ping', '—')
beat('B13', 'q1', 'q2', S3, 'Soalan 1 melekat pada kelompok; tapisan pertama', 'Lateral drift', 'SYSTEM "APA MASALAH DIA?" type-on + garis penunjuk', '40 % orang malap', '—', 'LOCK', '—')
beat('B14', 'q2', 'q3', S3, 'Soalan 2; tapisan kedua', 'Lateral drift', 'SYSTEM "APA DIA RISAU?"', '70 % malap', '—', 'LOCK', '—')
beat('B15', 'q3', 'cluster', S3, 'Soalan 3; tinggal satu kelompok', 'Mula rack focus', 'SYSTEM "BILA DIA BELI?"', 'Hanya kelompok kekal terang', '—', 'LOCK', '—')
beat('B16', 'cluster', 'semua_orang', S3, 'BURUJ KUNING: kelompok menyala jadi siluet kuning; tag CONTOH · PEMILIK F&B', 'Rack focus + orbit 15°', 'SYSTEM tag dengan garis penunjuk', 'Kelompok bertukar kuning (gelombang 0.6 s)', 'Signal Line menyambung siluet kelompok', 'CHORD PERTAMA (pad)', '—')
beat('B17', 'semua_orang', 'orang_betul', S3, 'Strike #1', 'Statik', 'NOISE "Semua orang." → garis kuning memotong', '—', 'Garis = pemotong', 'Crackle → glitch', '—')
beat('B18', 'orang_betul', 's04', S3, 'Kelompok mengecut jadi ikon dan terbang ke nod CARI', 'Pull-back kecil', 'SIGNAL "Orang yang betul." ("betul" kuning)', 'Kelompok → ikon', 'Nod CARI menyala penuh', 'Ping + whoosh kecil', 'Whoosh ke tajuk 02')
beat('B19', 's04', 'ad_shout', S4, 'Tajuk 3D "02 CAKAP"', 'Push-through', 'Tajuk 3D', 'Kelompok F&B kuning di bawah, orang ramai kelabu', 'Rail: nod 02 berdenyut', 'Whoosh-through; hats 8th masuk', 'Push-through')
beat('B20', 'ad_shout', 'diri_sendiri', S4, 'Kad iklan MENJERIT "KAMI YANG TERBAIK!"; gelombang lavender luas', 'Wide, shake halus', 'NOISE bergegar di kad', 'Kelompok BERPALING (condong menjauh, malap)', '—', 'Megaphone distorted', '—')
beat('B21', 'diri_sendiri', 'tiada_peduli', S4, 'Gelombang terus memancar', 'Wide', 'NOISE "Cakap pasal diri sendiri…"', 'Kekal membelakangi', '—', 'Crackle', '—')
beat('B22', 'tiada_peduli', 'strike2', S4, 'Huruf hanyut jadi zarah', 'Wide', 'NOISE "…tiada siapa peduli." huruf hanyut', 'Huruf → zarah', '—', 'Desiran pasir', '—')
beat('B23', 'strike2', 'type1', S4, 'Strike #2: Signal Line memotong kad, teks iklan pecah', 'Punch-in 3 %', '—', 'Teks pecah jadi zarah', 'Garis memotong kad', 'GLITCH', '—')
beat('B24', 'type1', 'masalah_dia', S4, 'Ayat F&B ditaip (2 baris) + label CONTOH + ikon cawan; pancaran SEMPIT kuning ke kelompok', 'Push-in ke kad (1.0→1.08)', 'SYSTEM typewriter + cursor kuning; hold ≥ 2.6 s selepas lengkap', 'Kelompok BERPALING KE MESEJ + menyala', 'Pancaran sempit kad → kelompok', 'Keystroke setiap aksara → shimmer', '—')
beat('B25', 'masalah_dia', 'to_rail2', S4, 'Frame benchmark SF2', 'Pull-back reveal', 'SIGNAL "Cakap pasal masalah dia." ("masalah dia." kuning)', 'Kelompok menghadap mesej', 'Pancaran kekal', 'Ping + ARPEGGIO masuk', '—')
beat('B26', 'to_rail2', 's05', S4, 'Kad melipat jadi ikon → nod CAKAP menyala', '—', '—', '—', 'Nod 02 penuh', 'Whoosh kecil', 'Whoosh ke tajuk 03')
beat('B27', 's05', 'uji', S5, 'Tajuk 3D "03 SAMBUNG"; dunia bertukar ke pandangan oblique (bandar)', 'Push-through, kemudian tilt ke bawah', 'Tajuk 3D', 'Lautan dari atas, kebanyakan ungu', 'Rail: nod 03 berdenyut', 'BUILD bermula', 'Push-through')
beat('B28', 'uji', 'menjadi', S5, 'Signal Line bercabang 3 (tiga variasi iklan F&B); 2 cabang malap & putus (✕)', 'Ikut cabang', 'SYSTEM "UJI" ×3', '—', 'Cabang → 2 mati', 'Tick ×3, 2 "putus" (thud)', '—')
beat('B29', 'menjadi', 'besarkan', S5, 'Laluan pemenang menyala', 'Ikut laluan', 'SYSTEM "YANG MENJADI"', '—', 'Pemenang menebal', 'Ping', '—')
beat('B30', 'besarkan', 'bukan_ramai', S5, 'Arus cahaya menjalar sepanjang laluan', 'TRACKING LAJU ke atas laluan (satu-satunya momen laju)', 'SIGNAL "BESARKAN DENGAN ADS." ("BESARKAN" kuning)', 'Orang ramai melintas laju', 'Denyut arus elektrik', 'Hi-hat 16th + RISER', '—')
beat('B31', 'bukan_ramai', 'drop', S5, 'Kamera melambat sebelum drop', 'Deselerasi', 'NOISE "Bukan lebih ramai." (pudar cepat)', '—', '—', 'Riser memuncak → potong 1/8 beat', '—')
beat('B32', 'drop', 'yang_betul', S5, 'DROP: gelombang penyalaan, lautan bertukar KUNING orang demi orang', 'CRANE-OUT besar', 'Tiada teks (payoff visual)', 'Gelombang kuning merebak dari kelompok', 'Laluan pemenang bersinar', 'DROP: boom + groove penuh', '—')
beat('B33', 'yang_betul', 'sweep', S5, 'Frame benchmark SF3: Signal Line mengalir ke underline headline', 'Crane-out perlahan', 'SIGNAL "Lebih ramai yang betul." ("yang betul." kuning)', 'Lautan kuning (peta bandar malam)', 'Garis → underline', 'Groove penuh', 'SWEEP #1 penuh skrin')
beat('B34', 's06', 'ramai_nampak', S6, 'Rail turun dan terbuka jadi 3 baris rumusan', 'Tenang, push 1 %', 'SIGNAL "CARI. CAKAP. SAMBUNG." + artefak', 'Lautan sangat samar', 'Rail = senarai', 'RESOLVE (chord terbuka) + tick ×3', '—')
beat('B35', 'ramai_nampak', 'cari_beli', S6, 'Ayat hook kembali, kemudian MORPH #3', 'Statik', 'NOISE "Ramai yang nampak." → RAMAI & NAMPAK scramble serentak, "yang" kekal', '—', '—', 'Scramble digital', '—')
beat('B36', 'cari_beli', 's07', S6, '"Cari yang beli."', 'Statik', 'SIGNAL "Cari yang beli." ("beli" kuning + underline)', '—', 'Underline', 'PING PALING JELAS', 'Baris runtuh jadi satu garis')
beat('B37', 's07', 's08', S7, 'Signal Line jadi underline wordmark LOKADIGITAL; tagline ditaip', 'Statik, push 1 %', 'Wordmark + SYSTEM type-on tagline', '—', 'Underline logo', 'LOGO STING', 'Wordmark naik; garis jatuh ke tengah')
beat('B38', 's08', 'dm', S8, 'Lautan kuning dimampatkan jadi satu Signal Line', 'Statik', 'SIGNAL "Nak orang yang betul?"', 'Zarah kuning memampat ke garis', 'Garis terbentuk', 'Bed', '—')
beat('B39', 'dm', 'next', S8, 'CTA UTAMA: garis melukis ikon DM + underline', 'Statik', 'SIGNAL besar "DM LOKADIGITAL" ("DM" kuning) + SYSTEM kecil "FOLLOW · SAVE" (60.6)', '—', 'Melukis ikon DM', 'PING + sub lembut; tick', '—')
beat('B40', 'next', 'cover', S8, 'Kad NEXT · EP03 meluncur dari kanan + tekstur framework 20 %', 'Parallax halus', 'SYSTEM "NEXT · EP03" + SIGNAL "Viral is not a strategy."', '—', '—', 'Swish kad', 'Crossfade ke cover')
beat('B41', 'cover', 'fade_out', S8, 'COVER FRAME (= thumbnail): lautan separuh kelabu / separuh kuning', 'Statik', 'SIGNAL "Ramai nampak. Kenapa tak ramai beli?"', 'Separuh kelabu / separuh kuning', '—', 'Bed fade', '—')
beat('B42', 'fade_out', 'end', S8, 'Fade ke hitam, tinggal titik kuning berdenyut = frame pertama', 'Statik', '—', '—', 'Titik kuning', 'SENYAP 0.8 s', 'LOOP ke B01')

def T(e): return 0.0 if e is None else EV[e]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    beats = [dict(b, t0=T(b['start']), t1=T(b['end'])) for b in B]
    for a, b2 in zip(beats, beats[1:]):
        assert abs(a['t1'] - b2['t0']) < 1e-6, (a['id'], b2['id'])
    assert abs(beats[-1]['t1'] - DUR) < 1e-6
    # reading-time QC
    qc = []
    for s, e, txt, w, y in TEXT:
        hold = round(EV[e] - EV[s], 3); req = round(need(w, y), 2)
        qc.append(dict(text=txt, start=EV[s], hold=hold, need=req, ok=hold + 1e-6 >= req))
    drift = {k: round(EV[k] - RAW[k], 3) for k in RAW}
    json.dump(dict(bpm=BPM, beat=BEAT, origin=ORIGIN, dur=DUR, events=EV, beats=beats, reading_qc=qc, drift=drift),
              open(os.path.join(here, 'beatmap.json'), 'w'), indent=1, ensure_ascii=False)

    def bb(t): k = (t - ORIGIN) / BEAT; return f'{int(k // 4) + 1}.{int(k % 4) + 1}' if t >= ORIGIN else '—'
    md = ['# EP02 "ORANG YANG BETUL" — Beat Map v1', '',
          '> **Status:** 🟡 Untuk semakan bersama animatic. Dijana oleh [`animatic/beatmap.py`](animatic/beatmap.py) (satu sumber timing untuk animatic dan audio).',
          f'> Asas: [storyboard v5 FINAL](../STORYBOARD/STORYBOARD_EP02.md) · benchmark visual: [style frames v2](../ASSETS/STYLE_FRAMES/README.md) · **tiada voiceover**.',
          f'> Grid: **{BPM} BPM** (1 beat = {BEAT:.3f} s, 1 bar = {BEAT*4:.3f} s), origin {ORIGIN} s = impact hook. Setiap cue disnap ke ½ beat. Durasi **{DUR} s** = sama dengan storyboard.', '',
          '## Ringkasan scene', '', '| Scene | Mula | Tamat | Durasi | Bar |', '|---|---|---|---|---|']
    scenes = {}
    for b in beats: scenes.setdefault(b['scene'], [b['t0'], b['t1']]); scenes[b['scene']][1] = b['t1']
    for s, (a, z) in scenes.items(): md.append(f'| {s} | {a:.2f} | {z:.2f} | {z-a:.2f} s | {bb(a)} |')
    md += ['', '## Beat map', '', 'Lajur: **Masa** (s) · **Dur** · **Bar.beat** · visual action · kamera · typography · zarah · Signal Line · muzik & SFX · transition ke beat seterusnya.', '']
    cur = None
    for b in beats:
        if b['scene'] != cur:
            cur = b['scene']; md += ['', f'### {cur}', '', '| Beat | Masa | Dur | Bar | Visual action | Kamera | Typography | Zarah | Signal Line | Muzik & SFX | Transition |', '|---|---|---|---|---|---|---|---|---|---|---|']
        md.append(f"| {b['id']} | {b['t0']:.2f}–{b['t1']:.2f} | {b['t1']-b['t0']:.2f} | {bb(b['t0'])} | {b['action']} | {b['cam']} | {b['type']} | {b['part']} | {b['line']} | {b['audio']} | {b['trans']} |")
    md += ['', '## QC masa bacaan (hold ≥ 0.4 s + 0.3 s/perkataan, min 1.0 s, +0.5 s jika kuning)', '', '| Teks | Mula | Hold | Perlu | Status |', '|---|---|---|---|---|']
    for q in qc: md.append(f"| {q['text']} | {q['start']:.2f} | {q['hold']:.2f} | {q['need']:.2f} | {'✅' if q['ok'] else '⚠️'} |")
    snapd = {k: v for k, v in drift.items() if abs(v) > 0.001 and k not in ADJ}
    md += ['', '## Anjakan dari storyboard', '', '### A. Penyesuaian disengajakan (masa bacaan)', '',
           'Urutan dan kandungan storyboard tidak berubah. Hanya timing digeser supaya setiap ayat lulus peraturan masa bacaan.', '',
           '| Cue | Storyboard | Beat map | Anjakan | Sebab |', '|---|---|---|---|---|']
    for k in ADJ: md.append(f'| {k} | {RAW[k]:.2f} | {EV[k]:.3f} | {drift[k]:+.3f} | {ADJ[k][1]} |')
    md += ['', '### B. Snap ke beat grid', '', f'Anjakan maksimum: **{max([abs(v) for v in snapd.values()] or [0]):.3f} s** (had ±0.165 s).', '',
           '| Cue | Storyboard | Beat map | Anjakan |', '|---|---|---|---|']
    for k, v in snapd.items(): md.append(f'| {k} | {RAW[k]:.2f} | {EV[k]:.3f} | {v:+.3f} |')
    md += ['', '## Nota penyelarasan dengan benchmark', '',
           '- **S01 siluet:** storyboard menyebut siluet "kembali jadi titik". Benchmark SF1 (≈6.2 s) menunjukkan siluet masih utuh, jadi siluet **kekal** sehingga 6.7 s dan hanya lebur semasa roll 90° ke S02. Mesej tidak berubah; ia mengikut frame yang diluluskan.',
           '- **S01 Signal Line:** mengikut SF1 v2: garis pendek di paras kepala siluet, dan hanya memanjang merentas frame semasa transition (6.7–6.9 s).']
    open(os.path.join(here, '..', 'BEAT_MAP_EP02.md'), 'w').write('\n'.join(md) + '\n')
    bad = [q for q in qc if not q['ok']]
    print('beats', len(beats), 'max snap drift', max(abs(v) for k, v in drift.items() if k not in ADJ), 'reading-time issues', len(bad))
    for q in bad: print('  ', q)

if __name__ == '__main__':
    main()
