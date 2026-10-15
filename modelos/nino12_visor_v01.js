/* OAF 6B: view verified, timestamped NOAA data outputs only.
   NO NOAA remote fetch from visitors. NO ICEN categories or "alertas" invented.
*/
(function(){
'use strict';
const panel=document.getElementById('oaf-nino-pred-data');
if(!panel)return;
const status=document.getElementById('oaf-nino-pred-status');
const output=document.getElementById('oaf-nino-pred-results');
const refresh=document.getElementById('oaf-nino-pred-refresh');
const url='datos/modelo_nino12_experimental.json';
const fmt=(n,d=2)=>Number.isFinite(n)?n.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
let loaded=false;
async function show(){
  refresh.disabled=true;
  output.hidden=true;
  status.textContent='Buscando el último archivo oceánico procesado y verificado…';
  try{
    const resp=await fetch(url,{cache:'no-store'});
    if(!resp.ok)throw Error('El resultado verificado todavía no está disponible (HTTP '+resp.status+').');
    const j=await resp.json();
    if(j.es_icen!==false||j.es_pronostico_institucional!==false||j.producto!=='OISST v2.1 mensual Niño 1+2 (sstoi.indices)'
      ||typeof j.ultimo_valor_anomalia_c!=='number'||typeof j.pronostico_ar1_c!=='number'
      ||!j.evaluacion||!Array.isArray(j.series_recientes)||!j.mes_ultimo_observado||!j.mes_predicho)throw Error('No supera comprobación del formato y procedencia de datos');
    const [yr,mon]=j.mes_ultimo_observado.split('-').map(Number);
    const utc=new Date(),age=(utc.getUTCFullYear()-yr)*12+utc.getUTCMonth()+1-mon;
    if(age>3 || age<0)throw Error('La serie oceánica está desactualizada o tiene una fecha futura');
    document.getElementById('oaf-n12-latest').textContent=fmt(j.ultimo_valor_anomalia_c)+' °C';
    document.getElementById('oaf-n12-latest-month').textContent=j.mes_ultimo_observado;
    document.getElementById('oaf-n12-forecast').textContent=fmt(j.pronostico_ar1_c)+' °C';
    document.getElementById('oaf-n12-forecast-month').textContent=j.mes_predicho;
    document.getElementById('oaf-n12-persistence').textContent=fmt(j.pronostico_persistencia_c)+' °C';
    const metric=j.evaluacion.metricas;
    const ar=metric?.ar1?.mae_c,ps=metric?.persistencia?.mae_c;
    if(!Number.isFinite(ar)||!Number.isFinite(ps))throw Error('Verificación estadística incompleta');
    document.getElementById('oaf-n12-error').textContent='MAE modelo: '+fmt(ar)+' °C · persistencia: '+fmt(ps)+' °C. '+j.evaluacion.num_folds+' pronósticos retrospectivos.';
    const recent=j.evaluacion.reciente_12_meses;
    const ci=j.evaluacion.intervalo_heuristico_skill_95;
    const strong=j.evaluacion.habilidad_consistente_demostrada===true;
    let review='';
    if(recent&&Number.isFinite(recent.mae_ar1_c)&&Number.isFinite(recent.mae_persistencia_c)){
       review+='Últimos 12 meses: error medio AR(1) '+fmt(recent.mae_ar1_c,4)+' °C frente a '+fmt(recent.mae_persistencia_c,4)+' °C de persistencia. ';
    }
    if(Array.isArray(ci)&&ci.length===2&&ci.every(Number.isFinite)){
       review+='Intervalo exploratorio de mejora relativa por remuestreo: '+fmt(ci[0]*100,1)+' % a '+fmt(ci[1]*100,1)+' %. ';
    }
    document.getElementById('oaf-n12-eval').textContent=(strong?
       'Las pruebas retrospectivas superaron las referencias seleccionadas; NO existe validación prospectiva ni operativa. ' :
       'El modelo NO ha demostrado una mejora consistente frente a persistencia. La cifra publicada es un ensayo, NO una alerta ni un pronóstico validado. ')+review;
    const rows=document.getElementById('oaf-n12-recent');
    rows.replaceChildren();
    for(const record of j.series_recientes.slice(-6)){
      if(!/^\d{4}-\d{2}$/.test(record.mes)||!Number.isFinite(record.nino12_anom_c))continue;
      const tr=document.createElement('tr');
      [record.mes,fmt(record.nino12_anom_c)+' °C'].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td)});
      rows.appendChild(tr);
    }
    document.getElementById('oaf-n12-issued').textContent='Procesado: '+j.fecha_procesamiento_utc+
      ' · NOAA CPC OISST v2.1 (no ICEN). Anomalías mensuales SST Niño 1+2. Evaluación walk-forward retrospectiva, no archivo de pronósticos emitidos en tiempo real.';
    status.textContent='Se encontraron resultados del modelo experimental, con procedencia y métricas visibles.';
    output.hidden=false;
  }catch(e){
    status.textContent='Sin predicción oceánica publicable: '+e.message+' Los datos no se sustituyen por estimaciones ficticias. Consulta ENFEN para el estado oficial.';
  }finally{refresh.disabled=false}
}
refresh.addEventListener('click',show);
function maybeLoad(){
 if((location.hash==='#nino')&&!loaded){loaded=true;show()}
}
addEventListener('hashchange',maybeLoad);
maybeLoad();
})();
