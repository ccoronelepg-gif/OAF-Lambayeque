/* OAF-Lambayeque 8M — visualización observacional de vecindad de grillas.
 * Únicamente usa respuestas científicas verificadas y publicadas de Open-Meteo.
 * Las "diferencias" son de reanálisis, no mediciones SENAMHI ni alertas.
 */
(()=>{
 "use strict";
 const main=document.getElementById("oaf-neighbour-8m");
 if(!main)return;
 const el=id=>document.getElementById(id);
 const select=el("oaf-8m-site"),state=el("oaf-8m-state"),
       table=el("oaf-8m-table"),chart=el("oaf-8m-plot"),
       compass=el("oaf-8m-compass"),directionLabel=el("oaf-8m-direction");
 const directions=["NW","N","NE","W","C","E","SW","S","SE"];
 const sites=["Chiclayo","Jayanca","Motupe","Olmos"];
 let report=null,points=[],pairs=[],selected="E",initialized=false;
 const format=(x,n=2)=>typeof x==="number"&&Number.isFinite(x)
   ?x.toLocaleString("es-PE",{minimumFractionDigits:n,maximumFractionDigits:n}):"No evaluable";
 const td=(row,value)=>{const n=document.createElement("td");n.textContent=String(value);row.append(n)};
 const svg=(tag,attributes={},content)=>{
   const n=document.createElementNS("http://www.w3.org/2000/svg",tag);
   for(const [key,value] of Object.entries(attributes))n.setAttribute(key,String(value));
   if(content!==undefined)n.textContent=content;
   return n;
 };
 function buildChart(){
   chart.replaceChildren();
   const loc=select.value;
   const sample=pairs.filter(x=>x.localidad===loc&&x.direccion===selected);
   if(!sample.length){
     const msg=document.createElement("p");msg.className="small";
     msg.textContent="Aún no hay 360 meses válidos para esta dirección. No se generan series simuladas.";
     chart.append(msg);return;
   }
   const years=new Map();
   for(const row of sample){
     const yr=Number(row.mes.slice(0,4));
     if(!years.has(yr))years.set(yr,[]);
     years.get(yr).push(row.delta_tmedia_c);
   }
   const pointsYear=[...years].sort((a,b)=>a[0]-b[0]).map(([year,vals])=>({
     year,diff:vals.reduce((a,b)=>a+b,0)/vals.length
   }));
   if(pointsYear.length!==30||pointsYear.some(x=>!Number.isFinite(x.diff)))return;
   const W=780,H=245,L=52,R=20,T=25,B=42;
   const max=Math.max(.1,...pointsYear.map(x=>Math.abs(x.diff)))*1.15;
   const xx=i=>L+i*(W-L-R)/29;
   const yy=v=>T+(max-v)/(2*max)*(H-T-B);
   const fig=svg("svg",{viewBox:`0 0 ${W} ${H}`,role:"img",
     "aria-label":"Diferencias anuales de temperatura de reanálisis 1996 a 2025"});
   fig.style.cssText="width:100%;height:auto;max-height:275px";
   fig.append(svg("line",{x1:L,x2:W-R,y1:yy(0),y2:yy(0),stroke:"#718896","stroke-width":1.6}));
   [-1,0,1].forEach(k=>{
     fig.append(svg("text",{x:7,y:yy(k*max)+3,fill:"#557285","font-size":11},
       (k*max).toFixed(2)));
   });
   const path=pointsYear.map((v,i)=>(i?"L":"M")+xx(i).toFixed(2)+" "+yy(v.diff).toFixed(2)).join(" ");
   fig.append(svg("path",{d:path,stroke:"#13869d","stroke-width":2.8,fill:"none",
     "stroke-linejoin":"round","stroke-linecap":"round"}));
   pointsYear.forEach((d,i)=>{
     if(i%5===0||i===29)
       fig.append(svg("text",{x:xx(i),y:H-13,"text-anchor":"middle",
         fill:"#506c7d","font-size":11},String(d.year)));
     const dot=svg("circle",{cx:xx(i),cy:yy(d.diff),r:2.5,fill:"#13869d"});
     dot.append(svg("title",{},d.year+": "+format(d.diff,3)+" °C"));
     fig.append(dot);
   });
   fig.append(svg("text",{x:L,y:14,"font-size":12,fill:"#395c70"},
     "Vecino "+selected+" menos centro (°C)"));
   chart.append(fig);
 }
 function draw(){
   if(!report)return;
   const place=select.value;
   const set=report.por_localidad[place];
   const mine=points.filter(x=>x.localidad===place);
   const map=new Map(mine.map(x=>[x.direccion,x]));
   el("oaf-8m-count").textContent=String(report.n_pares_mensuales);
   el("oaf-8m-grid").textContent=set.n_vecinos_con_celda_distinta===null
     ?"—":String(set.n_vecinos_con_celda_distinta)+"/8";
   el("oaf-8m-anomaly").textContent=format(set.max_mae_diferencia_anomalias_c);
   compass.replaceChildren();
   for(const name of directions){
     const item=map.get(name);
     const cell=document.createElement("button");
     cell.type="button";
     cell.style.cssText="min-height:66px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:2px;border:1px solid #bfd6df;border-radius:10px;cursor:pointer";
     if(name==="C"){
       cell.disabled=true;
       cell.style.background="#e8f0f2";
       cell.textContent="Centro";
     }else{
       const m=item?.mae_tmedia_c;
       const intensity=typeof m==="number"?Math.min(100,Math.round(m/2*100)):0;
       cell.style.background=m===undefined?"#f0f4f5":`hsl(190 42% ${96-intensity*0.32}%)`;
       const label=document.createElement("strong");label.textContent=name;
       const value=document.createElement("small");
       value.textContent=typeof m==="number"?format(m,2)+" °C":"—";
       cell.append(label,value);
       if(name===selected)cell.style.outline="3px solid #157fa0";
       cell.setAttribute("aria-pressed",String(name===selected));
       cell.addEventListener("click",()=>{
         selected=name;draw();
       });
     }
     cell.title=name==="C"?"Punto de referencia original":(item?
       "Dirección "+name+"; cambio de píxel: "+(item.celda_distinta?"sí":"no"):"Sin datos disponibles");
     compass.append(cell);
   }
   table.replaceChildren();
   for(const name of directions.filter(x=>x!=="C")){
     const x=map.get(name),r=document.createElement("tr");
     td(r,name);
     td(r,x?format(x.distancia_solicitud_centro_km):"—");
     td(r,x?format(x.mae_tmedia_c):"—");
     td(r,x?format(x.max_abs_delta_c):"—");
     td(r,x?format(x.mae_diferencia_anomalias_c):"—");
     td(r,x?(x.celda_distinta?"Sí":"No"):"—");
     table.append(r);
   }
   const candidate=map.get(selected);
   directionLabel.textContent=candidate?
     select.value+" · "+selected+" · "+format(candidate.distancia_solicitud_centro_km,2)+
     " km desde el centro · "+(candidate.celda_distinta?"píxel diferente":"mismo píxel")+
     " · altitud API Δ "+format(candidate.delta_elevacion_api_vs_centro_m,1)+" m":
     "Seleccione un rumbo con resultados verificables";
   buildChart();
 }
 async function load(){
   state.textContent="Revisando las fuentes originales de sensibilidad espacial y las series mensuales…";
   try{
     const [rv,rc]=await Promise.all([
       fetch("datos/sensibilidad_vecindad_8m/vista_8m.json",{cache:"no-store"}),
       fetch("datos/sensibilidad_vecindad_8m/pares_mensuales_8m.csv",{cache:"no-store"})
     ]);
     if(!rv.ok||!rc.ok)throw Error("No hay informes 8M disponibles");
     const v=await rv.json(),text=await rc.text();
     const lines=text.trim().split(/\r?\n/),header=lines.shift().split(",");
     if(v.fase!=="8M"||v.no_validacion_instrumental!==true||
        v.no_habilidad_predictiva_demostrada!==true||
        !Array.isArray(v.puntos)||!sites.every(x=>v.por_localidad?.[x])||
        !["localidad","direccion","mes","delta_tmedia_c"].every(k=>header.includes(k)))
       throw Error("El reporte no acredita sus condiciones de transparencia");
     const parsed=[];
     for(const line of lines){
       if(!line.trim())continue;
       const cells=line.split(",");
       if(cells.length!==header.length)throw Error("Fila CSV mensual incompatible");
       const r=Object.fromEntries(header.map((k,i)=>[k,cells[i]]));
       if(!sites.includes(r.localidad)||!directions.includes(r.direccion)||r.direccion==="C"||
          !/^\d{4}-(0[1-9]|1[0-2])$/.test(r.mes))
         throw Error("Punto, mes o rumbo inesperado");
       const delta=Number(r.delta_tmedia_c);
       if(!Number.isFinite(delta))throw Error("Diferencia de temperatura no numérica");
       r.delta_tmedia_c=delta;
       parsed.push(r);
     }
     if(v.resultados_disponibles){
       if(v.n_pares_mensuales!==11520||parsed.length!==11520||v.puntos.length!==36||
          sites.some(s=>parsed.filter(x=>x.localidad===s).length!==2880))
         throw Error("Cobertura espacial 1996–2025 incompleta");
     }else if(parsed.length||v.n_pares_mensuales!==0||v.puntos.length)
       throw Error("El informe pendiente no puede contener resultados incompletos");
     report=v;points=v.puntos;pairs=parsed;draw();
     state.textContent=v.resultados_disponibles
       ?"Sensibilidad descriptiva de reanálisis en 36 posiciones; los cambios incluyen elección de píxel y ajuste de elevación del proveedor. No son mediciones de parcela ni precisión prospectiva."
       :"No están archivadas las doce fuentes históricas necesarias. No se presentan valores simulados.";
   }catch(err){
     report=null;points=[];pairs=[];
     table.replaceChildren();chart.replaceChildren();compass.replaceChildren();
     state.textContent="Análisis 8M no disponible: "+err.message+
       ". No se sustituyen observaciones por estimaciones ficticias.";
   }
 }
 select.addEventListener("change",()=>{selected="E";draw()});
 el("oaf-8m-refresh")?.addEventListener("click",load);
 main.addEventListener("toggle",()=>{if(main.open&&!initialized){initialized=true;load()}});
})();
