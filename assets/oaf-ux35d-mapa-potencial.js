/* OAF UX72 — Capa cartográfica de favorabilidad agroclimática a 7 días.
 * Puntos meteorológicos con coordenadas reales (no superficies/interpolaciones).
 * Se monta EXCLUSIVAMENTE en el visor C y conserva sus controles/diagnóstico.
 */
(function(){"use strict";
const NS="http://www.w3.org/2000/svg",$=id=>document.getElementById(id);
const core=()=>window.OAFClimaticPotentialCore;
const state={enabled:false,model:"botrytis",points:[],data:[],zones:[],today:null,request:0,abort:null,loading:false,ready:false,
 lastError:"",selected:null,viewObserver:null,overlayObserver:null,fetchedAt:null};
const fmt=(v,d=1)=>Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}):"—";
const localDate=()=>new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
function displayModel(){
 const crop=$("oaf-ux35c-crop")?.value,org=$("oaf-ux35c-organism")?.value;
 if(crop==="arandano"&&org==="botrytis")return "botrytis";
 if(crop==="mango"&&org==="ceratitis")return "ceratitis";
 return null
}
function scene(){return window.oafUx29ScenarioApi?.get?.()?.scene}
function textStatus(message){
 const target=$("oaf-ux35d-mapstatus");if(target)target.textContent=message;
 const general=$("oaf-ux35-mapstatus");
 if(general&&state.enabled)general.textContent=message;
}
function showPanel(){
 const pane=$("oaf-ux29-scenario"),intro=pane?.querySelector(".oaf-ux35-mapintro"),mapcol=pane?.querySelector(".oaf-ux29-mapcontent");
 if(!pane||!mapcol||!$("oaf-ux35c-controls"))return false;
 if(intro)intro.textContent="Mapa de polígonos aproximados por proximidad a una muestra meteorológica (≤28 km). NO son áreas de infección, incidencia ni probabilidad fitosanitaria.";
 if(!$("oaf-ux35d-panel")){
  const panel=document.createElement("section");
  panel.id="oaf-ux35d-panel";panel.className="oaf-ux35d-panel";
  panel.innerHTML='<div class="oaf-ux35d-heading"><strong>Mapa de condiciones potencialmente favorables · 7 días</strong>'+
   '<div class="oaf-ux35d-actions"><button id="oaf-ux35d-refresh" type="button">Actualizar mapa</button><button id="oaf-ux35d-export" type="button" disabled>Descargar puntos PDF</button><button id="oaf-ux35d-polygons-export" type="button" disabled>Descargar polígonos PDF</button></div></div>'+
   '<p id="oaf-ux35d-mapstatus" role="status" aria-live="polite">Marca la capa C para consultar la malla de puntos meteorológicos.</p>'+
   '<div id="oaf-ux35d-legend" class="oaf-ux35d-legend" hidden></div>'+
   '<div id="oaf-ux35d-point-detail" class="oaf-ux35d-point-detail" hidden></div>'+
   '<small>Fuente: Open-Meteo Forecast (temperatura y HR a 2 m), coordenadas WGS84. El contorno está simplificado; los polígonos representan cobertura meteorológica aproximada, no delimitaciones validadas de infección o cultivo.</small>';
  const mapNode=mapcol.querySelector(".oaf-ux29-scenemap");if(mapNode)mapNode.after(panel);else mapcol.append(panel);
  $("oaf-ux35d-refresh").addEventListener("click",()=>refresh(true));
  $("oaf-ux35d-export").addEventListener("click",()=>window.OAFReportPDF?.export("C","puntos"));
   $("oaf-ux35d-polygons-export").addEventListener("click",()=>window.OAFReportPDF?.export("C","poligonos"));
 }
 return true
}
function sizeMarkers(){
 const svg=$("oaf-ux29-forecast-map"),g=$("oaf-ux35d-points");if(!svg||!g)return;
 const v=(svg.getAttribute("viewBox")||"0 0 700 380").split(/[\s,]+/).map(Number);
 const scale=v.length===4&&v.every(Number.isFinite)?Math.max(.2,v[2]/700):1;
 for(const dot of g.querySelectorAll("circle[data-ux35d-point]")){
  dot.setAttribute("r",String(Math.max(1.3,6.6*scale)));
  dot.setAttribute("stroke-width",String(Math.max(.4,1.3*scale)));
 }
}
function meterValue(record){
 const i=record?.indicator;
 if(!i)return {fill:"#aeb9b4",label:"Sin datos verificables"};
 if(i.kind==="humedad_favorable"){
  if(i.episodes===0)return {fill:"#609883",label:"No se detectó el criterio"};
  if(i.episodes===1)return {fill:"#e6ad42",label:"Un episodio HR >90% ≥6 h"};
  return {fill:"#c46b3a",label:i.episodes+" episodios HR >90% ≥6 h"};
 }
 const m=state.data.filter(x=>x.indicator?.kind==="acumulacion_termica").map(x=>x.indicator.degreesDaysMin);
 const lo=Math.min(...m),hi=Math.max(...m),fraction=hi>lo?(i.degreesDaysMin-lo)/(hi-lo):.5;
 const hue=207-27*fraction,light=67-30*fraction;
 return {fill:"hsl("+hue+" 58% "+light+"%)",label:fmt(i.degreesDaysMin,1)+"–"+fmt(i.degreesDaysMax,1)+" GD (bases 9,1/8,47 °C; sin riesgo clasificado)"};
}
function onPick(point){
 state.selected=point.id;
 const el=$("oaf-ux35d-point-detail"),i=point.indicator;
 if(!el)return;
 el.hidden=false;
 const name=state.model==="botrytis"?"Arándano · Botrytis cinerea":"Mango · Ceratitis capitata";
 const info=!i?"No se pudieron comprobar todos los registros horarios: "+(point.error||"Sin datos"):
  i.kind==="humedad_favorable"?
  "Episodios de HR del aire >90% durante ≥6 h: "+i.episodes+"; mayor racha: "+i.longestStreak+" h. No es humectación foliar medida ni infección.":
  "Grados-día acumulados: "+fmt(i.degreesDaysMin,2)+" GD (base 9,1 °C) a "+fmt(i.degreesDaysMax,2)+" GD (base 8,47 °C). No hay biofix ni MTD local.";
 const lines=[point.id+" · "+name,info,
  "Coordenada consultada: "+fmt(point.lat,5)+", "+fmt(point.lon,5)+
  " · Celda devuelta: "+fmt(point.modelledLat,4)+", "+fmt(point.modelledLon,4)];
 el.replaceChildren();
 for(let j=0;j<lines.length;j++){const e=document.createElement(j===0?"strong":"p");e.textContent=lines[j];el.append(e)}
}
function legend(){
 const el=$("oaf-ux35d-legend");if(!el)return;
 el.replaceChildren();el.hidden=true;
 if(!state.data.length)return;
 const date=state.today,period=core().requiredDates(date);
 const head=document.createElement("div");
 head.textContent=state.model==="botrytis"?
  "Arándano · Botrytis · episodios de humedad relativa (NO riesgo de infección)":
  "Mango · Ceratitis · grados-día del periodo (NO riesgo de infestación)";
 el.append(head);
 const chips=state.model==="botrytis"?
  [["#609883","0 episodios detectados"],["#e6ad42","1 episodio"],["#c46b3a","2 o más episodios"],["#aeb9b4","Sin datos válidos"]]:
  [["#a9cbdf","Menor acumulación relativa"],["#35698d","Mayor acumulación relativa"],["#aeb9b4","Sin cálculo válido"]];
 for(const [color,label] of chips){const span=document.createElement("span");const dot=document.createElement("i");dot.style.background=color;span.append(dot,document.createTextNode(label));el.append(span)}
 const valid=state.data.filter(x=>x.indicator),foot=document.createElement("p");
 foot.textContent=period[0]+" al "+period.at(-1)+" · "+valid.length+" de "+state.data.length+" puntos con datos completos · consulta "+new Date().toLocaleString("es-PE",{timeZone:"America/Lima"})+
  ". Escala cromática relativa; no expresa intensidad de plagas, probabilidad o semáforo de riesgo.";
 el.append(foot);el.hidden=false
}
function paint(){
 const svg=$("oaf-ux29-forecast-map"),s=scene();
 if(!svg)return;
 svg.querySelector("#oaf-ux35d-points")?.remove();
 svg.querySelector("#oaf-ux35d-zones")?.remove();
 if(!state.enabled||!state.data.length||!s||!$("oaf-ux35c-enable")?.checked)return;
 const zones=document.createElementNS(NS,"g");zones.id="oaf-ux35d-zones";
 zones.setAttribute("aria-label","Polígonos meteorológicos aproximados, no riesgo fitosanitario validado");
 const lookup=new Map(state.data.map(p=>[p.id,p]));
 for(const z of state.zones){
  const point=lookup.get(z.pointId),coords=z.geometry?.coordinates?.[0];
  if(!point||!coords)continue;
  const props=meterValue(point),poly=document.createElementNS(NS,"polygon");
  poly.setAttribute("points",coords.map(v=>s.x(v[0]).toFixed(2)+","+s.y(v[1]).toFixed(2)).join(" "));
  poly.setAttribute("data-ux35d-zone",z.id);
  poly.setAttribute("fill",props.fill);poly.setAttribute("fill-opacity",point.indicator?".62":".20");
  poly.setAttribute("stroke","#315344");poly.setAttribute("stroke-opacity",".5");
  poly.setAttribute("stroke-width",".5");poly.setAttribute("role","button");poly.setAttribute("tabindex","0");
  poly.setAttribute("aria-label",z.id+": "+props.label+". Polígono climático aproximado");
  poly.addEventListener("pointerdown",e=>e.stopPropagation());
  poly.addEventListener("click",e=>{e.stopPropagation();onPick(point)});
  poly.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();onPick(point)}});
  const title=document.createElementNS(NS,"title");
  title.textContent=z.id+" · "+props.label+" · distancia máxima de referencia "+z.representativeDistanceKm+" km. No riesgo comprobado";
  poly.append(title);zones.append(poly);
 }
 svg.append(zones);
 const group=document.createElementNS(NS,"g");group.id="oaf-ux35d-points";
 group.setAttribute("aria-label","Puntos de muestreo meteorológico del modelo seleccionado");
 const existing=svg.querySelector("#oaf-ux35c-result-marker");
 svg.insertBefore(group,existing||null);
 for(const r of state.data){
  const x=s.x(r.lon),y=s.y(r.lat);
  if(!Number.isFinite(x)||!Number.isFinite(y))continue;
  const props=meterValue(r),point=document.createElementNS(NS,"circle");
  point.dataset.ux35dPoint=r.id;point.setAttribute("data-ux35d-point",r.id);
  point.setAttribute("cx",x);point.setAttribute("cy",y);
  point.setAttribute("r","6.6");point.setAttribute("fill",props.fill);
  point.setAttribute("stroke","#ffffff");point.setAttribute("stroke-width","1.3");
  point.setAttribute("opacity",r.indicator?"0.96":"0.68");
  point.setAttribute("role","button");point.setAttribute("tabindex","0");
  point.setAttribute("aria-label",r.id+" "+props.label);
  point.addEventListener("pointerdown",e=>e.stopPropagation());
  point.addEventListener("click",e=>{e.stopPropagation();onPick(r)});
  point.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();onPick(r)}});
  const title=document.createElementNS(NS,"title");title.textContent=r.id+" · "+props.label;point.append(title);
  group.append(point)
 }
 sizeMarkers();legend();
}
function reset(abort=true){
 state.request++;if(abort&&state.abort){state.abort.abort();state.abort=null}
 state.data=[];state.points=[];state.zones=[];state.selected=null;state.today=null;state.lastError="";state.loading=false;
 const detail=$("oaf-ux35d-point-detail");if(detail)detail.hidden=true;
 const legendEl=$("oaf-ux35d-legend");if(legendEl)legendEl.hidden=true;
 const exp=$("oaf-ux35d-export");if(exp)exp.disabled=true;
 const exportZones=$("oaf-ux35d-polygons-export");if(exportZones)exportZones.disabled=true;
 state.fetchedAt=null;paint()
}
function buildUrl(points,model){
 const params=new URLSearchParams({
  latitude:points.map(p=>p.lat).join(","),longitude:points.map(p=>p.lon).join(","),
  timezone:"America/Lima",hourly:model==="botrytis"?"relative_humidity_2m":"temperature_2m",
  forecast_days:"8",cell_selection:"land"
 });
 return "https://api.open-meteo.com/v1/forecast?"+params.toString()
}
async function refresh(force=false){
 if(!showPanel())return;
 const enable=$("oaf-ux35c-enable"),model=displayModel(),s=scene();
 state.enabled=Boolean(enable?.checked);state.model=model;
 if(!state.enabled){reset();textStatus("Capa C desactivada. No se muestran condiciones climáticas.");return}
 if(!model){reset();textStatus("Para este cultivo/organismo no hay un indicador meteorológico documentado disponible.");return}
 if(!s?.rings?.length){textStatus("Preparando contorno de Lambayeque…");return}
 const today=localDate();
 if(!force&&state.data.length&&state.model===model&&state.today===today){paint();return}
 reset();state.enabled=true;state.model=model;state.today=today;
 const seq=state.request,coreApi=core();if(!coreApi){textStatus("No se cargó el motor del mapa climático.");return}
 let points;
 try{points=coreApi.sampleGrid(s.rings,{columns:10,rows:8,max:30})}
 catch(e){textStatus("No hay un límite regional válido para muestrear: "+e.message);return}
 state.points=points;
 try{state.zones=window.OAFPotentialPolygons?.zones(s.rings,points,{step:.055,maxKm:28})||[]}
 catch(e){state.zones=[];textStatus("No se generaron polígonos interiores: "+e.message)}
 state.loading=true;
 textStatus("Consultando datos horarios reales de "+points.length+" puntos dentro del contorno regional…");
 const abort=new AbortController();state.abort=abort;
 const timer=setTimeout(()=>abort.abort(),35000);
 try{
  const res=await fetch(buildUrl(points,model),{signal:abort.signal,cache:"no-store",headers:{accept:"application/json"}});
  if(!res.ok)throw Error("Proveedor meteorológico HTTP "+res.status);
  const raw=await res.json();
  if(raw.error)throw Error(raw.reason||"El proveedor devolvió error");
  const data=coreApi.assessBatch(Array.isArray(raw)?raw:[raw],points,model,today);
  if(seq!==state.request)return;
  state.data=data;state.fetchedAt=new Date().toISOString();
  const ok=data.filter(p=>p.indicator).length;
  const providerCells=new Set(data.filter(p=>p.indicator).map(p=>p.modelledLat.toFixed(3)+","+p.modelledLon.toFixed(3)));
  if(!ok)throw Error("No se recibieron series completas y aplicables del periodo.");
  const exportBtn=$("oaf-ux35d-export");if(exportBtn)exportBtn.disabled=false;
  const ez=$("oaf-ux35d-polygons-export");if(ez)ez.disabled=!state.zones.length;
  paint();textStatus(
   "Capa climática consultada: "+ok+" de "+points.length+" puntos válidos, "+providerCells.size+
   " celdas meteorológicas devueltas · "+coreApi.requiredDates(today)[0]+" al "+coreApi.requiredDates(today).at(-1)+
   ". "+state.zones.length+" polígonos climáticos aproximados de proximidad, NO áreas de infección. Selecciona un polígono para sus valores."
  )
 }catch(e){
  if(seq!==state.request)return;
  state.data=[];state.lastError=String(e.message||e);paint();
  textStatus("No se pudo mostrar el mapa climático: "+state.lastError+". No se dibujan datos ficticios.")
 }finally{
  clearTimeout(timer);
  if(seq===state.request){state.loading=false;state.abort=null}
 }
}
function toGeoJSON(){
 const features=state.data.map(p=>{
  const i=p.indicator;
  return {type:"Feature",id:p.id,geometry:{type:"Point",coordinates:[p.lon,p.lat]},
   properties:{
    id:p.id,cultivo:state.model==="botrytis"?"Arándano":"Mango",
    organismo:state.model==="botrytis"?"Botrytis cinerea":"Ceratitis capitata",
    indicador:state.model,modelo_estado:"teorico_sin_calibracion_local",
    fechas_periodo:i?.dates||core()?.requiredDates(state.today)||null,
    episodios_hr_sobre_90_6h:i?.kind==="humedad_favorable"?i.episodes:null,
    horas_hr_sobre_90:i?.kind==="humedad_favorable"?i.hoursOver90:null,
    grados_dia_base_9_1:i?.kind==="acumulacion_termica"?i.degreesDaysMin:null,
    grados_dia_base_8_47:i?.kind==="acumulacion_termica"?i.degreesDaysMax:null,
    datos_completos:Boolean(i),error:p.error||null,
    modelled_lat:p.modelledLat??null,modelled_lon:p.modelledLon??null,
    fuente_meteorologica:"https://open-meteo.com/en/docs",fecha_consulta:state.fetchedAt,
    es_riesgo_calibrado:false,
    observacion:"Punto meteorológico, no distribución del cultivo, abundancia ni zona continua de riesgo."
   }};
 });
 return {type:"FeatureCollection",name:"OAF_Lambayeque_favorabilidad_climatica_no_riesgo",
  metadata:{version:"ux72",source:"Open-Meteo Forecast",model:state.model,generated:state.fetchedAt,
   reference:core()?.MODEL[state.model]?.reference,
   boundary:"datos/zonificacion_8n/limite_lambayeque_referencial.geojson (simplificado, no oficial)",
   disclaimer:"Puntos de muestreo. Sin interpolación, distribución de hospedantes, incidencia ni calibración local."},
  features};
}
function polygonsGeoJSON(){
 const src=toGeoJSON(),byId=new Map(src.features.map(f=>[f.id,f.properties]));
 return {type:"FeatureCollection",name:"OAF_poligonos_potencial_climatico_NO_RIESGO",
  metadata:{...src.metadata,version:"ux73",
   method:"Teselas geométricas completamente interiores al contorno simplificado, asignadas al punto meteorológico más próximo (≤28 km). Representatividad no calibrada.",
   disclaimer:"No son áreas de incidencia, presencia, infección o riesgo fitosanitario validado."},
  features:state.zones.map(z=>({type:"Feature",id:z.id,geometry:z.geometry,
   properties:{...byId.get(z.pointId),zone_id:z.id,point_id:z.pointId,
    distancia_representativa_km:z.representativeDistanceKm,
    metodo:"vecino_mas_cercano_sin_validacion_espacial",
    es_riesgo_calibrado:false,probabilidad_infeccion:null,incidencia:null}}))};
}
function exportPolygons(){
 if(!state.zones.length||!state.today)return;
 const blob=new Blob([JSON.stringify(polygonsGeoJSON(),null,2)],{type:"application/geo+json"});
 const url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="OAF_poligonos_potencial_"+state.model+"_"+state.today+".geojson";
 document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function exportGeoJSON(){
 if(!state.data.length||!state.today)return;
 const file=new Blob([JSON.stringify(toGeoJSON(),null,2)],{type:"application/geo+json"});
 const url=URL.createObjectURL(file),a=document.createElement("a");
 a.href=url;a.download="OAF_potencial_climatico_"+state.model+"_"+state.today+".geojson";
 document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function init(){
 if(state.ready||!showPanel())return;
 state.ready=true;
 const toggle=$("oaf-ux35c-enable"),crop=$("oaf-ux35c-crop"),org=$("oaf-ux35c-organism");
 if(!toggle||!crop||!org)return;
 toggle.addEventListener("change",()=>refresh(true));
 crop.addEventListener("change",()=>refresh(true));
 org.addEventListener("change",()=>refresh(true));
 document.addEventListener("oaf:scenario-map-redrawn",()=>{
  paint();
  if(toggle.checked&&!state.data.length&&!state.loading&&!state.lastError)refresh()
 });
 const svg=$("oaf-ux29-forecast-map");
 if(svg&&!state.viewObserver){
  state.viewObserver=new MutationObserver(()=>sizeMarkers());
  state.viewObserver.observe(svg,{attributes:true,attributeFilter:["viewBox"]})
 }
 if(svg&&!state.overlayObserver){
  state.overlayObserver=new MutationObserver(()=>{
   if(state.enabled&&state.data.length&&(!svg.querySelector("#oaf-ux35d-points")||!svg.querySelector("#oaf-ux35d-zones")))paint()
  });
  state.overlayObserver.observe(svg,{childList:true})
 }
 window.addEventListener("oaf:geodata",()=>{
  paint();
  if(toggle.checked&&!state.data.length&&!state.loading&&!state.lastError)refresh()
 });
 if(toggle.checked)refresh(true)
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
window.OAFPotentialLayer={refresh:()=>refresh(true),toGeoJSON,polygonsGeoJSON,getState:()=>({enabled:state.enabled,model:state.model,total:state.data.length,polygons:state.zones.length,valid:state.data.filter(p=>p.indicator).length,error:state.lastError}),paint};
})();
