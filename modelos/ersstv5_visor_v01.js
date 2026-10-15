/* OAF-Lambayeque Fase 6C: ERSSTv5 product only, never ICEN official.
   This reader handles missing/unverified data without placeholder numbers.
*/
(function(){
"use strict";
const panel=document.getElementById('oaf-ersstv5-6c');
if(!panel)return;
const btn=document.getElementById('oaf-ersstv5-load'),status=document.getElementById('oaf-ersstv5-status'),output=document.getElementById('oaf-ersstv5-output');
const val=(v,d=2)=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
let initialized=false;
async function show(){
 btn.disabled=true;output.hidden=true;status.textContent='Consultando archivo NOAA ERSSTv5 generado por el proyecto…';
 try{
  const r=await fetch('datos/modelo_ersstv5_nino12_6c.json',{cache:'no-store'});
  if(!r.ok)throw Error('Archivo de resultados aún no disponible (HTTP '+r.status+')');
  const j=await r.json();
  if(j.fase!=='6C'||j.fuente!=='NOAA CPC'||!String(j.producto).startsWith('ERSSTv5')||
     j.es_icen_oficial!==false||j.es_alerta!==false||j.es_pronostico_institucional!==false||
     !j.modelos_horizontes||!j.promedio_3m_indicativo||!Number.isFinite(j.ultima_anomalia_ersstv5_c)||
     !/^\d{4}-\d{2}$/.test(j.mes_ultimo_observado))
     throw Error('Formato o procedencia del producto no verificados');
  const [year,mon]=j.mes_ultimo_observado.split('-').map(Number);
  const now=new Date(),age=(now.getUTCFullYear()-year)*12+now.getUTCMonth()+1-mon;
  if(age<1||age>3)throw Error('La referencia mensual está desactualizada o pertenece a un mes futuro');
  const three=j.promedio_3m_indicativo;
  if(three.es_icen_oficial!==false||!Number.isFinite(three.promedio_trimestral_ersstv5_c))
     throw Error('Promedio indicativo inválido');
  document.getElementById('oaf-ersstv5-latest').textContent=val(j.ultima_anomalia_ersstv5_c)+' °C';
  document.getElementById('oaf-ersstv5-date').textContent=j.mes_ultimo_observado;
  document.getElementById('oaf-ersstv5-mean3').textContent=val(three.promedio_trimestral_ersstv5_c)+' °C';
  document.getElementById('oaf-ersstv5-mean-date').textContent=three.mes_central;
  const table=document.getElementById('oaf-ersstv5-results');
  table.replaceChildren();
  for(const k of ['1','2','3']){
    const h=j.modelos_horizontes[k];
    if(!h||!Number.isFinite(h.pronostico_ar1_c)||!Number.isFinite(h.pronostico_persistencia_c)
       ||!Number.isFinite(h.metricas?.ar1?.mae_c)||!Number.isFinite(h.metricas?.persistencia?.mae_c)
       ||!Number.isFinite(h.metricas_ultimos_12?.ar1?.mae_c)
       ||!Number.isFinite(h.metricas_ultimos_12?.persistencia?.mae_c)
       ||!/^\d{4}-\d{2}$/.test(h.mes_objetivo))
      throw Error('Un horizonte carece de verificación o datos válidos');
    const tr=document.createElement('tr');
    const cells=[k+' mes'+(k==='1'?'':'es')+' · '+h.mes_objetivo,
      val(h.pronostico_ar1_c)+' °C',val(h.pronostico_persistencia_c)+' °C',
      val(h.metricas.ar1.mae_c,3)+' / '+val(h.metricas.persistencia.mae_c,3)+' °C',
      val(h.metricas_ultimos_12.ar1.mae_c,3)+' / '+val(h.metricas_ultimos_12.persistencia.mae_c,3)+' °C',
      h.mejora_consistente_demostrada===true?'Sí (solo retrospectivo)':'No demostrada'];
    for(const cell of cells){const td=document.createElement('td');td.textContent=cell;tr.appendChild(td)}
    table.appendChild(tr);
  }
  const cmp=j.comparacion_oisst;
  document.getElementById('oaf-ersstv5-compare').textContent=cmp?.estado==='comparacion_exploratoria_no_validacion'?
   'Diferencia ERSSTv5–OISST en el último mes común '+cmp.ultimo_mes_comun+': '+val(cmp.diferencia_ultimo_mes_c)+' °C. Diferencia media absoluta entre productos: '+val(cmp.mae_entre_productos_c)+' °C ('+cmp.meses_comunes+' meses). No es error de pronóstico.' :
   'Comparación OISST–ERSSTv5 todavía no disponible o no válida.';
  status.textContent='Datos NOAA procesados, origen '+j.mes_ultimo_observado+'. Archivo generado: '+j.fecha_procesamiento_utc+'.';
  output.hidden=false;
 }catch(err){
   status.textContent='Sin resultado ERSSTv5 publicable: '+err.message+'. El módulo no sustituye datos ausentes ni muestra una clasificación ENFEN inventada.';
 }finally{btn.disabled=false}
}
btn.addEventListener('click',show);
function route(){if(location.hash==='#nino'&&!initialized){initialized=true;show()}}
addEventListener('hashchange',route);route();
})();