/* OAF UX30 · Visor territorial único con árbol SIG multicapa y diagnóstico explicativo.
 * Las capas SIGRID son de organismos oficiales; las capas de susceptibilidad no son
 * pronósticos de zonas inundadas. No representa sequías/calor sin datos verificables.
 */
(function(){"use strict";
const $=id=>document.getElementById(id),node=(tag,cls)=>{const v=document.createElement(tag);if(cls)v.className=cls;return v};
const layerSpec=[
 ["base","Mapa base y límites políticos",[
  ["base","Mapa base de Lambayeque",true,"Visualiza el contorno regional simplificado de Lambayeque que sirve como referencia para ubicar las demás capas. No sustituye límites políticos oficiales ni mapas catastrales."],
  ["departamento","Límite departamental",true,"Límite político referencial de Lambayeque del INEI (2013). Ayuda a reconocer el territorio; no es una delimitación legal para un predio."],
  ["provincia","Límites provinciales",true,"Delimitaciones de las tres provincias de Lambayeque publicadas en SIGRID con base INEI. Sirven para estudiar la ubicación de los peligros."],
  ["distrito","Límites distritales",false,"Separa distritos y muestra nombres donde el servicio oficial lo permite. La precisión depende de la escala cartográfica INEI (2018)."]
 ]],
 ["peligros","Peligros y susceptibilidad",[
  ["regional","Susceptibilidad regional a inundaciones",true,"Muestra las zonas más o menos propensas a inundarse, según la cartografía regional elaborada por INGEMMET. No representa inundaciones actuales ni caudales pronosticados."],
  ["movmasa","Movimientos en masa por lluvia fuerte",false,"Señala laderas y vertientes susceptibles a deslizamientos y otros movimientos durante lluvias intensas. Es información de predisposición territorial de CENEPRED."],
  ["fluvial","Inundación fluvial · puntos documentados",false,"Ubica registros históricos de inundación ocasionada por el desborde de ríos y cauces; los puntos proceden de evaluaciones geológicas del Niño Costero 2017."],
  ["pluvial","Inundación pluvial · puntos documentados",false,"Ubica registros de acumulación o anegamiento asociado a lluvias, incluso sin desbordamiento de ríos. Son observaciones históricas, no polígonos de inundación futura."],
  ["detritos","Quebradas y flujos de detritos · puntos",false,"Muestra registros geológicos de flujos de detritos y lodo. En quebradas, las lluvias intensas pueden movilizar piedras, tierra y agua; requiere vigilancia local."],
  ["erosion","Erosión fluvial · puntos documentados",false,"Señala lugares con antecedentes de desgaste o socavación de riberas, potencialmente relevantes para terrenos agrícolas, puentes y canales."],
  ["floodpoints","Puntos críticos de inundación · MINAM",false,"Inventario georreferenciado de puntos críticos publicado por MINAM. Un punto es un lugar identificado para revisión; no representa la superficie completa del peligro."],
  ["geopoints","Zonas críticas geológicas · INGEMMET",false,"Inventario de zonas críticas geológicas de INGEMMET difundido por SIGRID. Permite identificar sectores documentados de inestabilidad."],
  ["drought","Sequía y déficit hídrico · diagnóstico",false,"La sequía es un déficit persistente de agua o lluvia respecto al comportamiento habitual. Esta selección habilita una explicación, pero no dibuja una zonificación de sequía: aún falta una capa regional validada."],
  ["heat","Anomalías de calor · diagnóstico",false,"Una anomalía de calor supone temperaturas superiores a una referencia climatológica. Esta selección no dibuja áreas cálidas porque aún no se ha integrado una geocapa regional validada."]
 ]],
 ["hidro","Cuencas, ríos y drenajes",[
  ["basin","Cuencas hidrográficas ANA",false,"Las cuencas agrupan superficies cuyo escurrimiento se dirige hacia una red de drenaje común. Son útiles para relacionar lluvias aguas arriba con sectores aguas abajo."],
  ["drain","Ríos, quebradas y drenajes IGN",false,"Se visualiza la red hidrográfica de la Carta Nacional a escala 1:100 000. No indica el caudal actual ni confirma que un cauce tenga agua."],
  ["quebradas","Quebradas y cauces menores",false,"Visualiza los trazos de quebradas y cauces de la cartografía del IGN, incluidos cursos estacionales. No predice activaciones ni flujos de detritos."]
 ]],
 ["vias","Red vial MTC",[
  ["nacional","Carreteras nacionales",false,"Carreteras de la red vial nacional registrada por el MTC. La línea dibujada no confirma que una carretera sea transitable durante una emergencia."],
  ["departamental","Carreteras departamentales",false,"Vías que conectan centros y territorios provinciales según el inventario oficial del MTC. No contiene cortes o bloqueos en tiempo real."],
  ["vecinal","Caminos vecinales y rurales",false,"Red vecinal o rural que conecta localidades y espacios productivos. Su disponibilidad efectiva puede cambiar por lluvias, erosión o deslizamientos."]
 ]],
 ["emergencias","Respuesta ante emergencias",[
  ["hospital","Hospitales",false,"Establecimientos clasificados como hospitales en la cartografía institucional. El mapa no confirma disponibilidad actual de camas ni atención de urgencias."],
  ["posta","Centros y puestos de salud",false,"Establecimientos de salud del primer nivel de atención, según los registros disponibles. Su clasificación debe contrastarse con la institución prestadora."],
  ["policia","Comisarías y Policía",false,"Puntos de comisarías georreferenciados. Su ubicación no indica efectivos disponibles ni tiempos de respuesta."],
  ["bomberos","Compañías de bomberos",false,"Ubicaciones referenciales de compañías de bomberos. La cartografía no acredita dotación, operatividad ni tiempo estimado de atención."]
 ]],
 ["agri","Territorio agrícola y exposición",[
  ["agricola","Superficie agrícola · MINAM 2018",false,"Representa áreas agrícolas cartografiadas por MINAM con referencia de 2018. No identifica el cultivo sembrado actualmente."],
  ["exposicion","Exposición agrícola a inundaciones · cruce visual",false,"Superpone superficie agrícola y susceptibilidad regional. Permite identificar coincidencias para revisión, pero no calcula hectáreas inundadas ni pérdidas."],
  ["agroflood","Áreas agrícolas en zona susceptible · cruce visual",false,"Muestra conjuntamente agricultura y susceptibilidad fluvial. El cruce es visual; no delimita inundación prevista ni cuantifica superficie afectada."],
  ["inundacionregion","Susceptibilidad fluvial · polígonos INGEMMET",false,"Capa vectorial de polígonos de susceptibilidad fluvial a escala nacional 1:1 000 000. Cubre el ámbito regional por consulta; representa predisposición, no área que se inundará en un evento próximo."]
 ]]
];
const spec=new Map(layerSpec.flatMap(g=>g[2].map(a=>[a[0],{id:a[0],title:a[1],default:a[2],meaning:a[3],group:g[1]}])));
const state={on:Object.fromEntries([...spec].map(([k,v])=>[k,v.default])),scene:null,selected:[],contains:null,legacy:null,
 points:[],pointsStatus:"pendiente", activePoint:null, dragging:new Map(),gesture:null,view:[0,0,700,340],lastZoom:1};
const SIGRID="https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer",
 HAZARD="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer",
 INGEMMET="https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer",
 MINAM="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
const on=k=>!!state.on[k];
function sv(tag,attrs){const e=document.createElementNS("http://www.w3.org/2000/svg",tag);Object.entries(attrs||{}).forEach(([k,v])=>e.setAttribute(k,String(v)));return e}
function text(el,content){el.textContent=String(content);return el}
function overlaySrc(service,layers){
 const b=state.scene?.bounds;if(!b)return "";
 return service+"/export?"+new URLSearchParams({bbox:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  bboxSR:"4326",imageSR:"4326",size:"1100,535",format:"png32",transparent:"true",dpi:"130",
  layers:"show:"+layers,f:"image"});
}
function makeTree(){
 const pane=$("oaf-ux29-territory"),tree=pane?.querySelector(".oaf-ux29-tree");
 if(!tree||$("oaf-ux30-layer-tree"))return;
 pane.dataset.ux30Active="true";
 const legacy=node("div","oaf-ux30-legacy");legacy.id="oaf-ux30-legacy";
 while(tree.firstChild)legacy.append(tree.firstChild);
 pane.append(legacy);state.legacy=legacy;
 const groups=node("div","oaf-ux30-layer-tree");groups.id="oaf-ux30-layer-tree";
 for(const [id,label,entries] of layerSpec){
  const d=node("details","oaf-ux30-section");d.open=id==="base"||id==="peligros";
  const head=node("summary");head.append(text(node("span"),label));d.append(head);
  const wrap=node("div","oaf-ux30-options");
  for(const [key,title,checked] of entries){
   const item=node("label","oaf-ux30-option"),check=node("input");check.type="checkbox";check.dataset.ux30Layer=key;check.checked=checked;
   const span=text(node("span"),title),tiny=node("small");
   if(key==="drought"||key==="heat")tiny.textContent="Diagnóstico · sin polígono";
   if(key==="exposicion"||key==="agroflood")tiny.textContent="Cruce visual";
   if(key==="fluvial"||key==="pluvial"||key==="detritos"||key==="erosion")tiny.textContent="Puntos históricos 2017";
   item.append(check,span);if(tiny.textContent)item.append(tiny);wrap.append(item);
  }
  d.append(wrap);groups.append(d);
 }
 tree.replaceChildren(groups);
 const filters=$("oaf-ux26-filtros"),area=node("details","oaf-ux30-section oaf-ux30-area");area.open=true;
 const head=node("summary");head.textContent="Filtrar por provincia, distrito y cuenca";area.append(head);
 if(filters){area.append(filters);filters.classList.add("oaf-ux30-filter-widget");}
 tree.prepend(area);
 const controls=node("div","oaf-ux30-layer-actions");
 const all=node("button");all.type="button";all.textContent="Limpiar selección";
 all.addEventListener("click",()=>{for(const k in state.on)state.on[k]=["base","departamento","provincia"].includes(k);refreshControls();applyLegacy();render();});
 const reset=node("button");reset.type="button";reset.textContent="Mapa base";reset.addEventListener("click",()=>{state.on=Object.fromEntries([...spec].map(([k])=>[k,["base","departamento","provincia"].includes(k)]));refreshControls();applyLegacy();render();});
 controls.append(all,reset);tree.prepend(controls);
 tree.addEventListener("change",ev=>{
  const key=ev.target?.dataset?.ux30Layer;if(!key)return;
  state.on[key]=ev.target.checked;applyLegacy();render();
 });
 const p=pane.querySelector(".oaf-ux29-maphead strong");if(p)p.textContent="Mapa político y temático de Lambayeque";
 const title=pane.querySelector(".oaf-ux29-top h2");if(title)title.textContent="Visor geográfico de Lambayeque";
 const lead=pane.querySelector(".oaf-ux29-top p");if(lead)lead.textContent="Selecciona las capas en el panel izquierdo y explora el mapa. El diagnóstico explica cada selección en lenguaje sencillo y diferencia peligros documentados de estimaciones pendientes.";
 const board=pane.querySelector(".oaf-ux29-diagbody");if(board)board.setAttribute("aria-live","polite");
 if(!pane.querySelector("#oaf-ux30-map-help")){
  const help=text(node("p","oaf-ux30-map-help"),"Navegación: arrastra para mover, usa la rueda para acercar y dos dedos para ampliar en celular. Selecciona los puntos para consultar su información.");
  pane.querySelector(".oaf-ux29-mapcolumn .oaf-ux29-mapcontent")?.prepend(help);
 }
}
function refreshControls(){
 document.querySelectorAll("[data-ux30-layer]").forEach(c=>c.checked=on(c.dataset.ux30Layer));
}
function setCheck(id,checked){
 const e=$(id);if(!e||e.checked===checked)return;
 e.checked=checked;e.dispatchEvent(new Event("change",{bubbles:true}));
}
function applyLegacy(){
 // La lógica previa sigue a cargo de consultas MINAM/INGEMMET y los puntos de emergencia.
 const layer=$("oaf-ux25-raster");if(layer&&layer.value!=="none"){layer.value="none";layer.dispatchEvent(new Event("change",{bubbles:true}))}
 setCheck("oaf-ux25-minam",on("floodpoints"));
 setCheck("oaf-ux25-geologico",on("geopoints"));
 setCheck("oaf-ux26-agricultura",false); // Geocapa agrícola gestionada aquí para evitar duplicaciones.
 for(const [id,key] of [["national","nacional"],["regional","departamental"],["vecinal","vecinal"]]){
  const e=document.querySelector('[data-ux28-road="'+id+'"]');if(e&&e.checked!==on(key)){e.checked=on(key);e.dispatchEvent(new Event("change",{bubbles:true}))}
 }
 for(const key of ["hospital","posta","policia","bomberos"]){
  const e=document.querySelector('[data-ux28-emergency="'+key+'"]');if(e&&e.checked!==on(key)){e.checked=on(key);e.dispatchEvent(new Event("change",{bubbles:true}))}
 }
 const d=document.querySelector('[data-ux28-emergency="defensa"]');if(d?.checked){d.checked=false;d.dispatchEvent(new Event("change",{bubbles:true}))}
}
function render(){
 const scene=state.scene,pane=$("oaf-ux29-territory");if(!scene||!pane)return;
 const map=scene.svg;
 map.querySelectorAll(".oaf-ux30-layer").forEach(x=>x.remove());
 const defs=sv("defs",{class:"oaf-ux30-layer"});
 const clip=sv("clipPath",{id:"oaf-ux30-clip-region",clipPathUnits:"userSpaceOnUse"});
 const boundary=map.querySelector('[data-oaf-ux24-boundary="true"]');
 if(boundary){boundary.style.opacity=on("base")?"1":"0";}
 if(boundary)clip.append(sv("path",{d:boundary.getAttribute("d")}));
 defs.append(clip);map.append(defs);
 const back=sv("g",{class:"oaf-ux30-layer","clip-path":"url(#oaf-ux30-clip-region)"});
 const front=sv("g",{class:"oaf-ux30-layer"});
 const add=(service,layers,opacity,name)=>{
  const image=sv("image",{href:overlaySrc(service,layers),x:0,y:0,width:700,height:340,opacity,
   preserveAspectRatio:"none","pointer-events":"none"});image.dataset.title=name;image.dataset.ux30Server=service;image.dataset.ux30Ids=String(layers);
  image.addEventListener("error",()=>{image.dataset.error="true";diagnosis()});
  back.append(image);
 };
 if(on("regional")||on("exposicion")||on("agroflood"))add(HAZARD,5010502,.77,"Susceptibilidad regional");
 if(on("movmasa"))add(HAZARD,5090022,.42,"Movimientos en masa");
 if(on("inundacionregion"))add(INGEMMET,0,.54,"Susceptibilidad fluvial en polígonos");
 if(on("agricola")||on("exposicion")||on("agroflood"))add(MINAM,1,.35,"Superficie agrícola 2018");
 const political=["departamento","provincia","distrito"].filter(on).map(k=>({departamento:6020100,provincia:6020200,distrito:6020300}[k]));
 if(political.length)add(SIGRID,political.join(","),.8,"Límites administrativos");
 if(on("basin"))add(SIGRID,6030100,.55,"Cuencas hidrográficas ANA");
 if(on("drain")||on("quebradas"))add(SIGRID,6030200,.84,"Red hidrográfica IGN 1:100 000");
 for(const p of state.points){
  if(!on(p.category))continue;
  const [lon,lat]=p.coords;
  if(state.selected?.length&&state.contains&&!state.selected.every(k=>state.contains(k.geo,[lon,lat])))continue;
  const x=scene.x(lon),y=scene.y(lat);
  if(x<0||x>700||y<0||y>340)continue;
  const circle=sv("circle",{cx:x,cy:y,r:4.3,fill:p.color,stroke:"#fff","stroke-width":1.2,
   tabindex:"0",role:"button","aria-label":p.label});
  circle.classList.add("oaf-ux30-feature");circle.dataset.ux30Radius="4.3";
  circle.addEventListener("click",()=>{state.activePoint=p;diagnosis()});
  circle.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();state.activePoint=p;diagnosis()}});
  const ttl=sv("title");ttl.textContent=p.label;circle.append(ttl);front.append(circle);
 }
 // Insert underneath independent road and emergency point markers.
 const before=map.querySelector("circle.oaf-ux25-point, circle.oaf-ux28-emergency-marker");
 map.insertBefore(back,before||null);map.append(front);
 diagnosis();adjustMarkerSizes();
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
 heading(box,"Ámbito de consulta",area+" · "+district+" · "+watershed+". Las capas y recuentos reflejan este filtro cuando su fuente dispone de geometrías.");
 const chosen=[...spec].filter(([id])=>on(id));
 if(!chosen.length)heading(box,"Sin capas activas","Marca una o varias casillas para ver la explicación de cada fuente.");
 for(const [id,def] of chosen){
  const status=["drought","heat"].includes(id)?"Sin geometría regional oficial integrada":"Capa seleccionada";
  heading(box,def.title,def.meaning,status);
 }
 const types=["fluvial","pluvial","detritos","erosion"].filter(on);
 if(types.length){
  const c=state.points.filter(p=>types.includes(p.category)&&(!state.selected?.length||!state.contains||state.selected.every(k=>state.contains(k.geo,p.coords)))).length;
  heading(box,"Inventario histórico de peligros","Hay "+c+" puntos descargados de las categorías seleccionadas dentro del filtro. Corresponden a registros históricos de 2017 y no necesariamente al total de puntos críticos actuales.",state.pointsStatus||state.pointsStatus);
 }
 if(on("exposicion")||on("agroflood"))heading(box,"Importante sobre agricultura",
  "La superposición de los mapas de agricultura y susceptibilidad identifica coincidencias visuales. No es una intersección vectorial calibrada ni calcula hectáreas en riesgo o posibles pérdidas.");
 const failed=pane.querySelectorAll(".oaf-ux30-layer image[data-error=true]").length;
 if(failed)heading(box,"Algunas capas externas no respondieron",
  failed+" capa(s) no se pudieron cargar desde los geoservicios. Consulta la fuente oficial en Metadatos y trazabilidad.");
 if(state.activePoint){
  const p=state.activePoint;heading(box,"Punto consultado: "+p.label,
   "Tipo: "+(p.type||"no consignado")+". Fuente: INGEMMET/CENEPRED, evaluación geológica de El Niño Costero 2017. "+
   "Referencia: "+(p.year||"2017")+". Este punto no determina la extensión del peligro.");
 }
 heading(box,"Lectura del mapa",
  "Un área susceptible puede necesitar evaluación preventiva. Las capas de puntos, polígonos y redes viales se levantaron en distintas fechas. La coincidencia espacial por sí sola no demuestra que un evento esté ocurriendo o vaya a ocurrir.");
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
  state.points=data.features.map(f=>{
    const p=f.properties||{},type=String(p.tipo_pel||"");
    const cat=classify(type),coords=f.geometry?.coordinates;
    if(!cat||f.geometry?.type!=="Point"||!Array.isArray(coords)||!coords.every(Number.isFinite))return null;
    return {coords,category:cat,color:colors[cat],label:type,year:p.fecha_doc||"2017",type};
  }).filter(Boolean);
  state.pointsStatus="cargados: "+state.points.length;
 }catch(e){state.pointsStatus="fuente no disponible";}finally{clearTimeout(timer);render()}
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
    img.setAttribute("href",overlaySrc(img.dataset.ux30Server,img.dataset.ux30Ids));
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
   img.setAttribute("x",v[0]);img.setAttribute("y",v[1]);
   img.setAttribute("width",v[2]);img.setAttribute("height",v[3]);
   img.setAttribute("href",service+"/export?"+query);
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
 refreshDetailMap();
}
function adjustMarkerSizes(){
 const map=$("oaf-ux24-region-map");if(!map)return;
 const scale=getView(map)[2]/700;
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
 '<ul><li><a href="'+SIGRID+'" target="_blank" rel="noopener noreferrer">SIGRID/CENEPRED · límites políticos, cuencas, hidrografía e inventario histórico FENC 2017</a></li>'+
 '<li><a href="'+HAZARD+'" target="_blank" rel="noopener noreferrer">SIGRID/CENEPRED · susceptibilidad regional a inundaciones y movimientos en masa</a></li>'+
 '<li><a href="'+INGEMMET+'/0" target="_blank" rel="noopener noreferrer">INGEMMET · susceptibilidad fluvial representada por polígonos a escala 1:1 000 000</a></li>'+
 '<li><a href="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer" target="_blank" rel="noopener noreferrer">MTC/IDEP · carreteras nacionales, departamentales y vecinales</a></li>'+
 '<li><a href="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer" target="_blank" rel="noopener noreferrer">IGN/IDEP · hospitales, puestos de salud, comisarías y bomberos</a></li>'+
 '<li><a href="'+MINAM+'/1" target="_blank" rel="noopener noreferrer">MINAM · superficie agrícola nacional, referencia 2018</a></li>'+
 '<li><a href="https://www.senamhi.gob.pe/site/vigilancia-climatica/" target="_blank" rel="noopener noreferrer">SENAMHI · vigilancia climática, sequías y temperaturas</a></li><li><a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_EXPOSICION_INUNDACIONES_UX27.md" target="_blank" rel="noopener noreferrer">OAF UX27 · análisis cuantitativo agrícola y alcance de las 1 234 ha documentadas por CENEPRED</a></li><li><a href="datos/riesgos_ux27/indicadores_cenepred_2025.csv" download>Indicadores CENEPRED para nueve distritos de Lambayeque (CSV)</a></li></ul>'+
 '<p>Los datos de FENC 2017 son inventarios de lugares afectados, no mapas de inundación actual. La susceptibilidad regional es un raster, mientras que la capa INGEMMET de inundación fluvial utiliza polígonos de susceptibilidad. La exposición agrícola es visual y no una superficie calculada.</p>'+
 '<a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_VISOR_TERRITORIAL_UX30.md" target="_blank" rel="noopener noreferrer">Leer metodología detallada de la fase UX30 ↗</a>';
 tab.append(section);
}
function init(){
 makeTree();metadata();
 // Instalar primero el enlace de render: los filtros anteriores pueden redibujar el mapa de inmediato.
 window.oafUx30AfterDraw=function(context){
  state.scene=context.scene;state.selected=context.selected||[];state.contains=context.contains||null;
  if(!state.mapInit){state.mapInit=true;navigation(state.scene.svg);}
  render();if(state.pointsStatus==="pendiente")loadHistory();
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