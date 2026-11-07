/* OAF UX71: audit scientific bibliography crosswalk without asserting field-level validation.
 * Execute: node tests/auditoria_bibliografica_ux71.cjs
 */
"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict");
const read=p=>JSON.parse(fs.readFileSync(p,"utf8"));
const original=read("datos/sanidad_agroexportadora_2026.json");
const old=read("datos/validacion_cientifica_fitosanidad_ux70.json");
const models=read("datos/fitosanitario_modelos_ux69.json");
const a=read("datos/bibliografia_validada_fitosanidad_ux71.json");
const sources=new Map(a.fuentes.map(x=>[x.id,x]));
const ids=new Set(original.organismos.map(x=>x.id));
assert.equal(original.organismos.length,23);
assert.equal(a.fichas.length,23);
assert.equal(sources.size,a.fuentes.length,"No puede haber IDs bibliográficos duplicados");
assert.equal(a.fuentes.length,35);
assert.equal(a.inventario.fichas,original.organismos.length);
for(const f of a.fichas){
 assert.ok(ids.has(f.id_ficha),"Ficha inexistente "+f.id_ficha);
 const source=original.organismos.find(o=>o.id===f.id_ficha);
 assert.equal(f.cultivo_id,source.crop_id);
 assert.equal(f.tipo,source.tipo);
 assert.equal(f.nombre_actual,source.agentes);
 assert.equal(f.habilitar_mapa_riesgo,false,"No hay validación de riesgo local: "+f.id_ficha);
 assert.equal(f.calibrado_lambayeque,false);
 assert.equal(f.registro_SENASA_producto_verificado,false);
 assert.ok(f.referencias_especificas.length>=1,"Sin fuente "+f.id_ficha);
 assert.ok(f.nota_revision.length>=55,"Falta advertencia científica "+f.id_ficha);
 assert.ok(f.variables_y_verificaciones_requeridas.length>=3);
 for(const id of f.referencias_especificas){
  assert.ok(sources.has(id),"Referencia inexistente "+id);
  const citation=sources.get(id);
  assert.match(citation.url,/^https:\/\//);
  if(citation.doi)assert.ok(citation.url.includes(citation.doi)||citation.url.startsWith("https://doi.org/"));
  assert.ok(citation.alcance_y_limitacion.length>=30);
 }
}
assert.equal(new Set(a.fichas.map(f=>f.id_ficha)).size,23);
assert.equal(old.auditadas.length,a.fichas.length);
assert.equal(models.models.length,2);
assert.equal(a.extension_cafe.length,2);
assert.equal(a.fichas.filter(f=>f.nivel_geografico==="local_grupo").length,1);
assert.equal(a.fichas.filter(f=>f.nivel_geografico==="muestras_lambayeque").length,1);
assert.equal(a.fichas.find(f=>f.id_ficha==="maracuya-enfermedad-2").nivel_geografico,"muestras_lambayeque");
assert.equal(a.fichas.find(f=>f.id_ficha==="mango-plaga-1").nivel_geografico,"local_grupo");
assert.equal(a.fichas.find(f=>f.id_ficha==="palto-plaga-2").estado_bibliografico,"evidencia_directa_insuficiente");
assert.ok(a.discrepancias_clave.some(x=>x.detalle.includes("Oxapampa")&&x.detalle.includes("granadilla")));
assert.ok(a.discrepancias_clave.some(x=>x.detalle.includes("8.47")&&x.detalle.includes("9.1")));
assert.ok(a.discrepancias_clave.some(x=>x.detalle.includes("22/30")&&/incidencia|prevalencia/i.test(x.detalle)));
assert.equal(original.organismos.flatMap(o=>o.productos||[]).filter(p=>p.ficha_confirmada===true).length,0);
console.log(JSON.stringify({version:"UX71",fichas_auditadas:a.fichas.length,fuentes_catalogadas:a.fuentes.length,
 fichas_con_evidencia_regional_del_grupo:1,fichas_con_muestras_estudiadas_en_lambayeque:1,
 fichas_con_modelo_local_validado:0,productos_registrados_y_verificados_por_auditoria:0,status:"integridad_documental_correcta"},null,2));
