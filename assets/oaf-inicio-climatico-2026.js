/* OAF-Lambayeque | Portada clara, lectura interpretativa y calidad del aire.
   Fuentes en vivo: Open-Meteo pronóstico; Open-Meteo Air Quality / CAMS global.
   No se fabrican valores, diagnósticos, alertas ni riesgos fitosanitarios. */
(() => {
"use strict";
const ids = id => document.getElementById(id);
const coords = {
  Chiclayo:[-6.7714,-79.8409], Jayanca:[-6.39278,-79.8228],
  Motupe:[-6.15083,-79.7142], Olmos:[-5.98825,-79.74723]
};
const format = (n, digits=1) => Number.isFinite(n) ? n.toLocaleString("es-PE",{maximumFractionDigits:digits,minimumFractionDigits:digits}) : "—";
const finite = x => typeof x === "number" && Number.isFinite(x);
const put = (id, text) => {const e=ids(id);if(e)e.textContent=text;};
const airDescription = a => {
  if(!finite(a))return null;
  if(a<=20)return "buena";
  if(a<=40)return "razonable";
  if(a<=60)return "moderada";
  if(a<=80)return "mala";
  if(a<=100)return "muy mala";
  return "extremadamente mala";
};
let requestSequence=0;
function dateText(iso) {
  if(typeof iso!=="string" || !/^\d{4}-\d\d-\d\dT\d\d:\d\d/.test(iso))return "fecha y hora no disponibles";
  return iso.slice(8,10)+"/"+iso.slice(5,7)+"/"+iso.slice(0,4)+" · "+iso.slice(11,16)+" (hora de Lima)";
}
function url(base, lat, lon, attrs){
  return base+"?"+new URLSearchParams(Object.assign({
    latitude:String(lat),longitude:String(lon),timezone:"America/Lima"
  },attrs));
}
async function getJson(url){
  const response=await fetch(url,{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const data=await response.json();
  if(!data || data.error || !data.current || !data.current.time)throw Error("Datos actuales no disponibles");
  return data;
}
function analysis(weather,air,locality){
  const phrases=[];
  if(weather){
    if(finite(weather.temperature_2m))phrases.push("🌡️ Temperatura del aire: "+format(weather.temperature_2m)+" °C. Es un valor informativo modelado; no se determina si es inusual sin compararlo con una referencia climática local adecuada.");
    if(finite(weather.relative_humidity_2m))phrases.push("💧 Humedad relativa: "+format(weather.relative_humidity_2m,0)+" %. No demuestra que el follaje esté mojado ni permite diagnosticar enfermedades.");
    if(finite(weather.precipitation))phrases.push("🌧️ Precipitación modelada del intervalo reciente: "+format(weather.precipitation)+" mm. Esta variable no predice la precipitación futura.");
    if(finite(weather.shortwave_radiation))phrases.push("☀️ Radiación de onda corta: "+format(weather.shortwave_radiation,0)+" W/m², valor informativo para la hora indicada, no índice UV.");
    if(finite(weather.wind_speed_10m))phrases.push("🌬️ Viento modelado a 10 m: "+format(weather.wind_speed_10m)+" km/h. No representa ráfagas ni exposición precisa en parcela.");
  }
  if(air && finite(air.european_aqi))phrases.push("🌫️ Calidad del aire, índice europeo calculado con CAMS: "+format(air.european_aqi,0)+" ("+airDescription(air.european_aqi)+"). No es un sensor local ni diagnóstico sanitario.");
  else phrases.push("Calidad del aire: no evaluable en esta consulta; no se sustituye por una estimación inventada.");
  phrases.push("Lectura orientativa para "+locality+"; las respuestas de personas, animales y cultivos dependen del contexto y de mediciones complementarias. Interpretación aún no validada localmente.");
  return phrases.join(" ");
}
function reset(){
  for(const id of ["temp","prec","hum","vpd","wind","rad","air"]){
    put("oaf-live-"+id,"—");
    put("oaf-meta-"+id,"Esperando hora de validez · fuente modelada");
  }
}
async function update(){
  const site=ids("oaf-home-location");
  if(!site)return;
  const city=site.value;
  const custom=city==="Mi zona productora"?window.OAFTerritory?.getPoint?.("inicio"):null;
   if(!Object.prototype.hasOwnProperty.call(coords,city)&&!custom)return;
  const seq=++requestSequence;
  const button=ids("oaf-home-refresh");
  if(button)button.disabled=true;
  reset();
  put("oaf-home-source","Actualizando información de "+city+"…");
  put("oaf-home-analysis","Consultando las condiciones actuales para elaborar una lectura breve y orientativa.");
  const [lat,lon]=custom?[custom.lat,custom.lon]:coords[city];
  const wUrl=url("https://api.open-meteo.com/v1/forecast",lat,lon,{
    current:"temperature_2m,relative_humidity_2m,precipitation,shortwave_radiation,wind_speed_10m",
    forecast_days:"1"
  });
  const aUrl=url("https://air-quality-api.open-meteo.com/v1/air-quality",lat,lon,{
    current:"european_aqi,pm2_5,pm10",
    domains:"cams_global",
    forecast_days:"1"
  });
  const [w,a]=await Promise.allSettled([getJson(wUrl),getJson(aUrl)]);
  if(seq!==requestSequence)return;
  if(button)button.disabled=false;
  const weather=w.status==="fulfilled"?w.value.current:null;
  const air=a.status==="fulfilled"?a.value.current:null;
  if(weather){
    const t=weather.temperature_2m,rh=weather.relative_humidity_2m;
    put("oaf-live-temp",finite(t)?format(t)+" °C":"—");
    put("oaf-live-hum",finite(rh)?format(rh,0)+" %":"—");
    put("oaf-live-prec",finite(weather.precipitation)?format(weather.precipitation)+" mm":"—");
    put("oaf-live-rad",finite(weather.shortwave_radiation)?format(weather.shortwave_radiation,0)+" W/m²":"—");
    put("oaf-live-wind",finite(weather.wind_speed_10m)?format(weather.wind_speed_10m)+" km/h":"—");
    const vpd=finite(t)&&finite(rh)&&rh>=0&&rh<=100&&t>-80
      ?Math.max(0,0.6108*Math.exp((17.27*t)/(t+237.3))*(1-rh/100)):null;
    put("oaf-live-vpd",finite(vpd)?format(vpd,2)+" kPa":"—");
  }
  if(air && finite(air.european_aqi)){
    put("oaf-live-air",format(air.european_aqi,0)+" · "+airDescription(air.european_aqi));
  }
  const wtime=weather?.time,atime=air?.time;
  const wt="Validez: "+dateText(wtime)+" · Open-Meteo, modelo meteorológico; no observación instrumental.";
  const at="Validez: "+dateText(atime)+" · Open-Meteo/CAMS global; modelo de calidad del aire.";
  for(const id of ["temp","prec","hum","vpd","wind","rad"])
    put("oaf-meta-"+id,weather?wt:"Sin dato · Open-Meteo (modelo meteorológico)");
  put("oaf-meta-air",air?at:"Sin dato · Open-Meteo/CAMS global (modelo)");
  const time=wtime||atime;
  put("oaf-home-source","Consulta de "+city+" · "+dateText(time)+". Son valores estimados, no mediciones locales.");
  const outlook=analysis(weather,air,city);
  const pm=(air&&finite(air.pm2_5)&&finite(air.pm10))
    ? " PM₂.₅: "+format(air.pm2_5)+" µg/m³; PM₁₀: "+format(air.pm10)+" µg/m³ (estimaciones).":"";
  put("oaf-home-analysis", (!weather?"No se pudo obtener el modelo meteorológico en este momento. ":"")+outlook+pm);
  if(typeof CustomEvent==="function" && typeof document.dispatchEvent==="function")
    document.dispatchEvent(new CustomEvent("oaf:weather",{detail:{localidad:city,current:weather,air,time}}));
  if(!weather && !air){
    put("oaf-home-source","No hay datos recientes disponibles para "+city+".");
  }
}
function init(){
  if(!ids("oaf-home-location"))return;
  ids("oaf-home-location").addEventListener("change",update);
  ids("oaf-home-refresh")?.addEventListener("click",update);
  update();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();