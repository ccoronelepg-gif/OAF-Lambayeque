/* OAF 8H · visor de fuentes instrumentales con prohibición de validar
   temperatura desde registros de precipitación. Sin datos simulados. */
(()=>{
'use strict';
const details=document.getElementById('oaf-audit-8h');
if(!details)return;
const $=id=>document.getElementById(id);
const status=$('oaf-8h-status'),table=$('oaf-8h-estaciones'),chart=$('oaf-8h-cobertura');
const summary='datos/auditoria_instrumental_8h/estado_8h.json';
const stationCSV='datos/auditoria_instrumental_8h/estaciones_8h.csv';
const fmt=n=>Number.isFinite(Number(n))?Number(n).toLocaleString('es-PE'):'—';
function cell(tr,text){const td=document.createElement('td');td.textContent=String(text);tr.appendChild(td);return td;}
function rowsFromCSV(text){
 const lines=text.trim().split(/\r?\n/),columns=lines.shift().split(',');
 // El CSV es del pipeline Python: los nombres y URLs no contienen comas.
 return lines.map(line=>{
   const fields=line.split(',');
   if(fields.length!==columns.length)throw Error('CSV con separadores inesperados');
   return Object.fromEntries(columns.map((k,i)=>[k,fields[i]]));
 });
}
let loaded=false;
async function display(){
 status.textContent='Consultando fuentes instrumentales y reportes archivados…';
 try{
  const [r,a]=await Promise.all([fetch(summary,{cache:'no-store'}),fetch(stationCSV,{cache:'no-store'})]);
  if(!r.ok||!a.ok)throw Error('Archivos 8H no disponibles en GitHub Pages');
  const d=await r.json(),list=rowsFromCSV(await a.text());
  if(d.fase!=='8H'||d.comparabilidad_directa_variables!==false||
     d.estaciones_aptas_validacion_temperatura_8e!==0||
     d.intervalos_prediccion_90_publicables!==false||
     d.aptitud_operativa!==false||list.length!==5||
     list.some(x=>x.apto_contraste_8e_temperatura!=='false'))
    throw Error('El reporte incumple los criterios conservadores de 8H');
  $('oaf-8h-station-n').textContent=fmt(d.estaciones_historicas_precipitacion);
  $('oaf-8h-month-n').textContent=fmt(d.meses_estacion_precipitacion);
  $('oaf-8h-temperature-n').textContent=fmt(d.estaciones_aptas_validacion_temperatura_8e);
  table.replaceChildren();chart.replaceChildren();
  for(const x of list){
   const tr=document.createElement('tr');
   cell(tr,x.estacion);cell(tr,fmt(x.meses_completos_precipitacion));
   cell(tr,x.primer_mes+' a '+x.ultimo_mes);
   cell(tr,x.punto_oaf_provisional_mas_cercano+' ('+x.distancia_referencial_km+' km; provisional)');
   cell(tr,'No: falta temperatura e identidad instrumental');
   table.append(tr);
   const item=document.createElement('div');item.style.cssText='display:grid;grid-template-columns:110px 1fr 45px;gap:12px;align-items:center;margin:10px 0';
   const label=document.createElement('span');label.className='small';label.textContent=x.estacion;
   const bg=document.createElement('div');bg.style.cssText='height:13px;border-radius:8px;background:#e5eff5;overflow:hidden';
   const bar=document.createElement('div');bar.style.cssText='height:100%;background:#0e8c9d;border-radius:8px;width:'+Math.min(100,Number(x.meses_completos_precipitacion)/240*100).toFixed(1)+'%';
   bg.append(bar);const num=document.createElement('strong');num.textContent=fmt(x.meses_completos_precipitacion);num.style.fontSize='12px';
   item.append(label,bg,num);chart.append(item);
  }
  status.textContent='Archivo SENAMHI histórico: precipitación mensual 1996–2015. Cero estaciones con Tmedia instrumental contrastable y metadatos completos para evaluar 8E. Las distancias son exploratorias, no emparejamientos válidos.';
 }catch(e){
   table.replaceChildren();chart.replaceChildren();
   status.textContent='La auditoría no está disponible o falló su control de procedencia: '+e.message+'. No se reemplaza con datos simulados.';
 }
}
details.addEventListener('toggle',()=>{if(details.open&&!loaded){loaded=true;display()}});
$('oaf-8h-refresh')?.addEventListener('click',display);
})();