/* OAF UX76 · 3 fuentes fijas y liderazgo respaldado por errores comprobados.
 * ERA5 es reanalisis/climatologia, NO pronostico numerico futuro.
 * Nunca confundir desacuerdo entre pronosticos con MAE observado.
 * PWA y web comparten el mismo modulo.
 */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const modelMeta=[
 {id:"era5",name:"ERA5",kind:"Referencia climatológica histórica",color:"#31946e"},
 {id:"open",name:"Open-Meteo",kind:"Pronóstico meteorológico",color:"#278eb8"},
 {id:"rf",name:"Random Forest",kind:"Pronóstico experimental OAF",color:"#aa65b4"}
];
const state={benchmark:null,history:null,benchmarkError:null,historyError:null,weekly:null,monthly:null,loading:false};
const E=(tag,cls,txt)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(txt!==undefined)x.textContent=String(txt);return x};
const fmt=(n,d=2)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"Pendiente";
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:NaN;
function safe(v){return Number.isFinite(v)&&v>=0?v:null;}
function dailyBenchmark(variable,year){
 const metric=variable==="rain"?"rain":"temp";
 const report=state.benchmark?.pruebas?.[String(year)];
 if(report?.origenes<24)return null;
 const inc=report.metricas?.incumbente?.[metric]?.mae;
 const era=report.metricas?.climatologia?.[metric]?.mae;
 const candidate=report.metricas?.direct?.[metric]?.mae;
 if(![inc,era,candidate].every(Number.isFinite))return null;
 return {year,sample:report.origenes,rf:inc,era5:era,experimental: candidate,
         leader:inc<era?"RF incumbente":era<inc?"ERA5 (climatología)":"Empate"};
}
/* Para el mismo conjunto de emisiones completas, todos los competidores
 * deben disponer de los 7 dias, sin promediar sobre distintas muestras.
 */
