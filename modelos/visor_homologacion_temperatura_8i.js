/* OAF 8I: solo cifras calculadas en el pipeline; nunca datos sintéticos en público. */
(()=>{
'use strict';
const root=document.getElementById("oaf-instrumental-8i");
if(!root)return;
const e=id=>document.getElementById(id);
let initialized=false;
const url="datos/homologacion_temperatura_8i/estado_8i.json";
const csvUrl="datos/homologacion_temperatura_8i/comparacion_mensual_8i.csv";
const fmt=v=>typeof v==="number"&&Number.isFinite(v)?
 v.toLocaleString("es-PE",{maximumFractionDigits:3}):"No evaluable";
function addCell(tr,value){const td=document.createElement("td");td.textContent=String(value);tr.appendChild(td)}
async function render(){
 const message=e("oaf-8i-status"),table=e("oaf-8i-localidades"),plot=e("oaf-8i-grafico");
 message.textContent="Verificando el estado de homologación instrumental…";
 try{
   const [r,check]=await Promise.all([fetch(url,{cache:"no-store"}),fetch(csvUrl,{cache:"no-store"})]);
   if(!r.ok||!check.ok)throw Error("No se encuentran los reportes publicados");
   const data=await r.json();
   const csv=await check.text();
   if(data.fase!=="8I"||data.habilidad_prospectiva_8e_demostrada!==false||
     data.validacion_instrumental_independiente_certificada!==false||
     data.intervalos_predictivos_90_calibrados!==false||
     !Number.isInteger(data.n_meses_con_pares_estacion_era5)||
     !Number.isInteger(data.n_archivos_fuente_autorizados)||
     !csv.startsWith("codigo_estacion,nombre_estacion,mes,"))throw Error("El informe no supera controles de verificación");
   e("oaf-8i-archivos").textContent=String(data.n_archivos_fuente_autorizados);
   e("oaf-8i-completos").textContent=String(data.n_meses_completos);
   e("oaf-8i-pares").textContent=String(data.n_meses_con_pares_estacion_era5);
   const all=data.por_localidad||{},sites=["Chiclayo","Jayanca","Motupe","Olmos"];
   table.replaceChildren();plot.replaceChildren();
   let valid=0;
   for(const city of sites){
     const dataCity=all[city];
     if(!dataCity||!Number.isInteger(dataCity.n))throw Error("Falta localidad o número de contrastes");
     const tr=document.createElement("tr");
     addCell(tr,city);addCell(tr,dataCity.n);addCell(tr,fmt(dataCity.mae_c));
     addCell(tr,fmt(dataCity.rmse_c));addCell(tr,fmt(dataCity.sesgo_c));
     table.append(tr);
     valid+=dataCity.n;
   }
   if(valid!==data.n_meses_con_pares_estacion_era5)throw Error("Conteos por localidad inconsistentes");
   if(valid===0){
      const p=document.createElement("p");
      p.className="small";p.textContent="No existe una serie instrumental Tmedia certificada y comparable. Los gráficos de error aparecerán solo cuando existan datos instrumentales autorizados y aceptados por el control de calidad.";
      plot.appendChild(p);
      message.textContent="Pendiente: SENAMHI instrumental Tmedia. El importador está preparado; no se han inventado datos.";
   } else {
      const max=Math.max(.01,...sites.map(city=>all[city].mae_c||0));
      for(const city of sites){
        const item=document.createElement("div");
        item.style.cssText="display:grid;grid-template-columns:96px 1fr 77px;gap:10px;align-items:center;margin:9px 0";
        const label=document.createElement("span");label.className="small";label.textContent=city;
        const bg=document.createElement("div");bg.style.cssText="background:#e4eff5;height:13px;border-radius:6px;overflow:hidden";
        const bar=document.createElement("div");bar.style.cssText="height:100%;background:#078f95;width:"+((all[city].mae_c||0)/max*100).toFixed(1)+"%";
        bg.appendChild(bar);
        const count=document.createElement("small");count.textContent=fmt(all[city].mae_c)+" °C";
        item.append(label,bg,count);plot.append(item);
      }
      message.textContent="Comparación descriptiva preliminar de estación y reanálisis; no constituye validación independiente ni prueba de habilidad del modelo 8E.";
   }
 }catch(err){
    table.replaceChildren();plot.replaceChildren();
    message.textContent="No es posible verificar las series térmicas: "+err.message+". No se simulan observaciones.";
 }
}
root.addEventListener("toggle",()=>{if(root.open&&!initialized){initialized=true;render()}});
e("oaf-8i-refresh")?.addEventListener("click",render);
})();
