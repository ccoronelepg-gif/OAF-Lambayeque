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

**Regla de publicación:** solo se calcularán indicadores climáticos de los diez puntos cuando estén archivadas las **seis fuentes originales completas**, evitando presentar un bloque aislado como una climatología de treinta años. Se utilizarán el mismo periodo y modelos de la fase 8P.

En la primera ejecución la plataforma completó correctamente **1 de las 6 fuentes climáticas**; las restantes se obtendrán mediante GitHub Actions a un ritmo conservador y respetando los límites del proveedor. El [estado vivo](datos/transectos_8q/estado_transectos_8q.json) permite comprobar cuántas fuentes hay realmente. Una vez completas, se informarán por testigo la temperatura media de 30 años, la precipitación media anual, la humedad relativa y la radiación, sin atribuir causalidad de altitud por sí sola.

**Control posterior necesario:** comprobar identidad de píxeles ERA5 y ERA5-Land entre los puntos intermedios. Dos consultas distintas pueden reutilizar la misma celda. También será necesario incorporar unidades climáticas por cuenca, pendiente y exposición, y evaluar series observadas de SENAMHI.

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

**Estado:** el muestreo DEM intermedio está comprobado; la comparación climática multivariable de los diez puntos sigue en ejecución. **Zonas homogéneas certificadas: cero.**
