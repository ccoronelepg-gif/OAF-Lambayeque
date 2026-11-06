/* OAF UX30 · Visor territorial único con árbol SIG multicapa y diagnóstico explicativo.
 * Las capas SIGRID son de organismos oficiales; las capas de susceptibilidad no son
 * pronósticos de zonas inundadas. No representa sequías/calor sin datos verificables.
 */
(function(){"use strict";
const $=id=>document.getElementById(id),node=(tag,cls)=>{const v=document.createElement(tag);if(cls)v.className=cls;return v};
const layerSpec=[
 ["peligros","A. Peligros climáticos e hidrometeorológicos",[
  ["flood","Peligro de inundaciones",true,"Cartografía de susceptibilidad a inundaciones por lluvias fuertes publicada por CENEPRED (2021), capa 5090024. Representa predisposición territorial; no es una huella de inundación actual ni una alerta vigente.","CENEPRED · S05CP/MapServer/5090024"],
  ["rainIntense","Peligro de lluvias intensas",false,"Pendiente de conexión. Los productos históricos de precipitación y los pronósticos puntuales disponibles no constituyen por sí solos una capa espacial validada de peligro de lluvias intensas.",null],
  ["drought","Sequía y déficit hídrico",false,"Pendiente de conexión. El inventario histórico de emergencias por sequía no representa el déficit hídrico actual ni una superficie de sequía validada para Lambayeque.",null],
  ["heat","Temperaturas extremas",false,"Frecuencia histórica de olas de calor del SENAMHI/IDESEP y registro térmico puntual documentado en Jayanca (2024). La capa disponible representa extremos cálidos históricos; no es un pronóstico ni cubre por sí sola extremos fríos.","SENAMHI/IDESEP · WMS frecuencia histórica de olas de calor"]
 ]],
 ["agroclimatic","B. Condiciones agroclimáticas",[
  ["humidity","Exceso de humedad y condiciones favorables para enfermedades",false,"Pendiente de conexión. La humedad relativa ambiental a 2 m no equivale a horas reales de humedad foliar; todavía no existe una superficie geoespacial validada de mojado foliar y condiciones epidemiológicas.",null],
  ["wind","Vientos fuertes",false,"Pendiente de conexión. Los datos meteorológicos puntuales disponibles no constituyen una capa espacial regional validada de intensidad y peligro por vientos fuertes.",null]
 ]]
];
const spec=new Map(layerSpec.flatMap(g=>g[2].map(a=>[a[0],{id:a[0],title:a[1],default:a[2],meaning:a[3],source:a[4]||"",available:Boolean(a[4]),group:g[1]}])));
const state={on:Object.fromEntries([...spec].map(([k,v])=>[k,v.default])),basemap:{satellite:false},scene:null,selected:[],contains:null,legacy:null,
 points:[],pointsStatus:"pendiente",hydroLines:[],hydroStatus:"pendiente",hydroLoading:false,droughtStatus:"pendiente",heatStatus:"pendiente",activePoint:null, dragging:new Map(),gesture:null,view:[0,0,700,340],lastZoom:1};
const SIGRID="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer",
 SIGRID_HYDRO="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer",
 HAZARD="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer",
 ANA="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer",
 WORLD_IMAGERY="https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
 MINAM="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
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
    "SENAMHI/IDESEP · frecuencia histórica de olas de calor; no es pronóstico";
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
  refreshControls();applyLegacy();render();
 });
 const reset=node("button");reset.type="button";reset.textContent="Mapa base";
 reset.addEventListener("click",()=>{
  for(const key of Object.keys(state.on))state.on[key]=false;
  state.basemap.satellite=false;
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
  state.on[key]=ev.target.checked;applyLegacy();render();
  if(key==="heat"&&on("heat"))loadHeat();
 });
 const p=pane.querySelector(".oaf-ux29-maphead strong");if(p)p.textContent="Mapa político y temático de Lambayeque";
 const title=pane.querySelector(".oaf-ux29-top h2");if(title)title.textContent="Visor geográfico de Lambayeque";
 const lead=pane.querySelector(".oaf-ux29-top p");if(lead)lead.textContent="Activa las capas climáticas e hidrometeorológicas y las condiciones agroclimáticas disponibles. Las capas sin fuente espacial validada se identifican como pendientes de conexión.";
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
 // La lógica previa sigue a cargo de consultas MINAM/INGEMMET y los puntos de emergencia.
 const layer=$("oaf-ux25-raster");if(layer&&layer.value!=="none"){layer.value="none";layer.dispatchEvent(new Event("change",{bubbles:true}))}
 setCheck("oaf-ux25-minam",on("floodpoints"));
 setCheck("oaf-ux25-geologico",false);
 setCheck("oaf-ux26-agricultura",false); // Geocapa agrícola gestionada aquí para evitar duplicaciones.
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
async function loadHydro(){
 if(state.hydroLoading||state.hydroStatus!=="pendiente"||!state.scene)return;
 state.hydroLoading=true;state.hydroStatus="consultando ríos y quebradas del IGN";diagnosis();
 const b=state.scene.bounds;
 const groups=[
  {type:"drain",where:"tipo IN ('R','RN','RI','RS','AC')"},
  {type:"quebradas",where:"tipo IN ('Q','Q1','QB','QQ','QI','QS')"}
 ];
 // Consultas separadas: una clase no puede ocupar el límite de 2000 registros de la otra.
 const outcomes=await Promise.all(groups.map(async group=>{
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),16000);
  try{
   const params=new URLSearchParams({where:group.where,outFields:"objectid,tipo,r_q_text,nombre,fuente",
    returnGeometry:"true",geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
    geometryType:"esriGeometryEnvelope",spatialRel:"esriSpatialRelIntersects",
    inSR:"4326",outSR:"4326",geometryPrecision:"5",maxAllowableOffset:"0.003",
    resultRecordCount:"2000",f:"geojson"});
   const response=await fetch(SIGRID_HYDRO+"/6030200/query?"+params,{signal:controller.signal,cache:"no-store"});
   if(!response.ok)throw Error("HTTP "+response.status);
   const data=await response.json();
   if(data.error||!Array.isArray(data.features))throw Error("respuesta GeoJSON inválida");
   const lines=data.features.flatMap(feature=>{
    const geom=feature.geometry,props=feature.properties||{};
    if(!geom||!["LineString","MultiLineString"].includes(geom.type))return [];
    const traces=geom.type==="LineString"?[geom.coordinates]:geom.coordinates;
    return traces.filter(t=>Array.isArray(t)&&t.length>=2).map(coords=>({
     category:group.type,coords,name:props.r_q_text||props.nombre||props.tipo||"Sin nombre"
    }));
   });
   return {type:group.type,lines,partial:data.features.length===2000,error:null};
  }catch(e){return {type:group.type,lines:[],partial:false,error:String(e)}}
  finally{clearTimeout(timer)}
 }));
 state.hydroLines=outcomes.flatMap(r=>r.lines);
 state.hydroStatus=outcomes.map(r=>(r.type==="drain"?"Ríos":"Quebradas")+": "+
  (r.error?"servicio no disponible":r.lines.length+" trazos"+(r.partial?" (consulta parcial)":""))).join(" · ");
 state.hydroLoading=false;render();
}
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
 heading(box,"Lectura del mapa","La susceptibilidad indica predisposición y no un evento actual. Las capas pendientes no generan polígonos, puntos ni niveles de riesgo.");
 const failed=pane.querySelectorAll(".oaf-ux30-layer image[data-error=true]").length;
 if(failed)heading(box,"Una fuente cartográfica no respondió",failed+" servicio(s) no se pudieron cargar. Comprueba la disponibilidad del organismo de origen.");
}
function classify(value){
 const v=String(value||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
 if(v.includes("inundacion fluvial"))return "fluvial";
 if(v.includes("inundacion pluvial")||v.includes("precipitacion pluvial"))return "pluvial";
 if(v.includes("erosion fluvial"))return "erosion";
 if(v.includes("flujo")||v.includes("detrito")||v.includes("lodo"))return "detritos";
 return null;
}
async function loadHistory(){
 if(state.pointsStatus&&state.pointsStatus!=="pendiente")return;
 state.pointsStatus="cargando";
 const ctl=new AbortController(),timer=setTimeout(()=>ctl.abort(),16000);
 try{
  const b=state.scene?.bounds;if(!b)return;
  const q=new URLSearchParams({where:"nom_dep LIKE '%LAMBAYEQUE%'",outFields:"objectid,nom_dep,tipo_pel,fecha_doc,fuente",
   geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),geometryType:"esriGeometryEnvelope",
   spatialRel:"esriSpatialRelIntersects",inSR:"4326",outSR:"4326",returnGeometry:"true",resultRecordCount:"1800",f:"geojson"});
  const res=await fetch(SIGRID+"/6010100/query?"+q,{signal:ctl.signal,cache:"no-store"});
  if(!res.ok)throw Error("HTTP "+res.status);
  const data=await res.json();if(data.error||!Array.isArray(data.features))throw Error("Respuesta incompatible");
  const colors={fluvial:"#268ac4",pluvial:"#418bba",detritos:"#b8792b",erosion:"#ad4653"};
  const historicPoints=data.features.map(f=>{
    const p=f.properties||{},type=String(p.tipo_pel||"");
    const cat=classify(type),coords=f.geometry?.coordinates;
    if(!cat||f.geometry?.type!=="Point"||!Array.isArray(coords)||!coords.every(Number.isFinite))return null;
    return {coords,category:cat,color:colors[cat],label:type,year:p.fecha_doc||"2017",type,
     source:"INGEMMET, inventario geológico FENC 2017",sourceUrl:SIGRID+"/6010100",
     detail:"Registro histórico de peligro; no equivale a área inundada."};
  }).filter(Boolean);
  state.points=state.points.filter(p=>!["fluvial","pluvial","erosion","detritos"].includes(p.category)).concat(historicPoints);
  state.pointsStatus="INGEMMET 2017: "+historicPoints.length+" puntos del ámbito consultado";
 }catch(e){state.pointsStatus="fuente no disponible";}finally{clearTimeout(timer);render()}
}

