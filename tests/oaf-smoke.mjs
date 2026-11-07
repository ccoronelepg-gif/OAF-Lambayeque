/* Pruebas de regresión independientes del navegador para OAF-Lambayeque.
 * Ejecutar con: node --test tests/oaf-smoke.mjs
 */
import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,existsSync} from "node:fs";
import {resolve,dirname} from "node:path";
import {fileURLToPath} from "node:url";
import {Script,runInNewContext} from "node:vm";

const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),"..");
const pathOf=path=>resolve(ROOT,path);
const read=path=>readFileSync(pathOf(path),"utf8");
const exists=path=>existsSync(pathOf(path));
const html=read("index.html");

test("Los seis paneles principales existen y el bloque semanal redundante de Inicio fue eliminado",()=>{
  for(const page of ["inicio","clima","autor","cultivos","nino","verificaciones"])
    assert.match(html,new RegExp('<section[^>]+data-page="'+page+'"'));
  assert.doesNotMatch(html,/id="oaf-forecast-home"/);
  assert.match(read("assets/oaf-territorio-compartido.js"),/Mi zona productora · coordenadas \/ UTM/);
});

test("Todas las bibliotecas JavaScript de la portada existen y tienen sintaxis válida",()=>{
  const refs=[...html.matchAll(/<script\b[^>]*\bsrc=["']([^"']+)/g)].map(x=>x[1].split("?")[0]);
  assert.ok(refs.length>=40,"faltan scripts principales");
  assert.equal(refs.length,new Set(refs).size,"script duplicado en el HTML");
  for(const file of refs){
    assert.ok(exists(file),"no existe "+file);
    assert.doesNotThrow(()=>new Script(read(file),{filename:file}),"sintaxis incorrecta en "+file);
  }
});

test("Todas las hojas de estilo enlazadas existen",()=>{
  const files=[...html.matchAll(/<link\b[^>]*\brel=["']stylesheet["'][^>]*\bhref=["']([^"']+)/g)].map(x=>x[1].split("?")[0]);
  assert.ok(files.length>=20);
  for(const file of files)assert.ok(exists(file),"CSS no encontrado: "+file);
});

test("PWA: manifiesto, iconos, ruta offline y recursos precargados disponibles",()=>{
  const manifest=JSON.parse(read("manifest.webmanifest"));
  assert.equal(manifest.display,"standalone");
  assert.ok(manifest.icons.length>=3);
  for(const icon of manifest.icons)assert.ok(exists(icon.src),"icono inexistente: "+icon.src);
  const sw=read("sw.js");
  assert.match(sw,/const RELEASE="oaf-pwa-shell-[^"]+"/);
  const core=sw.match(/const CORE=\[([\s\S]*?)\];/);
  assert.ok(core,"falta catálogo de recursos PWA");
  const paths=[...core[1].matchAll(/"(\.\/[^"]+)"/g)].map(x=>x[1].slice(2)).filter(Boolean);
  assert.equal(paths.length,new Set(paths).size,"hay recursos repetidos en el precaché");
  for(const file of paths)assert.ok(exists(file),"precaché inexistente: "+file);
  for(const file of ["assets/oaf-ux14-reorganizacion.css","assets/oaf-ux14-reorganizacion.js",
   "assets/oaf-ux15-rf-salidas.js","assets/oaf-responsive-celulares-ux19.js",
   "assets/oaf-ux21-editorial.js","assets/oaf-ux17-fotos-mapas.css"])
   assert.ok(paths.includes(file),"recurso esencial no precargado: "+file);
  assert.ok(exists("offline.html"));
  assert.match(sw,/if\(isScientificData\(url\)\)return/,"los datos científicos deben consultarse en red");
});

function mockSvg(tag){
  return {tag,attrs:{},children:[],textContent:"",
    setAttribute(k,v){this.attrs[k]=String(v);},
    append(...children){this.children.push(...children);},
    replaceChildren(...children){this.children=[...children];}};
}

test("PWA: actualización atómica, sin almacenar pronósticos o avisos caducados",()=>{
  const sw=read("sw.js");
  assert.match(sw,/const REQUIRED=\[/,"falta la lista de recursos críticos");
  for(const file of ["./","./offline.html","./manifest.webmanifest",
    "./assets/oaf-pwa.js","./assets/oaf-territorio-compartido.js",
    "./assets/oaf-parcelas-ux39.js","./assets/oaf-ux15-rf-salidas.js"]){
    assert.ok(sw.includes(JSON.stringify(file)),"recurso crítico no exigido: "+file);
  }
  assert.match(sw,/if\(missing\.length\)throw new Error/,"una instalación parcial no debe activarse");
  assert.match(sw,/if\(isScientificData\(url\)\)return/,"datos científicos siempre en red");
  assert.match(sw,/if\(!isInScope\(url\)\)return/,"los proveedores externos no deben interceptarse");
  assert.match(sw,/fetch\(req,\{cache:"no-store"\}\)/,"HTML debe revalidarse en la red");
});

test("El gráfico semanal usa barras y ejes continuos incluso con lluvia fraccionaria y ceros",()=>{
  const window={};
  const document={readyState:"loading",addEventListener(){},getElementById(){return null},
    createElementNS(_ns,tag){return mockSvg(tag);},createElement:mockSvg};
  runInNewContext(read("assets/oaf-ux15-rf-salidas.js"),{window,document,console}, {filename:"oaf-ux15-rf-salidas.js"});
  assert.equal(typeof window.OAFWeeklyBars,"function");
  const root=mockSvg("div");
  const dates=["2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-10-31","2026-11-01","2026-11-02"];
  window.OAFWeeklyBars(root,dates,[
    {name:"Open-Meteo",color:"#2288aa",values:[0,0.1,0.2,0.3,0.4,0.2,0]},
    {name:"Random Forest",color:"#9966aa",values:[0,0.2,0.3,null,0.1,0.4,0.5]}
  ],"mm/día");
  const svg=root.children[0];
  assert.equal(svg.tag,"svg");
  const bars=svg.children.filter(x=>x.tag==="rect");
  assert.equal(bars.length,13,"no deben dibujarse barras para valores faltantes");
  assert.equal(bars.filter(x=>Number(x.attrs.height)===0).length,3,"los ceros no deben simular lluvia");
  const labels=svg.children.filter(x=>x.tag==="text").map(x=>x.textContent);
  const ticks=svg.children.filter(x=>x.tag==="text"&&x.attrs.x==="53").map(x=>Number(x.textContent.replace(",",".")));
  assert.ok(ticks.length>=5);
  assert.equal(ticks.length,new Set(ticks).size,"el eje repite etiquetas");
  assert.ok(ticks.every((v,i)=>i===0||v>ticks[i-1]),"las etiquetas no son crecientes");
  assert.equal(labels.filter(t=>/^\d\d\/\d\d$/.test(t)).length,7);
});

test("UTM WGS84 zona 17S convierte puntos conocidos y rechaza coordenadas fuera de Lambayeque",()=>{
  const window={};
  const document={readyState:"loading",addEventListener(){}};
  runInNewContext(read("assets/oaf-territorio-compartido.js"),{window,document,console},{filename:"oaf-territorio-compartido.js"});
  const api=window.OAFTerritory;
  for(const [name,e,n,lat,lon] of [
    ["Chiclayo",628093.629,9251369.164,-6.7714,-79.8409],
    ["Motupe",642270.905,9319951.242,-6.15083,-79.7142],
    ["Olmos",638657.194,9337936.142,-5.98825,-79.74723]
  ]){
    const [a,b]=api.utmToGeographic(e,n,17,"S");
    assert.ok(Math.abs(a-lat)<0.00001&&Math.abs(b-lon)<0.00001,name+" no convirtió correctamente");
  }
  assert.throws(()=>api.validatePoint(-8,-78),/fuera del ámbito/);
});

test("Errores asíncronos de parcela usan el token de la consulta vigente",()=>{
  const js=read("assets/oaf-parcelas-ux39.js");
  assert.match(js,/if\(seq===tokens\[k\]\.model\)out\.textContent="Sin resultado verificable/);
  assert.match(js,/if\(seq===tokens\[k\]\.agro\)out\.textContent="Contexto climático no verificable/);
});

test("Los archivos científicos base mantienen estructura válida y advertencias sobre RF",()=>{
  const sanidad=JSON.parse(read("datos/sanidad_agroexportadora_2026.json"));
  const ids=new Set(sanidad.cultivos.map(x=>x.id));
  assert.equal(sanidad.n_cultivos,sanidad.cultivos.length);
  assert.equal(sanidad.total_organismos,sanidad.organismos.length);
  assert.ok(sanidad.organismos.every(o=>ids.has(o.crop_id)));
  const rf=JSON.parse(read("datos/rf_experimental_ux15.json"));
  assert.equal(rf.operativo_certificado,false);
  assert.match(read("assets/oaf-ux15-rf-salidas.js"),/RF no se muestra porque mejora/);
  // Si la descarga ERA5 falla o no hay skill, el archivo debe declarar indisponibilidad
  // y no publicar pronósticos incompletos como si fueran una salida operativa.
  if(rf.estado==="no_disponible"){
    assert.equal(rf.operativo_certificado,false);
    assert.equal(rf.alertas_automaticas,false);
    assert.match(rf.error||"",/ERA5|archive-api|timeout|timed out/i);
    assert.equal(rf.pronostico_diario_rf_experimental,undefined);
  }else{
    assert.ok(rf.pronostico_diario_rf_experimental&&typeof rf.pronostico_diario_rf_experimental==="object");
    for(const [city,forecast] of Object.entries(rf.pronostico_diario_rf_experimental)){
      assert.equal(forecast.length,rf.horizonte_semanal,city);
      assert.ok(forecast.every(x=>typeof x.fecha==="string"));
    }
  }
});




test("UX54: portada concisa, histórico ampliado, estaciones, relieve y consulta de parcela",()=>{
  const home=read("index.html"),agro=read("assets/oaf-agro-charts-2026.js");
  const structure=read("assets/oaf-ux9-estructura.js");
  const style=read("assets/oaf-agroexportacion-2026.css");
  assert.match(home,/Ciencia de datos — Observatorio Agroclimático y Fitosanitario/);
  assert.doesNotMatch(home,/id="oaf-trust-legend"|Metodología, fuentes y trazabilidad →/);
  assert.match(structure,/archive\("oaf-agro-home-map"\)/);
  assert.match(structure,/archive\("oaf-agro-home-existing-forecast"\)/);
  assert.match(home,/Monitoreo Agroclimático/);
  assert.match(home,/1996–2025/);
  assert.match(agro,/oaf-regional-map-legend/);
  assert.match(agro,/datos\/humedad_8z\/humedad_vpd_mensual_8z\.csv/);
  assert.match(agro,/humedad_relativa_pct/);
  assert.match(agro,/radiacion_mj_m2/);
  assert.match(style,/oaf-agro-history-tile/);
  assert.match(style,/min-height:410px/);
  const exportUI=read("assets/oaf-agroexportacion-2026.js");
  assert.match(exportUI,/id="oaf-stations-map"/);
  assert.match(exportUI,/id="oaf-stations-list"/);
  assert.match(read("assets/oaf-territorio-compartido.js"),/clima:\(\)=>/);
  assert.match(read("assets/oaf-area-ux38.js"),/function climate\(point\)/);
  assert.match(read("assets/oaf-ux9-predicciones.js"),/oaf-ux9-final-lluvia/);
});

test("UX66: módulo C fitosanitario enlazado, con motor independiente y sin modelos genéricos",()=>{
  const html=read("index.html"),sw=read("sw.js"),js=read("assets/oaf-ux35c-fitosanitario.js");
  assert.match(html,/oaf-ux35c-fitosanitario\.js\?v=20261106-ux69/);
  assert.match(html,/oaf-ux35c-fitosanitario\.css\?v=20261106-ux68/);
  assert.match(sw,/oaf-pwa-shell-2026-11-06-ux69/);
  assert.match(sw,/\.\/assets\/oaf-ux35c-fitosanitario\.js/);
  assert.match(sw,/\.\/assets\/oaf-ux35c-fitosanitario\.css/);
  assert.match(js,/Botrytis cinerea/);
  assert.match(js,/No hay todavía un modelo específico documentado/);
  assert.match(js,/ux35cPointPick/);
  assert.match(js,/oaf-ux35c-province/);
  assert.doesNotMatch(js,/probabilidad de infección calibrada|riskScore\s*=/i);
  const window={};
  const document={readyState:"loading",addEventListener(){}};
  runInNewContext(js,{window,document,console,Intl,Date,URLSearchParams,Map,Set,Number,Array,Error,Math},{filename:"oaf-ux35c-fitosanitario.js"});
  const core=window.OAFPhytosanitaryCore;
  assert.equal(typeof core.evaluateForecast,"function");
  const start="2026-11-06",time=[],vars={
    temperature_2m:[],relative_humidity_2m:[],precipitation:[],
    shortwave_radiation:[],vapour_pressure_deficit:[],wind_speed_10m:[]
  };
  for(let d=0;d<9;d++){
    const date=new Date(start+"T12:00:00Z");date.setUTCDate(date.getUTCDate()+d);
    const day=date.toISOString().slice(0,10);
    for(let h=0;h<24;h++){
      time.push(day+"T"+String(h).padStart(2,"0")+":00");
      vars.temperature_2m.push(22);vars.relative_humidity_2m.push(d===2&&h>=2&&h<10?95:70);
      vars.precipitation.push(0);vars.shortwave_radiation.push(150);
      vars.vapour_pressure_deficit.push(.5);vars.wind_speed_10m.push(10);
    }
  }
  const result=core.evaluateForecast({time,...vars});
  assert.equal(result.daily.length,7);
  assert.equal(result.episodes,1);
  assert.equal(result.longest,8);
  const missing={time:time.slice(),...Object.fromEntries(Object.entries(vars).map(([k,v])=>[k,v.slice()]))};
  missing.relative_humidity_2m[50]=null;
  assert.throws(()=>core.evaluateForecast(missing),/Dato ausente/);
});

test("UX69: Ceratitis capitata en mango usa grados-día propios, sin semáforo de infestación",()=>{
 const html=read("index.html"),sw=read("sw.js"),src=read("modelos/ceratitis_mango_termico_ux69.js");
 const main=read("assets/oaf-ux35c-fitosanitario.js");
 const registry=JSON.parse(read("datos/fitosanitario_modelos_ux69.json"));
 assert.match(html,/ceratitis_mango_termico_ux69\.js\?v=20261106-ux69/);
 assert.ok(html.indexOf("modelos/ceratitis_mango_termico_ux69.js")<html.indexOf("assets/oaf-ux35c-fitosanitario.js"),
   "El núcleo térmico debe cargarse antes del módulo C");
 assert.match(sw,/\.\/modelos\/ceratitis_mango_termico_ux69\.js/);
 assert.equal(registry.crops.length,7);
 assert.equal(registry.models.length,2);
 assert.ok(registry.models.every(m=>m.calibration.status.includes("sin_")&&m.sources.length));
 assert.ok(registry.pending.some(m=>m.crop_id==="cafe"&&m.taxon==="Hemileia vastatrix"));
 assert.match(main,/id:"ceratitis"/);
 assert.match(main,/hourlyVariables:isThermal\?\["temperature_2m"\]:VARS/);
 assert.match(main,/renderThermalOutput/);
 assert.match(main,/Información insuficiente para clasificar el riesgo/);
 const context={window:{},Date,Map,Number,Array,Math};
 runInNewContext(src,context,{filename:"modelos/ceratitis_mango_termico_ux69.js"});
 const core=context.window.OAFCeratitisThermal;
 assert.equal(core.MODEL.baseC,9.1);
 assert.equal(core.MODEL.referenceDD,341);
 assert.equal(core.MODEL.calibratedInLambayeque,false);
 const time=[],temperature_2m=[];
 for(let d=0;d<9;d++){
  const dt=new Date("2026-11-06T12:00:00Z");dt.setUTCDate(dt.getUTCDate()+d);
  const day=dt.toISOString().slice(0,10);
  for(let hour=0;hour<24;hour++){
   time.push(day+"T"+String(hour).padStart(2,"0")+":00");
   temperature_2m.push(25);
  }
 }
 const week=core.evaluate({time,temperature_2m},{mode:"forecast",today:"2026-11-06"});
 assert.equal(week.indicator,"thermal");
 assert.equal(week.days,7);
 assert.ok(Math.abs(week.accumulatedDD-111.3)<1e-8);
 assert.ok(week.daily.every(d=>Math.abs(d.gdd-15.9)<1e-8));
 assert.equal(week.risk,undefined,"No se debe fabricar riesgo de infestación");
 const nowMs=Date.parse("2026-11-07T23:30:00-05:00");
 const current=core.evaluate({time,temperature_2m},{mode:"current",nowMs});
 assert.equal(current.days,1);
 assert.ok(Math.abs(current.accumulatedDD-15.9)<1e-8);
 assert.equal(current.indicator,"thermal");

 const historical=core.evaluate({time,temperature_2m},{mode:"history",today:"2026-11-20",start:"2026-11-07",end:"2026-11-09"});
 assert.equal(historical.days,3);
 assert.ok(Math.abs(historical.accumulatedDD-47.7)<1e-8);
 const nullSeries=temperature_2m.slice();nullSeries[35]=null;
 assert.throws(()=>core.evaluate({time,temperature_2m:nullSeries},{mode:"forecast",today:"2026-11-06"}),/Temperatura faltante/);
 const hotSeries=temperature_2m.slice();for(let h=24;h<48;h++)hotSeries[h]=35;
 assert.throws(()=>core.evaluate({time,temperature_2m:hotSeries},{mode:"forecast",today:"2026-11-06"}),/fuera del intervalo experimental/);
 const incomplete={time:time.slice(1),temperature_2m:temperature_2m.slice(1)};
 assert.throws(()=>core.evaluate(incomplete,{mode:"history",today:"2026-11-20",start:"2026-11-06",end:"2026-11-08"}),/Faltan horas/);
});
