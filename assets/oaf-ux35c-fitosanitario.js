/* OAF-Lambayeque · Módulo C fitosanitario, primera integración operativa.
 * Modelo habilitado: arándano / Botrytis cinerea, indicador meteorológico exploratorio
 * HR >90% durante >=6 h consecutivas. NO representa mojado foliar ni probabilidad de infección.
 * Los demás pares cultivo-organismo quedan pendientes hasta documentar parámetros específicos.
 */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const ROOT="https://api.open-meteo.com/v1";
const ARCHIVE="https://archive-api.open-meteo.com/v1/archive";
const VARS=["temperature_2m","relative_humidity_2m","precipitation","shortwave_radiation","vapour_pressure_deficit","wind_speed_10m"];
const SITES={
 "Chiclayo":{lat:-6.7714,lon:-79.8409,province:"Chiclayo",district:"Chiclayo"},
 "Jayanca":{lat:-6.39278,lon:-79.8228,province:"Lambayeque",district:"Jayanca"},
 "Motupe":{lat:-6.15083,lon:-79.7142,province:"Lambayeque",district:"Motupe"},
 "Olmos":{lat:-5.98825,lon:-79.74723,province:"Lambayeque",district:"Olmos"}
};
const CROPS=[
 {id:"arandano",name:"Arándano",organisms:[{id:"botrytis",name:"Botrytis cinerea",kind:"hongo",status:"proxy",model:"RH90_6H",source:"UC IPM · Botrytis blight"}]},
 {id:"mango",name:"Mango",organisms:[]},
 {id:"palto",name:"Palto",organisms:[]},
 {id:"vid",name:"Vid",organisms:[]},
 {id:"banano",name:"Banano",organisms:[]},
 {id:"maracuya",name:"Maracuyá",organisms:[]},
 {id:"cafe",name:"Café",organisms:[]}
];
const state={site:"Motupe",coords:{...SITES.Motupe},result:null,request:0,marker:null};
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmt=(v,d=1)=>Number.isFinite(v)?v.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
function localDate(){return new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date())}
function addDays(iso,n){const d=new Date(iso+"T12:00:00Z");d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10)}
function groupHourly(hourly){
 if(!hourly||!Array.isArray(hourly.time))throw Error("La API no devolvió una serie horaria.");
 for(const k of VARS)if(!Array.isArray(hourly[k])||hourly[k].length!==hourly.time.length)throw Error("Serie incompleta: "+k);
 const days=new Map();
 for(let i=0;i<hourly.time.length;i++){
  const stamp=hourly.time[i];if(typeof stamp!=="string"||!/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-2][0-9]:00$/.test(stamp))throw Error("Marca horaria inválida.");
  const date=stamp.slice(0,10),hour=Number(stamp.slice(11,13));
  if(!days.has(date))days.set(date,new Map());
  if(days.get(date).has(hour))throw Error("Hora duplicada: "+stamp);
  const row={};for(const k of VARS){const v=hourly[k][i];if(typeof v!=="number"||!Number.isFinite(v))throw Error("Dato ausente/no numérico: "+k+" · "+stamp);row[k]=v}
  if(row.relative_humidity_2m<0||row.relative_humidity_2m>100||row.precipitation<0||row.shortwave_radiation<0)throw Error("Dato meteorológico fuera de rango.");
  days.get(date).set(hour,row);
 }
 return days;
}
function scanEpisodes(rows){
 let streak=0,longest=0,episodes=0,totalHigh=0,episodeDates=new Set();
 for(const row of rows){
  if(row.relative_humidity_2m>90){streak++;totalHigh++;longest=Math.max(longest,streak);if(streak===6){episodes++;episodeDates.add(row.time.slice(0,10))}else if(streak>6)episodeDates.add(row.time.slice(0,10))}
  else streak=0;
 }
 return {episodes,longest,totalHigh,episodeDates:[...episodeDates]};
}
function validateDay(days,date){
 const day=days.get(date);if(!day||day.size!==24)throw Error("No hay 24 registros horarios completos para "+date+".");
 const rows=[];for(let h=0;h<24;h++){const r=day.get(h);if(!r)throw Error("Falta la hora "+h+" de "+date);rows.push({...r,time:date+"T"+String(h).padStart(2,"0")+":00"})}return rows;
}
function evaluateForecast(hourly){
 const days=groupHourly(hourly),today=localDate(),rows=[];
 for(let i=1;i<=7;i++)rows.push(...validateDay(days,addDays(today,i)));
 const result=scanEpisodes(rows),daily=[];
 for(let i=1;i<=7;i++){
  const date=addDays(today,i),r=validateDay(days,date);
  daily.push({date,high:r.filter(x=>x.relative_humidity_2m>90).length,rain:r.reduce((a,x)=>a+x.precipitation,0),
   tmean:r.reduce((a,x)=>a+x.temperature_2m,0)/24,rhmean:r.reduce((a,x)=>a+x.relative_humidity_2m,0)/24,
   solar:r.reduce((a,x)=>a+x.shortwave_radiation*.0036,0),wind:r.reduce((a,x)=>a+x.wind_speed_10m,0)/24});
 }
 return {...result,daily,period:"Pronóstico de siete días completos",method:"Horas consecutivas con HR del aire a 2 m >90%; umbral exploratorio de contexto favorable citado por UC IPM."};
}
function evaluateCurrent(hourly){
 const days=groupHourly(hourly),now=localDate(),all=[];
 for(const [date,hours] of days){for(let h=0;h<24;h++){const r=hours.get(h);if(r)all.push({...r,time:date+"T"+String(h).padStart(2,"0")+":00"})}}
 const cutoff=Date.now()-24*60*60*1000,rows=all.filter(x=>new Date(x.time+":00-05:00").getTime()>=cutoff).slice(-24);
 if(rows.length!==24)throw Error("No se obtuvieron 24 horas recientes completas para el indicador.");
 const s=scanEpisodes(rows);
 return {...s,daily:[{date:now,high:s.totalHigh,rain:rows.reduce((a,x)=>a+x.precipitation,0),
  tmean:rows.reduce((a,x)=>a+x.temperature_2m,0)/rows.length,rhmean:rows.reduce((a,x)=>a+x.relative_humidity_2m,0)/rows.length,
  solar:rows.reduce((a,x)=>a+x.shortwave_radiation*.0036,0),wind:rows.reduce((a,x)=>a+x.wind_speed_10m,0)/rows.length}],
  period:"Últimas 24 horas del producto meteorológico",method:"Serie horaria de modelo meteorológico; no equivale a observación instrumental en parcela."};
}
function evaluateHistorical(hourly,start,end){
 const days=groupHourly(hourly),rows=[],daily=[];
 for(let date=start;date<=end;date=addDays(date,1)){
  const day=days.get(date);if(!day||day.size!==24)continue;
  const r=validateDay(days,date);rows.push(...r);
  daily.push({date,high:r.filter(x=>x.relative_humidity_2m>90).length,rain:r.reduce((a,x)=>a+x.precipitation,0),
   tmean:r.reduce((a,x)=>a+x.temperature_2m,0)/24,rhmean:r.reduce((a,x)=>a+x.relative_humidity_2m,0)/24,
   solar:r.reduce((a,x)=>a+x.shortwave_radiation*.0036,0),wind:r.reduce((a,x)=>a+x.wind_speed_10m,0)/24});
 }
 if(!rows.length)throw Error("El reanálisis no devolvió días completos para el periodo.");
 const s=scanEpisodes(rows);
 return {...s,daily,period:"Análisis histórico ERA5/ERA5-Land mediante Open-Meteo Archive",
  method:"Recuento exploratorio de episodios horarios HR del aire a 2 m >90% durante >=6 h consecutivas; no es humectación foliar."};
}
function apiUrl(base,coords,extra){
 const q=new URLSearchParams({latitude:String(coords.lat),longitude:String(coords.lon),timezone:"America/Lima",hourly:VARS.join(","),...extra});
 return base+"?"+q.toString();
}
async function getJson(url){
 const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),25000);
 try{const r=await fetch(url,{signal:ctl.signal,cache:"no-store"});if(!r.ok)throw Error("Proveedor meteorológico HTTP "+r.status);const j=await r.json();if(j.error)throw Error(j.reason||"Error del proveedor");return j}
 finally{clearTimeout(timer)}
}
function controlsMarkup(){
 return '<div class="oaf-ux35c-controls" id="oaf-ux35c-controls">'+
 '<h3>Configuración del escenario fitosanitario</h3>'+
 '<label>Cultivo<select id="oaf-ux35c-crop">'+CROPS.map(c=>'<option value="'+c.id+'">'+c.name+'</option>').join("")+'</select></label>'+
 '<label>Plaga o enfermedad<select id="oaf-ux35c-organism"></select></label>'+
 '<p class="oaf-ux35c-note" id="oaf-ux35c-model-note" role="status"></p>'+
 '<label>Localidad<select id="oaf-ux35c-site">'+Object.keys(SITES).map(n=>'<option value="'+n+'" '+(n==="Motupe"?"selected":"")+'>'+n+'</option>').join("")+'<option value="parcel">Mi parcela · coordenadas</option></select></label>'+
 '<div class="oaf-ux35c-coords" id="oaf-ux35c-coords" hidden><label>Latitud<input id="oaf-ux35c-lat" inputmode="decimal" placeholder="-6.15083"></label><label>Longitud<input id="oaf-ux35c-lon" inputmode="decimal" placeholder="-79.71420"></label></div>'+
 '<label>Periodo de evaluación<select id="oaf-ux35c-period"><option value="current">Condiciones actuales · últimas 24 h</option><option value="forecast" selected>Pronóstico a 7 días</option><option value="history">Análisis histórico · ERA5</option></select></label>'+
 '<div class="oaf-ux35c-history" id="oaf-ux35c-history" hidden><label>Desde<input type="date" id="oaf-ux35c-start"></label><label>Hasta<input type="date" id="oaf-ux35c-end"></label></div>'+
 '<label>Fenología del cultivo<select id="oaf-ux35c-phenology"><option value="unknown">No confirmada</option><option value="flowering">Floración</option><option value="fruit">Fructificación / cosecha</option><option value="vegetative">Desarrollo vegetativo</option></select></label>'+
 '<button type="button" id="oaf-ux35c-run" class="oaf-ux35c-run">Ejecutar / actualizar escenario</button>'+
 '<p class="oaf-ux35c-status" id="oaf-ux35c-status" role="status" aria-live="polite">Selecciona el escenario y ejecuta la consulta meteorológica.</p>'+
 '<div id="oaf-ux35c-output" class="oaf-ux35c-output" hidden></div>'+
 '<small class="oaf-ux35c-source">Meteorología: Open-Meteo Forecast / Archive. Resolución puntual del proveedor; no se extrapola a parcelas vecinas.</small>'+
 '</div>';
}
function setOrganisms(){
 const crop=$( "oaf-ux35c-crop"),organism=$("oaf-ux35c-organism"),note=$("oaf-ux35c-model-note");
 if(!crop||!organism||!note)return;
 const item=CROPS.find(c=>c.id===crop.value),available=item?.organisms||[];
 organism.replaceChildren();
 if(available.length){for(const o of available){const opt=document.createElement("option");opt.value=o.id;opt.textContent=o.name;organism.append(opt)}organism.disabled=false;
  note.textContent="Modelo disponible: indicador meteorológico exploratorio específico para "+item.name+". No equivale a diagnóstico ni riesgo confirmado.";
 }else{const opt=document.createElement("option");opt.value="";opt.textContent="Sin modelo validado disponible";organism.append(opt);organism.disabled=true;
  note.textContent="No hay todavía un modelo específico documentado y validado para este cultivo en OAF. No se asignarán umbrales genéricos ni resultados ficticios."}
}
function updatePeriod(){
 const p=$("oaf-ux35c-period");if(!$("oaf-ux35c-history"))return;
 $("oaf-ux35c-history").hidden=p.value!=="history";
 const today=localDate();$("oaf-ux35c-end").max=today;$("oaf-ux35c-start").max=today;
 if(!$("oaf-ux35c-start").value){$("oaf-ux35c-start").value=addDays(today,-30);$("oaf-ux35c-end").value=addDays(today,-1)}
}
function renderMarker(){
 const svg=$("oaf-ux29-forecast-map"),scene=window.oafUx29ScenarioApi?.get?.()?.scene;
 if(!svg||!scene)return;
 if(!state.result?.coords||!$( "oaf-ux35c-enable")?.checked){svg.querySelector("#oaf-ux35c-result-marker")?.remove();return;}
 svg.querySelector("#oaf-ux35c-result-marker")?.remove();
 const x=scene.x(state.result.coords.lon),y=scene.y(state.result.coords.lat);
 if(!Number.isFinite(x)||!Number.isFinite(y))return;
 const ns="http://www.w3.org/2000/svg",g=document.createElementNS(ns,"g");g.id="oaf-ux35c-result-marker";
 const ring=document.createElementNS(ns,"circle");ring.setAttribute("cx",x);ring.setAttribute("cy",y);ring.setAttribute("r","12");ring.setAttribute("fill","#ffffff");ring.setAttribute("fill-opacity",".85");ring.setAttribute("stroke","#234d3d");ring.setAttribute("stroke-width","2");
 const dot=document.createElementNS(ns,"circle");dot.setAttribute("cx",x);dot.setAttribute("cy",y);dot.setAttribute("r","5");dot.setAttribute("fill",state.result.favorable?"#e68a22":"#2e8b57");dot.setAttribute("stroke","#fff");dot.setAttribute("stroke-width","1.5");
 const title=document.createElementNS(ns,"title");title.textContent=state.result.site+" · "+(state.result.favorable?"Favorabilidad meteorológica detectada":"No se detectó el criterio meteorológico");g.append(ring,dot,title);svg.append(g);
}
function renderOutput(result,phenology){
 const out=$("oaf-ux35c-output"),fav=result.episodes>0;
 const label=fav?"Se detectaron episodios de favorabilidad meteorológica":"No se detectó el criterio horario en el periodo";
 const phen=phenology==="flowering"?"Se indicó floración: etapa que requiere vigilancia reforzada; la interfaz no ha verificado esta fenología en campo.":
  phenology==="fruit"?"Se indicó fructificación/cosecha: inspeccionar frutos y retirar tejidos afectados según protocolo de campo.":
  phenology==="vegetative"?"Se indicó desarrollo vegetativo: mantener vigilancia del microclima del dosel.":
  "Fenología no confirmada; la susceptibilidad del hospedante no puede ponderarse.";
 out.innerHTML='<section class="oaf-ux35c-result"><strong>'+esc(label)+'</strong><p>'+esc(result.site)+' · '+esc(result.period)+' · '+esc(result.days.length)+' día(s) completos.</p>'+
 '<dl><div><dt>Episodios HR >90% durante ≥6 h</dt><dd>'+result.episodes+'</dd></div><div><dt>Mayor racha continua</dt><dd>'+result.longest+' h</dd></div><div><dt>Horas totales HR >90%</dt><dd>'+result.totalHigh+'</dd></div></dl>'+
 '<p><b>Interpretación:</b> '+(fav?"Se identificó al menos un episodio de humedad relativa del aire compatible con un contexto meteorológico favorable descrito para Botrytis.":"No se identificó el criterio horario evaluado; esto no descarta infección ni presencia del patógeno.")+'</p>'+
 '<p>'+esc(phen)+'</p></section>'+
 '<div class="oaf-ux35c-tablewrap"><table><thead><tr><th>Fecha</th><th>HR >90%</th><th>Temp. media</th><th>HR media</th><th>Lluvia</th><th>Viento medio</th></tr></thead><tbody>'+
 result.daily.map(d=>'<tr><td>'+esc(d.date)+'</td><td>'+d.high+' h</td><td>'+fmt(d.tmean)+' °C</td><td>'+fmt(d.rhmean)+' %</td><td>'+fmt(d.rain)+' mm</td><td>'+fmt(d.wind)+' km/h</td></tr>').join("")+
 '</tbody></table></div>'+
 '<p class="oaf-ux35c-warning"><b>Alcance:</b> este resultado expresa favorabilidad meteorológica, no riesgo fitosanitario confirmado, probabilidad de infección, diagnóstico ni recomendación de aplicación. La HR a 2 m no sustituye la medición de humedad foliar. <a href="https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/" target="_blank" rel="noopener noreferrer">Referencia biológica UC IPM</a>.</p>'+
 '<p class="oaf-ux35c-provenance">Fuente: '+esc(result.source)+' · '+esc(result.modelledAt)+' · Coordenada solicitada '+fmt(result.coords.lat,5)+', '+fmt(result.coords.lon,5)+' · Celda devuelta por proveedor '+fmt(result.returned.lat,4)+', '+fmt(result.returned.lon,4)+'. '+esc(result.method)+'</p>';
 out.hidden=false;
}
async function run(){
 const crop=$("oaf-ux35c-crop").value,organism=$("oaf-ux35c-organism").value,period=$("oaf-ux35c-period").value;
 const item=CROPS.find(c=>c.id===crop),model=item?.organisms.find(o=>o.id===organism);
 if(!model){$("oaf-ux35c-status").textContent="No se ejecutó: el par cultivo-organismo no dispone de modelo configurado.";return}
 let coords,site;
 if($("oaf-ux35c-site").value==="parcel"){
  coords={lat:Number($("oaf-ux35c-lat").value),lon:Number($("oaf-ux35c-lon").value)};site="Mi parcela";
  if(!Number.isFinite(coords.lat)||!Number.isFinite(coords.lon)||coords.lat< -7.3||coords.lat> -5.1||coords.lon< -80.8||coords.lon> -79){$("oaf-ux35c-status").textContent="Coordenadas inválidas o fuera de Lambayeque.";return}
 }else{site=$("oaf-ux35c-site").value;coords=SITES[site]}
 const seq=++state.request,btn=$("oaf-ux35c-run"),status=$("oaf-ux35c-status"),out=$("oaf-ux35c-output");
 btn.disabled=true;out.hidden=true;status.textContent="Consultando datos meteorológicos reales…";
 try{
  let raw,result,source;
  if(period==="history"){
   const start=$("oaf-ux35c-start").value,end=$("oaf-ux35c-end").value;
   if(!start||!end||start>end||end>=localDate())throw Error("Selecciona un intervalo histórico válido que termine antes de hoy.");
   const span=(Date.parse(end)-Date.parse(start))/86400000+1;if(span>366)throw Error("El intervalo histórico máximo de esta consulta es 366 días.");
   raw=await getJson(apiUrl(ARCHIVE,coords,{start_date:start,end_date:end,models:"era5_land"}));
   result=evaluateHistorical(raw.hourly,start,end);source="Open-Meteo Archive · ERA5-Land";
  }else{
   raw=await getJson(apiUrl(ROOT+"/forecast",coords,{forecast_days:"8",past_days:"1"}));
   result=period==="forecast"?evaluateForecast(raw.hourly):evaluateCurrent(raw.hourly);
   source="Open-Meteo Forecast · modelo meteorológico horario";
  }
  if(seq!==state.request)return;
  result={...result,site,coords,returned:{lat:raw.latitude,lon:raw.longitude},source,modelledAt:new Date().toLocaleString("es-PE",{timeZone:"America/Lima"})};
  result.favorable=result.episodes>0;
  state.result=result;
  renderOutput(result,$("oaf-ux35c-phenology").value);
  renderMarker();
  status.textContent="Consulta terminada. Resultado disponible como favorabilidad meteorológica; no es riesgo confirmado.";
 }catch(e){if(seq===state.request){status.textContent="No se pudo calcular el escenario: "+e.message+". No se rellenaron datos faltantes.";out.hidden=true;state.result=null;$("oaf-ux29-forecast-map")?.querySelector("#oaf-ux35c-result-marker")?.remove()}}
 finally{if(seq===state.request)btn.disabled=false}
}
function init(){
 const pane=$("oaf-ux29-scenario"),tree=pane?.querySelector(".oaf-ux29-tree");if(!pane||!tree||$("oaf-ux35c-controls"))return;
 const old=tree.querySelector('[data-ux35-key="phytosanitary"]')?.closest("details");
 if(!old)return;
 const toggle=old.querySelector('[data-ux35-key="phytosanitary"]');
 if(toggle){toggle.id="oaf-ux35c-enable";const label=toggle.closest("label");const hint=label?.querySelector("small");if(hint)hint.textContent="Activa esta capa para configurar y calcular el escenario fitosanitario.";}
 old.insertAdjacentHTML("beforeend",controlsMarkup());
 const controls=$("oaf-ux35c-controls");if(controls)controls.hidden=!toggle?.checked;
 toggle?.addEventListener("change",()=>{if(controls)controls.hidden=!toggle.checked;renderMarker()});
 setOrganisms();updatePeriod();
 $("oaf-ux35c-crop").addEventListener("change",setOrganisms);
 $("oaf-ux35c-period").addEventListener("change",updatePeriod);
 $("oaf-ux35c-site").addEventListener("change",()=>{$("oaf-ux35c-coords").hidden=$("oaf-ux35c-site").value!=="parcel"});
 $("oaf-ux35c-run").addEventListener("click",run);
 $("oaf-ux35c-phenology").addEventListener("change",()=>{if(state.result)renderOutput(state.result,$("oaf-ux35c-phenology").value)});
 const original=window.oafUx35Render;
 if(typeof original==="function")window.oafUx35Render=(...args)=>{original(...args);renderMarker()};
 pane.addEventListener("change",e=>{if(e.target?.dataset?.ux35Key==="phytosanitary")renderMarker()});
 window.addEventListener("oaf:geodata",renderMarker);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
window.OAFPhytosanitaryCore={evaluateForecast,evaluateCurrent,evaluateHistorical,groupHourly,scanEpisodes};
})();