/* UX31 · Inventarios históricos verificados y climatología SENAMHI */
const INDECI="https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6040000";
const SENAMHI_WMS="https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms";
const SENAMHI_LAYER="g_01_06:01_06_001_03_001_512_0000_00_00"; // frecuencia de olas de calor, verano
function heatWmsUrl(bounds){
 if(!bounds)return "";
 return SENAMHI_WMS+"?"+new URLSearchParams({
  SERVICE:"WMS",VERSION:"1.1.1",REQUEST:"GetMap",LAYERS:SENAMHI_LAYER,STYLES:"",
  SRS:"EPSG:4326",BBOX:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  WIDTH:"1100",HEIGHT:"535",FORMAT:"image/png",TRANSPARENT:"TRUE"
 });
}
function historicNorm(value){
 return String(value||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
}
async function loadDrought(){
 if(state.droughtStatus!=="pendiente")return;
 const b=state.scene?.bounds;if(!b)return;
 state.droughtStatus="consultando inventario INDECI 2003–2020";diagnosis();
 const query=new URLSearchParams({
  where:"nom_dep LIKE '%LAMBAYEQUE%' AND (fenomeno LIKE '%equ%' OR fenomeno LIKE '%EQU%')",
  outFields:"objectid_1,nom_dep,nom_prov,nom_dist,fecha,fenomeno,descrip,observ,fuente",
  geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  geometryType:"esriGeometryEnvelope",inSR:"4326",outSR:"4326",
  spatialRel:"esriSpatialRelIntersects",returnGeometry:"true",f:"geojson",resultRecordCount:"2000"
 });
 const controller=new AbortController(),limit=setTimeout(()=>controller.abort(),17500);
 try{
  const response=await fetch(INDECI+"/query?"+query,{signal:controller.signal,cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const data=await response.json();
  if(data.error||!Array.isArray(data.features))throw Error("GeoJSON inválido");
  const unique=new Set();
  const events=data.features.map(feature=>{
   const props=feature.properties||{},c=feature.geometry?.coordinates;
   if(feature.geometry?.type!=="Point"||!Array.isArray(c)||!c.every(Number.isFinite))return null;
   if(!historicNorm(props.fenomeno).includes("sequi"))return null;
   const id=props.objectid_1||[c.join(","),props.fecha,props.fenomeno].join("|");
   if(unique.has(id))return null;unique.add(id);
   return {coords:c,category:"drought",color:"#c9892c",label:"Sequía histórica · "+(props.nom_dist||props.nom_prov||"Lambayeque"),
    year:props.fecha||"2003–2020",type:String(props.fenomeno||"Sequía"),
    detail:String(props.descrip||props.observ||"Emergencia histórica registrada").slice(0,300),
    source:"INDECI, registro de emergencias 2003–2020",sourceUrl:INDECI};
  }).filter(Boolean);
  state.points=state.points.filter(p=>p.category!=="drought").concat(events);
  state.droughtStatus=events.length+" emergencias históricas con geometría"+(data.features.length>=2000?" (consulta limitada por el servidor)":"");
 }catch(e){state.droughtStatus="La consulta de INDECI no respondió; revisar enlace original."}
 finally{clearTimeout(limit);render();window.dispatchEvent(new Event("oaf:geodata"))}
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
 window.oafUx30RequestHistoricalClimate=()=>{
  if(window.oafUx35Wants?.drought&&state.droughtStatus==="pendiente")loadDrought();
  if(window.oafUx35Wants?.heat&&state.heatStatus==="pendiente")loadHeat();
 };
 
 // Instalar primero el enlace de render: los filtros anteriores pueden redibujar el mapa de inmediato.
 window.oafUx30AfterDraw=function(context){
  state.scene=context.scene;state.selected=context.selected||[];state.contains=context.contains||null;
  if(!state.mapInit){state.mapInit=true;navigation(state.scene.svg);}
  render();
  // La versión UX33 gestiona los registros geológicos y sus nombres, sin duplicar consultas.
  if(on("drought")&&state.droughtStatus==="pendiente")loadDrought();
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