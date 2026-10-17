/* 8Q OAF: transectos lineales del DEM y series 1996-2025 bajo vigilancia.
 * Ningún mapa crea polígonos climáticos o certifica alerta fitosanitaria. */
(()=>{
"use strict";
const details=document.getElementById("oaf-transects-8q");if(!details)return;
const el=id=>document.getElementById(id),status=el("oaf-8q-status"),
      map=el("oaf-8q-map"),table=el("oaf-8q-table"),
      coherenceTable=el("oaf-8q-coherence");
let state=null,samples=[],metrics=[],coherence=[],shape=null;
const fmt=x=>typeof x==="number"&&Number.isFinite(x)?x.toLocaleString("es-PE",{maximumFractionDigits:1}):"—";
const parseCsv=s=>{
 const lines=s.trim().split(/\r?\n/),heads=lines.shift().split(",");
 return lines.filter(Boolean).map(line=>{
  const cols=line.split(",");
  if(cols.length!==heads.length)throw Error("CSV de transectos incompleto");
  return Object.fromEntries(heads.map((k,i)=>[k,cols[i]]));
 });
};
const svg=(tag,attrs={},tip)=>{
 const o=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [k,v]of Object.entries(attrs))o.setAttribute(k,String(v));
 if(tip!==undefined){const t=document.createElementNS("http://www.w3.org/2000/svg","title");t.textContent=tip;o.append(t)}
 return o;
};
function render(){
 if(!state||!shape)return;
 map.replaceChildren();table.replaceChildren();coherenceTable.replaceChildren();
 const coords=shape.features[0].geometry.coordinates[0];
 const xmin=Math.min(...coords.map(p=>p[0])),xmax=Math.max(...coords.map(p=>p[0]));
 const ymin=Math.min(...coords.map(p=>p[1])),ymax=Math.max(...coords.map(p=>p[1]));
 const W=790,H=525,pad=25;
 const x=v=>pad+(v-xmin)/(xmax-xmin)*(W-2*pad);
 const y=v=>H-pad-(v-ymin)/(ymax-ymin)*(H-2*pad);
 const fig=svg("svg",{viewBox:"0 0 790 525",role:"img",
  "aria-label":"Tres transectos de muestreo DEM entre testigos piloto V1 y V2. No son rutas ni zonas homogéneas."});
 fig.style.cssText="width:100%;height:auto;max-height:550px";
 fig.append(svg("path",{d:coords.map((p,i)=>(i?"L":"M")+x(p[0]).toFixed(2)+","+y(p[1]).toFixed(2)).join(" ")+" Z",
  fill:"#eaf1e8",stroke:"#516f7a","stroke-width":1.5}));
 const nodal=[...samples];
 const ref={
  M0163:{lat:-6.46875,lon:-79.53125},M0184:{lat:-6.40625,lon:-79.53125},
  M0224:{lat:-6.3125,lon:-79.5625},
  M0234:{lat:-6.28125,lon:-79.34375},M0308:{lat:-6.125,lon:-79.375}
 };
 const colors={V1a:"#d17e3a",V1b:"#2b8a7e",V2:"#785f9f"};
 for(const segment of state.transectos){
  const a=ref[segment.inicio],b=ref[segment.fin];
  if(!a||!b)continue;
  fig.append(svg("line",{x1:x(a.lon),y1:y(a.lat),x2:x(b.lon),y2:y(b.lat),
    stroke:colors[segment.transecto]||"#333","stroke-width":2.5,
    "stroke-dasharray":"5,4"},
    "Línea de muestreo conceptual "+segment.transecto+", no ruta real sobre el terreno"));
 }
 for(const point of nodal){
  const c=svg("circle",{cx:x(point.longitud),cy:y(point.latitud),r:5.5,
    fill:colors[point.transecto]||"#444",stroke:"#fff","stroke-width":1.2},
    point.testigo_id+" · "+point.transecto+" · "+fmt(point.altitud_dem_m)+" m DEM");
  fig.append(c);
 }
 for(const [id,p]of Object.entries(ref)){
   fig.append(svg("circle",{cx:x(p.lon),cy:y(p.lat),r:7,fill:"#fff",
     stroke:"#202f41","stroke-width":2},id+" · testigo principal V1/V2"));
 }
 map.append(fig);
 const message=document.createElement("p");message.className="small";
 message.textContent="Círculos blancos: testigos originales. Puntos coloreados: muestras intermedias DEM. Las líneas discontinuas indican únicamente un transecto conceptual; no representan caminos, continuidad de la topografía ni fronteras zonales.";
 map.append(message);
 for(const item of samples){
  const m=metrics.find(x=>x.testigo_id===item.testigo_id);
  const tr=document.createElement("tr");
  const values=[item.transecto,item.testigo_id,fmt(item.altitud_dem_m),
    fmt(item.salto_altitudinal_lineal_m),
    fmt(item.distancia_al_objetivo_km),
    m?fmt(m.tmedia_1996_2025_c):"Pendiente",
    m?fmt(m.precipitacion_anual_media_mm):"Pendiente"];
  for(const text of values){const td=document.createElement("td");td.textContent=String(text);tr.append(td)}
  table.append(tr);
 }
 for(const pair of coherence){
   const tr=document.createElement("tr");
   const fields=[pair.transecto,pair.testigo_a+"–"+pair.testigo_b,
      Number(pair.correlacion_anomalia_tmedia_360_meses).toFixed(3),
      Number(pair.mae_diferencia_anomalia_tmedia_c).toFixed(3),
      pair.igual_celda_temperatura==="true"?"Sí":"No",
      pair.igual_celda_precipitacion==="true"?"Sí":"No",
      "No"];
   for(const value of fields){
      const td=document.createElement("td");td.textContent=value;tr.append(td);
   }
   coherenceTable.append(tr);
 }
}
async function load(){
 status.textContent="Comprobando diez puntos intermedios y sus fuentes climáticas originales…";
 try{
  const paths=["datos/transectos_8q/estado_transectos_8q.json",
   "datos/transectos_8q/muestras_intermedias_8q.csv",
   "datos/transectos_8q/comparacion_climatica_8q.csv",
   "datos/zonificacion_8n/limite_lambayeque_referencial.geojson",
   "datos/transectos_8q/coherencia_anomalias_8q.csv"];
  const resp=await Promise.all(paths.map(p=>fetch(p,{cache:"no-store"})));
  if(resp.some(r=>!r.ok))throw Error("Archivos fuente todavía no disponibles");
  const [r,points,clima,geom,anom]=await Promise.all(resp.map((v,i)=>
    (i===0||i===3)?v.json():v.text()));
  if(r.fase!=="8Q"||r.zonas_contiguas_homogeneas_demostradas!==0||
    r.poligonos_agroclimaticos_certificados!==0||
    r.modelo_predictivo_zonal_validado!==false||
    r.instrumentos_SENAMHI_confirmados!==0||
    geom.features?.[0]?.properties?.codigo_ubigeo!=="14")
    throw Error("Los límites científicos del estudio no concuerdan");
  const p=parseCsv(points),m=parseCsv(clima),corr=parseCsv(anom);
  if(p.length!==r.testigos_intermedios_dem_seleccionados||
     m.length!==r.n_testigos_intermedios_30_anios_completos||
     corr.length!==r.n_comparaciones_de_anomalias_por_pares)
     throw Error("Datos y reportes de muestreo incompatibles");
  for(const o of p){
   for(const k of ["latitud","longitud","altitud_dem_m",
                    "salto_altitudinal_lineal_m","distancia_al_objetivo_km"]){
      o[k]=Number(o[k]);if(!Number.isFinite(o[k]))throw Error("Coordenadas no numéricas");
   }
   if(o.homogeneidad_espacial_acreditada!=="false")
     throw Error("Una muestra DEM no es una zona homogénea acreditada");
  }
  for(const o of m){
    for(const k of ["tmedia_1996_2025_c","precipitacion_anual_media_mm"])
     {o[k]=Number(o[k]);if(!Number.isFinite(o[k]))throw Error("Clima no numérico")}
    if(o.clima_instrumental_verificado!=="false")throw Error("Reanálisis no es instrumento");
  }
  for(const pair of corr){
    if(pair.independencia_instrumental_verificada!=="false")
      throw Error("Correlación modelada no equivale a prueba instrumental");
    if(!Number.isFinite(Number(pair.correlacion_anomalia_tmedia_360_meses))||
       !Number.isFinite(Number(pair.mae_diferencia_anomalia_tmedia_c)))
      throw Error("Correlación mensual no numérica");
  }
  state=r;samples=p;metrics=m;coherence=corr;shape=geom;
  el("oaf-8q-sites").textContent=String(p.length);
  el("oaf-8q-sources").textContent=r.fuentes_climaticas_verificadas+"/6";
  el("oaf-8q-complete").textContent=String(m.length);
  status.textContent=m.length>0
   ?"Comparación descriptiva de "+m.length+" puntos con 360 meses. No prueba continuidad climática, habilidad predictiva o representatividad agrícola."
   :"Altitudes DEM verificadas de "+p.length+" puntos. Series meteorológicas completas pendientes ("+
     r.fuentes_climaticas_verificadas+"/6). Sin declarar homogeneidad entre testigos.";
  render();
 }catch(err){
  map.replaceChildren();table.replaceChildren();coherenceTable.replaceChildren();
  status.textContent="Sin resultados presentables: "+err.message+". No se simulan perfiles o zonas.";
 }
}
el("oaf-8q-reload")?.addEventListener("click",load);
let started=false;details.addEventListener("toggle",()=>{if(details.open&&!started){started=true;load()}});
})();
