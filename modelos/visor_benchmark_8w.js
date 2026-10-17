/* OAF 8W: visores de evaluación retrospectiva, NO pronóstico operacional. */
(()=>{
'use strict';
const panel=document.getElementById('oaf-benchmark-8w');
if(!panel)return;
const el=id=>document.getElementById(id);
const site=el('oaf-8w-site'), horizon=el('oaf-8w-h'), objective=el('oaf-8w-target');
const format=(v,k=3)=>typeof v==='number'&&Number.isFinite(v)?v.toLocaleString('es-PE',{maximumFractionDigits:k,minimumFractionDigits:k}):'—';
const names={climatologia:'Climatología',persistencia:'Persistencia',
local_ridge:'Modelo local',local_viento:'Modelo local + viento',
local_viento_sst:'Modelo local + viento + SST',con_corrientes:'Variante + corrientes',
climatologia_evento:'Climatología de eventos'};
let state=null;
const td=(tr,s)=>{
const cell=document.createElement('td');
cell.textContent=String(s);
tr.append(cell);
};
function display(){
if(!state)return;
const s=site.value,h=Number(horizon.value),t=objective.value;
const records=state.metricas_continuas.filter(r=>r.localidad===s&&r.horizonte_meses===h&&r.objetivo===t);
const base=records.find(r=>r.modelo==='local_ridge');
const table=el('oaf-8w-table');
table.replaceChildren();
for(const r of records){
 const tr=document.createElement('tr');
 td(tr,names[r.modelo]||r.modelo);td(tr,format(r.mae));td(tr,format(r.rmse));
 td(tr,base?format(100*(base.mae-r.mae)/base.mae,2)+' %':'—');
 td(tr,r.n);table.append(tr);
}
const es=state.metricas_eventos.filter(r=>r.localidad===s&&r.horizonte_meses===h);
const eventTable=el('oaf-8w-events');eventTable.replaceChildren();
const b=es.find(r=>r.modelo==='climatologia_evento');
for(const r of es){
const tr=document.createElement('tr');
td(tr,names[r.modelo]||r.modelo);td(tr,format(r.brier,5));
td(tr,b?format(100*(1-r.brier/b.brier),2)+' %':'—');
td(tr,r.eventos+' / '+r.n);eventTable.append(tr);
}
const current=state.metricas_sensibilidad_corrientes.filter(r=>r.localidad===s&&r.horizonte_meses===h&&r.objetivo===t);
const cur=el('oaf-8w-currents');cur.replaceChildren();
for(const r of current){
const tr=document.createElement('tr');
td(tr,names[r.modelo]||r.modelo);td(tr,format(r.mae));td(tr,format(r.rmse));td(tr,r.n);cur.append(tr);
}
el('oaf-8w-unit').textContent=t==='temperatura_aire_c'?'Errores en °C':'Errores en mm/mes';
el('oaf-8w-status').textContent='Evaluación retrospectiva sobre reanálisis. Las comparaciones con corrientes se hicieron únicamente en 2023–2025 y NO usan la misma historia de entrenamiento que los modelos principales.';
}
async function open(){
if(state)return display();
el('oaf-8w-status').textContent='Leyendo resultados archivados de fase 8W...';
try{
const r=await fetch('datos/benchmark_8w/estado_benchmark_8w.json',{cache:'no-store'});
if(!r.ok)throw Error('Reporte de métricas no encontrado');
const d=await r.json();
if(d.fase!=='8W'||d.prediccion_operativa_validada!==false||d.alertas_agricolas_permitidas!==false)
 throw Error('Metadatos de seguridad incompatibles');
state=d;
el('oaf-8w-forecast-count').textContent=d.n_predicciones_continuas.toLocaleString('es-PE');
el('oaf-8w-event-count').textContent=d.n_pronosticos_probabilisticos_eventos.toLocaleString('es-PE');
el('oaf-8w-current-count').textContent=d.n_predicciones_sensibilidad_corrientes.toLocaleString('es-PE');
display();
}catch(err){el('oaf-8w-status').textContent='No fue posible validar los resultados: '+err.message;}
}
panel.addEventListener('toggle',()=>{if(panel.open)open()});
[site,horizon,objective].forEach(x=>x.addEventListener('change',display));
if(panel.open)open();
})();
