/* UX64 · Regresión de geoservicios SIGRID usados por los visores territoriales.
 * Ejecutar: node tests/auditoria_ux64_sigrid.cjs
 * Valida metadatos y estructura de consultas; no sustituye la comprobación visual del mapa.
 */
"use strict";
const assert = require("node:assert/strict");
const BASE = "https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer";
const BBOX = [-80.95, -7.25, -78.95, -5.35];
async function request(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(url, { signal: controller.signal, headers: { accept: "application/json" } });
    assert.equal(response.ok, true, "HTTP " + response.status + " en " + url);
    const data = await response.json();
    assert.equal(Boolean(data.error), false, data.error?.message || "Error ArcGIS");
    return data;
  } finally { clearTimeout(timer); }
}
async function metadata(id, type, geometryType) {
  const data = await request(BASE + "/" + id + "?f=json");
  assert.equal(data.type, type, "Tipo incorrecto en capa " + id);
  if (geometryType) assert.equal(data.geometryType, geometryType, "Geometría incorrecta en capa " + id);
  return data;
}
async function query(id, where, outFields) {
  const params = new URLSearchParams({
    where, geometry: BBOX.join(","), geometryType: "esriGeometryEnvelope",
    inSR: "4326", outSR: "4326", spatialRel: "esriSpatialRelIntersects",
    returnGeometry: "true", outFields, resultRecordCount: "2000", f: "geojson"
  });
  const data = await request(BASE + "/" + id + "/query?" + params);
  assert.ok(Array.isArray(data.features), "La capa " + id + " no devolvió features[]");
  for (const feature of data.features) {
    assert.ok(feature.geometry, "Geometría vacía en capa " + id);
    assert.ok(["Point","MultiPoint","LineString","MultiLineString","Polygon","MultiPolygon"].includes(feature.geometry.type),
      "Geometría no compatible en capa " + id);
  }
  return data.features.length;
}
(async () => {
  const layers = [
    [6010100, "Feature Layer", "esriGeometryPoint"],
    [6020100, "Feature Layer", "esriGeometryPolygon"],
    [6020200, "Feature Layer", "esriGeometryPolygon"],
    [6020300, "Feature Layer", "esriGeometryPolygon"],
    [6030200, "Feature Layer", "esriGeometryPolyline"],
    [6040000, "Feature Layer", "esriGeometryPoint"]
  ];
  await Promise.all(layers.map(([id,type,geometry]) => metadata(id,type,geometry)));
  const [historic, rivers, districts, droughts] = await Promise.all([
    query(6010100, "nom_dep LIKE '%LAMBAYEQUE%'", "nom_dep,tipo_pel,fecha_doc,fuente"),
    query(6030200, "tipo IN ('R','RN','RI','RS','AC')", "tipo,nombre,r_q_text"),
    query(6020300, "iddpto='14'", "iddpto,iddist,nombdist,nombprov"),
    query(6040000, "nom_dep LIKE '%LAMBAYEQUE%'", "nom_dep,nom_prov,nom_dist,fecha,fenomeno")
  ]);
  console.log(JSON.stringify({
    revision: "UX64", servicio: BASE, estado: "metadatos_y_consultas_correctos",
    capas: layers.map(x => x[0]), resultados: {
      puntos_geologicos_INGEMMET_2017: historic,
      tramos_hidrograficos_IGN: rivers,
      distritos_INEI: districts,
      emergencias_INDECI_2003_2020: droughts
    },
    nota: "Cero registros no se interpreta como ausencia de peligro; la prueba valida respuesta y geometría del servicio."
  }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
