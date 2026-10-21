(function simpleWeather(){
"use strict";
const $=id=>document.getElementById(id);
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const fmt=(x,n=0)=>Number(x).toLocaleString("es-PE",{minimumFractionDigits:n,maximumFractionDigits:n});
function classify(d){
 const w=d?.current||null,a=d?.air||null,city=d?.localidad||"la localidad seleccionada";
 const current=$("oaf-home-analysis");if(!current)return;
 const parent=current.closest(".oaf-home-interpretation");if(parent)parent.classList.add("oaf-plain-weather");
 const content=[];const advice=[];
 if(w&&finite(w.temperature_2m)){
  const t=w.temperature_2m;
  const state=t>=32?"Hace bastante calor":t>=28?"El ambiente está cálido":t>=19?"La temperatura es moderada":"El ambiente está fresco";
  content.push(["🌡️ Temperatura",`${state} (${fmt(t,1)} °C). ${t>=30?"Conviene hacer pausas y buscar sombra durante las horas más calurosas.":"La sensación puede cambiar con el sol y el viento."}`]);
  if(t>=30)advice.push("Evita exponer innecesariamente al personal al sol intenso; revisa el riego según el cultivo y el suelo.");
 }
 if(w&&finite(w.relative_humidity_2m)){
  const h=w.relative_humidity_2m;
  const state=h>=85?"El aire está muy húmedo":h>=70?"Hay bastante humedad ambiental":h<=35?"El aire está seco":"La humedad es intermedia";
  content.push(["💧 Humedad",`${state} (${fmt(h)} %). ${h>=80?"Vigila ventilación y hojas que permanezcan mojadas; esto no confirma ninguna enfermedad.":h<=35?"El ambiente podría favorecer el secado más rápido.":"La situación debe revisarse junto con la temperatura."}`]);
  if(h>=85)advice.push("Observa las plantas en campo si hay humedad persistente; no decidas tratamientos solo con este indicador.");
 }
 if(w&&finite(w.shortwave_radiation)){
  const r=w.shortwave_radiation;
  content.push(["☀️ Luz solar",r>=700?`La radiación solar es intensa en este momento (${fmt(r)} W/m²). Se recomienda protección solar para las labores al aire libre.`:r>=300?`Hay radiación solar apreciable (${fmt(r)} W/m²); busca sombra en actividades prolongadas.`:`La radiación solar es baja en la hora consultada (${fmt(r)} W/m²).`]);
 }
 if(w&&finite(w.precipitation)){
  const mm=w.precipitation;
  content.push(["🌧️ Lluvia reciente",mm>0?`El modelo indica ${fmt(mm,1)} mm durante el intervalo reciente. Para saber qué días podría llover, consulta Predicciones y anomalías.`:"En el intervalo reciente no se aprecia lluvia en el modelo para esta zona."]);
 }
 if(w&&finite(w.wind_speed_10m)){
  const k=w.wind_speed_10m;
  content.push(["🌬️ Viento",k>=30?`El viento es elevado (${fmt(k)} km/h); revisa las condiciones antes de realizar aplicaciones o trabajos expuestos.`:k>=16?`Hay viento perceptible (${fmt(k)} km/h). Tenlo en cuenta para las labores agrícolas.`:`El viento es relativamente suave (${fmt(k)} km/h) en el modelo consultado.`]);
 }
 if(a&&finite(a.european_aqi)){
  const q=a.european_aqi;
  const state=q<=20?"buena":q<=40?"razonable":q<=60?"moderada":q<=80?"desfavorable":q<=100?"muy desfavorable":"extremadamente desfavorable";
  const action=q>60?"Las personas sensibles deberían reducir el esfuerzo prolongado al aire libre y consultar la información sanitaria correspondiente.":"No aparecen señales elevadas según este índice regional.";
  content.push(["🌫️ Calidad del aire",`La calidad del aire modelada es ${state} (índice europeo ${fmt(q)}). ${action}`]);
 }else content.push(["🌫️ Calidad del aire","No hay una estimación actual verificable para mostrar; se evita asignar un nivel sin datos."]);
 if(!content.length){current.textContent="No se recibieron indicadores actuales para explicar el clima de esta localidad. Vuelve a actualizar los datos.";return}
 current.replaceChildren();
 const lead=document.createElement("p");lead.textContent=`Así se encuentra el ambiente en ${city}, según la información meteorológica disponible:`;
 const list=document.createElement("ul");
 for(const [title,description] of content){const li=document.createElement("li");const strong=document.createElement("strong");strong.textContent=title;li.append(strong,document.createTextNode(description));list.append(li)}
 const tip=document.createElement("p");tip.className="oaf-weather-advice";tip.textContent=advice.length?`Consejo práctico: ${advice.slice(0,2).join(" ")}`:"Consejo práctico: revisa las condiciones y el suelo de tu parcela antes de ajustar el riego, la ventilación o las labores agrícolas.";
 const foot=document.createElement("p");foot.className="oaf-ux9-source";foot.textContent="Lectura orientativa elaborada por OAF a partir de los valores horarios disponibles de Open-Meteo y, cuando hay datos, CAMS. Las etiquetas de calor, humedad y radiación son descriptivas, no anomalías climáticas ni diagnósticos.";
 current.append(lead,list,tip,foot);
}
document.addEventListener("oaf:weather",e=>classify(e.detail));
})();
