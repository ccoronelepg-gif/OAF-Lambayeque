/* OAF-Lambayeque PWA v1: mismas pestañas y fuentes que la web.
 * No guardar predicciones, JSON operativos ni avisos meteorológicos en CacheStorage.
 * Sitio en GitHub Pages: todo URL se resuelve relativo al scope /OAF-Lambayeque/. */
"use strict";
const RELEASE="oaf-pwa-shell-2026-10-22-v12";
const STATIC="oaf-pwa-static-2026-10-22-v12";
const SCOPE=new URL("./",self.registration.scope);
const ROOT=new URL("./",SCOPE).href;
const OFFLINE=new URL("offline.html",SCOPE).href;
const CORE=[
 "./","./offline.html","./manifest.webmanifest",
 "./assets/oaf-pwa.css","./assets/oaf-pwa.js",
 "./assets/oaf-app-icon.svg","./assets/oaf-app-maskable.svg",
 "./assets/logo-cecg.svg",
 "./assets/oaf-responsive-celulares-ux19.css",
 "./assets/oaf-ux24-riesgos-subpestanas.css",
 "./assets/oaf-ux24-riesgos-subpestanas.js",
 "./assets/oaf-ux27-exposicion-agricola.css",
 "./assets/oaf-ux27-exposicion-agricola.js",
 "./assets/oaf-ux28-vias-emergencias.css",
 "./assets/oaf-ux28-vias-emergencias.js"
];
const isInScope=url=>url.origin===SCOPE.origin&&url.pathname.startsWith(SCOPE.pathname);
const isScientificData=url=>url.pathname.includes("/datos/")||
  /\.(?:json|geojson|csv|pdf|xml|txt|zip|nc|parquet)$/i.test(url.pathname)||
  /(?:api|forecast|warning|boletin|ensoadvisory)/i.test(url.pathname.split("/").at(-1)||"");
const isStatic=url=>/\.(?:js|css|svg|png|jpe?g|webp|gif|woff2?|ico)$/i.test(url.pathname);

async function save(cache,request,response){
 if(response&&response.ok&&response.type!=="opaque")await cache.put(request,response.clone());
 return response;
}
async function precacheCore(){
 const cache=await caches.open(RELEASE);
 // Keep install tolerant to transient asset errors while requiring the core HTML.
 await Promise.allSettled(CORE.map(async local=>{
  const url=new URL(local,SCOPE);
  const result=await fetch(url.href,{cache:"reload"});
  if(!result.ok)throw new Error("Sin recurso "+url.pathname);
  await cache.put(url.href,result);
 }));
 if(!(await cache.match(ROOT)))throw new Error("No se pudo guardar la portada de OAF.");
}
self.addEventListener("install",event=>{
 event.waitUntil(precacheCore());
 // Do not skipWaiting automatically: prevent mid-session changes to interactive reports.
});
self.addEventListener("activate",event=>{
 event.waitUntil((async()=>{
  const all=await caches.keys();
  await Promise.all(all.filter(name=>name.startsWith("oaf-pwa-")&&![RELEASE,STATIC].includes(name)).map(name=>caches.delete(name)));
  await self.clients.claim();
 })());
});
async function navigate(req){
 const cache=await caches.open(RELEASE);
 try{
  // Network-first: every online visit checks GitHub Pages for newer HTML.
  const res=await fetch(req,{cache:"no-store"});
  if(res.ok)await save(cache,req,res);
  return res;
 }catch(_error){
  const existing=await cache.match(req,{ignoreSearch:true});
  if(existing)return existing;
  if(new URL(req.url).pathname===SCOPE.pathname||new URL(req.url).pathname.endsWith("/index.html")){
    const home=await cache.match(ROOT);if(home)return home;
  }
  return (await cache.match(OFFLINE))||new Response("Sin conexión. OAF necesita Internet para los pronósticos actuales.",{
    status:503,headers:{"Content-Type":"text/plain; charset=utf-8"}});
 }
}
async function staticFirst(req,event){
 const cache=await caches.open(STATIC);
 // Core resources are precached in RELEASE; newly fetched assets live in STATIC.
 const saved=(await cache.match(req))||(await caches.match(req));
 const refresh=fetch(req).then(async res=>{
  if(res.ok)await save(cache,req,res);
  return res;
 }).catch(()=>null);
 if(saved){
  event.waitUntil(refresh);
  return saved;
 }
 return (await refresh)||Response.error();
}
self.addEventListener("fetch",event=>{
 const req=event.request;
 if(req.method!=="GET")return;
 const url=new URL(req.url);
 if(!isInScope(url))return; // never intercept Open-Meteo, NOAA, SENAMHI or third parties
 if(isScientificData(url))return; // network-only; old advisories must not masquerade as current
 if(req.mode==="navigate"){
  event.respondWith(navigate(req));return;
 }
 if(isStatic(url)){
  event.respondWith(staticFirst(req,event));return;
 }
 // All other site endpoints follow the browser's native network behavior.
});
self.addEventListener("message",event=>{
 if(event.data?.type==="SKIP_WAITING")self.skipWaiting();
});
