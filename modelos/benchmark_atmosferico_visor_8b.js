/* Fase 8B · Public NOAA CPC ocean-atmosphere hindcast verification.
 * Shows retrospective skill, not an operational coastal El Nino prediction.
 */
(function(){
"use strict";
const p=document.getElementById("oaf-atmos-8b");
if(!p)return;
const b=document.getElementById("oaf-atmos-8b-refresh");
const status=document.getElementById("oaf-atmos-8b-status");
const output=document.getElementById("oaf-atmos-8b-output");
const tbody=document.getElementById("oaf-atmos-8b-rows");
const method=document.getElementById("oaf-atmos-8b-method");
const format=(n,d=3)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let started=false;
async function load(){
 b.disabled=true;output.hidden=true;
 status.textContent="Consultando resultados de la evaluación atmosférica realizada con datos oficiales NOAA CPC…";
 try{
  const res=await fetch("datos/benchmark_atmosferico_8b.json",{cache:"no-store"});
  if(!res.ok)throw Error("Resultados no publicados (HTTP "+res.status+")");
  const j=await res.json();
  if(j.fase!=="8B"||j.estado!=="comparacion_historica_sin_habilidad_operativa"||
     j.es_icen_oficial!==false||j.es_alerta_enfen!==false||
     j.demuestra_prediccion_elnino_costero!==false||
     j.validacion_prospectiva!==false||
     !j.resultados_por_horizonte||
     !Array.isArray(j.predictores_mes_origen)||
     !["soi_estandarizado","alisios_pacifico_central","alisios_pacifico_oriental"].every(x=>j.predictores_mes_origen.includes(x))){
      throw Error("Procedencia, límites o índice científico incorrectos");
  }
  const computed=[];
  for(const h of [1,2,3]){
   const r=j.resultados_por_horizonte[String(h)];
   const m=r?.metricas;
   if(!r||r.validacion_prospectiva!==false||r.n_origenes_evaluados<120||
      !Number.isFinite(m?.persistencia?.mae_c)||!Number.isFinite(m?.ar1_solo_tsm?.mae_c)||
      !Number.isFinite(m?.tsm_mas_atmosfera?.mae_c)||
      !Number.isFinite(r.beneficio_vs_ar1)||
      !Array.isArray(r.intervalo_descriptivo_bloques_12m_95)||
      r.intervalo_descriptivo_bloques_12m_95.length!==2){
       throw Error("Horizonte "+h+" con pruebas incompletas");
   }
   const increase=(r.beneficio_vs_ar1<0?"Empeoró ":"Mejoró ")+
       format(Math.abs(r.beneficio_vs_ar1*100),1)+" % vs solo TSM";
   const cells=[h+" mes"+(h===1?"":"es"),String(r.n_origenes_evaluados),
      format(m.persistencia.mae_c)+" °C",
      format(m.ar1_solo_tsm.mae_c)+" °C",
      format(m.tsm_mas_atmosfera.mae_c)+" °C",
      increase];
   computed.push(cells);
  }
  tbody.replaceChildren();
  for(const cells of computed){
    const tr=document.createElement("tr");
    for(const value of cells){const td=document.createElement("td");td.textContent=value;tr.appendChild(td)}
    tbody.appendChild(tr);
  }
  method.textContent="Fuentes: NOAA CPC SOI y anomalías de viento 850 hPa (Pacífico central y oriental); "+
   "NOAA NCEI ERSSTv5 Niño 1+2 reajustada por el OAF. "+
   "Último mes en común: "+j.origen_ultimo_comun+
   " · "+j.num_meses_comunes+" meses alineados · "+j.primer_origen_de_prueba+
   " en adelante; regresión Ridge con parámetro fijo "+j.regularizacion_ridge_fija+
   ". Esta es una comparación histórica no vintage: el archivo actual puede contener revisiones.";
  status.textContent="Experimento retrospectivo completado. En esta ejecución, agregar SOI y vientos NO aportó una mejora estable frente a solo TSM. No se usa el modelo ampliado para emitir alertas.";
  output.hidden=false;
 }catch(e){
  status.textContent="Comparación 8B no disponible: "+e.message+". No se crean resultados hipotéticos.";
 }finally{b.disabled=false}
}
b.addEventListener("click",load);
p.addEventListener("toggle",()=>{if(p.open&&!started){started=true;load()}});
})();