# Fase 8U — Viento, temperatura superficial del mar y corrientes marinas para el OAF-Lambayeque

**Investigación regional implementada en octubre de 2026 · referencia OAF: 1996–2025.**

## 1. Propósito y hallazgo de la fase anterior

En 8T, agregar el índice oceánico Niño 1+2 de NOAA con retraso de dos meses a la regresión térmica regional no mejoró de manera consistente el error predictivo en la misma fuente de reanálisis ERA5-Land. La diferencia fue **−0,0431 %** en el control cronológico y **+0,0098 %** en el control espacial. Este resultado no demuestra ausencia de influencia oceánica; obliga a investigar una representación multivariable más pertinente de la circulación costera.

La fase 8U empieza a **incorporar fuentes independientes por variable**, primero viento atmosférico y SST regional ya archivada, además de una ruta reproducible para fuentes oceánicas vectoriales. **No se mezclan reanálisis, SST y corrientes como si fueran la misma medición.**

## 2. Factores y mecanismos físicos que hay que diferenciar

| Factor | Variable y unidad | Utilidad posible | Cautela |
|---|---|---|---|
| Viento de superficie sobre tierra | Velocidad media a 10 m (m/s), dirección dominante (grados meteorológicos, *desde*) | Cambios en advección, evapotranspiración, humedad superficial, dispersión de esporas e influencia costera | Viento a 10 m modelado no es microclima del cultivo ni viento marítimo sobre la franja litoral |
| Viento sobre el mar | Componentes u/v a 10 m (m/s), tensión superficial | Transporte de Ekman, afloramiento costero y mezcla superficial | Una lectura terrestre no sustituye una cuadrícula marina de viento ni demuestra afloramiento |
| Temperatura superficial del mar (SST) | Temperatura °C y anomalías °C | Calentamiento del Pacífico oriental, humedad, posibles anomalías de lluvia y convección | Niño 1+2 representa una región oceánica grande, no temperatura exacta frente a Pimentel o Santa Rosa |
| Corriente superficial marina | Componentes **u** (este–oeste) y **v** (norte–sur), m/s; módulo y rumbo derivados de ambas | Transporte de agua, advección térmica, estructura superficial del océano | No puede reconstruirse solo con viento o SST; hay que obtener datos **u/v realmente observados/modelados** |
| Lluvia, radiación, humedad y Tmax | ERA5/ERA5-Land ya conservados en 8O/8P | Objetivos agroclimáticos potencialmente más sensibles a fenómenos costeros; riesgos agrícolas condicionados al cultivo | Requieren ensayos separados con validación por temporada y estaciones SENAMHI |

La circulación asociada al afloramiento puede conectar viento paralelo a costa, transporte superficial y SST, pero **no equivale automáticamente a El Niño Costero ni a probabilidad de enfermedad**. La respuesta varía según latitud, época, viento marino real, corrientes oceánicas, altitud, exposición y precipitación. Para arándano y vid serán imprescindibles registros de fenología, humedad foliar y evaluaciones sanitarias de campo.

## 3. Implementación efectiva: viento ERA5 para cuatro localidades

Se programaron y empezaron a ejecutar consultas diarias a la [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) con selección de modelo **ERA5**, huso `America/Lima`, selección de celda `land` y velocidad en **m/s**. Las cuatro coordenadas fijas son los centros históricos de Chiclayo, Jayanca, Motupe y Olmos previamente utilizados en 8M, no parcelas ni estaciones oficiales.

