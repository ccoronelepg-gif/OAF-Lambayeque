# Fase 8P — Ampliación de testigos agroclimáticos y contraste de vecindades

**OAF-Lambayeque · ejecución de octubre de 2026 · periodo climático 1996–2025**

## 1. Motivo y objetivo

La fase 8O obtuvo perfiles multivariables históricos de 19 puntos y encontró dos conglomerados estadísticos; uno agrupaba 17 puntos de gran diversidad espacial y altitudinal, mientras el otro agrupaba dos puntos del extremo occidental con cotas DEM de 0 y −1 m, pendientes de comprobar si pertenecen a territorio agrícola terrestre. Por eso **no se pueden declarar dos zonas homogéneas para Lambayeque**.

La fase 8P sustituye la propuesta de extrapolar conglomerados no contiguos por una estrategia incremental: **densificar los testigos de clima y comparar primero nodos cercanos entre sí**. Los pares similares identifican sitios prioritarios de comprobación, no polígonos zonales ni modelos predictivos validados.

## 2. Muestreo nuevo ejecutado

A partir de **420 puntos de elevación DEM GLO-90** previamente archivados y auditados en 8O, se seleccionaron **62 testigos adicionales**, evitando repetir los 19 testigos originales. Los testigos se eligieron mediante muestreo determinista de máxima separación geográfica entre puntos de cada estrato altitudinal, con prioridad a montaña y zonas de transición.

| Estrato físico de diseño | Testigos nuevos |
|---|---:|
| Planicie, <100 m, únicamente DEM >5 m | 10 |
| Valle bajo, 100–299 m | 10 |
| Piedemonte, 300–799 m | 12 |
| Ladera baja, 800–1.599 m | 10 |
| Ladera media, 1.600–2.499 m | 8 |
| Alta montaña, ≥2.500 m | 12 |
| **Total adicional** | **62** |

La red de testigos climáticos por estudiar pasa de **19 a 81**. Los 62 nuevos no son estaciones meteorológicas SENAMHI y no se consideran automáticamente sitios representativos de cultivos. La selección excluye nuevos puntos con cota DEM ≤5 m como **filtro precautorio frente a línea de costa incierta**, sin afirmar que todas las cotas inferiores sean mar ni que el conjunto restante sea necesariamente agrícola.

El diseño regional generó además **1.244 aristas de cercanía de hasta 8,5 km** entre los 420 nodos DEM: constituyen relaciones geométricas para organizar el muestreo, **no regiones climatológicamente homogéneas**, límites de cuenca o caminos sin barreras.

## 3. Variables y control de los registros históricos

Se reaprovechan las 19 climatologías 8O (360 meses por punto) sin volver a descargarlas. Los 62 testigos nuevos se dividieron en cuatro grupos de **16, 16, 16 y 14** ubicaciones. Por grupo se descargan seis bloques independientes:

- **ERA5-Land**, tres décadas 1996–2005, 2006–2015 y 2016–2025: temperatura media, máxima y mínima diaria a 2 m.
- **ERA5**, las mismas tres décadas: precipitación diaria, humedad relativa media diaria y radiación solar diaria.

Esto requiere **24 respuestas del proveedor** (cuatro grupos × dos modelos × tres décadas), con URL original, SHA-256, fecha de descarga y muestras diarias completas, sin interpolación ni mezclas de variables incompatibles. El workflow descarga como máximo **dos bloques nuevos por ejecución** y continuará desde los archivos verificados existentes; se detiene o deja pendientes los que el proveedor no permita comprobar.

**Una ubicación nueva solo se incorpora a los resultados de clima cuando cuenta con las seis fuentes correspondientes a su grupo y con 360 meses completos de todas las variables.** Mientras tanto no se publica como perfil histórico terminado. Los 19 perfiles anteriores permanecen identificados como fase 8O; los nuevos llevarán etiqueta 8P.

## 4. Identificación exploratoria de vecindades similares

Para cada par de puntos con climatologías completas, se exigen **separación de hasta 20 km** y elevación DEM mayor de 5 m. Se calculan diferencias de:

1. Temperatura media normal por mes calendario.
2. Amplitud diaria media de temperatura, Tmax − Tmin.
3. Precipitación media mensual y diferencia de lluvia anual.
4. Humedad relativa media.
5. Radiación solar media mensual.

Las normales se calculan sobre **1996–2025**. Para mantener comparabilidad al agregarse nuevos lotes, las variables se estandarizan con los promedios y desviaciones estándar fijas de los **19 testigos originales 8O**, evitando que cambie la escala al ingresar un nuevo grupo.

