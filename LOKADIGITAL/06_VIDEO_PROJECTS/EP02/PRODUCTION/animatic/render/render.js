// EP02 animatic frame capture.
//   node render.js <outDir> [workers] [comma-separated seconds for PNG stills]
// Frames: <outDir>/f00000.jpg ... at 30 fps for the full beat-map duration.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const BM = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'beatmap.json'), 'utf8'));
const FPS = 30, N = Math.round(BM.dur * FPS);
const out = path.resolve(process.argv[2] || 'frames'), workers = +process.argv[3] || 4, only = process.argv[4];
(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--allow-file-access-from-files'] });
  const frames = only ? only.split(',').map(s => Math.round(parseFloat(s) * FPS)) : [...Array(N).keys()];
  fs.mkdirSync(out, { recursive: true });
  let idx = 0, done = 0; const t0 = Date.now();
  async function work() {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
    await page.goto('file://' + path.join(__dirname, 'animatic.html'));
    await page.evaluate(bm => window.init(bm), BM);
    await page.waitForFunction(() => window.READY === true);
    while (idx < frames.length) {
      const f = frames[idx++];
      const data = await page.evaluate(([t, fr, png]) => { renderFrame(t, fr); return document.getElementById('c').toDataURL(png ? 'image/png' : 'image/jpeg', 0.92); }, [f / FPS, f, !!only]);
      fs.writeFileSync(path.join(out, `f${String(f).padStart(5, '0')}.${only ? 'png' : 'jpg'}`), Buffer.from(data.split(',')[1], 'base64'));
      if (++done % 150 === 0) console.log(`${done}/${frames.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    await page.close();
  }
  await Promise.all([...Array(Math.min(workers, frames.length))].map(work));
  await browser.close();
  console.log('done', frames.length, 'frames', ((Date.now() - t0) / 1000).toFixed(1) + 's');
})();
