/* OAF Lambayeque UX35 · Escenarios agroclimáticos multicapa.
 * Un visor, árbol de selección, cartografía territorial compartida, antecedentes
 * 1983/1998/2017/2023, lluvia 7 días, ENFEN estacional, empresas OSM y diagnóstico.
 * NO ES un pronóstico de caudales ni polígonos futuros de inundación.
 */
(function(){"use strict";
const $=id=>document.getElementById(id);
const E=(name,cls)=>{const a=document.createElement(name);if(cls)a.className=cls;return a};
const SVG=(name,props={})=>{const a=document.createElementNS("http://www.w3.org/2000/svg",name);
 Object.entries(props).forEach(([k,v])=>a.setAttribute(k,String(v)));return a};
const CEN="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer";
const SIG="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer";
const MINAM="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
const MTC="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer";
const WMS="https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms";
const HEAT_WMS="g_01_06:01_06_001_03_001_512_0000_00_00";
const COMPANIES="datos/riesgos_ux35/ubicaciones_agroindustriales_referenciales.geojson";
const YEARS=[1983,1993,1998,2007,2017,2023];
const FALLBACK_PAGES={
 old2017:"https://sigrid.cenepred.gob.pe/sigridv3/documento/16310",
 climate:"https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-19-2026/",
 senamhi:"https://www.senamhi.gob.pe/"
};
const addKeys=[
 ["phytosanitary","C. Riesgo agroclimático fitosanitario","Pendiente de conexión: todavía no existe una capa geoespacial validada que integre cultivo, organismo perjudicial y condiciones agroclimáticas. No se dibujan polígonos ni puntos simulados."]
];
const extra=new Map(addKeys.map(([id,name,meaning])=>[id,{name,meaning}]));
const state={
 on:{phytosanitary:false},territorial:{},
 year:2017,days:7,threshold:40,
 comp:[],companyStatus:"pendiente",
 history:new Map(),historyStatus:"pendiente",historyError:"",historyRequested:new Set(),
 histLocations:[],loaded:false,active:null,ready:false,current:[],
 zoomObserver:null,selectionName:"Todo Lambayeque",scene:null
};
const stations=[
 {name:"Chiclayo",lat:-6.7714,lon:-79.8409},{name:"Jayanca",lat:-6.39278,lon:-79.8228},
 {name:"Motupe",lat:-6.15083,lon:-79.7142},{name:"Olmos",lat:-5.98825,lon:-79.74723}
];
const enabled=k=>!!(state.on[k]??state.territorial[k]);
function activate(){
 const pane=$("oaf-ux29-scenario");if(!pane||pane.dataset.ux35Active==="true")return;
 pane.dataset.ux35Active="true";
 const root=$("oaf-escenarios-riesgo-agroclimatico");root?.classList.add("oaf-ux35-only-visor");
 const intro=pane.querySelector(".oaf-ux29-top");
 if(intro)intro.innerHTML='<span class="oaf-ux29-kicker">OAF-LAMBAYEQUE · ESCENARIOS DE RIESGO AGROCLIMÁTICO</span>'+
  '<h2>Visor de escenarios de riesgo agroclimático</h2>'+
  '<p>Este visor conserva un único módulo temático para representar el riesgo fitosanitario por cultivo y organismo perjudicial. La conexión espacial está pendiente de validación.</p>';
 const maphead=pane.querySelector(".oaf-ux29-maphead");
 if(maphead?.querySelector("strong"))maphead.querySelector("strong").textContent="Riesgo agroclimático fitosanitario · Lambayeque";
 const tree=pane.querySelector(".oaf-ux29-tree");
 if(tree){tree.replaceChildren();buildTree(tree)}
 const map=pane.querySelector(".oaf-ux29-mapcontent");
 if(map)map.innerHTML='<div class="oaf-ux35-mapintro">La única capa temática de esta subpestaña es el riesgo agroclimático fitosanitario. Su representación espacial se habilitará cuando exista una fuente geográfica validada.</div>'+
 '<div class="oaf-ux29-scenemap"><svg id="oaf-ux29-forecast-map" viewBox="0 0 700 380" role="img" aria-label="Mapa referencial de Lambayeque para el módulo de riesgo agroclimático fitosanitario"></svg>'+
 '<p class="oaf-ux29-mapcaption">Contorno regional de referencia. No se representan zonas, puntos ni niveles de riesgo fitosanitario mientras la capa esté pendiente de conexión.</p></div>'+
 '<div id="oaf-ux35-mapstatus" role="status" class="oaf-ux35-mapstatus">Riesgo agroclimático fitosanitario · pendiente de conexión.</div>';
 pane.addEventListener("change",handleChange);
 pane.addEventListener("click",handleClick);
 const svg=$("oaf-ux29-forecast-map");
 if(svg){
  state.zoomObserver=new MutationObserver(()=>applyZoomStyles(svg));
  state.zoomObserver.observe(svg,{attributes:true,attributeFilter:["viewBox"]});
  navigation(svg);
 }
 window.addEventListener("oaf:geodata",()=>{if(state.ready)render()});
 meta();
}
function group(parent,title,open){
 const d=E("details","oaf-ux35-group");d.open=!!open;const t=E("summary");t.textContent=title;d.append(t);parent.append(d);return d;
}
function check(parent,key,name,checked,small){
 const lab=E("label","oaf-ux35-check");
 const input=E("input");input.type="checkbox";input.dataset.ux35Key=key;input.checked=!!checked;
 const span=E("span");span.textContent=name;
 lab.append(input,span);if(small){const hint=E("small");hint.textContent=small;lab.append(hint)}
 parent.append(lab);
}
function field(parent,label,id,choices,value){
 const container=E("label","oaf-ux35-field");container.textContent=label;
 const select=E("select");select.id=id;
 choices.forEach(([v,t])=>{const o=E("option");o.value=String(v);o.textContent=t;select.append(o)});
 select.value=String(value);container.append(select);parent.append(container);
}
function buildTree(tree){
 const group=E("details","oaf-ux35-group");group.open=true;
 const title=E("summary");title.textContent="C. Riesgo agroclimático fitosanitario";group.append(title);
 const lab=E("label","oaf-ux35-check"),input=E("input");input.type="checkbox";
 input.dataset.ux35Key="phytosanitary";input.checked=false;
 const span=E("span");span.textContent="Riesgo agroclimático fitosanitario";
 const hint=E("small");hint.textContent="Pendiente de conexión · no existe todavía una superficie espacial validada por cultivo y organismo perjudicial.";
 lab.append(input,span,hint);group.append(lab);tree.append(group);
}
function attachTerritoryFilters(){
 for(const key of ["prov","dist","basin"]){
  const target=$("oaf-ux26-"+key),mirror=$("oaf-ux35-"+key);
  if(!target||!mirror)continue;
  const sync=()=>{
   const selected=mirror.value;
   mirror.replaceChildren();
   for(const option of target.options){const o=option.cloneNode(true);mirror.append(o)}
   mirror.value=target.value;mirror.disabled=target.disabled;
  };
  sync();const observer=new MutationObserver(sync);
  observer.observe(target,{childList:true,attributes:true,subtree:true});
  target.addEventListener("change",()=>{sync();requestAnimationFrame(render)});
 }
}
function navigation(svg){
 // ViewBox-based navigation, no distortion of map geometry or enlarged markers.
 let pointer=null;
 const bounds=()=>{const a=(svg.getAttribute("viewBox")||"0 0 700 380").split(/[\s,]+/).map(Number);
  return a.length===4&&a.every(Number.isFinite)?a:[0,0,700,380]};
 const set=(x,y,w,h)=>{
  const nw=Math.min(700,Math.max(80,w)),nh=Math.min(380,Math.max(80*380/700,h));
  const xx=Math.max(0,Math.min(700-nw,x)),yy=Math.max(0,Math.min(380-nh,y));
  svg.setAttribute("viewBox",[xx,yy,nw,nh].map(q=>q.toFixed(2)).join(" "));
 };
 svg.addEventListener("wheel",e=>{
  e.preventDefault();
  const v=bounds(),factor=e.deltaY>0?1.2:.82,box=svg.getBoundingClientRect();
  const fx=Math.min(1,Math.max(0,(e.clientX-box.left)/Math.max(1,box.width)));
  const fy=Math.min(1,Math.max(0,(e.clientY-box.top)/Math.max(1,box.height)));
  const w=v[2]*factor,h=v[3]*factor;
  set(v[0]-(w-v[2])*fx,v[1]-(h-v[3])*fy,w,h);
 },{passive:false});
 svg.addEventListener("pointerdown",e=>{
  if(e.pointerType==="mouse"&&e.button!==0)return;
  if(e.target.closest("circle.oaf-ux35-point"))return;
  pointer={id:e.pointerId,x:e.clientX,y:e.clientY,start:bounds()};
  try{svg.setPointerCapture(e.pointerId)}catch{}
 });
 svg.addEventListener("pointermove",e=>{
  if(!pointer||e.pointerId!==pointer.id)return;
  const rect=svg.getBoundingClientRect(),[x,y,w,h]=pointer.start;
  set(x-(e.clientX-pointer.x)*w/Math.max(1,rect.width),
   y-(e.clientY-pointer.y)*h/Math.max(1,rect.height),w,h);
 });
 for(const ev of ["pointerup","pointercancel","lostpointercapture"])
  svg.addEventListener(ev,e=>{if(pointer&&pointer.id===e.pointerId)pointer=null});
}

function handleChange(e){
 const target=e.target;
 if(target?.dataset?.ux35Key==="phytosanitary"){
  state.on.phytosanitary=target.checked;render();return;
 }
}
function handleClick(e){
 const action=e.target.closest("[data-ux35-action]");if(!action)return;
}
function requestSharedData(){
 const wanted={
  district:enabled("distrito")||enabled("provincia"),
  historical:enabled("fluvial")||enabled("pluvial")||enabled("erosion")||enabled("detritos")||state.on.pastFlood||state.on.pastMass,
  hydroRio:enabled("drain")||state.on.futureRiver,hydroQuebrada:enabled("quebradas"),
  drought:enabled("drought")||state.on.futureDrought,heat:enabled("heat")||state.on.futureHeat,
 };
 window.oafUx35Wants=wanted;
  window.oafUx30RequestDraw?.();
  window.oafUx33Load?.();
  window.oafUx30RequestHistoricalClimate?.();
}
async function loadCompanies(){
 if(state.companyStatus!=="pendiente")return;
 state.companyStatus="cargando";
 try{
  const r=await fetch(COMPANIES,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);
  const content=await r.json();if(!Array.isArray(content.features))throw Error("GeoJSON incompleto");
  state.comp=content.features.filter(f=>f.geometry?.type==="Point"&&f.geometry.coordinates?.length===2);
  state.companyStatus=state.comp.length+" ubicaciones referenciales";
 }catch(e){state.companyStatus="No se pudo cargar el catálogo local";state.comp=[]}
 render();
}
async function loadHistory(year){
 if(!YEARS.includes(year)||state.history.has(year)||state.historyRequested.has(year))return;
 state.historyRequested.add(year);state.historyStatus="cargando";render();
 const start=year+"-01-01",end=year+"-03-31";
 const tasks=stations.map(async loc=>{
  const params=new URLSearchParams({
   latitude:String(loc.lat),longitude:String(loc.lon),start_date:start,end_date:end,
   daily:"precipitation_sum",timezone:"America/Lima"
  });
  const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),16000);
  try{
   const url="https://archive-api.open-meteo.com/v1/archive?"+params;
   const response=await fetch(url,{signal:ctl.signal,cache:"no-store"});
   if(!response.ok)throw Error("HTTP "+response.status);
   const payload=await response.json(),rain=payload.daily?.precipitation_sum;
   if(!Array.isArray(rain)||rain.length<85||rain.some(x=>x!==null&&!Number.isFinite(Number(x))))throw Error("serie incompleta");
   const usable=rain.filter(v=>v!==null);
   if(usable.length<85)throw Error("datos faltantes");
   return {...loc,sum:usable.reduce((a,b)=>a+Number(b),0),days:usable.length,source:"Open-Meteo Archive"};
  }finally{clearTimeout(timer)}
 });
 const results=await Promise.allSettled(tasks);
 const success=results.filter(i=>i.status==="fulfilled").map(i=>i.value);
 state.history.set(year,{records:success,total:tasks.length,loadedAt:new Date().toISOString()});
 state.historyStatus=success.length?success.length+" de "+tasks.length+" localidades":"sin datos válidos";
 state.historyRequested.delete(year);render();
}
function data(){
 return window.oafUx29ScenarioApi?.get()||{};
}
function render(){
 const pane=$("oaf-ux29-scenario"),svg=$("oaf-ux29-forecast-map"),api=data(),scene=api.scene;
 if(!pane||!svg||!scene)return;
 state.ready=true;state.scene=scene;state.current=[];
 const viewBox=svg.getAttribute("viewBox")||"0 0 700 380";
 svg.replaceChildren();svg.setAttribute("viewBox",viewBox);
 svg.append(SVG("rect",{x:0,y:0,width:700,height:380,fill:"#f0f7f2"}));
 const defs=SVG("defs"),clip=SVG("clipPath",{id:"oaf-ux35-region-clip",clipPathUnits:"userSpaceOnUse"});
 for(const ring of scene.rings){
  const d=ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+" "+scene.y(p[1]).toFixed(2)).join(" ")+" Z";
  clip.append(SVG("path",{d,"fill-rule":"evenodd","clip-rule":"evenodd"}));
 }
 defs.append(clip);svg.append(defs);
 const region=SVG("g",{"clip-path":"url(#oaf-ux35-region-clip)"});svg.append(region);
 for(const ring of scene.rings){
  const d=ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+" "+scene.y(p[1]).toFixed(2)).join(" ")+" Z";
  region.append(SVG("path",{d,fill:"#dcefe2","fill-opacity":".48",stroke:"none","pointer-events":"none"}));
 }
 const outline=SVG("g",{"pointer-events":"none"});
 for(const ring of scene.rings){
  const d=ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+" "+scene.y(p[1]).toFixed(2)).join(" ")+" Z";
  outline.append(SVG("path",{d,fill:"none",stroke:"#28644e","stroke-width":2.2}));
 }
 svg.append(outline);
 const labels=SVG("g",{id:"oaf-ux35-labels","pointer-events":"none"});svg.append(labels);
 const footer=SVG("text",{x:350,y:361,fill:"#3b5b50","font-size":12,"text-anchor":"middle"});
 footer.textContent="Lambayeque · contorno regional referencial";svg.append(footer);
 status();diagnosis();
}
function renderLabels(){
 const svg=$("oaf-ux29-forecast-map"),group=$("oaf-ux35-labels");if(!svg||!group)return;
 group.replaceChildren();
 const bounds=(svg.getAttribute("viewBox")||"0 0 700 380").split(/[,\s]+/).map(Number);
 if(bounds.length!==4||bounds.some(x=>!Number.isFinite(x)))return;
 const [bx,by,bw,bh]=bounds,k=bw/700;
 const candidates=state.current.slice().sort((a,b)=>b.rank-a.rank);
 const seen=[],max=bw>500?19:bw>260?35:70;let drawn=0;
 for(const p of candidates){
  if(drawn>=max)break;
  const xx=(p.x-bx)/bw*700,yy=(p.y-by)/bh*380;
  if(xx<20||xx>680||yy<13||yy>356)continue;
  const str=String(p.name).slice(0,40),len=Math.min(180,str.length*5.5+12);
  const bbox=[xx,yy-14,xx+len,yy+6];
  if(seen.some(b=>b[0]<bbox[2]&&b[2]>bbox[0]&&b[1]<bbox[3]&&b[3]>bbox[1]))continue;
  seen.push(bbox);
  const label=SVG("text",{x:p.x+9*k,y:p.y-5*k,fill:"#1b4c3e","font-size":11*k,
   "font-weight":"750",stroke:"#fff","stroke-width":3*k,"paint-order":"stroke"});
  label.textContent=str;group.append(label);drawn++;
 }
}
function applyZoomStyles(svg){
 const v=(svg.getAttribute("viewBox")||"0 0 700 380").split(/[,\s]+/).map(Number);
 if(v.length!==4)return;
 const scale=v[2]/700;
 for(const point of svg.querySelectorAll("circle.oaf-ux35-point")){
  point.setAttribute("r",Math.max(.5,Number(point.dataset.ux35Radius||5)*scale).toFixed(2));
  point.setAttribute("stroke-width",Math.max(.2,1.5*scale).toFixed(2));
 }
 renderLabels();
}
function status(){
 const display=$("oaf-ux35-mapstatus");if(!display)return;
 display.textContent=state.on.phytosanitary?
  "C. Riesgo agroclimático fitosanitario: pendiente de conexión. No existe un geodato validado para dibujar riesgo por cultivo y organismo perjudicial.":
  "La única capa temática está desactivada. Su conexión geoespacial permanece pendiente.";
}
function diagnosis(){
 const pane=$("oaf-ux29-scenario"),target=pane?.querySelector(".oaf-ux29-diagbody");if(!target)return;
 target.replaceChildren();
 const section=(header,body,level)=>{
  const box=E("section","oaf-ux35-diagnosis-section"),h=E("strong"),p=E("p");
  h.textContent=header;p.textContent=body;box.append(h,p);
  if(level){const small=E("small");small.textContent=level;box.append(small)}
  target.append(box);
 };
 const selected=(window.oafUx30Context?.()?.selected||[]).map(p=>p.name).join(" ∩ ");
 section("Ámbito territorial",selected||"Región Lambayeque · mapa referencial");
 section("C. Riesgo agroclimático fitosanitario",state.on.phytosanitary?
  "Pendiente de conexión. No se asigna nivel de riesgo ni se dibuja una superficie hasta disponer de datos espaciales validados por cultivo, organismo perjudicial y periodo.":
  "Capa desactivada. No se representa ningún escenario fitosanitario.");
 section("Disponibilidad de datos","Los indicadores meteorológicos puntuales existentes no constituyen una capa regional de riesgo fitosanitario. La humedad relativa ambiental no equivale a horas reales de humedad foliar ni confirma infección.");
 section("Criterio de representación","No se generan polígonos, puntos, probabilidades ni semáforos artificiales. La capa se habilitará cuando exista una fuente geoespacial verificable y una metodología validada para relacionar cultivo, plaga o enfermedad y condiciones agroclimáticas.");
}
function meta(){
 const area=$("oaf-ux30-metadatos")||document.querySelector('[data-page="verificaciones"]');
 if(!area||$("oaf-ux35-metadatos"))return;
 const div=E("section","oaf-ux35-metadatos");div.id="oaf-ux35-metadatos";
 div.innerHTML='<h2>Fuentes y trazabilidad de escenarios agroclimáticos</h2>'+
 '<p>Se comparan tres productos diferentes: reanálisis histórico, pronóstico meteorológico puntual y cartografía oficial de susceptibilidad. No se convierten automáticamente en estimaciones de caudal o zonas inundadas futuras.</p>'+
 '<ul><li><a href="https://sigrid.cenepred.gob.pe/sigridv3/documento/16310" target="_blank" rel="noopener noreferrer">CENEPRED 2023 · escenarios El Niño 1983/1998/2017/2023</a></li>'+
 '<li><a href="https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-19-2026/" target="_blank" rel="noopener noreferrer">ENFEN · Comunicado Oficial 19-2026 (30/10/2026)</a></li>'+
 '<li><a href="https://www.senamhi.gob.pe/" target="_blank" rel="noopener noreferrer">SENAMHI · avisos y escenarios estacionales</a></li>'+
 '<li><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noopener noreferrer">Open-Meteo Archive · datos históricos modelados, no estaciones</a></li>'+
 '<li><a href="https://open-meteo.com/en/docs" target="_blank" rel="noopener noreferrer">Open-Meteo Forecast · precipitación pronosticada 7 días</a></li>'+
 '<li><a href="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6010100" target="_blank" rel="noopener noreferrer">INGEMMET · inventario 2017</a></li>'+
 '<li><a href="'+COMPANIES+'" target="_blank" rel="noopener noreferrer">Agroindustrias y fundos referenciales · GeoJSON OpenStreetMap (no padrón SUNAT)</a></li>'+
 '<li><a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_ESCENARIOS_AGROCLIMATICOS_UX35.md" target="_blank" rel="noopener noreferrer">Metodología UX35 · uso e incertidumbre del visor</a></li></ul>';
 area.append(div);
}
function init(){
 window.oafUx35Render=()=>render();
 window.oafUx35Diagnosis=()=>diagnosis();
 window.oafUx35Wants={district:false,historical:false,hydroRio:false,hydroQuebrada:false,drought:false,heat:false};
 activate();
 const api=window.oafUx29ScenarioApi;
 if(api?.get()?.scene)render();
 else{
  let cycles=0;const probe=()=>{
   if(api?.get()?.scene){render();return;}
   if(++cycles<25)setTimeout(probe,300);
   else status();
  };setTimeout(probe,250);
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();