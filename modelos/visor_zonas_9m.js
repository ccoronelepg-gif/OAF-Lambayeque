/* OAF 9M: mapa de filtros físicos sobre UNA tesela; no extender resultados a todo Lambayeque. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const NS="http://www.w3.org/2000/svg";
const floors={
  llanura_costa:["Planicie (0–99 m)","#2d83ae"],
  valle_bajo:["Valle (100–299 m)","#3fa387"],
  piedemonte:["Piedemonte (300–799 m)","#c6a052"],
  montana_baja:["Ladera baja (800–1599 m)","#d48b55"],
  montana_media:["Ladera media (1600–2499 m)","#9e81b9"],
  montana_alta:["Alta montaña (≥2500 m)","#685090"],
  cota_negativa_revisar:["Altitud DEM negativa (revisar)","#7e8b91"]};
const fmt=(v,d=1)=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:d}):"—";
const el=(tag,attrs={},text)=>{
 const p=document.createElementNS(NS,tag);
 for(const [key,value] of Object.entries(attrs))p.setAttribute(key,String(value));
 if(text!==undefined)p.textContent=text;
 return p;
};
function geomPath(geometry,xy){
 if(!geometry)return"";
 const groups=geometry.type==="Polygon"?[geometry.coordinates]:geometry.coordinates;
 return groups.map(poly=>poly.map(ring=>ring.map(([lon,lat],i)=>
   (i?"L":"M")+xy.x(lon).toFixed(1)+" "+xy.y(lat).toFixed(1)).join(" ")+" Z").join(" ")).join(" ");
}
async function get(path){
 const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("No disponible: "+path);
 return r.json();
}
function setText(id,v){const e=$(id);if(e)e.textContent=v}
async function init(){
 if(!$("oaf-9m-visor"))return;
 try{
  const [report,geo]=await Promise.all([
   get("datos/sensibilidad_9m/estado_relieve_9m.json"),
   get("datos/sensibilidad_9m/sectores_filtrados_tesela_9m.geojson")]);
  if(report.fase!=="9M"||report.n_sectores_9k!==42||
     report.n_cuencas_ANA_certificadas!==0||report.n_zonas_homogeneas_certificadas!==0||
     report.alerta_fitosanitaria_generada!==false||
     geo.features.length!==report.n_geometrias_refinadas)
   throw Error("Estado de calidad SIG inconsistente");
  let hydro=null;
  try{hydro=await get("datos/sensibilidad_9m/estado_cuencas_ana_9m.json")}catch(e){}
  setText("oaf-9m-count",String(report.n_sector_evaluados_con_dos_escalas));
  setText("oaf-9m-hydro",hydro?String(hydro.n_sectores_9k_con_interseccion):"—");
  setText("oaf-9m-change",report.resumen_cambio_fraccion_30grados_270_450.mediana===null?
   "—":fmt(report.resumen_cambio_fraccion_30grados_270_450.mediana*100,1)+" pp");
  setText("oaf-9m-status","Corte 17/10/2026: evaluación DEM de "+
   report.n_sector_evaluados_con_dos_escalas+" de los 42 polígonos 9K en la única tesela GLO-90 disponible. "+
   "Se distinguen cobertura total, parcial y sectores fuera de esta tesela.");
  if(!hydro){
   setText("oaf-9m-catchments","Capa ANA/IDEP pendiente de evaluación: no se han asignado cuencas.");
  }else if(!hydro.cobertura_institucional_capa_descargada){
   setText("oaf-9m-catchments","Fuente hidrográfica ANA/IDEP no recuperada: "+
    (hydro.problema_acceso||"sin respuesta")+"; sin asignación de cuencas.");
  }else{
   setText("oaf-9m-catchments","Se consultó la capa de unidades hidrográficas ANA/IDEP: "+
    hydro.n_unidades_devueltas+" geometrías de origen, "+
    hydro.n_sectores_9k_con_interseccion+
    " sectores con al menos un cruce referencial. No se ha validado la vigencia ni certificado el límite de cuencas.");
  }
  const select=$("oaf-9m-floor"),table=$("oaf-9m-table"),map=$("oaf-9m-map");
  for(const [key,[name]] of Object.entries(floors)){
   const o=document.createElement("option");o.value=key;o.textContent=name;select.append(o);
  }
  const legend=$("oaf-9m-legend");
  for(const [key,[name,c]] of Object.entries(floors)){
   const item=document.createElement("span");item.className="oaf-9m-key";
   const chip=document.createElement("i");chip.style.background=c;
   item.append(chip,document.createTextNode(name));legend.append(item);
  }
  const featureById=new Map(geo.features.map(f=>[f.properties.id_sector_9k,f]));
  // Mostrar geometrías publicadas (los datos no recuperables NO se rellenan).
  const coords=geo.features.flatMap(f=>{
   const g=f.geometry;
   if(!g)return[];
   const pp=g.type==="Polygon"?[g.coordinates]:g.coordinates;
   return pp.flatMap(poly=>poly.flatMap(ring=>ring));
  });
  if(!coords.length)throw Error("Ninguna geometría SIG evaluable");
  const mnX=Math.min(...coords.map(p=>p[0])),mxX=Math.max(...coords.map(p=>p[0]));
  const mnY=Math.min(...coords.map(p=>p[1])),mxY=Math.max(...coords.map(p=>p[1]));
  const W=850,H=510,pad=22,dx=Math.max(.01,mxX-mnX),dy=Math.max(.01,mxY-mnY);
  const xy={x:v=>pad+(v-mnX)/dx*(W-2*pad),
            y:v=>H-pad-(v-mnY)/dy*(H-2*pad)};
  function detail(f){
   const p=f.properties;const m=report.muestra_sectorial?.find(r=>r.id_sector===p.id_sector_9k);
   // La tabla de sensibilidad se carga por CSV y el tooltip identifica ID y procedencia.
   setText("oaf-9m-detail",p.id_sector_9k+" · "+floors[p.piso][0]+
    " · orientación dominante "+(p.orientacion_dominante||"no definida")+
    " · fracción de píxeles compatibles (270 m, pendiente ≤30°) "+
    fmt(p.fraccion_fisica_filtrada_270m_30*100,1)+" %. "+
    "La máscara es experimental y corresponde únicamente a la tesela S07 W080; "+
    "no permite extrapolar aptitud agrícola ni incidencia fitosanitaria.");
  }
  function draw(){
   table.replaceChildren();map.replaceChildren();
   const svg=el("svg",{viewBox:"0 0 "+W+" "+H,role:"img",
    "aria-label":"Máscaras físicas de la tesela Copernicus S07 W080 por clase de elevación; no zonas agrícolas certificadas."});
   const display=geo.features.filter(f=>select.value==="todas"||f.properties.piso===select.value);
   for(const f of display){
    const p=f.properties,name=floors[p.piso]?.[0]||p.piso;
    const path=el("path",{d:geomPath(f.geometry,xy),
       fill:floors[p.piso]?.[1]||"#888","fill-opacity":0.78,tabindex:0});
    path.append(el("title",{},p.id_sector_9k+" · "+name+" · "+
     fmt(p.fraccion_fisica_filtrada_270m_30*100)+" % de píxeles compatibles"));
    path.addEventListener("click",()=>detail(f));
    path.addEventListener("keydown",e=>{
      if(e.key==="Enter"||e.key===" "){e.preventDefault();detail(f)}
    });
    svg.append(path);
    const row=document.createElement("tr");
    for(const v of [p.id_sector_9k,name,
      (p.orientacion_dominante||"—"),
      fmt(p.fraccion_fisica_filtrada_270m_30*100,1)+" %",
      p.tipo_cobertura_tesela==="completa"?"Completa":"Parcial"]){
     const cell=document.createElement("td");cell.textContent=v;row.append(cell);
    }
    table.append(row);
   }
   map.append(svg);
   setText("oaf-9m-visible",display.length+" máscaras filtradas en la vista. "+
     "Los sectores no presentes no cuentan con cobertura procesada en esta tesela.");
  }
  select.addEventListener("change",draw);draw();
 }catch(e){
  setText("oaf-9m-status","Análisis 9M pendiente de publicación o verificación: "+e.message+
   ". Los mapas 9K y 9L permanecen disponibles.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();