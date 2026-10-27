/* OAF UX38 · Consultas independientes de coordenadas en series científicas.
   Nunca convertir una localidad RF preentrenada en estimación puntual certificada.
   Open-Meteo: ERA5-Land 0,1 grados; no equivale a sensor de parcela. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const cached=new Map(),token={clima:0,predicciones:0};
const base={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const num=(x,d=1)=>Number.isFinite(x)?x.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
const el=(tag,cls,content)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(content!==undefined)x.textContent=content;return x;};
function monthRows(payload){
 const d=payload?.daily;if(!d||!Array.isArray(d.time))throw Error("Serie histórica sin fechas verificables");
 const groups=new Map(),fields=["temperature_2m_mean","precipitation_sum","shortwave_radiation_sum"];
 d.time.forEach((date,i)=>{
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date))return;
  const m=date.slice(0,7),row=groups.get(m)||{days:0,count:[0,0,0],sum:[0,0,0]};row.days++;
  fields.forEach((name,j)=>{const v=d[name]?.[i];if(Number.isFinite(v)){row.sum[j]+=v;row.count[j]++;}});groups.set(m,row);
 });
 return groups;
}
async function archive(point,start,end){
 const args=new URLSearchParams({latitude:String(point.lat),longitude:String(point.lon),start_date:start,end_date:end,
  daily:"temperature_2m_mean,precipitation_sum,shortwave_radiation_sum",models:"era5_land",timezone:"America/Lima"});
 const key=[point.lat.toFixed(6),point.lon.toFixed(6),start,end].join("|");
 if(!cached.has(key)){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),22000);
  const task=fetch("https://archive-api.open-meteo.com/v1/archive?"+args,{signal:controller.signal,cache:"no-store"})
   .then(async response=>{if(!response.ok)throw Error("HTTP "+response.status);return response.json()})
   .then(j=>{if(j.error)throw Error(j.reason||"Servicio histórico no disponible");return j;})
   .catch(err=>{cached.delete(key);throw err;}).finally(()=>clearTimeout(timer));
  cached.set(key,task);
 }
 return cached.get(key);
}
function table(target,headers,rows){
 const box=el("div","oaf-area-scroll"),t=el("table"),thead=el("thead"),tr=el("tr");
 headers.forEach(title=>{const th=el("th",null,title);th.scope="col";tr.append(th)});
 thead.append(tr);t.append(thead);
 const tbody=el("tbody");rows.forEach(record=>{const line=el("tr");record.forEach(v=>line.append(el("td",null,String(v))));tbody.append(line)});
 t.append(tbody);box.append(t);target.append(box);
}
function barChart(target,labels,values,unit){
 const v=values.filter(Number.isFinite);if(!v.length)return;
 const lo=Math.min(0,...v),hi=Math.max(1,...v),max=Math.max(1,hi-lo);
 const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
 svg.setAttribute("viewBox","0 0 720 235");svg.setAttribute("role","img");svg.setAttribute("width","100%");
 svg.setAttribute("aria-label","Comparación mensual por punto, unidades "+unit);
 labels.forEach((label,i)=>{
  if(!Number.isFinite(values[i]))return;
  const x=42+i*640/labels.length,y=183-(values[i]-lo)/max*142,width=Math.max(4,640/labels.length-9);
  const rect=document.createElementNS(svg.namespaceURI,"rect");rect.setAttribute("x",String(x));rect.setAttribute("y",String(Math.min(y,183)));rect.setAttribute("height",String(Math.max(1,Math.abs(y-183))));rect.setAttribute("width",String(width));rect.setAttribute("rx","2");rect.setAttribute("fill","#39836a");
  const tip=document.createElementNS(svg.namespaceURI,"title");tip.textContent=label+": "+num(values[i])+" "+unit;rect.append(tip);svg.append(rect);
  const lbl=document.createElementNS(svg.namespaceURI,"text");lbl.setAttribute("x",String(x+width/2));lbl.setAttribute("y","211");lbl.setAttribute("text-anchor","middle");lbl.setAttribute("font-size","11");lbl.setAttribute("fill","#486958");lbl.textContent=label.slice(-2);svg.append(lbl);
 });
 target.append(svg);
}
function statsPoint(payload,point){
 return "Punto solicitado: "+point.lat.toFixed(5)+", "+point.lon.toFixed(5)+". Centro de celda utilizada por el reanálisis: "+
 (Number.isFinite(payload.latitude)?payload.latitude.toFixed(4):"no informado")+", "+
 (Number.isFinite(payload.longitude)?payload.longitude.toFixed(4):"no informado")+".";
}
function targetHistoric(){
 let root=$("oaf-area-clima-serie");const original=$("oaf-hist-plot");
 if(!original)return null;
 if(!root){root=el("section","oaf-area-scientific");root.id="oaf-area-clima-serie";original.after(root);}
 original.hidden=true;
 const note=$("#oaf-history .oaf-figure-caption");if(note)note.hidden=true;
 const status=$("#oaf-hist-status");if(status)status.hidden=true;
 return root;
}
function restoreHistoric(){
 $("oaf-area-clima-serie")?.remove();const plot=$("oaf-hist-plot");if(plot)plot.hidden=false;
 const status=$("oaf-hist-status");if(status)status.hidden=false;
 const caption=$("#oaf-history .oaf-figure-caption");if(caption)caption.hidden=false;
}
async function climate(point){
 const q=++token.clima,root=targetHistoric();if(!root)return;
 const yearValue=Number($("oaf-hist-year")?.value);
 const year=Number.isInteger(yearValue)&&yearValue>=1996&&yearValue<=2025?yearValue:2025;
 const kind=$("oaf-hist-variable")?.value||"precipitacion_mm";
 const idx=kind==="temperatura_c"?0:kind==="radiacion_mj_m2"?2:1;
 const units=["°C","mm","MJ/m²"],names=["Temperatura media","Precipitación acumulada","Radiación solar acumulada"];
 root.textContent="Consultando la serie del año "+year+" para la coordenada introducida…";
 try{
  const payload=await archive(point,year+"-01-01",year+"-12-31");
  if(q!==token.clima||!window.OAFTerritory?.getActivePoint?.("clima"))return;
  const months=monthRows(payload),labels=[],values=[],rows=[];
  for(let month=1;month<=12;month++){
   const name=year+"-"+String(month).padStart(2,"0"),r=months.get(name);
   const val=r?.count[idx]>0?(idx===0?r.sum[idx]/r.count[idx]:r.sum[idx]):NaN;
   labels.push(name);values.push(val);rows.push([name,Number.isFinite(val)?num(val)+" "+units[idx]:"Sin datos",String(r?.count[idx]||0)]);
  }
  root.replaceChildren(el("h3",null,"Serie histórica georreferenciada · "+point.name+" · "+year));
  root.append(el("p",null,names[idx]+" · "+statsPoint(payload,point)));
  barChart(root,labels,values,units[idx]);
  table(root,["Mes","Valor mensual","Días con datos"],rows);
  const finite=values.filter(Number.isFinite);
  let interpretation="Los datos no permiten interpretar una serie anual completa.";
  if(finite.length===12){
   const max=Math.max(...finite),min=Math.min(...finite);
   const maxMonth=labels[values.indexOf(max)],minMonth=labels[values.indexOf(min)];
   interpretation="Durante "+year+", el valor mensual mayor de "+names[idx].toLowerCase()+" fue "+num(max)+" "+units[idx]+" en "+maxMonth+" y el menor "+num(min)+" "+units[idx]+" en "+minMonth+". Son diferencias temporales modeladas en la celda del punto solicitado.";
  }
  root.append(el("p","oaf-area-interpretacion","Interpretación agroclimática: "+interpretation+" La información no demuestra presencia de plagas o enfermedades ni cuantifica pérdidas."));
  root.append(el("p","oaf-area-metodo","Fuente: Open-Meteo Archive · ERA5-Land, consulta puntual WGS84. No se calculan anomalías respecto a 1996–2025 hasta construir una normal de esa misma celda. El visor histórico predeterminado permanece disponible al elegir Chiclayo, Jayanca, Motupe u Olmos."));
 }catch(err){if(q===token.clima)root.textContent="La serie del punto no está disponible: "+err.message+". No se sustituye por otra localidad.";}
}
function dist(p,a){
 const r=Math.PI/180,dLat=(a[0]-p.lat)*r,dLon=(a[1]-p.lon)*r;
 const t=Math.sin(dLat/2)**2+Math.cos(p.lat*r)*Math.cos(a[0]*r)*Math.sin(dLon/2)**2;
 return 12742*Math.asin(Math.min(1,Math.sqrt(t)));
}
function resetMonthly(){$("oaf-area-predicciones-resumen")?.remove();}
async function monthly(point){
 const q=++token.predicciones,pane=$("oaf-ux14-rf-mes");if(!pane)return;
 let panel=$("oaf-area-predicciones-resumen");
 if(!panel){panel=el("section","oaf-area-scientific");panel.id="oaf-area-predicciones-resumen";pane.append(panel);}
 const nearby=Object.entries(base).map(([name,coords])=>({name,km:dist(point,coords)})).sort((a,b)=>a.km-b.km);
 const select=$("oaf-ux16-mes-ciudad");
 if(select&&select.value!==nearby[0].name){select.value=nearby[0].name;select.dispatchEvent(new Event("change",{bubbles:true}));}
 panel.textContent="Consultando la referencia mensual específica de "+point.name+"…";
 try{
  const data=await archive(point,"2021-01-01","2025-12-31");
  if(q!==token.predicciones||!window.OAFTerritory?.getActivePoint?.("predicciones"))return;
  const grouped=monthRows(data),months=new Map();
  for(const [m,v] of grouped){
   const n=Number(m.slice(-2));
   const [year,month]=m.split("-").map(Number),completeDays=new Date(year,month,0).getDate();
   if(v.count[0]!==completeDays||v.count[1]!==completeDays||v.days!==completeDays)continue;
   const row=months.get(n)||[];row.push({temp:v.sum[0]/v.days,rain:v.sum[1]});months.set(n,row);
  }
  panel.replaceChildren(el("h3",null,"Contexto agroclimático de la zona productiva: "+point.name));
  panel.append(el("p",null,statsPoint(data,point)));
  panel.append(el("p",null,"El gráfico Random Forest del visor corresponde a "+nearby[0].name+" (punto de referencia aproximadamente a "+num(nearby[0].km)+" km). No representa un cálculo RF efectuado en la parcela: se muestra únicamente para comparación territorial."));
  const rows=[];
  const refs=[[11,"Nov 2026"],[12,"Dic 2026"],[1,"Ene 2027"],[2,"Feb 2027"],[3,"Mar 2027"],[4,"Abr 2027"]];
  for(const [m,title] of refs){
   const records=months.get(m)||[],r=records.length?records.reduce((a,x)=>a+x.rain,0)/records.length:NaN;
   const t=records.length?records.reduce((a,x)=>a+x.temp,0)/records.length:NaN;
   rows.push([title,Number.isFinite(r)?num(r)+" mm":"Sin datos",Number.isFinite(t)?num(t)+" °C":"Sin datos",records.length+"/5"]);
  }
  table(panel,["Mes de comparación","Lluvia histórica media","Temperatura histórica media","Años válidos"],rows);
  const valid=rows.filter(r=>!r[1].startsWith("Sin datos"));
  panel.append(el("p","oaf-area-interpretacion",valid.length===6?
   "Lectura agroclimática: se aprecia el patrón climatológico local de noviembre a abril obtenido para esta celda. Estos promedios de 2021–2025 ayudan a contextualizar los resultados; NO son una predicción de los meses 2026–2027.":
   "Lectura agroclimática: la referencia de cinco años contiene meses incompletos y no permite una comparación integral. No se rellenan ausencias."));
  panel.append(el("p","oaf-area-metodo","Fuente: Open-Meteo Archive · ERA5-Land (reanálisis, 2021–2025). Para predicciones mensuales RF reales en este punto harían falta variables de entrada georreferenciadas, entrenamiento y validación espacial/temporal del modelo."));
 }catch(err){if(q===token.predicciones)panel.textContent="No hay referencia mensual verificable para las coordenadas: "+err.message+". El RF mostrado sigue siendo solamente el de la localidad predeterminada.";}
}
function update(scope,point){
 if(!point)return;
 if(scope==="clima")climate(point);
 else if(scope==="predicciones")monthly(point);
}
function init(){
 window.oafAreaUX38={update,restoreHistoric,resetMonthly};
 for(const scope of ["clima","predicciones"]){
  const p=window.OAFTerritory?.getActivePoint?.(scope);
  if(p)update(scope,p);
 }
 document.addEventListener("oaf:area-update",e=>{
  const {scope,point,active}=e.detail||{};
  if(scope==="clima"){if(active&&point)climate(point);else{++token.clima;restoreHistoric();}}
  if(scope==="predicciones"){if(active&&point)monthly(point);else{++token.predicciones;resetMonthly();}}
  if(scope==="inicio")document.dispatchEvent(new Event("oaf:area-home-refresh"));
 });
 const hist=$("oaf-hist-place");
 hist?.addEventListener("change",()=>{++token.clima;restoreHistoric();});
 const pred=$("oaf-ux16-mes-ciudad");
 // La selección manual sigue funcionando; una elección propia de localidad no altera otras pestañas.
 pred?.addEventListener("change",()=>{});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();