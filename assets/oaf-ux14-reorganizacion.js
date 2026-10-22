/* UX14 - Arquitectura: Clima = observación; Predicciones = investigación propia */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const E=(tag,cls,text)=>{let x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x};
const L=(title,url)=>{let a=E("a",null,title);a.href=url;a.rel="noopener noreferrer";if(!url.startsWith("#"))a.target="_blank";return a};
const coord={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
let initDone=false;
function section(title,tagline,desc,id){
 const s=E("section","oaf-ux14-block");s.id=id;
 const header=E("div","oaf-ux14-heading");header.append(E("small",null,tagline),E("h2",null,title),E("p",null,desc));s.append(header);return s;
}
function moveStructure(){
 if(initDone||!$("oaf-ux9-predicciones")||!$("oaf-agro-clima")||!$("oaf-agro-autor"))return;
 initDone=true;
 const climate=$("oaf-agro-clima"),autor=$("oaf-agro-autor"),old=$("oaf-ux9-predicciones");
 // Existing meteorological forecasts are EXTERNAL; keep their chart IDs and event wiring.
 const weekly=$("oaf-ux9-pronostico"),enso=$("oaf-ux9-nino"),concl=$("oaf-ux9-conclusiones");
 if(weekly){const title=weekly.querySelector("h2");if(title)title.textContent="Pronóstico agroclimático semanal · 7 días";climate.append(weekly)}
 if(enso)climate.append(enso);
 if(concl)climate.append(concl);
 const own=$("oaf-clima-bloque-modelo");
 if(own){
   own.querySelector(".oaf-agro-block-head h2").textContent="Análisis predictivo propio: Random Forest y paisajes agroclimáticos";
   own.querySelector(".oaf-agro-block-head p").textContent="El análisis cartográfico organiza sectores según relieve y condiciones agroclimáticas; permite comparar la lluvia histórica con las estimaciones mensuales Random Forest y una climatología de referencia. Los paisajes son agrupaciones exploratorias y no delimitaciones oficiales de riesgo agrícola.";
   const tiles=own.querySelectorAll(":scope > .oaf-agro-split > .oaf-agro-tile");
   if(tiles[1]){
      const archive=$("oaf-agro-archive-autor")?.querySelector("div")||$("oaf-meta-legacy");
      const details=E("details","oaf-ux14-legacy");details.append(E("summary",null,"Comparación técnica RF y GCN (archivo histórico)"));
      details.append(tiles[1]);archive?.append(details);
   }
   const landscape=own.querySelector(":scope > .oaf-agro-split > .oaf-agro-tile");
   if(landscape){
     const p=landscape.querySelector("p");if(p)p.textContent="Panel resumido: consulta dentro de esta pestaña los cinco paisajes, la lluvia histórica, las salidas retrospectivas RF y la climatología. El mapa técnico de sectores conserva sus archivos originales.";
     const anchor=landscape.querySelector('a[href*="ecorregiones-clima-10k.html"]');
     if(anchor){anchor.href="#oaf-ux14-rf-mes";anchor.textContent="Consultar gráfico por paisaje, sin superposiciones ↓"}
     const extra=L("Abrir cartografía técnica en página independiente ↗","ecorregiones-clima-10k.html");
     extra.className="oaf-ux15-landscape-secondary";landscape.append(extra);
   }
   autor.append(own);
 }
 const stations=$("oaf-clima-bloque-estaciones");
 if(stations){climate.append(stations);const label=stations.querySelector("h2");if(label)label.textContent="Trazabilidad instrumental · estaciones y pisos altitudinales";}
 const oldHead=$("autor")?.querySelector(".oaf-forecast-split");
 if(oldHead){const tech=$("oaf-agro-archive-autor")?.querySelector("div");if(tech)tech.append(oldHead)}
 const nav=$("oaf-menu-autor");if(nav){const tech=$("oaf-agro-archive-autor")?.querySelector("div");if(tech)tech.append(nav)}
 const intro=E("div","oaf-ux14-intro");
 intro.innerHTML='<span>INTELIGENCIA ARTIFICIAL APLICADA AL CLIMA · LAMBAYEQUE</span><h1>Predicciones y Anomalías</h1><p>Esta sección analiza la variabilidad de la lluvia y la temperatura en Lambayeque mediante <strong>Python, Random Forest y análisis geoespacial</strong>. Reúne la comparación semanal de algoritmos, una evaluación mensual por paisaje y mapas de relieve para estudiar diferencias territoriales. Los errores retrospectivos ayudan a identificar dónde se requiere mejorar la predicción, pero no sustituyen su validación con observaciones nuevas. <strong>Modelo propio en investigación y mejora continua:</strong> no emitir decisiones agrícolas ni alertas oficiales a partir de estos resultados por sí solos.</p>';
 autor.prepend(intro);
 const status=E("div","oaf-ux14-alert");
 status.append(E("strong",null,"Estado científico: modelo Random Forest en investigación y mejora continua"));
 intro.after(status);
 const live=section("Horizonte de siete días · Comparación de modelos","01 · Próximos siete días","El gráfico semanal muestra, para una localidad y las mismas fechas, la referencia diaria de Open-Meteo y el modelo experimental Random Forest elaborado por OAF. Puedes elegir lluvia o temperatura y contrastar las diferencias de ambas curvas. Para evaluar cuál predijo mejor, es necesario compararlas posteriormente con observaciones verificadas; la semejanza entre modelos no acredita precisión.","oaf-ux14-rf-semana");
 live.innerHTML+='<div class="oaf-ux14-controls"><label for="oaf-ux14-ciudad">Localidad</label><select id="oaf-ux14-ciudad"><option>Chiclayo</option><option>Jayanca</option><option>Motupe</option><option>Olmos</option></select><label for="oaf-ux14-variable">Variable</label><select id="oaf-ux14-variable"><option value="rain">Precipitación (mm/día)</option><option value="tmax">Temperatura máxima (°C)</option></select></div><div class="oaf-ux14-chart" id="oaf-ux14-weekchart" role="img" aria-label="Referencia externa para siete días"></div><div class="oaf-ux14-key"><span><i style="background:#419bd2"></i>Referencia meteorológica externa</span><span><i style="background:#b3c2ba"></i>Random Forest OAF · experimental</span></div><p class="oaf-ux14-source" id="oaf-ux14-weekstatus">Consultando proveedor de referencia…</p>';
 const month=section("Horizonte mensual y evolución por paisajes","02 · Investigación mensual","La vista inicial corresponde a los escenarios experimentales de noviembre de 2026 a abril de 2027 para una localidad. Se muestra la lluvia mensual estimada por Random Forest junto con la climatología histórica de referencia; también puedes cambiar a la evaluación retrospectiva 2021–2025 por paisaje. Comprueba la fecha del último dato utilizado: los errores calculados a un mes no demuestran precisión a seis meses ni validación operativa.","oaf-ux14-rf-mes");
 month.innerHTML+='<div class="oaf-ux14-controls"><label for="oaf-ux14-paisaje">Paisaje agroclimático (experimental)</label><select id="oaf-ux14-paisaje"><option value="todos">Todos los paisajes</option></select><label for="oaf-ux14-metric">Serie mostrada</label><select id="oaf-ux14-metric"><option value="all">Observado, RF y climatología</option><option value="rf">RF y observado</option><option value="ref">Climatología y observado</option></select></div><div class="oaf-ux14-metrics" id="oaf-ux14-kpis"></div><div class="oaf-ux14-chart" id="oaf-ux14-monthchart" role="img" aria-label="Evaluación mensual retrospectiva por paisaje"></div><div class="oaf-ux14-key"><span><i style="background:#2e8ab8"></i>Lluvia observada</span><span><i style="background:#e49d4d"></i>RF retrospectivo</span><span><i style="background:#43977a"></i>Climatología</span></div><p class="oaf-ux14-source" id="oaf-ux14-monthstatus">Cargando evaluación retrospectiva 10K…</p><p class="oaf-ux14-no-forecast"><strong>Próximos meses:</strong> pronósticos RF candidatos disponibles por localidad desde noviembre de 2026. Son cálculos experimentales sin validación prospectiva suficiente y no deben emplearse como alertas.</p>';
 if(own){own.after(live,month)}else{status.after(live,month)}
 const compareArchive=$("oaf-agro-archive-autor")?.querySelector("div");
 if(compareArchive)compareArchive.append(E("p","oaf-agro-caption","Comparaciones históricas Random Forest, GCN y CNN accesibles en Metadatos y Trazabilidad; no son el pronóstico público operativo."));
 // The old parent has no visible forecast after moving its contents.
 if(old&&!old.children.length)old.remove();
 const climIntro=$("clima")?.querySelector(".viewhead p");
 if(climIntro)climIntro.textContent="Consulta mapas, datos históricos y el pronóstico semanal. Los modelos propios están en Predicciones y Anomalías.";
 const menu=$("oaf-menu-clima");
 if(menu){const links=menu.querySelectorAll('a[href^="#"]');for(const l of links)if(l.getAttribute("href")==="#oaf-clima-bloque-modelo")l.setAttribute("href","#autor")}
 const ninoLabel=$("oaf-ux9-pronostico")?.querySelector(".oaf-agro-block-head p");
 if(ninoLabel)ninoLabel.textContent="Pronóstico externo a siete días obtenido mediante Open-Meteo. El OAF visualiza lluvia, temperatura y fechas de consulta; no debe confundirse con una predicción propia de Random Forest.";
 highlightStations();
 renderHome();
 initDaily();
 initMonth();
 document.documentElement.dataset.oafUx14="reorganizado";
}
function highlightStations(){
 const target=$("oaf-stations-map");if(!target)return;
 const palette=["#c34e55","#1c8fbc","#d98b29","#6e68c9","#268c67","#a74e9f","#ae7732","#3c79c8","#cc667c","#008d91","#b28a39","#667d30","#dd6660","#505fa7","#6e9363","#923e7f"];
 const colors=new Map();let next=0;
 function paint(){
   const svg=target.querySelector("svg");if(!svg)return;
   const dots=[...svg.querySelectorAll("circle.oaf-map-symbol")];
   for(const dot of dots){
     const name=(dot.getAttribute("aria-label")||"").replace(/\s+-?\d+(?:\.\d+)?\s+metros.*$/,"");
     if(!colors.has(name))colors.set(name,palette[next++%palette.length]);
     const color=colors.get(name);dot.setAttribute("fill",color);dot.style.fill=color;dot.setAttribute("stroke","#fff");dot.setAttribute("stroke-width","2.5");dot.setAttribute("r","8");}
   let legend=$("oaf-ux14-station-legend");if(!legend){legend=E("div","oaf-ux14-station-legend");legend.id="oaf-ux14-station-legend";target.after(legend);}
   legend.replaceChildren();for(const [name,color] of colors){const chip=E("span");const sw=E("i");sw.style.backgroundColor=color;chip.append(sw,document.createTextNode(name));legend.append(chip)}
 }
 const ob=new MutationObserver(()=>paint());ob.observe(target,{childList:true});
 paint();
}
function renderHome(){
 const hero=$("inicio")?.querySelector(".oaf-home-shell>.oaf-hero-2026");if(!hero)return;
 const parent=hero.parentElement,layout=E("div","oaf-ux14-home-hero");hero.before(layout);layout.append(hero);
 const side=E("aside","oaf-ux14-home-side");
 side.innerHTML='<article class="oaf-ux14-tile oaf-ux14-nino"><small>SEGUIMIENTO DE EL NIÑO COSTERO</small><h2>Estado oficial ENFEN</h2><p id="oaf-ux14-home-enso">Leyendo el último comunicado documentado…</p><p id="oaf-ux14-home-prob">Las probabilidades por intensidad se presentan únicamente cuando procede de un boletín oficial y están fechadas.</p><div class="oaf-ux15-explain" id="oaf-ux15-enfen-exp">Las categorías representan temperaturas oceánicas de la región Niño 1+2; no indican la probabilidad de lluvias intensas en Lambayeque.</div><div class="oaf-ux15-source"><strong>Fuente:</strong> <a href="https://enfen.imarpe.gob.pe/comunicados/" target="_blank" rel="noopener noreferrer">ENFEN · boletín y figura oficial ↗</a></div></article>';
 layout.append(side);
 fetch("datos/estado_enso_verificado_ux9_2026.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error(r.status);return r.json()}).then(d=>{
   $("oaf-ux14-home-enso").textContent=(d.enfen?.estado||"No verificado")+" · comunicado "+(d.enfen?.numero||"sin número")+" del "+(d.enfen?.fecha_emision||"sin fecha")+". Condición costera; no indica lluvia diaria por sí sola.";
   const prob=$("oaf-ux14-home-prob");
   fetch("datos/enfen_probabilidades_portada_2026.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("No hay cuadro");return r.json()}).then(p=>{
     if(p.comunicado!==d.enfen.numero||p.fecha_publicacion!==d.enfen.fecha_emision)throw Error("Ediciones distintas");
     const row=p.meses.find(x=>x.mes==="2026-10");if(!row)throw Error("Mes faltante");
     prob.replaceChildren();
     prob.append(E("strong",null,"Probabilidades oficiales ICEN · octubre 2026"));
     const bars=E("div","oaf-ux14-prob-bars");
     for(const [key,label,color] of [["extraordinaria","Extraordinaria","#ac3f38"],["fuerte","Fuerte","#d88248"],["moderada","Moderada","#e3b952"]]){
       const value=row[key],item=E("div","oaf-ux14-probline");
       item.append(E("span",null,label),E("b",null,value+" %"));
       const bar=E("div","oaf-ux14-probtrack"),inner=E("i");inner.style.width=value+"%";inner.style.background=color;bar.append(inner);item.append(bar);bars.append(item);}
     prob.append(bars);
    const info=$("oaf-ux15-enfen-exp");
    if(info)info.textContent="Interpretación: esta probabilidad expresa la categoría de calentamiento oceánico prevista para octubre de 2026, no la probabilidad de lluvia, inundación o afectación agrícola. El boletín fue emitido el 16/10/2026; consulta si existe uno posterior.";
    const citation=$("inicio")?.querySelector(".oaf-ux15-source a");if(citation)citation.href=p.fuente;
   }).catch(()=>{prob.replaceChildren(E("span",null,"Probabilidades no verificables para este comunicado; revisa el gráfico oficial."),L("ENFEN ↗",d.enfen?.fuente||"https://enfen.imarpe.gob.pe/comunicados/"))});
 }).catch(()=>$("oaf-ux14-home-enso").textContent="No se pudo verificar una actualización del organismo oficial. Consulta ENFEN.");

}
const fmt=(v,dec=1)=>Number(v).toLocaleString("es-PE",{maximumFractionDigits:dec,minimumFractionDigits:dec});
async function getForecast(city){
 const [lat,lon]=coord[city];const params=new URLSearchParams({latitude:lat,longitude:lon,timezone:"America/Lima",forecast_days:7,daily:"precipitation_sum,temperature_2m_max"});
 const r=await fetch("https://api.open-meteo.com/v1/forecast?"+params);if(!r.ok)throw Error("Open-Meteo: HTTP "+r.status);
 const d=(await r.json()).daily;
 if(!d||d.time?.length!==7||!d.precipitation_sum?.every(Number.isFinite)||!d.temperature_2m_max?.every(Number.isFinite))throw Error("Valores diarios no válidos");
 return d;
}
async function initHomeWeather(){
 try{const d=await getForecast("Chiclayo"),mm=d.precipitation_sum.reduce((x,y)=>x+y,0),max=Math.max(...d.temperature_2m_max);
 $("oaf-ux14-home-weather").textContent="Chiclayo · próximos 7 días: "+fmt(mm)+" mm acumulados previstos y máxima hasta "+fmt(max)+" °C. Pronóstico externo Open-Meteo; puede cambiar."; }
 catch(e){$("oaf-ux14-home-weather").textContent="Pronóstico no disponible. Consulta Clima Regional para comprobar la fuente."}
}
function svgChart(id,series,labels,unit,zero=true){
 const root=$(id);if(!root)return;
 const available=series.filter(s=>s.values.length===labels.length&&s.values.every(Number.isFinite));
 if(!available.length){root.textContent="No existe una serie numérica verificable.";return;}
 const ns="http://www.w3.org/2000/svg",make=(tag,attr,text)=>{const el=document.createElementNS(ns,tag);Object.entries(attr||{}).forEach(([k,v])=>el.setAttribute(k,String(v)));if(text!==undefined)el.textContent=text;return el};
 const W=790,H=300,L=50,R=24,T=20,B=45;const values=available.flatMap(s=>s.values);const ymin=zero?0:Math.min(...values)-2,ymax=Math.max(...values,zero?1:0),hi=ymax+(ymax-ymin||1)*.13,dx=i=>L+(i+.5)*(W-L-R)/labels.length,dy=v=>T+(hi-v)/(hi-ymin)*(H-T-B);
 const s=make("svg",{viewBox:"0 0 790 300",role:"img","aria-label":"Gráfico de "+unit});for(let i=0;i<=4;i++){let n=ymin+(hi-ymin)*i/4,y=dy(n);s.append(make("line",{x1:L,x2:W-R,y1:y,y2:y,stroke:"#dce6e0"}),make("text",{x:L-8,y:y+4,"text-anchor":"end",fill:"#5d746a","font-size":11},fmt(n,0)))}
 const colors=["#2e8ab8","#e49d4d","#43977a"];for(const [si,item] of available.entries()){
   const color=item.color||colors[si],pts=item.values.map((v,i)=>dx(i)+","+dy(v)).join(" ");
   s.append(make("polyline",{points:pts,fill:"none",stroke:color,"stroke-width":3.4,"stroke-linecap":"round","stroke-linejoin":"round"}));
   item.values.forEach((v,i)=>{const q=make("circle",{cx:dx(i),cy:dy(v),r:4.2,fill:color,stroke:"#fff","stroke-width":1.5,tabindex:0,role:"img","aria-label":labels[i]+" "+item.name+" "+fmt(v)+" "+unit});q.append(make("title",{},labels[i]+" · "+item.name+": "+fmt(v)+" "+unit));s.append(q)});
 }
 labels.forEach((t,i)=>{if(i%(Math.max(1,Math.ceil(labels.length/7)))===0||i===labels.length-1)s.append(make("text",{x:dx(i),y:H-13,"text-anchor":"middle",fill:"#5d746a","font-size":11},t))});
 root.replaceChildren(s);
}
let weekSeq=0;
function initDaily(){
 const city=$("oaf-ux14-ciudad"),variable=$("oaf-ux14-variable");if(!city||!variable)return;
 const call=async()=>{const q=++weekSeq,c=city.value;const out=$("oaf-ux14-weekstatus");out.textContent="Consultando meteorología para "+c+"…";
 try{const d=await getForecast(c);if(q!==weekSeq)return;const isRain=variable.value==="rain",values=isRain?d.precipitation_sum:d.temperature_2m_max;
 svgChart("oaf-ux14-weekchart",[{name:"Open-Meteo (externo)",values,color:isRain?"#419bd2":"#dc8555"}],d.time.map(x=>x.slice(5)),isRain?"mm/día":"°C",isRain);
 out.textContent="Open-Meteo · referencia externa para "+c+" del "+d.time[0]+" al "+d.time[6]+". RF OAF se compara en esta misma gráfica cuando coinciden las fechas.";document.dispatchEvent(new CustomEvent("oaf:ux16-externo-diario",{detail:{localidad:c,dias:d}})); }
 catch(e){if(q!==weekSeq)return;$("oaf-ux14-weekchart").textContent="Referencia externa no disponible.";out.textContent="No se puede mostrar un pronóstico sin datos: "+e.message}};
 city.addEventListener("change",call);variable.addEventListener("change",call);call();
}
function initMonth(){
 const sel=$("oaf-ux14-paisaje"),metric=$("oaf-ux14-metric");if(!sel||!metric)return;
 Promise.all([
 fetch("datos/ecopaisajes_10k/evaluacion_ecoclimatica_10k.json").then(r=>{if(!r.ok)throw Error("Evaluación no disponible");return r.json()}),
 fetch("datos/ecopaisajes_10k/series_sector_mes_10k.json").then(r=>{if(!r.ok)throw Error("Serie no disponible");return r.json()})
 ]).then(([meta,data])=>{
   if(meta.fase!=="10K"||data.fase!=="10K"||!Array.isArray(data.datos)||data.datos.length<1000)throw Error("Datos científicos incompletos");
   for(const [id,p] of Object.entries(meta.paisajes)){let o=E("option",null,p.nombre);o.value=id;sel.append(o)}
   const redraw=()=>{
    const rows=data.datos.filter(r=>sel.value==="todos"||r.paisaje===sel.value);if(!rows.length)return;
    const agg=Array.from({length:12},(_,i)=>{
      const records=rows.filter(r=>Number(r.mes.slice(-2))===i+1),avg=k=>records.reduce((s,r)=>s+Number(r[k]),0)/Math.max(1,records.length);
      return{obs:avg("observado_mm"),rf:avg("rf_mm"),clim:avg("climatologia_mm")}
    });
    const mae=(field)=>rows.reduce((s,r)=>s+Math.abs(Number(r[field])-Number(r.observado_mm)),0)/rows.length;
    const maeRF=mae("rf_mm"),maeClim=mae("climatologia_mm");
    const tiles=$("oaf-ux14-kpis");tiles.replaceChildren();for(const [title,value] of [["Paisajes / sectores",sel.value==="todos"?"5 / 39":meta.paisajes[sel.value].n_sectores+" sectores"],["MAE RF retrospectivo",fmt(maeRF)+" mm"],["MAE climatología",fmt(maeClim)+" mm"]]){
      const item=E("article");item.append(E("small",null,title),E("strong",null,value));tiles.append(item)}
    const show=metric.value,series=[{name:"Observado",values:agg.map(x=>x.obs),color:"#2e8ab8"}];
    if(show!=="ref")series.push({name:"RF retrospectivo",values:agg.map(x=>x.rf),color:"#e49d4d"});
    if(show!=="rf")series.push({name:"Climatología",values:agg.map(x=>x.clim),color:"#43977a"});
    if($("oaf-ux16-vista")?.value!=="futuro")svgChart("oaf-ux14-monthchart",series,["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],"mm/mes");
    if($("oaf-ux16-vista")?.value!=="futuro")$("oaf-ux14-monthstatus").textContent="Prueba retrospectiva 2021–2025 (10K), "+rows.length+" registros sector-mes; MAE RF "+fmt(maeRF)+" mm frente a climatología "+fmt(maeClim)+" mm. No es una proyección futura.";
   };
   sel.addEventListener("change",redraw);metric.addEventListener("change",redraw);redraw();
 }).catch(e=>{$("oaf-ux14-monthstatus").textContent="Modelo por paisaje no disponible: "+e.message;$("oaf-ux14-monthchart").textContent="Sin cifras: revisa el archivo técnico."});
}
document.addEventListener("oaf:ux9-ready",moveStructure);
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",moveStructure,{once:true});else moveStructure();
})();