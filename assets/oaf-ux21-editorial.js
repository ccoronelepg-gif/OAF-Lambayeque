/* UX21: énfasis en interpretaciones sin alterar ni duplicar fuentes científicas.
   Los datos y las secciones continúan siendo idénticos en la web y la PWA. */
(function(){
"use strict";
let queued=false;
function mark(root){
 const selectors=".notice,.oaf-figure-caption,.oaf-agro-caption,.oaf-ux9-overview,.oaf-agro-interpretation";
 const candidates=root.querySelectorAll?root.querySelectorAll(selectors):[];
 for(const el of candidates){
  if(el.classList.contains("oaf-ux21-interpretation"))continue;
  const text=(el.textContent||"").trim();
  if(/^Interpretaci[oó]n(?:\s+cient[ií]fica|\s+obligatoria|\s+del mapa)?\s*:/i.test(text))
   el.classList.add("oaf-ux21-interpretation");
 }
}
function refresh(){
 queued=false;const main=document.querySelector("main");if(main)mark(main);
}
function schedule(){
 if(queued)return;queued=true;
 (window.requestAnimationFrame||window.setTimeout)(refresh);
}
function init(){
 refresh();
 const main=document.querySelector("main");
 if(main)new MutationObserver(muts=>{
  if(muts.some(m=>m.addedNodes.length))schedule();
 }).observe(main,{subtree:true,childList:true});
 document.addEventListener("oaf:ux9-ready",schedule);
 document.addEventListener("oaf:ux11-ready",schedule);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();