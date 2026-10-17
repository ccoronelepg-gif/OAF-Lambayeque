/* OAF 8U – Evidencia marina y de viento. Cifras solo de archivos auditados. */
(()=>{
"use strict";
const root=document.getElementById("oaf-factors-8u");if(!root)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8u-status");
const tbody=$("oaf-8u-wind");
const fmt=n=>typeof n==="number"&&Number.isFinite(n)?
 n.toLocaleString("es-PE",{maximumFractionDigits:3}):"—";
function show(report){
 tbody.replaceChildren();
 $("oaf-8u-blocks").textContent=report.bloques_viento_obtenidos+"/3";
 $("oaf-8u-cities").textContent=report.testigos_viento_historico_completos+"/4";
 $("oaf-8u-current").textContent=report.corrientes_marinas_serie_historica_verificada?
   "Serie verificada":"Datos aún pendientes";
 for(const name of report.localidades){
  const v=report.resumen_viento_por_localidad.find(x=>x.localidad===name);
  const tr=document.createElement("tr");
  for(const val of [name,v?fmt(v.viento_media_ms):"Pendiente 30 años",
    v?fmt(v.viento_max_diario_prom_ms):"Pendiente 30 años",
    v?v.meses:report.bloques_viento_obtenidos*120,"ERA5, no SENAMHI"]){
    const td=document.createElement("td");td.textContent=String(val);tr.append(td);
  }
  tbody.append(tr);
 }
 status.textContent="Viento ERA5: "+report.bloques_viento_obtenidos+
   " de 3 décadas archivadas; "+report.meses_localidad_obtenidos+
   " meses-localidad verificables. SST Niño 1+2 NOAA: "+
   (report.indices_sst_noaa_1996_2025_archivados?"360 meses históricos disponibles (serie revisable).":"pendiente")+
   ". Corrientes oceánicas u/v: "+
   (report.corrientes_marinas_serie_historica_verificada?"verificadas.":"no disponibles todavía para inferir dinámica marina.")+
   " No hay pronóstico conjunto ni validación instrumental.";
}
async function load(){
 status.textContent="Auditando fuentes originales de viento, SST y catálogo de corrientes…";
 try{
   const response=await fetch("datos/viento_8u/estado_factores_8u.json",{cache:"no-store"});
   if(!response.ok)throw Error("Estado 8U todavía no publicado");
   const r=await response.json();
   if(r.fase!=="8U"||r.periodo!=="1996–2025"||
       r.corrientes_no_inferibles_del_viento_ni_del_SST!==true||
       r.datos_no_son_observaciones_senamhi!==true||
       r.modelo_predictivo_viento_corriente_ya_validado!==false||
       r.zonas_homogeneas_certificadas!==0||
       r.localidades?.length!==4||r.bloques_viento_obtenidos>3||
       r.resumen_viento_por_localidad?.length!==r.testigos_viento_historico_completos)
       throw Error("Metadatos fuente o control metodológico no coinciden");
   show(r);
 }catch(e){
   tbody.replaceChildren();
   status.textContent="Sin fuente 8U presentable: "+e.message;
 }
}
$("oaf-8u-refresh")?.addEventListener("click",load);
let started=false;root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;load()}});
})();