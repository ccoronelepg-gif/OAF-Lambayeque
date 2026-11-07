/* UX73: polígonos de C y capas A, integridad geométrica y variables climáticas. */
"use strict";
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const read=p=>fs.readFileSync(p,"utf8");
const win={};
vm.runInNewContext(read("modelos/mapa_potencial_fitosanitario_ux72.js"),{window:win,Date,Math,Number,Array,Map,Set,Error});
vm.runInNewContext(read("modelos/poligonos_potenciales_ux73.js"),{window:win,Math,Number,Array,Map,Set,Error});
const geo=JSON.parse(read("datos/zonificacion_8n/limite_lambayeque_referencial.geojson"));
const rings=geo.features.map(f=>f.geometry.coordinates[0]);
const samples=win.OAFClimaticPotentialCore.sampleGrid(rings,{columns:10,rows:8,max:30});
const zones=win.OAFPotentialPolygons.zones(rings,samples,{step:.055,maxKm:28});
assert.equal(samples.length,30);
assert.ok(zones.length>=80&&zones.length<=800,"Cobertura aproximada debe tener polígonos");
assert.equal(win.OAFPotentialPolygons.geometryCheck(zones,rings),true);
assert.ok(zones.every(z=>z.geometry.type==="Polygon"&&z.geometry.coordinates[0].length===5));
assert.ok(zones.every(z=>samples.some(p=>p.id===z.pointId)));
assert.ok(zones.every(z=>z.representativeDistanceKm<=28));
let duplicate=new Set();
for(const z of zones){assert.ok(!duplicate.has(z.id));duplicate.add(z.id)}
const today="2026-11-06",days={time:[],precipitation_sum:[],temperature_2m_max:[]};
for(let d=-30;d<8;d++){
 let day=win.OAFClimaticPotentialCore.addDays(today,d);
 days.time.push(day);days.precipitation_sum.push(d<0?1:d>0?12:0);
 days.temperature_2m_max.push(d>0?34:31);
}
const document={readyState:"loading",addEventListener(){}};
const scope={window:{},document,Date,Math,Intl,Number,Array,Map,Set,URLSearchParams,Error};
vm.runInNewContext(read("assets/oaf-ux73-peligros-poligonos.js"),scope);
const evaluate=scope.window.OAFTerritoryClimateCore.evaluateRow;
const raw={latitude:-6.15,longitude:-79.71,daily:days};
for(const key of ["rainIntense","flood","drought","heat"]){
 const v=evaluate(raw,key,today);
 assert.equal(v.dateFrom,key==="drought"?"2026-10-07":"2026-11-07");
 assert.equal(v.dateTo,key==="drought"?"2026-11-05":"2026-11-13");
 assert.equal(v.value,key==="drought"?30:key==="heat"?34:12);
}
const bad={...raw,daily:{...days,temperature_2m_max:days.temperature_2m_max.slice()}};
bad.daily.temperature_2m_max[31]=null;
assert.throws(()=>evaluate(bad,"heat",today),/Día sin datos/);
const ux30=read("assets/oaf-ux30-territorio-unificado.js");
assert.match(ux30,/function heatWmsUrl\(bounds\)/);
assert.match(ux30,/5090024/);
assert.match(ux30,/polygon\[data-ux73a-zone\]/);
const idx=read("index.html"),sw=read("sw.js"),c=read("assets/oaf-ux35d-mapa-potencial.js");
for(const a of ["modelos/poligonos_potenciales_ux73.js","assets/oaf-ux73-peligros-poligonos.js","assets/oaf-ux73-poligonos.css"]){
 assert.ok(idx.includes(a+"?v=20261106-ux73"),"Falta en index "+a);
 assert.ok(sw.includes("./"+a),"Falta en PWA "+a);
}
assert.match(sw,/oaf-pwa-shell-2026-11-06-ux73/);
assert.match(c,/oaf-ux35d-zones/);
assert.match(c,/function polygonsGeoJSON/);
assert.match(c,/es_riesgo_calibrado:false/);
console.log(JSON.stringify({version:"UX73",samplePoints:samples.length,polygonZones:zones.length,allWithinApproxRegion:true,
 dailyRainMax:12,rain30Days:30,maxTemp7d:34,floodRasterReference:"CENEPRED 5090024",localEpidemiologicalRiskValidated:false,status:"pass"},null,2));
