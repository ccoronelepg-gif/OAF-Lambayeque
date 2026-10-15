/* OAF 8A: observable immutable NOAA ERSSTv5 experimental forecast issue and verification.
 * No official ICEN, ENFEN category, or operational forecast confidence.
 */
(function(){
"use strict";
const root=document.getElementById("oaf-ocean-archive-8a");
if(!root)return;
const btn=document.getElementById("oaf-ocean-archive-8a-reload");
const stat=document.getElementById("oaf-ocean-archive-8a-status");
const panel=document.getElementById("oaf-ocean-archive-8a-data");
const rowTarget=document.getElementById("oaf-ocean-archive-8a-rows");
const method=document.getElementById("oaf-ocean-archive-8a-method");
const link=document.getElementById("oaf-ocean-archive-8a-link");
const n=(x,places=3)=>Number.isFinite(x)?x.toLocaleString("es-PE",{minimumFractionDigits:places,maximumFractionDigits:places}):"—";
let once=false;
async function load(){
 btn.disabled=true;
 panel.hidden=true;
 stat.textContent="Comprobando la emisión archivada y su estado de verificación…";
 try{
  const response=await fetch("datos/verificacion_oceanica_8a.json",{cache:"no-store"});
  if(!response.ok)throw Error("El resumen de emisiones aún no está publicado (HTTP "+response.status+")");
  const j=await response.json();
  if(j.fase!=="8A"||j.es_icen_oficial!==false||j.es_alerta_enfen!==false||
      j.validacion_operativa!==false||j.son_proyecciones_oceanicas_experimentales!==true||
      !Number.isInteger(j.pronosticos_archivados)||
      !Number.isInteger(j.predicciones_verificadas)||
      !Array.isArray(j.ultima_emision_pronosticos)||
      !["pendiente_maduracion_oceanica","con_verificaciones_exploratorias"].includes(j.estado)){
   throw Error("Procedencia o campos de verificación no autorizados");
  }
  const path=j.ultima_emision_almacenada;
  if(typeof path!=="string"||!/^datos\/pronosticos_oceanicos_emitidos\/\d{4}-\d{2}\.json$/.test(path))
   throw Error("Falta una emisión verificable con ruta admitida");
  const snapshotResponse=await fetch(path,{cache:"no-store"});
  if(!snapshotResponse.ok)throw Error("No se encuentra la emisión congelada");
  const issue=await snapshotResponse.json();
  if(issue.fase!=="8A"||issue.es_icen_oficial!==false||
     issue.es_alerta_enfen!==false||issue.prediccion_elnino_costero_validada!==false||
     !Array.isArray(issue.pronosticos)||issue.pronosticos.length!==3||
     typeof issue.emision_utc!=="string"||!(/^\d{4}-\d{2}$/.test(issue.mes_origen))){
   throw Error("Contenido de la emisión sin controles científicos");
  }
  const expected=issue.pronosticos.map(x=>x.mes_objetivo);
  if(expected.length!==new Set(expected).size)throw Error("Meses objetivo repetidos");
  rowTarget.replaceChildren();
  const current=j.ultima_emision_pronosticos;
  for(const record of issue.pronosticos){
   if(!Number.isInteger(record.horizonte_meses)||
      record.horizonte_meses<1||record.horizonte_meses>3||
      !Number.isFinite(record.pronostico_ar1_c)||
      !Number.isFinite(record.persistencia_c)||
      typeof record.emitido_antes_de_inicio_mes!=="boolean")throw Error("Pronóstico incompleto");
   const verification=current.find(x=>x.mes_objetivo===record.mes_objetivo&&x.horizonte_meses===record.horizonte_meses);
   const cells=[
     record.mes_objetivo,
     n(record.pronostico_ar1_c)+" °C",
     n(record.persistencia_c)+" °C",
     record.emitido_antes_de_inicio_mes?"Antes de comenzar el mes":"Intramensual (ahora-cast)",
     verification?.estado==="verificado_con_serie_revisada"?"Comparación retrospectiva disponible":"Pendiente de observación NOAA"
   ];
   const tr=document.createElement("tr");
   for(const value of cells){
     const td=document.createElement("td");td.textContent=value;tr.appendChild(td);
   }
   rowTarget.appendChild(tr);
  }
  method.textContent="Emisión congelada "+issue.emision_local_peru+
    " · Último valor disponible: "+issue.mes_origen+" ("+n(issue.anomalia_observada_origen_c)+" °C). "+
    "Fuente NOAA NCEI ERSSTv5 ajustada por el OAF a 1991–2020. "+
    "Verificados: "+j.predicciones_verificadas+" de "+j.pronosticos_archivados+
    " cálculos archivados; primera comparación posible: "+(j.primera_fecha_verificacion_posible||"sin fecha")+
    ". El desempeño del modelo no ha demostrado superar a persistencia.";
  link.href=path;
  stat.textContent=j.predicciones_verificadas===0?
   "Ninguna proyección archivada ha madurado para compararse con las observaciones NOAA. No se presentan aciertos ni habilidad prospectiva.":"Ya existen comparaciones exploratorias con observaciones NOAA posiblemente revisadas. No son alertas ni una validación operativa.";
  panel.hidden=false;
 }catch(error){
  stat.textContent="Registro oceánico no verificable: "+error.message+". No se reemplazan datos faltantes con cifras imaginadas.";
 }finally{btn.disabled=false}
}
btn.addEventListener("click",load);
root.addEventListener("toggle",()=>{if(root.open&&!once){once=true;load()}});
})();