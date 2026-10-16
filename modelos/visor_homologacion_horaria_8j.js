/* OAF-Lambayeque · 8J. Panel de horarios y representatividad.
 * Prohibido presentar datos ficticios o independencia instrumental no certificada.
 */
(()=>{
"use strict";
const root=document.getElementById("oaf-hourly-8j");if(!root)return;
const $=id=>document.getElementById(id);
const state=$("oaf-8j-state"),table=$("oaf-8j-months"),visual=$("oaf-8j-chart");
let ready=false;
function cell(tr,value){const td=document.createElement("td");td.textContent=String(value);tr.appendChild(td)}
const fmt=x=>typeof x==="number"&&Number.isFinite(x)?x.toLocaleString("es-PE",{maximumFractionDigits:2}):"—";
async function load(){
 state.textContent="Cargando resultados auditados de la fase 8J…";
 try{
 const [resp,csvresp]=await Promise.all([
   fetch("datos/homologacion_horaria_8j/estado_8j.json",{cache:"no-store"}),
   fetch("datos/homologacion_horaria_8j/comparaciones_horarias_8j.csv",{cache:"no-store"})
 ]);
 if(!resp.ok||!csvresp.ok)throw Error("No se encuentran las salidas 8J");
 const d=await resp.json(),csv=await csvresp.text();
 if(d.fase!=="8J"||d.validacion_independiente_demostrada!==false||
    d.habilidad_predictiva_8e_demostrada!==false||
    d.intervalos_predictivos_90_calibrados!==false||
    !Number.isInteger(d.estaciones_fuente_autorizada)||
    !Number.isInteger(d.meses_horarios_completos)||
    !Number.isInteger(d.pares_descriptivos_estacion_era5)||
    !csv.startsWith("codigo_estacion,localidad_oaf,mes,"))
    throw Error("La evidencia no satisface la política de verificaciones del OAF");
 $("oaf-8j-sources").textContent=fmt(d.estaciones_fuente_autorizada);
 $("oaf-8j-complete").textContent=fmt(d.meses_horarios_completos);
 $("oaf-8j-pairs").textContent=fmt(d.pares_descriptivos_estacion_era5);
 table.replaceChildren();visual.replaceChildren();
 const sites=["Chiclayo","Jayanca","Motupe","Olmos"];
 let n=0;
 for(const site of sites){
   const m=d.estadisticas_por_localidad?.[site];
   if(!m||!Number.isInteger(m.n))throw Error("Conteos geográficos inconsistentes");
   const tr=document.createElement("tr");
   cell(tr,site);cell(tr,m.n);
   cell(tr,typeof m.mae_c==="number"?fmt(m.mae_c)+" °C":"No evaluable");
   cell(tr,typeof m.sesgo_c==="number"?fmt(m.sesgo_c)+" °C":"No evaluable");
   table.appendChild(tr);n+=m.n;
 }
 if(n!==d.pares_descriptivos_estacion_era5)throw Error("La suma de localidades no coincide");
 if(!d.estaciones_fuente_autorizada){
   state.textContent="Pendiente: todavía no se dispone de series SENAMHI horarias autorizadas y verificadas. No se inventan temperaturas ni resultados.";
   const p=document.createElement("p");p.className="small";
   p.textContent="Cuando existan datos válidos, aparecerá la cobertura horaria mensual comprobada y su evaluación de representatividad.";
   visual.append(p);
 }else{
   const lines=csv.trim().split(/\r?\n/),head=lines.shift().split(",");
   const take=(r,key)=>r[head.indexOf(key)];
   for(const raw of lines.slice(0,24)){
     const row=raw.split(",");
     if(row.length!==head.length)throw Error("CSV de meses 8J malformado");
     const outer=document.createElement("div");outer.style.cssText="display:grid;grid-template-columns:115px 1fr 70px;align-items:center;gap:12px;margin:9px 0";
     const label=document.createElement("span");label.className="small";
     label.textContent=take(row,"localidad_oaf")+" "+take(row,"mes");
     const bg=document.createElement("div");bg.style.cssText="height:13px;border-radius:7px;background:#e4eef4;overflow:hidden";
     const percent=100*Number(take(row,"horas_validas"))/Math.max(1,Number(take(row,"horas_calendario")));
     const fill=document.createElement("div");fill.style.cssText="background:#068f9a;height:100%;width:"+Math.min(100,Math.max(0,percent)).toFixed(1)+"%";
     bg.append(fill);const val=document.createElement("small");val.textContent=percent.toFixed(1)+" %";
     outer.append(label,bg,val);visual.append(outer);
   }
   state.textContent="Contrastes exploratorios sujetos a auditoría de coordenadas, altitud, método temporal e independencia. No constituyen habilidad predictiva 8E.";
 }
 }catch(err){
   state.textContent="Sin datos 8J verificables: "+err.message+". No se reemplazan con valores simulados.";
   table.replaceChildren();visual.replaceChildren();
 }
}
root.addEventListener("toggle",()=>{if(root.open&&!ready){ready=true;load()}});
$("oaf-8j-reload")?.addEventListener("click",load);
})();
