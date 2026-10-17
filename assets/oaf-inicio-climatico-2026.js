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
    const t=weather.temperature_2m,h=weather.relative_humidity_2m,v=weather.wind_speed_10m;
    if(finite(t)){
      if(t>=33)phrases.push("Temperatura elevada ("+format(t)+" °C): puede aumentar el estrés térmico en personas y animales, especialmente durante exposición prolongada, y la demanda de agua de los cultivos.");
      else if(t>=29)phrases.push("Ambiente cálido ("+format(t)+" °C): conviene considerar hidratación, sombra y disponibilidad de agua para animales y plantas.");
      else if(t<16)phrases.push("Ambiente fresco ("+format(t)+" °C): las respuestas de plantas y animales dependen de la especie, etapa de crecimiento y exposición.");
      else phrases.push("Temperatura de "+format(t)+" °C, sin señalar un extremo térmico por este indicador aislado.");
    }
    if(finite(h)){
      if(h>=80)phrases.push("Humedad relativa alta ("+format(h,0)+" %): puede contribuir a ambientes húmedos, pero por sí sola no confirma mojado foliar, infecciones ni enfermedades.");
      else if(h<=35)phrases.push("Humedad relativa baja ("+format(h,0)+" %): la atmósfera puede favorecer mayor pérdida de agua; el efecto depende del cultivo y de la ventilación.");
    }
    if(finite(v)&&v>=30)phrases.push("Viento de "+format(v,0)+" km/h a 10 m: conviene considerar exposición durante labores y aplicaciones agrícolas; no equivale a medir ráfagas.");
  }
  if(air && finite(air.european_aqi)){
    const index=air.european_aqi,descriptor=airDescription(index);
    if(index<=20)phrases.push("Calidad del aire modelada buena (AQI europeo "+format(index,0)+"). Es una referencia general, no una garantía de exposición individual ni del estado de los cultivos.");
    else if(index<=40)phrases.push("Calidad del aire modelada razonable (AQI europeo "+format(index,0)+"); personas sensibles pueden requerir más información según el contaminante.");
    else phrases.push("Calidad del aire modelada "+descriptor+" (AQI europeo "+format(index,0)+"): la exposición puede ser relevante para la salud de las personas y los animales; el efecto vegetal requiere analizar contaminantes específicos.");
  } else {
    phrases.push("No se pudo evaluar la calidad del aire en esta consulta: el modelo no entregó un índice utilizable.");
  }
  phrases.push("Lectura orientativa para "+locality+"; valores de modelos regionales, no sensores locales, diagnóstico sanitario ni aviso oficial.");
  return phrases.slice(0,4).join(" ");
}
function reset(){
  for(const id of ["oaf-live-temp","oaf-live-prec","oaf-live-hum","oaf-live-vpd","oaf-live-wind","oaf-live-rad","oaf-live-air"])put(id,"—");
}
async function update(){
  const site=ids("oaf-home-location");
  if(!site)return;
  const city=site.value;
  if(!Object.prototype.hasOwnProperty.call(coords,city))return;
  const seq=++requestSequence;
  const button=ids("oaf-home-refresh");
  if(button)button.disabled=true;
  reset();
  put("oaf-home-source","Fuente: Open-Meteo (modelos meteorológico y de calidad del aire) · "+city+" · consultando fecha y hora…");
  put("oaf-home-analysis","Consultando las condiciones actuales para elaborar una lectura breve y orientativa.");
  const [lat,lon]=coords[city];
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
  const time=weather?.time||air?.time;
  put("oaf-home-source","Fuente: Open-Meteo (modelo meteorológico) · Calidad del aire: Open-Meteo/CAMS global (modelo) · "+city+
      " · "+dateText(time)+
      ". Calidad del aire: AQI europeo, no sensor local. Valores de validez modelada.");
  const outlook=analysis(weather,air,city);
  const pm=(air&&finite(air.pm2_5)&&finite(air.pm10))
    ? " PM₂.₅: "+format(air.pm2_5)+" µg/m³; PM₁₀: "+format(air.pm10)+" µg/m³ (estimaciones).":"";
  put("oaf-home-analysis", (!weather?"No se pudo obtener el modelo meteorológico en este momento. ":"")+outlook+pm);
  if(!weather && !air){
    put("oaf-home-source","Fuente: Open-Meteo (modelo externo) · "+city+" · sin conexión o datos actuales. No se muestran valores inventados.");
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