Se aplica un cribado **provisional, descriptivo, no normativo**: distancia ≤20 km, distancia multivariable normalizada ≤0,60, desnivel DEM ≤300 m, diferencia de temperatura media anual ≤1,5 °C y diferencia de lluvia anual ≤150 mm. Los puntos con cota DEM ≤5 m no forman parejas elegibles sin verificación de tierra/mar.

**No confundir:** superar esos umbrales no equivale a ser una zona climática homogénea ni a tener igual fenología, incidencia de plagas, régimen pluviométrico, exposición o aptitud agrícola. Son reglas para elegir qué pares comprobar primero. La diferencia no es validación con termómetros SENAMHI ni probabilidad de Niño Costero.

## 5. Resultados y controles inicialmente observados

- **420 centros DEM originales disponibles**.
- **62 nuevos testigos seleccionados** y comprobados sin duplicar los 19 anteriores.
- **1.244 relaciones geométricas de cercanía ≤8,5 km**.
- **19 testigos climáticos existentes 8O** (1996–2025) reutilizados para comenzar el contraste.
- Se identificó un primer par preliminar de interés **M0308–M0234**: aproximadamente 17,71 km entre centros, 258 m de desnivel DEM, distancia climática estandarizada ~0,250, diferencia media anual térmica ~1,05 °C y diferencia anual de lluvia ~53,2 mm (datos de reanálisis). **No implica que las superficies intermedias sean homogéneas**.
- Las nuevas climatologías 8P se incorporarán únicamente después de reunir los seis archivos decenales íntegros de cada grupo. El número actualizado de bloques y testigos completos está en [estado_clima_8p.json](datos/clima_contiguo_8p/estado_clima_8p.json).

El número de polígonos geográficos certificados y predicciones zonales comprobadas es **0**.

## 5A. Primera ampliación climática efectivamente calculada y control de píxeles (corte octubre 2026)

Se han descargado y validado **las seis fuentes decenales completas del primer grupo de 16 testigos nuevos**, por lo que existen ahora **35 testigos con 360 meses completos**: 19 de 8O y 16 de 8P. Se calcularon **19 pares con separación de hasta 20 km** y **cinco pares que superaron el cribado multivariable preliminar**.

**Auditoría fundamental de pseudorreplicación:** al revisar las coordenadas del centro de celda efectivamente devueltas por los JSON originales de ERA5 y ERA5-Land, se encontró que **cuatro de los cinco pares** comparten **la misma celda de ERA5** (fuente de lluvia, humedad y radiación). Aunque las coordenadas consultadas sean diferentes, estas variables no constituyen allí dos datos de reanálisis espacialmente independientes. Para esos pares las diferencias anuales de precipitación resultaron exactamente 0 mm. **No deben declararse zonas homogéneas por esa coincidencia artificial.** Los cinco pares aparecen en el CSV con los campos `igual_celda_era5`, `igual_celda_era5land` y `centros_de_ambos_modelos_diferentes`.

El par que **no** comparte centros de celda en ninguno de los dos modelos es **M0308–M0234**, ambos puntos altos de la muestra (DEM **3.236 y 2.978 m**). El contraste descriptivo entregó:

| Métrica | Valor |
|---|---:|
| Separación geográfica | **17,714 km** |
| Diferencia de altitud DEM | **258 m** |
| Distancia climática estandarizada | **0,24979** |
| Diferencia de temperatura media anual | **−1,046 °C** |
| Diferencia de precipitación anual promedio | **−53,237 mm** |
| Diferencia de humedad relativa media | **1,249 puntos porcentuales** |
| Identidad de celda ERA5 / ERA5-Land | **Diferentes / diferentes** |
| Zona montañosa homogénea certificada | **No** |

Este par es un **candidato prioritario para investigar continuidad climática de alta montaña**. Los 17,7 km de separación no garantizan que las laderas, vertientes y microcuencas intermedias sean homogéneas. Tampoco garantiza exactitud instrumental ni independencia estadística por autocorrelación espacial: celdas distintas pueden tener errores correlacionados.

La ampliación hacia los **46 testigos nuevos restantes** seguirá mediante la automatización, de acuerdo con el límite de consultas del proveedor. La cifra dinámica de lotes cargados y pares está en [`estado_clima_8p.json`](datos/clima_contiguo_8p/estado_clima_8p.json). No atribuir como validada ninguna zona ni emitir pronósticos por grupo todavía.

## 5B. Segundo corte: dos núcleos de vecindad que requieren investigación, sin polígonos

Con los **dos primeros grupos de descarga 8P completos**, el análisis cuenta con **51 testigos** (19 de 8O + 32 de 8P), todos con **1996–2025 completo**. Dentro de ese conjunto, 61 pares están a 20 km o menos, y 13 cumplen el filtro exploratorio. La auditoría de centros de celda revela **10 de esos 13 pares con una misma celda ERA5 o ERA5-Land compartida**. **Tres pares utilizan centros distintos en ambos modelos** (sin que eso signifique independientes desde el punto de vista estadístico).

