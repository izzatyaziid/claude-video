"""Draft VO with edge-tts (ms-MY-OsmanNeural). Writes assets/vo.wav + timing.json (line times + word times from edge-tts word boundaries).
Usage: python -I vo.py <project_dir>"""
import sys, os, json, asyncio, subprocess
import edge_tts
root = sys.argv[1]; S = json.load(open(os.path.join(root, "script.json"), encoding="utf-8"))
proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
async def one(ln, path):
    c = edge_tts.Communicate(ln["text"], S["voice"], rate=ln.get("rate", S["rate"]), pitch=ln.get("pitch", "+0Hz"), proxy=proxy, boundary="WordBoundary")
    words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append({"text": ch["text"], "start": ch["offset"] / 1e7, "end": (ch["offset"] + ch["duration"]) / 1e7})
    return words
async def main():
    t = 0.25; lines = []; parts = []
    for ln in S["lines"]:
        mp3 = os.path.join(root, "assets", "vo", ln["id"] + ".mp3"); wav = mp3[:-4] + ".wav"
        words = await one(ln, mp3)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "48000", "-ac", "1", wav], check=True)
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]))
        lead = words[0]["start"] if words else 0
        for w in words: w["start"] = round(t + w["start"] - lead, 3); w["end"] = round(t + w["end"] - lead, 3)
        lines.append({**ln, "start": round(t, 3), "end": round(t + d, 3), "words": words}); parts.append((wav, t)); t += d + ln["gap"]
    # mix all parts on a silent bed
    inputs = []; filt = []
    for i, (w, st) in enumerate(parts):
        inputs += ["-i", w]; filt.append(f"[{i}]adelay={int(st * 1000)}|{int(st * 1000)}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad=whole_dur={t:.3f}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[o]", "-ar", "48000", "-ac", "1", os.path.join(root, "assets", "vo.wav")], check=True)
    json.dump({"duration": round(t, 3), "lines": lines}, open(os.path.join(root, "timing.json"), "w"), ensure_ascii=False, indent=1)
    print("duration", round(t, 2))
asyncio.run(main())
