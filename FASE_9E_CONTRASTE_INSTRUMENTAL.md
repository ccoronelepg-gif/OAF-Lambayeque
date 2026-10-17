# Fase 9E — Contraste observacional y validación geográfica de estaciones

**Fecha:** 17 de octubre de 2026. **Alcance real:** comparación temporal entre tres archivos instrumentales aportados por el usuario, control diario completo y construcción de un protocolo bloqueante para contrastar con ERA5-Land y CHIRPS v3. **No se ha logrado identificar las estaciones oficialmente**; no hay MAE o RMSE estación–rejilla y no hay una nueva predicción validada.

## 1. Origen y metadatos comprobados

Se revisaron los archivos originales, su auditoría SHA-256 y las fuentes institucionales de consulta:
- [Portal Nacional de Datos Abiertos, catálogo SENAMHI](https://www.datosabiertos.gob.pe/dataset/datos-hidrometeorol%C3%B3gicos-de-libre-acceso).
- [Capa de estaciones meteorológicas SENAMHI publicada en el servidor cartográfico INGEMMET](https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_OTRAS_FUENTES/MapServer/1).
- [Servicios WFS de IDESEP/SENAMHI](https://idesep.senamhi.gob.pe/portalidesep/idesep_componente_catalogo_geoservicios_wfs.jsp).

En estos recursos no se encontró o acreditó una **correspondencia exacta y documentada** de los códigos de fichero 00000340, 00153114 y 00152107 con los nombres, latitudes, longitudes y altitudes oficiales. Una coincidencia numérica incompleta no es válida: en las fichas de [metadatos pendientes](datos/validacion_estaciones_9e/metadatos_identidad_9e.json) permanecen valores **nulos**. Tampoco se ha acreditado el propietario de los datos ni la licencia de republicación. No se cartografían estos tres códigos.

## 2. Resultados empíricos sobre meses 100 % completos

El registro mensual derivado de la fase 9D conserva el umbral interno ≥90 % de días, pero para el contraste estricto de 9E **solo** se consideraron meses con exactamente 100 % de días válidos. No se rellenaron vacíos ni se modificaron los originales.

| Código | Meses 1996–2013 (esperados) | Meses con lluvia 90 % | Meses de lluvia con 100 % |
|---|---:|---:|---:|
| 00000340 | 216 | 215 | 215 |
| 00153114 | 216 | 213 | 207 |
| 00152107 | 216 | 216 | 216 |

**Acumulados de años destacados**, disponibles solo cuando los 12 meses tienen 100 % de días diarios válidos:

| Código | 1983 | 1997 | 1998 | 2012 |
|---|---:|---:|---:|---:|
| 00000340 | Ausente | 378,10 | 1 847,10 | 489,40 |
| 00153114 | 1 836,00 | 204,10 | 2 258,00 | Ausente |
| 00152107 | 3 046,55 | 260,70 | 3 367,40 | 968,96 |

El año 1998 cumple el criterio de días completos en los tres archivos. En 1983, los códigos 00153114 y 00152107 también cumplen 100 % y el código 00000340 tiene cero días de precipitación válidos: jamás equiparar faltantes con sequía.

### Correlación mensual descriptiva (1996–2013)

Calculamos correlación de Pearson entre log(1 + precipitación mensual en mm). Se utiliza logaritmo para reducir la dominancia de máximos, pero la correlación sigue siendo exploratoria: puede reflejar el ciclo estacional o eventos comunes, no cercanía geográfica ni homogeneidad climática.

| Dos códigos | Meses iguales con días completos | r de log(1+mm) | Enero–abril: r log(1+mm) |
|---|---:|---:|---:|
| 00000340 y 00153114 | 206 | 0,81128 | 0,79908 |
| 00000340 y 00152107 | 215 | 0,78934 | 0,81028 |
| 00153114 y 00152107 | 207 | 0,87053 | 0,85201 |

Se ejecutó una sensibilidad adicional con el mismo calendario mensual:
| Códigos | Correlación tras retirar media de cada mes calendario | Correlación excluyendo 1998 | Correlación excluyendo 1997 y 1998 |
|---|---:|---:|---:|
| 00000340 y 00153114 | 0,60552 | 0,79201 | 0,79917 |
| 00000340 y 00152107 | 0,56640 | 0,77297 | 0,77370 |
| 00153114 y 00152107 | 0,71677 | 0,85662 | 0,85833 |

Las asociaciones se mantienen al excluir el año 1998, pero decrecen al retirar el ciclo medio calendario, lo que confirma que **parte de la similitud es estacional**. Los promedios utilizados aquí son descriptivos y están calculados sobre la muestra completa; no son una evaluación de predicción fuera de muestra ni una normal OMM.

Las correlaciones **no son evidencia de habilidad de predicción**; comparten los mismos meses objetivo y no representan series de predicciones emitidas con antelación. Tampoco se han estimado intervalos de confianza de dependencia espacial; no utilizar r como prueba de regiones homogéneas.

**Resultado reproducible:** [datos/validacion_estaciones_9e/contraste_observacional_9e.json](datos/validacion_estaciones_9e/contraste_observacional_9e.json), obtenido ejecutando [modelos/contraste_observacional_9e.py](modelos/contraste_observacional_9e.py). [GitHub Actions](.github/workflows/oaf_contraste_observacional_9e.yml) ejecuta el motor y publica la matriz.

## 3. Contraste con ERA5-Land / CHIRPS: estado REAL y regla de activación

El resultado actual es **NO REALIZADO POR IMPEDIMENTO METADOCUMENTAL**. No se inventa un punto ni se empareja el código 00152107 con Olmos por parecer más lluvioso.

La comparación requiere:
1. Ficha inequívoca que vincule **código del archivo** con identificador de estación, nombre, emplazamiento vigente en cada periodo, latitud, longitud y altitud, con fuente institucional verificable.
2. Confirmar unidades de las tres columnas y hora/intervalo de día pluviométrico de cada instrumento; registrar modificaciones y traslados.
3. Extraer píxel/valor de ERA5-Land y CHIRPS v3 **en la localización realmente confirmada** y conservar producto, versión, centro de celda, resolución, huso/ventana de acumulación, fecha de disponibilidad y URL/hash de descarga.
4. Comparar exclusivamente meses con cobertura suficiente y escala temporal equivalente. Reportar n pareado, sesgo (grilla menos estación), MAE, RMSE, desviación y extremos, separando periodos de entrenamiento y verificación donde proceda.
5. Verificar independencia: **CHIRPS v3 incorpora observaciones de pluviómetros en sus estimaciones**; si la estación específica ha sido asimilada, el contraste no es una validación instrumental independiente. Para independencia robusta, usar estaciones retenidas fuera del producto o una configuración *leave-one-gauge-out* cuando sea posible.
6. Los datos ERA5-Land son reanálisis de variables terrestres y no instrumentos puntuales. No interpretar una diferencia de escala entre punto y celda como error puramente instrumental.

El comparador preparado en [modelos/emparejamiento_reanalisis_9e.py](modelos/emparejamiento_reanalisis_9e.py) falla de forma deliberada mientras las fichas sigan con estado no verificado. Admite solamente productos identificados y puntos próximos a estaciones acreditadas, exige versión, fecha de disponibilidad y métricas emparejadas. **No se ha ejecutado con datos observados y celdas certificadas**. El protocolo no confunde un *hindcast* con un pronóstico emitido.

Referencias metodológicas:
- [Copernicus/ECMWF: ERA5-Land, reanálisis de variables terrestres](https://www.ecmwf.int/en/forecasts/datasets/era5-land-hourly-data-1950-present).
- [Climate Hazards Center UCSB: CHIRPS v3, producto 0,05° y composición con estaciones](https://www.chc.ucsb.edu/data/chirps3). La diferencia entre producto preliminar y final también afecta la disponibilidad histórica.
- [CHIRPS v3: diagnósticos de estación, corrección de pluviómetros y cobertura](https://www.chc.ucsb.edu/data/chirps3/diagnostics).
- [OMM: normales climatológicas estándar de 30 años, incluida 1991–2020](https://wmo.int/wmo-climatological-normals). El periodo 1996–2013 mostrado aquí no se debe rotular como normal 1996–2025.

## 4. Web pública

En **Análisis de clima regional → Comparación histórica de lluvias entre estaciones** se añadieron un panel desplegable, selector por año, gráfico de barras de precipitación estricta y correlaciones entre pares. Cada indicador tiene una explicación y se distingue el valor faltante de cero. Los nombres de etapas numéricas permanecen solo como referencias de desarrollo en archivos, no como títulos visibles.

## 5. Dictamen y siguiente etapa

**Resultado alcanzado:** corroboración de tres series, 1998 y 1983, tres correlaciones por pares y construcción de barreras de calidad documental para impedir emparejamientos falsos. **Pendiente por evidencia:** verificación de las fichas de estación, comparación estación vs ERA5-Land/CHIRPS, confirmación de cambios de ubicación, periodos 2015–2025 e independencia instrumental. La investigación de anomalías El Niño y de sanidad de arándano y vid continúa como experimentación, no alerta operativa.

Para la siguiente etapa, se priorizará corroborar nombres/códigos con fichas técnicas, verificar ubicación y recuperar observaciones más recientes de estaciones adicionales para evaluar diferentes pisos altitudinales. Sin esas evidencias no se declarará validación geoespacial.
