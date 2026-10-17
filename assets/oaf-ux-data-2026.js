/* OAF UX · resúmenes científicamente prudentes y pronósticos externos.
 * Solo datos reales de Open-Meteo / archivos auditable del repositorio.
 * No inventa probabilidades fitosanitarias, alertas ENFEN o anomalías locales. */
(()=>{
"use strict";
const g=id=>document.getElementById(id);
const coords={
 "Chiclayo":[-6.7714,-79.8409],"Jayanca":[-6.39278,-79.8228],
 "Motupe":[-6.15083,-79.7142],"Olmos":[-5.98825,-79.74723]
};
const series=[
 {key:"temperature_2m_max",id:"temp",label:"Temperatura máxima",unit:"°C",type:"line",meaning:"Temperatura máxima diaria estimada a 2 m. No describe directamente la temperatura del dosel."},
 {key:"precipitation_sum",id:"rain",label:"Precipitación diaria",unit:"mm",type:"bar",meaning:"Acumulado diario de lluvia pronosticada; no es lluvia medida por pluviómetro."},
 {key:"relative_humidity_2m_mean",id:"humidity",label:"Humedad relativa media",unit:"%",type:"line",meaning:"Humedad media del aire a 2 m. No demuestra que las hojas estén mojadas."},
 {key:"shortwave_radiation_sum",id:"radiation",label:"Radiación solar global",unit:"MJ/m²",type:"bar",meaning:"Suma diaria de radiación de onda corta. No equivale a radiación UV."}
];
let seq=0;
const fmt=(v,d=1)=>Number.isFinite(v)?v.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
const S="http://www.w3.org/2000/svg";
const el=(tag,attrs,text)=>{
 const n=document.createElementNS(S,tag);
 Object.entries(attrs||{}).forEach(([k,v])=>n.setAttribute(k,String(v)));
 if(text!==undefined)n.textContent=String(text);
 return n;
};
const get=async path=>{const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);return r.json()};
const set=(id,val)=>{const n=g(id);if(n)n.textContent=val};
function updateMap(city,model){
 if(!coords[city])return;
 const [lat,lon]=coords[city];
 const d=(n)=>fmt(n,3);
 const temp=model&&Number.isFinite(model.temperature_2m)?fmt(model.temperature_2m)+" °C (modelo externo)":"sin valor meteorológico confirmado";
 set("oaf-map-focus","Localidad: "+city+" · coordenadas de referencia urbana "+d(lat)+", "+d(lon)+" · temperatura "+temp+
    ". El mapa utiliza puntos DEM; franjas exploratorias, no zonificación agroclimática oficial.");
}
function renderChart(slot,dates,vals,entry,city,consulted){
 slot.replaceChildren();
 const W=540,H=225,L=45,R=20,T=19,B=41,iw=W-L-R,ih=H-T-B;
 const ymin=entry.type==="bar"?0:Math.min(...vals),ymax0=Math.max(...vals);
 const diff=Math.max(0.01,ymax0-ymin),pad=entry.type==="line"?Math.max(.35,diff*.17):Math.max(.4,ymax0*.12);
 const lo=entry.type==="line"?ymin-pad:0,hi=ymax0+pad,span=hi-lo||1;
 const x=i=>L+(i+.5)*iw/7,y=v=>T+ih-(v-lo)/span*ih;
 const svg=el("svg",{viewBox:"0 0 "+W+" "+H,role:"img",
   "aria-label":entry.label+" del "+dates[0]+" al "+dates[6]+" en "+city+". Modelo Open-Meteo.",
   preserveAspectRatio:"xMidYMid meet"
 });
 for(let k=0;k<4;k++){
  const val=lo+(hi-lo)*k/3,py=y(val);
  svg.append(el("line",{x1:L,y1:py,x2:W-R,y2:py,stroke:"#dce8e1","stroke-width":1}));
  svg.append(el("text",{x:L-7,y:py+4,"text-anchor":"end","font-size":11,fill:"#5d786d"},fmt(val,val<10?1:0)));
 }
 dates.forEach((date,i)=>{
  svg.append(el("text",{x:x(i),y:H-15,"text-anchor":"middle","font-size":11,fill:"#5d786d"},date.slice(5).replace("-","/")));
 });
 if(entry.type==="bar"){
  vals.forEach((v,i)=>{
   const bar=el("rect",{x:x(i)-iw/7*.31,y:y(v),width:iw/7*.62,height:Math.max(0,y(0)-y(v)),rx:3,fill:"#328a6a"});
   bar.append(el("title",{},dates[i]+" · "+fmt(v)+" "+entry.unit));svg.append(bar);
  });
 }else{
  svg.append(el("polyline",{points:vals.map((v,i)=>x(i)+","+y(v)).join(" "),fill:"none",stroke:"#126b70","stroke-width":3,"stroke-linejoin":"round"}));
  vals.forEach((v,i)=>{
   const circle=el("circle",{cx:x(i),cy:y(v),r:4,fill:"#126b70",stroke:"#fff","stroke-width":1.5});
   circle.append(el("title",{},dates[i]+" · "+fmt(v)+" "+entry.unit));svg.append(circle);
  });
 }
 slot.append(svg);
 set("oaf-forecast-"+entry.id+"-meta","Fuente: Open-Meteo · "+city+
      " · "+dates[0]+" a "+dates[6]+" · "+entry.unit+
      " · consulta "+consulted+" (hora de Lima).");
}
async function forecast(city){
 if(!coords[city]||!g("oaf-forecast-grid"))return;
 const order=++seq;
 for(const e of series){g("oaf-forecast-"+e.id)?.replaceChildren();set("oaf-forecast-"+e.id+"-meta","Consultando modelo externo para "+city+"…")}
 const [lat,lon]=coords[city];
 const params=new URLSearchParams({
  latitude:String(lat),longitude:String(lon),
  daily:series.map(x=>x.key).join(","),timezone:"America/Lima",forecast_days:"7"
 });
 try{
  const response=await get("https://api.open-meteo.com/v1/forecast?"+params);
  if(order!==seq)return;
  const dates=response?.daily?.time;
  if(!Array.isArray(dates)||dates.length!==7)throw Error("El proveedor no devolvió siete días");
  const consulted=new Date().toLocaleString("es-PE",{timeZone:"America/Lima",hour12:false});
  for(const e of series){
   const values=response.daily[e.key];
   if(!Array.isArray(values)||values.length!==7||!values.every(Number.isFinite)){
    set("oaf-forecast-"+e.id+"-meta","Serie no disponible en esta consulta. Fuente prevista: Open-Meteo; sin datos simulados.");continue;
   }
   renderChart(g("oaf-forecast-"+e.id),dates,values,e,city,consulted);
  }
  set("oaf-forecast-state","Pronóstico externo para "+city+" · siete días · fuente Open-Meteo. No es un pronóstico desarrollado por OAF.");
 }catch(e){
  if(order!==seq)return;
  set("oaf-forecast-state","No se dispone de pronósticos externos para "+city+". No se generan valores alternativos.");
  for(const entry of series)set("oaf-forecast-"+entry.id+"-meta","Sin datos: no fue posible consultar Open-Meteo.");
 }
}
async function enfenSummary(){
 try{
  const j=await get("datos/estado_enfen_3z.json");
  const reliable=j.verificacion==="verificada"&&j.numero&&j.fecha_emision&&
    j.estado_institucional&&/^https:\/\//.test(j.url_comunicado||"");
  if(!reliable){
   set("oaf-enfen-current","Comunicado oficial no confirmado en la última comprobación");
   set("oaf-enfen-date","Última consulta registrada: "+(j.fecha_consulta_utc||"no indicada")+". No se interpreta una consulta fallida como ausencia de El Niño.");
   const badge=g("oaf-enfen-status-badge");if(badge)badge.dataset.status="pending";
   return;
  }
  set("oaf-enfen-current","ENFEN · comunicado "+j.numero+" ("+j.fecha_emision+") · "+j.estado_institucional);
  set("oaf-enfen-date","Fuente ENFEN · emitido el "+j.fecha_emision+
      ". Consulte si existe una actualización oficial posterior.");
  const source=g("oaf-enfen-official-link");
  if(source){source.href=j.url_comunicado;source.textContent="Leer este comunicado oficial ↗";}
  const badge=g("oaf-enfen-status-badge");if(badge){badge.dataset.status="observed";badge.textContent="Comunicado verificado en archivo";}
 }catch(e){
  set("oaf-enfen-current","Estado oficial pendiente de comprobación");
  set("oaf-enfen-date","Sin acceso a la verificación institucional. Utilice la página oficial ENFEN.");
 }
}
function attach(){
 const sel=g("oaf-home-location");if(!sel)return;
 // The shared locality coordinator emits a single event; no duplicate API request.
 document.addEventListener("oaf:localidad",e=>{if(coords[e.detail?.localidad]){forecast(e.detail.localidad);updateMap(e.detail.localidad,null)}});
 document.addEventListener("oaf:weather",e=>{if(e.detail?.localidad===sel.value)updateMap(sel.value,e.detail.current)});
 forecast(sel.value);
 updateMap(sel.value,null);
 enfenSummary();
 // The observed/reference station objects are already available in the climate tab.
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",attach);
else attach();
})();