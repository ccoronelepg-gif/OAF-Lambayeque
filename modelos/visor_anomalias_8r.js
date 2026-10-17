/* OAF 8R: backtest 1 mes, reservando 2016–2025 y eliminando doble peso de píxeles. */
(()=>{
"use strict";
const panel=document.getElementById("oaf-forecast-8r");if(!panel)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8r-status"),table=$("oaf-8r-table"),sites=$("oaf-8r-sites"),
      spatial=$("oaf-8r-spatial"),bars=$("oaf-8r-bars");
const numbers=v=>Number(v).toLocaleString("es-PE",{maximumFractionDigits:3});
const labels={climatologia:"Climatología (anomalía = 0)",
              persistencia:"Persistencia mensual",
              regional_rezago:"Señal regional rezagada",
              jerarquico:"Regresión local + regional"};
function csv(txt){
 const lines=txt.trim().split(/\r?\n/),heads=lines.shift().split(",");
 return lines.filter(Boolean).map(line=>{
  const fields=line.split(",");
  if(fields.length!==heads.length)throw Error("CSV de predicciones malformado");
  return Object.fromEntries(heads.map((k,i)=>[k,fields[i]]));
 });
}
function reset(){table.replaceChildren();sites.replaceChildren();spatial.replaceChildren();bars.replaceChildren()}
function rowTo(table,values){
 const tr=document.createElement("tr");
 for(const value of values){const cell=document.createElement("td");cell.textContent=String(value);tr.append(cell)}
 table.append(tr);
}
function render(report,records){
 reset();
 const test=report.evaluacion_prueba_por_celda;
 const choice=report.estrategia_seleccionada_por_validacion;
 $("oaf-8r-strategy").textContent=labels[choice];
 $("oaf-8r-rmse").textContent=numbers(test[choice].rmse_c)+" °C";
 $("oaf-8r-skill").textContent=numbers(report.comparacion_prueba.skill_rmse_frente_persistencia*100)+" %";
 for(const key of Object.keys(labels)){
   rowTo(table,[labels[key],numbers(report.evaluacion_validacion_rmse_por_celda[key].rmse_c),
     numbers(test[key].rmse_c),key===choice?"Seleccionado 2011–2015":"Comparador"]);
   const bar=document.createElement("div");
   bar.style.cssText="display:flex;align-items:center;gap:10px;margin:7px 0";
   const cap=document.createElement("span");
   cap.textContent=labels[key];cap.style.cssText="width:185px;font-size:12px;flex-shrink:0";
   const width=Math.max(3,Math.min(100,100*test[key].rmse_c/test.climatologia.rmse_c));
   const line=document.createElement("span");
   line.style.cssText="display:block;width:"+width+"%;height:15px;background:"+
     (key===choice?"#159a91":"#8b9fa7")+";border-radius:5px";
   const label=document.createElement("span");label.textContent=numbers(test[key].rmse_c)+" °C";
   label.style.cssText="font-size:12px;white-space:nowrap";
   const area=document.createElement("span");area.style.cssText="flex:1;display:flex;align-items:center;min-width:80px";
   area.append(line);bar.append(cap,area,label);bars.append(bar);
 }
 for(const p of report.evaluacion_prueba_por_testigo){
  rowTo(sites,[p.id,p.transecto,
     numbers(p.rmse_seleccionado_c),numbers(p.rmse_persistencia_c),
     p.replica_de_celda_compartida?"Sí":"No"]);
 }
 const transfer=report.prueba_transferencia_espacial_de_coeficientes;
 rowTo(spatial,["Modelo con píxel retenido",
   numbers(transfer.evaluacion_global_puntos_retenidos.seleccionado.rmse_c)+" °C",
   transfer.n_celdas_retenidas_por_turno+" centros ERA5-Land"]);
 rowTo(spatial,["Persistencia con píxel retenido",
   numbers(transfer.evaluacion_global_puntos_retenidos.persistencia.rmse_c)+" °C",
   "Igual periodo 2016–2025"]);
 const desc=document.createElement("p");desc.className="small";
 desc.textContent="Datos del test 2016–2025: "+records.length+" meses-sitio; "+
   report.n_centros_celda_era5land_distintos+" centros ERA5-Land únicos. "+
   "El mes anterior se usa como predictor; no se consulta el mes futuro.";
 bars.append(desc);
}
async function load(){
 status.textContent="Auditando cortes temporales, SHA de fuentes y predicciones retrospectivas…";
 try{
   const r=await Promise.all([
     fetch("datos/validacion_predictiva_8r/estado_validacion_8r.json",{cache:"no-store"}),
     fetch("datos/validacion_predictiva_8r/predicciones_retrospectivas_8r.csv",{cache:"no-store"})]);
   if(r.some(x=>!x.ok))throw Error("El experimento aún no está publicado");
   const [report,txt]=await Promise.all([r[0].json(),r[1].text()]);
   const records=csv(txt);
   if(report.fase!=="8R"||report.periodo_normales_exclusivo_calibracion!=="1996–2010"||
      report.periodo_seleccion_estrategia!=="2011–2015"||
      report.periodo_prueba_estrictamente_reservado!=="2016–2025"||
      report.validacion_instrumental_independiente!==false||
      report.evaluacion_prospectiva_real!==false||
      report.zonas_agroclimaticas_homogeneas_certificadas!==0||
      report.n_sitios!==10||report.n_centros_celda_era5land_distintos<3||
      !report.prueba_transferencia_espacial_de_coeficientes?.variables_regionales_del_ajuste_excluyen_la_celda_retenida)
      throw Error("La versión de resultados no satisface garantías del backtest");
   if(records.length!==report.n_sitios*report.n_meses_prueba_por_sitio)
     throw Error("Número de pronósticos mensuales inconsistente");
   for(const rec of records){
     if(rec.mes_objetivo<"2016-01"||rec.mes_objetivo>"2025-12"||
        rec.ultimo_mes_observado>=rec.mes_objetivo||
        rec.metodo_seleccionado!==report.estrategia_seleccionada_por_validacion||
        !Number.isFinite(Number(rec.seleccionado_pred_c))||
        !Number.isFinite(Number(rec.observacion_anomalia_c)))
        throw Error("Se detectó inconsistencia temporal o de estimación");
   }
   render(report,records);
   status.textContent="Ensayo retrospectivo de 1 mes adelante con 1996–2010 para calibración, "+
      "2011–2015 para selección y 2016–2025 para prueba. "+
      "Fuente ERA5-Land, NO estaciones SENAMHI ni pronóstico operativo.";
 }catch(e){
  reset();status.textContent="No hay una evaluación 8R verificable: "+e.message+
    ". No se presentan indicadores sintéticos.";
 }
}
$("oaf-8r-refresh")?.addEventListener("click",load);
let started=false;panel.addEventListener("toggle",()=>{if(panel.open&&!started){started=true;load()}});
})();