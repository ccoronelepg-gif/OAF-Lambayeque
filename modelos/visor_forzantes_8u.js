(()=>{
"use strict";
const root=document.getElementById("oaf-factors-8u");if(!root)return;
const $=id=>document.getElementById(id);
const msg=$("oaf-8u-extra-status");
const bodies=[$("oaf-8u-extra-wind-table"),$("oaf-8u-extra-ocean-table"),$("oaf-8u-extra-current-table")];
const number=x=>Number.isFinite(+x)?Number(x).toLocaleString("es-PE",{maximumFractionDigits:3}):"—";
function csv(text){
 let lines=text.trim().split(/\r?\n/);
 if(!lines.length)return[];
 const keys=lines.shift().split(",");
 return lines.filter(Boolean).map(line=>{
  const vals=line.split(",");
  if(vals.length!==keys.length)throw Error("CSV no tiene esquema esperado");
  return Object.fromEntries(keys.map((k,i)=>[k,vals[i]]));
 });
}
function add(t,items){
 const tr=document.createElement("tr");
 for(const v of items){const td=document.createElement("td");td.textContent=String(v);tr.append(td)}
 t.append(tr);
}
async function read(path,json=true){
 const response=await fetch(path,{cache:"no-store"});
 if(!response.ok)throw Error("No disponible: "+path);
 return json?response.json():csv(await response.text());
}
async function update(){
 msg.textContent="Auditoría de vientos atmosféricos, SST regional y corrientes geostróficas…";
 try{
  const [w,s,c,wr,sr,cr]=await Promise.all([
   read("datos/meteorologia_8u/estado_viento_8u.json"),
   read("datos/oceanografia_8u/estado_oceanografia_8u.json"),
   read("datos/corrientes_8u/estado_corrientes_8u.json"),
   read("datos/meteorologia_8u/vientos_mensuales_8u.csv",false),
   read("datos/oceanografia_8u/tsm_nino12_mensual_8u.csv",false),
   read("datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv",false)]);
  if(w.fase!=="8U"||s.fase!=="8U"||c.fase!=="8U"||
     w.viento_inferido_no_es_corriente_oceanica!==true||
     s.tsm_costa_lambayeque_medido!==false||
     c.periodo_1996_2025_de_corrientes_completo!==false||
     sr.length!==360||wr.length!==w.n_filas_publicadas||
     cr.length!==c.n_filas_geostroficas_reales_fuente_modelada_publicadas||
     wr.some(x=>x.observacion_instrumental!=="false")||
     cr.some(x=>x.observacion_directa_campo!=="false"))
       throw Error("Fuentes o unidades no auditadas");
  bodies.forEach(x=>x.replaceChildren());
  $("oaf-8u-extra-wind").textContent=w.n_bloques_verificados+"/3";
  $("oaf-8u-extra-sst").textContent=String(sr.length);
  $("oaf-8u-extra-currents").textContent=c.n_series_punto_periodo_verificadas+"/4";
  for(const month of ["1997-03","1998-03","2017-03","2023-03","2025-12"]){
    const r=sr.find(x=>x.mes===month);
    if(r)add(bodies[1],[r.mes,number(r.tsm_nino12_c),number(r.anomalia_tsm_nino12_c)]);
  }
  if(wr.length===2160){
   for(const place of ["Chiclayo","Jayanca","Motupe","Olmos","Mar_frente_Pimentel","Mar_norte_Lambayeque"]){
    const rows=wr.filter(x=>x.sitio===place),N=rows.length;
    if(N!==360)throw Error("Series de viento incompletas por punto");
    const avg=k=>number(rows.reduce((sum,x)=>sum+(+x[k]),0)/N);
    add(bodies[0],[place,rows[0].ambiente,avg("velocidad_media_10m_m_s"),
      avg("componente_este_aprox_m_s"),avg("componente_norte_aprox_m_s")]);
   }
  }else add(bodies[0],["Climatología pendiente",w.n_bloques_verificados+"/3","—","—","—"]);
  if(cr.length){
   for(const place of [...new Set(cr.map(x=>x.punto))]){
    const rows=cr.filter(x=>x.punto===place);
    const average=k=>number(rows.reduce((sum,x)=>sum+(+x[k]),0)/rows.length);
    add(bodies[2],[place,String(rows.length)+" meses",average("u_este_geostrofica_m_s"),
       average("v_norte_geostrofica_m_s"),"Solo geostrófica"]);
   }
  }else add(bodies[2],["Pendiente",c.n_series_punto_periodo_verificadas+"/4","—","—","No imputada"]);
  msg.textContent="NOAA Niño 1+2: 360 meses de SST regional. Viento ERA5: "+
    w.n_bloques_verificados+"/3 bloques. Corrientes geostróficas NOAA/AOML: "+
    c.n_series_punto_periodo_verificadas+"/4 fuentes parciales 2017–2025. "+
    "No son mediciones directas frente a la costa ni predicciones ENSO validadas.";
 }catch(e){
  bodies.forEach(x=>x.replaceChildren());
  msg.textContent="No hay evidencia publicable completa: "+e.message;
 }
}
$("oaf-8u-extra-refresh")?.addEventListener("click",update);
let started=false;root.addEventListener("toggle",()=>{if(root.open&&!started){started=true;update()}});
})();