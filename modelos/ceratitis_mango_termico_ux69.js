/* OAF · UX69. C. capitata / mango: térmica exploratoria sin probabilidad de infestación.
 * Ricalde et al. 2012, Journal of Insect Science 12:33, DOI 10.1673/031.012.3301:
 * texto de resultados, Petrolina, umbral huevo-adulto 9.1 °C, K=341 °C·día.
 * ATENCIÓN: el resumen del mismo artículo cita 8.47 °C; se declara discrepancia.
 * Régimen de laboratorio 15–30 °C; el modelo NO está calibrado para Lambayeque.
 */
(function(root){"use strict";
const MODEL=Object.freeze({
 id:"ceratitis_mango_ux69",crop:"mango",organism:"Ceratitis capitata",
 baseC:9.1,referenceDD:341,minStudyC:15,maxStudyC:30,
 version:"0.1-exploratorio-2026-11-06",calibratedInLambayeque:false,
 source:"Ricalde et al. (2012), Journal of Insect Science 12:33",
 doi:"10.1673/031.012.3301",
 warning:"Temperatura del aire a 2 m no representa la temperatura de pupas en el suelo. No calcula una cohorte ni predice generaciones sin una fecha de inicio biológica y sin calibración local. El resumen de la publicación indica 8.47 °C, pero el texto de resultados indica 9.1 °C; se usa 9.1 °C como parámetro explícito del cuerpo del artículo."
});
function shift(date,days){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date))throw Error("Fecha no válida");
 const d=new Date(date+"T12:00:00Z");
 if(Number.isNaN(d.getTime())||d.toISOString().slice(0,10)!==date)throw Error("Fecha no válida");
 d.setUTCDate(d.getUTCDate()+days);return d.toISOString().slice(0,10);
}
function parse(hourly){
 if(!hourly||!Array.isArray(hourly.time)||!Array.isArray(hourly.temperature_2m)||
 hourly.time.length!==hourly.temperature_2m.length)throw Error("La serie térmica está incompleta");
 const days=new Map(),records=[];
 for(let i=0;i<hourly.time.length;i++){
  const stamp=hourly.time[i],t=hourly.temperature_2m[i];
  if(typeof stamp!=="string"||!/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):00$/.test(stamp))
   throw Error("Hora meteorológica inválida");
  if(typeof t!=="number"||!Number.isFinite(t)||t< -30||t>55)
   throw Error("Temperatura faltante o fuera de rango: "+stamp);
  const date=stamp.slice(0,10),hour=Number(stamp.slice(11,13));
  if(!days.has(date))days.set(date,new Map());
  if(days.get(date).has(hour))throw Error("Hora duplicada "+stamp);
  const row={time:stamp,date,hour,t};days.get(date).set(hour,row);records.push(row);
 }
 return {days,records};
}
function completeDay(days,date){
 const hours=days.get(date);
 if(!hours||hours.size!==24)throw Error("Faltan horas meteorológicas en "+date);
 return Array.from({length:24},(_,h)=>{
  const row=hours.get(h);
  if(!row)throw Error("Falta hora "+h+" en "+date);
  return row;
 });
}
function thermalDay(date,rows){
 if(rows.length!==24)throw Error("Se requieren 24 horas para el cálculo de grados-día");
 const tmean=rows.reduce((sum,row)=>sum+row.t,0)/24;
 if(tmean<MODEL.minStudyC||tmean>MODEL.maxStudyC)
  throw Error("Temperatura media "+tmean.toFixed(1)+" °C fuera del intervalo experimental 15–30 °C en "+date);
 return {date,tmean,gdd:Math.max(0,tmean-MODEL.baseC),hours:24};
}
function evaluate(hourly,opts){
 const {mode,today,start,end,nowMs}=opts||{},parsed=parse(hourly);
 const daily=[];
 if(mode==="current"){
  // Peru uses UTC-5 throughout the year. The 24 model hours must be consecutive and not future hours.
  const now=Number.isFinite(nowMs)?nowMs:Date.now();
  const cutoff=now-24*3600000;
  const rows=parsed.records.filter(r=>{
   const ms=Date.parse(r.time+":00-05:00");return ms>cutoff&&ms<=now;
  }).sort((a,b)=>a.time.localeCompare(b.time));
  if(rows.length!==24)throw Error("No hay 24 horas actuales completas");
  for(let i=1;i<rows.length;i++){
   const prev=Date.parse(rows[i-1].time+":00-05:00");
   const next=Date.parse(rows[i].time+":00-05:00");
   if(next-prev!==3600000)throw Error("La serie actual contiene saltos horarios");
  }
  daily.push(thermalDay(rows[rows.length-1].date+" · 24 h",rows));
 }else{
  let dates=[];
  if(mode==="forecast"){
   if(!today)throw Error("Fecha local requerida para pronóstico");
   dates=Array.from({length:7},(_,i)=>shift(today,i+1));
  }else if(mode==="history"){
   if(!start||!end||start>end||end>=today)throw Error("Rango histórico inválido");
   const days=(Date.parse(end)-Date.parse(start))/86400000+1;
   if(days>366)throw Error("Rango histórico máximo: 366 días");
   for(let d=start;d<=end;d=shift(d,1))dates.push(d);
  }else throw Error("Periodo térmico desconocido");
  for(const date of dates)daily.push(thermalDay(date,completeDay(parsed.days,date)));
 }
 const accumulatedDD=daily.reduce((total,day)=>total+day.gdd,0);
 return {
  indicator:"thermal",model:MODEL,baseC:MODEL.baseC,referenceDD:MODEL.referenceDD,
  accumulatedDD,daily,days:daily.length,method:"GD por día = max(T media diaria a 2 m − 9,1 °C, 0); suma del intervalo consultado. Sin biofix no se puede inferir generación.",
  status:"indicador térmico experimental, no riesgo ni generación",
  interpretation:"Acumulación térmica de referencia para C. capitata; el cálculo no mide abundancia, supervivencia, presencia ni daño en frutos.",
  limitation:MODEL.warning,
  sourceUrl:"https://doi.org/10.1673/031.012.3301"
 };
}
root.OAFCeratitisThermal={MODEL,evaluate,parse,shift};
})(typeof window!=="undefined"?window:globalThis);
