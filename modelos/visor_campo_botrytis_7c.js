/* OAF Fase 7C: public readiness metadata only — NEVER reads private field CSV. */
(function(){
"use strict";
const panel=document.getElementById("oaf-field-7c");
if(!panel)return;
const status=document.getElementById("oaf-field-7c-status");
const button=document.getElementById("oaf-field-7c-reload");
const info=document.getElementById("oaf-field-7c-info");
let first=false;
async function load(){
 button.disabled=true;
 info.hidden=true;
 status.textContent="Consultando únicamente el estado agregado de datos de campo…";
 try{
   const response=await fetch("datos/estado_campo_botrytis_7c.json",{cache:"no-store"});
   if(!response.ok)throw Error("Informe de calidad de campo no disponible (HTTP "+response.status+")");
   const data=await response.json();
   if(data.fase!=="7C"||typeof data.estado!=="string"||
      typeof data.hay_registros_campo!=="boolean"||
      data.hay_modelo_predictivo_de_infeccion!==false||
      data.probabilidad_infeccion_calibrada!==false||
      data.alerta_fitosanitaria!==false||
      data.validacion_prospectiva_en_parcela!==false)
      throw Error("El estado público no cumple controles científicos");
   const valid=["sin_datos_campo","requiere_correccion","solo_vigilancia_sin_validacion","datos_parciales_pendientes_de_validacion"];
   if(!valid.includes(data.estado))throw Error("Estado de investigación desconocido");
   const mapping={
    "sin_datos_campo":"Sin observaciones reales de parcelas. Las plantillas y pruebas de integridad están preparadas; no hay incidencia ni probabilidades que calcular.",
    "requiere_correccion":"Hay registros de campo, pero se detectaron problemas de integridad. No se entrena ningún modelo hasta resolverlos.",
    "solo_vigilancia_sin_validacion":"Existen algunas observaciones, pero todavía faltan diagnósticos, sensores calibrados o emparejamiento de parcela y fecha. No hay validación de infección.",
    "datos_parciales_pendientes_de_validacion":"Existen datos iniciales compatibles con algunos requisitos; falta evaluación epidemiológica independiente y por parcela. Ningún modelo de infección está validado."
   };
   status.textContent=mapping[data.estado];
   document.getElementById("oaf-field-7c-updated").textContent=data.fecha_generacion_utc||"sin fecha";
   document.getElementById("oaf-field-7c-private").textContent=data.conteos_ocultos_por_confidencialidad?
     "Conteos agregados protegidos por tratarse de pocas parcelas.":"Ningún nombre ni ubicación exacta de parcela se publica aquí.";
   info.hidden=false;
 }catch(e){
   status.textContent="El estado de campo no está disponible: "+e.message+". No se sustituyen datos faltantes.";
 }finally{button.disabled=false}
}
button.addEventListener("click",load);
panel.addEventListener("toggle",()=>{if(panel.open&&!first){first=true;load()}});
})();