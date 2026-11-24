#!/usr/bin/env bash
# Full rebuild: frames (Chromium) + score (numpy) -> 1080x1920 H.264/AAC master
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HERE/.work}"
mkdir -p "$WORK" "$HERE/out"
rm -rf "$WORK/frames"
node "$HERE/render/render.js" "$WORK/frames" 4
python3 "$HERE/audio/sound.py" "$WORK/score.wav"
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i "$WORK/frames/f%05d.jpg" -i "$WORK/score.wav" \
  -c:v libx264 -preset medium -crf 20 -maxrate 5500k -bufsize 11000k -profile:v high -pix_fmt yuv420p -r 30 \
  -af "volume=-1.9dB" -c:a aac -b:a 256k -ar 48000 \
  -movflags +faststart -metadata title="LOKADIGITAL EP01 - Viral Is Not A Strategy" \
  "$HERE/out/LOKADIGITAL_EP01_SignalNoise_1080x1920.mp4"
ls -lh "$HERE/out"
