const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => { const b = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await b.newPage({ viewport: { width: 3840, height: 2400 } });
  p.on('pageerror', e => { console.error(e.message); process.exit(1); });
  await p.goto('file://' + path.join(__dirname, 'reference_sheet.html')); await p.waitForFunction(() => window.DONE === true, null, { timeout: 60000 });
  const d = await p.evaluate(() => document.getElementById('c').toDataURL('image/jpeg', 0.93));
  fs.writeFileSync(path.join(__dirname, 'LD_SIGNATURE_CHARACTER_REFERENCE_SHEET_v1.jpg'), Buffer.from(d.split(',')[1], 'base64')); await b.close(); console.log('ok'); })();
