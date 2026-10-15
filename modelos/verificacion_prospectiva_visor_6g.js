/* OAF-Lambayeque 6G — real archival forecast verification reader.
   Never show fabricated zero-error metrics when reference data are pending. */
(function(){
"use strict";
const panel=document.getElementById("oaf-verify-6g");
if(!panel)return;
const btn=document.getElementById("oaf-verify-6g-refresh");
const status=document.getElementById("oaf-verify-6g-status");
const body=document.getElementById("oaf-verify-6g-table");
const results=document.getElementById("oaf-verify-6g-results");
const stat=document.getElementById("oaf-verify-6g-counter");
const area=document.getElementById("oaf-verify-6g-place");
const variable=document.getElementById("oaf-verify-6g-var");
const fmt=(v,d=2)=>Number.isFinite(v)?v.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let archive=null,once=false;
const varMap={
 "temperature_2m_mean":"Temperatura media (°C)",
 "precipitation_sum":"Lluvia diaria (mm)",
 "shortwave_radiation_sum":"Radiación diaria (MJ/m²)"
};
function render(){
 if(!archive)return;
 const selected=archive.metricas_por_localidad_horizonte_y_variable.filter(
   r=>r.localidad===area.value&&r.variable===variable.value);
 body.replaceChildren();
 for(let h=1;h<=7;h++){
   const obj=selected.find(r=>r.horizonte_dias===h);
   if(!obj)continue;
   const vals=[h+" día"+(h===1?"":"s"),String(obj.n_emisiones_verificadas),
     fmt(obj.mae)+" "+obj.unidad,fmt(obj.sesgo)+" "+obj.unidad,
     fmt(obj.rmse)+" "+obj.unidad];
   const row=document.createElement("tr");
   for(const val of vals){const cell=document.createElement("td");cell.textContent=val;row.appendChild(cell)}
   body.appendChild(row);
 }
 stat.textContent="Emisiones archivadas verificadas: "+archive.emisiones_distintas_verificadas+
   " · Jornadas verificadas por localidad: "+archive.jornadas_verificadas+
   " · Jornadas con referencia incompleta: "+archive.jornadas_con_referencia_incompleta;
 if(!selected.length){
   const tr=document.createElement("tr");
   const td=document.createElement("td");
   td.colSpan=5;
   td.textContent="Aún no hay jornadas verificadas para "+area.value+" y "+varMap[variable.value]+".";
   tr.appendChild(td);body.appendChild(tr);
 }
 results.hidden=false;
}
async function load(){
 btn.disabled=true;
 results.hidden=true;
 status.textContent="Consultando resultados archivados y su fecha de verificación…";
 try{
  const response=await fetch("datos/evaluacion_prospectiva_6g.json",{cache:"no-store"});
  if(!response.ok)throw Error("Resultado no publicado todavía (HTTP "+response.status+")");
  const j=await response.json();
  if(j.fase!=="6G"||j.son_predicciones_oaf!==false||
     j.validacion_instrumental!==false||j.retraso_seguridad_dias!==7||
     !Array.isArray(j.metricas_por_localidad_horizonte_y_variable)||
     !Number.isInteger(j.jornadas_verificadas)||!Number.isInteger(j.jornadas_elegibles)||
     !["pendiente_reanalisis","con_resultados_reanalisis"].includes(j.estado))
    throw Error("Producto de verificación no auditado");
  const first=j.primera_fecha_elegible;
  if(j.estado==="pendiente_reanalisis"){
    if(j.jornadas_verificadas!==0||j.metricas_por_localidad_horizonte_y_variable.length)
       throw Error("El estado pendiente contiene cifras inconsistentes");
    archive=j;
    status.textContent="Pendiente de datos de reanálisis. Primera fecha elegible: "+
      (first||"sin fecha")+". Pronósticos archivados: "+j.jornadas_pronosticadas_en_archivo+
      " jornadas por localidad. No se puede calcular todavía ningún error ni porcentaje de acierto.";
    return;
  }
  if(j.jornadas_verificadas<1)throw Error("Se declaró verificación sin jornadas comparables");
  if(j.metricas_por_localidad_horizonte_y_variable.some(x=>
     !Number.isFinite(x.mae)||!Number.isFinite(x.sesgo)||
     !Number.isFinite(x.rmse)||x.n_emisiones_verificadas<1||
     !Object.hasOwn(varMap,x.variable)))throw Error("Métricas inválidas");
  archive=j;
  status.textContent="Hay jornadas verificadas con reanálisis ERA5 / ERA5-Land. "+
    "Consulta los errores por localidad, variable y horizonte. "+
    "Estos datos NO son observaciones instrumentales SENAMHI ni una alerta OAF.";
  render();
 }catch(err){status.textContent="Verificación no disponible: "+err.message+". No se generan valores de reemplazo."}
 finally{btn.disabled=false}
}
area.addEventListener("change",render);
variable.addEventListener("change",render);
btn.addEventListener("click",load);
panel.addEventListener("toggle",()=>{if(panel.open&&!once){once=true;load()}});
})();
