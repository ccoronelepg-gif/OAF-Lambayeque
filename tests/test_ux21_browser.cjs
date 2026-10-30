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
   await page.locator('#oaf-primary-nav a[data-tab="autor"]').evaluate(el=>el.click());
   await page.waitForTimeout(1500);
   const bootDebug=await page.evaluate(()=>({
    className:document.documentElement.className,
    ids:["oaf-agro-home","oaf-agro-clima","oaf-agro-autor","oaf-ux9-predicciones","oaf-ux14-monthchart","oaf-ux14-monthstatus"]
      .map(id=>[id,!!document.getElementById(id)]),
    monthly:document.getElementById("oaf-ux14-monthstatus")?.textContent||""
   }));
   console.log("UX21_BOOT_DEBUG",JSON.stringify({width,bootDebug}));
   await page.waitForFunction(() => {
    const value=document.querySelector("#oaf-ux14-rf-mes #oaf-ux14-monthstatus")?.textContent?.trim()||"";
    return value.includes("RF no publicado como pronóstico operativo");
   }, {timeout:30000});
  await page.locator("#oaf-ux14-rf-mes #oaf-ux14-monthchart svg").waitFor({state:"attached",timeout:30000});
   await page.waitForTimeout(350);
   const status=await page.evaluate(()=>{
    const q=s=>document.querySelector(s);
    return {
     viewSwitches:document.querySelectorAll(".oaf-view-switch").length,
     cityBar:document.querySelectorAll(".oaf-contextbar").length,
     monthlyChart:!!q("#oaf-ux14-rf-mes #oaf-ux14-monthchart svg"),monthlyStatus:q("#oaf-ux14-rf-mes #oaf-ux14-monthstatus")?.textContent,
     monthlyView:q("#oaf-ux14-rf-mes #oaf-ux16-vista")?.value,
     monthlyLegend:q("#oaf-ux14-rf-mes .oaf-ux14-key")?.textContent,
     futureNote:q("#oaf-ux14-rf-mes .oaf-ux14-no-forecast")?.textContent,
     extraCards:document.querySelectorAll("#oaf-ux16-months").length,
     oldHomeBlock:document.querySelectorAll('#inicio #oaf-bloque-prediccion-inicio').length,
     summarySources:q("#oaf-home-summary-static")?.textContent,
     enfenStyle:q("#oaf-ux15-enfen-exp")?getComputedStyle(q("#oaf-ux15-enfen-exp")).fontStyle:null,
     mobileButton:!!q("#oaf-mobile-menu")
    };
   });
   assert.equal(status.viewSwitches,0,"Vista rápida/técnica permanece");
   assert.equal(status.cityBar,0,"Barra Cambiar zona permanece");
   assert.equal(status.oldHomeBlock,0,"Evolución histórica duplicada en Inicio");
   assert.equal(status.extraCards,0,"Tarjetas RF redundantes continúan");
   assert.equal(status.monthlyChart,true,"La evaluación mensual retrospectiva no se dibuja");
   assert.equal(status.monthlyView,"futuro","La vista mensual debe abrir en horizonte futuro");
   assert.ok(status.monthlyStatus?.includes("RF no publicado como pronóstico operativo")&&status.monthlyStatus?.includes("1/6 horizontes"),"El RF mensual no está bloqueado por su baja habilidad");
   assert.ok(status.monthlyLegend?.includes("ERA5")&&!status.monthlyLegend?.includes("Random Forest OAF"),"El gráfico futuro debe mostrar climatología y no RF no validado");
   assert.ok(status.futureNote?.includes("1 de 6 horizontes recursivos"),"El texto mensual no explica la evidencia del bloqueo");
   await page.locator("#oaf-ux14-rf-mes #oaf-ux16-vista").selectOption("historico");
   await page.waitForFunction(()=>document.querySelector("#oaf-ux14-rf-mes #oaf-ux14-monthstatus")?.textContent?.includes("Prueba retrospectiva 2021–2025"),{timeout:30000});
   const historical=await page.locator("#oaf-ux14-rf-mes #oaf-ux14-monthstatus").textContent();
   assert.ok(historical?.includes("Prueba retrospectiva 2021–2025"),"La vista histórica no se conserva");
   await page.locator("#oaf-ux14-rf-mes #oaf-ux16-vista").selectOption("futuro");
   await page.waitForFunction(()=>document.querySelector("#oaf-ux14-rf-mes #oaf-ux14-monthstatus")?.textContent?.includes("RF no publicado como pronóstico operativo"),{timeout:30000});
   assert.ok(status.summarySources?.includes("Open-Meteo")&&status.summarySources.includes("ENFEN"),"Fuentes no centralizadas");
   assert.equal(status.enfenStyle,"italic","Interpretación del Niño Costero no está en cursiva");
   await page.locator('#oaf-primary-nav a[data-tab="cultivos"]').evaluate(el=>el.click());
   await page.locator("#oaf-mg-fuentes a").waitFor({state:"attached",timeout:30000});
   const sources=await page.locator("#oaf-mg-fuentes a").allTextContents();
   assert.equal(sources.length,1,"Sanidad tiene enlaces de investigación duplicados");
   assert.ok(sources[0].includes("Fuente fitosanitaria"),"Fuente principal no visible");
   console.log("OAF UX21: "+width+"px, menú, Inicio, gráfica mensual, Sanidad e interpretación OK");
   await context.close();
  }
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
