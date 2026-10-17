# Fase 9N — Completar la cobertura DEM de los 42 sectores, evaluar incertidumbre y preparar validación climática independiente

**Observatorio Agroclimático y Fitosanitario OAF-Lambayeque · 17 de octubre de 2026.**

## 1. Objetivo y estado real

Ampliar la revisión cartográfica de 9M (35 sectores con DEM en una tesela) hasta los **42 sectores físicos exploratorios de 9K**, sin identificar una zona climáticamente homogénea solo porque los píxeles de relieve son parecidos. Diferenciar cobertura geométrica de cobertura instrumental, contrastar la sensibilidad a resolución de trabajo y priorizar sectores para verificar lluvia y temperatura con observaciones independientes.

**Resultado:** los **42/42 polígonos de 9K** alcanzan el criterio **geométrico** de cobertura completa (≥99,5 % de su contorno asociado a teselas válidas); el número no equivale a 42 microclimas homogéneos ni a 42 sectores productivos. Se descargaron y auditaron **cuatro nuevos archivos GeoTIFF Copernicus** y se reutilizó un original de 9L, de modo que hay **cinco teselas con fuente física real**.

La sexta tesela solicitada, **S08 W081**, devuelve HTTP 404 en el repositorio AWS de Copernicus. La caja geográfica de esa tesela surgió al examinar los extremos de las coordenadas de un polígono amplio, pero **ninguno de los 42 polígonos tiene una intersección de superficie significativa con la tesela ausente**. Por ello los 42 pueden superar el umbral de cobertura geométrica, a la vez que la auditoría conserva la ausencia original. **No se asigna elevación cero en las teselas faltantes ni se presupone su carácter terrestre u oceánico sin corroboración.**

## 2. Datos fuente, archivo inmutable y regionalización

