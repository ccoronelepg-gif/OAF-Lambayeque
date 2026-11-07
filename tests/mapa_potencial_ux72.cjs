/* OAF UX72: matemáticas, georreferencia y conexión real de la capa fitosanitaria.
 * node tests/mapa_potencial_ux72.cjs [--live]
 */
"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict"),vm=require("node:vm");
const read=p=>fs.readFileSync(p,"utf8");
const window={};vm.runInNewContext(read("modelos/mapa_potencial_fitosanitario_ux72.js"),{window,Date,Math,Number,Array,Map,Set,Error}, {filename:"mapa_potencial_fitosanitario_ux72.js"});
const core=window.OAFClimaticPotentialCore,geo=JSON.parse(read("datos/zonificacion_8n/limite_lambayeque_referencial.geojson"));
const rings=geo.features.map(x=>x.geometry.coordinates[0]);
const pts=core.sampleGrid(rings,{columns:10,rows:8,max:30});
assert.equal(pts.length,30,"La malla debe producir 30 puntos dentro del contorno");
assert.ok(pts.every(p=>core.pointInRegion(p.lon,p.lat,rings)));
const hourly={time:[],temperature_2m:[],relative_humidity_2m:[]},today="2026-11-06";
for(let d=0;d<8;d++){
 const date=core.addDays(today,d);
 for(let h=0;h<24;h++){
  hourly.time.push(date+"T"+String(h).padStart(2,"0")+":00");
  hourly.temperature_2m.push(25);
  hourly.relative_humidity_2m.push((d===1&&h>=21)||(d===2&&h<=3)?96:75);
 }
}
const b=core.evaluatePoint(hourly,"botrytis",today);
assert.equal(b.episodes,1,"Episodio de HR a través de medianoche");
assert.equal(b.longestStreak,7);
assert.equal(b.hoursOver90,7);
assert.equal(b.class,"un_episodio");
const m=core.evaluatePoint(hourly,"ceratitis",today);
assert.ok(Math.abs(m.degreesDaysMin-111.3)<1e-8);
assert.ok(Math.abs(m.degreesDaysMax-115.71)<1e-8);
assert.equal(m.class,"sin_categoria_de_riesgo");
assert.equal(m.validatedLocally,false);
assert.ok(m.degreesDaysMax>m.degreesDaysMin,"Ambas bases térmicas deben reflejar sensibilidad");
const absent={...hourly,relative_humidity_2m:hourly.relative_humidity_2m.slice()};
absent.relative_humidity_2m[35]=null;
assert.throws(()=>core.evaluatePoint(absent,"botrytis",today),/Falta hora/);
const badTemp={...hourly,temperature_2m:hourly.temperature_2m.slice()};
for(let i=24;i<48;i++)badTemp.temperature_2m[i]=35;
assert.throws(()=>core.evaluatePoint(badTemp,"ceratitis",today),/fuera del intervalo 15–30/);
const ones=pts.slice(0,2);
const validRaw=[{latitude:ones[0].lat,longitude:ones[0].lon,hourly},
 {latitude:ones[1].lat,longitude:ones[1].lon,hourly:{...hourly,relative_humidity_2m:hourly.relative_humidity_2m.slice(0,-1)}}];
