/* Validación automática estructural UX70. No sustituye validación científica o de campo. */
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const read=path=>JSON.parse(fs.readFileSync(path,"utf8"));
const catalog=read("datos/sanidad_agroexportadora_2026.json");
const audit=read("datos/validacion_cientifica_fitosanidad_ux70.json");
const models=read("datos/fitosanitario_modelos_ux69.json");
assert.equal(catalog.cultivos.length,6,"El catálogo base tenía seis cultivos");
assert.equal(catalog.organismos.length,23,"El catálogo base tenía 23 fichas");
assert.equal(audit.numero_cultivos_web,catalog.cultivos.length);
assert.equal(audit.numero_fichas_web,catalog.organismos.length);
assert.equal(audit.auditadas.length,catalog.organismos.length);
const cropIds=new Set(catalog.cultivos.map(c=>c.id));
const ids=new Set();
for(const item of audit.auditadas){
 assert.ok(!ids.has(item.id_catalogo),"Ficha auditada duplicada: "+item.id_catalogo);ids.add(item.id_catalogo);
 const src=catalog.organismos.find(o=>o.id===item.id_catalogo);
 assert.ok(src,"Ficha de auditoría sin ficha base: "+item.id_catalogo);
 assert.ok(cropIds.has(item.cultivo_id));
 assert.equal(item.cultivo_id,src.crop_id);
 assert.equal(item.taxon_declarado,src.agentes);
 assert.equal(item.nombre_ficha,src.nombre);
 assert.equal(item.fuente_actual_en_web,src.fuente);
 assert.equal(item.productos_en_ficha,(src.productos||[]).length);
 assert.ok(Array.isArray(item.fuentes_documentales_para_contraste));
 assert.ok(typeof item.observacion_cientifica==="string"&&item.observacion_cientifica.length>40);
 assert.equal(item.viable_para_prediccion_de_riesgo_local,false,
  "Ninguna ficha puede declararse calibrada localmente sin datos de campo: "+item.id_catalogo);
 for(const url of item.fuentes_documentales_para_contraste)
  assert.match(url,/^https:\/\//,"Fuente sin HTTPS en "+item.id_catalogo);
}
assert.equal(new Set(audit.auditadas.map(a=>a.id_catalogo)).size,23);
assert.equal(audit.auditadas.filter(a=>a.tipo==="plaga").length,12);
assert.equal(audit.auditadas.filter(a=>a.tipo==="enfermedad").length,11);
const products=catalog.organismos.flatMap(o=>o.productos||[]);
assert.equal(products.length,31);
assert.equal(products.filter(p=>p.ficha_confirmada===true).length,0);
assert.equal(audit.productos_registro_confirmado_en_json,0);
assert.equal(audit.productos_fichas_total,products.length);
assert.equal(models.crops.length,7,"El catálogo experimental incluye además café");
assert.equal(models.models.length,2,"Hay dos indicadores exploratorios, no 23 modelos validados");
assert.ok(models.models.every(m=>m.calibration.status.startsWith("sin_")));
assert.ok(audit.complemento_cafe.length===2);
assert.ok(audit.discrepancias_priorizadas.some(d=>d.detalle.includes("Plasmopara viticola")));
assert.ok(audit.discrepancias_priorizadas.some(d=>d.detalle.includes("Lasiodiplodia")));
const stats={revision:"UX70",test:"consistencia_inventarios_y_bloqueo_de_modelos_no_validados",
 cultivos_sanidad:6,fichas:23,plagas:12,enfermedades:11,productos:31,etiquetas_senasa_confirmadas:0,
 cultivos_visores:models.crops.length,indicadores_exploratorios:models.models.length,
 fichas_con_riesgo_local_validado:0,notas_auditoria:audit.discrepancias_priorizadas.length};
console.log(JSON.stringify(stats,null,2));
