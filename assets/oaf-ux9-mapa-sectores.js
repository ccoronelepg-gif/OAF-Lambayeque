(function map9(){
"use strict";
const $=id=>document.getElementById(id),N="http://www.w3.org/2000/svg";
const palette=[
["cota_negativa_revisar","DEM bajo cero · revisión","#748391"],
["llanura_costa","Costa 0–99 m","#3a90d0"],
["valle_bajo","Valle 100–299 m","#55b6b0"],
["piedemonte","Piedemonte 300–799 m","#86b867"],
["montana_baja","Laderas 800–1599 m","#dbb251"],
["montana_media","Montaña 1600–2499 m","#d57f67"],
["montana_alta","Alturas ≥2500 m","#9579cc"]
];
function svg(tag,props,content){const e=document.createElementNS(N,tag);for(const [k,v] of Object.entries(props||{}))e.setAttribute(k,String(v));if(content!==undefined)e.textContent=content;return e}
function coordsOf(f){const g=f.geometry;if(!g)return[];const polys=g.type==="Polygon"?[g.coordinates]:g.type==="MultiPolygon"?g.coordinates:[];return polys.flatMap(p=>p.flatMap(r=>r))}
function points(f,xy){const g=f.geometry,polys=g.type==="Polygon"?[g.coordinates]:g.coordinates;
return polys.map(poly=>poly.map(ring=>ring.map((p,i)=>`${i===0?"M":"L"}${xy.x(p[0]).toFixed(2)} ${xy.y(p[1]).toFixed(2)}`).join(" ")+"Z").join(" ")).join(" ")}
async function init(){
 const slot=$("oaf-ux9-map"),select=$("oaf-ux9-floor"),legend=$("oaf-ux9-map-legend"),summary=$("oaf-ux9-map-count"),detail=$("oaf-ux9-map-detail");
 if(!slot||!select||!legend||!summary||!detail)return;
 try{
  const response=await fetch("datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson",{cache:"no-store"});
  if(!response.ok)throw Error("Geometrías no disponibles: HTTP "+response.status);
  const data=await response.json();
  if(!Array.isArray(data.features)||data.features.length!==42||data.metadata?.son_zonas_homogeneas_validadas!==false)throw Error("Inconsistencia en la auditoría de 42 geometrías de influencia");
  const xs=data.features.flatMap(coordsOf),lon=xs.map(x=>x[0]),lat=xs.map(x=>x[1]);
  const W=850,H=520,pad=23,xmin=Math.min(...lon),xmax=Math.max(...lon),ymin=Math.min(...lat),ymax=Math.max(...lat),sx=(W-2*pad)/(xmax-xmin),sy=(H-2*pad)/(ymax-ymin),scale=Math.min(sx,sy);
  const x0=(W-(xmax-xmin)*scale)/2,y0=(H-(ymax-ymin)*scale)/2;
  const xy={x:z=>x0+(z-xmin)*scale,y:z=>H-y0-(z-ymin)*scale};
  const names=Object.fromEntries(palette.map(p=>[p[0],p[1]]));
  const colors=Object.fromEntries(palette.map(p=>[p[0],p[2]]));
  for(const [key,label] of palette){const opt=document.createElement("option");opt.value=key;opt.textContent=label;select.append(opt);
   const item=document.createElement("span"),chip=document.createElement("i");chip.style.background=colors[key];item.append(chip,document.createTextNode(label));legend.append(item);}
  const view=p=>{const q=p.properties;detail.textContent=`${q.id_sector} · ${names[q.estrato]||q.estrato}. Altitud en los nodos DEM de este sector: ${Math.round(q.alt_min_nodos_m)} a ${Math.round(q.alt_max_nodos_m)} m. ${q.n_nodos_dem} nodos analizados y ${q.n_testigos_perfil_30anios} testigos climáticos de referencia. Son polígonos de influencia del muestreo, no parcelas ni áreas agrícolas certificadas.`;};
  const draw=()=>{
    const root=svg("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":"Mapa por franjas de elevación de 42 sectores exploratorios en Lambayeque"});root.append(svg("rect",{width:W,height:H,fill:"#e4f2e8",rx:10}));
    const defs=svg("defs"),pattern=svg("pattern",{id:"oaf-ux9-topo-pattern",width:27,height:27,patternUnits:"userSpaceOnUse"});pattern.append(svg("circle",{cx:2,cy:2,r:1,fill:"#9cbeb0"}));defs.append(pattern);root.append(defs);
    root.append(svg("rect",{x:0,y:0,width:W,height:H,fill:"url(#oaf-ux9-topo-pattern)",opacity:.25}));
    let shown=0;
    for(const f of data.features){const q=f.properties;if(select.value!=="todos"&&select.value!==q.estrato)continue;const path=svg("path",{d:points(f,xy),fill:colors[q.estrato]||"#7f9694",stroke:"#f8fff9","stroke-width":1.2,"fill-opacity":".88",tabindex:0,role:"button","aria-label":`${q.id_sector}, ${names[q.estrato]||q.estrato}`});path.append(svg("title",{},`${q.id_sector} · ${names[q.estrato]||q.estrato} · ${q.n_nodos_dem} puntos DEM`));path.addEventListener("click",()=>view(f));path.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();view(f)}});root.append(path);shown++;}
    root.append(svg("text",{x:24,y:37,fill:"#25584b","font-size":15,"font-weight":800},"Lambayeque · cartografía del relieve"));
    summary.textContent=`${shown} de ${data.features.length} sectores exploratorios visibles. Selecciona un color o toca un polígono para conocer el piso y su evidencia.`;
    slot.replaceChildren(root);
  };
  select.addEventListener("change",draw);draw();
 }catch(e){slot.textContent="No se ha podido dibujar el mapa auditado: "+e.message;summary.textContent="La cartografía histórica sigue disponible en Metadatos y trazabilidad."}
}
document.addEventListener("oaf:ux9-ready",init);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
