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
assert.match(index,/oaf-ux15-rf-salidas\.js\?v=/,"No se actualizó script semanal en web");
assert(index.includes("oaf-ux14-reorganizacion.js?v=20261027-ux43"),"No se actualizó estructura semanal en web");
assert.match(read("sw.js"),/const RELEASE="oaf-pwa-shell-[^"]+"/,"Cache PWA no versionado");
assert(src.includes("relative_humidity_2m_mean")&&src.includes("shortwave_radiation_sum"),"Faltan indicadores diarios para área productiva");
assert(src.includes("et0_fao_evapotranspiration")&&src.includes("vapour_pressure_deficit_max"),"Faltan ET0 y DPV del pronóstico puntual");
assert(src.includes("function rfEvidence(rain)")&&src.includes("wins>=5"),"RF debe superar 5/7 horizontes y MAE medio para mostrarse");
assert(src.includes("RF no se muestra porque mejora"),"RF sin habilidad no debe aparecer como pronóstico");
assert(src.includes("MAE RF Tmax")&&src.includes("MAE clim. Tmax"),"La auditoría debe comparar también temperatura máxima");

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
 assert.equal(rows.length,7,"El modelo debe emitir exactamente siete días por localidad");
 assert.equal(rows[0].fecha,rf.fecha_local,"La primera fecha RF debe corresponder a la emisión local del archivo");
 const stamps=rows.map(x=>Date.parse(x.fecha+"T00:00:00Z"));
 assert(stamps.every(Number.isFinite),"Fecha diaria inválida");
 for(let i=1;i<stamps.length;i++)assert.equal(stamps[i]-stamps[i-1],86400000,"La serie RF debe tener días consecutivos sin huecos");
 assert(rows.every(x=>Number.isFinite(x.precipitacion_mm)&&x.precipitacion_mm>=0&&Number.isFinite(x.temperatura_max_c)),
  "Cada día debe tener lluvia no negativa y Tmax finita");
 assert.equal(byDate.size,7,"No se deben extender ni rellenar días posteriores al horizonte emitido");
 console.log("UX41 OK: 30 años ERA5, media calendario, caché y coincidencia estricta RF, presentación/PWA");
})().catch(e=>{console.error(e);process.exitCode=1});
