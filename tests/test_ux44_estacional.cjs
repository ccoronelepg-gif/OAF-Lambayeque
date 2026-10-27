/* UX44 · Comparación estacional de meses completos, retirada de contador.
 * Pruebas sin red, no se inventan datos de Open-Meteo.
 */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
const read=p=>fs.readFileSync(p,"utf8");
const src=read("assets/oaf-ux15-rf-salidas.js"),html=read("index.html"),css=read("assets/oaf-ux14-reorganizacion.css"),sw=read("sw.js");
new Function(src);
assert(html.includes("oaf-ux15-rf-salidas.js?v=20261027-ux44"));
assert(html.includes("oaf-ux42-interfaz.css?v=20261027-ux44"));
assert(sw.includes("oaf-pwa-shell-2026-10-27-ux44"));
assert(!html.includes("oaf-ux15-counter")&&!html.includes("oaf-ux14-counter")&&!html.includes("oaf-ux15-contador.js"),"El contador sigue activo");
assert(!fs.existsSync("assets/oaf-ux15-contador.js"),"No se eliminó el contador");
assert(!css.includes("oaf-ux15-counter")&&!css.includes("oaf-ux14-counter"),"Estilos del contador presentes");
assert(src.includes("ecmwf_seas5_ensemble_mean"));
assert(src.includes("seasonalEndpoint=")&&src.includes("seasonalMonthlyFromDaily"));
assert(src.includes('precipitation_sum,temperature_2m_mean'));
assert(src.includes("values.some(Number.isFinite)")&&src.includes('color:"#237fb1"'));
const start=src.indexOf("function seasonalMonthlyFromDaily("),end=src.indexOf("function seasonalRequest(",start);
assert(start>=0&&end>start);
const parse=vm.runInNewContext('(()=>{'+src.slice(start,end)+';return seasonalMonthlyFromDaily})()',{Date,Map,Set,Number,Error},{timeout:2000});
const months=["2026-11","2026-12","2027-01","2027-02","2027-03","2027-04"];
const days=[],rain=[],temp=[];
for(let y=2026,m=11;y<2027||m<=4;){
 const n=new Date(Date.UTC(y,m,0)).getUTCDate();
 for(let d=1;d<=n;d++){
  days.push(y+"-"+String(m).padStart(2,"0")+"-"+String(d).padStart(2,"0"));
  rain.push(2);temp.push(25+(m%3));
 }
 if(m===12){y++;m=1}else m++;
}
const complete=parse({time:days,precipitation_sum:rain,temperature_2m_mean:temp},months);
assert(complete.complete.every(Boolean),"No reconoce meses completos");
assert(complete.rainfall[0]===60&&complete.rainfall[1]===62&&complete.rainfall[3]===56&&complete.rainfall[5]===60,"Totales de lluvia mensuales erróneos");
assert(complete.temperature.every(Number.isFinite),"Sin medias de temperatura");
const filtered=days.map((x,i)=>i).filter(i=>days[i]!=="2027-02-16");
const partial=parse({time:filtered.map(i=>days[i]),precipitation_sum:filtered.map(i=>rain[i]),temperature_2m_mean:filtered.map(i=>temp[i])},months);
assert(Number.isNaN(partial.rainfall[3])&&Number.isNaN(partial.temperature[3])&&partial.complete[3]===false,"Mes parcial no debe publicarse");
assert(partial.rainfall.filter(Number.isFinite).length===5,"Meses válidos deben permanecer");
let duplicate;try{parse({time:[...days,...days.slice(-1)],precipitation_sum:[...rain,2],temperature_2m_mean:[...temp,25]},months)}catch(e){duplicate=e}
assert(duplicate?.message.includes("repetidas"),"No bloquea fechas repetidas");
console.log("UX44 OK: 6 meses válidos, febrero, mes incompleto excluido, contador retirado.");
