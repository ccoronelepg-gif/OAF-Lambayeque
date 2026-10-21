(function buildOAF(){
"use strict";
const $=id=>document.getElementById(id);
function node(tag,cls,id,html){const e=document.createElement(tag);if(cls)e.className=cls;if(id)e.id=id;if(html)e.innerHTML=html;return e}
const heading=(n,topic,name,desc)=>`<header class="oaf-agro-block-head"><span class="oaf-agro-kicker">${n} · ${topic}</span><h2>${name}</h2><p>${desc}</p></header>`;
const block=(id,h,inner)=>node("section","oaf-agro-block",id,h+inner);
const placeSel=id=>`<select id="${id}"><option>Chiclayo</option><option>Jayanca</option><option>Motupe</option><option>Olmos</option></select>`;
const variSel=id=>`<select id="${id}"><option value="precipitacion_mm">Precipitación (mm)</option><option value="temperatura_c">Temperatura (°C)</option></select>`;
const chart=(id)=>`<figure class="oaf-agro-chart" id="${id}"><p class="oaf-agro-progress">Cargando información documentada…</p></figure>`;
const note="Los resultados de elaboración propia se contrastan con modelos de referencia, fechas de prueba y fuentes abiertas. No se generan pronósticos multianuales numéricos sin validación suficiente.";
const ten=[
"OAF-Lambayeque es una plataforma de divulgación científica centrada en los cultivos de agroexportación y el clima regional.",
"Integra datos meteorológicos, oceánicos y territoriales de SENAMHI, ENFEN, NOAA, Copernicus, CHIRPS, Open-Meteo y otros proveedores documentados.",
"La información se revisa cuidadosamente según su cobertura, resolución, periodo, procedencia y limitaciones.",
"El responsable realiza análisis originales mediante estadística, ciencia de datos, Python, programación y sistemas de información geográfica.",
"Se investigan algoritmos de inteligencia artificial como Random Forest y se comparan con redes neuronales y referencias climatológicas.",
"Los estudios examinan lluvia, temperatura, humedad, radiación y viento en costa, valles, piedemonte y montaña de Lambayeque.",
"También se investigan las señales oceánicas de El Niño, anomalías climáticas y posibles episodios de lluvia regional.",
"El trabajo fitosanitario prioriza mango, vid, arándano, palto, maracuyá y banano, con literatura científica sobre plagas y enfermedades.",
"El propósito es estudiar la predicción de precipitación y de condiciones favorables para enfermedades, verificando su desempeño e incertidumbre.",
"El observatorio publica gráficos, mapas y resultados técnicos de elaboración propia, con metodología y trazabilidad para consulta e investigación."
];
const intro=node("div","oaf-agro-summary",null,`<h2>Ciencia de datos y agricultura de agroexportación en Lambayeque</h2>${ten.map(x=>`<p>${x}</p>`).join("")}`);
const home1=block("oaf-bloque-clima-actual",heading("01","Monitoreo agroclimático","¿Cómo está el clima?","Consulta indicadores y un mapa interactivo por localidad. Cada variable conserva su proveedor, periodo y fecha de actualización."),
`<div id="oaf-agro-home-zone"></div><div id="oaf-agro-home-metrics"></div><div id="oaf-agro-home-map"></div><p class="oaf-agro-interpretation">El mapa muestra altitudes y puntos de muestreo territorial, no mediciones instrumentales en cada parcela. La lectura meteorológica procede de proveedores identificados.</p>`);
const home2=block("oaf-bloque-prediccion-inicio",heading("02","Evolución histórica y predicciones","¿Cómo está cambiando el clima?","Dos dashboards: pronóstico del proveedor para siete días y serie histórica analizada por OAF. Los modelos propios de lluvia se identifican por separado."),
`<div class="oaf-agro-split"><article class="oaf-agro-tile"><span class="oaf-agro-chip external">Pronóstico externo · 7 días</span><h3>Lluvia prevista</h3><div class="oaf-agro-controls"><label for="oaf-h7-place">Localidad</label>${placeSel("oaf-h7-place")}</div>${chart("oaf-h7-chart")}<p class="oaf-agro-caption" id="oaf-h7-status">Fuente y vigencia pendientes de consulta.</p></article>
<article class="oaf-agro-tile"><span class="oaf-agro-chip">Análisis histórico OAF</span><h3>Evolución de lluvia y temperatura</h3><div class="oaf-agro-controls"><label for="oaf-historical-place">Localidad</label>${placeSel("oaf-historical-place")}<label for="oaf-historical-var">Variable</label>${variSel("oaf-historical-var")}</div>${chart("oaf-historical-chart")}<p class="oaf-agro-caption">Archivo retrospectivo ERA5 1996–2025 analizado por OAF; no constituye una proyección multianual.</p></article></div>
<div class="oaf-agro-facts"><div class="oaf-agro-fact"><small>Modelo del autor</small><strong>Random Forest · investigación</strong></div><div class="oaf-agro-fact"><small>Lluvia mensual alta</small><strong>Probabilidad en evaluación</strong></div><div class="oaf-agro-fact"><small>El Niño</small><strong>Señales océano-atmósfera</strong></div></div>
<div id="oaf-home-predictive-brief" class="oaf-agro-interpretation" role="status">Resumen predictivo OAF: consultando evaluación Random Forest y fuentes con fecha verificable…</div>
<p class="oaf-agro-interpretation">${note}</p><div id="oaf-agro-home-existing-forecast"></div><a class="oaf-agro-read-more" href="#autor">Modelos del autor y evaluación →</a>`);
const home3=block("oaf-bloque-cultivos-inicio",heading("03","Sanidad agroexportadora","Cultivos priorizados y situación fitosanitaria","Resumen de seis cultivos. Accede a las fichas de plagas y enfermedades con respaldo científico y enlaces a sus fuentes."),
`<div id="oaf-home-six-crops" class="oaf-agro-crop-grid"></div><p class="oaf-agro-caption">La información documental no confirma incidencia actual de organismos en una parcela.</p><a class="oaf-agro-read-more" href="#oaf-cultivos-catalogo">Abrir biblioteca fitosanitaria por cultivo →</a>`);
const clima1=block("oaf-clima-bloque-historico",heading("01","Clima regional e historia","Mapa interactivo y evolución histórica","Análisis de temperatura y precipitación 1996–2025 con filtros por localidad y franjas de altitud."),
`<div class="oaf-agro-split"><article class="oaf-agro-tile"><h3>Serie histórica</h3><div class="oaf-agro-controls"><label for="oaf-regional-place">Localidad</label>${placeSel("oaf-regional-place")}<label for="oaf-regional-var">Variable</label>${variSel("oaf-regional-var")}</div>${chart("oaf-regional-hist-chart")}<p class="oaf-agro-caption">Gráfico elaborado por el OAF utilizando el archivo meteorológico ERA5; no es una proyección futura.</p></article>
<article class="oaf-agro-tile"><h3>Mapa del relieve regional</h3><div class="oaf-agro-controls"><label for="oaf-regional-map-filter">Piso altitudinal</label><select id="oaf-regional-map-filter"><option value="all">Todos</option><option value="0-500">0–500 m</option><option value="500-1500">500–1500 m</option><option value="1500-3000">1500–3000 m</option><option value="3000-9000">Más de 3000 m</option></select></div><div class="oaf-agro-map-frame" id="oaf-regional-hist-map">Cargando DEM…</div><p class="oaf-agro-caption">Puntos DEM de muestreo, no estaciones meteorológicas.</p></article></div><p class="oaf-agro-interpretation">${note}</p>`);
const clima2=block("oaf-clima-bloque-modelo",heading("02","Análisis predictivo propio","Mapas y modelos de lluvia OAF","Random Forest y otros algoritmos comparados con climatología para comprender las diferencias por sector."),
`<div id="oaf-regional-own-map"></div><div class="oaf-agro-split"><article class="oaf-agro-tile"><h3>Modelo por paisajes agroclimáticos</h3><p>Dashboard interactivo del OAF para explorar sectores, evaluaciones y lluvias.</p><a class="oaf-agro-read-more" href="ecorregiones-clima-10k.html">Explorar cinco paisajes →</a></article><article class="oaf-agro-tile"><h3>Comparación predictiva</h3><p>Errores del modelo y referencia climatológica, ventanas de prueba e incertidumbre.</p><a class="oaf-agro-read-more" href="evaluacion-modelos-atmosfericos-10h.html">Comparar RF / GCN →</a></article></div><p class="oaf-agro-caption">Elaboración OAF con insumos abiertos de CHIRPS, NOAA y otros proveedores. Zonas geográficas experimentales.</p>`);
const clima3=block("oaf-clima-bloque-estaciones",heading("03","Trazabilidad instrumental","Estaciones y pisos altitudinales","Mapa de estaciones documentadas, altitud y cobertura. Las coordenadas históricas incluyen incertidumbre espacial."),
`<div class="oaf-agro-split"><article class="oaf-agro-tile"><div class="oaf-agro-controls"><label for="oaf-stations-floor">Piso altitudinal</label><select id="oaf-stations-floor"><option value="all">Todas</option><option value="0-500">0–500 m</option><option value="500-1500">500–1500 m</option><option value="1500-3000">1500–3000 m</option><option value="3000-9000">Más de 3000 m</option></select></div><div class="oaf-agro-map-frame" id="oaf-stations-map">Leyendo estaciones…</div></article><article class="oaf-agro-tile"><h3>Datos de las estaciones</h3><div id="oaf-stations-list" class="oaf-agro-progress">Cargando fichas…</div><p class="oaf-agro-caption">La localización procede de fichas documentales y puede ser aproximada.</p><a class="oaf-agro-link" href="observaciones-senamhi-10m.html">Consultar observaciones →</a><a class="oaf-agro-link" href="#verificaciones">Ver metadatos →</a></article></div>`);
const autor1=block("oaf-autor-pronosticos",heading("01","Python, estadística y Random Forest","Modelos de predicción y anomalías","Se desarrollan modelos propios de lluvia mensual y señales océano-atmósfera. La habilidad se compara con climatología, errores estadísticos y prueba temporal."),
`<div class="oaf-agro-split"><article class="oaf-agro-tile"><span class="oaf-agro-chip external">Pronóstico meteorológico de proveedor</span><h3>Próximos siete días</h3><p>Estos insumos tienen horizonte diario; el modelo Random Forest del OAF se evalúa principalmente a escala mensual.</p><div class="oaf-agro-controls"><label for="oaf-autor-7place">Localidad</label>${placeSel("oaf-autor-7place")}</div>${chart("oaf-autor-7chart")}<p class="oaf-agro-caption" id="oaf-autor-7status"></p></article><article class="oaf-agro-tile"><span class="oaf-agro-chip">Análisis y modelo propio</span><h3>Random Forest para lluvia mensual</h3><p>Explora resultados auditados y contrastes del algoritmo con la referencia climática.</p><div id="oaf-autor-rf-main"></div><a class="oaf-agro-link" href="random-forest-lluvias.html">Dashboard de Random Forest →</a></article></div>
<div class="oaf-agro-split"><article class="oaf-agro-tile"><h3>El Niño y anomalías climáticas</h3><p>Se investigan Niño 1+2, temperatura del mar, viento y su relación con la lluvia de Lambayeque.</p><div class="oaf-agro-fact" id="oaf-nino-signal">Leyendo índices históricos NOAA…</div><p class="oaf-agro-interpretation">Una anomalía oceánica aislada no predice un evento ni constituye por sí sola un aviso para cultivos.</p><a class="oaf-agro-read-more" href="#nino">Seguimiento océano-atmósfera →</a></article><article class="oaf-agro-tile"><h3>Lluvia mensual anómala</h3><p>Evaluación experimental de probabilidades de lluvia elevada y estabilidad predictiva por sectores.</p><div id="oaf-autor-rf-prob"></div><a class="oaf-agro-read-more" href="evaluacion-sectores-10f.html">Revisar pruebas por sector →</a></article></div>`);
const crops=node("section","oaf-agro-block","oaf-cultivos-catalogo",heading("01","Cultivos de agroexportación","Plagas y enfermedades de seis cultivos","Mango, vid, arándano, palto, maracuyá y banano. Información técnica sustentada en SENASA, INIA y literatura de investigación.")+
`<div class="oaf-agro-crop-browser"><label for="oaf-crop-filter">Cultivo priorizado</label><select id="oaf-crop-filter"><option value="mango">Mango</option><option value="vid">Vid</option><option value="arandano">Arándano</option><option value="palto">Palto</option><option value="maracuya">Maracuyá</option><option value="banano">Banano</option></select><div id="oaf-crop-detail" class="oaf-agro-browser-output">Cargando catálogo científico…</div></div><p class="oaf-agro-caption">La lista documental no confirma presencia actual de plagas o enfermedades en una parcela de Lambayeque.</p>`);
function move(id,to){const x=$(id),d=$(to);if(x&&d)d.append(x)}
function hoist(id,to){const x=$(id);if(!x)return;const e=x.closest(".oaf-home-module");if(e)$(to)?.append(e);}
function relocate(rest,homeShell,keep){for(const element of [...homeShell.children])if(!keep.has(element))rest.append(element);}
function init(){
 const home=$("inicio"),clima=$("clima"),author=$("autor"),crop=$("cultivos"),meta=$("verificaciones");
 if(!home||!clima||!author||!crop||!meta||$("oaf-agro-home"))return;
 const legacy=$("oaf-meta-legacy")||meta;
 const archive=node("div","oaf-agro-archive","oaf-agro-technical-archive",'<h2>Archivo científico y trazabilidad de las secciones reorganizadas</h2><p class="oaf-agro-caption">Módulos, mapas y resultados históricos reubicados sin alterar sus scripts ni sus identificadores.</p>');
 legacy.prepend(archive);
 function bucket(title,id){const details=node("details","oaf-agro-meta-collapsed",id,`<summary>${title}</summary><div></div>`);archive.append(details);return details.lastElementChild;}
 const ah=bucket("Archivo complementario de Inicio","oaf-agro-archive-home");
 const ac=bucket("Estaciones, mapas, modelos y auditorías complementarias del clima","oaf-agro-archive-clima");
 const aa=bucket("Experimentos, modelos y comparaciones técnicas anteriores","oaf-agro-archive-autor");
 const shell=home.querySelector(".oaf-home-shell"),guide=shell?.querySelector(".oaf-guide-link");
 if(!shell||!guide)return;
 guide.after(intro);
 const hs=node("div","oaf-agro-shell","oaf-agro-home");hs.append(home1,home2,home3);intro.after(hs);
 move("oaf-zone-primary","oaf-agro-home-zone");hoist("oaf-main-indicators","oaf-agro-home-metrics");hoist("oaf-regional-map-heading","oaf-agro-home-map");move("oaf-forecast-home","oaf-agro-home-existing-forecast");
 relocate(ah,shell,new Set([shell.querySelector(".hero"),guide,intro,hs]));
 const cs=node("div","oaf-agro-shell","oaf-agro-clima");cs.append(clima1,clima2,clima3);
 const viewhead=clima.querySelector(".viewhead");(viewhead||clima.firstElementChild)?.after(cs);
 move("oaf-9k-visor","oaf-regional-own-map");move("oaf-ecopaisajes-10k","oaf-regional-own-map");const ownMap=$("oaf-9k-visor");if(ownMap?.tagName==="DETAILS")ownMap.open=true;
 for(const e of [...clima.children])if(e!==viewhead&&e!==cs)ac.append(e);
 const ps=node("div","oaf-agro-shell","oaf-agro-autor");ps.append(autor1);author.prepend(ps);
 move("oaf-rf-unico-lluvias-10i","oaf-autor-rf-main");move("oaf-modelo-lluvia-10e","oaf-autor-rf-prob");
 for(const e of [...author.children])if(e!==ps)aa.append(e);
 const ch=crop.querySelector(".viewhead");if(ch)ch.after(crops);else crop.prepend(crops);
 document.documentElement.classList.add("oaf-agro-ready");
 document.dispatchEvent(new CustomEvent("oaf:agro-ready"));
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
