# Fase 8Q — Auditoría de continuidad entre núcleos agroclimáticos V1 y V2

**OAF-Lambayeque · Investigación de anomalías regionales · octubre de 2026**

## 1. Pregunta científica

Las fases 8O y 8P encontraron testigos cuyos perfiles meteorológicos de reanálisis se parecen, pero sus coordenadas pueden estar separadas hasta ~18 km y entre ellos existen valles, laderas y cumbres. **No se puede afirmar que existe un área homogénea continua solo porque dos extremos presenten temperaturas o lluvias parecidas.**

La fase 8Q plantea un **muestreo intermedio específico para comprobar esa hipótesis** antes de definir polígonos candidatos y modelos zonales de predicción.

## 2. Transectos seleccionados antes de comparar sus resultados

Se fijaron tres segmentos como hipótesis de estudio, basados en los núcleos exploratorios previos de 8P:

| Segmento | Núcleos originales | Altitud de los extremos DEM | Distancia geográfica |
|---|---|---|---|
| V1a, valle–piedemonte | M0163–M0224 | 521 y 307 m | 17,714 km |
| V1b, valle–piedemonte | M0184–M0224 | 212 y 307 m | 10,982 km |
| V2, montaña alta | M0234–M0308 | 2.978 y 3.236 m | 17,714 km |

En cada segmento se diseñaron cuatro objetivos de muestreo en las posiciones relativas 20 %, 40 %, 60 % y 80 %. Se seleccionó para cada objetivo el nodo disponible más cercano de la malla DEM de 420 centros de 8O, máximo a 5 km, evitando duplicados, extremos y cotas DEM inferiores a 5 m. Es un diseño geográfico **lineal conceptual** y no un levantamiento de una ruta topográfica continua, polígono agroclimático ni línea de menor coste/camino real.

En total se seleccionaron **10 puntos intermedios DEM** (V1a: cuatro; V1b: dos únicos adicionales porque otros objetivos ya estaban representados; V2: cuatro). Las cotas proceden del DEM del proveedor Open-Meteo, no de altímetros de campo.

## 3. Hallazgos físicos que cuestionan la continuidad homogénea

### V1a (centros con elevación DEM de 521 y 307 m)

En las posiciones intermedias se encontraron los nodos:
- M0179: 611 m
- M0184: 212 m
- M0202: 696 m
- **M0206: 1.120 m**, es decir, **770,2 m por encima de la elevación obtenida mediante interpolación lineal de los extremos** en esa fracción del segmento.

Estas cotas indican cambios topográficos importantes entre los centros, pero no demuestran por sí solas que la temperatura, humedad o precipitación difieran en la misma proporción.

### V1b (extremos DEM 212–307 m)

Se eligieron dos nodos DEM intermedios que no se repiten dentro del muestreo: M0203 (526 m) y M0205 (271 m). El diseño necesitará contrastar variaciones climáticas y otras posiciones adicionales si la cartografía agrícola oficial lo permite.

### V2 (extremos DEM 2.978 y 3.236 m)

Los puntos elegidos son:
- **M0253: 2.186 m**, situado **843,6 m por debajo** de la interpolación lineal del DEM entre extremos.
- M0262: 2.717 m
- **M0281: 3.839 m**, situado **706,2 m por encima** de la interpolación lineal.
- M0290: 3.546 m

La coexistencia de puntos de montaña de ~2.200 m y cumbres por encima de 3.800 m entre puntos originalmente parecidos impide tratar por defecto la zona como una superficie térmica, hídrica o fitosanitaria homogénea. La interpolación tiene incertidumbre porque los puntos se seleccionaron desde una malla regional y no representan una medición continua del perfil.

## 4. Próxima comparación climatológica reproducible, ya automatizada

Para los 10 nodos intermedios se diseñaron seis consultas históricas verificables, combinando:

- **ERA5-Land:** Tmedia, Tmax y Tmin a 2 m.
- **ERA5:** precipitación, humedad relativa media y radiación solar global.
- **Periodo fijo:** 1996–2025, tres décadas por modelo.
- **Parámetros:** zona America/Lima, selección de celda `land`, con URL de solicitud, UTC de adquisición y SHA-256 del JSON comprimido.
- **QA:** días completos, fechas iguales, valores finitos, unidades y coherencia Tmean/Tmin/Tmax. Ningún dato sintético puede ingresar al inventario productivo.

**Ejecución completada y auditada:** **6 de 6 respuestas históricas** originales archivadas, válidas y trazables mediante SHA-256; **10 de 10 puntos intermedios con 360 meses completos** de variables meteorológicas. Se conservaron por separado las coordenadas de las celdas proporcionadas por ERA5-Land (temperatura) y ERA5 (precipitación/humedad/radiación) en [`centros_modelados_8q.csv`](datos/transectos_8q/centros_modelados_8q.csv). Los centros resultaron constantes entre las tres décadas para cada punto y modelo.

