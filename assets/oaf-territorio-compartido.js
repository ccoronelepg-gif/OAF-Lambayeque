/* OAF Lambayeque · ubicaciones autónomas por pestaña · 27/10/2026.
 * WGS84; sin pronóstico semanal duplicado; nunca extrapolar mapas a una parcela.
 */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const cityNames=["Chiclayo","Jayanca","Motupe","Olmos"];
const cities={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const KEY="oaf-area-autonoma-20261027-";
const titles={inicio:"Mi zona productora",clima:"Mi área productora · clima regional",territorio:"Mi área productora · territorio y riesgos",predicciones:"Mi área productora · análisis climático",escenarios:"Mi área productora · escenarios de riesgo",cultivos:"Mi zona productora · cultivos y sanidad"};
const modes=["inicio","clima","territorio","predicciones","escenarios","cultivos"];
const states={},els={},revisions={},active={};
function valid(lat,lon){
 if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)throw Error("Latitud o longitud inválida.");
 if(lat< -7.3||lat> -5.1||lon< -80.8||lon> -79)throw Error("El punto queda fuera del ámbito geográfico del visor de Lambayeque.");
 return {lat,lon};
}
function utm(e,n,z,h){
 if(!Number.isFinite(e)||!Number.isFinite(n)||!Number.isInteger(z)||z<1||z>60||e<100000||e>900000||n<0||n>10000000||!["N","S"].includes(h))throw Error("Revisa Este, Norte, zona UTM y hemisferio.");
 const a=6378137,ec=.0066943799901413165,k=.9996,ep=ec/(1-ec),x=e-500000,y=n-(h==="S"?10000000:0),mu=(y/k)/(a*(1-ec/4-3*ec*ec/64-5*ec**3/256)),e1=(1-Math.sqrt(1-ec))/(1+Math.sqrt(1-ec));
 const p=mu+(3*e1/2-27*e1**3/32)*Math.sin(2*mu)+(21*e1**2/16-55*e1**4/32)*Math.sin(4*mu)+151*e1**3/96*Math.sin(6*mu)+1097*e1**4/512*Math.sin(8*mu);
 const N=a/Math.sqrt(1-ec*Math.sin(p)**2),T=Math.tan(p)**2,C=ep*Math.cos(p)**2,R=a*(1-ec)/(1-ec*Math.sin(p)**2)**1.5,D=x/(N*k);
 const lat=p-N*Math.tan(p)/R*(D**2/2-(5+3*T+10*C-4*C*C-9*ep)*D**4/24+(61+90*T+298*C+45*T*T-252*ep-3*C*C)*D**6/720);
 const lon=(D-(1+2*T+C)*D**3/6+(5-2*C+28*T-3*C*C+8*ep+24*T*T)*D**5/120)/Math.cos(p);
 return [lat*180/Math.PI,(z-1)*6-177+lon*180/Math.PI];
}
function save(k){try{sessionStorage.setItem(KEY+k,JSON.stringify(states[k]||null));}catch(_){}}
function load(k){try{const x=JSON.parse(sessionStorage.getItem(KEY+k));if(x&&typeof x.name==="string"){valid(x.lat,x.lon);return {lat:x.lat,lon:x.lon,name:x.name.slice(0,80)};}}catch(_){}return null;}
function fmt(v,d=1){return typeof v==="number"&&Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:d,minimumFractionDigits:d}):"—";}
function notice(k,msg){const v=els[k]?.querySelector(".oaf-area-message");if(v)v.textContent=msg;}
function mapURL(p){const params=new URLSearchParams({bbox:[p.lon-.027,p.lat-.020,p.lon+.027,p.lat+.020].join(","),layer:"mapnik",marker:p.lat+","+p.lon});return "https://www.openstreetmap.org/export/embed.html?"+params;}
function make(k){
 const wrap=document.createElement("section");wrap.className="oaf-area-local";wrap.id="oaf-area-"+k;
 wrap.setAttribute("aria-label",titles[k]);
 wrap.innerHTML='<details class="oaf-area-accordion"><summary><strong>'+titles[k]+'</strong><span> · Coordenadas geográficas o UTM (WGS84)</span></summary>'+
 '<form class="oaf-area-form"><div class="oaf-area-fields"><label>Nombre de la parcela o fundo<input name="name" maxlength="80" placeholder="Ej.: Fundo El Mango" autocomplete="off"></label>'+
 '<label>Tipo de coordenadas<select name="format"><option value="geo">Geográficas · latitud / longitud</option><option value="utm">UTM WGS84 · metros</option></select></label></div>'+
 '<div class="oaf-area-fields" data-fields="geo"><label>Latitud decimal<input name="lat" inputmode="decimal" placeholder="-6.15083"></label><label>Longitud decimal<input name="lon" inputmode="decimal" placeholder="-79.7142"></label></div>'+
 '<div class="oaf-area-fields" data-fields="utm" hidden><label>Este (m)<input name="east" inputmode="decimal" placeholder="640000"></label><label>Norte (m)<input name="north" inputmode="decimal" placeholder="9310000"></label><label>Zona UTM<input name="zone" type="number" min="1" max="60" value="17"></label><label>Hemisferio<select name="hemi"><option value="S">Sur</option><option value="N">Norte</option></select></label></div>'+
 '<div class="oaf-area-actions"><button type="submit" class="btn dark">Consultar mi área</button><button type="button" class="btn oaf-area-clear">Quitar ubicación</button></div>'+
 '<p class="oaf-area-message" role="status" aria-live="polite"></p></form>'+
 '<p class="oaf-area-help">La coordenada identifica un <strong>punto</strong>, no el polígono ni la extensión de la parcela. Cada pestaña conserva su propia ubicación durante esta sesión. Solo se comparan capas cuyos servicios responden.</p></details>'+
 '<div class="oaf-area-output" hidden><div class="oaf-area-heading" role="status"></div><iframe class="oaf-area-preview" title="Mapa de la ubicación consultada" loading="lazy" referrerpolicy="no-referrer"></iframe><div class="oaf-area-data" aria-live="polite"></div></div>';
 els[k]=wrap;revisions[k]=0;
 const f=wrap.querySelector("form"),field=n=>f.elements.namedItem(n);
 const change=()=>{const isUtm=field("format").value==="utm";wrap.querySelector('[data-fields="geo"]').hidden=isUtm;wrap.querySelector('[data-fields="utm"]').hidden=!isUtm;};
 field("format").addEventListener("change",change);
 f.addEventListener("submit",e=>{
  e.preventDefault();
  try{
   const num=n=>{const s=String(field(n).value||"").trim().replace(",",".");return s===""?NaN:Number(s);};
   const v=field("format").value==="utm"?utm(num("east"),num("north"),num("zone"),field("hemi").value):[num("lat"),num("lon")];
   const p=valid(v[0],v[1]);p.name=String(field("name").value||titles[k]).trim().slice(0,80)||titles[k];
   states[k]=p;active[k]=true;save(k);notice(k,"Coordenadas registradas en esta pestaña.");show(k);
   document.dispatchEvent(new CustomEvent("oaf:area-update",{detail:{scope:k,point:{...p},active:true}}));
  }catch(err){notice(k,err.message);}
 });
 wrap.querySelector(".oaf-area-clear").addEventListener("click",()=>{
  states[k]=null;active[k]=false;save(k);revisions[k]++;
  wrap.querySelector(".oaf-area-output").hidden=true;
  notice(k,"Ubicación particular desactivada únicamente en esta pestaña.");
  document.dispatchEvent(new CustomEvent("oaf:area-update",{detail:{scope:k,point:null,active:false}}));
  markers(); 
 });
 const previous=load(k);active[k]=Boolean(previous);if(previous){states[k]=previous;field("name").value=previous.name;field("lat").value=previous.lat;field("lon").value=previous.lon;}
 return wrap;
}
function show(k){
 const p=states[k],wrap=els[k];if(!wrap||!p)return;
 const out=wrap.querySelector(".oaf-area-output");
 if(!active[k]){out.hidden=true;return;}
 out.hidden=false;wrap.querySelector(".oaf-area-heading").textContent=p.name+" · "+p.lat.toFixed(5)+", "+p.lon.toFixed(5)+" · WGS84";
 const frame=wrap.querySelector(".oaf-area-preview");const url=mapURL(p);if(frame.getAttribute("src")!==url)frame.src=url;
 const data=wrap.querySelector(".oaf-area-data");
 data.textContent=(k==="inicio")?"Ubicación de referencia para los indicadores actuales, sin pronóstico semanal duplicado.":
 (k==="clima"||k==="predicciones"||k==="cultivos")?"Los resultados de esta coordenada se presentan en el visor de análisis de esta pestaña.":
 "Consultando las capas geográficas para el punto…";
 markers();
 if((k==="territorio"||k==="escenarios")&&!wrap.querySelector(".oaf-area-focus")){const button=document.createElement("button");button.type="button";button.className="btn oaf-area-focus";button.textContent="Enfocar mi punto en el visor";button.addEventListener("click",()=>focusMap(k));wrap.querySelector(".oaf-area-heading").after(button);}
 const seq=++revisions[k];if(k==="inicio")return;
 if(k==="territorio"||k==="escenarios")checkRisk(k,p,seq);
 else if(k!=="inicio")window.oafAreaUX38?.update?.(k,p);
}
async function json(u){
 const ctl=new AbortController(),timeout=setTimeout(()=>ctl.abort(),15000);
 try{const r=await fetch(u,{cache:"no-store",signal:ctl.signal});if(!r.ok)throw Error("HTTP "+r.status);const j=await r.json();if(j.error)throw Error(j.error.message||"Servicio no disponible");return j;}
 finally{clearTimeout(timeout);}
}
function focusMap(k){
 const p=states[k];if(!p)return;
 const id=k==="territorio"?"oaf-ux24-region-map":"oaf-ux29-forecast-map";const svg=$(id);
 const scene=k==="territorio"?window.oafUx30Context?.()?.scene:window.oafUx29ScenarioApi?.get?.()?.scene;
 if(!svg||!scene?.bounds)return;
 const x=scene.x(p.lon),y=scene.y(p.lat);
 if(!Number.isFinite(x)||!Number.isFinite(y))return;
 const w=230,h=112;
 svg.setAttribute("viewBox",Math.max(0,Math.min(700-w,x-w/2))+" "+Math.max(0,Math.min((k==="escenarios"?380:340)-h,y-h/2))+" "+w+" "+h);
 svg.scrollIntoView({behavior:"smooth",block:"center"});
}
async function current(k,p,seq){
 const data=els[k].querySelector(".oaf-area-data");
 try{
  const url="https://api.open-meteo.com/v1/forecast?"+new URLSearchParams({latitude:String(p.lat),longitude:String(p.lon),timezone:"America/Lima",forecast_days:k==="predicciones"?"3":"1",current:"temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",...(k==="predicciones"?{daily:"temperature_2m_max,precipitation_sum"}:{})});
  const j=await json(url);if(seq!==revisions[k])return;
  const v=j.current;if(!v||!Number.isFinite(v.temperature_2m))throw Error("Sin valores meteorológicos completos.");
  const t=v.temperature_2m,rh=v.relative_humidity_2m,vpd=Number.isFinite(rh)?Math.max(0,.6108*Math.exp(17.27*t/(t+237.3))*(1-rh/100)):NaN;
  data.replaceChildren();
  const h=document.createElement("p");h.textContent="Open-Meteo · condiciones modeladas a "+(v.time||"fecha no disponible")+" (hora local).";data.append(h);
  const list=document.createElement("p");list.textContent="Temperatura: "+fmt(t)+" °C · Humedad relativa: "+fmt(rh,0)+" % · Lluvia actual: "+fmt(v.precipitation)+" mm · Viento: "+fmt(v.wind_speed_10m)+" km/h · VPD calculado: "+fmt(vpd,2)+" kPa.";data.append(list);
  const caveat=document.createElement("p");caveat.className="oaf-area-limite";caveat.textContent=k==="cultivos"?
   "Estos indicadores describen condiciones ambientales, no incidencia de plagas, presencia de patógenos ni tratamiento recomendado. Los modelos históricos por localidad no se recalculan automáticamente para una parcela.":
   "Consulta puntual modelada; no equivale a registro en parcela ni a validación de un modelo predictivo OAF.";
  data.append(caveat);
 }catch(e){if(seq===revisions[k])data.textContent="No se pudo consultar la coordenada: "+e.message+" No se sustituye por datos de otra localidad.";}
}
async function archive(k,p,seq){
 const data=els[k].querySelector(".oaf-area-data");
 const now=new Date(),end=new Date(now);end.setUTCDate(end.getUTCDate()-6);const start=new Date(end);start.setUTCFullYear(start.getUTCFullYear()-1);start.setUTCDate(start.getUTCDate()+1);
 const iso=d=>d.toISOString().slice(0,10);
 try{
  const url="https://archive-api.open-meteo.com/v1/archive?"+new URLSearchParams({latitude:String(p.lat),longitude:String(p.lon),start_date:iso(start),end_date:iso(end),daily:"temperature_2m_mean,precipitation_sum",timezone:"America/Lima"});
  const j=await json(url);if(seq!==revisions[k])return;const d=j.daily;if(!d||!Array.isArray(d.time))throw Error("Archivo no disponible.");
  const months=new Map();d.time.forEach((day,i)=>{
   const key=day.slice(0,7);let v=months.get(key);if(!v){v={t:0,tc:0,r:0,rc:0};months.set(key,v);}
   const t=d.temperature_2m_mean?.[i],rain=d.precipitation_sum?.[i];
   if(Number.isFinite(t)){v.t+=t;v.tc++;}if(Number.isFinite(rain)){v.r+=rain;v.rc++;}
  });
  data.replaceChildren();
  const title=document.createElement("p");title.textContent="Serie histórica puntual · últimos 12 meses disponibles · reanálisis Open-Meteo Archive ("+iso(start)+" a "+iso(end)+").";data.append(title);
  const sc=document.createElement("div");sc.className="oaf-area-scroll";
  const table=document.createElement("table"),head=document.createElement("thead");head.innerHTML="<tr><th>Mes</th><th>Temperatura media</th><th>Precipitación acumulada</th></tr>";table.append(head);
  const tbody=document.createElement("tbody");for(const [m,v] of months){const tr=document.createElement("tr");for(const str of [m,v.tc?fmt(v.t/v.tc)+" °C":"Sin datos",v.rc?fmt(v.r)+" mm":"Sin datos"]){const td=document.createElement("td");td.textContent=str;tr.append(td);}tbody.append(tr);}
  table.append(tbody);sc.append(table);data.append(sc);
  const caveat=document.createElement("p");caveat.className="oaf-area-limite";caveat.textContent="Serie específica de la coordenada consultada. No reemplaza las series originales ERA5-Land/SENAMHI 1996–2025 ni las convierte en datos observados de finca. Meses parciales posibles según la ventana disponible.";data.append(caveat);
 }catch(e){if(seq===revisions[k])data.textContent="No hay serie histórica verificable para este punto: "+e.message+" Se mantienen, identificadas por separado, las series históricas regionales.";}
}
async function checkRisk(k,p,seq){
 const data=els[k].querySelector(".oaf-area-data");data.replaceChildren();
 const info=document.createElement("p");info.textContent="Consulta de intersección espacial del punto con cartografía oficial. La coincidencia no expresa magnitud, probabilidad de ocurrencia ni hectáreas afectadas.";data.append(info);
 const sources=[
  ["Susceptibilidad a inundaciones · CENEPRED","https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5010502/query"],
  ["Susceptibilidad a movimientos en masa · CENEPRED","https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5090022/query"],
  ["Susceptibilidad fluvial · INGEMMET","https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0/query"]
 ];
 const results=await Promise.all(sources.map(async ([name,endpoint])=>{
  try{
   const query=new URLSearchParams({geometry:JSON.stringify({x:p.lon,y:p.lat,spatialReference:{wkid:4326}}),geometryType:"esriGeometryPoint",spatialRel:"esriSpatialRelIntersects",inSR:"4326",outFields:"*",returnGeometry:"false",f:"json"});
   let features;
   try{const j=await json(endpoint+"?"+query);if(!Array.isArray(j.features))throw Error("consulta vectorial no disponible");features=j.features;}
   catch(first){
    const base=endpoint.replace(/\/\d+\/query$/,""),layer=endpoint.match(/\/(\d+)\/query$/)?.[1];if(!layer)throw first;
    const b={minLon:p.lon-.04,minLat:p.lat-.04,maxLon:p.lon+.04,maxLat:p.lat+.04};
    const q=new URLSearchParams({geometry:JSON.stringify({x:p.lon,y:p.lat,spatialReference:{wkid:4326}}),geometryType:"esriGeometryPoint",sr:"4326",layers:"all:"+layer,tolerance:"2",mapExtent:[b.minLon,b.minLat,b.maxLon,b.maxLat].join(","),imageDisplay:"700,340,96",returnGeometry:"false",f:"json"});
    const other=await json(base+"/identify?"+q);if(!Array.isArray(other.results))throw first;
    features=other.results.map(x=>({attributes:x.attributes||{}}));
   }
   const attrs=features.slice(0,3).map(x=>Object.entries(x.attributes||{}).filter(([key,v])=>v!==null&&typeof v!=="object"&&/(nivel|suscept|grado|clase|tipo|desc|peligro)/i.test(key)).slice(0,2).map(([,v])=>String(v).slice(0,65)).join(" · ")).filter(Boolean);
   return [name,features.length?"Intersección con "+features.length+" entidad(es) cartográficas"+(attrs.length?" · "+attrs.join("; "):""):"Sin intersección reportada a la escala de este servicio; no descarta el peligro."];
  }catch(e){return [name,"No verificable: el geoservicio no respondió con una intersección válida."];}
 }));
 if(seq!==revisions[k])return;
 const ul=document.createElement("ul");for(const [name,msg] of results){const li=document.createElement("li");const strong=document.createElement("strong");strong.textContent=name+": ";li.append(strong,document.createTextNode(msg));ul.append(li);}data.append(ul);
 const tip=document.createElement("p");tip.className="oaf-area-limite";tip.textContent="Verifica escala, vigencia y leyenda oficial antes de decisiones productivas. Este visor consulta el punto introducido; para analizar toda la superficie de una parcela se requiere su polígono. Los otros mapas conservan su fuente y escala.";data.append(tip);
 markers();
}
function pin(svg,scene,p,id){
 if(!svg)return;
 const old=svg.querySelector("#"+id);
 if(!p){old?.remove();return;}
 if(old?.dataset?.key===p.lat+","+p.lon){if(svg.lastElementChild!==old)svg.append(old);return;}
 old?.remove();if(!scene||!scene.bounds)return;
 const b=scene.bounds;if(p.lon<b.minLon||p.lon>b.maxLon||p.lat<b.minLat||p.lat>b.maxLat)return;
 const x=typeof scene.x==="function"?scene.x(p.lon):700*(p.lon-b.minLon)/(b.maxLon-b.minLon);
 const y=typeof scene.y==="function"?scene.y(p.lat):340*(b.maxLat-p.lat)/(b.maxLat-b.minLat);
 if(!Number.isFinite(x)||!Number.isFinite(y))return;
 const NS="http://www.w3.org/2000/svg",g=document.createElementNS(NS,"g");g.id=id;g.dataset.key=p.lat+","+p.lon;g.setAttribute("pointer-events","none");
 const halo=document.createElementNS(NS,"circle");halo.setAttribute("cx",x);halo.setAttribute("cy",y);halo.setAttribute("r","9");halo.setAttribute("fill","#e64d64");halo.setAttribute("fill-opacity",".24");
 const dot=document.createElementNS(NS,"circle");dot.setAttribute("cx",x);dot.setAttribute("cy",y);dot.setAttribute("r","4.5");dot.setAttribute("fill","#bc2852");dot.setAttribute("stroke","#fff");dot.setAttribute("stroke-width","2");
 const title=document.createElementNS(NS,"title");title.textContent=p.name+" · ubicación proporcionada";g.append(halo,dot,title);svg.append(g);
}
function markers(){
 const territory=$("oaf-ux24-region-map"),sc=window.oafUx30Context?.()?.scene;
 pin(territory,sc,active.territorio?states.territorio:null,"oaf-area-pin-territorio");
 const scenario=$("oaf-ux29-forecast-map"),forecast=window.oafUx29ScenarioApi?.get?.()?.scene;
 pin(scenario,forecast,active.escenarios?states.escenarios:null,"oaf-area-pin-escenarios");
}
function observeMaps(){
 ["oaf-ux24-region-map","oaf-ux29-forecast-map"].forEach(id=>{
  const svg=$(id);if(!svg)return;
  const obs=new MutationObserver(()=>{if(id==="oaf-ux24-region-map")pin(svg,window.oafUx30Context?.()?.scene,active.territorio?states.territorio:null,"oaf-area-pin-territorio");else pin(svg,window.oafUx29ScenarioApi?.get?.()?.scene,active.escenarios?states.escenarios:null,"oaf-area-pin-escenarios");});
  obs.observe(svg,{childList:true});
 });
 window.addEventListener("oaf:geodata",markers);
}
function init(){
 const locations={
  inicio:()=>document.querySelector("#oaf-zone-primary .oaf-zone-picker")||document.querySelector("#oaf-zone-primary .oaf-location-panel"),
  clima:()=>$("oaf-history")?.querySelector(".oaf-filterline"),
  territorio:()=>$("oaf-ux29-territory")?.querySelector(".oaf-ux29-maphead")||$("oaf-ux29-territory")||document.querySelector("#oaf-territorio-riesgos .oaf-ux24-intro"),
  predicciones:()=>$("oaf-ux16-future-controls")||$("oaf-ux14-rf-mes"),
  escenarios:()=>$("oaf-ux29-scenario")?.querySelector(".oaf-ux29-maphead")||$("oaf-ux29-scenario")||document.querySelector("#oaf-escenarios-riesgo-agroclimatico .oaf-ux24-intro"),
  cultivos:()=>$("oaf-sm-localidad")?.closest(".oaf-ux11-controls")||$("oaf-sanidad-ux11")?.querySelector(".oaf-ux11-model")
 };
 for(const k of modes){
  const el=make(k);let trials=0;
  const locate=()=>{const anchor=locations[k]();if(anchor){anchor.after(el);if(states[k])show(k);}
    else if(++trials<30)setTimeout(locate,300);};
  locate();
 }
 const site=$("oaf-home-location");
 const custom=site?.querySelector('option[value="Mi zona productora"]');custom?.remove();
 site?.addEventListener("change",()=>{active.inicio=false;els.inicio?.querySelector(".oaf-area-output")?.setAttribute("hidden","");document.dispatchEvent(new CustomEvent("oaf:area-update",{detail:{scope:"inicio",point:null,active:false}}));},true);
 const city=$("oaf-hist-place");
 city?.addEventListener("change",()=>{active.clima=false;els.clima?.querySelector(".oaf-area-output")?.setAttribute("hidden","");window.oafAreaUX38?.restoreHistoric?.();});
 ["oaf-hist-year","oaf-hist-variable"].forEach(id=>$(id)?.addEventListener("change",()=>{if(active.clima&&states.clima)window.oafAreaUX38?.update?.("clima",states.clima);}));
 $("oaf-sm-localidad")?.addEventListener("change",()=>{if(active.cultivos){active.cultivos=false;els.cultivos?.querySelector(".oaf-area-output")?.setAttribute("hidden","");document.dispatchEvent(new CustomEvent("oaf:area-update",{detail:{scope:"cultivos",point:null,active:false}}));}},true);
 observeMaps();markers();
 document.addEventListener("oaf:area-update",e=>{if(["territorio","escenarios"].includes(e.detail?.scope))markers();});
 const weeklyTable=$("wx-days")?.closest(".scroller");if(weeklyTable)weeklyTable.hidden=true;
 const weeklyHeading=Array.from($("wx-data")?.querySelectorAll("h2")||[]).find(e=>/siete días/i.test(e.textContent));if(weeklyHeading)weeklyHeading.hidden=true;
 const css=document.createElement("style");css.textContent=
 '.oaf-area-local{border:1px solid #c9ded4;border-radius:13px;background:#f5faf7;padding:13px 16px;margin:12px 0 21px;max-width:100%;box-sizing:border-box}'+
 '#oaf-area-territorio,#oaf-area-escenarios{margin:10px 12px;position:relative;z-index:1}'+
 '.oaf-ux29-mapcolumn .oaf-area-accordion{background:#eff8f3;border-radius:9px}'+
 '.oaf-area-local summary{cursor:pointer;color:#165745;padding:4px 0;font-size:15px}'+
 '.oaf-area-local summary span{color:#536e64;font-weight:400;font-size:12px}'+
 '.oaf-area-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0}'+
 '.oaf-area-fields label{display:flex;flex-direction:column;gap:5px;font-weight:700;font-size:12px}'+
 '.oaf-area-fields input,.oaf-area-fields select{width:100%;padding:10px;border:1px solid #b8cec3;border-radius:8px;font:inherit;min-width:0;box-sizing:border-box}'+
 '.oaf-area-actions{display:flex;gap:9px;flex-wrap:wrap}.oaf-area-message{font-size:12px;font-weight:700;color:#275d4d;min-height:14px}'+
 '.oaf-area-help,.oaf-area-limite{font-size:12px;color:#506b62;line-height:1.65}'+
 '.oaf-area-heading{font-weight:800;color:#1d5c4c;margin:12px 0}'+
 '.oaf-area-preview{width:100%;height:230px;border:1px solid #cbddd5;border-radius:11px}'+
 '.oaf-area-local [hidden]{display:none!important}'+
 '#oaf-area-clima .oaf-area-data,#oaf-area-cultivos .oaf-area-data,#oaf-area-predicciones .oaf-area-data{display:none!important}'+
 '.oaf-area-scientific{border:1px solid #c9ded4;border-radius:12px;background:#f6faf8;margin:14px 0;padding:15px}'+
 '.oaf-area-scientific h3{color:#1a5d49;font-size:17px}.oaf-area-interpretacion{font-style:italic;font-weight:750;color:#185441;line-height:1.65}.oaf-area-metodo{font-size:12px;color:#567068;line-height:1.7}'+
 '#oaf-area-territorio .oaf-area-preview,#oaf-area-escenarios .oaf-area-preview{display:none!important}'+
 '.oaf-area-data{font-size:13px;line-height:1.65}.oaf-area-data li{margin:8px 0}'+
 '.oaf-area-scroll{overflow:auto}.oaf-area-scroll table{width:100%;min-width:440px;border-collapse:collapse}.oaf-area-scroll th,.oaf-area-scroll td{padding:8px;border-bottom:1px solid #d4e4dc;text-align:left}'+
 '#oaf-forecast-home,#oaf-ux9-pronostico,#oaf-ux14-rf-semana,#oaf-anomaly-panel,#clima .oaf-dashboard-grid{display:none!important}'+
 '.oaf-ux35-check:has([data-ux35-key="rain7"]),.oaf-ux35-field:has(#oaf-ux35-horizon),.oaf-ux35-field:has(#oaf-ux35-threshold){display:none!important}'+
 '@media(max-width:590px){.oaf-area-fields{grid-template-columns:1fr}.oaf-area-preview{height:205px}}';
 document.head.append(css);
}
window.OAFTerritory={utmToGeographic:utm,validatePoint:valid,getPoint:k=>states[k]?{...states[k]}:null,getActivePoint:k=>active[k]&&states[k]?{...states[k]}:null,
 setPoint:(k,point)=>{
  if(!modes.includes(k))throw Error("Pestaña no reconocida.");
  const v=valid(Number(point.lat),Number(point.lon));v.name=String(point.name||titles[k]).trim().slice(0,80)||titles[k];
  states[k]=v;active[k]=true;save(k);const f=els[k]?.querySelector("form");
  if(f){if(f.elements.namedItem("name"))f.elements.namedItem("name").value=v.name;f.elements.namedItem("format").value="geo";f.elements.namedItem("lat").value=v.lat;f.elements.namedItem("lon").value=v.lon;els[k].querySelector('[data-fields="geo"]').hidden=false;els[k].querySelector('[data-fields="utm"]').hidden=true;}
  if(els[k])show(k);
  document.dispatchEvent(new CustomEvent("oaf:area-update",{detail:{scope:k,point:{...v},active:true}}));
  return {...v};
 },getState:()=>Object.fromEntries(modes.map(k=>[k,states[k]||null]))};
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();