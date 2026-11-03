/* OAF UX45 · inventario de integridad de seis áreas, PWA y fuentes. */
"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const root=path.resolve(__dirname,".."),read=p=>fs.readFileSync(path.join(root,p),"utf8");
const html=read("index.html"),sw=read("sw.js"),manifest=JSON.parse(read("manifest.webmanifest"));
const expected=["inicio","clima","autor","cultivos","nino","verificaciones"];
const pages=[...html.matchAll(/<section\s+data-page="([^"]+)"/g)].map(m=>m[1]);
assert.deepEqual(new Set(pages),new Set(expected),"La navegación perdió una de las seis áreas");
assert.equal(pages.length,6,"Secciones duplicadas o superpuestas");
const refs=[...html.matchAll(/<(?:script|link)\b[^>]*\b(?:src|href)="([^"]+)"/g)].map(m=>m[1])
 .filter(x=>!x.startsWith("#")&&!/^https?:|^data:|^mailto:/.test(x))
 .map(x=>decodeURIComponent(x.split(/[?#]/)[0]));
const missing=refs.filter(ref=>!fs.existsSync(path.join(root,ref)));
assert.deepEqual([...new Set(missing)],[],"Recursos CSS/JS referenciados que no existen");
const core=[...sw.matchAll(/"\.\/([^"]+)"/g)].map(m=>m[1]).filter(x=>x.length>0&&!x.endsWith("/"));
const missingCore=core.filter(ref=>!fs.existsSync(path.join(root,ref)));
assert.deepEqual([...new Set(missingCore)],[],"Recursos PWA precache inexistentes");
assert.equal(manifest.display,"standalone");
for(const icon of manifest.icons){
 assert(fs.existsSync(path.join(root,icon.src)),"Ícono no disponible "+icon.src);
}
assert(sw.includes("Network-first")&&sw.includes('isScientificData(url)'),"PWA no distingue avisos y datos de caché");
assert.match(sw,/const RELEASE="oaf-pwa-shell-2026-11-02-ux\d+"/,"PWA no invalida la caché tras cambios de interfaz");
assert(!html.includes("oaf-ux15-contador.js")&&!html.includes('id="oaf-ux15-counter"'),"El contador de visitas permanece");
const rf=JSON.parse(read("datos/rf_experimental_ux15.json"));
assert.equal(rf.operativo_certificado,false,"RF no debe marcarse operativo sin validación");
assert.equal(rf.alertas_automaticas,false,"No activar alertas experimentales");
if(rf.estado==="no_disponible"){
 assert.equal(rf.operativo_certificado,false,"RF no disponible no debe declararse operativo");
 assert.equal(rf.alertas_automaticas,false,"No activar alertas sin evidencia");
 assert.match(rf.error||"",/ERA5|archive-api|timeout|timed out/i);
 assert.equal(rf.pronostico_diario_rf_experimental,undefined,"No publicar pronósticos incompletos");
}else{
 assert.equal(rf.metrica_diaria?.backtest_semanal_recursivo?.por_horizonte?.length,7,"Faltan siete horizontes RF auditados");
 assert(Object.keys(rf.pronostico_diario_rf_experimental||{}).length>=4,"Pronósticos RF por cuatro localidades ausentes");
}
const enfen=JSON.parse(read("datos/estado_enso_verificado_ux9_2026.json"));
assert(enfen.enfen?.fuente?.startsWith("https://"),"Falta procedencia de ENFEN");
assert(/^\d{4}-\d\d-\d\d$/.test(enfen.enfen?.fecha_emision||""),"Fecha de emisión ENFEN inválida");
assert(html.includes("oaf-ux15-rf-salidas.js?v=20261102-ux54"),"Pronóstico UX54 no activado");
assert(html.includes("oaf-parcelas-ux39.js?v=20261029-ux51c"),"Análisis parcelario UX51 no activado");
const parcel=read("assets/oaf-parcelas-ux39.js");
assert(parcel.includes("esriGeometryPolygon")&&parcel.includes("esriGeometryMultipoint")&&parcel.includes("layerId:5090024"),"Falta consulta espacial vectorial/ráster correcta");
const weekly=read("assets/oaf-ux15-rf-salidas.js");
assert(weekly.includes("function rfEvidence(rain)")&&weekly.includes("wins>=5"),"No se aplica puerta de habilidad al RF semanal");
assert(weekly.includes("function monthlyRfEvidence(model)")&&weekly.includes("RF no se publica como pronóstico operativo")&&weekly.includes('variable==="rain"||evidence.temperatureValidated'),"No se aplica puerta de habilidad al RF mensual y su temperatura");
assert(weekly.includes("relative_humidity_2m_mean")&&weekly.includes("et0_fao_evapotranspiration"),"Faltan variables agroclimáticas por coordenadas");

// Integridad científica: procedencia, limitaciones y puertas de publicación de los modelos.
const rfPub=JSON.parse(read("datos/rf_robusto_10j/estado_publicacion_10j.json"));
const rf10j=JSON.parse(read("datos/rf_robusto_10j/auditoria_y_seleccion_10j.json"));
const rfManifest=JSON.parse(read("datos/rf_robusto_10j/manifest_modelo_candidato_10j.json"));
const rf10n=JSON.parse(read("datos/senamhi_10n/evaluacion_rf_estacion_10n.json"));
const humidityState=JSON.parse(read("datos/humedad_8z/estado_humedad_8z.json"));
const demState=JSON.parse(read("datos/muestreo_8o/estado_muestreo_8o.json"));
const stationState=JSON.parse(read("datos/estaciones_9d/auditoria_estaciones_9d.json"));
assert.equal(rfPub.puede_emitir_predicciones_operativas,false,"RF 10J no debe emitir pronóstico operativo");
assert.equal(rfPub.promocion_a_produccion_automatica,false,"RF 10J no debe promoverse automáticamente");
assert.equal(rfManifest.no_as_issued,true,"RF 10J debe conservar la limitación as-issued");
assert.equal(rfManifest.sin_estaciones_independientes,true,"RF 10J requiere validación instrumental independiente");
const rfRain=rf10j.resultados.lluvia.global;
assert(rfRain.mae_rf_mm>rfRain.mae_climatologia_mm,"RF 10J no debe presentarse como superior a climatología en MAE");
assert(rfRain.pr_auc_rf_p90<rfRain.pr_auc_ref_p90,"La PR-AUC P90 de RF no supera la referencia climatológica");
assert(rfRain.brier_rf_p95>rfRain.brier_ref_p95,"La calibración P95 de RF no supera la referencia");
assert.equal(rf10n.seleccion_validacion.peso_rf,0,"El RF de estaciones 10N debe conservar peso cero al no mejorar climatología");
assert.equal(rf10n.pronosticos_actuales_habilitados,false,"RF 10N no debe habilitar pronósticos actuales");
assert.equal(rf10n.QC_instrumental_formal_aprobado,false,"Los datos SENAMHI aportados no tienen QC formal aprobado");
assert.equal(humidityState.registros_mes_sitio,1440,"Humedad ERA5 debe conservar 1.440 registros mensuales");
assert.equal(humidityState.datos_reanalisis_no_sensor,true,"La humedad debe identificarse como reanálisis y no sensor");
assert.equal(humidityState.no_mide_humedad_dosel,true,"La humedad ERA5 no debe etiquetarse como humedad de dosel");
assert.equal(demState.nodos_dem_verificados,420,"El visor DEM debe usar el inventario auditado de 420 puntos");
assert.equal(demState.limite_administrativo_validado_inei_ign,false,"El límite regional no debe presentarse como validado INEI/IGN");
assert.equal(demState.zonas_homogeneas_demostradas,0,"El muestreo DEM no acredita zonas climáticas homogéneas");
assert.equal(demState.pronosticos_zonales_certificados,false,"No hay pronósticos zonales certificados");
assert(stationState.estaciones.every(x=>x.metadatos_senamhi_verificados===false),
 "Las tres series históricas 9D no deben mostrarse como estaciones oficiales georreferenciadas");
assert(stationState.estaciones.every(x=>x.latitud===null&&x.longitud===null),
 "No se deben inventar coordenadas para las estaciones 9D");

const seasonal=read("assets/oaf-ux15-rf-salidas.js");
assert(seasonal.includes('hourly:"precipitation,temperature_2m"')&&!seasonal.includes('daily:"precipitation_sum,temperature_2m_mean"'),
 "El pronóstico estacional usa variable no permitida por Open-Meteo");
const crop=JSON.parse(read("datos/sanidad_agroexportadora_2026.json"));
assert(typeof crop==="object"&&Object.keys(crop).length>0,"Catálogo fitosanitario vacío");
const boletines=JSON.parse(read("datos/boletines_institucionales_2026.json"));
assert(boletines.boletines.some(b=>b.id==="enfen19"&&b.url.includes("comunicado-oficial-enfen-n-19-2026")),"El comunicado ENFEN vigente debe apuntar a la publicación oficial N.º 19-2026");

const agro=read("assets/oaf-agro-charts-2026.js");
assert(agro.includes("oaf-regional-map-legend")||read("assets/oaf-agroexportacion-2026.js").includes("oaf-regional-map-legend"),"Falta leyenda altitudinal del DEM");
assert(agro.includes("datos/humedad_8z/humedad_vpd_mensual_8z.csv"),"La humedad histórica debe proceder del CSV mensual regional verificado");

const output={revision:"UX54",fecha_auditoria:new Date().toISOString(),paginas:pages,
 enlaces_internos_comprobados:refs.length,recursos_pwa_comprobados:core.length,
 iconos_pwa:manifest.icons.length,localidades_rf:Object.keys(rf.pronostico_diario_rf_experimental||{}).length,
 ultima_emision_rf:rf.fecha_generacion_utc,ultima_emision_enfen:enfen.enfen.fecha_emision,
 resultado:"PASA_CONTROL_ESTRUCTURAL; no equivale a disponibilidad en tiempo real de fuentes externas"};
fs.mkdirSync(path.join(root,"artifacts"),{recursive:true});
fs.writeFileSync(path.join(root,"artifacts","auditoria_ux45_estructura.json"),JSON.stringify(output,null,2)+"\n");
console.log(JSON.stringify(output,null,2));
