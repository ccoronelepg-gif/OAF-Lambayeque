/* OAF 10E — comparador público de predicciones experimentales del autor.
   Never claims official issuance, operational validation or active alerts. */
(function(){
 "use strict";
 const labels={RF_multivariable:"Random Forest · multivariable",
   GCN_multivariable:"GCN · multivariable",RF_solo_lluvia:"Random Forest · solo lluvia",
   GCN_solo_lluvia:"GCN · solo lluvia",
   climatologia_local_estacional:"Climatología local estacional"};
 const fmt=(v,digits=4)=>Number(v).toLocaleString("es-PE",{minimumFractionDigits:digits,maximumFractionDigits:digits});
 const box=document.getElementById("oaf-10e-resultados");
 if(!box)return;
 const cell=(tr,value)=>{const td=document.createElement("td");td.textContent=String(value);tr.append(td);};
 async function draw(){
  try{
   const response=await fetch("datos/probabilidades_10e/evaluacion_probabilistica_10e.json",{cache:"no-store"});
   if(!response.ok)throw Error("No hay un informe 10E publicado");
   const data=await response.json();
   if(data.fase!=="10E"||data.alertas_habilitadas!==false||
       data.modelo_operativo_certificado!==null||
       data.as_issued_disponible!==false||data.transferencia_espacial_validada!==false)
     throw Error("No se pudo certificar el alcance experimental");
   const h=document.createElement("p");
   h.className="small";
   h.textContent="Prueba histórica 2021–2025 · "+data.n_muestras_por_modelo.prueba+
     " observaciones localidad-mes · probabilidad de superar el percentil 90 histórico de cada localidad. Brier: menor es mejor.";
   const tbl=document.createElement("table"),thead=document.createElement("thead"),head=document.createElement("tr");
   for(const label of ["Método","Brier","PR-AUC","Eventos reales / casos"]) {
    const th=document.createElement("th");th.textContent=label;head.append(th);
   }
   thead.append(head);tbl.append(thead);
   const tbody=document.createElement("tbody");
   const order=["climatologia_local_estacional","RF_multivariable","GCN_multivariable",
                "RF_solo_lluvia","GCN_solo_lluvia"];
   for(const m of order){
    const r=data.resultados[m].global,tr=document.createElement("tr");
    for(const v of [labels[m],fmt(r.brier,4),fmt(r.pr_auc,4),r.eventos+" / "+r.n])cell(tr,v);
    tbody.append(tr);
   }
   tbl.append(tbody);
   const scroller=document.createElement("div");scroller.className="scroller";scroller.append(tbl);
   const detail=document.createElement("p");detail.className="oaf-figure-caption";
   const best=data.modelo_destacado_experimental_si_supera_climatologia;
   detail.textContent=best?
    "Modelo experimental destacado por sus métricas retrospectivas: "+labels[best]+
    ". Esto NO habilita predicciones operativas.":
    "No se acredita un ganador operativo. RF multivariable obtuvo el menor Brier de los algoritmos de IA, pero la climatología local tuvo mejores métricas. Se muestran ambos para evaluación científica.";
   const loc=document.createElement("p");loc.className="small";
   loc.textContent="Umbrales P90 aprendidos en entrenamiento (mm/mes): "+
    Object.entries(data.objetivo_umbral_p90_local_mm)
     .map(([name,v])=>name+" "+fmt(v,1)).join(" · ")+".";
   const note=document.createElement("p");note.className="notice";
   note.textContent="Advertencia: datos ERA5 y NOAA reprocesados, sin emisiones originales ni validación de estaciones independientes. Comparación válida solo para Chiclayo, Jayanca, Motupe y Olmos; NO para los 39 sectores de CHIRPS. Las corrientes geostróficas no se incluyeron porque su archivo cubre solamente 2017–2025. Cero alertas activas.";
   box.replaceChildren(h,scroller,detail,loc,note);
  }catch(e){
   const m=document.createElement("p");m.className="small";
   m.textContent="Resultados experimentales no disponibles o sin validación de procedencia; se mantienen deshabilitadas las alertas. Consulte el documento de metodología.";
   box.replaceChildren(m);
  }
 }
 draw();
})();
