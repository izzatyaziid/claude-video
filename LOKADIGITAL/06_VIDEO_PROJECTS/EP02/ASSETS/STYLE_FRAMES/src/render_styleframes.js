// Render EP02 style frames (stills only): node render_styleframes.js <outDir> [SF1,SF2,...]
// Output per frame: <ID>.png (2160x3840 review master), <ID>_1080.jpg (1080x1920 delivery size), <ID>_annotated.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const out = path.resolve(process.argv[2] || path.join(__dirname, '..'));
const ALL = { SF1: 'EP02_SF1_HOOK_SIAPA', SF2: 'EP02_SF2_CAKAP_MASALAH_DIA', SF3: 'EP02_SF3_SAMBUNG_YANG_BETUL', SF4: 'EP02_SF4_CARI_FAIL', SF5: 'EP02_SF5_SAMBUNG_AMPLIFIER' };
const pick = (process.argv[3] || Object.keys(ALL).join(',')).split(',');
const NAMES = Object.fromEntries(pick.map(k => [k, ALL[k]]));
(async () => {
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none', '--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
  await page.goto('file://' + path.join(__dirname, 'styleframes.html'));
  await page.waitForFunction(() => window.READY === true);
  fs.mkdirSync(out, { recursive: true });
  for (const id of Object.keys(NAMES)) {
    for (const annot of [false, true]) {
      const t0 = Date.now();
      const data = await page.evaluate(([i, a]) => window.render(i, a), [id, annot]);
      const file = path.join(out, NAMES[id] + (annot ? '_annotated' : '') + '.png');
      fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
      console.log(path.basename(file), ((Date.now() - t0) / 1000).toFixed(1) + 's');
    }
  }
  await browser.close();
})();
