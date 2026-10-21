/* Integridad responsiva sin paquetes: Node 18+. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const read = p => fs.readFileSync(path.join(root, p), "utf8");
const html = read("index.html");
const css = read("assets/oaf-responsive-celulares-ux19.css");
const js = read("assets/oaf-responsive-celulares-ux19.js");
const map = read("ecorregiones-clima-10k.html");
const routes = ["inicio", "clima", "nino", "cultivos", "autor", "verificaciones"];
assert.match(html, /<meta\s+name="viewport"\s+content="width=device-width,initial-scale=1(?:,viewport-fit=cover)?"/);
for (const route of routes) {
 assert.ok(html.includes('data-page="' + route + '"'),"Falta pestaña " + route);
 assert.ok(html.includes('data-tab="' + route + '"'),"Falta navegación a " + route);
}
assert.match(html,/oaf-responsive-celulares-ux19\.css\?v=/);
assert.match(html,/oaf-responsive-celulares-ux19\.js\?v=/);
for (const part of [
 "@media(max-width:900px)", "@media(max-width:700px)", "@media(max-width:395px)",
 "#oaf-mobile-menu", "#oaf-primary-nav.oaf-menu-open", "oaf-mobile-chart-host",
 "oaf-mobile-table-wrap", "oaf-ux12-photo", "oaf-ux14-home-hero",
 "object-fit:contain", "touch-action:manipulation"
]) assert.ok(css.replace(/\s*:\s*/g,":").includes(part), "Falta CSS móvil: " + part);
for (const chart of [
 "oaf-ux14-weekchart", "oaf-ux14-monthchart",
 "oaf-ux9-grafico-lluvia", "oaf-ux9-grafico-temperatura",
 "oaf-ux9-grafico-enso", "oaf-sm-chart", "oaf-bol-chart"
]) assert.ok(js.includes('"' + chart + '"'),"Falta gráfico adaptativo " + chart);
assert.ok(js.includes('document.querySelectorAll("[data-page] table")'));
assert.ok(js.includes('MutationObserver'));
assert.ok(map.includes("map.invalidateSize({pan:false})"),"Mapa Leaflet no reacciona al giro");
assert.ok(map.includes("@media(max-width:760px)"),"Mapa sin ancho móvil");
function balanced(text){
 let s=text.replace(/\/\*[\s\S]*?\*\//g,"").replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g,"");
 let level=0;for(const x of s){if(x==="{")level++;if(x==="}")level--;assert.ok(level>=0,"Llaves CSS desbalanceadas");}
 assert.equal(level,0,"Llaves CSS sin cerrar");
}
balanced(css);
console.log("UX19 OK: 6 pestañas, tamaños 395/700/900, navegación, fotos, 7 gráficas, tablas, mapa, CSS consistente");
