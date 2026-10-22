/* UX27 · exposición agrícola ante inundaciones: evidencia cuantitativa publicada.
 * No se inventan hectáreas por superposición de imágenes ni se extrapolan
 * los 9 distritos estudiados al conjunto de la región Lambayeque.
 * Fuentes: CENEPRED Plan Multisectorial 2025–2027, cuadro de riesgo MUY ALTO.
 */
(function(){
"use strict";
const C={districts:9,agriTotal:1380,agriSuscept:1234,population:231122,housesSuscept:50299,roadsSuscept:374,
  doc:"https://sigrid.cenepred.gob.pe/sigridv3/documento/17791",
  report:"https://sigrid.cenepred.gob.pe/sigridv3/storage/reporte_semanal/REPORTE_SEMANAL_202601_2.pdf"};
const format=n=>new Intl.NumberFormat("es-PE",{maximumFractionDigits:1}).format(n);
const byId=id=>document.getElementById(id);
const percentage=100*C.agriSuscept/C.agriTotal;
const panelHTML=[
 '<header class="oaf-ux27-head">',
 '<span class="oaf-ux24-tag">UX27 · Indicadores agrícolas · Fuente CENEPRED 2025</span>',
 '<h2>Exposición agrícola frente a inundaciones</h2>',
 '<p>Resultados documentados del escenario de <strong>riesgo muy alto de inundación</strong> del Plan Multisectorial 2025–2027. El cuadro oficial considera <strong>nueve distritos de Lambayeque</strong>. Sus valores no son una estimación de toda la región ni de un episodio futuro.</p>',
 '</header>',
 '<div class="oaf-ux27-metrics">',
 '<article><small>Distritos en riesgo muy alto</small><strong id="oaf-ux27-districts">9</strong><span>Del escenario CENEPRED</span></article>',
 '<article><small>Superficie agrícola considerada</small><strong>1 380 ha</strong><span>En los nueve distritos</span></article>',
 '<article><small>Superficie de mayor susceptibilidad</small><strong>1 234 ha</strong><span>Parte de la superficie anterior</span></article>',
 '<article><small>Proporción dentro del ámbito analizado</small><strong id="oaf-ux27-share">89,4 %</strong><span>No equivale al porcentaje regional</span></article>',
 '</div>',
 '<div class="oaf-ux27-analysis"><div class="oaf-ux27-analysis-top">',
 '<strong>Distribución dentro de la superficie agrícola considerada</strong>',
 '<span>1 234 ha de 1 380 ha</span></div>',
 '<div class="oaf-ux27-progress" role="img" aria-label="1 234 hectáreas de mayor susceptibilidad de 1 380 hectáreas agrícolas consideradas: 89,4 por ciento"><div id="oaf-ux27-fill"></div></div>',
 '<div class="oaf-ux27-analysis-foot"><span><i class="oaf-ux27-dot-high"></i>Mayor susceptibilidad: <b>1 234 ha</b></span><span>Otras áreas del ámbito considerado: <b>146 ha</b></span></div>',
 '<p>Los resultados proceden de la tabla del escenario de riesgo de inundación, no de la suma de píxeles de un mapa web. Las 146 ha restantes se obtienen por diferencia aritmética; <strong>no deben interpretarse automáticamente como terrenos libres de peligro.</strong></p>',
 '</div>',
 '<div class="oaf-ux27-riskmap"><div><h3>Capa de inundación para toda la región</h3>',
 '<p>La cobertura regional puede consultarse usando una capa nacional recortada visualmente a Lambayeque. Las clases <strong>muy alto, alto, medio y bajo</strong> corresponden a susceptibilidad territorial, no a pérdidas ni a probabilidad de inundación cuantificada.</p>',
 '<div class="oaf-ux27-buttons"><button type="button" data-layer="5090024">Ver inundación por lluvias fuertes · CENEPRED</button>',
 '<button type="button" data-layer="5010502">Ver susceptibilidad regional · INGEMMET</button></div>',
 '<p id="oaf-ux27-layer-status" role="status" class="oaf-ux27-layer-status">Para explorar la capa, utiliza el visor situado debajo de este resumen.</p></div>',
 '<aside><strong>¿Qué se puede cuantificar?</strong><p><b>Ahora:</b> cifras publicadas para los nueve distritos del escenario CENEPRED y conteos de puntos georreferenciados cargados por el visor.</p>',
 '<p><b>Próxima evaluación SIG:</b> intersección reproducible de la capa de susceptibilidad y los polígonos agrícolas de 2018, con resultados por provincia, distrito y cuenca. Se necesitan archivos espaciales completos y verificación de sus clases y escala.</p></aside></div>',
 '<div class="oaf-ux27-foot"><p><strong>Contexto territorial adicional del mismo escenario:</strong> 50 299 viviendas y 374 km de vías se registran en zonas de mayor susceptibilidad dentro de los nueve distritos clasificados con riesgo muy alto. Los indicadores se refieren al mismo ámbito, no a toda Lambayeque.</p>',
 '<p><strong>Fuente y reproducibilidad:</strong> <a href="'+C.doc+'" target="_blank" rel="noopener noreferrer">CENEPRED · escenario de riesgos 2025–2027</a> · ',
 '<a href="'+C.report+'" target="_blank" rel="noopener noreferrer">reporte oficial de enero de 2026, página 4</a> · ',
 '<a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090024" target="_blank" rel="noopener noreferrer">capa regionalizable de susceptibilidad 5090024</a> · ',
 '<a href="https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5010502" target="_blank" rel="noopener noreferrer">capa regional INGEMMET 5010502</a>.</p></div>'
].join("");
function init(){
 const root=byId("oaf-territorio-riesgos");
 if(!root||byId("oaf-ux27-exposicion"))return;
 const sec=document.createElement("section");sec.id="oaf-ux27-exposicion";sec.className="oaf-ux27-exposicion";
 sec.setAttribute("aria-label","Análisis cuantitativo oficial de exposición agrícola");
 sec.innerHTML=panelHTML;
 const grid=root.querySelector(".oaf-ux24-grid");
 if(grid)grid.before(sec);else root.prepend(sec);
 byId("oaf-ux27-fill").style.width=Math.min(100,Math.max(0,percentage)).toFixed(3)+"%";
 byId("oaf-ux27-share").textContent=format(percentage)+" %";
 const btns=sec.querySelectorAll("[data-layer]");
 for(const b of btns)b.addEventListener("click",()=>{
  const layer=b.dataset.layer;
  const select=byId("oaf-ux25-raster");
  const status=byId("oaf-ux27-layer-status");
  if(!select||![...select.options].some(o=>o.value===layer)){
   status.textContent="El selector de mapas aún no está disponible. Abre SIGRID desde los enlaces oficiales.";
   return;
  }
  select.value=layer;
  select.dispatchEvent(new Event("change",{bubbles:true}));
  btns.forEach(x=>x.setAttribute("aria-pressed",String(x===b)));
  status.textContent=layer==="5090024"?
   "Seleccionada: susceptibilidad nacional a inundaciones por lluvias fuertes (CENEPRED 2021), aplicada al ámbito regional.":
   "Seleccionada: susceptibilidad regional a inundaciones compilada por INGEMMET, publicada en SIGRID.";
  byId("oaf-ux24-region-map")?.scrollIntoView({block:"center",behavior:"smooth"});
 });
 // El filtro territorial pertenece a otra consulta: NO extrapolar los totales oficiales.
 const note=document.createElement("p");note.className="oaf-ux27-static-note";
 note.textContent="Las cifras del informe CENEPRED permanecen fijas al cambiar provincia, distrito o cuenca: la fuente publicada no entrega en este cuadro un desglose para cada filtro.";
 sec.querySelector(".oaf-ux27-head").append(note);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();