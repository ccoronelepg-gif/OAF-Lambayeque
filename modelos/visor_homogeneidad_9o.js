/* 9O — clima real 1996-2025, comparaciones exploratorias; no alertas */
(()=>{"use strict";
const $=id=>document.getElementById(id), NS="http://www.w3.org/2000/svg";
const floors={llanura_costa:"Planicie costera",valle_bajo:"Valle bajo",piedemonte:"Piedemonte",montana_baja:"Ladera baja",montana_media:"Ladera media",montana_alta:"Alta montaña",cota_negativa_revisar:"DEM negativo: revisar"};
const num=(v,d=1)=>typeof v==="number"&&Number.isFinite(v)?v.toLocaleString("es-PE",{maximumFractionDigits:d}):"—";
const label=x=>floors[x]||x;
const set=(id,v)=>{if($(id))$(id).textContent=v};
function node(t,props={},value){const e=document.createElementNS(NS,t);for(const [k,v] of Object.entries(props))e.setAttribute(k,String(v));if(value!==undefined)e.textContent=value;return e;}
async function load(path,asText=false){const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw Error("No se encontró "+path);return asText?r.text():r.json();}
function csv(raw){const lines=raw.trim().split(/\r?\n/);const head=lines.shift().split(",");return lines.map(line=>{const values=line.split(","),out={};head.forEach((k,i)=>out[k]=values[i]||"");return out;});}
function chart(rows,sector){
 const plot=$("oaf-9o-plot");plot.replaceChildren();
 const data=Array.from({length:12},(_,i)=>{const e=rows.find(x=>x.sector===sector&&Number(x.mes_calendario)===i+1);return e&&e.precipitacion_chirps_mm!==""?Number(e.precipitacion_chirps_mm):null});
 if(data.every(v=>v===null)){plot.textContent="No se pudieron calcular normales mensuales para este sector.";return;}
 const W=820,H=295,L=48,R=12,T=28,B=42,peak=1.15*Math.max(1,...data.filter(v=>v!==null));
 const fig=node("svg",{viewBox:"0 0 "+W+" "+H,role:"img","aria-label":"Promedio histórico mensual de lluvia CHIRPS, no pronóstico"});
 fig.style.width="100%";
 fig.append(node("line",{x1:L,y1:H-B,x2:W-R,y2:H-B,stroke:"currentColor","stroke-opacity":.35}));
 const names=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
 const step=(W-L-R)/12;
 data.forEach((v,i)=>{
  const x=L+i*step+step*.16;
  if(v!==null){
   const barH=Math.max(1,(H-T-B)*v/peak);
   const e=node("rect",{x:x,y:H-B-barH,width:step*.68,height:barH,rx:3,fill:i<3?"#358b9e":"#72a98b"});
   e.append(node("title",{},names[i]+": "+num(v,2)+" mm/mes"));fig.append(e);
  }else fig.append(node("rect",{x:x,y:H-B-6,width:step*.68,height:6,fill:"#b88c86"}));
  fig.append(node("text",{x:L+(i+.5)*step,y:H-B+20,"text-anchor":"middle","font-size":12,fill:"currentColor"},names[i]));
 });
 for(const f of [0,.5,1])fig.append(node("text",{x:L-8,y:H-B-(H-T-B)*f+4,"text-anchor":"end","font-size":11,fill:"currentColor"},num(f*peak,0)));
 fig.append(node("text",{x:L+8,y:15,"font-size":12,fill:"currentColor"},"Precipitación mensual CHIRPS v3 (mm)"));
 plot.append(fig);
}
async function start(){
 if(!$("oaf-9o-visor"))return;
 try{
  const path="datos/homogeneidad_9o/";
  const [result,sources,rawNormal,rawWitness]=await Promise.all([
   load(path+"diagnostico_homogeneidad_9o.json"),
   load(path+"fuentes_chirps_9o.json"),
   load(path+"normales_sectoriales_chirps_9o.csv",true),
   load(path+"normales_testigos_multivariable_9o.csv",true)
  ]);
  if(result.fase!=="9O"||sources.fase!=="9O"||result.n_sectores!==42||
     result.zonas_climaticas_homogeneas_certificadas!==0||
     result.modelo_predictivo_validado_por_sectores!==false||
     result.meses_fuente_chirps!==sources.n_meses_reales)
    throw Error("La auditoría de fuentes científicas no es coherente");
  const normals=csv(rawNormal),other=csv(rawWitness);
  if(normals.length!==42*12||other.length!==81*12)throw Error("Faltan climatologías por sector o por testigo");
  set("oaf-9o-months",result.meses_fuente_chirps+" / 360");
  set("oaf-9o-sector-count",result.n_sectores.toString());
  set("oaf-9o-witness-count",result.n_testigos_reanalisis_30anios.toString());
  set("oaf-9o-status",result.periodo_completo_chirps?
   "CHIRPS v3 final: normales 1996–2025 calculadas sobre 360 meses originales contrastados. NO corresponden a estaciones independientes.":
   "CHIRPS v3: "+result.meses_fuente_chirps+" meses históricos comprobados de 360; NO hay climatología completa. Los faltantes no se interpolan.");
  const sel=$("oaf-9o-sector"),byId=new Map(result.resumen_sectores.map(x=>[x.id,x]));
  for(const p of result.resumen_sectores){
   const option=document.createElement("option");option.value=p.id;option.textContent=p.id+" · "+label(p.piso);sel.append(option);
  }
  function draw(){
   const p=byId.get(sel.value);if(!p)return;
   chart(normals,p.id);
   set("oaf-9o-description",p.id+" · "+label(p.piso)+
       ". Lluvia media anual CHIRPS: "+num(p.precipitacion_anual_media_mm)+
       " mm/año de "+p.n_anios_completos+" años completos disponibles. "+
       "Píxeles terrestres presentes (mediana): "+p.n_pixeles_chirps_terrestres_mediana+
       ". La media del polígono no es una medición de finca ni un pronóstico.");
  }
  sel.addEventListener("change",draw);sel.value="S019";draw();
  const tbody=$("oaf-9o-pairs");tbody.replaceChildren();
  for(const p of result.candidatos_hidro_climaticos){
   const tr=document.createElement("tr");
   const vals=[p.sectores.join(" y "),p.unidades_hidrograficas.join(", "),
     num(p.corr_anomalia_log_lluvia_estacional,3),
     p.diferencia_relativa_precipitacion_media===null?"—":num(100*p.diferencia_relativa_precipitacion_media)+" %",
     "No validada"];
   for(const value of vals){const td=document.createElement("td");td.textContent=value;tr.append(td)}
   tbody.append(tr);
  }
  set("oaf-9o-nucleus",result.n_familias_comparadas+" familias de similitud 9K, "+
    result.n_pares_testigos_agrupados_chirps+" pares de testigos consultados. "+
    result.n_celdas_chirps_compartidas_entre_testigos+
    " píxeles CHIRPS fueron reutilizados por más de un testigo, no son observaciones independientes.");
  set("oaf-9o-validation","Validación externa incompleta: "+result.estaciones_instrumentales_9i+
    " estaciones históricas y "+result.meses_estacion_unicos_9i+
    " meses-estación diferentes en 9I; no existen 30 años de observaciones independientes por sector. Sin avisos automáticos de enfermedad ni El Niño Costero.");
 }catch(e){
  set("oaf-9o-status","Resultados climáticos de la fase pendientes: "+e.message+
    ". Se mantienen todos los datos topográficos y tableros 9K–9N.");
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);else start();
})();