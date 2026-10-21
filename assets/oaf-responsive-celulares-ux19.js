/* OAF UX19 · mejoras móviles no destructivas y accesibles */
(function(){
"use strict";
const CHART_IDS=[
 "oaf-ux14-weekchart","oaf-ux14-monthchart",
 "oaf-ux9-grafico-lluvia","oaf-ux9-grafico-temperatura",
 "oaf-ux9-grafico-enso","oaf-sm-chart","oaf-bol-chart"
];
let scheduled=false;
const mobile=()=>window.matchMedia("(max-width:700px)").matches;
function charts(){
 for(const id of CHART_IDS){
  const host=document.getElementById(id);
  if(!host)continue;
  if(!host.classList.contains("oaf-mobile-chart-host")){
   host.classList.add("oaf-mobile-chart-host");
   host.tabIndex=0;host.setAttribute("role","region");
   const label=host.getAttribute("aria-label")||"Gráfico científico interactivo";
   host.setAttribute("aria-label",label+". En celular, desliza horizontalmente para ver las etiquetas");
  }
  if(!host.nextElementSibling?.classList.contains("oaf-mobile-chart-hint")){
   const hint=document.createElement("small");
   hint.className="oaf-mobile-chart-hint";
   hint.textContent="↔ Desliza el gráfico para explorar todos los días y valores.";
   host.after(hint);
  }
 }
}
function tables(){
 const all=[...document.querySelectorAll("[data-page] table")];
 for(const table of all){
  if(table.closest(".oaf-mobile-table-wrap, .oaf-ux11-scroller, .scroller, .oaf-ux11-weather-table-wrap"))continue;
  // Tablas anchas de 4+ columnas: conservar todas las columnas y el orden.
  const cols=table.tHead?.rows?.[0]?.cells?.length||table.rows?.[0]?.cells?.length||0;
  if(cols<4)continue;
  const wrapper=document.createElement("div");
  wrapper.className="oaf-mobile-table-wrap";
  wrapper.tabIndex=0;
  wrapper.setAttribute("role","region");
  const heading=table.closest("section,article,.panel")?.querySelector("h2,h3");
  wrapper.setAttribute("aria-label",heading?"Tabla desplazable: "+heading.textContent.trim():"Tabla de datos científicos desplazable");
  table.before(wrapper);wrapper.append(table);
  const hint=document.createElement("small");
  hint.className="oaf-mobile-swipe-hint";
  hint.textContent="↔ Desliza la tabla para leer todas las columnas.";
  wrapper.after(hint);
 }
}
function navigation(){
 const button=document.getElementById("oaf-mobile-menu");
 const nav=document.getElementById("oaf-primary-nav");
 if(!button||!nav)return;
 button.setAttribute("aria-label","Abrir o cerrar las seis secciones del Observatorio");
 if(button.dataset.ux19Nav)return;
 button.dataset.ux19Nav="1";
 const closeOnNavigation=()=>{
  if(!mobile())return;
  nav.classList.remove("oaf-menu-open");
  button.setAttribute("aria-expanded","false");
 };
 for(const anchor of nav.querySelectorAll('a[href^="#"]')){
  anchor.addEventListener("click",closeOnNavigation);
 }
 window.addEventListener("hashchange",closeOnNavigation,{passive:true});
 window.addEventListener("resize",()=>{
  if(!mobile())closeOnNavigation();
 },{passive:true});
}
function mobileImages(){
 // Width and height attributes reduce layout shift without changing aspect ratios.
 for(const img of document.querySelectorAll(".oaf-ux12-photo img, .oaf-ux14-home-hero .heroimg img")){
  img.style.objectFit="contain";
  img.style.objectPosition="center";
  img.decoding="async";
 }
}
function refresh(){charts();tables();navigation();mobileImages();}
function scheduleRefresh(){
 if(scheduled)return;
 scheduled=true;
 window.requestAnimationFrame(()=>{scheduled=false;refresh()});
}
function init(){
 refresh();
 // Legacy OAF scripts generate forecast charts and sanitary product cards after initial page load.
 const target=document.querySelector("main");
 if(target)new MutationObserver(records=>{
   if(records.some(r=>r.addedNodes.length||r.removedNodes.length))scheduleRefresh();
 }).observe(target,{childList:true,subtree:true});
 document.addEventListener("oaf:ux9-ready",scheduleRefresh);
 document.addEventListener("oaf:ux11-ready",scheduleRefresh);
 window.addEventListener("orientationchange",scheduleRefresh,{passive:true});
 window.addEventListener("resize",scheduleRefresh,{passive:true});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
else init();
})();