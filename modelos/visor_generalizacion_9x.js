/* OAF 9X: resultados retrospectivos de transferencia espacial. */
(()=>{"use strict";
const $=s=>document.getElementById(s);
const show=(s,v)=>{if($(s))$(s).textContent=v};
const fmt=v=>typeof v==="number"&&Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:2}):"—";
const names={climatologia_global:"Climatología regional",climatologia_piso:"Climatología por piso",persistencia_anual:"Persistencia anual",random_forest:"Random Forest",gcn:"GCN (convolución de grafos)"};
const colors=["#426d95","#be9955","#398e80","#9375a0","#b76e64"];
function make(name,attrs={},content){const e=document.createElementNS("http://www.w3.org/2000/svg",name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));if(content!==undefined)e.textContent=content;return e;}
async function read(path){const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("Archivo no confirmado: "+path);return r.json();}
const polygons=g=>g.type==="Polygon"?[g.coordinates]:g.coordinates;
function mapBlocks(folds,features){
 const box=$("oaf-9x-map");box.replaceChildren();
 const map=new Map(folds.flatMap(f=>f.sectores_holdout.map(s=>[s,f.id])));
 const sectors=features.filter(f=>map.has(f.properties.id_sector));
 const points=sectors.flatMap(f=>polygons(f.geometry).flatMap(poly=>poly.flatMap(r=>r)));
 if(!points.length){box.textContent="Geometría no disponible";return;}
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 const W=820,H=480,pad=22;
 const xy=(a,b)=>[pad+(a-x0)/Math.max(.01,x1-x0)*(W-2*pad),H-pad-(b-y0)/Math.max(.01,y1-y0)*(H-2*pad)];
 const graph=make("svg",{viewBox:"0 0 "+W+" "+H,role:"img","aria-label":"Cinco grupos geográficos reservados para probar modelos de precipitación"});
 graph.style.width="100%";
 for(const feature of sectors){
  const sid=feature.properties.id_sector,b=map.get(sid);
  const d=polygons(feature.geometry).map(p=>p.map(r=>r.map((c,i)=>{
    const point=xy(c[0],c[1]);return(i?"L":"M")+point[0].toFixed(1)+","+point[1].toFixed(1);
  }).join(" ")+"Z").join(" ")).join(" ");
  const el=make("path",{d,fill:colors[b],"fill-opacity":.84,stroke:"#fff","stroke-width":1,role:"button",tabindex:0});
  const content=sid+" · bloque "+(b+1)+" · reservado para prueba, no área operativa validada";
  el.append(make("title",{},content));
  el.addEventListener("click",()=>show("oaf-9x-map-caption",content));
  el.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();show("oaf-9x-map-caption",content);}});
  graph.append(el);
 }
 box.append(graph);
 const legend=$("oaf-9x-legend");legend.replaceChildren();
 for(const f of folds){
  const entry=document.createElement("span");entry.className="oaf-9x-key";
  const dot=document.createElement("i");dot.style.background=colors[f.id];
  entry.append(dot,document.createTextNode("Bloque "+(f.id+1)+": "+f.n_sectores_holdout+" sectores"));
  legend.append(entry);
 }
}
async function init(){
 if(!$("oaf-9x-visor"))return;
 try{
  const base="datos/generalizacion_9x/";
  const [r,blocks,geo]=await Promise.all([read(base+"evaluacion_bloques_espaciales_9x.json"),read(base+"bloques_geograficos_9x.json"),read("datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson")]);
  if(r.fase!=="9X"||blocks.fase!=="9X"||blocks.n_folds!==5||r.n_predicciones_sector_mes_por_modelo!==2340||blocks.n_pixeles_compartidos_entre_bloques!==0||r.n_modelos_operativos_autorizados!==0||r.validacion_SENAMHI_externa!==false||r.alertas_fitosanitarias_activadas!==false)throw Error("Auditoría científica inconsistente");
  show("oaf-9x-status","CHIRPS histórico: 39 sectores, cinco bloques de exclusión espacial, 60 meses reservados (2021–2025). Se permite la lluvia pasada del sector de prueba, pero nunca se entrenó con su objetivo.");
  show("oaf-9x-winner",names[r.ganador_por_mae_descriptivo]||r.ganador_por_mae_descriptivo);
  const table=$("oaf-9x-grid");table.replaceChildren();
  for(const [key,v] of Object.entries(r.metricas_globales)){
   const tr=document.createElement("tr");
   for(const x of [names[key]||key,fmt(v.mae_mm)+" mm",fmt(v.rmse_mm)+" mm",fmt(r.skill_MAE_vs_climatologia_piso_pct[key])+" %",v.n]){
     const td=document.createElement("td");td.textContent=String(x);tr.append(td);
   }
   table.append(tr);
  }
  const floorTable=$("oaf-9x-floor-table");floorTable.replaceChildren();
  const fp=new Map();
  for(const r0 of r.metricas_por_piso){fp.set(r0.piso+":"+r0.modelo,r0);}
  for(const base of r.metricas_por_piso.filter(x=>x.modelo==="climatologia_piso")){
   const tr=document.createElement("tr");
   for(const v of [base.piso,fmt(base.mae_mm),fmt(fp.get(base.piso+":random_forest")?.mae_mm),fmt(fp.get(base.piso+":gcn")?.mae_mm),base.n]){
    const td=document.createElement("td");td.textContent=String(v);tr.append(td);
   }
   floorTable.append(tr);
  }
  const labels={random_forest:"Random Forest",gcn:"GCN",climatologia_piso:"climatología por piso"};
  show("oaf-9x-comparisons",Object.entries(r.bootstrap_espacial_bloques).map(([k,v])=>{
   const parts=k.split("_menos_");
   return (labels[parts[0]]||parts[0])+" menos "+(labels[parts[1]]||parts[1])+
   ": ΔMAE "+fmt(v.delta_mae_mm_positivo_es_peor)+" mm, intervalo exploratorio ["+v.rango_bootstrap_espacial_exploratorio_95_pct_mm.map(fmt).join("; ")+"] mm.";
  }).join(" ")+" Intervalos de solo cinco bloques; no demuestran independencia meteorológica.");
  mapBlocks(blocks.folds,geo.features);
 }catch(err){show("oaf-9x-status","No se puede cargar todavía una evaluación 9X comprobada: "+err.message+". Se conservan las métricas retrospectivas 9R–9W.");}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);else init();
})();