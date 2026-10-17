/* OAF 9A: comparación científica pareada 8W+RH/VPD.
Datos históricos revisados, NO pronósticos emitidos ni alertas agrícolas.
*/
(()=>{
'use strict';
const panel=document.getElementById('oaf-benchmark-9a');
if(!panel)return;
const e=id=>document.getElementById(id);
const loc=e('oaf-9a-site'),h=e('oaf-9a-h'),target=e('oaf-9a-target');
const body=e('oaf-9a-models'),season=e('oaf-9a-seasons'),events=e('oaf-9a-events');
const chart=e('oaf-9a-stability'),summary=e('oaf-9a-summary');
const modelNames={base_viento_sst:'Modelo 8W: local + viento + SST',
base_mas_rh:'8W + humedad relativa',
base_mas_vpd:'8W + VPD',
base_mas_rh_vpd:'8W + humedad + VPD'};
const label=v=>v==='temperatura_aire_c'?'Temperatura media':'Precipitación mensual';
let data=null;
const fmt=(v,k=3)=>typeof v==='number'&&Number.isFinite(v)
 ?v.toLocaleString('es-PE',{minimumFractionDigits:k,maximumFractionDigits:k}):'—';
const cell=(tr,val)=>{const td=document.createElement('td');td.textContent=String(val);tr.append(td);};
function svgNode(tag,attr,text){
 const node=document.createElementNS('http://www.w3.org/2000/svg',tag);
 for(const [k,v] of Object.entries(attr))node.setAttribute(k,String(v));
 if(text!==undefined)node.textContent=String(text);
 return node;
}
function redraw(){
if(!data)return;
const s=loc.value,hor=Number(h.value),obj=target.value;
const r=data.metricas_continuas.filter(x=>x.localidad===s&&x.horizonte_meses===hor&&x.objetivo===obj);
const base=r.find(x=>x.modelo==='base_viento_sst');
body.replaceChildren();
for(const a of r){
 const tr=document.createElement('tr');
 const change=base&&base.mae?100*(base.mae-a.mae)/base.mae:null;
 cell(tr,modelNames[a.modelo]||a.modelo);
 cell(tr,fmt(a.mae));cell(tr,fmt(a.rmse));
 cell(tr,a.modelo==='base_viento_sst'?'Referencia':(change>0?'+':'')+fmt(change,2)+' %');
 cell(tr,a.n);body.append(tr);
}
e('oaf-9a-units').textContent='Error MAE y RMSE de '+label(obj)
 +(obj==='temperatura_aire_c'?' (°C)':' (mm/mes)')+'. Menor error es mejor.';
const gg=data.estabilidad_cortes.filter(x=>x.localidad===s&&x.horizonte_meses===hor&&x.objetivo===obj);
chart.replaceChildren();
if(gg.length){
 const cols=['2011–13','2014–16','2017–19','2020–22','2023–25'];
 const vals=gg.flatMap(x=>x.mejora_pct_por_corte),lo=Math.min(-1,...vals)*1.2,
       hi=Math.max(1,...vals)*1.2,Y=v=>35+(205*(hi-v)/(hi-lo));
 const zero=Y(0);
 chart.append(svgNode('line',{x1:62,y1:zero,x2:740,y2:zero,stroke:'currentColor',opacity:.5}));
 gg.forEach((g,j)=>{
  g.mejora_pct_por_corte.forEach((v,i)=>{
   const x=74+i*133+j*29,y=Y(v);
   chart.append(svgNode('rect',{x,y:Math.min(y,zero),width:23,height:Math.max(1,Math.abs(y-zero)),
    rx:2,fill:['#3c8395','#b39455','#7288a9'][j]}));
  });
 });
 cols.forEach((text,i)=>chart.append(svgNode('text',{x:105+i*133,y:280,'text-anchor':'middle',
     fill:'currentColor','font-size':12},text)));
 const ley=e('oaf-9a-fold-caption');
 ley.textContent=gg.map(g=>modelNames[g.modelo].replace('8W + ','')+': '+
      g.cortes_con_mejora+'/5 cortes con menor MAE').join(' · ')+
  '. Cambio porcentual positivo = mejora respecto al modelo 8W.';
}
const rs=data.auditoria_2017_2023_enero_abril.filter(x=>
  x.localidad===s&&x.horizonte_meses===hor&&x.objetivo===obj &&
  ['base_viento_sst','base_mas_rh_vpd'].includes(x.modelo));
season.replaceChildren();
for(const r of rs){
 const tr=document.createElement('tr');
 for(const v of [r.anio,modelNames[r.modelo],fmt(r.mae,2),fmt(r.rmse,2),r.n])cell(tr,v);
 season.append(tr);
}
events.replaceChildren();
for(const r of data.metricas_eventos.filter(x=>x.localidad===s&&x.horizonte_meses===hor)){
 const tr=document.createElement('tr');
 for(const v of [modelNames[r.modelo],fmt(r.brier,5),r.eventos+' / '+r.n])cell(tr,v);
 events.append(tr);
}
const candidate=data.metrica_mae.find(x=>x.localidad===s&&x.horizonte_meses===hor
    &&x.objetivo===obj&&x.modelo==='base_mas_rh_vpd');
summary.textContent='Ensayo retrospectivo '+s+' · horizonte '+hor+' mes(es). '+
 (candidate?'Agregar RH + VPD '+(candidate.mejoria_pct>=0?'redujo':'aumentó')+
 ' el MAE frente a 8W en '+fmt(Math.abs(candidate.mejoria_pct),2)+' %. ':'')+
 'Esta diferencia no valida una predicción operativa ni demuestra causalidad.';
}
async function load(){
 if(data)return redraw();
 e('oaf-9a-status').textContent='Consultando benchmark 9A con SHA y trazabilidad...';
 try{
 const res=await fetch('datos/benchmark_9a/estado_benchmark_9a.json',{cache:'no-store'});
 if(!res.ok)throw Error('Aún no está publicado el benchmark 9A');
 const r=await res.json();
 if(r.fase!=='9A'||r.validacion_prospectiva!==false||r.alertas_agricolas_aprobadas!==false)
   throw Error('Metadatos científicos incompatibles');
 data=r;
 e('oaf-9a-num-cont').textContent=r.n_predicciones_continuas.toLocaleString('es-PE');
 e('oaf-9a-num-prob').textContent=r.n_eventos_probabilisticos.toLocaleString('es-PE');
 e('oaf-9a-num-fold').textContent=String(r.fechas_ensayo.length);
 e('oaf-9a-status').textContent='Hindcast ERA5/NOAA retrospectivo, no emitido históricamente. Sin comparación instrumental SENAMHI ni alertas fitosanitarias.';
 redraw();
 }catch(err){e('oaf-9a-status').textContent='Benchmark 9A sin validar: '+err.message;}
}
panel.addEventListener('toggle',()=>{if(panel.open)load()});
[loc,h,target].forEach(x=>x.addEventListener('change',redraw));
if(panel.open)load();
})();
