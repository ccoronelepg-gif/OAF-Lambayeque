/* OAF-Lambayeque | fase climática 6A
   Señales de anomalía comparando pronósticos EXTERNOS con reanálisis 1996-2025.
   No predice El Niño Costero ni implica probabilidad calibrada.
   Fuentes: https://open-meteo.com/en/docs y /docs/historical-weather-api
*/
(function(root){
  'use strict';
  const REF_START=1996, REF_END=2025, WINDOW=15, YEARS_MIN=25;
  const COORDS={
    Chiclayo:[-6.7714,-79.8409],
    Jayanca:[-6.39278,-79.8228],
    Motupe:[-6.15083,-79.7142],
    Olmos:[-5.98825,-79.74723]
  };
  function validDate(d){return typeof d==='string' && /^\d{4}-\d{2}-\d{2}$/.test(d) && Number.isFinite(Date.parse(d+'T00:00:00Z')) && new Date(d+'T00:00:00Z').toISOString().slice(0,10)===d}
  function sday(d){
    if(!validDate(d))throw Error('Fecha inválida: '+d);
    const m=Number(d.slice(5,7)),day=Number(d.slice(8,10));
    return Math.round((Date.UTC(2000,m-1,day)-Date.UTC(2000,0,1))/86400000);
  }
  function dist(a,b){const n=Math.abs(a-b);return Math.min(n,366-n)}
  function q(values,p){
    if(!values.length)throw Error('Sin valores para el percentil');
    const x=values.slice().sort((a,b)=>a-b),u=(x.length-1)*p,i=Math.floor(u),f=u-i;
    return x[i]*(1-f)+x[Math.min(i+1,x.length-1)]*f;
  }
  function isNum(x){return typeof x==='number'&&Number.isFinite(x)}
  function extract(d,variable){
    if(!d||!d.daily||!Array.isArray(d.daily.time)||!Array.isArray(d.daily[variable])||d.daily.time.length!==d.daily[variable].length)throw Error('Serie diaria incompatible: '+variable);
    const m=new Map();
    for(let i=0;i<d.daily.time.length;i++){
      const k=d.daily.time[i],v=d.daily[variable][i];
      if(!validDate(k)||m.has(k))throw Error('Fecha repetida o inválida: '+k);
      m.set(k,isNum(v)?v:null);
    }
    return m;
  }
  function prepare(temperatureData,rainData){
    const tm=extract(temperatureData,'temperature_2m_mean');
    const pm=extract(rainData,'precipitation_sum');
    const dates=[...new Set([...tm.keys(),...pm.keys()])].sort();
    if(dates.length<10500)throw Error('Base 1996–2025 incompleta; no alcanza el mínimo esperado');
    const raw=new Map(),list=[];
    for(const date of dates){
      const year=Number(date.slice(0,4));
      if(year<REF_START||year>REF_END)continue;
      const rec={date,year,day:sday(date),temp:tm.get(date)??null,rain:pm.get(date)??null};
      raw.set(date,rec);list.push(rec);
    }
    if(list.length<10500)throw Error('Insuficientes días dentro del periodo 1996–2025');
    return {raw,list,coverage:{
      dates:list.length,
      tempDays:list.filter(r=>isNum(r.temp)).length,
      rainDays:list.filter(r=>isNum(r.rain)).length,
      tempCell:[temperatureData.latitude,temperatureData.longitude],
      rainCell:[rainData.latitude,rainData.longitude]
    }};
  }
  function seasonalValues(hist,target,field){
    const grouped=new Map(),idx=sday(target);
    for(const r of hist.list){
      const v=r[field];if(isNum(v)&&dist(r.day,idx)<=WINDOW){
        if(!grouped.has(r.year))grouped.set(r.year,[]);
        grouped.get(r.year).push(v);
      }
    }
    const eligible=[...grouped.values()].filter(x=>x.length>=15);
    if(eligible.length<YEARS_MIN)throw Error('Referencia '+field+' insuficiente: '+eligible.length+' años válidos');
    return {values:eligible.flat(),years:eligible.length};
  }
  function nextDate(d,shift){
    const dt=new Date(d+'T00:00:00Z');dt.setUTCDate(dt.getUTCDate()+shift);return dt.toISOString().slice(0,10);
  }
  function sevenDayReference(hist,target){
    const grouped=new Map(),idx=sday(target);
    for(const r of hist.list){
      if(dist(r.day,idx)>WINDOW)continue;
      let sum=0,good=true;
      for(let k=0;k<7;k++){
        const key=nextDate(r.date,k);
        const v=hist.raw.get(key)?.rain;
        if(!isNum(v)||v<0){good=false;break}
        sum+=v;
      }
      if(!good)continue;
      if(!grouped.has(r.year))grouped.set(r.year,[]);
      grouped.get(r.year).push(sum);
    }
    const eligible=[...grouped.values()].filter(v=>v.length>=8);
    if(eligible.length<YEARS_MIN)throw Error('Referencia de lluvia incompleta: '+eligible.length+' años');
    return {values:eligible.flat(),years:eligible.length};
  }
  function compare(forecast,history){
    const daily=forecast?.daily;
    if(!daily||!Array.isArray(daily.time)||!Array.isArray(daily.temperature_2m_mean)||!Array.isArray(daily.precipitation_sum))throw Error('Pronóstico diario incompatible');
    if(daily.time.length<8||daily.temperature_2m_mean.length<8||daily.precipitation_sum.length<8)throw Error('Necesitamos hoy y siete jornadas futuras');
    const selected=[];
    for(let i=1;i<=7;i++){
      const date=daily.time[i],t=daily.temperature_2m_mean[i],p=daily.precipitation_sum[i];
      if(!validDate(date)||date!==nextDate(daily.time[0],i)||!isNum(t)||!isNum(p)||p<0)throw Error('Pronóstico incompleto o discontinuo para '+date);
      const base=seasonalValues(history,date,'temp'),mean=base.values.reduce((a,b)=>a+b,0)/base.values.length;
      const p10=q(base.values,.1),p90=q(base.values,.9);
      selected.push({
        date,tForecast:t,tClim:mean,delta:t-mean,p10,p90,
        signal:t>p90?'cálida':t<p10?'fría':'sin extremo térmico',
        years:base.years,pForecast:p
      });
    }
    const forecastRain=selected.reduce((a,b)=>a+b.pForecast,0);
    const rainRef=sevenDayReference(history,selected[0].date);
    const rainMedian=q(rainRef.values,.5),rainP90=q(rainRef.values,.9);
    return {
      days:selected,
      rain:{
        value:forecastRain,median:rainMedian,p90:rainP90,years:rainRef.years,
        signal:rainP90>0 && forecastRain>rainP90?'acumulado sobre P90':
          rainP90===0 && forecastRain>0?'precipitación prevista con P90 histórico de 0 mm':'sin excedencia del P90'
      },
      metadata:{
        period:'1996-2025',yearsExpected:30,seasonalWindow:'±15 días calendario',
        forecastSource:'Open-Meteo API (modelo externo)',
        historicalT:'ERA5-Land (reanálisis)',
        historicalP:'ERA5 (reanálisis)',
        tempYearsMin:Math.min(...selected.map(d=>d.years)),
        histCoverage:history.coverage,
        limitation:'Comparación de modelos de distinta naturaleza. No son probabilidades calibradas ni predicción de El Niño Costero.'
      }
    };
  }
  root.OAFClimateCore={prepare,compare,sday,q,seasonalValues,sevenDayReference};
  if(typeof document==='undefined')return;
  const panel=document.getElementById('oaf-anomaly-panel');
  if(!panel)return;
  const btn=document.getElementById('oaf-anomaly-run');
  const status=document.getElementById('oaf-anomaly-status');
  const place=document.getElementById('oaf-anomaly-place');
  const results=document.getElementById('oaf-anomaly-results');
  const cache=new Map();
  function number(x,d){return isNum(x)?x.toLocaleString('es-PE',{minimumFractionDigits:d,maximumFractionDigits:d}):'—'}
  async function fetchJSON(url){
    const r=await fetch(url,{cache:'no-store',headers:{Accept:'application/json'}});
    if(!r.ok)throw Error('HTTP '+r.status+' ('+r.url.split('?')[0]+')');
    const data=await r.json();if(data.error)throw Error(data.reason||'Error del proveedor');
    return data;
  }
  function urls(loc){
    const [lat,lon]=COORDS[loc];
    const q={latitude:String(lat),longitude:String(lon),timezone:'America/Lima'};
    const qp=(extra)=>new URLSearchParams(Object.assign({},q,extra)).toString();
    return [
      'https://api.open-meteo.com/v1/forecast?'+qp({daily:'temperature_2m_mean,precipitation_sum',forecast_days:'8'}),
      'https://archive-api.open-meteo.com/v1/archive?'+qp({start_date:'1996-01-01',end_date:'2025-12-31',daily:'temperature_2m_mean',models:'era5_land'}),
      'https://archive-api.open-meteo.com/v1/archive?'+qp({start_date:'1996-01-01',end_date:'2025-12-31',daily:'precipitation_sum',models:'era5'})
    ];
  }
  function draw(out,loc){
    document.getElementById('oaf-anomaly-t-days').textContent=out.days.filter(x=>x.signal!=='sin extremo térmico').length+' / 7';
    document.getElementById('oaf-anomaly-rain').textContent=number(out.rain.value,1)+' mm';
    document.getElementById('oaf-anomaly-rain-p90').textContent=number(out.rain.p90,1)+' mm';
    document.getElementById('oaf-anomaly-rain-class').textContent=out.rain.signal;
    const body=document.getElementById('oaf-anomaly-table');
    body.replaceChildren();
    for(const d of out.days){
      const tr=document.createElement('tr');
      const values=[d.date,number(d.tForecast,1)+' °C',number(d.delta,1)+' °C',number(d.p10,1)+' a '+number(d.p90,1)+' °C',d.signal];
      for(const v of values){const td=document.createElement('td');td.textContent=v;tr.appendChild(td)}
      body.appendChild(tr);
    }
    document.getElementById('oaf-anomaly-method').textContent=
      'Localidad: '+loc+'. Referencia 1996–2025: ≥'+out.metadata.tempYearsMin+
      ' años válidos por fecha; lluvia: '+out.rain.years+' años. Ventana estacional ±15 días. '+
      'T: ERA5-Land; lluvia: ERA5. Fecha de consulta: '+new Date().toLocaleString('es-PE',{timeZone:'America/Lima'})+
      '. Pronóstico externo Open-Meteo, diferente del reanálisis.';
    results.hidden=false;
  }
  async function run(){
    const key=place.value;btn.disabled=true;results.hidden=true;
    status.textContent='Consultando pronóstico y referencia climática 1996–2025 para '+key+'… (30 años de datos diarios).';
    try{
      let prepared=cache.get(key);
      let forecast;
      if(prepared){
        forecast=await fetchJSON(urls(key)[0]);
      }else{
        const links=urls(key);
        const all=await Promise.all(links.map(fetchJSON));
        forecast=all[0];prepared=prepare(all[1],all[2]);
        cache.set(key,prepared);
      }
      const out=compare(forecast,prepared);
      if(place.value!==key){status.textContent='La localidad cambió durante la descarga; vuelve a consultar.';return}
      draw(out,key);
      status.textContent='Señales climáticas calculadas para siete días futuros. Estas no son alertas operativas ni probabilidades de enfermedad.';
    }catch(err){
      status.textContent='Sin evaluación: '+err.message+'. No se rellenaron datos ausentes ni se mostraron estimaciones ficticias.';
    }finally{btn.disabled=false}
  }
  btn.addEventListener('click',run);
})(typeof globalThis!=='undefined'?globalThis:this);
