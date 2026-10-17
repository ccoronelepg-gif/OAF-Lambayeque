# Fase 9P — Continuidad CHIRPS v3 y estabilidad climática por década y sector

**Observatorio Agroclimático y Fitosanitario OAF-Lambayeque.** Fecha de corte documental: 17/10/2026. Estado: extracción de fuentes oficiales contrastadas con dos productos de la misma familia CHIRPS v3 y análisis retrospectivo de estabilidad temporal. **Ninguna zona está certificada como climáticamente homogénea ni se han calibrado pronósticos por polígono.**

## 1. Punto de partida y objetivo

La fase 9O verificó **108 meses mensuales de CHIRPS v3 final (nueve años completos)** entre 1996 y 2025: **1996–2000, 2002, 2011, 2018, 2025**. Quedaban **252 meses** para completar 360. Otras fuentes, conservadas desde 8O/8P, aportan 81 testigos de reanálisis ERA5/ERA5-Land para todos los meses de 1996–2025, **no 81 estaciones**.

El objetivo 9P es reducir, sin fabricar datos, los meses faltantes CHIRPS v3 y verificar si la fuerte correlación entre algunos sectores de la misma intercuenca persiste cuando cambia la selección temporal. Se consideran simultáneamente los **pisos altitudinales**, la clasificación de **42 polígonos físicos experimentales**, las intersecciones ANA/IDEP de 9M y las advertencias de procedencia de estaciones históricas.

## Resultado cuantitativo verificado — fase 9P (17/10/2026)

La fuente alternativa **USGS CHIRPS v3 final GLOBAL** superó los controles sobre **1996-01** y **2025-12**, comparados contra los CHIRPS final LATAM ya archivados. La diferencia máxima de medias de lluvia entre los **39 sectores con celda terrestre válida** fue de **0,000005 mm** en el primer mes y **0,000004 mm** en el segundo; asimismo, se comprobó cada uno de los **81 testigos**. Este contraste demuestra concordancia de los dos archivos para **los meses y posiciones verificados**, no asegura que futuras revisiones del proveedor sean idénticas.

Se recuperaron los **12 meses de 2001**, con SHA-256 propios, para pasar de **108 a 120 meses (10 años completos)** de CHIRPS en el periodo 1996–2025. Persisten **240 meses todavía no comprobados**, sin imputación. Los años completos son **1996–2002, 2011, 2018 y 2025**, distribuidos desigualmente entre décadas:

| Periodo | Años completos CHIRPS 9P | Límite |
|---|---:|---|
| 1996–2005 | **7/10** | Falta 2003–2005 |
| 2006–2015 | **1/10** | Solo 2011: no es un perfil decenal |
| 2016–2025 | **2/10** | 2018 y 2025: insuficiente para inferir estabilidad decenal |
| **1996–2025** | **10/30 años; 120/360 meses** | **NO existe normal completa CHIRPS de 30 años** |

### Sensibilidad temporal de los pares hidrofísicos

El contraste *leave-one-year-out* repite las correlaciones con nueve años cada vez, retirando un año de los diez observados. Se conservan los pares 9M previamente seleccionados, sin escoger puntos por su resultado:

| Sectores y unidad | Correlación histórica CHIRPS | Rango leave-one-year-out | Diferencia de lluvia media |
|---|---:|---:|---:|
| **S002–S003**, intercuenca 137779 | **0,94820** | **0,91569–0,95519** | **3,326 %** |
| **S003–S004**, intercuenca 137773 | **0,94323** | **0,93119–0,95557** | **11,505 %** |

Aunque las correlaciones sobre estos años permanecen relativamente altas, la diferencia de lluvia entre S003 y S004 sigue siendo material. En particular, los tres decenios tienen cobertura profundamente desigual (7/1/2 años), por lo que este experimento **no certifica estabilidad interdecenal de 30 años**. El parecido retrospectivo puede originarse por señal atmosférica común y por la estructura de la misma malla CHIRPS; no equivale a verificación meteorológica espacial independiente ni demuestra habilidad de pronóstico.

