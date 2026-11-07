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
 const summary=element("summary","Seguimiento historico RF vs Open-Meteo");box.append(summary);
 const text=element("p","Se conserva cada emision antes de conocer los resultados; el contraste posterior emplea ERA5 como REANALISIS, no medicion de una estacion.");box.append(text);
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
  const rf=evals?.rf?.[key],ext=evals?.open_meteo?.[key];
  return {date:e.fecha_local,rf:Number.isFinite(rf)?rf:null,ext:Number.isFinite(ext)?ext:null};
 });
}
function chart(rows){
 const subset=rows.filter(r=>Number.isFinite(r.rf)&&Number.isFinite(r.ext));
 if(subset.length<2)return null;
 const vals=subset.flatMap(r=>[r.rf,r.ext]),max=Math.max(0.1,...vals)*1.15;
 const svg=document.createElementNS(ns,"svg");svg.setAttribute("viewBox","0 0 750 235");
 svg.setAttribute("role","img");svg.setAttribute("aria-label","Comparacion de MAE de RF y Open-Meteo por fecha de emision");
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
 for(const key of ["rf","ext"]){
  const color=key==="rf"?"#a65bb4":"#2987b5";
  svg.append(node("polyline",{points:subset.map((r,i)=>x(i)+","+y(r[key])).join(" "),fill:"none",stroke:color,"stroke-width":3,"stroke-dasharray":key==="rf"?"6 4":""}));
  subset.forEach((r,i)=>{const c=node("circle",{cx:x(i),cy:y(r[key]),r:3.5,fill:color});c.append(node("title",{},r.date+" "+key+": "+n(r[key])));svg.append(c);});
 }
 subset.forEach((r,i)=>{if(i%Math.max(1,Math.ceil(subset.length/7))===0||i===subset.length-1)svg.append(node("text",{x:x(i),y:218,"text-anchor":"middle","font-size":11,fill:"#466658"},r.date.slice(5)));});
 return svg;
}
function render(){
 if(!install())return;
 const target=$("oaf-ux74-output");target.replaceChildren();
 if(error){target.append(element("p","Archivo aun no disponible: "+error));return;}
 if(!history){target.append(element("p","Consultando historial..."));return;}
 const rows=collect(),complete=rows.filter(r=>Number.isFinite(r.rf)&&Number.isFinite(r.ext));
 target.append(element("p","Emisiones registradas: "+rows.length+"; verificadas contra ERA5 y comparables entre RF/Open-Meteo: "+complete.length+"."));
 const graph=chart(rows);
 if(graph){target.append(graph);target.append(element("p","Curva morada discontinua: RF experimental. Curva azul: Open-Meteo emitido. Menor MAE significa mayor cercania al ERA5 (no validacion instrumental)."));}
 else target.append(element("p","El grafico de errores aparecera cuando existan al menos dos emisiones con los siete dias maduros y contrastados. No se muestran errores futuros inventados."));
 const table=element("table"),header=element("tr");
 for(const x of ["Emision","MAE RF","MAE Open-Meteo","Lectura"]){header.append(element("th",x));}table.append(header);
 for(const row of rows.slice(-14).reverse()){
  const tr=element("tr");tr.append(element("td",row.date),element("td",n(row.rf)),element("td",n(row.ext)));
  tr.append(element("td",Number.isFinite(row.rf)&&Number.isFinite(row.ext)?(row.rf<row.ext?"RF menor error":row.rf>row.ext?"Open-Meteo menor error":"Empate"):"Sin verificacion completa"));
  table.append(tr);
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