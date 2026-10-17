/* OAF 8O - points DEM and climatological pilot clusters (not certified zones). */
(()=>{
"use strict";
const panel=document.getElementById("oaf-homogeneity-8o");if(!panel)return;
const $=id=>document.getElementById(id);
const status=$("oaf-8o-state"),table=$("oaf-8o-table"),plot=$("oaf-8o-map");
const filter=$("oaf-8o-filter");
const colors={llanura_costa:"#2b83ba",valle_bajo:"#42af9c",piedemonte:"#deae57",
 montana_baja:"#d58249",montana_media:"#9879b5",montana_alta:"#594181",
 cota_negativa_revisar:"#79848c"};
const names={llanura_costa:"Planicie <100 m",valle_bajo:"Valle bajo 100–299 m",
 piedemonte:"Piedemonte 300–799 m",montana_baja:"Laderas 800–1599 m",
 montana_media:"Montaña 1600–2499 m",montana_alta:"Alta montaña ≥2500 m",
 cota_negativa_revisar:"Cotas DEM negativas"};
let ground=[],testigos=[],boundary=null,inventory=null,climate=null,groups=[];
const svg=(tag,attrs={},label)=>{
 const node=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [k,v] of Object.entries(attrs))node.setAttribute(k,String(v));
 if(label!==undefined)node.textContent=label;return node;
};
const fmt=v=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:1}):"—";
const parseCSV=s=>{
 const lines=s.trim().split(/\r?\n/),keys=lines.shift().split(",");
 return lines.filter(Boolean).map(line=>{
  const cols=line.split(",");
  if(cols.length!==keys.length)throw Error("CSV climático malformado");
  return Object.fromEntries(keys.map((k,i)=>[k,cols[i]]));
 });
};
function render(){
 if(!inventory||!boundary)return;
 table.replaceChildren();plot.replaceChildren();
 for(const key of Object.keys(colors)){
  const subset=ground.filter(r=>r.estrato_fisico_preliminar===key);
  const row=document.createElement("tr");
  const vals=[names[key],subset.length,
    subset.length?fmt(Math.min(...subset.map(x=>x.altitud_dem_m))):"—",
    subset.length?fmt(Math.max(...subset.map(x=>x.altitud_dem_m))):"—","No validada"];
  for(const v of vals){const td=document.createElement("td");td.textContent=String(v);row.append(td)}
  table.append(row);
 }
 const ring=boundary.features[0].geometry.coordinates[0];
 const xmin=Math.min(...ring.map(r=>r[0])),xmax=Math.max(...ring.map(r=>r[0]));
 const ymin=Math.min(...ring.map(r=>r[1])),ymax=Math.max(...ring.map(r=>r[1]));
 const W=760,H=525,pad=25;
 const x=v=>pad+(v-xmin)/(xmax-xmin)*(W-2*pad);
 const y=v=>H-pad-(v-ymin)/(ymax-ymin)*(H-2*pad);
 const fig=svg("svg",{viewBox:"0 0 760 525",role:"img",
  "aria-label":"Muestreo adaptativo de elevación de Lambayeque, no zonificación agroclimática validada"});
 fig.style.cssText="width:100%;height:auto;max-height:560px";
 fig.append(svg("path",{d:ring.map((p,i)=>(i?"L":"M")+x(p[0]).toFixed(1)+","+y(p[1]).toFixed(1)).join(" ")+" Z",
   fill:"#eff2eb",stroke:"#5d7a83","stroke-width":1.4}));
 for(const r of ground){
  if(filter.value!=="all"&&filter.value!==r.estrato_fisico_preliminar)continue;
  const point=svg("circle",{cx:x(r.longitud),cy:y(r.latitud),r:3.6,
   fill:colors[r.estrato_fisico_preliminar]||"#777",stroke:"#fff","stroke-width":0.7});
  point.append(svg("title",{},r.id+" · DEM "+fmt(r.altitud_dem_m)+" m · "+names[r.estrato_fisico_preliminar]));
  fig.append(point);
 }
 for(const t of testigos){
  const assoc=groups.find(g=>g.id===t.id);
  const circle=svg("circle",{cx:x(t.longitud),cy:y(t.latitud),r:7.5,
    stroke:"#173e50",fill:"none","stroke-width":2});
  circle.append(svg("title",{},t.id+" · testigo "+(assoc?.grupo_similitud_exploratoria||"sin perfil completo")));
  fig.append(circle);
 }
 plot.append(fig);
 const p=document.createElement("p");p.className="small";
 p.textContent="Puntos: DEM de Copernicus GLO-90 vía Open-Meteo, no termómetros ni parcelas. Anillos: testigos piloto de climatología. Polígono departamental referencial y simplificado, pendiente de validación oficial.";
 plot.append(p);
 const q=document.createElement("p");q.className="small";
 q.textContent=climate?.n_grupos_similitud_exploratorios?
  "Testigos con 30 años multivariables: "+climate.n_testigos_con_perfil_30anios+
  ". Conjuntos de similitud preliminares: "+climate.n_grupos_similitud_exploratorios+
  ". No son zonas homogéneas cartografiadas ni validadas.":
  "Perfiles climáticos multivariables pendientes: "+(climate?.n_fuentes_archivadas??0)+
  "/6 bloques históricos; 0 zonas climáticas certificadas.";
 plot.append(q);
 if(climate?.analisis?.ranking_cohesion_climatica_no_zonas){
   const title=document.createElement("strong");
   title.textContent="Cohesión de perfiles piloto (no zonas agrícolas)";
   plot.append(title);
   const info=document.createElement("ul");info.className="small";
   for(const g of climate.analisis.ranking_cohesion_climatica_no_zonas){
     const row=document.createElement("li");
     row.textContent=g.grupo+": "+g.n_testigos+
       " testigos; distancia climática interna "+g.distancia_climatica_interna_media+
       "; extensión entre testigos hasta "+g.diametro_geografico_testigos_km+
       " km, desnivel entre testigos "+g.rango_altitudinal_testigos_m+
       " m; cotas DEM ≤ 0 m: "+g.testigos_cota_dem_menor_o_igual_cero+
       ". No delimita una región agronómica confirmada.";
     info.append(row);
   }
   plot.append(info);
   const notice=document.createElement("p");notice.className="small";
   notice.textContent="La coincidencia de clasificación por décadas no sustituye un mapa terrestre oficial, estaciones independientes, continuidad geográfica ni validación de campo.";
   plot.append(notice);
 }
}
async function load(){
 status.textContent="Leyendo altitudes, malla y fuentes climáticas verificables…";
 try{
  const urls=["datos/muestreo_8o/estado_muestreo_8o.json",
    "datos/muestreo_8o/nodos_dem_8o.csv",
    "datos/muestreo_8o/testigos_climaticos_8o.csv",
    "datos/perfiles_climaticos_8o/estado_climatico_8o.json",
    "datos/perfiles_climaticos_8o/grupos_testigos_8o.csv",
    "datos/zonificacion_8n/limite_lambayeque_referencial.geojson"];
  const r=await Promise.all(urls.map(u=>fetch(u,{cache:"no-store"})));
  if(r.some(x=>!x.ok))throw Error("Archivos científicos aún no disponibles");
  const vals=await Promise.all(r.map((v,i)=>[0,3,5].includes(i)?v.json():v.text()));
  const [st,nodes,chosen,cl,clu,geom]=vals;
  if(st.zonas_homogeneas_demostradas!==0||cl.homogeneidad_espacial_certificada!==false||
    cl.zonas_agroclimaticas_operativas!==0||st.fase!=="8O"||cl.fase!=="8O"||
    geom.features?.[0]?.properties?.codigo_ubigeo!=="14")
      throw Error("Las garantías del reporte científico no concuerdan");
  const n=parseCSV(nodes),t=parseCSV(chosen),g=parseCSV(clu);
  if(n.length!==st.nodos_dem_verificados||t.length!==st.n_testigos_climaticos_seleccionados||
     g.length!==cl.n_testigos_con_perfil_30anios)
     throw Error("Conteo de datos geográficos/climáticos inconsistente");
  for(const collection of [n,t,g]){
   for(const p of collection){
    for(const field of ["latitud","longitud","altitud_dem_m"]){
      p[field]=Number(p[field]);
      if(!Number.isFinite(p[field]))throw Error("Número de altitud/coordenada inválido");
    }
   }
  }
  if(n.some(p=>p.homogeneidad_validada!=="false")||
     g.some(p=>p.zona_climatica_validada!=="false"))
    throw Error("No se admiten validaciones homogéneas sin datos");
  ground=n;testigos=t;boundary=geom;inventory=st;climate=cl;groups=g;
  $("oaf-8o-nodes").textContent=st.nodos_dem_verificados.toLocaleString("es-PE");
  $("oaf-8o-profiles").textContent=String(cl.n_testigos_con_perfil_30anios);
  $("oaf-8o-groups").textContent=String(cl.n_grupos_similitud_exploratorios);
  status.textContent="Elevaciones verificadas: "+n.length+"/"+st.nodos_diseno+
   " puntos, "+st.n_refuerzos+" de refinamiento. La similitud climática y continuidad territorial requieren verificación.";
  render();
 }catch(e){
  plot.replaceChildren();table.replaceChildren();
  status.textContent="Datos 8O todavía no comprobables: "+e.message+". No se presentan valores simulados.";
 }
}
filter.addEventListener("change",render);
$("oaf-8o-refresh")?.addEventListener("click",load);
let started=false;
panel.addEventListener("toggle",()=>{if(panel.open&&!started){started=true;load()}});
})();
