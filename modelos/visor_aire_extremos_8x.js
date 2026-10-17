/* OAF 8X: concentración de particulas CAMS (modelo, no sensor ni ECA).
   Diagnóstico de errores y años extremos; jamás emitir alertas. */
(()=>{
'use strict';
const pane=document.getElementById('oaf-aire-extremos-8x');
if(!pane)return;
const el=id=>document.getElementById(id);
const status=el('oaf-8x-status');
const site=el('oaf-8x-site');
const pollutant=el('oaf-8x-pollutant');
const graph=el('oaf-8x-air-graph');
const table=el('oaf-8x-extreme-table');
let records=[], extreme=[];
const months=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const num=(v,k=2)=>v===null||v===undefined||v===''?'—':Number(v).toLocaleString('es-PE',{maximumFractionDigits:k,minimumFractionDigits:k});
function parseCSV(text){
 const lines=text.trim().split(/\r?\n/);
 const head=lines.shift().split(',');
 return lines.map(line=>{
   const fields=[];let quoted=false, buf='';
   for(let i=0;i<line.length;i++){
     const c=line[i];
     if(c==='"'){if(quoted&&line[i+1]==='"'){buf+='"';i++;}else quoted=!quoted;}
     else if(c===','&&!quoted){fields.push(buf);buf='';}
     else buf+=c;
   }
   fields.push(buf);
   return Object.fromEntries(head.map((k,i)=>[k,fields[i]||'']));
 });
}
function node(tag,attrs,txt){
 const v=document.createElementNS('http://www.w3.org/2000/svg',tag);
 Object.entries(attrs).forEach(([k,val])=>v.setAttribute(k,String(val)));
 if(txt!==undefined)v.textContent=String(txt);
 return v;
}
function render(){
 const rows=records.filter(r=>r.localidad===site.value&&r.mes.startsWith('2025')&&r.mes_pm_completo_80pct==='True')
  .sort((a,b)=>a.mes.localeCompare(b.mes));
 const key=pollutant.value;
 graph.replaceChildren();
 if(rows.length<1){
  graph.append(node('text',{x:20,y:90,fill:'currentColor','font-size':16},'Sin datos PM verificados para esta ubicación y periodo.'));
 }else{
  const mx=Math.max(1,...rows.map(x=>Number(x[key])));
  graph.append(node('line',{x1:45,x2:739,y1:190,y2:190,stroke:'currentColor',opacity:0.25}));
  rows.forEach(r=>{
   const m=Number(r.mes.slice(5))-1,v=Number(r[key]); if(!Number.isFinite(v))return;
   const height=145*v/mx;
   graph.append(node('rect',{x:58+m*56,y:190-height,width:35,height,rx:4,fill:key.startsWith('pm25')?'#27889a':'#ac824d'}));
   graph.append(node('text',{x:75+m*56,y:207,'text-anchor':'middle',fill:'currentColor','font-size':11},months[m]));
   graph.append(node('text',{x:75+m*56,y:185-height,'text-anchor':'middle',fill:'currentColor','font-size':10},num(v,1)));
  });
 }
 const subset=extreme.filter(r=>r.localidad===site.value&&r.objetivo===el('oaf-8x-extreme-variable').value
  &&r.horizonte_meses===el('oaf-8x-h').value&&r.estacion==='enero_abril');
 const tb=document.createDocumentFragment();
 for(const r of subset){
  if(!['local_ridge','local_viento_sst'].includes(r.modelo))continue;
  const tr=document.createElement('tr');
  for(const x of [r.anio_prueba,r.modelo==='local_ridge'?'Local':'Local + viento + TSM',num(r.mae,2),num(r.error_absoluto_max,2),r.meses_prueba]){
   const td=document.createElement('td');td.textContent=String(x);tr.append(td);
  }
  tb.append(tr);
 }
 table.replaceChildren(tb);
 el('oaf-8x-unit').textContent=key.startsWith('pm25')?'Concentración PM₂.₅ estimada (µg/m³)':'Concentración PM₁₀ estimada (µg/m³)';
}
async function load(){
 if(records.length)return render();
 status.textContent='Comprobando archivos de fuente y cobertura...';
 try{
 const [s0,s1,s2,s3]=await Promise.all([
  fetch('datos/aire_8x/estado_aire_8x.json',{cache:'no-store'}),
  fetch('datos/aire_8x/particulas_mensuales_8x.csv',{cache:'no-store'}),
  fetch('datos/extremos_8x/estado_extremos_8x.json',{cache:'no-store'}),
  fetch('datos/extremos_8x/error_extremos_2017_2023_8x.csv',{cache:'no-store'})]);
 if(!s0.ok)throw Error('No está publicado el estado de calidad del aire');
 const meta=await s0.json();
 if(meta.fase!=='8X'||meta.serie_pm_1996_2025_completa!==false
   ||meta.comparacion_legal_ECA_habilitada!==false)throw Error('Metadatos PM incompatibles');
 if(!s1.ok)throw Error('Aún no hay CSV PM verificable');
 records=parseCSV(await s1.text());
 if(records.length!==meta.filas_mes_sitio)throw Error('Contabilidad PM inconsistente');
 el('oaf-8x-air-count').textContent=String(meta.meses_pm_80pct_aptos);
 el('oaf-8x-site-count').textContent=String(new Set(records.map(x=>x.localidad)).size);
 if(s2.ok&&s3.ok){
  const extmeta=await s2.json();
  if(extmeta.fase==='8X'&&extmeta.prediccion_operativa===false){
    extreme=parseCSV(await s3.text());
    el('oaf-8x-extreme-count').textContent=String(extmeta.n_grupos_mae_estacional);
  }
 }
 status.textContent='PM₂.₅ y PM₁₀: producto CAMS Global modelado, NO estación SENAMHI. Sin evaluación normativa ECA ni alerta agrícola.';
 render();
 }catch(err){status.textContent=err.message;}
}
pane.addEventListener('toggle',()=>{if(pane.open)load()});
[site,pollutant,el('oaf-8x-h'),el('oaf-8x-extreme-variable')].forEach(x=>x.addEventListener('change',render));
if(pane.open)load();
})();
