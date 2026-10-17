# Fase 9H — Contraste retrospectivo de las estaciones con CHIRPS v3, ERA5 y ERA5-Land

**Ejecución:** 17 de octubre de 2026. **Estado científico:** contraste con archivos externos reales para **lluvia CHIRPS v3 de 1998** y **lluvia ERA5 atmosférico 1996–2013**. La descarga de **temperatura ERA5-Land** quedó pendiente por tiempo de espera del servidor; no se calcularon métricas para ella. Las seis coordenadas documentales son candidatas, no posiciones históricas certificadas del pluviómetro.

## 1. Antecedentes y entradas originales

Las tres series observadas provienen de `datos/estaciones_9d/originales/`, con SHA-256 intactas y nombres corroborados documentalmente en [fase 9F](FASE_9F_IDENTIDAD_TERRITORIAL.md). La fase [9G](FASE_9G_SENSIBILIDAD_GEOGRAFICA.md) archivó **dos ubicaciones alternativas por estación**, que aquí se mantienen como **dos hipótesis espaciales** y no como réplicas independientes. Se emparejan únicamente meses con el 100 % de sus días observados. Nunca se imputan meses faltantes.

La comparación depende de la convención pluviométrica de la estación, no documentada aún: horas de cierre y fecha efectiva del acumulado. La coincidencia del mes civil no demuestra equivalencia instrumental diaria. La calidad integral del archivo y la licencia siguen por acreditar.

## 2. Proveniencia y extracción verificable

### CHIRPS v3 mensual LATAM, episodio 1998

Se descargaron **12 GeoTIFF reales** (enero–diciembre de 1998) desde el directorio UCSB `https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/`. Cada ráster se comprobó como EPSG:4326, una banda y píxel físicamente próximo a la consulta; se registraron URL y SHA-256. La distinción de archivo final/preliminar **no se certificó por ráster**. Son **72 pares** estación–píxel: 3 estaciones × 2 ubicaciones × 12 meses. Científicamente equivalen a **36 meses estación distintos** porque los dos escenarios comparten el mismo registro instrumental. CHIRPS puede incorporar datos de estaciones dentro de su producción: **no se puede afirmar independencia**.

| Estación | Precipitación estación 1998 | CHIRPS 1998: coordenada 1 | CHIRPS 1998: coordenada 2 | MAE mensual escenario 1 | MAE mensual escenario 2 |
|---|---:|---:|---:|---:|---:|
| El Espinal | 1 847,10 mm | 1 053,53 mm | 1 053,53 mm | 70,27 mm | 70,27 mm |
| Puchaca | 2 258,00 mm | 1 572,53 mm | 1 698,93 mm | 84,80 mm | 85,16 mm |
| Virrey | 3 367,40 mm | 1 396,17 mm | 1 396,17 mm | 169,30 mm | 169,30 mm |

**Interpretación:** CHIRPS subestima en este episodio de lluvias extraordinarias los totales observados en los tres archivos. No significa que subestime necesariamente todos los años ni que estas diferencias representen habilidad predictiva. En Virrey, la diferencia es grande; amerita investigar resolución, topografía, convención pluviométrica, QC y posibles cambios de estación antes de atribuir causa.

**Sensibilidad espacial CHIRPS:** Virrey y El Espinal devuelven **el mismo píxel** desde ambas coordenadas alternativas. Puchaca devuelve dos píxeles distintos, separados **5,56 km**; la diferencia entre MAE es **+0,359 mm/mes**, pero el sesgo mensual cambia **+10,534 mm** (escenario 2 menos 1). No seleccionar retrospectivamente el píxel cuyo error resulte menor.

### ERA5 atmosférico, 1996–2013

El servicio [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) devolvió datos reales diarios de precipitación con selección explícita `models=era5`, `daily=precipitation_sum`, `timezone=America/Lima` y `cell_selection=land`. Sus valores diarios fueron agrupados sin interpolación en meses de calendario completo. Se registraron **dos respuestas originales con URL y SHA-256** correspondientes a 1996–2005 y 2006–2013.

**ERA5 atmosférico es una grilla aproximada de 0,25°**, distinta de ERA5-Land (0,1°) y distinta de los pluviómetros. Los centros son los que retornó Open-Meteo; no se dedujeron de las coordenadas solicitadas.

| Estación | Meses instrumentales completos 1996–2013 | MAE mensual ERA5 · ubicación 1 | MAE mensual ERA5 · ubicación 2 | MAE ERA5 1998 · ubicación 1 |
|---|---:|---:|---:|---:|
| El Espinal | 215 | 73,54 mm | 73,54 mm | 94,85 mm |
| Puchaca | 207 | 93,06 mm | 155,15 mm | 368,09 mm |
| Virrey | 216 | 22,77 mm | 22,77 mm | 81,47 mm |

Son **1 276 pares estación–celda** (duplicación de 638 meses observados entre los dos escenarios). Los valores de MAE de la tabla principal corresponden a **todo 1996–2013**, mientras que la última columna se limita a 1998. **No es apropiado comparar directamente un MAE de CHIRPS 1998 contra un MAE de ERA5 1996–2013 sin igualar periodos.**

### Comparación en meses idénticos: El Niño 1998

Para evitar comparar errores de horizontes diferentes, se armonizaron los **12 meses de enero a diciembre de 1998**, utilizando únicamente el **escenario documental 1** en las tres estaciones. Los datos son retrospectivos y están archivados en los dos CSV de la fase; no se ha seleccionado retrospectivamente la coordenada más favorable.

| Estación | Meses observados comunes | MAE CHIRPS v3 1998 | MAE ERA5 atmosférico 1998 |
|---|---:|---:|---:|
| El Espinal | 12 | 70,27 mm/mes | 94,85 mm/mes |
| Puchaca | 12 | 84,80 mm/mes | 368,09 mm/mes |
| Virrey | 12 | 169,30 mm/mes | 81,47 mm/mes |

