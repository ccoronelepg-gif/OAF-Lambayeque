/* OAF UX74: auditoria de emisiones, MAE contra ERA5 posterior (no instrumental). */
(function(){
"use strict";
const $=id=>document.getElementById(id),ns="http://www.w3.org/2000/svg";
let history=null,error="",loaded=false,installed=false;
const n=(v)=>Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:2}):"Pendiente";
function element(tag,text){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;}
function install(){
 if(installed)return true;
 const host=$("oaf-ux14-rf-semana");if(!host)return false;
 const box=element("details");box.id="oaf-ux74-rf-monitor";box.className="oaf-ux74-rf-monitor";
 const summary=element("summary","Precisión archivada · ERA5 / Open-Meteo / Random Forest");box.append(summary);
 const text=element("p","Se congelan las tres referencias al emitir. ERA5 es una climatología histórica, Open-Meteo un pronóstico, y RF un modelo experimental. La evaluación posterior emplea ERA5 como REANÁLISIS, no datos instrumentales.");box.append(text);
 const control=element("div");control.className="oaf-ux74-rf-controls";
 const city=element("select");city.id="oaf-ux74-city";
 for(const v of ["Chiclayo","Jayanca","Motupe","Olmos"]){const o=element("option",v);o.value=v;city.append(o);}
 const variable=element("select");variable.id="oaf-ux74-variable";
 for(const pair of [["rain","Lluvia (mm/dia)"],["temp","Temperatura maxima (C)"]]){
  const o=element("option",pair[1]);o.value=pair[0];variable.append(o);
 }
 const refresh=element("button","Actualizar");refresh.type="button";
 const output=element("div");output.id="oaf-ux74-output";
 control.append(city,variable,refresh);box.append(control,output);host.append(box);
 city.addEventListener("change",render);variable.addEventListener("change",render);
 refresh.addEventListener("click",()=>load(true));
 box.addEventListener("toggle",()=>{if(box.open&&!loaded)load(false);});
 installed=true;return true;
}
function collect(){
 const city=$("oaf-ux74-city")?.value||"Chiclayo",rain=($("oaf-ux74-variable")?.value||"rain")==="rain";
 const key=rain?"mae_lluvia_mm":"mae_tmax_c";
 return (history?.emisiones||[]).map(e=>{
  const evals=e.verificacion_era5?.por_localidad?.[city];
  const rf=evals?.rf?.[key],ext=evals?.open_meteo?.[key],era=evals?.era5_climatologia?.[key];
  return {date:e.fecha_local,rf:Number.isFinite(rf)?rf:null,ext:Number.isFinite(ext)?ext:null,era:Number.isFinite(era)?era:null};
 });
}
function chart(rows){
 const subset=rows.filter(r=>Number.isFinite(r.rf)&&Number.isFinite(r.ext)&&Number.isFinite(r.era));
 if(subset.length<2)return null;
 const vals=subset.flatMap(r=>[r.rf,r.ext,r.era]),max=Math.max(0.1,...vals)*1.15;
 const svg=document.createElementNS(ns,"svg");svg.setAttribute("viewBox","0 0 750 235");
 svg.setAttribute("role","img");svg.setAttribute("aria-label","Comparación de MAE por emisión: ERA5 climatología, Open-Meteo y Random Forest");
 function node(name,attrs,title){
  const el=document.createElementNS(ns,name);
  for(const pair of Object.entries(attrs))el.setAttribute(pair[0],String(pair[1]));
  if(title!==undefined)el.textContent=title;return el;
 }
 const x=i=>45+i*660/(subset.length-1),y=v=>190-158*v/max;
 for(let i=0;i<=4;i++){
  const yy=190-i*39.5;
  svg.append(node("line",{x1:45,x2:716,y1:yy,y2:yy,stroke:"#cdded5"}));
  svg.append(node("text",{x:38,y:yy+4,"text-anchor":"end","font-size":11,fill:"#466658"},n(i*max/4)));
 }
 for(const [key,color] of [["era","#31946e"],["ext","#2987b5"],["rf","#a65bb4"]]){
  svg.append(node("polyline",{points:subset.map((r,i)=>x(i)+","+y(r[key])).join(" "),fill:"none",stroke:color,"stroke-width":3,"stroke-dasharray":key==="rf"?"6 4":key==="era"?"3 3":""}));
  subset.forEach((r,i)=>{const c=node("circle",{cx:x(i),cy:y(r[key]),r:3.5,fill:color});
    c.append(node("title",{},r.date+" "+key+": "+n(r[key])));svg.append(c);});
 }
 subset.forEach((r,i)=>{if(i%Math.max(1,Math.ceil(subset.length/7))===0||i===subset.length-1)
   svg.append(node("text",{x:x(i),y:218,"text-anchor":"middle","font-size":11,fill:"#466658"},r.date.slice(5)));});
 return svg;
}
function render(){
 if(!install())return;
 const target=$("oaf-ux74-output");target.replaceChildren();
 if(error){target.append(element("p","Historial no disponible: "+error));return;}
 if(!history){target.append(element("p","Consultando historial..."));return;}
 const rows=collect(),complete=rows.filter(r=>Number.isFinite(r.rf)&&Number.isFinite(r.ext)&&Number.isFinite(r.era));
 target.append(element("p","Emisiones registradas: "+rows.length+"; verificadas en las tres vías (7 días cada una): "+complete.length+"."));
 if(complete.length>=14){
  const means={era:complete.reduce((a,b)=>a+b.era,0)/complete.length,
               ext:complete.reduce((a,b)=>a+b.ext,0)/complete.length,
               rf:complete.reduce((a,b)=>a+b.rf,0)/complete.length};
  const best=Object.entries(means).sort((a,b)=>a[1]-b[1])[0];
  const name=best[0]==="era"?"ERA5 (climatología)":best[0]==="ext"?"Open-Meteo":"Random Forest";
  const city=$("oaf-ux74-city")?.value||"Chiclayo";
  const unit=$("oaf-ux74-variable")?.value==="temp"?" °C":" mm/día";
  target.append(element("p","Líder PROVISIONAL en "+city+": "+name+" (MAE "+n(best[1])+unit+"). Mismo conjunto de "+complete.length+" emisiones; no es certificación instrumental."));
 }else target.append(element("p","Todavía NO se puede determinar cuál de los tres es más certero: se requieren al menos 14 emisiones completas comparables."));
 const graph=chart(rows);
 if(graph){target.append(graph);target.append(element("p","Verde: referencia climatológica ERA5 (1996–2025 o respaldo 2021–2025 suavizado, según emisión); azul: Open-Meteo; morado discontinuo: RF. Menor MAE = menor diferencia frente a ERA5 posterior (no estaciones)."));}
 else target.append(element("p","El gráfico de las tres fuentes aparecerá al verificar al menos dos emisiones completas con los siete días. La referencia ERA5 emitida se incorpora a partir de UX76; no se inventan emisiones anteriores."));
 const table=element("table"),header=element("tr");
 for(const x of ["Emisión","MAE ERA5 clima","MAE Open-Meteo","MAE RF","Líder de emisión"]){header.append(element("th",x));}table.append(header);
 for(const row of rows.slice(-14).reverse()){
  const tr=element("tr");tr.append(element("td",row.date),element("td",n(row.era)),element("td",n(row.ext)),element("td",n(row.rf)));
  const valid=[row.era,row.ext,row.rf].every(Number.isFinite);
  const best=valid?[
    ["ERA5",row.era],["Open-Meteo",row.ext],["RF",row.rf]
  ].sort((a,b)=>a[1]-b[1])[0][0]:"Sin verificación triple";
  tr.append(element("td",best));table.append(tr);
 }
 const scroll=element("div");scroll.className="oaf-ux74-rf-scroll";scroll.append(table);target.append(scroll);
}
async function load(force){
 if(!install())return;
 try{
  const r=await fetch("datos/seguimiento_rf_ux74/emisiones.json",{cache:force?"no-store":"default"});
  if(!r.ok)throw Error("HTTP "+r.status);
  const j=await r.json();
  if(j.version!=="UX74"||!Array.isArray(j.emisiones))throw Error("Formato no esperado");
  history=j;error="";
 }catch(e){history=null;error=e.message||String(e);}
 loaded=true;render();
}
function start(){
 if(install())return;
 let tries=0;const retry=()=>{if(!install()&&++tries<25)setTimeout(retry,400);};retry();
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start,{once:true});else start();
window.OAFRFMonitorUX74={refresh:()=>load(true),getState:()=>({loaded,emisiones:history?.emisiones?.length||0,error})};
})();