// Frame capture: node render.js <outDir> [workers] [comma-separated seconds for stills]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const FPS = 30, DUR = 59.0, N = Math.round(FPS * DUR);
const out = process.argv[2] || 'frames', workers = +process.argv[3] || 4, only = process.argv[4];
(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
  const url = 'file://' + path.resolve(__dirname, 'scene.html');
  const frames = only ? only.split(',').map(s => Math.round(parseFloat(s) * FPS)) : [...Array(N).keys()];
  fs.mkdirSync(out, { recursive: true });
  let idx = 0, done = 0; const t0 = Date.now();
  async function work() {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
    await page.goto(url); await page.waitForFunction(() => window.READY === true);
    while (idx < frames.length) {
      const f = frames[idx++];
      const data = await page.evaluate(([t, png]) => { renderFrame(t); return document.getElementById('c').toDataURL(png ? 'image/png' : 'image/jpeg', 0.95); }, [f / FPS, !!only]);
      const ext = only ? 'png' : 'jpg';
      fs.writeFileSync(path.join(out, `f${String(f).padStart(5, '0')}.${ext}`), Buffer.from(data.split(',')[1], 'base64'));
      if (++done % 150 === 0) console.log(`${done}/${frames.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    await page.close();
  }
  await Promise.all([...Array(workers)].map(work));
  await browser.close();
  console.log('done', ((Date.now() - t0) / 1000).toFixed(1) + 's');
})();
