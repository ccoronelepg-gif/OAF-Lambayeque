/* OAF UX52 · Visores amplios, capas esenciales y enfoque de parcela.
   Ajustes progresivos sobre UX29–UX40. No altera los cálculos de peligros. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const SVG_NS="http://www.w3.org/2000/svg";
const create=(tag)=>document.createElementNS(SVG_NS,tag);
const layouts=["territory","scenario"];
const allowed=new Set(["base","departamento","provincia","distrito","regional","movmasa",
 "fluvial","pluvial","detritos","erosion","floodpoints","geopoints","basin","drain",
 "quebradas","nacional","departamental","vecinal"]);
const TERRITORY_NAMES=[
 ["Mapa base","1 · Límites políticos"],
 ["Peligros y susceptibilidad","2 · Peligros y susceptibilidades"],
 ["Cuencas, ríos","3 · Cuencas y ríos"],
 ["Red vial","4 · Red vial"]
];
function trimTerritory(){
 const tree=$("oaf-ux30-layer-tree");if(!tree||tree.dataset.ux52Trimmed)return;
 tree.dataset.ux52Trimmed="true";
 for(const section of [...tree.querySelectorAll(":scope > details.oaf-ux30-section")]){
  const head=section.querySelector("summary");
  const text=head?.textContent||"";
  const match=TERRITORY_NAMES.find(([prefix])=>text.includes(prefix));
  if(!match){section.remove();continue;}
  head.textContent=match[1];
  for(const label of section.querySelectorAll("label.oaf-ux30-option")){
   const key=label.querySelector("input")?.dataset.ux30Layer;
   if(!allowed.has(key)||key==="base"){label.hidden=true;label.classList.add("oaf-ux52-hidden-layer");}
   if(key==="geopoints"){const span=label.querySelector("span");if(span)span.textContent="Zonas críticas geológicas · INGEMMET";}
   if(key==="vecinal"){const span=label.querySelector("span");if(span)span.textContent="Vías distritales, vecinales y rurales · MTC";}
  }
 }
 const hazard=[...tree.querySelectorAll("details")].find(d=>d.querySelector("summary")?.textContent?.includes("Peligros y susceptibilidades"));
 if(hazard&&!$("oaf-ux52-relief-toggle")){
  const label=document.createElement("label");label.className="oaf-ux30-option oaf-ux52-elevation";
  label.innerHTML='<input id="oaf-ux52-relief-toggle" type="checkbox"><span>Relieve topográfico · sombreado de elevación</span><small>Vista de apoyo. No mide depresiones, cotas ni profundidad de inundación.</small>';
  const opts=hazard.querySelector(".oaf-ux30-options");opts?.insertBefore(label,opts.firstElementChild||null);
  label.querySelector("input").addEventListener("change",()=>{relief();});
 }
}
function trimScenario(){
 const pane=$("oaf-ux29-scenario"),tree=pane?.querySelector(".oaf-ux29-tree");
 if(!tree||tree.dataset.ux52Trimmed)return;
 tree.dataset.ux52Trimmed="true";
 // Desactivar la superposición agrícola heredada antes de ocultar controles duplicados.
 for(const key of ["agricola","exposicion","agroflood","inundacionregion"]){
  const input=tree.querySelector('[data-ux35-key="territory:'+key+'"]');
  if(input?.checked){input.checked=false;input.dispatchEvent(new Event("change",{bubbles:true}));}
 }
 for(const details of [...tree.querySelectorAll(":scope > details.oaf-ux35-group")]){
  const label=details.querySelector("summary")?.textContent||"";
  if(label.startsWith("Territorio ·")||label.includes("Filtros geográficos"))details.remove();
  else if(label.startsWith("4 ·")){details.open=false;}
  else if(label.includes("Vigilancia hidrológica")){details.open=false;details.querySelector("summary").textContent="5 · Análisis hidrológico";}
 }
 const intro=tree.querySelector(".oaf-ux35-tree-intro");
 if(intro)intro.textContent="Superpón antecedentes, lluvias y escenarios. Selecciona tu zona en el panel Mi zona productiva, debajo del mapa.";
 const historic=tree.querySelector("#oaf-ux35-histyear");
 if(historic){
  historic.title="Años de referencia; la disponibilidad de reanálisis varía por año";
  for(const year of [1993,2007])if(![...historic.options].some(o=>Number(o.value)===year)){
   const option=document.createElement("option");option.value=String(year);option.textContent=String(year);
   historic.append(option);
  }
  const options=[...historic.options].sort((a,b)=>Number(a.value)-Number(b.value));
  historic.replaceChildren(...options);
 }
}
function syncStructure(type){
 const pane=$("oaf-ux29-"+type),layout=pane?.querySelector(".oaf-ux29-layout");
 const col=layout?.querySelector(".oaf-ux29-mapcolumn");
 if(!col)return;
 const header=col.querySelector(".oaf-ux29-maphead");
 const toolbar=col.querySelector(".oaf-ux29-toolbar");
 const area=pane.querySelector("#oaf-area-"+(type==="territory"?"territorio":"escenarios"));
 const parcel=pane.querySelector("#oaf-parcel-"+(type==="territory"?"territorio":"escenarios"));
 const content=col.querySelector(".oaf-ux29-mapcontent");
 const bottom=col.querySelector(".oaf-ux29-bottom");
 // Cabecera > controles de zoom y ampliación > coordenadas/UTM > parcela > mapa.
 // Reubicar nodos existentes conserva escuchadores, datos y controles originales.
 let previous=header;
 for(const child of [toolbar,area,parcel,content,bottom]){
  if(!child||!previous)continue;
  if(child.parentElement!==col||child.previousElementSibling!==previous)previous.after(child);
  previous=child;
 }
 const diagnosis=layout.querySelector(".oaf-ux29-diagnosis");
 if(diagnosis){
  diagnosis.querySelector(".oaf-ux29-diagnosishead span")?.replaceChildren(document.createTextNode("ANÁLISIS CONTEXTUAL"));
  diagnosis.querySelector(".oaf-ux29-diagnosishead h3")?.replaceChildren(document.createTextNode("Diagnóstico del territorio"));
 }
 if(type==="scenario"&&diagnosis){
  // El panel puntual es redundante: la evaluación consolidada se presenta en el diagnóstico general.
  // Mantener su nodo técnico oculto para no romper las consultas de coordenadas de UX39.
  const point=pane.querySelector("#oaf-area-point-details-escenarios");
  const extras=diagnosis.querySelector(".oaf-ux29-diagextras");
  if(point&&extras&&point.parentElement!==extras)extras.append(point);
  const hydro=$("oaf-ux36-panel"),validation=$("oaf-ux37-panel");
  if(hydro&&(hydro.parentElement!==layout||hydro.previousElementSibling!==diagnosis))diagnosis.after(hydro);
  const anchor=hydro||diagnosis;
  if(validation&&(validation.parentElement!==layout||validation.previousElementSibling!==anchor))anchor.after(validation);
  const hg=$("oaf-ux36-hydrogroup");
  if(hg){
   hg.open=false;
   const summary=hg.querySelector("summary");
   if(summary&&summary.textContent!=="5 · Análisis hidrológico")summary.textContent="5 · Análisis hidrológico";
  }
 }
}
function markerSize(svg,id){
 const g=svg.querySelector("#"+id);if(!g)return;
 const view=(svg.getAttribute("viewBox")||"0 0 700 340").split(/[\s,]+/).map(Number);
 const width=view[2]||700;
 const scale=Math.max(.07,Math.min(1,width/700));
 // En pantalla el punto permanece legible sin volverse desproporcionado.
 const ratio=Math.pow(scale,.85);
 const circles=[...g.querySelectorAll("circle")];
 for(const c of circles){
  if(!c.dataset.ux52BaseRadius)c.dataset.ux52BaseRadius=c.getAttribute("r")||"4.5";
  c.setAttribute("r",(Number(c.dataset.ux52BaseRadius)*ratio).toFixed(2));
 }
 if(circles[1])circles[1].setAttribute("stroke-width",(2*ratio).toFixed(2));
}
function mapFocus(type,point){
 if(!point||!Number.isFinite(point.lat)||!Number.isFinite(point.lon))return;
 const svg=$(type==="territory"?"oaf-ux24-region-map":"oaf-ux29-forecast-map");
 const scene=type==="territory"?window.oafUx30Context?.()?.scene:window.oafUx29ScenarioApi?.get?.()?.scene;
 if(!svg||!scene||typeof scene.x!=="function"||typeof scene.y!=="function")return;
 const x=scene.x(point.lon),y=scene.y(point.lat);
 if(!Number.isFinite(x)||!Number.isFinite(y))return;
 const maxY=type==="scenario"?380:340, width=215,height=width*maxY/700;
 const xx=Math.max(0,Math.min(700-width,x-width/2));
 const yy=Math.max(0,Math.min(maxY-height,y-height/2));
 svg.setAttribute("viewBox",[xx,yy,width,height].map(v=>v.toFixed(2)).join(" "));
 markerSize(svg,type==="territory"?"oaf-area-pin-territorio":"oaf-area-pin-escenarios");
}
function prepareMap(type){
 const id=type==="territory"?"oaf-ux24-region-map":"oaf-ux29-forecast-map";
 const svg=$(id);if(!svg||svg.dataset.ux52Prepared)return;
 svg.dataset.ux52Prepared="true";
 const pinId=type==="territory"?"oaf-area-pin-territorio":"oaf-area-pin-escenarios";
 const observer=new MutationObserver((mutations)=>{
  if(mutations.some(m=>m.attributeName==="viewBox"||m.type==="childList")){
   markerSize(svg,pinId);
   if(type==="territory")relief();
  }
 });
 observer.observe(svg,{attributes:true,attributeFilter:["viewBox"],childList:true});
 const point=window.OAFTerritory?.getActivePoint?.(type==="territory"?"territorio":"escenarios");
 if(point)markerSize(svg,pinId);
}
const reliefURL="https://services.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/export";
let reliefTimer=null;
function relief(){
 const svg=$("oaf-ux24-region-map"),enabled=$("oaf-ux52-relief-toggle")?.checked;
 if(!svg)return;
 let img=$("oaf-ux52-relief-image");
 let mask=$("oaf-ux52-relief-mask");
 if(!enabled){img?.remove();mask?.remove();return;}
 const scene=window.oafUx30Context?.()?.scene,b=scene?.bounds;
 if(!b)return;
 if(!mask){
  const boundary=svg.querySelector('[data-oaf-ux24-boundary="true"]');
  if(boundary){
   const defs=create("defs"),clip=create("clipPath");
   clip.id="oaf-ux52-relief-clip";
   const boundaryCopy=boundary.cloneNode(true);
   boundaryCopy.removeAttribute("id");
   boundaryCopy.removeAttribute("class");
   clip.append(boundaryCopy);defs.append(clip);defs.id="oaf-ux52-relief-mask";
   svg.insertBefore(defs,svg.firstChild);
   mask=defs;
  }
 }
 if(!img){
  img=create("image");img.id="oaf-ux52-relief-image";
  img.setAttribute("preserveAspectRatio","none");img.setAttribute("opacity",".55");
  img.setAttribute("pointer-events","none");
  img.setAttribute("style","mix-blend-mode:multiply");
  if(mask)img.setAttribute("clip-path","url(#oaf-ux52-relief-clip)");
  // El sombreado queda debajo de puntos, rótulos y trazos de peligro.
  const landmark=svg.querySelector("g.oaf-ux30-layer")||svg.querySelector("circle")||svg.lastChild;
  svg.insertBefore(img,landmark||null);
 }
 clearTimeout(reliefTimer);
 reliefTimer=setTimeout(()=>{
  if(!$("oaf-ux52-relief-toggle")?.checked||!img.isConnected)return;
  const v=(svg.getAttribute("viewBox")||"0 0 700 340").split(/[\s,]+/).map(Number);
  if(v.length!==4||v.some(z=>!Number.isFinite(z)))return;
  const g={minLon:b.minLon+(v[0]/700)*(b.maxLon-b.minLon),maxLon:b.minLon+((v[0]+v[2])/700)*(b.maxLon-b.minLon),
   maxLat:b.maxLat-(v[1]/340)*(b.maxLat-b.minLat),minLat:b.maxLat-((v[1]+v[3])/340)*(b.maxLat-b.minLat)};
  const params=new URLSearchParams({
   bbox:[g.minLon,g.minLat,g.maxLon,g.maxLat].join(","),bboxSR:"4326",imageSR:"4326",
   size:"1100,535",format:"png",transparent:"true",dpi:"120",f:"image"
  });
  img.setAttribute("x",String(v[0]));img.setAttribute("y",String(v[1]));
  img.setAttribute("width",String(v[2]));img.setAttribute("height",String(v[3]));
  const url=reliefURL+"?"+params;
  if(img.getAttribute("href")!==url)img.setAttribute("href",url);
 },280);
}
function init(){
 trimTerritory();trimScenario();
 for(const kind of layouts){
  syncStructure(kind);prepareMap(kind);
  const col=$("oaf-ux29-"+kind)?.querySelector(".oaf-ux29-mapcolumn");
  if(col&&col.dataset.ux52Observe!=="true"){
   col.dataset.ux52Observe="true";
   new MutationObserver(()=>syncStructure(kind)).observe(col,{childList:true});
  }
  const content=col?.querySelector(".oaf-ux29-mapcontent");
  if(content&&content.dataset.ux53Observe!=="true"){
   // UX39 inserta la parcela dentro del mapa de escenarios; detectar esa inserción.
   content.dataset.ux53Observe="true";
   new MutationObserver(mutations=>{
    if(mutations.some(m=>[...m.addedNodes].some(n=>n.nodeType===1&&(
     n.id==="oaf-parcel-escenarios"||n.id==="oaf-area-point-details-escenarios"||
     n.id==="oaf-ux36-panel"||n.id==="oaf-ux37-panel"
    ))))syncStructure(kind);
   }).observe(content,{childList:true});
  }
 }
 const pane=$("oaf-ux29-scenario"),layout=pane?.querySelector(".oaf-ux29-layout");
 if(layout&&!layout.dataset.ux52HydroObserve){
  layout.dataset.ux52HydroObserve="true";
  new MutationObserver(()=>syncStructure("scenario")).observe(layout,{childList:true});
 }
 relief();
}
document.addEventListener("oaf:area-update",e=>{
 const kind=e.detail?.scope==="territorio"?"territory":e.detail?.scope==="escenarios"?"scenario":null;
 if(kind&&e.detail.active&&e.detail.point)requestAnimationFrame(()=>mapFocus(kind,e.detail.point));
 if(kind)requestAnimationFrame(()=>prepareMap(kind));
});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",()=>{
 init();setTimeout(init,250);setTimeout(init,1100);setTimeout(init,3200);
},{once:true});else{init();setTimeout(init,350);setTimeout(init,1500);}
})();