const batches=core.assessBatch(validRaw,ones,"botrytis",today);
assert.equal(batches.length,2);
assert.equal(batches[0].indicator.episodes,1);
assert.equal(batches[1].indicator,null);
assert.ok(batches[1].error);
const html=read("index.html"),sw=read("sw.js"),ui=read("assets/oaf-ux35d-mapa-potencial.js");
const base=read("assets/oaf-ux35-escenarios-multicapas.js");
assert.match(html,/modelos\/mapa_potencial_fitosanitario_ux72\.js\?v=20261106-ux72/);
assert.match(html,/assets\/oaf-ux35d-mapa-potencial\.js\?v=20261106-ux72/);
assert.match(html,/assets\/oaf-ux35d-mapa-potencial\.css\?v=20261106-ux72/);
assert.ok(html.indexOf("modelos/mapa_potencial_fitosanitario_ux72.js")<html.indexOf("assets/oaf-ux35d-mapa-potencial.js"));
assert.match(sw,/oaf-pwa-shell-2026-11-06-ux72/);
for(const asset of ["modelos/mapa_potencial_fitosanitario_ux72.js","assets/oaf-ux35d-mapa-potencial.js","assets/oaf-ux35d-mapa-potencial.css"]){
 assert.ok(sw.includes("./"+asset),"Falta caché "+asset);
}
assert.match(base,/oaf:scenario-map-redrawn/,"Redibujo base debe notificar al overlay");
assert.match(ui,/oaf:scenario-map-redrawn/);
assert.match(ui,/function paint\(/);
assert.match(ui,/function toGeoJSON\(/);
assert.match(ui,/es_riesgo_calibrado:false/);
assert.match(ui,/if\(!res\.ok\)/);
console.log(JSON.stringify({version:"UX72",status:"core_gis_y_meteo_pruebas_positivas",samplePoints:pts.length,humidityEpisodes:b.episodes,streakHours:b.longestStreak,gddBase91:m.degreesDaysMin,gddBase847:m.degreesDaysMax,localRiskValidated:false},null,2));
async function checkLive(){
 const params=new URLSearchParams({
  latitude:pts.map(x=>x.lat).join(","),longitude:pts.map(x=>x.lon).join(","),
  timezone:"America/Lima",hourly:"temperature_2m,relative_humidity_2m",
  forecast_days:"8",cell_selection:"land"
 });
 const url="https://api.open-meteo.com/v1/forecast?"+params;
 let lastError;
 for(let tries=0;tries<3;tries++){
  const c=new AbortController(),timer=setTimeout(()=>c.abort(),45000);
  try{
   const response=await fetch(url,{signal:c.signal});
   if(!response.ok)throw Error("HTTP "+response.status);
   const body=await response.json();
   if(body.error)throw Error(body.reason||"Error del proveedor");
   assert.ok(Array.isArray(body)&&body.length===pts.length,"La API de 30 puntos debe devolver 30 series");
   for(const [i,item] of body.entries()){
    assert.ok(Number.isFinite(item.latitude)&&Number.isFinite(item.longitude),"Celda faltante "+i);
    assert.equal(item.hourly.time.length,item.hourly.temperature_2m.length);
    assert.equal(item.hourly.time.length,item.hourly.relative_humidity_2m.length);
    assert.ok(item.hourly.time.length>=8*24);
    assert.ok(item.hourly.temperature_2m.every(v=>v===null||Number.isFinite(v)));
    assert.ok(item.hourly.relative_humidity_2m.every(v=>v===null||Number.isFinite(v)));
   }
   const today=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
   const b=core.assessBatch(body,pts,"botrytis",today);
   const m=core.assessBatch(body,pts,"ceratitis",today);
   const countB=b.filter(x=>x.indicator).length,countM=m.filter(x=>x.indicator).length;
   console.log(JSON.stringify({version:"UX72",provider:"Open-Meteo Forecast multi-location",requested:pts.length,returned:body.length,validHumidity:countB,validThermal:countM,date:today,firstLocation:body[0].latitude+","+body[0].longitude},null,2));
   assert.ok(countB>0,"No se recibieron condiciones HR horarias completas");
   // Grados-día pueden no ser aplicables fuera del intervalo experimental, p.ej. la sierra.
   return
  }catch(e){lastError=e;await new Promise(resolve=>setTimeout(resolve,1000*(tries+1)))}
  finally{clearTimeout(timer)}
 }
 throw lastError
}
if(process.argv.includes("--live"))checkLive().catch(e=>{console.error(e);process.exitCode=1});
