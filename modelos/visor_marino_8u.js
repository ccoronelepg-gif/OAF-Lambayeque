/* OAF 8U, reading only genuine audited weather/ocean evidence. */
(()=>{
"use strict";
const details=document.getElementById("oaf-factors-8u");
if(!details)return;
const $=id=>document.getElementById(id);
const marine=$("oaf-8u-marine"),text=$("oaf-8u-marine-status");
if(!marine||!text)return;
const fmt=v=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:3}):"—";
function write(table,values){
 const tr=document.createElement("tr");
 for(const v of values){
  const td=document.createElement("td");td.textContent=String(v);tr.append(td);
 }
 table.append(tr);
}
async function load(){
 marine.replaceChildren();
 text.textContent="Comprobando procedencia y cobertura de las fuentes marinas…";
 const result=await Promise.allSettled([
  fetch("datos/marino_8u/estado_marino_8u.json",{cache:"no-store"}).then(r=>{
   if(!r.ok)throw Error("Sin archivo marino auditado");return r.json();
  })]);
 const remarks=[];
 if(result[0].status==="fulfilled"){
  const data=result[0].value;
  if(data.fase==="8U"&&data.corrientes_historicas_30_anios_integradas===false&&
      data.validacion_instrumental_independiente===false&&
      data.habilidad_pronostico_marino_demostrada===false&&
      Array.isArray(data.puntos)&&data.puntos.length===3&&
      /^[a-f0-9]{64}$/.test(data.sha256_respuesta_marina_original)){
   for(const p of data.puntos){
     const values=[p.id,fmt(p.sst_media_modelada_c),
      fmt(p.velocidad_media_modelada_ms),fmt(p.u_media_modelada_ms),
      fmt(p.v_media_modelada_ms),p.n_horas_con_las_3_variables];
     write(marine,values);
   }
   remarks.push("Corrientes y SST modeladas archivadas "+data.fecha_de_consulta_utc+
       " (72 horas, NO 30 años ni boyas reales).");
  }else remarks.push("La fuente marina disponible no supera los controles de interpretación.");
 }else remarks.push("Aún no hay pronóstico marino modelado validado.");
 text.textContent=remarks.join(" ");
}
$("oaf-8u-marine-refresh")?.addEventListener("click",load);
let initialized=false;
details.addEventListener("toggle",()=>{
 if(details.open&&!initialized){initialized=true;load()}
});
})();