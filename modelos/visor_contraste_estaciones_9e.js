/* OAF-Lambayeque · contraste histórico de tres series sin metadatos geográficos.
   El panel no representa zonas espaciales ni comparación contra ERA5/CHIRPS. */
(()=>{
"use strict";
const el=id=>document.getElementById(id);
const f=(n,d=1)=>n===null||!Number.isFinite(n)?"Sin datos":n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d});
function create(parent,tag,className,text){
 const node=document.createElement(tag);
 if(className)node.className=className;
 if(text!==undefined)node.textContent=text;
 parent.append(node);return node;
}
function draw(data){
 const year=Number(el("oaf-compare-year").value);
 const chart=el("oaf-compare-chart");
 chart.replaceChildren();
 const values=data.estaciones.map(x=>({code:x.codigo_archivo,row:x.anios_ejemplo_100pct.find(t=>t.anio===year)}));
 const max=Math.max(1,...values.map(x=>x.row?.total_mm_estricto||0));
 for(const x of values){
  const line=create(chart,"div","oaf-compare-line");
  create(line,"div","oaf-compare-name","Estación "+x.code);
  const track=create(line,"div","oaf-compare-track");
  const bar=create(track,"div","oaf-compare-bar");
  const valid=x.row?.total_mm_estricto!==null && x.row?.total_mm_estricto!==undefined;
  bar.style.width=valid?(100*x.row.total_mm_estricto/max).toFixed(2)+"%":"0%";
  if(!valid)track.classList.add("oaf-compare-nodata");
  create(line,"strong","oaf-compare-number",valid?f(x.row.total_mm_estricto,1)+" mm":"Sin año completo");
 }
 const available=values.filter(x=>x.row?.total_mm_estricto!==null);
 let msg="Las barras muestran acumulados de lluvia de cada archivo, únicamente con 12 meses de observación completa. La longitud expresa lluvia, no riesgo de inundación. ";
 if(year===1998)msg+="En 1998 los tres archivos tienen los 365 días de precipitación registrados, pero aún falta cotejar precisión e identidad de las estaciones.";
 else if(year===1983)msg+="En 1983 dos archivos están completos, mientras que el código 00000340 carece de lluvia válida: el espacio vacío no significa sequía.";
 else if(available.length<3)msg+="Una barra sin valor indica cobertura insuficiente; no se realizó imputación.";
 else msg+="Las diferencias no autorizan inferir altitud o proximidad geográfica.";
 el("oaf-compare-legend").textContent="Cómo interpretar: "+msg;
}
async function init(){
 if(!el("oaf-contraste-estaciones"))return;
 const response=await fetch("datos/validacion_estaciones_9e/contraste_observacional_9e.json",{cache:"no-store"});
 if(!response.ok)throw Error("Datos 9E no disponibles HTTP "+response.status);
 const data=await response.json();
 if(data.fase!=="9E"||data.estaciones?.length!==3||data.pares?.length!==3)throw Error("Esquema de datos inconsistente");
 const sel=el("oaf-compare-year");
 for(const y of [1982,1983,1997,1998,2012,2013]){
  const option=document.createElement("option");option.value=String(y);option.textContent=String(y);sel.append(option);
 }
 sel.value="1998";
 const list=el("oaf-compare-correlations");
 list.replaceChildren();
 for(const p of data.pares){
  const cell=create(list,"div","oaf-compare-card");
  create(cell,"small","","Series "+p.codigo_a+" / "+p.codigo_b);
  create(cell,"strong","",f(p.correlacion_log1p_lluvia_mensual,2));
  create(cell,"span","",p.meses_comunes_100pct+" meses comparables (1996–2013)");
 }
 const v=el("oaf-compare-status");
 v.textContent="Los tres archivos siguen sin ficha geográfica oficial verificada. No hay comparación ERA5-Land/CHIRPS calculada.";
 sel.addEventListener("change",()=>draw(data));
 draw(data);
}
const run=()=>init().catch(e=>{if(el("oaf-compare-status"))el("oaf-compare-status").textContent="No se cargó el contraste de observaciones: "+e.message});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);
else run();
})();