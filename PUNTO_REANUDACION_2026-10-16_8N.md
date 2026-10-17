# OAF-Lambayeque — Punto de reanudación 16/10/2026 · Fase 8N

## Estado técnico confirmado
**Parte 8N implementada y verificada**, primera malla regional para establecer zonas agroclimáticas espacial y altitudinalmente diferenciadas, paso previo a modelos predictivos por ambiente.

Se conservó el proyecto en GitHub `ccoronelepg-gif/OAF-Lambayeque`, rama `main`; portal https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.

### Datos reales de la fase 8N
- Límite **histórico simplificado y referencial**, procedente de `juaneladio/peru-geojson`, departamento Lambayeque UBIGEO 14. **NO equivale a un límite IGN/INEI vigente acreditado.** Contrastar con INEI IDE e IGN en siguientes fases. El documento `datos/zonificacion_8n/limite_lambayeque_referencial.geojson` incluye fuente.
- Cuadrícula de **69 puntos interiores** con paso **0,125°**; NO representa una malla raster total, porcentaje de superficie territorial ni predios agrícolas.
- Open-Meteo Elevation API devolvió altitudes DEM para **69/69 puntos**, en **dos lotes** archivable con JSON comprimido, URL, hora y SHA-256: directorio `datos/zonificacion_8n/elevacion_fuentes/`.
- **Clasificación altitudinal de diseño**, no zonificación climática validada:
  - 35 puntos, 0–99 m, planicie muy baja.
  - 18 puntos, 100–299 m, planicie/valle bajo.
  - 6 puntos, 300–799 m, piedemonte.
  - 3 puntos, 800–1599 m, ladera baja.
  - 4 puntos, 1600–2499 m, ladera media.
  - 1 punto, ≥2500 m, parte alta andina (3236 m).
  - 2 puntos, cotas DEM negativas (-2 a -1 m), verificar precisión/datum, sin imputar.
- **0 zonas agroclimáticas verdaderamente homogéneas acreditadas y 0 pronósticos zonales operativos validados**. Los cortes en metros son PRELIMINARES e impuestos únicamente para muestreo; NO valores normativos/ecológicos oficiales.
- Los cuatro puntos antiguos OAF del 8M son referencias **costeras y valles**; no representan laderas y cabeceras de Lambayeque.

### Implementación real
- `modelos/zonificacion_preliminar_8n.py`: geografía (punto-en-polígono), malla, API DEM y validación, estratos provisionales, informe determinista sin datos ficticios.
- `tests/test_zonificacion_8n.py`: 8 pruebas sintéticas aisladas sobre límite, calendario de malla, SHA, DEM incompleto, bandas, cobertura y no homologación prematura.
- `.github/workflows/oaf_zonificacion_8n.yml`: CI en cambios de código y mensual, revisa fuentes y genera productos.
- `datos/zonificacion_8n/estado_8n.json` / `nodos_altitudinales_8n.csv` / `malla_geografica_8n.csv`: resultados documentados y auditados.
- `modelos/visor_zonificacion_8n.js` + `index.html`: mapa interactivo de 69 puntos/leyenda/estratos y filtros en sección «Verificación de datos».
- `FASE_8N_ZONIFICACION_AGROCLIMATICA.md`: metodología, estándares, límites científicos, plan para aglomeración climática verdaderamente homogénea.
- Tests del 8N y regresiones de 8I,8J,8K,8L,8M y checks generales pasaron en commit web 8N; run de 8N `38992598970` success.

### Regla metodológica permanente
La altitud **NO determina por sí sola** una zona climática homogénea. Antes de definir zonas predictivas hay que incorporar longitudinalmente clima 1996–2025 por nodos y por estratos (Tmean, Tmax/Tmin, lluvia, RH, radiación, evapotranspiración y otras variables), exposición costa/valle/orientación y relieve; controlar estaciones SENAMHI, incertidumbre, continuidad espacial y validación fuera de muestra.

**No extrapolar los cuatro municipios OAF a toda Lambayeque** ni declarar modelo climático/zona aprobado solo por poseer altitud DEM. Alta montaña tiene un solo nodo y necesita densificación especial. No inferir enfermedades de arándano/vid sin campo y fenología; no confundir Niño Costero con temperatura local ni atribuir a OAF alertas oficiales de ENFEN.

### Parte siguiente recomendada: 8O
1. Contrastar la geometría con límites IGN/INEI e incrementar nodos en zonas montañosas y transiciones. Usar DEM con proyección/área adecuados; salida actual no da porcentaje de hectáreas.
2. Implementar descarga por lotes/cortes (respetando rate limit) de 1996–2025 para clima multivariable en puntos representativos de cada piso, con pref. SENAMHI cuando esté disponible.
3. Construir agrupación **espacial y climática** usando similitud de las normales mensuales/anuales, amplitud térmica, precipitación, humedad, radiación y altitude; evaluar clústeres contiguos/estacionales, con incertidumbre y validación espacial cruzada. No adoptar automáticamente seis o siete zonas porque fueron los estratos de muestreo.
4. Solo entonces estudiar modelos de anomalías por zona y pronósticos experimentales, evaluar sesgo de downscaling Open-Meteo `elevation=nan` frente a default en experimento separado, y diferenciar cultivo/fenología.
5. Mantener módulos ENFEN/OAF, arándano y vid con fuentes institucionales y documentos científicos. Climatología OAF 1996–2025, OMM comparativa 1991–2020.

El usuario prefiere avance ejecutivo automático sin cuestionarios ni tareas manuales.
