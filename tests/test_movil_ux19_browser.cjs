/* Browser smoke-test UX19, ejecutar con servidor en http://127.0.0.1:8765.
 * Instalar: npm i --no-save playwright@1.56.1 && npx playwright install chromium */
const { chromium } = require("playwright");
const fs = require("node:fs");
const assert = require("node:assert/strict");
const snapshots="artifacts/mobile-ux19";
fs.mkdirSync(snapshots,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try {
  const context=await browser.newContext({deviceScaleFactor:1,locale:"es-PE",reducedMotion:"reduce"});
  // API del clima y rastreadores no condicionan diseño responsivo.
  await context.route("**/*", async route=>{
   const url=route.request().url();
   if(url.startsWith("http://127.0.0.1:8765/"))await route.continue();
   else await route.abort("blockedbyclient");
  });
  const page=await context.newPage();
  const base="http://127.0.0.1:8765/";
  for(const width of [320,375,390,430,768]){
   await page.setViewportSize({width,height:800});
   await page.goto(base,{waitUntil:"domcontentloaded",timeout:45000});
   await page.waitForTimeout(850);
   const data=await page.evaluate(()=>({
    viewport:window.innerWidth,
    body:document.body.scrollWidth,
    html:document.documentElement.scrollWidth,
    cssLoaded:[...document.styleSheets].some(s=>s.href?.includes("responsive-celulares-ux19.css")),
    menu:document.getElementById("oaf-mobile-menu")?.getBoundingClientRect().width,
    navVisible:(()=>{
      const e=document.getElementById("oaf-primary-nav");return e?getComputedStyle(e).display!=="none":false;
    })()
   }));
   assert.ok(data.cssLoaded,"CSS responsivo ausente");
   assert.ok(data.html<=width+4,"El documento excede el ancho a "+width+": "+JSON.stringify(data));
   if(width<=700){
    assert.ok(data.menu>30,"No aparece el botón de menú a "+width);
    assert.equal(data.navVisible,false,"Navegación desplegada de inicio sin tocar menú");
   }
   await page.screenshot({path:snapshots+"/portada-"+width+".png",fullPage:false});
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(base,{waitUntil:"domcontentloaded",timeout:45000});
  await page.locator("#oaf-mobile-menu").click();
  assert.ok(await page.locator("#oaf-primary-nav").isVisible(),"Menú no se abre");
  await page.locator('#oaf-primary-nav a[data-tab="cultivos"]').click();
  await page.waitForTimeout(350);
  assert.ok(await page.locator('[data-page="cultivos"]').isVisible(),"Cultivos y Sanidad no se abre");
  assert.equal(await page.locator("#oaf-mobile-menu").getAttribute("aria-expanded"),"false","Menú no se cierra tras navegar");
  await page.screenshot({path:snapshots+"/cultivos-390.png",fullPage:false});
  for(const tab of ["autor","clima"]){
   await page.locator("#oaf-mobile-menu").click();
   await page.locator('#oaf-primary-nav a[data-tab="'+tab+'"]').click();
   await page.waitForTimeout(300);
   assert.ok(await page.locator('[data-page="'+tab+'"]').isVisible(),"La pestaña "+tab+" no se muestra");
   await page.screenshot({path:snapshots+"/"+tab+"-390.png",fullPage:false});
  }
  await page.goto(base+"ecorregiones-clima-10k.html",{waitUntil:"domcontentloaded",timeout:45000});
  await page.setViewportSize({width:375,height:812});
  await page.waitForTimeout(250);
  const m=await page.evaluate(()=>({
   width:document.documentElement.scrollWidth,
   viewport:window.innerWidth,
   map:document.querySelector("#map")?.getBoundingClientRect().width,
   selector:document.querySelector(".controls select")?.getBoundingClientRect().width
  }));
  assert.ok(m.width<=379,"Mapa técnico desborda pantalla: "+JSON.stringify(m));
  assert.ok(m.map>230&&m.map<=375,"Mapa técnico no responde a móvil: "+JSON.stringify(m));
  await page.screenshot({path:snapshots+"/paisajes-375.png",fullPage:false});
  console.log("UX19: control de tamaños 320,375,390,430,768px, menú, tres pestañas y mapa 10K OK");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
