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
 if(!external||(point?external.pointKey!==identity:external.localidad!==city)){status.textContent="Consultando pronóstico para "+(point?point.name:city)+"…";return}
 const data=external.dias,days=data.time||[];
 if(days.length!==7)return;
 const rainfall=variable==="rain",field=rainfall?"precipitacion_mm":"temperatura_max_c";
 const ext=rainfall?data.precipitation_sum:data.temperature_2m_max;
 let rows=point?[]:rf?.pronostico_diario_rf_experimental?.[city]||[];
 if(rf?.estado!=="candidato_experimental_generado"||!Array.isArray(rows))rows=[];
 const map=new Map(rows.map(r=>[r.fecha,r[field]]));
 // Never shift the RF in time to make curves overlap. Missing days remain gaps.
 const forest=days.map(d=>map.has(d)&&Number.isFinite(map.get(d))?map.get(d):NaN);
 const matched=forest.filter(Number.isFinite).length;
 const group=[{name:"Open-Meteo · externo",color:"#278eb8",values:ext}];
 if(matched)group.push({name:"Random Forest OAF · experimental",color:"#aa65b4",values:forest,dash:"7 4"});
 plot(output,days.map(d=>d.slice(5)),group,rainfall?"mm/día":"°C");
 if(key)legend(key,[["#278eb8","Open-Meteo · referencia externa"],["#aa65b4","Random Forest OAF · experimental (trazo discontinuo)"]]);
 let message="Comparación de "+(point?point.name+" ("+identity+" WGS84)":city)+" del "+days[0]+" al "+days.at(-1)+". ";
 if(matched){
  const diffs=forest.map((v,i)=>Number.isFinite(v)&&Number.isFinite(ext[i])?Math.abs(v-ext[i]):NaN).filter(Number.isFinite);
  const mean=diffs.reduce((a,b)=>a+b,0)/diffs.length;
  message+="Coincidencia: "+matched+"/7 fechas; diferencia absoluta media entre pronósticos: "+fmt(mean)+(rainfall?" mm/día.":" °C.");
  message+=" Es una diferencia entre modelos, NO error comprobado contra lluvia o temperatura observadas.";
 } else message+=point?"No hay RF calibrado para esta parcela; se consulta la coordenada indicada. ":"No hay una emisión RF con fechas coincidentes; no se desplaza artificialmente la línea.";
 if(rf?.fecha_generacion_utc)message+=" RF emitido: "+rf.fecha_generacion_utc.slice(0,16)+" UTC.";
 message+=" Referencia vigente: Open-Meteo. RF es una emisión archivada, no ajustada a fechas nuevas.";
 status.textContent=message+" Consultando promedio ERA5 1996–2025…";
 era5Reference(point||city).then(history=>{
  if(version!==weekVersion||!output.isConnected)return;
  const averages=days.map(date=>history[variable==="rain"?"rain":"tmax"][date.slice(5)]??NaN);
  const valid=averages.filter(Number.isFinite).length;
  if(!valid)throw Error("Sin registros históricos suficientes para estos días");
  const lines=[...group,{name:"ERA5 1996–2025 · promedio histórico",color:"#31946e",values:averages,dash:"3 3"}];
  plot(output,days.map(d=>d.slice(5)),lines,rainfall?"mm/día":"°C");
  if(key)legend(key,[["#278eb8","Open-Meteo · pronóstico vigente"],["#aa65b4","RF OAF · emisión experimental"],["#31946e","ERA5 1996–2025 · promedio histórico, no pronóstico"]]);
  const delta=ext.map((value,i)=>Number.isFinite(value)&&Number.isFinite(averages[i])?value-averages[i]:NaN).filter(Number.isFinite);
  const mean=delta.length?delta.reduce((a,b)=>a+b,0)/delta.length:NaN;
  const comment=Number.isFinite(mean)?" Open-Meteo se sitúa en promedio "+fmt(Math.abs(mean))+(rainfall?" mm/día":" °C")+(mean>=0?" por encima":" por debajo")+" de la referencia histórica en estos días.":"";
  status.textContent=message+" ERA5: "+valid+"/7 fechas de referencia histórica disponibles; no son predicciones."+comment;
 }).catch(e=>{
  if(version===weekVersion&&output.isConnected)status.textContent=message+" ERA5 no disponible ("+e.message+"); no se reemplaza con cifras supuestas.";
 });
}
const MONTHS=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
function records(){return rf?.estado==="candidato_experimental_generado"&&rf?.unidades_temperatura==="Diario Tmax; mensual temperatura media (no promedio de Tmax)"}
function future(){
 const city=$("oaf-ux16-mes-ciudad")?.value||"Chiclayo",variable=$("oaf-ux16-mes-variable")?.value||"rain";
 const root=$("oaf-ux14-monthchart"),status=$("oaf-ux14-monthstatus"),key=$("oaf-ux14-rf-mes")?.querySelector(".oaf-ux14-key");
 const rows=records()?rf?.escenarios_mensuales_rf_experimentales?.[city]:null;
 if(!Array.isArray(rows)||rows.length<6){root.textContent="Escenario RF prospectivo no disponible para esta localidad o versión del modelo.";status.textContent="No se publican cifras sin una salida RF experimental y versión de variables verificadas.";return}
 const f=variable==="rain"?"precipitacion_mm":"temperatura_media_c",unit=variable==="rain"?"mm/mes":"°C";
 const baseline=monthlyHistory?.[city];
 const climates=rows.slice(0,6).map(r=>baseline?.[Number(r.mes.slice(-2))] ? baseline[Number(r.mes.slice(-2))][variable==="rain"?"precipitacion_mm":"temperatura_c"] : NaN);
 const series=[{name:"RF 10O · proyección experimental",values:rows.slice(0,6).map(r=>r[f]),color:"#aa65b4",dash:"7 4"}];
 if(climates.some(Number.isFinite))series.push({name:"Climatología ERA5 1996–2020",values:climates,color:"#339878"});
 plot(root,rows.slice(0,6).map(r=>MONTHS[Number(r.mes.slice(-2))-1]+" "+r.mes.slice(2,4)),series,unit);
 if(key)legend(key,[["#aa65b4","Random Forest 10O · futuro experimental"],["#339878","Climatología ERA5 1996–2020 · referencia histórica"]]);
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
 if(vista==="futuro")future();else hist();
 
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
async function weeklyPoint(point){
 const token=++customRequest;
 if(!point){external=null;const city=$("oaf-ux14-ciudad");city?.dispatchEvent(new Event("change",{bubbles:true}));return;}
 const key=point.lat.toFixed(5)+","+point.lon.toFixed(5);
 const params=new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),
  timezone:"America/Lima",forecast_days:"7",daily:"precipitation_sum,temperature_2m_max"});
 const status=$("oaf-ux14-weekstatus");if(status)status.textContent="Consultando pronóstico para "+point.name+"…";
 try{
  const res=await fetch("https://api.open-meteo.com/v1/forecast?"+params,{cache:"no-store"});
  if(!res.ok)throw Error("Open-Meteo HTTP "+res.status);
  const d=(await res.json()).daily;
  if(!Array.isArray(d?.time)||d.time.length!==7||!d.precipitation_sum?.every(Number.isFinite)||!d.temperature_2m_max?.every(Number.isFinite))throw Error("Respuesta diaria incompleta");
  if(token!==customRequest||!window.OAFTerritory?.getActivePoint?.("semanal"))return;
  external={localidad:"Punto personalizado",pointKey:key,dias:d};week();
 }catch(err){if(token===customRequest&&status){$("oaf-ux14-weekchart").textContent="No se recuperaron datos para esta coordenada.";status.textContent="Consulta no disponible: "+err.message;}}
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