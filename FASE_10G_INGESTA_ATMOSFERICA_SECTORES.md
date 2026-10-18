# Fase 10G — Incorporación de variables meteorológicas espacialmente trazables a 39 sectores

**Objetivo:** obtener temperatura, radiación solar, humedad relativa, VPD, viento, nubosidad y presión atmosférica para los **39 sectores exploratorios** de Lambayeque sin adjudicarles las cuatro series de Chiclayo/Jayanca/Motupe/Olmos como si fueran propias de todos los polígonos.

## 1. Fuente, resolución y evidencia

Se utiliza la [API histórica Open-Meteo para ERA5](https://open-meteo.com/en/docs/historical-weather-api), modelo explícito **`era5`** y resolución nominal **0,25° (~25 km)** con historia 1996–2025. La API es intermediaria de los campos ERA5 (fuente ECMWF/Copernicus), no una estación meteorológica. El modelo ERA5-Land, que ofrece ~0,1°, **no se ha usado** aquí; la selección de una sola versión ERA5 previene el cambio implícito de modelo cuando el proveedor ofrece una mezcla por defecto.

**Geometrías:** `datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson`, 42 polígonos exploratorios, 39 con series CHIRPS completas según auditoría 9W. Se extrae exactamente **un punto garantizado dentro de cada polígono** con `shapely.representative_point()`. No se presume que el punto sea el centroide, la ubicación de una finca ni el promedio meteorológico del polígono.

**Coordenadas conservadas:** localización consultada y **latitud/longitud retornadas por la API** (celda ERA5 realmente seleccionada), elevación del proveedor, sector de origen y agrupaciones de sectores que comparten celda ERA5. Si dos sectores comparten una celda, **no son dos muestras climáticas espacialmente independientes**.

**Cota DEM negativa:** el sector `S001` conserva la advertencia de altitud inferior a cero en el inventario 9K; la elevación del proveedor no la corrige ni la valida automáticamente. Esta diferencia puede deberse a relieve costero, DEM o selección de celda; requiere revisión geográfica.

## 2. Variables y agregación

| Campo mensual | Fuente diaria ERA5 | Cálculo y unidad |
|---|---|---|
| Temperatura media del aire | `temperature_2m_mean` | Media de días válidos, °C |
| Humedad relativa | `relative_humidity_2m_mean` | Media de días, % |
| Viento a 10 m | `wind_speed_10m_mean` | Media de días, **m/s** |
| Radiación solar de onda corta | `shortwave_radiation_sum` | **Suma** de todos los días del mes, MJ/m² |
| Presión media al nivel del mar | `pressure_msl_mean` | Media de días, hPa; **NO presión de la parcela** |
| Nubosidad media | `cloud_cover_mean` | Media diaria, % |
| Déficit de presión de vapor | `vapour_pressure_deficit_max` | Media mensual de los máximos diarios, kPa |

El control exige **todos los días calendario** de cada mes y rechaza nulos, valores no finitos, unidades inesperadas, cambios de celda entre ventanas, duplicados sector-mes y pérdida de procedencia SHA. La presión **al nivel del mar** no equivale a presión local de un predio de alta montaña.

La consulta usa `timezone=GMT`, `models=era5`, `cell_selection=nearest`, `elevation=nan` para evitar una corrección de altitud interpolada por Open-Meteo, con un `nan` por coordenada; se conserva siempre lo reportado por la celda ERA5. Las distintas latitudes y altitudes aún pueden verse afectadas por la resolución gruesa del reanálisis.

## 3. Procedimiento automático y estados

**Etapa A — inventario y piloto 2023:** `modelos/ingesta_era5_39_sectores_10g.py --mode pilot`: genera 39 puntos de consulta, verifica su inclusión en los polígonos y consulta todas las siete variables en 2023 (**468 registros sector-mes previstos**). Se auditan las celdas y agrupaciones compartidas. La evaluación piloto no autoriza ningún pronóstico.

**Etapa B — descarga multianual:** `--mode full` consulta tres intervalos 1996–2005, 2006–2015 y 2016–2025, cada uno dividido en lotes de cinco coordenadas. Tras comprobar todas las respuestas, exporta **14.040 filas sector-mes**, 360 por sector, matriz `muestra_era5_mensual_10g.csv`, inventario de solicitudes y SHA en `auditoria_atmosfera_10g.json`. Si una petición falla se **interrumpe y no inventa registros faltantes**.

**Etapa C — comparación predictiva (posterior):** para evitar filtración temporal, toda variable meteorológica incorporada a RF/GCN debe usarse **únicamente con el rezago que realmente pudiera haberse observado en la fecha histórica de emisión**; los archivos ERA5 actuales fueron reprocesados después de los eventos. Se requerirá validar si las nuevas covariables aportan habilidad frente a lluvia CHIRPS + océano y climatología (fase 10F), con particiones 1997–2015 entrenamiento, 2016–2018 ajuste, 2019–2020 calibración, 2021–2025 prueba; y cinco bloques espaciales. **No afirmar mejoras predictivas si todavía no se ha reentrenado.**

## 4. Limitaciones vigentes

- Son **reanalisis/modelos ERA5**, no sensores, estaciones de SENAMHI, datos exactos del cultivo ni promedios areales.
- Un sector puede compartir con otros la **misma celda atmosférica ERA5** y diferir mucho en altitud: la independencia e identificación territorial deben controlarse.
- Cobertura retrospectiva **no equivale a registro as-issued** disponible cuando se emitió un supuesto pronóstico.
- Los polígonos 9K **no son límites oficialmente delimitados ni pisos ecológicos certificados**.
- Estas variables ayudan a estudiar condiciones de lluvia alta, **pero no demuestran un evento El Niño costero ni infección de arándano/vid**. Esas probabilidades requieren etiquetas y validaciones distintas.
- Las corrientes geostróficas 2017–2025 siguen fuera de un entrenamiento 1997–2015 por cobertura incompleta.
- **Cero alertas automáticas o modelos operativos autorizados**.

## 5. Archivos y evidencias

- [Motor de ingesta y validación](modelos/ingesta_era5_39_sectores_10g.py)
- [Pruebas de QA espacial, física y temporal](tests/test_ingesta_era5_10g.py)
- [GitHub Actions de piloto](.github/workflows/oaf_10g_piloto.yml)
- [GitHub Actions de extensión histórica](.github/workflows/oaf_10g_completo.yml)
- [Puntos de muestreo y advertencias](datos/atmosfera_sectorial_10g/puntos_y_advertencias_10g.json)
- [Auditoría del piloto](datos/atmosfera_sectorial_10g/piloto_era5_2023_10g.json)
- [Matriz temporal completa cuando pase QA](datos/atmosfera_sectorial_10g/muestra_era5_mensual_10g.csv)
- [Manifiesto de auditoría SHA y celdas compartidas](datos/atmosfera_sectorial_10g/auditoria_atmosfera_10g.json)

### Línea investigativa del autor
La web mantiene separadas: **fuentes institucionales**, **estimaciones de lluvia alta (RF/GCN vs climatología)**, **estudio de El Niño costero/global**, y **condiciones asociadas a enfermedades agrícolas en arándano y vid**. Los modelos entrenados por el autor son experimentales hasta validación instrumental/prospectiva.