function prospective(city,variable){
 const key=variable==="rain"?"mae_lluvia_mm":"mae_tmax_c";
 const rows=[];
 for(const entry of state.history?.emisiones||[]){
  const x=entry?.verificacion_era5?.por_localidad?.[city];
  if(!x||x.dias!==7)continue;
  const era=safe(x.era5_climatologia?.[key]);
  const open=safe(x.open_meteo?.[key]);
  const rf=safe(x.rf?.[key]);
  if([era,open,rf].some(v=>v===null))continue;
  rows.push({date:entry.fecha_local,era,open,rf});
 }
 if(!rows.length)return {n:0,status:"sin evaluaciones de tres fuentes comparables"};
 const result={n:rows.length,era5:mean(rows.map(r=>r.era)),
             open:mean(rows.map(r=>r.open)),rf:mean(rows.map(r=>r.rf))};
 const names=[{name:"ERA5",mae:result.era5},{name:"Open-Meteo",mae:result.open},
              {name:"Random Forest",mae:result.rf}].sort((a,b)=>a.mae-b.mae);
 result.leader=names[0].name;
 result.second=names[1].name;
 result.gap=names[1].mae-names[0].mae;
 result.eligible=rows.length>=14;
 result.status=result.eligible?"líder provisional de emisiones verificadas":"muestra insuficiente para declarar liderazgo";
 return result;
}
function ensure(section){
 const chart=$(section==="weekly"?"oaf-ux14-weekchart":"oaf-ux14-monthchart");
 const status=$(section==="weekly"?"oaf-ux14-weekstatus":"oaf-ux14-monthstatus");
 if(!chart||!status)return null;
 const id="oaf-ux76-"+section+"-ranking";
 let box=$(id);
 if(!box){
  box=E("section","oaf-ux76-ranking");
  box.id=id;box.setAttribute("aria-label","Comparación de precisión de tres referencias");
  box.append(E("h3",null,"Comparador permanente · ERA5 / Open-Meteo / Random Forest"));
  const cards=E("div","oaf-ux76-cards");cards.id=id+"-cards";box.append(cards);
  const winner=E("p","oaf-ux76-result");winner.id=id+"-result";box.append(winner);
  const detail=E("p","oaf-ux76-method");detail.id=id+"-method";box.append(detail);
  status.after(box);
 }
 return box;
}
function display(section,payload){
 const box=ensure(section);if(!box)return;
 const cards=$(box.id+"-cards");cards.replaceChildren();
 const vals=section==="weekly"?
   {era5:payload.era5,open:payload.open,rf:payload.rf}:
   {era5:payload.era5,open:payload.open,rf:payload.rf};
 const period=section==="weekly"?"/7 días":"/6 meses";
 for(const meta of modelMeta){
  const card=E("div","oaf-ux76-model"),head=E("strong",null,meta.name);
  card.style.borderTop="4px solid "+meta.color;
  const subtitle=E("small",null,meta.kind);
  const list=Array.isArray(vals[meta.id])?vals[meta.id]:[];
  const found=list.filter(Number.isFinite).length;
  const reading=E("span","oaf-ux76-reading",found+" "+period+" con datos"+(found?" · "+(section==="weekly"?"serie diaria":"serie mensual"):""));
  card.append(head,subtitle,reading);cards.append(card);
 }
 const result=$(box.id+"-result"),method=$(box.id+"-method");
 const loc=payload.city||"Lambayeque";
 const name=payload.variable==="rain"?"lluvia":"temperatura";
 if(section==="monthly"){
  result.textContent="Modelo más certero en los tres: aún sin prueba mensual prospectiva comparable. Los tres se mantienen en el gráfico para contrastar escenarios.";
  method.textContent="Localidad: "+loc+" · "+name+
   ". ERA5 = promedio 1996–2020, no predicción. Open-Meteo = ECMWF SEAS5 estacional; RF = candidato experimental. Las comparaciones retrospectivas no autorizan un ranking entre los tres.";
  return;
 }
 if(payload.point){
  result.textContent="Precisión en esta parcela: sin validación local para comparar los tres.";
  method.textContent="ERA5 es la referencia histórica del punto. Open-Meteo es el pronóstico disponible; RF solo se emite para las cuatro localidades entrenadas. No se extrapolan sus resultados a parcelas.";
  return;
 }
 const v2025=dailyBenchmark(payload.variable,2025);
 const v2026=dailyBenchmark(payload.variable,2026);
 const now=prospective(loc,payload.variable);
 if(now.eligible){
  result.textContent="Menor error en emisiones verificadas: "+now.leader+" (MAE "+fmt(now[now.leader==="ERA5"?"era5":now.leader==="Open-Meteo"?"open":"rf"])+
   (payload.variable==="rain"?" mm/día":" °C")+"). Liderazgo provisional, "+now.n+" emisiones de 7 días.";
 }else{
  result.textContent="Modelo más certero entre los tres: aún no determinable. "+(v2026?"En la prueba retrospectiva 2026, entre ERA5 y RF, tuvo menor MAE "+v2026.leader+".":"Esperando evaluación retrospectiva.");
 }
 method.textContent=(v2026?
  "Retrospectiva regional 2026 ("+v2026.sample+" orígenes): MAE ERA5 "+fmt(v2026.era5)+
  ", RF publicado "+fmt(v2026.rf)+", RF nuevo experimental "+fmt(v2026.experimental)+
  (payload.variable==="rain"?" mm/día.":" °C."):"Sin resultados comparables de 2026.")+
  (v2025?" En 2025 ganó "+v2025.leader+" entre ERA5 y RF.":"")+
  " Open-Meteo requiere pronósticos guardados antes de los eventos y contraste posterior. "+(now.n?
    "Emisiones con tres vías verificadas: "+now.n+".":"Todavía no hay emisiones con tres vías verificadas.")+
  " ERA5 = climatología histórica, no pronóstico futuro. La verificación disponible es ERA5 de reanálisis, no estaciones.";
}
function renderWeekly(payload){
 if(!payload||!Array.isArray(payload.dates)||payload.dates.length!==7)return;
 state.weekly=payload;display("weekly",payload);
}
function renderMonthly(payload){
 if(!payload||!Array.isArray(payload.months)||payload.months.length!==6)return;
 state.monthly=payload;display("monthly",payload);
}
function refresh(){
 if(state.weekly)display("weekly",state.weekly);
 if(state.monthly)display("monthly",state.monthly);
}
async function load(url,validator){
 const response=await fetch(url,{cache:"no-store"});
 if(!response.ok)throw Error("HTTP "+response.status);
 const value=await response.json();if(!validator(value))throw Error("Formato no validado");
 return value;
}
async function init(){
 if(state.loading)return;state.loading=true;
 await Promise.all([
  load("datos/rf_experimento_ux75/evaluacion_reentrenamiento.json",
       v=>v?.estado==="evaluacion_completa"&&!!v?.pruebas?.["2026"])
  .then(v=>{state.benchmark=v;state.benchmarkError=null})
  .catch(e=>{state.benchmarkError=String(e.message||e)}),
  load("datos/seguimiento_rf_ux74/emisiones.json",
       v=>v?.version==="UX74"&&Array.isArray(v.emisiones))
  .then(v=>{state.history=v;state.historyError=null})
  .catch(e=>{state.historyError=String(e.message||e)})
 ]);
 state.loading=false;refresh();
}
window.OAFModelCompareUX76={
 renderWeekly,renderMonthly,refresh,load:init,
 dailyBenchmark,prospective,
 getStatus:()=>({benchmark:!!state.benchmark,history:!!state.history,
  benchmarkError:state.benchmarkError,historyError:state.historyError})
};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
else init();
})();