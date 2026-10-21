(function sanitary11(){
"use strict";
const $=id=>document.getElementById(id);
const places={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const nfmt=(n,d=1)=>Number(n).toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d});
const element=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e};
const set=(id,value)=>{const v=$(id);if(v)v.textContent=String(value)};
const link=(name,url)=>{const a=element("a",null,name);if(/^https:\/\//.test(url)){a.href=url;a.target="_blank";a.rel="noopener noreferrer"}return a};
const dname=s=>{const [year,mon,day]=s.split("-");return day+"/"+mon};
const state={organisms:[],crops:[],model:null,mg:null,forecast:new Map(),selected:null,weather:null,request:0};
function option(value,text){const o=document.createElement("option");o.value=value;o.textContent=text;return o}
function refill(id,entries,selected){
 const s=$(id);if(!s)return;const prev=selected??s.value;s.replaceChildren(...entries.map(([v,n])=>option(v,n)));
 if([...s.options].some(o=>o.value===prev))s.value=prev;
}
function optionsFor(type,kind,crop){
 let records=state.organisms.filter(x=>x.crop_id===crop&&(kind==="todos"||x.tipo===kind));
 return records.map(x=>[x.id,x.nombre+" · "+x.agentes]).sort((a,b)=>a[1].localeCompare(b[1],"es"));
}
function drawIllustration(rec){
 const t=$("oaf-sm-ilustracion");if(!t)return;
 const bug=rec.tipo==="plaga",col=bug?"#f1c774":"#c2e4ac";
 const icon=bug?`<g transform="translate(210 60)" fill="#275a54" stroke="#204e46" stroke-width="4"><ellipse cx="0" cy="30" rx="29" ry="35" fill="#edaf69"/><ellipse cx="0" cy="-11" rx="18" ry="22" fill="#e9c48d"/><path d="M-22 6l-44 -28M22 6l44 -28M-29 29l-45 13M29 29l45 13M-23 53l-41 31M23 53l41 31M-6-31l-14-24M6-31l14-24" fill="none" stroke="#366760" stroke-width="6"/><path d="M0 0v63" stroke="#c97346"/><circle cx="-7" cy="-17" r="3"/><circle cx="7" cy="-17" r="3"/></g>`:`<g transform="translate(215 98)" fill="${col}" stroke="#5a8f65" stroke-width="4"><circle cx="-32" cy="-22" r="23"/><circle cx="12" cy="-44" r="18"/><circle cx="41" cy="4" r="23"/><circle cx="-2" cy="25" r="20"/><path d="M-46-42l-20-22m83 8 18-26m25 90 25 14m-90 29-8 25" fill="none"/></g>`;
 t.innerHTML=`<svg viewBox="0 0 370 146" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ilustración esquemática de hojas y ${bug?"plaga":"organismo causante de enfermedad"}; no es fotografía diagnóstica"><defs><linearGradient id="ux11leaf" x2="0.7" y2="1"><stop stop-color="#d8f3d2"/><stop offset="1" stop-color="#69ab87"/></linearGradient></defs><rect width="370" height="146" fill="#e6f4e8"/><path d="M0 145Q80 23 159 91T370 55V146Z" fill="#a9d5bb"/><g transform="translate(45 24)"><path d="M88 112Q-15 20 31 2Q118 12 88 112Z" fill="url(#ux11leaf)" stroke="#4a9672" stroke-width="4"/><path d="M88 112Q113-9 173 13Q201 89 88 112Z" fill="#7ebfa0" stroke="#408c76" stroke-width="4"/><path d="M88 112L31 19M88 112l75-93" stroke="#4e997b" stroke-width="4" fill="none"/></g>${icon}</svg>`;
}
function renderSource(id,r){const area=$(id);if(!area)return;area.replaceChildren();const refs=[...new Set(r.referencias||[])].filter(x=>/^https:\/\//.test(x));refs.forEach((url,i)=>area.append(link(i===0?"Fuente fitosanitaria ↗":"Investigación complementaria ↗",url)))}
function refreshFilters(scope,crop){
 const prefix=scope==="model"?"sm":"mg",t=$(scope==="model"?"oaf-sm-tipo":"oaf-mg-tipo")?.value||"todos";
 const s=$(scope==="model"?"oaf-sm-patogeno":"oaf-mg-patogeno");
 refill(s.id,optionsFor(t, t, crop),s.value);
}
function dependent(prefix){
 const crop=$(`oaf-${prefix}-cultivo`)?.value||"mango",typ=$(`oaf-${prefix}-tipo`)?.value||"todos";
 refill(`oaf-${prefix}-patogeno`,optionsFor(typ,typ,crop),null);
}
const getCurrent=prefix=>state.organisms.find(r=>r.id===$(`oaf-${prefix}-patogeno`)?.value);
function renderConditions(r){
 const area=$("oaf-sm-condiciones");if(!area)return;
 const types={
 temperatura:["Temperatura y actividad biológica","La temperatura modifica la tasa de desarrollo o actividad del organismo, pero no equivale a una curva de población. Para determinar fluctuación poblacional se necesitan trampas, conteos repetidos, fenología y abundancia de hospedantes."],
 humedad:["Humedad y periodos de mojado","Lluvia y humedad relativa pueden favorecer procesos epidemiológicos, pero no miden directamente el mojado foliar ni confirman infección. La fenología, el inóculo y la ventilación modifican la respuesta."],
 suelo:["Saturación y drenaje del suelo","La lluvia pronosticada no representa la humedad real del sustrato ni el riego. Son necesarias observaciones en raíces, humedad del suelo, drenaje y diagnóstico."],
 estres:["Estrés y heridas","Calor, déficit hídrico y heridas son factores de predisposición; el clima por sí solo no permite concluir infección de madera ni muerte regresiva."],
 bioseguridad:["Ingreso y dispersión","La presencia de R4T depende de la introducción y dispersión del patógeno. No se emite predicción de ocurrencia a partir de una serie meteorológica."]
 };
 const t=types[r.clasificacion]||["Vigilancia integrada","Es necesaria observación directa del cultivo."];
 area.replaceChildren();area.append(element("strong",null,t[0]),element("p",null,t[1]),element("small",null,"Comprobación de campo: "+r.vigilancia));
}
function renderTable(j){
 const box=$("oaf-sm-tabla");if(!box)return;box.replaceChildren();
 const table=element("table","oaf-ux11-weather-table"),head=document.createElement("thead"),body=document.createElement("tbody");
 const tr=document.createElement("tr");["Día","Lluvia prevista","T. media","HR media"].forEach(v=>tr.append(element("th",null,v)));head.append(tr);
 j.days.forEach((date,i)=>{const row=document.createElement("tr");[dname(date),nfmt(j.precip[i])+" mm",nfmt(j.temp[i])+" °C",nfmt(j.hum[i],0)+" %"].forEach(value=>row.append(element("td",null,value)));body.append(row)});
 table.append(head,body);box.append(table);
}
function renderManage(){
 const r=getCurrent("mg");if(!r)return;
 set("oaf-mg-title",r.nombre);set("oaf-mg-species",r.agentes);set("oaf-mg-tipo-badge",r.tipo==="plaga"?"Plaga · "+r.crop_nombre:"Enfermedad · "+r.crop_nombre);
 set("oaf-mg-dano",r.dano);set("oaf-mg-cultural",r.manejo_cultural);renderSource("oaf-mg-fuentes",r);set("oaf-mg-clima",r.modelo_nota);
 const area=$("oaf-mg-productos");if(!area)return;area.replaceChildren();
 if(!r.productos?.length){
  const c=element("div","oaf-ux11-product");c.append(element("strong",null,"Sin producto específico de etiqueta confirmada en esta ficha"),element("p",null,"No se debe recomendar automáticamente un plaguicida para este cultivo y organismo. Consulta SIGIA por nombre del cultivo y plaga, o a SENASA y a un especialista en MIP."));area.append(c);
 }else for(const p of r.productos){
  const c=element("div","oaf-ux11-product");
  const chip=element("span","oaf-ux11-badge "+(p.tipo.startsWith("Biol")?"":"amber"),p.tipo);
  c.append(chip,element("strong",null,p.nombre),element("small",null,p.ingrediente),element("p",null,p.registro),element("p",null,p.nota));if(p.modo)c.append(element("small",null,"Modo de acción: "+p.modo));c.append(link("Consultar ficha / documento ↗",p.fuente));area.append(c);
 }
}
function plot(rain,humidity,dates){
 const out=$("oaf-sm-chart");if(!out)return;const W=720,H=270,L=42,R=48,T=18,B=42;
 const ns="http://www.w3.org/2000/svg",make=(name,attrs={},text)=>{const e=document.createElementNS(ns,name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(text!==undefined)e.textContent=text;return e};
 const svg=make("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":"Barras de lluvia diaria y línea de humedad relativa estimada para siete días"});
 const max=Math.max(5,...rain)*1.15,x=i=>L+(i+.5)*(W-L-R)/7,yy=v=>T+(H-T-B)*(1-v/max),yh=v=>T+(H-T-B)*(1-v/100);
 for(let i=0;i<=4;i++){let yy1=T+(H-T-B)*i/4;svg.append(make("line",{x1:L,y1:yy1,x2:W-R,y2:yy1,class:"gridline"}));svg.append(make("text",{x:L-7,y:yy1+4,"text-anchor":"end",class:"axis"},nfmt(max*(1-i/4),0)))}
 const points=[];rain.forEach((mm,i)=>{let rect=make("rect",{x:x(i)-20,y:yy(mm),width:40,height:Math.max(1,yy(0)-yy(mm)),rx:5,fill:mm>=10?"#217aa8":"#50abd0"});rect.append(make("title",{},`${dates[i]}: ${nfmt(mm)} mm`));svg.append(rect);let y=yh(humidity[i]);points.push(x(i)+","+y);svg.append(make("text",{x:x(i),y:H-14,"text-anchor":"middle",class:"axis"},dname(dates[i])));});
 svg.append(make("polyline",{points:points.join(" "),stroke:"#e39a4d","stroke-width":4,fill:"none","stroke-linecap":"round","stroke-linejoin":"round"}));
 humidity.forEach((v,i)=>{let cir=make("circle",{cx:x(i),cy:yh(v),r:4,fill:"#e39a4d",stroke:"#fff","stroke-width":1.3});cir.append(make("title",{},`${dates[i]}: humedad media ${nfmt(v,0)} %`));svg.append(cir)});
 out.replaceChildren(svg);
}
async function week(place){
 if(!state.forecast.has(place)){
  const [latitude,longitude]=places[place];
  const query=new URLSearchParams({latitude:String(latitude),longitude:String(longitude),timezone:"America/Lima",forecast_days:"7",daily:"precipitation_sum,temperature_2m_max",hourly:"relative_humidity_2m,temperature_2m"});
  state.forecast.set(place,fetch("https://api.open-meteo.com/v1/forecast?"+query).then(r=>{if(!r.ok)throw Error("API "+r.status);return r.json()}).then(j=>{
    const daily=j.daily,hourly=j.hourly;
    if(!daily||!hourly||daily.time?.length!==7||daily.precipitation_sum?.length!==7||!hourly.time||!hourly.relative_humidity_2m)throw Error("Serie diaria/horaria incompleta");
    const group=daily.time.map(day=>hourly.time.map((t,i)=>[t,hourly.relative_humidity_2m[i],hourly.temperature_2m[i]]).filter(x=>x[0].startsWith(day)));
    const humid=group.map(row=>{const nums=row.map(x=>x[1]).filter(Number.isFinite);return nums.length>=12?nums.reduce((a,b)=>a+b,0)/nums.length:NaN});
    const avgtemp=group.map(row=>{const nums=row.map(x=>x[2]).filter(Number.isFinite);return nums.length>=12?nums.reduce((a,b)=>a+b,0)/nums.length:NaN});
    if(!humid.every(Number.isFinite)||!avgtemp.every(Number.isFinite)||!daily.precipitation_sum.every(Number.isFinite)||!daily.temperature_2m_max.every(Number.isFinite))throw Error("Faltantes meteorológicos");
    return {days:daily.time,precip:daily.precipitation_sum,hum:humid,temp:avgtemp,max:daily.temperature_2m_max};
  }).catch(e=>{state.forecast.delete(place);throw e}));
 }
 return state.forecast.get(place);
}
function renderConclusion(r,weekData,place){
 const rain=weekData.precip.reduce((a,v)=>a+v,0),wet=weekData.hum.filter(v=>v>=80).length,wetter=weekData.precip.filter(v=>v>=1).length,
 hot=weekData.max.filter(v=>v>=30).length,cool=weekData.temp.filter(v=>v>=18&&v<=30).length;
 const details=`En ${place}, los próximos siete días muestran aproximadamente ${nfmt(rain)} mm de lluvia, ${wetter} días con al menos 1 mm y ${wet} días con humedad media de 80 % o más.`;
 let status="monitor",msg="";
 switch(r.clasificacion){
 case "humedad": status=wet>=2||wetter>=2?"attention":"monitor";msg=wet>=2||wetter>=2?"Hay señales de humedad o lluvia que justifican revisar más frecuentemente flores, hojas y frutos susceptibles.":"La semana muestra pocas señales de humedad persistente; la inspección no debe abandonarse.";break;
 case "temperatura":msg=`Se observan ${cool} días con temperatura media aproximadamente entre 18 y 30 °C y ${hot} días de calor (máximas ≥30 °C). Esto puede modificar la actividad o desarrollo de algunos insectos, pero no permite saber si sus poblaciones aumentarán sin trampas y conteos.`;break;
 case "suelo":msg=wetter>=2?"Hay días con lluvia prevista; comprueba drenaje real y riego antes de considerar riesgo de pudrición radicular.":"El pronóstico no indica lluvia repetida; aun así, el riego o mal drenaje pueden saturar el suelo y favorecer daño radicular.";break;
 case "estres":msg=hot>=2?"Hay días con calor previsto; revisa estrés hídrico y heridas de poda, sin deducir por ello presencia de patógenos de madera.":"La semana no muestra calor repetido intenso en este pronóstico; vigila heridas y estado hídrico igualmente.";break;
 case "bioseguridad":status="unavailable";msg="Fusarium R4T NO puede predecirse por temperatura o lluvia únicamente. Prioriza higiene, cuarentena, material sano, control de movimientos y reporte de síntomas a SENASA.";break;
 default: msg="La fenología y el manejo del cultivo son esenciales para interpretar esta semana. Acompaña estos datos con muestreo y diagnóstico.";
 }
 const c=$("oaf-sm-conclusion");if(c){c.dataset.state=status;c.textContent=details+" "+msg+" Vigilancia específica para "+r.nombre+": "+r.vigilancia+". Señales meteorológicas orientativas, no una probabilidad validada de infección, incidencia o infestación."}
}
let sequence=0;
async function renderModel(){
 const r=getCurrent("sm"),place=$("oaf-sm-localidad")?.value||"Chiclayo";if(!r)return;const q=++sequence;
 set("oaf-sm-clase",(r.tipo==="plaga"?"Plaga":"Enfermedad")+" · "+r.crop_nombre);set("oaf-sm-titulo",r.nombre);set("oaf-sm-agente",r.agentes);set("oaf-sm-principio",r.modelo_nota);renderSource("oaf-sm-fuentes",r);drawIllustration(r);renderConditions(r);
 set("oaf-sm-conclusion","Consultando el pronóstico meteorológico para "+place+"…");
 try{const j=await week(place);if(q!==sequence)return;const total=j.precip.reduce((a,b)=>a+b,0),mean=j.hum.reduce((a,b)=>a+b,0)/7,tmax=Math.max(...j.max);
  const ms=$("oaf-sm-datos");ms?.replaceChildren();
  for(const [lbl,n,unit] of [["Lluvia prevista 7 días",total,"mm"],["Humedad media",mean,"%"],["Temperatura máxima",tmax,"°C"]]){const d=element("div");d.append(element("small",null,lbl),element("strong",null,nfmt(n,1)+" "+unit));ms?.append(d)}
  plot(j.precip,j.hum,j.days);renderTable(j);renderConclusion(r,j,place);
  set("oaf-sm-metadato",`Datos de Open-Meteo consultados por OAF para ${place}: ${j.days[0]} a ${j.days.at(-1)}. Estos son insumos del proveedor, no un pronóstico fitosanitario validado por Random Forest. ${r.vigilancia}. Las conclusiones se basan en relaciones de literatura y requieren comprobación parcelaria. En Metadatos permanece el método completo.`);
 }catch(e){if(q!==sequence)return;set("oaf-sm-conclusion","Sin pronóstico verificable para esta localidad: "+e.message+". No se asigna un riesgo artificial.");set("oaf-sm-chart","Pronóstico temporalmente no disponible.");$("oaf-sm-datos")?.replaceChildren();$("oaf-sm-tabla")?.replaceChildren();}
}
function init(){
 if(!$("oaf-sanidad-ux11")||$("oaf-sanidad-ux11").dataset.ready)return;
 $("oaf-sanidad-ux11").dataset.ready="1";
 fetch("datos/sanidad_agroexportadora_2026.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()}).then(d=>{
  if(d.organismos?.length!==23||d.cultivos?.length!==6)throw Error("Catálogo científico incompleto");
  state.organisms=d.organismos;state.crops=d.cultivos;
  refill("oaf-sm-localidad",Object.keys(places).map(s=>[s,s]),"Chiclayo");
  for(const k of ["sm","mg"]){refill("oaf-"+k+"-cultivo",d.cultivos.map(c=>[c.id,c.nombre]),"mango");refill("oaf-"+k+"-tipo",[["todos","Todas"],["plaga","Plagas"],["enfermedad","Enfermedades"]],"todos");dependent(k);}
  $("oaf-sm-localidad").addEventListener("change",renderModel);
  for(const k of ["sm","mg"]){for(const prop of ["cultivo","tipo"]){$(`oaf-${k}-${prop}`).addEventListener("change",()=>{dependent(k);k==="sm"?renderModel():renderManage()})}
   $(`oaf-${k}-patogeno`).addEventListener("change",k==="sm"?renderModel:renderManage);
  }
  document.addEventListener("click",event=>{const a=event.target.closest?.('#oaf-home-six-crops .oaf-agro-crop-card');if(!a?.dataset.crop)return;const select=$("oaf-mg-cultivo");if(select){select.value=a.dataset.crop;dependent("mg");renderManage()}},true);
  renderManage();renderModel();
 }).catch(e=>{set("oaf-sm-conclusion","No se pudo cargar el catálogo científico: "+e.message);set("oaf-mg-title","Catálogo no disponible: "+e.message)});
}
document.addEventListener("oaf:ux11-ready",init);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
