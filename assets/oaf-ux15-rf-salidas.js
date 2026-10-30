/* UX16 — Dos gráficas compartidas (semanal y mensual) y un bloque sin gráfica de escenarios RF. */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const E=(tag,cls,txt)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=String(txt);return e};
const places=["Chiclayo","Jayanca","Motupe","Olmos"];
const fmt=(v,p=1)=>Number(v).toLocaleString("es-PE",{minimumFractionDigits:p,maximumFractionDigits:p});
let initialized=false,rf=null,external=null,monthlyReady=false,monthlyHistory=null;
const geo={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const era5WeekCache=new Map();let weekVersion=0;
const NS="http://www.w3.org/2000/svg";
function plot(root,axis,series,unit){
 if(!root)return;
 const all=series.flatMap(s=>s.values.filter(Number.isFinite));
 if(!all.length){root.textContent="No hay datos numéricos comprobados para este periodo.";return}
 const W=790,H=300,L=57,R=22,T=22,B=56;
 const rain=unit.startsWith("mm"),rawLow=rain?0:Math.min(...all)-.5;
 const rawHigh=Math.max(...all,rain?.05:Math.min(...all)+.5);
 const stepRaw=Math.max(.01,(rawHigh-rawLow)/4),mag=10**Math.floor(Math.log10(stepRaw)),part=stepRaw/mag;
 const tickStep=(part<=1?1:part<=2?2:part<=2.5?2.5:part<=5?5:10)*mag;
 const low=rain?0:Math.floor(rawLow/tickStep)*tickStep;
 const top=Math.max(low+4*tickStep,Math.ceil(rawHigh/tickStep)*tickStep);
 const tickCount=Math.round((top-low)/tickStep);
 const tickText=v=>Number(v.toFixed(tickStep<.01?3:tickStep<1?2:tickStep<2?1:0)).toLocaleString("es-PE",{maximumFractionDigits:tickStep<.01?3:tickStep<1?2:tickStep<2?1:0});
 const x=i=>L+(i+.5)*(W-L-R)/axis.length,y=v=>T+(top-v)/(top-low)*(H-T-B);
 const tag=(name,attrs,txt)=>{const a=document.createElementNS(NS,name);for(const [k,v] of Object.entries(attrs||{}))a.setAttribute(k,String(v));if(txt!==undefined)a.textContent=txt;return a};
 const svg=tag("svg",{viewBox:"0 0 790 300",role:"img","aria-label":unit+" · "+series.map(s=>s.name).join(" frente a ")});
 for(let k=0;k<=tickCount;k++){const v=low+tickStep*k,Y=y(v);svg.append(tag("line",{x1:L,x2:W-R,y1:Y,y2:Y,stroke:"#dae7df","stroke-width":1}),tag("text",{x:L-8,y:Y+4,"text-anchor":"end",fill:"#536d62","font-size":12},tickText(v)))}
 for(const s of series){
  let segment=[];const segments=[];
  s.values.forEach((v,i)=>{if(Number.isFinite(v))segment.push([x(i),y(v)]);else if(segment.length){segments.push(segment);segment=[]}});
  if(segment.length)segments.push(segment);
  for(const seg of segments){if(seg.length>=2)svg.append(tag("polyline",{points:seg.map(([a,b])=>a+","+b).join(" "),stroke:s.color,"stroke-width":3.7,fill:"none","stroke-linecap":"round","stroke-linejoin":"round","stroke-dasharray":s.dash||""}));}
  s.values.forEach((v,i)=>{if(!Number.isFinite(v))return;const point=tag("circle",{cx:x(i),cy:y(v),r:4.8,fill:s.color,stroke:"#fff","stroke-width":1.8,tabindex:0,role:"img","aria-label":axis[i]+" "+s.name+": "+fmt(v)+" "+unit});
   point.append(tag("title",{},axis[i]+" · "+s.name+": "+fmt(v)+" "+unit));svg.append(point)});
 }
 const step=Math.max(1,Math.ceil(axis.length/9));
 axis.forEach((label,i)=>{if(i%step===0||i===axis.length-1)svg.append(tag("text",{x:x(i),y:H-17,"text-anchor":"middle",fill:"#617c6e","font-size":11},String(label).slice(0,10)))});
 root.replaceChildren(svg);
}
/* UX43 · Barras agrupadas: pronóstico y promedio histórico nunca se confunden.
 * Campos RF sólo en fechas emitidas. Los ceros tienen altura cero.
 */
function weeklyBars(root,dates,series,unit){
 if(!root||dates.length!==7)return;
 const numeric=series.flatMap(a=>a.values.filter(Number.isFinite));
 if(!numeric.length){root.textContent="Sin datos numéricos verificados.";return}
 const rain=unit.startsWith("mm"),W=840,H=315,L=62,R=20,T=23,B=66;
 const minVal=rain?0:Math.min(...numeric),maxVal=Math.max(...numeric);
 const span=Math.max(.01,maxVal-minVal);
 const tentative=(span+(rain?0:1))/5,base=10**Math.floor(Math.log10(Math.max(.01,tentative)));
 const ratio=tentative/base,step=(ratio<=1?1:ratio<=2?2:ratio<=2.5?2.5:ratio<=5?5:10)*base;
 const bottom=rain?0:Math.floor((minVal-.4)/step)*step;
 const top=Math.max(bottom+5*step,Math.ceil((maxVal+.1)/step)*step);
 const n=Math.round((top-bottom)/step),innerW=W-L-R,band=innerW/7,barWidth=Math.min(19,band/(series.length+1.25));
 const slots=series.length,scale=v=>T+(top-v)/(top-bottom)*(H-T-B),baseline=scale(bottom);
 const NS="http://www.w3.org/2000/svg";
 const tag=(name,attrs={},str)=>{const a=document.createElementNS(NS,name);
  for(const [k,v]of Object.entries(attrs))a.setAttribute(k,String(v));
  if(str!==undefined)a.textContent=str;return a};
 const tickText=v=>Number(v.toFixed(step<.01?3:step<1?2:step<2?1:0)).toLocaleString("es-PE",{maximumFractionDigits:step<.01?3:step<1?2:step<2?1:0});
 const svg=tag("svg",{viewBox:"0 0 840 315",role:"img","aria-label":"Barras comparativas de "+unit+" para siete días"});
 svg.append(tag("title",{},"Pronóstico diario y referencia histórica para siete días"));
 for(let k=0;k<=n;k++){
  const v=bottom+step*k,y=scale(v);
  svg.append(tag("line",{x1:L,x2:W-R,y1:y,y2:y,stroke:"#dbe7df","stroke-width":"1"}));
  svg.append(tag("text",{x:L-9,y:y+4,"text-anchor":"end",fill:"#45695b","font-size":"12"},tickText(v)));
 }
 for(let i=0;i<7;i++){
  const xc=L+(i+.5)*band;
  svg.append(tag("text",{x:xc,y:H-30,"text-anchor":"middle","font-size":"12",fill:"#375d4c"},dates[i].slice(8,10)+"/"+dates[i].slice(5,7)));
  for(let j=0;j<slots;j++){
   const item=series[j],value=item.values[i];
   if(!Number.isFinite(value))continue;
   const xx=xc-(slots*barWidth)/2+j*barWidth;
   const yy=scale(value),height=Math.max(0,baseline-yy);
   const rect=tag("rect",{x:xx,y:Math.min(baseline,yy),width:Math.max(3,barWidth-3),height:height,fill:item.color,rx:2,
      tabindex:0,role:"img","aria-label":dates[i]+" · "+item.name+": "+fmt(value,2)+" "+unit});
   rect.append(tag("title",{},dates[i]+" · "+item.name+": "+fmt(value,2)+" "+unit));
   svg.append(rect);
  }
 }
 svg.append(tag("text",{x:L,y:H-8,fill:"#627b6c","font-size":"11"},rain?"Precipitación diaria (mm)":"Temperatura máxima del día (°C) · eje comparativo"));
 if(!rain)svg.append(tag("text",{x:W-R,y:H-8,"text-anchor":"end",fill:"#7b6950","font-size":"10"},"Eje vertical truncado; comparar alturas, no proporciones absolutas."));
 root.replaceChildren(svg);
}
window.OAFWeeklyBars=weeklyBars;
function rfEvidence(rain){
 const rows=rf?.metrica_diaria?.backtest_semanal_recursivo?.por_horizonte||[];
 const keyRF=rain?"mae_rf_lluvia_mm":"mae_rf_temperatura_c";
 const keyBase=rain?"mae_climatologia_lluvia_mm":"mae_climatologia_temperatura_c";
 const valid=rows.filter(row=>Number.isFinite(row[keyRF])&&Number.isFinite(row[keyBase]));
 const wins=valid.filter(row=>row[keyRF]<row[keyBase]).length;
 const meanRF=valid.length?valid.reduce((sum,row)=>sum+row[keyRF],0)/valid.length:NaN;
 const meanBase=valid.length?valid.reduce((sum,row)=>sum+row[keyBase],0)/valid.length:NaN;
 return {rows:valid,wins,meanRF,meanBase,eligible:valid.length===7&&wins>=5&&meanRF<meanBase};
}
window.OAFWeeklyEvidence=rfEvidence;
function weeklyOverview(days,externalValues,rfValues,eraValues,rain,point){
 const chart=$("oaf-ux14-weekchart");if(!chart)return;
 let host=$("oaf-ux43-week-summary");
 if(!host){host=E("div","oaf-ux43-week-summary");host.id="oaf-ux43-week-summary";chart.after(host);}
 host.replaceChildren();
 const valid=externalValues.every(Number.isFinite);
 if(!valid)return;
 const total=externalValues.reduce((a,b)=>a+b,0),max=Math.max(...externalValues);
 const peak=externalValues.indexOf(max),matched=rfValues.filter(Number.isFinite).length,evidence=rfEvidence(rain);
 const rfLabel=point?"No validado para parcela":evidence.eligible?matched+"/7 fechas coincidentes":"Retirado del gráfico · "+evidence.wins+"/7 mejoras";
 const labels=rain?[
  ["Lluvia prevista (7 días)",fmt(total,2)+" mm"],
  ["Día de mayor lluvia",days[peak].slice(8,10)+"/"+days[peak].slice(5,7)+" · "+fmt(max,2)+" mm"],
  ["RF OAF",rfLabel]
 ]:[
  ["Temperatura máxima prevista",fmt(max,1)+" °C"],
  ["Día más cálido",days[peak].slice(8,10)+"/"+days[peak].slice(5,7)],
  ["RF OAF",rfLabel]
 ];
 for(const [title,value] of labels){const cell=E("div","oaf-ux43-stat");cell.append(E("small",null,title),E("strong",null,value));host.append(cell);}
 if(point||!evidence.eligible){
  const note=E("p","oaf-ux43-stamp",point?
   "RF: sin entrenamiento parcelario validado; el pronóstico de este punto procede de Open-Meteo.":
   "RF: permanece en el panel de auditoría y no se presenta como pronóstico cuando no demuestra ventaja consistente frente a la climatología.");
  host.append(note);
 }
 if(!point&&evidence.rows.length===7){
  const message=evidence.eligible?
   "RF supera el criterio retrospectivo mínimo de 5/7 horizontes y menor MAE medio, pero sigue siendo experimental y requiere validación prospectiva e instrumental.":
   "RF no supera el criterio de publicación: mejora "+evidence.wins+"/7 horizontes de "+(rain?"lluvia":"temperatura máxima")+". Se omite de la gráfica comparativa; consulta la auditoría para ver el detalle.";
  host.append(E("p","oaf-ux43-model-warning",message));
 }
}
function weeklyModelAudit(){
 let target=$("oaf-ux43-model-audit");
 if(!target){
  target=E("details","oaf-ux43-model-audit");target.id="oaf-ux43-model-audit";
  target.append(E("summary",null,"Entrenamiento RF · evaluación y actualización"));
  $("oaf-ux14-weekstatus")?.after(target);
 }
 if(!target)return;
 const metric=rf?.metrica_diaria;
 if(rf?.estado!=="candidato_experimental_generado"||!metric){target.querySelector("summary").textContent="RF: salida no disponible";return}
 const active=target.open;
 target.replaceChildren(E("summary",null,"Entrenamiento RF · evaluación y actualización"));
 const stamp=rf.fecha_generacion_utc||"Sin fecha",last=Object.values(rf.ultimos_dias_era5||{}).sort().at(-1)||"No informado";
 const backtest=metric.backtest_semanal_recursivo||null;
 target.append(E("p",null,"Emisión: "+stamp+" · Último ERA5 incorporado: "+last+". Fuente: ERA5 reanálisis, cuatro localidades."));
 target.append(E("p",null,"Prueba 2025 a un día: MAE lluvia RF "+metric.mae_lluvia_mm+" mm, climatología "+metric.mae_climatologia_local_lluvia_mm+
  " mm; temperatura RF "+metric.mae_temperatura_c+" °C, climatología "+metric.mae_climatologia_local_temperatura_c+" °C."));
 if(backtest){
  const rows=backtest.por_horizonte||[],rain=rfEvidence(true),temp=rfEvidence(false);
  target.append(E("p",null,"Backtest de siete días encadenados (2025): "+backtest.n_origenes+" orígenes retrospectivos; evaluación por horizonte sin utilizar días futuros como rezagos."));
  target.append(E("p","oaf-ux43-model-warning","Habilidad comparada con climatología: lluvia "+rain.wins+"/7 horizontes mejores; temperatura máxima "+temp.wins+"/7. "+
   ((!rain.eligible||!temp.eligible)?"El candidato no se promueve a pronóstico operativo ni se muestra como serie predictiva en la gráfica.":"Aun con este resultado, permanece experimental y no tiene validación prospectiva ni instrumental.")));
  target.append(E("p",null,"MAE medio del backtest: lluvia RF "+fmt(rain.meanRF,2)+" mm frente a climatología "+fmt(rain.meanBase,2)+" mm; temperatura máxima RF "+fmt(temp.meanRF,2)+" °C frente a climatología "+fmt(temp.meanBase,2)+" °C."));
  const table=E("table"),head=E("tr");
  for(const x of ["Día","MAE RF lluvia","MAE clim. lluvia","MAE RF Tmax","MAE clim. Tmax"]){head.append(E("th",null,x))}
  table.append(head);
  for(const row of rows){
   const tr=E("tr");
   for(const cell of [row.dias_adelante,fmt(row.mae_rf_lluvia_mm,2)+" mm",fmt(row.mae_climatologia_lluvia_mm,2)+" mm",
    fmt(row.mae_rf_temperatura_c,2)+" °C",fmt(row.mae_climatologia_temperatura_c,2)+" °C"]){tr.append(E("td",null,cell))}
   table.append(tr);
  }
  target.append(table);
 }else{
  target.append(E("p",null,"Validación recursiva a siete días: aún sin resultado publicado por el proceso de reentrenamiento. No se infiere precisión semanal del MAE de un día."));
 }
 target.append(E("p","oaf-ux43-stamp","Modelo experimental; el reanálisis no es observación instrumental. La evaluación retrospectiva no acredita pronósticos emitidos en tiempo real."));
 target.open=active;
}
function legend(root,entries){root.replaceChildren();for(const [color,name] of entries){const s=E("span"),i=E("i");i.style.background=color;s.append(i,document.createTextNode(name));root.append(s)}}
/* Línea de base meteorológica, no predicción: media por día calendario ERA5 1996–2025.
 * Se representa sólo si al menos 20 de 30 años aportan valores por variable y fecha.
 */
function era5Reference(city){
 const custom=city&&typeof city==="object",loc=custom?[city.lat,city.lon]:geo[city];
 const cacheKey=custom?city.lat.toFixed(5)+","+city.lon.toFixed(5):city;
 if(!loc)return Promise.reject(Error("Localidad no contemplada por ERA5"));
 if(era5WeekCache.has(cacheKey))return era5WeekCache.get(cacheKey);
 const args=new URLSearchParams({latitude:String(loc[0]),longitude:String(loc[1]),
  start_date:"1996-01-01",end_date:"2025-12-31",
  daily:"precipitation_sum,temperature_2m_max",models:"era5",timezone:"America/Lima"});
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),28000);
 const task=fetch("https://archive-api.open-meteo.com/v1/archive?"+args,{signal:controller.signal,cache:"no-store"})
  .then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()})
  .then(j=>{
   const d=j.daily;if(j.error||!Array.isArray(d?.time)||d.time.length<10000)throw Error("Archivo ERA5 1996–2025 incompleto");
   const groups=new Map();
   d.time.forEach((date,i)=>{
    if(!/^(?:199[6-9]|20(?:0\d|1\d|2[0-5]))-\d{2}-\d{2}$/.test(date))return;
    const key=date.slice(5),rain=d.precipitation_sum?.[i],temp=d.temperature_2m_max?.[i];
    if(!groups.has(key))groups.set(key,{rain:[],tmax:[]});
    const a=groups.get(key);
    if(Number.isFinite(rain)&&rain>=0)a.rain.push(rain);
    if(Number.isFinite(temp))a.tmax.push(temp);
   });
   const average=values=>values?.length>=20?values.reduce((acc,v)=>acc+v,0)/values.length:NaN;
   return {rain:Object.fromEntries([...groups].map(([k,v])=>[k,average(v.rain)])),
    tmax:Object.fromEntries([...groups].map(([k,v])=>[k,average(v.tmax)])),
    years:"1996–2025",cell:[j.latitude,j.longitude]};
  }).catch(e=>{era5WeekCache.delete(cacheKey);throw e}).finally(()=>clearTimeout(timeout));
 era5WeekCache.set(cacheKey,task);
 return task;
}
function week(){
 const version=++weekVersion,point=window.OAFTerritory?.getActivePoint?.("semanal");
 const city=$("oaf-ux14-ciudad")?.value||"Chiclayo",variable=$("oaf-ux14-variable")?.value||"rain";
 const identity=point?point.lat.toFixed(5)+","+point.lon.toFixed(5):city;
 const output=$("oaf-ux14-weekchart"),status=$("oaf-ux14-weekstatus"),key=$("oaf-ux14-rf-semana")?.querySelector(".oaf-ux14-key");
 if(!output||!status)return;
 if(!point)renderPointDetails(null);
 if(!external||(point?external.pointKey!==identity:external.localidad!==city)){status.textContent="Consultando pronóstico para "+(point?point.name:city)+"…";return}
 const data=external.dias,days=data.time||[];
 if(days.length!==7)return;
 const rainfall=variable==="rain",field=rainfall?"precipitacion_mm":"temperatura_max_c";
 const ext=rainfall?data.precipitation_sum:data.temperature_2m_max;
 const evidence=rfEvidence(rainfall);
 const canPlotRF=!point&&evidence.eligible;
 let rows=canPlotRF?rf?.pronostico_diario_rf_experimental?.[city]||[]:[];
 if(rf?.estado!=="candidato_experimental_generado"||!Array.isArray(rows))rows=[];
 const map=new Map(rows.map(r=>[r.fecha,r[field]]));
 // No desplazar fechas: RF solo se grafica si supera el criterio de habilidad y coincide con la emisión.
 const forest=days.map(d=>canPlotRF&&map.has(d)&&Number.isFinite(map.get(d))?map.get(d):NaN);
 const matched=forest.filter(Number.isFinite).length;
 const group=[{name:"Open-Meteo · externo",color:"#278eb8",values:ext}];
 if(canPlotRF&&matched)group.push({name:"Random Forest OAF · experimental",color:"#aa65b4",values:forest,dash:"7 4"});
 weeklyBars(output,days,group,rainfall?"mm/día":"°C");
 weeklyOverview(days,ext,forest,null,rainfall,point);
 weeklyModelAudit();
 if(key){
  const items=[["#278eb8","Open-Meteo · pronóstico vigente"]];
  if(canPlotRF&&matched)items.push(["#aa65b4","Random Forest OAF · candidato experimental"]);
  legend(key,items);
 }
 if(point)renderPointDetails(point,data,external.metadata);
 let message="Pronóstico de "+(point?point.name+" ("+identity+" WGS84)":city)+" del "+days[0]+" al "+days.at(-1)+". ";
 if(canPlotRF&&matched){
  const diffs=forest.map((v,i)=>Number.isFinite(v)&&Number.isFinite(ext[i])?Math.abs(v-ext[i]):NaN).filter(Number.isFinite);
  const mean=diffs.reduce((a,b)=>a+b,0)/diffs.length;
  message+="RF coincide en "+matched+"/7 fechas; diferencia absoluta media entre pronósticos: "+fmt(mean)+(rainfall?" mm/día.":" °C.")+
   " Es una diferencia entre modelos, NO error comprobado contra observaciones.";
 }else if(point)message+="El punto utiliza Open-Meteo; no se extrapola RF desde otra localidad ni se afirma entrenamiento parcelario.";
 else message+="RF no se muestra porque mejora "+evidence.wins+"/7 horizontes de "+(rainfall?"lluvia":"temperatura máxima")+" frente a climatología; queda disponible solo en auditoría.";
 if(rf?.fecha_generacion_utc)message+=" RF emitido: "+rf.fecha_generacion_utc.slice(0,16)+" UTC.";
 message+=" Referencia vigente: Open-Meteo. ERA5 es referencia histórica, no pronóstico.";
 status.textContent=message+" Consultando promedio ERA5 1996–2025…";
 era5Reference(point||city).then(history=>{
  if(version!==weekVersion||!output.isConnected)return;
  const averages=days.map(date=>history[variable==="rain"?"rain":"tmax"][date.slice(5)]??NaN);
  const valid=averages.filter(Number.isFinite).length;
  if(!valid)throw Error("Sin registros históricos suficientes para estos días");
  const lines=[...group,{name:"ERA5 1996–2025 · promedio histórico",color:"#31946e",values:averages,dash:"3 3"}];
  weeklyBars(output,days,lines,rainfall?"mm/día":"°C");
  weeklyOverview(days,ext,forest,averages,rainfall,point);
  if(key){
   const items=[["#278eb8","Open-Meteo · pronóstico vigente"]];
   if(canPlotRF&&matched)items.push(["#aa65b4","RF OAF · emisión experimental"]);
   items.push(["#31946e","ERA5 1996–2025 · promedio histórico, no pronóstico"]);
   legend(key,items);
  }
  const delta=ext.map((value,i)=>Number.isFinite(value)&&Number.isFinite(averages[i])?value-averages[i]:NaN).filter(Number.isFinite);
  const mean=delta.length?delta.reduce((a,b)=>a+b,0)/delta.length:NaN;
  const comment=Number.isFinite(mean)?" Open-Meteo se sitúa en promedio "+fmt(Math.abs(mean))+(rainfall?" mm/día":" °C")+(mean>=0?" por encima":" por debajo")+" de la referencia histórica en estos días.":"";
  status.textContent=message+" ERA5: "+valid+"/7 fechas de referencia histórica disponibles; no son predicciones."+comment;
 }).catch(e=>{
  if(version===weekVersion&&output.isConnected)status.textContent=message+" ERA5 no disponible ("+e.message+"); no se reemplaza con cifras supuestas.";
 });
}
/* UX45 · API estacional oficial ECMWF SEAS5, media de ensamble.
 * La API NO admite daily=precipitation_sum. Usa datos NATIVOS de 6 horas:
 * hourly=precipitation,temperature_2m (4 periodos de 6 h por día).
 * La lluvia mensual suma sus aportes de 6 h (mm) y la temperatura es la
 * media de los registros 6 h (°C); sólo meses con cobertura 100% completa.
 * El modelo (~36 km) no está corregido por sesgo para parcelas.
 */
