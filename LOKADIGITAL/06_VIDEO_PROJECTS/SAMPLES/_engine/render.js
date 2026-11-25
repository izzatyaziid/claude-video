// Shared frame renderer for LokaDigital sample videos.
//   node render.js <page.html> <outDir> <durationSec> [workers=4] [stills: comma-separated seconds]
// The page must expose: async window.init(), window.renderFrame(t, frameIndex) drawing into <canvas id="out" 1080x1920>.
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const [page_, outDir, durS, wS, stills] = process.argv.slice(2);
const FPS = 30, N = Math.round(parseFloat(durS) * FPS), workers = +wS || 4;
(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--force-color-profile=srgb', '--font-render-hinting=none'] });
  const frames = stills ? stills.split(',').map(s => Math.round(parseFloat(s) * FPS)) : [...Array(N).keys()];
  fs.mkdirSync(outDir, { recursive: true }); let idx = 0, done = 0; const t0 = Date.now();
  async function work() {
    const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    p.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
    p.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
    await p.goto('file://' + path.resolve(page_)); await p.waitForFunction(() => typeof window.init === 'function', null, { timeout: 60000 });
    await p.evaluate(() => window.init());
    while (idx < frames.length) { const f = frames[idx++];
      const d = await p.evaluate(([t, f, png]) => { window.renderFrame(t, f); return document.getElementById('out').toDataURL(png ? 'image/png' : 'image/jpeg', 0.93); }, [f / FPS, f, !!stills]);
      fs.writeFileSync(path.join(outDir, `f${String(f).padStart(5, '0')}.${stills ? 'png' : 'jpg'}`), Buffer.from(d.split(',')[1], 'base64'));
      if (++done % 150 === 0) console.log(`${done}/${frames.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`); }
    await p.close(); }
  await Promise.all([...Array(Math.min(workers, frames.length))].map(work)); await browser.close();
  console.log('done', frames.length, 'frames', ((Date.now() - t0) / 1000).toFixed(1) + 's');
})();
