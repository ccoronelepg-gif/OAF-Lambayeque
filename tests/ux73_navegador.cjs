/* UX73: prueba del mapa REAL A y C con API Open-Meteo simulada,
 * para separar visualización de disponibilidad de terceros. */
"use strict";
const assert=require("node:assert/strict"),{chromium}=require("playwright"),fs=require("node:fs");
const fmt=x=>String(x).padStart(2,"0");
const date=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
function shift(today,n){const d=new Date(today+"T12:00:00Z");d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)}
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1000},acceptDownloads:true});
  const pageErrors=[];page.on("pageerror",e=>pageErrors.push(e.message));
  page.on("console",msg=>{if(msg.type()==="error")console.error("PAGE_CONSOLE_ERROR",msg.text())});
  page.on("dialog",async dialog=>{console.error("PAGE_DIALOG",dialog.message());await dialog.dismiss()});
  await page.route("https://sig.cenepred.gob.pe/**",route=>route.abort("failed"));
  await page.route("https://idesep.senamhi.gob.pe/**",route=>route.abort("failed"));
  let dailyCalls=0,hourlyCalls=0;
  await page.route("https://api.open-meteo.com/**",async route=>{
   const u=new URL(route.request().url()),latitude=u.searchParams.get("latitude")||"";
   if(!latitude.includes(",")){await route.continue();return}
   const lats=latitude.split(",").map(Number),lons=(u.searchParams.get("longitude")||"").split(",").map(Number);
   assert.equal(lats.length,lons.length);
   const today=date(),response=lats.map((lat,i)=>{
    if(u.searchParams.has("daily")){
     const daily={time:[],precipitation_sum:[],temperature_2m_max:[]};
     for(let d=-30;d<8;d++){
      daily.time.push(shift(today,d));
      daily.precipitation_sum.push(d>0?12:1);
      daily.temperature_2m_max.push(34);
     }
     return {latitude:lat,longitude:lons[i],daily}
    }
    const hourly={time:[],relative_humidity_2m:[],temperature_2m:[]};
    for(let d=0;d<8;d++)for(let h=0;h<24;h++){
     hourly.time.push(shift(today,d)+"T"+fmt(h)+":00");
     hourly.relative_humidity_2m.push(d===2&&h>=4&&h<12?95:75);
     hourly.temperature_2m.push(26);
    }
    return {latitude:lat,longitude:lons[i],hourly};
   });
   if(u.searchParams.has("daily"))dailyCalls++;else hourlyCalls++;
   await route.fulfill({status:200,contentType:"application/json",headers:{"access-control-allow-origin":"*"},body:JSON.stringify(response)});
  });
  await page.goto("http://127.0.0.1:8765/index.html",{waitUntil:"domcontentloaded",timeout:90000});
  await page.waitForSelector("#oaf-ux30-layer-tree",{state:"attached",timeout:45000});
  await page.waitForFunction(()=>window.OAFTerritoryClimate?.getState()?.points===30&&window.OAFTerritoryClimate?.getState()?.zones>0,null,{timeout:45000});
  let summary=await page.evaluate(()=>({mode:window.OAFTerritoryClimate.getState().mode,zones:document.querySelectorAll("#oaf-ux73a-zones polygon").length,status:document.getElementById("oaf-ux73a-status")?.textContent}));
  assert.equal(summary.mode,"flood","La capa de inundaciones está activa por defecto");
  assert.ok(summary.zones>30,"La inundación debe presentar contexto de lluvia aunque falle CENEPRED, con aviso explícito");
  assert.match(await page.locator("#oaf-ux73a-legend").innerText(),/NO.*susceptibilidad|NO.*riesgo|NO.*peligro/i);
  await page.evaluate(()=>{
   const el=document.querySelector('[data-ux30-layer="rainIntense"]');
   el.checked=true;el.dispatchEvent(new Event("change",{bubbles:true}))
  });
  await page.waitForFunction(()=>window.OAFTerritoryClimate?.getState()?.mode==="rainIntense"&&document.querySelectorAll("#oaf-ux73a-zones polygon").length>30,null,{timeout:25000});
  assert.match(await page.locator("#oaf-ux73a-legend").innerText(),/precipitación/i);
  await page.evaluate(()=>{
   const el=document.querySelector('[data-ux30-layer="drought"]');
   el.checked=true;el.dispatchEvent(new Event("change",{bubbles:true}))
  });
  await page.waitForFunction(()=>window.OAFTerritoryClimate?.getState()?.mode==="drought"&&document.querySelectorAll("#oaf-ux73a-zones polygon").length>30,null,{timeout:25000});
  assert.match(await page.locator("#oaf-ux73a-legend").innerText(),/30 días/i);
  await page.evaluate(()=>{
   const el=document.querySelector('[data-ux30-layer="heat"]');
   el.checked=true;el.dispatchEvent(new Event("change",{bubbles:true}))
  });
  await page.waitForFunction(()=>window.OAFTerritoryClimate?.getState()?.mode==="heat"&&document.querySelectorAll("#oaf-ux73a-zones polygon").length>30,null,{timeout:25000});
  assert.match(await page.locator("#oaf-ux73a-legend").innerText(),/Temperatura máxima/i);
  // UX74 - Exportacion real de PDF bajo navegador (datos simulados SOLO en pruebas).
  async function verifyPdf(selector,tag){
    console.log("PDF_VERIFY_START",selector,tag,await page.locator(selector).isEnabled());
    let download;
    try{[download]=await Promise.all([page.waitForEvent("download",{timeout:15000}),page.locator(selector).evaluate(button=>button.click())]);}
    catch(e){console.log("PDF_DOWNLOAD_DEBUG",await page.evaluate(()=>({debug:window.__pdfDebug,reportApi:typeof window.OAFReportPDF?.export,button:document.querySelector("#oaf-ux74a-points")?.outerHTML.slice(0,600)})));throw e;}
    assert.ok(download.suggestedFilename().endsWith(".pdf"),"El enlace debe producir PDF y no GeoJSON");
    const file=await download.path(),raw=fs.readFileSync(file);
    assert.equal(raw.subarray(0,8).toString("ascii"),"%PDF-1.4");
    assert.ok(raw.toString("latin1").includes("startxref")&&raw.toString("latin1").includes("%%EOF"));
    assert.ok(raw.length>10000,"PDF incompleto");
    fs.copyFileSync(file,"/tmp/oaf_ux74_"+tag+".pdf");
    return {file:download.suggestedFilename(),bytes:raw.length};
  }
  await page.evaluate(()=>{
    window.__pdfDebug=[];
    const original=window.OAFReportPDF.export;
    window.OAFReportPDF.export=async(...args)=>{
      window.__pdfDebug.push("export: "+JSON.stringify(args));
      try{const result=await original(...args);window.__pdfDebug.push("result "+JSON.stringify(result));return result;}
      catch(e){window.__pdfDebug.push("error "+e.stack);throw e;}
    };
    document.querySelector("#oaf-ux74a-points").addEventListener("click",()=>window.__pdfDebug.push("button click event"));
  });
  console.log("PDF_MODULE_DIAGNOSTIC",await page.evaluate(()=>({pdfModule:typeof window.OAFReportPDF,apiA:typeof window.OAFTerritoryClimate?.toGeoJSON,geoA:window.OAFTerritoryClimate?.toGeoJSON?.()?.features?.length,scripts:[...document.scripts].filter(x=>x.src.includes("ux74")).map(x=>x.src),pageErrors:[]})),pageErrors);
  assert.ok(await page.locator("#oaf-ux74a-points").isEnabled());
  assert.ok(await page.locator("#oaf-ux74a-polygons").isEnabled());
  const aPoints=await verifyPdf("#oaf-ux74a-points","a_puntos");
  const aZones=await verifyPdf("#oaf-ux74a-polygons","a_poligonos");
  assert.ok(pageErrors.every(e=>!e.includes("heatWmsUrl")),"El mapa no debe arrojar ReferenceError por WMS");
  await page.screenshot({path:"/tmp/oaf_ux73_peligros_a.png",fullPage:true});
  // Activar módulo C dentro del portal, sin fixture.
  await page.waitForSelector("#oaf-ux35c-enable",{state:"attached",timeout:45000});
  await page.evaluate(()=>{
   document.getElementById("oaf-ux35c-crop").value="arandano";
   document.getElementById("oaf-ux35c-crop").dispatchEvent(new Event("change",{bubbles:true}));
   document.getElementById("oaf-ux35c-enable").checked=true;
   document.getElementById("oaf-ux35c-enable").dispatchEvent(new Event("change",{bubbles:true}));
  });
  await page.waitForFunction(()=>window.OAFPotentialLayer?.getState()?.valid===30&&window.OAFPotentialLayer?.getState()?.polygons>30,null,{timeout:35000});
  const collection=await page.evaluate(()=>window.OAFPotentialLayer.polygonsGeoJSON());
  assert.ok(collection.features.length>30);
  assert.ok(collection.features.every(f=>f.geometry.type==="Polygon"&&f.properties.es_riesgo_calibrado===false));
  assert.ok(await page.locator("#oaf-ux35d-polygons-export").isEnabled());
  assert.equal(await page.locator("#oaf-ux35d-zones polygon").count(),collection.features.length);
  const cPoints=await verifyPdf("#oaf-ux35d-export","c_puntos");
  const cZones=await verifyPdf("#oaf-ux35d-polygons-export","c_poligonos");
  await page.screenshot({path:"/tmp/oaf_ux73_fitosanitario_c.png",fullPage:true});
  console.log(JSON.stringify({version:"UX73",page:"index.html integral",
   floodContextPolygons:summary.zones,areaA_modes:["flood","rainIntense","drought","heat"],
   pdfDownloads:{aPoints,aZones,cPoints,cZones},
   fitosanitaryPolygons:collection.features.length,dailyCalls,hourlyCalls,
   geojsonNoValidatedRisks:collection.features.every(x=>x.properties.es_riesgo_calibrado===false),
   heatWmsReferenceError:pageErrors.some(x=>x.includes("heatWmsUrl")),
   status:"full_browser_passed"},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
