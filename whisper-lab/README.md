# whisper-lab: faster-whisper Malay test (2026-11-25)

Separate test folder. Free, local, no paid API. The model weights (`models/`) and the venv (`.venv/`) are not committed.

## Setup (repeatable)
```bash
cd whisper-lab
python3 -m venv .venv
./.venv/bin/pip install faster-whisper psutil 'av<19'   # av 19 breaks faster-whisper 1.2
export HF_HOME=$PWD/models HF_HUB_DISABLE_XET=1
./.venv/bin/python -c "from huggingface_hub import snapshot_download as d; d('Systran/faster-whisper-small')"
```
Network: the model download needs the hosts huggingface.co and us.aws.cdn.hf.co (added to the cloud environment).

## Test
Data: Google FLEURS `ms_my` dev set (real human Malay speech with reference transcripts, CC-BY-4.0), first 10 distinct sentences, 111 s of audio.
```bash
HF_HOME=$PWD/models HF_HUB_OFFLINE=1 ./.venv/bin/python -I test_malay.py <fleurs_dir> small 10 ms
```

## Results (cloud container: 4 CPU cores, 16 GB RAM, CPU only, int8)
| Model | Language | WER | Speed | Peak RAM | CPU |
|---|---|---|---|---|---|
| base (142 MB) | auto | 37.6% | 3.7x realtime | 507 MB | ~2 cores |
| base | ms (forced) | 41.0% | 5.0x | 496 MB | ~1.9 cores |
| **small (464 MB)** | auto | 20.5% | 2.7x | 770 MB | ~2.3 cores |
| **small** | **ms (forced)** | **20.5%** | **3.5x** | **770 MB** | ~2.2 cores |

Notes:
- Auto language detection often labels Malay as Indonesian (`id`); force `language="ms"`.
- WER is inflated by number formatting ("100m" vs "100 meter", "satu" vs "1") and spelling; meaning is mostly intact on `small`, but names and rare words still go wrong. Always proofread before using a transcript.
- Recommendation: `small`, int8, `language="ms"`. Use it to transcribe reference videos, not for production VO (LokaDigital uses no voiceover).