- **Variables:** `wind_speed_10m_mean`, `wind_speed_10m_max`, `wind_direction_10m_dominant`.
- **Bloques:** 1996–2005, 2006–2015 y 2016–2025. Se descargan progresivamente por GitHub Actions, como máximo una década por ejecución, respetando HTTP 429.
- **Verificación:** calendario diario exacto, números finitos, rangos físicos, unidades de m/s y grados, coordenadas de celda, URL completa y SHA-256 del archivo original. No se imputan días ni décadas faltantes.
- **Agregación:** velocidad media diaria por mes y media mensual del máximo diario. A partir de dirección dominante diaria y velocidad media diaria se aproxima un vector meteorológico: `u = −velocidad × sen(dirección)`, `v = −velocidad × cos(dirección)`. Son **componentes orientativas**, no integrales de vectores horarios exactos; su error proviene de resumir la dirección y velocidad del día por separado.
- **Publicación regional:** una localidad obtiene indicador completo 1996–2025 solo si existen sus 360 meses, procedentes de las tres décadas originales auditadas.

Archivo del motor: [`modelos/viento_oceano_8u.py`](modelos/viento_oceano_8u.py). Pruebas: [`tests/test_viento_oceano_8u.py`](tests/test_viento_oceano_8u.py). Automatización: [`.github/workflows/oaf_viento_oceano_8u.yml`](.github/workflows/oaf_viento_oceano_8u.yml).

Datos: [`datos/viento_8u/estado_factores_8u.json`](datos/viento_8u/estado_factores_8u.json), [`viento_mensual_8u.csv`](datos/viento_8u/viento_mensual_8u.csv) y los JSON originales gz con metadatos SHA en `datos/viento_8u/fuentes/`.

### Resultados reales del viento 1996–2025: descarga completada

Los tres bloques diarios 1996–2005, 2006–2015 y 2016–2025 están **completos**, con JSON originales, metadatos URL y SHA-256 auditados. Se obtuvieron **1.440 meses-localidad** (4 localidades × 360 meses) y **10.958 días por localidad**.

| Localidad | Viento medio diario agregado a 30 años (m/s) | Media de máximos diarios (m/s) | Centros de celda ERA5 por localidad |
|---|---:|---:|---:|
| Chiclayo | **3,138** | 4,985 | 1 |
| Jayanca | **2,410** | 4,003 | 1 |
| Motupe | **1,890** | 3,453 | 1 |
| Olmos | **1,393** | 2,989 | 1 |

El descenso entre las cuatro ubicaciones **no permite atribuir un gradiente causal exclusivo costa–interior**: influyen selección espacial de celdas, relieve, exposición del punto, rugosidad y reanálisis; no son estaciones SENAMHI.

### Asociación descriptiva viento–SST Niño1+2, 1996–2025

Se calcularon primero normales mensuales del propio punto basadas en **1996–2025** y se restaron de cada viento mensual. Estas normales se utilizan **solo para diagnóstico descriptivo**, no para entrenamiento de un pronóstico retrospectivo (donde introducirían información futura). Se compararon el viento de un mes y el índice SST NOAA Niño1+2 observado **en el mismo mes** o **dos meses antes**. La asociación de dos meses usa 358 meses por localidad.

| Localidad | Pearson r: anomalía de velocidad del viento vs SST t−2 | Pearson r: componente zonal aproximada del viento vs SST t−2 | Pearson r: componente meridional aproximada del viento vs SST t−2 |
|---|---:|---:|---:|
| Chiclayo | +0,17252 | −0,40218 | +0,11805 |
| Jayanca | +0,21774 | −0,30892 | +0,11890 |
| Motupe | +0,15706 | −0,26237 | +0,13544 |
| Olmos | +0,19407 | −0,16926 | +0,20262 |

Las correlaciones de velocidad son débiles; la componente zonal aproximada muestra una relación negativa más pronunciada en algunos puntos. La convención del viento atmosférico es hacia donde sopla para **u/v**, calculado desde la dirección meteorológica *de donde proviene*. **No confundir estos u/v de viento con u/v de corrientes oceánicas**.

No se aplicó una prueba de significación con autocorrelación temporal ni separación por década, no hay contraste con viento marítimo u observaciones instrumentales y, por ello, **ninguno de estos coeficientes demuestra mecanismo causal, pronóstico o eficiencia predictiva**.

