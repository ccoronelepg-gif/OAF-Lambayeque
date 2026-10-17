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
