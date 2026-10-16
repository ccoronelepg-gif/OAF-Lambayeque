/* OAF Lambayeque 8K · auditoría de geografía, evidencia y procedencia.
 * Solo reporta metadatos derivados de fuentes archivadas; no trata lluvia
 * como temperaturas instrumentales ni confunde respuesta API con grilla 8D.
 */
(()=>{
 "use strict";
 const pane=document.getElementById("oaf-spatial-8k");
 if(!pane)return;
 const $=id=>document.getElementById(id);
 const status=$("oaf-8k-status"),table=$("oaf-8k-table");
 const select=$("oaf-8k-site"),details=$("oaf-8k-source");
 let data=null,started=false;
 const pretty=(x,n=2)=>Number.isFinite(x)?x.toLocaleString("es-PE",{maximumFractionDigits:n,minimumFractionDigits:n}):"—";
 const coord=x=>Number.isFinite(x)?x.toFixed(5):"Sin metadatos";
 const add=(tr,value)=>{const td=document.createElement("td");td.textContent=String(value);tr.append(td)};
 function draw(){
   if(!data)return;
   table.replaceChildren();
   const {indicadores:m,localidades:sites}=data;
   $("oaf-8k-cells").textContent=String(m.respuestas_geograficas_proveedor_8k);
   $("oaf-8k-stations").textContent=String(m.estaciones_con_tmax_tmin_en_boletin_senamhi);
   $("oaf-8k-verified").textContent=String(m.coordenadas_celda_8d_originales_verificadas);
   for(const p of sites){
     const tr=document.createElement("tr");
     add(tr,p.localidad_oaf);
     add(tr,coord(p.latitud_solicitada)+", "+coord(p.longitud_solicitada));
     add(tr,Number.isFinite(p.celda_devuelta_por_openmeteo_lat)
       ?coord(p.celda_devuelta_por_openmeteo_lat)+", "+coord(p.celda_devuelta_por_openmeteo_lon)
       :"No disponible");
     add(tr,Number.isFinite(p.distancia_solicitud_celda_devuelta_km)
       ?pretty(p.distancia_solicitud_celda_devuelta_km)+" km":"Sin medición");
     table.append(tr);
   }
   const site=select.value;
   const selected=sites.find(s=>s.localidad_oaf===site);
   if(!selected)return;
   details.replaceChildren();
   const p=document.createElement("p");p.className="small";
   p.textContent=site+": proveedor Open-Meteo informa "+
     (selected.celda_devuelta_por_openmeteo_lat===null?"sin metadatos de celda devuelta":
     "centro de celda de "+coord(selected.celda_devuelta_por_openmeteo_lat)+", "+coord(selected.celda_devuelta_por_openmeteo_lon))+
     ". La altitud de "+(selected.elevacion_reportada_openmeteo_m??"—")+
     " m es la elevación reportada por la API, NO una orografía ERA5-Land certificada.";
   details.append(p);
   const candidates=data.estaciones_historicas_lluvia_cercanas.filter(s=>s.localidad_oaf===site);
   const h=document.createElement("strong");h.textContent="Referencias instrumentales históricas más próximas (solo lluvia)";
   details.append(h);
   const ul=document.createElement("ul");ul.className="small";
   for(const c of candidates){
     const li=document.createElement("li");
     li.textContent=c.estacion_historica+": "+pretty(c.distancia_a_punto_oaf_km)+
       " km, coordenada "+(c.variante_coordenada.includes("alternativa")?"alternativa no corroborada":"usada en estudios previos")+
       ". Sin datos térmicos instrumentales verificables.";
     ul.append(li);
   }
   details.append(ul);
   const fine=document.createElement("p");fine.className="small";
   fine.textContent="La lista de estaciones con Tmax/Tmin en un boletín oficial identifica candidatas para buscar datos, pero no supone disponer de series diarias, códigos o periodos corroborados.";
   details.append(fine);
 }
 async function load(){
   status.textContent="Comprobando catálogo geográfico y huellas de procedencia…";
   try{
     const r=await fetch("datos/seleccion_espacial_8k/vista_8k.json",{cache:"no-store"});
     if(!r.ok)throw Error("Informe 8K no disponible: "+r.status);
     const obj=await r.json(),m=obj.indicadores;
     if(obj.fase!=="8K"||!m||
        m.validez_predictiva_8e_demostrada!==false||
        m.validacion_espacial_independiente!==false||
        m.coordenadas_celda_8d_originales_verificadas!==0||
        m.estaciones_termometricas_confirmadas!==0||
        !Array.isArray(obj.localidades)||obj.localidades.length!==4||
        !Array.isArray(obj.estaciones_historicas_lluvia_cercanas)||
        !Array.isArray(obj.candidatas_termometricas_documentadas)||
        obj.candidatas_termometricas_documentadas.some(z=>z.serie_instrumental_tmedia_obtenida!==false))
          throw Error("Metadatos no superan las condiciones de transparencia");
     data=obj;draw();
     status.textContent="Consulta registrada: "+m.respuestas_geograficas_proveedor_8k+
       " coordenadas devueltas por Open-Meteo. "+
       m.estaciones_con_tmax_tmin_en_boletin_senamhi+
       " estaciones citadas en un boletín de temperatura, sin series diarias obtenidas. "+
       "La identidad de la celda original del modelo 8D sigue sin verificarse.";
   }catch(err){table.replaceChildren();details.replaceChildren();
     status.textContent="Metadatos geográficos no comprobables: "+err.message+". No se muestran ubicaciones simuladas.";
   }
 }
 select.addEventListener("change",draw);
 $("oaf-8k-refresh")?.addEventListener("click",load);
 pane.addEventListener("toggle",()=>{if(pane.open&&!started){started=true;load()}});
})();
