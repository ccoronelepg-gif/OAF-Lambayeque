/* OAF 8N · malla regional DEM y ESTRATOS ALTITUDINALES NO validados como
   zonas homogéneas agroclimáticas. No publicar habilidad predictiva. */
(()=>{
"use strict";
const panel=document.getElementById("oaf-zones-8n");if(!panel)return;
const el=id=>document.getElementById(id);
const status=el("oaf-8n-status"),canvas=el("oaf-8n-map"),tbody=el("oaf-8n-table");
const filter=el("oaf-8n-filter"),legend=el("oaf-8n-legend");
const classes=[
 ["planicie_muy_baja","Planicie muy baja (< 100 m)","#237fbe"],
 ["planicie_valle_interior","Planicie y valle bajo (100–299 m)","#38a39d"],
 ["piedemonte","Piedemonte (300–799 m)","#d4a34f"],
 ["ladera_baja","Ladera baja (800–1599 m)","#ca7c47"],
 ["ladera_media","Ladera media (1600–2499 m)","#9878b6"],
 ["zona_alta_andina","Zonas altas (≥ 2500 m)","#684b88"],
 ["cota_negativa_dem_verificar","Cota DEM negativa (verificar)","#727f88"]
];
const byId=new Map(classes.map(x=>[x[0],x]));
let records=[],stats=null,shape=null;
const n=v=>Number.isFinite(v)?Number(v).toLocaleString("es-PE",{maximumFractionDigits:0}):"—";
const svg=(tag,attrs,text)=>{
 const node=document.createElementNS("http://www.w3.org/2000/svg",tag);
 for(const [k,v] of Object.entries(attrs||{}))node.setAttribute(k,String(v));
 if(text!==undefined)node.textContent=text;
 return node;
};
const pointInRecords=()=>records.filter(r=>filter.value==="all"||r.estrato_altitudinal_preliminar===filter.value);
function render(){
 if(!shape||!stats)return;
 canvas.replaceChildren();tbody.replaceChildren();legend.replaceChildren();
 for(const [name,label,color] of classes){
   const item=document.createElement("span");
   item.style.cssText="display:inline-flex;align-items:center;gap:6px;font-size:12px;margin:4px 10px 4px 0";
   const marker=document.createElement("span");
   marker.style.cssText="display:inline-block;width:12px;height:12px;background:"+color+";border-radius:4px";
   item.append(marker,document.createTextNode(label));legend.append(item);
   const values=stats.estratos[name];
   if(!values)continue;
   const tr=document.createElement("tr");
   for(const val of [label,values.n_puntos_dem,n(values.alt_min_m),n(values.alt_max_m),"No validada"]){
     const td=document.createElement("td");td.textContent=String(val);tr.append(td);
   }
   tbody.append(tr);
 }
 const coords=shape.features?.[0]?.geometry?.coordinates;
 if(!Array.isArray(coords))return;
 const paths=shape.features[0].geometry.type==="Polygon"?[coords]:coords;
 const exterior=paths.flatMap(g=>g[0]);
 const lons=exterior.map(x=>x[0]),lats=exterior.map(x=>x[1]);
 const x0=Math.min(...lons),x1=Math.max(...lons),y0=Math.min(...lats),y1=Math.max(...lats);
 const W=770,H=465,pad=26;
 const x=lon=>pad+(lon-x0)/(x1-x0)*(W-2*pad);
 const y=lat=>H-pad-(lat-y0)/(y1-y0)*(H-2*pad);
 const view=svg("svg",{viewBox:"0 0 770 465",role:"img",
   "aria-label":"Mapa preliminar de puntos altitudinales de Lambayeque; no es zonificación climática validada"});
 view.style.cssText="display:block;width:100%;height:auto;max-height:540px";
 paths.forEach(poly=>{
   const d=poly.map((ring,i)=>ring.map((pt,j)=>(j?"L":"M")+x(pt[0]).toFixed(2)+" "+y(pt[1]).toFixed(2)).join(" ")+" Z").join(" ");
   view.append(svg("path",{d,fill:"#e9f2ed",stroke:"#557985","stroke-width":1.6,"fill-rule":"evenodd"}));
 });
 for(const r of pointInRecords()){
   const item=byId.get(r.estrato_altitudinal_preliminar);
   if(!item)continue;
   const circle=svg("circle",{cx:x(r.longitud),cy:y(r.latitud),r:5,fill:item[2],
     stroke:"#fff","stroke-width":1.2});
   circle.append(svg("title",{},r.id+" · DEM "+n(r.altitud_dem_m)+" m · "+
     item[1]+", no validado climáticamente"));
   view.append(circle);
 }
 const sites=[["Chiclayo",-6.7714,-79.8409],["Jayanca",-6.39278,-79.8228],
              ["Motupe",-6.15083,-79.7142],["Olmos",-5.98825,-79.74723]];
 for(const [name,lat,lon] of sites){
   const cx=x(lon),cy=y(lat);
   const ring=svg("circle",{cx,cy,r:8,fill:"none",stroke:"#273d45","stroke-width":1.5,
                            "stroke-dasharray":"2,2"});
   ring.append(svg("title",{},name+" · punto de referencia histórico 8M, NO sensor"));
   view.append(ring);
 }
 canvas.append(view);
 const note=document.createElement("p");note.className="small";
 note.textContent="Puntos coloreados: elevaciones estimadas de un DEM. Círculos discontinuos: los cuatro puntos históricos de referencia 8M (no estaciones meteorológicas). La malla es una muestra de centros, no un mapa continuo ni parcelas con clasificación confirmada.";
 canvas.append(note);
}
async function load(){
 status.textContent="Cargando límite regional referencial y elevaciones DEM trazables…";
 try{
  const paths=["datos/zonificacion_8n/estado_8n.json",
               "datos/zonificacion_8n/nodos_altitudinales_8n.csv",
               "datos/zonificacion_8n/limite_lambayeque_referencial.geojson"];
  const resp=await Promise.all(paths.map(p=>fetch(p,{cache:"no-store"})));
  if(resp.some(r=>!r.ok))throw Error("La fuente geográfica o DEM no se encuentra publicada");
  const [report,csv,geometry]=await Promise.all([resp[0].json(),resp[1].text(),resp[2].json()]);
  const lines=csv.trim().split(/\r?\n/),columns=lines.shift().split(",");
  if(report.fase!=="8N"||report.homogeneidad_climatica_estadistica_demostrada!==false||
    report.pronosticos_8e_recalibrados!==false||report.validacion_instrumental_SENAMHI!==false||
    report.zonas_operativas_aprobadas!==0||report.nodos_en_malla_regional_referencial<30||
    !["id","latitud","longitud","altitud_dem_m","estrato_altitudinal_preliminar"].every(k=>columns.includes(k)))
    throw Error("El estado regional no satisface la garantía metodológica");
  const parsed=[];
  for(const line of lines){
    if(!line.trim())continue;
    const parts=line.split(",");
    if(parts.length!==columns.length)throw Error("Fila DEM dañada");
    const item=Object.fromEntries(columns.map((k,i)=>[k,parts[i]]));
    for(const key of ["latitud","longitud","altitud_dem_m"]){
      item[key]=Number(item[key]);if(!Number.isFinite(item[key]))throw Error("Altitud/coordenada inválida");
    }
    if(!byId.has(item.estrato_altitudinal_preliminar)||
       item.clima_homogeneo_validado!=="false")
      throw Error("Estrato sin tipología documentada");
    parsed.push(item);
  }
  if(parsed.length!==report.nodos_con_elevacion_dem_verificada)throw Error("Conteos DEM inconsistentes");
  if(report.cobertura_puntual_completa&&parsed.length!==report.nodos_en_malla_regional_referencial)
    throw Error("Se declara cobertura sin todos los puntos");
  if(geometry.features?.[0]?.properties?.codigo_ubigeo!=="14")
    throw Error("Límite geográfico no pertenece a Lambayeque");
  records=parsed;stats=report;shape=geometry;
  el("oaf-8n-nodes").textContent=String(report.nodos_en_malla_regional_referencial);
  el("oaf-8n-elevated").textContent=String(report.nodos_con_elevacion_dem_verificada);
  el("oaf-8n-certified").textContent=String(report.zonas_operativas_aprobadas);
  render();
  status.textContent=report.cobertura_puntual_completa
   ?"Malla regional DEM completa: "+parsed.length+" puntos. Estratos físicos preliminares; cero zonas climáticas homogéneas validadas. Límite secundario simplificado, pendiente de contraste con INEI/IGN."
   :"Cobertura DEM parcial ("+parsed.length+"/"+report.nodos_en_malla_regional_referencial+"). Sin clasificaciones operativas regionales.";
 }catch(e){
  records=[];stats=null;shape=null;canvas.replaceChildren();tbody.replaceChildren();
  status.textContent="No se pudo comprobar la zonificación preliminar: "+e.message+". No se generan altitudes ficticias.";
 }
}
filter.addEventListener("change",render);
el("oaf-8n-refresh")?.addEventListener("click",load);
let started=false;
panel.addEventListener("toggle",()=>{if(panel.open&&!started){started=true;load()}});
})();
