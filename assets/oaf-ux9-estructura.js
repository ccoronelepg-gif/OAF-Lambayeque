(function ux9Layout(){
"use strict";
const $=id=>document.getElementById(id);
function attach(){
 const root=$("oaf-agro-home"),clima=$("oaf-agro-clima"),autor=$("oaf-agro-autor"),legacy=$("oaf-meta-legacy");
 if(!root||!clima||!autor||!legacy||$("oaf-ux9-predicciones"))return;
 const archivedHome=$("oaf-agro-archive-home")?.querySelector("div")||legacy;
 const archivedAutor=$("oaf-agro-archive-autor")?.querySelector("div")||legacy;
 const archive=(id,where=archivedHome)=>{const x=$(id);if(x)where.append(x)};
 const intro=document.querySelector(".oaf-agro-summary");
 if(intro&&!intro.querySelector(".oaf-intro-columns")){
  const paragraphs=[...intro.querySelectorAll(":scope > p")];
  const wrapper=document.createElement("div");wrapper.className="oaf-intro-columns";
  intro.append(wrapper);paragraphs.forEach(p=>wrapper.append(p));
 }
 // Eliminar duplicaciones visibles sin borrar sus contenedores o fuentes científicas.
 archive("oaf-agro-home-map");archive("oaf-agro-home-existing-forecast");
 const b1=$("oaf-bloque-clima-actual");
 b1?.querySelector(":scope > .oaf-agro-interpretation")?.remove();
 const b2=$("oaf-bloque-prediccion-inicio");
 if(b2){
  const h=b2.querySelector(".oaf-agro-block-head p");if(h)h.textContent="Descubre cómo han variado la lluvia y la temperatura con registros históricos analizados por OAF. Las predicciones de siete días se consultan en su pestaña especializada.";
  const tiles=b2.querySelectorAll(":scope > .oaf-agro-split > .oaf-agro-tile");
  if(tiles[0]&&tiles.length>1)archivedHome.append(tiles[0]);
  b2.querySelector(".oaf-agro-split")?.classList.add("oaf-ux9-one-chart");
  for(const q of [...b2.querySelectorAll(":scope > .oaf-agro-facts,:scope > .oaf-agro-interpretation")])archivedHome.append(q);
  archive("oaf-home-predictive-brief");
 }
 // El visor histórico 9K puede quedar en Metadatos; el nuevo mapa usa directamente el archivo GeoJSON publicado.
 archive("oaf-9k-visor", $("oaf-agro-archive-clima")?.querySelector("div")||legacy);
 archive("oaf-ecopaisajes-10k",$("oaf-agro-archive-clima")?.querySelector("div")||legacy);
 const mapSlot=$("oaf-regional-own-map");
 if(mapSlot){
  mapSlot.innerHTML='<div class="oaf-ux9-map-wrap"><div><div class="oaf-ux9-form"><label for="oaf-ux9-floor">Selecciona un piso de relieve</label><select id="oaf-ux9-floor"><option value="todos">Todos los pisos</option></select></div><div id="oaf-ux9-map" class="oaf-ux9-map" role="group" aria-label="Mapa interactivo de sectores de relieve y clima investigados"></div></div><aside class="oaf-ux9-map-info"><strong>Relieve y sectores OAF</strong><p id="oaf-ux9-map-count">Consultando cartografía auditada…</p><div id="oaf-ux9-map-legend" class="oaf-ux9-map-legend"></div><p id="oaf-ux9-map-detail">Selecciona un sector del mapa para conocer su elevación y su evidencia científica.</p></aside></div><p class="oaf-ux9-source">Mapa elaborado por OAF con 42 geometrías exploratorias del muestreo 9K. Sus colores distinguen franjas altitudinales; no son pronósticos ni zonas oficiales de cultivo. <a href="#verificaciones">Detalles y verificaciones →</a></p>';
 }
 const previous=$("oaf-autor-pronosticos");if(previous)archivedAutor.append(previous);
 const newUI=document.createElement("div");newUI.id="oaf-ux9-predicciones";
 newUI.innerHTML=`
<section id="oaf-ux9-pronostico" class="oaf-agro-block">
<header class="oaf-agro-block-head"><span class="oaf-agro-kicker">01 · Pronóstico agroclimático semanal</span><h2>¿Qué clima se espera durante los próximos siete días?</h2><p>Este panel consulta los modelos meteorológicos disponibles mediante Open-Meteo para estimar lluvia y calor día por día. El OAF procesa y explica esa información. Su modelo Random Forest, desarrollado en Python, se investiga a escala mensual y no se presenta como pronóstico diario.</p></header>
<div class="oaf-ux9-form"><label for="oaf-ux9-localidad">Localidad de Lambayeque</label><select id="oaf-ux9-localidad"><option>Chiclayo</option><option>Jayanca</option><option>Motupe</option><option>Olmos</option></select></div>
<div id="oaf-ux9-resumen-meteo" class="oaf-ux9-overview" role="status">Consultando el pronóstico actualizado…</div>
<div class="oaf-agro-split"><article class="oaf-color-dash"><h3>¿Qué días podría llover?</h3><div id="oaf-ux9-grafico-lluvia" class="oaf-ux9-chart" role="img" aria-label="Lluvia diaria pronosticada"></div><div class="oaf-ux9-legend"><span><i style="background:#49aee7"></i>Lluvia ligera</span><span><i style="background:#236bc6"></i>Acumulado más alto</span></div></article><article class="oaf-color-dash"><h3>¿Habrá días calurosos?</h3><div id="oaf-ux9-grafico-temperatura" class="oaf-ux9-chart" role="img" aria-label="Temperatura máxima diaria estimada"></div><div class="oaf-ux9-legend"><span><i style="background:#ffbb58"></i>Temperatura máxima</span><span><i style="background:#e76c44"></i>Días más cálidos</span></div></article></div>
<div id="oaf-ux9-dias" class="oaf-ux9-dates" aria-label="Resumen diario pronosticado"></div>
<p class="oaf-ux9-source" id="oaf-ux9-fuente-meteo">Origen: Open-Meteo; datos meteorológicos de modelos externos. El OAF realiza la visualización e interpretación divulgativa. La hora de actualización y los días cubiertos se identifican al consultar el proveedor.</p>
</section>
<section id="oaf-ux9-nino" class="oaf-agro-block">
<header class="oaf-agro-block-head"><span class="oaf-agro-kicker">02 · Océano y anomalías climáticas</span><h2>¿Qué señales muestran El Niño y El Niño Costero?</h2><p>El Niño Costero se sigue cerca de Perú; El Niño global se evalúa en el Pacífico ecuatorial central. Son fenómenos relacionados, pero no se clasifican con el mismo indicador. El OAF contrasta índices oceánicos, antecedentes y boletines de las instituciones especializadas.</p></header>
<div class="oaf-agro-split"><article class="oaf-color-dash"><h3>Temperatura del mar · Niño 1+2</h3><div class="oaf-ux9-form"><label for="oaf-ux9-meses">Meses del gráfico</label><select id="oaf-ux9-meses"><option value="12">12 meses</option><option value="24" selected>24 meses</option><option value="36">36 meses</option></select></div><div id="oaf-ux9-grafico-enso" class="oaf-ux9-chart" role="img" aria-label="Serie de anomalías históricas del mar Niño 1 más 2"></div><p id="oaf-ux9-enso-fecha" class="oaf-ux9-source">Recuperando registro histórico NOAA con base 1991–2020.</p></article><article class="oaf-color-dash"><h3>Qué indican los comunicados</h3><div class="oaf-ux9-enso-summary" id="oaf-ux9-enfen-estado" role="status">Consultando la última revisión documental ENFEN…</div><div class="oaf-ux9-enso-summary" id="oaf-ux9-noaa-estado" role="status">Consultando la perspectiva NOAA…</div><p class="oaf-ux9-source">La intensidad de El Niño global no se traslada automáticamente al Niño Costero ni determina lluvias específicas para Lambayeque. <a href="#nino">Boletines y análisis →</a></p></article></div>
<div class="oaf-ux9-overview" id="oaf-ux9-enso-interpretacion">Analizando las anomalías oceánicas y sus fechas para una lectura sencilla.</div>
</section>
<section id="oaf-ux9-conclusiones" class="oaf-ux9-final">
<span class="oaf-agro-kicker">Lectura rápida para productores</span><h2>Conclusiones de la situación agroclimática</h2>
<section><h3>¿Se esperan lluvias?</h3><p id="oaf-ux9-final-lluvia" aria-live="polite">Consultando los próximos siete días para identificar las fechas con precipitación prevista.</p></section>
<section><h3>¿Qué pasa con la temperatura?</h3><p id="oaf-ux9-final-temperatura">Revisando las máximas previstas para la localidad elegida.</p></section>
<section><h3>¿Cómo evoluciona El Niño?</h3><p id="oaf-ux9-final-enso">Revisando información fechada de ENFEN y NOAA y las anomalías del océano.</p></section>
<section><h3>Consulta científica</h3><p>Para conocer las fuentes, cómo se construyen los modelos en Python/Random Forest, sus límites y la metodología completa, visita <a href="#verificaciones">Metadatos y trazabilidad →</a>. Los pronósticos cambian con cada actualización y deben interpretarse para cada localidad.</p></section>
</section>`;
 autor.append(newUI);
 document.documentElement.dataset.oafUx9="activo";
 document.dispatchEvent(new CustomEvent("oaf:ux9-ready"));
}
document.addEventListener("oaf:agro-ready",attach);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",attach,{once:true});else attach();
})();
