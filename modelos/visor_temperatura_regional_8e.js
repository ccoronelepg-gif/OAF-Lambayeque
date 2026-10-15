/* OAF Fase 8E: original dated temperature issue and subsequent ERA5-Land verification.
 * No official ENFEN/SENAMHI alert, no calibrated probability, no disease risk.
 */
(function(){
"use strict";
const root=document.getElementById("oaf-temp-8e");
if(!root)return;
const btn=document.getElementById("oaf-temp-8e-run");
const filter=document.getElementById("oaf-temp-8e-filter");
const message=document.getElementById("oaf-temp-8e-message");
const table=document.getElementById("oaf-temp-8e-body");
const section=document.getElementById("oaf-temp-8e-data");
const provenance=document.getElementById("oaf-temp-8e-provenance");
const source=document.getElementById("oaf-temp-8e-original");
const fmt=(x,d=2)=>typeof x==="number"&&Number.isFinite(x)?
  x.toLocaleString("es-PE",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
let snapshot=null,ledger=null,started=false;

function draw(){
 if(!snapshot||!ledger)return;
 const months=new Set(snapshot.pronosticos.map(x=>x.mes_objetivo));
 if(months.size!==3)throw Error("El archivo no tiene tres meses objetivo distintos");
 table.replaceChildren();
 let count=0;
 for(const x of snapshot.pronosticos){
  if(filter.value!=="todos"&&filter.value!==x.mes_objetivo)continue;
  const values=[
    x.localidad,x.mes_objetivo,
    fmt(x.pronostico_nino_t300_c)+" °C",
    fmt(x.pronostico_local_c)+" °C",
    x.emitido_antes_inicio_mes?"Antes del inicio":"Intramensual",
    ledger.pronosticos_comparados===0?"Aún sin verificación":"Ver estado en informe"
  ];
  const tr=document.createElement("tr");
  values.forEach(v=>{const td=document.createElement("td");td.textContent=v;tr.appendChild(td)});
  table.appendChild(tr);count++;
 }
 if(!count)throw Error("No hay emisiones para el mes seleccionado");
 provenance.textContent="Emisión original: "+snapshot.emision_peru+
   " · Mes de origen: "+snapshot.mes_origen+
   " · Fuente ERA5-Land 2 m, anomalías Niño 1+2 NOAA NCEI, T300 NOAA/PMEL del mes anterior. "+
   "Comparados con referencia ERA5-Land: "+ledger.pronosticos_comparados+
   " de "+ledger.pronosticos_originales_archivados+
   " · Primera fecha posible: "+(ledger.primera_verificacion_posible||"todavía sin fecha")+
   ". Entrenamiento hasta 2022-12, clima normal fija 1996–2022.";
 source.href="datos/pronosticos_temperatura_regional_8e/"+snapshot.mes_origen+".json";
 message.textContent=ledger.pronosticos_comparados===0?
   "Primera emisión archivada. Ningún mes ha madurado para comprobar el error real. No se asignan aciertos ni probabilidades.":
   "Existen comparaciones exploratorias con reanálisis ERA5-Land; aún no hay validación instrumental ni habilidad operativa demostrada.";
 section.hidden=false;
}

async function load(){
 btn.disabled=true;section.hidden=true;
 message.textContent="Comprobando que las emisiones y el estado posterior tengan procedencia y fechas válidas…";
 try{
  const response=await fetch("datos/verificacion_temperatura_regional_8e.json",{cache:"no-store"});
  if(!response.ok)throw Error("Verificación regional no publicada (HTTP "+response.status+")");
  const j=await response.json();
  if(j.fase!=="8E"||!["esperando_cierre_y_reanalisis","con_comparaciones_prospectivas_experimentales"].includes(j.estado)||
     j.es_icen_oficial!==false||j.es_alerta_enfen!==false||j.es_alerta_senamhi!==false||
     j.validacion_instrumental!==false||j.habilidad_prospectiva_demostrada!==false||
     j.probabilidades_calibradas!==false||!Number.isInteger(j.pronosticos_originales_archivados)||
     !Number.isInteger(j.pronosticos_comparados)||!(/^\d{4}-\d{2}$/.test(j.ultima_emision||"")))
    throw Error("El resumen no cumple las garantías de autenticidad");
  const path="datos/pronosticos_temperatura_regional_8e/"+j.ultima_emision+".json";
  const r=await fetch(path,{cache:"no-store"});
  if(!r.ok)throw Error("Emisión original no disponible");
  const i=await r.json();
  if(i.fase!=="8E"||i.mes_origen!==j.ultima_emision||
     i.es_icen_oficial!==false||i.es_alerta_enfen!==false||
     i.validacion_instrumental!==false||i.habilidad_prospectiva_demostrada!==false||
     !Array.isArray(i.pronosticos)||i.pronosticos.length!==12||
     typeof i.emision_peru!=="string")
    throw Error("El archivo original tiene campos incompatibles");
  const allowed=["Chiclayo","Jayanca","Motupe","Olmos"];
  const pair=new Set();
  for(const x of i.pronosticos){
   if(!allowed.includes(x.localidad)||!Number.isInteger(x.horizonte_meses)||
      x.horizonte_meses<1||x.horizonte_meses>3||
      !Number.isFinite(x.pronostico_local_c)||!Number.isFinite(x.pronostico_nino_t300_c)||
      typeof x.emitido_antes_inicio_mes!=="boolean")throw Error("Algún pronóstico no supera controles");
   const key=x.localidad+"|"+x.mes_objetivo;
   if(pair.has(key))throw Error("Pronóstico duplicado");
   pair.add(key);
  }
  snapshot=i;ledger=j;
  filter.replaceChildren();
  const all=document.createElement("option");all.value="todos";all.textContent="Todos los meses";filter.appendChild(all);
  const months=[...new Set(i.pronosticos.map(x=>x.mes_objetivo))].sort();
  for(const month of months){const option=document.createElement("option");option.value=month;option.textContent=month;filter.appendChild(option)}
  draw();
 }catch(e){
  snapshot=null;ledger=null;
  message.textContent="Sin pronósticos verificables: "+e.message+". No se presentan cifras simuladas.";
 }finally{btn.disabled=false}
}
btn.addEventListener("click",load);
filter.addEventListener("change",()=>{if(snapshot){try{draw()}catch(e){section.hidden=true;message.textContent=e.message}}});
root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;load()}});
})();