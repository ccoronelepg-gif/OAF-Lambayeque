/* 9R: GCN vs Random Forest, pronóstico simulado a un mes con CHIRPS final. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const fmt=(x,n=1)=>typeof x==="number"&&Number.isFinite(x)?
 x.toLocaleString("es-PE",{maximumFractionDigits:n}):"—";
const set=(id,v)=>{if($(id))$(id).textContent=v;};
const floor={
 llanura_costa:"Costa baja",valle_bajo:"Valle bajo",piedemonte:"Piedemonte",
 montana_baja:"Ladera baja",montana_media:"Ladera media",montana_alta:"Montaña alta",
 cota_negativa_revisar:"Cota negativa / pendiente de revisión"};
const colors={"Climatología":"#9aaba5","Random Forest":"#247da5","GCN":"#d99b4c"};
function el(tag,props={},txt){
 const n=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [k,v] of Object.entries(props))n.setAttribute(k,String(v));
 if(txt!==undefined)n.textContent=txt;return n;
}
async function read(url){
 const response=await fetch(url,{cache:"no-store"});
 if(!response.ok)throw Error("Archivo aún no accesible: "+url);
 return response.json();
}
function figure(data,key){
 const p=$("oaf-9r-chart");p.replaceChildren();
 const models=["Climatología","Random Forest","GCN"];
 const max=Math.max(1,...models.map(k=>data[k][key]))*1.15;
 const W=780,H=208,L=156,R=112;
 const svg=el("svg",{role:"img",viewBox:"0 0 "+W+" "+H,
   "aria-label":"Comparación de errores de los tres métodos en el periodo 2021–2025"});
 svg.style.width="100%";
 models.forEach((name,i)=>{
  const val=data[name][key],y=19+i*61,w=val/max*(W-L-R);
  svg.append(el("text",{x:L-10,y:y+24,fill:"currentColor","font-size":13,
   "text-anchor":"end"},name));
  const r=el("rect",{x:L,y,width:Math.max(w,1),height:33,rx:5,fill:colors[name]});
  r.append(el("title",{},name+": "+fmt(val,2)+" mm"));
  svg.append(r);
  svg.append(el("text",{x:L+Math.max(w,1)+9,y:y+23,fill:"currentColor","font-size":13},fmt(val,2)+" mm"));
 });
 p.append(svg);
}
function cell(tr,v){const x=document.createElement("td");x.textContent=String(v);tr.append(x);}
async function init(){
 if(!$("oaf-9r-visor"))return;
 try{
  const j=await read("datos/validacion_predictiva_9r/comparacion_modelos_9r.json");
  if(j.fase!=="9R"||j.origen_CHIRPS.meses_verificados!==360||
     j.n_modelos_operativamente_validados!==0||
     j.pronostico_2026_comprobado!==false||
     j.conjuntos.n_meses_prueba!==60||
     !j.metricas_prueba["Random Forest"]||!j.metricas_prueba.GCN)
   throw Error("La verificación del experimento no coincide con los datos");
  const test=j.metricas_prueba;
  set("oaf-9r-winner",j.mejor_modelo_ml_por_mae);
  set("oaf-9r-nodes",j.grafo.n_nodos_con_lluvia_valida+" sectores");
  set("oaf-9r-errors",fmt(test[j.mejor_modelo_ml_por_mae].mae_mm,2)+" mm");
  set("oaf-9r-status","Experimento 1996–2025 reproducible: entrenamiento 1997–2015, "+
   "validación 2016–2020 y evaluación posterior reservada 2021–2025. Se comparan "+
   j.n_predicciones_sector_mes_prueba+" predicciones sector-mes. El ganador se refiere al MAE "+
   "del CHIRPS final retrospectivo, NO a pronósticos reales emitidos en esas fechas.");
  const metric=$("oaf-9r-metric");
  metric.addEventListener("change",()=>figure(test,metric.value));
  figure(test,metric.value);
  const table=$("oaf-9r-score-table");table.replaceChildren();
  for(const name of ["Climatología","Random Forest","GCN"]){
   const r=test[name],tr=document.createElement("tr");
   [name,fmt(r.mae_mm,2),fmt(r.rmse_mm,2),fmt(r.bias_mm,2),
     r.skill_mae_vs_climatologia_pct===null?"—":fmt(r.skill_mae_vs_climatologia_pct,1)+" %"].forEach(x=>cell(tr,x));
   table.append(tr);
  }
  const perFloor=$("oaf-9r-floors");perFloor.replaceChildren();
  for(const [id,f] of Object.entries(j.comparacion_por_piso_altitudinal)){
   const tr=document.createElement("tr");
   const rf=f.metrics["Random Forest"].mae_mm,gcn=f.metrics.GCN.mae_mm;
   [floor[id]||id,f.n_sector,fmt(rf,2),fmt(gcn,2),
    rf<gcn?"Random Forest":gcn<rf?"GCN":"Empate"].forEach(x=>cell(tr,x));
   perFloor.append(tr);
  }
  const perGroup=$("oaf-9r-groups");perGroup.replaceChildren();
  for(const [id,g] of Object.entries(j.comparacion_por_grupo_exploratorio_9q)){
   const tr=document.createElement("tr");
   [id,g.sectors.join(", "),g.n_evaluable,
    g.metrics?fmt(g.metrics["Random Forest"].mae_mm,2):"—",
    g.metrics?fmt(g.metrics.GCN.mae_mm,2):"—"].forEach(x=>cell(tr,x));
   perGroup.append(tr);
  }
  const anomalies=$("oaf-9r-anomalies");anomalies.replaceChildren();
  for(const [name,x] of Object.entries(j.anomalia_lluvia_muy_alta_umbral_percentil80_train)){
   const tr=document.createElement("tr");
   [name,x.n_true_anomaly,x.tp,fmt(x.precision,3),fmt(x.recall,3),fmt(x.f1,3)].forEach(v=>cell(tr,v));
   anomalies.append(tr);
  }
  const year=$("oaf-9r-years");year.replaceChildren();
  for(const r of j.metricas_por_anio_test){
    const tr=document.createElement("tr");
    [r.year,fmt(r.metrics["Climatología"].mae_mm,2),
     fmt(r.metrics["Random Forest"].mae_mm,2),fmt(r.metrics.GCN.mae_mm,2)]
      .forEach(x=>cell(tr,x));
    year.append(tr);
  }
  const mlBetter=test[j.mejor_modelo_ml_por_mae].mae_mm<test["Climatología"].mae_mm;
  set("oaf-9r-caution",mlBetter?
   "El modelo "+j.mejor_modelo_ml_por_mae+" superó la climatología en MAE dentro de la prueba histórica. "+
   "La cobertura real de estaciones, la disponibilidad de CHIRPS por fecha de emisión y la geometría posterior de los sectores siguen sin verificarse prospectivamente.":
   "Ninguno de los dos modelos de aprendizaje automático superó la climatología en MAE de esta muestra. No hay fundamento para reemplazar el método sencillo con ML todavía.");
 }catch(e){
  set("oaf-9r-status","Resultados experimentales pendientes de verificación o publicación: "+e.message+
   ". Los análisis históricos 9Q siguen disponibles.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();