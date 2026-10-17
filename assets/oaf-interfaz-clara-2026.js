/* Navegacion 2026: los codigos internos de fases no son titulos publicos.
   Mantiene nombres de archivos, IDs, fuentes y referencias tecnicas sin cambios. */
(() => {
"use strict";
function clearStageTitles(){
  const nodes=document.querySelectorAll("summary,h1,h2,h3,h4,h5,h6,.eyebrow");
  for(const el of nodes){
    for(const node of el.childNodes){
      if(node.nodeType!==Node.TEXT_NODE)continue;
      const old=node.nodeValue;
      if(!/\bFase\s*\d+[A-Za-z]?\b/i.test(old))continue;
      let next=old.replace(/\bFase\s*\d+[A-Za-z]?\s*(?:[·:—–-]\s*)?/gi,"");
      next=next.replace(/\s*[·:—–-]\s*$/,"");
      if(next!==old)node.nodeValue=next;
    }
  }
}
function accordionFocus(){
  const panels=[...document.querySelectorAll("details.panel")];
  panels.forEach(box=>{
    box.addEventListener("toggle",()=>{
      if(!box.open)return;
      const section=box.closest("[data-page]");
      if(!section)return;
      for(const other of panels){
        if(other===box||other.closest("[data-page]")!==section)continue;
        if(other.contains(box)||box.contains(other))continue;
        if(other.open)other.open=false;
      }
    });
  });
}
function init(){clearStageTitles();accordionFocus();}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();