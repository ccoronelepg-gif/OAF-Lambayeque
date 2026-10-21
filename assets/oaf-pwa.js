/* OAF-Lambayeque App v1 · misma interfaz y módulos del portal público.
 * Los eventos de instalación exigen un gesto real del usuario.
 * No se solicitan permisos de ubicación, notificaciones ni datos privados. */
(function(){
"use strict";
let installEvent=null,registration=null,reloading=false;
const standalone=()=>window.matchMedia("(display-mode: standalone)").matches||
  window.navigator.standalone===true;
const isIOS=()=>/iPad|iPhone|iPod/i.test(navigator.userAgent)||
  (navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);
const button=(text,cls)=>{const b=document.createElement("button");b.type="button";b.className=cls;b.textContent=text;return b};
const elem=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el};
function build(){
 if(document.getElementById("oaf-pwa-install-wrap"))return;
 const host=elem("div");host.id="oaf-pwa-install-wrap";
 const box=elem("div","oaf-pwa-banner");
 const icon=elem("img","oaf-pwa-logo");
 icon.src="assets/oaf-app-icon.svg";icon.alt="Ícono OAF-Lambayeque";
 icon.width=45;icon.height=45;
 const copy=elem("div","oaf-pwa-copy");
 copy.append(elem("strong",null,"Instala OAF-Lambayeque en tu celular"),
   elem("small",null,"El mismo observatorio: clima, RF, mapas, cultivos, sanidad, boletines y datos científicos."));
 const actions=elem("div","oaf-pwa-actions");
 const action=button("Cómo instalar","oaf-pwa-action");action.id="oaf-pwa-install-button";
 const dismiss=button("×","oaf-pwa-dismiss");
 dismiss.setAttribute("aria-label","Ocultar invitación de instalación");
 const instructions=elem("div","oaf-pwa-instructions");
 instructions.id="oaf-pwa-instructions";instructions.hidden=true;
 instructions.setAttribute("role","note");
 actions.append(action,dismiss);
 box.append(icon,copy,actions,instructions);host.append(box);
 const where=document.querySelector(".oaf-contextbar")||document.querySelector("header");
 if(where)where.after(host);else document.body.prepend(host);
 const info=elem("div","oaf-pwa-status");info.id="oaf-pwa-network-status";info.hidden=true;
 info.setAttribute("role","status");info.setAttribute("aria-live","polite");
 host.after(info);
 const update=elem("div","oaf-pwa-update");update.id="oaf-pwa-update";update.hidden=true;
 update.setAttribute("role","status");update.setAttribute("aria-live","polite");
 update.append(elem("span",null,"Hay una nueva versión de OAF-Lambayeque disponible."));
 const refresh=button("Actualizar aplicación","oaf-pwa-action");
 refresh.id="oaf-pwa-refresh";
 refresh.addEventListener("click",()=>{
  if(registration?.waiting){registration.waiting.postMessage({type:"SKIP_WAITING"});}
  else location.reload();
 });
 const later=button("Después","oaf-pwa-dismiss");
 later.setAttribute("aria-label","Actualizar más tarde");
 later.addEventListener("click",()=>update.hidden=true);
 update.append(refresh,later);document.body.append(update);
 function showInstructions(){
  const message=isIOS()?
   "En Safari, toca Compartir (cuadrado con flecha) → Añadir a pantalla de inicio → Añadir. La aplicación conservará las mismas seis pestañas.":
   "En Chrome para Android, abre el menú ⋮ y elige «Instalar aplicación» o «Añadir a pantalla principal». Después ábrela desde su ícono OAF.";
  instructions.textContent=message;
  instructions.hidden=!instructions.hidden;
 }
 action.addEventListener("click",async()=>{
  if(!installEvent){showInstructions();return}
  const prompt=installEvent;installEvent=null;
  try{
   await prompt.prompt();
   await prompt.userChoice;
  }catch(error){console.warn("OAF: no se pudo abrir la instalación",error);showInstructions()}
  action.textContent="Cómo instalar";
 });
 dismiss.addEventListener("click",()=>{
  host.hidden=true;
  try{sessionStorage.setItem("oaf-install-dismissed","yes")}catch(_e){}
 });
 if(standalone()||sessionStorageSafe())host.hidden=true;
 statusNetwork();
}
function sessionStorageSafe(){try{return sessionStorage.getItem("oaf-install-dismissed")==="yes"}catch(_e){return false}}
function statusNetwork(){
 const status=document.getElementById("oaf-pwa-network-status");
 if(!status)return;
 if(!navigator.onLine){
  status.hidden=false;
  status.textContent="Sin conexión a Internet. Puedes abrir recursos guardados, pero NO se actualizan pronósticos, alertas, porcentajes de El Niño ni datos de estaciones. Verifica siempre la fecha y la fuente antes de utilizarlos.";
 }else{
  status.hidden=true;status.textContent="";
 }
}
function offerUpdate(){
 if(!navigator.serviceWorker.controller||!registration?.waiting)return;
 const update=document.getElementById("oaf-pwa-update");
 if(update)update.hidden=false;
}
async function connectWorker(){
 if(!("serviceWorker" in navigator)||!window.isSecureContext)return;
 try{
  registration=await navigator.serviceWorker.register(new URL("app/sw.js",document.baseURI).href,{scope:new URL("app/",document.baseURI).href,updateViaCache:"none"});
  if(registration.waiting)offerUpdate();
  registration.addEventListener("updatefound",()=>{
   const worker=registration.installing;
   if(!worker)return;
   worker.addEventListener("statechange",()=>{
    if(worker.state==="installed"&&navigator.serviceWorker.controller)offerUpdate();
   });
  });
  navigator.serviceWorker.addEventListener("controllerchange",()=>{
   if(reloading)return;reloading=true;window.location.reload();
  });
  document.addEventListener("visibilitychange",()=>{
   if(document.visibilityState==="visible")registration.update().catch(()=>{});
  });
 }catch(err){console.warn("OAF: aplicación web sin instalación sin conexión",err)}
}
window.addEventListener("beforeinstallprompt",event=>{
 event.preventDefault();
 installEvent=event;
 const btn=document.getElementById("oaf-pwa-install-button");
 if(btn)btn.textContent="Instalar OAF";
 const host=document.getElementById("oaf-pwa-install-wrap");
 if(host&&!standalone()&&!sessionStorageSafe())host.hidden=false;
});
window.addEventListener("appinstalled",()=>{
 installEvent=null;
 const host=document.getElementById("oaf-pwa-install-wrap");if(host)host.hidden=true;
});
window.addEventListener("online",statusNetwork);
window.addEventListener("offline",statusNetwork);
function init(){build();connectWorker()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
else init();
})();