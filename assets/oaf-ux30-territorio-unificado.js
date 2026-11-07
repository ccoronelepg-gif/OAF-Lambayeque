/* OAF UX30 · Visor territorial único con árbol SIG multicapa y diagnóstico explicativo.
 * Las capas SIGRID son de organismos oficiales; las capas de susceptibilidad no son
 * pronósticos de zonas inundadas. No representa sequías/calor sin datos verificables.
 */
(function(){"use strict";
const $=id=>document.getElementById(id),node=(tag,cls)=>{const v=document.createElement(tag);if(cls)v.className=cls;return v};
const layerSpec=[
 ["peligros","A. Peligros climáticos e hidrometeorológicos",[
  ["flood","Peligro de inundaciones",true,"Cartografía de susceptibilidad a inundaciones por lluvias fuertes publicada por CENEPRED (2021), capa 5090024. Representa predisposición territorial; no es una huella de inundación actual ni una alerta vigente.","CENEPRED · S05CP/MapServer/5090024"],
  ["rainIntense","Peligro de lluvias intensas",false,"Indicador pronosticado de precipitación máxima diaria (mm/24 h) durante siete días; zonas de proximidad a puntos de Open-Meteo. NO es cartografía oficial de peligro ni umbral SENAMHI de aviso.",null],
  ["drought","Sequía y déficit hídrico",false,"Lluvia acumulada modelada de los 30 días anteriores (mm). Un total bajo NO equivale a sequía: sin climatología normal, balance hídrico, SPEI/SPI o demanda del cultivo no hay índice de déficit validado.",null],
  ["heat","Temperaturas extremas",false,"Temperatura máxima pronosticada a 2 m de los próximos siete días (Open-Meteo), junto con WMS histórico de calor SENAMHI/IDESEP si responde. No es un aviso de ola de calor ni predicción de daños.","SENAMHI/IDESEP · WMS histórico y Open-Meteo Forecast 7 días"]
 ]],
 ["agroclimatic","B. Condiciones agroclimáticas",[
  ["humidity","Exceso de humedad y condiciones favorables para enfermedades (humedad relativa y horas de humedad foliar)",false,"Pendiente de conexión. La humedad relativa ambiental a 2 m no equivale a horas reales de humedad foliar; todavía no existe una superficie geoespacial validada de mojado foliar y condiciones epidemiológicas.",null],
  ["wind","Vientos fuertes",false,"Pendiente de conexión. Los datos meteorológicos puntuales disponibles no constituyen una capa espacial regional validada de intensidad y peligro por vientos fuertes.",null]
 ]]
];
const spec=new Map(layerSpec.flatMap(g=>g[2].map(a=>[a[0],{id:a[0],title:a[1],default:a[2],meaning:a[3],source:a[4]||"",available:Boolean(a[4]),group:g[1]}])));
const state={on:Object.fromEntries([...spec].map(([k,v])=>[k,v.default])),basemap:{satellite:false},scene:null,selected:[],contains:null,legacy:null,
 points:[],heatStatus:"pendiente",activePoint:null, dragging:new Map(),gesture:null,view:[0,0,700,340],lastZoom:1};
const SIGRID="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer",
 SIGRID_HYDRO="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer",
 HAZARD="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer",
 ANA="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer",
 WORLD_IMAGERY="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
 MINAM="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
// Servicio WMS oficial de frecuencia histórica de olas de calor (SENAMHI IDESEP).
// El servicio puede estar temporalmente fuera de línea; las condiciones pronosticadas
// de temperatura del módulo A se obtienen por separado de Open-Meteo (UX73).
function heatWmsUrl(bounds){
 if(!bounds||![bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].every(Number.isFinite))return "";
 const p=new URLSearchParams({
  service:"WMS",version:"1.1.1",request:"GetMap",
  layers:"g_01_06:01_06_001_03_001_512_0000_00_00",
  styles:"",srs:"EPSG:4326",
  bbox:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  width:"1100",height:"535",format:"image/png",transparent:"TRUE"
 });
 return "https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms?"+p;
}
const on=k=>!!state.on[k];
function sv(tag,attrs){const e=document.createElementNS("http://www.w3.org/2000/svg",tag);Object.entries(attrs||{}).forEach(([k,v])=>e.setAttribute(k,String(v)));return e}
function text(el,content){el.textContent=String(content);return el}
function overlaySrc(service,layers,layerDefs){
 const b=state.scene?.bounds;if(!b)return "";
 const query=new URLSearchParams({bbox:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  bboxSR:"4326",imageSR:"4326",size:"1100,535",format:"png32",transparent:"true",dpi:"130",
  layers:"show:"+layers,f:"image"});
 if(layerDefs)query.set("layerDefs",JSON.stringify(layerDefs));
 return service+"/export?"+query;
}
function satelliteSrc(bounds){
 if(!bounds)return "";
 const query=new URLSearchParams({bbox:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  bboxSR:"4326",imageSR:"4326",size:"1100,535",format:"jpg",transparent:"false",dpi:"120",f:"image"});
 return WORLD_IMAGERY+"/export?"+query;
}
function makeTree(){
 const pane=$("oaf-ux29-territory"),tree=pane?.querySelector(".oaf-ux29-tree");
 if(!tree||$("oaf-ux30-layer-tree"))return;
 // Apagar los controles heredados antes de retirarlos del DOM: no se conservan capas antiguas ocultas.
 applyLegacy();
  // Retirar el selector heredado de capas de inundación que UX27 insertaba fuera del árbol.
  document.querySelector("#oaf-ux27-exposicion .oaf-ux27-riskmap")?.remove();
 pane.querySelector("#oaf-ux30-legacy")?.remove();
 tree.replaceChildren();state.legacy=null;
 pane.dataset.ux30Active="true";
 const groups=node("div","oaf-ux30-layer-tree");groups.id="oaf-ux30-layer-tree";
 for(const [id,label,entries] of layerSpec){
  const d=node("details","oaf-ux30-section");d.open=id==="peligros";
  const head=node("summary");head.append(text(node("span"),label));d.append(head);
  const wrap=node("div","oaf-ux30-options");
  for(const [key,title,checked] of entries){
   const def=spec.get(key),item=node("label","oaf-ux30-option"),check=node("input");
   check.type="checkbox";check.dataset.ux30Layer=key;check.checked=checked;
   const span=text(node("span"),title),tiny=node("small");
   tiny.textContent=!def.available?"Pendiente de conexión · no se representa información ficticia":
    key==="flood"?"CENEPRED 2021 · susceptibilidad, no inundación observada":
    key==="heat"?"Open-Meteo 7 días · T máxima; WMS histórico adicional":
    key==="rainIntense"?"Open-Meteo 7 días · máxima precipitación diaria (mm), no alerta":
    key==="drought"?"Open-Meteo · lluvia modelada 30 días anteriores, no SPI/SPEI":
    "Datos meteorológicos, sin riesgo oficial";
   item.append(check,span,tiny);wrap.append(item);
  }
  d.append(wrap);groups.append(d);
 }
 tree.replaceChildren(groups);
 const filters=$("oaf-ux26-filtros"),area=node("details","oaf-ux30-section oaf-ux30-area");area.open=true;
 const head=node("summary");head.textContent="Filtrar por provincia, distrito y cuenca";area.append(head);
 if(filters){
  // La superficie agrícola era una capa temática adicional; se retira solo ese selector y se conservan los filtros territoriales.
  filters.querySelector("#oaf-ux26-agricultura")?.closest("label")?.remove();
  area.append(filters);filters.classList.add("oaf-ux30-filter-widget");
 }
 tree.prepend(area);
 const controls=node("div","oaf-ux30-layer-actions");
 const all=node("button");all.type="button";all.textContent="Limpiar selección";
 all.addEventListener("click",()=>{
  for(const key of Object.keys(state.on))state.on[key]=false;
  state.activePoint=null;refreshControls();applyLegacy();render();
 });
 const reset=node("button");reset.type="button";reset.textContent="Mapa base";
 reset.addEventListener("click",()=>{
  for(const key of Object.keys(state.on))state.on[key]=false;
  state.activePoint=null;state.basemap.satellite=false;
  const relief=$("oaf-ux52-relief-toggle");
  if(relief?.checked){relief.checked=false;relief.dispatchEvent(new Event("change",{bubbles:true}))}
  refreshControls();applyLegacy();render();
 });
 const satellite=node("label","oaf-ux30-option oaf-ux30-basemap-option"),satCheck=node("input");
 satCheck.type="checkbox";satCheck.id="oaf-ux30-satellite-toggle";satCheck.dataset.ux30Basemap="satellite";
 const satText=text(node("span"),"Imagen satelital · Esri World Imagery");
 const satHint=text(node("small"),"Fondo cartográfico; no es una capa temática adicional.");
 satellite.append(satCheck,satText,satHint);
 controls.append(all,reset,satellite);tree.prepend(controls);
 tree.addEventListener("change",ev=>{
  const basemap=ev.target?.dataset?.ux30Basemap;
  if(basemap==="satellite"){state.basemap.satellite=ev.target.checked;render();return;}
  const key=ev.target?.dataset?.ux30Layer;if(!key||!spec.has(key))return;
  state.on[key]=ev.target.checked;if(!ev.target.checked&&state.activePoint?.category===key)state.activePoint=null;applyLegacy();render();
  if(key==="heat"&&on("heat"))loadHeat();
 });
 const p=pane.querySelector(".oaf-ux29-maphead strong");if(p)p.textContent="Mapa político y temático de Lambayeque";
 const title=pane.querySelector(".oaf-ux29-top h2");if(title)title.textContent="Visor geográfico de Lambayeque";
 const lead=pane.querySelector(".oaf-ux29-top p");if(lead)lead.textContent="Activa las capas climáticas e hidrometeorológicas y las condiciones agroclimáticas disponibles. Los indicadores meteorológicos muestran áreas de influencia aproximadas; las susceptibilidades oficiales se identifican por fuente y año.";
 const board=pane.querySelector(".oaf-ux29-diagbody");if(board)board.setAttribute("aria-live","polite");
 const content=pane.querySelector(".oaf-ux29-mapcolumn .oaf-ux29-mapcontent");
 if(!pane.querySelector("#oaf-ux30-map-help")){
  const help=text(node("p","oaf-ux30-map-help"),"Navegación: arrastra para mover, usa la rueda para acercar y dos dedos para ampliar en celular.");
  content?.prepend(help);
 }
 if(content&&!content.querySelector("#oaf-ux30-satellite-credit")){
  const credit=text(node("small","oaf-ux30-satellite-credit"),"Imagen satelital: © Esri, Vantor, Earthstar Geographics y la comunidad GIS. La fecha y resolución varían por zona.");
  credit.id="oaf-ux30-satellite-credit";credit.hidden=true;content.append(credit);
 }
}
function refreshControls(){
 document.querySelectorAll("[data-ux30-layer]").forEach(c=>c.checked=on(c.dataset.ux30Layer));
 const satellite=$("oaf-ux30-satellite-toggle");if(satellite)satellite.checked=!!state.basemap.satellite;
}
function setCheck(id,checked){
 const e=$(id);if(!e||e.checked===checked)return;
 e.checked=checked;e.dispatchEvent(new Event("change",{bubbles:true}));
}
function applyLegacy(){
 // Apagar selectores heredados que ya no forman parte del inventario visible del visor.
 const layer=$("oaf-ux25-raster");if(layer&&layer.value!=="none"){layer.value="none";layer.dispatchEvent(new Event("change",{bubbles:true}))}
 setCheck("oaf-ux25-minam",on("floodpoints"));
 setCheck("oaf-ux25-geologico",false);
 setCheck("oaf-ux26-agricultura",false); // Selector agrícola retirado del inventario temático.
 for(const [id,key] of [["national","nacional"],["regional","departamental"],["vecinal","vecinal"]]){
  const e=document.querySelector('[data-ux28-road="'+id+'"]');if(e&&e.checked!==on(key)){e.checked=on(key);e.dispatchEvent(new Event("change",{bubbles:true}))}
 }
 for(const key of ["hospital","posta","policia","bomberos"]){
  const e=document.querySelector('[data-ux28-emergency="'+key+'"]');if(e&&e.checked!==on(key)){e.checked=on(key);e.dispatchEvent(new Event("change",{bubbles:true}))}
 }
 const d=document.querySelector('[data-ux28-emergency="defensa"]');if(d?.checked){d.checked=false;d.dispatchEvent(new Event("change",{bubbles:true}))}
}

/* UX32: GeoJSON de la red IGN 1:100 000, con ríos y quebradas separados por "tipo".
   Dibujar vectores evita que el mapa se quede vacío por límites de escala del MapServer. */
function updateLoadStatus(){
 if(typeof window.oafUx33Diagnosis==="function"){const previous=document.getElementById("oaf-ux32-map-status");if(previous)previous.hidden=true;return;}
 const pane=$("oaf-ux29-territory"),container=pane?.querySelector(".oaf-ux29-mapcontent");if(!container)return;
 let bar=$("oaf-ux32-map-status");
 if(!bar){bar=node("div","oaf-ux32-map-status");bar.id="oaf-ux32-map-status";bar.setAttribute("role","status");bar.setAttribute("aria-live","polite");container.prepend(bar);}
 const active=[...spec.keys()].filter(on);
 if(!active.length){bar.hidden=true;return;}
 bar.hidden=false;
 const messages=[];
 if(on("flood")){
  const image=[...pane.querySelectorAll("image[data-ux30-server]")].find(x=>x.dataset.ux30Ids==="5090024");
  messages.push("Inundaciones · "+(image?.dataset.error==="true"?"CENEPRED no respondió":image?.dataset.loaded==="true"?"CENEPRED cargado":"consultando CENEPRED"));
 }
 if(on("heat"))messages.push("Temperaturas extremas · "+state.heatStatus);
 for(const key of active){const def=spec.get(key);if(!def.available)messages.push(def.title+": pendiente de conexión");}
 bar.textContent=messages.join(" · ")+". Las capas pendientes no dibujan datos ni asignan niveles de riesgo.";
}
function render(){
 const scene=state.scene,pane=$("oaf-ux29-territory");if(!scene||!pane)return;
 const map=scene.svg;updateLoadStatus();
 const satelliteCredit=pane.querySelector("#oaf-ux30-satellite-credit");
 if(satelliteCredit)satelliteCredit.hidden=!state.basemap.satellite;
 map.querySelectorAll(".oaf-ux30-layer").forEach(x=>x.remove());
 const defs=sv("defs",{class:"oaf-ux30-layer"});
 const clip=sv("clipPath",{id:"oaf-ux30-clip-region",clipPathUnits:"userSpaceOnUse"});
 const boundary=map.querySelector('[data-oaf-ux24-boundary="true"]');
 if(boundary){boundary.style.opacity="1";clip.append(sv("path",{d:boundary.getAttribute("d")}));}
 defs.append(clip);map.append(defs);
 const back=sv("g",{class:"oaf-ux30-layer","clip-path":"url(#oaf-ux30-clip-region)"});
 const front=sv("g",{class:"oaf-ux30-layer"});
 const add=(service,layers,opacity,name,layerDefs)=>{
  const image=sv("image",{href:overlaySrc(service,layers,layerDefs),x:0,y:0,width:700,height:340,opacity,
   preserveAspectRatio:"none","pointer-events":"none"});
  image.dataset.title=name;image.dataset.ux30Server=service;image.dataset.ux30Ids=String(layers);
  if(layerDefs)image.dataset.ux30Defs=JSON.stringify(layerDefs);
  image.addEventListener("error",()=>{image.dataset.error="true";diagnosis()});
  image.addEventListener("load",()=>{image.dataset.loaded="true";diagnosis()});back.append(image);
 };
 if(state.basemap.satellite){
  const image=sv("image",{href:satelliteSrc(scene.bounds),x:0,y:0,width:700,height:340,opacity:"1",
   preserveAspectRatio:"none","pointer-events":"none"});
  image.dataset.title="Imagen satelital · Esri World Imagery";image.dataset.ux30Satellite="true";
  image.addEventListener("error",()=>{image.dataset.error="true";diagnosis()});
  image.addEventListener("load",()=>{image.dataset.loaded="true";diagnosis()});back.append(image);
 }
 if(on("flood"))add(HAZARD,5090024,.78,"Peligro de inundaciones · susceptibilidad CENEPRED 2021");
 if(on("heat")){
  const wms=sv("image",{href:heatWmsUrl(scene.bounds),x:0,y:0,width:700,height:340,
   opacity:".45",preserveAspectRatio:"none","pointer-events":"none"});
  wms.dataset.title="SENAMHI · frecuencia histórica de olas de calor, verano";wms.dataset.ux31Wms="heat";
  wms.addEventListener("error",()=>{wms.dataset.error="true";diagnosis()});
  wms.addEventListener("load",()=>{wms.dataset.loaded="true";diagnosis()});back.append(wms);
 }
 for(const p of state.points){
  if(!on(p.category))continue;
  const [lon,lat]=p.coords;
  if(state.selected?.length&&state.contains&&!state.selected.every(k=>state.contains(k.geo,[lon,lat])))continue;
  const x=scene.x(lon),y=scene.y(lat);if(x<0||x>700||y<0||y>340)continue;
  const circle=sv("circle",{cx:x,cy:y,r:6,fill:p.color,stroke:"#fff","stroke-width":1.2,tabindex:"0",role:"button","aria-label":p.label});
  circle.classList.add("oaf-ux30-feature","oaf-ux31-heat");circle.dataset.ux30Radius="6";
  circle.addEventListener("click",()=>{state.activePoint=p;diagnosis()});
  circle.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();state.activePoint=p;diagnosis()}});
  const ttl=sv("title");ttl.textContent=p.label;circle.append(ttl);front.append(circle);
 }
 if(boundary){
  const outline=boundary.cloneNode(true);outline.removeAttribute("id");outline.removeAttribute("data-oaf-ux24-boundary");
  outline.setAttribute("fill","none");outline.setAttribute("stroke","#1d634b");outline.setAttribute("stroke-width","2.2");
  outline.setAttribute("vector-effect","non-scaling-stroke");outline.setAttribute("pointer-events","none");
  outline.style.fill="none";outline.style.stroke="#1d634b";outline.style.strokeWidth="2.2";outline.style.pointerEvents="none";front.append(outline);
 }
 map.insertBefore(back,null);map.append(front);
 diagnosis();adjustMarkerSizes();
 if(typeof window.oafUx33AfterDraw==="function")window.oafUx33AfterDraw({scene,state,on,map});
 document.dispatchEvent(new CustomEvent("oaf:territory-map-redrawn"));
 refreshDetailMap();
}
function diagnoseItem(key){
 const def=spec.get(key);return def?def.meaning:"No hay descripción disponible.";
}
function heading(parent,title,body,status){
 const section=node("section","oaf-ux30-diagnosis-item"),h=text(node("strong"),title),p=text(node("p"),body);
 section.append(h,p);if(status){const small=text(node("small"),status);section.append(small)}parent.append(section);
}
function diagnosis(){
 const pane=$("oaf-ux29-territory"),box=pane?.querySelector(".oaf-ux29-diagbody");if(!box)return;
 box.replaceChildren();
 const area=$("oaf-ux26-prov")?.selectedOptions?.[0]?.textContent?.trim()||"Todas las provincias";
 const district=$("oaf-ux26-dist")?.selectedOptions?.[0]?.textContent?.trim()||"Todos los distritos";
 const watershed=$("oaf-ux26-basin")?.selectedOptions?.[0]?.textContent?.trim()||"Todas las cuencas";
 heading(box,"Ámbito",area+" · "+district+" · "+watershed+". Los filtros se aplican cuando la fuente dispone de geometrías.");
 const chosen=[...spec].filter(([id])=>on(id));
 if(!chosen.length)heading(box,"Sin capas activas","Selecciona una de las seis capas temáticas disponibles.");
 for(const [id,def] of chosen){
  let status=def.available?"Fuente espacial disponible":"Pendiente de conexión · no se representa información ficticia";
  if(["rainIntense","drought","heat"].includes(id))status="Indicador climático UX73 · consulta en el mapa, ver leyenda (no es nivel oficial de peligro).";
  if(id==="flood"){
   const image=[...pane.querySelectorAll("image[data-ux30-server]")].find(x=>x.dataset.ux30Ids==="5090024");
   status="CENEPRED 2021 · "+(image?.dataset.error==="true"?"geoservicio no disponible":image?.dataset.loaded==="true"?"capa cargada correctamente":"solicitando geoservicio");
  }else if(id==="heat"){
   const image=pane.querySelector('image[data-ux31-wms="heat"]');
   status="SENAMHI/IDESEP · "+(image?.dataset.error==="true"?"WMS no disponible":image?.dataset.loaded==="true"?"WMS cargado":"consultando WMS")+" · "+state.heatStatus;
  }
  heading(box,def.title,def.meaning,status);
 }
 if(state.activePoint){
  const p=state.activePoint;
  heading(box,"Punto consultado: "+p.label,"Tipo: "+(p.type||"no consignado")+". Fecha o periodo: "+(p.year||"sin fecha")+
   ". Fuente: "+(p.source||"organismo oficial")+". "+(p.detail||"Registro puntual documentado; no representa toda el área afectada."));
 }
 heading(box,"Lectura del mapa","La susceptibilidad indica predisposición y no un evento actual. Los polígonos climáticos son áreas de proximidad a muestras meteorológicas, no niveles oficiales de peligro o riesgo. Las susceptibilidades oficiales se interpretan por separado.");
 const failed=pane.querySelectorAll(".oaf-ux30-layer image[data-error=true]").length;
 if(failed)heading(box,"Una fuente cartográfica no respondió",failed+" servicio(s) no se pudieron cargar. Comprueba la disponibilidad del organismo de origen.");
}
async function loadHeat(){
 if(state.heatStatus!=="pendiente")return;
 state.heatStatus="consultando punto meteorológico SENAMHI";diagnosis();
 try{
  const response=await fetch("datos/riesgos_ux31/calor_historico_senamhi_lambayeque.geojson",{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const data=await response.json();
  if(!Array.isArray(data.features))throw Error("GeoJSON inválido");
  const entries=data.features.map(f=>{
   const p=f.properties||{},coords=f.geometry?.coordinates;
   if(f.geometry?.type!=="Point"||!Array.isArray(coords)||!coords.every(Number.isFinite))return null;
   return {coords,category:"heat",color:"#dc583d",label:"Calor histórico · "+String(p.estacion||"Estación SENAMHI"),
    year:p.fecha||"2024",type:p.tipo||"registro térmico",
    detail:"Máxima registrada "+p.maxima_celsius+" °C ("+p.fecha+"); anomalía promedio de temperatura máxima de marzo 2024: +"+p.anomalia_maxima_marzo_2024_celsius+" °C.",
    source:"SENAMHI, boletín climático marzo 2024",sourceUrl:p.fuente_url||"https://www.senamhi.gob.pe/"};
  }).filter(Boolean);
  state.points=state.points.filter(p=>p.category!=="heat").concat(entries);
  state.heatStatus=entries.length+" estación/es con registro histórico documentado";
 }catch(e){state.heatStatus="No disponible el registro SENAMHI incorporado."}
 finally{render();window.dispatchEvent(new Event("oaf:geodata"))}
}

function adaptOriginal(){
 const pane=$("oaf-ux29-territory");
 if(!pane)return;
 const map=$("oaf-ux24-region-map");
 if(map&&!map.dataset.ux30Nav){map.dataset.ux30Nav="true";navigation(map);}
 const old=getUrlHash();
 if(old==="oaf-territorio-riesgos"||old==="clima")render();
}
function getUrlHash(){try{return decodeURIComponent(location.hash.slice(1))}catch{return""}}
function getView(map){
 const v=(map.getAttribute("viewBox")||"0 0 700 340").trim().split(/[\s,]+/).map(Number);
 return v.length===4&&v.every(Number.isFinite)?v:[0,0,700,340];
}
function refreshDetailMap(){
 const map=$("oaf-ux24-region-map"),scene=state.scene;
 if(!map||!scene)return;
 clearTimeout(state.highResTimer);
 state.highResTimer=setTimeout(()=>{
  const v=getView(map),b=scene.bounds;
  if(v[2]>=699){
   for(const img of map.querySelectorAll("image[data-ux30-server]")){
    img.setAttribute("x","0");img.setAttribute("y","0");
    img.setAttribute("width","700");img.setAttribute("height","340");
    img.setAttribute("href",overlaySrc(img.dataset.ux30Server,img.dataset.ux30Ids,img.dataset.ux30Defs?JSON.parse(img.dataset.ux30Defs):null));
   }
   for(const img of map.querySelectorAll('image[data-ux31-wms]')){
    img.setAttribute("x","0");img.setAttribute("y","0");
    img.setAttribute("width","700");img.setAttribute("height","340");
    img.setAttribute("href",heatWmsUrl(b));
   }
   for(const img of map.querySelectorAll("image[data-ux30-satellite]")){
    img.setAttribute("x","0");img.setAttribute("y","0");img.setAttribute("width","700");img.setAttribute("height","340");
    img.setAttribute("href",satelliteSrc(b));
   }
   return;
  }
  const geo={
   minLon:b.minLon+(v[0]/700)*(b.maxLon-b.minLon),
   maxLon:b.minLon+((v[0]+v[2])/700)*(b.maxLon-b.minLon),
   maxLat:b.maxLat-(v[1]/340)*(b.maxLat-b.minLat),
   minLat:b.maxLat-((v[1]+v[3])/340)*(b.maxLat-b.minLat)
  };
  for(const img of map.querySelectorAll("image[data-ux30-server]")){
   const service=img.dataset.ux30Server,ids=img.dataset.ux30Ids;
   const query=new URLSearchParams({
    bbox:[geo.minLon,geo.minLat,geo.maxLon,geo.maxLat].join(","),
    bboxSR:"4326",imageSR:"4326",size:"1100,535",
    format:"png32",transparent:"true",dpi:"130",layers:"show:"+ids,f:"image"
   });
   if(img.dataset.ux30Defs)query.set("layerDefs",img.dataset.ux30Defs);
   img.setAttribute("x",v[0]);img.setAttribute("y",v[1]);
   img.setAttribute("width",v[2]);img.setAttribute("height",v[3]);
   img.setAttribute("href",service+"/export?"+query);
  }
  for(const img of map.querySelectorAll('image[data-ux31-wms]')){
   img.setAttribute("x",v[0]);img.setAttribute("y",v[1]);
   img.setAttribute("width",v[2]);img.setAttribute("height",v[3]);
   img.setAttribute("href",heatWmsUrl(geo));
  }
  for(const img of map.querySelectorAll("image[data-ux30-satellite]")){
   img.setAttribute("x",v[0]);img.setAttribute("y",v[1]);
   img.setAttribute("width",v[2]);img.setAttribute("height",v[3]);
   img.setAttribute("href",satelliteSrc(geo));
  }
 },450);
}
function setView(map,b){
 const maxW=700,minW=42,ratio=700/340;
 let w=Math.max(minW,Math.min(maxW,b[2]));let h=w/ratio;
 let x=Math.max(0,Math.min(700-w,b[0])),y=Math.max(0,Math.min(340-h,b[1]));
 map.setAttribute("viewBox",[x,y,w,h].map(n=>n.toFixed(2)).join(" "));
 state.view=[x,y,w,h];
 adjustMarkerSizes();
 if(typeof window.oafUx33OnZoom==="function")window.oafUx33OnZoom();
 refreshDetailMap();
}
function adjustMarkerSizes(){
 const map=$("oaf-ux24-region-map");if(!map)return;
 const scale=getView(map)[2]/700;
 for(const line of map.querySelectorAll("path.oaf-ux32-hydroline")){
  line.setAttribute("stroke-width",Math.max(.14,(line.getAttribute("stroke-dasharray")==="none"?1.6:1.35)*scale).toFixed(2));
 }
 for(const elem of map.querySelectorAll("circle.oaf-ux25-point,circle.oaf-ux28-emergency-marker,circle.oaf-ux30-feature")){
  const original=Number(elem.dataset.ux30Radius||elem.getAttribute("r")||4);
  if(!elem.dataset.ux30Radius)elem.dataset.ux30Radius=original;
  elem.setAttribute("r",Math.min(9,Math.max(.4,original*scale)).toFixed(2));
  elem.setAttribute("stroke-width",Math.max(.15,1.2*scale).toFixed(2));
 }
}
function screenXY(map,e){const r=map.getBoundingClientRect();return{x:(e.clientX-r.left)/r.width,y:(e.clientY-r.top)/r.height}}
function zoom(map,factor,anchor){
 const [x,y,w,h]=getView(map);
 const nx=w*factor,nh=h*factor;
 const fx=anchor?.x??.5,fy=anchor?.y??.5;
 setView(map,[x+(w-nx)*fx,y+(h-nh)*fy,nx,nh]);
}
function navigation(map){
 map.style.touchAction="none";
 map.addEventListener("wheel",e=>{e.preventDefault();zoom(map,e.deltaY<0?.81:1.23,screenXY(map,e))},{passive:false});
 map.addEventListener("pointerdown",e=>{
  if(e.pointerType==="mouse"&&e.button!==0)return;
  if(e.target.closest("circle[role=button]"))return;
  try{map.setPointerCapture(e.pointerId)}catch{}
  state.dragging.set(e.pointerId,{x:e.clientX,y:e.clientY});
 },true);
 map.addEventListener("pointermove",e=>{
  if(!state.dragging.has(e.pointerId))return;
  const before=state.dragging.get(e.pointerId);state.dragging.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(state.dragging.size===1){
   const b=getView(map),rect=map.getBoundingClientRect();
   setView(map,[b[0]-(e.clientX-before.x)/rect.width*b[2],
    b[1]-(e.clientY-before.y)/rect.height*b[3],b[2],b[3]]);
  }else if(state.dragging.size===2){
   const current=[...state.dragging.values()],span=Math.hypot(current[0].x-current[1].x,current[0].y-current[1].y);
   if(state.gesture?.span)zoom(map,Math.max(.65,Math.min(1.4,state.gesture.span/span)),{x:.5,y:.5});
   state.gesture={span};
  }
 },true);
 const end=e=>{state.dragging.delete(e.pointerId);state.gesture=null};
 for(const name of ["pointerup","pointercancel","lostpointercapture"])map.addEventListener(name,end,true);
 map.addEventListener("dblclick",e=>{e.preventDefault();zoom(map,.8,screenXY(map,e));},{passive:false});
 for(const button of document.querySelectorAll("#oaf-ux29-territory [data-ux29-zoom]")){
  button.addEventListener("click",e=>{
   e.stopImmediatePropagation();e.preventDefault();
   const action=button.dataset.ux29Zoom;
   if(action==="reset")setView(map,[0,0,700,340]);
   else zoom(map,action==="in"?.75:1.3,{x:.5,y:.5});
  },true);
 }
 new MutationObserver(()=>adjustMarkerSizes()).observe(map,{attributes:true,attributeFilter:["viewBox"]});
}
function metadata(){
 const tab=document.querySelector('[data-page="verificaciones"]');if(!tab||$("oaf-ux30-metadatos"))return;
 const section=node("section","oaf-ux30-metadata");section.id="oaf-ux30-metadatos";
 section.innerHTML='<h2>Fuentes del visor geográfico de Lambayeque</h2>'+
 '<p>Este apartado reúne las fuentes oficiales y las notas metodológicas de las capas de peligros, límites, infraestructura, agricultura y análisis agroclimático, con sus fechas y alcances.</p>'+
 '<ul><li><a href="'+SIGRID+'" target="_blank" rel="noopener noreferrer">SIGRID/CENEPRED · límites políticos e inventario de puntos históricos FENC 2017</a></li><li><a href="'+ANA+'/8" target="_blank" rel="noopener noreferrer">ANA/GeoIDEP · unidades hidrográficas (polígonos y límites de cuenca)</a> · <a href="'+ANA+'/7" target="_blank" rel="noopener noreferrer">capa de límites y rótulos</a></li><li><a href="'+SIGRID_HYDRO+'/6030200" target="_blank" rel="noopener noreferrer">IGN/SIGRID · ríos y quebradas, Carta Nacional 1:100 000 (capas vectoriales)</a></li>'+
 '<li><a href="'+HAZARD+'/5090024" target="_blank" rel="noopener noreferrer">CENEPRED · susceptibilidad a inundaciones por lluvias fuertes (2021)</a> · <a href="'+HAZARD+'/5090023" target="_blank" rel="noopener noreferrer">El Niño (2021)</a> · <a href="'+HAZARD+'/5090022" target="_blank" rel="noopener noreferrer">movimientos en masa (2021)</a></li>'+
 '<li><a href="https://sigrid.cenepred.gob.pe/sigridv3/documento/22910" target="_blank" rel="noopener noreferrer">CENEPRED · escenario de riesgo por lluvias octubre–diciembre 2026, con mapa y SHAPE</a></li>'+
 '<li><a href="https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_trimestral/101_shape.zip" target="_blank" rel="noopener noreferrer">Descarga SHAPE del escenario octubre–diciembre 2026</a></li>'+
 '<li><a href="https://sigrid.cenepred.gob.pe/sigridv3/documento/22169" target="_blank" rel="noopener noreferrer">CENEPRED · estudio nacional de inundaciones y movimientos en masa asociados a El Niño, actualización 2026</a></li>'+
 '<li><a href="https://sigrid.cenepred.gob.pe/sigridv3/documento/22600" target="_blank" rel="noopener noreferrer">ANA · fichas técnicas referenciales de puntos críticos 2026 para Lambayeque</a></li>'+
 '<li><a href="'+WORLD_IMAGERY+'" target="_blank" rel="noopener noreferrer">Esri · World Imagery, imágenes satelitales de fecha variable por zona</a></li>'+
 '<li><a href="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer" target="_blank" rel="noopener noreferrer">MTC/IDEP · carreteras nacionales, departamentales y vecinales</a></li>'+
 '<li><a href="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer" target="_blank" rel="noopener noreferrer">IGN/IDEP · hospitales, puestos de salud, comisarías y bomberos</a></li>'+
 '<li><a href="'+MINAM+'/1" target="_blank" rel="noopener noreferrer">MINAM · superficie agrícola nacional, referencia 2018</a></li>'+
 '<li><a href="https://www.senamhi.gob.pe/site/vigilancia-climatica/" target="_blank" rel="noopener noreferrer">SENAMHI · vigilancia climática, sequías y temperaturas</a></li><li><a href="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6010100" target="_blank" rel="noopener noreferrer">INGEMMET/SIGRID · puntos 2017 de inundación fluvial, pluvial y erosión</a></li><li><a href="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6040000" target="_blank" rel="noopener noreferrer">INDECI/SIGRID · emergencias de sequía (inventario 2003–2020)</a></li><li><a href="https://idesep.senamhi.gob.pe/portalidesep/wms.do" target="_blank" rel="noopener noreferrer">SENAMHI/IDESEP · WMS histórico de frecuencia de olas de calor</a></li><li><a href="https://www.senamhi.gob.pe/load/file/02221SENA-134.pdf" target="_blank" rel="noopener noreferrer">SENAMHI · registro térmico Jayanca–La Viña (marzo 2024)</a></li><li><a href="datos/riesgos_ux31/calor_historico_senamhi_lambayeque.geojson" target="_blank" rel="noopener noreferrer">OAF · GeoJSON del punto histórico SENAMHI con metadatos</a></li><li><a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_EVENTOS_HISTORICOS_UX31.md" target="_blank" rel="noopener noreferrer">Metodología UX31 · fuentes y límites de las capas históricas</a></li><li><a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_EXPOSICION_INUNDACIONES_UX27.md" target="_blank" rel="noopener noreferrer">OAF UX27 · análisis cuantitativo agrícola y alcance de las 1 234 ha documentadas por CENEPRED</a></li><li><a href="datos/riesgos_ux27/indicadores_cenepred_2025.csv" download>Indicadores CENEPRED para nueve distritos de Lambayeque (CSV)</a></li></ul>'+
 '<p>Los datos de FENC 2017 son inventarios de lugares afectados, no mapas de inundación actual. La susceptibilidad regional es un raster, mientras que la capa INGEMMET de inundación fluvial utiliza polígonos de susceptibilidad. La exposición agrícola es visual y no una superficie calculada.</p>'+
 '<a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_VISOR_TERRITORIAL_UX30.md" target="_blank" rel="noopener noreferrer">Leer metodología detallada de la fase UX30 ↗</a> · <a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_CORRECCIONES_VISOR_UX32.md" target="_blank" rel="noopener noreferrer">Corrección de capas geológicas, cuencas e hidrografía UX32 ↗</a> · <a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_GEOCAPAS_ETIQUETAS_UX33.md" target="_blank" rel="noopener noreferrer">Geocapas etiquetadas, distritos y contraste agrícola UX33 ↗</a> · <a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_REPARACION_HIDROGRAFIA_UX34.md" target="_blank" rel="noopener noreferrer">Corrección de ríos y quebradas UX34 ↗</a>';
 tab.append(section);
}
function init(){
 makeTree();metadata();
 window.oafUx30RequestDraw=()=>render();
 window.oafUx30Catalog=()=>layerSpec.map(([id,title,entries])=>({id,title,entries:entries.map(([key,label,checked,meaning])=>({key,label,checked,meaning}))}));
 window.oafUx30Context=()=>({scene:state.scene,selected:state.selected,contains:state.contains,points:state.points});
 window.oafUx30RequestHistoricalClimate=()=>{if(on("heat")&&state.heatStatus==="pendiente")loadHeat();};
 
 // Instalar primero el enlace de render: los filtros anteriores pueden redibujar el mapa de inmediato.
 window.oafUx30AfterDraw=function(context){
  state.scene=context.scene;state.selected=context.selected||[];state.contains=context.contains||null;
  if(!state.mapInit){state.mapInit=true;navigation(state.scene.svg);}
  render();
  // Solo se carga la capa histórica de temperaturas extremas cuando se activa su control.
  if(on("heat")&&state.heatStatus==="pendiente")loadHeat();
  // Comparte eventos de sequía y calor con el visor de escenarios si están seleccionados.
  window.oafUx30RequestHistoricalClimate?.();
  // La versión UX33 gestiona líneas y etiquetas de la red hidrográfica.
 };
 applyLegacy();adaptOriginal();
 const pane=$("oaf-ux29-territory");
 if(pane){
  pane.addEventListener("change",e=>{
   if(e.target?.matches("#oaf-ux26-prov,#oaf-ux26-dist,#oaf-ux26-basin")){state.activePoint=null;requestAnimationFrame(()=>diagnosis());}
  });
  // Layer sources can update independently of user input.
  const delay=()=>requestAnimationFrame(()=>{if(state.scene)render()});
  window.addEventListener("hashchange",delay);
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();