/* OAF 8S: resultados regionales solo tras CI y archivos de reanálisis auditados. */
(()=>{
"use strict";
const panel=document.getElementById("oaf-regional-8s");if(!panel)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8s-status"),folds=$("oaf-8s-folds"),alt=$("oaf-8s-altitude"),
      graphic=$("oaf-8s-graphic"),spatial=$("oaf-8s-spatial");
const pretty=x=>Number.isFinite(Number(x))?
 Number(x).toLocaleString("es-PE",{minimumFractionDigits:2,maximumFractionDigits:3}):"—";
function row(where,cells){
 const tr=document.createElement("tr");
 for(const content of cells){const td=document.createElement("td");td.textContent=String(content);tr.append(td)}
 where.append(tr);
}
function clear(){folds.replaceChildren();alt.replaceChildren();graphic.replaceChildren();spatial.replaceChildren()}
function visualize(s){
 clear();
 $("oaf-8s-cells").textContent=s.centros_celda_era5land_unicos;
 $("oaf-8s-temporal").textContent=pretty(s.evaluacion_temporal.seleccionado.rmse_c)+" °C";
 $("oaf-8s-spatial").textContent=pretty(s.evaluacion_con_bloque_retenido.seleccionado.rmse_c)+" °C";
 const base=s.evaluacion_con_bloque_retenido;
 const limits=[
  ["Modelo seleccionado",base.seleccionado.rmse_c],
  ["Persistencia",base.persistencia.rmse_c],
  ["Climatología",base.climatologia.rmse_c]];
 for(const [name,val] of limits){
  const line=document.createElement("div");
  line.style.cssText="display:flex;gap:8px;align-items:center;margin:8px 0;font-size:12px";
  const label=document.createElement("span");label.textContent=name;label.style.cssText="width:148px;flex-shrink:0";
  const wrapper=document.createElement("span");wrapper.style.cssText="flex:1;min-width:80px";
  const bar=document.createElement("span");bar.style.cssText="display:block;border-radius:5px;height:14px;width:"+
      Math.max(3,Math.min(100,100*val/base.climatologia.rmse_c))+"%;background:"+
      (name==="Modelo seleccionado"?"#168c83":"#849ba5");
  wrapper.append(bar);
  const value=document.createElement("strong");value.textContent=pretty(val)+" °C";
  line.append(label,wrapper,value);graphic.append(line);
 }
 for(const window of s.cortes_temporales){
  const selected=window.modelo_elegido;
  const scores=window.rmse_prueba_por_modelo;
  row(folds,[window.prueba,selected,pretty(scores[selected]),
    pretty(scores.persistencia),pretty(scores.climatologia),
    scores[selected]<scores.persistencia?"Sí":"No"]);
 }
 for(const b of s.evaluacion_por_estrato_altitudinal){
  row(alt,[b.estrato,b.n,pretty(b.seleccionado.rmse_c),
   pretty(b.persistencia.rmse_c),
   pretty(100*b.skill_rmse_vs_persistencia)+" %",
   b.mejora_persistencia?"Sí":"No"]);
 }
 const splitGroup={};
 for(const f of s.pliegues_espaciales){
   (splitGroup[f.bloque]??=[]).push(f);
 }
 for(const [block,recs] of Object.entries(splitGroup)){
    const improvement=recs.filter(x=>x.rmse_prueba_retenido<x.rmse_persistencia_retenido).length;
    row(spatial,[block,recs[0].centros_retenidos,recs.length,improvement+"/"+recs.length,
       "Banda latitudinal, no cuenca"]);
 }
 const note=document.createElement("p");note.className="small";
 note.textContent="La comparación usa "+
  s.testigos_empleados+" testigos ("+
  s.testigos_excluidos_dem_le_5m+" descartados preventivamente por cota DEM ≤5 m), "+
  s.centros_celda_era5land_unicos+" centros de celda distintos, "+
  s.n_cortes_rolling_origin+" ventanas temporales y "+
  s.n_bloques_espaciales_latitudinales+" franjas de prueba. "+
  "No es una evaluación SENAMHI ni pronóstico prospectivo.";
 graphic.append(note);
}
async function update(){
 status.textContent="Recalculando referencias de los archivos históricos 8O/8P…";
 try{
  const response=await fetch("datos/validacion_regional_8s/estado_validacion_8s.json",{cache:"no-store"});
  if(!response.ok)throw Error("El análisis regional aún no fue archivado");
  const s=await response.json();
  if(s.fase!=="8S"||s.prediccion_operativa_o_prospectiva_demostrada!==false||
      s.habilidad_confirmada_con_estaciones_SENAMHI!==false||
      s.zonas_agroclimaticas_homogeneas_certificadas!==0||
      s.ningun_test_utilizado_en_ajuste_o_seleccion!==true||
      s.señal_regional_entrenamiento_excluye_bloque_espacial_retenido!==true||
      s.n_cortes_rolling_origin!==5||s.cortes_temporales.length!==5||
      s.n_bloques_espaciales_latitudinales!==4||
      !s.evaluacion_temporal||!s.evaluacion_con_bloque_retenido)
    throw Error("El informe no satisface los controles de validación");
  visualize(s);
  const gain=s.evaluacion_con_bloque_retenido.skill_rmse_vs_persistencia;
  status.textContent="Cinco pruebas cronológicas sobre ERA5-Land y cuatro bloques geográficos latitudinales, "+
    s.n_predicciones_espaciales+" resultados retrospectivos. "+
    "Variación RMSE frente a persistencia: "+pretty(gain*100)+" %. "+
    (gain<0?"En este contraste empeora la persistencia. ":"")+
    "No hay verificación con estaciones independientes ni zonas certificadas.";
 }catch(e){
  clear();status.textContent="Fase 8S sin resultados regionales verificables: "+e.message;
 }
}
$("oaf-8s-refresh")?.addEventListener("click",update);
let started=false;panel.addEventListener("toggle",()=>{if(panel.open&&!started){started=true;update()}});
})();