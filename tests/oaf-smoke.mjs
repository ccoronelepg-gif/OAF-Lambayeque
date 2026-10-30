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
  for(const [city,forecast] of Object.entries(rf.pronostico_diario_rf_experimental)){
    assert.equal(forecast.length,rf.horizonte_semanal,city);
    assert.ok(forecast.every(x=>typeof x.fecha==="string"));
  }
});
