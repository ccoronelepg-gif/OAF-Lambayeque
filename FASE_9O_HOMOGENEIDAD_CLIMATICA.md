# Fase 9O — Evaluación exploratoria de semejanza climática por sector y cuenca

**OAF-Lambayeque | Fecha de corte: 17/10/2026 | Estado:** metodología científica reproducible, primeras series CHIRPS verificadas, perfiles completos ERA5/ERA5-Land. Los resultados son retrospectivos y **no validan homogeneidad, aptitud de cultivo ni pronósticos**.

## 1. Objetivo

Contrastar las **42 superficies experimentales** de 9K–9N, divididas por pisos altitudinales y unidades hidrográficas de ANA/IDEP, con **precipitación satélite-pluviómetros CHIRPS v3** (0,05°; final mensual) y variables ERA5/ERA5-Land (temperatura, precipitación, humedad relativa y radiación de onda corta). Descartar la idea de que dos sectores parecidos geográficamente necesariamente tienen clima igual.

**Periodo de referencia principal: 1996–2025.** La referencia OMM 1991–2020 se mantiene para comparabilidad, no se intercambia con 1996–2025 ni con la climatología propia de NOAA NMME.

## 2. Distinción estricta de fuentes y observaciones

| Capa | Periodo | Variables | ¿Observación independiente? |
|---|---|---|---|
| CHIRPS v3 final LATAM | Muestra de **nueve años completos**: 1996–2000, 2002, 2011, 2018 y 2025 (108 meses verificados) | Lluvia mensual en celdas de 0,05° | **No se ha probado independencia**: incorpora pluviómetros. La grilla no representa 30 años completos de normales, aunque los años elegidos atraviesan el periodo. |
| ERA5-Land por Open-Meteo, fuentes congeladas 8O y 8P | **1996–2025 completos** | Temperatura media, máxima y mínima | Reanálisis, no estación de campo. |
| ERA5 por Open-Meteo, fuentes congeladas 8O y 8P | **1996–2025 completos** | Lluvia, humedad relativa y radiación | Reanálisis, con píxeles compartidos entre testigos. |
| Tres estaciones documentadas 9I | Meses efectivamente archivados en seis años **1996, 1998, 2002, 2007, 2011, 2013** | Lluvia instrumental retrospectiva | Ubicación histórica y posible dependencia con estaciones usadas por CHIRPS no están certificadas. |

CHIRPS: [Climate Hazards Center — CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) y [archivo mensual LATAM](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/). CHIRPS v3 combina estimaciones satelitales con datos de estaciones. ERA5/ERA5-Land accedido en bloques archivados mediante Open-Meteo desde fases 8O y 8P.

**Por qué CHIRPS tiene nueve años y no treinta:** el intento inicial de descargar 360 GeoTIFF confirmó 60 meses (1996–2000), pero las solicitudes posteriores devolvieron HTTP **403** del proveedor. Una segunda tanda deliberadamente distribuida entre décadas confirmó otros 60 meses (1996, 2002, 2011, 2018, 2025); se fusionaron ambos conjuntos sin duplicar los 12 meses de 1996, verificando sus SHA-256. **Resultado: 108 meses de nueve años completos, 252 meses sin datos comprobados.** Los HTTP 403 documentan fallos de acceso, no ausencia climatológica. No se ha calculado una normal CHIRPS completa de 30 años. Los perfiles ERA5/ERA5-Land sí cubren los 360 meses de 1996–2025.

## 3. Método de extracción geográfica

`modelos/chirps_homogeneidad_9o.py` toma los 42 polígonos SIG 9K, los 81 testigos y 108 meses efectivamente verificados de CHIRPS v3 final LATAM. Para cada archivo:

1. Verifica que es GeoTIFF de una banda, EPSG:4326, resolución 0,05° y dominio de Lambayeque.
2. Lee solo el recorte regional y convierte celdas inválidas (incluyendo **-9999** del océano y ausencia de datos) en valores faltantes, **nunca en lluvia cero**.
3. Obtiene la media y dispersión espacial de **píxeles cuyos centros caen dentro** del polígono (no estaciones), con los píxeles inválidos excluidos. Si ningún centro de celda válido cae dentro, el sector queda con valor ausente.
4. Conserva el píxel CHIRPS de cada testigo, las coordenadas del centro y registra explícitamente cuándo dos testigos consultan el mismo píxel.
5. Registra URL y SHA-256 del GeoTIFF original por mes, además de meses no verificados. Por tamaño y gestión de repositorio no conserva dentro de GitHub los aproximadamente 1,5 GB que representarían los 360 TIFF originales. Para reproducir la extracción es necesario **volver a descargar el original y comparar SHA antes de usarlo**.

