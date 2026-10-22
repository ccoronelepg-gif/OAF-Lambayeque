/* OAF-Lambayeque UX33 · mapas vectoriales con etiquetas y estados de carga.
 * Geometrías siempre procedentes de geoservicios. No se generan ubicaciones ficticias.
 * Las etiquetas individuales solo usan nombres publicados por las fuentes.
 */
(function(){"use strict";
const S={
 ctx:null,features:{district:[],hydroRio:[],hydroQuebrada:[],historical:[],agri:[]},
 phase:{district:"pendiente",hydroRio:"pendiente",hydroQuebrada:"pendiente",historical:"pendiente",agri:"pendiente"},
 note:{},count:{},partial:{},started:{},names:{},current:0
};
const HOST="https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer";
const SERFOR="https://geo.serfor.gob.pe/geoservicios/rest/services/Visor/Limites_Politicos_Administrativos/MapServer";
const AGRI="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
const el=id=>document.getElementById(id);
const tag=(name,attrs={})=>{const n=document.createElementNS("http://www.w3.org/2000/svg",name);
 Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));return n};
const norm=v=>String(v||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
const val=(p,...keys)=>{for(const key of keys){const v=p?.[key]??p?.[key.toLowerCase()]??p?.[key.toUpperCase()];if(v!==undefined&&v!==null&&String(v).trim())return String(v).trim()}return ""};
const categories={fluvial:"#0879bd",pluvial:"#3379bd",erosion:"#ba4d4d",detritos:"#a87325"};
const geoService={district:SERFOR+"/2",hydroRio:HOST+"/6030200",hydroQuebrada:HOST+"/6030200",historical:HOST+"/6010100",agri:AGRI+"/1"};
const bounds=()=>S.ctx?.scene?.bounds;
function queryUrl(key,where,outFields,amount=1700){
 const b=bounds();if(!b)return "";
 return geoService[key]+"/query?"+new URLSearchParams({
  where,geometry:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),
  geometryType:"esriGeometryEnvelope",spatialRel:"esriSpatialRelIntersects",
  inSR:"4326",outSR:"4326",outFields,returnGeometry:"true",
  geometryPrecision:"5",maxAllowableOffset:key==="historical"?"0":"0.001",
  resultRecordCount:String(amount),f:"geojson"
 });
}
async function fetchJSON(url){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
 try{
  const r=await fetch(url,{signal:controller.signal,cache:"no-store"});
  if(!r.ok)throw Error("HTTP "+r.status);
  const json=await r.json();
  if(json.error||!Array.isArray(json.features))throw Error(json?.error?.message||"GeoJSON incompatible");
  return json.features;
 }finally{clearTimeout(timer)}
}
function featureCategory(props){
 const c=norm(val(props,"tipo_pel"));
 if(c.includes("inundacion fluvial"))return "fluvial";
 if(c.includes("inundacion pluvial")||c.includes("precipitacion pluvial"))return "pluvial";
 if(c.includes("erosion fluvial"))return "erosion";
 if(c.includes("flujo de detritos")||c==="flujos"||c.includes("lodo"))return "detritos";
 return "";
}
function needs(k){
 const on=S.ctx?.on;if(!on)return false;
 if(k==="historical")return ["fluvial","pluvial","erosion","detritos"].some(on);
 if(k==="hydroRio")return on("drain");
 if(k==="hydroQuebrada")return on("quebradas");
 if(k==="district")return on("distrito");
 if(k==="agri")return on("agricola")||on("exposicion");
 return false;
}
async function ensure(k){
 if(!S.ctx||!needs(k)||S.phase[k]!=="pendiente"||S.started[k])return;
 S.started[k]=true;S.phase[k]="cargando";paintStatus();
 let where="1=1",fields="*",max=1700;
 if(k==="district"){where="IDDPTO='14'";fields="IDDPTO,IDPROV,NOMBPROV,IDDIST,NOMBDIST";max=220}
 else if(k==="hydroRio"){where="tipo IN ('R','RN','RI','RS','AC')";fields="tipo,nombre,r_q_text";max=2000}
 else if(k==="hydroQuebrada"){where="tipo IN ('Q','Q1','QB','QQ','QI','QS')";fields="tipo,nombre,r_q_text";max=2000}
 else if(k==="historical"){where="1=1";fields="objectid,nom_dep,tipo_pel,fecha_doc,fuente,url";max=2000}
 else if(k==="agri"){where="1=1";fields="OBJECTID_1,NOMBDIST,CATEGORIA,USO";max=300}
 try{
  let results=await fetchJSON(queryUrl(k,where,fields,max));
  // Distrito: fallback a la capa vectorial referencial de SIGRID si SERFOR bloquea las consultas.
  if(k==="district")results=results.filter(f=>f.geometry&&["Polygon","MultiPolygon"].includes(f.geometry.type));
  if(k==="historical")results=results.filter(f=>f.geometry?.type==="Point");
  if(k.startsWith("hydro"))results=results.filter(f=>["LineString","MultiLineString"].includes(f.geometry?.type));
  if(k==="agri")results=results.filter(f=>["Polygon","MultiPolygon"].includes(f.geometry?.type));
  S.features[k]=results;S.partial[k]=results.length>=max;
  S.phase[k]=results.length?"listo":"vacío";
  S.count[k]=results.length;
  if(!results.length)S.note[k]="El servidor respondió sin geometrías para esta zona. No se simulan elementos.";
 }catch(error){
  if(k==="district"){
   try{
    const old=geoService.district;
    geoService.district=HOST+"/6020300";
    const res=await fetchJSON(queryUrl("district","iddpto='14'","iddpto,iddist,nombdist,nombprov",180));
    S.features.district=res.filter(f=>["Polygon","MultiPolygon"].includes(f.geometry?.type));
    S.count.district=S.features.district.length;S.phase.district=S.count.district?"listo":"vacío";
    if(!S.count.district)S.note.district="El servicio alternativo SIGRID tampoco entregó distritos.";
   }catch(e){
    S.phase[k]="error";S.note[k]="No respondió el catálogo de geometrías oficiales ("+String(error).slice(0,100)+").";
   }
  }else{
   S.phase[k]="error";S.note[k]="El geoservicio no permitió recuperar GeoJSON ("+String(error).slice(0,110)+").";
  }
 }finally{
  S.started[k]=false;drawVectors();paintStatus();
 }
}
function loadAll(){
 for(const key of ["district","historical","hydroRio","hydroQuebrada","agri"])if(needs(key))ensure(key);
}
function polygonRings(g){
 if(!g)return [];
 return g.type==="Polygon"?[g.coordinates]:g.type==="MultiPolygon"?g.coordinates:[];
}
function lineArrays(g){
 if(!g)return [];
 return g.type==="LineString"?[g.coordinates]:g.type==="MultiLineString"?g.coordinates:[];
}
function pointXY(coords){
 return [S.ctx.scene.x(Number(coords[0])),S.ctx.scene.y(Number(coords[1]))];
}
function coordPath(list){
 return list.filter(p=>Array.isArray(p)&&p.length>=2&&p.every(Number.isFinite))
  .map((p,i)=>{const [x,y]=pointXY(p);return (i?"L":"M")+x.toFixed(2)+" "+y.toFixed(2)}).join(" ");
}
function featurePath(f){
 return polygonRings(f.geometry).flatMap(poly=>poly.map(r=>coordPath(r)+" Z")).join(" ");
}
function centerOf(f){
 let outer=polygonRings(f.geometry).map(p=>p[0]).filter(r=>r?.length>=3);
 if(!outer.length)return null;
 const pts=outer.reduce((a,b)=>a.length>=b.length?a:b,[]);
 // BBox center approximate label anchor, not a geographic claim or a calculated centroid.
 const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);
 return [(Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2];
}
function view(){
 const m=S.ctx?.map;const v=(m?.getAttribute("viewBox")||"0 0 700 340").trim().split(/[\s,]+/).map(Number);
 return v.length===4&&v.every(Number.isFinite)?v:[0,0,700,340];
}
function drawVectors(){
 const c=S.ctx;if(!c)return;const svg=c.map;
 svg.querySelectorAll(".oaf-ux33-svg").forEach(n=>n.remove());
 const defs=tag("defs",{class:"oaf-ux33-svg"});
 const matrix=tag("filter",{id:"oaf-ux33-agri-contrast",x:"0%",y:"0%",width:"100%",height:"100%","color-interpolation-filters":"sRGB"});
 // Strong amber/orange while retaining the exact transparency of the MINAM geometry.
 matrix.append(tag("feColorMatrix",{type:"matrix",
  values:"0 0 0 0 0.90  0 0 0 0 0.39  0 0 0 0 0.07  0 0 0 1 0"}));defs.append(matrix);svg.append(defs);
 const agriculture=[...svg.querySelectorAll('image[data-ux30-server]')]
  .filter(e=>e.dataset.ux30Server?.includes("ServicioGeoINEA"));
 agriculture.forEach(e=>{e.setAttribute("filter","url(#oaf-ux33-agri-contrast)");e.setAttribute("opacity",".92");e.dataset.ux33Agriculture="true"});
 const root=tag("g",{class:"oaf-ux33-svg","clip-path":"url(#oaf-ux30-clip-region)"});
 root.setAttribute("aria-label","Geometrías oficiales con nombres consultables");
 const polygonG=tag("g",{class:"oaf-ux33-polygons"});
 const hydroG=tag("g",{class:"oaf-ux33-hydro"});
 const pointsG=tag("g",{class:"oaf-ux33-points"});
 const labelsG=tag("g",{class:"oaf-ux33-labels","pointer-events":"none"});
 const candidates=[];
 if(c.on("distrito")&&S.features.district.length){
  for(const feature of S.features.district){
   const d=featurePath(feature);if(!d)continue;
   const props=feature.properties||{},name=val(props,"NOMBDIST","nombdist");
   const polygon=tag("path",{d,fill:"none",stroke:"#6a447e","stroke-width":"1.25","stroke-dasharray":"4.5 2",
    "stroke-linejoin":"round","pointer-events":"stroke"});
   polygon.setAttribute("tabindex","0");polygon.setAttribute("role","button");
   polygon.setAttribute("aria-label",name?"Distrito de "+name:"Distrito sin nombre publicado");
   const title=tag("title");title.textContent=name?"Distrito: "+name:"Límite distrital INEI";polygon.append(title);
   polygon.addEventListener("click",()=>writeDetail("Distrito",name||"Sin nombre","INEI/SERFOR: límites censales referenciales"));
   polygon.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();polygon.dispatchEvent(new Event("click"))}});
   polygonG.append(polygon);
   const center=centerOf(feature);
   if(name&&center)candidates.push({kind:"polygon",text:name,coord:center,priority:100,feature});
  }
 }
 for(const [key,color,dash] of [["hydroRio","#087cb6","none"],["hydroQuebrada","#259bb6","5 3"]]){
  const selected=key==="hydroRio"?c.on("drain"):c.on("quebradas");
  if(!selected)continue;
  for(const f of S.features[key]){
   const props=f.properties||{},name=val(props,"r_q_text","nombre"),lines=lineArrays(f.geometry);
   for(const coords of lines){
    const d=coordPath(coords);if(!d)continue;
    const path=tag("path",{d,fill:"none",stroke:color,"stroke-width":"1.7","stroke-dasharray":dash,
      "stroke-linecap":"round","stroke-linejoin":"round","pointer-events":"stroke"});
    const label=(key==="hydroRio"?"Río":"Quebrada")+(name?" "+name:"");
    path.setAttribute("role","button");path.setAttribute("tabindex","0");path.setAttribute("aria-label",label);
    const title=tag("title");title.textContent=label;path.append(title);
    path.addEventListener("click",()=>writeDetail("Red hidrográfica IGN",label,"Inventario cartográfico IGN 1:100 000; no representa caudal."));
    path.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();path.dispatchEvent(new Event("click"))}});
    hydroG.append(path);
    if(name&&coords.length>1)candidates.push({kind:"line",text:label,
      coord:coords[Math.floor(coords.length/2)],priority:key==="hydroRio"?85:70});
   }
  }
 }
 const historical=S.features.historical;
 if(historical.length){
  for(const [index,f] of historical.entries()){
   const p=f.properties||{},kind=category(val(p,"tipo_pel"));
   if(!kind||!c.on(kind))continue;
   const coords=f.geometry?.coordinates;if(!Array.isArray(coords)||coords.length<2||!coords.every(Number.isFinite))continue;
   if(c.state.selected?.length&&c.state.contains&&!c.state.selected.every(sel=>c.state.contains(sel.geo,coords)))continue;
   const [x,y]=pointXY(coords),label=val(p,"tipo_pel")||"Peligro documentado";
   const dot=tag("circle",{cx:x,cy:y,r:"3.9",fill:categories[kind],stroke:"#fff","stroke-width":"1.2",role:"button",tabindex:"0",
    "aria-label":label+" (INGEMMET 2017)"});
   dot.classList.add("oaf-ux33-historic-point");
   const title=tag("title");title.textContent=label+" · "+(val(p,"fecha_doc")||"2017");dot.append(title);
   dot.addEventListener("click",()=>writeDetail("Punto geológico histórico",label,val(p,"fecha_doc")||"2017",val(p,"fuente")||"INGEMMET"));
   dot.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();dot.dispatchEvent(new Event("click"))}});
   pointsG.append(dot);
   candidates.push({kind:"point",text:label,coord:coords,priority:50,increment:index});
  }
 }
 // Labels for emergency points are taken from the names already supplied by IGN/IDEP.
 for(const symbol of svg.querySelectorAll("circle.oaf-ux28-emergency-marker")){
  const name=(symbol.getAttribute("aria-label")||"").replace(/;\s*consultar ficha.*/i,"").trim();
  if(name&&!/sin nombre|registro$/i.test(name)){
   const x=Number(symbol.getAttribute("cx")),y=Number(symbol.getAttribute("cy"));
   if(Number.isFinite(x)&&Number.isFinite(y))candidates.push({kind:"xy",text:name,xy:[x,y],priority:110});
  }
 }
 // Where MINAM supplies category/district metadata, label the agricultural polygons by that source attribute.
 if((c.on("agricola")||c.on("exposicion"))&&S.features.agri.length){
  for(const f of S.features.agri){
   const p=f.properties||{},className=val(p,"CATEGORIA"),district=val(p,"NOMBDIST");
   const label=className||district;const center=centerOf(f);
   if(label&&center)candidates.push({kind:"agri",text:label,coord:center,priority:65});
  }
 }
 root.append(polygonG,hydroG,pointsG,labelsG);svg.append(root);
 S.labelCandidates=candidates;S.svgRoot=root;S.labelGroup=labelsG;
 drawLabels();
 paintStatus();
}
function category(value){
 const v=norm(value);
 if(v.includes("inundacion fluvial"))return "fluvial";
 if(v.includes("inundacion pluvial")||v.includes("precipitacion pluvial"))return "pluvial";
 if(v.includes("erosion fluvial"))return "erosion";
 if(v.includes("detrito")||v.includes("lodo")||v==="flujos")return "detritos";
 return "";
}
function drawLabels(){
 const ctx=S.ctx,group=S.labelGroup;if(!ctx||!group)return;
 group.replaceChildren();
 const [vx,vy,vw,vh]=view(),k=vw/700;
 const maxLabels=vw>500?18:vw>280?44:vw>120?88:160;
 const occupied=[];
 const candidates=(S.labelCandidates||[]).slice().sort((a,b)=>b.priority-a.priority);
 let count=0;
 for(const entry of candidates){
  if(count>=maxLabels)break;
  const [x,y]=entry.xy||pointXY(entry.coord);
  const sx=(x-vx)/vw*700,sy=(y-vy)/vh*340;
  if(!Number.isFinite(sx)||!Number.isFinite(sy)||sx<8||sx>688||sy<14||sy>330)continue;
  const str=String(entry.text||"").trim().slice(0,50);if(!str)continue;
  const width=Math.min(185,Math.max(35,str.length*5.4)),height=15;
  const px=entry.kind==="point"||entry.kind==="xy"?sx+12:sx;
  const py=entry.kind==="point"||entry.kind==="xy"?sy-6:sy;
  const box={x:px-5,y:py-11,w:width+10,h:height+4};
  if(box.x<0||box.x+box.w>700)continue;
  if(occupied.some(a=>a.x<box.x+box.w&&a.x+a.w>box.x&&a.y<box.y+box.h&&a.y+a.h>box.y))continue;
  occupied.push(box);
  const t=tag("text",{x:(vx+px/700*vw).toFixed(2),y:(vy+py/340*vh).toFixed(2),
    fill:entry.kind==="line"?"#165c86":entry.kind==="agri"?"#713b14":"#214e40",
    "font-size":(11.2*k).toFixed(3),"font-weight":"700",
    "paint-order":"stroke","stroke":"#fff","stroke-width":(2.8*k).toFixed(3),
    "stroke-linejoin":"round","pointer-events":"none"});
  t.textContent=str;group.append(t);count++;
 }
 // Keep clickable points, label sizes and stroke widths consistent during zoom.
 for(const dot of group.parentNode?.querySelectorAll("circle.oaf-ux33-historic-point")||[]){
  dot.setAttribute("r",Math.max(.45,3.9*k).toFixed(3));
  dot.setAttribute("stroke-width",Math.max(.14,1.1*k).toFixed(3));
 }
 for(const path of group.parentNode?.querySelectorAll("path")||[]){
  path.setAttribute("stroke-width",Math.max(.13,1.5*k).toFixed(3));
 }
}
function writeDetail(subject,label,detail,source){
 const pane=el("oaf-ux29-territory"),existing=el("oaf-ux33-selected-detail");
 let section=existing;
 if(!section){
  section=document.createElement("section");section.id="oaf-ux33-selected-detail";section.className="oaf-ux30-diagnosis-item";
  pane?.querySelector(".oaf-ux29-diagextras")?.prepend(section);
 }
 section.replaceChildren();
 const h=document.createElement("strong");h.textContent=subject+": "+label;
 const p=document.createElement("p");p.textContent=detail+(source?" · "+source:"");
 section.append(h,p);
}
function paintStatus(){
 const ctx=S.ctx;if(!ctx)return;
 const host=el("oaf-ux29-territory")?.querySelector(".oaf-ux29-mapcontent");if(!host)return;
 let bar=el("oaf-ux33-status");
 if(!bar){bar=document.createElement("div");bar.id="oaf-ux33-status";bar.className="oaf-ux33-status";
  bar.setAttribute("role","status");host.prepend(bar)}
 const active=Object.keys(S.phase).filter(needs);
 if(!active.length){bar.hidden=true;return}
 bar.hidden=false;
 const labels={district:"Distritos",hydroRio:"Ríos",hydroQuebrada:"Quebradas",historical:"Puntos INGEMMET",agri:"Agricultura"};
 const messages=active.map(key=>{
  const state=S.phase[key];
  return labels[key]+": "+(state==="listo"?S.count[key]+" registros":state==="cargando"?"consultando":
   state==="vacío"?"0 geometrías":state==="error"?"sin conexión":state);
 });
 bar.textContent=messages.join(" · ")+" — Etiquetas según atributos disponibles.";
}
function appendDiagnosis(box){
 if(!box)return;
 const chosen=Object.keys(S.phase).filter(needs);if(!chosen.length)return;
 const part=document.createElement("section");part.className="oaf-ux30-diagnosis-item";
 const heading=document.createElement("strong");heading.textContent="Estado de geometrías y etiquetas";
 const desc=document.createElement("p");
 const name={district:"límites distritales",hydroRio:"ríos IGN",hydroQuebrada:"quebradas IGN",historical:"peligros INGEMMET",agri:"superficie agrícola MINAM"};
 desc.textContent=chosen.map(k=>name[k]+": "+(S.phase[k]==="listo"?S.count[k]+" registros":S.phase[k])+(S.note[k]?" ("+S.note[k]+")":"")).join(" · ")+
 ". Los nombres se muestran únicamente cuando forman parte de los atributos oficiales. La falta de datos se indica; no se inventan ubicaciones.";
 part.append(heading,desc);box.append(part);
}
function start(ctx){
 S.ctx=ctx;
 // Render attached to the legacy map is available even if the previous draw completed before initialization.
 drawVectors();loadAll();
}
function retry(key){
 if(["district","historical","hydroRio","hydroQuebrada","agri"].includes(key) &&
    S.phase[key]==="error"){S.phase[key]="pendiente";S.note[key]="";}
 loadAll();
 drawVectors();
}
function init(){
 window.oafUx33AfterDraw=start;
 window.oafUx33OnZoom=()=>drawLabels();
 window.oafUx33LayerChange=(key)=>{
  const names={distrito:"district",fluvial:"historical",pluvial:"historical",
    detritos:"historical",erosion:"historical",drain:"hydroRio",quebradas:"hydroQuebrada",
    agricola:"agri",exposicion:"agri"};
  if(names[key])retry(names[key]);
 };
 window.oafUx33Diagnosis=appendDiagnosis;
 if(typeof window.oafUx30RequestDraw==="function")window.oafUx30RequestDraw();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
else init();
})();