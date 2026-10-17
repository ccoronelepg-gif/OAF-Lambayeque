# OAF-Lambayeque — Fase 8Z: Humedad y aerosoles históricos (17 octubre 2026)

**Estado: infraestructura, ingesta y análisis descriptivo ejecutados en el repositorio; NO pronósticos de contaminación ni alertas fitosanitarias.**

## 1. Nuevas variables y alcance agroclimático

Se añadió **humedad relativa media del aire a 2 m (%)** y **déficit de presión de vapor (VPD, kPa)** desde **ERA5 mediante Open-Meteo Historical Weather API**, para el periodo **1996-01 a 2025-12**, en las referencias Chiclayo, Jayanca, Motupe y Olmos. El VPD es una medida de la demanda evaporativa atmosférica. No supone medición directa dentro del dosel de arándano/vid ni estima mojado foliar o presión de enfermedad por sí sola.

Las variables se descargaron con salida **diaria**: `relative_humidity_2m_mean` y `vapour_pressure_deficit_max`, modeladas ERA5 con zona `America/Lima`. La agregación de VPD en la salida mensual consiste en **media de los máximos diarios** y **máximo entre los máximos diarios**, no VPD medio horario. La humedad mensual es la media ponderada por día de las medias diarias. Se verifican 360 meses completos/localidad (incluido febrero de años bisiestos), unidades %, kPa, extremos no físicos, celdas geográficas y SHA-256 original.

