/* UX43 · Barras agrupadas, ceros, RF sin fechas y auditoría de entrenamiento. */
"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm");
const script=fs.readFileSync("assets/oaf-ux15-rf-salidas.js","utf8");
const python=fs.readFileSync("modelos/pronostico_rf_experimental_ux15.py","utf8");
const rf=JSON.parse(fs.readFileSync("datos/rf_experimental_ux15.json","utf8"));
const html=fs.readFileSync("index.html","utf8"),sw=fs.readFileSync("sw.js","utf8");
assert(html.includes("oaf-ux15-rf-salidas.js?v=20261027-ux43"));
assert(html.includes("oaf-ux14-reorganizacion.js?v=20261027-ux43"));
assert(sw.includes("oaf-pwa-shell-2026-10-27-ux43"));
for(const piece of [script,fs.readFileSync("assets/oaf-ux14-reorganizacion.js","utf8")])new Function(piece);
assert(script.includes("weeklyBars(output,days,group")&&script.includes("weeklyBars(output,days,lines"),"El pronóstico no usa barras al cargar modelos");
assert(python.includes("backtest_semanal_recursivo")&&python.includes("origin+dt.timedelta(days=6)")&&python.includes('k<origin.isoformat()'),
 "Falta backtest temporal con historia truncada al inicio del horizonte");
assert(python.includes("test_diario_2025_congelado"),"Falta anotación de test congelado");
assert(rf.estado==="candidato_experimental_generado"&&rf.alertas_automaticas===false&&rf.operativo_certificado===false,"RF no es un pronóstico operativo certificado");
assert(rf.control_nuevos_datos?.series_pronosticos_emitidos_son_etiquetas_entrenamiento===false,"No se deben incluir pronósticos emitidos como observaciones");
const daily=rf.metrica_diaria?.backtest_semanal_recursivo;
assert(daily?.n_origenes>=40,"Faltan orígenes de predicción recursiva sin filtración de futuro");
assert(daily.por_horizonte.length===7);
for(let lead=1;lead<=7;lead++){
 const r=daily.por_horizonte[lead-1];
 assert(r.dias_adelante===lead&&r.n>=40);
 for(const field of ["mae_rf_lluvia_mm","mae_climatologia_lluvia_mm","rmse_rf_lluvia_mm","sesgo_rf_lluvia_mm","mae_rf_temperatura_c"]){
  assert(Number.isFinite(r[field]),"Falta métrica "+field+" del día "+lead);
 }
}
// Verificar renderizado SVG sin Playwright y sin servicios externos.
class Node{
 constructor(tag){this.tagName=tag;this.attrs={};this.children=[];this.textContent="";}
 setAttribute(key,value){this.attrs[key]=String(value);}
 append(...nodes){this.children.push(...nodes)}
 replaceChildren(...nodes){this.children=[...nodes]}
}
const document={createElementNS:(_ns,tag)=>new Node(tag)};
const start=script.indexOf("/* UX43 · Barras agrupadas");
const end=script.indexOf("function weeklyOverview(",start);
assert(start>0&&end>start);
const plot=vm.runInNewContext('(()=>{const fmt=(v,p=1)=>Number(v).toLocaleString("es-PE",{maximumFractionDigits:p,minimumFractionDigits:p});'+
 'const document=this.document;'+script.slice(start,end)+'return weeklyBars})()',
 {document}, {timeout:2500});
const chart=new Node("div"),dates=["2026-10-27","2026-10-28","2026-10-29","2026-10-30","2026-10-31","2026-11-01","2026-11-02"];
plot(chart,dates,[
 {name:"Open-Meteo",color:"#278eb8",values:[0,.03,.09,.2,.4,.07,.01]},
 {name:"RF",color:"#aa65b4",values:[0,.02,NaN,NaN,NaN,NaN,NaN]},
 {name:"ERA5",color:"#31946e",values:[.02,.04,.06,.08,.1,.02,.04]}
],"mm/día");
assert(chart.children[0].tagName==="svg");
const nodes=chart.children[0].children;
const rects=nodes.filter(x=>x.tagName==="rect");
assert.equal(rects.length,16,"Barras deben incluir sólo valores finitos: 7+2+7");
const zeros=rects.filter(x=>x.attrs["aria-label"]?.includes(": 0,00 mm/día")||Number(x.attrs.height)===0);
assert(zeros.length>=1&&zeros.some(x=>Number(x.attrs.height)===0),"Un día sin lluvia debe dibujar altura cero");
const ticks=nodes.filter(x=>x.tagName==="text"&&x.attrs["text-anchor"]==="end").map(x=>x.textContent);
assert(ticks.length>=4&&new Set(ticks).size===ticks.length,"El eje Y presenta valores repetidos");
assert(nodes.filter(x=>x.tagName==="text"&&x.textContent.includes("/")).length>=7,"Faltan etiquetas de fechas");
const chart2=new Node("div");
plot(chart2,dates,[{name:"Open-Meteo",color:"#278eb8",values:[24,25,26,27,26,24,23]}],"°C");
assert(chart2.children[0].children.filter(x=>x.tagName==="rect").length===7,"No se grafican barras de temperatura");
console.log("UX43 OK: barras reales agrupadas, lluvia cero, decimales, datos faltantes y 7 horizontes RF recursivos 2025");
