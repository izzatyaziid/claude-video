const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:2,viewport:{width:794,height:1123}});
for(const f of fs.readdirSync(__dirname).filter(f=>/^draft_.*\.html$/.test(f))){
  await p.goto('file://'+path.join(__dirname,f));await p.evaluate(()=>document.fonts.ready);
  const n=f.replace('.html','');
  await p.pdf({path:path.join(__dirname,n+'.pdf'),width:'210mm',height:'297mm',printBackground:true});
  await p.screenshot({path:path.join(__dirname,n+'.png')});}
await b.close();})();
