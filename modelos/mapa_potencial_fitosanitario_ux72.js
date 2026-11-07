/* OAF UX72 — núcleo de cartografía de condiciones climáticas potenciales.
 * Los colores NO representan incidencia, probabilidad ni riesgo fitosanitario calibrado.
 * Evaluación por punto meteorológico, sin interpolación ni polígonos inferidos.
 */
(function(root){"use strict";
const MODEL={
 botrytis:{id:"botrytis_arandano",crop:"arandano",organism:"Botrytis cinerea",kind:"humedad_favorable",thresholdRH:90,minimumConsecutiveHours:6,validatedLocally:false,
  description:"Indicador exploratorio de episodios HR del aire >90 % durante ≥6 horas, NO horas de mojado foliar.",
  reference:"https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/"},
 ceratitis:{id:"ceratitis_mango",crop:"mango",organism:"Ceratitis capitata",kind:"acumulacion_termica",baseReportedResults:9.1,baseReportedAbstract:8.47,referenceDD:341,temperatureRange:[15,30],validatedLocally:false,
  description:"Grados-día por temperatura del aire a 2 m; no infiere generaciones ni densidad. Bases teóricas 8,47/9,1 °C discrepantes dentro de Ricalde et al. (2012).",
  reference:"https://doi.org/10.1673/031.012.3301"}
};
function addDays(date,offset){const d=new Date(date+"T12:00:00Z");if(Number.isNaN(d.getTime()))throw Error("Fecha inválida");
 d.setUTCDate(d.getUTCDate()+offset);return d.toISOString().slice(0,10)}
function inRing(lon,lat,ring){
 let inArea=false;
 for(let i=0,j=ring.length-1;i<ring.length;j=i++){
  const x=ring[i][0],y=ring[i][1],x0=ring[j][0],y0=ring[j][1];
  if((y>lat)!==(y0>lat) && lon<(x0-x)*(lat-y)/(y0-y)+x)inArea=!inArea;
 }return inArea
}
function pointInRegion(lon,lat,rings){return rings.some(r=>inRing(lon,lat,r))}
function sampleGrid(rings,opts={}){
 if(!Array.isArray(rings)||!rings.length)throw Error("Se requiere el contorno georreferenciado de Lambayeque.");
 const valid=rings.filter(r=>Array.isArray(r)&&r.length>=4&&r.every(p=>Array.isArray(p)&&p.length>=2&&p.every(Number.isFinite)));
 if(!valid.length)throw Error("Contorno geográfico incompleto");
 const all=valid.flat(),lons=all.map(p=>p[0]),lats=all.map(p=>p[1]);
 const west=Math.min(...lons),east=Math.max(...lons),south=Math.min(...lats),north=Math.max(...lats);
 const columns=opts.columns||9,rows=opts.rows||8,max=opts.max||45;
 if(columns<2||rows<2||max<4||columns>20||rows>20||max>100)throw Error("Malla fuera de rango");
 const res=[];
 // Malla determinista de CENTROS, no celdas de riesgo: todo se asigna a puntos reales.
 for(let j=0;j<rows;j++)for(let i=0;i<columns;i++){
  const lon=west+(i+.5)*(east-west)/columns,lat=north-(j+.5)*(north-south)/rows;
  if(pointInRegion(lon,lat,valid)){
   res.push({id:"P"+String(res.length+1).padStart(2,"0"),lon:+lon.toFixed(5),lat:+lat.toFixed(5)});
  }
 }
 if(res.length>max){const every=res.length/max;return Array.from({length:max},(_,i)=>res[Math.floor(i*every)])}
 if(!res.length)throw Error("La malla no produjo puntos dentro del contorno.");
 return res;
}
function requiredDates(today){return Array.from({length:7},(_,i)=>addDays(today,i+1))}
function validateHours(hourly,dates,field){
 if(!hourly||!Array.isArray(hourly.time)||!Array.isArray(hourly[field])||hourly.time.length!==hourly[field].length)
  throw Error("Serie meteorológica incompleta: "+field);
 const table=new Map();
 for(let i=0;i<hourly.time.length;i++){
  const t=hourly.time[i],v=hourly[field][i];
  if(typeof t!=="string"||!/^\d{4}-\d{2}-\d{2}T(?:[01]\d|2[0-3]):00$/.test(t))
   throw Error("Hora meteorológica inválida");
  if(table.has(t))throw Error("Marca horaria duplicada: "+t);
  if(v!==null&&(typeof v!=="number"||!Number.isFinite(v)))throw Error("Valor meteorológico inválido: "+t);
  table.set(t,v);
 }
 const byDay=new Map();
 for(const date of dates){
  const values=[];
  for(let h=0;h<24;h++){
   const key=date+"T"+String(h).padStart(2,"0")+":00";
   if(!table.has(key)||table.get(key)===null)throw Error("Falta hora "+key);
   values.push(table.get(key));
  }
  byDay.set(date,values);
 }
 return byDay;
}
function evaluatePoint(hourly,model,today){
 if(!MODEL[model])throw Error("Modelo no aprobado para este indicador");
 const dates=requiredDates(today),bot=model==="botrytis";
 const field=bot?"relative_humidity_2m":"temperature_2m",byDay=validateHours(hourly,dates,field);
 if(bot){
  const all=dates.flatMap(d=>byDay.get(d));
  if(all.some(v=>v<0||v>100))throw Error("Humedad relativa fuera del intervalo 0–100 %");
  let streak=0,episodes=0,longest=0,hours=0;
  for(const rh of all){
   if(rh>MODEL.botrytis.thresholdRH){streak++;hours++;longest=Math.max(longest,streak);if(streak===MODEL.botrytis.minimumConsecutiveHours)episodes++}
   else streak=0;
  }
  return {model,kind:"humedad_favorable",episodes,hoursOver90:hours,longestStreak:longest,
   label:episodes===0?"Sin episodio detectado":episodes===1?"Un episodio ≥6 h":"Dos o más episodios ≥6 h",
   class:episodes===0?"no_detectado":episodes===1?"un_episodio":"varios_episodios",
   dates:[dates[0],dates.at(-1)],validatedLocally:false};
 }
 const out=[],baseA=MODEL.ceratitis.baseReportedAbstract,baseB=MODEL.ceratitis.baseReportedResults;
 let gdA=0,gdB=0;
 for(const date of dates){
  const vals=byDay.get(date);
  if(vals.some(x=>x< -30||x>55))throw Error("Temperatura fuera de intervalo físico");
  const mean=vals.reduce((a,b)=>a+b,0)/24;
  if(mean<15||mean>30)throw Error("Temperatura media fuera del intervalo 15–30 °C del estudio de laboratorio en "+date);
  const a=Math.max(0,mean-baseA),b=Math.max(0,mean-baseB);
  gdA+=a;gdB+=b;out.push({date,tmean:mean,gddBase847:a,gddBase91:b});
 }
 return {model,kind:"acumulacion_termica",degreesDaysMin:gdB,degreesDaysMax:gdA,meanTemperature:out.reduce((a,x)=>a+x.tmean,0)/out.length,
  dates:[dates[0],dates.at(-1)],daily:out,validatedLocally:false,
  label:"Acumulación térmica · referencia experimental",class:"sin_categoria_de_riesgo"};
}
function assessBatch(data,points,model,today){
 if(!Array.isArray(data)||data.length!==points.length)throw Error("La respuesta múltiple no corresponde a los puntos consultados");
 return points.map((p,i)=>{
  const raw=data[i],loc={...p,modelledLat:raw?.latitude,modelledLon:raw?.longitude};
  if(!Number.isFinite(loc.modelledLat)||!Number.isFinite(loc.modelledLon))
   return {...loc,error:"Celda del proveedor no identificada",indicator:null};
  try{return {...loc,indicator:evaluatePoint(raw.hourly,model,today),error:null}}
  catch(e){return {...loc,error:String(e.message||e),indicator:null}}
 });
}
root.OAFClimaticPotentialCore={MODEL,addDays,pointInRegion,sampleGrid,validateHours,evaluatePoint,assessBatch,requiredDates};
})(typeof window!=="undefined"?window:globalThis);