Fuente: **Copernicus DEM GLO-90**, Cloud Optimized GeoTIFF, Digital Surface Model (DSM) 2021, unos 90 m en el ecuador. Como DSM, representa además vegetación, edificios e infraestructura. No es topografía instrumentada a escala de parcela. Documentación primaria: [AWS Registry of Open Data](https://registry.opendata.aws/copernicus-dem/) y [estructura de los archivos GLO-90](https://copernicus-dem-90m.s3.amazonaws.com/readme.html).

| Tesela 1° × 1° | Estado y trazabilidad |
|---|---|
| **S06 W080** | GeoTIFF nuevo archivado con SHA-256 |
| **S06 W081** | GeoTIFF nuevo archivado con SHA-256 |
| **S07 W080** | Original SHA-256 archivado y reutilizado desde 9L |
| **S07 W081** | GeoTIFF nuevo archivado con SHA-256 |
| **S08 W080** | GeoTIFF nuevo archivado con SHA-256 |
| **S08 W081** | Fuente no disponible, HTTP 404; jamás se trata como terreno plano |

Los archivos permanecen bajo `datos/cobertura_multitesela_9n/fuentes/`, salvo el original 9L que no se duplica ni sobrescribe. Cada tesela se verifica por **bytes y SHA-256**, TIFF real, una banda, EPSG:4326, dimensiones y contorno de 1° esperado; el inventario `fuentes_dem_9n.json` asocia origen HTTP y huella con cada elemento. Los fallos quedan en `teselas_no_disponibles_9n.json`, no se omiten del conteo.

## 3. Método reproducible y prevención de falsa precisión

1. Leer los 42 polígonos exploratorios 9K con su **piso altitudinal físico preliminar** (costa, valle, piedemonte, laderas y montaña; cotas DEM negativas separadas).
2. Detectar teselas desde las **cajas envolventes**, pero medir intersección verdadera con la geometría y distinguir tesela necesaria por cuadro de consulta de la superficie que realmente se debe procesar.
3. Procesar todas las teselas disponibles en sus **coordenadas originales**, recortando cada polígono al cuadrante válido, sin extender elevaciones a teselas 404.
4. Comparar alturas, orientaciones del descenso de ladera y pendiente con resoluciones de análisis aproximadamente **270 m** y **450 m** (agregación del GLO-90). En ambas se evalúan los límites de pendiente **20°, 30°, 40°** como parámetros de sensibilidad, no como umbrales de aptitud agrícola.
5. Mantener el mismo **piso altitudinal por píxel**; no suponer que un nodo de 800–1599 m describe necesariamente toda su superficie. Excluir valores no finitos, celdas sin vecinos para gradiente y puntos fuera del polígono.
6. Conservar explícitamente cada fracción geométrica de cobertura de origen, número de teselas, fracción de píxeles que cumplen altitud y pendiente, diferencia entre escalas y geometría filtrada. No confundir diferencia de máscaras de relieve con skill climatológico, capacidad predictiva ni pronóstico fitosanitario.
7. Ejecutar control de reproducción offline contra los archivos originales; verificar que las geometrías finales estén incluidas en su sector 9K y que **ninguna zona sea declarada homogénea o validada**.

## 4. Cobertura y sensibilidad observadas

| Indicador | Fase 9M | Fase 9N |
|---|---:|---:|
| Sectores con cobertura completa (≥99,5 % del contorno) | 26 | **42** |
| Sectores con cobertura parcial | 9 | **0** |
| Sectores sin DEM evaluable | 7 | **0** |
| Total de polígonos originales registrados | 42 | **42** |
| Teselas de fuente GLO-90 válidas | 1 | **5** |
| Tesela adicional consultada sin archivo | — | **1** |

El **cambio absoluto mediano** de la fracción de píxeles compatibles con el piso nominal y pendiente ≤30°, al pasar de 270 m a 450 m, fue **0,01459 (1,459 puntos porcentuales)** entre los 42 polígonos. La diferencia máxima fue **0,17957 (17,957 puntos)**, identificada en el sector **S019**, asociado preliminarmente al piso de **1600–2499 m**. Estos porcentajes describen la sensibilidad de la máscara raster al método de análisis, **no un error de pronóstico de precipitación ni una estadística de superficie agrícola**.

Los sectores de elevación negativa se conservan separados para revisión, ya que el DSM y las áreas próximas a la línea de costa pueden contener celdas marinas y referencias verticales cuyo significado requiere comprobación. No se transforman automáticamente en un tipo de campo o zona apta.

**Nota temporal:** 9N utiliza un DSM de época anterior y no un pronóstico ambiental emitido en 2026. No hay inferencia prospectiva a partir de sus pendientes.

## 5. Comparación hidrográfica y limitación de las agrupaciones

Se mantienen las **17 geometrías ANA/IDEP** descargadas en 9M, **91 intersecciones referenciales** y **107 fragmentos hidrofísicos cartográficos**. No se reinterpretan automáticamente como 107 microclimas. El cálculo de 9N refina la capa de elevación y pendiente, sin modificar los límites originales de ANA ni certificar su vigencia.

Solo **dos fragmentos** del inventario 9M unieron superficies de dos sectores físicos 9K (HM011 y HM015), ambos de carácter preliminar. La delimitación operativa necesita revisar además divisorias naturales, escorrentía, estaciones y la representatividad de cada piso. No se usa el cruce geométrico con ANA como validación independiente del clima.

## 6. Preparación de contrastes instrumentales y prioridad de trabajo

La fase añade `modelos/prioridades_validacion_9n.py`, que marca para los **42 sectores** los motivos de revisión antes de afirmar uniformidad: ausencia de cobertura, desnivel contradictorio entre piso nominal y relieve raster, cambios importantes entre resoluciones, falta de testigo climático próximo y cotas DEM negativas.

El inventario climático ya documentado dispone de **81 testigos con perfiles retrospectivos 1996–2025**, pero **no son 81 estaciones instrumentales independientes**: están derivados de ERA5 y ERA5-Land. Los **51 pares de semejanza climática** de 8P incluyen solo **seis pares con centros diferentes en ambos reanálisis**, de los cuales **cinco** pertenecen al mismo piso físico. Son pruebas de consistencia entre celdas modeladas, no independencia meteorológica.

La fase 9I recuperó **213 meses estación únicos** en **tres estaciones históricas**, distribuidos en seis años: 1996, 1998, 2002, 2007, 2011 y 2013. No representan un archivo instrumental homogéneo de 30 años. Además, las coordenadas históricas presentan alternativas documentales no resueltas.

**CHIRPS v3 (0,05°) incluye datos de estaciones pluviométricas en su producto final**, por lo que comparar directamente CHIRPS v3 y los pluviómetros que podrían haber sido incorporados en su elaboración no demuestra independencia estricta. Se requiere identificación de observaciones usadas para asimilación y, preferentemente, muestreo fuera de esas estaciones. Documentación: [Climate Hazards Center – CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3).

En consecuencia: **0 zonas homogéneas instrumentalmente certificadas, 0 modelos calibrados de pronóstico zonal, 0 alertas de enfermedad de arándano/vid derivadas de estos polígonos**.

## 7. Recursos entregados

- [Motor multipieza GLO-90](modelos/cobertura_multitesela_9n.py), conservando archivos originales y verificando SHA.
- [Mapa de sectores DEM filtrados](datos/cobertura_multitesela_9n/mascaras_multitesela_9n.geojson).
- [Tabla de cobertura y sensibilidad para los 42 sectores](datos/cobertura_multitesela_9n/evaluacion_42_sectores_9n.json).
- [Estado territorial y comparación con 9M](datos/cobertura_multitesela_9n/estado_cobertura_9n.json).
- [Manifiesto de descargas y errores por tesela](datos/cobertura_multitesela_9n/fuentes_dem_9n.json) y [lista de archivos faltantes](datos/cobertura_multitesela_9n/teselas_no_disponibles_9n.json).
- [Prioridades de contraste climático, sin inventar observaciones](datos/cobertura_multitesela_9n/prioridades_validacion_climatica_9n.json).
- [Pruebas topográficas e integridad](tests/test_cobertura_9n.py), [workflow de descarga y QA](.github/workflows/oaf_cobertura_9n.yml).
- [Visor público](modelos/visor_multitesela_9n.js) dentro de **Análisis de clima regional** con filtros por piso y cobertura y advertencia explícita sobre los datos faltantes.

Las cinco pestañas, capas, dashboards y análisis 8O–9M quedan conservados.

## 8. Próxima fase 9O

La fase 9O deberá **evaluar verdaderamente la homogeneidad climática en lugar de inferirla solo del relieve**. En particular, producir mapas de precipitación CHIRPS v3 1996–2025, cruzar la rejilla 0,05° con sectores físicos y unidades ANA, reconocer explícitamente píxeles y observaciones compartidas, comparar variabilidad intra/intersector con climatologías temporales independientes, realizar sensibilidad temporal y examinar la relación entre precipitación, radiación, VPD, HR, temperatura y elevación. Incorporar estaciones observadas y metadatos SENAMHI para contraste ajeno a la grilla, y empezar validación prospectiva solo cuando los pronósticos archivados tengan tiempo de emisión e información de verificación madura.

**No existe fundamento todavía para emitir una predicción diferenciada por los 107 fragmentos o recomendar tratamientos fitosanitarios a partir de su semejanza geométrica.**
