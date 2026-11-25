"""Build (and optionally render) one or more style previews.
Usage: python make.py 01 02 ...   (style module names under styles/, e.g. s01_manifesto)
Each project lands in out/<slug>/, the MP4 in renders/<slug>.mp4 when --render is passed."""
import sys, os, importlib, shutil, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

HERE = os.path.dirname(os.path.abspath(__file__))
SCAFFOLD = os.path.join(HERE, "..", "hf-lab", "lab-test")
LOGO = os.path.join(HERE, "..", "drafts", "ref002-samples", "assets", "logo.jpg")

def build(mod_name, render=False):
    st = importlib.import_module("styles." + mod_name)
    d = os.path.join(HERE, "out", st.SLUG); os.makedirs(os.path.join(d, "assets"), exist_ok=True)
    for f in ("hyperframes.json", "package.json"): shutil.copy(os.path.join(SCAFFOLD, f), d)
    json.dump({"id": st.SLUG, "name": st.NAME}, open(os.path.join(d, "meta.json"), "w"))
    shutil.copy(LOGO, os.path.join(d, "assets", "logo.jpg"))
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(lib.page(st))
    m = lib.Mix(seed=hash(st.SLUG) % 1000); st.sound(m)
    raw = os.path.join(d, "assets", "mix_raw.wav"); m.write(raw)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000",
                    os.path.join(d, "assets", "mix.wav")], check=True)
    os.remove(raw)
    print("built", st.SLUG)
    if render:
        os.makedirs(os.path.join(HERE, "renders"), exist_ok=True)
        env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1")
        out = os.path.join(HERE, "renders", f"{st.SLUG}.mp4")
        r = subprocess.run(["npx", "--yes", "hyperframes@0.9.94", "render", "-o", out, "-q", "looks"], cwd=d, env=env, capture_output=True, text=True)
        print("render", st.SLUG, "ok" if os.path.exists(out) else r.stdout[-800:] + r.stderr[-800:])

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in args: build(a, "--render" in sys.argv)
