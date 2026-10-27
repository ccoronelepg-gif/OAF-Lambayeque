/* Auditoría periódica orientativa. No modifica datos ni genera alertas meteorológicas. */
"use strict";
const fs=require("node:fs"),path=require("node:path");
const urls=[
 {fuente:"Open-Meteo Archive ERA5-Land",url:"https://archive-api.open-meteo.com/v1/archive?latitude=-6.15083&longitude=-79.7142&start_date=2025-01-01&end_date=2025-01-03&daily=temperature_2m_mean,precipitation_sum&timezone=America%2FLima&models=era5_land"},
 {fuente:"CENEPRED SIGRID · capa 5090024",url:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024?f=pjson"},
 {fuente:"INGEMMET · susceptibilidad fluvial 1:1 000 000",url:"https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0?f=pjson"}
];
async function check({fuente,url}){
 const timestamp=new Date().toISOString(),controller=new AbortController(),id=setTimeout(()=>controller.abort(),20000);
 try{
  const result=await fetch(url,{signal:controller.signal,headers:{"accept":"application/json"}});
  if(!result.ok)throw Error("HTTP "+result.status);
  const body=await result.json();
  if(body.error)throw Error(body.error.message||"geoservicio indicó error");
  const data=fuente.startsWith("Open")?Array.isArray(body.daily?.time)&&body.daily.time.length===3:
   Boolean(body.name||body.type||body.capabilities);
  if(!data)throw Error("Respuesta sin fechas o metadatos esperados");
  return {fuente,estado:"responde",fecha_utc:timestamp,metadatos:fuente.startsWith("Open")?{modelo:"era5_land",dias:body.daily.time.length,celda:[body.latitude,body.longitude]}:{nombre:body.name,tipo:body.type,version:body.currentVersion}};
 }catch(e){return {fuente,estado:"no_verificable",fecha_utc:timestamp,motivo:String(e.message).slice(0,300)};}
 finally{clearTimeout(id);}
}
(async()=>{
 const states=await Promise.all(urls.map(check));
 const obj={revision:"UX39",fecha_utc:new Date().toISOString(),alcance:"Disponibilidad técnica de tres servicios; NO validación de sus peligros ni pronóstico de parcela.",fuentes:states};
 const target=path.resolve("ux39-auditoria-servicios.json");fs.writeFileSync(target,JSON.stringify(obj,null,2)+"\n");
 for(const r of states)console.log(r.fuente,":",r.estado,r.motivo||"");
 const summary=process.env.GITHUB_STEP_SUMMARY;
 if(summary)fs.appendFileSync(summary,["## Auditoría UX39: disponibilidad de fuentes","",...states.map(r=>"- "+r.fuente+": **"+r.estado+"**"+(r.motivo?" ("+r.motivo+")":"")),"","Nota: Una capa que no responde no equivale a riesgo ausente."].join("\n"));
})().catch(e=>{console.error(e);process.exitCode=1});
