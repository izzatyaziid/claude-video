// Usage: node build.js  -> exports LOKADIGITAL_Marketing_Package.pdf + .png from package.html
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 2 });
  await p.goto('file://' + path.resolve(__dirname, 'package.html')); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: 'LOKADIGITAL_Marketing_Package.pdf', width: '210mm', height: '297mm', printBackground: true });
  await p.setViewportSize({ width: 794, height: 1123 });
  await p.screenshot({ path: 'LOKADIGITAL_Marketing_Package.png', fullPage: false });
  await b.close();
})();
