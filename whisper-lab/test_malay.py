"""Malay transcription test: faster-whisper on CPU, int8. Reports WER, speed and peak RAM.
Usage: python -I test_malay.py <fleurs_dir> <model_name> <n_clips> [lang, e.g. ms]"""
import sys, os, csv, re, time, tarfile, threading
import psutil
from faster_whisper import WhisperModel

data_dir, model_name, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
lang = sys.argv[4] if len(sys.argv) > 4 else None
proc = psutil.Process()
peak = {"rss": 0, "cpu": []}
stop = False
def watch():
    proc.cpu_percent(None)
    while not stop:
        peak["rss"] = max(peak["rss"], proc.memory_info().rss)
        peak["cpu"].append(proc.cpu_percent(0.25))
threading.Thread(target=watch, daemon=True).start()

rows, seen = [], set()
with open(os.path.join(data_dir, "dev.tsv"), encoding="utf-8") as f:
    for r in csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
        if r[0] in seen: continue
        seen.add(r[0]); rows.append((r[1], r[3]))
        if len(rows) == n: break
wav_dir = os.path.join(data_dir, "wav"); os.makedirs(wav_dir, exist_ok=True)
want = {"dev/" + w for w, _ in rows}
with tarfile.open(os.path.join(data_dir, "dev.tar.gz")) as tf:
    for m in tf:
        if m.name in want and m.isfile():
            with tf.extractfile(m) as src, open(os.path.join(wav_dir, os.path.basename(m.name)), "wb") as dst:
                dst.write(src.read())

def norm(s): return re.sub(r"[^\w\s]", " ", s.lower()).split()
def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j-1] + 1, prev + (r != h))
    return d[-1]

t0 = time.time()
model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=4)
load = time.time() - t0
errs = words = 0; audio = 0.0; t1 = time.time(); langs = []
for wav, ref in rows:
    segs, info = model.transcribe(os.path.join(wav_dir, wav), language=lang, beam_size=5, vad_filter=False)
    hyp = " ".join(s.text for s in segs).strip()
    audio += info.duration; langs.append(f"{info.language}:{info.language_probability:.2f}")
    e = wer(norm(ref), norm(hyp)); errs += e; words += len(norm(ref))
    print(f"--- REF: {ref}\n    HYP: {hyp}\n    lang={langs[-1]} errors={e}")
dt = time.time() - t1; stop = True; time.sleep(0.3)
cpu = sorted(peak["cpu"])
print(f"\nMODEL {model_name} int8 lang={lang or 'auto'} | clips {len(rows)} | audio {audio:.1f}s | transcribe {dt:.1f}s | "
      f"speed {audio/dt:.2f}x realtime | load {load:.1f}s | WER {100*errs/words:.1f}% | "
      f"peak RAM {peak['rss']/2**20:.0f} MB | CPU avg {sum(cpu)/len(cpu):.0f}% (of {psutil.cpu_count()} cores x100)")
