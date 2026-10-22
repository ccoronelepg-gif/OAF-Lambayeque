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
const SIG="https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer";
const MINAM="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer";
const MTC="https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer";
const WMS="https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms";
const HEAT_WMS="g_01_06:01_06_001_03_001_512_0000_00_00";
const COMPANIES="datos/riesgos_ux35/ubicaciones_agroindustriales_referenciales.geojson";
const YEARS=[1983,1998,2017,2023];
const FALLBACK_PAGES={
 old2017:"https://sigrid.cenepred.gob.pe/sigridv3/documento/16310",
 climate:"https://enfen.imarpe.gob.pe/comunicados/",
 senamhi:"https://www.senamhi.gob.pe/"
};
const addKeys=[
 ["pastRain","Lluvia histórica · comparación 1983/1998/2017/2023","Estimación de lluvia acumulada enero–marzo por localidad de Open-Meteo Archive (reconstrucción modelada). No son datos medidos por una estación ni un mapa continuo."],
 ["pastFlood","Puntos históricos de inundación fluvial y pluvial · 2017","Registros geológicos históricos INGEMMET del Niño Costero 2017. Un punto señala un sitio registrado, no la superficie inundada."],
 ["pastMass","Deslizamientos y flujos documentados · 2017","Registros geológicos de flujos de detritos y movimientos en masa del Niño Costero 2017 cuando el inventario tiene esa clasificación."],
 ["past2023","Escenario de riesgo de El Niño · CENEPRED 2023","Estudio oficial de 2023 que considera 1983, 1998, 2017 y 2023 para analizar riesgos de inundación y movimientos en masa. La ficha enlaza el estudio; no se dibuja una geometría no verificada."],
 ["rain7","Lluvia pronosticada · próximos siete días","Pronóstico puntual Open-Meteo para Chiclayo, Jayanca, Motupe y Olmos. Se acumula en la ventana seleccionada; no representa toda la región."],
 ["seasonal","Perspectiva noviembre 2026–verano 2027 · ENFEN","ENFEN N.º 18-2026 (16/10) anticipa lluvias sobre lo normal en costa norte, caudales altos en el río La Leche desde noviembre y altas temperaturas. Es una perspectiva cualitativa, sin mm mensuales por distrito."],
 ["futureFlood","Escenario orientativo: lluvia + susceptibilidad a inundación","Permite contrastar señales meteorológicas con zonas susceptibles cartografiadas. No predice dónde se inundará, ni niveles o probabilidades."],
 ["futureMass","Escenario orientativo: movimientos en masa","Contrasta la susceptibilidad de laderas con señales de lluvia. No calcula la probabilidad ni los lugares exactos de deslizamientos."],
 ["futureRiver","Vigilancia de crecidas y desbordes","Muestra ríos y zonas susceptibles. Sin caudal hidrométrico calibrado no es posible afirmar que un río se desbordará."],
 ["futureDrought","Posible sequía y déficit hídrico","La lluvia insuficiente sostenida puede originar déficit hídrico agrícola. Se requiere SPI, suelo y reservas; no se dibuja un polígono futuro de sequía."],
 ["futureHeat","Mapas históricos de calor · SENAMHI","Frecuencia estacional de olas de calor y un antecedente térmico puntual. No es un pronóstico de temperatura extrema para una fecha específica."],
 ["companies","Empresas agroindustriales y fundos referenciales","Muestra oficinas y algunos terrenos agroindustriales con coordenadas públicas de OpenStreetMap. La formalidad tributaria de cada empresa debe verificarse con SUNAT; no es censo regional."]
];
const extra=new Map(addKeys.map(([id,name,meaning])=>[id,{name,meaning}]));
const state={
 on:{pastRain:true,pastFlood:true,pastMass:false,past2023:false,rain7:true,seasonal:true,
 futureFlood:true,futureMass:false,futureRiver:false,futureDrought:false,futureHeat:false,companies:true},
 territorial:{base:true,departamento:true,provincia:true,regional:true,agricola:true},
 year:2017,days:7,threshold:40,
 comp:[],companyStatus:"pendiente",
 history:new Map(),historyStatus:"pendiente",historyError:"",historyRequested:new Set(),
 histLocations:[],loaded:false,active:null,ready:false,current:[],
 zoomObserver:null,selectionName:"Todo Lambayeque"
};
const stations=[
 {name:"Chiclayo",lat:-6.7714,lon:-79.8409},{name:"Jayanca",lat:-6.39278,lon:-79.8228},
 {name:"Motupe",lat:-6.15083,lon:-79.7142},{name:"Olmos",lat:-5.98825,lon:-79.74723}
];
const enabled=k=>!!(state.on[k]??state.territorial[k]);
function activate(){
 const pane=$("oaf-ux29-scenario");if(!pane||pane.dataset.ux35Active==="true")return;
 pane.dataset.ux35Active="true";
 const root=$("oaf-escenarios-riesgo-agroclimatico");
 root?.classList.add("oaf-ux35-only-visor");
 const intro=pane.querySelector(".oaf-ux29-top");
 if(intro)intro.innerHTML='<span class="oaf-ux29-kicker">OAF-LAMBAYEQUE · ANÁLISIS RETROSPECTIVO Y ESCENARIOS</span>'+
  '<h2>Visor de escenarios de riesgo agroclimático</h2>'+
  '<p>Superpón antecedentes de El Niño, pronósticos meteorológicos y capas territoriales para identificar ámbitos que merecen vigilancia preventiva. El diagnóstico diferencia evidencia histórica, señales actuales y escenarios no validados.</p>';
 const maphead=pane.querySelector(".oaf-ux29-maphead");
 if(maphead)maphead.querySelector("strong").textContent="Mapa multicapa · Lambayeque";
 const tree=pane.querySelector(".oaf-ux29-tree");
 if(tree){tree.replaceChildren();buildTree(tree)}
 const map=pane.querySelector(".oaf-ux29-mapcontent");
 if(map)map.innerHTML='<div class="oaf-ux35-mapintro">Selecciona los grupos de capas para comparar antecedentes, pronósticos y exposición agrícola. Haz clic en un punto para ver la información disponible.</div>'+
 '<div class="oaf-ux29-scenemap"><svg id="oaf-ux29-forecast-map" viewBox="0 0 700 380" role="img" aria-label="Visor geográfico de escenarios del Niño, pronósticos de lluvia y territorio de Lambayeque"></svg>'+
 '<p class="oaf-ux29-mapcaption">Capas históricas y de susceptibilidad superpuestas; los círculos de lluvia son consultas puntuales y no predicciones de polígonos afectados.</p></div>'+
 '<div class="oaf-ux35-outlook" id="oaf-ux35-outlook"><strong>Perspectiva regional ENFEN · Comunicado 18-2026</strong>'+
 '<div><span>Nov.–dic. 2026: lluvias sobre lo normal en costa norte</span><span>Verano 2027: lluvias sobre lo normal en costa norte</span><span>Río La Leche: caudales superiores a lo normal principalmente desde noviembre</span></div>'+
 '<small>Escenarios regionales cualitativos: no son mm mensuales por distrito ni huellas futuras de inundación.</small></div>'+
 '<div id="oaf-ux35-mapstatus" role="status" class="oaf-ux35-mapstatus">Consultando geocapas y pronósticos…</div>';
 const extraSlot=pane.querySelector(".oaf-ux29-diagextras");
 if(extraSlot)extraSlot.innerHTML='<div class="oaf-ux35-method"><strong>Interpretación científica</strong>'+
  '<p>La susceptibilidad es una propiedad territorial. Una lluvia prevista no demuestra inundación. Las estimaciones históricas, la perspectiva estacional y la predicción a siete días son fuentes distintas.</p></div>';
 pane.addEventListener("change",handleChange);
 pane.addEventListener("click",handleClick);
 const svg=$("oaf-ux29-forecast-map");
 if(svg){
  state.zoomObserver=new MutationObserver(()=>applyZoomStyles(svg));
  state.zoomObserver.observe(svg,{attributes:true,attributeFilter:["viewBox"]});
 }
 window.addEventListener("oaf:geodata",()=>{if(state.ready)render()});
 window.addEventListener("oaf:emergencydata",()=>{if(state.ready)render()});
 loadCompanies();
 attachTerritoryFilters();
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
 const overview=E("div","oaf-ux35-tree-intro");overview.textContent="Activa cada capa con su casilla. Las categorías se pueden combinar sin perder su procedencia.";
 tree.append(overview);
 const historic=group(tree,"1 · Antecedentes del Fenómeno El Niño",true);
 for(const key of ["pastRain","pastFlood","pastMass","past2023"]){
  const e=extra.get(key);check(historic,key,e.name,state.on[key],key==="pastRain"?"Reanálisis histórico; cuatro localidades":key==="past2023"?"Estudio oficial; enlace en Metadatos":"Inventario geológico 2017");
 }
 field(historic,"Año para comparar acumulados enero–marzo","oaf-ux35-histyear",YEARS.map(y=>[y,String(y)]),state.year);
 const forecast=group(tree,"2 · Lluvias pronosticadas y perspectivas",true);
 for(const key of ["rain7","seasonal"]){const e=extra.get(key);check(forecast,key,e.name,state.on[key])}
 field(forecast,"Horizonte del pronóstico","oaf-ux35-horizon",[[3,"Próximos 3 días"],[7,"Próximos 7 días"]],state.days);
 field(forecast,"Umbral descriptivo de lluvia acumulada","oaf-ux35-threshold",[[20,"20 mm"],[40,"40 mm"],[70,"70 mm"],[100,"100 mm"]],state.threshold);
 const possible=group(tree,"3 · Consecuencias y peligros potenciales",true);
 for(const key of ["futureFlood","futureMass","futureRiver","futureDrought","futureHeat"]){
  const e=extra.get(key);check(possible,key,e.name,state.on[key],["futureFlood","futureRiver","futureDrought"].includes(key)?"Vigilancia, no alerta confirmada":null);
 }
 const companies=group(tree,"4 · Agricultura y empresas agroindustriales",true);
 check(companies,"companies",extra.get("companies").name,state.on.companies,"Muestra georreferenciada OSM · sin padrón completo");
 const catalog=window.oafUx30Catalog?.()||[];
 for(const grp of catalog){
  const sec=group(tree,"Territorio · "+grp.title,false);
  for(const entry of grp.entries){
   if(entry.key==="agroflood")continue;
   if(state.territorial[entry.key]===undefined)state.territorial[entry.key]=false;
   check(sec,"territory:"+entry.key,entry.label,state.territorial[entry.key],
    ["exposicion","agroflood"].includes(entry.key)?"Cruce visual, no hectáreas":null);
  }
 }
 const regional=group(tree,"5 · Filtros geográficos",true);
 regional.innerHTML+='<div class="oaf-ux35-sync-note">Los filtros se comparten con el visor territorial para utilizar sus límites oficiales.</div>';
 for(const [id,label] of [["prov","Provincia"],["dist","Distrito"],["basin","Cuenca"]]){
  const wrap=E("label","oaf-ux35-field");wrap.textContent=label;
  const input=E("select");input.id="oaf-ux35-"+id;input.dataset.ux35Filter=id;wrap.append(input);regional.append(wrap);
 }
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
function handleChange(e){
 const target=e.target;
 if(target.dataset.ux35Key){
  const key=target.dataset.ux35Key;
  if(key.startsWith("territory:"))state.territorial[key.slice(10)]=target.checked;
  else state.on[key]=target.checked;
  requestSharedData();
  if(key==="pastRain"&&state.on.pastRain)loadHistory(state.year);
  if(key==="rain7"&&state.on.rain7)window.oafUx29ScenarioApi?.loadRain();
  render();return;
 }
 if(target.id==="oaf-ux35-histyear"){
  state.year=Number(target.value);state.active=null;
  if(state.on.pastRain)loadHistory(state.year);render();return;
 }
 if(target.id==="oaf-ux35-horizon"){state.days=Number(target.value);render();return}
 if(target.id==="oaf-ux35-threshold"){state.threshold=Number(target.value);render();return}
 if(target.dataset.ux35Filter){
  const ref=$("oaf-ux26-"+target.dataset.ux35Filter);
  if(ref&&[...ref.options].some(opt=>opt.value===target.value)){
   ref.value=target.value;ref.dispatchEvent(new Event("change",{bubbles:true}));
   setTimeout(render,500);
  }
 }
}
function handleClick(e){
 const action=e.target.closest("[data-ux35-action]");
 if(!action)return;
 const command=action.dataset.ux35Action;
 if(command==="retry-history"){state.history.delete(state.year);loadHistory(state.year);render()}
 if(command==="retry-companies"){state.companyStatus="pendiente";loadCompanies();}
}
function requestSharedData(){
 const wanted={
  district:enabled("distrito")||enabled("provincia"),
  historical:enabled("fluvial")||enabled("pluvial")||enabled("erosion")||enabled("detritos")||state.on.pastFlood||state.on.pastMass,
  hydroRio:enabled("drain")||state.on.futureRiver,hydroQuebrada:enabled("quebradas"),
 };
 window.oafUx35Wants=wanted;
 window.oafUx33Load?.();
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
 state.ready=true;
 const viewBox=svg.getAttribute("viewBox")||"0 0 700 380";
 svg.replaceChildren();svg.setAttribute("viewBox",viewBox);
 svg.append(SVG("rect",{x:0,y:0,width:700,height:380,fill:"#f0f7f2"}));
 const defs=SVG("defs"),clip=SVG("clipPath",{id:"oaf-ux35-region-clip",clipPathUnits:"userSpaceOnUse"});
 for(const ring of scene.rings){
  clip.append(SVG("path",{d:ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+" "+scene.y(p[1]).toFixed(2)).join(" ")+" Z"}));
 }
 defs.append(clip);svg.append(defs);
 const ctx=window.oafUx30Context?.();
 const clipRoots=(ctx?.selected||[]).filter(e=>e.geo);
 const polygonD=g=>{
  const geom=g?.type==="Feature"?g.geometry:g;
  const polygons=geom?.type==="Polygon"?[geom.coordinates]:geom?.type==="MultiPolygon"?geom.coordinates:[];
  return polygons.flatMap(poly=>poly.map(r=>r.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+
   " "+scene.y(p[1]).toFixed(2)).join(" ")+" Z")).join(" ");
 };
 const base=SVG("g",{"clip-path":"url(#oaf-ux35-region-clip)"});svg.append(base);
 let region=base;
 clipRoots.forEach((v,i)=>{
  const path=polygonD(v.geo);if(!path)return;
  const c=SVG("clipPath",{id:"oaf-ux35-filter-"+i,clipPathUnits:"userSpaceOnUse"});
  c.append(SVG("path",{d,"fill-rule":"evenodd","clip-rule":"evenodd"}));
  defs.append(c);
  const group=SVG("g",{"clip-path":"url(#oaf-ux35-filter-"+i+")"});region.append(group);region=group;
 });
 const bound=scene.bounds;
 const raster=(service,ids,alpha,label,params={})=>{
  const q=new URLSearchParams({bbox:[bound.minLon,bound.minLat,bound.maxLon,bound.maxLat].join(","),
   bboxSR:"4326",imageSR:"4326",size:"1000,515",format:"png32",transparent:"true",dpi:"110",
   layers:"show:"+ids,f:"image",...params});
  const img=SVG("image",{href:service+"/export?"+q,x:0,y:0,width:700,height:340,opacity:alpha,
   preserveAspectRatio:"none","pointer-events":"none"});
  const title=SVG("title");title.textContent=label;img.append(title);region.append(img);
 };
 if(enabled("regional")||state.on.futureFlood||enabled("exposicion"))raster(CEN,"5010502",.7,"Susceptibilidad regional a inundaciones");
 if(enabled("movmasa")||state.on.futureMass)raster(CEN,"5090022",.44,"Movimientos en masa");
 if(enabled("inundacionregion"))raster("https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer","0",.42,"Susceptibilidad fluvial en polígonos");
 if(enabled("agricola")||enabled("exposicion")||enabled("agroflood")){
  raster(MINAM,"1",.87,"Superficie agrícola MINAM 2018");
 }
 if(enabled("departamento")||enabled("provincia"))raster(SIG,[enabled("departamento")?"6020100":null,enabled("provincia")?"6020200":null].filter(Boolean).join(","),.68,"Límites políticos");
 if(enabled("basin"))raster(SIG,"6030100",.52,"Cuencas ANA");
 const rds=[enabled("vecinal")?"8":null,enabled("departamental")?"9":null,enabled("nacional")?"10":null].filter(Boolean);
 if(rds.length)raster(MTC,rds.join(","),.84,"Red vial MTC");
 if(enabled("heat")||state.on.futureHeat){
  const q=new URLSearchParams({SERVICE:"WMS",VERSION:"1.1.1",REQUEST:"GetMap",LAYERS:HEAT_WMS,STYLES:"",
   SRS:"EPSG:4326",BBOX:[bound.minLon,bound.minLat,bound.maxLon,bound.maxLat].join(","),
   WIDTH:"1050",HEIGHT:"510",FORMAT:"image/png",TRANSPARENT:"TRUE"});
  region.append(SVG("image",{href:WMS+"?"+q,x:0,y:0,width:700,height:340,opacity:.4,preserveAspectRatio:"none","pointer-events":"none"}));
 }
 const shared=window.oafUx33Data?.();
 const textCandidates=[];
 const points=[];
 const inFilter=coords=>!ctx?.selected?.length||!ctx.contains||ctx.selected.every(t=>ctx.contains(t.geo,coords));
 const line=(pts,stroke,dash,width,title)=>{
  const d=pts.filter(p=>p?.length>=2).map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(2)+" "+scene.y(p[1]).toFixed(2)).join(" ");
  if(!d)return;
  const path=SVG("path",{d,fill:"none",stroke,"stroke-width":width,
   "stroke-dasharray":dash||"none","stroke-linecap":"round","pointer-events":"stroke"});
  if(title){const tt=SVG("title");tt.textContent=title;path.append(tt)}
  region.append(path);
 };
 const polyrings=g=>g?.type==="Polygon"?[g.coordinates]:g?.type==="MultiPolygon"?g.coordinates:[];
 const serviceDetails=(label,detail)=>{
  const body=pane.querySelector(".oaf-ux29-diagextras");if(!body)return;
  let box=$("oaf-ux35-selection");
  if(!box){box=E("div","oaf-ux35-selected");box.id="oaf-ux35-selection";body.prepend(box)}
  box.replaceChildren();
  const strong=E("strong");strong.textContent=label;
  const p=E("p");p.textContent=detail;
  box.append(strong,p);
 };
 // Shared cartography from geographic visor, with exact class and date.
 const drawPolygon=f=>{
  const rings=polyrings(f.geometry);
  for(const poly of rings)for(const ring of poly)line(ring,"#67438f","4 2",1.3,"Límite distrital INEI");
 };
 if(shared&&enabled("distrito")){
  for(const f of shared.features?.district||[]){
   if(!f.geometry)continue;drawPolygon(f);
   const p=f.properties||{},name=p.NOMBDIST||p.nombdist;
   if(name){const ring=polyrings(f.geometry)?.[0]?.[0];if(ring?.length>2){
    const x=ring.reduce((a,v)=>a+v[0],0)/ring.length,y=ring.reduce((a,v)=>a+v[1],0)/ring.length;
    textCandidates.push({name,x:scene.x(x),y:scene.y(y),rank:90});
   }}
  }
 }
 const hydro=shared?.features||{};
 const drawHydro=(key,show,color)=>{
  if(!show)return;
  for(const f of hydro[key]||[]){
   const g=f.geometry,lines=g?.type==="MultiLineString"?g.coordinates:g?.type==="LineString"?[g.coordinates]:[];
   const p=f.properties||{},name=p.r_q_text||p.nombre||"";
   for(const coords of lines){
    line(coords,color,key==="hydroQuebrada"?"5 3":null,1.55,name);
    if(name&&coords.length)textCandidates.push({name,x:scene.x(coords[Math.floor(coords.length/2)][0]),y:scene.y(coords[Math.floor(coords.length/2)][1]),rank:70});
   }
  }
 };
 drawHydro("hydroRio",enabled("drain")||state.on.futureRiver,"#1265a0");
 drawHydro("hydroQuebrada",enabled("quebradas"),"#259bb8");
 const kinds={fluvial:"#277bc0",pluvial:"#4178bb",erosion:"#b84e46",detritos:"#ab792a"};
 for(const f of shared?.features?.historical||[]){
  const p=f.properties||{},txt=String(p.tipo_pel||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
  const kind=txt.includes("inundacion fluvial")?"fluvial":txt.includes("inundacion pluvial")||txt.includes("precipitacion pluvial")?"pluvial":
   txt.includes("erosion fluvial")?"erosion":txt.includes("detrito")||txt.includes("lodo")?"detritos":null;
  if(!kind||!(enabled(kind)||state.on.pastFlood&&["fluvial","pluvial"].includes(kind)||state.on.pastMass&&kind==="detritos"))continue;
  const coords=f.geometry?.coordinates;if(!coords||!inFilter(coords))continue;
  points.push({lon:coords[0],lat:coords[1],color:kinds[kind],label:p.tipo_pel||kind,
   detail:"Inventario histórico INGEMMET · El Niño Costero 2017. "+(p.fecha_doc||"")+" · Ubicación puntual, no área afectada.",type:"hist"});
 }
 for(const p of ctx?.points||[]){
  if(!["drought","heat"].includes(p.category)||!enabled(p.category)&&!(p.category==="heat"&&state.on.futureHeat)&&!(p.category==="drought"&&state.on.futureDrought))continue;
  if(!inFilter(p.coords))continue;
  points.push({lon:p.coords[0],lat:p.coords[1],label:p.label,color:p.color,detail:p.detail||p.source,type:"climate"});
 }
 // Servicios de emergencia: mismas capas de IGN/IDEP que el visor territorial.
 const services=window.oafUx28Points?.()?.points||{};
 const colors={hospital:"#c24b49",posta:"#3e9f77",policia:"#315f9c",bomberos:"#ef9236"};
 for(const kind of Object.keys(colors)){
  if(!enabled(kind))continue;
  for(const feature of services[kind]||[]){
   const coords=feature.geometry?.coordinates;
   if(!Array.isArray(coords)||!inFilter(coords))continue;
   const p=feature.properties||{};
   const name=p.NOMBRE||p.nombre||("Establecimiento "+kind);
   points.push({lon:coords[0],lat:coords[1],label:name,color:colors[kind],type:"emergency",
    detail:"Infraestructura IGN/IDEP: "+kind+". La posición cartográfica no confirma atención, horarios ni capacidad de emergencia."});
  }
 }
 for(const f of state.comp){
  if(!state.on.companies)break;
  const p=f.properties||{},coords=f.geometry.coordinates;
  if(!inFilter(coords))continue;
  points.push({lon:coords[0],lat:coords[1],label:p.nombre,color:"#8754a3",type:"company",
   detail:(p.tipo==="oficina"?"Oficina":"Área agrícola referencial")+" · "+p.distrito+". "+
     p.observacion+" · "+p.estatus_formal_verificado+". Fuente geográfica: OpenStreetMap / Mapcarta."});
 }
 // Forecast is not spatially interpolated.
 if(state.on.rain7){
  for(const p of api.daily?.items||[]){
   const total=p.rain.slice(0,state.days).reduce((a,b)=>a+Number(b),0);
   const flag=total>=state.threshold;
   if(!inFilter([p.lon,p.lat]))continue;
   points.push({lon:p.lon,lat:p.lat,label:p.name+" · "+total.toFixed(1)+" mm previstos",
    color:flag?"#c45b36":"#187eaa",type:"forecast",radius:11,
    detail:"Pronóstico Open-Meteo: "+total.toFixed(1)+" mm acumulados en "+state.days+" días. "+
     (flag?"Supera el umbral descriptivo seleccionado; NO equivale a alerta oficial.":"Por debajo del umbral descriptivo seleccionado.")});
  }
 }
 if(state.on.pastRain){
  const hist=state.history.get(state.year);
  for(const p of hist?.records||[]){
   if(!inFilter([p.lon,p.lat]))continue;
   points.push({lon:p.lon,lat:p.lat,label:p.name+" · "+Math.round(p.sum)+" mm · "+state.year,
    color:"#8171b8",type:"history",radius:8,
    detail:"Estimación histórica de reanálisis para enero–marzo "+state.year+": "+p.sum.toFixed(1)+
     " mm. No es medición de pluviómetro ni mapa de lluvia continua."});
  }
 }
 // Symbols are interactive and their sizes are corrected on zoom.
 for(const p of points){
  const x=scene.x(p.lon),y=scene.y(p.lat);
  if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>700||y<0||y>340)continue;
  const dot=SVG("circle",{cx:x,cy:y,r:p.radius||4.5,fill:p.color,stroke:"#fff","stroke-width":1.5,tabindex:"0",role:"button",
   "aria-label":p.label});
  dot.dataset.ux35Radius=p.radius||4.5;
  dot.classList.add("oaf-ux35-point");
  const title=SVG("title");title.textContent=p.label;dot.append(title);
  dot.addEventListener("click",()=>{state.active=p;serviceDetails(p.label,p.detail);diagnosis()});
  dot.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();dot.dispatchEvent(new Event("click"))}});
  region.append(dot);
  textCandidates.push({name:p.label,x,y,rank:p.type==="company"?85:p.type==="forecast"?100:p.type==="history"?70:45});
 }
 const outline=SVG("g",{"pointer-events":"none"});
 for(const ring of scene.rings){
  outline.append(SVG("path",{d:ring.map((p,i)=>(i?"L":"M")+scene.x(p[0]).toFixed(1)+" "+scene.y(p[1]).toFixed(1)).join(" ")+" Z",
   fill:"none",stroke:"#28644e","stroke-width":2}));
 }
 svg.append(outline);
 const labels=SVG("g",{id:"oaf-ux35-labels","pointer-events":"none"});svg.append(labels);
 const footer=SVG("text",{x:350,y:361,fill:"#3b5b50","font-size":12,"text-anchor":"middle"});
 footer.textContent="Antecedentes y susceptibilidad ≠ pronóstico hidráulico de inundación";svg.append(footer);
 state.current=textCandidates;
 renderLabels();
 status();
 diagnosis();
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
 const outlook=$("oaf-ux35-outlook");if(outlook)outlook.hidden=!state.on.seasonal;
 const shared=window.oafUx33Data?.()?.phase||{};
 const hist=state.history.get(state.year);
 const signals=[
  "Lluvia prevista: "+(data().daily?.state||"pendiente"),
  state.on.pastRain?"Lluvia histórica "+state.year+": "+(hist?hist.records.length+" de 4 puntos":state.historyRequested.has(state.year)?"consultando":"sin consultar"):null,
  state.on.companies?"Agroindustrias: "+state.companyStatus:null,
  (enabled("drain")||state.on.futureRiver)?"Ríos: "+(shared.hydroRio||"sin respuesta"):null,
  enabled("quebradas")?"Quebradas: "+(shared.hydroQuebrada||"sin respuesta"):null,
  (state.on.pastFlood||state.on.pastMass)?"Puntos INGEMMET: "+(shared.historical||"sin respuesta"):null
 ].filter(Boolean);
 display.textContent=signals.join(" · ");
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
 section("Ámbito territorial",selected||"Región Lambayeque · mapa referencial",
  "Los filtros dependen de la cartografía oficial disponible.");
 const current=data(),daily=current.daily;
 if(state.on.rain7){
  if(!daily||daily.state==="pendiente"||daily.state==="cargando")section("Lluvia de los próximos "+state.days+" días","Consultando pronóstico meteorológico externo.");
  else if(daily.items?.length){
   const found=daily.items.map(p=>({name:p.name,amount:p.rain.slice(0,state.days).reduce((a,b)=>a+Number(b),0)}))
    .sort((a,b)=>b.amount-a.amount);
   section("Lluvias pronosticadas · "+state.days+" días",
    found.map(p=>p.name+": "+p.amount.toFixed(1)+" mm").join(" · ")+
    ". Son cuatro localidades puntuales; no permiten deducir lluvia continua sobre cada cuenca.");
   const high=found.filter(p=>p.amount>=state.threshold);
   section("Posible señal de acumulación",
    high.length?"El acumulado supera "+state.threshold+" mm en "+high.map(i=>i.name).join(", ")+
     ". Esto justifica revisar avisos oficiales, no constituye una predicción de inundación.":
     "Ninguna localidad consultada supera el umbral orientativo de "+state.threshold+
     " mm. No se descartan lluvias fuertes en otros sectores.");
  }else section("Lluvia prevista","El proveedor no devolvió datos meteorológicos suficientes. No se realizan estimaciones.");
 }
 if(state.on.pastRain){
  const past=state.history.get(state.year);
  section("Comparación histórica · enero a marzo "+state.year,
   past?.records?.length?past.records.map(p=>p.name+": "+p.sum.toFixed(0)+" mm").join(" · ")+
    ". Fuente: reanálisis meteorológico; período de tres meses, NO comparable directamente con el acumulado a 7 días.":
   "Sin datos históricos aún para el año seleccionado. La consulta intenta obtener reanálisis de cuatro localidades.",
   "Antecedentes 1983, 1998, 2017 y 2023 · Open-Meteo Archive");
 }
 if(state.on.past2023)section("Escenario oficial de El Niño 2023",
  "CENEPRED evaluó potenciales afectaciones considerando lluvias de 1983, 1998, 2017 y 2023. Este es un estudio de escenarios de riesgo, no un polígono de eventos realmente inundados.",
  "La ficha original se encuentra en Metadatos y trazabilidad.");
 if(state.on.seasonal)section("Perspectiva de noviembre 2026 en adelante",
  "ENFEN (16/10/2026) prevé lluvias superiores a lo normal en la costa norte durante el resto de 2026 y el verano de 2027, y caudales sobre lo normal en el río La Leche principalmente desde noviembre. "+
  "También señala temperaturas del aire muy elevadas en la costa y niveles bajos del reservorio Tinajones para la época. "+
  "Es una perspectiva cualitativa regional: no son milímetros mensuales por distrito ni fechas precisas de desborde.",
  "Perspectiva cualitativa institucional · no alerta operativa por distrito");
 if(state.on.futureFlood||enabled("regional")||enabled("inundacionregion"))
  section("Inundaciones y anegamientos potenciales",
  "Si coinciden lluvias importantes con terrenos de alta susceptibilidad, pueden presentarse anegamientos en sectores urbanos y agrícolas. "+
  "El mapa muestra predisposición, no la huella futura de inundación ni su profundidad.");
 if(state.on.futureRiver)section("Posibles crecidas y desbordamientos",
  "La respuesta de un río depende de lluvia aguas arriba, suelo, reservorios y estado del cauce. "+
  "Sin mediciones hidrométricas y un modelo calibrado NO puede confirmarse el aumento de caudal ni señalar un punto futuro de desborde.");
 if(state.on.futureMass||enabled("movmasa"))section("Deslizamientos y quebradas",
  "Las lluvias intensas sobre pendientes y depósitos inestables pueden favorecer movimientos en masa y activación de quebradas. "+
  "Las capas históricas ayudan a priorizar sectores de revisión, sin representar la ocurrencia próxima.");
 if(state.on.futureDrought||enabled("drought"))section("Sequía y déficit hídrico",
  "La persistencia de pocas lluvias puede reducir la humedad disponible para cultivos. Para estimar sequía se necesitan anomalías respecto a normales climáticas, SPI y disponibilidad de riego.");
 if(state.on.futureHeat||enabled("heat"))section("Calor y estrés térmico",
  "Las temperaturas anómalas pueden elevar la demanda evaporativa y afectar a cultivos y poblaciones vulnerables. El mapa histórico de SENAMHI no es pronóstico del próximo episodio.");
 if(state.on.companies)section("Infraestructura agroindustrial documentada",
  state.comp.length+" ubicaciones referenciales visibles al activar la casilla. Son oficinas y terrenos mapeados en OpenStreetMap, "+
  "con información sobre su procedencia. No es inventario de todos los establecimientos formales ni se han calculado sus daños.",
  "Verificar vigencia y formalidad comercial en SUNAT, y la ubicación detallada con cada empresa.");
 const catalog=window.oafUx30Catalog?.()||[];
 for(const group of catalog)for(const info of group.entries)if(state.territorial[info.key])
  section(info.label,info.meaning);
 if(state.on.pastFlood||state.on.pastMass)section("Antecedentes de daños documentados",
  "Los puntos de INGEMMET corresponden a lugares geológicos inspeccionados por el evento de 2017; no deben extrapolarse como extensión de daños en 1983, 1998 o 2023.");
 const interactions=[state.on.futureFlood,state.on.futureMass,state.on.futureRiver,state.on.futureDrought,state.on.futureHeat].filter(Boolean).length;
 if(interactions)section("Lectura integrada para ciudades y agricultura",
  "Prioriza la revisión de drenes urbanos, pasos por quebradas, accesos rurales, parcelas y sistemas de riego "+
  "cuando coexistan señales de lluvia con antecedentes o susceptibilidad. "+
  "Para avisos de emergencia consulta a SENAMHI, ANA, CENEPRED e INDECI; este visor no emite alertas automáticas.");
}
function meta(){
 const area=$("oaf-ux30-metadatos")||document.querySelector('[data-page="verificaciones"]');
 if(!area||$("oaf-ux35-metadatos"))return;
 const div=E("section","oaf-ux35-metadatos");div.id="oaf-ux35-metadatos";
 div.innerHTML='<h2>Fuentes y trazabilidad de escenarios agroclimáticos</h2>'+
 '<p>Se comparan tres productos diferentes: reanálisis histórico, pronóstico meteorológico puntual y cartografía oficial de susceptibilidad. No se convierten automáticamente en estimaciones de caudal o zonas inundadas futuras.</p>'+
 '<ul><li><a href="https://sigrid.cenepred.gob.pe/sigridv3/documento/16310" target="_blank" rel="noopener noreferrer">CENEPRED 2023 · escenarios El Niño 1983/1998/2017/2023</a></li>'+
 '<li><a href="https://enfen.imarpe.gob.pe/comunicados/" target="_blank" rel="noopener noreferrer">ENFEN · comunicado oficial más reciente, 18-2026 (16/10/2026)</a></li>'+
 '<li><a href="https://www.senamhi.gob.pe/" target="_blank" rel="noopener noreferrer">SENAMHI · avisos y escenarios estacionales</a></li>'+
 '<li><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noopener noreferrer">Open-Meteo Archive · datos históricos modelados, no estaciones</a></li>'+
 '<li><a href="https://open-meteo.com/en/docs" target="_blank" rel="noopener noreferrer">Open-Meteo Forecast · precipitación pronosticada 7 días</a></li>'+
 '<li><a href="https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6010100" target="_blank" rel="noopener noreferrer">INGEMMET · inventario 2017</a></li>'+
 '<li><a href="'+COMPANIES+'" target="_blank" rel="noopener noreferrer">Agroindustrias y fundos referenciales · GeoJSON OpenStreetMap (no padrón SUNAT)</a></li>'+
 '<li><a href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_ESCENARIOS_AGROCLIMATICOS_UX35.md" target="_blank" rel="noopener noreferrer">Metodología UX35 · uso e incertidumbre del visor</a></li></ul>';
 area.append(div);
}
function init(){
 window.oafUx35Render=()=>render();
 window.oafUx35Diagnosis=()=>diagnosis();
 activate();
 requestSharedData();
 if(state.on.pastRain)loadHistory(state.year);
 const api=window.oafUx29ScenarioApi;
 if(api?.get()?.scene){render();if(state.on.rain7)api.loadRain()}
 else{
  // El contorno geojson se carga de manera asíncrona; no bloquear la página.
  let cycles=0;const probe=()=>{
   if(api?.get()?.scene){render();if(state.on.rain7)api.loadRain();return}
   if(++cycles<25)setTimeout(probe,300);
   else status();
  };setTimeout(probe,250);
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();