### Resultados comparados del periodo completo 1996–2025

| Transecto | Mínimo de temperatura media de largo plazo | Máximo | Amplitud entre muestras |
|---|---:|---:|---:|
| V1a (4 muestras) | **19,0854 °C** (M0206, 1.120 m DEM) | **22,0676 °C** (M0184, 212 m) | **2,9822 °C** |
| V1b (2 muestras adicionales) | **21,7073 °C** (M0203, 526 m) | **22,0021 °C** (M0205, 271 m) | **0,2948 °C** |
| V2 (4 muestras) | **7,2269 °C** (M0281, 3.839 m) | **15,2893 °C** (M0253, 2.186 m) | **8,0624 °C** |

Estas cifras representan diferencias entre climatologías **modeladas en distintas coordenadas**, potencialmente afectadas por la elección de celda y el ajuste de elevación de Open-Meteo. No son sesgos frente a termómetros ni prueban por sí solas una relación causal altitud–temperatura. Sí muestran por qué no debemos atribuir la misma Tmedia a todos los ambientes de un transecto.

El análisis de las celdas originales identificó:

- **ERA5-Land:** **4 de los 10 puntos** comparten centro de celda con otro punto del mismo transecto. V1a comparte celda en M0179–M0184; V2 comparte celda en M0281–M0290.
- **ERA5:** **7 de los 10 puntos** comparten centro de celda con otros del mismo transecto: tres de V1a y los cuatro puntos V2.
- En **V2, las cuatro series de precipitación, humedad y radiación provienen de una misma celda ERA5**. Que la lluvia modelada sea exactamente **1.419,53 mm/año** para los cuatro nodos **NO constituye evidencia de un régimen pluviométrico homogéneo real** entre las laderas o cumbres.

En V1a, la precipitación anual histórica del modelo asciende a **1.355,28 mm** para tres nodos que reutilizan centro ERA5 y a **2.097,91 mm** en M0206 que consulta otra celda; esta diferencia no prueba una frontera climática precisa porque el cambio de píxel puede crear discontinuidades artificiales.

**Resultado científico útil:** la heterogeneidad térmica/altitudinal del transecto V2 y el contraste térmico de V1a indican que una zonificación que suponga temperaturas absolutas homogéneas en esos recorridos sería poco defendible. Para **predicción de anomalías**, sin embargo, también es necesario comparar cuánto se parecen las **anomalías temporales locales tras descontar la normal de cada sitio**: dos sitios con temperaturas base diferentes podrían compartir cierta señal temporal. Esa cuestión se evaluará separadamente para no confundir temperatura absoluta con respuesta anómala compartida.

**Control posterior necesario:** contrastar independientemente los ajustes altitudinales del proveedor y verificar datos SENAMHI, máscara tierra/mar, orientación de laderas, cuencas y uso agrícola. No asumir independencia estadística incluso entre centros de píxel distintos.

## 5. Hallazgos y conclusiones de aplicación agrícola

**Resultado comprobado hasta el corte:** existe **heterogeneidad física del relieve** entre los puntos seleccionados de V1 y V2. **NO se ha demostrado ni refutado formalmente todavía la homogeneidad climática espacial** porque falta completar las series históricas de los puntos intermedios y evaluar su continuidad con cartografía de terreno.

Para arándano y vid no se puede extrapolar incidencia o riesgo de enfermedades a partir de estas elevaciones, ni convertirlas en pronósticos operativos de El Niño Costero. Los avisos oficiales del ENFEN mantienen prioridad y la climatología de referencia OAF sigue siendo 1996–2025, con OMM 1991–2020 para comparaciones justificadas.

### Fuentes y artefactos del trabajo

- [Modelo reproducible de diseño y adquisición](modelos/transectos_continuidad_8q.py).
- [Pruebas del motor de selección](tests/test_transectos_continuidad_8q.py).
- [Automatización y recuperación progresiva de fuentes](.github/workflows/oaf_transectos_8q.yml).
- [Inventario de tres transectos y resultados](datos/transectos_8q/estado_transectos_8q.json).
- [CSV de diez nodos intermedios y desvío altitudinal](datos/transectos_8q/muestras_intermedias_8q.csv).
- [Climatologías obtenidas cuando existan seis bloques completos](datos/transectos_8q/comparacion_climatica_8q.csv).
- [Mapa de fase 8Q en Verificación de datos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).
- [Base ERA5-Land Copernicus](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- [API histórica Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api).

**Estado:** muestreo DEM y climatologías históricas completas de los diez puntos publicados y auditados. **Zonas homogéneas certificadas: cero; predicción zonal independiente acreditada: cero.**
