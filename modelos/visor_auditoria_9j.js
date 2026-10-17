/* Fase 9J: audita evidencias de emisión; nunca presenta MAE si no hay contraste maduro. */
(()=>{"use strict";
const $=id=>document.getElementById(id);
const tag=(name,text)=>{const n=document.createElement(name);if(text!==undefined)n.textContent=text;return n;};
const number=x=>Number.isFinite(x)?x.toLocaleString("es-PE"):"—";
async function load(){
 const r=await fetch("datos/auditoria_vintage_9j/estado_prospectivo_9j.json",{cache:"no-store"});
 if(!r.ok)throw Error("Informe 9J sin publicar (HTTP "+r.status+")");
 const data=await r.json();
 if(data.fase!=="9J"||data.oaf_habilidad_prospectiva_demostrada!==false||
    data.enso_nino_costero_predictivo_validado!==false)
    throw Error("Estado científico inesperado");
 return data;
}
function pill(id,value,note){
 const x=$(id);if(!x)return;
 x.replaceChildren();
 x.append(tag("strong",number(value)),tag("span",note));
}
function show(r){
 const d=r.diarios_externos, t=r.temperatura_mensual_propia, o=r.sst_mensual_propia;
 pill("oaf-9j-daily",d.n_localidad_dia_pronosticados,"Pronósticos diarios externos archivados");
 pill("oaf-9j-monthly",t.n_predicciones_premes,"Pronósticos OAF de temperatura previos al mes");
 pill("oaf-9j-verified",r.verificacion_externa_6g.n_dias_verificados+
      r.verificacion_temperatura_8g.n_pronosticos_verificados,
      "Comparaciones posteriores efectivamente verificadas");
 $("oaf-9j-status").textContent="Corte "+r.corte_local+" (Perú). Primera verificación diaria admisible: "+
   d.fecha_primer_contraste_posible+". Primera verificación de temperatura mensual: "+
   t.primera_fecha_elegible_teorica+" (octubre, intramensual); la primera premensual: "+
   t.primera_validacion_premes_teorica+".";
 const row=$("oaf-9j-ledger");row.replaceChildren();
 for(const p of d.emisiones){
   const tr=tag("tr");
   const date=tag("td",p.fecha_emision_local);
   const n=tag("td",String(p.n_localidad_dia_pronosticados));
   const first=tag("td",p.primera_fecha_elegible);
   const link=tag("a","Ver commit original ↗");
   if(!/^[a-f0-9]{40}$/.test(p.commit_git))throw Error("SHA Git inválido");
   link.href="https://github.com/ccoronelepg-gif/OAF-Lambayeque/commit/"+p.commit_git;
   link.target="_blank";link.rel="noopener noreferrer";
   const proof=tag("td");proof.append(link);
   tr.append(date,n,first,proof);row.append(tr);
 }
 const source=$("oaf-9j-cautions");source.replaceChildren();
 const line=tag("p","Se mantienen por separado: "+o.n_predicciones_premes+
  " predicciones OAF oceánicas previas al mes, "+
  t.n_nowcasts_intramensuales+" estimaciones de temperatura intramensuales y "+
  o.n_nowcasts_intramensuales+" estimación oceánica intramensual. "+
  "Ninguna equivale a un pronóstico validado de El Niño Costero, ni a una alerta de plagas.");
 source.append(line);
 const note=tag("p","No se calcula MAE, RMSE ni sesgo con 0 verificaciones. "+
 "NOAA NMME y Copernicus C3S son fuentes candidatas para nuevas emisiones históricas, "+
 "pero sus series numéricas aún no han sido incorporadas ni verificadas en el OAF.");
 note.className="oaf-figure-caption";source.append(note);
}
async function init(){
 const box=$("oaf-9j-visor");if(!box)return;
 try{show(await load())}catch(e){
  $("oaf-9j-status").textContent="Informe 9J no disponible: "+e.message+
   ". No se infieren métricas sin fuente verificada.";
 }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();