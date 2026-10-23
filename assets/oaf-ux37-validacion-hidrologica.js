/* OAF-Lambayeque UX37 · Auditoría hidrométrica y evaluación de modelos.
 * Solo procesa CSV local con caudales observados y simulados proporcionados por la
 * persona usuaria. No simula valores, no consume API PHISIS/PEOT ni emite alertas.
 */
(function(){"use strict";
const $=id=>document.getElementById(id);
const mk=(tag,cls)=>{const x=document.createElement(tag);if(cls)x.className=cls;return x};
const REQUIRED=["fecha","rio","estacion","latitud","longitud","caudal_observado_m3s",
"caudal_simulado_m3s","fuente","modelo","fecha_descarga"];
const TEMPLATE="datos/hidrologia_ux37/plantilla_validacion_caudales.csv";
const fmt=(v,n=2)=>Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:n,minimumFractionDigits:n}):"No calculable";
const normalize=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().trim();
const state={records:[],errors:[],duplicates:0,gaps:0,span:0,coverage:0,ready:false,source:"",metadata:{},quality:"sin archivo",validated:false};
const endpoints=[
 ["SENAMHI · PHISIS","https://www.gob.pe/21712-consultar-la-informacion-hidrologica-peruana-en-la-plataforma-phisis-consultar-el-monitoreo-hidrologico-de-los-rios-peruanos"],
 ["PEOT · Sistema Hidrológico Tinajones","https://www.gob.pe/40915-acceder-al-sistema-de-informacion-hidrologica-tinajones"],
 ["Método y límites UX37","https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_VALIDACION_HIDROLOGICA_UX37.md"]
];
function label(){
 const group=$("oaf-ux37-group");if(!group)return;
 group.querySelector("summary").textContent="7 · Validación de series y modelos hidrológicos";
}
function build(){
 const container=$("oaf-ux29-scenario");
 if(!container||$("oaf-ux37-panel"))return false;
 const panel=mk("section","oaf-ux37-panel");panel.id="oaf-ux37-panel";
 panel.innerHTML='<header><span class="oaf-ux37-kicker">UX37 · Hidrología cuantitativa · Control de calidad</span>'+
 '<h2>Validación de caudales observados y simulados</h2>'+
 '<p>Importa una serie diaria con <b>caudal observado y caudal simulado</b>, la misma estación, coordenadas y procedencia. El procesamiento es local: no se transmiten archivos al OAF ni se publican en GitHub.</p></header>'+
 '<div class="oaf-ux37-actions"><button type="button" id="oaf-ux37-load">Importar CSV con datos reales</button>'+
 '<input id="oaf-ux37-file" type="file" accept=".csv,text/csv" hidden />'+
 '<a href="'+TEMPLATE+'" download>Descargar plantilla CSV vacía</a>'+
 '<button type="button" id="oaf-ux37-clear" class="oaf-ux37-secondary">Limpiar resultados</button></div>'+
 '<p class="oaf-ux37-status" id="oaf-ux37-status" role="status">No se han importado mediciones. No hay resultados de calibración ni validación.</p>'+
 '<div id="oaf-ux37-metadata" class="oaf-ux37-metadata" hidden></div>'+
 '<div id="oaf-ux37-quality" class="oaf-ux37-quality" aria-live="polite"></div>'+
 '<div id="oaf-ux37-results" class="oaf-ux37-results" hidden></div>'+
 '<div id="oaf-ux37-plot" class="oaf-ux37-plot" hidden></div>'+
 '<div class="oaf-ux37-sources"><strong>Obtener observaciones y documentar el origen:</strong> '+
 endpoints.map(([title,href])=>'<a href="'+href+'" target="_blank" rel="noopener noreferrer">'+title+' ↗</a>').join(" · ")+
 '<p>Una serie importada no queda certificada por OAF. Las métricas describen concordancia entre dos series, no la seguridad de una infraestructura ni el riesgo de inundación de un distrito.</p></div>';
 const target=$("oaf-ux36-panel")||container.querySelector(".oaf-ux29-mapcontent");
 if(target?.id==="oaf-ux36-panel")target.after(panel);else target?.append(panel);
 const tree=container.querySelector(".oaf-ux29-tree");
 if(tree&&!$("oaf-ux37-group")){
  const div=mk("details","oaf-ux35-group oaf-ux37-group");div.id="oaf-ux37-group";div.open=false;
  const sum=mk("summary");div.append(sum);
  const p=mk("p");p.textContent="Comparar series diarias de caudal con control de calidad y métricas hidrológicas. La validación no se activa sin datos emparejados y trazabilidad.";
  div.append(p);
  const b=mk("button");b.type="button";b.textContent="Ir al panel de validación";
  b.addEventListener("click",()=>panel.scrollIntoView({block:"start",behavior:"smooth"}));
  div.append(b);
  const filters=[...tree.querySelectorAll("details")].find(x=>x.querySelector("summary")?.textContent?.includes("Filtros"));
  if(filters)filters.before(div);else tree.append(div);
  label();
 }
 const file=$("oaf-ux37-file");
 $("oaf-ux37-load").addEventListener("click",()=>file.click());
 file.addEventListener("change",async()=>{
  if(file.files?.length)await importFile(file.files[0]);file.value="";
 });
 // Resolver enlaces directos cuando el panel se inserta dinámicamente.
 if(location.hash==="#oaf-ux37-panel")window.dispatchEvent(new Event("hashchange"));
 $("oaf-ux37-clear").addEventListener("click",()=>{
  reset();$("oaf-ux37-status").textContent="Resultados y registros eliminados del navegador. No hay mediciones cargadas.";
 });
 return true;
}
function reset(){
 state.records=[];state.errors=[];state.duplicates=0;state.gaps=0;state.span=0;
 state.coverage=0;state.ready=false;state.source="";state.metadata={};state.quality="sin archivo";
 for(const id of ["oaf-ux37-metadata","oaf-ux37-results","oaf-ux37-plot"]){
  const x=$(id);if(x){x.replaceChildren();x.hidden=true}
 }
 const q=$("oaf-ux37-quality");if(q)q.replaceChildren();
}
function splitCSV(line,sep){
 const cells=[],acc=[];let quoted=false;
 for(let i=0;i<line.length;i++){
  const c=line[i];
  if(c==='"'){
   if(quoted&&line[i+1]==='"'){acc.push('"');i++}else quoted=!quoted;
  }else if(c===sep&&!quoted){cells.push(acc.join("").trim());acc.length=0}
  else acc.push(c);
 }
 cells.push(acc.join("").trim());
 if(quoted)throw Error("Fila CSV con comillas sin cerrar");
 return cells;
}
function parseCSV(content){
 const lines=content.replace(/^\uFEFF/,"").split(/\r?\n/).filter(s=>s.trim());
 if(lines.length<2)throw Error("El CSV no contiene observaciones.");
 if(lines.length>25001)throw Error("Se admiten como máximo 25 000 registros.");
 const sep=lines[0].includes(";")?";":",";
 const header=splitCSV(lines[0],sep).map(x=>normalize(x));
 const fields=new Set(header);
 for(const col of REQUIRED)if(!fields.has(col))throw Error("Falta la columna requerida: "+col);
 const rows=[];
 for(let n=1;n<lines.length;n++){
  const values=splitCSV(lines[n],sep);
  if(values.length!==header.length)throw Error("Número de columnas incorrecto en la fila "+(n+1));
  const p=Object.fromEntries(header.map((key,i)=>[key,values[i]]));
  p._row=n+1;rows.push(p);
 }
 return rows;
}
function iso(s){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(s))return null;
 const [y,m,d]=s.split("-").map(Number);
 const date=new Date(Date.UTC(y,m-1,d));
 return date.getUTCFullYear()===y&&date.getUTCMonth()===m-1&&date.getUTCDate()===d?date:null;
}
function decimal(s){
 if(s===null||s===undefined||String(s).trim()==="")return null;
 const text=String(s).trim().replace(",",".");
 if(!/^[+-]?(?:\d+(?:\.\d+)?|\.\d+)$/.test(text))return NaN;
 return Number(text);
}
function parseDateWithUTC(raw){
 const d=iso(raw);if(!d)return null;
 const today=new Date(),end=Date.UTC(today.getFullYear(),today.getMonth(),today.getDate());
 if(d.getTime()>end)return null;
 return d;
}
function riverName(raw){
 const n=normalize(raw);
 if(n==="leche"||n==="la leche"||n==="rio la leche")return "La Leche";
 if(n==="chancay"||n==="chancay-lambayeque"||n==="chancay–lambayeque"||n==="chancay lambayeque"||n==="rio chancay"||n==="rio chancay lambayeque")return "Chancay–Lambayeque";
 if(n==="zana"||n==="rio zana")return "Zaña";
 return null;
}
function validate(rows){
 const valid=[],errors=[],seen=new Set();
 let duplicates=0,first=null;
 for(const row of rows){
  const issue=[],date=parseDateWithUTC(row.fecha),download=parseDateWithUTC(row.fecha_descarga);
  const river=riverName(row.rio),station=String(row.estacion||"").trim();
  const lat=decimal(row.latitud),lon=decimal(row.longitud);
  const observed=decimal(row.caudal_observado_m3s),simulated=decimal(row.caudal_simulado_m3s);
  if(!date)issue.push("fecha inválida o futura");
  if(!download)issue.push("fecha_descarga inválida o futura");
  else if(date&&download<date)issue.push("descarga anterior a la observación");
  if(!river)issue.push("río no reconocido");
  if(!station)issue.push("sin estación");
  if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat<-19||lat>0||lon<-83||lon>-68)issue.push("coordenadas fuera de Perú");
  if(observed===null||!Number.isFinite(observed)||observed<0||observed>1000000)issue.push("caudal observado inválido");
  if(simulated===null||!Number.isFinite(simulated)||simulated<0||simulated>1000000)issue.push("caudal simulado inválido");
  if(!String(row.fuente||"").trim())issue.push("sin fuente");
  if(!String(row.modelo||"").trim())issue.push("sin identificación del modelo");
  const id=[river,normalize(station),row.fecha].join("|");
  if(seen.has(id)){duplicates++;issue.push("fecha duplicada en la misma estación")}else seen.add(id);
  if(!first&&issue.length===0)first={river,station,lat,lon,source:row.fuente,model:row.modelo,download:row.fecha_descarga};
  if(first&&issue.length===0){
   if(river!==first.river||normalize(station)!==normalize(first.station)||String(row.modelo).trim()!==String(first.model).trim())issue.push("mezcla de río, estación o modelo");
   if(Math.abs(lat-first.lat)>.005||Math.abs(lon-first.lon)>.005)issue.push("coordenadas inconsistentes para la estación");
   if(String(row.fuente).trim()!==String(first.source).trim())issue.push("fuente cambiante en el mismo archivo");
  }
  if(issue.length){errors.push({row:row._row,reasons:issue});continue}
  valid.push({date,iso:row.fecha,obs:observed,sim:simulated});
 }
 valid.sort((a,b)=>a.date-b.date);
 const span=valid.length?1+Math.round((valid.at(-1).date-valid[0].date)/86400000):0;
 const gaps=Math.max(0,span-valid.length),coverage=span?valid.length/span:0;
 return {valid,errors,duplicates,gaps,span,coverage,first};
}
function mean(a){return a.reduce((s,v)=>s+v,0)/a.length}
function metrics(rows){
 if(rows.length<2)return null;
 const obs=rows.map(r=>r.obs),sim=rows.map(r=>r.sim),n=rows.length;
 const mo=mean(obs),ms=mean(sim),ss=obs.reduce((s,v)=>s+(v-mo)**2,0);
 const sso=Math.sqrt(ss/n),sss=Math.sqrt(sim.reduce((s,v)=>s+(v-ms)**2,0)/n);
 if(!(ss>1e-10)||!(sso>0)||!(sss>0)||!(mo>0))return null;
 let se=0,ae=0,delta=0,cov=0;
 for(let i=0;i<n;i++){
  const d=sim[i]-obs[i];se+=d*d;ae+=Math.abs(d);delta+=d;cov+=(obs[i]-mo)*(sim[i]-ms);
 }
 const rmse=Math.sqrt(se/n),mae=ae/n,nse=1-se/ss;
 const pearson=cov/(n*sso*sss),alpha=sss/sso,beta=ms/mo;
 const kge=1-Math.hypot(pearson-1,alpha-1,beta-1);
 const maxO=rows.reduce((a,b)=>b.obs>a.obs?b:a);
 const maxS=rows.reduce((a,b)=>b.sim>a.sim?b:a);
 return {n,rmse,mae,nse,kge,pearson,pbias:delta/obs.reduce((a,b)=>a+b,0)*100,
  meanObserved:mo,meanSimulated:ms,
  peakObserved:maxO.obs,peakSimulated:maxS.sim,peakObservedDate:maxO.iso,peakSimulatedDate:maxS.iso,
  peakLagDays:Math.round((maxS.date-maxO.date)/86400000)};
}
function pairQuality(a){
 const hasBasic=a.valid.length>=30&&a.span>=30;
 // 80% daily coverage: exploratory threshold; no guarantee of statistical validity.
 const highCoverage=a.coverage>=.8;
 return {eligible:hasBasic&&highCoverage,reason:!hasBasic?
  "Se requieren al menos 30 días de registro y 30 pares válidos en una estación.":!highCoverage?
  "La cobertura diaria es inferior a 80 %; revisa los períodos faltantes.":""};
}
function metricTile(title,value,detail){
 const tile=mk("article");
 const h=mk("small");h.textContent=title;
 const v=mk("strong");v.textContent=value;
 const d=mk("span");d.textContent=detail;
 tile.append(h,v,d);return tile;
}
function renderQuality(a){
 const host=$("oaf-ux37-quality");if(!host)return;
 host.replaceChildren();
 const p=mk("p");
 p.textContent=a.valid.length+" pares válidos · "+a.errors.length+" filas descartadas · "+
 a.duplicates+" duplicados · "+a.gaps+" días ausentes · "+
 fmt(a.coverage*100,1)+" % de cobertura diaria en "+a.span+" días.";
 host.append(p);
 if(a.errors.length){
  const details=mk("details");const summary=mk("summary");
  summary.textContent="Revisar filas descartadas ("+a.errors.length+")";details.append(summary);
  const list=mk("ul");
  for(const e of a.errors.slice(0,25)){
   const li=mk("li");li.textContent="Fila "+e.row+": "+e.reasons.join("; ");list.append(li);
  }
  if(a.errors.length>25){const last=mk("li");last.textContent="Se muestran las primeras 25 filas descartadas.";list.append(last)}
  details.append(list);host.append(details);
 }
}
function drawChart(records){
 const root=$("oaf-ux37-plot");if(!root||!records.length)return;
 root.replaceChildren();root.hidden=false;
 const title=mk("strong");title.textContent="Serie diaria comparada (observado y simulado, m³/s)";
 root.append(title);
 const width=680,height=255,margin={left:53,right:18,top:18,bottom:38};
 const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
 svg.setAttribute("viewBox","0 0 "+width+" "+height);svg.setAttribute("role","img");
 svg.setAttribute("aria-label","Evolución de caudales observados y simulados para el archivo importado");
 const tag=(name,attrs)=>{const n=document.createElementNS("http://www.w3.org/2000/svg",name);
  for(const [k,v] of Object.entries(attrs||{}))n.setAttribute(k,String(v));return n};
 let maxVal=1;
 for(const r of records)maxVal=Math.max(maxVal,r.obs,r.sim);
 // Resumir solo trazado si el archivo es grande; las métricas usan todos los registros.
 const visual=records.length>1100?records.filter((r,i)=>i%Math.ceil(records.length/1000)===0||i===records.length-1):records;
 const x=i=>margin.left+i/Math.max(1,visual.length-1)*(width-margin.left-margin.right);
 const y=v=>height-margin.bottom-v/maxVal*(height-margin.top-margin.bottom);
 for(let i=0;i<=4;i++){
  const val=maxVal*i/4,yy=y(val);
  svg.append(tag("line",{x1:margin.left,y1:yy,x2:width-margin.right,y2:yy,stroke:"#d9e5e3","stroke-width":1}));
  const label=tag("text",{x:margin.left-7,y:yy+4,"text-anchor":"end","font-size":11,fill:"#52736a"});
  label.textContent=fmt(val,0);svg.append(label);
 }
 function line(key,color){
  const path=tag("path",{d:visual.map((r,i)=>(i?"L":"M")+x(i).toFixed(1)+" "+y(r[key]).toFixed(1)).join(" "),
   fill:"none",stroke:color,"stroke-width":2,"stroke-linejoin":"round","stroke-linecap":"round"});
  svg.append(path);
 }
 line("obs","#1874a0");line("sim","#dd8939");
 for(const [xpos,t] of [[margin.left,records[0].iso],[width-margin.right,records.at(-1).iso]]){
  const lab=tag("text",{x:xpos,y:height-12,"text-anchor":xpos===margin.left?"start":"end","font-size":11,fill:"#4e685d"});
  lab.textContent=t;svg.append(lab);
 }
 root.append(svg);
 const legend=mk("p");legend.textContent="Azul: caudal observado · Naranja: caudal simulado · Fecha local proporcionada en el CSV";
 root.append(legend);
}
function present(a){
 state.records=a.valid;state.errors=a.errors;state.duplicates=a.duplicates;
 state.gaps=a.gaps;state.span=a.span;state.coverage=a.coverage;state.metadata=a.first||{};
 renderQuality(a);
 const metadata=$("oaf-ux37-metadata");metadata.replaceChildren();metadata.hidden=false;
 const p=mk("p");p.textContent=a.first?
  "Río: "+a.first.river+" · Estación: "+a.first.station+" · Coordenadas: "+
  fmt(a.first.lat,4)+", "+fmt(a.first.lon,4)+" · Modelo: "+a.first.model+
  " · Fuente declarada: "+a.first.source+" · Fecha de descarga declarada: "+a.first.download:
  "No se identificó una estación válida.";
 metadata.append(p);
 const gate=pairQuality(a),result=$("oaf-ux37-results");
 result.replaceChildren();result.hidden=false;
 if(!gate.eligible){
  const msg=mk("p","oaf-ux37-warning");msg.textContent="Evaluación no habilitada: "+gate.reason+
   " No se generan puntuaciones a partir de una muestra insuficiente.";result.append(msg);
  $("oaf-ux37-plot").replaceChildren();$("oaf-ux37-plot").hidden=true;return;
 }
 const overall=metrics(a.valid);
 if(!overall){
  const msg=mk("p","oaf-ux37-warning");
  msg.textContent="La serie observada o simulada es constante/cero. No se calculan NSE/KGE sin variabilidad suficiente.";
  result.append(msg);$("oaf-ux37-plot").hidden=true;return;
 }
 // 70/30 cut in chronological order: exploratory score, NOT independent if model trained on these dates.
 const split=Math.floor(a.valid.length*.7);
 const recent=metrics(a.valid.slice(split));
 const title=mk("h3");title.textContent="Indicadores descriptivos de comparación";result.append(title);
 const grid=mk("div","oaf-ux37-kpis");
 for(const [k,v,d] of [
  ["NSE",fmt(overall.nse,3),"1 es ajuste perfecto; puede ser negativo"],
  ["KGE (2009)",fmt(overall.kge,3),"Correlación, variabilidad y sesgo"],
  ["RMSE",fmt(overall.rmse,2)+" m³/s","Error cuadrático medio"],
  ["MAE",fmt(overall.mae,2)+" m³/s","Error absoluto medio"],
  ["PBIAS",fmt(overall.pbias,2)+" %","Positivo: sobreestimación media"],
  ["Desfase de picos",String(overall.peakLagDays)+" días","Diferencia entre máximos del período"]
 ])grid.append(metricTile(k,v,d));
 result.append(grid);
 const meta=mk("p","oaf-ux37-summary");
 meta.textContent="Pico observado "+fmt(overall.peakObserved,2)+" m³/s ("+overall.peakObservedDate+") · "+
 "Pico simulado "+fmt(overall.peakSimulated,2)+" m³/s ("+overall.peakSimulatedDate+"). "+
 "El desempeño no confirma capacidad de pronóstico de crecidas sin validación externa.";
 result.append(meta);
 const hold=mk("p","oaf-ux37-holdout");
 hold.textContent="Bloque cronológico final (30 % de la serie, "+(a.valid.length-split)+
 " registros): "+(recent?"NSE "+fmt(recent.nse,3)+" · KGE "+fmt(recent.kge,3)+" · RMSE "+
 fmt(recent.rmse,2)+" m³/s.":"no calculable por variabilidad insuficiente.")+
 " Este tramo NO es una validación independiente si los mismos días participaron en el entrenamiento o la selección del modelo.";
 result.append(hold);
 state.ready=true;drawChart(a.valid);
}
async function importFile(file){
 reset();
 const status=$("oaf-ux37-status");
 if(!file.name.toLowerCase().endsWith(".csv")){status.textContent="Selecciona un archivo .csv.";return}
 if(file.size>3*1024*1024){status.textContent="Archivo demasiado grande: máximo 3 MB.";return}
 try{
  status.textContent="Analizando registros locales y comprobando fechas, unidades y metadatos…";
  const text=await file.text(),rows=parseCSV(text);
  const validation=validate(rows);
  status.textContent="CSV procesado localmente. "+validation.valid.length+" pares aceptados; "+
   validation.errors.length+" filas descartadas. Fuente y calibración no verificadas por OAF.";
  present(validation);
 }catch(error){status.textContent="No se pudo evaluar el CSV: "+error.message}
}
function init(){
 let count=0;
 const retry=()=>{
  if(build())return;
  if(++count<30)setTimeout(retry,300);
 };
 retry();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();