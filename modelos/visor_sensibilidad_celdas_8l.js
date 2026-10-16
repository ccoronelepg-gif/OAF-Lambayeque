/* OAF-Lambayeque fase 8L: datos históricos REALES únicamente.
   Compara selección de celda, nunca observaciones SENAMHI o predicciones.
*/
(()=>{
 "use strict";
 const panel=document.getElementById("oaf-sensitivity-8l");
 if(!panel)return;
 const $=id=>document.getElementById(id);
 const site=$("oaf-8l-site"),plot=$("oaf-8l-plot"),table=$("oaf-8l-table"),state=$("oaf-8l-status");
 let report=null,rows=[],started=false;
 const format=(x,dec=2)=>typeof x==="number"&&Number.isFinite(x)
   ?x.toLocaleString("es-PE",{minimumFractionDigits:dec,maximumFractionDigits:dec}):"No evaluable";
 function add(td,text){const node=document.createElement("td");node.textContent=String(text);td.append(node)}
 function textSVG(tag,attrs,txt){
   const x=document.createElementNS("http://www.w3.org/2000/svg",tag);
   for(const [k,v] of Object.entries(attrs||{}))x.setAttribute(k,String(v));
   if(txt!==undefined)x.textContent=txt;return x;
 }
 function chart(yearly){
   plot.replaceChildren();
   if(!yearly.length){
     const p=document.createElement("p");p.className="small";
     p.textContent="No hay series históricas completas verificadas. No se generan gráficos ficticios.";
     plot.append(p);return;
   }
   const W=780,H=292,left=60,right=18,top=32,bottom=48;
   const vals=yearly.map(r=>r.delta);
   const abs=Math.max(.1,...vals.map(Math.abs))*1.2;
   const Y=v=>top+(abs-v)*((H-top-bottom)/(2*abs));
   const X=i=>left+i*(W-left-right)/(yearly.length-1);
   const svg=textSVG("svg",{viewBox:`0 0 ${W} ${H}`,
     role:"img","aria-label":"Cambio anual de temperatura al seleccionar celda nearest en lugar de land"});
   svg.classList.add("oaf-chart");
   svg.style.cssText="width:100%;height:auto;max-height:315px";
   for(let k=-2;k<=2;k++){
     const t=k*abs/2,y=Y(t);
     svg.append(textSVG("line",{x1:left,x2:W-right,y1:y,y2:y,
       stroke:k===0?"#57798b":"#d9e8ed","stroke-width":k===0?1.6:1}));
     svg.append(textSVG("text",{x:left-8,y:y+4,"text-anchor":"end",
       fill:"#406073","font-size":11},t.toFixed(2)));
   }
   const path=yearly.map((r,i)=>(i?"L":"M")+X(i).toFixed(2)+","+Y(r.delta).toFixed(2)).join(" ");
   svg.append(textSVG("path",{d:path,stroke:"#087f92",fill:"none","stroke-width":2.8,
     "stroke-linejoin":"round","stroke-linecap":"round"}));
   yearly.forEach((r,i)=>{
     if(i%5===0||i===yearly.length-1)svg.append(textSVG("text",{
       x:X(i),y:H-17,"text-anchor":"middle",fill:"#395a6c","font-size":11},String(r.year)));
     const c=textSVG("circle",{cx:X(i),cy:Y(r.delta),r:2.8,fill:"#087f92"});
     const title=textSVG("title",{},r.year+": "+format(r.delta,3)+" °C");
     c.append(title);svg.append(c);
   });
   svg.append(textSVG("text",{x:left,y:18,fill:"#395a6c","font-size":12},
     "Diferencia media anual: nearest − land (°C)"));
   plot.append(svg);
 }
 function render(){
   if(!report)return;
   table.replaceChildren();
   for(const name of ["Chiclayo","Jayanca","Motupe","Olmos"]){
     const value=report.por_localidad[name];
     const tr=document.createElement("tr");
     add(tr,name);add(tr,value.n);
     add(tr,format(value.mae_entre_selecciones_c));
     add(tr,format(value.max_abs_diferencia_c));
     add(tr,format(value.mae_diferencia_anomalias_c));
     add(tr,value.centros_distintos===null?"No evaluable":value.centros_distintos?"Sí":"No");
     table.append(tr);
   }
   const selected=report.por_localidad[site.value];
   $("oaf-8l-complete").textContent=report.resultado_disponible?String(report.n_pares_mensuales):"0";
   $("oaf-8l-mean").textContent=format(selected.mae_entre_selecciones_c);
   $("oaf-8l-max").textContent=format(selected.max_abs_diferencia_c);
   const grouped=new Map();
   for(const r of rows.filter(r=>r.localidad===site.value)){
     const year=Number(r.mes.slice(0,4));
     if(!grouped.has(year))grouped.set(year,[]);
     grouped.get(year).push(r.diferencia_nearest_menos_land_c);
   }
   const years=[...grouped.entries()].sort((a,b)=>a[0]-b[0])
     .map(([year,values])=>({year,delta:values.reduce((a,b)=>a+b,0)/values.length}));
   chart(years);
 }
 async function load(){
   state.textContent="Consultando fuentes 8L y verificando los pares mensuales…";
   try{
     const [res,csvRes]=await Promise.all([
       fetch("datos/sensibilidad_celdas_8l/estado_8l.json",{cache:"no-store"}),
       fetch("datos/sensibilidad_celdas_8l/pares_mensuales_8l.csv",{cache:"no-store"})]);
     if(!res.ok||!csvRes.ok)throw Error("No existen archivos 8L disponibles");
     const obj=await res.json(),txt=await csvRes.text(),lines=txt.trim().split(/\r?\n/);
     const fields=lines.shift().split(",");
     const required=["localidad","mes","diferencia_nearest_menos_land_c"];
     if(obj.fase!=="8L"||obj.habilidad_prospectiva_8e_demostrada!==false||
        obj.independencia_instrumental_demostrada!==false||
        obj.apto_para_alertas_niño_o_fitosanitarias!==false||
        obj.celdas_8d_originales_inequivocamente_identificadas!==false||
        !required.every(k=>fields.includes(k))||typeof obj.resultado_disponible!=="boolean")
       throw Error("Estado científico o estructura incompatible");
     const parsed=[];
     for(const line of lines){
       if(!line.trim())continue;
       const parts=line.split(",");
       if(parts.length!==fields.length)throw Error("Fila CSV incorrecta");
       const r=Object.fromEntries(fields.map((k,i)=>[k,parts[i]]));
       const val=Number(r.diferencia_nearest_menos_land_c);
       if(!["Chiclayo","Jayanca","Motupe","Olmos"].includes(r.localidad)||
          !/^\d{4}-(0[1-9]|1[0-2])$/.test(r.mes)||
          !Number.isFinite(val))throw Error("Valor climático CSV inválido");
       r.diferencia_nearest_menos_land_c=val;
       parsed.push(r);
     }
     if(obj.resultado_disponible &&
       (obj.n_pares_mensuales!==1440||parsed.length!==1440||
        ["Chiclayo","Jayanca","Motupe","Olmos"].some(s=>parsed.filter(x=>x.localidad===s).length!==360)))
       throw Error("El análisis completo requiere 360 meses por localidad");
     if(!obj.resultado_disponible&&(parsed.length!==0||obj.n_pares_mensuales!==0))
       throw Error("Estado pendiente con filas indebidamente presentes");
     report=obj;rows=parsed;render();
     state.textContent=obj.resultado_disponible
       ?"Comparación histórica 1996–2025 de ambos criterios de celda; reanálisis, no medición SENAMHI ni validación predictiva. Los efectos de ajuste de elevación del proveedor no se aíslan automáticamente."
       :"No hay seis bloques históricos completos verificados. El sistema no sustituye resultados ausentes por simulaciones.";
   }catch(err){report=null;rows=[];table.replaceChildren();plot.replaceChildren();
     state.textContent="No se puede mostrar una comparación verificable: "+err.message;}
 }
 site.addEventListener("change",render);
 $("oaf-8l-refresh")?.addEventListener("click",load);
 panel.addEventListener("toggle",()=>{if(panel.open&&!started){started=true;load()}});
})();
