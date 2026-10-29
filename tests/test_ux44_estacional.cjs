/* UX45: prueba contra el contrato SEAS5: 6h, no precipitación diaria inexistente. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
const read=p=>fs.readFileSync(p,"utf8");
const src=read("assets/oaf-ux15-rf-salidas.js"),html=read("index.html"),
 css=read("assets/oaf-ux14-reorganizacion.css"),sw=read("sw.js");
new Function(src);
assert.match(html,/oaf-ux15-rf-salidas\.js\?v=/);
assert.match(sw,/const RELEASE="oaf-pwa-shell-[^"]+"/);
assert(!html.includes("oaf-ux15-counter")&&!html.includes("oaf-ux15-contador.js"));
assert(!fs.existsSync("assets/oaf-ux15-contador.js"));
assert(!css.includes("oaf-ux15-counter"));
assert(src.includes("models:\"ecmwf_seas5_ensemble_mean\",hourly:\"precipitation,temperature_2m\""),
 "La API estacional requiere hourly=precipitation,temperature_2m");
assert(!src.includes('daily:"precipitation_sum,temperature_2m_mean"'),"Se usa una variable estacional inexistente");
const start=src.indexOf("function seasonalMonthlyFromSixHourly(");
const end=src.indexOf("function seasonalRequest(",start);
assert(start>=0&&end>start,"Falta agregado de lluvia 6h y media térmica");
const parse=vm.runInNewContext('(()=>{'+src.slice(start,end)+';return seasonalMonthlyFromSixHourly})()',
 {Date,Map,Set,Number,Error},{timeout:2500});
const months=["2026-11","2026-12","2027-01","2027-02","2027-03","2027-04"];
const time=[],rain=[],temp=[];
for(let y=2026,m=11;y<2027||m<=4;){
 const count=new Date(Date.UTC(y,m,0)).getUTCDate();
 for(let d=1;d<=count;d++)for(const h of ["00","06","12","18"]){
  time.push(y+"-"+String(m).padStart(2,"0")+"-"+String(d).padStart(2,"0")+"T"+h+":00");
  rain.push(.5);temp.push(25);
 }
 if(m===12){y++;m=1}else m++;
}
const h={time,precipitation:rain,temperature_2m:temp};
const result=parse(h,months);
assert(result.complete.every(Boolean));
assert(result.rainfall[0]===60&&result.rainfall[1]===62&&result.rainfall[3]===56&&result.rainfall[5]===60,
 "Lluvia por mes no coincide con cuatro intervalos de 6h cada día");
assert(result.temperature.every(x=>x===25),"Se suman las temperaturas en vez de promediarlas");
const remove=time.findIndex(t=>t==="2027-02-16T12:00");
const shortened={time:time.filter((_,i)=>i!==remove),
 precipitation:rain.filter((_,i)=>i!==remove),
 temperature_2m:temp.filter((_,i)=>i!==remove)};
const partial=parse(shortened,months);
assert(partial.complete[3]===false&&Number.isNaN(partial.rainfall[3])&&Number.isNaN(partial.temperature[3]),
 "Un mes con una medición 6h faltante debe quedar vacío");
assert(partial.rainfall.filter(Number.isFinite).length===5);
let dup;try{parse({time:[...time,time[0]],precipitation:[...rain,.5],temperature_2m:[...temp,25]},months)}catch(e){dup=e}
assert(dup?.message.includes("duplicadas"),"Debe rechazar fechas/horas duplicadas");
console.log("UX45 OK: contrato API 6h, lluvia mensual mm, temperatura °C, meses parciales y contador eliminado");
