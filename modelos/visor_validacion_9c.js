/* OAF-Lambayeque Fase 9C. Panel empirico sin librerias.
   Datos archivados en datos/validacion_9c/resultados_9c.json.
   No es un sistema de alertas ni valida ocurrencias fitosanitarias. */
(() => {
"use strict";
const $ = (id) => document.getElementById(id);
const CONFIG = {
  file: "datos/validacion_9c/resultados_9c.json",
  locals: ["Chiclayo", "Jayanca", "Motupe", "Olmos"]
};
function fmt(n,d=4) {
  return Number.isFinite(n) ? n.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}) : "—";
}
function buildBar(title,value,cap,tone) {
  const wrap = document.createElement("div");
  wrap.style.margin = "10px 0";
  const head = document.createElement("div");
  head.style.cssText = "display:flex;justify-content:space-between;gap:10px;font-size:13px;";
  const name = document.createElement("span");name.textContent=title;
  const number=document.createElement("strong");number.textContent=fmt(value,5);
  head.append(name,number);
  const track=document.createElement("div"); track.style.cssText="height:13px;background:#e6edf0;border-radius:7px;overflow:hidden;margin-top:5px;";
  const fill=document.createElement("div");
  fill.style.cssText="height:100%;border-radius:7px;transition:width .2s;";
  fill.style.width=(cap?100*value/cap:0).toFixed(2)+"%";
  fill.style.background=tone==="base"?"#165f85":"#c78b28";
  track.append(fill);wrap.append(head,track);return wrap;
}
function fillSelect(id,options) {
  const el=$(id);if(!el)return;
  el.replaceChildren(...options.map(({v,t})=>{const op=document.createElement("option");op.value=v;op.textContent=t;return op;}));
}
function put(id,value) {const el=$(id);if(el)el.textContent=String(value)}
async function init(){
 const panel=$("oaf-validacion-9c");if(!panel)return;
 const source=await fetch(CONFIG.file,{cache:"no-store"});
 if(!source.ok)throw Error("Archivo 9C no disponible: HTTP "+source.status);
 const data=await source.json();
 if(data.fase!=="9C"||!Array.isArray(data.continuo)||!Array.isArray(data.extremos))throw Error("Esquema 9C no reconocido");
 const summary=data.resumen;
 put("oaf-9c-score",summary.continuas_mejoras_mae+"/"+summary.continuas_grupos);
 put("oaf-9c-extreme-score",summary.prob_mejoras_brier+"/"+summary.prob_grupos);
 put("oaf-9c-approved",summary.continuas_ic_bonferroni_positivo+summary.prob_ic_bonferroni_positivo);
 fillSelect("oaf-9c-site",CONFIG.locals.map(x=>({v:x,t:x})));
 fillSelect("oaf-9c-h",[1,2,3].map(x=>({v:String(x),t:x+" mes"+(x>1?"es":"")})));
 fillSelect("oaf-9c-variable",[
  {v:"temperatura_aire_c",t:"Temperatura (°C)"},
  {v:"precipitacion_mes_mm",t:"Precipitación (mm)"}]);
 $("oaf-9c-site").value="Jayanca";$("oaf-9c-h").value="3";$("oaf-9c-variable").value="precipitacion_mes_mm";
 function draw(){
  const local=$("oaf-9c-site").value,h=Number($("oaf-9c-h").value),v=$("oaf-9c-variable").value;
  const selected=data.continuo.find(x=>x.localidad===local&&x.horizonte_meses===h&&x.variable===v);
  const output=$("oaf-9c-visual");output.replaceChildren();
  if(!selected){put("oaf-9c-legend","Sin pareja estadistica verificable para la selección.");return;}
  const upper=Math.max(selected.referencia_8w,selected.candidato_rh_vpd,0.00001);
  const subtitle=document.createElement("p");
  subtitle.style.fontWeight="650";
  subtitle.textContent="Error medio absoluto (MAE) · "+local+" · "+h+" mes(es)";
  output.append(subtitle,
    buildBar("Referencia: viento + SST",selected.referencia_8w,upper,"base"),
    buildBar("Candidata: + humedad + VPD",selected.candidato_rh_vpd,upper,"candidate"));
  const delta=selected.mejora_referencia_menos_candidato;
  const txt=document.createElement("p");txt.style.fontSize="13px";
  txt.textContent="Diferencia MAE (referencia − candidata): "+fmt(delta,5)+
   (v==="temperatura_aire_c"?" °C":" mm")+
   ". IC 95 % bloques de 3 años: ["+selected.ic95_bloques_3_anios.map(x=>fmt(x,5)).join("; ")+"]"+
   ". IC conservador por multiplicidad: ["+selected.ic_familiar_bonferroni_bloques_3_anios.map(x=>fmt(x,5)).join("; ")+"]";
  output.append(txt);
  const event=data.extremos.find(x=>x.localidad===local&&x.horizonte_meses===h);
  if(v==="precipitacion_mes_mm"&&event){
   const t=document.createElement("p");t.style.fontSize="13px";
   t.textContent="Lluvia P90 enero–abril: "+event.eventos+" eventos en "+event.meses+
     " meses evaluados. Brier de referencia: "+fmt(event.referencia_8w,5)+
     " · candidato: "+fmt(event.candidato_rh_vpd,5)+
     ". Muestra insuficiente: "+(event.evidencia_de_extremos_suficiente?"no":"sí")+".";
   output.append(t);
  }
  const verdict=selected.ic_familiar_bonferroni_bloques_3_anios[0]>0
     ? "Resultado exploratorio favorable, pendiente de verificación prospectiva e instrumental."
     : "No se observa mejora robusta con control conservador de comparaciones múltiples.";
  put("oaf-9c-legend","Leyenda: las barras comparan errores sobre los mismos meses. Una barra menor indica menor error. "+verdict+
   " Datos retrospectivos ERA5/NOAA; las cuatro localidades no representan los pisos altitudinales de toda la región.");
 }
 for(const id of ["oaf-9c-site","oaf-9c-h","oaf-9c-variable"])$(id).addEventListener("change",draw);
 draw();
 put("oaf-9c-status","Resultados 9C originales y métodos disponibles para auditoría.");
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",()=>init().catch(e=>put("oaf-9c-status","9C no cargó: "+e.message)));
else init().catch(e=>put("oaf-9c-status","9C no cargó: "+e.message));
})();
