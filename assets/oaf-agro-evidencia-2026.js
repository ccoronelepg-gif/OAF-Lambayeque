(function evidenceOAF(){
"use strict";
const get=path=>fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()});
function init(){
 const home=document.getElementById("oaf-home-predictive-brief");
 if(!home)return;
 Promise.allSettled([get("datos/rf_precipitacion_10i/informe_rf_lluvia_10i.json"),get("datos/estado_enfen_3z.json")]).then(results=>{
  const [rf,enfen]=results;
  home.replaceChildren();
  const title=document.createElement("strong");title.textContent="Vigilancia predictiva y análisis científico · resumen";
  const para=document.createElement("p");para.style.margin="7px 0 0";
  const notes=[];
  if(rf.status==="fulfilled"){
   const r=rf.value,metrics=r.resultados?.lluvia?.global;
   if(metrics&&Number.isFinite(metrics.mae_rf_mm)&&Number.isFinite(metrics.mae_climatologia_mm)){
    notes.push(`Random Forest OAF (evaluación histórica ${r.particiones?.prueba?.join(" a ")||"2021–2025"}): error MAE ${metrics.mae_rf_mm.toFixed(2)} mm, frente a ${metrics.mae_climatologia_mm.toFixed(2)} mm de la climatología. El modelo aún requiere mejora para superar la referencia.`);
   }else notes.push("El modelo Random Forest tiene documentación reproducible, pero la síntesis de métricas no está disponible en esta consulta.");
  }else notes.push("Los resultados de evaluación Random Forest no están disponibles para síntesis.");
  if(enfen.status==="fulfilled"){
   const e=enfen.value;
   if(e.verificacion==="verificada"&&e.fecha_emision&&e.estado_institucional){
    notes.push(`Último comunicado ENFEN archivado: ${e.fecha_emision}, ${e.estado_institucional}. Consultar la institución para posibles actualizaciones.`);
   }else notes.push("Comunicado ENFEN vigente: verificación automática pendiente; consultar publicación institucional para el estado más reciente.");
  }else notes.push("Comunicados ENFEN: consulta institucional pendiente.");
  notes.push("Para lluvia de siete días se muestran datos del proveedor externo; las probabilidades de brotes fitosanitarios no se publican sin validación de campo.");
  para.textContent=notes.join(" ");
  const link=document.createElement("a");link.href="#autor";link.className="oaf-agro-link";link.textContent="Consultar predicciones y auditoría →";
  home.append(title,para,link);
 }).catch(()=>{home.textContent="Consulta de modelos y comunicados temporalmente no disponible. Revisa Predicciones y boletines."});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
