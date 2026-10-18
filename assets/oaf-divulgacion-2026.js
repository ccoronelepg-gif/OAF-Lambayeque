/* OAF 2026 · interacción editorial y catálogo.
   Preserva el enrutador y los visores científicos originales. */
(()=>{"use strict";
const ready=fn=>document.readyState==="loading"?document.addEventListener("DOMContentLoaded",fn,{once:true}):fn();
const normalize=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
function init(){
 const field=document.getElementById("oaf-meta-search");
 const cards=[...document.querySelectorAll(".oaf-meta-card")];
 const none=document.getElementById("oaf-meta-none");
 if(field){
  const filter=()=>{
   const term=normalize(field.value.trim());
   let visible=0;
   for(const card of cards){
    const match=!term||normalize(card.dataset.oafSearch+" "+card.textContent).includes(term);
    card.hidden=!match;
    if(match)visible++;
   }
   if(none)none.classList.toggle("is-visible",visible===0);
   const count=document.getElementById("oaf-meta-count");
   if(count)count.textContent=visible+" fichas temáticas disponibles";
  };
  field.addEventListener("input",filter);
  filter();
 }
 const toggle=document.getElementById("oaf-meta-toggle");
 const legacy=document.getElementById("oaf-meta-legacy");
 function sync(){
  if(!legacy||!toggle)return;
  const expanded=legacy.classList.contains("oaf-meta-visible");
  toggle.setAttribute("aria-expanded",String(expanded));
  toggle.textContent=expanded?"Ocultar archivo técnico":"Explorar archivo técnico completo";
 }
 if(toggle&&legacy){
  toggle.addEventListener("click",()=>{
   legacy.classList.toggle("oaf-meta-visible");
   sync();
  });
  sync();
 }
 function deepLink(){
  let raw="";
  try{raw=decodeURIComponent(location.hash.slice(1))}catch{return}
  if(!raw||!legacy)return;
  const target=document.getElementById(raw);
  if(target&&legacy.contains(target)&&raw!=="oaf-meta-legacy"){
   legacy.classList.add("oaf-meta-visible");
   sync();
   for(let node=target.parentElement;node&&node!==legacy;node=node.parentElement){
    if(node.tagName==="DETAILS")node.open=true;
   }
  }
 }
 window.addEventListener("hashchange",deepLink);
 deepLink();
 const state=document.getElementById("oaf-editorial-datestamp");
 if(state)state.textContent="Diseño editorial · actualización 18/10/2026; fechas de los datos indicadas en cada gráfico.";
}
ready(init);
})();