/* OAF 9Q: pisos altitudinales exploratorios y CHIRPS 1996–2025. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const names={llanura_costa:"Costa baja 0–99 m",valle_bajo:"Valle 100–299 m",
piedemonte:"Piedemonte 300–799 m",montana_baja:"Ladera baja 800–1599 m",
montana_media:"Ladera media 1600–2499 m",montana_alta:"Alta montaña ≥2500 m",
cota_negativa_revisar:"Cota negativa DSM: revisar"};
const fmt=(n,d=1)=>typeof n==="number"&&Number.isFinite(n)?n.toLocaleString("es-PE",{maximumFractionDigits:d}):"Sin dato válido";
const set=(id,v)=>{const node=$(id);if(node)node.textContent=v;};
const get=async path=>{const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("Archivo no publicado: "+path);return r.json();};
const sv=(name,attrs,text)=>{const node=document.createElementNS("http://www.w3.org/2000/svg",name);for(const [k,v] of Object.entries(attrs||{}))node.setAttribute(k,String(v));if(text!==undefined)node.textContent=text;return node;};
const vars=[
 {key:"lluvia_anual_mediana_sectores_mm",name:"Lluvia mediana anual por sector (mm/año)"},
 {key:"temperatura_era5land_media_testigos_c",name:"Temperatura ERA5-Land (°C)"},
 {key:"humedad_era5_media_testigos_pct",name:"Humedad relativa ERA5 (%)"},
 {key:"radiacion_era5_media_testigos_mj_m2_dia_equiv",name:"Radiación de onda corta ERA5 (MJ/m² mensual)"}
];
function plot(data,key){
 const root=$("oaf-9q-graphic");root.replaceChildren();
 const rows=data.filter(f=>Number.isFinite(f[key]));
 if(!rows.length){root.textContent="Este indicador no tiene registros comparables.";return;}
 const W=820,H=Math.max(260,rows.length*39+54),L=197,R=108,T=15;
 const values=rows.map(f=>f[key]);const min=Math.min(0,...values),max=Math.max(...values,1);
 const ext=max-min||1,fw=W-L-R;
 const figure=sv("svg",{viewBox:"0 0 "+W+" "+H,role:"img","aria-label":vars.find(a=>a.key===key)?.name+" por piso altitudinal"});
 figure.style.width="100%";
 rows.forEach((row,i)=>{
  const yy=T+i*39,x=L+fw*((0-min)/ext),end=L+fw*((row[key]-min)/ext);
  figure.append(sv("text",{x:L-8,y:yy+22,"font-size":12,"text-anchor":"end",fill:"currentColor"},names[row.clase_piso]||row.clase_piso));
  const r=sv("rect",{x:Math.min(x,end),y:yy+5,width:Math.max(1,Math.abs(end-x)),height:22,rx:3,fill:i%2===0?"#277fa5":"#689e88"});
  r.append(sv("title",{},(names[row.clase_piso]||row.clase_piso)+": "+fmt(row[key],2)));figure.append(r);
  figure.append(sv("text",{x:Math.min(W-R+8,end+8),y:yy+22,"font-size":12,fill:"currentColor"},fmt(row[key],1)));
 });
 root.append(figure);
}
function cell(tr,value){const td=document.createElement("td");td.textContent=String(value);tr.append(td);}
async function init(){
 if(!$("oaf-9q-visor"))return;
 try{
  const b="datos/recuperacion_9q/";
  const [d,s,g]=await Promise.all([get(b+"diagnostico_pisos_y_agrupaciones_9q.json"),get(b+"fuentes_chirps_9q.json"),get(b+"agrupaciones_exploratorias_9q.geojson")]);
  if(d.fase!=="9Q"||s.fase!=="9Q"||d.meses_chirps_360!==s.n_meses_chirps_verificados||
     d.n_zonas_homogeneas_instrumentalmente_certificadas!==0||s.zonas_climaticas_homogeneas_certificadas!==0||
     d.habilidad_pronostico_exante_validada!==false||d.n_sectores!==42||g.features.length!==d.n_grupos_propuestos)
    throw Error("Inconsistencia entre las fuentes de datos");
  set("oaf-9q-months",s.n_meses_chirps_verificados+" / 360");
  set("oaf-9q-annual",d.n_anios_fuente_completos+" / 30");
  set("oaf-9q-groups",String(d.n_grupos_propuestos));
  set("oaf-9q-status",d.n_meses_faltantes===0?
   "CHIRPS v3 FINAL 1996–2025: 360 meses identificados por URL y SHA-256, serie descriptiva completa; no equivale a datos de estaciones independientes.":
   "CHIRPS v3: "+d.meses_chirps_360+" meses reales de 360. Faltan "+d.n_meses_faltantes+" sin imputar.");
  const selector=$("oaf-9q-plot-type");
  vars.forEach(item=>{const o=document.createElement("option");o.value=item.key;o.textContent=item.name;selector.append(o);});
  selector.value=vars[0].key;
  selector.addEventListener("change",()=>plot(d.comparacion_de_pisos,selector.value));
  plot(d.comparacion_de_pisos,selector.value);
  const tb=$("oaf-9q-floor-table");tb.replaceChildren();
  for(const floor of d.comparacion_de_pisos){
   const tr=document.createElement("tr");
   [names[floor.clase_piso]||floor.etiqueta,floor.n_sectores,floor.sectores_con_lluvia_valida,
    fmt(floor.lluvia_anual_mediana_sectores_mm),fmt(floor.temperatura_era5land_media_testigos_c),
    fmt(floor.humedad_era5_media_testigos_pct)].forEach(x=>cell(tr,x));
   tb.append(tr);
  }
  const tbody=$("oaf-9q-group-table");tbody.replaceChildren();
  if(!g.features.length){
   const tr=document.createElement("tr"),td=document.createElement("td");td.colSpan=4;
   td.textContent="Ninguna pareja cumplió simultáneamente todos los filtros. Los sectores permanecen separados hasta contar con mejor evidencia.";tr.append(td);tbody.append(tr);
  }
  for(const feature of g.features){
   const p=feature.properties,tr=document.createElement("tr");
   [p.id,names[p.piso]||p.piso,p.sectores.join(", "),"Hipótesis, no validada"].forEach(x=>cell(tr,x));tbody.append(tr);
  }
  const mapBox=$("oaf-9q-map");mapBox.replaceChildren();
  if(g.features.length){
   const polys=geom=>geom.type==="Polygon"?[geom.coordinates]:geom.type==="MultiPolygon"?geom.coordinates:[];
   const points=g.features.flatMap(f=>polys(f.geometry).flatMap(p=>p.flatMap(ring=>ring)));
   const lons=points.map(p=>p[0]),lats=points.map(p=>p[1]);
   const left=Math.min(...lons),right=Math.max(...lons),
         bottom=Math.min(...lats),top=Math.max(...lats);
   const W=850,H=500,pad=23,dx=Math.max(.01,right-left),dy=Math.max(.01,top-bottom);
   const proj={x:lon=>pad+(lon-left)/dx*(W-2*pad),
               y:lat=>H-pad-(lat-bottom)/dy*(H-2*pad)};
   const fig=sv("svg",{viewBox:"0 0 "+W+" "+H,role:"img",
      "aria-label":"Polígonos hidroclimáticos de agrupaciones no certificadas"});
   fig.style.width="100%";
   const colors={montana_alta:"#765f9e",montana_media:"#967ac0",
     piedemonte:"#be9946",valle_bajo:"#53a080",llanura_costa:"#378baf"};
   for(const feature of g.features){
     const p=feature.properties;
     const dpath=polys(feature.geometry).map(poly=>poly.map(ring=>
       ring.map((point,i)=>(i?"L":"M")+proj.x(point[0]).toFixed(2)+","+
                         proj.y(point[1]).toFixed(2)).join(" ")+"Z").join(" ")).join(" ");
     const f=sv("path",{d:dpath,fill:colors[p.piso]||"#759b8b",
        stroke:"#f5f9f8","stroke-width":1.5,"fill-opacity":.85,
        tabindex:0,role:"button"});
     const tip=p.id+" · "+(names[p.piso]||p.piso)+" · "+p.sectores.join(", ")+
       " · Propuesta exploratoria, no certificada";
     f.append(sv("title",{},tip));
     const select=()=>set("oaf-9q-map-detail",tip);
     f.addEventListener("click",select);
     f.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();select();}});
     fig.append(f);
   }
   mapBox.append(fig);
  }else{mapBox.textContent="No se publicaron grupos: ninguno satisfizo todos los filtros científicos.";}
  set("oaf-9q-science",d.n_pares_mismo_piso_cuenca_cercanos_evaluados+
   " pares próximos con piso y unidad hidrográfica común examinados; "+
   d.n_pares_lluvia_y_testigos_multivariable_satisfacen_criterios+
   " superaron los filtros de semejanza de lluvia, temperatura, humedad y radiación sin reutilizar el mismo píxel CHIRPS. "+
   "Los grupos NO son pisos ecológicos oficiales ni zonas homogéneas certificadas.");
 }catch(e){set("oaf-9q-status","Resultados 9Q pendientes de publicación o verificación: "+e.message+". Los paneles 9O–9P permanecen disponibles.");}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();