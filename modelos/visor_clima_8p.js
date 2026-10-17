/* OAF 8P: candidatos espaciales, no polígonos agrícolas verificados. */
(()=>{
"use strict";
const root=document.getElementById("oaf-neighbors-8p");if(!root)return;
const $=id=>document.getElementById(id);
const state=$("oaf-8p-state"),tbody=$("oaf-8p-table"),map=$("oaf-8p-map");
let dem=[],newPoints=[],complete=[],pairs=[],summary=null,boundary=null;
const COLORS={llanura_costa:"#2d82b7",valle_bajo:"#2da989",
 piedemonte:"#d0a045",montana_baja:"#d47c47",montana_media:"#9c7cb7",
 montana_alta:"#5f438d",cota_negativa_revisar:"#7e8790"};
const svg=(tag,attrs={},title)=>{
 const el=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [key,val] of Object.entries(attrs))el.setAttribute(key,String(val));
 if(title!==undefined){const tip=document.createElementNS("http://www.w3.org/2000/svg","title");tip.textContent=title;el.append(tip);}
 return el;
};
const num=v=>typeof v==="number"&&Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:2}):"—";
function csv(text){
 const lines=text.trim().split(/\r?\n/),headers=lines.shift().split(",");
 return lines.filter(Boolean).map(line=>{
  const values=line.split(",");
  if(values.length!==headers.length)throw Error("Encabezados de CSV incompatibles");
  return Object.fromEntries(headers.map((key,i)=>[key,values[i]]));
 });
}
function format(rows){
 for(const r of rows){
  for(const k of ["latitud","longitud","altitud_dem_m"]){
    if(k in r){r[k]=Number(r[k]);if(!Number.isFinite(r[k]))throw Error("Coordenada DEM no numérica")}
  }
 }
 return rows;
}
function draw(){
 if(!summary||!boundary)return;
 tbody.replaceChildren();map.replaceChildren();
 $("oaf-8p-samples").textContent=String(newPoints.length+19);
 $("oaf-8p-new").textContent=String(summary.testigos_nuevos_con_30_anios);
 $("oaf-8p-similar").textContent=String(summary.pares_que_superan_filtro_exploratorio);
 const ring=boundary.features[0].geometry.coordinates[0];
 const xmin=Math.min(...ring.map(p=>p[0])),xmax=Math.max(...ring.map(p=>p[0]));
 const ymin=Math.min(...ring.map(p=>p[1])),ymax=Math.max(...ring.map(p=>p[1]));
 const W=770,H=510,pad=24;
 const x=v=>pad+(v-xmin)/(xmax-xmin)*(W-2*pad);
 const y=v=>H-pad-(v-ymin)/(ymax-ymin)*(H-2*pad);
 const fig=svg("svg",{viewBox:"0 0 770 510",role:"img",
   "aria-label":"Nodos DEM, testigos climáticos nuevos y pares localmente similares preliminares"});
 fig.style.cssText="width:100%;height:auto;max-height:550px";
 fig.append(svg("path",{d:ring.map((p,i)=>(i?"L":"M")+x(p[0]).toFixed(2)+","+y(p[1]).toFixed(2)).join(" ")+" Z",
  fill:"#edf3ef",stroke:"#526e7f","stroke-width":1.8}));
 for(const r of dem){
  const circle=svg("circle",{cx:x(r.longitud),cy:y(r.latitud),r:1.5,
    fill:COLORS[r.estrato_fisico_preliminar]||"#777"});
  fig.append(circle);
 }
 const lookup=new Map([...newPoints,...complete].map(p=>[p.id,p]));
 // Similar pairs shown only as screening lines when both source points exist.
 for(const pair of pairs.slice(0,300)){
  const a=lookup.get(pair.nodo_a),b=lookup.get(pair.nodo_b);
  if(!a||!b)continue;
  fig.append(svg("line",{x1:x(a.longitud),y1:y(a.latitud),x2:x(b.longitud),y2:y(b.latitud),
    stroke:"#227c9c","stroke-width":2.2,"stroke-dasharray":"5,3",opacity:.65},
    "Pareja climática exploratoria, no zonificación agrícola"));
 }
 for(const p of newPoints){
  const point=svg("circle",{cx:x(p.longitud),cy:y(p.latitud),r:4,
    fill:"#fff",stroke:"#203c51","stroke-width":1.1},
    p.id+" · nuevo nodo 8P, DEM "+num(p.altitud_dem_m)+" m");
  fig.append(point);
 }
 const completed=new Set(complete.map(p=>p.id));
 for(const p of complete){
  const ring=svg("circle",{cx:x(p.longitud),cy:y(p.latitud),r:6.2,
    fill:"none",stroke:"#117e90","stroke-width":2.3},
    p.id+" · climatología 1996–2025 disponible (reanálisis, no estación)");
  fig.append(ring);
 }
 map.append(fig);
 const key=document.createElement("p");key.className="small";
 key.textContent="Puntos pequeños: malla DEM de 420 nodos. Centros blancos: 62 nuevos testigos seleccionados. Anillos turquesa: climatología completa (incluye 19 de 8O). Líneas discontinuas: pares locales que superan filtros exploratorios; nunca perímetros o alertas.";
 map.append(key);
 for(const r of pairs.slice(0,12)){
  const tr=document.createElement("tr");
  for(const val of [r.nodo_a+" – "+r.nodo_b,
   num(Number(r.distancia_geografica_km)),num(Number(r.desnivel_dem_m)),
   num(Number(r.distancia_climatica_estandarizada)),
   num(Math.abs(Number(r.diferencia_tmedia_anual_c))),
   num(Math.abs(Number(r.diferencia_precipitacion_anual_mm))),"No"]){
    const td=document.createElement("td");td.textContent=String(val);tr.append(td);
  }
  tbody.append(tr);
 }
 if(!pairs.length){
  const tr=document.createElement("tr");const td=document.createElement("td");
  td.colSpan=7;td.textContent="Aún no hay pares que cumplan el filtro descriptivo; se esperan más fuentes climáticas 8P.";
  tr.append(td);tbody.append(tr);
 }
}
async function load(){
 state.textContent="Comprobando testigos, normal climática, límites y grafos…";
 try{
  const paths=[
   "datos/muestreo_8o/nodos_dem_8o.csv",
   "datos/zonas_contiguas_8p/nuevos_testigos_8p.csv",
   "datos/clima_contiguo_8p/estado_clima_8p.json",
   "datos/clima_contiguo_8p/testigos_perfil_completo_8p.csv",
   "datos/clima_contiguo_8p/pares_similares_exploratorios_8p.csv",
   "datos/zonificacion_8n/limite_lambayeque_referencial.geojson"];
  const results=await Promise.all(paths.map(path=>fetch(path,{cache:"no-store"})));
  if(results.some(p=>!p.ok))throw Error("No hay fuentes regionales completas en el repositorio");
  const [d,n,s,c,p,g]=await Promise.all(results.map((item,i)=>[2,5].includes(i)?item.json():item.text()));
  if(s.fase!=="8P"||s.zonas_homogeneas_geograficas_certificadas!==0||
    s.n_poligonos_agricolas_validados!==0||s.validacion_instrumental!==false||
    s.precision_predictiva_zonal_demostrada!==false||
    g.features?.[0]?.properties?.codigo_ubigeo!=="14")throw Error("No se acredita integridad científica");
  const base=format(csv(d)),up=format(csv(n)),full=format(csv(c)),similar=csv(p);
  if(base.length!==420||up.length!==62||full.length!==s.testigos_total_con_30_anios||
      similar.length!==s.pares_que_superan_filtro_exploratorio||
      up.some(v=>v.apto_para_zona_operativa!=="false")||
      full.some(v=>v.apto_para_zona_operativa!=="false"))
    throw Error("Recuentos, zona operativa o estructura incompatibles");
  dem=base;newPoints=up;complete=full;pairs=similar;boundary=g;summary=s;
  state.textContent="Muestreo 8P: 62 testigos nuevos; "+s.testigos_nuevos_con_30_anios+
   " nuevos con clima 1996–2025 completo; "+s.lotes_climaticos_verificados+
   "/24 fuentes históricas verificadas. Criterios de proximidad y clima son exploratorios, no zonas agroclimáticas certificadas.";
  draw();
 }catch(err){
  tbody.replaceChildren();map.replaceChildren();
  state.textContent="No se presentan zonas sin datos verificables: "+err.message;
 }
}
$("oaf-8p-refresh")?.addEventListener("click",load);
let started=false;root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;load()}});
})();
