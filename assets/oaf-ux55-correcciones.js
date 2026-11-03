/* OAF UX55 · Correcciones solicitadas: inicio, series históricas y visores */
(()=>{"use strict";
const $=selector=>document.querySelector(selector),ns="http://www.w3.org/2000/svg";let mapsWired=false;
const cities={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const el=(tag,cls,txt)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n};
const fmt=(v,d=1)=>Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}):"—";
const svg=(tag,attrs={},txt)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(txt!==undefined)n.textContent=txt;return n};
function drawBars(host,rows,unit,color="#278eb8"){
 host.replaceChildren();if(!rows.length){host.textContent="No hay datos completos para representar.";return}
 const max=Math.max(1,...rows.map(x=>Number(x.value)||0));
 rows.forEach(row=>{const item=el("div","oaf-ux55-bar");const val=el("strong","",fmt(row.value,1));const track=el("div","oaf-ux55-track");const bar=el("i");bar.style.height=Math.max(2,(Number(row.value)||0)/max*100)+"%";bar.style.background=color;track.append(bar);const label=el("small","",row.label);item.title=row.label+": "+fmt(row.value,1)+" "+unit;item.append(val,track,label);host.append(item)});
}
async function fetchJSON(url){const r=await fetch(url,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);return r.json()}
function monthKeys(){const p=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit"}).formatToParts(new Date());let y=+p.find(x=>x.type==="year").value,m=+p.find(x=>x.type==="month").value+1;if(m===13){m=1;y++}return Array.from({length:6},()=>{const k=y+"-"+String(m).padStart(2,"0");if(++m===13){m=1;y++}return k})}
function currentMonthKey(){const p=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit"}).formatToParts(new Date());return p.find(x=>x.type==="year").value+"-"+p.find(x=>x.type==="month").value}
function monthLabel(key){const [y,m]=key.split("-").map(Number);return new Date(Date.UTC(y,m-1,1)).toLocaleDateString("es-PE",{month:"long",year:"numeric",timeZone:"UTC"})}
function buildCarousel(){
 const side=$("#inicio .oaf-ux14-home-side");if(!side||side.dataset.ux55Ready)return false;side.dataset.ux55Ready="1";
 side.classList.add("oaf-ux42-carousel","oaf-ux55-carousel");side.replaceChildren();
 const slides=[];
 const addSlide=(id,title,subtitle)=>{const card=el("article","oaf-ux14-tile oaf-ux42-slide oaf-ux55-slide");card.id="oaf-ux55-"+id;card.hidden=true;card.append(el("small","",subtitle),el("h2","",title));const body=el("p","oaf-ux42-highlight","Consultando fuente…");body.id="oaf-ux55-"+id+"-body";card.append(body);const chart=el("div","oaf-ux55-chart");chart.id="oaf-ux55-"+id+"-chart";card.append(chart);const note=el("p","oaf-ux42-note");note.id="oaf-ux55-"+id+"-note";card.append(note);slides.push(card);side.append(card);return card};
 const official=addSlide("enfen","Estado oficial ENFEN","SEGUIMIENTO DE EL NIÑO COSTERO · REGIÓN NIÑO 1+2");
 const week=addSlide("week","Pronóstico meteorológico","PRÓXIMOS SIETE DÍAS");
 const season=addSlide("season","Perspectiva estacional de precipitación","PRÓXIMOS SEIS MESES · ECMWF SEAS5");
 const controls=el("nav","oaf-ux42-controls");controls.setAttribute("aria-label","Carrusel de información climática");
 const back=el("button","","‹");back.type="button";back.setAttribute("aria-label","Anterior");
 const next=el("button","","›");next.type="button";next.setAttribute("aria-label","Siguiente");
 const dots=slides.map((s,i)=>{const b=el("button","oaf-ux42-dot",String(i+1));b.type="button";b.setAttribute("aria-label",["Estado ENFEN","Pronóstico 7 días","Perspectiva estacional"][i]);controls.append(b);return b});
 let index=0,timer=null;
 const go=i=>{index=(i+slides.length)%slides.length;slides.forEach((s,j)=>{s.hidden=j!==index;s.setAttribute("aria-hidden",String(j!==index))});dots.forEach((b,j)=>b.setAttribute("aria-current",String(j===index)))};
 const stop=()=>{if(timer)clearInterval(timer);timer=null};
 const start=()=>{stop();if(!document.hidden&&!matchMedia("(prefers-reduced-motion: reduce)").matches)timer=setInterval(()=>go(index+1),14000)};
 back.addEventListener("click",()=>{go(index-1);start()});next.addEventListener("click",()=>{go(index+1);start()});
 controls.prepend(back);controls.append(next);side.append(controls);dots.forEach((b,i)=>b.addEventListener("click",()=>{go(i);start()}));
 side.addEventListener("mouseenter",stop);side.addEventListener("mouseleave",start);side.addEventListener("focusin",stop);side.addEventListener("focusout",e=>{if(!side.contains(e.relatedTarget))start()});document.addEventListener("visibilitychange",start);
 const selected=()=>{const p=window.OAFTerritory?.getActivePoint?.("inicio");if(p)return {name:p.name,lat:p.lat,lon:p.lon};const name=$("#oaf-home-location")?.value||"Chiclayo",c=cities[name]||cities.Chiclayo;return {name,lat:c[0],lon:c[1]}};
 const load=async()=>{
  const p=selected(),enfenBody=$("#oaf-ux55-enfen-body"),enfenChart=$("#oaf-ux55-enfen-chart"),enfenNote=$("#oaf-ux55-enfen-note");
  try{
   const [d,probability]=await Promise.all([fetchJSON("datos/estado_enfen_3z.json"),fetchJSON("datos/enfen_probabilidades_portada_2026.json")]);
    enfenBody.textContent=(d.estado_institucional||"Estado no verificado")+" · Comunicado N.º "+d.numero+"-"+d.anio+" · "+d.fecha_emision+".";
    const matches=probability.institucion==="ENFEN"&&probability.comunicado===String(d.numero)+"-"+String(d.anio)&&Array.isArray(probability.meses);
    const current=currentMonthKey(),categories=[
     {key:"extraordinaria",label:"Extraordinaria",color:"#b52d25"},
     {key:"fuerte",label:"Fuerte",color:"#d45b38"},
     {key:"moderada",label:"Moderada",color:"#e5a344"},
     {key:"debil",label:"Débil",color:"#e6c75d"},
     {key:"neutral",label:"Neutral",color:"#9eaaa8"},
     {key:"fria",label:"Fría",color:"#5b9db5"}
    ];
    const selected=matches?probability.meses.find(x=>x.mes>=current&&categories.some(c=>Number.isFinite(Number(x[c.key])))):null;
    enfenChart.replaceChildren();
    if(selected){
     const month=el("strong","oaf-ux55-enfen-month","Probabilidad por categoría · "+monthLabel(selected.mes)+" · "+(probability.region||"Niño 1+2"));
     const rows=el("div","oaf-ux55-enfen-rows");
     for(const category of categories){
      const value=Number(selected[category.key]);
      if(!Number.isFinite(value)||value<=0)continue;
      const row=el("div","oaf-ux55-enfen-row");
      const label=el("span","",category.label);
      const track=el("span","oaf-ux55-enfen-track");
      const fill=el("i");fill.style.width=Math.max(0,Math.min(100,value))+"%";fill.style.background=category.color;track.append(fill);
      const percent=el("strong","",fmt(value,0)+" %");
      row.append(label,track,percent);rows.append(row);
     }
     enfenChart.append(month,rows);
     enfenChart.append(el("small","oaf-ux55-enfen-foot","Probabilidades de magnitud del índice ICEN para Niño 1+2; no son probabilidades de lluvia, inundación ni daños locales."));
    }else{
     enfenChart.textContent="No hay una probabilidad mensual verificable para el periodo actual en el comunicado consultado.";
    }
    enfenNote.textContent="Interpretación: ENFEN mantiene la Alerta de El Niño Costero. Para Niño 1+2 prevé magnitud extraordinaria hasta febrero de 2027 y descenso gradual hasta junio. Proyecta lluvias por encima de lo normal en la costa norte entre noviembre de 2026 y enero de 2027 y caudales superiores a lo normal desde diciembre en los ríos Tumbes, Chira, Piura, La Leche y Jequetepeque. En Lambayeque conviene vigilar especialmente La Leche. Es una perspectiva regional, no una predicción de inundación para una parcela.";
    const link=el("a","","ENFEN · comunicado oficial y Figura 2 ↗");link.href=probability.fuente||d.url_comunicado||"https://enfen.imarpe.gob.pe/comunicados/";link.target="_blank";link.rel="noopener noreferrer";enfenNote.append(" ",link);
  }catch(e){enfenBody.textContent="No se pudo comprobar el estado oficial ENFEN.";enfenNote.textContent="Consulta los comunicados originales del organismo. No se mostrará una probabilidad sin fuente verificable."}
  const wb=$("#oaf-ux55-week-body"),wc=$("#oaf-ux55-week-chart"),wn=$("#oaf-ux55-week-note");wb.textContent="Consultando Open-Meteo para "+p.name+"…";wc.replaceChildren();
  try{
   const q=new URLSearchParams({latitude:p.lat,longitude:p.lon,daily:"precipitation_sum,temperature_2m_max,temperature_2m_min,shortwave_radiation_sum",timezone:"America/Lima",forecast_days:"7"});
   const d=await fetchJSON("https://api.open-meteo.com/v1/forecast?"+q);
   if(!d.daily||d.daily.time?.length!==7||!["precipitation_sum","temperature_2m_max","temperature_2m_min","shortwave_radiation_sum"].every(k=>Array.isArray(d.daily[k])&&d.daily[k].length===7&&d.daily[k].every(Number.isFinite)))throw Error("Serie diaria incompleta");
   const rows=d.daily.time.map((date,i)=>({label:date.slice(5),value:d.daily.precipitation_sum[i]}));drawBars(wc,rows,"mm/día");
   const total=d.daily.precipitation_sum.reduce((a,b)=>a+b,0),rainDays=rows.filter(x=>x.value>=1).length,maxT=Math.max(...d.daily.temperature_2m_max),rad=d.daily.shortwave_radiation_sum.reduce((a,b)=>a+b,0);
   wb.textContent=p.name+" · "+d.daily.time[0]+" a "+d.daily.time[6]+" · "+fmt(total)+" mm acumulados previstos.";
   wn.textContent="Interpretación: "+(total<1?"no se esperan acumulados relevantes de precipitación en el periodo consultado.":rainDays+" día(s) con al menos 1 mm previsto; revisar la distribución diaria y los avisos oficiales.")+" Temperatura máxima prevista: "+fmt(maxT)+" °C. Radiación solar acumulada: "+fmt(rad)+" MJ/m². Fuente: Open-Meteo Forecast API; pronóstico externo sujeto a actualización.";
  }catch(e){wb.textContent="Pronóstico de siete días no disponible para "+p.name+".";wn.textContent="No se reemplazan datos ausentes por valores simulados. Detalle: "+e.message}
  const sb=$("#oaf-ux55-season-body"),sc=$("#oaf-ux55-season-chart"),sn=$("#oaf-ux55-season-note");sb.textContent="Consultando ECMWF SEAS5 para "+p.name+"…";sc.replaceChildren();
  try{
   const months=monthKeys(),q=new URLSearchParams({latitude:p.lat,longitude:p.lon,models:"ecmwf_seas5_ensemble_mean",hourly:"precipitation",forecast_days:"215",timezone:"America/Lima",precipitation_unit:"mm"});
   const d=await fetchJSON("https://seasonal-api.open-meteo.com/v1/seasonal?"+q);
   const h=d.hourly;if(!Array.isArray(h?.time)||!Array.isArray(h?.precipitation)||h.time.length!==h.precipitation.length)throw Error("Serie estacional incompatible");
   const groups=new Map();for(let i=0;i<h.time.length;i++){const t=h.time[i];if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(t))continue;const m=t.slice(0,7);if(!months.includes(m))continue;if(!groups.has(m))groups.set(m,[]);groups.get(m).push({time:t,rain:h.precipitation[i]})}
   const vals=months.map(m=>{const a=groups.get(m)||[],parts=m.split("-").map(Number),days=new Date(Date.UTC(parts[0],parts[1],0)).getUTCDate(),perDay=new Map();a.forEach(x=>perDay.set(x.time.slice(0,10),(perDay.get(x.time.slice(0,10))||0)+1));const complete=a.length===days*4&&perDay.size===days&&[...perDay.values()].every(n=>n===4)&&a.every(x=>Number.isFinite(x.rain)&&x.rain>=0);return {month:m,value:complete?a.reduce((s,x)=>s+x.rain,0):NaN,complete}}).filter(x=>x.complete);
   if(!vals.length)throw Error("No hay meses completos para resumir");
   drawBars(sc,vals.map(x=>({label:x.month.slice(5)+"/"+x.month.slice(0,4).slice(2),value:x.value})),"mm/mes","#8069b6");
   sb.textContent=p.name+" · "+vals[0].month+" a "+vals.at(-1).month+" · "+vals.length+" meses completos.";
   const sum=vals.reduce((s,x)=>s+x.value,0),avg=sum/vals.length;
   sn.textContent="Interpretación: el escenario de ensamble acumula "+fmt(sum)+" mm en los meses completos disponibles (media "+fmt(avg)+" mm/mes). Es una perspectiva estacional de escala aproximada de 36 km, no un pronóstico puntual ni una garantía de lluvia para una parcela. Contrastar con ENFEN, SENAMHI y la evolución de los pronósticos de corto plazo. Fuente: Open-Meteo Seasonal API · ECMWF SEAS5 (51 miembros; media de ensamble).";
  }catch(e){sb.textContent="La perspectiva estacional no está disponible para "+p.name+".";sn.textContent="No se presentan meses parciales como si fueran acumulados completos. Detalle: "+e.message}
 };
 load();$("#oaf-home-location")?.addEventListener("change",load);document.addEventListener("oaf:area-update",e=>{if(e.detail?.scope==="inicio")load()});
 go(0);start();return true;
}
function historicalPanel(){
 const climate=$("#clima");if(!climate||$("#oaf-ux55-historical"))return;
 const panel=el("section","oaf-ux55-historical");panel.id="oaf-ux55-historical";
 panel.append(el("small","oaf-ux55-eyebrow","SERIES HISTÓRICAS · 1996–2025"),el("h2","","Evolución anual de temperatura, precipitación y radiación solar"),el("p","","Comparación anual derivada de ERA5 para las localidades del observatorio. Se exige disponibilidad de los 12 meses; los años incompletos se muestran sin barra."));
 const controls=el("div","oaf-ux55-controls");
 const city=el("select");city.id="oaf-ux55-hist-city";Object.keys(cities).forEach(n=>{const o=el("option","",n);o.value=n;city.append(o)});
 const variable=el("select");variable.id="oaf-ux55-hist-variable";[["temperatura_c","Temperatura media (°C)"],["precipitacion_mm","Precipitación acumulada (mm/año)"],["radiacion_mj_m2","Radiación solar acumulada (MJ/m²/año)"]].forEach(([v,t])=>{const o=el("option","",t);o.value=v;variable.append(o)});
 controls.append(el("label","","Localidad"),city,el("label","","Variable"),variable);panel.append(controls);
 const chart=el("div","oaf-ux55-hist-chart");chart.id="oaf-ux55-hist-chart";panel.append(chart);
 const status=el("p","oaf-ux55-hist-note","Cargando serie histórica ERA5…");status.id="oaf-ux55-hist-status";panel.append(status);
 const anchor=$("#oaf-menu-clima");if(anchor)anchor.after(panel);else climate.querySelector(".viewhead")?.after(panel);
 fetch("datos/lambayeque_mensual_era5_8d.csv",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.text()}).then(raw=>{
  const lines=raw.trim().split(/\r?\n/),head=lines.shift().split(","),records=lines.map(line=>Object.fromEntries(head.map((k,i)=>[k,line.split(",")[i]])));
  const draw=()=>{const name=city.value,key=variable.value,rows=records.filter(r=>r.localidad===name&&/^\d{4}-\d{2}$/.test(r.mes)),by=new Map();rows.forEach(r=>{const y=r.mes.slice(0,4);if(!by.has(y))by.set(y,[]);by.get(y).push(Number(r[key]))});
   const annual=Array.from({length:30},(_,i)=>{const y=String(1996+i),a=by.get(y)||[],ok=a.length===12&&a.every(Number.isFinite);return {label:y.slice(2),value:ok?(key==="temperatura_c"?a.reduce((s,x)=>s+x,0)/12:a.reduce((s,x)=>s+x,0)):NaN}});
   const valid=annual.filter(x=>Number.isFinite(x.value));drawBars(chart,annual,"",key==="temperatura_c"?"#258b74":key==="precipitacion_mm"?"#278eb8":"#c58a42");
   status.textContent=name+" · "+valid.length+"/30 años completos · "+({temperatura_c:"media anual de 12 medias mensuales",precipitacion_mm:"suma de 12 acumulados mensuales",radiacion_mj_m2:"suma de 12 acumulados mensuales"}[key])+". Fuente: ERA5, archivo mensual OAF. No equivale a medición de estación.";
  };city.addEventListener("change",draw);variable.addEventListener("change",draw);draw();
 }).catch(e=>{chart.textContent="No se pudo cargar el histórico: "+e.message;status.textContent="Se conservan las fuentes y datos originales en Metadatos y trazabilidad."});
}
function scienceNote(){
 const home=$("#inicio");if(!home||$("#oaf-ux55-science"))return;
 const box=el("section","oaf-ux55-science");box.id="oaf-ux55-science";
 box.append(el("small","oaf-ux55-eyebrow","CIENCIA Y DATOS DEL OBSERVATORIO AGROCLIMÁTICO Y FITOSANITARIO"),el("h2","","Información confiable para mejores decisiones agrícolas"),el("p","","Esta plataforma integra datos meteorológicos y climáticos de fuentes reconocidas, información satelital y de reanálisis, registros de estaciones disponibles, cartografía geoespacial y análisis desarrollados por el Observatorio. Cada producto debe conservar su fuente, periodo, resolución, unidades y limitaciones para que el usuario sepa qué está observando."),el("p","","El trabajo con ciencia de datos y modelos de aprendizaje automático —incluido Random Forest— permite explorar patrones, evaluar escenarios y comparar resultados con referencias independientes. Los modelos experimentales se diferencian de los pronósticos oficiales y solo se presentan como operativos cuando su desempeño ha sido validado. El propósito es acercar información útil, comprensible y trazable a pequeños agricultores, productores, técnicos y ciudadanos interesados, para apoyar decisiones oportunas sobre sus cultivos, el agua y los riesgos climáticos."));
 const hero=home.querySelector(".oaf-ux14-home-hero")||home.querySelector(".oaf-hero-2026");if(hero)hero.after(box);else home.prepend(box);
}
function trimStations(){
 const list=$("#oaf-stations-list"),table=list?.querySelector("table");if(!table)return;
 table.querySelectorAll("tr").forEach(row=>{while(row.children.length>3)row.lastElementChild.remove()});
}
function removeNoise(){
 const scopes=[$("#oaf-ux29-territory"),$("#oaf-ux29-scenario")].filter(Boolean);
 for(const root of scopes){
  root.querySelectorAll("#oaf-area-point-details-territorio,#oaf-area-point-details-escenarios,.oaf-area-point-details").forEach(node=>{node.hidden=true;node.setAttribute("aria-hidden","true");node.style.display="none"});
  root.querySelectorAll("#oaf-ux33-status,#oaf-ux32-map-status,.oaf-ux33-status").forEach(node=>node.remove());
  for(const node of [...root.querySelectorAll("h1,h2,h3,h4,p,small,strong,span,div,section,article")]){
   if(node.children.length&&!node.matches(".oaf-ux29-stat,.oaf-ux29-metric,.oaf-ux29-kpi"))continue;
   const t=(node.textContent||"").replace(/\s+/g," ").trim().toLowerCase();
   if(t==="diagnóstico espacial del punto"){const target=node.closest(".oaf-ux29-diagnosis-item,.oaf-ux29-stat,.oaf-ux29-metric,.oaf-ux29-kpi")||node;target.hidden=true;target.setAttribute("aria-hidden","true");target.style.display="none"}
   else if(t.includes("138 registros")||t.includes("148 puntos igm")){const target=node.closest(".oaf-ux29-stat,.oaf-ux29-metric,.oaf-ux29-kpi,.oaf-ux33-status")||node;if(target!==root)target.remove()}
  }
 }
}
function reinforceMaps(){
 if(mapsWired)return;mapsWired=true;
 const redrawTerritory=()=>requestAnimationFrame(()=>window.oafUx30RequestDraw?.());
 const redrawScenario=()=>requestAnimationFrame(()=>{window.oafUx35Render?.();window.oafUx35Diagnosis?.()});
 document.addEventListener("change",e=>{
  const t=e.target;
  if(t?.closest("#oaf-ux29-territory")&&(t.matches("[data-ux30-layer],#oaf-ux26-prov,#oaf-ux26-dist,#oaf-ux26-basin,select,input[type=checkbox]")))redrawTerritory();
  if(t?.closest("#oaf-ux29-scenario")&&(t.matches("[data-ux35-key],#oaf-ux35-histyear,#oaf-ux35-horizon,#oaf-ux35-threshold,[data-ux35-filter]")||t.dataset.ux35Filter))redrawScenario();
 });
 window.addEventListener("oaf:geodata",()=>{redrawTerritory();redrawScenario()});
 document.addEventListener("oaf:area-update",e=>{if(e.detail?.scope==="territorio")redrawTerritory();if(e.detail?.scope==="escenarios")redrawScenario()});
 let tries=0;const wait=()=>{if(window.oafUx30RequestDraw||window.oafUx35Render){redrawTerritory();redrawScenario();return}if(++tries<40)setTimeout(wait,250)};wait();
}
function init(){let n=0;const probe=()=>{const ready=buildCarousel();historicalPanel();scienceNote();trimStations();removeNoise();reinforceMaps();if(!ready&&n++<80)setTimeout(probe,250)};probe();const observer=new MutationObserver(()=>{trimStations();removeNoise()});observer.observe(document.body,{childList:true,subtree:true});}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();