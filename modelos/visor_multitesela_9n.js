/* OAF 9N — cartografía multipieza validada, 42 sectores sin imputar elevación faltante. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const NS="http://www.w3.org/2000/svg";
const PALETTE={
 llanura_costa:["Costa baja","#3087a3"],
 valle_bajo:["Valle bajo","#48a28a"],
 piedemonte:["Piedemonte","#c59e4b"],
 montana_baja:["Ladera baja","#c58753"],
 montana_media:["Ladera media","#9975ae"],
 montana_alta:["Alta montaña","#725b9d"],
 cota_negativa_revisar:["DEM negativo, revisar","#9a9a9a"]};
const label=x=>PALETTE[x]?.[0]||x;
const fmt=(v,d=1)=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:d}):"—";
function svg(t,attributes={},text){
 const e=document.createElementNS(NS,t);
 for(const [k,v] of Object.entries(attributes))e.setAttribute(k,String(v));
 if(text!==undefined)e.textContent=text;
 return e;
}
function path(geometry,scale){
 if(!geometry)return"";
 const groups=geometry.type==="Polygon"?[geometry.coordinates]:geometry.coordinates;
 return groups.map(poly=>poly.map(ring=>ring.map(([x,y],i)=>
  (i?"L":"M")+scale.x(x).toFixed(1)+" "+scale.y(y).toFixed(1)).join(" ")+"Z").join(" ")).join(" ");
}
async function read(url){
 const r=await fetch(url,{cache:"no-store"});
 if(!r.ok)throw Error("Falta el archivo "+url);
 return r.json();
}
function txt(id,text){if($(id))$(id).textContent=text}
async function init(){
 if(!$("oaf-9n-visor"))return;
 try{
  const base="datos/cobertura_multitesela_9n/";
  const [status,manifest,rows,finalGeo,prevGeo]=await Promise.all([
    read(base+"estado_cobertura_9n.json"),read(base+"fuentes_dem_9n.json"),
    read(base+"evaluacion_42_sectores_9n.json"),
    read(base+"mascaras_multitesela_9n.geojson"),
    read("datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson")
  ]);
  if(status.fase!=="9N"||status.n_sectores_9k!==42||rows.length!==42||
    status.n_zonas_agroclimaticas_homogeneas_validadas!==0||
    status.n_geometrias_filtro!==finalGeo.features.length ||
    status.teselas_archivadas_validas!==manifest.teselas_que_pudieron_abrirse.length)
   throw Error("Auditoría de cobertura incoherente");
  try{
    const todo=await read(base+"prioridades_validacion_climatica_9n.json");
    if(todo.fase!=="9N"||todo.n_sectores!==42||
       todo.zonas_climaticamente_homogeneas_certificadas!==0)
      throw Error("Inventario de prioridades inconsistente");
    const counts=todo.conteos_prioridad;
    txt("oaf-9n-validation","Prioridades de verificación: "+
      (counts.alta||0)+" sectores de prioridad alta, "+
      (counts.media||0)+" media y "+
      (counts.basica_pendiente_de_validacion||0)+
      " pendientes de validación estándar. Los 81 perfiles ERA5/ERA5-Land son reanálisis, no pluviómetros independientes. Las 3 estaciones históricas de 9I no validan 1996–2025 por sector.");
  }catch(e){
    txt("oaf-9n-validation","Inventario de contraste instrumental pendiente: "+e.message+
      ". No hay pruebas de homogeneidad espacial independientes certificadas.");
  }
  const byId=new Map(rows.map(r=>[r.id_sector,r]));
  txt("oaf-9n-summary",status.n_sectores_cobertura_completa+
      " con cobertura completa · "+status.n_sectores_cobertura_parcial+
      " parcial · "+status.n_sectores_sin_dem+" sin DEM · 42 sectores inventariados");
  txt("oaf-9n-status","Evaluación topográfica GLO-90 de "+
      status.teselas_archivadas_validas+" de "+status.teselas_necesarias+
      " teselas necesarias. Solo muestra compatibilidad física del DSM; no demuestra microclimas iguales.");
  const failures=manifest.teselas_que_no_pudieron_comprobarse;
  txt("oaf-9n-tile-status",failures.length ?
    "Teselas no verificadas: "+failures.map(f=>f.id).join(", ")+
    ". Esas partes siguen sin elevación contrastada; la ausencia de archivo no equivale a altitud cero.":
    "Se archivaron los seis cuadrantes requeridos con SHA-256. Esta cobertura no certifica estaciones ni condiciones de cultivo.");
  const selectors=$("oaf-9n-floor"),filterStatus=$("oaf-9n-coverage");
  for(const [value,[name]] of Object.entries(PALETTE)){
   const option=document.createElement("option");
   option.value=value;option.textContent=name;selectors.append(option);
  }
  const colors=$("oaf-9n-legend");
  for(const [key,[name,c]] of Object.entries(PALETTE)){
   const item=document.createElement("span");item.className="oaf-9n-key";
   const chip=document.createElement("i");chip.style.background=c;
   item.append(chip,document.createTextNode(name));colors.append(item);
  }
  // La base 9K muestra TODO el contorno, incluso cuando falta DEM.
  const points=prevGeo.features.flatMap(f=>{
   const p=f.geometry.type==="Polygon"?[f.geometry.coordinates]:f.geometry.coordinates;
   return p.flatMap(poly=>poly.flatMap(ring=>ring));
  });
  const lons=points.map(p=>p[0]),lats=points.map(p=>p[1]);
  const minX=Math.min(...lons),maxX=Math.max(...lons),
        minY=Math.min(...lats),maxY=Math.max(...lats);
  const W=820,H=570,pad=20,dx=Math.max(maxX-minX,.01),dy=Math.max(maxY-minY,.01);
  const scale={x:x=>pad+(x-minX)/dx*(W-2*pad),
               y:y=>H-pad-(y-minY)/dy*(H-2*pad)};
  const resultById=new Map(finalGeo.features.map(f=>[f.properties.sector_9k,f]));
  const details=$("oaf-9n-detail");
  function show(row){
   details.textContent=row.id_sector+" · "+label(row.piso_nominal)+
    ". DEM: "+row.cobertura+
    "; teselas útiles: "+row.n_teselas_con_datos+
    "; compatibilidad de altitud y pendiente ≤30° (~270 m): "+
      (row.compatible_270m_30===null?"no evaluable":fmt(100*row.compatible_270m_30)+" %")+
    "; dirección dominante de descenso: "+(row.orientacion_frecuente_270||"no calculada")+
    "; diferencia absoluta entre 270 m y 450 m: "+
    (row.diferencia_abs_30_270_vs_450===null?"no evaluable":
      fmt(row.diferencia_abs_30_270_vs_450*100,2)+" puntos porcentuales")+
    ". Piso físico de la muestra y cuencas no equivalen a climatología homogénea.";
  }
  function draw(){
   const target=$("oaf-9n-map"),table=$("oaf-9n-table");
   target.replaceChildren();table.replaceChildren();
   const graph=svg("svg",{viewBox:"0 0 "+W+" "+H,role:"img",
     "aria-label":"Mapa de sectores DEM Copernicus GLO-90 9N; la ausencia de color interior no representa altitud cero"});
   graph.style.width="100%";
   const sectorRows=rows.filter(row=>(selectors.value==="todos"||
       selectors.value===row.piso_nominal)&&
       (filterStatus.value==="todos"||filterStatus.value===row.cobertura));
   for(const row of sectorRows){
    const old=prevGeo.features.find(f=>f.properties.id_sector===row.id_sector);
    if(!old)continue;
    const outlined=svg("path",{d:path(old.geometry,scale),
       fill:"#eeeeee","fill-opacity":0.18,
       stroke:row.cobertura==="sin_dem"?"#8c5e5e":"#94a9a9",
       "stroke-width":1.2,"stroke-dasharray":row.cobertura==="completa"?"none":"5 3",
       tabindex:0,role:"button"});
    outlined.append(svg("title",{},row.id_sector+" · "+row.cobertura+" · "+label(row.piso_nominal)));
    outlined.addEventListener("click",()=>show(row));
    outlined.addEventListener("keydown",e=>{
      if(e.key==="Enter"||e.key===" "){e.preventDefault();show(row)}
    });
    graph.append(outlined);
    const filtered=resultById.get(row.id_sector);
    if(filtered){
      const filled=svg("path",{d:path(filtered.geometry,scale),
        fill:PALETTE[row.piso_nominal]?.[1]||"#888","fill-opacity":.78,
        stroke:"#fbfbfb","stroke-width":.7,tabindex:0,role:"button"});
      filled.append(svg("title",{},row.id_sector+" · compatibilidad "+
        fmt((row.compatible_270m_30||0)*100)+" % de píxeles"));
      filled.addEventListener("click",()=>show(row));
      filled.addEventListener("keydown",e=>{
       if(e.key==="Enter"||e.key===" "){e.preventDefault();show(row)}
      });
      graph.append(filled);
    }
    const tr=document.createElement("tr");
    for(const str of [row.id_sector,label(row.piso_nominal),row.cobertura,
       row.compatible_270m_30===null?"—":fmt(row.compatible_270m_30*100,1)+" %",
       row.diferencia_abs_30_270_vs_450===null?"—":
          fmt(row.diferencia_abs_30_270_vs_450*100,1)+" pp"]){
      const td=document.createElement("td");td.textContent=str;tr.append(td);
    }
    table.append(tr);
   }
   target.append(graph);
   txt("oaf-9n-shown",sectorRows.length+
      " sectores según los filtros. Gris/discontinuo: información insuficiente o cobertura parcial.");
  }
  selectors.addEventListener("change",draw);
  filterStatus.addEventListener("change",draw);
  draw();
 }catch(e){
  txt("oaf-9n-status","No se puede cargar la cartografía científica 9N: "+e.message+
    ". Los resultados ya verificados de 9K, 9L y 9M permanecen disponibles.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();