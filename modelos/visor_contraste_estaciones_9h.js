/* OAF 9H: comparaciones mensuales observación versus productos externos.
   No muestra métricas cuando no existen pares, ni asigna validación independiente. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const fmt=(n,d=1)=>typeof n==="number"&&Number.isFinite(n)?
 n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
function node(type,text,cls){
 const el=document.createElement(type);if(text!==undefined)el.textContent=text;
 if(cls)el.className=cls;return el;
}
async function read(path){
 const response=await fetch(path,{cache:"no-store"});
 if(!response.ok)throw Error("archivo "+path+" HTTP "+response.status);
 return response.json();
}
function drawBars(parent,items,unit,label){
 const max=Math.max(1,...items.map(x=>x.score?.mae||0));
 const title=node("h4",label,"oaf-9h-plot-title");parent.append(title);
 for(const s of items){
  const wrap=node("div",undefined,"oaf-9h-line");
  const caption=node("div",undefined,"oaf-9h-label");
  caption.append(node("span",s.name),node("strong",s.score?fmt(s.score.mae,2)+" "+unit:"Sin datos suficientes"));
  wrap.append(caption);
  const track=node("div",undefined,"oaf-9h-track");
  const bar=node("div",undefined,"oaf-9h-bar");
  bar.style.width=s.score?(100*s.score.mae/max).toFixed(2)+"%":"0%";
  track.append(bar);wrap.append(track);
  parent.append(wrap);
 }
 parent.append(node("p","Barra = error absoluto medio (MAE). Menor valor no implica automáticamente mejor pronóstico o independencia del conjunto observado.","oaf-figure-caption"));
}
function details(report,summary,variable){
 const title=$("oaf-9h-current");title.replaceChildren();
 const site=$("oaf-9h-site").value;
 const candidate=$("oaf-9h-scenario").value;
 const blocks=$("oaf-9h-plot");blocks.replaceChildren();
 const chi=report.resumen_por_producto_y_escenario.filter(s=>s.codigo_archivo===site&&s.escenario===candidate);
 const supplemental=summary?.sintesis?.filter(s=>s.codigo_archivo===site&&s.escenario===candidate)||[];
 const p=supplemental.find(s=>s.producto==="ERA5_atmosferico"&&s.variable==="precipitation_sum");
 const mx=supplemental.find(s=>s.producto==="ERA5-Land_temperatura"&&s.variable==="temperature_2m_max");
 const mn=supplemental.find(s=>s.producto==="ERA5-Land_temperatura"&&s.variable==="temperature_2m_min");
 const ch=chi.find(s=>s.producto==="CHIRPS-v3 mensual LATAM");
 const base=report.sensibilidad_de_celdas.find(s=>s.codigo_archivo===site&&s.producto==="CHIRPS-v3 mensual LATAM");
 const labels=report.resumen_por_producto_y_escenario.find(x=>x.codigo_archivo===site)?.nombre||site;
 title.append(node("h3",labels+" · "+(candidate==="documental_1"?"Coordenada 1":"Coordenada 2")));
 const grid=node("div",undefined,"oaf-9h-indicators");
 const summaryCell=(heading,score,unit,sub)=>{
   const cell=node("article",undefined,"oaf-9h-number");
   cell.append(node("small",heading));
   cell.append(node("strong",score?fmt(score.mae,2)+" "+unit:"Sin pares"));
   cell.append(node("span",score?"MAE · "+score.n_meses+" meses · sesgo "+fmt(score.sesgo??score.sesgo_producto_menos_estacion_mm,2)+" "+unit:sub));
   grid.append(cell);
 };
 summaryCell("CHIRPS v3 · lluvia 1998",ch?.episodio_1998,"mm","Pendiente de extracción");
 summaryCell("ERA5 atmósfera · lluvia 1996–2013",p?.metricas_periodo,"mm","Sin meses pareados");
 summaryCell("ERA5-Land · temperatura máxima",mx?.metricas_periodo,"°C","Sin observaciones completas");
 summaryCell("ERA5-Land · temperatura mínima",mn?.metricas_periodo,"°C","Sin observaciones completas");
 title.append(grid);
 const compare=node("p","CHIRPS: "+(base?.mismo_centro_celda_entre_escenarios===true?
   "las dos ubicaciones documentales devuelven el mismo píxel; no son dos validaciones independientes.":
   base?.mismo_centro_celda_entre_escenarios===false?
   "las dos ubicaciones documentales usan píxeles diferentes, separados "+fmt(base.centros_separados_km,2)+" km.":"estado de celda no confirmado.")+
   " Los errores son retrospectivos y no equivalen a habilidad predictiva operativa.","oaf-figure-caption");
 title.append(compare);
 const pre=variable==="lluvia";
 if(pre){
  const all=[
   {name:"CHIRPS · 1998",score:ch?.episodio_1998?{mae:ch.episodio_1998.mae_mm}:null},
   {name:"ERA5 atmósfera · 1998",score:p?.metricas_1998},
   {name:"ERA5 atmósfera · 1996–2013",score:p?.metricas_periodo}
  ];
  drawBars(blocks,all,"mm","Comparación descriptiva de errores de precipitación — intervalos distintos");
 }else{
  drawBars(blocks,[
   {name:"ERA5-Land Tmax mensual",score:mx?.metricas_periodo},
   {name:"ERA5-Land Tmin mensual",score:mn?.metricas_periodo}
  ],"°C","Errores mensuales de temperatura a 2 m");
 }
 const text="CHIRPS 1998: "+report.n_pares_chirps+" pares totales de los seis escenarios."+
  " Complemento ERA5: "+(summary?.n_pares_era5_precipitacion??"pendiente")+
  " pares de precipitación y "+(summary?.n_pares_era5_land_temperatura??"pendiente")+
  " pares de temperatura. No sumar escenarios como observaciones independientes.";
 $("oaf-9h-overview").textContent=text;
}
async function init(){
 if(!$("oaf-9h-visor"))return;
 const [r,s]=await Promise.allSettled([
  read("datos/validacion_estaciones_9h/comparacion_observacional_9h.json"),
  read("datos/validacion_estaciones_9h/contraste_era5_complementario_9h.json")
 ]);
 if(r.status!=="fulfilled"||r.value.fase!=="9H")throw Error("Falta contraste de CHIRPS auditado");
 const main=r.value;
 const other=s.status==="fulfilled"&&s.value.fase==="9H"?s.value:null;
 const select=$("oaf-9h-site");
 const sites=new Map();
 for(const entry of main.resumen_por_producto_y_escenario)
  sites.set(entry.codigo_archivo,entry.nombre);
 for(const [id,name] of sites){
  const opt=node("option",name);opt.value=id;select.append(opt);
 }
 select.value="00153114";
 const show=()=>details(main,other,$("oaf-9h-kind").value);
 for(const control of ["oaf-9h-site","oaf-9h-scenario","oaf-9h-kind"])
  $(control).addEventListener("change",show);
 show();
 $("oaf-9h-state").textContent=other?
  "Fuentes rastreables y periodos verificados; las comparaciones son exploratorias y sin certificación del emplazamiento histórico.":
  "CHIRPS verificado; las temperaturas/lluvia ERA5 complementarias todavía no están disponibles en el repositorio.";
}
const run=()=>init().catch(error=>{
 if($("oaf-9h-state"))$("oaf-9h-state").textContent="No se puede cargar el contraste: "+error.message+
 ". No se publican métricas faltantes.";
});
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);
else run();
})();