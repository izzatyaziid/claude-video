#!/bin/bash
# Downscale a 4K (2160x3840) master to an Instagram Reels / TikTok upload file:
# 1080x1920, 30 fps, H.264 High, yuv420p, BT.709, AAC 48 kHz, faststart, capped bitrate.
# Detail comes from the 4K render (supersampled), so text and edges stay crisp at 1080.
# Usage: ./export_social.sh <master_4k.mp4> <out_1080x1920.mp4>
set -e
in="$1"; out="$2"
ffmpeg -v error -y -i "$in" \
  -vf "scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=3:3:0.3:3:3:0,format=yuv420p" \
  -r 30 -c:v libx264 -preset slow -profile:v high -level 4.2 -crf 17 -maxrate 10M -bufsize 20M -g 60 -bf 2 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$out"
ffprobe -v error -show_entries stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,bit_rate -show_entries format=duration,size -of compact "$out"
