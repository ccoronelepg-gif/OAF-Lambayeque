(function chartsOAF(){
"use strict";
const $=id=>document.getElementById(id), svgNS="http://www.w3.org/2000/svg";
function svg(name,attr,text){const e=document.createElementNS(svgNS,name);for(const [k,v] of Object.entries(attr||{}))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=String(text);return e}
const city={
Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]
};
const req=(path)=>fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status+" · "+path);return r});
const csv=t=>{const rows=t.trim().replace(/^\uFEFF/,"").split(/\r?\n/).map(r=>r.split(",")),headers=rows.shift();return rows.filter(r=>r.length===headers.length).map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]])))};
const fmt=(v,d=1)=>Number(v).toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d});
function error(id,message){const target=$(id);if(target){target.replaceChildren();const p=document.createElement("p");p.className="oaf-agro-progress";p.textContent=message;target.append(p)}}
function plot(id,values,labels,{mode="bar",unit="mm",source="",baseline=null}={}){
 const el=$(id);if(!el||!values.length||values.every(v=>!Number.isFinite(v))){error(id,"Serie no disponible: faltan datos verificables.");return}
 const nums=values.filter(Number.isFinite),W=760,H=300,top=29,left=57,right=15,bottom=55;
 const ymin=Math.min(0,...nums),ymax=Math.max(...nums),span=Math.max(1,ymax-ymin),y0=ymin-span*.10,y1=ymax+span*.14,ph=H-top-bottom,pw=W-left-right;
 const x=i=>left+(i+.5)*pw/values.length,y=v=>top+(y1-v)/(y1-y0)*ph;
 const graph=svg("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":`${source}. Serie: ${unit}`});
 for(let i=0;i<=4;i++){let v=y0+(y1-y0)*i/4,Y=y(v);graph.append(svg("line",{x1:left,y1:Y,x2:W-right,y2:Y,class:"oaf-chart-grid"}));graph.append(svg("text",{x:4,y:Y+4,class:"oaf-chart-axis"},fmt(v,1)))}
 graph.append(svg("line",{x1:left,y1:y(0),x2:W-right,y2:y(0),stroke:"#a9c8b5","stroke-width":1.3}));
 if(mode==="line"){
  let coords=values.map((v,i)=>Number.isFinite(v)?`${x(i)},${y(v)}`:null).filter(Boolean);
  graph.append(svg("polyline",{points:coords.join(" "),class:"oaf-chart-line"}));
  values.forEach((v,i)=>{if(!Number.isFinite(v))return;const circle=svg("circle",{cx:x(i),cy:y(v),r:values.length>15?3:5,class:"oaf-chart-dot"});circle.append(svg("title",{},`${labels[i]} · ${fmt(v,1)} ${unit}`));graph.append(circle)})
 }else{
  const bw=Math.min(39,pw/values.length*.71);
  values.forEach((v,i)=>{if(!Number.isFinite(v))return;const rect=svg("rect",{x:x(i)-bw/2,y:Math.min(y(0),y(v)),width:bw,height:Math.max(1,Math.abs(y(0)-y(v))),rx:2,class:"oaf-chart-bar"});rect.append(svg("title",{},`${labels[i]} · ${fmt(v,1)} ${unit}`));graph.append(rect)})
 }
 const step=Math.max(1,Math.ceil(labels.length/7));
 labels.forEach((lbl,i)=>{if(i%step!==0&&i!==labels.length-1)return;graph.append(svg("text",{x:x(i),y:H-22,"text-anchor":"middle",class:"oaf-chart-axis"},String(lbl).slice(0,10)))});
 const caption=document.createElement("figcaption");caption.textContent=`${source} · ${unit} · ${labels[0]}–${labels.at(-1)}. Pasa el cursor sobre barras o puntos para consultar valores.`;
 el.replaceChildren(graph,caption);
}
let historic;
async function loadHistoric(){if(historic)return historic;historic=req("datos/lambayeque_mensual_era5_8d.csv").then(r=>r.text()).then(csv);return historic}
async function annual(id,placeId,varId){
 const place=$(placeId)?.value,kind=$(varId)?.value; if(!place||!kind)return;
 try{
 const rows=(await loadHistoric()).filter(r=>r.localidad===place&&/^(199[6-9]|20[0-2]\d)-\d\d$/.test(r.mes));
 const grouped=new Map();
 for(const r of rows){const yr=r.mes.slice(0,4);if(!grouped.has(yr))grouped.set(yr,[]);grouped.get(yr).push(Number(r[kind]))}
 const years=[...grouped.keys()].sort().filter(y=>Number(y)<=2025), vals=years.map(y=>{const a=grouped.get(y);return a.length===12&&a.every(Number.isFinite)?(kind==="precipitacion_mm"?a.reduce((x,z)=>x+z,0):a.reduce((x,z)=>x+z,0)/12):NaN});
 plot(id,vals,years,{mode:"line",unit:kind==="precipitacion_mm"?"mm/año":"°C",source:`Análisis OAF de ERA5 · ${place} · datos históricos`});
 }catch(e){error(id,"No se pudo leer la serie histórica: "+e.message)}
}
const days=new Map();
async function daily(place){if(!days.has(place)){
const [lat,lon]=city[place]||city.Chiclayo;
const query=new URLSearchParams({latitude:String(lat),longitude:String(lon),daily:"precipitation_sum,temperature_2m_max",timezone:"America/Lima",forecast_days:"7"});
days.set(place,req("https://api.open-meteo.com/v1/forecast?"+query).then(r=>r.json()).then(j=>{if(!j.daily||!Array.isArray(j.daily.time)||j.daily.time.length!==7)throw Error("Horizonte de siete días incompleto");return j}));
}return days.get(place)}
async function weekly(id,placeId,statusId){const p=$(placeId)?.value||"Chiclayo";try{
const j=await daily(p); const v=j.daily.precipitation_sum;if(!Array.isArray(v)||v.length!==7)throw Error("Sin acumulados diarios completos");
plot(id,v,j.daily.time.map(x=>x.slice(5)),{unit:"mm/día",source:`Modelo meteorológico externo · ${p}`});
if($(statusId))$(statusId).textContent=`Fuente: Open-Meteo · localidad: ${p} · datos diarios ${j.daily.time[0]} a ${j.daily.time.at(-1)} · timezone America/Lima.`;
}catch(e){error(id,"Pronóstico temporalmente no disponible: "+e.message);if($(statusId))$(statusId).textContent="No se completan datos ausentes con valores estimados."}}
function viewBoxProjection(points,width=720,height=420){const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),lat0=(minY+maxY)/2,cf=Math.cos(lat0*Math.PI/180),s=Math.min((width-95)/Math.max(.05,(maxX-minX)*cf),(height-68)/Math.max(.05,maxY-minY));return {x:lon=>width/2+(lon-(minX+maxX)/2)*cf*s,y:lat=>height/2-(lat-(minY+maxY)/2)*s}}
async function regionMap(){
 const field=$("oaf-regional-map-filter"),target=$("oaf-regional-hist-map");if(!field||!target)return;
 try{
 const [csvResp,geoResp]=await Promise.all([req("datos/muestreo_8o/nodos_dem_8o.csv"),req("datos/zonificacion_8n/limite_lambayeque_referencial.geojson")]);
 const pts=csv(await csvResp.text()).map(r=>({lat:Number(r.latitud),lon:Number(r.longitud),h:Number(r.altitud_dem_m),id:r.id})).filter(p=>[p.lat,p.lon,p.h].every(Number.isFinite));
 const geo=await geoResp.json();const ring=geo?.features?.find(f=>f.geometry?.type==="Polygon")?.geometry.coordinates?.[0]||[];
 if(pts.length!==420||ring.length<3)throw Error("Inventario cartográfico no coincide con 420 puntos");
 const project=viewBoxProjection([...pts.map(p=>[p.lon,p.lat]),...ring],720,420);
 const draw=()=>{
  const root=svg("svg",{viewBox:"0 0 720 420",role:"img","aria-label":"Mapa exploratorio de altitudes del muestreo DEM Lambayeque"});
  root.append(svg("rect",{x:0,y:0,width:720,height:420,fill:"#f4faf6",rx:13}));
  root.append(svg("polygon",{points:ring.map(p=>project.x(p[0]).toFixed(2)+","+project.y(p[1]).toFixed(2)).join(" "),class:"oaf-map-outline"}));
  let shown=0;const range=field.value==="all"?[-1000,10000]:field.value.split("-").map(Number);
  for(const p of pts){const visible=p.h>=range[0]&&p.h<range[1];if(visible)shown++;const c=svg("circle",{cx:project.x(p.lon),cy:project.y(p.lat),r:visible?3.4:2,fill:visible?"#44846c":"#bccac0",opacity:visible?".9":".10"});if(visible)c.append(svg("title",{},`${p.id}: ${p.h.toFixed(0)} m (DEM)`));root.append(c)}
  for(const [name,[lat,lon]] of Object.entries(city)){root.append(svg("circle",{cx:project.x(lon),cy:project.y(lat),r:5,class:"oaf-map-symbol"}));root.append(svg("text",{x:project.x(lon)+7,y:project.y(lat)-7,fill:"#1d4b41","font-size":12},name))}
  const footer=document.createElement("p");footer.className="oaf-agro-caption";footer.textContent=`${shown} de 420 puntos DEM representados · franjas experimentales · límite regional referencial.`;
  target.replaceChildren(root,footer);
 };
 field.addEventListener("change",draw);draw();
 }catch(e){target.textContent="Mapa sin datos verificables: "+e.message}
}
async function stationMap(){
 const field=$("oaf-stations-floor"),target=$("oaf-stations-map"),list=$("oaf-stations-list");if(!field||!target||!list)return;
 try{
 const [f9,f10]=await Promise.all([req("datos/validacion_estaciones_9f/identificacion_territorial_9f.json").then(r=>r.json()),req("datos/senamhi_estaciones_10m/manifest_fuentes_10m.json").then(r=>r.json())]);
 const stations=[];
 for(const s of f9.estaciones||[]){const c=s.coordenadas_dereferencia;if(c?.length===2&&Number.isFinite(s.altitud_de_referencia_m))stations.push({name:s.nombre,lat:c[0],lon:c[1],h:s.altitud_de_referencia_m,source:"Auditoría territorial 9F",note:s.estado_cartografico||""})}
 const dms=s=>{const parts=String(s).match(/\d+(?:\.\d+)?/g);if(!parts)return NaN;return -(Number(parts[0])+Number(parts[1]||0)/60+Number(parts[2]||0)/3600)};
 const seen=new Set(stations.map(s=>s.name.toUpperCase()));
 for(const s of f10.fuentes_nuevas||[]){const name=String(s.estacion||"").toUpperCase();if(!name||seen.has(name))continue;const lat=dms(s.latitud_dms),lon=dms(s.longitud_dms),h=Number(s.altitud_m);if(![lat,lon,h].every(Number.isFinite))continue;stations.push({name:s.estacion,lat,lon,h,source:"SENAMHI/DRD 10M",note:"Archivo documental recibido; control instrumental pendiente"});seen.add(name)}
 if(!stations.length)throw Error("Estaciones sin posición verificable");
 const pr=viewBoxProjection([...stations.map(p=>[p.lon,p.lat]),...Object.values(city).map(p=>[p[1],p[0]])],720,420);
 const draw=()=>{
  const [lo,hi]=field.value==="all"?[-1000,10000]:field.value.split("-").map(Number);
  const ss=stations.filter(p=>p.h>=lo&&p.h<hi);
  const map=svg("svg",{viewBox:"0 0 720 420",role:"img","aria-label":"Estaciones meteorológicas por pisos altitudinales"});
  map.append(svg("rect",{x:0,y:0,width:720,height:420,fill:"#f0f8f2",rx:14}));
  for(const s of ss){const x=pr.x(s.lon),y=pr.y(s.lat);const c=svg("circle",{cx:x,cy:y,r:8,class:"oaf-map-symbol",tabindex:0,role:"button","aria-label":`${s.name} ${s.h} metros`});c.append(svg("title",{},`${s.name} · ${s.h} m · ${s.source}`));const select=()=>{list.textContent=`${s.name}: ${s.h} m de altitud de referencia. ${s.source}. ${s.note}. Consulta metadatos para la resolución geográfica.`};c.addEventListener("click",select);c.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select()}});map.append(c);map.append(svg("text",{x:x+12,y:y-9,fill:"#1b5346","font-size":12},s.name))}
  for(const [name,[lat,lon]] of Object.entries(city))map.append(svg("circle",{cx:pr.x(lon),cy:pr.y(lat),r:2.5,fill:"#899c93"}));
  const p=document.createElement("p");p.className="oaf-agro-caption";p.textContent=`${ss.length} estaciones con posición documental en el filtro seleccionado. Fuente: inventarios 9F y 10M.`;
  target.replaceChildren(map,p);
  list.textContent=ss.map(s=>`${s.name} · ${s.h} m · ${s.source}`).join(" | ")||"No hay estaciones documentadas en esta franja.";
 };
 field.addEventListener("change",draw);draw();
 }catch(e){target.textContent="Ubicación de estaciones no disponible: "+e.message;list.textContent="La fuente instrumental se conserva en Metadatos."}
}
async function ninoSignal(){
 const box=$("oaf-nino-signal");if(!box)return;
 try{const rows=csv(await req("datos/noaa_ersstv5_nino12_mensual.csv").then(r=>r.text())).filter(r=>Number.isFinite(Number(r.anomalia_ersstv5_c)));const last=rows.at(-1);if(!last)throw Error("Sin anomalía válida");box.replaceChildren();
 const small=document.createElement("small");small.textContent="NOAA ERSSTv5 · Niño 1+2 · último mes archivado";const value=document.createElement("strong");value.textContent=`${last.mes} · ${fmt(Number(last.anomalia_ersstv5_c),2)} °C de anomalía`;const p=document.createElement("p");p.className="oaf-agro-caption";p.textContent="Indicador oceánico histórico; no asigna por sí solo categoría de alerta ni pronostica lluvia en una parcela.";box.append(small,value,p);
 }catch(e){box.textContent="Serie oceánica no disponible: "+e.message}
}
function setup(){
 const configs=[["oaf-historical-chart","oaf-historical-place","oaf-historical-var"],["oaf-regional-hist-chart","oaf-regional-place","oaf-regional-var"]];
 for(const [id,p,v] of configs){const cb=()=>annual(id,p,v);$(p)?.addEventListener("change",cb);$(v)?.addEventListener("change",cb);cb()}
 for(const [id,p,status] of [["oaf-h7-chart","oaf-h7-place","oaf-h7-status"],["oaf-autor-7chart","oaf-autor-7place","oaf-autor-7status"]]){const cb=()=>weekly(id,p,status);$(p)?.addEventListener("change",cb);cb()}
 document.addEventListener("oaf:localidad",e=>{const next=e.detail?.localidad;if(!city[next])return;for(const id of ["oaf-h7-place","oaf-autor-7place","oaf-historical-place","oaf-regional-place"]){const s=$(id);if(s&&s.value!==next){s.value=next;s.dispatchEvent(new Event("change"))}}});
 regionMap();stationMap();ninoSignal();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",setup,{once:true});else setup();
})();
