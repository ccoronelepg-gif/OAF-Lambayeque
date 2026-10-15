/* OAF 8D: experimental regional climate anomaly hindcast display.
 * The descriptive 1996–2025 climate is NOT used to fit the 2023+ test.
 * ERA5/ERA5-Land are reanalyses and not certified SENAMHI field observations.
 */
(function(){
"use strict";
const root=document.getElementById("oaf-regional-8d");
if(!root)return;
const loadButton=document.getElementById("oaf-regional-8d-load");
const city=document.getElementById("oaf-regional-8d-city");
const variable=document.getElementById("oaf-regional-8d-variable");
const status=document.getElementById("oaf-regional-8d-status");
const table=document.getElementById("oaf-regional-8d-results");
const region=document.getElementById("oaf-regional-8d-data");
const detail=document.getElementById("oaf-regional-8d-detail");
const fmt=(x,d=2)=>Number.isFinite(x)?x.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let science=null,started=false;
const units={"temperatura_c":"°C","precipitacion_mm":"mm","radiacion_mj_m2":"MJ/m²"};
const labels={"temperatura_c":"temperatura media","precipitacion_mm":"lluvia acumulada","radiacion_mj_m2":"radiación solar acumulada"};
function render(){
 if(!science)return;
 const chosen=science.localidades?.[city.value]?.resultados_modelos?.[variable.value];
 if(!chosen){status.textContent="Sin datos verificados para esta localidad/variable.";region.hidden=true;return}
 table.replaceChildren();
 for(const h of [1,2,3]){
  const r=chosen[String(h)],m=r?.metricas;
  const keys=["climatologia_cero","persistencia_local","modelo_local","modelo_nino","modelo_nino_t300"];
  if(!r||r.validado_prospectivamente!==false||r.n_entrenamiento<250||r.n_prueba<35||
     keys.some(k=>!Number.isFinite(m?.[k]?.mae)))throw Error("Métricas inconsistentes en "+city.value+" / "+h);
  const values=[h+" mes"+(h===1?"":"es"),String(r.n_prueba),
    ...keys.map(k=>fmt(m[k].mae)+" "+units[variable.value]),
    fmt(100*r.mejora_nino_vs_local,1)+" %",
    fmt(100*r.mejora_nino_t300_vs_local,1)+" %"];
  const tr=document.createElement("tr");
  for(const item of values){const td=document.createElement("td");td.textContent=item;tr.appendChild(td)}
  table.appendChild(tr);
 }
 detail.textContent="Localidad: "+city.value+" · Variable: "+labels[variable.value]+
  ". Anomalías mensuales definidas con referencia fija 1996–2022 para impedir fuga de datos; "+
  "referencia descriptiva de 30 años: 1996–2025. "+
  "Comparadores: climatología (anomalía 0), persistencia local, Ridge local, "+
  "Ridge local+Niño 1+2 y Ridge local+Niño 1+2+T300. "+
  "MAE más bajo indica menor error en la muestra retrospectiva. "+
  "No representa pronóstico de la próxima campaña ni medición SENAMHI.";
 status.textContent="Evaluación retrospectiva completada. La ventaja oceánica, si existe, debe verificarse con emisiones reales y estaciones regionales independientes.";
 region.hidden=false;
}
async function load(){
 loadButton.disabled=true;region.hidden=true;
 status.textContent="Consultando datos regionales ERA5 / ERA5-Land y comparación NOAA Niño 1+2…";
 try{
  const response=await fetch("datos/benchmark_impacto_lambayeque_8d.json",{cache:"no-store"});
  if(!response.ok)throw Error("El informe 8D todavía no ha terminado de publicarse (HTTP "+response.status+")");
  const x=await response.json();
  if(x.fase!=="8D"||x.estado!=="retrospectivo_regional_no_validado_prospectivamente"||
     x.validacion_prospectiva_real!==false||x.validacion_instrumental_senamhi!==false||
     x.es_icen_oficial!==false||x.es_alerta_enfen!==false||
     x.climatologia_entrenamiento!=="1996–2022, fija para toda predicción de prueba 2023–2026"||
     !x.localidades||Object.keys(x.localidades).length!==4){
     throw Error("La procedencia o el diseño temporal no pasan los controles de calidad");
  }
  science=x;
  render();
 }catch(e){
  science=null;status.textContent="Análisis regional no disponible: "+e.message+". No se crean resultados de reemplazo.";
 }finally{loadButton.disabled=false}
}
loadButton.addEventListener("click",load);
city.addEventListener("change",()=>{if(science){try{render()}catch(e){status.textContent=e.message;region.hidden=true}}});
variable.addEventListener("change",()=>{if(science){try{render()}catch(e){status.textContent=e.message;region.hidden=true}}});
root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;load()}});
})();