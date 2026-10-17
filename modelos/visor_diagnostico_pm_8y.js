/* OAF 8Y: asociaciones PM vs clima, sin predicción ni causalidad. */
(()=>{
"use strict";
const panel=document.getElementById("oaf-diagnostico-8y");
if(!panel)return;
const e=id=>document.getElementById(id);
const loc=e("oaf-8y-localidad"),pm=e("oaf-8y-pm");
const plot=e("oaf-8y-correlations"),table=e("oaf-8y-table"),message=e("oaf-8y-message");
let data=null;
const names={
  viento_10m_m_s:"Velocidad del viento",
  precipitacion_mes_mm:"Precipitación mensual",
  temperatura_aire_c:"Temperatura del aire",
  radiacion_mes_mj_m2:"Radiación corta",
  anomalia_nino12_c:"SST Niño 1+2 (regional)"
};
function node(tag, attrs, str){
  const x=document.createElementNS("http://www.w3.org/2000/svg",tag);
  Object.entries(attrs).forEach(([k,v])=>x.setAttribute(k,String(v)));
  if(str!==undefined)x.textContent=String(str);
  return x;
}
function fmt(v){return typeof v==="number"&&Number.isFinite(v)?v.toFixed(3):"Sin evidencia suficiente";}
function render(){
  if(!data)return;
  const rows=data.comparaciones.filter(x=>x.localidad===loc.value&&x.particula===pm.value);
  table.replaceChildren();plot.replaceChildren();
  let found=0;
  rows.forEach((r,i)=>{
    const tr=document.createElement("tr");
    for(const str of [names[r.meteorologia]||r.meteorologia,fmt(r.pearson_bruto),
                      fmt(r.pearson_sin_ciclo_mensual),String(r.meses_comunes),
                      r.signo_sin_ciclo_estable===null?"No evaluable":r.signo_sin_ciclo_estable?"Sí (exploratorio)":"No"]){
      const td=document.createElement("td");td.textContent=str;tr.append(td);
    }
    table.append(tr);
    if(r.pearson_sin_ciclo_mensual===null)return;
    found++;
    const y=42+i*57, x0=380, barwidth=Math.abs(r.pearson_sin_ciclo_mensual)*250;
    plot.append(node("text",{x:8,y:y+6,"font-size":14,fill:"currentColor"},names[r.meteorologia]||r.meteorologia));
    plot.append(node("line",{x1:x0,y1:y-19,x2:x0,y2:y+17,stroke:"currentColor",opacity:.5}));
    plot.append(node("rect",{x:r.pearson_sin_ciclo_mensual>=0?x0:x0-barwidth,y:y-11,width:barwidth,height:20,
                            fill:r.pearson_sin_ciclo_mensual>=0?"#278c78":"#b06d54",rx:2}));
    plot.append(node("text",{x:650,y:y+6,"font-size":13,fill:"currentColor"},
                         fmt(r.pearson_sin_ciclo_mensual)));
  });
  const duplicate=(data.parejas_series_identicas||[]).filter(p=>p.sitios.includes(loc.value));
  const caution=duplicate.length?
    " El punto seleccionado comparte serie PM idéntica con "+duplicate.map(x=>x.sitios.filter(s=>s!==loc.value).join(", ")).join("; ")+".":"";
  message.textContent=found?rows[0].meses_comunes+
    " meses coincidentes; correlaciones desestacionalizadas de 2023–2025, sin prueba causal ni habilidad predictiva."+caution:
    "No existen 24 meses válidos emparejados para evaluar la asociación. No se muestran valores inventados."+caution;
  e("oaf-8y-cell-unique").textContent=String(data.n_series_pm_unicas_en_periodo);
}
async function load(){
  if(data)return render();
  message.textContent="Revisando matriz de aerosol y clima...";
  try{
    const r=await fetch("datos/diagnostico_pm_8y/estado_diagnostico_pm_8y.json",{cache:"no-store"});
    if(!r.ok)throw Error("Resultados 8Y todavía no archivados");
    const d=await r.json();
    if(d.fase!=="8Y"||d.inferencia_causal_permitida!==false
       ||d.alertas_por_pm_o_fitosanidad_aprobadas!==false)
       throw Error("Metadatos de seguridad incompatibles");
    data=d;
    e("oaf-8y-overlap").textContent=d.n_meses_pm_con_cobertura.toLocaleString("es-PE");
    e("oaf-8y-evaluable").textContent=d.n_comparaciones_evaluables+" / "+d.n_comparaciones;
    render();
  }catch(err){message.textContent="Sin serie evaluable: "+err.message;}
}
panel.addEventListener("toggle",()=>{if(panel.open)load()});
[loc,pm].forEach(x=>x.addEventListener("change",render));
if(panel.open)load();
})();
