/* Prueba de integración OAF UX21: Chromium móvil 390px y escritorio 1366px. */
const {chromium}=require("playwright"),assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  for(const width of [390,1366]){
   const context=await browser.newContext({viewport:{width,height:860},deviceScaleFactor:1});
   await context.route("**/*",route=>{
    const u=route.request().url();
    if(u.startsWith("http://127.0.0.1:8765/"))return route.continue();
    return route.abort();
   });
   const page=await context.newPage();
   await page.goto("http://127.0.0.1:8765/",{waitUntil:"domcontentloaded",timeout:60000});
   await page.locator("#oaf-ux16-vista").waitFor({state:"attached",timeout:30000});
   await page.waitForTimeout(350);
   const status=await page.evaluate(()=>{
    const q=s=>document.querySelector(s);
    return {
     viewSwitches:document.querySelectorAll(".oaf-view-switch").length,
     cityBar:document.querySelectorAll(".oaf-contextbar").length,
     monthlyValue:q("#oaf-ux16-vista")?.value,
     extraCards:document.querySelectorAll("#oaf-ux16-months").length,
     oldHomeBlock:document.querySelectorAll('#inicio #oaf-bloque-prediccion-inicio').length,
     summarySources:q("#oaf-home-summary-static")?.innerText,
     enfenStyle:q("#oaf-ux15-enfen-exp")?getComputedStyle(q("#oaf-ux15-enfen-exp")).fontStyle:null,
     mobileButton:!!q("#oaf-mobile-menu")
    };
   });
   assert.equal(status.viewSwitches,0,"Vista rápida/técnica permanece");
   assert.equal(status.cityBar,0,"Barra Cambiar zona permanece");
   assert.equal(status.oldHomeBlock,0,"Evolución histórica duplicada en Inicio");
   assert.equal(status.extraCards,0,"Tarjetas RF redundantes continúan");
   assert.equal(status.monthlyValue,"futuro","El gráfico mensual no abre noviembre 2026");
   assert.ok(status.summarySources?.includes("Open-Meteo")&&status.summarySources.includes("ENFEN"),"Fuentes no centralizadas");
   assert.equal(status.enfenStyle,"italic","Interpretación del Niño Costero no está en cursiva");
   if(width===390){
    await page.locator("#oaf-mobile-menu").click();
    await page.locator('#oaf-primary-nav a[data-tab="cultivos"]').click();
   }else await page.locator('#oaf-primary-nav a[data-tab="cultivos"]').click();
   await page.locator("#oaf-mg-fuentes a").waitFor({state:"attached",timeout:30000});
   const sources=await page.locator("#oaf-mg-fuentes a").allTextContents();
   assert.equal(sources.length,1,"Sanidad tiene enlaces de investigación duplicados");
   assert.ok(sources[0].includes("Fuente fitosanitaria"),"Fuente principal no visible");
   console.log("OAF UX21: "+width+"px, menú, Inicio, gráfica mensual, Sanidad e interpretación OK");
   await context.close();
  }
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
