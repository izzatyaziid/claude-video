# EP01 — Quality Control Report

## Technical (measured on the delivered master)
| Check | Result |
|---|---|
| Resolution / aspect | 1080×1920, 9:16 ✅ |
| Frame rate / duration | 30 fps CFR, 59.00 s (1770 frames) ✅ |
| Video | H.264 High, yuv420p, CRF 20 capped at 5.5 Mbps (avg 4.98 Mbps), faststart ✅ |
| Audio | AAC 256 kbps, 48 kHz stereo ✅ |
| Loudness | **−14.0 LUFS integrated**, true peak −3.2 dBFS, LRA 7.9 LU (TikTok/Reels target) ✅ |
| File size | 37 MB (under platform and GitHub limits) ✅ |
| Safe zones | Key copy sits between y≈230 and y≈1600. Bottom caption/UI zone and right-rail icons are kept clear of critical text ✅ |

## Creative review — issues found and fixed during QC
| # | Issue | Fix |
|---|---|---|
| 1 | Statement "MORE CONTENT / DOESN'T MEAN / MORE GROWTH." lines touched; the outline line read as a collision | Leading opened from 1.00 to 1.10 em, block re-centred |
| 2 | Brand end-card reflection was faded with a dark overlay that left a hard rectangular band across the purple bloom (looked cheap) | Reflection rebuilt as an alpha-masked mirror layer. No overlay, the bloom stays continuous |
| 3 | Reflection competed with the tagline | Reflection opacity cut to 16 % with a 115 px falloff |
| 4 | Score too hot (−8 LUFS): sustained pads on the Signal, "A SYSTEM IS." and brand chords were crushing the mix | Pads re-balanced, reverb sends reduced, master normalised to −14 LUFS |
| 5 | Energy hole at 41–43 s (overview had no groove) | Groove carried through the overview in a thinner form under the build riser |
| 6 | First encode (CRF 17, tune grain) went over 160 MB because film grain eats bitrate | Re-encoded with a capped bitrate. Grain still reads, and the file now survives platform re-encoding |

## Checklist
- **Storytelling:** Hook (accelerating "POST." + 365 counter) → Problem (storm, freeze, silence, truth) → Insight (gap chart, diagnosis, noise → signal) → Strategy (6-stage system) → Impact (philosophy + "A SYSTEM IS.") → Brand. One metaphor, carried start to finish ✅
- **Pacing:** fast (0–8 s) → dead stop (7.85–8.6 s silence) → measured (12–25 s) → rhythmic (25–43 s) → staccato (43–46 s) → breath → slam (49.3 s) → slow resolve (52–59 s). No two consecutive sections move at the same speed ✅
- **Typography:** one family (Inter / Inter Display), three roles (display, copy, labels). Every super enters with a masked rise and exits with a masked lift ✅
- **Visual consistency:** yellow is used only for signal and meaning (sales?, GROWTH, a system, signal, active node, KEEP, winner, scale, A SYSTEM IS., brand bar) ✅
- **Sound design:** every visible action has a matched sound (slams, pills, ticks per counter value, line-draw tones, scan, lock, winner, rings, gleam). Tape-stop and true silence on the freeze ✅
- **Colour:** ink blacks, purple key light, no rainbow gradients. The only non-brand hue is a 0.4 s RGB-split on the word "noise.", which is deliberate ✅
- **Brand positioning:** strategic and analytical. No "go viral" promises; the brand line closes the film ✅

## Known limitations (stated honestly)
1. **No voiceover in the master.** TTS services were unreachable from the production environment, so the film is built super-led (it works with sound off). The Malay-English VO script is timed and ready for a human recording.
2. **Wordmark is a typographic placeholder** (Inter Display). Replace it with the official LOKADIGITAL logo if one exists.
3. **Data in the visuals is illustrative UI** (retention %, labels). The film makes no claims about client results.
4. Graphics are fully procedural (no live-action footage). If live-action or 3D plates become available, the storm and brand scenes are the natural places to composite them.