Archivos reales: [diagnóstico por localidad](datos/relaciones_viento_sst_8u/estado_relaciones_8u.json), [1440 comparaciones mensuales](datos/relaciones_viento_sst_8u/comparaciones_mensuales_8u.csv) y [motor de cálculo](modelos/relaciones_viento_sst_8u.py).

## 4. SST: dos escalas complementarias

**SST regional ya disponible:** 360 anomalías mensuales 1996–2025 del índice **Niño 1+2 NOAA CPC**, con archivo y SHA congelados en [fase 8T](datos/oceano_8t/noaa_cpc_sstoi_indices.meta.json). Es un índice revisado hasta 2026, no la versión necesariamente conocida al emitir un pronóstico en cada año histórico y **no equivale al ICEN de ENFEN**.

**SST local frente a Lambayeque — fuente identificada, extracción y QA pendientes:** [NOAA NCEI OISST versión 2.1](https://upwell.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.html), malla 0,25° con valores diarios desde 1981. Las posibles ubicaciones marinas deberán seleccionarse en celdas realmente oceánicas y a diferentes distancias de la costa, y comprobar máscara tierra/mar. No se permite atribuir a una playa una celda de SST que en realidad sea terrestre, ni tratar el índice Niño 1+2 como temperatura costera medida.

## 4A. Cruce cuantitativo viento–Niño 1+2 (realizado con datos archivados)

Se contrastaron **358 meses emparejados** por cada una de las cuatro localidades, usando normales mensuales de viento de cada sitio calculadas sobre 1996–2025 y la anomalía Niño 1+2 de NOAA desplazada **dos meses**. La normal 1996–2025 aquí solo sirve para análisis **descriptivo**, **no** puede usarse como normal aprendida para una predicción retrospectiva que reserve años posteriores.

| Localidad | Correlación de velocidad media de viento con Niño 1+2 t−2 | Correlación de componente zonal aproximada con Niño 1+2 t−2 |
|---|---:|---:|
| Chiclayo | +0,172522 | **−0,604520** |
| Jayanca | +0,217735 | −0,396361 |
| Motupe | +0,157064 | −0,385576 |
| Olmos | +0,194071 | −0,311165 |

Los índices son descriptivos de series históricas reanalizadas/revisadas: no son causalidad, no controlan automáticamente tendencias, dependencia temporal, ENSO de otras regiones, perturbaciones costeras ni exposición de laderas, y no demuestran capacidad de anticipar lluvias o vientos de campo. La componente zonal estimada usa dirección dominante diaria y velocidad media diaria, por lo cual tampoco equivale a una observación vectorial instantánea. Los coeficientes y su SHA quedan en [correlaciones_viento_sst_8u.json](datos/viento_8u/correlaciones_viento_sst_8u.json).

## 5. Corrientes marinas: revisión de fuentes y control anti-datos-ficticios

Se identificaron dos fuentes legítimas con componentes físicas **u/v**:

- **NASA/JPL PO.DAAC OSCAR v2.0 final, 0,25°**, colección `OSCAR_L4_OC_FINAL_V2.0`, [ficha oficial NASA](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0). Producto con velocidades superficiales zonal y meridional en m/s, derivadas de altimetría, viento y gradientes térmicos. Puede requerir acceso **Earthdata Login** y descarga netCDF/subconjunto validado.
- **Copernicus Marine GLORYS12V1**, producto `GLOBAL_MULTIYEAR_PHY_001_030`, [ficha oficial Copernicus](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description). Reanálisis oceánico con velocidades hacia este y hacia norte, varios niveles de profundidad y malla de ~1/12°. La comparación de superficie deberá fijar **nivel, celda oceánica, huso UTC, calidad y máscara costera**.

**Advertencia de detección importante:** el [antiguo servidor NOAA ERDDAP `jplOscar`](https://coastwatch.pfeg.noaa.gov/erddap/info/jplOscar/index.html) tiene una descripción que indica 1992–presente, pero su atributo de cobertura temporal disponible documenta **2011-12-06 a 2014-09-26**, insuficiente para 1996–2025. **No se utilizará esa subserie ni se imputará para crear un registro de 30 años.**

Al corte 8U actual, **no hay una serie de u/v marinos 1996–2025 archivada, validada y asociada a puntos oceánicos de Lambayeque**. La variable figura como pendiente, no como evidencia medida. Su incorporación requerirá URL/granulos netCDF originales, huellas verificables, unidades m/s, archivos de máscaras y concordancia temporal, con series completas por celda o una cobertura histórica explícitamente parcial.

## 5A. Primera instantánea de corrientes y SST en mar abierto: 16–18 octubre de 2026

Se completó una adquisición adicional **real de archivo de pronóstico modelado**, sin atribuirle 30 años de climatología ni observaciones de boyas. Fuente: Open-Meteo Marine Forecast, productos marinos de Météo-France, datos horarios de SST y velocidad/dirección de corriente, tres ubicaciones sobre el Pacífico frente a Lambayeque (longitud solicitada −80,7°; latitudes −6,1°, −6,5° y −6,9°). Se usó preferencia `cell_selection=sea` y se archivó la respuesta original.

**Fecha de adquisición:** 17/10/2026 03:51:48 UTC. **Archivo SHA-256:** `1459507b8405ea5d9dab9a2b1e42622e38a0a81a1dfc13bdb9bd0729559c693e`. La serie devuelta cubre **72 horas desde el 16/10/2026 hasta el 18/10/2026, hora de Perú**; parte del periodo es anterior a la descarga, por lo que tampoco representa una secuencia enteramente de pronósticos futuros emitidos antes de empezar.

| Punto piloto sobre mar (latitud solicitada) | SST media modelada (°C) | Velocidad media de corriente (m/s) | u media: este positivo (m/s) | v media: norte positivo (m/s) |
|---|---:|---:|---:|---:|
| Norte, −6,1° | **26,0569** | 0,1701 | −0,0998 | +0,1316 |
| Centro, −6,5° | **25,5903** | 0,1636 | −0,1033 | +0,1193 |
| Sur, −6,9° | **24,9319** | 0,1782 | −0,1346 | +0,0624 |

Los vectores medios modelados poseen **componente oeste y norte** en los tres puntos. La dirección de corriente indica *hacia dónde* fluye el agua (0° = norte), mientras la dirección del viento meteorológico indica *desde dónde* sopla. **El proveedor devolvió la velocidad marina en km/h**; antes de obtener estas cifras en m/s se aplicó explícitamente la conversión km/h ÷ 3,6, con pruebas automatizadas de unidad. Se conservaron las coordenadas **de celda efectivamente devueltas**, diferentes de las coordenadas solicitadas.

La diferencia de SST media modelada de esta instantánea entre norte y sur es **1,125 °C**; no es una anomalía frente a una climatología local ni una estimación de calentamiento por El Niño. Tampoco es una observación de velocidad de la **Corriente de Humboldt** ni permite afirmar circulación costera completa: se trata de tres puntos marinos y un producto modelado cuya precisión costera es limitada.

Fuentes: [Open-Meteo Marine](https://open-meteo.com/en/docs/marine-weather-api); [estado y celdas del muestreo 8U](datos/marino_8u/estado_marino_8u.json); [archivo de fuente y SHA](datos/marino_8u/fuentes/ocean_forecast_2026-10-17.meta.json). El programa [instantanea_marina_8u.py](modelos/instantanea_marina_8u.py) archiva una instantánea diaria bajo auditoría de columnas y unidades, sin reutilizarla como serie 1996–2025.

**El número de series de corrientes oceánicas completas e independientes durante 1996–2025 sigue siendo cero.** Hace falta investigar NASA OSCAR v2 o el reanálisis de Copernicus Marine con componentes u/v a resolución adecuada para la costa peruana, y distinguir corrientes oceánicas superficiales, afloramiento e influencia de vientos de tierra.

## 5B. Validación de sensibilidad al tamaño de muestra: 81 testigos de 8P

Durante la fase 8U, la automatización de 8P completó **24/24 bloques históricos** y los **81 testigos programados**. Esta adquisición no modifica las cuatro series de viento a 10 m ni los tres puntos marinos de 72 horas, pero sí amplía el experimento de predicción térmica de fases 8S/8T.

Los ensayos se recalcularon de forma automática tras los cambios en 8P con sus mismos procedimientos de selección y fechas sin fuga temporal:

- 81 testigos climáticos completos en el repositorio; después del filtrado precautorio DEM ≤5 m, **79 testigos**, equivalentes a **55 centros ERA5-Land diferentes**.
- **9.240 predicciones retrospectivas espacio–mes** en la comparación de 5 cortes cronológicos y 4 bandas espaciales, sin duplicar celdas.
- RMSE de persistencia: **0,459102 °C**.
- RMSE de 8S sin Niño 1+2, control por bandas retenidas: **0,439071 °C**.
- RMSE 8T, método preseleccionado por validación que incorpora Niño 1+2 solo cuando valida favorablemente: **0,438524 °C**.
- **Mejora incremental del RMSE de 8T frente a 8S ≈0,1246 %**. La variante oceánica fue elegida en **3/5 periodos temporales y 9/20 pliegues espaciales**: no hay beneficio grande ni prueba prospectiva de pronóstico de El Niño Costero.

Las diferencias frente al corte anterior (65 testigos, 50 centros) **dependen también del cambio de cobertura**; no deben atribuirse a una mejora del algoritmo sin comparar ambas muestras de forma controlada.

Fuentes reproducibles: [inventario 8P](datos/clima_contiguo_8p/estado_clima_8p.json), [reporte 8S](datos/validacion_regional_8s/estado_validacion_8s.json) y [reporte 8T](datos/validacion_oceanica_8t/estado_oceanico_8t.json). Los modelos son retrospectivos frente a ERA5-Land, no termómetros SENAMHI.

## 6. Qué se podrá evaluar cuando haya datos suficientes

**Primero:** la asociación de viento sobre mar, SST costera, corrientes superficiales y lluvia/temperatura/HR agrícola por temporada, sin confundir retrasos y simultaneidad. **Después:** nuevos backtests con entrenamiento previo, validación y prueba temporal independiente, selección fija de predictores y control geográfico por cuencas y pisos altitudinales. Las fases 8R–8T mostraron la importancia de contar una vez cada celda y de comparar siempre persistencia y climatología.

Especial atención: **el efecto de SST y viento sobre temperatura media no tiene por qué equivaler al efecto sobre lluvias extremas**, que son un objetivo específico de interés para El Niño Costero. Además, mareas, corrientes superficiales, circulación subsuperficial, ondas Kelvin y transporte costero son mecanismos distintos; no reemplazar corrientes marinas por velocidad del viento.

## 7. Estado científico

- Viento ERA5 1996–2025: **completado, 3 bloques archivados y 1.440 meses-localidad auditados**.
- SST histórica regional Niño 1+2: **disponible, versión histórica revisable**.
- SST local OISST y corriente oceánica u/v 1996–2025: **acceso/ingesta y verificación todavía pendientes**.
- Reanálisis no sustituye estación SENAMHI ni monitoreo oceánico local; estaciones instrumentales independientes utilizadas = **0**.
- Predicción integrada multivariable validada de Niño Costero = **no demostrada**.
- Polígonos agroclimáticos homogéneos certificados = **0**.
- Alertas de enfermedad de arándano o vid validadas con evaluaciones de campo = **0**.

Este reporte registra tanto la evidencia disponible como los componentes todavía no obtenidos: **no atribuye al OAF habilidades predictivas u oceanográficas inexistentes**.
