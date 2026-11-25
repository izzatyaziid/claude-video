#!/bin/bash
# render styles one after another: ./render_queue.sh s04_funnel3d s05_split ...
cd "$(dirname "$0")"
for s in "$@"; do /home/user/claude-video/whisper-lab/.venv/bin/python make.py "$s" --render; done
