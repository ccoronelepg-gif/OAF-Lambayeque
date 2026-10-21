(function boletines11(){
"use strict";
const $=id=>document.getElementById(id),SVG="http://www.w3.org/2000/svg";
const el=(tag,text,cls)=>{const q=document.createElement(tag);if(cls)q.className=cls;if(text!==undefined)q.textContent=text;return q};
const set=(id,t)=>{if($(id))$(id).textContent=t};
const full=path=>fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return /csv$/.test(path)?r.text():r.json()});
const num=x=>Number(x).toLocaleString("es-PE",{minimumFractionDigits:2,maximumFractionDigits:2});
function chartFrom(records){
 const root=$("oaf-bol-chart");if(!root)return;const n=Number($("oaf-bol-periodo")?.value||24);
 const months=records.slice(-n);if(months.length!==n){set("oaf-bol-chart","La serie no contiene suficientes meses válidos para ese periodo.");return}
 const W=740,H=295,L=53,R=14,T=22,B=52,values=months.map(x=>x.v),min=Math.min(-1,...values)-.3,max=Math.max(1,...values)+.4,x=i=>L+(i+.5)*(W-L-R)/months.length, y=v=>T+(max-v)/(max-min)*(H-T-B);
 const s=(name,attrs={},txt)=>{const n=document.createElementNS(SVG,name);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(txt!==undefined)n.textContent=txt;return n};
 const graph=s("svg",{viewBox:`0 0 ${W} ${H}`,role:"img","aria-label":"Anomalías mensuales NOAA NCEI ERSSTv5 de Niño 1+2 con base 1991–2020"});
 for(let i=0;i<=4;i++){let value=min+(max-min)*i/4,Y=y(value);graph.append(s("line",{x1:L,y1:Y,x2:W-R,y2:Y,class:"gridline"}));graph.append(s("text",{x:L-6,y:Y+4,"text-anchor":"end",class:"axis"},num(value)))}
 graph.append(s("line",{x1:L,y1:y(0),x2:W-R,y2:y(0),stroke:"#718f85","stroke-width":1.7}));
 months.forEach((r,i)=>{const yy=y(r.v),base=y(0),q=s("rect",{x:x(i)-Math.max(8,(W-L-R)/months.length*.64)/2,y:Math.min(base,yy),width:Math.max(8,(W-L-R)/months.length*.64),height:Math.max(1,Math.abs(base-yy)),rx:4,tabindex:0,role:"button","aria-label":r.m+" anomalía "+num(r.v)+" grados Celsius",fill:r.v>=1?"#bd513f":r.v>=0?"#e59063":r.v<=-1?"#316996":"#67a9ce"});q.append(s("title",{},r.m+" · "+num(r.v)+" °C"));
 const detail=()=>set("oaf-bol-grafico-dato","Mes "+r.m+": "+num(r.v)+" °C respecto de la base 1991–2020. "+(r.v>0?"Anomalía positiva (más cálido)":r.v<0?"Anomalía negativa (más frío)":"Sin anomalía")+". No representa pronóstico local.");
 q.addEventListener("click",detail);q.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();detail()}});graph.append(q);
 if(i%Math.max(1,Math.round(n/6))===0||i===months.length-1)graph.append(s("text",{x:x(i),y:H-20,"text-anchor":"middle",class:"axis"},r.m.slice(2)))});
 root.replaceChildren(graph);const last=months.at(-1);set("oaf-bol-grafico-dato","Último mes en la serie archivada: "+last.m+" · anomalía "+num(last.v)+" °C. Barras rojas: cálido; azules: frío. Haz clic o pulsa Tab en cada barra.");
}
function render(data){
 const grid=$("oaf-boletines-tarjetas");if(!grid)return;grid.replaceChildren();
 for(const b of data.boletines){
 const article=el("article",undefined,"oaf-ux11-institution");
 const chip=el("span",b.institucion+" · "+b.tipo,"oaf-ux11-badge "+(b.institucion==="ENFEN"?"":"blue")),h=el("h3",b.titulo),date=el("small",b.fecha?`Publicado ${b.fecha}`:"Portal con fechas propias; verificar cada aviso"),
 p=el("p",b.resumen),sign=el("p","Para el agricultor: "+b.implicacion),a=el("a","Abrir publicación del organismo ↗");
 a.href=b.url;a.target="_blank";a.rel="noopener noreferrer";article.append(chip,h,date,p,sign,a);grid.append(article);
 }
 set("oaf-bol-conclusion",data.conclusion_general);
 set("oaf-bol-corte",data.edicion||"Verificar fecha del comunicado");
 const timeline=$("oaf-bol-evolucion");
 if(timeline){
  timeline.replaceChildren();
  for(const e of data.evolucion||[]){
   const card=el("article",undefined,"oaf-ux11-timeline-item");
   const date=el("time",e.fecha);date.dateTime=e.fecha;
   const heading=el("strong",e.etiqueta+" · "+e.estado);
   const description=el("p",e.detalle);
   const anchor=el("a","Ver comunicado ↗");anchor.href=e.url;anchor.target="_blank";anchor.rel="noopener noreferrer";
   card.append(date,heading,description,anchor);timeline.append(card);
  }
 }
 const summaries=$("oaf-bol-mensajes");if(summaries){
  summaries.replaceChildren();
  const kinds=[["ENFEN",data.boletines[0].clave,"Estado comunicado el 16/10/2026"],["NOAA",data.boletines[2].clave,"Perspectiva publicada el 08/10/2026"],["Lambayeque","Consultar avisos SENAMHI","La lluvia diaria exige un aviso con fecha y ubicación"]];
  for(const [org,meaning,desc] of kinds){const a=el("article");a.append(el("span",org),el("strong",meaning),el("span",desc));summaries.append(a)}
 }
 const holder=$("oaf-bol-interpretaciones");if(holder){
  holder.replaceChildren();const ul=el("ul");
  for(const sentence of [
   "ENFEN mantiene el estado de Alerta de El Niño Costero en su comunicado del 16 de octubre; indica seguimiento y preparación, no lluvias automáticas en cada valle.",
   "NOAA describe un El Niño global fortaleciéndose al 8 de octubre. Su magnitud se refiere al Pacífico ecuatorial central, no directamente al grado de lluvia en Lambayeque.",
   "ENFEN 16-2026 proyectó lluvias superiores al promedio en la costa norte y posibles episodios moderados a fuertes desde noviembre; el comunicado 18 conserva la alerta. Es una perspectiva regional, no un pronóstico diario.",
   "Para temperatura elevada, viento y precipitaciones puntuales, consulta los avisos vigentes de SENAMHI; las fechas del portal son distintas de la fecha de esta síntesis."
  ])ul.append(el("li",sentence));
  holder.append(ul);
 }
}
async function ocean(){
 try{const txt=await full("datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv");
  const list=txt.trim().split(/\r?\n/).slice(1).map(l=>l.split(",")).filter(row=>row.length===3&&row[2].trim()!==""&&Number.isFinite(Number(row[2]))).map(row=>({m:row[0],v:Number(row[2])}));
  chartFrom(list);
  if(list.length){const last=list.at(-1),previous=list.at(-2);set("oaf-bol-noaa-meta",`NOAA NCEI ERSSTv5 · dato histórico hasta ${last.m}: ${num(last.v)} °C de anomalía. Respecto a ${previous.m}: ${last.v>previous.v?"aumentó":last.v<previous.v?"disminuyó":"sin cambio apreciable"}. Esta gráfica procede del archivo histórico OAF; la evaluación de intensidad oficial corresponde a ENFEN/NOAA según su región.`)}
 }catch(e){set("oaf-bol-chart","No se puede mostrar la serie archivada: "+e.message)}
}
function init(){
 const period=$("oaf-bol-periodo");
 if(period&&!period.dataset.bound){period.dataset.bound="1";period.addEventListener("change",ocean)}

 if(!$("oaf-boletines-ux11")||$("oaf-boletines-ux11").dataset.ready)return;
 $("oaf-boletines-ux11").dataset.ready="1";
 full("datos/boletines_institucionales_2026.json").then(d=>{if(d.boletines?.length!==5)throw Error("Documentos incompletos");render(d)}).catch(e=>set("oaf-boletines-tarjetas","No se pudo recuperar el índice documental: "+e.message));
 ocean();
}
document.addEventListener("oaf:ux11-ready",init);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
