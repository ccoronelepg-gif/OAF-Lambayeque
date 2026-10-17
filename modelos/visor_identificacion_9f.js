/* OAF 9F | Nombres confirmados mediante máximos registrados por SENAMHI.
   Posiciones informativas con discrepancias históricas; no geocodificación precisa. */
(()=>{
"use strict";
const byId=id=>document.getElementById(id);
function fmt(n,nd=1){return typeof n==="number"&&Number.isFinite(n)?n.toLocaleString("es-PE",{maximumFractionDigits:nd,minimumFractionDigits:nd}):"—"}
function h(tag,text,cls){
 const e=document.createElement(tag);
 if(text!==undefined)e.textContent=text;
 if(cls)e.className=cls;
 return e;
}
const NS="http://www.w3.org/2000/svg";
const svg=(tag,attrs,text)=>{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs||{}))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e};
function mapPlot(data,chosen){
 const region=byId("oaf-9f-position");if(!region)return;
 region.replaceChildren();
 const img=svg("svg",{viewBox:"0 0 690 225",role:"img","aria-label":"Esquema norte-sur de las tres referencias cartográficas publicadas por SENAMHI; no representa el sitio exacto del sensor."});
 const lonMin=-80.1,lonMax=-79.1,latMin=-7.02,latMax=-5.4;
 const xx=lon=>65+(lon-lonMin)/(lonMax-lonMin)*560;
 const yy=lat=>24+(latMax-lat)/(latMax-latMin)*178;
 img.append(svg("rect",{x:47,y:13,width:608,height:190,rx:13,fill:"#f7fbfb",stroke:"#d8e8e6"}));
 for(const v of [0,1,2,3,4]){
  let yyGrid=22+v*44;
  img.append(svg("path",{d:"M 50 "+yyGrid+" H 650",stroke:"#dfeceb","stroke-dasharray":"4 6"}));
 }
 img.append(svg("text",{x:65,y:18,"font-size":11,fill:"#627d88"},"Norte"));
 img.append(svg("text",{x:65,y:198,"font-size":11,fill:"#627d88"},"Sur"));
 img.append(svg("text",{x:450,y:198,"font-size":11,fill:"#627d88"},"Este ↗"));
 data.estaciones.forEach((st,i)=>{
  const [lat,lon]=st.coordenadas_dereferencia;
  const px=xx(lon),py=yy(lat),selected=chosen===st.codigo_archivo;
  img.append(svg("circle",{cx:px,cy:py,r:selected?13:10,fill:selected?"#c97838":(i===0?"#117e98":"#34927b"),stroke:"#ffffff","stroke-width":3}));
  const label=i===1?-16:24;
  img.append(svg("text",{x:px+14,y:py+label+2,"font-size":12,"font-weight":selected?"800":"650",fill:"#184455"},st.nombre));
 });
 region.append(img);
}
function detail(data,st){
 const box=byId("oaf-9f-detail");box.replaceChildren();
 h("h3",st.nombre).append; // intentionally no effect, title added below
 box.append(h("h3",st.nombre));
 box.append(h("p",st.sector_referencia+". Código de archivo "+st.codigo_archivo+"; código documental "+st.codigo_catalogo+"."));
 const ext=h("p",undefined,"oaf-9f-extreme");
 ext.append(h("strong",fmt(st.dia_maximo_coincidente.lluvia_mm)+" mm"));
 ext.append(h("span"," · máximo diario coincidente con SENAMHI el "+st.dia_maximo_coincidente.fecha+"."));
 box.append(ext);
 const base=st.resumen_1998;
 box.append(h("p","Precipitación de 1998: "+fmt(base.lluvia_1998_mm)+" mm; media anual de referencia (1996–2013 sin 1997–1998): "+fmt(base.media_anual_base_exploratoria_mm)+" mm, calculada con "+base.anos_base_validos+" años completos. Relación descriptiva: "+fmt(base.factor_sobre_media_base,2)+" veces."));
 const track=h("div",undefined,"oaf-9f-compare");
 const left=h("div",undefined,"oaf-9f-bar");
 left.style.width="100%";
 track.append(left);
 box.append(track);
 box.append(h("p","Altitud publicada en boletín de extremos: "+st.altitud_de_referencia_m+" m; otros documentos registran "+st.altitudes_alternativas_publicadas_m.join(" y ")+" m. Estas cifras NO han sido conciliadas con la historia de emplazamientos."));
 box.append(h("p","Coordenadas de referencia del boletín: latitud "+fmt(st.coordenadas_dereferencia[0],5)+"°, longitud "+fmt(st.coordenadas_dereferencia[1],5)+"°. El esquema cartográfico usa esta referencia, no la posición instrumental acreditada."));
 const a=h("a","Consultar documento institucional ↗");a.href=st.fuente_cartografica;a.target="_blank";a.rel="noopener noreferrer";box.append(a);
 byId("oaf-9f-caption").textContent="Interpretación: el total de 1998 es observado, pero la media de comparación se calcula solo con "+base.anos_base_validos+
   " años completos del intervalo 1996–2013, excluyendo 1997 y 1998. Es una comparación exploratoria, NO una normal climática de 30 años ni evidencia de pronóstico.";
 mapPlot(data,st.codigo_archivo);
}
async function init(){
 if(!byId("oaf-stations-identified"))return;
 const r=await fetch("datos/validacion_estaciones_9f/identificacion_territorial_9f.json",{cache:"no-store"});
 if(!r.ok)throw Error("archivo territorial "+r.status);
 const data=await r.json();
 if(data.fase!=="9F"||data.estaciones?.length!==3||data.coordenadas_historicas_sin_incertidumbre!==false)throw Error("esquema incompatible");
 const sel=byId("oaf-9f-site");
 for(const st of data.estaciones){
  const op=document.createElement("option");op.value=st.codigo_archivo;op.textContent=st.nombre;sel.append(op);
 }
 sel.value="00152107";
 sel.addEventListener("change",()=>detail(data,data.estaciones.find(s=>s.codigo_archivo===sel.value)));
 detail(data,data.estaciones.find(s=>s.codigo_archivo===sel.value));
 byId("oaf-9f-status").textContent="Tres nombres confirmados mediante coincidencias exactas de fecha y precipitación. Emplazamientos históricos y altitudes aún requieren conciliación.";
}
const run=()=>init().catch(e=>{if(byId("oaf-9f-status"))byId("oaf-9f-status").textContent="No se pudo cargar la información territorial: "+e.message});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);
else run();
})();