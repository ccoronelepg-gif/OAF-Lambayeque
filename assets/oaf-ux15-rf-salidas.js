/* UX16 — Dos gráficas compartidas (semanal y mensual) y un bloque sin gráfica de escenarios RF. */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const E=(tag,cls,txt)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=String(txt);return e};
const places=["Chiclayo","Jayanca","Motupe","Olmos"];
const fmt=(v,p=1)=>Number(v).toLocaleString("es-PE",{minimumFractionDigits:p,maximumFractionDigits:p});
let initialized=false,rf=null,external=null,monthlyReady=false,monthlyHistory=null;
const NS="http://www.w3.org/2000/svg";
function plot(root,axis,series,unit){
 if(!root)return;
 const all=series.flatMap(s=>s.values.filter(Number.isFinite));
 if(!all.length){root.textContent="No hay datos numéricos comprobados para este periodo.";return}
 const W=790,H=300,L=57,R=22,T=22,B=56;
 const low=unit.startsWith("mm")?0:Math.min(...all)-1.5;
 const top=Math.max(...all,low+.8)+(Math.max(...all)-low)*.12;
 const x=i=>L+(i+.5)*(W-L-R)/axis.length,y=v=>T+(top-v)/(top-low)*(H-T-B);
 const tag=(name,attrs,txt)=>{const a=document.createElementNS(NS,name);for(const [k,v] of Object.entries(attrs||{}))a.setAttribute(k,String(v));if(txt!==undefined)a.textContent=txt;return a};
 const svg=tag("svg",{viewBox:"0 0 790 300",role:"img","aria-label":unit+" · "+series.map(s=>s.name).join(" frente a ")});
 for(let k=0;k<=4;k++){const v=low+(top-low)*k/4,Y=y(v);svg.append(tag("line",{x1:L,x2:W-R,y1:Y,y2:Y,stroke:"#dae7df","stroke-width":1}),tag("text",{x:L-8,y:Y+4,"text-anchor":"end",fill:"#536d62","font-size":12},fmt(v,0)))}
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
function week(){
 const city=$("oaf-ux14-ciudad")?.value||"Chiclayo",variable=$("oaf-ux14-variable")?.value||"rain";
 const output=$("oaf-ux14-weekchart"),status=$("oaf-ux14-weekstatus"),key=$("oaf-ux14-rf-semana")?.querySelector(".oaf-ux14-key");
 if(!output||!status)return;
 if(!external||external.localidad!==city){status.textContent="Consultando la referencia meteorológica para "+city+"…";return}
 const data=external.dias,days=data.time||[];
 if(days.length!==7)return;
 const rainfall=variable==="rain",field=rainfall?"precipitacion_mm":"temperatura_max_c";
 const ext=rainfall?data.precipitation_sum:data.temperature_2m_max;
 let rows=rf?.pronostico_diario_rf_experimental?.[city]||[];
 if(rf?.estado!=="candidato_experimental_generado"||!Array.isArray(rows))rows=[];
 const map=new Map(rows.map(r=>[r.fecha,r[field]]));
 // Never shift the RF in time to make curves overlap. Missing days remain gaps.
 const forest=days.map(d=>map.has(d)&&Number.isFinite(map.get(d))?map.get(d):NaN);
 const matched=forest.filter(Number.isFinite).length;
 const group=[{name:"Open-Meteo · externo",color:"#278eb8",values:ext}];
 if(matched)group.push({name:"Random Forest OAF · experimental",color:"#aa65b4",values:forest,dash:"7 4"});
 plot(output,days.map(d=>d.slice(5)),group,rainfall?"mm/día":"°C");
 if(key)legend(key,[["#278eb8","Open-Meteo · referencia externa"],["#aa65b4","Random Forest OAF · experimental (trazo discontinuo)"]]);
 let message="Comparación de "+city+" del "+days[0]+" al "+days.at(-1)+". ";
 if(matched){
  const diffs=forest.map((v,i)=>Number.isFinite(v)&&Number.isFinite(ext[i])?Math.abs(v-ext[i]):NaN).filter(Number.isFinite);
  const mean=diffs.reduce((a,b)=>a+b,0)/diffs.length;
  message+="Coincidencia: "+matched+"/7 fechas; diferencia absoluta media entre pronósticos: "+fmt(mean)+(rainfall?" mm/día.":" °C.");
  message+=" Es una diferencia entre modelos, NO error comprobado contra lluvia o temperatura observadas.";
 } else message+="No hay una emisión RF con fechas coincidentes; no se desplaza artificialmente la línea.";
 if(rf?.fecha_generacion_utc)message+=" RF emitido: "+rf.fecha_generacion_utc.slice(0,16)+" UTC.";
 message+=" OpenWeather requiere credenciales y todavía no está conectado: la referencia actual es Open-Meteo.";
 status.textContent=message;
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
 status.textContent="Localidad: "+city+". Proyección autoregresiva experimental "+rows[0].mes+"–"+rows[5].mes+" emitida "+(rf.fecha_generacion_utc||"sin fecha")+". MAE RF retrospectivo de UN paso: "+(mae?.mae_lluvia_mm??"s/d")+" mm/mes. No mide precisión a seis meses ni permite emitir alertas. La línea histórica NO es un pronóstico.";
}
function cards(){
 const area=$("oaf-ux16-future-cards"),city=$("oaf-ux16-mes-ciudad")?.value||"Chiclayo";if(!area)return;
 area.replaceChildren();
 const rows=records()?rf?.escenarios_mensuales_rf_experimentales?.[city]:null;
 if(!Array.isArray(rows)||rows.length<6){area.append(E("p",null,"Esperando resultados RF experimentales mensuales verificados para esta localidad."));return}
 for(const row of rows.slice(0,6)){
  const tile=E("article","oaf-ux15-future-month"),month=MONTHS[Number(row.mes.slice(-2))-1]+" "+row.mes.slice(0,4);
  tile.append(E("strong",null,month),E("span",null,"Lluvia RF: "+fmt(row.precipitacion_mm)+" mm/mes"),E("span",null,"T. media RF: "+fmt(row.temperatura_media_c)+" °C"),E("small","oaf-ux15-future-badge","Candidato · no operativo"));
  area.append(tile);
 }
}
function hist(){
 const current=$("oaf-ux14-metric");if(current)current.dispatchEvent(new Event("change",{bubbles:true}));
 const key=$("oaf-ux14-rf-mes")?.querySelector(".oaf-ux14-key");
 if(key)legend(key,[["#2e8ab8","Lluvia observada CHIRPS"],["#e49d4d","Random Forest 10K · retrospectivo"],["#43977a","Climatología histórica"]]);
}
function month(){
 const vista=$("oaf-ux16-vista")?.value||"historico",historicalControls=$("oaf-ux16-historical-controls"),futureControls=$("oaf-ux16-future-controls");
 if(historicalControls)historicalControls.hidden=vista==="futuro";
 if(futureControls)futureControls.hidden=vista!=="futuro";
 const historicalKpis=$("oaf-ux14-kpis");if(historicalKpis)historicalKpis.hidden=vista==="futuro";
 if(vista==="futuro")future();else hist();
 cards();
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
 const predictions=E("section","oaf-ux16-future-panel");predictions.id="oaf-ux16-months";
 predictions.append(E("small","oaf-ux15-rf-chip","03 · Random Forest experimental"),E("h3",null,"Predicción de noviembre de 2026 a abril de 2027, por localidad"),
 E("p",null,"Precipitación y temperatura media mensual derivadas del candidato RF 10O. Selecciona una localidad y cambia arriba la vista del gráfico para compararla con su climatología histórica."));
 const controls=E("div","oaf-ux14-controls"),label2=E("label",null,"Localidad para próximos meses"),sel2=E("select");sel2.id="oaf-ux16-months-city";
 for(const name of places){const op=E("option",null,name);sel2.append(op)}
 controls.append(label2,sel2);predictions.append(controls);
 const cardsRoot=E("div","oaf-ux15-future-calendar");cardsRoot.id="oaf-ux16-future-cards";predictions.append(cardsRoot);
 predictions.append(E("p","oaf-ux14-source","Random Forest 10O: investigación y mejora continua. Las emisiones futuras necesitan evaluación prospectiva; no sustituyen los avisos SENAMHI ni constituyen recomendaciones operativas."));
 block.after(predictions);
 const redraw=()=>{const a=citySel.value;if(sel2.value!==a)sel2.value=a;month()};
 selector.addEventListener("change",month);
 citySel.addEventListener("change",redraw);
 varSel.addEventListener("change",month);
 sel2.addEventListener("change",()=>{citySel.value=sel2.value;month()});
 const varWeek=$("oaf-ux14-variable");
 varWeek?.addEventListener("change",()=>queueMicrotask(week));
 $("oaf-ux14-ciudad")?.addEventListener("change",()=>{external=null;week()});
 fetch("datos/rf_experimental_ux15.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("RF "+r.status);return r.json()}).then(d=>{
  if(d.operativo_certificado!==false||d.alertas_automaticas!==false)throw Error("RF no identificado como candidato");
  rf=d;week();cards();if(selector.value==="futuro")future();
 }).catch(e=>{rf={estado:"datos_no_disponibles"};week();cards();console.warn("OAF RF",e)});
 climatology();
 cards();
}
document.addEventListener("oaf:ux16-externo-diario",event=>{external=event.detail;week()});
document.addEventListener("oaf:ux9-ready",()=>queueMicrotask(setup));
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup,{once:true});else setup();
})();