/* OAF-Lambayeque · UX-7: navegación temática accesible.
   No mueve, oculta ni modifica ningún módulo científico. */
(()=>{"use strict";
const ready=fn=>document.readyState==="loading"?document.addEventListener("DOMContentLoaded",fn,{once:true}):fn();
function init(){
 const outlines=[...document.querySelectorAll(".oaf-page-outline")];
 if(outlines.length!==6)return;
 const float=document.createElement("a");
 float.className="oaf-outline-float";
 float.textContent="↑ Índice de esta pestaña";
 float.href="#oaf-menu-inicio";
 float.setAttribute("aria-label","Volver al índice de la pestaña actual");
 float.hidden=true;
 document.body.append(float);
 function active(){
  return document.querySelector('main > section[data-page]:not([hidden])');
 }
 function updateLinks(){
  const page=active();
  const name=page?.getAttribute("data-page")||"inicio";
  const target="#oaf-menu-"+name;
  float.href=target;
  const hash=location.hash;
  document.querySelectorAll(".oaf-outline-item[aria-current]").forEach(a=>a.removeAttribute("aria-current"));
  const link=page?.querySelector(".oaf-outline-item[href]");
  if(page){
   const match=[...page.querySelectorAll(".oaf-outline-item")].find(a=>a.getAttribute("href")===hash);
   if(match)match.setAttribute("aria-current","location");
  }
  // Se muestra únicamente cuando el índice de la pestaña queda atrás.
  const outline=page?.querySelector(".oaf-page-outline");
  float.hidden=!outline||outline.getBoundingClientRect().bottom>110;
 }
 let queued=false;
 function schedule(){
  if(queued)return;
  queued=true;
  requestAnimationFrame(()=>{queued=false;updateLinks()});
 }
 window.addEventListener("hashchange",()=>{
  schedule();
  // Si el destino existe dentro de un panel cerrado, abrirlo antes de navegar.
  let key="";
  try{key=decodeURIComponent(location.hash.slice(1))}catch{return}
  const dest=document.getElementById(key);
  if(!dest)return;
  for(let p=dest.parentElement;p;p=p.parentElement){
   if(p.tagName==="DETAILS")p.open=true;
  }
 });
 window.addEventListener("scroll",schedule,{passive:true});
 window.addEventListener("resize",schedule);
 document.querySelectorAll(".oaf-page-outline .oaf-outline-item").forEach(a=>{
  a.addEventListener("click",()=>{
   const href=a.getAttribute("href");
   // El router original conserva la selección de página.
   // Al repetir un mismo enlace, facilitar igualmente el desplazamiento.
   if(href===location.hash){
    const dest=document.getElementById(href.slice(1));
    if(dest){for(let p=dest.parentElement;p;p=p.parentElement){if(p.tagName==="DETAILS")p.open=true}
    dest.scrollIntoView({block:"start",behavior:"auto"});}
   }
   requestAnimationFrame(schedule);
  });
 });
 schedule();
}
ready(init);
})();