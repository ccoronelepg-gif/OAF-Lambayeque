/* UX69 · Smoke de proveedores meteorológicos reales del módulo C.
 * No genera ni guarda datos; falla ante API incompleta.
 * Ejecutar: node tests/consulta_meteorologica_ux69.cjs
 */
"use strict";
const assert=require("node:assert/strict");
const sites=[{name:"Motupe",lat:-6.15083,lon:-79.7142},{name:"Olmos",lat:-5.98825,lon:-79.74723}];
async function check(url,scope){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
 try{
  const response=await fetch(url,{signal:controller.signal,headers:{accept:"application/json"}});
  assert.equal(response.ok,true,scope+" respondió HTTP "+response.status);
  const data=await response.json();
  assert.equal(Boolean(data.error),false,data.reason||scope+": error del proveedor");
  assert.ok(Number.isFinite(data.latitude)&&Number.isFinite(data.longitude),scope+": coordenadas no válidas");
  const hourly=data.hourly;
  assert.ok(Array.isArray(hourly?.time)&&hourly.time.length>0,scope+": sin serie temporal");
  assert.equal(hourly.time.length,hourly.temperature_2m?.length,scope+": temperatura no alineada");
  assert.ok(hourly.temperature_2m.every(x=>typeof x==="number"&&Number.isFinite(x)),scope+": temperatura faltante");
  return {scope,modelledLatitude:data.latitude,modelledLongitude:data.longitude,hours:hourly.time.length,
    from:hourly.time[0],to:hourly.time[hourly.time.length-1]};
 }finally{clearTimeout(timer)}
}
(async()=>{
 const results=[];
 for(const site of sites){
  const params=new URLSearchParams({latitude:String(site.lat),longitude:String(site.lon),
    hourly:"temperature_2m",timezone:"America/Lima",forecast_days:"8",past_days:"2"});
  results.push(await check("https://api.open-meteo.com/v1/forecast?"+params,site.name+" pronóstico térmico"));
 }
 const historical=new URLSearchParams({latitude:String(sites[0].lat),longitude:String(sites[0].lon),
  start_date:"2025-10-01",end_date:"2025-10-03",hourly:"temperature_2m",
  timezone:"America/Lima",models:"era5_land"});
 results.push(await check("https://archive-api.open-meteo.com/v1/archive?"+historical,"Motupe ERA5-Land histórico"));
 console.log(JSON.stringify({revision:"UX69",state:"proveedores_responden_con_series_numericas_reales",results},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
