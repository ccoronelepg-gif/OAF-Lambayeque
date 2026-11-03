/* OAF Lambayeque UX42 · Carrusel informativo institucional, 15 s.
 * ENFEN oficial ≠ pronóstico meteorológico externo ≠ RF experimental.
 * Cambio automático pausado cuando el usuario interactúa y con pestaña oculta.
 */
(()=>{"use strict";
const $=id=>document.getElementById(id),places={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const el=(tag,cl,text)=>{const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=text;return x;};
const fmt=(n,d=1)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let started=false,index=0,timer=null,seq=0,monthlySeq=0,paused=false;
const slides=[],buttons=[];
function go(i){
 if(!slides.length)return;index=(i+slides.length)%slides.length;
 slides.forEach((s,j)=>{s.hidden=j!==index;s.setAttribute("aria-hidden",String(j!==index));});
 buttons.forEach((b,j)=>{b.setAttribute("aria-current",String(j===index));});
}
function stop(){if(timer)clearInterval(timer);timer=null;}
function start(){
 stop();if(paused||document.hidden||window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches)return;
 timer=setInterval(()=>{if(!paused&&!document.hidden)go(index+1)},15000);
}
function location(){
 const p=window.OAFTerritory?.getActivePoint?.("inicio");
 if(p)return {name:p.name,lat:p.lat,lon:p.lon,custom:true};
 const name=$("oaf-home-location")?.value;
 if(places[name])return {name,lat:places[name][0],lon:places[name][1],custom:false};
 return {name:"Chiclayo",lat:places.Chiclayo[0],lon:places.Chiclayo[1],custom:false};
}
function nextFullMonths(){const parts=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Lima",year:"numeric",month:"2-digit"}).formatToParts(new Date());let y=Number(parts.find(x=>x.type==="year")?.value),m=Number(parts.find(x=>x.type==="month")?.value)+1;if(m===13){m=1;y++}return Array.from({length:6},()=>{const key=y+"-"+String(m).padStart(2,"0");m++;if(m===13){m=1;y++}return key})}
function completeSeasonalRain(hourly,months){if(!Array.isArray(hourly?.time)||!Array.isArray(hourly?.precipitation)||hourly.time.length!==hourly.precipitation.length)throw Error("Serie estacional incompleta");const groups=new Map(),seen=new Set();for(let i=0;i<hourly.time.length;i++){const time=hourly.time[i];if(typeof time!=="string"||!/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$/.test(time))throw Error("Fecha estacional inválida");if(seen.has(time))throw Error("Horas estacionales duplicadas");seen.add(time);const month=time.slice(0,7);if(!months.includes(month))continue;if(!groups.has(month))groups.set(month,[]);groups.get(month).push({time,rain:hourly.precipitation[i]})}return months.map(month=>{const rows=groups.get(month)||[],parts=month.split("-").map(Number),days=new Date(Date.UTC(parts[0],parts[1],0)).getUTCDate(),perDay=new Map();for(const row of rows){const day=row.time.slice(0,10);perDay.set(day,(perDay.get(day)||0)+1)}const complete=rows.length===days*4&&perDay.size===days&&Array.from(perDay.values()).every(n=>n===4)&&rows.every(row=>Number.isFinite(row.rain)&&row.rain>=0);return {month,value:complete?rows.reduce((sum,row)=>sum+row.rain,0):NaN,complete}})}
async function monthly(){const p=location(),body=$("oaf-ux42-month-body"),plot=$("oaf-ux42-month-plot");if(!body||!plot)return;const request=++monthlySeq,months=nextFullMonths();body.textContent="Consultando ECMWF SEAS5 para seis meses completos en "+p.name+"…";plot.replaceChildren();try{const params=new URLSearchParams({latitude:String(p.lat),longitude:String(p.lon),models:"ecmwf_seas5_ensemble_mean",hourly:"precipitation,temperature_2m",forecast_days:"217",timezone:"America/Lima",precipitation_unit:"mm"}),response=await fetch("https://seasonal-api.open-meteo.com/v1/seasonal?"+params,{cache:"no-store"});if(!response.ok)throw Error("HTTP "+response.status);const data=await response.json();if(data.error||!data.hourly)throw Error(data.reason||"No hay serie horaria estacional");if(data.hourly_units?.precipitation&&data.hourly_units.precipitation!=="mm")throw Error("Unidad de precipitación distinta de mm");const values=completeSeasonalRain(data.hourly,months).filter(row=>row.complete&&Number.isFinite(row.value));if(request!==monthlySeq)return;if(!values.length)throw Error("No se encontraron meses completos con cuatro intervalos diarios de seis horas");smallBars(plot,values.map(row=>({label:row.month.slice(5,7)+"/"+row.month.slice(2,4),n:row.value})),"mm");const total=values.reduce((sum,row)=>sum+row.value,0);body.textContent=values[0].month+" – "+values.at(-1).month+" · "+p.name+" · precipitación acumulada del escenario: "+fmt(total)+" mm.";const note=$("oaf-ux42-month-note");if(note)note.textContent=values.length+"/6 meses completos. Fuente: Open-Meteo Seasonal API · ECMWF SEAS5 (media de ensamble); lluvia mensual=sumatoria de intervalos de 6 h. Escenario externo de escala regional, sin corrección local para parcela y distinto del Random Forest OAF."}catch(error){if(request===monthlySeq){body.textContent="La perspectiva estacional no está disponible para "+p.name+" en esta consulta.";plot.textContent="No se dibujan meses parciales ni cifras sin cobertura completa.";const note=$("oaf-ux42-month-note");if(note)note.textContent="Fuente prevista: Open-Meteo Seasonal API · ECMWF SEAS5. Error: "+error.message}}}
function construct(){
 const side=$("inicio")?.querySelector(".oaf-ux14-home-side");
 const official=side?.querySelector(".oaf-ux14-nino");if(!official||started)return false;
 started=true;side.classList.add("oaf-ux42-carousel");
 official.id="oaf-ux42-slide-official";official.classList.add("oaf-ux42-slide");slides.push(official);
 const officialDate=el("p","oaf-ux42-official-meta","ENFEN · Comunicado Oficial 19-2026 · 30/10/2026");
 const interpretation=official.querySelector("#oaf-ux15-enfen-exp");
 if(interpretation)interpretation.after(officialDate);else official.prepend(officialDate);
 for(const [id,kicker,heading,bodyId,plotId,noteId,note] of [
  ["week","PRÓXIMOS 7 DÍAS","Pronóstico meteorológico", "oaf-ux42-week-body","oaf-ux42-week-plot","oaf-ux42-week-note","Precipitación diaria (mm). Fuente: Open-Meteo Forecast API."],
  ["month","PRÓXIMOS SEIS MESES COMPLETOS","Perspectiva estacional de precipitación","oaf-ux42-month-body","oaf-ux42-month-plot","oaf-ux42-month-note","Fuente: Open-Meteo Seasonal API · ECMWF SEAS5."]]){
  const card=el("article","oaf-ux14-tile oaf-ux42-slide");card.id="oaf-ux42-slide-"+id;card.hidden=true;
  card.append(el("small",null,kicker),el("h2",null,heading),el("p","oaf-ux42-highlight",""));
  card.lastChild.id=bodyId;
  const chart=el("div","oaf-ux42-minichart");chart.id=plotId;chart.setAttribute("role","img");chart.setAttribute("aria-label","Gráfico de precipitación por fecha");card.append(chart);
  const noteEl=el("p","oaf-ux42-note",note);noteEl.id=noteId;card.append(noteEl);
  const a=el("a",null,"Ver análisis y gráficos completos ↗");a.href="#autor";card.append(a);
  side.append(card);slides.push(card);
 }
 const controls=el("nav","oaf-ux42-controls");controls.setAttribute("aria-label","Cambiar resumen agroclimático");
 const back=el("button",null,"‹");back.type="button";back.setAttribute("aria-label","Anterior");back.addEventListener("click",()=>{go(index-1);start()});controls.append(back);
 for(let i=0;i<slides.length;i++){
  const b=el("button","oaf-ux42-dot",String(i+1));b.type="button";b.setAttribute("aria-label",["ENFEN oficial","Próximos 7 días","Horizonte mensual"][i]);
  b.addEventListener("click",()=>{go(i);start()});buttons.push(b);controls.append(b);
 }
 const next=el("button",null,"›");next.type="button";next.setAttribute("aria-label","Siguiente");next.addEventListener("click",()=>{go(index+1);start()});controls.append(next);
 side.append(controls);side.addEventListener("mouseenter",()=>{paused=true;stop()});
 side.addEventListener("mouseleave",()=>{paused=false;start()});
 side.addEventListener("focusin",()=>{paused=true;stop()});
 side.addEventListener("focusout",e=>{if(!side.contains(e.relatedTarget)){paused=false;start()}});
 document.addEventListener("visibilitychange",start);
 $("oaf-home-location")?.addEventListener("change",()=>{weather();monthly();const name=$("oaf-home-location")?.value;if(places[name])document.dispatchEvent(new CustomEvent("oaf:localidad",{detail:{localidad:name,source:"oaf-home-location"}}))});
 document.addEventListener("oaf:area-update",e=>{if(e.detail?.scope==="inicio"){weather();monthly()}});
 go(0);weather();monthly();start();return true;
}
function init(){let retries=0;const probe=()=>{if(!construct()&&++retries<45)setTimeout(probe,250)};probe()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();