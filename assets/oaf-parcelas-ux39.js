/* UX39 · Geovisor de parcelas OAF-Lambayeque.
 * Entrada puntual en WGS84/UTM delegada a OAFTerritory.
 * GeoJSON/KML y trazado sobre SVG; superficies aproximadas, NO deslinde catastral.
 * Los datos oficiales solo se califican tras una respuesta verificable del geoservicio.
 */
(()=>{"use strict";
const $=id=>document.getElementById(id),KEY="oaf-ux39-parcela-20261027-",scopes=["territorio","escenarios"];
const parcels={territorio:null,escenarios:null},drafts={territorio:[],escenarios:[]},drawing={territorio:false,escenarios:false},revision={territorio:0,escenarios:0},tokens={territorio:{risk:0,model:0,agro:0,audit:0},escenarios:{risk:0,model:0,agro:0,audit:0}};
const sv=(t,props={})=>{const e=document.createElementNS("http://www.w3.org/2000/svg",t);Object.entries(props).forEach(([k,v])=>e.setAttribute(k,String(v)));return e;};
const node=(t,cls,txt)=>{const e=document.createElement(t);if(cls)e.className=cls;if(txt!==undefined)e.textContent=String(txt);return e;};
const fmt=(n,d=2)=>Number.isFinite(n)?n.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}):"—";
const ringclose=ring=>ring[0][0]===ring.at(-1)[0]&&ring[0][1]===ring.at(-1)[1]?ring:[...ring,ring[0]];
function project(k){return k==="territorio"?window.oafUx30Context?.()?.scene:window.oafUx29ScenarioApi?.get?.()?.scene}
function image(k){return $(k==="territorio"?"oaf-ux24-region-map":"oaf-ux29-forecast-map")}
function fromXY(scene,x,y){
 const bounds=scene?.bounds;if(!bounds)throw Error("El visor regional aún no tiene escala geográfica");
 const lx=scene.x(bounds.minLon),rx=scene.x(bounds.maxLon),ty=scene.y(bounds.maxLat),by=scene.y(bounds.minLat);
 return [bounds.minLon+(x-lx)*(bounds.maxLon-bounds.minLon)/(rx-lx),
  bounds.maxLat-(y-ty)*(bounds.maxLat-bounds.minLat)/(by-ty)];
}
function countVertices(polys){return polys.reduce((total,p)=>total+p.reduce((n,r)=>n+r.length,0),0);}
function parsePolygons(geometry){
 if(!geometry||!["Polygon","MultiPolygon"].includes(geometry.type))throw Error("Se requiere un polígono GeoJSON, no puntos ni líneas");
 const polys=geometry.type==="Polygon"?[geometry.coordinates]:geometry.coordinates;
 if(!Array.isArray(polys)||!polys.length||polys.length>20)throw Error("Cantidad de polígonos no admisible (máximo 20)");
 if(countVertices(polys)>3000)throw Error("La parcela excede 3 000 vértices. Simplifica el archivo antes de cargarlo");
 return polys.map(poly=>{
  if(!Array.isArray(poly)||!poly.length||poly.length>30)throw Error("Número de anillos no válido");
  return poly.map(raw=>{
   if(!Array.isArray(raw)||raw.length<3)throw Error("El anillo debe contener al menos tres vértices");
   const ring=raw.map(v=>{
    if(!Array.isArray(v)||v.length<2)throw Error("Coordenada GeoJSON no válida");
    const [lon,lat]=v.map(Number);window.OAFTerritory?.validatePoint?.(lat,lon);
    if(!Number.isFinite(lat)||!Number.isFinite(lon)||lon< -80.8||lon> -79||lat< -7.3||lat> -5.1)throw Error("La parcela debe ubicarse en el ámbito regional de Lambayeque");
    return [lon,lat];
   });
   return ringclose(ring);
  });
 });
}
function signedArea(ring,cos){
 let sum=0;for(let i=0;i<ring.length-1;i++)sum+=(ring[i][0]*cos*ring[i+1][1]-ring[i+1][0]*cos*ring[i][1]);
 return sum/2;
}
function surface(polys){
 const vertices=polys.flat(2),meanLat=vertices.reduce((a,p)=>a+p[1],0)/vertices.length,cos=Math.cos(meanLat*Math.PI/180);
 const meterLon=111320*cos,meterLat=110574;
 let total=0;
 for(const polygon of polys){const outer=Math.abs(signedArea(polygon[0],cos));const holes=polygon.slice(1).reduce((acc,r)=>acc+Math.abs(signedArea(r,cos)),0);total+=Math.max(0,outer-holes);}
 return total*111320*110574/10000; // signedArea ya incluye el factor coseno
}
function inRing(lon,lat,ring){
 let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const [xi,yi]=ring[i],[xj,yj]=ring[j],cross=(yi>lat)!==(yj>lat)&&lon<(xj-xi)*(lat-yi)/(yj-yi)+xi;
  if(cross)inside=!inside;
 }return inside;
}
function contains(polys,lon,lat){return polys.some(poly=>inRing(lon,lat,poly[0])&&!poly.slice(1).some(h=>inRing(lon,lat,h)));}
function interior(polys){
 let sx=0,sy=0,n=0;for(const poly of polys){for(const [lon,lat] of poly[0].slice(0,-1)){sx+=lon;sy+=lat;n++;}}
 const lon=sx/n,lat=sy/n;if(contains(polys,lon,lat))return {lon,lat};
 const ring=polys[0][0];for(let k=0;k<ring.length-1;k++){
  const lo=ring[k][0]*.98+lon*.02,la=ring[k][1]*.98+lat*.02;
  if(contains(polys,lo,la))return {lon:lo,lat:la};
 }
 return {lon:ring[0][0],lat:ring[0][1]};
}
function limits(polys){
 const a=polys.flat(2);return {minLon:Math.min(...a.map(p=>p[0])),maxLon:Math.max(...a.map(p=>p[0])),minLat:Math.min(...a.map(p=>p[1])),maxLat:Math.max(...a.map(p=>p[1]))};
}
function ui(k){return $("oaf-parcel-"+k);}
function report(k,msg){const r=ui(k)?.querySelector("[data-ux39-report]");if(r)r.textContent=msg;const heading=ui(k)?.querySelector(".oaf-parcel-fold>summary strong");if(heading)heading.textContent=parcels[k]?"Parcela: "+parcels[k].name+" · "+fmt(parcels[k].ha,2)+" ha":"Delimitar parcela";}
function save(k){try{sessionStorage.setItem(KEY+k,JSON.stringify(parcels[k]));}catch(_){report(k,"La geometría puede visualizarse, pero no pudo conservarse en esta sesión.");}}
function restore(k){try{const raw=JSON.parse(sessionStorage.getItem(KEY+k));if(raw?.geometry){const polygons=parsePolygons(raw.geometry);parcels[k]={name:String(raw.name||"Parcela").slice(0,80),polygons,geometry:{type:"MultiPolygon",coordinates:polygons},ha:surface(polygons)};}}catch(_){}}
function draw(k){
 const svg=image(k),scene=project(k);if(!svg||!scene?.bounds)return;
 const old=svg.querySelector("#oaf-ux39-geom-"+k);old?.remove();
 const points=drawing[k]&&drafts[k].length?[[ringclose(drafts[k])]]:parcels[k]?.polygons;
 if(!points)return;
 const d=points.flatMap(poly=>poly.map(ring=>ring.map((xy,i)=>(i?"L":"M")+scene.x(xy[0]).toFixed(2)+" "+scene.y(xy[1]).toFixed(2)).join(" ")+" Z")).join(" ");
 const g=sv("g",{id:"oaf-ux39-geom-"+k,"pointer-events":"none"});
 const shape=sv("path",{d,fill:parcels[k]?"#e5a443":"none","fill-opacity":".19",stroke:"#bd7430","stroke-width":"3","stroke-linejoin":"round","stroke-dasharray":drawing[k]?"7 4":"none","fill-rule":"evenodd"});g.append(shape);
 if(drawing[k])for(const [lon,lat] of drafts[k])g.append(sv("circle",{cx:scene.x(lon),cy:scene.y(lat),r:4,fill:"#b85a2d",stroke:"#fff","stroke-width":2}));
 if(parcels[k]){const p=interior(parcels[k].polygons);const pin=sv("circle",{cx:scene.x(p.lon),cy:scene.y(p.lat),r:6,fill:"#b9532c",stroke:"#fff","stroke-width":2});
  const caption=sv("title");caption.textContent=parcels[k].name+" · "+fmt(parcels[k].ha)+" ha (aproximadas)";pin.append(caption);g.append(pin);}
 svg.append(g);
}
function setPolygon(k,geometry,name){
 const polygons=parsePolygons(geometry),ha=surface(polygons);
 if(!Number.isFinite(ha)||ha<0.00005||ha>200000)throw Error("Superficie fuera del intervalo admitido (0,5 m² a 200 000 ha)");
 const title=String(name||"Parcela productiva").slice(0,80).trim()||"Parcela productiva";
 parcels[k]={name:title,polygons,geometry:{type:"MultiPolygon",coordinates:polygons},ha};
 drafts[k]=[];drawing[k]=false;save(k);draw(k);revision[k]++;Object.keys(tokens[k]).forEach(q=>tokens[k][q]++);
 const p=interior(polygons);
 try{window.OAFTerritory?.setPoint?.(k,{lat:p.lat,lon:p.lon,name:title});}catch(e){report(k,"Polígono cargado; revisa la ubicación: "+e.message);}
 report(k,title+" · superficie aproximada "+fmt(ha,3)+" ha · "+countVertices(polygons)+" vértices. Se mantiene una geometría vectorial sobre las capas del visor.");
 refresh(k);document.dispatchEvent(new CustomEvent("oaf:parcel-update",{detail:{scope:k,parcel:{name:title,ha,geometry:parcels[k].geometry}}}));
}
function geoJSON(text){
 const j=JSON.parse(text);
 if(j.type==="FeatureCollection"){const features=(j.features||[]).filter(x=>["Polygon","MultiPolygon"].includes(x.geometry?.type));
  if(features.length!==1)throw Error("El archivo debe contener exactamente una parcela de tipo Polygon/MultiPolygon");
  return {geometry:features[0].geometry,name:features[0].properties?.nombre||features[0].properties?.name};}
 if(j.type==="Feature")return {geometry:j.geometry,name:j.properties?.nombre||j.properties?.name};
 return {geometry:j,name:null};
}
function parseKML(raw){
 const xml=new DOMParser().parseFromString(raw,"application/xml");
 if(xml.querySelector("parsererror"))throw Error("Archivo KML mal formado");
 const polygons=[...xml.getElementsByTagName("Polygon")];
 if(!polygons.length||polygons.length>20)throw Error("KML sin polígonos o con más de 20 polígonos");
 const parseRing=root=>{
  const coord=root?.getElementsByTagName("coordinates")?.[0]?.textContent||"";
  const points=coord.trim().split(/\s+/).map(t=>t.split(",").slice(0,2).map(Number));
  return points;
 };
 const coords=polygons.map(poly=>{
  const outer=poly.getElementsByTagName("outerBoundaryIs")[0];
  const holes=[...poly.getElementsByTagName("innerBoundaryIs")];
  if(!outer)throw Error("KML sin límite exterior");
  return [parseRing(outer),...holes.map(parseRing)];
 });
 const title=xml.getElementsByTagName("name")[0]?.textContent||"Parcela KML";
 return {geometry:{type:"MultiPolygon",coordinates:coords},name:title};
}
async function fileRead(k,file){
 if(!file||file.size>1024*1024)throw Error("El archivo debe ser GeoJSON o KML y pesar como máximo 1 MB");
 const raw=await file.text(),parsed=/\.kml$/i.test(file.name)?parseKML(raw):geoJSON(raw);
 setPolygon(k,parsed.geometry,parsed.name||file.name.replace(/\.(geojson|json|kml)$/i,""));
}
function mapClick(k,event){
 if(!drawing[k])return;
 if(event.target.closest('[data-oaf-action]'))return;
 const svg=image(k),sc=project(k);if(!svg||!sc?.bounds)return;
 const m=svg.getScreenCTM();if(!m)return;
 const p=svg.createSVGPoint();p.x=event.clientX;p.y=event.clientY;
 const pt=p.matrixTransform(m.inverse()),loc=fromXY(sc,pt.x,pt.y);
 if(!Number.isFinite(loc[0])||!Number.isFinite(loc[1]))return;
 try{window.OAFTerritory?.validatePoint?.(loc[1],loc[0]);}catch(e){report(k,"Vértice fuera del ámbito admitido");return;}
 if(drafts[k].length>=400){report(k,"Máximo 400 vértices por trazado. Cierra el polígono.");return;}
 drafts[k].push(loc);draw(k);report(k,drafts[k].length+" vértices trazados. Pulsa «Cerrar polígono» cuando termines.");
 event.preventDefault();event.stopPropagation();
}
function attachMap(k){
 const svg=image(k);if(!svg||svg.dataset.ux39Map)return false;svg.dataset.ux39Map="yes";
 svg.addEventListener("click",e=>mapClick(k,e),true);
 const watcher=new MutationObserver(()=>{
  const q=parcels[k]||drafts[k].length;
  if(q&&!svg.querySelector("#oaf-ux39-geom-"+k))draw(k);
 });
 watcher.observe(svg,{childList:true});
 draw(k);return true;
}
function listenLayers(k){
 const parent=$(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
 parent?.addEventListener("change",e=>{
  if(e.target?.matches('[data-ux30-layer],[data-ux35-layer],[data-ux29-layer],[data-ux35-key],#oaf-ux25-raster')){updateActive(k);scheduleAudit(k);}
 });
}
function activeLayers(k){
 const root=$(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
 const all=[...root?.querySelectorAll("input:checked")||[]].filter(input=>input.closest(".oaf-ux29-sidebar"));
 return all.map(input=>input.closest("label")?.textContent?.trim()?.replace(/\s+/g," ").slice(0,65)).filter(Boolean).slice(0,35);
}
function updateActive(k){
 const out=ui(k)?.querySelector("[data-ux39-layers]");if(!out)return;
 const items=activeLayers(k);out.textContent=items.length?"Capas activas en este visor ("+items.length+"): "+items.join(" · "):"No hay capas activadas para contrastar.";
}
function mount(k){
 const anchor=$("oaf-area-"+k),pane=$(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
 if(!anchor||!pane||ui(k))return false;
 const wrapper=node("section","oaf-parcel-panel");wrapper.id="oaf-parcel-"+k;
 wrapper.innerHTML='<details class="oaf-parcel-fold"><summary><strong>Delimitar parcela</strong><span> · Dibujar / GeoJSON / KML</span></summary>'+
  '<div class="oaf-parcel-actions"><button type="button" data-action="start">Dibujar parcela</button><button type="button" data-action="finish" disabled>Cerrar polígono</button><button type="button" data-action="undo" disabled>Deshacer vértice</button><button type="button" data-action="clear">Borrar polígono</button><button type="button" data-action="export">Exportar GeoJSON</button></div>'+
  '<label class="oaf-parcel-upload">Importar parcela GeoJSON / KML <input type="file" accept=".geojson,.json,.kml,application/geo+json" data-ux39-file></label>'+
  '<p class="oaf-parcel-info" data-ux39-report role="status" aria-live="polite">Dibuja en el mapa o importa un archivo WGS84.</p>'+
  '<p class="oaf-parcel-caveat">Superficie orientativa; no sustituye una delimitación catastral.</p>'+
  '<details class="oaf-parcel-layers"><summary>Capas activas</summary><p class="oaf-parcel-info" data-ux39-layers></p></details>'+
  '<details class="oaf-parcel-advanced"><summary>Herramientas de análisis</summary>'+
  '<div class="oaf-parcel-actions"><button type="button" data-action="risk">Evaluar intersecciones y superficie aproximada</button><button type="button" data-action="model">Modelo climático por sector · validar</button><button type="button" data-action="agro">Contexto agroclimático y fitosanitario</button><button type="button" data-action="audit">Auditar fuentes</button><button type="button" data-action="send">Usar punto en Cultivos y sanidad</button></div>'+
  '<div data-ux39-risk class="oaf-parcel-results" aria-live="polite"></div>'+
  '<div data-ux39-model class="oaf-parcel-results" aria-live="polite"></div>'+
  '<div data-ux39-agro class="oaf-parcel-results" aria-live="polite"></div>'+
  '<div data-ux39-audit class="oaf-parcel-results" aria-live="polite"></div>'+
  '</details></details>';
 const mapcolumn=pane.querySelector(".oaf-ux29-mapcolumn");
 const content=mapcolumn?.querySelector(".oaf-ux29-mapcontent");
 if(!content)return false;
 // Territorio: la parcela sigue bajo el bloque de mapa.
 // Escenarios: el perímetro y el diagnóstico van inmediatamente tras el SVG,
 // antes de UX36 (hidrología) y UX37 (validación de caudales).
 if(k==="escenarios"){
  const scenarioMap=content.querySelector(".oaf-ux29-scenemap");
  if(scenarioMap)scenarioMap.after(wrapper);else content.prepend(wrapper);
  const hydro=content.querySelector("#oaf-ux36-panel");
  if(hydro){
   const quality=content.querySelector("#oaf-ux37-panel");
   let tail=quality||hydro;
   for(const id of ["oaf-ux35-outlook","oaf-ux35-mapstatus"]){
    const item=content.querySelector("#"+id);
    if(item){tail.after(item);tail=item;}
   }
  }
 }else content.after(wrapper);
 if(k==="territorio"){
  const help=content.querySelector("#oaf-ux30-map-help"),map=content.querySelector(".oaf-ux29-mainmapcard");
  if(map){
   const frame=map.querySelector(".oaf-ux24-mapframe");
   if(frame)map.prepend(frame);
   if(help)map.after(help);
  }
 }
 // Permite consultar las capas con el mapa más grande sin alterar su SVG.
 const toolbar=mapcolumn.querySelector(".oaf-ux29-toolbar");
 if(toolbar&&!toolbar.querySelector(".oaf-map-expand")){
  const enlarge=node("button","oaf-map-expand","Ampliar mapa");
  enlarge.type="button";enlarge.setAttribute("aria-pressed","false");
  enlarge.title="Ampliar el visor geográfico";
  const reset=()=>{
   mapcolumn.classList.remove("oaf-map-expanded");
   enlarge.textContent="Ampliar mapa";enlarge.setAttribute("aria-pressed","false");
  };
  enlarge.addEventListener("click",()=>{
   const expanded=mapcolumn.classList.toggle("oaf-map-expanded");
   enlarge.textContent=expanded?"Cerrar vista ampliada":"Ampliar mapa";
   enlarge.setAttribute("aria-pressed",String(expanded));
  });
  document.addEventListener("keydown",ev=>{if(ev.key==="Escape")reset();});
  toolbar.append(enlarge);
 }
 // Evaluación de punto disponible bajo el mapa, sin saturar la cabecera.
 const originalData=anchor.querySelector(".oaf-area-data");
 if(originalData&&!$("oaf-area-point-details-"+k)){
  const pointDetails=node("details","oaf-point-diagnosis");
  pointDetails.id="oaf-area-point-details-"+k;
  pointDetails.innerHTML='<summary>Diagnóstico espacial del punto</summary>';
  pointDetails.append(originalData);
  wrapper.after(pointDetails);
 }
 const get=n=>wrapper.querySelector('[data-action="'+n+'"]');
 get("start").addEventListener("click",()=>{
  wrapper.querySelector(".oaf-parcel-fold").open=true;
  drawing[k]=true;drafts[k]=[];get("start").disabled=true;get("finish").disabled=false;get("undo").disabled=false;
  report(k,"Haz clic en el mapa para colocar los vértices del perímetro, al menos tres. No arrastres para dibujar.");
 });
 get("undo").addEventListener("click",()=>{drafts[k].pop();draw(k);report(k,drafts[k].length+" vértices trazados.");});
 get("finish").addEventListener("click",()=>{
  if(drafts[k].length<3){report(k,"Se necesitan al menos 3 vértices.");return;}
  try{setPolygon(k,{type:"Polygon",coordinates:[drafts[k]]},"Parcela trazada");get("start").disabled=false;get("finish").disabled=true;get("undo").disabled=true;}
  catch(e){report(k,e.message);}
 });
 get("export").addEventListener("click",()=>{
  const parcel=parcels[k];if(!parcel){report(k,"Primero dibuja o importa un polígono.");return;}
  const json=JSON.stringify({type:"FeatureCollection",features:[{type:"Feature",properties:{nombre:parcel.name,area_aproximada_ha:Number(parcel.ha.toFixed(4)),fuente:"usuario",sistema:"WGS84 EPSG:4326",aviso:"No es deslinde catastral"},geometry:parcel.geometry}]},null,2);
  const blob=new Blob([json],{type:"application/geo+json"}),url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download="parcela-oaf-"+k+".geojson";document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
 });
 get("clear").addEventListener("click",()=>{parcels[k]=null;drafts[k]=[];drawing[k]=false;get("start").disabled=false;get("finish").disabled=true;get("undo").disabled=true;save(k);draw(k);report(k,"Polígono borrado de este visor. El punto geográfico se conserva hasta pulsar «Quitar ubicación».");refresh(k);});
 wrapper.querySelector("[data-ux39-file]").addEventListener("change",async e=>{
  const file=e.target.files?.[0];if(!file)return;
  try{await fileRead(k,file);get("start").disabled=false;get("finish").disabled=true;get("undo").disabled=true;}catch(err){report(k,"Importación rechazada: "+err.message);}
  e.target.value="";
 });
 get("risk").addEventListener("click",()=>risk(k));
 get("model").addEventListener("click",()=>model(k));
 get("agro").addEventListener("click",()=>agro(k));
 get("audit").addEventListener("click",()=>audit(k));
 get("send").addEventListener("click",()=>{
  const p=window.OAFTerritory?.getActivePoint?.(k);
  if(!p){report(k,"Primero introduce coordenadas o delimita la parcela.");return;}
  try{window.OAFTerritory?.setPoint?.("cultivos",p);report(k,"Punto enviado a Cultivos y sanidad. Puedes abrir esa pestaña para seleccionar el cultivo y el organismo.");}
  catch(e){report(k,"No se pudo copiar la ubicación: "+e.message);}
 });
 restore(k);if(parcels[k])report(k,"Parcela de la sesión restaurada: "+parcels[k].name+" ("+fmt(parcels[k].ha)+" ha aproximadas).");
 attachMap(k);listenLayers(k);updateActive(k);if(parcels[k]){draw(k);refresh(k);}
 return true;
}
function refresh(k){
 const selectors=["risk","model","agro","audit"];for(const s of selectors)if(ui(k)){const t=ui(k).querySelector("[data-ux39-"+s+"]");if(t)t.textContent="";}
 updateActive(k);draw(k);
}
function setText(k,section,text){const d=ui(k)?.querySelector("[data-ux39-"+section+"]");if(d)d.textContent=text;return d;}
function current(k){const poly=parcels[k],point=window.OAFTerritory?.getActivePoint?.(k);return {poly,point};}
function auditState(k,name,result){
 const report=ui(k)?.querySelector("[data-ux39-audit]");if(!report)return;
 const line=node("p",null,name+": "+result);report.append(line);
}
const CENEPRED_BASE="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer";
const LAYERS=[
 {name:"INGEMMET · susceptibilidad a inundación fluvial (vector, 1:1 000 000)",kind:"vector",
  url:"https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0/query",
  metadataUrl:"https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0?f=json",
  territorio:["inundacionregion","regional"],escenarios:["futureFlood","regional","suscept"]},
 {name:"CENEPRED · susceptibilidad a movimientos en masa por lluvias fuertes (ráster)",kind:"raster",layerId:5090022,
  url:CENEPRED_BASE+"/identify",metadataUrl:CENEPRED_BASE+"/5090022?f=json",
  territorio:["movmasa"],escenarios:["futureMass","mass"]},
 {name:"CENEPRED · susceptibilidad a inundaciones por lluvias fuertes (ráster)",kind:"raster",layerId:5090024,
  url:CENEPRED_BASE+"/identify",metadataUrl:CENEPRED_BASE+"/5090024?f=json",
  territorio:["regional","inundacionregion"],escenarios:["futureFlood","regional","suscept"]}
];
async function fetched(url,timeout=18000){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
 try{const res=await fetch(url,{signal:controller.signal,cache:"no-store"});if(!res.ok)throw Error("HTTP "+res.status);const v=await res.json();if(v.error)throw Error(v.error.message||"error del servicio");return v;}
 finally{clearTimeout(timer);}
}
async function posted(url,params,timeout=30000){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeout);
 try{
  const res=await fetch(url,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8"},
   body:params.toString(),signal:controller.signal,cache:"no-store"});
  if(!res.ok)throw Error("HTTP "+res.status);
  const v=await res.json();if(v.error)throw Error(v.error.message||"error del servicio");return v;
 }finally{clearTimeout(timer);}
}
function webMercatorToWgs84(point,sr){
 const wkid=Number(sr?.latestWkid||sr?.wkid||4326),x=Number(point[0]),y=Number(point[1]);
 if([3857,102100,102113].includes(wkid)){
  const lon=x/6378137*180/Math.PI,lat=(2*Math.atan(Math.exp(y/6378137))-Math.PI/2)*180/Math.PI;
  return [lon,lat];
 }
 return [x,y];
}
function esriRingsToPolygons(rings,sr){
 const clean=(rings||[]).filter(r=>Array.isArray(r)&&r.length>=4).map(raw=>ringclose(raw.map(p=>webMercatorToWgs84(p,sr))));
 if(!clean.length)return [];
 let outers=clean.filter(r=>signedArea(r,1)<0),holes=clean.filter(r=>signedArea(r,1)>=0);
 if(!outers.length){
  const ordered=[...clean].sort((a,b)=>Math.abs(signedArea(b,1))-Math.abs(signedArea(a,1)));
  outers=ordered.slice(0,1);holes=ordered.slice(1);
 }
 const polygons=outers.map(r=>[r]);
 for(const hole of holes){
  const p=hole[0],candidates=polygons.filter(poly=>inRing(p[0],p[1],poly[0]))
   .sort((a,b)=>Math.abs(signedArea(a[0],1))-Math.abs(signedArea(b[0],1)));
  if(candidates.length)candidates[0].push(hole);else polygons.push([hole]);
 }
 return polygons;
}
function normalizeArcGISFeature(feature){
 const g=feature?.geometry;
 if(g?.rings){
  const polygons=esriRingsToPolygons(g.rings,g.spatialReference);
  if(!polygons.length)throw Error("Geometría ArcGIS sin anillos válidos");
  return {...feature,geometry:{type:polygons.length===1?"Polygon":"MultiPolygon",
   coordinates:polygons.length===1?polygons[0]:polygons,spatialReference:{wkid:4326}}};
 }
 if(g&&["Polygon","MultiPolygon"].includes(g.type))return feature;
 throw Error("La fuente devolvió una entidad sin geometría poligonal completa");
}
function geoContains(feature,lon,lat){
 const g=feature.geometry;if(!g||!["Polygon","MultiPolygon"].includes(g.type))return false;
 const shapes=g.type==="Polygon"?[g.coordinates]:g.coordinates;
 return contains(shapes,lon,lat);
}
function samplePoints(poly,steps=15){
 const {minLon,maxLon,minLat,maxLat}=limits(poly),points=[];
 for(let i=0;i<steps;i++)for(let j=0;j<steps;j++){
  const lon=minLon+(i+.5)*(maxLon-minLon)/steps,lat=minLat+(j+.5)*(maxLat-minLat)/steps;
  if(contains(poly,lon,lat))points.push({lon,lat});
 }
 if(!points.length){
  const p=interior(poly);
  if(Number.isFinite(p.lon)&&Number.isFinite(p.lat)&&contains(poly,p.lon,p.lat))points.push(p);
 }
 return points;
}
function fraction(poly,features,steps=40){
 const points=samplePoints(poly,steps);if(!points.length)return {fraction:NaN,sampleCount:0,overlapCount:0};
 let overlap=0;
 for(const point of points)if(features.some(feature=>geoContains(feature,point.lon,point.lat)))overlap++;
 return {fraction:overlap/points.length,sampleCount:points.length,overlapCount:overlap};
}
function orientEsriRing(ring,clockwise){
 const closed=ringclose(ring.map(p=>[Number(p[0]),Number(p[1])])),isClockwise=signedArea(closed,1)<0;
 return isClockwise===clockwise?closed:closed.slice().reverse();
}
function esriPolygon(polygons){
 const rings=[];
 for(const polygon of polygons){
  if(!polygon?.length)continue;
  rings.push(orientEsriRing(polygon[0],true));
  for(const hole of polygon.slice(1))rings.push(orientEsriRing(hole,false));
 }
 return {rings,spatialReference:{wkid:4326}};
}
function vectorQueryParams(polygons){
 return new URLSearchParams({where:"1=1",geometry:JSON.stringify(esriPolygon(polygons)),
  geometryType:"esriGeometryPolygon",inSR:"4326",spatialRel:"esriSpatialRelIntersects",
  outFields:"*",
  returnGeometry:"true",outSR:"4326",resultRecordCount:"2000",f:"json"});
}
function rasterIdentifyParams(layerId,points,bounds){
 return new URLSearchParams({geometryType:"esriGeometryMultipoint",
  geometry:JSON.stringify({points:points.map(p=>[p.lon,p.lat]),spatialReference:{wkid:4326}}),
  sr:"4326",layers:"all:"+layerId,tolerance:"1",
  mapExtent:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  imageDisplay:"1000,1000,96",returnGeometry:"false",f:"json"});
}
function rasterClassInfo(metadata){
 const renderer=metadata?.drawingInfo?.renderer||metadata?.renderer||{},unique={},breaks=[];
 for(const item of renderer.uniqueValueInfos||[])if(item?.value!==undefined)unique[String(item.value)]=item.label||String(item.value);
 for(const item of renderer.classBreakInfos||[])if(Number.isFinite(Number(item.classMaxValue)))breaks.push({
  min:Number(item.classMinValue??-Infinity),max:Number(item.classMaxValue),label:item.label||String(item.classMaxValue)});
 return {unique,breaks};
}
function cenepredClass(result,classInfo={}){
 const attributes=result?.attributes||{},keys=["n_peligro","n_pelig_mm","niv_sus","leyenda","value","gridcode","grid_code","class","nivel"];
 let raw;
 const thematic=Object.entries(attributes).find(([key,value])=>/(n_peligro|n_pelig_mm|leyenda)/i.test(key)&&value!==undefined&&value!==null&&String(value).trim()!=="");
 if(thematic)raw=thematic[1];
 if(raw===undefined)for(const key of keys){if(attributes[key]!==undefined&&attributes[key]!==null&&String(attributes[key]).trim()!==""){raw=attributes[key];break;}}
 if(raw===undefined){
  const entry=Object.entries(attributes).find(([key,value])=>/(value|pixel|grid|pelig|suscep|class|nivel|code)/i.test(key)&&value!==undefined&&value!==null&&String(value).trim()!=="");
  if(entry)raw=entry[1];
 }
 if(raw===undefined)raw=result?.value??result?.name;
 if(raw===undefined||raw===null||String(raw).trim()==="")return "Sin clasificar";
 const value=String(raw),normalized=value.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
 if(normalized.includes("muy")&&normalized.includes("alto"))return "Muy alto";
 if(normalized.includes("alto"))return "Alto";
 if(normalized.includes("medio"))return "Medio";
 if(normalized.includes("bajo"))return "Bajo";
 if(Number.isFinite(Number(value))){
  const code=String(Number(value));
  if(classInfo.unique?.[code])return classInfo.unique[code];
  const match=(classInfo.breaks||[]).find(item=>Number(value)>item.min&&Number(value)<=item.max);
  if(match)return match.label;
  return "Código "+code;
 }
 return value.slice(0,60);
}
function parseRasterClasses(results,sampleCount,classInfo={}){
 const counts={};
 for(const result of results||[]){const label=cenepredClass(result,classInfo);counts[label]=(counts[label]||0)+1;}
 const identified=(results||[]).length,total=Number(sampleCount)||0;
 return {counts,identified,sampleCount:total,coverage:total?Math.min(1,identified/total):0,
  complete:total>0&&identified===total};
}
async function vectorIntersection(layer,polygons,areaHa){
 const params=vectorQueryParams(polygons),data=await fetched(layer.url+"?"+params,30000);
 if(!Array.isArray(data.features))throw Error("El servicio no devolvió un arreglo de entidades");
 if(data.exceededTransferLimit||data.features.length>=2000)throw Error("Límite de 2 000 entidades; consulta incompleta, no se calculan hectáreas");
 if(data.features.length&&data.features.some(f=>!f.geometry||(!f.geometry.rings&&!["Polygon","MultiPolygon"].includes(f.geometry.type))))
  throw Error("La fuente devolvió entidades sin geometría poligonal completa");
 if(!data.features.length)return {name:layer.name,kind:"vector",responded:true,hasData:false,features:0};
 const features=data.features.map(normalizeArcGISFeature),stats=fraction(polygons,features,40);
 return {name:layer.name,kind:"vector",responded:true,hasData:true,features:features.length,stats,areaHa};
}
const rasterMetadataCache=new Map();
async function rasterMetadata(layer){
 if(!rasterMetadataCache.has(layer.layerId)){
  const pending=fetched(layer.metadataUrl,18000).then(metadata=>{
   if(metadata.type!=="Raster Layer")throw Error("La capa "+layer.layerId+" no está publicada como ráster");
   return metadata;
  }).catch(error=>{rasterMetadataCache.delete(layer.layerId);throw error;});
  rasterMetadataCache.set(layer.layerId,pending);
 }
 return rasterMetadataCache.get(layer.layerId);
}
async function rasterIntersection(layer,polygons){
 const points=samplePoints(polygons,15);if(!points.length)throw Error("No se generaron puntos interiores para el muestreo");
 const params=rasterIdentifyParams(layer.layerId,points,limits(polygons));
 const [data,metadata]=await Promise.all([posted(layer.url,params,30000),rasterMetadata(layer)]);
 if(!Array.isArray(data.results))throw Error("Identify no devolvió el arreglo results");
 const summary=parseRasterClasses(data.results,points.length,rasterClassInfo(metadata));
 return {name:layer.name,kind:"raster",responded:true,hasData:summary.identified>0,samples:points.length,summary};
}
async function risk(k){
 const {poly,point}=current(k),out=setText(k,"risk","");
 if(!point){out.textContent="Ingresa un punto geográfico o importa/dibuja una parcela para evaluar el territorio.";return;}
 const seq=++tokens[k].risk;out.append(node("h4",null,"Evaluación espacial · "+point.name));
 if(!poly){out.append(node("p",null,"Hay un punto válido. Se ejecuta la evaluación puntual del visor original; para analizar superficies necesitas delimitar o importar el polígono de la parcela."));return;}
 out.append(node("p",null,"Parcela: "+fmt(poly.ha,3)+" ha aproximadas. Se consultan las capas seleccionadas usando el polígono real y, para CENEPRED, puntos de identificación dentro de la parcela."));
 const src=$(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
 const selected=Array.from(src?.querySelectorAll("input:checked")||[]).map(x=>x.dataset.ux30Layer||x.dataset.ux35Key||x.dataset.ux29Layer).filter(Boolean);
 const chosen=LAYERS.filter(layer=>selected.some(value=>(layer[k]||[]).includes(value)));
 if(!chosen.length){out.append(node("p",null,"No hay capas de inundación o movimientos en masa seleccionadas. Activa las capas correspondientes en el árbol del visor y vuelve a evaluar."));return;}
 const results=await Promise.all(chosen.map(async layer=>{
  try{return layer.kind==="vector"?await vectorIntersection(layer,poly.polygons,poly.ha):await rasterIntersection(layer,poly.polygons);}
  catch(error){return {name:layer.name,kind:layer.kind,responded:false,error:error.message};}
 }));
 if(seq!==tokens[k].risk||!ui(k))return;
 const table=node("table"),header=node("tr");
 ["Fuente y tipo","Cobertura de la consulta","Resultado zonal"].forEach(x=>header.append(node("th",null,x)));table.append(header);
 results.forEach(row=>{
  const tr=node("tr");
  let coverage="",result="";
  if(!row.responded){coverage="No verificable";result=row.error||"Servicio sin respuesta";}
  else if(row.kind==="vector"){
   coverage=row.features+" polígonos devueltos por la consulta de intersección";
   if(!row.features)result="Sin intersección devuelta. No se asignan 0 ha y esto no descarta peligro.";
   else if(!row.stats||!Number.isFinite(row.stats.fraction)||!row.stats.sampleCount)
    result="El servicio encontró polígonos, pero el muestreo no permite cuantificar la superficie.";
   else if(!row.stats.overlapCount)
    result="Intersección vectorial confirmada; la malla no resolvió una superficie cuantificable a esta escala.";
   else result=fmt(row.stats.fraction*row.areaHa,3)+" ha aproximadas · "+fmt(row.stats.fraction*100,1)+" % de puntos muestreados";
  }else{
   const s=row.summary;coverage=s.identified+"/"+s.sampleCount+" puntos con valor identificable ("+fmt(s.coverage*100,1)+" % de cobertura de respuesta)";
   if(!s.identified)result="Sin valores ráster identificables; no equivale a susceptibilidad baja ni a ausencia de peligro.";
   else result=Object.entries(s.counts).map(([label,count])=>label+": "+count+" ("+fmt(count/s.identified*100,1)+" %)").join(" · ");
  }
  [row.name,coverage,result].forEach(value=>tr.append(node("td",null,value)));table.append(tr);
 });
 out.append(table);
 const good=results.filter(v=>v.responded).length;
 out.append(node("p","oaf-parcel-caveat",
  "Interpretación: INGEMMET consulta polígonos vectoriales contra la geometría de la parcela y estima el solapamiento mediante una cuadrícula de 40 × 40 centros; las hectáreas son aproximadas, no una intersección topológica exacta. CENEPRED consulta capas ráster mediante Identify multipunto: los porcentajes describen la distribución de puntos muestreados, no hectáreas exactas. Sus capas representan susceptibilidad cartográfica y no el peligro actual ni un pronóstico. Una consulta vacía, parcial o bloqueada por CORS no demuestra ausencia de peligro."));
 auditState(k,"Control de capas geoespaciales",good+" de "+results.length+" consultas respondieron; la cobertura y resolución se informan por separado.");
}
let auditTimer={};
function scheduleAudit(k){clearTimeout(auditTimer[k]);auditTimer[k]=setTimeout(()=>{if(ui(k)&&current(k).point)audit(k);},1000);}
async function audit(k){
 const out=setText(k,"audit",""),point=current(k).point,poly=current(k).poly;
 out.append(node("h4",null,"Auditoría de disponibilidad y trazabilidad"));
 out.append(node("p",null,"Fecha local: "+new Date().toLocaleString("es-PE",{timeZone:"America/Lima"})+". La respuesta de un servicio no valida por sí sola la precisión temática, la escala ni la vigencia de una capa."));
 out.append(node("p",null,"Entrada: "+(point?"WGS84 "+point.lat.toFixed(5)+", "+point.lon.toFixed(5):"sin punto")+"; "+(poly?"polígono "+fmt(poly.ha,3)+" ha":"sin polígono")+". "+activeLayers(k).length+" capas marcadas."));
 if(!point)return;
 const checks=[
  {name:"Archivo ERA5-Land",url:"https://archive-api.open-meteo.com/v1/archive?"+new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),start_date:"2025-01-01",end_date:"2025-01-03",daily:"precipitation_sum",timezone:"America/Lima",models:"era5_land"}),describe:j=>j.daily?.time?.length===3?"serie diaria · 3 días · celda "+fmt(j.latitude,4)+", "+fmt(j.longitude,4):"respuesta sin tres días"},
  {name:"INGEMMET · capa 0",url:LAYERS[0].metadataUrl,describe:j=>j.type==="Feature Layer"?"vectorial · "+j.geometryType+" · "+(j.supportedQueryFormats||"formatos no informados"):"tipo de capa: "+(j.type||"no informado")},
  {name:"CENEPRED · capa 5090022",url:LAYERS[1].metadataUrl,describe:j=>j.type==="Raster Layer"?"ráster · requiere Identify, no consulta vectorial":("tipo de capa: "+(j.type||"no informado"))},
  {name:"CENEPRED · capa 5090024",url:LAYERS[2].metadataUrl,describe:j=>j.type==="Raster Layer"?"ráster · requiere Identify, no consulta vectorial":("tipo de capa: "+(j.type||"no informado"))}
 ];
 const seq=++tokens[k].audit;
 const checked=await Promise.all(checks.map(async item=>{try{const j=await fetched(item.url,18000);return [item.name,item.describe(j)];}catch(e){return [item.name,"no verificable desde este navegador ("+e.message+")"];}}));
 if(seq!==tokens[k].audit)return;
 for(const [name,value] of checked)out.append(node("p",null,name+": "+value));
 out.append(node("p","oaf-parcel-caveat","Las capas CENEPRED 5090022 y 5090024 son ráster; la aplicación las consulta con Identify y no con Query de polígonos. INGEMMET es una capa vectorial poligonal. Si el navegador bloquea una petición por CORS, la fuente queda como no verificable desde esta sesión; consulta su visor oficial."));
}
function climDaily(payload){
 const daily=payload.daily;if(!daily?.time?.length)throw Error("Datos climáticos diarios ausentes");
 const grouped=new Map();
 daily.time.forEach((date,i)=>{
  const year=date.slice(0,4),month=+date.slice(5,7),key=year+"-"+String(month).padStart(2,"0");
  let r=grouped.get(key);if(!r){r={year:+year,month,days:0,rain:0,t:0,nr:0,nt:0};grouped.set(key,r);}
  r.days++;const rain=daily.precipitation_sum?.[i],t=daily.temperature_2m_mean?.[i];
  if(Number.isFinite(rain)){r.rain+=rain;r.nr++;}if(Number.isFinite(t)){r.t+=t;r.nt++;}
 });
 for(const [k,r] of grouped){const days=new Date(r.year,r.month,0).getDate();
  if(r.days!==days||r.nr!==days||r.nt!==days)grouped.delete(k);else r.t/=days;
 }
 return grouped;
}
function arModel(data,varKey){
 const normals=[],rows=[],modelRows=[];
 for(let m=1;m<=12;m++){
  const training=[];for(let yr=2001;yr<=2020;yr++){const x=data.get(yr+"-"+String(m).padStart(2,"0"));if(x)training.push(x[varKey]);}
  const mean=training.length>=16?training.reduce((a,b)=>a+b,0)/training.length:NaN;normals[m]=mean;
 }
 let top=0,denom=0;
 for(let y=2002;y<=2020;y++)for(let m=1;m<=12;m++){
  const month=String(m).padStart(2,"0"),a=data.get(y+"-"+month),prev=data.get((y-1)+"-"+month),base=normals[m];
  if(!a||!prev||!Number.isFinite(base))continue;
  top+=(prev[varKey]-base)*(a[varKey]-base);denom+=(prev[varKey]-base)**2;
 }
 const alpha=Math.max(-.45,Math.min(.85,denom?top/denom:0));
 let sumErr=0,sumBase=0,n=0,sumSq=0;
 for(let y=2021;y<=2025;y++)for(let m=1;m<=12;m++){
  const month=String(m).padStart(2,"0"),actual=data.get(y+"-"+month),prev=data.get((y-1)+"-"+month),base=normals[m];
  if(!actual||!prev||!Number.isFinite(base))continue;
  const pred=base+alpha*(prev[varKey]-base);
  const v=varKey==="rain"?Math.max(0,pred):pred;
  sumErr+=Math.abs(actual[varKey]-v);sumSq+=(actual[varKey]-v)**2;sumBase+=Math.abs(actual[varKey]-base);n++;
 }
 const scores={alpha,mae:n?sumErr/n:NaN,rmse:n?Math.sqrt(sumSq/n):NaN,base:n?sumBase/n:NaN,n};
 const chosen=n>=48&&scores.mae<scores.base?alpha:0;
 const projections=new Map();
 for(let yr=2026;yr<=2027;yr++)for(let m=1;m<=12;m++){
  const key=yr+"-"+String(m).padStart(2,"0"),before=(yr-1)+"-"+String(m).padStart(2,"0");
  const prev=projections.get(before)??data.get(before)?.[varKey],base=normals[m];
  projections.set(key,Number.isFinite(prev)&&Number.isFinite(base)?(varKey==="rain"?Math.max(0,base+chosen*(prev-base)):base+chosen*(prev-base)):NaN);
 }
 return {scores,chosen,projections};
}
async function model(k){
 const {point,poly}=current(k),out=setText(k,"model","");
 if(!point){out.textContent="Primero ubica el punto o dibuja la parcela.";return;}
 out.append(node("h4",null,"Modelo exploratorio y validación temporal para "+point.name));
 out.append(node("p",null,"Consultando ERA5-Land 2001–2025 para entrenar una regresión estacional de rezago anual (AR-12), con comparación contra climatología y evaluación 2021–2025 fuera del periodo de entrenamiento…"));
 const seq=++tokens[k].model,query=new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),start_date:"2001-01-01",end_date:"2025-12-31",
  daily:"temperature_2m_mean,precipitation_sum",timezone:"America/Lima",models:"era5_land"});
 try{
  const result=await fetched("https://archive-api.open-meteo.com/v1/archive?"+query,30000);
  if(seq!==tokens[k].model)return;
  const series=climDaily(result),rain=arModel(series,"rain"),temp=arModel(series,"t");
  out.replaceChildren(node("h4",null,"Validación espacial puntual · "+point.name));
  out.append(node("p",null,"Fuente ERA5-Land · "+point.lat.toFixed(5)+", "+point.lon.toFixed(5)+"; celda modelada "+fmt(result.latitude,4)+", "+fmt(result.longitude,4)+". Entrenamiento 2001–2020; prueba temporal 2021–2025. No hay variables ENSO ni predicción hidráulica."));
  const table=node("table");table.innerHTML="<thead><tr><th>Variable</th><th>MAE AR-12 (prueba)</th><th>MAE climatología</th><th>Meses evaluados</th></tr></thead>";
  for(const [label,m,unit] of [["Lluvia mensual",rain,"mm"],["Temperatura media",temp,"°C"]]){
   const tr=node("tr");[label,fmt(m.scores.mae)+" "+unit,fmt(m.scores.base)+" "+unit,String(m.scores.n)].forEach(x=>tr.append(node("td",null,x)));table.append(tr);
  }
  out.append(table);
  const months=[[2026,11],[2026,12],[2027,1],[2027,2],[2027,3],[2027,4]];
  const t=node("table");t.innerHTML="<thead><tr><th>Mes</th><th>Referencia lluvia (mm)</th><th>Referencia temperatura (°C)</th></tr></thead>";
  for(const [y,m] of months){const key=y+"-"+String(m).padStart(2,"0"),tr=node("tr");
   [key,fmt(rain.projections.get(key)),fmt(temp.projections.get(key))].forEach(x=>tr.append(node("td",null,x)));t.append(tr);
  }
  out.append(node("h4",null,"Escenario de referencia Nov 2026–Abr 2027 (NO pronóstico operativo)"),t);
  out.append(node("p","oaf-parcel-caveat","Regla reproducible: AR-12 con efecto estacional entrenado en 2001–2020, contrastado en 2021–2025; si no mejora el MAE climatológico, usa climatología. Proyección recursiva, NO entrenamiento Random Forest, sin observaciones de finca y sin validación de anticipaciones a 3–7 meses. El error temporal mostrado corresponde a 1 paso, no a ese horizonte; usar solo para exploración científica."));
 }catch(e){if(seq===tokens[k].model)out.textContent="Sin resultado verificable del modelo para esta coordenada: "+e.message+". No se rellenan datos faltantes con cifras supuestas.";}
}
async function agro(k){
 const {point,poly}=current(k),out=setText(k,"agro","");
 if(!point){out.textContent="Indica una ubicación WGS84 o UTM para consultar el ambiente productivo.";return;}
 const seq=++tokens[k].agro,query=new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),timezone:"America/Lima",forecast_days:"3",
  daily:"precipitation_sum,temperature_2m_max,temperature_2m_min",hourly:"relative_humidity_2m"});
 out.textContent="Consultando meteorología para "+point.name+"…";
 try{
  const j=await fetched("https://api.open-meteo.com/v1/forecast?"+query);
  if(seq!==tokens[k].agro)return;
  const d=j.daily,h=j.hourly;
  if(d?.time?.length<3||!Array.isArray(d.precipitation_sum)||!h?.time?.length)throw Error("Datos meteorológicos incompletos");
  const valid=d.precipitation_sum.slice(0,3).filter(Number.isFinite),max=d.temperature_2m_max.slice(0,3).filter(Number.isFinite),humid=h.relative_humidity_2m.filter(Number.isFinite);
  if(valid.length<3||max.length<3||!humid.length)throw Error("No hay cobertura completa para 3 días");
  const rain=valid.reduce((a,b)=>a+b,0),temp=Math.max(...max),meanHum=humid.reduce((a,b)=>a+b,0)/humid.length;
  out.replaceChildren(node("h4",null,"Contexto agroclimático · "+point.name));
  out.append(node("p",null,"Open-Meteo (modelo meteorológico externo), ventana "+d.time[0]+" a "+d.time[2]+": precipitación acumulada "+fmt(rain)+" mm; máxima de temperatura "+fmt(temp)+" °C; humedad relativa horaria media "+fmt(meanHum)+" %. "+(poly?"Polígono cargado: "+fmt(poly.ha)+" ha.":"La extensión parcelaria no ha sido delineada.")));
  let flags=[];if(meanHum>=80)flags.push("Humectación atmosférica elevada: intensifica el monitoreo visual de síntomas y condiciones de follaje.");if(rain>=15)flags.push("Lluvia en el periodo: verifica drenajes, riego y accesos.");if(temp>=32)flags.push("Temperatura máxima elevada: examina estrés hídrico y necesidades de riego.");
  if(!flags.length)flags.push("Sin señales meteorológicas que superen los umbrales descriptivos del prototipo; mantén el monitoreo habitual.");
  for(const flag of flags)out.append(node("p",null,flag));
  const crop=$("oaf-sm-cultivo")?.selectedOptions?.[0]?.textContent,organism=$("oaf-sm-patogeno")?.selectedOptions?.[0]?.textContent;
  if(crop)out.append(node("p",null,"Consulta fitosanitaria del portal: "+crop+(organism?" · "+organism:"")+". Puedes pulsar «Usar punto en Cultivos y sanidad» para recalcular allí con estas coordenadas."));
  out.append(node("p","oaf-parcel-caveat","Umbrales ambientales de revisión, no modelos de probabilidad de infestación o infección. Sin fenología, riego, historial de trampas ni incidencia observada no se estima el riesgo sanitario real ni se prescriben pesticidas."));
 }catch(e){if(seq===tokens[k].agro)out.textContent="Contexto climático no verificable: "+e.message;}
}
function init(){
 for(const k of scopes){let count=0;const tryMount=()=>{if(mount(k))return;if(++count<45)setTimeout(tryMount,250);};tryMount();}
 document.addEventListener("oaf:area-update",e=>{if(!scopes.includes(e.detail?.scope))return;const k=e.detail.scope;
  if(e.detail?.active&&e.detail.point){if(ui(k)){updateActive(k);draw(k);scheduleAudit(k);}}else{++revision[k];Object.keys(tokens[k]).forEach(q=>tokens[k][q]++);if(ui(k))report(k,"Se quitó el punto. Puedes conservar o borrar la delimitación por separado.");}
 });
 window.addEventListener("oaf:geodata",()=>{for(const k of scopes)draw(k)});
}
window.OAFParcelas={get:k=>parcels[k]?{name:parcels[k].name,ha:parcels[k].ha,geometry:parcels[k].geometry}:null,parsePolygons,contains,surface,limits,samplePoints,esriPolygon,esriRingsToPolygons,normalizeArcGISFeature,vectorQueryParams,rasterIdentifyParams,parseRasterClasses,rasterClassInfo,fraction};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();