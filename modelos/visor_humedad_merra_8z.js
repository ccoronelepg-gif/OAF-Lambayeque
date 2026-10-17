/* 8Z OAF - Humedad ERA5 1996-2025 + panel aerosol NASA CMR sin valores PM atribuidos. */
(()=>{
"use strict";
const panel=document.getElementById("oaf-8z-humedad");
if(!panel)return;
const el=id=>document.getElementById(id);
const format=(n,dec=2)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:dec,maximumFractionDigits:dec}):"—";
const columns={rh_2m_media_pct:["Humedad relativa media","%"],
vpd_max_diario_media_mes_kpa:["Media mensual del VPD máximo diario","kPa"],
vpd_max_diario_max_mes_kpa:["Máximo VPD diario del mes","kPa"]};
let rows=[],data=null,nasa=null;
function parse(text){
const lines=text.trim().split(/\r?\n/),head=lines.shift().split(",");
return lines.map(l=>{
 const v=[];let part="",quoted=false;
 for(let i=0;i<l.length;i++){
   if(l[i]==='"'){quoted=!quoted;continue;}
   if(l[i]===','&&!quoted){v.push(part);part="";}else{part+=l[i];}
 }
 v.push(part);
 return Object.fromEntries(head.map((key,i)=>[key,v[i]||""]));
});
}
function node(tag,attrs,label){
 const e=document.createElementNS("http://www.w3.org/2000/svg",tag);
 Object.entries(attrs||{}).forEach(([k,v])=>e.setAttribute(k,String(v)));
 if(label!==undefined)e.textContent=String(label);
 return e;
}
function render(){
if(!data)return;
const site=el("oaf-8z-site").value,key=el("oaf-8z-variable").value;
const p=rows.filter(x=>x.localidad===site);
const years=[];
for(let year=1996;year<=2025;year++){
const valid=p.filter(x=>x.mes.startsWith(String(year)));
if(valid.length!==12)continue;
const v=valid.reduce((s,x)=>s+Number(x[key]),0)/12;
years.push({year,val:v});
}
const svg=el("oaf-8z-graph");
svg.replaceChildren();
if(!years.length)return;
const ys=years.map(x=>x.val),vmin=Math.min(...ys),vmax=Math.max(...ys);
let lo=vmin-(vmax-vmin||1)*.12,hi=vmax+(vmax-vmin||1)*.12;
const Y=v=>22+200*(hi-v)/(hi-lo);
const X=i=>56+(i*680/(years.length-1));
svg.append(node("line",{x1:56,x2:746,y1:222,y2:222,stroke:"currentColor",opacity:.25}));
svg.append(node("polyline",{
points:years.map((x,i)=>X(i).toFixed(1)+","+Y(x.val).toFixed(1)).join(" "),
fill:"none",stroke:"#2d8d9d","stroke-width":3}));
years.forEach((r,i)=>{svg.append(node("circle",{cx:X(i),cy:Y(r.val),r:3,fill:"#2d8d9d"}))});
for(const i of [0,9,19,29]){
svg.append(node("text",{x:X(i),y:254,'text-anchor':"middle",fill:"currentColor",'font-size':13},years[i].year));
}
for(let i=0;i<4;i++){
 const num=lo+(hi-lo)*i/3;
 svg.append(node("text",{x:49,y:Y(num)+4,'text-anchor':"end",fill:"currentColor",'font-size':12},format(num,1)));
}
el("oaf-8z-chart-title").textContent=columns[key][0]+" ("+columns[key][1]+") · "+site;
el("oaf-8z-chart-note").textContent="30 puntos anuales promediados de los meses del reanálisis ERA5. No son estaciones ni microclima del cultivo.";
const tb=el("oaf-8z-pm-relations");tb.replaceChildren();
if(data.relationship){
 for(const x of data.relationship.comparaciones.filter(x=>x.localidad===site)){
  const tr=document.createElement("tr");
  const desc=x.particula.startsWith("pm25")?"PM₂.₅":"PM₁₀";
  for(const s of [desc,x.covariable==="rh_2m_media_pct"?"Humedad relativa":"VPD máximo diario",
                   x.meses_solapados,
                   x.pearson_bruto===null?"No evaluable":format(x.pearson_bruto,3),
                   x.pearson_deseasonalizado===null?"No evaluable":format(x.pearson_deseasonalizado,3)]){
   const td=document.createElement("td");td.textContent=String(s);tr.append(td);
  }
  tb.append(tr);
 }
}
}
async function load(){
if(data)return render();
el("oaf-8z-status").textContent="Leyendo bases de humedad ERA5 y NASA...";
try{
const endpoints=await Promise.all([
 fetch("datos/humedad_8z/estado_humedad_8z.json",{cache:"no-store"}),
 fetch("datos/humedad_8z/humedad_vpd_mensual_8z.csv",{cache:"no-store"}),
 fetch("datos/merra2_8z/estado_piloto_merra2_8z.json",{cache:"no-store"}),
 fetch("datos/relaciones_pm_humedad_8z/estado_relacion_pm_humedad_8z.json",{cache:"no-store"})]);
if(endpoints.slice(0,3).some(x=>!x.ok))throw Error("Sin archivos 8Z completos");
const h=await endpoints[0].json(), raw=await endpoints[1].text();
nasa=await endpoints[2].json();
if(h.fase!=="8Z"||h.no_alertas_fitosanitarias!==true||nasa.serie_merra2_pm_mensual_archivada!==false)
 throw Error("No se puede validar el estado científico de la fuente");
rows=parse(raw);
if(rows.length!==h.registros_mes_sitio)throw Error("CSV humedad y metadatos no coinciden");
data={h,nasa,relationship:null};
if(endpoints[3].ok){
 const q=await endpoints[3].json();
 if(q.fase==="8Z"&&q.correlacion_causal===false)data.relationship=q;
}
el("oaf-8z-count").textContent=String(h.registros_mes_sitio);
el("oaf-8z-nasa").textContent=String(Object.keys(nasa.catalogo_metadatos_nasa||{}).length);
el("oaf-8z-coincidence").textContent=data.relationship?
String(data.relationship.comparaciones_evaluables)+" / 16":"Pendiente";
el("oaf-8z-status").textContent="ERA5 modelado 1996–2025. MERRA-2: solo metadatos de NASA; NO se han descargado series PM históricas.";
render();
}catch(ex){el("oaf-8z-status").textContent="Verificación pendiente: "+ex.message;}
}
panel.addEventListener("toggle",()=>{if(panel.open)load()});
[el("oaf-8z-site"),el("oaf-8z-variable")].forEach(x=>x.addEventListener("change",render));
if(panel.open)load();
})();
