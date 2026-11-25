"""Placeholder Malay VO with Meta MMS-TTS (facebook/mms-tts-zlm, CC-BY-NC-4.0: drafts only, not for client/commercial release).
Writes assets/vo.wav (48 kHz mono) and timing.json (line + word times; word times split by character count).
Usage: python -I tts.py <project_dir>"""
import sys, os, json, re
import numpy as np, torch, scipy.signal, scipy.io.wavfile as wf
from transformers import VitsModel, AutoTokenizer

root = sys.argv[1]
script = json.load(open(os.path.join(root, "script.json"), encoding="utf-8"))
torch.manual_seed(7)
tok = AutoTokenizer.from_pretrained("facebook/mms-tts-zlm")
model = VitsModel.from_pretrained("facebook/mms-tts-zlm")
model.config.speaking_rate = 1.05
model.config.noise_scale = 0.55
SR = 48000; LEAD = 0.45
out, t, lines = [np.zeros(int(LEAD * SR))], LEAD, []
for ln in script["lines"]:
    spoken = ln["text"].replace("DM LOKADIGITAL", "di em, loka dijital").replace("content", "kontent")
    with torch.no_grad():
        wav = model(**tok(spoken.lower(), return_tensors="pt")).waveform[0].numpy()
    wav = scipy.signal.resample_poly(wav, SR, model.config.sampling_rate)
    # trim leading/trailing silence
    env = np.abs(wav) > 0.02 * np.abs(wav).max()
    nz = np.nonzero(env)[0]; wav = wav[max(0, nz[0] - 480): nz[-1] + 2400]
    wav = wav / (np.abs(wav).max() + 1e-9) * 0.89
    d = len(wav) / SR
    words = ln["text"].split(); chars = sum(len(w) for w in words); wt, c = [], 0
    for w in words:
        wt.append({"text": w, "start": round(t + d * c / chars, 3), "end": round(t + d * (c + len(w)) / chars, 3)}); c += len(w)
    lines.append({**ln, "start": round(t, 3), "end": round(t + d, 3), "words": wt})
    out += [wav, np.zeros(int(ln["gap"] * SR))]; t += d + ln["gap"]
vo = np.concatenate(out).astype(np.float32)
os.makedirs(os.path.join(root, "assets"), exist_ok=True)
wf.write(os.path.join(root, "assets", "vo.wav"), SR, (vo * 32767).astype(np.int16))
json.dump({"duration": round(t, 3), "lines": lines}, open(os.path.join(root, "timing.json"), "w"), ensure_ascii=False, indent=1)
print("duration", round(t, 2), "s")
