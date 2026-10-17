/* OAF-Lambayeque | Arquitectura pública, octubre 2026.
   No fabrica datos. Estado de las fuentes desde JSON auditados y mapa desde DEM real. */
(()=>{
"use strict";
const byId=id=>document.getElementById(id);
const assign=(id,value)=>{const x=byId(id);if(x)x.textContent=String(value)};
async function json(path){
 const response=await fetch(path,{cache:"no-store"});
 if(!response.ok)throw Error(path+" HTTP "+response.status);
 return response.json();
}
async function news(){
 const sources=[
  ["datos/estado_monitoreo_3z.json",data=>{
    const month=data.ultimo_mes_disponible;
    assign("oaf-news-chirps",month?"Último mes: "+month:"Sin mes validado");
    assign("oaf-news-chirps-detail",
     (data.meses_con_raster_verificado??"—")+" meses con raster comprobado; consulta "+
     (data.fecha_ejecucion_utc||"sin fecha")+
     ". Estimación CHIRPS, no estación ni lluvia actual.");
  },"oaf-news-chirps","oaf-news-chirps-detail"],
  ["datos/estado_enfen_3z.json",data=>{
   const valid=data.verificacion==="verificada"&&data.fecha_emision&&data.estado_institucional&&/^https:\/\//.test(data.url_comunicado||"");
   assign("oaf-news-enfen",valid?"Verificado: "+data.estado_institucional:"Estado oficial por confirmar");
   assign("oaf-news-enfen-detail",valid?
     "Boletín "+(data.numero??"")+" emitido "+data.fecha_emision+
     ". Consulte fuente ENFEN para cambios.":
     "La última consulta automatizada no confirmó un estado oficial. Revise comunicados ENFEN; el OAF no emite alertas.");
  },"oaf-news-enfen","oaf-news-enfen-detail"],
  ["datos/aire_8x/estado_aire_8x.json",data=>{
    assign("oaf-news-air",(data.filas_mes_sitio??"—")+" registros mes–localidad");
    assign("oaf-news-air-detail",data.periodo_piloto_predefinido+
      " · CAMS modelado; "+(data.n_pares_sitio_series_pm_identicas??0)+
      " pares de series idénticas. No certifica calidad ECA.");
  },"oaf-news-air","oaf-news-air-detail"],
  ["datos/benchmark_9a/estado_benchmark_9a.json",data=>{
   assign("oaf-news-model",(data.fechas_ensayo||[]).length+" cortes de validación");
   assign("oaf-news-model-detail","Comparación de "+Number(data.n_predicciones_continuas||0).toLocaleString("es-PE")+
    " predicciones retrospectivas, NO alertas operativas ni verificación instrumental.");
  },"oaf-news-model","oaf-news-model-detail"]
 ];
 await Promise.all(sources.map(async ([url,render,label,detail])=>{
    try{render(await json(url));}
    catch(error){assign(label,"No disponible");assign(detail,"No se pudo verificar la fuente; no se muestran datos simulados.");}
 }));
 assign("oaf-news-updated","Fuente y periodo indicados en cada tarjeta. Para información institucional vigente, consulte los enlaces oficiales. Un archivo procesado no implica condiciones actuales.");
}
const bands=[
 {min:0,max:99,hex:"#51aa9b"},
 {min:100,max:299,hex:"#84bc70"},
 {min:300,max:799,hex:"#dfbd64"},
 {min:800,max:1599,hex:"#de9458"},
 {min:1600,max:2499,hex:"#bd727a"},
 {min:2500,max:Infinity,hex:"#8a71b0"}
];
const svgNS="http://www.w3.org/2000/svg";
function svg(tag,attrs,textValue){
 const element=document.createElementNS(svgNS,tag);
 for(const [key,value] of Object.entries(attrs||{}))element.setAttribute(key,String(value));
 if(textValue!==undefined)element.textContent=String(textValue);
 return element;
}
function csv(text){
 const [header,...rest]=text.trim().split(/\r?\n/);
 const fields=header.replace(/^\uFEFF/,"").split(",");
 return rest.map(line=>Object.fromEntries(
  line.split(",").map((value,index)=>[fields[index],value])
 ));
}
function polygonPoints(geo){
 if(!geo||geo.type!=="FeatureCollection")throw Error("Polígono referencial no disponible");
 const polygon=geo.features?.find(f=>f.geometry?.type==="Polygon");
 if(!polygon)return [];
 const ring=polygon.geometry.coordinates?.[0]||[];
 return ring.filter(p=>Array.isArray(p)&&p.length>=2&&p.every(Number.isFinite));
}
async function map(){
 const plot=byId("oaf-altitudinal-map"),sel=byId("oaf-map-level");
 if(!plot||!sel)return;
 try{
  const [r,g]=await Promise.all([
   fetch("datos/muestreo_8o/nodos_dem_8o.csv",{cache:"no-store"}),
   json("datos/zonificacion_8n/limite_lambayeque_referencial.geojson")
  ]);
  if(!r.ok)throw Error("CSV DEM no disponible");
  const pts=csv(await r.text()).map(p=>({
   id:p.id,lat:Number(p.latitud),lon:Number(p.longitud),alt:Number(p.altitud_dem_m),
   official:p.homogeneidad_validada==="true"
  }));
  if(pts.length!==420||pts.some(p=>![p.lat,p.lon,p.alt].every(Number.isFinite))){
   throw Error("Los 420 puntos DEM no coinciden con el inventario");
  }
  const ring=polygonPoints(g);
  const all=[[...ring],pts.map(p=>[p.lon,p.lat])].flat();
  const longitude=all.map(p=>p[0]),latitude=all.map(p=>p[1]);
  const minX=Math.min(...longitude),maxX=Math.max(...longitude);
  const minY=Math.min(...latitude),maxY=Math.max(...latitude);
  // Proyección local equirectangular: escala compartida, corrige longitud por cos(lat).
  const midLon=(minX+maxX)/2,midLat=(minY+maxY)/2;
  const lonFactor=Math.cos(midLat*Math.PI/180);
  const scale=Math.min(622/Math.max(.01,(maxX-minX)*lonFactor),388/Math.max(.01,maxY-minY));
  const sx=x=>360+(x-midLon)*lonFactor*scale;
  const sy=y=>235-(y-midLat)*scale;
  const draw=()=>{
   const filter=sel.value;
   plot.replaceChildren();
   plot.append(svg("rect",{x:15,y:15,width:690,height:440,rx:16,fill:"#eaf3ef"}));
   if(ring.length>2){
    plot.append(svg("polygon",{points:ring.map(([x,y])=>sx(x).toFixed(2)+","+sy(y).toFixed(2)).join(" "),
       fill:"#d3e9dc","fill-opacity":.60,stroke:"#477b69","stroke-width":2,
       "stroke-dasharray":"6 4"}));
   }
   const selected=pts.filter(p=>{
     const band=bands.find(x=>p.alt>=x.min&&p.alt<=x.max);
     return filter==="all"||(band&&String(band.min)===filter);
   });
   pts.forEach(p=>{
      const band=bands.find(b=>p.alt>=b.min&&p.alt<=b.max);
      const included=selected.includes(p);
      const mark=svg("circle",{
        cx:sx(p.lon),cy:sy(p.lat),r:included?3.5:2,
        fill:band?.hex||"#8b8f91",opacity:included?.92:.08,
        stroke:included?"#fff":"none","stroke-width":included?.65:0
      });
      if(included)mark.append(svg("title",{},p.id+": "+p.alt+" m (DEM)"));
      plot.append(mark);
   });
   for(const [name,lat,lon] of [
    ["Chiclayo",-6.7714,-79.8409],["Jayanca",-6.39278,-79.8228],
    ["Motupe",-6.15083,-79.7142],["Olmos",-5.98825,-79.74723]
   ]){
     const x=sx(lon),y=sy(lat);
     plot.append(svg("circle",{cx:x,cy:y,r:5,fill:"#193b45",stroke:"#fff","stroke-width":2}));
     plot.append(svg("text",{x:x+8,y:y-7,"font-size":12,fill:"#193b45","font-weight":700},name));
   }
   plot.append(svg("text",{x:34,y:36,"font-size":11,fill:"#45676d"},"Límite aproximado · DEM auditado"));
   const counts=selected.length;
   assign("oaf-map-stats",counts+" puntos DEM mostrados de "+pts.length+
     ". Fuente: muestreo 8O; contorno secundario referencial, no oficial.");
  };
  sel.addEventListener("change",draw);
  draw();
 }catch(err){
   plot.replaceChildren();
   plot.append(svg("text",{x:30,y:90,fill:"#6d4a4a","font-size":18},"Mapa no disponible: datos sin verificar"));
   assign("oaf-map-stats","Error al revisar el inventario DEM. No se generan puntos ficticios.");
 }
}
function init(){
 news();
 map();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();
