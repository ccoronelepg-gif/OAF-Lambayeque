/* Fase 6F — visualizar exclusivamente resultados históricos comprobados */
(function(){
'use strict';
const panel=document.getElementById('oaf-benchmark-6f');
if(!panel)return;
const btn=document.getElementById('oaf-benchmark-run');
const status=document.getElementById('oaf-benchmark-status');
const output=document.getElementById('oaf-benchmark-output');
const fmt=(n,p=3)=>Number.isFinite(n)?n.toLocaleString('es-PE',{minimumFractionDigits:p,maximumFractionDigits:p}):'—';
let loaded=false;
async function load(){
 btn.disabled=true;output.hidden=true;status.textContent='Leyendo evaluación histórica con datos auditables…';
 try{
   const r=await fetch('datos/benchmark_variables_6f.json',{cache:'no-store'});
   if(!r.ok)throw Error('Archivo de resultados pendiente (HTTP '+r.status+')');
   const j=await r.json();
   if(j.fase!=='6F'||j.estado!=='experimental_retrospectivo'||
      j.evaluacion_separada!=='2026-01-01 a 2026-09-30'||
      j.predictores_emitidos_antes_de_validez!==true||!j.sin_optimizacion_en_holdout||!j.resultados)
      throw Error('Formato, temporalidad o procedencia no válidos');
   const body=document.getElementById('oaf-benchmark-results');
   body.replaceChildren();
   for(const city of ['Chiclayo','Jayanca','Motupe','Olmos']){
     const result=j.resultados[city],scores=result?.metricas;
     if(!result||result.validacion_operativa!==false||
        !scores||!Number.isFinite(scores.raw?.mae_c)||
        !Number.isFinite(scores.corrected_base?.mae_c)||
        !Number.isFinite(scores.corrected_plus?.mae_c)||
        scores.corrected_plus.n<3000||
        !Array.isArray(result.intervalo_exploratorio_95))
        throw Error('Evaluación faltante o insuficiente de '+city);
     const label=result.mejora_retrospectiva_consistente===true?'Señal histórica favorable':'No demuestra mejora consistente';
     const cells=[city,String(scores.corrected_plus.n),fmt(scores.raw.mae_c),
                  fmt(scores.corrected_base.mae_c),fmt(scores.corrected_plus.mae_c),
                  fmt(result.mejora_relativa_vs_basico*100,1)+' %',
                  label];
     const row=document.createElement('tr');
     cells.forEach(v=>{const td=document.createElement('td');td.textContent=v;row.appendChild(td)});
     body.appendChild(row);
   }
   document.getElementById('oaf-benchmark-method').textContent=
     'Variables: radiación, humedad y viento predichos 24 horas antes. '+
     'Referencia: temperatura reanalizada ERA5-Land (NO estación SENAMHI). '+
     'Entrenamiento: '+j.entrenamiento+'. Evaluación separada: '+j.evaluacion_separada+
     '. Archivo generado: '+j.fecha_utc+
     '. Los resultados no validan la predicción de El Niño Costero ni de enfermedades agrícolas.';
   status.textContent='Evaluación retrospectiva completada. Comparar MAE más bajo es mejor; no atribuir causalidad a variables individuales.';
   output.hidden=false;
 }catch(e){
   status.textContent='Sin resultados publicables: '+e.message+'. No se muestran pruebas sintéticas ni porcentajes inventados.';
 }finally{btn.disabled=false}
}
btn.addEventListener('click',load);
panel.addEventListener('toggle',()=>{if(panel.open&&!loaded){loaded=true;load()}});
})();