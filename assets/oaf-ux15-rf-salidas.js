(function(){
"use strict";
const $=id=>document.getElementById(id);
const el=(tag,cls,txt)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(txt!==undefined)x.textContent=String(txt);return x};
const dateNames=["noviembre","diciembre","enero","febrero","marzo","abril"];
const places=["Chiclayo","Jayanca","Motupe","Olmos"];
const number=(n,dp=1)=>Number(n).toLocaleString("es-PE",{minimumFractionDigits:dp,maximumFractionDigits:dp});
let data=null,loaded=false;
function graphical(root,points,field,color,unit){
 root.replaceChildren();
 if(!points?.length||points.some(x=>!Number.isFinite(x[field]))){root.textContent="La serie RF no tiene datos numéricos comprobables.";return}
 const NS="http://www.w3.org/2000/svg",W=780,H=250,L=55,R=20,T=23,B=44,arr=points.map(x=>x[field]);
 const low=field.includes("precipitacion")?0:Math.min(...arr)-1.8,high=Math.max(...arr,low+1),top=high+(high-low)*.12;
 const X=i=>L+(i+.5)*(W-L-R)/points.length,Y=v=>T+(top-v)/(top-low)*(H-T-B);
 const svg=(tag,props,txt)=>{let x=document.createElementNS(NS,tag);for(let [k,v] of Object.entries(props||{}))x.setAttribute(k,String(v));if(txt!==undefined)x.textContent=txt;return x};
 const chart=svg("svg",{viewBox:"0 0 780 250",role:"img","aria-label":"Resultados experimentales Random Forest: "+unit});
 for(let n=0;n<=4;n++){let v=low+(top-low)*n/4,y=Y(v);
 chart.append(svg("line",{x1:L,y1:y,x2:W-R,y2:y,stroke:"#dfebe1"}),svg("text",{x:L-7,y:y+3,"text-anchor":"end",fill:"#658174","font-size":12},number(v,0)))}
 const line=svg("polyline",{points:arr.map((v,i)=>X(i)+","+Y(v)).join(" "),stroke:color,"stroke-width":4,fill:"none","stroke-linecap":"round","stroke-linejoin":"round"});
 chart.append(line);
 points.forEach((p,i)=>{let name=p.fecha||p.mes,px=X(i),py=Y(p[field]);
 const dot=svg("circle",{cx:px,cy:py,r:5,fill:color,stroke:"#fff","stroke-width":2,tabindex:0,role:"img","aria-label":name+" "+number(p[field])+" "+unit});
 dot.append(svg("title",{},name+" · "+number(p[field])+" "+unit));chart.append(dot);
 chart.append(svg("text",{x:px,y:H-14,"text-anchor":"middle",fill:"#547365","font-size":11},name.slice(5)))});
 root.append(chart);
}
function panel(title,sub,id){
 const p=el("article","oaf-ux15-rf-out");
 p.id=id;p.append(el("span","oaf-ux15-rf-chip","Random Forest OAF · candidato experimental"),
 el("h3",null,title),el("p","oaf-ux15-rf-sub",sub));return p
}
function drawWeek(){
 const root=$("oaf-ux15-rf-week"),loc=$("oaf-ux14-ciudad"),varsel=$("oaf-ux14-variable");if(!root||!loc||!varsel)return;
 const rows=data?.pronostico_diario_rf_experimental?.[loc.value];
 const chart=$("oaf-ux15-weekchart"),meta=$("oaf-ux15-weekmeta");
 if(data?.estado!=="candidato_experimental_generado"||!Array.isArray(rows)||rows.length!==7){
  chart.textContent="El modelo Random Forest propio no dispone todavía de una ejecución experimental completa para este horizonte.";
  meta.textContent="Estado de entrenamiento: "+(data?.estado||"pendiente")+". Se conserva separada la referencia del proveedor externo mostrada arriba.";return
 }
 const key=varsel.value==="rain"?"precipitacion_mm":"temperatura_max_c";
 graphical(chart,rows,key,"#8d64a6",key==="precipitacion_mm"?"mm/día":"°C");
 const score=data?.metrica_diaria||{};
 meta.textContent="RF propio (candidato), generado "+(data.fecha_generacion_utc||"sin fecha")+". Error de prueba retrospectiva 2025: MAE lluvia "+number(score.mae_lluvia_mm)+" mm/día; temperatura "+number(score.mae_temperatura_c)+" °C. Entradas ERA5 reanalizadas, avance autoregresivo: no hay validación as-issued ni habilidad certificada a siete días.";
}
function drawMonth(){
 const root=$("oaf-ux15-monthgrid"),target=$("oaf-ux15-monthchart"),info=$("oaf-ux15-monthmeta"),sel=$("oaf-ux15-month-city");
 if(!root||!sel)return;
 root.replaceChildren();
 const rows=data?.escenarios_mensuales_rf_experimentales?.[sel.value];
 const good=data?.estado==="candidato_experimental_generado"&&Array.isArray(rows)&&rows.length>=6;
 const selected=good?rows.slice(0,6):Array.from({length:6},(_,i)=>({mes:i<2?"2026-"+(i+11):"2027-"+String(i-1).padStart(2,"0")}));
 selected.forEach((row,i)=>{
   const tile=el("article","oaf-ux15-future-month");
   tile.append(el("strong",null,dateNames[i][0].toUpperCase()+dateNames[i].slice(1)+" "+row.mes.slice(0,4)));
   if(good){tile.append(el("span",null,"Precipitación: "+number(row.precipitacion_mm)+" mm/mes"),el("span",null,"T. media: "+number(row.temperatura_media_c)+" °C"));
     tile.append(el("small","oaf-ux15-future-badge","RF experimental · no operativo"));}
   else tile.append(el("span",null,"RF en entrenamiento · sin salida verificable"),el("small","oaf-ux15-future-badge","No publicar valor aún"));
   root.append(tile);
 });
 if(!good){target.textContent="No existen pronósticos mensuales futuros emitidos por el RF con archivo comprobado.";
 info.textContent="Se muestra el calendario de investigación desde noviembre de 2026, sin rellenarlo con cifras inventadas. Estado: "+(data?.estado||"pendiente")+".";
 return;}
 graphical(target,selected,"precipitacion_mm","#b27a46","mm/mes");
 const score=data?.metrica_mensual||{};
 info.textContent="Proyección RF autoregresiva experimental generada "+(data.fecha_generacion_utc||"sin fecha")+". MAE retrospectivo 2021–2025: "+number(score.mae_lluvia_mm)+" mm/mes, temperatura "+number(score.mae_temp_c)+" °C. No son probabilidades certificadas, ni pronóstico oficial, ni validación de emisiones originales.";
}
function attach(){
 if(loaded)return;
 const week=$("oaf-ux14-rf-semana"),monthly=$("oaf-ux14-rf-mes");
 if(!week||!monthly)return;
 loaded=true;
 const wk=panel("Salida del algoritmo propio · RF 7 días","Comparación con la referencia meteorológica superior; no confundir una serie externa con un modelo entrenado.","oaf-ux15-rf-week");
 const chart=el("div","oaf-ux14-chart");chart.id="oaf-ux15-weekchart";wk.append(chart);
 const note=el("p","oaf-ux14-source","Comprobando ejecución RF…");note.id="oaf-ux15-weekmeta";wk.append(note);
 const external=$("oaf-ux14-weekstatus");if(external)external.after(wk);else week.append(wk);
 const mn=panel("Desde noviembre de 2026 · RF por localidad","Horizonte mensual investigado con modelos Random Forest y series históricas. Las cifras futuras aparecen solo al generar un candidato reproducible.","oaf-ux15-rf-future");
 const wrap=el("div","oaf-ux14-controls"),label=el("label",null,"Localidad del candidato mensual"),sel=el("select");sel.id="oaf-ux15-month-city";
 for(const name of places){const opt=el("option",null,name);sel.append(opt)}wrap.append(label,sel);mn.append(wrap);
 const cards=el("div","oaf-ux15-future-calendar");cards.id="oaf-ux15-monthgrid";mn.append(cards);
 const mchart=el("div","oaf-ux14-chart");mchart.id="oaf-ux15-monthchart";mn.append(mchart);
 const mnote=el("p","oaf-ux14-source","Consultando estado RF");mnote.id="oaf-ux15-monthmeta";mn.append(mnote);
 monthly.append(mn);
 $("oaf-ux14-ciudad")?.addEventListener("change",drawWeek);
 $("oaf-ux14-variable")?.addEventListener("change",drawWeek);
 sel.addEventListener("change",drawMonth);
 fetch("datos/rf_experimental_ux15.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()}).then(d=>{
  if(d.operativo_certificado!==false||d.alertas_automaticas!==false)throw Error("Falta control de carácter experimental");
  data=d;drawWeek();drawMonth();
 }).catch(e=>{data={estado:"archivo_no_disponible"};drawWeek();drawMonth();console.warn("OAF: salida RF no disponible",e)});
}
document.addEventListener("oaf:ux9-ready",()=>queueMicrotask(attach));
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",attach,{once:true});else attach();
})();