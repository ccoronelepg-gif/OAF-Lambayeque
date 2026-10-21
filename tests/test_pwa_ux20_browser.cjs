/* OAF UX20, ejecutar bajo servidor local en http://127.0.0.1:8765/ */
const {chromium}=require("playwright"),assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const context=await browser.newContext({viewport:{width:390,height:844},
   isMobile:true,hasTouch:true,serviceWorkers:"allow"});
  await context.route("**/*",route=>{
   const url=route.request().url();
   if(url.startsWith("http://127.0.0.1:8765/"))return route.continue();
   return route.abort();
  });
  const page=await context.newPage(),base="http://127.0.0.1:8765/";
  await page.goto(base+"?app=pwa#inicio",{waitUntil:"domcontentloaded",timeout:60000});
  await page.waitForTimeout(1000);
  const manifest=await page.locator('link[rel="manifest"]').getAttribute("href");
  assert.ok(manifest.includes("manifest.webmanifest"),"Manifest no vinculado");
  const data=await page.evaluate(async()=>{
   const response=await fetch(document.querySelector('link[rel="manifest"]').href);
   const manifest=await response.json();
   return {name:manifest.name,icons:manifest.icons.length,
      secure:window.isSecureContext,
      hasWorker:("serviceWorker" in navigator),
      tabs:[...document.querySelectorAll("section[data-page]")].map(e=>e.dataset.page)};
  });
  assert.ok(data.secure&&data.hasWorker,"Requiere localhost seguro");
  assert.ok(data.name.startsWith("OAF-Lambayeque"));
  assert.ok(data.icons>=3);
  for(const name of ["inicio","clima","autor","cultivos","nino","verificaciones"]){
   assert.ok(data.tabs.includes(name),"Perdida de pestaña: "+name);
  }
  await page.waitForFunction(()=>navigator.serviceWorker.controller!==null,{timeout:45000}).catch(async()=>{
   await page.reload({waitUntil:"domcontentloaded"});
   await page.waitForFunction(()=>navigator.serviceWorker.controller!==null,{timeout:15000});
  });
  const bar=page.locator("#oaf-pwa-install-wrap");
  assert.ok(await bar.count(),"No se muestra acceso a instalación");
  const action=page.locator("#oaf-pwa-install-button");
  await action.click();
  const instructions=page.locator("#oaf-pwa-instructions");
  assert.ok(await instructions.isVisible(),"No aparecen pasos para Android");
  await page.locator("#oaf-mobile-menu").click();
  await page.locator('#oaf-primary-nav a[data-tab="cultivos"]').click();
  await page.waitForTimeout(250);
  assert.ok(await page.locator("#cultivos").isVisible(),"No se abre Sanidad en la app");
  await context.setOffline(true);
  await page.goto(base+"offline.html",{waitUntil:"domcontentloaded",timeout:15000});
  assert.ok((await page.locator("h1").textContent()).includes("No hay conexión"));
  console.log("OAF App: manifiesto, SW, seis pestañas, instrucciones, Sanidad y pantalla offline OK");
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
