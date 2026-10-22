/* UX29 · Dos visores multicapa inspirados en el patrón de navegación de SIGRID.
   Integración visual original OAF, sin reproducir código ni activos de SIGRID.
   El diagnóstico territorial no es una alerta ni una predicción hidráulica. */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const mk=(tag,cls)=>{const e=document.createElement(tag);if(cls)e.className=cls;return e};
const S="/"; // rutas relativas al portal
const SOURCES={
 cenepred:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer",
 mtc:"https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer",
 minam:"https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer",
 ana:"https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/FeatureServer/7"
};
const POINTS=[
 {name:"Chiclayo",lat:-6.7714,lon:-79.8409},
 {name:"Jayanca",lat:-6.39278,lon:-79.8228},
 {name:"Motupe",lat:-6.15083,lon:-79.7142},
 {name:"Olmos",lat:-5.98825,lon:-79.74723}
];
const daily={state:"pendiente",items:[],date:"",error:""};
const scenario={scene:null,ready:false,shown:false,selected:"",days:7,threshold:40,
 layer:{precip:true,suscept:true,nino:false,mass:false,roads:false,agri:false,basins:false},
 overlays:[],basins:[],basinsState:"pendiente"};
function svg(name,attrs){const e=document.createElementNS("http://www.w3.org/2000/svg",name);for(const [k,v] of Object.entries(attrs||{}))e.setAttribute(k,String(v));return e}
function htmlEscape(text){return String(text).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function mapUrl(server,layers,box,opacity){
 const params=new URLSearchParams({
  bbox:[box.minLon,box.minLat,box.maxLon,box.maxLat].join(","),
  bboxSR:"4326",imageSR:"4326",size:"1050,525",format:"png32",
  transparent:"true",dpi:"110",layers:"show:"+layers,f:"image"
 });
 return server+"/export?"+params;
}
function block(cls,html){const d=mk("div",cls);d.innerHTML=html;return d}
function diagram(type){
 const wrapper=mk("div","oaf-ux29-workbench");
 wrapper.id="oaf-ux29-"+type;
 wrapper.dataset.ux29Type=type;
 wrapper.innerHTML=
  '<div class="oaf-ux29-top"><span class="oaf-ux29-kicker">VISOR GEOGRÁFICO · OAF-LAMBAYEQUE</span>'+
  '<h2>'+(type==="territory"?"Territorio y riesgos climáticos":"Escenarios agroclimáticos y eventos potenciales")+'</h2>'+
  '<p>'+(type==="territory"?
  "Selecciona capas oficiales para explorar la exposición territorial y consulta una interpretación por tema. Los datos cartográficos conservan la autoría y fecha de sus instituciones.":
  "Combina la susceptibilidad territorial con pronósticos de lluvia por localidad y cartografía de apoyo. La respuesta del caudal y las áreas inundadas requieren modelos hidrológicos e hidráulicos validados.")+'</p></div>'+
  '<div class="oaf-ux29-layout">'+
  '<aside class="oaf-ux29-sidebar" aria-label="Árbol de capas del mapa"><div class="oaf-ux29-sidehead"><strong>CAPAS</strong><small>Marca o desmarca lo que deseas consultar</small></div><div class="oaf-ux29-tree"></div></aside>'+
  '<section class="oaf-ux29-mapcolumn" aria-label="Mapa interactivo"><div class="oaf-ux29-maphead"><strong>Mapa del territorio</strong><span>Región Lambayeque · Perú</span></div><div class="oaf-ux29-toolbar" aria-label="Controles del mapa"><button type="button" data-ux29-zoom="in" aria-label="Acercar mapa" title="Acercar mapa">+</button><button type="button" data-ux29-zoom="out" aria-label="Alejar mapa" title="Alejar mapa">−</button><button type="button" data-ux29-zoom="reset" aria-label="Restablecer extensión regional">Ajustar mapa</button><span>Capas consultables · OAF</span></div><div class="oaf-ux29-mapcontent"></div><div class="oaf-ux29-bottom"><span><i class="oaf-ux29-north">N ↑</i> Base regional simplificada · EPSG:4326</span><a href="https://sigrid.cenepred.gob.pe/sigridv3/mapa" target="_blank" rel="noopener noreferrer">Contrastar con SIGRID ↗</a></div></section>'+
  '<aside class="oaf-ux29-diagnosis" aria-label="Diagnóstico del territorio"><div class="oaf-ux29-diagnosishead"><span>ANÁLISIS CONTEXTUAL</span><h3>Diagnóstico del territorio</h3></div>'+
  '<div class="oaf-ux29-diagbody" role="status" aria-live="polite"></div>'+
  '<div class="oaf-ux29-diagextras"></div></aside></div>';
 return wrapper;
}
function details(parent,title,open=true){
 const d=mk("details","oaf-ux29-group");d.open=open;
 const summary=mk("summary");summary.textContent=title;d.append(summary);parent.append(d);return d;
}
function mountTerritory(){
 const root=$("oaf-territorio-riesgos"),grid=root?.querySelector(".oaf-ux24-grid");
 if(!root||!grid||$("oaf-ux29-territory"))return;
 const pane=diagram("territory");
 const introduction=root.querySelector(".oaf-ux24-intro");
 if(introduction)introduction.after(pane);else grid.before(pane);
 const tree=pane.querySelector(".oaf-ux29-tree"),content=pane.querySelector(".oaf-ux29-mapcontent");
 const geo=details(tree,"Peligros y susceptibilidad",true);
 const layers=$("oaf-ux25-controls");if(layers)geo.append(layers);
 const hazard=grid.children[1];if(hazard)geo.append(hazard);
 const region=details(tree,"Provincia, distrito y cuenca",true);
 const selection=$("oaf-ux26-filtros");if(selection)region.append(selection);
 const road=details(tree,"Red vial · MTC",false),rescue=details(tree,"Respuesta ante emergencias",false);
 const oldControls=$("oaf-ux28-panel")?.querySelector(".oaf-ux28-controls");
 if(oldControls){
  const sets=[...oldControls.querySelectorAll("fieldset")];
  if(sets[0])road.append(sets[0]);if(sets[1])rescue.append(sets[1]);
  oldControls.remove();
 }
 const mapCard=grid.children[0];
 if(mapCard){mapCard.classList.add("oaf-ux29-mainmapcard");content.append(mapCard);}
 if(!grid.children.length)grid.remove();
 const diag=pane.querySelector(".oaf-ux29-diagbody"),extra=pane.querySelector(".oaf-ux29-diagextras");
 const detail=$("oaf-ux25-detail"),rdetail=$("oaf-ux28-details");
 if(detail)extra.append(detail);
 if(rdetail)extra.append(rdetail);
 const state=$("oaf-ux28-status");if(state)extra.append(state);
 const refresh=()=>updateTerritory(pane);
 pane.addEventListener("change",refresh);
 pane.addEventListener("click",()=>requestAnimationFrame(refresh));
 for(const elem of [detail,rdetail]){
  if(elem)new MutationObserver(()=>requestAnimationFrame(refresh)).observe(elem,{childList:true,subtree:false});
 }
 refresh();
}
function valueOf(id){const e=$(id);return e?.selectedOptions?.[0]?.textContent?.trim()||"Todo Lambayeque"}
const descriptions={
 "5090024":"Susceptibilidad a inundaciones por lluvias fuertes, CENEPRED (2021). Representa predisposición, no superficie efectivamente inundada.",
 "5090023":"Susceptibilidad asociada a lluvias de eventos El Niño, CENEPRED (2021). No predice el episodio actual.",
 "5090022":"Susceptibilidad a movimientos en masa por lluvias fuertes, CENEPRED. Relevante para laderas y quebradas.",
 "5010502":"Susceptibilidad regional a inundación compilada por INGEMMET/SIGRID. Revisar escala y fecha del producto.",
 "none":"No se está mostrando una capa raster de peligro. El mapa mantiene límites y superposiciones seleccionadas."
};
function updateTerritory(pane){
 if(pane?.dataset?.ux30Active==='true')return; // UX30 owns the diagnosis when the unified territorial viewer is mounted.
 const d=pane.querySelector(".oaf-ux29-diagbody");if(!d)return;
 const layer=$("oaf-ux25-raster")?.value||"none";
 const territory=[valueOf("oaf-ux26-prov"),valueOf("oaf-ux26-dist"),valueOf("oaf-ux26-basin")];
 const isOn=id=>Boolean($(id)?.checked);
 const roads=[...document.querySelectorAll("[data-ux28-road]:checked")].map(e=>({
  national:"nacionales",regional:"departamentales",vecinal:"vecinales"}[e.dataset.ux28Road]));
 const emergency=[...document.querySelectorAll("[data-ux28-emergency]:checked")].map(e=>({
  hospital:"hospitales",posta:"puestos y centros de salud",policia:"comisarías",
  bomberos:"bomberos",defensa:"directorio Defensa Civil"}[e.dataset.ux28Emergency]));
 const geos=Number(!!isOn("oaf-ux25-minam"))+Number(!!isOn("oaf-ux25-geologico"));
 d.replaceChildren();
 const p=(head,body)=>{const section=mk("section","oaf-ux29-finding");const strong=mk("strong");strong.textContent=head;const text=mk("p");text.textContent=body;section.append(strong,text);d.append(section)};
 p("Ámbito seleccionado",territory.join(" · "));
 p("Cartografía de peligro",descriptions[layer]||"Consultar la ficha del servicio SIGRID.");
 const hazard=document.querySelector("#oaf-ux24-hazard-list button[aria-pressed=\"true\"]");
 if(hazard){const narrative=$("oaf-ux24-hazard-detail")?.textContent?.trim();
 p("Evento seleccionado: "+hazard.textContent.trim(),narrative||"Consulta los inventarios y antecedentes históricos de esta categoría.");}
 p("Capas superpuestas",[
  geos+" inventarios de peligros",
  isOn("oaf-ux26-agricultura")?"superficie agrícola MINAM":"agricultura desactivada",
  roads.length?roads.join(", "):"vías desactivadas",
  emergency.length?emergency.join(", "):"servicios de emergencia desactivados"
 ].join(" · ")+".");
 p("Interpretación para el territorio","Las coincidencias cartográficas identifican ámbitos para revisión técnica, pero no certifican daños, transitabilidad de vías ni capacidad de respuesta. Selecciona puntos del mapa para revisar el registro original.");
 const note=mk("p","oaf-ux29-diagnote");note.textContent="Categorías y fechas provienen de las entidades oficiales. Los filtros pueden depender de disponibilidad de sus geoservicios.";d.append(note);
}
function scenarioControls(workbench){
 const tree=workbench.querySelector(".oaf-ux29-tree");
 const met=details(tree,"Señales de lluvia pronosticada",true);
 met.innerHTML+='<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="precip" checked> Lluvia acumulada prevista · Open-Meteo</label>'+
 '<label class="oaf-ux29-field" for="oaf-ux29-days">Ventana temporal desde hoy<select id="oaf-ux29-days"><option value="3">Próximos 3 días</option><option value="7" selected>Próximos 7 días</option></select></label>'+
 '<label class="oaf-ux29-field" for="oaf-ux29-threshold">Umbral descriptivo de precipitación acumulada (mm)<select id="oaf-ux29-threshold"><option value="20">20 mm</option><option value="40" selected>40 mm</option><option value="70">70 mm</option><option value="100">100 mm</option></select></label>';
 const peril=details(tree,"Peligros preexistentes · SIGRID",true);
 peril.innerHTML+='<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="suscept" checked> Susceptibilidad a inundaciones · CENEPRED</label>'+
 '<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="nino"> Susceptibilidad histórica El Niño</label>'+
 '<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="mass"> Movimientos en masa por lluvia</label>';
 const rivers=details(tree,"Cuencas y respuesta hidrológica",true);
 rivers.innerHTML+='<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="basins"> Polígonos de cuencas · ANA</label>'+
 '<div class="oaf-ux29-limit"><strong>Incremento de caudales</strong><p>Sin pronóstico de caudal o altura de río validado en el OAF. Se requiere información hidrométrica y modelamiento por cuenca.</p>'+
 '<a href="https://www.senamhi.gob.pe/" target="_blank" rel="noopener noreferrer">Monitoreo oficial SENAMHI ↗</a></div>';
 const exposure=details(tree,"Infraestructura y exposición",false);
 exposure.innerHTML+='<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="roads"> Vías MTC · redes 8/9/10</label>'+
 '<label class="oaf-ux29-check"><input type="checkbox" data-ux29-layer="agri"> Superficie agrícola MINAM (referencia 2018)</label>';
 const links=details(tree,"Modelos del OAF y fuentes",false);
 links.innerHTML='<a class="oaf-ux29-doclink" href="#oaf-ux14-rf-semana">Comparación semanal Random Forest ↗</a>'+
 '<a class="oaf-ux29-doclink" href="#oaf-ux14-rf-mes">Modelo mensual y paisajes ↗</a>'+
 '<a class="oaf-ux29-doclink" href="https://sigrid.cenepred.gob.pe/sigridv3/escenarios" target="_blank" rel="noopener noreferrer">Escenarios oficiales CENEPRED ↗</a>';
 workbench.addEventListener("change",ev=>{
  const input=ev.target;
  if(input?.matches("[data-ux29-layer]"))scenario.layer[input.dataset.ux29Layer]=input.checked;
  if(input?.id==="oaf-ux29-days")scenario.days=Number(input.value);
  if(input?.id==="oaf-ux29-threshold")scenario.threshold=Number(input.value);
  renderScenario();
 });
}
function attachScenario(){
 const root=$("oaf-escenarios-riesgo-agroclimatico");
 if(!root||$("oaf-ux29-scenario"))return;
 const pane=diagram("scenario");
 const intro=root.querySelector(".oaf-ux24-intro");
 if(intro)intro.after(pane);else root.prepend(pane);
 scenarioControls(pane);
 const container=pane.querySelector(".oaf-ux29-mapcontent");
 container.innerHTML='<div class="oaf-ux29-scenemap"><svg id="oaf-ux29-forecast-map" viewBox="0 0 700 380" role="img" aria-label="Mapa experimental de precipitación por localidad, susceptibles históricas y cuencas"><text x="350" y="180" text-anchor="middle" fill="#426f59">Cargando mapa de Lambayeque…</text></svg>'+
 '<div class="oaf-ux29-mapcaption">La lluvia se muestra en localidades de referencia; no se interpolan áreas entre estaciones ni se predicen polígonos de inundación.</div></div>'+
 '<div id="oaf-ux29-scene-status" role="status" class="oaf-ux29-scenestatus">Preparando cartografía de referencia…</div>';
 const extra=pane.querySelector(".oaf-ux29-diagextras");
 extra.innerHTML='<div class="oaf-ux29-calculation"><strong>Ámbito del diagnóstico</strong><p id="oaf-ux29-selected">Toda la región · Lambayeque</p></div>'+
 '<p class="oaf-ux29-links"><a href="https://open-meteo.com/en/docs" target="_blank" rel="noopener noreferrer">Procedencia Open-Meteo ↗</a> · <a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend" target="_blank" rel="noopener noreferrer">Leyenda SIGRID ↗</a></p>';
 root.dataset.oafUx29Prepared="true";
 loadScenarioOutline();
}
function pointProjection(geo){
 const polygons=geo.features?.filter(x=>x.geometry?.type==="Polygon"||x.geometry?.type==="MultiPolygon").flatMap(f=>{
  const g=f.geometry;return g.type==="Polygon"?[g.coordinates]:g.coordinates;
 })||[];
 const rings=polygons.map(p=>p[0]).filter(r=>r?.length>=3);
 const pts=rings.flat(),xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);
 if(!pts.length||pts.some(p=>p.length<2||!p.every(Number.isFinite)))throw Error("contorno sin coordenadas válidas");
 const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);
 const factor=Math.cos(((minY+maxY)/2)*Math.PI/180);
 const scale=Math.min(560/((maxX-minX)*factor),264/(maxY-minY));
 const x=lon=>350+(lon-(minX+maxX)/2)*factor*scale;
 const y=lat=>170-(lat-(minY+maxY)/2)*scale;
 return {x,y,rings,bounds:{minLon:(minX+maxX)/2-350/(factor*scale),maxLon:(minX+maxX)/2+350/(factor*scale),
 minLat:(minY+maxY)/2-170/scale,maxLat:(minY+maxY)/2+170/scale}};
}
async function loadScenarioOutline(){
 try{
  const r=await fetch("datos/zonificacion_8n/limite_lambayeque_referencial.geojson",{cache:"no-store"});
  if(!r.ok)throw Error("HTTP "+r.status);
  const geo=await r.json();scenario.scene=pointProjection(geo);
  scenario.ready=true;renderScenario();
 }catch(e){
  const node=$("oaf-ux29-scene-status");if(node)node.textContent="No se pudo consultar el contorno referencial regional: "+e.message+". Comprueba la fuente.";
 }
}
async function loadRain(){
 if(daily.state!=="pendiente")return;
 daily.state="cargando";diagnosisScenario();
 const tasks=POINTS.map(async place=>{
  const params=new URLSearchParams({latitude:String(place.lat),longitude:String(place.lon),daily:"precipitation_sum,precipitation_probability_max",
   timezone:"America/Lima",forecast_days:"7"});
  const url="https://api.open-meteo.com/v1/forecast?"+params;
  const ctl=new AbortController(),id=setTimeout(()=>ctl.abort(),13000);
  try{
   const r=await fetch(url,{signal:ctl.signal,cache:"no-store"});
   if(!r.ok)throw Error("HTTP "+r.status);
   const j=await r.json();
   if(j.error||!Array.isArray(j.daily?.precipitation_sum)||!Array.isArray(j.daily?.time))throw Error("series incompletas");
   const rain=j.daily.precipitation_sum.map(v=>v===null||v===undefined||v===""?NaN:Number(v));
   if(rain.length<3||rain.some(v=>!Number.isFinite(v)||v<0))throw Error("lluvia diaria no válida");
   return {...place,dates:j.daily.time.slice(0,7),rain:rain.slice(0,7),
    precipProbability:j.daily.precipitation_probability_max?.slice(0,7)||[],updated:Date.now()};
  }finally{clearTimeout(id)}
 });
 const all=await Promise.allSettled(tasks);
 daily.items=all.filter(r=>r.status==="fulfilled").map(r=>r.value);
 daily.error=all.filter(r=>r.status==="rejected").map(r=>String(r.reason)).slice(0,2).join(" · ");
 daily.state=daily.items.length?(daily.items.length===POINTS.length?"listo":"parcial"):"error";
 daily.date=new Date().toLocaleString("es-PE",{timeZone:"America/Lima",day:"2-digit",month:"2-digit",year:"numeric",hour:"2-digit",minute:"2-digit"});
 renderScenario();
}
function scenarioSvgImage(parent,layer,source,opacity,cls){
 const scene=scenario.scene,im=svg("image",{
  href:mapUrl(source,layer,scene.bounds),x:0,y:0,width:700,height:340,opacity,
  preserveAspectRatio:"none","pointer-events":"none"});
 im.classList.add("oaf-ux29-maplayer",cls);
 im.addEventListener("error",()=>{
  const n=$("oaf-ux29-scene-status");if(n)n.textContent="Una capa externa no respondió. Utiliza SIGRID/IDEP para consultar la fuente original.";
 });
 parent.append(im);
}
function basinPath(geometry,scene){
 const groups=geometry?.type==="Polygon"?[geometry.coordinates]:geometry?.type==="MultiPolygon"?geometry.coordinates:[];
 return groups.flatMap(poly=>poly.map(ring=>ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(1)+" "+scene.y(p[1]).toFixed(1)).join(" ")+" Z")).join(" ");
}
async function loadBasins(){
 if(scenario.basinsState!=="pendiente"||!scenario.scene)return;
 scenario.basinsState="cargando";
 const b=scenario.scene.bounds;
 const q=new URLSearchParams({where:"1=1",outFields:"NOMBRE,CODIGO",returnGeometry:"true",outSR:"4326",
  f:"geojson",geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  geometryType:"esriGeometryEnvelope",inSR:"4326",spatialRel:"esriSpatialRelIntersects",resultRecordCount:"200"});
 const ctl=new AbortController(),timeout=setTimeout(()=>ctl.abort(),15000);
 try{
  const res=await fetch(SOURCES.ana+"/query?"+q,{cache:"no-store",signal:ctl.signal});
  if(!res.ok)throw Error("HTTP "+res.status);
  const data=await res.json();if(data.error||!Array.isArray(data.features))throw Error("GeoJSON inválido");
  scenario.basins=data.features.filter(f=>f.geometry&&["Polygon","MultiPolygon"].includes(f.geometry.type));
  scenario.basinsState="listo";
 }catch(e){scenario.basinsState="error"}finally{clearTimeout(timeout);renderScenario()}
}
function styleAmount(mm){return mm>=scenario.threshold?"#c25d3b":mm>=scenario.threshold*.5?"#d9a042":"#257d96"}
function rainSum(p){return p.rain.slice(0,scenario.days).reduce((s,v)=>s+v,0)}
function renderScenario(){
 if(typeof window.oafUx35Render==="function")return window.oafUx35Render();
 const scene=scenario.scene,target=$("oaf-ux29-forecast-map");
 if(!scene||!target)return;
 target.replaceChildren();
 target.append(svg("rect",{x:0,y:0,width:700,height:380,fill:"#ecf3ef"}));
 const defs=svg("defs",{}),clip=svg("clipPath",{id:"oaf-ux29-region-clip",clipPathUnits:"userSpaceOnUse"});
 for(const ring of scene.rings){const d=ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(1)+" "+scene.y(p[1]).toFixed(1)).join(" ")+" Z";clip.append(svg("path",{d,"fill-rule":"evenodd","clip-rule":"evenodd"}));}
 defs.append(clip);target.append(defs);
 const g=svg("g",{"clip-path":"url(#oaf-ux29-region-clip)"});target.append(g);
 if(scenario.layer.suscept)scenarioSvgImage(g,"5090024",SOURCES.cenepred,".68","oaf-ux29-hazard");
 if(scenario.layer.nino)scenarioSvgImage(g,"5090023",SOURCES.cenepred,".40","oaf-ux29-el-nino");
 if(scenario.layer.mass)scenarioSvgImage(g,"5090022",SOURCES.cenepred,".35","oaf-ux29-mass");
 if(scenario.layer.agri)scenarioSvgImage(g,"1",SOURCES.minam,".29","oaf-ux29-agri");
 if(scenario.layer.roads)scenarioSvgImage(g,"8,9,10",SOURCES.mtc,".87","oaf-ux29-roads");
 if(scenario.layer.basins){
  if(scenario.basinsState==="pendiente")loadBasins();
  for(const b of scenario.basins){
   const d=basinPath(b.geometry,scene);if(!d)continue;
   const node=svg("path",{d,fill:"none",stroke:"#2674ac","stroke-width":1.8,"stroke-dasharray":"6 3","pointer-events":"none"});
   g.append(node);
  }
 }
 for(const ring of scene.rings){
  const d=ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(1)+" "+scene.y(p[1]).toFixed(1)).join(" ")+" Z";
  g.append(svg("path",{d,fill:"#c6e8d1","fill-opacity":".1",stroke:"#3b795c","stroke-width":2.3,"pointer-events":"none"}));
 }
 if(scenario.layer.precip){
  for(const place of daily.items){
   const amount=rainSum(place),cx=scene.x(place.lon),cy=scene.y(place.lat);
   const circle=svg("circle",{cx,cy,r:12,fill:styleAmount(amount),stroke:"#fff","stroke-width":2,tabindex:0,role:"button",
    "aria-label":place.name+": "+amount.toFixed(1)+" mm en "+scenario.days+" días"});
   circle.addEventListener("click",()=>{scenario.selected=place.name;diagnosisScenario();highlightSelected(target)});
   circle.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();circle.dispatchEvent(new Event("click"))}});
   circle.dataset.place=place.name;
   const title=svg("title",{});title.textContent=place.name+" · "+amount.toFixed(1)+" mm ("+scenario.days+" días)";circle.append(title);
   g.append(circle);
   const lbl=svg("text",{x:cx+15,y:cy+4,fill:"#174b3f","font-size":12,"font-weight":750,
    stroke:"#f0f8f4","stroke-width":3,"paint-order":"stroke", "pointer-events":"none"});
   lbl.textContent=place.name;g.append(lbl);
  }
 }
 const caption=svg("text",{x:350,y:363,fill:"#416357","font-size":13,"text-anchor":"middle"});
 caption.textContent="Susceptibilidad histórica + lluvia pronosticada en puntos. SIN pronóstico hidráulico.";target.append(caption);
 const north=svg("text",{x:650,y:36,fill:"#276449","font-size":15,"font-weight":800});north.textContent="N ↑";target.append(north);
 highlightSelected(target);
 const status=$("oaf-ux29-scene-status");
 if(status)status.textContent="Lluvia externa: "+({pendiente:"sin consultar",cargando:"consultando",listo:"datos recibidos",parcial:"carga parcial",error:"no disponible"}[daily.state]||daily.state)+
 (daily.date?" · consulta "+daily.date:"")+
 (scenario.layer.basins?" · cuencas ANA: "+scenario.basinsState:"")+".";
 diagnosisScenario();
}
function highlightSelected(svgElement){
 for(const circle of svgElement.querySelectorAll("circle[data-place]")){
  const active=circle.dataset.place===scenario.selected;
  circle.setAttribute("stroke",active?"#173d33":"#fff");
  circle.setAttribute("stroke-width",active?4:2);
  circle.setAttribute("r",active?14:12);
 }
}
function diagnosisScenario(){
 if(typeof window.oafUx35Diagnosis==="function")return window.oafUx35Diagnosis();
 const pane=$("oaf-ux29-scenario");if(!pane)return;
 const d=pane.querySelector(".oaf-ux29-diagbody");if(!d)return;
 const selected=daily.items.find(i=>i.name===scenario.selected);
 const scored=daily.items.map(i=>({name:i.name,mm:rainSum(i)})).sort((a,b)=>b.mm-a.mm);
 const counts=scored.filter(p=>p.mm>=scenario.threshold);
 const act=Object.entries(scenario.layer).filter(([k,v])=>v).map(([k])=>({
  precip:"lluvia prevista",suscept:"susceptibilidad fluvial/pluvial",nino:"escenario histórico El Niño",
  mass:"movimientos en masa",roads:"red vial",agri:"superficie agrícola",basins:"cuencas ANA"}[k]));
 const section=(h,t)=>{const box=mk("section","oaf-ux29-finding"),a=mk("strong"),b=mk("p");
  a.textContent=h;b.textContent=t;box.append(a,b);d.append(box)};
 d.replaceChildren();
 section("Capas activadas",act.join(" · ")||"Ninguna capa seleccionada");
 section("Referencia temporal",scenario.days+" días · Umbral descriptivo "+scenario.threshold+" mm acumulados (definido por el usuario, NO umbral de alerta).");
 if(daily.state==="error"){
  section("Disponibilidad de datos","No se pudo verificar la lluvia pronosticada de Open-Meteo. No se identifican señales meteorológicas ni se emiten conclusiones cuantitativas.");
 }else if(daily.state==="pendiente"||daily.state==="cargando"){
  section("Pronóstico de precipitación","El visor consultará 4 localidades de referencia cuando se abra la subpestaña.");
 }else{
  const summary=scored.map(i=>i.name+": "+i.mm.toFixed(1)+" mm").join(" · ");
  section("Lluvia prevista por localidad",summary+". Son pronósticos externos puntuales, no totales observados ni un mapa de precipitación continua.");
  section("Señal de revisión meteorológica",
   counts.length?counts.map(p=>p.name).join(", ")+" alcanza(n) el umbral descriptivo seleccionado. Esto no implica inundación ni representa una alerta oficial.":
    "Ninguna localidad consultada alcanza el umbral descriptivo seleccionado. Esto NO descarta lluvias fuertes en otros sectores.");
  if(selected){
   const max=Math.max(...selected.rain.slice(0,scenario.days));
   section("Detalle seleccionado: "+selected.name, "Acumulado estimado "+rainSum(selected).toFixed(1)+
    " mm; día con mayor lluvia "+max.toFixed(1)+" mm. Fuente: Open-Meteo; actualización de consulta "+daily.date+".");
  }
  if(daily.state==="parcial")section("Cobertura parcial","Solo "+daily.items.length+" de cuatro localidades respondieron. No se generaliza a toda Lambayeque.");
 }
 section("Posible respuesta de ríos y quebradas",
  "Una precipitación intensa en una cuenca puede favorecer escorrentía y aumentos de caudal. El OAF no ha estimado niveles, caudales (m³/s), tiempos de concentración ni crecidas: se necesitan series hidrométricas y un modelo hidrológico validado.");
 section("Posibilidad de inundaciones",
  "La capa SIGRID representa áreas históricamente susceptibles. Su coincidencia visual con lluvia prevista es orientativa; no define extensión, profundidad, fecha ni probabilidad de inundación futura.");
 section("Recomendación de interpretación",
  "Contrasta el pronóstico meteorológico con avisos SENAMHI/ENFEN, la vigilancia de caudales y los mapas oficiales de CENEPRED antes de adoptar decisiones de emergencia.");
 const label=$("oaf-ux29-selected");if(label)label.textContent=selected?selected.name+" · "+selected.lat.toFixed(3)+", "+selected.lon.toFixed(3):"4 localidades de referencia · Lambayeque";
}
function watchScenario(){
 const root=$("oaf-escenarios-riesgo-agroclimatico");if(!root)return;
 const isVisible=()=>Boolean(root.closest('[data-page="autor"]:not([hidden])'))&&!root.hidden;
 const wake=()=>{if(!isVisible())return;scenario.shown=true;if(daily.state==="pendiente")loadRain();};
 window.addEventListener("hashchange",()=>requestAnimationFrame(wake));
 const tab=$("oaf-ux24-tabs-autor");
 tab?.addEventListener("click",()=>setTimeout(wake,0));
 setTimeout(wake,300);
}
function mapToolbar(){
 document.querySelectorAll(".oaf-ux29-workbench").forEach(panel=>{
  const svgId=panel.dataset.ux29Type==="territory"?"oaf-ux24-region-map":"oaf-ux29-forecast-map";
  const element=()=>$(svgId);
  const fullWidth=700,fullHeight=panel.dataset.ux29Type==="territory"?340:380;
  panel.querySelectorAll("[data-ux29-zoom]").forEach(button=>button.addEventListener("click",()=>{
   const map=element();if(!map)return;
   const raw=(map.getAttribute("viewBox")||"0 0 700 "+fullHeight).trim().split(/[,\s]+/).map(Number);
   if(raw.length!==4||raw.some(v=>!Number.isFinite(v)))return;
   const [x,y,w,h]=raw;
   if(button.dataset.ux29Zoom==="reset"){map.setAttribute("viewBox","0 0 700 "+fullHeight);return}
   const scale=button.dataset.ux29Zoom==="in"?.8:1.25;
   const nw=Math.min(fullWidth,Math.max(140,w*scale)),nh=Math.min(fullHeight,Math.max(fullHeight*.2,h*scale));
   const nx=Math.min(fullWidth-nw,Math.max(0,x+(w-nw)/2));
   const ny=Math.min(fullHeight-nh,Math.max(0,y+(h-nh)/2));
   map.setAttribute("viewBox",[nx.toFixed(2),ny.toFixed(2),nw.toFixed(2),nh.toFixed(2)].join(" "));
  }));
 });
}
function init(){
 window.oafUx29ScenarioApi={
  get:()=>({scene:scenario.scene,daily,locations:POINTS,days:scenario.days,threshold:scenario.threshold}),
  loadRain:()=>loadRain(),
  refresh:()=>renderScenario()
 };
 mountTerritory();attachScenario();mapToolbar();watchScenario();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();