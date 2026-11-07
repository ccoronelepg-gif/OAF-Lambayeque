/* OAF UX72 — Capa cartográfica de favorabilidad agroclimática a 7 días.
 * Puntos meteorológicos con coordenadas reales (no superficies/interpolaciones).
 * Se monta EXCLUSIVAMENTE en el visor C y conserva sus controles/diagnóstico.
 */
(function(){"use strict";
const NS="http://www.w3.org/2000/svg",$=id=>document.getElementById(id);
const core=()=>window.OAFClimaticPotentialCore;
const state={enabled:false,model:"botrytis",points:[],data:[],today:null,request:0,abort:null,loading:false,ready:false,
 lastError:"",selected:null,viewObserver:null};
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
 if(intro)intro.textContent="Mapa de puntos meteorológicos consultados. Los colores indican condiciones climáticas, NO presencia, incidencia ni riesgo calibrado. El contorno regional es referencial.";
 if(!$("oaf-ux35d-panel")){
  const panel=document.createElement("section");
  panel.id="oaf-ux35d-panel";panel.className="oaf-ux35d-panel";
  panel.innerHTML='<div class="oaf-ux35d-heading"><strong>Mapa de condiciones potencialmente favorables · 7 días</strong>'+
   '<button id="oaf-ux35d-refresh" type="button">Actualizar mapa</button></div>'+
   '<p id="oaf-ux35d-mapstatus" role="status" aria-live="polite">Marca la capa C para consultar la malla de puntos meteorológicos.</p>'+
   '<div id="oaf-ux35d-legend" class="oaf-ux35d-legend" hidden></div>'+
   '<div id="oaf-ux35d-point-detail" class="oaf-ux35d-point-detail" hidden></div>'+
   '<small>Fuente: Open-Meteo Forecast (temperatura y HR a 2 m), coordenadas WGS84. El contorno está simplificado; los puntos NO son parcelas ni polígonos de infección. Leyenda válida solo para el modelo seleccionado.</small>';
  const mapNode=mapcol.querySelector(".oaf-ux29-scenemap");if(mapNode)mapNode.after(panel);else mapcol.append(panel);
  $("oaf-ux35d-refresh").addEventListener("click",()=>refresh(true));
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
 if(!state.enabled||!state.data.length||!s||!$("oaf-ux35c-enable")?.checked)return;
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
  point.addEventListener("click",e=>{e.stopPropagation();onPick(r)});
  point.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();onPick(r)}});
  const title=document.createElementNS(NS,"title");title.textContent=r.id+" · "+props.label;point.append(title);
  group.append(point)
 }
 sizeMarkers();legend();
}
function reset(abort=true){
 state.request++;if(abort&&state.abort){state.abort.abort();state.abort=null}
 state.data=[];state.points=[];state.selected=null;state.today=null;state.lastError="";state.loading=false;
 const detail=$("oaf-ux35d-point-detail");if(detail)detail.hidden=true;
 const legendEl=$("oaf-ux35d-legend");if(legendEl)legendEl.hidden=true;
 paint()
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
 state.points=points;state.loading=true;
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
  state.data=data;
  const ok=data.filter(p=>p.indicator).length;
  const providerCells=new Set(data.filter(p=>p.indicator).map(p=>p.modelledLat.toFixed(3)+","+p.modelledLon.toFixed(3)));
  if(!ok)throw Error("No se recibieron series completas y aplicables del periodo.");
  paint();textStatus(
   "Capa climática consultada: "+ok+" de "+points.length+" puntos válidos, "+providerCells.size+
   " celdas meteorológicas devueltas · "+coreApi.requiredDates(today)[0]+" al "+coreApi.requiredDates(today).at(-1)+
   ". Puntos de muestra, NO superficies continuas de riesgo. Selecciona un punto para sus valores."
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
 if(toggle.checked)refresh(true)
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
window.OAFPotentialLayer={refresh:()=>refresh(true),getState:()=>({enabled:state.enabled,model:state.model,total:state.data.length,valid:state.data.filter(p=>p.indicator).length,error:state.lastError}),paint};
})();
