(function predictions9(){
"use strict";
const $=id=>document.getElementById(id),N="http://www.w3.org/2000/svg";
const places={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const fmt=(n,d=1)=>Number(n).toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d});
const day=s=>{const p=String(s).split("-");return p.length===3?`${p[2]}/${p[1]}`:s};
const source=(path,type="json")=>fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status} — ${path}`);return type==="text"?r.text():r.json()});
const node=(name,attr,text)=>{const n=document.createElementNS(N,name);for(const [key,value] of Object.entries(attr||{}))n.setAttribute(key,String(value));if(text!==undefined)n.textContent=String(text);return n};
const set=(id,value)=>{const n=$(id);if(n)n.textContent=value};
const ellipsize=s=>String(s).length>18?String(s).slice(0,18)+"…":String(s);
const columns=(target,labels,values,opt={})=>{
 const div=$(target);if(!div)return;
 const valid=values?.length===labels?.length&&values.length>0&&values.every(Number.isFinite);
 if(!valid){set(target,"El proveedor no devolvió una serie numérica completa.");return}
 const W=750,H=300,L=54,R=26,T=26,B=49,max=Math.max(...values,0),min=opt.zero?0:Math.min(0,...values),span=Math.max(1,max-min),lo=opt.zero?0:min-span*.10,hi=max+span*.14+(.2*(max===0)),plotW=W-L-R,plotH=H-T-B,dy=x=>T+(hi-x)/(hi-lo)*plotH,dx=i=>L+plotW*(i+.5)/values.length;
 const root=node("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":opt.label||"Gráfico de datos"});
 for(let i=0;i<5;i++){const val=lo+(hi-lo)*i/4,Y=dy(val);root.append(node("line",{x1:L,y1:Y,x2:W-R,y2:Y,stroke:"#d5e5dd","stroke-width":1}));root.append(node("text",{x:L-8,y:Y+4,"text-anchor":"end","font-size":12,fill:"#59796c"},fmt(val,1)))}
 if(opt.line){
  const d=values.map((v,i)=>`${dx(i).toFixed(1)},${dy(v).toFixed(1)}`).join(" ");
  root.append(node("polyline",{points:d,fill:"none",stroke:"#ec7b42","stroke-width":5,"stroke-linejoin":"round","stroke-linecap":"round"}));
  values.forEach((v,i)=>{const x=dx(i),y=dy(v),p=node("circle",{cx:x,cy:y,r:5,fill:v>=32?"#c74e4b":"#f4a44c",stroke:"#fff","stroke-width":2,tabindex:0,role:"img","aria-label":`${labels[i]}: ${fmt(v,1)} ${opt.unit}`});p.append(node("title",{},`${labels[i]} · ${fmt(v,1)} ${opt.unit}`));root.append(p)});
 }else{
  const width=Math.min(44,plotW/values.length*.65);
  values.forEach((v,i)=>{const x=dx(i),y=dy(v),y0=dy(0),b=node("rect",{x:x-width/2,y:Math.min(y,y0),width,height:Math.max(1,Math.abs(y0-y)),rx:4,fill:opt.enso?(v>=2?"#d76549":v>=.5?"#e9b257":v<=-.5?"#3e88b7":"#70b1a5"):(v>=10?"#2773bd":"#52b2dc"),tabindex:0,role:"img","aria-label":`${labels[i]}: ${fmt(v,1)} ${opt.unit}`});b.append(node("title",{},`${labels[i]} · ${fmt(v,1)} ${opt.unit}`));root.append(b)});
 }
 const step=Math.max(1,Math.ceil(labels.length/7));labels.forEach((s,i)=>{if(i%step===0||i===labels.length-1)root.append(node("text",{x:dx(i),y:H-18,"text-anchor":"middle","font-size":12,fill:"#567368"},ellipsize(s)))});
 div.replaceChildren(root);
};
const state={daily:null,enso:null};
function forecastSummary(d){
 const site=d.site;
 const days=d.dates.filter((_,i)=>d.rain[i]>=.5);
 const total=d.rain.reduce((a,v)=>a+v,0), max=Math.max(...d.rain),maxDay=d.dates[d.rain.indexOf(max)],tmax=Math.max(...d.temps),dayT=d.dates[d.temps.indexOf(tmax)];
 const text=days.length?`En ${site}, el pronóstico indica lluvia medible en ${days.length} de los próximos siete días: ${days.map(day).join(", ")}. El mayor acumulado diario previsto sería de ${fmt(max,1)} mm el ${day(maxDay)}. El total estimado de la semana es ${fmt(total,1)} mm.`:`En ${site}, el modelo muestra menos de 0,5 mm por día durante los siete días consultados. Esto no garantiza ausencia de lluvia localizada.`;
 set("oaf-ux9-resumen-meteo",text);
 set("oaf-ux9-final-lluvia",text+" Son predicciones diarias del proveedor meteorológico y pueden modificarse.");
 set("oaf-ux9-final-temperatura",`La temperatura máxima prevista en ${site} alcanzaría ${fmt(tmax,1)} °C el ${day(dayT)}. ${tmax>=32?"Se recomienda precaución por calor durante las labores agrícolas.":tmax>=28?"Se prevén jornadas cálidas; prioriza hidratación y protección solar.":"Revisa la evolución diaria antes de planificar las labores."}`);
 const badges=$("oaf-ux9-dias");if(badges){badges.replaceChildren();d.dates.forEach((date,i)=>{const b=document.createElement("span");if(d.rain[i]>=.5)b.className="rain";b.textContent=`${day(date)} · ${fmt(d.rain[i],1)} mm`;badges.append(b)})}
}
let order=0;
async function forecast(){
 const city=$("oaf-ux9-localidad")?.value||"Chiclayo",p=places[city],orderNow=++order;
 if(!p)return;
 const qs=new URLSearchParams({latitude:String(p[0]),longitude:String(p[1]),timezone:"America/Lima",daily:"precipitation_sum,temperature_2m_max",forecast_days:"7"});
 set("oaf-ux9-resumen-meteo",`Consultando la perspectiva meteorológica para ${city}…`);
 try{
  const j=await source("https://api.open-meteo.com/v1/forecast?"+qs);if(orderNow!==order)return;
  const d=j.daily||{},dates=d.time,rain=d.precipitation_sum,temps=d.temperature_2m_max;
  if(!Array.isArray(dates)||dates.length!==7||!Array.isArray(rain)||rain.length!==7||!rain.every(Number.isFinite)||!Array.isArray(temps)||temps.length!==7||!temps.every(Number.isFinite))throw Error("Faltan días o valores válidos");
  columns("oaf-ux9-grafico-lluvia",dates.map(day),rain,{zero:true,unit:"mm/día",label:"Precipitación diaria prevista con Open-Meteo"});
  columns("oaf-ux9-grafico-temperatura",dates.map(day),temps,{line:true,unit:"°C",label:"Máxima diaria prevista con Open-Meteo"});
  state.daily={site:city,dates,rain,temps};forecastSummary(state.daily);
  const now=new Date().toLocaleString("es-PE",{timeZone:"America/Lima",hour12:false});
  set("oaf-ux9-fuente-meteo",`Datos modelados mediante Open-Meteo, del ${dates[0]} al ${dates[6]}. Consulta: ${now}, hora peruana. Análisis divulgativo por OAF. No equivale a un modelo Random Forest diario propio, ni garantiza cantidades exactas en una parcela.`);
 }catch(e){
  if(orderNow!==order)return;state.daily=null;
  set("oaf-ux9-resumen-meteo","El pronóstico diario no está disponible en esta consulta. No se estiman cantidades ni fechas sin datos.");
  set("oaf-ux9-grafico-lluvia","Sin serie de lluvia verificable.");
  set("oaf-ux9-grafico-temperatura","Sin serie de temperaturas verificable.");
  set("oaf-ux9-final-lluvia","No puedo indicar días con lluvia porque el proveedor no respondió con siete días completos.");
  set("oaf-ux9-final-temperatura","Sin temperaturas máximas verificables en esta consulta.");
  set("oaf-ux9-fuente-meteo","Error de consulta de Open-Meteo: "+e.message+". Comprueba la conexión y vuelve a entrar a esta sección.");
 }
}
async function enso(){
 try{
  const [records,status]=await Promise.all([source("datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv","text"),source("datos/estado_enso_verificado_ux9_2026.json")]);
  const rows=records.trim().split(/\r?\n/).slice(1).map(x=>x.split(",")).filter(x=>x.length===3&&x[2].trim()!==""&&Number.isFinite(Number(x[2]))).map(x=>({month:x[0],anomaly:Number(x[2])}));
  if(rows.length<36||!status.enfen?.fecha_emision||!status.noaa?.fecha_emision)throw Error("Registro o informe documental incompleto");
  state.enso={rows,status};
  const months=$("oaf-ux9-meses");
  function draw(){
   const recent=rows.slice(-Number(months?.value||24));columns("oaf-ux9-grafico-enso",recent.map(r=>r.month.slice(2)),recent.map(r=>r.anomaly),{enso:true,unit:"°C",label:"Anomalía histórica Niño 1+2 NOAA NCEI referida a 1991–2020"});
  }
  months?.addEventListener("change",draw);draw();
  const recent=rows.at(-1),previous=rows.at(-2);
  set("oaf-ux9-enso-fecha",`Fuente: NOAA NCEI ERSSTv5, referencia 1991–2020; último mes archivado ${recent.month}, anomalía ${fmt(recent.anomaly,2)} °C. Registro histórico disponible en el repositorio del OAF. Las barras representan diferencia térmica, no categoría oficial del evento.`);
  const en=$("oaf-ux9-enfen-estado"),no=$("oaf-ux9-noaa-estado");if(en){
    en.replaceChildren();
    const s=document.createElement("strong");s.textContent=`Niño Costero · ${status.enfen.estado}`;
    const p=document.createElement("p");p.textContent=`Comunicado ENFEN ${status.enfen.numero}, ${status.enfen.fecha_emision}. Es el estado reportado para esa fecha; la intensidad de un evento no se deduce del gráfico Niño 1+2.`;
    const link=document.createElement("a");link.href=status.enfen.fuente;link.rel="noopener noreferrer";link.target="_blank";link.textContent="Ver comunicado ENFEN ↗";
    en.append(s,p,link);
  }
  if(no){
    no.replaceChildren();
    const h=document.createElement("strong");h.textContent="El Niño global · perspectiva NOAA CPC";
    const p=document.createElement("p");p.textContent=status.noaa.descripcion;
    const a=document.createElement("a");a.textContent="Consultar pronóstico de NOAA ↗";a.href=status.noaa.fuente;a.rel="noopener noreferrer";a.target="_blank";
    no.append(h,p,a);
  }
  const movement=recent.anomaly>previous.anomaly?"aumentó":recent.anomaly<previous.anomaly?"disminuyó":"se mantuvo";
  const interpretation=`El último dato mensual Niño 1+2 archivado es de ${recent.month} (${fmt(recent.anomaly,2)} °C sobre su referencia); respecto al mes anterior, la anomalía ${movement}. Este índice ayuda a seguir el calentamiento costero, pero no define por sí mismo la magnitud de El Niño ni las lluvias en Lambayeque.`;
  set("oaf-ux9-enso-interpretacion",interpretation);
  set("oaf-ux9-final-enso",`${interpretation} ENFEN comunicó ${status.enfen.estado} el ${status.enfen.fecha_emision}. NOAA CPC publicó una perspectiva de El Niño global fuerte a muy fuerte probable (emisión ${status.noaa.fecha_emision}). Estas dos valoraciones no son equivalentes; confirma las actualizaciones oficiales antes de concluir intensidad o impacto local.`);
 }catch(e){
  set("oaf-ux9-enso-interpretacion","No es posible evaluar las anomalías con los archivos actuales: "+e.message);
  set("oaf-ux9-grafico-enso","Serie oceánica no disponible.");
  set("oaf-ux9-final-enso","No se puede determinar la situación del fenómeno con información actualizada en este momento. Consulta ENFEN y NOAA CPC.");
  set("oaf-ux9-enfen-estado","Consulta pendiente. Revisa el portal de ENFEN.");
  set("oaf-ux9-noaa-estado","Consulta pendiente. Revisa el pronóstico NOAA CPC.");
 }
}
function init(){
 if(!$("oaf-ux9-predicciones")||$("oaf-ux9-predicciones").dataset.initialized)return;
 $("oaf-ux9-predicciones").dataset.initialized="true";
 $("oaf-ux9-localidad")?.addEventListener("change",forecast);
 document.addEventListener("oaf:localidad",e=>{const name=e.detail?.localidad,sel=$("oaf-ux9-localidad");if(sel&&places[name]&&sel.value!==name){sel.value=name;forecast()}});
 forecast();enso();
}
document.addEventListener("oaf:ux9-ready",init);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