La media de los píxeles es una **media espacial no ponderada por áreas pequeñas**, pues los centros del rango estrecho de latitudes varían poco en superficie, pero no es una integral exacta de precipitación sobre un polígono agrícola. La desviación estándar es heterogeneidad **entre píxeles del producto**, no entre sensores independientes. Una celda compartida no da réplicas adicionales.

## 4. Climatología multivariable y comparación por unidades hidrográficas

`modelos/diagnostico_homogeneidad_9o.py` reconstruye exactamente los bloques crudos 8O (19 puntos) y 8P (62 puntos) para 81 testigos × 360 meses. Comprueba temperatura (ERA5-Land), lluvia/humedad/radiación (ERA5), fechas y perfiles completos. Produce **972 registros de normales mensuales ERA5/ERA5-Land** (81 × 12) y **504 registros de lluvia CHIRPS por sector y mes calendario** (42 × 12). Para CHIRPS, cada normal muestra el número real de años disponibles. Un valor basado en cinco años es *muestra histórica parcial*, no promedio de 30 años.

Se comparan dos tipos de parejas:
- **Tres familias preliminares C01–C03** de similitud climática 9K, con testigos a distintas altitudes dentro de su piso. El sistema cuantifica sobre los 108 meses comunes verificados, cuando existen datos, correlación de anomalías desestacionalizadas de `log1p(lluvia)`, diferencias de lluvia y diferencias de temperatura de reanálisis. Píxeles repetidos de CHIRPS quedan marcados.
- **Pares de sectores con una intercuenca común**, candidatos en fase 9M, especialmente S002–S003 y S003–S004 (HM015 y HM011). La correlación de series CHIRPS y la diferencia de lluvia son descriptivas, **no una decisión de fusionar**. Cualquier pareja sin suficientes meses comunes se rotula insuficiente.

Los 81 perfiles de reanálisis cubren 1996–2025; la independencia espacial de sus celdas y la homogeneidad del área comprendida entre dos nodos **no están demostradas**. Para declarar una zona operativa haría falta estación instrumental independiente, comprobación física de cuenca y relieve, separación espacial de entrenamiento/prueba y evidencia de estabilidad histórica.

## 4A. Resultados cuantitativos auditados el 17/10/2026

Se recuperaron **108 GeoTIFF mensuales CHIRPS v3 final** con URL y SHA-256 por archivo, lo que permite evaluar **nueve años completos**: 1996–2000, 2002, 2011, 2018 y 2025. Otros **252 meses de 1996–2025** no están verificados; ningún valor faltante fue imputado ni confundido con precipitación de 0 mm. El archivo digital de reanálisis previo permite, independientemente de CHIRPS, reconstruir **81 testigos × 360 meses** de temperatura, lluvia ERA5, humedad relativa y radiación, y elaborar **972 normales de mes calendario** de reanálisis.

Entre las **42 superficies de influencia**, **39** contienen al menos un píxel terrestre CHIRPS cuyo centro está dentro del polígono; **S028, S032 y S034** no tienen celdas de consulta con valor válido en la malla seleccionada. La ausencia puede responder al tamaño o posición del polígono respecto del píxel, y **no demuestra ausencia de tierra, ausencia de lluvia ni ausencia de actividad agrícola**. Los 81 testigos se ubican en **80 píxeles CHIRPS distintos**; una posición de celda está compartida y no cuenta como observación independiente.

### Parejas con la misma unidad hidrográfica de referencia (9M)

Se calculó correlación sobre la lluvia mensual CHIRPS en escala `log1p`, restando la media de cada mes calendario para reducir el ciclo estacional. El resultado es descriptivo del producto y los años muestreados, no prueba de independencia instrumental:

