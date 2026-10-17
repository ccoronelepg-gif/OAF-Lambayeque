/* Fase 9K: polígonos cartográficos de influencia muestral, no zonas homogéneas aprobadas. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const SVG_NS="http://www.w3.org/2000/svg";
const svg=(tag,attrs={},txt)=>{const e=document.createElementNS(SVG_NS,tag);
 for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));
 if(txt!==undefined)e.textContent=txt;return e;};
const STYLES=[
 ["llanura_costa","Planicie costera (0–99 m)","#2483aa"],
 ["valle_bajo","Valle bajo (100–299 m)","#44a18b"],
 ["piedemonte","Piedemonte (300–799 m)","#c6a34a"],
 ["montana_baja","Ladera baja (800–1599 m)","#ce8755"],
 ["montana_media","Ladera media (1600–2499 m)","#926caa"],
 ["montana_alta","Alta montaña (≥2500 m)","#654896"],
 ["cota_negativa_revisar","DEM negativo: revisión","#777e85"]];
const color=Object.fromEntries(STYLES.map(x=>[x[0],x[2]]));
const labels=Object.fromEntries(STYLES.map(x=>[x[0],x[1]]));
const n=x=>Number(x).toLocaleString("es-PE",{maximumFractionDigits:1});
const pathFor=(geom,xy)=>{
 const polygons=geom.type==="Polygon"?[geom.coordinates]:geom.coordinates;
 return polygons.map(poly=>poly.map(ring=>ring.map(([lon,lat],i)=>
   (i?"L":"M")+xy.x(lon).toFixed(2)+" "+xy.y(lat).toFixed(2)).join(" ")+"Z").join(" ")).join(" ");
};
function initMap(geo,report){
 const selector=$("oaf-9k-floor"),map=$("oaf-9k-map"),legend=$("oaf-9k-legend");
 legend.replaceChildren();
 for(const [value,label,paint] of STYLES){
  const span=document.createElement("span");span.className="oaf-9k-key";
  const chip=document.createElement("i");chip.style.backgroundColor=paint;
  span.append(chip,document.createTextNode(label));legend.append(span);
  const opt=document.createElement("option");opt.value=value;opt.textContent=label;selector.append(opt);
 }
 const boundaries=geo.features.flatMap(f=>f.geometry.type==="Polygon"?
   f.geometry.coordinates:[...f.geometry.coordinates]);
 const all=boundaries.flatMap(poly=>poly.flatMap(r=>r));
 const lon=all.map(q=>q[0]),lat=all.map(q=>q[1]);
 const xmin=Math.min(...lon),xmax=Math.max(...lon),ymin=Math.min(...lat),ymax=Math.max(...lat);
 const W=850,H=560,pad=24;
 const dy=Math.max(0.01,ymax-ymin),dx=Math.max(0.01,xmax-xmin);
 const x=z=>pad+(z-xmin)/dx*(W-2*pad);
 const y=z=>H-pad-(z-ymin)/dy*(H-2*pad);
 const xy={x,y};
 function draw(){
  map.replaceChildren();
  const root=svg("svg",{viewBox:"0 0 850 560",role:"img",
      "aria-label":"Sectores de influencia DEM por altitud de Lambayeque, agrupación preliminar y no límites oficiales"});
  root.classList.add("oaf-9k-svg");
  let shown=0,similar=0;
  for(const f of geo.features){
   const p=f.properties;
   if(selector.value!=="todos"&&selector.value!==p.estrato)continue;
   if($("oaf-9k-only-core").checked&&p.estado_evidencia!=="hipotesis_nucleo_conectado")continue;
   const e=svg("path",{d:pathFor(f.geometry,xy),
    fill:color[p.estrato]||"#939d9f",
    "fill-opacity":p.estado_evidencia==="hipotesis_nucleo_conectado"?"0.92":"0.66",
    stroke:p.estado_evidencia==="hipotesis_nucleo_conectado"?"#122f37":"#ffffff",
    "stroke-width":p.estado_evidencia==="hipotesis_nucleo_conectado"?"1.8":"0.8",
    tabindex:0,role:"button",
    "aria-label":p.id_sector+" "+labels[p.estrato]+
       ", entre "+n(p.alt_min_nodos_m)+" y "+n(p.alt_max_nodos_m)+" metros DEM, no validado"});
   e.append(svg("title",{},p.id_sector+" · "+labels[p.estrato]+" · "+p.n_nodos_dem+
       " nodos DEM · altitudes centrales "+n(p.alt_min_nodos_m)+"–"+n(p.alt_max_nodos_m)+
       " m · "+(p.familia_similitud||"sin núcleo multicelda")));
   const select=()=>{
    $("oaf-9k-detail").textContent=p.id_sector+" — "+labels[p.estrato]+
      ". Agrupa "+p.n_nodos_dem+" centros DEM; altitudes medidas en los centros: "+
      n(p.alt_min_nodos_m)+"–"+n(p.alt_max_nodos_m)+" m. "+
      "Testigos climáticos próximos: "+p.n_testigos_perfil_30anios+
      ". Familia de similitud: "+(p.familia_similitud||"sin núcleo multicelda")+
      ". Superficie cartográfica de influencia, NO zona agrícola ni clima homogéneo certificado.";
   };
   e.addEventListener("click",select);
   e.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();select();}});
   root.append(e);shown++;
   similar+=Number(p.estado_evidencia==="hipotesis_nucleo_conectado");
  }
  map.append(root);
  $("oaf-9k-visible").textContent=shown+" sectores de influencia en la vista; "+
    similar+" con hipótesis multicelda conectada";
 }
 selector.addEventListener("change",draw);
 $("oaf-9k-only-core").addEventListener("change",draw);
 draw();
 $("oaf-9k-geom-note").textContent=
   report.n_nodos_dem+" puntos con DEM; "+report.n_testigos_con_360_meses+
   " testigos con climatologías 1996–2025; "+report.n_familias_multicelda_exploratorias+
   " familias multicelda exploratorias; "+report.n_poligonos_graficos_exploratorios+
   " piezas geométricas. "+report.n_nodos_no_asociados+
   " puntos DEM sin testigo climático cercano del mismo piso. No representan porcentajes de superficie.";
}
async function init(){
 if(!$("oaf-9k-visor"))return;
 const status=$("oaf-9k-status");
 try{
  const [a,b]=await Promise.all(["datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson",
    "datos/sectores_agroclimaticos_9k/estado_sectores_9k.json"].map(u=>fetch(u,{cache:"no-store"})));
  if(!a.ok||!b.ok)throw Error("las geometrías o metadatos 9K todavía no están publicados");
  const [geo,report]=await Promise.all([a.json(),b.json()]);
  if(report.fase!=="9K"||report.n_zonas_homogeneas_certificadas!==0||
     report.validacion_espacial_de_pronosticos!==false||
     geo.features.length!==report.n_poligonos_graficos_exploratorios)
     throw Error("auditoría SIG inconsistente");
  initMap(geo,report);
  status.textContent="Cartografía 9K generada a partir de DEM y perfiles regionales; solo agrupaciones exploratorias.";
  try{
   const r=await fetch("datos/sectores_agroclimaticos_9k/inventario_nmme_9k.json",{cache:"no-store"});
   if(!r.ok)throw Error("inventario NOAA pendiente");
   const j=await r.json();
   $("oaf-9k-nmme").textContent="NOAA NMME: "+j.fuentes_netcdf_comprobadas+
     " de "+j.fuentes_netcdf_esperadas+" NetCDF de anomalías 2026-10 inspeccionados. "+
     "Es una señal de escala regional (~1°) y NO un pronóstico por altitud o por polígono. "+
     (j.errores_consulta.length?"Incidencias de acceso: "+j.errores_consulta.length+".":"");
  }catch(e){$("oaf-9k-nmme").textContent="Lectura NOAA NMME pendiente: "+e.message+
    ". No se imputan predicciones a los sectores."}
 }catch(e){status.textContent="Mapa 9K pendiente: "+e.message+
   ". Las fases 8N, 8O y 8P conservan los 420 puntos DEM y testigos originales."}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();