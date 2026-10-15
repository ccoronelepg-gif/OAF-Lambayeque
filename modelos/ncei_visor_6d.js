/* OAF-Lambayeque Fase 6D: NCEI ERSSTv5 rebasado 1991–2020.
 * Datos experimentales versionados, no ICEN ni pronósticos validados.
 */
(function(){
"use strict";
const panel=document.getElementById('oaf-ncei-6d');
if(!panel)return;
const status=document.getElementById('oaf-ncei-status');
const output=document.getElementById('oaf-ncei-output');
const btn=document.getElementById('oaf-ncei-load');
const num=(x,d=2)=>Number.isFinite(x)?x.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
let first=false;
async function refresh(){
 btn.disabled=true;
 output.hidden=true;
 status.textContent='Leyendo la serie NOAA NCEI procesada y sus controles de calidad…';
 try{
   const res=await fetch('datos/modelo_ersstv5_ncei_6d.json',{cache:'no-store'});
   if(!res.ok)throw Error('Resultado aún no publicado: HTTP '+res.status);
   const data=await res.json();
   const valid=data.fase==='6D'&&data.fuente==='NOAA NCEI'
     &&data.es_icen_oficial===false&&data.es_alerta===false
     &&data.serie_oaf_ajustada_base==='1991-2020'
     &&data.serie_noaa_orig_anom_base==='1971-2000'
     &&data.valores_rebasados_no_indice_oficial===true
     &&data.contraste_cpc_ersstv5&&data.modelos_horizontes
     &&Number.isFinite(data.ultima_anomalia_ersstv5_c)
     &&/^\d{4}-(0[1-9]|1[0-2])$/.test(data.mes_ultimo_observado);
   if(!valid)throw Error('Procedencia o campos de datos incorrectos');
   if(data.contraste_cpc_ersstv5.calidad_suficiente!==true)
     throw Error('No se superó el contraste de consistencia con la serie CPC');
   const [y,m]=data.mes_ultimo_observado.split('-').map(Number);
   const now=new Date();
   const age=(now.getUTCFullYear()-y)*12+now.getUTCMonth()+1-m;
   if(age<1)throw Error('El último mes no está cerrado');
   const current=age<=3&&data.prediccion_actual_disponible===true;
   document.getElementById('oaf-ncei-date').textContent=data.mes_ultimo_observado;
   document.getElementById('oaf-ncei-value').textContent=num(data.ultima_anomalia_ersstv5_c,3)+' °C';
   document.getElementById('oaf-ncei-difference').textContent=num(data.contraste_cpc_ersstv5.media_abs_diferencias_ultimos24_c,3)+' °C';
   document.getElementById('oaf-ncei-difference-date').textContent=data.contraste_cpc_ersstv5.ultima_fecha_comun;
   const tbody=document.getElementById('oaf-ncei-horizons');
   tbody.replaceChildren();
   for(const key of ['1','2','3']){
     const row=data.modelos_horizontes[key];
     if(!row||!Number.isFinite(row.metricas?.ar1?.mae_c)
       ||!Number.isFinite(row.metricas?.persistencia?.mae_c)
       ||!Number.isFinite(row.metricas_ultimos_12?.ar1?.mae_c)
       ||!Number.isFinite(row.metricas_ultimos_12?.persistencia?.mae_c))
       throw Error('Métricas históricas incompletas');
     if(current&&(!Number.isFinite(row.pronostico_ar1_c)||!/^\d{4}-\d{2}$/.test(row.mes_objetivo)))
       throw Error('Estimación mensual ausente o inválida');
     const cells=[
       current?row.mes_objetivo:key+' mes'+(key==='1'?'':'es'),
       current?num(row.pronostico_ar1_c,3)+' °C':'No disponible',
       num(row.metricas.ar1.mae_c,3)+' / '+num(row.metricas.persistencia.mae_c,3)+' °C',
       num(row.metricas_ultimos_12.ar1.mae_c,3)+' / '+num(row.metricas_ultimos_12.persistencia.mae_c,3)+' °C',
       'Sin validación prospectiva'
     ];
     const tr=document.createElement('tr');
     for(const cell of cells){const td=document.createElement('td');td.textContent=cell;tr.appendChild(td)}
     tbody.appendChild(tr);
   }
   status.textContent=current
     ?'Fuente cerrada hasta '+data.mes_ultimo_observado+'. Estimaciones experimentales no validadas; muestran peor desempeño que persistencia en los 12 meses recientes.'
     :'El producto NOAA está desactualizado; se muestran únicamente verificaciones históricas, sin pronóstico actual.';
   document.getElementById('oaf-ncei-method').textContent=
     'Fuente: NOAA NCEI ERSSTv5; climatología original 1971–2000, transformada por OAF a 1991–2020. '
     +'Último mes comparable con CPC: '+data.contraste_cpc_ersstv5.ultima_fecha_comun
     +'. Versión generada: '+data.fecha_procesamiento_utc+'. No es ICEN oficial ni predicción validada de El Niño Costero.';
   output.hidden=false;
 }catch(err){
   status.textContent='Datos no publicables: '+err.message+'. No se reemplazan por valores inventados.';
 }finally{btn.disabled=false}
}
btn.addEventListener('click',refresh);
panel.addEventListener('toggle',()=>{if(panel.open&&!first){first=true;refresh()}});
})();
