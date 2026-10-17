/* OAF 9I: visor de comparación estrictamente simultánea, con periodos y ausencias visibles. */
(()=>{
"use strict";
const $=id=>document.getElementById(id);
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
const fmt=(n)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:2,maximumFractionDigits:2}):"—";
async function load(){
 const r=await fetch("datos/validacion_estaciones_9i/diagnostico_multianual_9i.json",{cache:"no-store"});
 if(!r.ok)throw Error("el diagnóstico 9I todavía no se ha publicado ("+r.status+")");
 const j=await r.json();
 if(j.fase!=="9I"||j.independencia_CHIRPS_validada!==false||
    j.pronosticos_archivados_con_vintage!==false)throw Error("metadatos científicos inesperados");
 return j;
}
function show(j){
 const code=$("oaf-9i-site").value,year=Number($("oaf-9i-year").value);
 const escenario=$("oaf-9i-scenario").value;
 const rec=j.resultados_estacion_escenario_anio.find(x=>
   x.codigo_archivo===code&&x.escenario===escenario&&x.anio===year);
 const report=$("oaf-9i-results");
 report.replaceChildren();
 if(!rec || !rec.n_meses_comunes){
   const p=el("p","No hay meses comunes verificados para esta estación, año y coordenada. No se calculan errores ni se estima lluvia faltante.");
   p.className="notice";report.append(p);return;
 }
 const line=el("p","Meses de estación con observación completa y ambos productos disponibles: "+
   rec.n_meses_comunes+" de 12. "+
   (rec.anio_completo_12_meses?"Cobertura anual completa.":"Cobertura parcial: no representar como año completo."));
 report.append(line);
 const grid=el("div");grid.className="oaf-9i-metrics";
 const score=(name,data)=>{
   const section=el("article");section.append(el("small",name));
   const number=el("strong",data?fmt(data.mae_mm_mes)+" mm/mes":"Sin datos");
   section.append(number);
   section.append(el("span",data?"MAE · Sesgo "+fmt(data.sesgo_producto_menos_estacion_mm_mes)+" mm/mes":"Sin pares comparables"));
   grid.append(section);
 };
 score("CHIRPS v3",rec.chirps);score("ERA5 atmosférico",rec.era5);
 report.append(grid);
 const max=Math.max(1,rec.chirps?.mae_mm_mes||0,rec.era5?.mae_mm_mes||0);
 for(const [name,d] of [["CHIRPS v3",rec.chirps],["ERA5 atmósfera",rec.era5]]){
   if(!d)continue;
   const box=el("div");box.className="oaf-9i-bar-row";
   box.append(el("p",name+" · "+fmt(d.mae_mm_mes)+" mm/mes"));
   const track=el("div");track.className="oaf-9i-track";
   const bar=el("div");bar.className="oaf-9i-fill";
   bar.style.width=(100*d.mae_mm_mes/max).toFixed(2)+"%";
   track.append(bar);box.append(track);report.append(box);
 }
 const note=el("p","Las barras muestran errores retrospectivos para los mismos "+rec.n_meses_comunes+
   " meses. Menor MAE no demuestra un mejor pronóstico futuro. Las dos coordenadas alternativas no son estaciones independientes.");
 note.className="oaf-figure-caption";report.append(note);
}
async function init(){
 if(!$("oaf-9i-visor"))return;
 const status=$("oaf-9i-status");
 try{
   const j=await load();
   const site=$("oaf-9i-site");
   const distinct=new Map();
   for(const rec of j.resultados_estacion_escenario_anio)distinct.set(rec.codigo_archivo,rec.nombre);
   for(const [code,name] of distinct){
     const opt=el("option",name);opt.value=code;site.append(opt);
   }
   const year=$("oaf-9i-year");
   for(const yr of j.anios_prespecificados){
     const opt=el("option",String(yr));opt.value=String(yr);year.append(opt);
   }
   site.value="00153114";year.value="1998";
   for(const id of ["oaf-9i-site","oaf-9i-year","oaf-9i-scenario"])
     $(id).addEventListener("change",()=>show(j));
   show(j);
   const yearsWithData=j.anios_resumen.filter(y=>y.meses_estacion_distintos_emparejados>0).map(y=>y.anio);
   status.textContent="Periodos con pares comprobados: "+yearsWithData.join(", ")+
     ". "+j.meses_estacion_unicos_emparejados+" meses-estación únicos (sin contar dos veces las coordenadas)."+
     (yearsWithData.length<j.anios_prespecificados.length?
     " Otros años aún sin pares CHIRPS disponibles.":"");
 }catch(error){
   status.textContent="Diagnóstico 9I pendiente: "+error.message+
     ". El contraste histórico 9H permanece disponible arriba.";
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();