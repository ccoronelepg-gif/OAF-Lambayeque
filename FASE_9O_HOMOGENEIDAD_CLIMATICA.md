# Fase 9O — Evaluación exploratoria de semejanza climática por sector y cuenca

**OAF-Lambayeque | Fecha de corte: 17/10/2026 | Estado:** metodología científica reproducible, primeras series CHIRPS verificadas, perfiles completos ERA5/ERA5-Land. Los resultados son retrospectivos y **no validan homogeneidad, aptitud de cultivo ni pronósticos**.

## 1. Objetivo

Contrastar las **42 superficies experimentales** de 9K–9N, divididas por pisos altitudinales y unidades hidrográficas de ANA/IDEP, con **precipitación satélite-pluviómetros CHIRPS v3** (0,05°; final mensual) y variables ERA5/ERA5-Land (temperatura, precipitación, humedad relativa y radiación de onda corta). Descartar la idea de que dos sectores parecidos geográficamente necesariamente tienen clima igual.

**Periodo de referencia principal: 1996–2025.** La referencia OMM 1991–2020 se mantiene para comparabilidad, no se intercambia con 1996–2025 ni con la climatología propia de NOAA NMME.

## 2. Distinción estricta de fuentes y observaciones

| Capa | Periodo | Variables | ¿Observación independiente? |
|---|---|---|---|
| CHIRPS v3 final LATAM | Piloto de cinco años completos preespecificados: **1996, 2002, 2011, 2018, 2025** | Lluvia mensual en celdas de 0,05° | **No se ha probado independencia**: incorpora pluviómetros. La grilla no representa 30 años completos de normales, aunque los años elegidos atraviesan el periodo. |
| ERA5-Land por Open-Meteo, fuentes congeladas 8O y 8P | **1996–2025 completos** | Temperatura media, máxima y mínima | Reanálisis, no estación de campo. |
| ERA5 por Open-Meteo, fuentes congeladas 8O y 8P | **1996–2025 completos** | Lluvia, humedad relativa y radiación | Reanálisis, con píxeles compartidos entre testigos. |
| Tres estaciones documentadas 9I | Meses efectivamente archivados en seis años **1996, 1998, 2002, 2007, 2011, 2013** | Lluvia instrumental retrospectiva | Ubicación histórica y posible dependencia con estaciones usadas por CHIRPS no están certificadas. |

CHIRPS: [Climate Hazards Center — CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) y [archivo mensual LATAM](https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/). CHIRPS v3 combina estimaciones satelitales con datos de estaciones. ERA5/ERA5-Land accedido en bloques archivados mediante Open-Meteo desde fases 8O y 8P.

**Por qué el piloto CHIRPS tiene cinco años:** el primer intento de descargar 360 GeoTIFF recibió una interrupción del proveedor tras 60 meses confirmados. La extracción ejecutable se limita prudentemente a cinco años distribuidos a lo largo del periodo solicitado para reducir carga; esta muestra **no autoriza** presentar una climatología CHIRPS 1996–2025 completa. Se mantienen rutas, fechas, SHA-256, errores reales y denominadores de años completos. El código admite ampliar a 360 meses cuando las 360 fuentes puedan recuperarse y auditarse.

## 3. Método de extracción geográfica

`modelos/chirps_homogeneidad_9o.py` toma los 42 polígonos SIG 9K, los 81 testigos y 60 meses preespecificados de CHIRPS v3 final LATAM. Para cada archivo:

1. Verifica que es GeoTIFF de una banda, EPSG:4326, resolución 0,05° y dominio de Lambayeque.
2. Lee solo el recorte regional y convierte celdas inválidas (incluyendo **-9999** del océano y ausencia de datos) en valores faltantes, **nunca en lluvia cero**.
3. Obtiene la media y dispersión espacial de **píxeles cuyos centros caen dentro** del polígono (no estaciones), con los píxeles inválidos excluidos. Si ningún centro de celda válido cae dentro, el sector queda con valor ausente.
4. Conserva el píxel CHIRPS de cada testigo, las coordenadas del centro y registra explícitamente cuándo dos testigos consultan el mismo píxel.
5. Registra URL y SHA-256 del GeoTIFF original por mes, además de meses no verificados. Por tamaño y gestión de repositorio no conserva dentro de GitHub los aproximadamente 1,5 GB que representarían los 360 TIFF originales. Para reproducir la extracción es necesario **volver a descargar el original y comparar SHA antes de usarlo**.

La media de los píxeles es una **media espacial no ponderada por áreas pequeñas**, pues los centros del rango estrecho de latitudes varían poco en superficie, pero no es una integral exacta de precipitación sobre un polígono agrícola. La desviación estándar es heterogeneidad **entre píxeles del producto**, no entre sensores independientes. Una celda compartida no da réplicas adicionales.

## 4. Climatología multivariable y comparación por unidades hidrográficas

`modelos/diagnostico_homogeneidad_9o.py` reconstruye exactamente los bloques crudos 8O (19 puntos) y 8P (62 puntos) para 81 testigos × 360 meses. Comprueba temperatura (ERA5-Land), lluvia/humedad/radiación (ERA5), fechas y perfiles completos. Produce **972 registros de normales mensuales ERA5/ERA5-Land** (81 × 12) y **504 registros de lluvia CHIRPS por sector y mes calendario** (42 × 12). Para CHIRPS, cada normal muestra el número real de años disponibles. Un valor basado en cinco años es *muestra histórica parcial*, no promedio de 30 años.

Se comparan dos tipos de parejas:
- **Tres familias preliminares C01–C03** de similitud climática 9K, con testigos a distintas altitudes dentro de su piso. El sistema cuantifica, cuando existen datos, correlación de anomalías desestacionalizadas de `log1p(lluvia)`, diferencias de lluvia y diferencias de temperatura de reanálisis. Píxeles repetidos de CHIRPS quedan marcados.
- **Pares de sectores con una intercuenca común**, candidatos en fase 9M, especialmente S002–S003 y S003–S004 (HM015 y HM011). La correlación de series CHIRPS y la diferencia de lluvia son descriptivas, **no una decisión de fusionar**. Cualquier pareja sin suficientes meses comunes se rotula insuficiente.

Los 81 perfiles de reanálisis cubren 1996–2025; la independencia espacial de sus celdas y la homogeneidad del área comprendida entre dos nodos **no están demostradas**. Para declarar una zona operativa haría falta estación instrumental independiente, comprobación física de cuenca y relieve, separación espacial de entrenamiento/prueba y evidencia de estabilidad histórica.

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
