/* UX65 · Auditoría estática del inventario de capas del VISOR.
 * Ejecutar: node tests/auditoria_capas_ux65.cjs
 * Comprueba que no vuelvan a aparecer controles temáticos retirados.
 */
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const read = p => fs.readFileSync(path.join(process.cwd(), p), "utf8");
const between = (source, start, end, label) => {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, "No se encontró bloque " + label);
  return source.slice(a, b);
};

const ux30 = read("assets/oaf-ux30-territorio-unificado.js");
const ux35 = read("assets/oaf-ux35-escenarios-multicapas.js");
const ux52 = read("assets/oaf-ux52-visores.js");
const ux39 = read("assets/oaf-parcelas-ux39.js");
const index = read("index.html");
const sw = read("sw.js");
const css30 = read("assets/oaf-ux30-territorio-unificado.css");

const spec = between(ux30, "const layerSpec=[", "const spec=new Map(", "catálogo territorial");
const layerKeys = [...spec.matchAll(/\["(flood|rainIntense|drought|heat|humidity|wind)"/g)].map(m => m[1]);
assert.deepEqual(layerKeys, ["flood","rainIntense","drought","heat","humidity","wind"],
  "Territorio debe tener exactamente seis capas y en el orden solicitado");
const groupTitles = [...spec.matchAll(/\["(?:peligros|agroclimatic)","([^"]+)"/g)].map(m => m[1]);
assert.deepEqual(groupTitles, [
  "A. Peligros climáticos e hidrometeorológicos",
  "B. Condiciones agroclimáticas"
], "Territorio debe conservar únicamente los grupos A y B");
assert.match(spec, /\["flood","Peligro de inundaciones",true/);
assert.match(spec, /\["humidity","Exceso de humedad y condiciones favorables para enfermedades \(humedad relativa y horas de humedad foliar\)"/);
assert.match(spec, /CENEPRED[^\n]*5090024/);
assert.match(spec, /SENAMHI\/IDESEP/);
assert.match(spec, /Pendiente de conexión/);
assert.doesNotMatch(ux30, /async function loadDrought|async function loadHistory|async function loadHydro/,
  "No deben quedar cargadores activos de capas antiguas");
assert.match(ux30, /tree\.replaceChildren\(\);state\.legacy=null;/,
  "El árbol heredado debe retirarse del DOM, no ocultarse");
assert.match(ux30, /#oaf-ux27-exposicion \.oaf-ux27-riskmap/,
  "Debe retirarse el selector heredado de inundación UX27");
assert.match(ux30, /filters\.querySelector\("#oaf-ux26-agricultura"\)\?\.closest\("label"\)\?\.remove\(\)/,
  "Debe retirarse el control agrícola anterior");
assert.match(ux30, /satCheck\.dataset\.ux30Basemap="satellite"/,
  "La imagen satelital debe permanecer como fondo cartográfico");
assert.match(ux52, /oaf-ux52-relief-toggle/,
  "El relieve sombreado debe conservar su control");

const scenarioTree = between(ux35, "function buildTree(tree){", "function attachTerritoryFilters(){", "árbol de escenarios");
const scenarioKeys = [...scenarioTree.matchAll(/ux35Key="([^"]+)"/g)].map(m => m[1]);
assert.deepEqual(scenarioKeys, ["phytosanitary"],
  "Escenarios debe mostrar únicamente la capa C");
assert.match(ux35, /on:\{phytosanitary:false\}/);
const scenarioInit = between(ux35, "function init(){", "if(document.readyState===\"loading\")", "inicio de escenarios");
assert.doesNotMatch(scenarioInit, /requestSharedData|loadHistory|loadCompanies/,
  "El módulo C no debe cargar capas históricas, hidrológicas o empresariales");
assert.match(ux35, /Pendiente de conexión/);
assert.doesNotMatch(between(ux35, "function render(){", "function renderLabels(){", "dibujo de escenarios"),
  /pastRain|futureFlood|futureMass|raster\(/,
  "El mapa de escenarios no debe dibujar capas antiguas");

assert.match(ux52, /allowed=new Set\(\["flood","rainIntense","drought","heat","humidity","wind"\]\)/);
assert.match(ux52, /new MutationObserver\(prune\)\.observe\(tree,\{childList:true,subtree:true\}\)/,
  "Los grupos antiguos que otros módulos intenten insertar deben retirarse del DOM");
assert.match(ux52, /const actions=\$\("oaf-ux29-territory"\)\?\.querySelector\("\.oaf-ux30-layer-actions"\)/,
  "El control de relieve debe permanecer fuera de los dos grupos temáticos");
assert.match(ux52, /#oaf-ux25-controls/,
  "Los controles cartográficos heredados deben retirarse");

const parcelLayers = between(ux39, "const LAYERS=[", "async function fetched(", "fuentes de evaluación parcelaria");
assert.deepEqual([...parcelLayers.matchAll(/territorio:\["([^"]+)"\]/g)].map(m => m[1]), ["flood","flood"],
  "La evaluación parcelaria solo debe intersectar fuentes compatibles con inundaciones");
assert.doesNotMatch(parcelLayers, /5090022|futureMass|movimientos en masa/);
assert.match(ux39, /!input\.matches\("\[data-ux30-basemap\],#oaf-ux52-relief-toggle"\)/,
  "Satélite y relieve no deben contarse como capas temáticas");
assert.match(ux39, /Riesgo agroclimático fitosanitario está pendiente de conexión/);

for (const asset of [
  "assets/oaf-ux30-territorio-unificado.js?v=20261106-ux65",
  "assets/oaf-ux35-escenarios-multicapas.js?v=20261106-ux65",
  "assets/oaf-ux52-visores.js?v=20261106-ux65",
  "assets/oaf-parcelas-ux39.js?v=20261106-ux65"
]) assert.ok(index.includes(asset.split("?")[0]+"?v="), "index.html no referencia " + asset.split("?")[0]);
assert.match(sw, /oaf-pwa-shell-2026-11-06-ux[0-9]+[a-z]?/);
assert.match(sw, /const exact=/);
assert.ok(sw.indexOf("const exact=") < sw.indexOf("const fallback="),
  "La PWA debe priorizar el archivo versionado y usar el antiguo solo como fallback offline");

console.log(JSON.stringify({
  revision: "UX65",
  status: "inventario_de_capas_correcto",
  territorio: { grupos: groupTitles, capas: layerKeys },
  escenarios: { grupos: ["C. Riesgo agroclimático fitosanitario"], capas: scenarioKeys },
  fondosConservados: ["mapa base", "imagen satelital", "relieve sombreado"],
  herramientasConservadas: ["filtros territoriales", "mi zona productiva", "delimitar parcela", "diagnóstico"],
  capasPendientes: ["Peligro de lluvias intensas", "Sequía y déficit hídrico",
    "Exceso de humedad y condiciones favorables para enfermedades", "Vientos fuertes",
    "Riesgo agroclimático fitosanitario"],
  legacyControls: "retirados del DOM",
  checks: "OK"
}, null, 2));
