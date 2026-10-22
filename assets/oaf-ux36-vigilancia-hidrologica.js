/* OAF Lambayeque UX36 · vigilancia hidrológica y trazabilidad cuantitativa.
 * Las masas anuales históricas no son caudales m3/s ni probabilidades.
 * PHISIS/PEOT se consultan en sus portales oficiales; sin API de lectura
 * verificable no se declara conexión en tiempo real.
 */
(function(){"use strict";
const DATA="datos/hidrologia_ux36/referencias_cuencas_lambayeque.json";
const CSV="datos/hidrologia_ux36/plantilla_observaciones_hidrometricas.csv";
const $=id=>document.getElementById(id);
const el=(tag,cls)=>{const e=document.createElement(tag);if(cls)e.className=cls;return e};
const svg=(tag,props={})=>{const n=document.createElementNS("http://www.w3.org/2000/svg",tag);
 Object.entries(props).forEach(([k,v])=>n.setAttribute(k,String(v)));return n};
const norm=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
const fmt=(n,d=1)=>Number(n).toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d});
const state={data:null,loaded:"pendiente",selected:"leche",lines:true,reference:true,
 storage:true,csvRecords:[],csvStatus:"Sin mediciones cargadas; consulta PHISIS o PEOT",riverSegments:0,started:false};
