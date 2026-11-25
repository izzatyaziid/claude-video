#!/usr/bin/env bash
# mux.sh <framesDir> <score.wav> <out.mp4> <title>
# Two-pass EBU R128 loudness normalisation to -14 LUFS / -1.5 dBTP, H.264 high, AAC 48 kHz, 30 fps.
set -euo pipefail
F="$1"; A="$2"; O="$3"; TITLE="${4:-LOKADIGITAL}"
J=$(ffmpeg -hide_banner -i "$A" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
LN="loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"
ffmpeg -v error -y -framerate 30 -i "$F/f%05d.jpg" -i "$A" -c:v libx264 -preset slow -crf 20 -maxrate 6000k -bufsize 12000k -pix_fmt yuv420p -profile:v high \
  -af "$LN,aresample=48000" -c:a aac -b:a 192k -movflags +faststart -shortest -metadata title="$TITLE" "$O"
ffmpeg -hide_banner -i "$O" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tr -s ' '
