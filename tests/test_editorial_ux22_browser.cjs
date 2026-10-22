/* OAF UX22: verify summary copy, alignment and balanced space in site + installed PWA. */
const {chromium}=require("playwright"),assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try {
  const context=await browser.newContext({locale:"es-PE",reducedMotion:"reduce"});
  const page=await context.newPage(),base="http://127.0.0.1:8765/";
  await context.route("**/*",route=>route.request().url().startsWith(base)?route.continue():route.abort());
  for(const width of [320,360,390,700,1280]){
    await page.setViewportSize({width,height:900});
    await page.goto(base+"?app=pwa#inicio",{waitUntil:"domcontentloaded",timeout:45000});
    const details=await page.locator("#oaf-home-summary-static").evaluate(el=>{
      const p=el.querySelector(".oaf-ux22-sintesis"),s=getComputedStyle(p),r=p.getBoundingClientRect(),box=el.getBoundingClientRect();
      return {text:p.textContent.trim(),alignment:s.textAlign,lines:r.height/parseFloat(s.lineHeight),
              width:r.width,panelWidth:box.width,fontSize:s.fontSize,
              extraScroll:document.documentElement.scrollWidth-window.innerWidth};
    });
    assert.equal(details.alignment,"justify","No se justifica el texto con ancho "+width);
    const words=details.text.split(/\s+/).length;
    assert.ok(words<=70,"El resumen vuelve a ser demasiado largo: "+words+" palabras");
    for(const source of ["ENFEN","SENAMHI","NOAA","CHIRPS","ERA5","Open-Meteo","CAMS","Random Forest"])assert.ok(details.text.includes(source),"Fuente/algoritmo ausente: "+source);
    assert.ok(details.width>=details.panelWidth-60,"El resumen desaprovecha el ancho del recuadro: "+JSON.stringify(details));
    assert.ok(details.extraScroll<=4,"La página se desborda: "+JSON.stringify(details));
    if(width<=390)assert.ok(details.lines<=11,"El texto no cabe en ~10 líneas en móvil: "+JSON.stringify(details));
    if(width>=700)assert.ok(details.lines<=10,"Más de 10 líneas en escritorio: "+JSON.stringify(details));
    console.log("UX22 width="+width+" words="+words+" lines="+details.lines.toFixed(1)+" align="+details.alignment);
  }
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
