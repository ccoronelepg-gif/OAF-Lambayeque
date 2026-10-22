/* UX24 · Web y PWA. No se desplaza ni elimina contenido existente. */
(function(){"use strict";
const territoryHTML="\n<div class=\"oaf-ux24-intro\"><span class=\"oaf-ux24-tag\">Territorio · Prevención · Fuentes oficiales</span><h2>Territorio y riesgos climáticos de Lambayeque</h2><p>Explora los principales peligros asociados con lluvias intensas, crecidas, quebradas, erosión y déficit hídrico. Este apartado relaciona antecedentes documentados con la vigilancia agroclimática e identifica la fuente y fecha de los estudios consultados.</p></div>\n<div class=\"oaf-ux24-grid\">\n <article class=\"oaf-ux24-card\"><h3>Visor territorial con capas oficiales</h3>\n  <div class=\"oaf-ux24-mapframe\"><svg id=\"oaf-ux24-region-map\" viewBox=\"0 0 700 340\" role=\"img\" aria-label=\"Contorno referencial simplificado de Lambayeque, sin áreas de peligro representadas\"><text x=\"350\" y=\"170\" fill=\"#456d5c\" font-size=\"16\" text-anchor=\"middle\">Cargando contorno de Lambayeque…</text></svg>\n  <div class=\"oaf-ux24-map-note\">Contorno regional simplificado de referencia superpuesto a capas oficiales, si están disponibles. <strong>Las capas de susceptibilidad y los puntos geográficos proceden de servicios oficiales y solo se muestran cuando están disponibles.</strong> Consulta estas capas en los visores de las instituciones responsables.</div></div>\n  <a class=\"oaf-ux24-source\" href=\"https://sigrid.cenepred.gob.pe/sigridv3/\" target=\"_blank\" rel=\"noopener noreferrer\">Abrir mapas oficiales SIGRID ↗</a>\n  <a class=\"oaf-ux24-source\" href=\"https://www.gob.pe/15516-consultar-los-peligros-geologicos-en-el-territorio-peruano\" target=\"_blank\" rel=\"noopener noreferrer\">Abrir Perú en Alerta ↗</a>\n </article>\n <article class=\"oaf-ux24-card\"><h3>Selecciona un peligro</h3>\n  <p>Los conteos proceden del informe INGEMMET de <strong>diciembre de 2023</strong>; son puntos críticos históricos, no alertas actuales ni porcentajes del territorio.</p>\n  <div class=\"oaf-ux24-hazard-list\" id=\"oaf-ux24-hazard-list\" aria-label=\"Tipos de peligros en Lambayeque\"></div>\n  <div class=\"oaf-ux24-hazard-detail\" id=\"oaf-ux24-hazard-detail\" aria-live=\"polite\"></div>\n  <a class=\"oaf-ux24-source\" href=\"https://www.gob.pe/institucion/ingemmet/noticias/879706-lambayeque-ingemmet-identifica-172-zonas-criticas-ante-el-fenomeno-el-nino\" target=\"_blank\" rel=\"noopener noreferrer\">Estudio INGEMMET: 172 zonas críticas (2023) ↗</a>\n </article>\n</div>\n<div class=\"oaf-ux24-steps\">\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">01 · Hidrología</span><h3>Cuencas y drenaje</h3><p>Estudiar Chancay-Lambayeque, La Leche-Motupe y Zaña, crecidas, quebradas, escorrentía e infraestructura hidráulica.</p></article>\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">02 · Territorio</span><h3>Exposición agrícola</h3><p>Relacionar peligros cartografiados y, cuando se disponga de datos verificados, parcelas, vías productivas y sistemas de riego.</p></article>\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">03 · Anomalías</span><h3>Sequía y calor</h3><p>Contrastar antecedentes con indicadores de déficit hídrico, temperatura extrema, pisos altitudinales y series históricas.</p></article>\n</div>\n<p class=\"oaf-ux24-disclaimer\">Se consultan capas oficiales de susceptibilidad e inventarios georreferenciados mediante servicios cartográficos externos. Los polígonos de peligro para detalle parcelario y el análisis de exposición agrícola requieren fuentes y escalas adicionales; el contorno referencial no delimita áreas seguras.</p>";
const predictiveHTML="\n<div class=\"oaf-ux24-intro\"><span class=\"oaf-ux24-tag\">Investigación aplicada · SIG · IA</span><h2>Escenarios de riesgo agroclimático</h2><p>Este espacio organiza la investigación que relacionará anomalías de lluvia, temperatura y condiciones territoriales con los peligros que pueden afectar a la agricultura regional. Nuestros modelos predictivos se encuentran en entrenamiento y mejora continua.</p></div>\n<div class=\"oaf-ux24-steps\">\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">Componente 1</span><h3>Señales agroclimáticas</h3><p>Analizar lluvia mensual, anomalías, intensidad y duración de periodos húmedos, temperatura y condiciones de sequía mediante comparaciones meteorológicas.</p><a class=\"oaf-ux24-source\" href=\"#oaf-ux14-rf-semana\">Comparación semanal Random Forest ↗</a></article>\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">Componente 2</span><h3>Exposición territorial</h3><p>Integrar capas oficiales de ríos, quebradas, susceptibilidad y, cuando estén disponibles, cartografía agrícola e infraestructura de riego.</p><a class=\"oaf-ux24-source\" href=\"#oaf-territorio-riesgos\">Consultar territorio y peligros ↗</a></article>\n <article class=\"oaf-ux24-card\"><span class=\"oaf-ux24-tag\">Componente 3</span><h3>Evaluación de escenarios</h3><p>Desarrollar y contrastar métodos hidrológicos y geoespaciales antes de estimar áreas inundables o pérdidas. La lluvia pronosticada no determina por sí sola el riesgo de inundación.</p><a class=\"oaf-ux24-source\" href=\"#oaf-ux14-rf-mes\">Análisis mensual por paisaje ↗</a></article>\n</div>\n<div class=\"oaf-ux24-card\"><h3>Estado de integración</h3><p><strong>Disponible:</strong> modelos y análisis de lluvia y temperatura, comparaciones retrospectivas y paisajes agroclimáticos OAF. <strong>Desarrollo siguiente:</strong> integrar capas oficiales de peligros, datos de exposición y validación específica de escenarios territoriales.</p><p>Las fuentes oficiales pueden consultarse en <a href=\"https://sigrid.cenepred.gob.pe/sigridv3/\" target=\"_blank\" rel=\"noopener noreferrer\">SIGRID</a> e <a href=\"https://www.gob.pe/15516-consultar-los-peligros-geologicos-en-el-territorio-peruano\" target=\"_blank\" rel=\"noopener noreferrer\">INGEMMET</a>. Consulta la trazabilidad del proyecto en <a href=\"#verificaciones\">Metadatos y trazabilidad</a>.</p></div>";
const $=id=>document.getElementById(id);
const hazards=[
 ["fluvial","Inundación fluvial","37 zonas críticas (2023)","Desbordes y crecidas de ríos. Consulta las capas oficiales para identificar localizaciones y exposición de infraestructura y terrenos."],
 ["pluvial","Inundación pluvial","18 zonas críticas (2023)","Acumulación de agua durante lluvias y dificultades de drenaje. El análisis local requiere pendientes, cobertura y capacidad hidráulica."],
 ["quebradas","Quebradas y detritos","93 zonas críticas (2023)","Flujos de detritos asociados con quebradas y vertientes, especialmente durante precipitaciones intensas."],
 ["erosion","Erosión fluvial","11 zonas críticas (2023)","Erosión de riberas que puede afectar márgenes, obras hidráulicas y terrenos cercanos a los cauces."],
 ["sequia","Sequía y déficit hídrico","Análisis climático","Déficit de lluvia y posibles impactos hídricos. No corresponde al inventario geológico de 2023; requiere series temporales e indicadores especializados."]
];
const configs=[
 {page:"clima",title:"Análisis de la región",lead:"Explora el clima de Lambayeque, su territorio y los antecedentes de peligros asociados a eventos extremos.",names:["Clima regional","Territorio y riesgos climáticos"],base:"oaf-region-clima",risk:"oaf-territorio-riesgos"},
 {page:"autor",title:"Predicciones y anomalías",lead:"Diferencia los modelos agroclimáticos OAF del desarrollo de escenarios de riesgo territorial.",names:["Análisis agroclimático","Escenarios de riesgo agroclimático"],base:"oaf-analisis-agroclimatico",risk:"oaf-escenarios-riesgo-agroclimatico"}
];
function el(tag,cls){const x=document.createElement(tag);if(cls)x.className=cls;return x}
function build(cfg){
 const root=$(cfg.page);if(!root||$(cfg.risk))return;
 const head=el("div","oaf-ux24-subtabs");head.id="oaf-ux24-tabs-"+cfg.page;
 head.innerHTML='<p class="oaf-ux24-kicker">Explora los contenidos del observatorio</p><h2></h2><p class="oaf-ux24-description"></p><nav class="oaf-ux24-tablist"></nav>';
 head.querySelector("h2").textContent=cfg.title;head.querySelector(".oaf-ux24-description").textContent=cfg.lead;
 const nav=head.querySelector("nav");nav.setAttribute("aria-label","Subsecciones de "+cfg.title);
 cfg.names.forEach((name,i)=>{const a=el("a","oaf-ux24-tab");a.textContent=name;a.href="#"+(i?cfg.risk:cfg.base);nav.append(a)});
 const anchor=el("div","oaf-ux24-primary-anchor");anchor.id=cfg.base;anchor.setAttribute("aria-hidden","true");
 const section=el("section","oaf-ux24-risk-pane");section.id=cfg.risk;section.hidden=true;
 section.setAttribute("aria-label",cfg.names[1]);section.innerHTML=cfg.page==="clima"?territoryHTML:predictiveHTML;
 root.prepend(head,anchor);root.append(section);cfg.root=root;cfg.pane=section;cfg.tabs=head;
}
function activate(cfg,on){if(!cfg.root)return;
 cfg.root.classList.toggle("oaf-ux24-risk-active",on);cfg.pane.hidden=!on;
 cfg.tabs.querySelectorAll(".oaf-ux24-tab").forEach((a,i)=>{if(Boolean(i)===on)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});
}
function sync(){
 let key="";try{key=decodeURIComponent(location.hash.slice(1))}catch{}
 const item=$(key);
 for(const cfg of configs){if(!cfg.root)continue;
  if(key===cfg.risk||(item&&cfg.pane.contains(item))){activate(cfg,true);continue}
  if(key===cfg.base||key===cfg.page||(item&&cfg.root.contains(item)))activate(cfg,false);
 }
}
function hazardUI(){
 const list=$("oaf-ux24-hazard-list"),out=$("oaf-ux24-hazard-detail");if(!list||!out)return;
 function select(h){
  for(const b of list.querySelectorAll("button"))b.setAttribute("aria-pressed",String(b.dataset.kind===h[0]));
  out.replaceChildren();const strong=el("strong");strong.textContent=h[2];const p=el("p");p.textContent=h[3];out.append(strong,p);
 }
 for(const h of hazards){const b=el("button","oaf-ux24-hazard");b.type="button";b.textContent=h[1];b.dataset.kind=h[0];b.setAttribute("aria-pressed","false");b.addEventListener("click",()=>select(h));list.append(b)}
 select(hazards[0]);
}
function svgNode(tag,attrs){const n=document.createElementNS("http://www.w3.org/2000/svg",tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));return n}
async function regionalOutline(){
 const svg=$("oaf-ux24-region-map");if(!svg)return;
 try{
  const r=await fetch("datos/zonificacion_8n/limite_lambayeque_referencial.geojson",{cache:"no-store"});if(!r.ok)throw Error("límite");
  const data=await r.json();const feat=data.features.find(f=>f.geometry&&["Polygon","MultiPolygon"].includes(f.geometry.type));if(!feat)throw Error("geometría");
  const polys=feat.geometry.type==="Polygon"?[feat.geometry.coordinates]:feat.geometry.coordinates;
  const rings=polys.map(p=>p[0]).filter(a=>a.length>=3),points=rings.flat();
  const lons=points.map(x=>x[0]),lats=points.map(x=>x[1]);
  const minX=Math.min(...lons),maxX=Math.max(...lons),minY=Math.min(...lats),maxY=Math.max(...lats);
  if(![minX,maxX,minY,maxY].every(Number.isFinite)||maxX<=minX||maxY<=minY)throw Error("coordenadas");
  const cos=Math.cos((minY+maxY)/2*Math.PI/180),factor=Math.min(560/((maxX-minX)*cos),263/(maxY-minY));
  const xx=x=>350+(x-(minX+maxX)/2)*cos*factor,yy=y=>170-(y-(minY+maxY)/2)*factor;
  svg.replaceChildren(svgNode("rect",{x:0,y:0,width:700,height:340,fill:"#eef6f2"}));
  for(let x=70;x<700;x+=70)svg.append(svgNode("line",{x1:x,x2:x,y1:0,y2:340,stroke:"#dfeae3"}));
  for(let y=50;y<340;y+=50)svg.append(svgNode("line",{x1:0,x2:700,y1:y,y2:y,stroke:"#dfeae3"}));
  for(const ring of rings)svg.append(svgNode("path",{d:ring.map((p,i)=>(i?"L":"M")+xx(p[0]).toFixed(2)+" "+yy(p[1]).toFixed(2)).join(" ")+" Z",fill:"#b9dec8",stroke:"#2c785b","stroke-width":2.5,"data-oaf-ux24-boundary":"true"}));
  // Raster exportado por CENEPRED: el BBOX se calcula según esta misma proyección gráfica.
  const bounds={minLon:(minX+maxX)/2-350/(cos*factor),maxLon:(minX+maxX)/2+350/(cos*factor),minLat:(minY+maxY)/2-170/factor,maxLat:(minY+maxY)/2+170/factor};
  officialStart({svg,x:xx,y:yy,bounds});
  const north=svgNode("text",{x:645,y:32,fill:"#215b47","font-size":16,"font-weight":800,"text-anchor":"middle"});north.textContent="N ↑";svg.append(north);
  const label=svgNode("text",{x:350,y:315,fill:"#296852","font-size":15,"font-weight":750,"text-anchor":"middle"});label.textContent="LAMBAYEQUE · CONTORNO REFERENCIAL";svg.append(label);
 }catch(error){
  svg.replaceChildren();const t=svgNode("text",{x:350,y:170,fill:"#546d62","font-size":15,"text-anchor":"middle"});t.textContent="Contorno no disponible. Consulta SIGRID o INGEMMET.";svg.append(t);
 }
}

/* UX25 · capas oficiales en vivo: raster CENEPRED 2021 y puntos MINAM/INGEMMET.
   Los datos se solicitan a sus geoservicios; OAF no produce las geometrías de peligros. */
const officialState={scene:null,layers:"5090024",minam:true,geologico:true,points:{minam:[],geologico:[]},loaded:{minam:false,geologico:false},valid:false};
const GIS={
 raster:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer",
 minam:"https://geoservidorperu.minam.gob.pe/arcgis/rest/services/hiroambienplanificacion/caracterizacion_territorio_riesgo_desastres/MapServer",
 geologico:"https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer"
};
function officialUI(){
 const frame=document.querySelector("#oaf-territorio-riesgos .oaf-ux24-mapframe");
 if(!frame||$("oaf-ux25-controls"))return;
 const controls=el("div","oaf-ux25-controls");controls.id="oaf-ux25-controls";
 controls.innerHTML='<div class="oaf-ux25-heading"><strong>Capas geográficas oficiales</strong><span>Selecciona qué información visualizar sobre el contorno regional</span></div>'+
 '<label class="oaf-ux25-selectlabel" for="oaf-ux25-raster">Susceptibilidad a inundaciones (CENEPRED)</label>'+
 '<select id="oaf-ux25-raster"><option value="5090024">Lluvias intensas · escenario de 2021</option><option value="5090023">Eventos El Niño · escenario de 2021</option><option value="5010502">Susceptibilidad regional a inundaciones · INGEMMET</option><option value="5090022">Movimientos en masa por lluvia fuerte · CENEPRED</option><option value="none">Solo mapa base</option></select>'+
 '<div class="oaf-ux25-toggles"><label><input type="checkbox" id="oaf-ux25-minam" checked> Puntos críticos de inundación · MINAM</label>'+
 '<label><input type="checkbox" id="oaf-ux25-geologico" checked> Zonas críticas geológicas · INGEMMET/SIGRID</label></div>'+
 '<p id="oaf-ux25-map-status" class="oaf-ux25-map-status" role="status">Preparando geoservicios oficiales…</p>'+
 '<div class="oaf-ux25-legend"><span><i class="oaf-ux25-dot oaf-ux25-flood"></i>Puntos de inundación</span><span><i class="oaf-ux25-dot oaf-ux25-geo"></i>Zonas geológicas</span></div><p class="oaf-ux25-legend-foot">Categorías del raster CENEPRED: <b>muy alto, alto, medio y bajo</b>. Los colores oficiales se interpretan según la <a target="_blank" rel="noopener noreferrer" href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend">leyenda del geoservicio</a>.</p>';
 frame.before(controls);
 const detail=el("div","oaf-ux25-detail");detail.id="oaf-ux25-detail";
 detail.textContent="Selecciona un punto del mapa para consultar sus atributos, fecha y fuente original.";
 frame.after(detail);
 const src=el("p","oaf-ux25-source-detail");
 src.innerHTML='Susceptibilidad: <a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024" target="_blank" rel="noopener noreferrer">CENEPRED · lluvias intensas (2021)</a> y <a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090023" target="_blank" rel="noopener noreferrer">eventos El Niño (2021)</a>. '+ 
 'Puntos inventariados: <a href="https://geoservidorperu.minam.gob.pe/arcgis/rest/services/hiroambienplanificacion/caracterizacion_territorio_riesgo_desastres/MapServer/3" target="_blank" rel="noopener noreferrer">MINAM</a> y <a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5020500" target="_blank" rel="noopener noreferrer">INGEMMET/SIGRID (inventario actualizado a 2022)</a>. No equivale a una alerta vigente.';
 detail.after(src);
 const m=el("a","oaf-ux24-source");m.href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_CAPAS_RIESGOS_UX25.md";m.target="_blank";m.rel="noopener noreferrer";m.textContent="Metodología y procedencia de capas UX25 ↗";src.after(m);
 $("oaf-ux25-raster").addEventListener("change",e=>{officialState.layers=e.target.value;drawOfficial()});
 $("oaf-ux25-minam").addEventListener("change",e=>{officialState.minam=e.target.checked;drawOfficial()});
 $("oaf-ux25-geologico").addEventListener("change",e=>{officialState.geologico=e.target.checked;drawOfficial()});
}
function officialStatus(){
 const element=$("oaf-ux25-map-status");if(!element)return;
 const a=officialState.loaded;
 const status=Object.keys(a).map(k=>a[k]===true?(k==="minam"?"MINAM":"INGEMMET/SIGRID")+": "+officialState.points[k].length+" puntos cargados":
 a[k]==="error"?(k==="minam"?"MINAM":"INGEMMET/SIGRID")+": servicio no disponible":"Cargando puntos "+(k==="minam"?"MINAM":"INGEMMET") );
 const ras=officialState.layers==="none"?"Sin raster":officialState.rasterStatus||"Solicitando capa raster oficial";
 element.textContent=ras+" · "+status.join(" · ")+".";
}
function mapRasterUrl(layer,scene,server){
 const {bounds}=scene;
 const query=new URLSearchParams({
  bbox:[bounds.minLon,bounds.minLat,bounds.maxLon,bounds.maxLat].join(","),
  bboxSR:"4326",imageSR:"4326",size:"900,438",
  format:"png32",transparent:"true",dpi:"110",
  layers:"show:"+layer,f:"image"
 });
 return server+"/export?"+query.toString();
}
function officialTooltip(record,which){
 const p=record.properties||{};
 const heading=which==="minam"?"Punto crítico por inundación · MINAM":"Zona crítica geológica · INGEMMET/SIGRID";
 const title=[p.nom_lugar,p.paraje,p.nom_dist,p.nom_dpto,p.nom_dep].find(x=>typeof x==="string"&&x.trim())||"Ubicación sin nombre publicado";
 const risk=[p.tip_peligr,p.tipo_pel,p.n_peligro].find(x=>typeof x==="string"&&x.trim())||"Peligro: consultar fuente";
 const date=[p.fecha_actu,p.fecha_doc].find(x=>typeof x==="string"&&x.trim())||"Fecha: consultar ficha técnica";
 const output=$("oaf-ux25-detail");if(!output)return;
 output.replaceChildren();
 const h=el("strong");h.textContent=heading+" · "+title;
 const t=el("p");t.textContent="Tipo: "+risk+". "+date+".";
 output.append(h,t);
 const note=[p.descrip,p.e_expuesto,p.elemento].find(x=>typeof x==="string"&&x.trim());
 if(note){const e=el("p");e.textContent=note.slice(0,350);output.append(e)}
 const href=which==="minam"?GIS.minam+"/3":GIS.geologico+"/5020500";
 const a=el("a");a.href=href;a.target="_blank";a.rel="noopener noreferrer";a.textContent="Consultar geoservicio original ↗";output.append(a);
}
function drawOfficial(){
 const sc=officialState.scene;if(!sc)return;
 const svg=sc.svg;
 svg.querySelectorAll(".oaf-ux25-maplayer").forEach(n=>n.remove());
 if(officialState.layers!=="none"){
  officialState.rasterStatus="Consultando raster CENEPRED";
  const image=svgNode("image",{x:0,y:0,width:700,height:340,href:mapRasterUrl(officialState.layers,sc,GIS.raster),opacity:".75","preserveAspectRatio":"none"});
  image.classList.add("oaf-ux25-maplayer");
  image.addEventListener("load",()=>{if(!image.isConnected)return;officialState.rasterStatus="Capa raster solicitada a CENEPRED";officialStatus()});
  image.addEventListener("error",()=>{if(!image.isConnected)return;officialState.rasterStatus="La capa raster no respondió; abre SIGRID";officialStatus()});
  const boundary=svg.querySelector('[data-oaf-ux24-boundary="true"]');
  svg.insertBefore(image,boundary||null);
 }else officialState.rasterStatus="Vista sin raster";
 for(const [key,enabled,color] of [["minam",officialState.minam,"#cf6a25"],["geologico",officialState.geologico,"#74449d"]]){
  if(!enabled)continue;
  for(const record of officialState.points[key]){
   const pt=record.geometry?.coordinates;
   if(!Array.isArray(pt)||pt.length<2||!pt.every(Number.isFinite))continue;
   const cx=sc.x(pt[0]),cy=sc.y(pt[1]);
   if(cx<0||cx>700||cy<0||cy>340)continue;
   const dot=svgNode("circle",{cx:cx.toFixed(2),cy:cy.toFixed(2),r:5,fill:color,stroke:"#fff","stroke-width":1.25,tabindex:"0",role:"button","aria-label":"Consultar ubicación oficial de "+(key==="minam"?"inundación":"peligro geológico")});
   dot.classList.add("oaf-ux25-maplayer","oaf-ux25-point");
   const open=()=>officialTooltip(record,key);
   dot.addEventListener("click",open);
   dot.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();open()}});
   svg.append(dot);
  }
 }
 officialStatus();
}
function geometryPoint(feature){
 if(feature.geometry?.type==="Point")return feature;
 if(Number.isFinite(feature.geometry?.x)&&Number.isFinite(feature.geometry?.y))return {type:"Feature",geometry:{type:"Point",coordinates:[feature.geometry.x,feature.geometry.y]},properties:feature.attributes||{}};
 return null;
}
async function officialPoints(which,layer,where){
 const sc=officialState.scene;if(!sc)return;
 const extent=sc.bounds;
 const params=new URLSearchParams({
  where,geometry:[extent.minLon,extent.minLat,extent.maxLon,extent.maxLat].join(","),
  geometryType:"esriGeometryEnvelope",inSR:"4326",spatialRel:"esriSpatialRelIntersects",
  outFields:which==="minam"?"nom_dpto,nom_dist,paraje,tip_peligr,fecha_actu,fecha_doc,descrip":"nom_dep,nom_lugar,nom_dist,tipo_pel,fecha_doc,e_expuesto",
  returnGeometry:"true",outSR:"4326",resultRecordCount:"1500",f:"geojson"
 });
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),18000);
 try{
  const url=layer+"/query?"+params.toString();
  const res=await fetch(url,{cache:"no-store",signal:controller.signal});
  if(!res.ok)throw Error("HTTP "+res.status);
  const geo=await res.json();
  if(geo.error||!Array.isArray(geo.features))throw Error("respuesta no GeoJSON");
  officialState.points[which]=geo.features.map(geometryPoint).filter(Boolean).filter(f=>{
   const [x,y]=f.geometry.coordinates;
   const d=String(which==="minam"?f.properties?.nom_dpto||"":f.properties?.nom_dep||"").toLocaleUpperCase("es-PE");
   return x>=extent.minLon&&x<=extent.maxLon&&y>=extent.minLat&&y<=extent.maxLat&&(!d||d.includes("LAMBAYEQUE"));
  }).slice(0,1500);
  officialState.loaded[which]=true;
 }catch(err){officialState.loaded[which]="error"}finally{clearTimeout(timer);drawOfficial()}
}
function officialStart(scene){
 officialState.scene=scene;officialStatus();drawOfficial();
 // Las capas de puntos se obtienen directamente de proveedores oficiales; el visor solo las reproyecta para la pantalla.
 officialPoints("minam",GIS.minam+"/3","1=1");
 officialPoints("geologico",GIS.geologico+"/5020500","1=1");
}

function init(){
 configs.forEach(build);
 const nav=document.querySelector('#oaf-primary-nav a[data-tab="clima"]');if(nav)nav.textContent="Análisis de la región";
 hazardUI();officialUI();sync();regionalOutline();
 window.addEventListener("hashchange",sync);
 // Abrir también los enlaces directos cuando la página se carga por primera vez.
 if(configs.some(c=>location.hash==="#"+c.risk||location.hash==="#"+c.base))window.dispatchEvent(new Event("hashchange"));
 document.querySelectorAll(".oaf-ux24-tab").forEach(a=>a.addEventListener("click",()=>{if(a.getAttribute("href")===location.hash){sync();a.closest(".oaf-ux24-subtabs").scrollIntoView({block:"start"})}}));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();