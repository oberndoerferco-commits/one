// Controlled LCP test: Moto-G-like phone, Slow-4G-ish network, 4x CPU, fresh context each run, alternating themes.
const {chromium,devices}=require('playwright');
const path=process.argv[2]||'/en-de/products/joggers-om', N=+(process.argv[3]||5);
const T={live:'210624381253',draft:'210626511173'};
(async()=>{const b=await chromium.launch(); const res={live:[],draft:[]};
for(let i=0;i<N;i++) for(const k of (i%2?['draft','live']:['live','draft'])){
 const ctx=await b.newContext({...devices['Pixel 5']}); const p=await ctx.newPage(); const cdp=await ctx.newCDPSession(p);
 await cdp.send('Network.enable'); await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:150,downloadThroughput:1.6*1024*1024/8,uploadThroughput:750*1024/8});
 await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
 await p.addInitScript(()=>{window.__lcp=0;window.__lcpEl='';new PerformanceObserver(l=>{for(const e of l.getEntries()){window.__lcp=e.startTime;window.__lcpEl=(e.element&&(e.element.currentSrc||e.element.tagName))||e.url||''}}).observe({type:'largest-contentful-paint',buffered:true})});
 await p.goto('https://www.oberndoerferco.com'+path+(path.includes('?')?'&':'?')+'preview_theme_id='+T[k],{waitUntil:'load',timeout:120000}); await p.waitForTimeout(3000);
 const r=await p.evaluate(()=>({lcp:Math.round(window.__lcp),el:String(window.__lcpEl).split('/').pop().slice(0,50)}));
 res[k].push(r.lcp); console.log(k,i,r.lcp,'ms',r.el); await ctx.close();}
const med=a=>{a=[...a].sort((x,y)=>x-y);return a[Math.floor(a.length/2)]};
console.log('MEDIAN live',med(res.live),'draft',med(res.draft)); await b.close();})();
