/* OAF UX45 · Auditoría de disponibilidad pública, sin publicar cifras ni llaves.
 * No confundir disponibilidad HTTP del proveedor con validación científica.
 */
"use strict";
const fs=require("node:fs");
const sources=[
 {name:"Open-Meteo pronóstico 7 días",url:"https://api.open-meteo.com/v1/forecast?latitude=-6.77&longitude=-79.84&timezone=America%2FLima&forecast_days=7&daily=precipitation_sum%2Ctemperature_2m_max",expected:"daily"},
 {name:"ERA5 archivo histórico",url:"https://archive-api.open-meteo.com/v1/archive?latitude=-6.77&longitude=-79.84&start_date=2026-10-10&end_date=2026-10-17&timezone=America%2FLima&models=era5&daily=precipitation_sum%2Ctemperature_2m_max",expected:"daily"},
 {name:"ECMWF SEAS5 estacional 6h",url:"https://seasonal-api.open-meteo.com/v1/seasonal?latitude=-6.77&longitude=-79.84&timezone=America%2FLima&forecast_days=217&models=ecmwf_seas5_ensemble_mean&hourly=precipitation%2Ctemperature_2m",expected:"hourly"},
 {name:"Comunicado ENFEN 18-2026",url:"https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-18-2026/",expected:"html"}
];
async function check(source){
 const started=Date.now(),result={fuente:source.name,fecha:new Date().toISOString()};
 try{
  const response=await fetch(source.url,{headers:{"User-Agent":"OAF-Lambayeque-Ux45/1.0 (+scientific-integrity-audit)"},signal:AbortSignal.timeout(20000)});
  result.http=response.status;
  result.latencia_ms=Date.now()-started;
  if(!response.ok){result.estado="NO_DISPONIBLE";return result;}
  if(source.expected==="html"){result.estado="RESPONDE_HTTP";return result;}
  const json=await response.json(),series=json[source.expected];
  result.n_muestras=series?.time?.length||0;
  if(source.expected==="hourly"){
   result.variables=Array.isArray(series?.precipitation)&&Array.isArray(series?.temperature_2m);
   result.unidades=[json.hourly_units?.precipitation,json.hourly_units?.temperature_2m];
   const months=["2026-11","2026-12","2027-01","2027-02","2027-03","2027-04"];
   result.cobertura_mensual=months.map(month=>{
    const entries=series.time.filter(t=>typeof t==="string"&&t.startsWith(month+"-"));
    const [y,m]=month.split("-").map(Number);
    const required=new Date(Date.UTC(y,m,0)).getUTCDate()*4;
    return {mes:month,muestras:entries.length,requeridas:required,completo:entries.length===required};
   });
   result.meses_completos=result.cobertura_mensual.filter(m=>m.completo).length;
   result.estado=result.n_muestras>=8&&result.variables?"DATOS_COMPATIBLES":"ESTRUCTURA_INCOMPATIBLE";
  }else{
   result.variables=Array.isArray(series?.precipitation_sum)&&Array.isArray(series?.temperature_2m_max);
   result.estado=result.n_muestras>=7&&result.variables?"DATOS_COMPATIBLES":"ESTRUCTURA_INCOMPATIBLE";
  }
 }catch(err){result.estado="NO_VERIFICABLE";result.motivo=err.name==="TimeoutError"?"Tiempo de espera superado":String(err.message||err).slice(0,140);}
 return result;
}
(async()=>{
 const items=await Promise.all(sources.map(check));
 const report={fecha:new Date().toISOString(),ambito:"Comprobación desde GitHub Actions; no comprueba disponibilidad en el teléfono del usuario",servicios:items};
 fs.mkdirSync("artifacts",{recursive:true});
 fs.writeFileSync("artifacts/auditoria_ux45_fuentes_live.json",JSON.stringify(report,null,2)+"\n");
 console.log(JSON.stringify(report,null,2));
 // A network/API outage is not a passing result and not a deployment blocker:
 // it remains explicitly NO_DISPONIBLE / NO_VERIFICABLE in the public audit artifact.
})().catch(err=>{console.error(err);process.exitCode=1});
