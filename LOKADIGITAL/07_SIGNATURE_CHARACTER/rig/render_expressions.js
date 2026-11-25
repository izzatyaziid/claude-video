// node render_expressions.js <outDir>  -> transparent 1024 PNGs of every expression / pose in the reference set
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const out = path.resolve(process.argv[2] || path.join(__dirname, '..', 'expressions'));
const SET = {
  E01_skeptical: { expr: {} },
  E02_neutral: { expr: { neutral: 1 } },
  E03_confident_smile: { expr: { smile: 1 } },
  E04_smirk: { expr: { smirk: 1 } },
  E05_surprised: { expr: { surprised: 1 } },
  E06_thinking: { expr: { thinking: 1 }, tilt: 0.04 },
  E07_focused: { expr: { focused: 1 } },
  E08_worried: { expr: { worried: 1 } },
  P01_look_left: { expr: { neutral: 1 }, yaw: -0.8, eyeX: -0.9 },
  P02_look_right: { expr: { neutral: 1 }, yaw: 0.8, eyeX: 0.9 },
  P03_tilt_curious: { expr: { thinking: 0.6, smile: 0.3 }, tilt: 0.09, eyeY: -0.5 },
  P04_blink: { expr: { neutral: 1 }, blink: 1 },
};
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1024, height: 1024 } });
  p.on('pageerror', e => { console.error('PAGE', e.message); process.exit(1); }); p.on('console', m => m.type() === 'error' && console.error(m.text()));
  await p.goto('file://' + path.join(__dirname, 'expressions.html')); await p.waitForFunction(() => window.READY === true, null, { timeout: 60000 });
  fs.mkdirSync(out, { recursive: true });
  for (const [k, v] of Object.entries(SET)) { const d = await p.evaluate(x => window.shot(x), v); fs.writeFileSync(path.join(out, k + '.png'), Buffer.from(d.split(',')[1], 'base64')); console.log(k); }
  await b.close();
})();
