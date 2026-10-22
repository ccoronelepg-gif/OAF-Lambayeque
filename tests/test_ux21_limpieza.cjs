/* OAF UX21: editorial, diseño unificado y cero duplicaciones visibles. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,".."),get=p=>fs.readFileSync(path.join(root,p),"utf8");
const html=get("index.html"),shell=get("assets/oaf-ux-shell-2026.js"),
  main=get("assets/oaf-ux9-estructura.js"),m=get("assets/oaf-ux15-rf-salidas.js"),
  sani=get("assets/oaf-ux11-sanidad.js"),clim=get("assets/oaf-ux9-lectura-clima.js");
const enfen=get("assets/oaf-ux14-reorganizacion.js"),css=get("assets/oaf-ux21-lectura-limpia.css");
const ux21=get("assets/oaf-ux21-editorial.js");
assert.ok(!html.includes('class="oaf-view-switch"'),"Conmutador aún visible");
assert.ok(!html.includes('class="oaf-contextbar"'),"Zona redundante aún visible");
assert.ok(html.includes('id="oaf-home-summary-static"'),"Falta resumen central");
// UX22: el objetivo, las fuentes y la metodología están sintetizados en un único párrafo,
 // sin exigir etiquetas largas redundantes que el usuario pidió eliminar.
const summary=html.match(/<p class="oaf-ux22-sintesis">([^<]*)<\/p>/)?.[1];
assert.ok(summary,"Falta síntesis editorial en Inicio");
assert.ok(summary.includes("productores")&&summary.includes("especialistas"),"Falta propósito divulgativo");
assert.ok(summary.includes("Python")&&summary.includes("SIG"),"Falta metodología propia");
assert.ok(summary.includes("experiment")||summary.includes("en evaluación"),"Falta límite científico RF");
assert.ok(summary.split(/\s+/).length<=70,"Síntesis supera el tamaño solicitado");
for(const t of ["ENFEN","SENAMHI","NOAA","CHIRPS","ERA5","Open-Meteo","CAMS","Random Forest"])assert.ok(summary.includes(t),"Falta fuente o modelo "+t);
assert.ok(!html.includes('class="oaf-source-split"'),"Dos paneles con fuentes duplicadas");
assert.ok(main.includes("archivedHome.append(b2)"),"Bloque histórico no archivado");
assert.ok(!m.includes("oaf-ux16-future-panel"),"Se duplicaron tarjetas mensuales");
assert.ok(m.includes('selector.value="futuro"'),"Mes futuro no preseleccionado");
assert.ok(sani.includes('link("Fuente fitosanitaria ↗",principal)'),"Debe aparecer una fuente única");
assert.ok(!sani.includes("Investigación complementaria ↗"),"Enlaces repetidos no eliminados");
assert.ok(clim.includes('strongTip.textContent="Consejo práctico: "'),"Consejo práctico no resalta");
assert.ok(!clim.includes("Lectura orientativa elaborada por OAF"),"Párrafo de fuentes repetido");
assert.ok(css.includes(".oaf-ux15-explain")&&css.includes("font-style:italic!important"));
assert.ok(!enfen.includes('Ver figura del boletín ENFEN ↗'),"Enlace ENFEN redundante");
assert.ok(enfen.includes('ENFEN · boletín y figura oficial ↗'));
assert.ok(shell.includes('if(!byId("oaf-mobile-menu")'),"El menú móvil dejó de inicializar");
for(const file of ["assets/oaf-ux21-editorial.js","assets/oaf-ux21-lectura-limpia.css"])assert.ok(html.includes(file));
for(const text of [shell,m,sani,clim,enfen,ux21])new Function(text);
console.log("UX21 OK: sin duplicados de Inicio/Sanidad, futuro mensual, objetivo, fuentes e interpretaciones.");