const seasonalCache=new Map();
const seasonalEndpoint="https://seasonal-api.open-meteo.com/v1/seasonal";
function seasonalMonthlyFromSixHourly(hourly,months){
 if(!Array.isArray(hourly?.time)||!Array.isArray(hourly?.precipitation)||
    !Array.isArray(hourly?.temperature_2m)||
    hourly.time.length!==hourly.precipitation.length||
    hourly.time.length!==hourly.temperature_2m.length)
    throw Error("Serie estacional de seis horas incompleta");
 const byMonth=new Map(),seen=new Set();
 for(let i=0;i<hourly.time.length;i++){
  const time=hourly.time[i];
  if(typeof time!=="string"||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(time))
   throw Error("Marca de tiempo estacional no válida");
  if(seen.has(time))throw Error("Horas estacionales duplicadas");
  seen.add(time);
  const month=time.slice(0,7);if(!months.includes(month))continue;
  if(!byMonth.has(month))byMonth.set(month,[]);
  byMonth.get(month).push({time,rain:hourly.precipitation[i],temp:hourly.temperature_2m[i]});
 }
 const rainfall=[],temperature=[],complete=[];
 for(const key of months){
  const rows=byMonth.get(key)||[],[year,month]=key.split("-").map(Number);
  const days=new Date(Date.UTC(year,month,0)).getUTCDate();
  const dailyCounts=new Map();
  for(const row of rows){const date=row.time.slice(0,10);dailyCounts.set(date,(dailyCounts.get(date)||0)+1);}
  const valid=rows.length===days*4&&dailyCounts.size===days&&
   [...dailyCounts.values()].every(n=>n===4)&&
   rows.every(row=>Number.isFinite(row.rain)&&row.rain>=0&&Number.isFinite(row.temp));
  rainfall.push(valid?rows.reduce((a,b)=>a+b.rain,0):NaN);
  temperature.push(valid?rows.reduce((a,b)=>a+b.temp,0)/rows.length:NaN);
  complete.push(valid);
 }
 return {rainfall,temperature,complete};
}
function seasonalRequest(city){
 if(seasonalCache.has(city))return seasonalCache.get(city);
 const coords=geo[city];
 if(!coords)return Promise.reject(Error("Localidad estacional sin coordenadas"));
 const params=new URLSearchParams({latitude:String(coords[0]),longitude:String(coords[1]),
  models:"ecmwf_seas5_ensemble_mean",hourly:"precipitation,temperature_2m",
  forecast_days:"217",timezone:"America/Lima",precipitation_unit:"mm"});
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),28000);
 const task=fetch(seasonalEndpoint+"?"+params,{cache:"no-store",signal:controller.signal}).then(r=>{
  if(!r.ok)throw Error("HTTP "+r.status);return r.json();
 }).then(j=>{
  if(j.error||!j.hourly)throw Error(j.reason||"Sin datos estacionales de seis horas");
  if(j.hourly_units?.precipitation&&j.hourly_units.precipitation!=="mm")throw Error("Unidad de lluvia distinta de mm");
  if(j.hourly_units?.temperature_2m&&j.hourly_units.temperature_2m!=="°C")throw Error("Unidad térmica distinta de °C");
  return {hourly:j.hourly,cell:[j.latitude,j.longitude],model:"ECMWF SEAS5 · media de ensamble"};
 }).catch(e=>{
  return {error:e.message||"Sin respuesta del proveedor",model:"ECMWF SEAS5 · media de ensamble"};
 }).finally(()=>clearTimeout(timeout));
 seasonalCache.set(city,task);
 return task;
}
let seasonToken=0;
function seasonalStatus(){
 let note=$("oaf-ux44-seasonal-note");
 if(!note){const chart=$("oaf-ux14-monthchart");if(!chart)return null;
  note=E("p","oaf-ux44-seasonal-note");note.id="oaf-ux44-seasonal-note";
  note.setAttribute("role","status");note.setAttribute("aria-live","polite");
  chart.after(note);
 }
 return note;
}
const MONTHS=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
function records(){return rf?.estado==="candidato_experimental_generado"&&rf?.unidades_temperatura==="Diario Tmax; mensual temperatura media (no promedio de Tmax)"}
function future(){
 const previousNote=$("oaf-ux44-seasonal-note");if(previousNote)previousNote.hidden=false;
 const city=$("oaf-ux16-mes-ciudad")?.value||"Chiclayo",variable=$("oaf-ux16-mes-variable")?.value||"rain";
 const root=$("oaf-ux14-monthchart"),status=$("oaf-ux14-monthstatus"),key=$("oaf-ux14-rf-mes")?.querySelector(".oaf-ux14-key");
 const rows=records()?rf?.escenarios_mensuales_rf_experimentales?.[city]:null;
 if(!Array.isArray(rows)||rows.length<6){root.textContent="Escenario RF prospectivo no disponible para esta localidad o versión del modelo.";status.textContent="No se publican cifras sin una salida RF experimental y versión de variables verificadas.";return}
 const f=variable==="rain"?"precipitacion_mm":"temperatura_media_c",unit=variable==="rain"?"mm/mes":"°C";
 const baseline=monthlyHistory?.[city];
 const climates=rows.slice(0,6).map(r=>baseline?.[Number(r.mes.slice(-2))] ? baseline[Number(r.mes.slice(-2))][variable==="rain"?"precipitacion_mm":"temperatura_c"] : NaN);
 const months=rows.slice(0,6).map(r=>r.mes);
 const series=[{name:"RF 10O · proyección experimental",values:rows.slice(0,6).map(r=>r[f]),color:"#aa65b4",dash:"7 4"}];
 const legends=[["#aa65b4","Random Forest OAF · experimental"]];
 if(climates.some(Number.isFinite)){
  series.push({name:"Climatología ERA5 1996–2020",values:climates,color:"#339878"});
  legends.push(["#339878","ERA5 1996–2020 · referencia histórica"]);
 }
 const note=seasonalStatus(),cached=seasonalCache.get(city);
 if(cached?.data){
  const values=cached.data[variable==="rain"?"rainfall":"temperature"];
  if(values.some(Number.isFinite)){
   series.push({name:"Open-Meteo / ECMWF SEAS5 · ensamble estacional",values,color:"#237fb1",dash:""});
   legends.push(["#237fb1","Open-Meteo · ECMWF SEAS5 estacional (36 km)"]);
  }
  const count=values.filter(Number.isFinite).length;
  if(note)note.textContent=count
   ?"Open-Meteo estacional (ECMWF SEAS5, ensamble): "+count+"/6 meses completos; lluvia mensual=suma de intervalos de 6 h, temperatura=media de 6 h. Pronóstico de área de ~36 km, sin corrección local de sesgo. Meses sin cobertura quedan vacíos."
   :"Open-Meteo estacional: no hay meses completos válidos en el horizonte consultado; no se dibujan cifras.";
 }else if(cached?.error){
  if(note)note.textContent="Open-Meteo estacional no disponible: "+cached.error+". Se conservan RF y ERA5, sin completar datos faltantes.";
 }else{
  if(note)note.textContent="Consultando Open-Meteo estacional / ECMWF SEAS5; sólo se mostrarán meses con datos completos.";
  const request=++seasonToken;
  seasonalRequest(city).then(payload=>{
   const present=seasonalCache.get(city);
   if(!present)return;
   const next=payload.error?{error:payload.error}:{data:seasonalMonthlyFromSixHourly(payload.hourly,months),cell:payload.cell};
   seasonalCache.set(city,next);
   if(request===seasonToken&&$("oaf-ux16-vista")?.value==="futuro"&&$("oaf-ux16-mes-ciudad")?.value===city)future();
  }).catch(e=>{
   seasonalCache.set(city,{error:e.message||"Error de datos"});
   if(request===seasonToken&&$("oaf-ux16-vista")?.value==="futuro"&&$("oaf-ux16-mes-ciudad")?.value===city)future();
  });
 }
 plot(root,months.map(r=>MONTHS[Number(r.slice(-2))-1]+" "+r.slice(2,4)),series,unit);
 if(key)legend(key,legends);
 const mae=rf?.metrica_mensual;
 const multi=mae?.evaluacion_multihorizonte?.por_horizonte||[];
 const lead3=multi.find(x=>x.meses_adelante===3),lead6=multi.find(x=>x.meses_adelante===6);
 status.textContent="Localidad: "+city+". RF candidato "+rows[0].mes+"–"+rows[5].mes+", desde último mes ERA5 completo: "+(rf.ultimo_mes_con_datos?.[city]||"sin fecha")+". Los 6 meses mostrados implican entre "+(rows[0].adelanto_desde_ultimo_mes_observado||2)+" y "+(rows[5].adelanto_desde_ultimo_mes_observado||7)+" pasos autoregresivos. MAE retrospectivo de 1 paso RF "+(mae?.mae_lluvia_mm??"s/d")+" mm/mes frente a climatología "+(mae?.mae_climatologia_local_mm??"s/d")+" mm/mes. "+(lead3?"Backtest recursivo del mes 3: RF "+fmt(lead3.mae_rf_mm)+" mm y climatología "+fmt(lead3.mae_climatologia_local_mm)+" mm. ":"")+(lead6?"En el mes 6: RF "+fmt(lead6.mae_rf_mm)+" mm y climatología "+fmt(lead6.mae_climatologia_local_mm)+" mm. ":"")+"El mes 7 de anticipación no dispone todavía de comprobación comparable.";
}
function hist(){
 const current=$("oaf-ux14-metric");if(current)current.dispatchEvent(new Event("change",{bubbles:true}));
 const key=$("oaf-ux14-rf-mes")?.querySelector(".oaf-ux14-key");
 if(key){
 const option=current?.value||"all",labels=[["#2e8ab8","Lluvia observada CHIRPS"]];
 if(option!=="ref")labels.push(["#e49d4d","Random Forest 10K · retrospectivo"]);
 if(option!=="rf")labels.push(["#43977a","Climatología histórica"]);
 legend(key,labels);
 }
}
function month(){
 const vista=$("oaf-ux16-vista")?.value||"historico",historicalControls=$("oaf-ux16-historical-controls"),futureControls=$("oaf-ux16-future-controls");
 if(historicalControls)historicalControls.hidden=vista==="futuro";
 if(futureControls)futureControls.hidden=vista!=="futuro";
 const historicalKpis=$("oaf-ux14-kpis");if(historicalKpis)historicalKpis.hidden=vista==="futuro";
 if(vista==="futuro")future();else{const note=$("oaf-ux44-seasonal-note");if(note)note.hidden=true;hist();}
 
}
async function climatology(){
 try{
  const r=await fetch("datos/lambayeque_mensual_era5_8d.csv",{cache:"no-store"});
  if(!r.ok)throw Error("Histórico ERA5");
  const lines=(await r.text()).trim().split(/\r?\n/);const headers=lines.shift().split(",");const byCity={};
  for(const line of lines){const parts=line.split(",");if(parts.length!==headers.length)continue;const d=Object.fromEntries(headers.map((k,i)=>[k,parts[i]]));
   if(!places.includes(d.localidad)||d.mes<"1996-01"||d.mes>"2020-12")continue;
   const mo=Number(d.mes.slice(5)),rain=Number(d.precipitacion_mm),temp=Number(d.temperatura_c);
   if(!Number.isFinite(rain)||!Number.isFinite(temp))continue;
   const month=(byCity[d.localidad]||={})[mo]||((byCity[d.localidad][mo])={precipitacion_mm:0,temperatura_c:0,n:0});
   month.precipitacion_mm+=rain;month.temperatura_c+=temp;month.n++;
  }
  for(const values of Object.values(byCity))for(const d of Object.values(values)){d.precipitacion_mm/=d.n;d.temperatura_c/=d.n;}
  monthlyHistory=byCity;
  if($("oaf-ux16-vista")?.value==="futuro")future();
 }catch(e){console.warn("OAF: climatología no disponible",e)}
}
function setup(){
 if(initialized||!$("oaf-ux14-rf-semana")||!$("oaf-ux14-rf-mes"))return;
 initialized=true;
 // Legacy code had two duplicated charts. Remove those panels instead of keeping them hidden.
 $("oaf-ux15-rf-week")?.remove();$("oaf-ux15-rf-future")?.remove();
 const block=$("oaf-ux14-rf-mes"),plotArea=$("oaf-ux14-monthchart");
 const wrapper=E("div","oaf-ux16-month-view");
 const label=E("label",null,"Vista del gráfico mensual"),selector=E("select");
 selector.id="oaf-ux16-vista";
 for(const [value,title] of [["historico","Evaluación 2021–2025 · por paisaje"],["futuro","Noviembre 2026–abril 2027 · por localidad"]]){const option=E("option",null,title);option.value=value;selector.append(option)}
 selector.value="futuro"; // Abrir noviembre 2026–abril 2027 por defecto, sin borrar la vista retrospectiva.
 label.htmlFor=selector.id;wrapper.append(label,selector);
 const historical=$("oaf-ux14-rf-mes")?.querySelector(".oaf-ux14-controls");
 if(historical){historical.id="oaf-ux16-historical-controls";historical.before(wrapper)}
 else plotArea?.before(wrapper);
 const futureControl=E("div","oaf-ux14-controls");futureControl.id="oaf-ux16-future-controls";futureControl.hidden=true;
 const cityLabel=E("label",null,"Localidad"),citySel=E("select");cityLabel.htmlFor="oaf-ux16-mes-ciudad";citySel.id=cityLabel.htmlFor;
 for(const place of places){const opt=E("option",null,place);citySel.append(opt)}
 const varLabel=E("label",null,"Variable"),varSel=E("select");varSel.id="oaf-ux16-mes-variable";varLabel.htmlFor=varSel.id;
 for(const [val,txt] of [["rain","Precipitación mensual (mm)"],["temp","Temperatura media mensual (°C)"]]){const opt=E("option",null,txt);opt.value=val;varSel.append(opt)}
 futureControl.append(cityLabel,citySel,varLabel,varSel);
 if(historical)historical.after(futureControl);else wrapper.after(futureControl);
 // Se conservan las proyecciones en el gráfico mensual con filtros; se elimina la cuadrícula repetida de seis tarjetas.
 const redraw=()=>month();
 selector.addEventListener("change",month);
 citySel.addEventListener("change",redraw);
 varSel.addEventListener("change",month);
 const varWeek=$("oaf-ux14-variable");
 varWeek?.addEventListener("change",()=>queueMicrotask(week));
 $("oaf-ux14-ciudad")?.addEventListener("change",()=>{external=null;week()});
 fetch("datos/rf_experimental_ux15.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("RF "+r.status);return r.json()}).then(d=>{
  if(d.operativo_certificado!==false||d.alertas_automaticas!==false)throw Error("RF no identificado como candidato");
  rf=d;week();if(selector.value==="futuro")future();
 }).catch(e=>{rf={estado:"datos_no_disponibles"};week();console.warn("OAF RF",e)});
 climatology();
 month();
}
let customRequest=0;
function renderPointDetails(point,daily,metadata){
 const existing=$("oaf-ux51-point-details");
 if(!point||!daily){if(existing)existing.hidden=true;return;}
 let panel=existing;
 if(!panel){
  panel=E("section","oaf-ux51-point-details");panel.id="oaf-ux51-point-details";
  const anchor=$("oaf-ux14-weekstatus")||$("oaf-ux14-weekchart");
  if(anchor)anchor.after(panel);
 }
 if(!panel)return;
 panel.hidden=false;
 if(!document.getElementById("oaf-ux51-point-style")){
  const style=E("style");style.id="oaf-ux51-point-style";
  style.textContent=".oaf-ux51-point-details{margin:14px 0;padding:14px;border:1px solid #c8ddd2;border-radius:12px;background:#f5faf7;overflow:auto}.oaf-ux51-point-details h3{margin:0 0 8px;color:#185b49;font-size:16px}.oaf-ux51-point-details p{font-size:12px;line-height:1.55;color:#536d62}.oaf-ux51-point-details table{width:100%;min-width:760px;border-collapse:collapse;font-size:12px}.oaf-ux51-point-details th,.oaf-ux51-point-details td{padding:7px;border-bottom:1px solid #d8e6de;text-align:right}.oaf-ux51-point-details th:first-child,.oaf-ux51-point-details td:first-child{text-align:left}.oaf-ux51-point-details th{color:#185b49;background:#eaf4ee}";
  document.head.append(style);
 }
 panel.replaceChildren(E("h3",null,"Indicadores agroclimáticos · área productiva"));
 const cellLat=metadata?.latitude,cellLon=metadata?.longitude;
 const cellText=Number.isFinite(cellLat)&&Number.isFinite(cellLon)?
  "Celda de modelo devuelta: "+cellLat.toFixed(4)+", "+cellLon.toFixed(4)+".":
  "El proveedor no informó la coordenada central de la celda.";
 panel.append(E("p",null,"Coordenada solicitada WGS84: "+point.lat.toFixed(5)+", "+point.lon.toFixed(5)+". "+cellText+
  " Pronóstico externo Open-Meteo; no es una medición de sensor dentro del predio."));
 const columns=[
  ["precipitation_sum","Lluvia","mm"],["temperature_2m_max","T. máx.","°C"],["temperature_2m_min","T. mín.","°C"],
  ["relative_humidity_2m_mean","HR media","%"],["shortwave_radiation_sum","Radiación","MJ/m²"],
  ["wind_speed_10m_max","Viento máx.","km/h"],["et0_fao_evapotranspiration","ET₀ FAO","mm"],
  ["vapour_pressure_deficit_max","DPV máx.","kPa"]
 ];
 const table=E("table"),head=E("tr");head.append(E("th",null,"Día"));
 for(const col of columns)head.append(E("th",null,col[1]+" ("+col[2]+")"));
 const thead=E("thead");thead.append(head);table.append(thead);
 const body=E("tbody");
 daily.time.forEach((date,i)=>{
  const tr=E("tr");tr.append(E("td",null,date));
  for(const [key,label,unit] of columns){
   const value=daily[key]?.[i];
   tr.append(E("td",null,Number.isFinite(value)?fmt(value,1):"—"));
  }
  body.append(tr);
 });
 table.append(body);panel.append(table);
 panel.append(E("p",null,"Lectura: la lluvia y la temperatura describen el pronóstico diario; humedad, radiación, viento, evapotranspiración de referencia y DPV ayudan a contextualizar la demanda atmosférica. Los campos sin dato se muestran como —, nunca se imputan."));
}
async function weeklyPoint(point){
 const token=++customRequest;
 if(!point){external=null;renderPointDetails(null);const city=$("oaf-ux14-ciudad");city?.dispatchEvent(new Event("change",{bubbles:true}));return;}
 const key=point.lat.toFixed(5)+","+point.lon.toFixed(5);
 const params=new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),
  timezone:"America/Lima",forecast_days:"7",
  daily:"precipitation_sum,temperature_2m_max,temperature_2m_min,relative_humidity_2m_mean,shortwave_radiation_sum,wind_speed_10m_max,et0_fao_evapotranspiration,vapour_pressure_deficit_max"});
 const status=$("oaf-ux14-weekstatus");if(status)status.textContent="Consultando pronóstico e indicadores agroclimáticos para "+point.name+"…";
 try{
  const res=await fetch("https://api.open-meteo.com/v1/forecast?"+params,{cache:"no-store"});
  if(!res.ok)throw Error("Open-Meteo HTTP "+res.status);
  const payload=await res.json(),d=payload.daily;
  if(!Array.isArray(d?.time)||d.time.length!==7||!d.precipitation_sum?.every(Number.isFinite)||!d.temperature_2m_max?.every(Number.isFinite))
   throw Error("Respuesta diaria incompleta en lluvia o temperatura máxima");
  if(token!==customRequest||!window.OAFTerritory?.getActivePoint?.("semanal"))return;
  external={localidad:"Punto personalizado",pointKey:key,dias:d,metadata:{latitude:payload.latitude,longitude:payload.longitude,dailyUnits:payload.daily_units||{}}};
  week();
 }catch(err){
  if(token===customRequest&&status){
   renderPointDetails(null);
   $("oaf-ux14-weekchart").textContent="No se recuperaron datos para esta coordenada.";
   status.textContent="Consulta no disponible: "+err.message;
  }
 }
}

document.addEventListener("oaf:area-update",e=>{
 if(e.detail?.scope!=="semanal")return;
 if(e.detail.active&&e.detail.point)weeklyPoint(e.detail.point);
 else {++customRequest;external=null;week();}
});
document.addEventListener("DOMContentLoaded",()=>setTimeout(()=>{const p=window.OAFTerritory?.getActivePoint?.("semanal");if(p)weeklyPoint(p);},300));
document.addEventListener("oaf:ux42-repaint-week",()=>week());
document.addEventListener("oaf:ux16-externo-diario",event=>{if(window.OAFTerritory?.getActivePoint?.("semanal"))return;external=event.detail;week()});
document.addEventListener("oaf:ux9-ready",()=>queueMicrotask(setup));
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup,{once:true});else setup();
})();