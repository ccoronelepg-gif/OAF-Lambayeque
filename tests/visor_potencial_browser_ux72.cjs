/* UX72: prueba navegador de activación, carga y desactivación de la capa C.
 * Datos meteorológicos REPRODUCIBLES simulados en navegador.
 * La API real se valida separadamente en mapa_potencial_ux72.cjs --live.
 */
"use strict";
const assert=require("node:assert/strict");
const {chromium}=require("playwright");
const fmt=n=>String(n).padStart(2,"0");
const localToday=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
const addDays=(t,d)=>{const x=new Date(t+"T12:00:00Z");x.setUTCDate(x.getUTCDate()+d);return x.toISOString().slice(0,10)};
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:1000},acceptDownloads:true});
  const jsErrors=[];page.on("pageerror",error=>jsErrors.push(error.message));
  let intercepted=0;
  await page.route("https://api.open-meteo.com/**",async route=>{
   intercepted++;
   const u=new URL(route.request().url()),lats=(u.searchParams.get("latitude")||"").split(",").map(Number),
    lons=(u.searchParams.get("longitude")||"").split(",").map(Number),today=localToday(),data=[];
   assert.equal(lats.length,lons.length);
   for(let i=0;i<lats.length;i++){
    const hourly={time:[],temperature_2m:[],relative_humidity_2m:[]};
    for(let day=0;day<8;day++)for(let h=0;h<24;h++){
     hourly.time.push(addDays(today,day)+"T"+fmt(h)+":00");
     hourly.temperature_2m.push(25);
     hourly.relative_humidity_2m.push(day===2&&h>=3&&h<12?95:70);
    }
    data.push({latitude:lats[i],longitude:lons[i],hourly})
   }
   await route.fulfill({status:200,contentType:"application/json",
    headers:{"access-control-allow-origin":"*"},body:JSON.stringify(data)});
  });
  await page.goto("http://127.0.0.1:8765/tests/fixtures/ux72-visor.html",{waitUntil:"domcontentloaded",timeout:60000});
  await page.waitForSelector("#oaf-ux35c-enable",{timeout:15000});
  await page.locator("#oaf-ux35c-enable").check();
  await page.waitForFunction(()=>window.OAFPotentialLayer?.getState().valid===30,null,{timeout:20000});
  assert.equal(await page.locator("#oaf-ux35d-points circle[data-ux35d-point]").count(),30);
  assert.ok(await page.locator("#oaf-ux35d-export").isEnabled());
  assert.match(await page.locator("#oaf-ux35d-legend").innerText(),/Botrytis/);
  await page.locator("#oaf-ux35d-points circle[data-ux35d-point]").first().click();
  assert.ok(await page.locator("#oaf-ux35d-point-detail").isVisible());
  assert.match(await page.locator("#oaf-ux35d-point-detail").innerText(),/episodios/i);
  const b=await page.evaluate(()=>window.OAFPotentialLayer.toGeoJSON());
  assert.equal(b.features.length,30);
  assert.ok(b.features.every(f=>f.type==="Feature"&&f.geometry.type==="Point"&&f.properties.es_riesgo_calibrado===false));
  await page.screenshot({path:"/tmp/oaf_ux72_botrytis.png",fullPage:true});
  await page.locator("#oaf-ux35c-crop").selectOption("mango");
  await page.waitForFunction(()=>window.OAFPotentialLayer?.getState().model==="ceratitis"&&window.OAFPotentialLayer?.getState().valid===30,null,{timeout:20000});
  assert.match(await page.locator("#oaf-ux35d-legend").innerText(),/Ceratitis/i);
  await page.locator("#oaf-ux35d-points circle[data-ux35d-point]").first().click();
  assert.match(await page.locator("#oaf-ux35d-point-detail").innerText(),/Grados.día/i);
  const c=await page.evaluate(()=>window.OAFPotentialLayer.toGeoJSON());
  assert.ok(c.features.every(f=>f.properties.grados_dia_base_9_1>0&&f.properties.grados_dia_base_8_47>0));
  await page.screenshot({path:"/tmp/oaf_ux72_ceratitis.png",fullPage:true});
  await page.locator("#oaf-ux35c-enable").uncheck();
  assert.equal(await page.locator("#oaf-ux35d-points circle[data-ux35d-point]").count(),0);
  assert.ok(intercepted>=2);
  assert.deepEqual(jsErrors,[]);
  console.log(JSON.stringify({version:"UX72",browser:"Chromium",source:"fixture + deterministic mock (real API independently tested)",
   botrytisPoints:30,ceratitisPoints:30,GeoJSONFeatures:30,
   toggleOnAndOff:true,pointSelection:true,pageErrors:jsErrors,networkRequests:intercepted,status:"visual_interaction_passed"},null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
