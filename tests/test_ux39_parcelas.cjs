/* UX39 – pruebas de regresión de parcela y trazabilidad sin servicios externos. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const root=path.resolve(__dirname,".."),read=x=>fs.readFileSync(path.join(root,x),"utf8");
const index=read("index.html"),sw=read("sw.js"),css=read("assets/oaf-parcelas-ux39.css");
const core=read("assets/oaf-territorio-compartido.js"),src=read("assets/oaf-parcelas-ux39.js"),hist=read("assets/oaf-area-ux38.js");
for(const js of [src,core,sw,hist])new Function(js);
assert.match(index,/oaf-parcelas-ux39\.js\?v=/,"Script no activado en la web");
assert(index.includes('oaf-parcelas-ux39.css?v=20261027-ux39'),"CSS no activado en la web");
assert(index.includes('oaf-visores-ux40.css?v=20261027-ux40')&&sw.includes('"./assets/oaf-visores-ux40.css"'),"Diseño UX40 no incluido en web y PWA");
assert(sw.includes('"./assets/oaf-parcelas-ux39.js"')&&sw.includes('"./assets/oaf-parcelas-ux39.css"'),"PWA no incluye módulo de parcelas");
assert(core.includes('territorio:()=>$("oaf-ux29-territory")?.querySelector(".oaf-ux29-maphead")'),"Territorio no integrado dentro del visor");
assert(core.includes('escenarios:()=>$("oaf-ux29-scenario")?.querySelector(".oaf-ux29-maphead")'),"Escenarios no integrados dentro del visor");
assert(core.includes('getActivePoint:k=>active[k]'),"Pérdida de independencia de puntos");
assert(core.includes('setPoint:(k,point)=>'),"API pública para centrar parcelas no disponible");
assert(src.includes("data-action=\"export\""),"No permite exportar GeoJSON");
assert(css.includes("@media(max-width:700px)"),"Falta adaptación de pantalla táctil");
const ux40=read("assets/oaf-visores-ux40.css");
assert(ux40.includes("oaf-map-expanded")&&ux40.includes("@media(max-width:790px)"),"No se ajustaron visores a escritorio y móvil");
assert(src.includes("content.after(wrapper)")&&src.includes("wrapper.after(pointDetails)"),"El mapa debe preceder a parcela y diagnóstico");
assert(src.includes("oaf-parcel-fold")&&!src.includes('<details open><summary><strong>Delimitación'),"La delimitación debe iniciar plegada");
assert(core.includes("dataFor(k)")&&core.includes("oaf-area-point-details-"),"Los resultados de punto deben conservarse debajo del mapa");
const w={OAFTerritory:{validatePoint:(lat,lon)=>{
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||lat< -7.3||lat> -5.1||lon< -80.8||lon> -79)throw Error("fuera de Lambayeque");
}}};
const d={readyState:"loading",addEventListener(){}};
vm.runInNewContext(src,{window:w,document:d,setTimeout,clearTimeout,URLSearchParams,Date,console,sessionStorage:{setItem(){},getItem(){return null}}},{timeout:3000});
const api=w.OAFParcelas;assert(api,"No se instaló el API de polígonos");
const outer=[[-79.700,-6.200],[-79.699,-6.200],[-79.699,-6.199],[-79.700,-6.199],[-79.700,-6.200]];
const hole=[[-79.6999,-6.1999],[-79.6998,-6.1999],[-79.6998,-6.1998],[-79.6999,-6.1998],[-79.6999,-6.1999]];
const polygon=api.parsePolygons({type:"Polygon",coordinates:[outer]});
assert(api.contains(polygon,-79.6995,-6.1995),"El punto interno debe pertenecer al polígono");
assert(!api.contains(polygon,-79.800,-6.200),"El punto externo no debe intersectar el polígono");
const area=api.surface(polygon);assert(area>1.15&&area<1.25,"Área geográfica aproximada incoherente: "+area);
const holes=api.parsePolygons({type:"Polygon",coordinates:[outer,hole]});
assert(!api.contains(holes,-79.69985,-6.19985),"Los huecos no deben contar como superficie de parcela");
assert(api.surface(holes)<area,"El hueco no descuenta superficie");
const two=api.parsePolygons({type:"MultiPolygon",coordinates:[[outer],[[[-79.702,-6.2],[-79.701,-6.2],[-79.701,-6.199],[-79.702,-6.199],[-79.702,-6.2]]]]});
assert(api.surface(two)>area*1.9,"MultiPolygon no contabiliza los dos polígonos");
assert.throws(()=>api.parsePolygons({type:"Polygon",coordinates:[outer.map(x=>[x[0]+5,x[1]])]}),/fuera/,"No rechazó coordenadas fuera de región");
assert.throws(()=>api.parsePolygons({type:"Point",coordinates:[-79.7,-6.2]}),/polígono/,"No rechazó geometría puntual");
assert(src.includes("exceededTransferLimit"),"La cuantificación debe detectar truncamiento de capa");
assert(src.includes("data.features.length&&data.features.some(f=>!f.geometry"),"No se deben convertir entidades sin geometría en cero hectáreas");
assert(src.includes("Una consulta vacía, parcial o bloqueada por CORS no demuestra ausencia de peligro"),"Falta advertencia ante consulta vacía o bloqueada");
assert(src.includes("no una intersección topológica exacta")&&src.includes("porcentajes describen la distribución de puntos muestreados"),"Advertencia de incertidumbre científica ausente");
assert(src.includes("2021;y<=2025"),"Falta backtesting fuera del entrenamiento");
const esri=api.esriPolygon(polygon);
assert.equal(esri.spatialReference.wkid,4326,"La consulta vectorial debe enviar WGS84");
assert.equal(esri.rings.length,1,"La geometría Esri debe conservar el anillo exterior");
const signed=ring=>ring.slice(0,-1).reduce((sum,p,i)=>{
 const q=ring[(i+1)%(ring.length-1)];return sum+p[0]*q[1]-q[0]*p[1];
},0)/2;
assert(signed(esri.rings[0])<0,"El anillo exterior Esri debe estar orientado en sentido horario");
const vectorParams=api.vectorQueryParams(polygon);
assert.equal(vectorParams.get("geometryType"),"esriGeometryPolygon","INGEMMET debe recibir la geometría real, no una envolvente");
assert.equal(vectorParams.get("spatialRel"),"esriSpatialRelIntersects");
const samples=api.samplePoints(polygon,5);
assert(samples.length>0&&samples.every(p=>api.contains(polygon,p.lon,p.lat)),"El muestreo debe excluir puntos externos y huecos");
const identify=api.rasterIdentifyParams(5090024,samples,api.limits(polygon));
assert.equal(identify.get("geometryType"),"esriGeometryMultipoint","CENEPRED ráster debe consultarse con Identify multipunto");
assert.equal(identify.get("layers"),"all:5090024");
const classes=api.parseRasterClasses([
 {attributes:{n_peligro:"Muy Alto"}},{attributes:{n_peligro:"Alto"}},
 {attributes:{n_peligro:"Medio"}},{attributes:{n_peligro:"Bajo"}}
],4);
assert.equal(classes.identified,4);assert.equal(classes.coverage,1);
assert.deepEqual({...classes.counts},{"Muy alto":1,Alto:1,Medio:1,Bajo:1});
const numericClasses=api.parseRasterClasses([{attributes:{"Pixel Value":3}},{value:2}],2,{unique:{"3":"Alto","2":"Medio"}});
assert.deepEqual({...numericClasses.counts},{Alto:1,Medio:1},"No se traducen valores numéricos de raster según la leyenda");
const rawCodes=api.parseRasterClasses([{attributes:{"Pixel Value":7}}],1);
assert.equal(rawCodes.counts["Código 7"],1,"Un valor raster numérico debe conservarse como código y no perderse como sin clasificar");
const noData=api.parseRasterClasses([],9);
assert.equal(noData.identified,0);assert.equal(noData.coverage,0);
const normalized=api.normalizeArcGISFeature({attributes:{LEYENDA:"Alto"},geometry:{rings:esri.rings,spatialReference:{wkid:4326}}});
assert.equal(normalized.geometry.type,"Polygon");
assert(api.contains([normalized.geometry.coordinates],-79.6995,-6.1995),"Conversión de geometría Esri a GeoJSON incorrecta");

const start=src.indexOf("function arModel("),end=src.indexOf("async function model(",start);
const arModel=new Function(src.slice(start,end)+";return arModel;")();
const rows=new Map();
for(let y=2001;y<=2025;y++)for(let m=1;m<=12;m++){
 const key=y+"-"+String(m).padStart(2,"0");rows.set(key,{rain:m*2,t:20+m/10});
}
const predictor=arModel(rows,"rain");
assert.equal(predictor.scores.n,60,"Validación de 60 meses esperada");
assert(Math.abs(predictor.scores.mae)<.001,"MAE incorrecto en climatología perfecta");
assert.equal(predictor.projections.get("2027-04"),8,"Modelo de referencia mensual incorrecto");
console.log("UX51 OK · GeoJSON/MultiPolygon/huecos/ha/consulta vectorial exacta/Identify ráster/zonas/AR-12/PWA");
