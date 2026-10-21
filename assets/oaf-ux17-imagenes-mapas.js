/* OAF UX17: resiliencia fotográfica y herramientas cartográficas sin datos inventados. */
(function(){
"use strict";
const fallback="assets/oaf-sin-foto-patogeno.svg";
const seen=new WeakSet();
function installPhoto(image){
 if(!image||seen.has(image))return;seen.add(image);
 if(image.closest(".oaf-ux12-photo"))return; /* galería tiene fallback y atribución propios */
 if(!image.getAttribute("alt"))image.alt="Imagen ilustrativa del observatorio";
 image.decoding="async";
 if(!image.closest(".heroimg"))image.loading="lazy";
 if(/^https:\/\//i.test(image.getAttribute("src")||""))image.referrerPolicy="no-referrer";
 const onError=()=>{
  if(image.dataset.oafFallbackApplied==="1")return;
  image.dataset.oafFallbackApplied="1";
  const original=image.getAttribute("src")||"";
  image.src=fallback;image.classList.add("oaf-ux17-pictogram");
  image.alt="Ilustración de respaldo: la fotografía original no está disponible";
  const frame=image.parentElement;
  if(frame&&!frame.querySelector(".oaf-ux17-image-unavailable")){
   const cap=document.createElement("small");
   cap.className="oaf-ux17-image-unavailable";
   cap.textContent="La imagen externa no cargó. Se muestra una ilustración provisional.";
   if(original.startsWith("https://")){
    const link=document.createElement("a");link.href=original;link.target="_blank";link.rel="noopener noreferrer";
    link.textContent=" Ver imagen original ↗";cap.append(link);
   }
   frame.append(cap);
  }
 };
 image.addEventListener("error",onError,{passive:true});
 if(image.complete&&image.naturalWidth===0)onError();
}
function media(root){
 (root.querySelectorAll?root.querySelectorAll("img"):[]).forEach(installPhoto);
 const hero=document.querySelector("#inicio .oaf-ux14-home-hero .heroimg");
 const photo=hero?.querySelector("img:not(.oaf-ux17-pictogram)");
 if(hero&&photo){
  const src=photo.getAttribute("src")||"";
  if(src.startsWith("assets/"))hero.style.setProperty("--oaf-hero-background",'url("'+src.replace(/"/g,"%22")+'")');
 }
}
function maps(){
 const slot=document.getElementById("oaf-ux9-map"),select=document.getElementById("oaf-ux9-floor"),legend=document.getElementById("oaf-ux9-map-legend");
 if(!slot||!select||!legend||slot.dataset.oafUx17)return;
 slot.dataset.oafUx17="1";
 const div=document.createElement("div");div.className="oaf-ux17-map-tools";
 const label=document.createElement("label");label.textContent="Transparencia de polígonos";
 const opacity=document.createElement("input");opacity.type="range";opacity.min="25";opacity.max="100";opacity.step="5";opacity.value="90";opacity.setAttribute("aria-label","Opacidad de sectores coloreados");
 const val=document.createElement("output");val.textContent="90 %";
 label.append(opacity,val);
 const button=document.createElement("button");button.type="button";button.textContent="Ver todos los pisos";
 button.addEventListener("click",()=>{select.value="todos";select.dispatchEvent(new Event("change",{bubbles:true}))});
 div.append(label,button);slot.before(div);
 const paint=()=>slot.querySelectorAll('svg path[role="button"]').forEach(x=>x.setAttribute("fill-opacity",String(Number(opacity.value)/100)));
 opacity.addEventListener("input",()=>{val.textContent=opacity.value+" %";paint()});
 new MutationObserver(paint).observe(slot,{childList:true});
 paint();
 function links(){
  for(const [i,node] of [...legend.children].entries()){
   if(node.dataset.oafAction)return;
   node.dataset.oafAction="1";node.setAttribute("role","button");node.tabIndex=0;
   const apply=()=>{const opt=select.options[i+1];if(opt){select.value=opt.value;select.dispatchEvent(new Event("change",{bubbles:true}))}};
   node.addEventListener("click",apply);
   node.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();apply()}});
  }
 }
 links();
 new MutationObserver(links).observe(legend,{childList:true});
}
function boot(){
 media(document);maps();
 const observer=new MutationObserver(muts=>{
  if(muts.some(m=>m.addedNodes.length)){
   for(const m of muts)for(const node of m.addedNodes){
    if(node.nodeType===1){
     if(node.tagName==="IMG")installPhoto(node);
     media(node);
    }
   }
   if(!document.getElementById("oaf-ux9-map")?.dataset.oafUx17)maps();
  }
 });
 observer.observe(document.body,{childList:true,subtree:true});
 document.addEventListener("oaf:ux9-ready",maps);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();