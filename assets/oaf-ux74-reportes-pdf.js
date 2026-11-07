/* OAF UX74 - Informes cartograficos PDF autocontenidos, sin CDN. */
(function () {
"use strict";
const $=id=>document.getElementById(id);
const enc=s=>new TextEncoder().encode(s);
const join=chunks=>{const n=chunks.reduce((s,b)=>s+b.length,0),out=new Uint8Array(n);let i=0;for(const b of chunks){out.set(b,i);i+=b.length;}return out;};
const num=(x,d=1)=>Number.isFinite(Number(x))?Number(x).toLocaleString("es-PE",{maximumFractionDigits:d}):"Sin datos";
const fixed=(n,d=4)=>Number.isFinite(Number(n))?Number(n).toFixed(d):"-";
const limits={rainIntense:[1,10,30],flood:[1,10,30],drought:[10,30,75],heat:[25,30,35]};
const scales={rainIntense:["#a3c7b9","#7ab3d4","#2e84b8","#15517f"],flood:["#a3c7b9","#7ab3d4","#2e84b8","#15517f"],drought:["#bc9352","#deb975","#b6bd92","#5c9fa5"],heat:["#83b6c9","#f0c76f","#eb964c","#d45235"]};
const titles={rainIntense:"Precipitacion maxima diaria pronosticada",flood:"Lluvia como contexto de inundacion, NO peligro",drought:"Precipitacion acumulada en 30 dias anteriores",heat:"Temperatura maxima prevista en siete dias",botrytis:"Arandano - Botrytis cinerea, episodios de HR",ceratitis:"Mango - Ceratitis capitata, grados-dia"};
function interpretation(layer,model){
 if(layer==="C"&&model==="botrytis")return "Se cuentan episodios de humedad relativa del aire mayor de 90 por ciento durante al menos seis horas continuas. El resultado no mide humectacion foliar, infeccion o incidencia de Botrytis.";
 if(layer==="C")return "Se acumulan grados-dia a dos temperaturas base (9,1 y 8,47 C) descritas en literatura. No hay biofix, trampas o calibracion de desarrollo local; el gradiente no cuantifica poblaciones de Ceratitis.";
 if(model==="drought")return "El acumulado de lluvia de 30 dias es descriptivo: NO equivale al indice SPI/SPEI, sequia oficial o deficit hidrico de cultivos.";
 if(model==="heat")return "La temperatura maxima prevista no identifica por si sola una ola de calor. Se necesitan percentiles historicos y duracion.";
 if(model==="flood")return "El mapa es lluvia meteorologica como contexto. NO sustituye la susceptibilidad oficial de CENEPRED ni un modelo hidraulico.";
 return "Los intervalos representan magnitudes de lluvia y no umbrales de aviso SENAMHI ni probabilidad de danos.";
}
function val(f,model){
 const p=f.properties||{};
 if(model==="botrytis")return p.episodios_hr_sobre_90_6h;
 if(model==="ceratitis")return p.grados_dia_base_9_1;
 return p.valor;
}
function desc(f,model){
 const p=f.properties||{},v=val(f,model);
 if(v===null||v===undefined||!Number.isFinite(Number(v)))return "Sin datos";
 if(model==="botrytis")return num(v,0)+" episodios HR";
 if(model==="ceratitis")return num(p.grados_dia_base_9_1)+"-"+num(p.grados_dia_base_8_47)+" GD";
 return num(v)+" "+(p.unidad||"");
}
function style(f,model,min,max){
 const v=val(f,model);if(v===null||v===undefined||!Number.isFinite(Number(v)))return "#b6bdbc";
 if(model==="botrytis")return Number(v)===0?"#609883":Number(v)===1?"#e6ad42":"#c46b3a";
 if(model==="ceratitis"){const p=max>min?(Number(v)-min)/(max-min):.5;const r=Math.round(170-p*105),g=Math.round(205-p*110),b=Math.round(226-p*81);return "rgb("+r+","+g+","+b+")";}
 const levels=limits[model]||limits.rainIntense;let i=0;while(i<levels.length&&Number(v)>=levels[i])i++;return (scales[model]||scales.rainIntense)[i];
}
function eachCoord(geom,fn){
 if(!geom)return;
 if(geom.type==="Point"){fn(geom.coordinates);return;}
 if(geom.type==="Polygon"){for(const ring of geom.coordinates||[])for(const xy of ring)fn(xy);return;}
 if(geom.type==="MultiPolygon"){for(const poly of geom.coordinates||[])for(const ring of poly)for(const xy of ring)fn(xy);}
}
function drawGeometry(ctx,g,project,fill,points){
 if(g?.type==="Point"){const xy=project(g.coordinates);ctx.beginPath();ctx.arc(xy[0],xy[1],points?6:4,0,Math.PI*2);ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle="#244b42";ctx.lineWidth=1.3;ctx.stroke();return;}
 const polys=g?.type==="Polygon"?[g.coordinates]:g?.type==="MultiPolygon"?g.coordinates:[];
 for(const poly of polys){ctx.beginPath();for(const ring of poly){ring.forEach((xy,i)=>{const q=project(xy);if(i)ctx.lineTo(q[0],q[1]);else ctx.moveTo(q[0],q[1]);});ctx.closePath();}ctx.fillStyle=fill;ctx.fill("evenodd");ctx.strokeStyle="#587168";ctx.lineWidth=.7;ctx.stroke();}
}
async function imageFor(features,model,geometry){
 const canvas=document.createElement("canvas");canvas.width=1440;canvas.height=800;
 const ctx=canvas.getContext("2d");if(!ctx)throw Error("No se pudo construir el mapa");
 ctx.fillStyle="#fff";ctx.fillRect(0,0,1440,800);
 let outline=[];
 try{const r=await fetch("datos/zonificacion_8n/limite_lambayeque_referencial.geojson",{cache:"force-cache"});if(r.ok){const g=await r.json();outline=(g.features||[]).map(x=>x.geometry).filter(Boolean);}}catch(_){}
 const coords=[];for(const f of features)eachCoord(f.geometry,p=>coords.push(p));for(const g of outline)eachCoord(g,p=>coords.push(p));
 const ll=coords.filter(p=>Array.isArray(p)&&Number.isFinite(p[0])&&Number.isFinite(p[1]));
 if(!ll.length)throw Error("Sin coordenadas trazables");
 const lon0=Math.min(...ll.map(x=>x[0])),lon1=Math.max(...ll.map(x=>x[0])),lat0=Math.min(...ll.map(x=>x[1])),lat1=Math.max(...ll.map(x=>x[1]));
 const correction=Math.cos((lat0+lat1)/2*Math.PI/180),rangeX=Math.max(.01,(lon1-lon0)*correction),rangeY=Math.max(.01,lat1-lat0);
 const mx=920/rangeX,my=655/rangeY,scale=Math.min(mx,my),ox=35+(920-rangeX*scale)/2,oy=68+(655-rangeY*scale)/2;
 const project=p=>[ox+(p[0]-lon0)*correction*scale,oy+(lat1-p[1])*scale];
 ctx.fillStyle="#f4f7f4";ctx.fillRect(24,55,952,676);
 for(const g of outline)drawGeometry(ctx,g,project,"#e5eae6",false);
 const numbers=features.map(f=>val(f,model)).filter(x=>x!==null&&x!==undefined&&Number.isFinite(Number(x))).map(Number);
 const min=numbers.length?Math.min(...numbers):0,max=numbers.length?Math.max(...numbers):1;
 const ordered=[...features].sort((a,b)=>a.geometry?.type==="Point"?1:-1);
 for(const f of ordered)drawGeometry(ctx,f.geometry,project,style(f,model,min,max),geometry==="puntos");
 ctx.font="bold 28px Arial";ctx.fillStyle="#194b3b";ctx.fillText("OAF Lambayeque | Representacion cartografica",33,36);
 ctx.fillStyle="#193f35";ctx.font="bold 20px Arial";ctx.fillText("Leyenda y trazabilidad",1010,86);
 const items=model==="botrytis"?[["#609883","0 episodios"],["#e6ad42","1 episodio"],["#c46b3a","2 o mas"],["#b6bdbc","Sin datos"]]:
 model==="ceratitis"?[["#aacde2","Menor acumulacion relativa"],["#417391","Mayor acumulacion relativa"],["#b6bdbc","Sin datos"]]:
 (scales[model]||scales.rainIntense).map((c,i)=>[c,["Clase 1","Clase 2","Clase 3","Clase 4"][i]]);
 items.forEach(([color,label],i)=>{const y=132+i*53;ctx.fillStyle=color;ctx.fillRect(1008,y-19,30,25);ctx.strokeStyle="#43645a";ctx.strokeRect(1008,y-19,30,25);ctx.fillStyle="#274a3d";ctx.font="17px Arial";ctx.fillText(label,1050,y);});
 const notes=["Coordenadas: WGS84",geometry==="puntos"?"Puntos meteorologicos":"Poligonos de proximidad","No es cartografia oficial","Metodo: vecino mas cercano","Contorno regional referencial"];
 ctx.fillStyle="#38584b";ctx.font="17px Arial";notes.forEach((n,i)=>ctx.fillText(n,1008,405+i*39));
 ctx.fillStyle="#6c7a74";ctx.font="15px Arial";ctx.fillText("Fuente meteorologica: Open-Meteo",1008,657);
 ctx.fillText("Uso: exploracion y vigilancia.",1008,686);
 return canvas.toDataURL("image/jpeg",.86).split(",")[1];
}
function escapePdf(s){
 return String(s).replace(/[\u2010-\u2015]/g,"-").replace(/[\u2265]/g,">=").replace(/[\u2264]/g,"<=").replace(/[\u2022]/g,"-").replace(/[^\x20-\x7e\xa0-\xff]/g,"?").replace(/[\\()]/g,"\\$&").replace(/[\x80-\xff]/g,c=>"\\"+c.charCodeAt(0).toString(8).padStart(3,"0"));
}
function pdf(jpg,report){
 const jpeg=Uint8Array.from(atob(jpg),c=>c.charCodeAt(0));
 const objs=[null],reserve=()=>{objs.push(null);return objs.length-1;},set=(n,b)=>objs[n]=b;
 const regular=reserve(),bold=reserve(),imageId=reserve(),pagesId=reserve(),catalogId=reserve();
 set(regular,enc("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"));
 set(bold,enc("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"));
 set(imageId,join([enc("<< /Type /XObject /Subtype /Image /Width 1440 /Height 800 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length "+jpeg.length+" >>\nstream\n"),jpeg,enc("\nendstream")]));
 const pages=[],rows=report.features.map((f,i)=>{const p=f.properties||{},xy=f.geometry?.type==="Point"?f.geometry.coordinates:null;return [
 String(i+1),String(p.id||p.zone_id||f.id||"").slice(0,19),String(p.point_id||p.id||"").slice(0,15),
 desc(f,report.model).slice(0,30),xy?fixed(xy[1])+", "+fixed(xy[0]):num(p.distancia_representativa_km,1)+" km"
 ];});
 const pageRows=[[]];for(let i=0;i<rows.length;i+=36)pageRows.push(rows.slice(i,i+36));
 const size=842,high=595;
 const addText=(arr,x,y,text,font=10,b=false)=>arr.push("BT /F"+(b?"2":"1")+" "+font+" Tf 1 0 0 1 "+x.toFixed(1)+" "+y.toFixed(1)+" Tm ("+escapePdf(text)+") Tj ET\n");
 const paragraph=(arr,x,y,content,columns=47,step=13,font=9)=>{
  const words=String(content).split(/\s+/);let line="",out=[];
  for(const word of words){if((line+" "+word).trim().length>columns){out.push(line);line=word;}else line=(line+" "+word).trim();}
  if(line)out.push(line);
  out.forEach((l,i)=>addText(arr,x,y-i*step,l,font));return y-out.length*step;
 };
 for(let pageIndex=0;pageIndex<pageRows.length;pageIndex++){
  const pageId=reserve(),contentId=reserve();pages.push(pageId);
  const parts=["q\n"],isCover=pageIndex===0;
  addText(parts,32,559,"OBSERVATORIO AGROCLIMATICO Y FITOSANITARIO - LAMBAYEQUE",14,true);
  addText(parts,32,537,(isCover?"REPORTE CARTOGRAFICO":"DETALLE DE REGISTROS")+" | "+report.layer+" - "+report.geometry,11,true);
  if(isCover){
   parts.push("q 548 0 0 304 30 202 cm /Im0 Do Q\n");
   addText(parts,590,501,report.title.slice(0,39),10,true);
   addText(parts,590,478,"Elementos: "+rows.length+" | validos: "+report.valid,9);
   addText(parts,590,459,"Fecha consulta: "+report.date.slice(0,19),9);
   addText(parts,590,438,"Variable / unidad:",9,true);
   let y=paragraph(parts,590,424,report.variable,35,14,9);
   addText(parts,590,y-9,"Interpretacion:",9,true);
   y=paragraph(parts,590,y-23,report.interpretation,37,13,8.5);
   addText(parts,32,183,"METODOLOGIA Y LIMITACIONES",10,true);
   paragraph(parts,32,166,"Cada poligono hereda el indicador de la muestra meteorologica mas cercana (hasta 28 km). No se calculan valores continuos, ni se representan parcelas verificadas. Contorno simplificado y referencial.",112,13,9);
   paragraph(parts,32,130,"Fuente: Open-Meteo Forecast. Emision y periodo: "+report.date+". Datos extraidos de la consulta actual, no de un conjunto sintetico.",112,13,9);
   paragraph(parts,32,93,"ATENCION: NO es un mapa oficial de peligro, infestacion, infeccion o riesgo calibrado. No usar para decisiones fitosanitarias ni de emergencia sin evaluacion de campo.",112,13,9);
  }else{
   const head=["N","ID","Punto asociado","Indicador","Coordenada WGS84 / distancia"];
   const xpos=[32,55,185,340,579];head.forEach((v,i)=>addText(parts,xpos[i],503,v,9,true));
   for(let r=0;r<pageRows[pageIndex].length;r++){
    const y=482-r*12.2;pageRows[pageIndex][r].forEach((v,i)=>addText(parts,xpos[i],y,v,i===3?8.5:8.2));
    if(r%2===1)parts.push("0.8 w 0.9 0.94 0.91 RG 32 "+(y-3)+" m 807 "+(y-3)+" l S\n");
   }
  }
  addText(parts,32,30,"OAF | Datos meteorologicos modelados y geometrias aproximadas | WGS84 | "+(pageIndex+1)+"/"+pageRows.length,8);
  const body=enc(parts.join("")+"Q\n");set(contentId,join([enc("<< /Length "+body.length+" >>\nstream\n"),body,enc("endstream")]));
  set(pageId,enc("<< /Type /Page /Parent "+pagesId+" 0 R /MediaBox [0 0 "+size+" "+high+"] /Resources << /Font << /F1 "+regular+" 0 R /F2 "+bold+" 0 R >> /XObject << /Im0 "+imageId+" 0 R >> >> /Contents "+contentId+" 0 R >>"));
 }
 set(pagesId,enc("<< /Type /Pages /Kids ["+pages.map(x=>x+" 0 R").join(" ")+"] /Count "+pages.length+" >>"));
 set(catalogId,enc("<< /Type /Catalog /Pages "+pagesId+" 0 R >>"));
 const head=enc("%PDF-1.4\n%OAF\n");let length=head.length;const chunks=[head],offset=[0];
 for(let i=1;i<objs.length;i++){if(!objs[i])throw Error("Objeto PDF vacio "+i);offset[i]=length;const chunk=join([enc(i+" 0 obj\n"),objs[i],enc("\nendobj\n")]);length+=chunk.length;chunks.push(chunk);}
 const begin=length;let xref="xref\n0 "+objs.length+"\n0000000000 65535 f \n";
 for(let i=1;i<objs.length;i++)xref+=String(offset[i]).padStart(10,"0")+" 00000 n \n";
 chunks.push(enc(xref+"trailer\n<< /Size "+objs.length+" /Root "+catalogId+" 0 R >>\nstartxref\n"+begin+"\n%%EOF"));
 return new Blob(chunks,{type:"application/pdf"});
}
async function exportReport(layer,geometry){
 const api=layer==="C"?window.OAFPotentialLayer:window.OAFTerritoryClimate;
 if(!api)throw Error("El visor cartografico aun no ha cargado");
 const fc=geometry==="puntos"?api.toGeoJSON?.():api.polygonsGeoJSON?.();
 if(!Array.isArray(fc?.features)||!fc.features.length)throw Error("No hay puntos/poligonos consultados para exportar");
 const model=fc.metadata?.model||"rainIntense",date=fc.metadata?.generated||new Date().toISOString();
 const valid=fc.features.filter(f=>val(f,model)!==null&&val(f,model)!==undefined&&Number.isFinite(Number(val(f,model)))).length;
 const report={features:fc.features,layer,geometry,model,date,valid,title:titles[model]||model,variable:titles[model]||model,interpretation:interpretation(layer,model)};
 const jpg=await imageFor(fc.features,model,geometry);
 const blob=pdf(jpg,report),url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="OAF_"+layer+"_"+geometry+"_"+model+"_"+date.slice(0,10)+".pdf";document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);
 return {pages:1+Math.ceil(fc.features.length/36),count:fc.features.length};
}
/* Delegacion: los visores pueden recrear botones al cambiar pestañas,
 * y los eventos registrados en nodos originales no sobreviven al reemplazo. */
document.addEventListener("click",event=>{
 const button=event.target?.closest?.("#oaf-ux74a-points,#oaf-ux74a-polygons,#oaf-ux35d-export,#oaf-ux35d-polygons-export");
 if(!button||button.disabled)return;
 event.preventDefault();
 event.stopImmediatePropagation();
 const layer=button.id.startsWith("oaf-ux74a")?"A":"C";
 const geometry=button.id.includes("polygons")?"poligonos":"puntos";
 window.OAFReportPDF.export(layer,geometry);
},true);
window.OAFReportPDF={export:async(layer,geometry)=>{
 try{return await exportReport(layer,geometry)}catch(e){console.error("OAF PDF",e);alert("No se pudo generar el PDF: "+(e.message||e));throw e;}
},_test:{pdf,desc,style}};
})();