**Estado de validación:** 0 zonas climáticas homogéneas certificadas, 0 cuencas operativas oficialmente ratificadas, 0 ajustes NMME por sector con habilidad prospectiva demostrada y 0 alertas fitosanitarias derivadas.

## 2. Fuente oficial alternativa y control de identidad antes de fusionar

Se identificó el directorio **USGS/FEWS NET, CHIRPS v3 FINAL mensual GLOBAL (GeoTIFF, 0,05°)**: [archivo institucional USGS](https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/global/monthly/chirps/final/downloads/monthly/).

**Producto anterior archivado (9O):** [CHC/UCSB, CHIRPS v3 FINAL mensual LATAM](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/).

Aunque ambos se anuncian como CHIRPS v3 final, el cambio de proveedor o dominio de cobertura **no garantiza equivalencia numérica ni idéntica revisión histórica**. Se implementó `modelos/mirror_chirps_9p.py` bajo una política de rechazo por defecto:

1. Descargar **dos meses de referencia**, 1996-01 y 2025-12, previamente confirmados en 9O.
2. Leer exclusivamente la ventana geográfica de Lambayeque en los TIFF GLOBAL, mediante SIG raster y verificar CRS EPSG:4326, resolución 0,05° y cuadrante.
3. Comparar **los 42 sectores** (media de las celdas internas) y **los 81 testigos** (píxel exacto) contra las filas 9O originales. No sustituir celdas marinas/sin datos por lluvia cero.
4. Rechazar el espejo si las diferencias de cualquier valor superan **0,04 mm** sobre los registros redondeados a 5 decimales o si cambió la máscara de datos. Este margen es una tolerancia de **identidad de producto**, no un error tolerado para cultivos.
5. Solo si ambas pruebas pasan, agregar en lotes **máximo cuatro meses inéditos por ejecución**, cada uno con URL, formato global, SHA-256 del TIFF original, 42 filas de sector y 81 filas de testigo. Nunca sobrescribir una fuente anterior ni confundir CHIRPS v3 *preliminary* o v2 con *final*.
6. Si el servicio institucional devuelve un error (403, 404, timeout), conservar su causa y **0 incorporaciones** en vez de atribuirlas a datos inexistentes.

La salida del ensayo de equivalencia y los meses adicionales se publican en `datos/continuidad_9p/fuentes_adicionales_chirps_9p.json`, `meses_adicionales_sectores_9p.csv` y `meses_adicionales_testigos_9p.csv`. Los archivos GLOBAL (~22 MB) no se incorporan al repositorio, para evitar multiplicar gigabytes de imágenes: sus huellas SHA-256 y URL permiten verificar una descarga posterior. La comparación de datos derivada se conserva con sus identificadores.

## 3. Estabilidad temporal realmente comprobable

La evaluación utiliza solo **años con los 12 meses CHIRPS presentes**, para cada sector, y separa las décadas:

| Década | Año y cobertura | Interpretación |
|---|---|---|
| 1996–2005 | Se cuentan únicamente años completos reales | Cinco años no equivalen a climatología decenal completa |
| 2006–2015 | Se cuentan únicamente años completos reales | Una cantidad pequeña de años no certifica estabilidad climática |
| 2016–2025 | Se cuentan únicamente años completos reales | La evaluación climática puede estar insuficientemente muestreada |

Los pares preidentificados en 9M/9O son **S002–S003** (intercuenca 137779) y **S003–S004** (intercuenca 137773). No se eligen pares ni umbrales según su mejor puntuación observada.

La correlación de anomalías de lluvia se evalúa sobre `log1p(P)` con el promedio de cada mes calendario eliminado. El análisis calcula:

- Correlación de todos los años efectivamente presentes.
- Correlación excluyendo uno de los años por iteración (*leave-one-year-out*), reportando mínimo, mediana y máximo, sin declarar el resultado una validación ex ante.
- Correlaciones prescindiendo respectivamente de los primeros cinco años del archivo y del periodo 2016–2025, cuando hay al menos dos años completos restantes.
- Diferencia porcentual de precipitación media acumulada entre los sectores, calculada sobre exactamente los mismos meses válidos.
- Disponibilidad explícita para los **30 años × 42 sectores**, sin fingir que un vacío es 0 mm.

