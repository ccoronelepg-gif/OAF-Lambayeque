/* OAF 8T: NOAA indice Niño1+2 con fuente revisada; prueba retrospectiva no operativa. */
(()=>{
"use strict";
const root=document.getElementById("oaf-ocean-8t");if(!root)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8t-status");
const windows=$("oaf-8t-windows"),folds=$("oaf-8t-spatial");
const nf=x=>typeof x==="number"&&Number.isFinite(x)?x.toLocaleString("es-PE",{maximumFractionDigits:4}):"—";
const title={jerarquico_8s:"Solo anomalías meteorológicas",jerarquico_nino12:"Anomalías + Niño 1+2"};
function addrow(target,values){
 const tr=document.createElement("tr");
 for(const v of values){let td=document.createElement("td");td.textContent=String(v);tr.append(td)}
 target.append(tr);
}
function reset(){
 windows.replaceChildren();folds.replaceChildren();
 for(const id of ["oaf-8t-cells","oaf-8t-base","oaf-8t-ocean"])$(id).textContent="—";
}
function show(r){
 reset();
 const overall=r.comparacion_bloques_espaciales;
 $("oaf-8t-cells").textContent=String(r.n_centros_temperatura_era5land_unicos);
 $("oaf-8t-base").textContent=nf(overall.modelo_8s_sin_oceano.rmse_c)+" °C";
 $("oaf-8t-ocean").textContent=nf(overall.modelo_seleccionado.rmse_c)+" °C";
 for(const w of r.ventanas_temporales){
  addrow(windows,[w.prueba,title[w.modelo_preseleccionado]||w.modelo_preseleccionado,
      nf(w.rmse_validacion_8s),nf(w.rmse_validacion_nino12),
      nf(w.rmse_prueba_8s),nf(w.rmse_prueba_oceanico),
      nf(w.rmse_prueba_seleccionado)]);
 }
 for(const s of r.controles_espaciales){
  addrow(folds,[String(s.corte),s.franja,s.celdas_retenidas,
      title[s.modelo_preseleccionado]||s.modelo_preseleccionado,
      nf(s.rmse_8s),nf(s.rmse_oceano),nf(s.rmse_seleccionado)]);
 }
 const percent=overall.mejora_RMSE_vs_8S;
 const comparison=percent==null?"sin comparación válida":nf(percent*100)+" %";
 status.textContent="Se fijó NOAA CPC Niño 1+2 con SHA-256; índice revisable y usado t−2. "+
   r.n_evaluaciones_espaciales+" predicciones históricas sobre "+r.n_centros_temperatura_era5land_unicos+
   " centros de celda. Variación RMSE ante 8S: "+comparison+
   ". "+
   (percent<0?"La estrategia preseleccionada empeora respecto al modelo 8S sin índice oceánico. ":"")+
   "Los índices no son los boletines ICEN/ENFEN ni comprueban habilidad de pronóstico prospectivo.";
}
async function load(){
 status.textContent="Validando índice NOAA, periodos reservados y archivos climáticos…";
 try{
  const response=await fetch("datos/validacion_oceanica_8t/estado_oceanico_8t.json",{cache:"no-store"});
  if(!response.ok)throw Error("La evaluación oceánica todavía no está publicada");
  const r=await response.json();
  if(r.fase!=="8T"||r.n_cortes_temporales!==5||
      r.rezago_oceanico_meses!==2||r.indice_1996_2025_se_puede_revisar_expost!==true||
      r.prediccion_prospectiva_demostrada!==false||
      r.habilidad_nino_costero_predecir_ENFEN_demostrada!==false||
      r.fuentes_de_datos_senamhi_instrumentales_integradas!==0||
      r.zonas_homogeneas_certificadas!==0||
      r.n_bloques_geo!==4||
      r.seleccion_de_modelo_solo_validacion_pasada!==true||
      r.bloque_latitudinal_retenido_fuera_del_ajuste_y_predictores_regionales!==true||
      r.n_evaluaciones_espaciales<=0||
      r.ventanas_temporales?.length!==5||
      r.controles_espaciales?.length!==20)
    throw Error("Los controles de honestidad y cronología 8T no concuerdan");
  show(r);
 }catch(e){
  reset();status.textContent="Sin evaluación NOAA publicada y verificable: "+e.message;
 }
}
$("oaf-8t-refresh")?.addEventListener("click",load);
let initiated=false;root.addEventListener("toggle",()=>{if(root.open&&!initiated){initiated=true;load()}});
})();