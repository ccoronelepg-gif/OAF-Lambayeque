# Fase 9D: integración de tres series meteorológicas históricas de Lambayeque

**Fecha de procesamiento:** 17 de octubre de 2026. **Estado:** datos originales íntegros incorporados a GitHub, auditoría y CSV mensual reproducibles. **No** se ha confirmado la identidad geográfica de las estaciones ni realizado una nueva validación de la habilidad predictiva 9A–9C.

## 1. Inventario de evidencia original

Los originales aportados por el usuario no contienen cabecera ni metadatos institucionales. El orden de seis campos se interpreta provisionalmente como año, mes, día, precipitación, temperatura máxima y mínima. Las unidades mm y grados Celsius también se asumen pendientes de ficha original. El valor -99.9 es dato faltante, nunca lluvia cero.

| Código de archivo | Fechas | Filas | Lluvia válida | Tmax válida | Tmin válida |
|---|---|---:|---:|---:|---:|
| 00000340 | 15/11/1964 a 31/07/2014 | 18 156 | 16 028 | 15 573 | 16 129 |
| 00153114 | 01/03/1963 a 31/07/2014 | 18 781 | 18 374 | 5 407 | 5 416 |
| 00152107 | 01/01/1964 a 31/12/2013 | 18 263 | 17 834 | 0 | 0 |
| **Totales** | | **55 200** | | | |

No hay fechas repetidas, omisiones en la secuencia de fechas ni inversiones entre temperaturas máxima y mínima. Sí existen ausencias de medición: las fechas completas no implican datos medidos completos.

## 2. Resultados retrospectivos de lluvia

Acumulados de lluvia anual expresados en mm, *solo* cuando los doce meses contienen cada uno por lo menos 90 % de días válidos. Este umbral es un criterio interno del OAF, no una norma adjudicada a la OMM.

| Código | 1983 | 1997 | 1998 | 2012 |
|---|---:|---:|---:|---:|
| 00000340 | Sin datos | 378,10 | 1 847,10 | 489,40 |
| 00153114 | 1 836,00 | 204,10 | 2 258,00 | Incompleto |
| 00152107 | 3 046,55 | 260,70 | 3 367,40 | 968,96 |

La serie 00000340 **no tiene lluvia válida en 1983**. No representar los meses ausentes como sequía ni interpretar un cero como ausencia. Se identificaron valores de lluvia mayores o iguales a 150 mm/día para revisión. El máximo observado es **330 mm el 10/02/2012 en el código 00152107**. El dato se conservó y se señalizó: aún no está verificado externamente.

## 3. Tramo 1996–2013 y limitaciones de normal climática

| Código | Meses posibles | Lluvia útil | Tmax útil | Tmin útil |
|---|---:|---:|---:|---:|
| 00000340 | 216 | 215 | 214 | 214 |
| 00153114 | 216 | 213 | 171 | 171 |
| 00152107 | 216 | 216 | 0 | 0 |

Regla de mes útil: al menos 90 % de días del mes natural con valor registrado para la variable específica. No imputación, no extrapolación ni escalado automático de totales con faltantes. Se generaron **1 814 filas mensuales**, con cobertura individual de precipitación, Tmax y Tmin.

Las tres series terminan en 2013 o 2014 y **no permiten construir la normal completa 1996–2025**. Tampoco completan 1991–2020. Los resúmenes 1996–2013 son **descriptivos de 18 años**, no normales de 30 años. En la superposición con el benchmark 9A/9C de 2011–2025, las estaciones pueden aportar observaciones como máximo entre 2011–2013 y parte de 2014, con cobertura por variable y sin coordenadas verificadas.

## 4. Procedencia y cautela científica

La información fue suministrada por el usuario. Los archivos no ofrecen nombres, latitud, longitud, altitud, nombre del operador, estaciones instrumentales, métodos originales de QC o licencia. **No es posible certificar que estos códigos corresponden a estaciones concretas SENAMHI solamente por el nombre de archivo.** Por ello no se les dibuja un pin ni se les asigna piso altitudinal.

Referencias oficiales para comprobar la identidad:
- SENAMHI — datos hidrometeorológicos y estaciones: https://www.senamhi.gob.pe/?p=estaciones
- Gobierno del Perú — datos hidrometeorológicos: https://www.gob.pe/institucion/senamhi/pages/9313-conocer-los-datos-hidrometeorologicos-del-peru
- Capa de estaciones publicada en INGEMMET: https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_OTRAS_FUENTES/MapServer/1

La información histórica observada no constituye por sí sola un pronóstico. Sin coincidencia geográfica entre estación y celda ERA5, ventanas y convenciones horarias, **no se calculan MAE ni Brier contra 9A/9C**. No se emiten alertas meteorológicas, fitosanitarias o ENSO oficiales.

## 5. Archivos incorporados y proceso reproducible

- Originales: datos/estaciones_9d/originales/qc00000340.txt, qc00153114.txt y qc00152107.txt.
- Metadatos de integridad, faltantes y extremos: datos/estaciones_9d/auditoria_estaciones_9d.json.
- Series mensuales con cobertura y sin imputar: datos/estaciones_9d/series_mensuales_9d.csv.
- Motor Python estándar: modelos/estaciones_instrumentales_9d.py. Verifica SHA-256, orden diario, campos, valores ausentes, bandera de lluvia intensa, límites termométricos y reproducibilidad con la opción --check.
- GitHub Actions: .github/workflows/oaf_estaciones_instrumentales_9d.yml.
- Dashboard: pestaña **Análisis de clima regional → Fase 9D**. El panel ofrece 3 códigos, 3 variables, rangos históricos, barras anuales y leyendas de faltantes y cobertura.

## 6. Ruta a fase 9E

Verificar nombres, coordenadas y altitudes oficiales y derechos de uso; emparejar observaciones con ERA5-Land/CHIRPS para la localización real; estimar sesgo y habilidad de extremos observados, validación espacial fuera de muestra y evaluar versiones de datos disponibles en fecha de emisión. No extrapolar automáticamente a los seis pisos altitudinales sin evidencia instrumental en cada subzona.

## 7. Auditoría temporal de disponibilidad real (vintage)

Se publicó [matriz de riesgos y disponibilidad temporal 9D](datos/estaciones_9d/auditoria_temporal_9d.json) contrastando documentación 8W/9A/9C y las tres series incorporadas. En los cortes 9A las variables RH/VPD pertenecen al mes de origen, y no al objetivo; eso limita fuga de objetivos futuros, **pero no demuestra disponibilidad al emitir**. Viento reanalizado, temperaturas y lluvia ERA5/ERA5-Land, índices históricos NOAA revisados y RH/VPD histórico no disponen en este repositorio de un archivo de *vintage* congelado según fecha de publicación. Los textos de estaciones tampoco contienen hora, fecha de difusión o metadatos institucionales. Esta limitación es distinta del control de error MAE/Brier y bloquea atribuir habilidad operativa al hindcast.

La próxima evaluación prospectiva debe conservar copia y huella SHA de predictores realmente disponibles a cada fecha de emisión, registrar latencia de publicación y evitar calcular atributos con valores conocidos solo después de la emisión. El archivo del observatorio no permite reconstruir retrospectivamente los vintages perdidos.
