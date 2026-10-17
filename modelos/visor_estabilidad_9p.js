/* Fase 9P: estabilidad climática por décadas. Ningún grupo aquí es certificado. */
(()=>{"use strict";
const id=x=>document.getElementById(x);
const text=(x,v)=>{const n=id(x);if(n)n.textContent=v};
const fmt=(v,d=2)=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:d}):"Sin datos";
async function data(name){
 const r=await fetch("datos/continuidad_9p/"+name,{cache:"no-store"});
 if(!r.ok)throw Error("Datos 9P aún no publicados: "+name);
 return r.json();
}
async function init(){
 if(!id("oaf-9p-visor"))return;
 try{
 const [report,mirror]=await Promise.all([
   data("estado_estabilidad_9p.json"),
   data("fuentes_adicionales_chirps_9p.json")]);
 if(report.fase!=="9P"||mirror.fase!=="9P"||
    report.n_zonas_climaticamente_homogeneas_certificadas!==0||
    report.precision_predictiva_de_alertas_validada!==false||
    report.n_meses_chirps_agregados_9p!==mirror.n_meses_9p_nuevos||
    report.n_meses_chirps_comprobados_total!==mirror.n_meses_referencia_9o+
      mirror.n_meses_9p_nuevos)
  throw Error("La información fuente no pasó la verificación de 9P.");
 text("oaf-9p-months",report.n_meses_chirps_comprobados_total+" / 360");
 text("oaf-9p-years",report.n_anios_fuente_completos+" / 30");
 text("oaf-9p-source",mirror.mirroring_verificado?
   "Espejo USGS verificado por comparación con CHIRPS LATAM, "+
   mirror.n_meses_9p_nuevos+" meses adicionales. Archivos identificados mediante SHA-256.":
   "USGS aún no superó la prueba de equivalencia con CHIRPS LATAM. "+
   "No se han incorporado meses de una fuente diferente."+
   (mirror.problema_sonda?" Incidencia: "+mirror.problema_sonda:""));
 const decades=id("oaf-9p-decades");decades.replaceChildren();
 for(const [range,count] of Object.entries(report.anios_por_decada_fuentes)){
   const tr=document.createElement("tr");
   [range,String(count)+" de 10 años completos",
     count>=5?"Muestra con al menos 5 años; no certificada":
     "Insuficiente para validar una década"].forEach(v=>{
      const td=document.createElement("td");td.textContent=v;tr.append(td);
     });
   decades.append(tr);
 }
 const tbody=id("oaf-9p-pairs");tbody.replaceChildren();
 for(const pair of report.resumen_pares){
   const tr=document.createElement("tr");
   [pair.sector_a+" – "+pair.sector_b,String(pair.n_anios_comunes),
     fmt(pair.r_todos_meses,3),
     pair.r_loyo_min===null?"No evaluable":fmt(pair.r_loyo_min,3)+" a "+fmt(pair.r_loyo_max,3),
     pair.diferencia_lluvia_anual_pct===null?"No evaluable":
       fmt(pair.diferencia_lluvia_anual_pct,1)+" %",
     "Sin validación"].forEach(v=>{
       const td=document.createElement("td");td.textContent=v;tr.append(td);
     });
   tbody.append(tr);
 }
 text("oaf-9p-conclusion","El contraste usa "+
   report.n_anios_fuente_completos+
   " años CHIRPS con 12 meses comprobados y hasta "+
   report.testigos_reanalisis_1996_2025_completos+
   " puntos de reanálisis 1996–2025. La correlación se recalcula excluyendo un año"+
   " cada vez; no mide la precisión futura de un pronóstico ni certifica microclimas.");
 }catch(err){
   text("oaf-9p-source","Visor 9P pendiente de datos: "+err.message+
   ". Los resultados de las fases 9O y anteriores continúan disponibles.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();