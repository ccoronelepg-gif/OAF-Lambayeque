/* OAF 9L: DEM continuo y máscara altitudinal limitada a 3 familias; sin alertas. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const NS="http://www.w3.org/2000/svg";
const mk=(t,attrs,txt)=>{const el=document.createElementNS(NS,t);
 for(const [k,v] of Object.entries(attrs||{}))el.setAttribute(k,String(v));
 if(txt!==undefined)el.textContent=txt;return el;};
const COLORS={C01:"#c7a14a",C02:"#5d4a94",C03:"#9677ae"};
function polypath(geom,project){
 if(!geom)return "";
 const polys=geom.type==="Polygon"?[geom.coordinates]:geom.coordinates;
 return polys.map(poly=>poly.map(ring=>
   ring.map((pt,i)=>(i?"L":"M")+project.x(pt[0]).toFixed(1)+","+
                               project.y(pt[1]).toFixed(1)).join(" ")+"Z"
  ).join(" ")).join(" ");
}
function describe(v){
 if(v===null||v===undefined)return"sin datos";
 return Number(v).toLocaleString("es-PE",{maximumFractionDigits:1});
}
async function run(){
 if(!$("oaf-9l-visor"))return;
 const status=$("oaf-9l-state"),map=$("oaf-9l-map"),list=$("oaf-9l-list");
 try{
  const paths=["datos/relieve_9l/nucleos_restringidos_relieve_9l.geojson",
               "datos/relieve_9l/estado_relieve_9l.json"];
  const res=await Promise.all(paths.map(x=>fetch(x,{cache:"no-store"})));
  if(res.some(r=>!r.ok))throw Error("fuentes 9L aún no publicadas");
  const [geo,meta]=await Promise.all(res.map(r=>r.json()));
  if(meta.fase!=="9L"||meta.zonas_homogeneas_instrumentales_certificadas!==0||
     meta.comparacion_nmme.prediccion_por_sector_generada!==false||
     meta.n_familias!==3||geo.features.length!==5)
     throw Error("metadatos científicos 9L no conformes");
  status.textContent="Copernicus GLO-90: "+meta.n_sectores_9k_auditados+
   " núcleos geométricos de "+meta.n_familias+
   " familias evaluados. Muestra raster agregada a ~270 m para el análisis.";
  const all=geo.features.filter(f=>f.geometry);
  const points=all.flatMap(f=>f.geometry.type==="Polygon"?
     f.geometry.coordinates.flat(1):f.geometry.coordinates.flat(2));
  const minX=Math.min(...points.map(p=>p[0])),maxX=Math.max(...points.map(p=>p[0]));
  const minY=Math.min(...points.map(p=>p[1])),maxY=Math.max(...points.map(p=>p[1]));
  const W=900,H=525,pad=18,spanX=Math.max(maxX-minX,.01),spanY=Math.max(maxY-minY,.01);
  const p={x:lon=>pad+(lon-minX)/spanX*(W-2*pad),
           y:lat=>H-pad-(lat-minY)/spanY*(H-2*pad)};
  const svg=mk("svg",{viewBox:"0 0 900 525",role:"img",
   "aria-label":"Mapa de cinco núcleos de muestra recortados a franjas de elevación DEM y pendiente; no son áreas homogéneas certificadas."});
  svg.style.cssText="display:block;width:100%;max-height:540px";
  list.replaceChildren();
  for(const f of geo.features){
    const a=f.properties;
    const tr=document.createElement("tr");
    for(const value of [a.sector_9k,a.familia,
       describe(a.altitud_cog_p50_m)+" m",
       describe(a.pendiente_cog_p90_grados)+"°",
       (100*a.fraccion_compatible_en_muestra_raster).toFixed(1)+" %"]){
      const td=document.createElement("td");td.textContent=String(value);tr.append(td);
    }
    list.append(tr);
    if(!f.geometry)continue;
    const item=mk("path",{d:polypath(f.geometry,p),fill:COLORS[a.familia]||"#787878",
     stroke:"#f2f9f5","stroke-width":0.9, "fill-opacity":0.84});
    item.append(mk("title",{},a.sector_9k+" · "+a.familia+" · DEM mediana "+
       describe(a.altitud_cog_p50_m)+" m; "+(100*a.fraccion_compatible_en_muestra_raster).toFixed(1)+
       " % de píxeles compatibles con clase y pendiente. No validado."));
    svg.append(item);
  }
  map.replaceChildren(svg);
  try{
    const r=await fetch("datos/relieve_9l/consulta_unidades_hidrograficas_9l.json",{cache:"no-store"});
    if(!r.ok)throw Error("sin archivo público de unidades");
    const hydro=await r.json();
    if(hydro.fase!=="9L")throw Error("procedencia incompatible");
    $("oaf-9l-cuencas").textContent=hydro.n_intersecciones_sector_unidad_referencial>0?
      "Cartografía hidrográfica referencial: "+hydro.n_intersecciones_sector_unidad_referencial+
      " cruces preliminares; ningún límite certificado por ANA y ninguna predicción por cuenca validada.":
      "Consulta hidrográfica institucional: no fue posible confirmar unidades para los sectores. "+
      "Se conservan sin asignación de cuenca; consulta registrada: "+
      (hydro.mensaje_error||"no hay polígonos encontrados")+".";
  }catch(e){
    $("oaf-9l-cuencas").textContent="Consulta de cuencas no disponible: "+e.message+
     ". No se asignaron cuencas por inferencia.";
  }
  $("oaf-9l-conclusion").textContent=
    "Solo se evaluaron "+meta.n_sectores_9k_auditados+
    " fragmentos de las familias C01, C02 y C03. El porcentaje describe la máscara raster "+
    "dentro del polígono previo, NO el porcentaje agrícola o climático regional. "+
    "Se comprobaron 0 cuencas oficiales y 0 zonas de homogeneidad instrumental. "+
    "NOAA NMME sigue con dos celdas gruesas; no existe corrección estadística altitudinal validada.";
 }catch(err){
  status.textContent="Mapa 9L pendiente: "+err.message+
   ". Se conserva visible la zonificación preliminar 9K.";
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);
else run();
})();