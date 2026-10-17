/* OAF 8U – Evidencia marina y de viento. Cifras solo de archivos auditados. */
(()=>{
"use strict";
const root=document.getElementById("oaf-factors-8u");if(!root)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8u-status");
const tbody=$("oaf-8u-wind"), correlations=$("oaf-8u-correlations"),
      coverage=$("oaf-8u-coverage");
const fmt=n=>typeof n==="number"&&Number.isFinite(n)?
 n.toLocaleString("es-PE",{maximumFractionDigits:3}):"—";
function show(report,associations,coastal){
 tbody.replaceChildren();correlations.replaceChildren();coverage.replaceChildren();
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
 for(const item of associations.localidades){
   const tr=document.createElement("tr");
   for(const val of [item.localidad,item.n_meses_rezago_2,
       fmt(item.r_anomalia_viento_sst_menos_2),
       fmt(item.r_componente_u_aproximada_sst_menos_2),
       fmt(item.r_componente_v_aproximada_sst_menos_2),
       "Descriptivo, no pronóstico"]){
     const td=document.createElement("td");td.textContent=String(val);tr.append(td);
   }
   correlations.append(tr);
 }
 $("oaf-8u-sst").textContent=coastal.archivos_sst_verificados+"/"+coastal.archivos_sst_previstos;
 for(const record of coastal.cobertura_diaria_por_archivo||[]){
  const row=document.createElement("tr");
  for(const value of [record.sitio,record.periodo.join("–"),
        record.dias_validos,record.dias_faltantes,
        record.cobertura_completa?"Década completa":"Archivo parcial, no climatología"]){
    const td=document.createElement("td");td.textContent=String(value);row.append(td);
  }
  coverage.append(row);
 }
 status.textContent="Viento ERA5: "+report.bloques_viento_obtenidos+
   " de 3 décadas archivadas; "+report.meses_localidad_obtenidos+
   " meses-localidad verificables. SST Niño 1+2 NOAA: "+
   (report.indices_sst_noaa_1996_2025_archivados?"360 meses históricos disponibles (serie revisable).":"pendiente")+
   ". Corrientes oceánicas u/v: "+
   (report.corrientes_marinas_serie_historica_verificada?"verificadas.":"no disponibles todavía para inferir dinámica marina.")+
   " SST oceánica OISST: "+coastal.archivos_sst_verificados+"/6 archivos recibidos, "+
   (coastal.n_dias_faltantes_en_archivos_recibidos||0)+" días faltantes en archivos recuperados; "+
   coastal.sitios_con_sst_30anios_completa+" sitios con 30 años completos. "+
   "No hay pronóstico conjunto ni validación instrumental.";
}
async function load(){
 status.textContent="Auditando fuentes originales de viento, SST y catálogo de corrientes…";
 try{
   const urls=["datos/viento_8u/estado_factores_8u.json",
       "datos/relaciones_viento_sst_8u/estado_relaciones_8u.json",
       "datos/sst_costera_8u/estado_sst_8u.json"];
   const responses=await Promise.all(urls.map(u=>fetch(u,{cache:"no-store"})));
   if(responses.some(r=>!r.ok))throw Error("Fuentes 8U todavía no publicadas");
   const [r,associations,coastal]=await Promise.all(responses.map(x=>x.json()));
   if(r.fase!=="8U"||r.periodo!=="1996–2025"||
       r.corrientes_no_inferibles_del_viento_ni_del_SST!==true||
       r.datos_no_son_observaciones_senamhi!==true||
       r.modelo_predictivo_viento_corriente_ya_validado!==false||
       r.zonas_homogeneas_certificadas!==0||
       r.localidades?.length!==4||r.bloques_viento_obtenidos>3||
       r.resumen_viento_por_localidad?.length!==r.testigos_viento_historico_completos)
       throw Error("Metadatos fuente o control metodológico no coinciden");
   if(associations.fase!=="8U"||associations.habilidad_predictiva_validada!==false||
       associations.corrientes_marinas_vectoriales_utilizadas!==false||
       associations.localidades?.length!==4||associations.n_comparaciones!==1440||
       coastal.fase!=="8U"||coastal.sst_no_es_velocidad_de_corrientes!==true||
       coastal.sitios_con_sst_30anios_completa>coastal.puntos_oceanicos_de_ensayo||
       coastal.archivos_sst_verificados>coastal.archivos_sst_previstos)
       throw Error("Asociaciones o SST costera sin procedencia metodológica");
   show(r,associations,coastal);
 }catch(e){
   tbody.replaceChildren();correlations.replaceChildren();coverage.replaceChildren();
   status.textContent="Sin fuente 8U presentable: "+e.message;
 }
}
$("oaf-8u-refresh")?.addEventListener("click",load);
let started=false;root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;load()}});
})();