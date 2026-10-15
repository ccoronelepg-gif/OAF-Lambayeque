/* OAF Fase 7B - retrospective validation of the atmospheric RH signal,
 * NOT disease, leaf wetness or field validation.
 */
(function(){
"use strict";
const p=document.getElementById("oaf-botrytis-validation");
if(!p)return;
const b=document.getElementById("oaf-botrytis-validate-run");
const s=document.getElementById("oaf-botrytis-validate-status");
const table=document.getElementById("oaf-botrytis-validate-rows");
const content=document.getElementById("oaf-botrytis-validate-output");
const pct=v=>typeof v==="number"&&Number.isFinite(v)?(v*100).toLocaleString("es-PE",{maximumFractionDigits:1,minimumFractionDigits:1})+" %":"No calculable";
let started=false;
async function load(){
 b.disabled=true;content.hidden=true;s.textContent="Consultando evaluación histórica de la señal de humedad…";
 try{
  const r=await fetch("datos/botrytis_indicador_7b_backtest.json",{cache:"no-store"});
  if(!r.ok)throw Error("Los datos aún no han terminado de evaluarse (HTTP "+r.status+")");
  const j=await r.json();
  if(j.fase!=="7B"||j.es_prediccion_de_botrytis!==false||
     j.es_verificacion_humectacion_foliar!==false||
     j.son_registros_de_campo!==false||j.es_alerta!==false||
     j.primer_dia!=="2026-01-01"||j.ultimo_dia!=="2026-09-30"||!j.resultados)
    throw Error("No se verificó la fuente o la declaración científica del informe");
  const output=[];
  for(const name of ["Chiclayo","Jayanca","Motupe","Olmos"]){
   const d=j.resultados[name],cm=d?.matriz;
   if(!d||!cm||d.dias_evaluados<180)throw Error("Faltan suficientes fechas verificables para "+name);
   const keys=["verdaderos_positivos","falsos_positivos","falsos_negativos","verdaderos_negativos"];
   if(keys.some(x=>!Number.isInteger(cm[x])||cm[x]<0)||
      keys.reduce((a,x)=>a+cm[x],0)!==d.dias_evaluados||
      d.validacion_biologica!==false)throw Error("Métricas inconsistentes en "+name);
   output.push([name,String(d.dias_evaluados),
    String(d.episodios_diarios_previstos),String(d.episodios_diarios_referencia),
    String(cm.verdaderos_positivos),String(cm.falsos_positivos),
    String(cm.falsos_negativos),String(cm.verdaderos_negativos),
    pct(d.sensibilidad),pct(d.precision_positiva)]);
  }
  table.replaceChildren();
  for(const cells of output){
   const tr=document.createElement("tr");
   for(const text of cells){
    const td=document.createElement("td");td.textContent=text;tr.appendChild(td);
   }
   table.appendChild(tr);
  }
  s.textContent="Evaluación meteorológica retrospectiva con humedad a 2 m archivada 24 h antes; comparación posterior con reanálisis ERA5. No hay diagnóstico ni validación de Botrytis.";
  document.getElementById("oaf-botrytis-validate-provenance").textContent=
    "Periodo "+j.primer_dia+" a "+j.ultimo_dia+" · archivo generado "+j.fecha_procesamiento_utc+
    " · pronóstico Previous Runs y reanálisis ERA5. Una coincidencia no demuestra infección ni humectación foliar.";
  content.hidden=false;
 }catch(e){
  s.textContent="Evaluación todavía no publicable: "+e.message+". No se muestran cifras de reemplazo.";
 }finally{b.disabled=false}
}
b.addEventListener("click",load);
p.addEventListener("toggle",()=>{if(p.open&&!started){started=true;load()}});
})();