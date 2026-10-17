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
const stab=state.estabilidad_variantes.find(r=>r.localidad===s&&r.horizonte_meses===h&&r.objetivo===t&&r.modelo==='local_viento_sst');
const chart=el('oaf-8w-stability'); chart.replaceChildren();
const create=(tag,attrs,text)=>{
 const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
 for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));
 if(text!==undefined)e.textContent=String(text);
 return e;
};
if(stab){
 const vals=stab.mejora_por_corte_pct, low=Math.min(-1,...vals)*1.15,
 high=Math.max(1,...vals)*1.15, y=v=>18+(174*(high-v)/(high-low)), zero=y(0);
 chart.setAttribute('viewBox','0 0 750 240');
 chart.append(create('line',{x1:44,y1:zero,x2:734,y2:zero,stroke:'currentColor',opacity:.4}));
 const labels=['2011–13','2014–16','2017–19','2020–22','2023–25'];
 vals.forEach((v,i)=>{
   const x=78+i*135,yy=y(v);
   chart.append(create('rect',{x,y:Math.min(yy,zero),width:70,height:Math.max(1,Math.abs(yy-zero)),
     fill:v>=0?'#267b69':'#a75a53',rx:3}));
   chart.append(create('text',{x:x+35,y:(v>=0?yy-5:yy+16),'text-anchor':'middle',
     'font-size':13,fill:'currentColor'},(v>0?'+':'')+format(v,1)+' %'));
   chart.append(create('text',{x:x+35,y:215,'text-anchor':'middle','font-size':12,
     fill:'currentColor'},labels[i]));
 });
 el('oaf-8w-folds-desc').textContent=stab.cortes_mejora+' de '+stab.total_cortes+
  ' cortes con menor MAE que el modelo local. Se evalúan los mismos años por variante.';
}
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
