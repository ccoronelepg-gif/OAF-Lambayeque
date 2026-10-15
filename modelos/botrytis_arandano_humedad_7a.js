/* OAF-Lambayeque · Fase 7A: condiciones pronosticadas de humedad prolongada.
 * Arándano / Botrytis cinerea. UC IPM describes >~90% RH for >=6 continuous h
 * as one possible favourable context. NOT an infection probability or risk score.
 * Source hourly 2m ambient predictions, NOT leaf wetness or canopy sensors.
 */
(function(root){
"use strict";
const SITES={Motupe:[-6.15083,-79.7142],Jayanca:[-6.39278,-79.8228],
             Olmos:[-5.98825,-79.74723],Chiclayo:[-6.7714,-79.8409]};
const VARS=["temperature_2m","relative_humidity_2m","precipitation","shortwave_radiation","vapour_pressure_deficit"];
function dayAfter(date,shift){
 const d=new Date(date+"T00:00:00Z");
 if(Number.isNaN(d.valueOf())||d.toISOString().slice(0,10)!==date)throw Error("Fecha inválida "+date);
 d.setUTCDate(d.getUTCDate()+shift);
 return d.toISOString().slice(0,10);
}
function evaluate(hourly){
 if(!hourly||!Array.isArray(hourly.time)||hourly.time.length<192)
   throw Error("Se necesitan ocho jornadas horarias (hoy + siete futuras)");
 const times=hourly.time,seen=new Set(),byDate=new Map();
 for(const variable of VARS)
   if(!Array.isArray(hourly[variable])||hourly[variable].length!==times.length)
     throw Error("Serie horaria incompleta: "+variable);
 for(let i=0;i<times.length;i++){
   const stamp=times[i];
   if(typeof stamp!=="string"||!/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):00$/.test(stamp)||seen.has(stamp))
     throw Error("Marcas horarias inválidas o repetidas");
   seen.add(stamp);
   const date=stamp.slice(0,10),hour=Number(stamp.slice(11,13));
   if(!byDate.has(date))byDate.set(date,new Map());
   byDate.get(date).set(hour,Object.fromEntries(VARS.map(v=>[v,hourly[v][i]])));
 }
 const today=times[0].slice(0,10);
 const days=Array.from({length:7},(_,i)=>dayAfter(today,i+1));
 const flattened=[],summaries=[];
 for(const day of days){
   const values=byDate.get(day);
   if(!values||values.size!==24)throw Error("El "+day+" no cuenta con 24 horas completas");
   let wetHours=0,valid=true,rain=0,radSum=0,vpdSum=0;
   for(let hour=0;hour<24;hour++){
     const v=values.get(hour);
     if(!v){valid=false;break}
     const t=v.temperature_2m,rh=v.relative_humidity_2m,p=v.precipitation,
           rad=v.shortwave_radiation,dpv=v.vapour_pressure_deficit;
     if([t,rh,p,rad,dpv].some(x=>typeof x!=="number"||!Number.isFinite(x))||
         rh<0||rh>100||p<0||rad<0||dpv<0||t< -20||t>55)
       {valid=false;break}
     flattened.push({day,hour,t,rh,rain:p,rad,dpv});
     if(rh>90)wetHours++;
     rain+=p;radSum+=rad*0.0036;vpdSum+=dpv;
   }
   if(!valid)throw Error("Datos horarios faltantes o fuera de rango en "+day);
   summaries.push({date:day,highRHHours:wetHours,rainMm:rain,
      solarMJm2:radSum,vpdMean:vpdSum/24,tempMean:0,
      maxSequenceWithinDay:0,hasEndOfSixHourEpisode:false});
 }
 if(flattened.length!==168)throw Error("Serie futura no continua o incompleta");
 // Conditions can span midnight: streak is NOT reset between days.
 let streak=0,longest=0,streakTemps=[],episodes=0;
 const grouped=new Map(summaries.map(x=>[x.date,x]));
 for(const h of flattened){
   const summary=grouped.get(h.day);
   summary.tempMean+=h.t/24;
   if(h.rh>90){
     streak++;streakTemps.push(h.t);
     summary.maxSequenceWithinDay=Math.max(summary.maxSequenceWithinDay,
       Math.min(streak,h.hour+1));
     longest=Math.max(longest,streak);
     if(streak===6){episodes++;summary.hasEndOfSixHourEpisode=true}
     if(streak>6)summary.hasEndOfSixHourEpisode=true;
   }else{streak=0;streakTemps=[]}
 }
 // An episode is attributed to the calendar day on which the sixth hour falls.
 const daysWithEpisode=summaries.filter(x=>x.hasEndOfSixHourEpisode).length;
 return {days:summaries,daysWithEpisode,longestContinuousRH:longest,
   totalHighRHHours:summaries.reduce((n,x)=>n+x.highRHHours,0),
   continuousEpisodes:episodes,
   threshold:"HR >90 % durante al menos seis horas continuas",
   observation:"Pronóstico externo a 2 m; no es humectación foliar ni diagnóstico."};
}
root.OAFBotrytisCore={evaluate,dayAfter};
if(typeof document==="undefined")return;
const panel=document.getElementById("botrytis-panel");
if(!panel)return;
const site=document.getElementById("botrytis-place");
const btn=document.getElementById("botrytis-run");
const status=document.getElementById("botrytis-status");
const output=document.getElementById("botrytis-results");
const number=(n,places=1)=>n.toLocaleString("es-PE",{minimumFractionDigits:places,maximumFractionDigits:places});
async function run(){
 const place=site.value,coords=SITES[place];
 if(!coords){status.textContent="Localidad no admitida";return}
 btn.disabled=true;output.hidden=true;
 status.textContent="Consultando siete jornadas futuras de humedad, temperatura, lluvia, radiación y DPV para "+place+"…";
 try{
  const params=new URLSearchParams({
   latitude:String(coords[0]),longitude:String(coords[1]),timezone:"America/Lima",
   hourly:VARS.join(","),forecast_days:"8"
  });
  const response=await fetch("https://api.open-meteo.com/v1/forecast?"+params.toString(),{cache:"no-store"});
  if(!response.ok)throw Error("Proveedor meteorológico HTTP "+response.status);
  const data=await response.json();
  if(data.error||!data.hourly)throw Error(data.reason||"No hay horas pronosticadas");
  const result=evaluate(data.hourly);
  if(site.value!==place){status.textContent="La localidad cambió durante la consulta. Vuelve a analizar.";return}
  document.getElementById("botrytis-episodes").textContent=result.continuousEpisodes+" tramo(s)";
  document.getElementById("botrytis-longest").textContent=result.longestContinuousRH+" horas";
  document.getElementById("botrytis-days").textContent=result.daysWithEpisode+" de 7";
  const tbody=document.getElementById("botrytis-rows");tbody.replaceChildren();
  for(const d of result.days){
   const tr=document.createElement("tr");
   for(const v of [d.date,String(d.highRHHours)+" h",number(d.rainMm)+" mm",
       number(d.solarMJm2)+" MJ/m²",number(d.vpdMean,2)+" kPa",
       d.hasEndOfSixHourEpisode?"Sí, humedad prolongada":"No identificado"]){
     const td=document.createElement("td");td.textContent=v;tr.appendChild(td);
   }
   tbody.appendChild(tr);
  }
  document.getElementById("botrytis-provenance").textContent=
   "Consulta a Open-Meteo "+new Date().toLocaleString("es-PE",{timeZone:"America/Lima"})+
   " · "+place+" · horas locales America/Lima · pronóstico externo 2 m. "+result.threshold+
   ". Episodios que cruzan medianoche se cuentan en la fecha donde alcanzan la sexta hora.";
  const bloom=document.getElementById("botrytis-bloom").value;
  document.getElementById("botrytis-phenology").textContent=bloom==="si"?
   "Se indicó floración en campo. Esta etapa es susceptible, pero el módulo NO observa humectación de flores ni confirma patógeno.":
   "Fenología no confirmada. No es posible valorar la susceptibilidad real del lote sin saber si está en floración.";
  status.textContent="Revisión meteorológica experimental finalizada. Los resultados NO expresan probabilidad de Botrytis ni justifican una aplicación.";
  output.hidden=false;
 }catch(err){status.textContent="Evaluación no disponible: "+err.message+". No se sustituyeron datos ausentes."}
 finally{btn.disabled=false}
}
btn.addEventListener("click",run);
site.addEventListener("change",()=>{output.hidden=true;status.textContent="Localidad modificada. Actualiza la consulta."});
document.getElementById("botrytis-bloom").addEventListener("change",()=>{
 if(!output.hidden){
  const bloom=document.getElementById("botrytis-bloom").value;
  document.getElementById("botrytis-phenology").textContent=bloom==="si"?
   "Se indicó floración en campo. Esta etapa es susceptible, pero no observamos humectación ni patógeno.":
   "Fenología no confirmada. La susceptibilidad del lote no está documentada.";
 }
});
})(typeof globalThis!=="undefined"?globalThis:this);