**Resultados verificados y publicados: 1.440 meses-localidad**, cuatro sitios × 360 meses, con fuentes comprimidas originales y metadatos. Se documenta todo en:
- [Datos mensuales RH y VPD](datos/humedad_8z/humedad_vpd_mensual_8z.csv).
- [Estado trazable de humedad](datos/humedad_8z/estado_humedad_8z.json).
- [Motor Python](modelos/humedad_agroclimatica_8z.py), [tests](tests/test_humedad_agroclimatica_8z.py) y [GitHub Actions](.github/workflows/oaf_humedad_agroclimatica_8z.yml).
- [Open-Meteo Historical API y campos diarios oficiales](https://open-meteo.com/en/docs/historical-weather-api).

El periodo reciente 1996–2025 sigue siendo la **referencia descriptiva de 30 años**. En modelos predictivos posteriores se prohíbe estimar la climatología de una prueba usando cualquier parte de esa propia prueba.

## 2. Primer cruce PM₂.₅/PM₁₀ con RH y VPD

La fuente CAMS Global archivada en fase 8X ahora cubre **2023–2025, con 144 meses-localidad**, 36 por referencia geográfica. Se detectaron series PM idénticas de **Motupe y Olmos** durante los 36 meses, por lo que **no son cuatro series aerosol estadísticamente independientes**. Los aerosoles son estimaciones de modelo global, NO PM medido por estaciones de SENAMHI.

El motor [`modelos/relacion_pm_humedad_8z.py`](modelos/relacion_pm_humedad_8z.py) integra solo los meses comunes de 2023–2025 y ejecuta **16 comparaciones**, cuatro sitios × dos partículas × dos covariables (RH y VPD). Calcula Pearson bruto y tras descontar el promedio por mes calendario; aplica exclusión de un año a la vez como contraste descriptivo. **No hay p-valores, causalidad inferida, independencia espacial ni pronóstico validado**.

Hallazgos seleccionados de Chiclayo sobre los 36 meses:
- PM₂.₅ ↔ RH: **r bruto +0,233255**, **r desestacionalizado +0,007970**.
- PM₂.₅ ↔ VPD: **r bruto −0,373253**, **r desestacionalizado −0,184673**.
- PM₁₀ ↔ RH: **r bruto +0,289779**, **r desestacionalizado −0,156723**.

La magnitud y el signo dependen del tratamiento estacional y del año omitido. Esto no prueba mecanismos agronómicos ni efectos de El Niño. Salida: [`datos/relaciones_pm_humedad_8z/estado_relacion_pm_humedad_8z.json`](datos/relaciones_pm_humedad_8z/estado_relacion_pm_humedad_8z.json). [Tests](tests/test_relacion_pm_humedad_8z.py) y [workflow](.github/workflows/oaf_relacion_pm_humedad_8z.yml).

Se corrigió además el diagnóstico 8Y previo para actualizar los cálculos contra los **144 registros PM de 2023–2025** realmente publicados, sin mantener los 48 de 2025 como si fueran la serie completa.

## 3. Piloto científico NASA MERRA-2: verificación real del catálogo

**Hallazgo: se verificó en NASA CMR la existencia de granulos en 1998 y 2025 de ambas colecciones**, pero los ficheros NetCDF NO fueron descargados ni convertidos en concentraciones mensuales PM de Lambayeque. Las cuatro consultas de muestra a NASA CMR dieron archivos:
- **M2T1NXAER (aerosoles de superficie, 2D)**: 15 marzo 1998 y 15 julio 2025.
- **M2I3NVAER (mezclas de aerosoles en columna, 3D)**: 15 marzo 1998 y 15 julio 2025.

Archivo reproducible: [`datos/merra2_8z/estado_piloto_merra2_8z.json`](datos/merra2_8z/estado_piloto_merra2_8z.json). El programa [`modelos/piloto_merra2_pm_8z.py`](modelos/piloto_merra2_pm_8z.py) consulta CMR sin autenticación para confirmar metadatos y contiene fórmulas y tests sintéticos verificados; **los metadatos jamás equivalen a datos observados o promedios de PM calculados**.

### Fórmula oficial NASA MERRA-2 para PM₂.₅ seco a superficie

Según [NASA GMAO MERRA-2 FAQ](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/faq_merra-2/), usando especies superficiales M2T1NXAER:

`PM2.5 (kg/m³) = DUSMASS25 + OCSMASS + BCSMASS + SSSMASS25 + SO4SMASS * (132.14 / 96.06)`.

Para expresar en µg/m³ se multiplica la salida kg/m³ por **10⁹**. El factor de sulfato convierte masa iónica de sulfato al equivalente usado por NASA. OCSMASS ya está representado como masa de materia orgánica del modelo, por lo que **no se añade arbitrariamente un factor 1,8**. La ecuación representa PM₂.₅ seco, sin crecimiento higroscópico explícito.

### PM₁₀ requiere otro producto tridimensional

NASA especifica que **no se obtiene PM₁₀ total a partir de los cinco campos superficiales PM₂.₅**. Requiere el producto de mezcla de aerosoles M2I3NVAER, **nivel inferior 72**, y densidad del aire `AIRDENS`, con combinación:

`PM10 (kg/m³) = (1.375 * SO4 + BCphobic + BCphilic + OCphobic + OCphilic + DU001 + DU002 + DU003 + 0.74 * DU004 + SS001 + SS002 + SS003 + SS004) * AIRDENS`.

Mismas unidades finales µg/m³ multiplicando por 10⁹. **Necesita confirmar los nombres de variables y AIRDENS de los granulos seleccionados** antes de generar la serie; en 8Z solo se han validado matemáticamente las fórmulas con pruebas sintéticas.

Referencia: [NASA MERRA-2 FAQ fórmula PM10 nivel 72](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/faq_merra-2/). Detalle de la colección [M2T1NXAER](https://access.earthdata.nasa.gov/collections/C1276812830-GES_DISC). MERRA-2 desde 1980, resolución 0,5° × 0,625°; tiene celdas demasiado gruesas para representar por sí solas parcelas y pisos altitudinales complejos de Lambayeque.

## 4. Visualización y límites

El portal integra el panel «Fase 8Z · Humedad, VPD y aerosoles históricos NASA» dentro de [Verificación de datos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones). Muestra gráficos anuales 1996–2025 con filtros por localidad y variable, tablas de PM con RH/VPD solo en meses coincidentes, y número de archivos NASA del catálogo CMR. No se muestra ninguna supuesta serie PM NASA calculada.

Esta fase aporta factores para análisis futuro de variabilidad de humedad y demanda atmosférica, **pero no autoriza umbrales de Botrytis, oídio o enfermedad de vid/arándano**, pues faltan datos de microclima foliar, medición en campo, fenología y evaluaciones fitosanitarias verificadas. De igual modo no autoriza alertas de contaminación ni comprobación de estándares ECA con CAMS.

## 5. Próxima fase: 9A

Se propone iniciar una nueva serie de trabajo **9A — Sensibilidad predictiva con humedad/VPD**:

1. Incorporar únicamente las variables ERA5 de RH y VPD que tienen 1996–2025 íntegros a un **benchmark walk-forward** contra el 8W, con exactamente las mismas localidades, cortes, pronósticos y métricas, y auditar el efecto en extremos.
2. Diseñar pruebas para anticipar años húmedos/secos comparando climatología, persistencia, SST, viento y RH/VPD, con estimadores ajustados exclusivamente en cada entrenamiento.
3. Construir *subset* real MERRA-2 1996–2025 previa autenticación y autorización NASA Earthdata si corresponde; completar NetCDF, conversión oficial PM₂.₅ y PM₁₀, resolución y sesgo frente a CAMS 2023–2025. **Sin datos descargados, abstenerse de emitir tendencias PM de 30 años**.
4. Añadir contrastes instrumentales SENAMHI por pisos agroclimáticos homogéneos; usar ENFEN/IMARPE como fuentes oficiales para anomalías oceánicas y SENASA para hechos fitosanitarios, sin confundir correlaciones con pronósticos certificados.

**Dictamen de fase 8Z: integración histórica RH/VPD completada, relaciones PM descriptivas examinadas, fórmula NASA correctamente codificada y existencia histórica de archivos confirmada; NO se dispone aún de serie NASA PM procesada ni de alertas operativas.**