**Lectura científica:** CHIRPS tiene menor MAE en El Espinal y Puchaca en este episodio, mientras que ERA5 atmosférico lo tiene en Virrey. **No es un ranking general**: las celdas tienen distinta resolución, los lugares exactos de los pluviómetros históricos no están certificados y CHIRPS puede incorporar observaciones pluviométricas en su elaboración, por lo que la comparación no es necesariamente independiente. Según el [Climate Hazards Center, CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3), el producto incorpora observaciones de estaciones y procedimientos de corrección de subcaptación del pluviómetro; debe verificarse si las series locales presentan correcciones equivalentes antes de emitir conclusiones de calidad instrumental.

**Sensibilidad espacial ERA5:** El Espinal y Virrey retornan el mismo centro de celda para ambas coordenadas. Puchaca cambia entre las celdas aproximadas `(-6.5, -79.5)` y `(-6.25, -79.5)`: un cambio notable debido a la malla gruesa, que incrementa el MAE mensual histórico de **93,056 a 155,147 mm**. Esta divergencia no justifica elegir a posteriori la ubicación 1, ni demuestra cuál describe la estación histórica.

### ERA5-Land, temperatura y lluvia

La primera extracción intentó precipitación de `models=era5_land` vía Open-Meteo. El endpoint devolvió **centros de celda, pero ninguna pareja válida de precipitación** (0 meses), coherente con la restricción documentada en la tabla de variables de [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api): la precipitación de su API se expone desde ERA5 atmosférico, no como precipitación nativa de ERA5-Land. No se ha rotulado un dato de ERA5 como si fuese ERA5-Land. **Esto no significa que la variable total precipitation no exista en el conjunto ERA5-Land del CDS**: allí los acumulados usan una convención temporal especial y requieren descarga/procesamiento correctos conforme a [documentación ECMWF](https://forum.ecmwf.int/t/calculating-daily-precipitation-sum-from-era5-land-hourly-data/2929/2).

Para temperaturas ERA5-Land, se programó la extracción real de `temperature_2m_max` y `temperature_2m_min` con evaluación mensual frente a las medias de máximos y mínimos diarios originales: El Espinal tiene **204 meses de temperatura completa** (1996–2013), Puchaca **146** y Virrey **0**. La consulta ERA5-Land **sufrió timeout del proveedor**, inclusive al fragmentarla por subperiodos. El programa dejó las métricas de temperatura ausentes (no cero). Se requiere reintentar el acceso o utilizar CDS con credenciales y procesamiento reproducible, sin fabricar valores.

## 3. Cobertura y significado estadístico

| Producto | Variable | Periodo | Pares CSV publicados | Estado |
|---|---|---|---:|---|
| CHIRPS v3 mensual | Lluvia | 1998 | **72** (36 meses estación únicos) | Extraído, MAE/RMSE/sesgo descriptivos |
| ERA5 atmosférico | Lluvia | 1996–2013 | **1 276** (638 meses estación únicos) | Extraído, MAE/RMSE/sesgo descriptivos |
| ERA5-Land por Open-Meteo | Lluvia | 1996–2013 | **0** | Variable no proporcionada en esa modalidad |
| ERA5-Land por Open-Meteo | Temperaturas Tmax/Tmin | 1996–2013 | **0** | API con timeout; **pendiente** |

**Advertencias irreductibles:** comparaciones retrospectivas de reanálisis ≠ pronósticos archivados (vintage); presencia de estaciones en CHIRPS potencialmente circular; diferencias de longitud/latitud, gradientes de montaña y posible cambio de emplazamiento; hora y QC instrumental no certificados; cobertura 1996–2013 insuficiente para validar la normal principal 1996–2025; no realizar generalizaciones fitosanitarias ni alertas El Niño a partir de estos errores.

## 4. Archivos, código y control de calidad

- [Extracción 1998 CHIRPS y primer intento ERA5-Land](modelos/contraste_instrumental_9h.py)
- [Datos CHIRPS con huellas originales y resultados](datos/validacion_estaciones_9h/comparacion_observacional_9h.json)
- [Pares mensuales CHIRPS CSV](datos/validacion_estaciones_9h/pares_mensuales_9h.csv)
- [Extractor independiente de ERA5 atmosférico y temperatura ERA5-Land](modelos/contraste_temperatura_era5_9h.py)
- [Resultados ERA5 y estado de temperatura](datos/validacion_estaciones_9h/contraste_era5_complementario_9h.json)
- [Pares mensuales de ERA5 y temperatura](datos/validacion_estaciones_9h/pares_era5_complementarios_9h.csv)
- [Integración del panel web](modelos/visor_contraste_estaciones_9h.js)
- [Acciones reproducibles](.github/workflows/oaf_contraste_instrumental_9h.yml) y [comparación complementaria](.github/workflows/oaf_era5_temperatura_9h.yml)

Todos los cálculos conservan `n_meses`, periodo, sesgo (producto menos estación), MAE y RMSE, sin rellenar vacíos. Los originales no se han alterado.

## 5. Próxima fase propuesta: 9I

Ampliar la muestra CHIRPS con años adicionales preespecificados, sin elegir retrospectivamente los intervalos con mejores errores; preparar alternativa reproducible a ERA5-Land por descarga CDS u otra fuente auténtica con mapeo correcto de acumulados. Comprobar los cambios históricos de estaciones y su régimen horario, contrastar independencia CHIRPS y documentar análisis espacial de los píxeles próximos. Una validación predictiva de anomalías requerirá después pronósticos archivados con sus fechas originales de emisión.
