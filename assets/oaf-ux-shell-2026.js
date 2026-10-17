/* OAF UX 2026 · Capa de navegación accesible y nivel de lectura.
 * No altera predicciones, modelos ni rutas de los módulos científicos. */
(()=>{"use strict";
const byId=id=>document.getElementById(id);
const allowed=["Chiclayo","Jayanca","Motupe","Olmos"];
const known=["inicio","clima","nino","cultivos","verificaciones"];
const controls=[["oaf-ux-view-quick","rapida"],["oaf-ux-view-technical","tecnica"]];
let mode="rapida";
function applyView(next){
 if(next!=="rapida"&&next!=="tecnica")return;
 mode=next;
 document.documentElement.dataset.oafView=next;
 controls.forEach(([id,value])=>{
  const b=byId(id);if(!b)return;
  b.setAttribute("aria-pressed",String(value===next));b.classList.toggle("is-current",value===next);
 });
 const explanation=byId("oaf-ux-view-description");
 if(explanation)explanation.textContent=next==="rapida"?
   "Vista rápida: orientaciones breves; los resultados técnicos originales permanecen disponibles.":
   "Vista técnica: acceso completo a metodología, datos, gráficas y verificaciones históricas.";
}
function setMobile(open){
 const btn=byId("oaf-mobile-menu"),nav=document.querySelector(".head nav[aria-label='Secciones principales']");
 if(!btn||!nav)return;
 btn.setAttribute("aria-expanded",String(Boolean(open)));
 nav.classList.toggle("oaf-menu-open",Boolean(open));
}
function setPlace(value){
 if(!allowed.includes(value))return;
 const active=byId("oaf-current-city");
 if(active)active.textContent=value;
 for(const id of ["oaf-home-location","localidad","oaf-dash-place","pred-place"]){
  const sel=byId(id);
  if(!sel||sel.value===value)continue;
  if(![...sel.options].some(o=>o.value===value))continue;
  sel.value=value;
  // Update the active pane only: preserve non-active modules and avoid
  // unnecessary network requests for all four independent forecasts.
  if(id==="oaf-home-location"||(!sel.closest("[data-page]")?.hidden&&id!=="pred-place")){
   sel.dispatchEvent(new Event("change",{bubbles:true}));
  }
 }
 document.dispatchEvent(new CustomEvent("oaf:localidad",{detail:{localidad:value}}));
}
function hashAccess(){
 const raw=decodeURIComponent(location.hash.slice(1));
 if(raw==="verificaciones"||raw==="inicio"||raw==="clima"||raw==="cultivos"||raw==="nino")return;
 const el=byId(raw);
 if(el?.closest('[data-page="verificaciones"]'))applyView("tecnica");
}
function init(){
 if(!byId("oaf-ux-view-quick"))return;
 controls.forEach(([id,value])=>byId(id)?.addEventListener("click",()=>applyView(value)));
 byId("oaf-mobile-menu")?.addEventListener("click",()=>{
  const menu=byId("oaf-mobile-menu");setMobile(menu.getAttribute("aria-expanded")!=="true");
 });
 document.querySelectorAll(".head nav a[data-tab]").forEach(a=>a.addEventListener("click",()=>setMobile(false)));
 document.addEventListener("keydown",e=>{if(e.key==="Escape")setMobile(false)});
 document.addEventListener("click",e=>{
  const b=e.target.closest?.("[data-oaf-set-city]");
  if(b){setPlace(b.dataset.oafSetCity);return}
  const to=e.target.closest?.("[data-oaf-deepen]");
  if(to){applyView("tecnica");return}
 });
 const sel=byId("oaf-home-location");
 if(sel){
  sel.addEventListener("change",()=>setPlace(sel.value));
  setPlace(sel.value);
 }
 window.addEventListener("hashchange",hashAccess);
 hashAccess();
 applyView(mode);
 // Mark the place on every page, including mobile.
 const nav=document.querySelector(".head nav[aria-label='Secciones principales']");
 if(nav)nav.id="oaf-primary-nav";
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();