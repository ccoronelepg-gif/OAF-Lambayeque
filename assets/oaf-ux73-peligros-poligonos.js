/* OAF UX73 · Peligros A: cartografía climatológica no oficial mediante
 * teselas de proximidad al punto meteorológico más cercano.
 * Flood: la fuente oficial CENEPRED se dibuja en UX30 y NO se modifica.
 * Rain/drought/heat: indicadores meteorológicos no equivalen a amenazas oficiales.
 */
(function(){"use strict";
const $=id=>document.getElementById(id),NS="http://www.w3.org/2000/svg";
const keys=["rainIntense","drought","heat","flood"],climateKeys=["rainIntense","drought","heat"];
const names={rainIntense:"Precipitación diaria máxima pronosticada",drought:"Lluvia acumulada 30 días anteriores",heat:"Temperatura máxima pronosticada",flood:"Lluvia pronosticada como contexto de inundación (NO susceptibilidad oficial)"};
const state={ready:false,loading:false,request:0,abort:null,points:[],zones:[],data:[],
 latest:null,mode:"rainIntense",today:null,error:"",timer:null,observer:null};
const context=()=>window.oafUx30Context?.();
const fmt=(n,d=1)=>Number.isFinite(n)?n.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}):"—";
const localDate=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
function activeKeys(){return climateKeys.filter(k=>document.querySelector('[data-ux30-layer="'+k+'"]')?.checked)}
function mode(){return activeKeys().at(-1)||(document.querySelector('[data-ux30-layer="flood"]')?.checked?"flood":null)}
function status(t){const e=$("oaf-ux73a-status");if(e)e.textContent=t}
function renderPanel(){
 const pane=$("oaf-ux29-territory"),container=pane?.querySelector(".oaf-ux29-mapcontent");if(!container)return false;
 if(!$("oaf-ux73a-panel")){
  const div=document.createElement("section");div.id="oaf-ux73a-panel";div.className="oaf-ux73a-panel";
  div.innerHTML='<strong>Capas A · verificación y leyenda</strong>'+
   '<div class="oaf-ux74-actions"><button id="oaf-ux74a-points" type="button" disabled>Descargar puntos PDF</button> <button id="oaf-ux74a-polygons" type="button" disabled>Descargar polígonos PDF</button></div>'+
   '<p id="oaf-ux73a-status" role="status">Activa una capa de lluvias, sequía o temperatura para mostrar los indicadores meteorológicos.</p>'+
   '<div id="oaf-ux73a-legend" hidden></div>'+
   '<div id="oaf-ux73a-selected" hidden></div>'+
   '<p>Cartografía CENEPRED 2021: <a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024" target="_blank" rel="noopener noreferrer">consultar susceptibilidad oficial a inundaciones</a>. Lluvias, sequía y temperatura: <a href="https://open-meteo.com/en/docs" target="_blank" rel="noopener noreferrer">Open-Meteo</a>, polígonos de representatividad aproximada de modelos meteorológicos. Las clases indican magnitudes, no peligros validados por SENAMHI.</p>';
  container.append(div);
  $("oaf-ux74a-points").addEventListener("click",()=>window.OAFReportPDF?.export("A","puntos"));
  $("oaf-ux74a-polygons").addEventListener("click",()=>window.OAFReportPDF?.export("A","poligonos"));
 }
 return true;
}
function clear(){const p=$("oaf-ux74a-points"),z=$("oaf-ux74a-polygons");if(p)p.disabled=true;if(z)z.disabled=true;state.request++;if(state.abort){state.abort.abort();state.abort=null}state.loading=false;state.data=[];state.zones=[];state.error="";
 const map=$("oaf-ux24-region-map");map?.querySelector("#oaf-ux73a-zones")?.remove();
 const legend=$("oaf-ux73a-legend");if(legend){legend.hidden=true;legend.replaceChildren()}
 const details=$("oaf-ux73a-selected");if(details)details.hidden=true;
}
function scheme(key,row){
 if(!row)return{color:"#b5c1bf",label:"Sin serie válida"};
 const value=row.value;
 if(key==="rainIntense"||key==="flood"){
  if(value<1)return{color:"#a3c7b9",label:"Menos de 1 mm/24 h"};
  if(value<10)return{color:"#7ab3d4",label:"1–10 mm/24 h"};
  if(value<30)return{color:"#2e84b8",label:"10–30 mm/24 h"};
  return{color:"#15517f",label:"≥30 mm/24 h"};
 }
 if(key==="drought"){
  if(value<10)return{color:"#bc9352",label:"Menos de 10 mm en 30 días"};
  if(value<30)return{color:"#deb975",label:"10–30 mm en 30 días"};
  if(value<75)return{color:"#b6bd92",label:"30–75 mm en 30 días"};
  return{color:"#5c9fa5",label:"≥75 mm en 30 días"};
 }
 if(value<25)return{color:"#83b6c9",label:"Menos de 25 °C"};
 if(value<30)return{color:"#f0c76f",label:"25–30 °C"};
 if(value<35)return{color:"#eb964c",label:"30–35 °C"};
 return{color:"#d45235",label:"≥35 °C"}
}
function evaluateRow(raw,key,today){
 const days=raw?.daily;
 if(!Array.isArray(days?.time)||!Array.isArray(days?.precipitation_sum)||!Array.isArray(days?.temperature_2m_max)||
  days.time.length!==days.precipitation_sum.length||days.time.length!==days.temperature_2m_max.length)
  throw Error("Series meteorológicas diarias incompletas");
 const ix=days.time.indexOf(today);if(ix<30||ix+7>=days.time.length)throw Error("Periodo de 30 días previos o 7 días futuros incompleto");
 for(let i=1;i<days.time.length;i++){
  const a=Date.parse(days.time[i-1]+"T12:00:00Z"),b=Date.parse(days.time[i]+"T12:00:00Z");
  if(!Number.isFinite(a)||b-a!==86400000)throw Error("Fechas no consecutivas");
 }
 const valid=(field,start,end)=>{
  const arr=days[field].slice(start,end);
  if(arr.length!==end-start||arr.some(x=>typeof x!=="number"||!Number.isFinite(x)))throw Error("Día sin datos: "+field);
  return arr
 };
 const rain=valid("precipitation_sum",ix+1,ix+8),
  past=valid("precipitation_sum",ix-30,ix),
  heat=valid("temperature_2m_max",ix+1,ix+8);
 if([...rain,...past].some(x=>x<0||x>700)||heat.some(x=>x< -30||x>55))
  throw Error("Valores meteorológicos fuera de rango");
 const maxRain=Math.max(...rain),total7=rain.reduce((a,b)=>a+b,0),past30=past.reduce((a,b)=>a+b,0),maxTemp=Math.max(...heat);
 return {value:key==="rainIntense"||key==="flood"?maxRain:key==="drought"?past30:maxTemp,
  maxRain,maxTemp,total7,past30,dryDays:past.filter(x=>x<1).length,
  dateFrom:key==="drought"?days.time[ix-30]:days.time[ix+1],
  dateTo:key==="drought"?days.time[ix-1]:days.time[ix+7],
  modelledLat:raw.latitude,modelledLon:raw.longitude};
}
function paint(){
 const scene=context()?.scene,map=scene?.svg||$("oaf-ux24-region-map");
 if(!map)return;
 map.querySelector("#oaf-ux73a-zones")?.remove();
 const key=mode();if(!key||!scene||!state.data.length||!state.zones.length)return;
 const group=document.createElementNS(NS,"g");group.id="oaf-ux73a-zones";
 group.setAttribute("aria-label",names[key]+" · polígonos de representación aproximada");
 const matches=new Map(state.data.map(x=>[x.id,x]));
 for(const zone of state.zones){
  const p=matches.get(zone.pointId),value=p?.indicators?.[key],geo=zone.geometry?.coordinates?.[0];
  if(!p||!geo)continue;
  const v=scheme(key,value),element=document.createElementNS(NS,"polygon");
  element.setAttribute("points",geo.map(pair=>scene.x(pair[0]).toFixed(2)+","+scene.y(pair[1]).toFixed(2)).join(" "));
  element.setAttribute("data-ux73a-zone",zone.id);
  element.setAttribute("fill",v.color);element.setAttribute("fill-opacity",value?(key==="flood"?".32":".55"):".16");
  element.setAttribute("stroke","#4c665e");element.setAttribute("stroke-opacity",".5");element.setAttribute("stroke-width",".55");
  element.setAttribute("role","button");element.setAttribute("tabindex","0");
  element.setAttribute("aria-label",zone.id+": "+v.label+". Estimación meteorológica, no peligro oficial");
  element.addEventListener("pointerdown",e=>e.stopPropagation());
  const select=()=>{
   const panel=$("oaf-ux73a-selected");if(!panel)return;
   panel.hidden=false;panel.textContent=zone.id+" · "+names[key]+" · "+v.label+". "+(value?
    "Punto: "+p.id+" (WGS84 "+fmt(p.lat,5)+", "+fmt(p.lon,5)+"), celda modelada "+fmt(value.modelledLat,4)+", "+fmt(value.modelledLon,4)+
    ". Periodo: "+value.dateFrom+" a "+value.dateTo+". Distancia máxima de asociación "+zone.representativeDistanceKm+" km.":"Datos incompletos.")+
    " No es índice SENAMHI de sequía, alerta de peligro, ni probabilidad de daño.";
  };
  element.addEventListener("click",e=>{e.stopPropagation();select()});
  element.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select()}});
  const tooltip=document.createElementNS(NS,"title");tooltip.textContent=zone.id+" · "+v.label;
  element.append(tooltip);group.append(element);
 }
 const front=map.querySelector("g.oaf-ux30-layer:last-of-type");
 if(front&&front.parentNode===map)map.insertBefore(group,front);
 else map.append(group);
 legend();
}
function legend(){
 const key=mode(),box=$("oaf-ux73a-legend");if(!box||!key)return;
 box.replaceChildren();box.hidden=false;
 const title=document.createElement("strong");title.textContent=names[key]+" · magnitud meteorológica (NO riesgo oficial)";box.append(title);
 const vals=(key==="rainIntense"||key==="flood")?[0,2,15,45]:key==="drought"?[0,18,40,90]:[20,27,32,37];
 for(const x of vals){
  const chip=document.createElement("span"),mark=document.createElement("i");
  const style=scheme(key,{value:x});mark.style.background=style.color;chip.append(mark,document.createTextNode(style.label));box.append(chip);
 }
 const small=document.createElement("p");
 small.textContent=key==="flood"?"Estos polígonos muestran SOLO lluvia pronosticada como contexto. El raster oficial CENEPRED 2021 es una capa independiente; sin él NO se conoce susceptibilidad ni riesgo de inundación.":
 "Teselas de proximidad ≤28 km; contorno aproximado. Escasa lluvia en 30 días NO es diagnóstico de sequía sin climatología de referencia." ;
 box.append(small);
}
function getToday(){return localDate()}
function url(points){
 const p=new URLSearchParams({
  latitude:points.map(x=>x.lat).join(","),longitude:points.map(x=>x.lon).join(","),
  daily:"precipitation_sum,temperature_2m_max",past_days:"30",forecast_days:"8",timezone:"America/Lima",cell_selection:"land"
 });return "https://api.open-meteo.com/v1/forecast?"+p
}
async function refresh(force=false){
 if(!renderPanel())return;
 const key=mode();
 if(!key){clear();status("No hay indicador de lluvia, déficit o temperatura seleccionado. La susceptibilidad de inundación CENEPRED funciona como capa independiente.");return}
 const today=getToday();
 if(!force&&state.data.length&&state.today===today){state.mode=key;paint();return}
 clear();state.mode=key;state.today=today;
 const current=state.request,core=window.OAFClimaticPotentialCore,poly=window.OAFPotentialPolygons;
 if(!core||!poly){status("Motor GIS incompleto. Revisa conexión del módulo.");return}
 state.loading=true;status("Consultando precipitación y temperatura de 30 puntos georreferenciados…");
 const controller=new AbortController();state.abort=controller;const timer=setTimeout(()=>controller.abort(),40000);
 try{
  const boundary=await fetch("datos/zonificacion_8n/limite_lambayeque_referencial.geojson",{signal:controller.signal,cache:"force-cache"});
  if(!boundary.ok)throw Error("Contorno regional HTTP "+boundary.status);
  const geo=await boundary.json();
  const rings=geo.features?.flatMap(f=>f.geometry?.type==="Polygon"?[f.geometry.coordinates[0]]:[])||[];
  if(!rings.length)throw Error("Límite geográfico sin geometría");
  const points=core.sampleGrid(rings,{columns:10,rows:8,max:30}),
   zones=poly.zones(rings,points,{step:.055,maxKm:28});
  const res=await fetch(url(points),{signal:controller.signal,cache:"no-store"});
  if(!res.ok)throw Error("Open-Meteo HTTP "+res.status);
  const raw=await res.json();
  if(!Array.isArray(raw)||raw.length!==points.length)throw Error("Respuesta multicelda desalineada");
  const data=points.map((p,i)=>{
   const byKey={},item=raw[i];
   for(const k of keys){try{byKey[k]=evaluateRow(item,k,today)}catch(e){byKey[k]=null}}
   return {...p,indicators:byKey}
  });
  if(current!==state.request)return;
  state.points=points;state.zones=zones;state.data=data;state.latest=new Date().toISOString();
  state.error="";paint();
  const bp=$("oaf-ux74a-points"),bz=$("oaf-ux74a-polygons");if(bp)bp.disabled=!data.length;if(bz)bz.disabled=!zones.length;
  const valid=data.filter(x=>x.indicators[key]).length;
  status(key+" · "+valid+" de "+points.length+" muestras completas; "+zones.length+" polígonos climáticos aproximados. Fuente: Open-Meteo; consulta "+new Date().toLocaleString("es-PE",{timeZone:"America/Lima"})+". No sustituye mapas oficiales SENAMHI/CENEPRED.");
 }catch(e){
  if(current!==state.request)return;
  state.error=e.message||String(e);state.data=[];state.zones=[];paint();
  status("No se pudo consultar este indicador: "+state.error+". Sin valores ficticios.");
 }finally{clearTimeout(timer);if(current===state.request){state.loading=false;state.abort=null}}
}
function setup(){
 if(state.ready||!renderPanel()||!$("oaf-ux30-layer-tree"))return;
 state.ready=true;
 const pane=$("oaf-ux29-territory");
 pane.addEventListener("change",e=>{
  const key=e.target?.dataset?.ux30Layer;
  if(!key)return;
  if(climateKeys.includes(key)){
   if(e.target.checked){
    // Una sola variable climática poligonal a la vez; mantener inundación independiente.
    for(const other of climateKeys)if(other!==key){const el=pane.querySelector('[data-ux30-layer="'+other+'"]');if(el?.checked){el.checked=false;el.dispatchEvent(new Event("change",{bubbles:true}))}}
    state.mode=key;refresh();
   }else if(!mode()){clear();status("Indicadores meteorológicos desactivados.")}
   else refresh();
  }else if(key==="flood"){
   refresh();
  }
 });
 document.addEventListener("oaf:territory-map-redrawn",()=>{
  if(state.data.length&&mode())paint();
  else if(mode()&&!state.loading&&!state.error)refresh();
 });
 const svg=$("oaf-ux24-region-map");
 if(svg){
  state.observer=new MutationObserver(()=>{
   if(state.data.length&&mode()&&!svg.querySelector("#oaf-ux73a-zones"))paint()
  });
  state.observer.observe(svg,{childList:true});
 }
 function pointsGeoJSON(){
 const key=mode(),features=state.data.map(p=>{
  const i=p.indicators?.[key]||null;
  return {type:"Feature",id:p.id,geometry:{type:"Point",coordinates:[p.lon,p.lat]},properties:{
   id:p.id,variable:key,valor:i?.value??null,unidad:key==="heat"?"°C":key==="drought"?"mm/30d":"mm/24h",
   periodo_inicio:i?.dateFrom||null,periodo_fin:i?.dateTo||null,
   lluvia_maxima_mm:i?.maxRain??null,temperatura_max_c:i?.maxTemp??null,
   lluvia_total_7d_mm:i?.total7??null,precipitacion_30d_mm:i?.past30??null,
   celda_modelada_lat:i?.modelledLat??null,celda_modelada_lon:i?.modelledLon??null,
   datos_completos:Boolean(i),fuente:"Open-Meteo Forecast",es_peligro_oficial:false,
   observacion:"Muestra meteorologica; no verifica amenaza oficial ni afectacion agricola."}};
 });
 return {type:"FeatureCollection",metadata:{model:key,generated:state.latest||new Date().toISOString(),
  source:"Open-Meteo Forecast",method:"muestreo puntual modelado; no amenaza oficial",
  disclaimer:"NO susceptibilidad CENEPRED, sequia SPI ni ola de calor oficial."},features};
}
function polygonsGeoJSON(){
 const source=pointsGeoJSON(),byId=new Map(source.features.map(p=>[p.id,p.properties]));
 return {type:"FeatureCollection",metadata:{...source.metadata,method:"Celdas interiores asignadas al vecino mas cercano <=28 km; sin validacion espacial."},
 features:state.zones.map(z=>({type:"Feature",id:z.id,geometry:z.geometry,properties:{
  ...(byId.get(z.pointId)||{}),id:z.id,zone_id:z.id,point_id:z.pointId,
  distancia_representativa_km:z.representativeDistanceKm,
  geometria_aproximada:true,es_peligro_oficial:false
 }}))};
}
 window.OAFTerritoryClimate={refresh:()=>refresh(true),evaluateRow,toGeoJSON:pointsGeoJSON,polygonsGeoJSON,getState:()=>({mode:mode(),zones:state.zones.length,points:state.points.length,error:state.error})};
 if(mode())refresh()
}
function init(){if(setup())return;let tries=0;const tick=()=>{setup();if(!state.ready&&++tries<20)setTimeout(tick,350)};tick()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
window.OAFTerritoryClimateCore={evaluateRow};
})();
