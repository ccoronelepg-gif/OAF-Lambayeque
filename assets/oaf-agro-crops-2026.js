(function catalogOAF(){
"use strict";
const $=id=>document.getElementById(id);
function tag(name,cls,text){const e=document.createElement(name);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
const names={mango:"🥭",vid:"🍇",arandano:"🫐",palto:"🥑",maracuya:"🌼",banano:"🍌"};
function init(){
 const target=$("oaf-home-six-crops"),filter=$("oaf-crop-filter"),detail=$("oaf-crop-detail");
 if(!target||!filter||!detail)return;
 fetch("datos/catalogo_cultivos_agroexportacion_2026.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()}).then(data=>{
  if(!Array.isArray(data.cultivos)||data.cultivos.length!==6)throw Error("Inventario científico incompleto");
  const crops=data.cultivos,byId=Object.fromEntries(crops.map(c=>[c.id,c]));
  target.replaceChildren();
  crops.forEach(c=>{
   const a=tag("a","oaf-agro-crop-card");a.href="#oaf-cultivos-catalogo";a.dataset.crop=c.id;
   const name=tag("strong",null,`${names[c.id]||"🌱"} ${c.nombre}`),p=tag("span",null,`${c.plagas.length} grupos de plagas · ${c.enfermedades.length} enfermedades documentadas`),small=tag("small",null,"Consultar ficha científica →");
   a.append(name,p,small);
   a.addEventListener("click",()=>{filter.value=c.id;render(c.id)});
   target.append(a);
  });
  function listing(title,items){
   const article=tag("article"),header=tag("h4",null,title),list=tag("ul");article.append(header,list);
   for(const item of items){
    const li=tag("li"),strong=tag("strong",null,item.nombre+" · "),em=tag("em",null,item.agentes||"Agente por identificar"),info=tag("p",null,"Vigilancia: "+item.vigilancia),source=tag("a",null,"Consultar fuente científica ↗");
    source.href=item.fuente;source.target="_blank";source.rel="noopener noreferrer";
    li.append(strong,em,info,source);list.append(li);
   }
   return article;
  }
  function render(id){
   const item=byId[id]||crops[0];detail.replaceChildren();
   const h=tag("h3","oaf-agro-browser-title",item.nombre),latin=tag("p","oaf-agro-caption","Nombre científico / grupo: "+item.scientific);
   const columns=tag("div","oaf-agro-crop-columns");columns.append(listing("Plagas de importancia",item.plagas),listing("Enfermedades a vigilar",item.enfermedades));
   const note=tag("p","oaf-agro-interpretation",item.lectura),dis=tag("p","oaf-agro-caption",data.aclaracion||"La evidencia debe contrastarse en campo.");
   detail.append(h,latin,columns,note,dis);
   filter.value=item.id;
  }
  filter.addEventListener("change",()=>render(filter.value));
  render(filter.value||"mango");
 }).catch(e=>{target.replaceChildren(tag("p","oaf-agro-progress","No fue posible cargar las fichas científicas: "+e.message));detail.textContent="El catálogo documental está disponible en el repositorio de GitHub."});
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
