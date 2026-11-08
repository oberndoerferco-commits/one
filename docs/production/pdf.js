const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.cwd()+'/ordine.html',{waitUntil:'load'});
await p.pdf({path:'Ordine-produzione-Oberndoerfer-2026-11.pdf',format:'A4',landscape:true,printBackground:true,margin:{top:'12mm',bottom:'12mm',left:'12mm',right:'12mm'}});
await p.setViewportSize({width:1123,height:794}); await p.screenshot({path:'preview.png',fullPage:true});
await b.close();})();
