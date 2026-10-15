/* Fase 8C · NOAA/PMEL T300 oceanic subsurface heat experiment.
   Retrospective holdout: NOT ICEN, ENFEN, rainfall or validated forecasts. */
(function(){
"use strict";
const panel=document.getElementById("oaf-subsurface-8c");
if(!panel)return;
const button=document.getElementById("oaf-subsurface-8c-refresh");
const status=document.getElementById("oaf-subsurface-8c-status");
const table=document.getElementById("oaf-subsurface-8c-tbody");
const output=document.getElementById("oaf-subsurface-8c-output");
const details=document.getElementById("oaf-subsurface-8c-details");
const fmt=(x,n=3)=>Number.isFinite(x)?x.toLocaleString("es-PE",{minimumFractionDigits:n,maximumFractionDigits:n}):"—";
let initialized=false;
async function load(){
 button.disabled=true;output.hidden=true;status.textContent="Consultando pruebas temporales con NOAA PMEL T300…";
 try{
  const response=await fetch("datos/benchmark_subsuperficial_8c.json",{cache:"no-store"});
  if(!response.ok)throw Error("Informe T300 aún no publicado (HTTP "+response.status+")");
  const j=await response.json();
  if(j.fase!=="8C"||j.estado!=="evaluacion_temporal_retrospectiva_no_operativa"||
     j.desfase_t300_meses!==1||j.desfase_soi_y_vientos_meses!==1||
     j.corte_entrenamiento_por_mes_objetivo!=="2022-12"||
     j.inicio_prueba_independiente!=="2023-01"||
     j.sin_ajuste_con_periodo_prueba!==true||
     j.se_ha_emitido_pronostico_prospectivo_8c!==false||
     j.prediccion_elnino_costero_validada!==false||
     j.es_icen_oficial!==false||j.es_alerta_enfen!==false||
     !j.evaluacion_meses_1_2_3)throw Error("Fuente o declaración científica inválida");
  const cells=[];
  for(const horizon of [1,2,3]){
   const r=j.evaluacion_meses_1_2_3[String(horizon)];
   const m=r?.metricas;
   if(!r||r.habilidad_operativa_demostrada!==false||r.n_prueba<30||
      !Array.isArray(r.intervalo_exploratorio_t300_vs_tendencia)||
      r.intervalo_exploratorio_t300_vs_tendencia.length!==2||
      !Number.isFinite(m?.persistencia_c?.mae_c)||
      !Number.isFinite(m?.sst_tendencia_c?.mae_c)||
      !Number.isFinite(m?.sst_tendencia_t300_c?.mae_c)||
      !Number.isFinite(m?.sst_tendencia_t300_atmosfera_c?.mae_c))
      throw Error("Datos de "+horizon+" mes(es) incompletos");
   const gain=r.mejora_t300_vs_tendencia;
   cells.push([
     horizon+" mes"+(horizon===1?"":"es"),String(r.n_prueba),
     fmt(m.persistencia_c.mae_c),fmt(m.sst_tendencia_c.mae_c),
     fmt(m.sst_tendencia_t300_c.mae_c),
     fmt(m.sst_tendencia_t300_atmosfera_c.mae_c),
     fmt(gain*100,1)+" %"
   ]);
  }
  table.replaceChildren();
  for(const arr of cells){
   const tr=document.createElement("tr");
   arr.forEach(value=>{const td=document.createElement("td");td.textContent=value;tr.appendChild(td)});
   table.appendChild(tr);
  }
  details.textContent="Objetivo: anomalía TSM Niño 1+2 reconstruida por OAF (1991–2020). "+
   "T300: temperatura media 0–300 m, Pacífico ecuatorial, NOAA/PMEL GODAS (anomalía base 1981–2010); último mes: "+
   j.ultimo_mes_reanalisis_t300+". "+
   "Modelos entrenados con meses objetivo hasta 2022-12; evaluación 2023 en adelante con parámetros fijos. "+
   "Fuente atmosférica de meses anteriores: SOI y anomalías de vientos NOAA CPC. "+
   "Los intervalos exploratorios de mejora de T300 incluyen cero en los tres horizontes. "+
   "Ninguna predicción 8C se ha emitido prospectivamente.";
  status.textContent="La variante T300 redujo el error en esta muestra retrospectiva, pero la mejora todavía NO es robusta. Agregar viento y SOI empeoró el modelo.";
  output.hidden=false;
 }catch(error){status.textContent="Resultados 8C no disponibles: "+error.message+". No se presentan valores ficticios."}
 finally{button.disabled=false}
}
button.addEventListener("click",load);
panel.addEventListener("toggle",()=>{if(panel.open&&!initialized){initialized=true;load()}});
})();