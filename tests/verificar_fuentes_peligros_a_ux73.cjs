/* UX73 · comprobar respuesta de CENEPRED y capacidad de SENAMHI.
 * La API meteorológica Open-Meteo se verifica también con la misma combinación de variables.
 * Estos tests NO inventan datos ni garantizan disponibilidad ininterrumpida.
 */
"use strict";
const assert=require("node:assert/strict");
async function get(url,timeout=30000){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
 try{return await fetch(url,{signal:controller.signal,headers:{accept:"*/*"}})}
 finally{clearTimeout(timer)}
}
async function checkCENEPRED(){
 const base="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer";
 const p=new URLSearchParams({bbox:"-80.7,-7.25,-79.1,-5.4",bboxSR:"4326",imageSR:"4326",
  size:"900,550",format:"png32",transparent:"true",layers:"show:5090024",f:"json"});
 const response=await get(base+"/export?"+p,38000);
 const body=await response.text();
 if(!response.ok)throw Error("CENEPRED export HTTP "+response.status+": "+body.slice(0,220));
 const j=JSON.parse(body);
 if(j.error)throw Error("CENEPRED export: "+JSON.stringify(j.error));
 assert.ok(j.href,"CENEPRED no devolvió href PNG: "+body.slice(0,250));
 const png=await get(j.href,32000);
 const bytes=Buffer.from(await png.arrayBuffer()),signature=bytes.subarray(0,8).toString("hex");
 assert.equal(png.ok,true,"PNG de CENEPRED HTTP "+png.status);
 assert.equal(signature,"89504e470d0a1a0a","CENEPRED no entregó imagen PNG válida");
 return {source:base,layer:5090024,layerUrl:j.href,pngBytes:bytes.length,pngSignature:signature}
}
async function checkWMS(){
 const url="https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms?service=WMS&version=1.1.1&request=GetCapabilities";
 const response=await get(url,28000),body=await response.text();
 if(!response.ok)throw Error("IDESEP HTTP "+response.status);
 const names=[...body.matchAll(/<Name>([^<]+)<\/Name>/g)].map(x=>x[1]).filter(x=>x.includes("01_06"));
 return {source:url,layerNames:names.slice(0,20),size:body.length}
}
async function checkForecast(){
 const p=new URLSearchParams({latitude:"-6.15083,-5.98825",longitude:"-79.7142,-79.74723",
  daily:"precipitation_sum,temperature_2m_max",past_days:"30",forecast_days:"8",timezone:"America/Lima",cell_selection:"land"});
 const response=await get("https://api.open-meteo.com/v1/forecast?"+p,25000),data=await response.json();
 if(!response.ok||data.error)throw Error("Open-Meteo "+(data.reason||response.status));
 assert.equal(data.length,2);
 const date=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
 const result=data.map((r,i)=>{
  const ix=r.daily?.time?.indexOf(date);
  assert.ok(ix>=30&&ix+7<r.daily.time.length);
  assert.equal(r.daily.time.length,r.daily.precipitation_sum.length);
  assert.equal(r.daily.time.length,r.daily.temperature_2m_max.length);
  return {i,todayIndex:ix,days:r.daily.time.length,from:r.daily.time[0],to:r.daily.time.at(-1),lat:r.latitude,lon:r.longitude};
 });
 return result
}
(async()=>{
 const status={fecha:new Date().toISOString(),checks:{}};
 for(const [name,fun] of Object.entries({cenepred:checkCENEPRED,idesepWms:checkWMS,openMeteoDaily:checkForecast})){
  try{status.checks[name]={ok:true,data:await fun()}}
  catch(e){status.checks[name]={ok:false,error:String(e.message||e)}}
 }
 console.log(JSON.stringify(status,null,2));
 if(!status.checks.openMeteoDaily.ok)process.exitCode=1;
 // Official services may have temporary downtime; expose the result without substituting fabricated data.
})().catch(e=>{console.error(e);process.exitCode=1});
