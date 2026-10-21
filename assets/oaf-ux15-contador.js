(function(){
"use strict";
function boot(){
 const root=document.getElementById("oaf-ux15-counter");
 if(!root||root.dataset.loaded)return;
 root.dataset.loaded="yes";
 const host="ccoronelepg-gif.github.io",key="OAF-Lambayeque";
 const num=document.createElement("span");num.className="oaf-ux15-counter-figure";
 num.textContent="Consultando…";
 const text=document.createElement("small");text.textContent="Visualizaciones públicas acumuladas, no personas únicas.";
 const link=document.createElement("a");link.href="https://counterapi.com/"+host+"/view/"+key;
 link.textContent="Consultar estadística del proveedor ↗";link.target="_blank";link.rel="noopener noreferrer";
 root.replaceChildren(num,text,link);
 let done=false;
 const render=value=>{
  if(!Number.isFinite(value)||value<0||done)return;
  done=true;num.textContent=Math.round(value).toLocaleString("es-PE")+" visitas";
  num.removeAttribute("data-unavailable");
 };
 const unavailable=()=>{
  if(done)return;
  num.dataset.unavailable="true";
  num.textContent="Contador temporalmente no disponible";
  text.textContent="El servicio externo no respondió; no se muestra una cifra inventada.";
 };
 // Endpoint público documentado de CounterAPI; una solicitud por visita de página.
 const url="https://counterapi.com/api/"+host+"/view/"+key;
 fetch(url,{cache:"no-store",mode:"cors"}).then(r=>{
  if(!r.ok)throw Error("HTTP "+r.status);return r.json();
 }).then(d=>{
  if(!Number.isFinite(Number(d.value)))throw Error("Respuesta sin contador");
  render(Number(d.value));
 }).catch(()=>{
  // JSONP de SOLO LECTURA: evita contar dos veces si el GET inicial fue procesado pero bloqueado por CORS.
  const callback="oafCountReadBack2026";const script=document.createElement("script");
  let finished=false;
  const fail=()=>{if(!finished){finished=true;delete window[callback];script.remove();unavailable()}};
  window[callback]=data=>{if(finished)return;finished=true;delete window[callback];script.remove();render(Number(data?.value));if(!done)unavailable()};
  script.src=url+"?readOnly=true&callback="+callback;
  script.async=true;script.onerror=fail;
  document.head.append(script);
  setTimeout(fail,6500);
 });
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();