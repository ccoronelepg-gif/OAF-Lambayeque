/* UX39 – comprobación de geovisores en Chromium; solo archivos locales. */
"use strict";
const {chromium}=require("playwright"),assert=require("node:assert/strict");
(async()=>{
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const context=await browser.newContext({viewport:{width:1365,height:850},locale:"es-PE"});
  await context.route("**/*",route=>route.request().url().startsWith("http://127.0.0.1:8765/")?route.continue():route.abort("blockedbyclient"));
  const page=await context.newPage();const errors=[];
  // UX54: respuesta estacional simulada sin Internet, seis meses completos Dic26–May27.
  const seasonalTime=[],seasonalRain=[],seasonalTemp=[];
  for(let y=2026,m=12;y<2027||m<=5;){
   const length=new Date(Date.UTC(y,m,0)).getUTCDate();
   for(let d=1;d<=length;d++)for(const hour of ["00","06","12","18"]){
    seasonalTime.push(y+"-"+String(m).padStart(2,"0")+"-"+String(d).padStart(2,"0")+"T"+hour+":00");
    seasonalRain.push(.3125);seasonalTemp.push(24.5);
   }
   if(m===12){y++;m=1}else m++;
  }
  await page.route("https://seasonal-api.open-meteo.com/**",route=>{
   const target=new URL(route.request().url());
   assert.equal(target.searchParams.get("models"),"ecmwf_seas5_ensemble_mean");
   assert.equal(target.searchParams.get("hourly"),"precipitation,temperature_2m");
   assert.equal(target.searchParams.get("daily"),null,"El proveedor estacional no admite precipitación diaria");
   return route.fulfill({
    status:200,contentType:"application/json",
    body:JSON.stringify({latitude:-6.77,longitude:-79.84,
     hourly_units:{precipitation:"mm",temperature_2m:"°C"},
     hourly:{time:seasonalTime,precipitation:seasonalRain,temperature_2m:seasonalTemp}})
   });
  });

  page.on("pageerror",err=>errors.push(err.message));
  await page.goto("http://127.0.0.1:8765/",{waitUntil:"domcontentloaded",timeout:45000});
  await page.waitForSelector("#oaf-parcel-territorio",{state:"attached",timeout:20000});
  await page.waitForSelector("#oaf-parcel-escenarios",{state:"attached",timeout:20000});
  await page.waitForFunction(()=>Boolean(window.oafUx30Context?.()?.scene?.bounds&&window.oafUx29ScenarioApi?.get?.()?.scene?.bounds),{timeout:20000});
  assert(await page.locator("#oaf-area-territorio").count(),"No se encuentra entrada de coordenadas del visor territorial");
  assert(await page.locator("#oaf-area-escenarios").count(),"No se encuentra entrada de coordenadas del visor de escenarios");
  const inside=await page.evaluate(()=>["territorio","escenarios"].map(k=>({
   area:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-area-"+k),
   polygon:!!document.querySelector("#oaf-ux29-"+(k==="territorio"?"territory":"scenario")+" .oaf-ux29-mapcolumn #oaf-parcel-"+k)
  })));
  assert(inside.every(x=>x.area&&x.polygon),"Los módulos deben estar DENTRO de la columna de mapas "+JSON.stringify(inside));
  const order=await page.evaluate(()=>["territorio","escenarios"].map(k=>{
   const root=document.getElementById(k==="territorio"?"oaf-ux29-territory":"oaf-ux29-scenario");
   const layout=root.querySelector(".oaf-ux29-layout"),column=root.querySelector(".oaf-ux29-mapcolumn");
   const area=column.querySelector("#oaf-area-"+k),map=column.querySelector(".oaf-ux29-mapcontent"),parcel=column.querySelector("#oaf-parcel-"+k);
   const diagnosis=layout.querySelector(".oaf-ux29-diagnosis");
   const hydro=k==="escenarios"?layout.querySelector("#oaf-ux36-panel"):null;
   const validation=k==="escenarios"?layout.querySelector("#oaf-ux37-panel"):null;
   const forecastMap=k==="escenarios"?column.querySelector(".oaf-ux29-scenemap"):null;
   const follows=(a,b)=>!!(a&&b&&(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING));
   return {k,areaBeforeParcel:follows(area,parcel),parcelBeforeMap:follows(parcel,map),
    mapBeforeDiagnosis:follows(map,diagnosis),
    hydroOrder:k==="territorio"||Boolean(hydro&&forecastMap&&follows(forecastMap,diagnosis)&&
      follows(diagnosis,hydro)&&hydro.parentElement===layout&&follows(hydro,validation)&&validation?.parentElement===layout),
    parcelFold:parcel.querySelector(".oaf-parcel-fold")?.open===false,
    pointPanelHidden:k==="territorio"||!column.querySelector("#oaf-area-point-details-"+k)||getComputedStyle(column.querySelector("#oaf-area-point-details-"+k)).display==="none",
    hasExpand:!!column.querySelector(".oaf-map-expand"),diagnosisFullWidth:!!diagnosis&&diagnosis.parentElement===layout};
  }));
  assert(order.every(x=>x.areaBeforeParcel&&x.parcelBeforeMap&&x.mapBeforeDiagnosis&&x.hydroOrder&&
    x.parcelFold&&x.pointPanelHidden&&x.hasExpand&&x.diagnosisFullWidth),
   "Jerarquía visual incorrecta: "+JSON.stringify(order));
  const weekly=await page.evaluate(()=>{
    const week=document.getElementById("oaf-ux14-rf-semana"),monthly=document.getElementById("oaf-ux14-rf-mes");
    return {weekly:!!week,monthly:!!monthly,first:!!(week&&monthly&&(week.compareDocumentPosition(monthly)&Node.DOCUMENT_POSITION_FOLLOWING)),
      visible:week?getComputedStyle(week).display!=="none":false,controls:!!document.getElementById("oaf-ux14-ciudad")};
  });
  assert(weekly.weekly&&weekly.monthly&&weekly.first&&weekly.visible&&weekly.controls,
    "Gráfico semanal RF/Open-Meteo/ERA5 no figura antes del horizonte mensual: "+JSON.stringify(weekly));
  // UX54: RF no validado se excluye; se muestran ERA5 y SEAS5 cuando están completos.
  await page.waitForFunction(()=>{
   const svg=document.querySelector("#oaf-ux14-monthchart svg");
   return svg&&svg.querySelectorAll("polyline").length>=2 &&
    document.querySelector("#oaf-ux44-seasonal-note")?.textContent.includes("6/6 meses");
  },null,{timeout:20000});
  const estacional=await page.evaluate(()=>{
   const root=document.querySelector("#oaf-ux14-rf-mes");
   return {polyline:root.querySelectorAll("#oaf-ux14-monthchart svg polyline").length,
    openMeteo:[...root.querySelectorAll(".oaf-ux14-key span")].some(x=>x.textContent.includes("Open-Meteo")),
    counter:!!document.querySelector("#oaf-ux15-counter"),message:document.querySelector("#oaf-ux44-seasonal-note")?.textContent};
  });
  assert(estacional.polyline===2&&estacional.openMeteo&&!estacional.counter,
    "Gráfico mensual debe mostrar climatología y SEAS5, sin presentar RF no validado: "+JSON.stringify(estacional));

  // Activar la pestaña de clima: el mapa está correctamente oculto mientras Inicio está activo.
  await page.locator('#oaf-primary-nav a[data-tab="clima"]').click();
  await page.waitForFunction(()=>document.querySelector('#clima')&&!document.querySelector('#clima').hidden,{timeout:10000});
  // UX54: mapas DEM por pisos, estaciones inventariadas y variables históricas adicionales.
  await page.waitForSelector("#oaf-regional-hist-map svg",{timeout:20000});
  await page.waitForSelector("#oaf-stations-map svg",{timeout:20000});
  await page.locator("#oaf-clima-bloque-historico #oaf-area-clima form").evaluate(el=>{
   for(let parent=el;parent;parent=parent.parentElement)if(parent.tagName==="DETAILS")parent.open=true;
  });
  await page.locator("#oaf-clima-bloque-historico #oaf-area-clima form").evaluate(el=>{
   for(let parent=el;parent;parent=parent.parentElement)if(parent.tagName==="DETAILS")parent.open=true;
  });
  await page.waitForSelector("#oaf-clima-bloque-historico #oaf-area-clima form",{timeout:20000});
  const climateMaps=await page.evaluate(()=>({
   dem:document.querySelectorAll("#oaf-regional-hist-map svg circle").length,
   demColors:new Set([...document.querySelectorAll("#oaf-regional-hist-map svg circle")].map(x=>x.getAttribute("fill"))).size,
   stations:document.querySelectorAll("#oaf-stations-list tbody tr").length,
   mapped:document.querySelectorAll("#oaf-stations-map svg circle.oaf-map-symbol").length,
   humidity:[...document.querySelectorAll("#oaf-regional-var option")].some(x=>x.value==="humedad_relativa_pct"),
   radiation:[...document.querySelectorAll("#oaf-regional-var option")].some(x=>x.value==="radiacion_mj_m2"),
   areaForm:!!document.querySelector("#oaf-clima-bloque-historico #oaf-area-clima form")
  }));
  assert(climateMaps.dem>=420&&climateMaps.demColors>=7,"El DEM debe distinguir las franjas altitudinales: "+JSON.stringify(climateMaps));
  assert(climateMaps.stations===13&&climateMaps.mapped>=5,"El inventario debe listar 13 estaciones y mapear solo las georreferenciadas: "+JSON.stringify(climateMaps));
  assert(climateMaps.humidity&&climateMaps.radiation&&climateMaps.areaForm,"Faltan variables o consulta de zona productora en data histórica: "+JSON.stringify(climateMaps));
  // Simular una respuesta ERA5 diaria completa para probar el cálculo 1996–2025 sin depender de Internet.
  const areaEraTime=[],areaEraTemp=[],areaEraRain=[],areaEraSolar=[],areaEraHumidity=[];
  for(let y=1996;y<=2025;y++)for(let t=Date.UTC(y,0,1);t<Date.UTC(y+1,0,1);t+=86400000){
   areaEraTime.push(new Date(t).toISOString().slice(0,10));
   areaEraTemp.push(24+(y-1996)/100);areaEraRain.push(0.1);
   areaEraSolar.push(18);areaEraHumidity.push(70);
  }
  await page.route("https://archive-api.open-meteo.com/**",route=>route.fulfill({status:200,contentType:"application/json",
   body:JSON.stringify({latitude:-6.77,longitude:-79.84,daily:{time:areaEraTime,
    temperature_2m_mean:areaEraTemp,precipitation_sum:areaEraRain,
    shortwave_radiation_sum:areaEraSolar,relative_humidity_2m_mean:areaEraHumidity}})}));
  await page.evaluate(()=>{const f=document.querySelector("#oaf-area-clima form");f.elements.namedItem("lat").value="-6.7714";f.elements.namedItem("lon").value="-79.8409";f.elements.namedItem("name").value="Punto histórico de prueba";f.requestSubmit()});
  await page.waitForSelector("#oaf-area-clima-serie svg",{timeout:45000});
  const customHistory=await page.evaluate(()=>({points:document.querySelectorAll("#oaf-area-clima-serie svg circle").length,title:document.querySelector("#oaf-area-clima-serie h3")?.textContent,source:document.querySelector("#oaf-area-clima-serie .oaf-area-metodo")?.textContent}));
  assert(customHistory.points===30&&customHistory.title?.includes("Punto histórico de prueba")&&customHistory.source?.includes("ERA5"),"No se construyó la serie histórica de la parcela: "+JSON.stringify(customHistory));

  // Probar los filtros DEM y de estaciones, además de la selección de un marcador.
  await page.locator("#oaf-regional-map-filter").selectOption("montana_alta");
  const filteredDem=await page.locator('#oaf-regional-hist-map svg circle[opacity=".94"]').count();
  assert(filteredDem>0&&filteredDem<420,"El filtro altitudinal del DEM no actualiza los puntos visibles: "+filteredDem);
  await page.locator("#oaf-regional-map-filter").selectOption("all");
  await page.locator("#oaf-stations-floor").selectOption("montana_alta");
  const highStations=await page.locator("#oaf-stations-list tbody tr").count();
  assert(highStations>0&&highStations<13,"El filtro altitudinal de estaciones no filtra el inventario: "+highStations);
  await page.locator("#oaf-stations-floor").selectOption("all");
  await page.locator("#oaf-stations-map svg circle.oaf-map-symbol").first().click();
  const selectedStation=await page.locator("#oaf-stations-selected").textContent();
  assert(/\(\d{6}\)/.test(selectedStation||""),"El marcador no abre la ficha resumida de la estación: "+selectedStation);
  // UX42: Carrusel Inicio y lectura independiente en área semanal.
  await page.locator('#oaf-primary-nav a[data-tab="inicio"]').click();
  await page.waitForFunction(()=>document.querySelector('#inicio')&&!document.querySelector('#inicio').hidden,{timeout:10000});
  await page.waitForSelector("#oaf-ux42-slide-official",{state:"attached",timeout:12000});
  const intro=await page.evaluate(()=>{
    const c=document.querySelector("#inicio .oaf-ux42-carousel");
    return {count:c?.querySelectorAll(".oaf-ux42-slide").length,
      dots:c?.querySelectorAll(".oaf-ux42-dot").length,
      official:c?.querySelector("#oaf-ux15-enfen-exp")?.textContent,
      source:c?.querySelector(".oaf-ux15-source")?.textContent};
  });
  assert(intro.count===3&&intro.dots===3,"No hay tres láminas en carrusel: "+JSON.stringify(intro));
  assert(intro.official?.includes("Interpretación:")&&!intro.official?.includes("inundación"),
    "Interpretación ENFEN innecesariamente descriptiva: "+intro.official);
  await page.evaluate(()=>document.querySelector('#inicio button[aria-label="Próximos 7 días"]').click());
  assert(await page.locator("#oaf-ux42-slide-week").evaluate(x=>!x.hidden),"Carrusel no muestra 7 días");
  await page.evaluate(()=>document.querySelector('#inicio button[aria-label="Horizonte mensual"]').click());
  assert(await page.locator("#oaf-ux42-slide-month").evaluate(x=>!x.hidden),"Carrusel no muestra mensual");
  const pointForecast={latitude:-6.15,longitude:-79.71,daily:{time:["2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-10-31","2026-11-01","2026-11-02"],
    precipitation_sum:[0.03,0.08,0.12,0.16,0.2,0.14,0.01],temperature_2m_max:[24,25,26,27,28,27,25],
    temperature_2m_min:[17,18,18,19,20,19,18],relative_humidity_2m_mean:[72,70,68,74,76,75,71],
    shortwave_radiation_sum:[18,19,20,21,19,18,17],wind_speed_10m_max:[12,13,11,14,15,12,10],
    et0_fao_evapotranspiration:[3.2,3.4,3.5,3.6,3.3,3.1,3.0],vapour_pressure_deficit_max:[1.1,1.2,1.3,1.0,0.9,1.0,1.2]}};
  const eraTime=[],eraRain=[],eraTemp=[],eraHumidity=[],eraRadiation=[];
  for(let y=1996;y<=2025;y++)for(let t=Date.UTC(y,0,1);t<Date.UTC(y+1,0,1);t+=86400000){
    eraTime.push(new Date(t).toISOString().slice(0,10));eraRain.push(0.1);eraTemp.push(26);eraHumidity.push(70);eraRadiation.push(18);
  }
  // El archivo histórico utiliza OTRO host: archive-api.open-meteo.com.
  await page.route("https://archive-api.open-meteo.com/**",route=>route.fulfill({status:200,contentType:"application/json",
    body:JSON.stringify({latitude:-6.15,longitude:-79.71,daily:{time:eraTime,precipitation_sum:eraRain,temperature_2m_max:eraTemp,temperature_2m_mean:eraTemp,relative_humidity_2m_mean:eraHumidity,shortwave_radiation_sum:eraRadiation}})}));
  await page.route("https://api.open-meteo.com/**",async route=>{
    const url=route.request().url();
    if(url.includes("archive"))await route.fulfill({status:200,contentType:"application/json",
      body:JSON.stringify({latitude:-6.15,longitude:-79.71,daily:{time:eraTime,precipitation_sum:eraRain,temperature_2m_max:eraTemp,temperature_2m_mean:eraTemp,relative_humidity_2m_mean:eraHumidity,shortwave_radiation_sum:eraRadiation}})});
    else await route.fulfill({status:200,contentType:"application/json",body:JSON.stringify(pointForecast)});
  });
  await page.locator('#oaf-primary-nav a[data-tab="autor"]').click();
  await page.waitForFunction(()=>document.querySelector('#autor')&&!document.querySelector('#autor').hidden,{timeout:10000});
  const formExists=await page.evaluate(()=>!!document.querySelector("#oaf-ux14-rf-semana #oaf-area-semanal form"));
  assert(formExists,"No hay coordenadas UTM/WGS84 en horizonte semanal");
  const outcome=await page.evaluate(()=>{
    const f=document.querySelector("#oaf-area-semanal form");
    f.elements.namedItem("lat").value="-6.15083";f.elements.namedItem("lon").value="-79.7142";
    f.elements.namedItem("name").value="Sector piloto";f.requestSubmit();
    return window.OAFTerritory.getActivePoint("semanal");
  });
  assert(outcome?.name==="Sector piloto"&&Math.abs(outcome.lat+6.15083)<.00001,"Consulta puntual semanal no guarda coordenadas");
  await page.waitForFunction(()=>document.querySelector("#oaf-ux14-weekchart svg")?.querySelectorAll("rect[role=img]").length>=14 && document.querySelector("#oaf-ux14-weekstatus")?.textContent.includes("ERA5:"),null,{timeout:22000});
  const plotInfo=await page.evaluate(()=>{
    const root=document.querySelector("#oaf-ux14-weekchart");
    const ticks=[...root.querySelectorAll('svg text[text-anchor="end"]')].map(x=>x.textContent);
    const desc=document.querySelector("#oaf-ux14-weekstatus")?.textContent;
    return {ticks,desc,polylines:root.querySelectorAll("svg polyline").length,
     bars:root.querySelectorAll("svg rect[role=img]").length,
     days:new Set([...root.querySelectorAll("svg rect[role=img]")].map(x=>x.getAttribute("aria-label").slice(0,10))).size};
  });
  assert(plotInfo.ticks.length>=4&&new Set(plotInfo.ticks).size===plotInfo.ticks.length,
    "Escala con etiquetas repetidas: "+JSON.stringify(plotInfo));
  assert(plotInfo.bars>=14&&plotInfo.days===7&&plotInfo.polylines===0,
    "El gráfico de siete días debe usar barras agrupadas, no líneas: "+JSON.stringify(plotInfo));
  assert(plotInfo.desc?.includes("Sector piloto")&&plotInfo.desc?.includes("ERA5"),
    "Análisis por coordenada/ERA5 no disponible: "+JSON.stringify(plotInfo));
  const pointTable=await page.evaluate(()=>{
    const root=document.querySelector("#oaf-ux51-point-details");
    return {visible:!!root&&!root.hidden,rows:root?.querySelectorAll("tbody tr").length||0,
      text:root?.textContent||"",headers:[...root?.querySelectorAll("thead th")||[]].map(x=>x.textContent)};
  });
  assert(pointTable.visible&&pointTable.rows===7,"No aparece la tabla agroclimática diaria de la parcela: "+JSON.stringify(pointTable));
  for(const field of ["HR media (%)","Radiación (MJ/m²)","ET₀ FAO (mm)","DPV máx. (kPa)"])
    assert(pointTable.headers.includes(field),"Falta el indicador "+field+": "+JSON.stringify(pointTable.headers));

  await page.locator('#oaf-primary-nav a[data-tab="verificaciones"]').click();
  await page.waitForFunction(()=>document.querySelector('#verificaciones')&&!document.querySelector('#verificaciones').hidden,{timeout:10000});
  await page.waitForFunction(()=>document.querySelector("#oaf-ux29-territory .oaf-ux29-mapcolumn .oaf-ux29-mapcontent svg"),{timeout:20000});
  const massTerritory=page.locator('#oaf-ux29-territory [data-ux30-layer="movmasa"]');
  await massTerritory.evaluate(el=>{for(let p=el;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true;});
  await massTerritory.check();
  await page.waitForSelector('#oaf-ux29-territory .oaf-ux30-layer image[data-title="Movimientos en masa"]',{timeout:10000});
  const layerDiagnosis=await page.locator("#oaf-ux29-territory .oaf-ux29-diagbody").textContent();
  assert(layerDiagnosis?.includes("Movimientos en masa"),"El diagnóstico no explica la capa geográfica seleccionada");
  await massTerritory.uncheck();
  await page.waitForFunction(()=>!document.querySelector('#oaf-ux29-territory .oaf-ux30-layer image[data-title="Movimientos en masa"]'),{timeout:10000});
  const result=await page.evaluate(()=>{
   const f=document.querySelector("#oaf-area-territorio form");f.elements.namedItem("name").value="Parcela de prueba";
   f.elements.namedItem("lat").value="-6.15083";f.elements.namedItem("lon").value="-79.7142";f.requestSubmit();
   return {point:window.OAFTerritory?.getActivePoint?.("territorio"),other:window.OAFTerritory?.getActivePoint?.("escenarios")};
  });
  assert(Math.abs(result.point?.lat+6.15083)<1e-5,"Punto territorial no fue persistido");
  assert(!result.other,"El punto del visor territorial contaminó escenarios");
  const geo={type:"FeatureCollection",features:[{type:"Feature",properties:{name:"Fundo de prueba"},geometry:{type:"Polygon",
   coordinates:[[[-79.7142,-6.15083],[-79.7132,-6.15083],[-79.7132,-6.14983],[-79.7142,-6.14983],[-79.7142,-6.15083]]]}}]};
  await page.locator("#oaf-parcel-territorio [data-ux39-file]").setInputFiles({
   name:"fundo.geojson",mimeType:"application/geo+json",buffer:Buffer.from(JSON.stringify(geo))
  });
  await page.waitForFunction(()=>!!window.OAFParcelas?.get?.("territorio"),null,{timeout:10000});
  const p=await page.evaluate(()=>window.OAFParcelas?.get?.("territorio"));
  assert(p&&p.ha>1&&p.ha<1.4,"El importador no calculó un polígono de superficie aproximada válida");
  await page.waitForTimeout(350);
  assert(await page.locator("#oaf-ux24-region-map #oaf-ux39-geom-territorio").count(),"El polígono no se dibujó en el SVG territorial");
  await page.locator('#oaf-primary-nav a[data-tab="autor"]').click();
  await page.waitForFunction(()=>document.querySelector('#autor')&&!document.querySelector('#autor').hidden,{timeout:10000});
  const massScenario=page.locator('#oaf-ux29-scenario [data-ux29-layer="mass"]');
  await massScenario.evaluate(el=>{for(let p=el;p;p=p.parentElement)if(p.tagName==="DETAILS")p.open=true;});
  await massScenario.check();
  await page.waitForSelector("#oaf-ux29-scenario .oaf-ux29-mass",{timeout:10000});
  await massScenario.uncheck();
  await page.waitForFunction(()=>!document.querySelector("#oaf-ux29-scenario .oaf-ux29-mass"),{timeout:10000});
  const escenario=await page.evaluate(()=>{
   const f=document.querySelector("#oaf-area-escenarios form");
   f.elements.namedItem("format").value="utm";
   f.elements.namedItem("format").dispatchEvent(new Event("change",{bubbles:true}));
   f.elements.namedItem("east").value="642270.904567";f.elements.namedItem("north").value="9319951.242352";
   f.elements.namedItem("zone").value="17";f.elements.namedItem("hemi").value="S";f.requestSubmit();
   return window.OAFTerritory.getActivePoint("escenarios");
  });
  assert(Math.abs(escenario.lat+6.15083)<.00001,"Conversión UTM S17 errónea en visor de escenarios");
  assert(Math.abs(escenario.lon+79.7142)<.00001,"Longitud UTM incorrecta");
  await page.waitForTimeout(350);
  assert(await page.locator("#oaf-ux29-forecast-map #oaf-area-pin-escenarios").count(),"El punto no se dibujó en el SVG del visor de escenarios");
  assert(await page.locator("#oaf-ux24-region-map #oaf-area-pin-territorio").count(),"Desapareció el punto territorial al definir escenario");
  // Prueba responsive: el visor debe aparecer ANTES del listado de capas en móvil.
  await page.locator('#oaf-primary-nav a[data-tab="verificaciones"]').click();
  await page.waitForFunction(()=>document.querySelector('#verificaciones')&&!document.querySelector('#verificaciones').hidden,{timeout:10000});
  await page.setViewportSize({width:390,height:844});
  const responsive=await page.evaluate(()=>{
   const layout=document.querySelector("#oaf-ux29-territory .oaf-ux29-layout"),
    map=document.querySelector("#oaf-ux29-territory .oaf-ux29-mapcolumn"),
    side=document.querySelector("#oaf-ux29-territory .oaf-ux29-sidebar");
   return {columns:getComputedStyle(layout).gridTemplateColumns,
    mapOrder:getComputedStyle(map).order,sideOrder:getComputedStyle(side).order,
    cssLoaded:[...document.styleSheets].some(x=>x.href?.includes("oaf-visores-ux40.css"))};
  });
  assert(responsive.cssLoaded&&responsive.mapOrder==="-1"&&responsive.sideOrder==="1",
    "Mapa no prioritario en móvil: "+JSON.stringify(responsive));
  const importantErrors=errors.filter(x=>/ux39|oaf-parcel|oaf-area|Cannot read properties of undefined/.test(x));
  assert.deepEqual(importantErrors,[],"Errores JavaScript en los nuevos módulos: "+importantErrors.join(" | "));
  console.log("UX39 browser OK: visores integrados, independencia, GeoJSON, áreas, marcador y UTM WGS84");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