| Sectores 9K | Unidad hidrográfica referencial | Correlación de anomalías (108 meses) | Diferencia relativa media de lluvia | ¿Fusión validada? |
|---|---|---:|---:|---|
| S002–S003 | Intercuenca 137779 | **0,95158** | **2,848 %** | **No** |
| S003–S004 | Intercuenca 137773 | **0,94382** | **12,674 %** | **No** |

La correlación relativamente alta de dos sectores se puede deber a variabilidad regional común y a píxeles interpolados por el mismo producto. Las diferencias de lluvia, elevación y exposición física siguen siendo motivos válidos para **mantener cautela** antes de fusionar. Ninguna cifra es una estimación de error de pronóstico.

### Contraste de los núcleos preexistentes C01, C02 y C03

- **C01, piedemonte:** dos testigos con correlación de anomalías CHIRPS de **0,845** y diferencia media de temperatura ERA5-Land de **0,948 °C**.
- **C02, montaña alta:** tres pares de testigos con correlaciones CHIRPS aproximadas **0,863–0,920**, pero uno presenta diferencia media de lluvia CHIRPS cercana a **24,9 %**; compartir tendencias no implica lluvia equivalente.
- **C03, ladera media:** tres pares con correlaciones CHIRPS aproximadas **0,908–0,963** y diferencias de temperatura modelada de hasta **1,139 °C**.

Las cifras se derivan de píxeles CHIRPS y ERA5/ERA5-Land, no de sensores independientes ubicados en los extremos. Por tanto se mantienen **tres núcleos exploratorios**, **0 certificaciones de zonas homogéneas** y **0 alertas agronómicas nuevas**.

## 5. Indicadores y estado de protección científica

Los resultados se consignan en:

- [Fuentes mensuales CHIRPS verificadas y SHA](datos/homogeneidad_9o/fuentes_chirps_9o.json).
- [Serie CHIRPS mensual por 42 sectores](datos/homogeneidad_9o/serie_sectores_chirps_9o.csv).
- [Serie CHIRPS mensual por 81 testigos](datos/homogeneidad_9o/serie_testigos_chirps_9o.csv).
- [Normales mensuales CHIRPS por sector y número de años](datos/homogeneidad_9o/normales_sectoriales_chirps_9o.csv).
- [Normales mensuales ERA5/ERA5-Land por testigo (30 años)](datos/homogeneidad_9o/normales_testigos_multivariable_9o.csv).
- [Diagnóstico reproducible de similitud y limitaciones](datos/homogeneidad_9o/diagnostico_homogeneidad_9o.json).
- [Motor original CHIRPS](modelos/chirps_homogeneidad_9o.py), [diagnóstico multivariable](modelos/diagnostico_homogeneidad_9o.py), [pruebas](tests/test_homogeneidad_9o.py) y [workflow CI](.github/workflows/oaf_homogeneidad_9o.yml).
- [Visor 9O de climatología](modelos/visor_homogeneidad_9o.js) y sus estilos, integrados en *Análisis de clima regional*.

La información debe publicarse como **conocimientos territoriales exploratorios**. El conjunto CHIRPS incorpora pluviómetros y no se ha demostrado independencia de los testigos o estaciones originales, por lo que no se debe convertir una alta correlación entre pixeles/sectores en un certificado de homogeneidad.

Se mantienen explícitamente **0 zonas instrumentales homogéneas certificadas**, **0 modelos de pronóstico por sector con skill ex-ante probado**, y **0 alertas fitosanitarias** emitidas por este análisis. El riesgo de arándano y vid requiere variables meteorológicas locales y observaciones reales de enfermedades y fenología.

## 6. Siguiente etapa científica — 9P

Ampliar gradual y cuidadosamente el periodo CHIRPS v3 hasta reunir los **360 meses de 1996–2025**, archivando metadatos por fuente, versiones y SHA. Tras alcanzar 30 años comparables, estimar medias, variabilidad interanual, extremos y anomalías por subcuenca/piso, y validar los agrupamientos con estaciones SENAMHI localizadas y fechadas. Poner a prueba los grupos seleccionados frente a *fuentes independientes, años no utilizados para definirlos* y cambios de malla; solo entonces comenzar la transferencia cuantitativa de pronósticos NMME, distinguiendo vintage ex-ante, resultado retrospectivo y evidencia de campo.
