/* 9W: comparación histórica GCN/Random Forest con referencias honestas. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const fmt=(n,d=2)=>typeof n==="number"&&Number.isFinite(n)?n.toLocaleString("es-PE",{minimumFractionDigits:0,maximumFractionDigits:d}):"—";
const text=(id,value)=>{const n=$(id);if(n)n.textContent=value};
async function load(path){const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("Reporte no disponible");return r.json()}
const name={climatologia:"Climatología del entrenamiento",
 random_forest:"Random Forest",gcn:"Red convolucional de grafos (GCN)",
 persistencia:"Persistencia estacional"};
const title={ "9R":"9R: entrenamiento hasta 2015; prueba 2021–2025",
"9R_2022_2025":"9R: mismos modelos, solo años 2022–2025",
"9T":"9T: entrenamiento hasta 2018; prueba 2022–2025"};
function cell(row,v){const e=document.createElement("td");e.textContent=String(v);row.append(e)}
async function render(){
 if(!$("oaf-9w-visor"))return;
 try{
  const data=await load("datos/validacion_9w/evaluacion_bloques_9w.json");
  const a=data.auditoria_matriz_9q_sectorial;
  if(data.fase!=="9W"||data.modelo_operativo_habilitado!==false||
    data.verificacion_as_issued_de_variables_rezagadas!==false||
    data.validacion_espacial_con_sectores_ausentes_en_entrenamiento!==false||
    a.meses_CHIRPS_final_verificados!==360||
    a.n_sectores_aptos_historia_CHIRPS!==39)
     throw Error("Integridad científica de la evaluación no aprobada");
  text("oaf-9w-status","CHIRPS v3 final 1996–2025: 360 meses comprobados, "+
    a.n_sectores_aptos_historia_CHIRPS+" sectores evaluables de 42. "+
    "El objetivo 9R fue cotejado con "+a.auditoria_de_objetivos_9R.n_comparaciones+
    " observaciones del archivo original. Análisis histórico retrospectivo, no pronóstico emitido.");
  const sel=$("oaf-9w-protocol");
  for(const item of data.modelos_y_pruebas){
    const opt=document.createElement("option");opt.value=item.protocolo;
    opt.textContent=title[item.protocolo]||item.protocolo;sel.append(opt);
  }
  function draw(){
    const x=data.modelos_y_pruebas.find(p=>p.protocolo===sel.value);
    if(!x)return;
    const tbody=$("oaf-9w-grid");tbody.replaceChildren();
    for(const [model,m] of Object.entries(x.metrica_modelos)){
      const row=document.createElement("tr");
      [name[model]||model,fmt(m.mae_mm,2)+" mm",
       fmt(m.rmse_mm,2)+" mm",
       fmt(x.skill_MAE_vs_climatologia_pct[model],1)+" %",
       x.casos_sector_mes_por_modelo].forEach(v=>cell(row,v));
      tbody.append(row);
    }
    text("oaf-9w-comparison",x.ganador_por_mae_incluyendo_baselines+
     " presenta el menor MAE dentro de "+(title[x.protocolo]||x.protocolo)+
     ". Esta clasificación corresponde exclusivamente a este diseño temporal.");
    const lines=[];
    for(const v of Object.values(x.comparacion_errores_emparejados)){
       const dir=v.delta_mae_mm_positivo_es_peor>0?"peor que":"mejor que";
       lines.push((name[v.comparacion.split("_menos_")[0]]||v.comparacion.split("_menos_")[0])+
         " frente a "+(name[v.comparacion.split("_menos_")[1]]||v.comparacion.split("_menos_")[1])+
         ": ΔMAE "+fmt(v.delta_mae_mm_positivo_es_peor,2)+
         " mm ("+dir+"); intervalo bootstrap anual 95 % ["+
         v.intervalo_bootstrap_anual_95_pct_mm.map(y=>fmt(y,2)).join("; ")+
         "] mm; "+v.n_bloques_anio+" bloques anuales.");
    }
    text("oaf-9w-details",lines.join(" "));
  }
  sel.addEventListener("change",draw);sel.value="9R";draw();
 }catch(e){
  text("oaf-9w-status","Evaluación 9W no disponible o no auditada: "+e.message+
    ". Se conservan los resultados publicados de 9R.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",render);
else render();
})();