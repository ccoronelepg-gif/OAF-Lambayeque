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
  await page.waitForSelector("#oaf-parcel-territorio",{state:"attached",timeout:20000});
  await page.waitForSelector("#oaf-parcel-escenarios",{state:"attached",timeout:20000});
  await page.waitForFunction(()=>Boolean(window.oafUx30Context?.()?.scene?.bounds&&window.oafUx29ScenarioApi?.get?.()?.scene?.bounds),{timeout:20000});
  assert(await page.locator("#oaf-area-territorio").count(),"No se encuentra entrada de coordenadas del visor territorial");
  assert(await page.locator("#oaf-area-escenarios").count(),"No se encuentra entrada de coordenadas del visor de escenarios");
  const inside=await page.evaluate(()=>["territorio","escenarios"].map(k=>({
   area:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-area-"+k),
   polygon:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-parcel-"+k)
  })));
  assert(inside.every(x=>x.area&&x.polygon),"Los módulos deben estar DENTRO de la columna de mapas "+JSON.stringify(inside));
  const order=await page.evaluate(()=>["territorio","escenarios"].map(k=>{
   const root=document.getElementById(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
   const column=root.querySelector(".oaf-ux29-mapcolumn"),children=[...column.children].map(x=>x.id||x.className);
   const area=column.querySelector("#oaf-area-"+k),map=column.querySelector(".oaf-ux29-mapcontent"),parcel=column.querySelector("#oaf-parcel-"+k);
   const diag=column.querySelector("#oaf-area-point-details-"+k);
   const hydro=k==="escenarios"?column.querySelector("#oaf-ux36-panel"):null;
   const forecastMap=k==="escenarios"?column.querySelector(".oaf-ux29-scenemap"):null;
   return {k,hydroOrder:k==="territorio"||Boolean(hydro&&forecastMap&&
      (forecastMap.compareDocumentPosition(parcel)&Node.DOCUMENT_POSITION_FOLLOWING)&&
      (diag.compareDocumentPosition(hydro)&Node.DOCUMENT_POSITION_FOLLOWING)&&
      (parcel.compareDocumentPosition(hydro)&Node.DOCUMENT_POSITION_FOLLOWING)&&
      hydro.parentElement===map),
    afterArea:!!(area.compareDocumentPosition(map)&Node.DOCUMENT_POSITION_FOLLOWING),
    afterMap:!!(map.compareDocumentPosition(parcel)&Node.DOCUMENT_POSITION_FOLLOWING),
    afterParcel:!!(parcel.compareDocumentPosition(diag)&Node.DOCUMENT_POSITION_FOLLOWING),
    parcelFold:parcel.querySelector(".oaf-parcel-fold")?.open===false,
    auditUnderMap:!!diag.querySelector(".oaf-area-data"),hasExpand:!!column.querySelector(".oaf-map-expand"),
    children};
  }));
  assert(order.every(x=>x.afterArea&&x.afterMap&&x.afterParcel&&x.hydroOrder&&x.parcelFold&&x.auditUnderMap&&x.hasExpand),
   "Jerarquía visual incorrecta: "+JSON.stringify(order));
  const weekly=await page.evaluate(()=>{
    const week=document.getElementById("oaf-ux14-rf-semana"),monthly=document.getElementById("oaf-ux14-rf-mes");
    return {weekly:!!week,monthly:!!monthly,first:!!(week&&monthly&&(week.compareDocumentPosition(monthly)&Node.DOCUMENT_POSITION_FOLLOWING)),
      visible:week?getComputedStyle(week).display!=="none":false,controls:!!document.getElementById("oaf-ux14-ciudad")};
  });
  assert(weekly.weekly&&weekly.monthly&&weekly.first&&weekly.visible&&weekly.controls,
    "Gráfico semanal RF/Open-Meteo/ERA5 no figura antes del horizonte mensual: "+JSON.stringify(weekly));
  // UX42: Carrusel Inicio y lectura independiente en área semanal.
  await page.waitForSelector("#oaf-ux42-slide-official",{state:"attached",timeout:12000});
  const intro=await page.evaluate(()=>{
    const c=document.querySelector("#inicio .oaf-ux42-carousel");
    return {count:c?.querySelectorAll(".oaf-ux42-slide").length,
      dots:c?.querySelectorAll(".oaf-ux42-dot").length,
      official:c?.querySelector("#oaf-ux15-enfen-exp")?.textContent,
      source:c?.querySelector(".oaf-ux15-source")?.textContent};
  });
  assert(intro.count===3&&intro.dots===3,"No hay tres láminas en carrusel: "+JSON.stringify(intro));
  assert(intro.official?.includes("Interpretación:")&&!intro.official?.includes("inundación"),
    "Interpretación ENFEN innecesariamente descriptiva: "+intro.official);
  await page.evaluate(()=>document.querySelector('#inicio button[aria-label="Próximos 7 días"]').click());
  assert(await page.locator("#oaf-ux42-slide-week").evaluate(x=>!x.hidden),"Carrusel no muestra 7 días");
  await page.evaluate(()=>document.querySelector('#inicio button[aria-label="Horizonte mensual"]').click());
  assert(await page.locator("#oaf-ux42-slide-month").evaluate(x=>!x.hidden),"Carrusel no muestra mensual");
  const pointForecast={daily:{time:["2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-10-31","2026-11-01","2026-11-02"],
    precipitation_sum:[0.03,0.08,0.12,0.16,0.2,0.14,0.01],temperature_2m_max:[24,25,26,27,28,27,25]}};
  const eraTime=[],eraRain=[],eraTemp=[];
  for(let y=1996;y<=2025;y++)for(let t=Date.UTC(y,0,1);t<Date.UTC(y+1,0,1);t+=86400000){
    eraTime.push(new Date(t).toISOString().slice(0,10));eraRain.push(0.1);eraTemp.push(26);
  }
  await page.route("https://api.open-meteo.com/**",async route=>{
    const url=route.request().url();
    if(url.includes("archive"))await route.fulfill({status:200,contentType:"application/json",
      body:JSON.stringify({latitude:-6.15,longitude:-79.71,daily:{time:eraTime,precipitation_sum:eraRain,temperature_2m_max:eraTemp}})});
    else await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(pointForecast)});
  });
  const formExists=await page.evaluate(()=>!!document.querySelector("#oaf-ux14-rf-semana #oaf-area-semanal form"));
  assert(formExists,"No hay coordenadas UTM/WGS84 en horizonte semanal");
  const outcome=await page.evaluate(()=>{
    const f=document.querySelector("#oaf-area-semanal form");
    f.elements.namedItem("lat").value="-6.15083";f.elements.namedItem("lon").value="-79.7142";
    f.elements.namedItem("name").value="Sector piloto";f.requestSubmit();
    return window.OAFTerritory.getActivePoint("semanal");
  });
  assert(outcome?.name==="Sector piloto"&&Math.abs(outcome.lat+6.15083)<.00001,"Consulta puntual semanal no guarda coordenadas");
  await page.waitForFunction(()=>document.querySelector("#oaf-ux14-weekchart svg")?.querySelectorAll("rect[role=img]").length>=14 && document.querySelector("#oaf-ux14-weekstatus")?.textContent.includes("ERA5:"),null,{timeout:22000});
  const plotInfo=await page.evaluate(()=>{
    const root=document.querySelector("#oaf-ux14-weekchart");
    const ticks=[...root.querySelectorAll('svg text[text-anchor="end"]')].map(x=>x.textContent);
    const desc=document.querySelector("#oaf-ux14-weekstatus")?.textContent;
    return {ticks,desc,polylines:root.querySelectorAll("svg polyline").length,
     bars:root.querySelectorAll("svg rect[role=img]").length,
     days:new Set([...root.querySelectorAll("svg rect[role=img]")].map(x=>x.getAttribute("aria-label").slice(0,10))).size};
  });
  assert(plotInfo.ticks.length>=4&&new Set(plotInfo.ticks).size===plotInfo.ticks.length,
    "Escala con etiquetas repetidas: "+JSON.stringify(plotInfo));
  assert(plotInfo.bars>=14&&plotInfo.days===7&&plotInfo.polylines===0,
    "El gráfico de siete días debe usar barras agrupadas, no líneas: "+JSON.stringify(plotInfo));
  assert(plotInfo.desc?.includes("Sector piloto")&&plotInfo.desc?.includes("ERA5"),
    "Análisis por coordenada/ERA5 no disponible: "+JSON.stringify(plotInfo));
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
  await page.waitForFunction(()=>!!window.OAFParcelas?.get?.("territorio"),null,{timeout:10000});
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
  // Prueba responsive: el visor debe aparecer ANTES del listado de capas en móvil.
  await page.setViewportSize({width:390,height:844});
  const responsive=await page.evaluate(()=>{
   const layout=document.querySelector("#oaf-ux29-territory .oaf-ux29-layout"),
    map=document.querySelector("#oaf-ux29-territory .oaf-ux29-mapcolumn"),
    side=document.querySelector("#oaf-ux29-territory .oaf-ux29-sidebar");
   return {columns:getComputedStyle(layout).gridTemplateColumns,
    mapOrder:getComputedStyle(map).order,sideOrder:getComputedStyle(side).order,
    cssLoaded:[...document.styleSheets].some(x=>x.href?.includes("oaf-visores-ux40.css"))};
  });
  assert(responsive.cssLoaded&&responsive.mapOrder==="-1"&&responsive.sideOrder==="1",
    "Mapa no prioritario en móvil: "+JSON.stringify(responsive));
  const importantErrors=errors.filter(x=>/ux39|oaf-parcel|oaf-area|Cannot read properties of undefined/.test(x));
  assert.deepEqual(importantErrors,[],"Errores JavaScript en los nuevos módulos: "+importantErrors.join(" | "));
  console.log("UX39 browser OK: visores integrados, independencia, GeoJSON, áreas, marcador y UTM WGS84");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