Se formaron **dos núcleos de puntos unidos por pares climáticamente parecidos y próximos**, sin interpolación espacial ni polígonos:

| Núcleo piloto | Testigos con climatología | Altitudes DEM | Enlaces con ambas celdas distintas | Interpretación correcta |
|---|---|---:|---:|---|
| **V1: transición de valle alto/piedemonte** | M0163, M0184, M0224 | 212–521 m | 2 | Conjunto local de tres puntos que justifica refinar el muestreo alrededor; no equivale a una zona agrícola continua |
| **V2: alta montaña** | M0234, M0308 | 2.978–3.236 m | 1 | Par montañoso con afinidad climatológica, separado aproximadamente 17,7 km, pendiente de verificar el espacio intermedio |

Las coordenadas de los nodos V1 son aproximadamente **−6,469 a −6,313° S y −79,562 a −79,531° O**; V2 se sitúa entre **−6,281 y −6,125° S, alrededor de −79,375° O**. No se atribuyen nombres de comunidades, parcelas ni estaciones oficiales sin cartografía y metadatos verificados.

**Advertencia:** estos núcleos únicamente están compuestos por nodos enlazados mediante una prueba de proximidad y perfiles de reanálisis. No existe evaluación del clima entre las ubicaciones, máscaras oficiales de tierra/mar, suelo agrícola, límites de cuenca ni contrastes independientes de SENAMHI. **No constituyen zonas homogéneas demostradas ni habilitan pronósticos o alertas por zona.**

El [estado climático 8P](datos/clima_contiguo_8p/estado_clima_8p.json) actualiza automáticamente el inventario, el número de pares y los núcleos cuando finalizan nuevos bloques, sin sustituir las fuentes anteriores.

## 6. Archivos y automatización

- [Muestreo de nuevos testigos y grafo](modelos/muestreo_zonas_contiguas_8p.py).
- [Modelo de comparación de clima por grupos 1996–2025](modelos/clima_vecindades_8p.py).
- [Programa de pruebas geográficas](tests/test_muestreo_zonas_8p.py).
- [Pruebas de calidad climática](tests/test_clima_vecindades_8p.py).
- [Inventario del diseño 8P](datos/zonas_contiguas_8p/estado_muestreo_8p.json).
- [Lista de 62 puntos nuevos](datos/zonas_contiguas_8p/nuevos_testigos_8p.csv).
- [Grafo de cercanía inicial 420 puntos](datos/zonas_contiguas_8p/aristas_cercania_8p.csv).
- [Estado climático y cobertura por grupos](datos/clima_contiguo_8p/estado_clima_8p.json).
- [Comparaciones de pares locales](datos/clima_contiguo_8p/pares_climaticos_cercanos_8p.csv) y [parejas seleccionadas para revisión](datos/clima_contiguo_8p/pares_similares_exploratorios_8p.csv).
- [Automatización del diseño](.github/workflows/oaf_zonas_8p.yml) y [adquisición climática](.github/workflows/oaf_clima_8p.yml).
- Panel público **Fase 8P** en [Verificación de datos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

## 7. ¿Qué falta para poder afirmar que existen zonas homogéneas?

El problema científico **no está resuelto solo por densificar y agrupar**. Antes de delimitar regiones con rigor debemos:

- **Verificar límites y tierra/mar** usando cartografía oficial IGN/INEI, así como usos de suelo, cuencas y continuidad territorial, especialmente en el litoral.
- **Completar los 81 testigos y expandir a la malla** donde existan fuertes gradientes de clima; detectar células ERA5-Land compartidas y evitar pseudo-replicación espacial.
- Comparar el comportamiento de grupos en las tres décadas y ventanas de verificación temporal y espacial independientes; evaluar sensibilidad al periodo base, pesos, distancia y umbrales.
- Definir **polígonos contiguos** solo si los gradientes climáticos y geografía apoyan separaciones reales, con áreas de transición e incertidumbre explícitas.
- Contrastar con **SENAMHI** y registros agronómicos reales. Para arándano y vid, agregar observaciones de campo y fenología, nunca extrapolar incidencia de enfermedad a partir del reanálisis por sí solo.
- Después preparar y verificar pronósticos de anomalías zonales frente a climatología y persistencia, y cruzar los avisos de Niño Costero con **ENFEN** como fuente oficial.

**Referencias:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), [ERA5-Land en Copernicus](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land), [Geoportal INEI](https://ide.inei.gob.pe/).

**Estado:** implementación y adquisición climática reales en curso, no zonas operativas.
