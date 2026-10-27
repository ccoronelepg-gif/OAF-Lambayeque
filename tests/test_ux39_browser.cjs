/* UX39 – comprobación de geovisores en Chromium; solo archivos locales. */
"use strict";
const {chromium}=require("playwright"),assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const context=await browser.newContext({viewport:{width:1365,height:850},locale:"es-PE"});
  await context.route("**/*",route=>route.request().url().startsWith("http://127.0.0.1:8765/")?route.continue():route.abort("blockedbyclient"));
  const page=await context.newPage();const errors=[];
  page.on("pageerror",err=>errors.push(err.message));
  await page.goto("http://127.0.0.1:8765/",{waitUntil:"domcontentloaded",timeout:45000});
  await page.waitForSelector("#oaf-parcel-territorio",{timeout:20000});
  await page.waitForSelector("#oaf-parcel-escenarios",{timeout:20000});
  assert(await page.locator("#oaf-area-territorio").count(),"No se encuentra entrada de coordenadas del visor territorial");
  assert(await page.locator("#oaf-area-escenarios").count(),"No se encuentra entrada de coordenadas del visor de escenarios");
  const inside=await page.evaluate(()=>["territorio","escenarios"].map(k=>({
   area:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-area-"+k),
   polygon:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-parcel-"+k)
  })));
  assert(inside.every(x=>x.area&&x.polygon),"Los módulos deben estar DENTRO de la columna de mapas "+JSON.stringify(inside));
  const result=await page.evaluate(()=>{
   const f=document.querySelector("#oaf-area-territorio form");f.elements.namedItem("name").value="Parcela de prueba";
   f.elements.namedItem("lat").value="-6.15083";f.elements.namedItem("lon").value="-79.7142";f.requestSubmit();
   return {point:window.OAFTerritory?.getActivePoint?.("territorio"),other:window.OAFTerritory?.getActivePoint?.("escenarios")};
  });
  assert(Math.abs(result.point?.lat+6.15083)<1e-5,"Punto territorial no fue persistido");
  assert(!result.other,"El punto del visor territorial contaminó escenarios");
  const geo={type:"FeatureCollection",features:[{type:"Feature",properties:{name:"Fundo de prueba"},geometry:{type:"Polygon",
   coordinates:[[[-79.7142,-6.15083],[-79.7132,-6.15083],[-79.7132,-6.14983],[-79.7142,-6.14983],[-79.7142,-6.15083]]]}}]};
  await page.locator("#oaf-parcel-territorio [data-ux39-file]").setInputFiles({
   name:"fundo.geojson",mimeType:"application/geo+json",buffer:Buffer.from(JSON.stringify(geo))
  });
  const p=await page.evaluate(()=>window.OAFParcelas?.get?.("territorio"));
  assert(p&&p.ha>1&&p.ha<1.4,"El importador no calculó un polígono de superficie aproximada válida");
  await page.waitForTimeout(350);
  assert(await page.locator("#oaf-ux24-region-map #oaf-ux39-geom-territorio").count(),"El polígono no se dibujó en el SVG territorial");
  const escenario=await page.evaluate(()=>{
   const f=document.querySelector("#oaf-area-escenarios form");
   f.elements.namedItem("format").value="utm";
   f.elements.namedItem("format").dispatchEvent(new Event("change",{bubbles:true}));
   f.elements.namedItem("east").value="642270.904567";f.elements.namedItem("north").value="9319951.242352";
   f.elements.namedItem("zone").value="17";f.elements.namedItem("hemi").value="S";f.requestSubmit();
   return window.OAFTerritory.getActivePoint("escenarios");
  });
  assert(Math.abs(escenario.lat+6.15083)<.00001,"Conversión UTM S17 errónea en visor de escenarios");
  assert(Math.abs(escenario.lon+79.7142)<.00001,"Longitud UTM incorrecta");
  await page.waitForTimeout(350);
  assert(await page.locator("#oaf-ux29-forecast-map #oaf-area-pin-escenarios").count(),"El punto no se dibujó en el SVG del visor de escenarios");
  assert(await page.locator("#oaf-ux24-region-map #oaf-area-pin-territorio").count(),"Desapareció el punto territorial al definir escenario");
  const importantErrors=errors.filter(x=>/ux39|oaf-parcel|oaf-area|Cannot read properties of undefined/.test(x));
  assert.deepEqual(importantErrors,[],"Errores JavaScript en los nuevos módulos: "+importantErrors.join(" | "));
  console.log("UX39 browser OK: visores integrados, independencia, GeoJSON, áreas, marcador y UTM WGS84");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