El análisis deja `null` para indicadores no evaluables, y separa claramente estabilidad de la señal regional compartida de homogeneidad entre parcelas. **Los residuos calculados con información histórica retrospectiva no miden habilidad de pronóstico emitido con anterioridad.**

## 4. Alcance científico y agricultura

Los sectores y familias C01, C02 y C03 son de similitud **exploratoria**: altitud, ladera, pertenencia a una unidad hidrográfica y correlación de lluvia no prueban microclimas homogéneos. Especialmente en el litoral, los sectores **S028, S032 y S034** no tenían centros de píxel CHIRPS terrestres válidos dentro del polígono original 9O. Esa limitación se sigue representando como **falta de soporte espacial**, no como precipitación cero.

Las tres estaciones históricas de 9I tienen datos repartidos en seis años históricos y coordenadas documentales alternativas. Comparar CHIRPS con pluviómetros que pudieron entrar en el algoritmo CHIRPS v3 puede implicar dependencia. No declarar independencia, ni extrapolar datos a parcelas.

Se mantienen **0 zonas homogéneas instrumentalmente certificadas**, **0 habilitaciones automáticas de predicción zonal**, **0 alertas de arándano/vid basadas en estos grupos** y **0 cuencas institucionales ratificadas como unidades operativas**. Las series ERA5/ERA5-Land son un apoyo climático de 30 años, no certificación de datos de campo ni sustitutos de ENFEN.

## 5. Entregables reproducibles y estado de publicación

| Entregable | Destino |
|---|---|
| Verificador de equivalencia USGS-CHC y extracción gradual | [mirror_chirps_9p.py](modelos/mirror_chirps_9p.py) |
| Comparación temporal sin selección oportunista de años | [estabilidad_climatica_9p.py](modelos/estabilidad_climatica_9p.py) |
| Resultados auditados, meses presentes y faltantes | [estado_estabilidad_9p.json](datos/continuidad_9p/estado_estabilidad_9p.json) |
| Comparación temporal de dos parejas de intercuenca | [pares_estabilidad_temporal_9p.csv](datos/continuidad_9p/pares_estabilidad_temporal_9p.csv) |
| Serie anual con conteo de meses y valores faltantes | [precipitacion_anual_9p.csv](datos/continuidad_9p/precipitacion_anual_9p.csv) |
| Fuente alternativa, controles y SHA-256 | [fuentes_adicionales_chirps_9p.json](datos/continuidad_9p/fuentes_adicionales_chirps_9p.json) |
| Portal interactivo en Análisis de clima regional | [visor_estabilidad_9p.js](modelos/visor_estabilidad_9p.js) |
| CI científica para reproducir análisis | [oaf_estabilidad_9p.yml](.github/workflows/oaf_estabilidad_9p.yml) |

El tablero compara las tres décadas y los rangos de correlación calculados, indica la cantidad de meses disponibles, el estado de equivalencia de los productos y mantiene las advertencias de ausencia de observaciones independientes.

## 6. Próxima fase 9Q

Con los registros disponibles y la fuente alternativa contrastada, extender el muestreo temporal CHIRPS v3 por tandas espaciadas sin vulnerar límites del proveedor; cuando existan **360 meses realmente disponibles** construir normales completas y sus anomalías. A continuación, revisar divisorias de cuencas, exposición, clima entre celdas diferentes y presencia de estaciones SENAMHI externas. Solo una validación temporal y espacial fuera de muestra permitiría definir zonas predictivas operativas; el material fitosanitario para **arándano y vid** requerirá incidencia de campo, fenología, umbrales científicos y verificación por cultivo.

**Referencias de fuente:** CHIRPS v3: Climate Hazards Center Infrared Precipitation with Stations, versión 3, DOI [10.15780/G2JQ0P](https://doi.org/10.15780/G2JQ0P); información metodológica en [Scientific Data](https://www.nature.com/articles/s41597-026-07096-4).
