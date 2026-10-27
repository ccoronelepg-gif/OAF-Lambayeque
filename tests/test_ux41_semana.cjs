/* UX41 · QA reproducible: ERA5 aporta referencia histórica y RF no se mueve de fecha. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const root=path.join(__dirname,".."),read=p=>fs.readFileSync(path.join(root,p),"utf8");
const src=read("assets/oaf-ux15-rf-salidas.js"),structure=read("assets/oaf-ux14-reorganizacion.js");
const area=read("assets/oaf-territorio-compartido.js"),index=read("index.html");
for(const s of [src,structure,area])new Function(s);
assert(src.includes("era5Reference("),"Falta línea ERA5 histórica en gráfico semanal");
assert(src.includes("tickText(v)"),"El eje semanal no utiliza escala decimal sin etiquetas repetidas");
assert(area.includes("semanal:"),"Falta modo independiente de coordenadas semanales");
assert(read("assets/oaf-ux42-portada-carrusel.js").includes("15000"),"Carrusel no utiliza 15 segundos");
assert(src.includes("models:\"era5\""),"Falta origen de ERA5");
assert(src.includes("start_date:\"1996-01-01\",end_date:\"2025-12-31\""),"Referencia temporal ERA5 no sustentada");
assert(src.includes("map.has(d)"),"RF debe emparejarse exclusivamente por fecha válida");
assert(!area.includes("#oaf-ux14-rf-semana,#oaf-anomaly-panel"),"El gráfico semanal sigue oculto");
assert(structure.includes('section("Predicción a siete días'),"No se creó la cabecera del cuadro semanal");
assert(structure.indexOf('const live=section("Predicción a siete días')<structure.indexOf('const month=section("Horizonte mensual'),"Gráfico no precede al mensual");
assert(index.includes("oaf-ux15-rf-salidas.js?v=20261027-ux43"),"No se actualizó script semanal en web");
assert(index.includes("oaf-ux14-reorganizacion.js?v=20261027-ux43"),"No se actualizó estructura semanal en web");
assert(read("sw.js").includes("oaf-pwa-shell-2026-10-27-ux43"),"Cache PWA no versionado");
const start=src.indexOf("/* Línea de base meteorológica"),end=src.indexOf("function week(){",start);
assert(start>=0&&end>start,"Falta cálculo de promedio por día del año");
const times=[],rain=[],temp=[];
for(let y=1996;y<=2025;y++){
 for(let t=Date.UTC(y,0,1);t<Date.UTC(y+1,0,1);t+=86400000){
  const d=new Date(t).toISOString().slice(0,10);times.push(d);
  rain.push(d.slice(5)==="10-27"?(y===2025?100:5):1);
  temp.push(d.slice(5)==="10-27"?(y===2025?35:25):24);
 }
}
assert(times.length>10000);
let calls=0;
const fakeFetch=async(url)=>{
 calls++;const u=new URL(url);
 assert.equal(u.hostname,"archive-api.open-meteo.com");
 assert.equal(u.searchParams.get("models"),"era5");
 return {ok:true,json:async()=>({latitude:-6.76,longitude:-79.85,daily:{time:times,precipitation_sum:rain,temperature_2m_max:temp}})};
};
const construct=new Function("fetch","AbortController","URLSearchParams","setTimeout","clearTimeout",
 'const geo={Chiclayo:[-6.7714,-79.8409]};const era5WeekCache=new Map();'+src.slice(start,end)+';return era5Reference;');
const climatology=construct(fakeFetch,AbortController,URLSearchParams,setTimeout,clearTimeout);
(async()=>{
 const [first,second]=await Promise.all([climatology("Chiclayo"),climatology("Chiclayo")]);
 assert.equal(calls,1,"ERA5 no utiliza caché para la misma localidad");
 assert.equal(first,second);
 assert(Math.abs(first.rain["10-27"]-(29*5+100)/30)<.0001);
 assert(Math.abs(first.tmax["10-27"]-(29*25+35)/30)<.0001);
 assert.equal(first.years,"1996–2025");
 const rf=JSON.parse(read("datos/rf_experimental_ux15.json"));
 const rows=rf.pronostico_diario_rf_experimental.Chiclayo;
 const byDate=new Map(rows.map(x=>[x.fecha,x.precipitacion_mm]));
 const current=["2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-10-31","2026-11-01","2026-11-02"];
 const matches=current.map(d=>byDate.has(d)?byDate.get(d):NaN);
 assert(matches.filter(Number.isFinite).length>=1,"No existe ninguna emisión RF que coincida con fechas de octubre");
 assert(!byDate.has("2026-11-04"),"El RF no puede rellenar fechas posteriores a su última emisión de siete días");
 console.log("UX41 OK: 30 años ERA5, media calendario, caché y coincidencia estricta RF, presentación/PWA");
})().catch(e=>{console.error(e);process.exitCode=1});
