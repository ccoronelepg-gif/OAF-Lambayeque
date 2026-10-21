(function(){
"use strict";
const el=(tag,cls,txt)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(txt!==undefined)x.textContent=String(txt);return x};
const get=path=>fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json()});
const iso=x=>{if(!x)return "Sin ejecución verificada";const d=new Date(x);return Number.isNaN(d.getTime())?"Sin fecha verificable":d.toLocaleString("es-PE",{timeZone:"America/Lima",day:"2-digit",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit",hour12:false})+" (Perú)"};
function link(label,url){const a=el("a",null,label);if(/^https:\/\//.test(url||"")){a.href=url;a.target="_blank";a.rel="noopener noreferrer"}return a}
function item(title,status,desc,href,at){
 const card=el("article","oaf-ux13-source"),h=el("strong",null,title),s=el("span","oaf-ux13-status",status),p=el("p",null,desc),date=el("small",null,"Última consulta: "+iso(at));
 card.append(h,s,p,date,link("Consultar fuente ↗",href));return card;
}
async function ready(){
 const parent=document.getElementById("oaf-boletines-evolucion"),meta=document.getElementById("oaf-meta-hub");
 if(!parent||!meta)return;
 const bar=el("div","oaf-ux13-panel");bar.id="oaf-fuentes-vigencia-2026";
 bar.append(el("h3",null,"Vigencia y comprobación automática de fuentes oficiales"),el("p",null,"La consulta del portal no confirma por sí sola que exista un aviso nuevo. Se muestran el estado del último intento y la fuente original; un fallo no se interpreta como normalidad climática."));
 const grid=el("div","oaf-ux13-source-grid");bar.append(grid);parent.append(bar);
 const details=el("details","oaf-ux13-model-detail");
 const summary=el("summary",null,"Actualización de modelos: qué es dinámico y qué sigue siendo experimental");
 const data=el("div","oaf-ux13-model-grid");
 details.append(summary,data);meta.prepend(details);
 try{
  const [state,chirps,enfen]=await Promise.all([
   get("datos/estado_fuentes_oficiales_auto.json"),
   get("datos/estado_monitoreo_3z.json").catch(()=>null),
   get("datos/estado_enfen_3z.json").catch(()=>null)
  ]);
  const pub=state.fuentes||{},ts=state.fecha_comprobacion_utc;
  for(const [id,name] of [["enfen","ENFEN"],["noaa","NOAA CPC"],["senamhi","SENAMHI"],["cenepred","CENEPRED"]]){
   const q=pub[id]||{};
   let label="Pendiente";
   if(q.estado_consulta==="indice_oficial_verificado")label="Índice consultado";
   if(q.estado_consulta==="nuevo_documento_por_interpretar")label="Documento nuevo: requiere lectura";
   if(q.estado_consulta==="sitio_accesible_fecha_aviso_no_verificada")label="Web accesible; fecha de aviso no comprobada";
   if(q.estado_consulta==="cambio_html_requiere_lectura")label="Cambió la página: verificar nuevo boletín";
   if(q.estado_consulta==="consulta_fallida")label="Consulta fallida";
   const memo=id==="enfen"&&q.ultimo_documento? q.ultimo_documento.titulo+" · el resumen del boletín no cambia automáticamente con este monitor.":q.tipo||"Estado documental según última ejecución del monitor.";
   grid.append(item(name,label,memo,q.url,ts||q.ultima_consulta_utc));
  }
  const notice=el("p","oaf-ux13-notice","Importante: la síntesis meteorológica del OAF se revisa documentalmente. No se generan automáticamente conclusiones oficiales a partir de cambios de una página.");bar.append(notice);
  const models=state.catalogo_modelos?.length?state.catalogo_modelos:[
    {nombre:"Open-Meteo",frecuencia:"API al abrir",estado:"dinamico_del_proveedor"},
    {nombre:"CHIRPS v3",frecuencia:"Tarea semanal; sujeto a publicación",estado:"depende_de_job_y_publicacion"},
    {nombre:"NOAA ERSSTv5",frecuencia:"Días 12 y 19 mensuales",estado:"depende_de_job_y_publicacion"},
    {nombre:"Random Forest",frecuencia:"Candidato sin publicación operativa",estado:"no_publicacion_automatica"}
  ];
  for(const m of models) {
   const x=el("article","oaf-ux13-model");
   x.append(el("strong",null,m.nombre),el("p",null,m.frecuencia),el("small",null,String(m.estado).replaceAll("_"," ")));
   data.append(x);
  }
  const tail=el("p","oaf-ux13-note","CHIRPS · último mes validado en el estado archivado: "+(chirps?.ultimo_mes_disponible||"no disponible")+". Estado 3Z ENFEN: "+(enfen?.verificacion||"no disponible")+". Esto NO significa que todas las series o modelos hayan sido reentrenados.");
  details.append(tail);
  if(!ts)bar.append(el("p","oaf-ux13-warning","Monitor diario configurado; su primera ejecución todavía no está acreditada."));
  else{
   const age=(Date.now()-new Date(ts).getTime())/86400000;
   if(!Number.isFinite(age)||age>3)bar.append(el("p","oaf-ux13-warning","Última comprobación antigua o sin fecha válida; consultar organismos directamente."));
  }
 }catch(e){
  grid.append(el("p","oaf-ux13-warning","El estado automático no se pudo consultar ("+e.message+"). No se afirma actualidad de los boletines."));
 }
}
document.addEventListener("oaf:ux11-ready",()=>{ready()},{once:true});
if(document.readyState!=="loading")ready();else document.addEventListener("DOMContentLoaded",ready,{once:true});
})();