function riverList(){
 return state.data?.rivers||[];
}
function chosen(){
 const items=riverList();return state.selected==="all"?items:items.filter(p=>p.id===state.selected);
}
function containsRiver(name,river){
 const candidate=norm(name).replace(/[–—]/g,"-"),tokens=(river.official_names||[]).map(norm);
 return candidate.length>3&&tokens.some(t=>candidate.includes(t.toLowerCase()));
}
function attach(){
 const pane=$("oaf-ux29-scenario"),tree=pane?.querySelector(".oaf-ux29-tree");
 if(!pane||!tree||$("oaf-ux36-hydrogroup"))return;
 const d=el("details","oaf-ux35-group oaf-ux36-group");d.id="oaf-ux36-hydrogroup";d.open=true;
 const summary=el("summary");summary.textContent="6 · Vigilancia hidrológica y Tinajones";d.append(summary);
 const txt=el("p","oaf-ux36-hint");txt.textContent="Comparación cuantitativa histórica por río. Los caudales y niveles actuales se consultan en las plataformas oficiales.";
 d.append(txt);
 const group=el("label","oaf-ux35-field");group.textContent="Río o sistema hídrico";
 const select=el("select");select.id="oaf-ux36-river";
 [["leche","Río La Leche"],["chancay","Chancay–Lambayeque"],["zana","Río Zaña"],["all","Comparar los tres ríos"]].forEach(([v,t])=>{
  const option=el("option");option.value=v;option.textContent=t;select.append(option);
 });select.value=state.selected;
 group.append(select);d.append(group);
 for(const [key,title,hint] of [
  ["reference","Comparación: promedio histórico frente a El Niño 1998","Masas anuales en hm³, no caudales ni niveles"],
  ["lines","Resaltar el río en la red hidrográfica oficial","Solo si el IGN publica el nombre del tramo"],
  ["storage","Ficha de vigilancia del reservorio Tinajones","Información oficial PEOT y ANA, sin dato en vivo"]
 ]){
  const lab=el("label","oaf-ux35-check"),input=el("input");input.type="checkbox";input.dataset.ux36Toggle=key;input.checked=state[key];
  const span=el("span");span.textContent=title;const small=el("small");small.textContent=hint;
  lab.append(input,span,small);d.append(lab);
 }
 const help=el("div","oaf-ux36-links");
 help.innerHTML='<a href="https://www.gob.pe/21712-consultar-la-informacion-hidrologica-peruana-en-la-plataforma-phisis-consultar-el-monitoreo-hidrologico-de-los-rios-peruanos" target="_blank" rel="noopener noreferrer">Ver caudales y niveles en PHISIS · SENAMHI ↗</a>'+
 '<a href="https://www.gob.pe/40915-acceder-al-sistema-de-informacion-hidrologica-tinajones" target="_blank" rel="noopener noreferrer">Consultar aportes y almacenamiento de Tinajones · PEOT ↗</a>';
 d.append(help);
 const filters=[...tree.querySelectorAll("details")].find(p=>p.querySelector("summary")?.textContent?.includes("5 · Filtros"));
 if(filters)filters.before(d);else tree.append(d);
 const mapContent=pane.querySelector(".oaf-ux29-mapcontent");
 const panel=el("section","oaf-ux36-panel");panel.id="oaf-ux36-panel";
 panel.innerHTML='<header><strong>Análisis hidrológico cuantitativo</strong><span>Referencias históricas y fuentes oficiales</span></header>'+
 '<div id="oaf-ux36-body">Consultando referencias documentadas…</div>'+
 '<div class="oaf-ux36-import">'+
 '<p><strong>Integrar mediciones verificables</strong> · Importa un CSV obtenido de PHISIS, SENAMHI o PEOT. El archivo permanece en tu navegador; OAF no lo publica ni valida su autenticidad.</p>'+
 '<input id="oaf-ux36-file" type="file" accept=".csv,text/csv" hidden />'+
 '<button type="button" id="oaf-ux36-import">Seleccionar CSV</button>'+
 '<a href="'+CSV+'" download>Plantilla CSV vacía</a><small id="oaf-ux36-csvstatus" role="status"></small></div>';
 if(mapContent){
  const before=$("oaf-ux35-mapstatus");
  if(before)before.before(panel);else mapContent.append(panel);
 }
 d.addEventListener("change",event=>{
  if(event.target.id==="oaf-ux36-river"){state.selected=event.target.value;refresh()}
  else if(event.target.dataset.ux36Toggle){state[event.target.dataset.ux36Toggle]=event.target.checked;refresh()}
 });
 $("oaf-ux36-import")?.addEventListener("click",()=>{$("oaf-ux36-file")?.click()});
 $("oaf-ux36-file")?.addEventListener("change",async e=>{
  const file=e.target.files?.[0];if(!file)return;
  await importCSV(file);e.target.value="";
 });
 // Make the same river network appear on both the original visor and scenario layer.
 const checkbox=pane.querySelector('[data-ux35-key="futureRiver"]');
 if(checkbox&&!checkbox.checked){
  checkbox.checked=true;
  checkbox.dispatchEvent(new Event("change",{bubbles:true}));
 }
}
function tableCell(row,value,header){
 const e=el(header?"th":"td");e.textContent=value;row.append(e);return e;
}
function renderPanel(){
 const host=$("oaf-ux36-body");if(!host)return;
 host.replaceChildren();
 if(!state.data){host.textContent=state.loaded==="error"?
  "No se pudo descargar la tabla histórica: consulte Metadatos y trazabilidad.":
  "Cargando los valores históricos publicados por el Gobierno Regional…";return}
 const p=el("p","oaf-ux36-explainer");
 p.textContent="Masas de agua anuales (hm³/año) publicadas en el Plan Hidráulico Regional. El volumen de 1998 se compara con una media histórica de período estadístico no precisado; NO indica caudal pico ni nivel de alerta.";
 host.append(p);
 if(state.reference){
  const table=el("table","oaf-ux36-table");
  const thead=el("thead"),tr=el("tr");
  ["Cuenca","Media histórica (hm³/año)","1998 (hm³/año)","Relación 1998 / media"].forEach(h=>tableCell(tr,h,true));
  thead.append(tr);table.append(thead);
  const body=el("tbody");
  for(const r of chosen()){
   const tr=el("tr");tableCell(tr,r.name,false);
   tableCell(tr,fmt(r.normal_annual_hm3,0),false);
   tableCell(tr,fmt(r.fen1998_annual_hm3,0),false);
   const ratio=r.fen1998_annual_hm3/r.normal_annual_hm3;
   tableCell(tr,fmt(ratio,1)+" veces",false);body.append(tr);
  }
  table.append(body);host.append(table);
  const bars=el("div","oaf-ux36-bars");
  for(const r of chosen()){
   const ratio=r.fen1998_annual_hm3/r.normal_annual_hm3;
   const row=el("div","oaf-ux36-barrow");
   const title=el("span");title.textContent=r.name+" · "+fmt(ratio,1)+"×";
   const track=el("div","oaf-ux36-bartrack"),bar=el("div","oaf-ux36-barfill");
   bar.style.width=Math.min(100,ratio/10*100)+"%";
   track.append(bar);row.append(title,track);bars.append(row);
  }
  host.append(bars);
  const note=el("p","oaf-ux36-note");note.textContent="La relación es solo una comparación de volumen anual observado/referencial; un episodio de inundación depende además de picos de caudal, cauces, infraestructura, drenajes y exposición.";host.append(note);
 }
 if(state.storage){
  const box=el("section","oaf-ux36-storage");
  const t=el("strong");t.textContent="Tinajones · referencia documentada, no medición actual";
  const txt=el("p");txt.textContent=state.data.tinajones.period_note;
  const link=el("a");link.href=state.data.tinajones.operational_data;link.rel="noopener noreferrer";
  link.target="_blank";link.textContent="Consultar el volumen y las descargas actualizadas en PEOT ↗";
  box.append(t,txt,link);host.append(box);
 }
 const imported=state.csvRecords.filter(r=>state.selected==="all"||r.river===state.selected);
 if(imported.length){
  const grouped=new Map();
  for(const row of imported){
   const key=row.river+" · "+row.station;
   const old=grouped.get(key);if(!old||row.date>old.date)grouped.set(key,row);
  }
  const info=el("div","oaf-ux36-imported");
  const title=el("strong");title.textContent="Mediciones importadas localmente (no auditadas por OAF)";
  info.append(title);
  for(const rec of grouped.values()){
   const div=el("p");div.textContent=rec.riverLabel+" · "+rec.station+" · "+
    rec.date+(rec.flow===null?"":" · Caudal: "+fmt(rec.flow,2)+" m³/s")+
    (rec.level===null?"":" · Nivel: "+fmt(rec.level,2)+" m")+
    (rec.volume===null?"":" · Almacenamiento: "+fmt(rec.volume,2)+" MMC")+
    " · Fuente declarada: "+rec.source;info.append(div);
  }
  host.append(info);
 }
 const notes=el("p","oaf-ux36-sourcestatus");
 notes.textContent="Datos históricos: compilación del Plan Hidráulico Regional difundida en 2018. "+
  (state.riverSegments?
  state.riverSegments+" tramos con nombre coincidente resaltados en el mapa. ":
  "No hay tramos con nombre coincidente cargados del servicio IGN. ") +
  "Para niveles, caudales y almacenamiento actuales, consulta las plataformas oficiales.";
 host.append(notes);
 const msg=$("oaf-ux36-csvstatus");if(msg)msg.textContent=state.csvStatus;
}
function selectedTraceName(label){
 return chosen().some(r=>containsRiver(label,r));
}
function mapHighlight(context){
 const svgRoot=context?.svg,scene=context?.scene;if(!svgRoot||!scene)return;
 svgRoot.querySelectorAll(".oaf-ux36-traces").forEach(n=>n.remove());
 state.riverSegments=0;
 if(!state.lines)return;
 const src=window.oafUx33Data?.();
 const rivers=src?.features?.hydroRio||[];
 const group=svg("g",{class:"oaf-ux36-traces","clip-path":"url(#oaf-ux35-region-clip)"});
 let current=group;
 const selection=(window.oafUx30Context?.()?.selected||[]).filter(x=>x.geo);
 selection.forEach((sel,i)=>{
  const next=svg("g",{"clip-path":"url(#oaf-ux35-filter-"+i+")"});current.append(next);current=next;
 });
 for(const f of rivers){
  const p=f.properties||{},name=p.r_q_text||p.nombre||"";
  if(!selectedTraceName(name))continue;
  const g=f.geometry,arr=g?.type==="LineString"?[g.coordinates]:g?.type==="MultiLineString"?g.coordinates:[];
  for(const line of arr){
   const d=line.filter(c=>c?.length>=2).map((c,i)=>(i?"L":"M")+scene.x(c[0]).toFixed(2)+" "+scene.y(c[1]).toFixed(2)).join(" ");
   if(!d)continue;
   const path=svg("path",{d,fill:"none",stroke:"#df781b","stroke-width":3.2,
    "stroke-linejoin":"round","stroke-linecap":"round","pointer-events":"none"});
   const nameTag=svg("title");nameTag.textContent="Cauce oficial IGN: "+name;path.append(nameTag);
   current.append(path);state.riverSegments++;
  }
 }
 svgRoot.append(group);
 renderPanel();
}
function appendDiagnosis(target){
 if(!target||!state.data)return;
 const rivers=chosen();if(!rivers.length)return;
 const box=el("section","oaf-ux35-diagnosis-section oaf-ux36-diagnosis");
 const title=el("strong");title.textContent="Vigilancia hidrológica · comparación verificable";
 const p=el("p");
 p.textContent=rivers.map(r=>r.name+": "+fmt(r.fen1998_annual_hm3/r.normal_annual_hm3,1)+
  " veces el volumen anual medio en 1998").join(" · ")+
  ". Es un antecedente histórico, no un indicador de caudal actual, riesgo cuantificado o probabilidad de desborde.";
 box.append(title,p);
 const more=el("p");
 more.textContent=state.selected==="leche"?
  "En La Leche, ENFEN prevé caudales sobre lo normal desde noviembre de 2026. Para evaluar un desborde hacen falta niveles, caudales medidos, umbrales y modelos hidráulicos.":
  state.selected==="chancay"?
  "La gestión del Chancay–Lambayeque depende también de derivaciones y de la operación de Tinajones. Un volumen anual elevado no determina crecida en un punto específico.":
  state.selected==="zana"?
  "Zaña requiere seguimiento hidrométrico propio. Los antecedentes de 1998 no se deben trasladar directamente a un pronóstico del verano de 2027.":
  "El contraste entre las tres cuencas es histórico y no constituye una jerarquía de amenaza actual.";
 box.append(more);target.append(box);
}
function csvLine(line){
 const out=[];let str="",inside=false;
 for(let i=0;i<line.length;i++){
  const ch=line[i];
  if(ch==='"'){if(inside&&line[i+1]==='"'){str+='"';i++}else inside=!inside}
  else if(ch===","&&!inside){out.push(str.trim());str=""}
  else str+=ch;
 }
 out.push(str.trim());return out;
}
function numerical(raw){
 if(raw===undefined||raw===null||String(raw).trim()==="")return null;
 const value=Number(raw);return Number.isFinite(value)&&value>=0?value:NaN;
}
function riverId(raw){
 const n=norm(raw).replace(/[–—]/g,"-");
 if(n.includes("tinajones"))return "tinajones";
 if(n.includes("leche"))return "leche";
 if(n.includes("chancay")||n.includes("lambayeque")||n==="reque")return "chancay";
 if(n.includes("zana"))return "zana";return "";
}
async function importCSV(file){
 if(file.size>2_000_000){state.csvStatus="Archivo demasiado grande (máximo 2 MB).";renderPanel();return}
 try{
  const text=await file.text(),lines=text.replace(/^\uFEFF/,"").trim().split(/\r?\n/);
  const headers=csvLine(lines.shift()||"").map(norm);
  const required=["fecha","rio","estacion","caudal_m3s","nivel_m","volumen_mmc","fuente"];
  if(required.some(k=>!headers.includes(k)))throw Error("Faltan columnas de la plantilla oficial OAF");
  const rows=[],seen=new Set();let bad=0;
  for(const line of lines.slice(0,25000)){
   if(!line.trim())continue;
   const cols=csvLine(line),obj=Object.fromEntries(headers.map((h,i)=>[h,cols[i]||""]));
   const river=riverId(obj.rio),date=obj.fecha,source=obj.fuente?.trim();
   const flow=numerical(obj.caudal_m3s),level=numerical(obj.nivel_m),volume=numerical(obj.volumen_mmc);
   if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!Number.isFinite(Date.parse(date))||
     Date.parse(date)>Date.now()||!river||!obj.estacion||!source||
     [flow,level,volume].every(v=>v===null)||
     [flow,level,volume].some(v=>Number.isNaN(v))){
    bad++;continue;
   }
   const key=[date,river,obj.estacion].join("|");if(seen.has(key))continue;seen.add(key);
   rows.push({date,river,riverLabel:obj.rio,station:obj.estacion,flow,level,volume,source});
  }
  state.csvRecords=rows;
  state.csvStatus="Importación local: "+rows.length+" registros con estructura válida; "+bad+
   " filas descartadas. Fuente declarada por quien importa, sin comprobación independiente.";
 }catch(e){state.csvStatus="No se pudo importar: "+String(e.message||e).slice(0,170)}
 renderPanel();appendToDiagnosis();
}
function appendToDiagnosis(){
 const box=$("oaf-ux29-scenario")?.querySelector(".oaf-ux29-diagbody");
 if(!box)return;
 box.querySelectorAll(".oaf-ux36-diagnosis").forEach(n=>n.remove());appendDiagnosis(box);
}
function refresh(){
 renderPanel();window.oafUx35Render?.();appendToDiagnosis();
}
async function loadData(){
 state.loaded="cargando";
 try{
  const r=await fetch(DATA,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);
  const data=await r.json();
  if(!Array.isArray(data.rivers)||data.rivers.length!==3||
   data.rivers.some(x=>!Number.isFinite(x.normal_annual_hm3)||!Number.isFinite(x.fen1998_annual_hm3)))throw Error("Valores históricos incompletos");
  state.data=data;state.loaded="listo";
 }catch(e){state.loaded="error"}
 refresh();
}
function meta(){
 const host=$("oaf-ux35-metadatos")||$("oaf-ux30-metadatos");
 if(!host||$("oaf-ux36-metadata"))return;
 const div=el("div","oaf-ux36-metadatos");div.id="oaf-ux36-metadata";
 const title=el("h3");title.textContent="Hidrología cuantitativa y Tinajones · UX36";
 const p=el("p");p.textContent="Las masas medias anuales y las del evento FEN 1998 proceden del Plan Hidráulico Regional. Los datos de tiempo real, caudales, niveles y volúmenes de Tinajones deben verificarse en PHISIS y PEOT. El OAF no afirma tener una conexión automática con sus portales.";
 div.append(title,p);
 const sources=[
  ["Plan Hidráulico Regional (compilación histórica 2018)","https://siga.regionlambayeque.gob.pe/mysiganew/content/sisadportPublicaTema_mostrar.php?pass=MTA1Nw%3D%3D&poco_id=12546"],
  ["SENAMHI · monitoreo hidrológico PHISIS","https://www.gob.pe/21712-consultar-la-informacion-hidrologica-peruana-en-la-plataforma-phisis-consultar-el-monitoreo-hidrologico-de-los-rios-peruanos"],
  ["PEOT · Sistema de Información Hidrológica Tinajones","https://www.gob.pe/40915-acceder-al-sistema-de-informacion-hidrologica-tinajones"],
  ["ANA · balance hídrico Chancay 2024–2025","https://www.gob.pe/institucion/ana/noticias/1244576-grupo-de-trabajo-padh-presenta-informe-de-evaluacion-2024-2025-en-la-cuenca-chancay-lambayeque"],
  ["Tabla histórica original OAF",DATA],
  ["Metodología e incertidumbre UX36","https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_HIDROLOGIA_CUENCAS_UX36.md"]
 ];
 const list=el("ul");for(const [name,url] of sources){
  const li=el("li"),a=el("a");a.href=url;a.textContent=name;a.rel="noopener noreferrer";a.target="_blank";li.append(a);list.append(li);
 }div.append(list);host.append(div);
}
function init(){
 window.oafUx36AfterRender=mapHighlight;
 window.oafUx36Diagnosis=appendDiagnosis;
 attach();meta();loadData();
 window.addEventListener("oaf:geodata",()=>window.oafUx35Render?.());
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();