/* OAF UX45 · inventario de integridad de seis áreas, PWA y fuentes. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=path.resolve(__dirname,".."),read=p=>fs.readFileSync(path.join(root,p),"utf8");
const html=read("index.html"),sw=read("sw.js"),manifest=JSON.parse(read("manifest.webmanifest"));
const expected=["inicio","clima","autor","cultivos","nino","verificaciones"];
const pages=[...html.matchAll(/<section\s+data-page="([^"]+)"/g)].map(m=>m[1]);
assert.deepEqual(new Set(pages),new Set(expected),"La navegación perdió una de las seis áreas");
assert.equal(pages.length,6,"Secciones duplicadas o superpuestas");
const refs=[...html.matchAll(/<(?:script|link)\b[^>]*\b(?:src|href)="([^"]+)"/g)].map(m=>m[1])
 .filter(x=>!x.startsWith("#")&&!/^https?:|^data:|^mailto:/.test(x))
 .map(x=>decodeURIComponent(x.split(/[?#]/)[0]));
const missing=refs.filter(ref=>!fs.existsSync(path.join(root,ref)));
assert.deepEqual([...new Set(missing)],[],"Recursos CSS/JS referenciados que no existen");
const core=[...sw.matchAll(/"\.\/([^"]+)"/g)].map(m=>m[1]).filter(x=>x.length>0&&!x.endsWith("/"));
const missingCore=core.filter(ref=>!fs.existsSync(path.join(root,ref)));
assert.deepEqual([...new Set(missingCore)],[],"Recursos PWA precache inexistentes");
assert.equal(manifest.display,"standalone");
for(const icon of manifest.icons){
 assert(fs.existsSync(path.join(root,icon.src)),"Ícono no disponible "+icon.src);
}
assert(sw.includes("Network-first")&&sw.includes('isScientificData(url)'),"PWA no distingue avisos y datos de caché");
assert(sw.includes("oaf-pwa-shell-2026-10-27-ux45"));
assert(!html.includes("oaf-ux15-contador.js")&&!html.includes('id="oaf-ux15-counter"'),"El contador de visitas permanece");
const rf=JSON.parse(read("datos/rf_experimental_ux15.json"));
assert.equal(rf.operativo_certificado,false,"RF no debe marcarse operativo sin validación");
assert.equal(rf.alertas_automaticas,false,"No activar alertas experimentales");
assert(rf.metrica_diaria?.backtest_semanal_recursivo?.por_horizonte?.length===7,"Faltan siete horizontes RF auditados");
assert(Object.keys(rf.pronostico_diario_rf_experimental||{}).length>=4,"Pronósticos RF por cuatro localidades ausentes");
const enfen=JSON.parse(read("datos/estado_enso_verificado_ux9_2026.json"));
assert(enfen.enfen?.fuente?.startsWith("https://"),"Falta procedencia de ENFEN");
assert(/^\d{4}-\d\d-\d\d$/.test(enfen.enfen?.fecha_emision||""),"Fecha de emisión ENFEN inválida");
assert(html.includes("oaf-ux15-rf-salidas.js?v=20261027-ux45"));
const seasonal=read("assets/oaf-ux15-rf-salidas.js");
assert(seasonal.includes('hourly:"precipitation,temperature_2m"')&&!seasonal.includes('daily:"precipitation_sum,temperature_2m_mean"'),
 "El pronóstico estacional usa variable no permitida por Open-Meteo");
const crop=JSON.parse(read("datos/sanidad_agroexportadora_2026.json"));
assert(typeof crop==="object"&&Object.keys(crop).length>0,"Catálogo fitosanitario vacío");
const output={fecha_auditoria:new Date().toISOString(),paginas:pages,
 enlaces_internos_comprobados:refs.length,recursos_pwa_comprobados:core.length,
 iconos_pwa:manifest.icons.length,localidades_rf:Object.keys(rf.pronostico_diario_rf_experimental||{}).length,
 ultima_emision_rf:rf.fecha_generacion_utc,ultima_emision_enfen:enfen.enfen.fecha_emision,
 resultado:"PASA_CONTROL_ESTRUCTURAL; no equivale a disponibilidad en tiempo real de fuentes externas"};
fs.mkdirSync(path.join(root,"artifacts"),{recursive:true});
fs.writeFileSync(path.join(root,"artifacts","auditoria_ux45_estructura.json"),JSON.stringify(output,null,2)+"\n");
console.log(JSON.stringify(output,null,2));
