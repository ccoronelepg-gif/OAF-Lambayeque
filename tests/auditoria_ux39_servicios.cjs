/* Auditoría de conectividad de fuentes efectivamente consumidas por OAF.
 * Una intersección vacía NO es ausencia de peligro. No se generan alertas.
 */
"use strict";
const fs=require("node:fs"),path=require("node:path");
const point={lat:-6.15083,lon:-79.7142};
const query=(extra={})=>new URLSearchParams({geometry:JSON.stringify({x:point.lon,y:point.lat,spatialReference:{wkid:4326}}),
 geometryType:"esriGeometryPoint",spatialRel:"esriSpatialRelIntersects",inSR:"4326",
 outFields:"*",returnGeometry:"false",f:"json",...extra});
const sources=[
 {fuente:"Open-Meteo · pronóstico de 7 días",timeout:20000,
  url:"https://api.open-meteo.com/v1/forecast?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),timezone:"America/Lima",forecast_days:"7",daily:"precipitation_sum,temperature_2m_max"}),
  valid:j=>Array.isArray(j.daily?.time)&&j.daily.time.length===7&&j.daily.precipitation_sum?.length===7&&j.daily.temperature_2m_max?.length===7,
  details:j=>({dias:j.daily.time.length,celda:[j.latitude,j.longitude]})},
 {fuente:"Open-Meteo Archive · ERA5-Land",timeout:20000,
  url:"https://archive-api.open-meteo.com/v1/archive?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),start_date:"2025-01-01",end_date:"2025-01-03",daily:"temperature_2m_mean,precipitation_sum",timezone:"America/Lima",models:"era5_land"}),
  valid:j=>Array.isArray(j.daily?.time)&&j.daily.time.length===3,
  details:j=>({modelo:"era5_land",dias:j.daily.time.length,celda:[j.latitude,j.longitude]})},
 {fuente:"Open-Meteo · ECMWF SEAS5 estacional",timeout:30000,
  url:"https://seasonal-api.open-meteo.com/v1/seasonal?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),models:"ecmwf_seas5_ensemble_mean",hourly:"precipitation,temperature_2m",forecast_days:"217",timezone:"America/Lima",precipitation_unit:"mm"}),
  valid:j=>Array.isArray(j.hourly?.time)&&j.hourly.time.length>0&&j.hourly.precipitation?.length===j.hourly.time.length&&j.hourly.temperature_2m?.length===j.hourly.time.length,
  details:j=>({modelo:"ecmwf_seas5_ensemble_mean",intervalos_6h:j.hourly.time.length,celda:[j.latitude,j.longitude],unidades:j.hourly_units})},
 {fuente:"CENEPRED SIGRID · susceptibilidad a inundaciones por lluvias fuertes · capa 5010502",timeout:20000,
  url:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5010502/query?"+query(),
  valid:j=>Array.isArray(j.features),
  details:j=>({entidades_intersectadas:j.features.length,escala:"según capa publicada"})},
 {fuente:"CENEPRED SIGRID · susceptibilidad a movimientos en masa · capa 5090022",timeout:20000,
  url:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090022/query?"+query(),
  valid:j=>Array.isArray(j.features),
  details:j=>({entidades_intersectadas:j.features.length,escala:"según capa publicada"})},
 {fuente:"INGEMMET · susceptibilidad a inundación fluvial 1:1 000 000 · capa 0",timeout:20000,
  url:"https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0/query?"+query(),
  valid:j=>Array.isArray(j.features),
  details:j=>({entidades_intersectadas:j.features.length,escala:"1:1 000 000"})}
];
async function check(item){
 const timestamp=new Date().toISOString(),controller=new AbortController(),id=setTimeout(()=>controller.abort(),item.timeout);
 try{
  const response=await fetch(item.url,{signal:controller.signal,headers:{accept:"application/json"}});
  if(!response.ok)throw Error("HTTP "+response.status);
  const body=await response.json();
  if(body.error)throw Error(body.error.message||"El servicio devolvió error");
  if(!item.valid(body))throw Error("Respuesta sin estructura o cobertura esperada");
  return {fuente:item.fuente,estado:"responde",fecha_utc:timestamp,metadatos:item.details(body)};
 }catch(error){return {fuente:item.fuente,estado:"no_verificable",fecha_utc:timestamp,motivo:String(error.message).slice(0,300)};}
 finally{clearTimeout(id);}
}
(async()=>{
 const results=await Promise.all(sources.map(check));
 const obj={revision:"UX49",fecha_utc:new Date().toISOString(),
  coordenada_muestra:point,
  alcance:"Disponibilidad técnica de las fuentes y respuesta de consulta puntual. No valida la precisión espacial, peligros, probabilidad ni pronóstico de una parcela.",
  fuentes:results};
 fs.writeFileSync(path.resolve("ux39-auditoria-servicios.json"),JSON.stringify(obj,null,2)+"\n");
 for(const r of results)console.log(r.fuente,":",r.estado,r.motivo||JSON.stringify(r.metadatos));
 const summary=process.env.GITHUB_STEP_SUMMARY;
 if(summary)fs.appendFileSync(summary,["## Auditoría UX49: servicios de datos","",
  ...results.map(r=>"- "+r.fuente+": **"+r.estado+"**"+(r.motivo?" ("+r.motivo+")":"")),
  "","Una consulta sin intersección no equivale a ausencia de peligro. La conectividad tampoco valida la exactitud temática de la capa."].join("\n"));
})().catch(error=>{console.error(error);process.exitCode=1});
