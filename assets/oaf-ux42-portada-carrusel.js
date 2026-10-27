/* OAF Lambayeque UX42 · Carrusel informativo institucional, 15 s.
 * ENFEN oficial ≠ pronóstico meteorológico externo ≠ RF experimental.
 * Cambio automático pausado cuando el usuario interactúa y con pestaña oculta.
 */
(()=>{"use strict";
const $=id=>document.getElementById(id),places={Chiclayo:[-6.7714,-79.8409],Jayanca:[-6.39278,-79.8228],Motupe:[-6.15083,-79.7142],Olmos:[-5.98825,-79.74723]};
const el=(tag,cl,text)=>{const x=document.createElement(tag);if(cl)x.className=cl;if(text!==undefined)x.textContent=text;return x;};
const fmt=(n,d=1)=>Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let started=false,index=0,timer=null,seq=0,rf=null,monthlyLoaded=false,paused=false;
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
function closest(p){return Object.entries(places).map(([city,[lat,lon]])=>({city,d:(lat-p.lat)**2+(lon-p.lon)**2*Math.cos(p.lat*Math.PI/180)**2})).sort((a,b)=>a.d-b.d)[0].city}
function smallBars(host,series,unit){
 const vals=series.map(x=>x.n).filter(Number.isFinite);host.replaceChildren();
 if(!vals.length){host.textContent="Serie numérica no disponible.";return;}
 const max=Math.max(...vals,0.1);
 for(const point of series){const wrap=el("div","oaf-ux42-bar"),track=el("div","oaf-ux42-bartrack");
  const value=el("span","oaf-ux42-val",fmt(point.n,unit==="°C"?1:1));
  const fill=el("i");fill.style.height=(Number.isFinite(point.n)?(point.n>0?Math.max(3,Math.min(100,point.n/max*100)):0):0)+"%";
  track.append(fill);wrap.append(value,track,el("small",null,point.label));host.append(wrap);
 }
}
async function weather(){
 const p=location(),card=$("oaf-ux42-slide-week");if(!card)return;
 const q=++seq,body=$("oaf-ux42-week-body"),plot=$("oaf-ux42-week-plot");
 body.textContent="Consultando siete días para "+p.name+"…";plot.replaceChildren();
 try{
  const query=new URLSearchParams({latitude:String(p.lat),longitude:String(p.lon),timezone:"America/Lima",forecast_days:"7",
   daily:"precipitation_sum,temperature_2m_max"});
  const response=await fetch("https://api.open-meteo.com/v1/forecast?"+query,{cache:"no-store"});
  if(!response.ok)throw Error("HTTP "+response.status);
  const j=await response.json(),d=j.daily;
  if(!Array.isArray(d?.time)||d.time.length!==7||!d.precipitation_sum?.every(Number.isFinite)||!d.temperature_2m_max?.every(Number.isFinite))throw Error("Serie diaria incompleta");
  if(q!==seq)return;
  const mm=d.precipitation_sum.reduce((a,b)=>a+b,0),tmax=Math.max(...d.temperature_2m_max);
  body.textContent=p.name+" · "+d.time[0]+" a "+d.time[6]+" · "+fmt(mm)+" mm acumulados · máxima "+fmt(tmax)+" °C.";
  smallBars(plot,d.time.map((day,i)=>({label:day.slice(8,10)+"/"+day.slice(5,7),n:d.precipitation_sum[i]})),"mm");
  $("oaf-ux42-week-note").textContent="Precipitación diaria (mm). Fuente: Open-Meteo Forecast API; pronóstico de área actualizado en cada consulta.";
 }catch(e){if(q===seq){body.textContent="Pronóstico externo no disponible para "+p.name+".";plot.textContent="Comprueba la conexión y consulta Predicciones.";}}
}
async function monthly(){
 const p=location(),body=$("oaf-ux42-month-body"),plot=$("oaf-ux42-month-plot");if(!body)return;
 if(!monthlyLoaded){
  try{const response=await fetch("datos/rf_experimental_ux15.json",{cache:"no-store"});if(!response.ok)throw Error("HTTP "+response.status);
   rf=await response.json();if(rf?.estado!=="candidato_experimental_generado")throw Error("Modelo no certificado");
  }catch(_){rf=null;}
  monthlyLoaded=true;
 }
 const city=closest(p),series=rf?.escenarios_mensuales_rf_experimentales?.[city]?.slice(0,6)||[];
 if(series.length!==6||series.some(r=>!Number.isFinite(r.precipitacion_mm))){
  body.textContent="El modelo mensual no tiene una serie verificable.";plot.replaceChildren();return;
 }
 smallBars(plot,series.map(r=>({label:r.mes.slice(5,7)+"/"+r.mes.slice(2,4),n:r.precipitacion_mm})),"mm");
 const total=series.reduce((a,b)=>a+b.precipitacion_mm,0);
 body.textContent="Nov. 2026 – Abr. 2027 · "+city+" · lluvia modelada acumulada: "+fmt(total)+" mm (RF experimental).";
 $("oaf-ux42-month-note").textContent=(p.custom?"Referencia de "+city+"; NO estimación validada para la parcela solicitada. ":"")+
 "Random Forest OAF: escenario experimental, no pronóstico oficial ni predicción calibrada para cada fundo.";
}
function construct(){
 const side=$("inicio")?.querySelector(".oaf-ux14-home-side");
 const official=side?.querySelector(".oaf-ux14-nino");if(!official||started)return false;
 started=true;side.classList.add("oaf-ux42-carousel");
 official.id="oaf-ux42-slide-official";official.classList.add("oaf-ux42-slide");slides.push(official);
 const officialDate=el("p","oaf-ux42-official-meta","Emitido: 16/10/2026 · Fuente: ENFEN, Comunicado 18-2026, figura 2a (Niño 1+2).");
 official.append(officialDate);
 for(const [id,kicker,heading,bodyId,plotId,noteId,note] of [
  ["week","PRÓXIMOS 7 DÍAS","Pronóstico meteorológico", "oaf-ux42-week-body","oaf-ux42-week-plot","oaf-ux42-week-note","Precipitación diaria (mm). Fuente: Open-Meteo Forecast API."],
  ["month","NOV. 2026 – ABR. 2027","Horizonte mensual OAF","oaf-ux42-month-body","oaf-ux42-month-plot","oaf-ux42-month-note","Escenario RF experimental."]]){
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
 $("oaf-home-location")?.addEventListener("change",()=>{weather();monthly()});
 document.addEventListener("oaf:area-update",e=>{if(e.detail?.scope==="inicio"){weather();monthly()}});
 go(0);weather();monthly();start();return true;
}
function init(){let retries=0;const probe=()=>{if(!construct()&&++retries<45)setTimeout(probe,250)};probe()}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();