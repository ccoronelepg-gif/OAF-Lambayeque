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

## 4. SST: dos escalas complementarias

**SST regional ya disponible:** 360 anomalías mensuales 1996–2025 del índice **Niño 1+2 NOAA CPC**, con archivo y SHA congelados en [fase 8T](datos/oceano_8t/noaa_cpc_sstoi_indices.meta.json). Es un índice revisado hasta 2026, no la versión necesariamente conocida al emitir un pronóstico en cada año histórico y **no equivale al ICEN de ENFEN**.

**SST local frente a Lambayeque — fuente identificada, extracción y QA pendientes:** [NOAA NCEI OISST versión 2.1](https://upwell.pfeg.noaa.gov/erddap/griddap/ncdcOisst21Agg_LonPM180.html), malla 0,25° con valores diarios desde 1981. Las posibles ubicaciones marinas deberán seleccionarse en celdas realmente oceánicas y a diferentes distancias de la costa, y comprobar máscara tierra/mar. No se permite atribuir a una playa una celda de SST que en realidad sea terrestre, ni tratar el índice Niño 1+2 como temperatura costera medida.

## 5. Corrientes marinas: revisión de fuentes y control anti-datos-ficticios

Se identificaron dos fuentes legítimas con componentes físicas **u/v**:

- **NASA/JPL PO.DAAC OSCAR v2.0 final, 0,25°**, colección `OSCAR_L4_OC_FINAL_V2.0`, [ficha oficial NASA](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0). Producto con velocidades superficiales zonal y meridional en m/s, derivadas de altimetría, viento y gradientes térmicos. Puede requerir acceso **Earthdata Login** y descarga netCDF/subconjunto validado.
- **Copernicus Marine GLORYS12V1**, producto `GLOBAL_MULTIYEAR_PHY_001_030`, [ficha oficial Copernicus](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description). Reanálisis oceánico con velocidades hacia este y hacia norte, varios niveles de profundidad y malla de ~1/12°. La comparación de superficie deberá fijar **nivel, celda oceánica, huso UTC, calidad y máscara costera**.

**Advertencia de detección importante:** el [antiguo servidor NOAA ERDDAP `jplOscar`](https://coastwatch.pfeg.noaa.gov/erddap/info/jplOscar/index.html) tiene una descripción que indica 1992–presente, pero su atributo de cobertura temporal disponible documenta **2011-12-06 a 2014-09-26**, insuficiente para 1996–2025. **No se utilizará esa subserie ni se imputará para crear un registro de 30 años.**

Al corte 8U actual, **no hay una serie de u/v marinos 1996–2025 archivada, validada y asociada a puntos oceánicos de Lambayeque**. La variable figura como pendiente, no como evidencia medida. Su incorporación requerirá URL/granulos netCDF originales, huellas verificables, unidades m/s, archivos de máscaras y concordancia temporal, con series completas por celda o una cobertura histórica explícitamente parcial.

## 6. Qué se podrá evaluar cuando haya datos suficientes

**Primero:** la asociación de viento sobre mar, SST costera, corrientes superficiales y lluvia/temperatura/HR agrícola por temporada, sin confundir retrasos y simultaneidad. **Después:** nuevos backtests con entrenamiento previo, validación y prueba temporal independiente, selección fija de predictores y control geográfico por cuencas y pisos altitudinales. Las fases 8R–8T mostraron la importancia de contar una vez cada celda y de comparar siempre persistencia y climatología.

Especial atención: **el efecto de SST y viento sobre temperatura media no tiene por qué equivaler al efecto sobre lluvias extremas**, que son un objetivo específico de interés para El Niño Costero. Además, mareas, corrientes superficiales, circulación subsuperficial, ondas Kelvin y transporte costero son mecanismos distintos; no reemplazar corrientes marinas por velocidad del viento.

## 7. Estado científico

- Viento ERA5 1996–2025: adquisición incremental verificable.
- SST histórica regional Niño 1+2: **disponible, versión histórica revisable**.
- SST local OISST y corriente oceánica u/v 1996–2025: **acceso/ingesta y verificación todavía pendientes**.
- Reanálisis no sustituye estación SENAMHI ni monitoreo oceánico local; estaciones instrumentales independientes utilizadas = **0**.
- Predicción integrada multivariable validada de Niño Costero = **no demostrada**.
- Polígonos agroclimáticos homogéneos certificados = **0**.
- Alertas de enfermedad de arándano o vid validadas con evaluaciones de campo = **0**.

Este reporte registra tanto la evidencia disponible como los componentes todavía no obtenidos: **no atribuye al OAF habilidades predictivas u oceanográficas inexistentes**.
