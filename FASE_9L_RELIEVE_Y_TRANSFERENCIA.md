# Fase 9L — Continuidad topográfica real de núcleos agroclimáticos y límite de transferencia estacional

**OAF-Lambayeque · 17/10/2026.** Estado: extracción real del Copernicus GLO-90 ejecutada, verificada y archivada; análisis piloto de relieve de 3 familias/5 polígonos. **No se declara delimitación oficial, homogeneidad climática observada, riesgo fitosanitario ni pronóstico altitudinal operativo.**

## 1. Antecedente y pregunta científica

La fase 9K produjo 42 polígonos gráficos de influencia, partiendo de 420 puntos de altitud DEM, 81 testigos con climatologías completas 1996–2025, y tres familias de similitud climática entre celdas distintas de ERA5 y ERA5-Land. Algunos sectores habían sido asociados por relaciones de vecindad, no por relieve continuo.

La fase 9L pregunta: **¿qué parte de las superficies asociadas a esas familias permanece dentro del mismo piso altitudinal cuando se utiliza un modelo de elevación espacialmente continuo y un filtro explícito de pendiente?** No intenta clasificar todo Lambayeque por pendientes sin observar topografía de cada parcela y cuenca.

## 2. Fuente geográfica original descargada y preservada

- **Copernicus DEM GLO-90, DSM 2021**, publicado en AWS Open Data como Cloud Optimized GeoTIFF. [Documentación del dataset](https://registry.opendata.aws/copernicus-dem/) y [guía de estructura de teselas](https://copernicus-dem-90m.s3.amazonaws.com/readme.html).
- **Tesela:** `Copernicus_DSM_COG_30_S07_00_W080_00_DEM.tif`, que cubre los 5 sectores de prueba prioritarios ubicados dentro del grado 7° S a 6° S, 80° O a 79° O.
- **URL original:** https://copernicus-dem-90m.s3.amazonaws.com/Copernicus_DSM_COG_30_S07_00_W080_00_DEM/Copernicus_DSM_COG_30_S07_00_W080_00_DEM.tif
- **Tamaño de origen:** 5.354.601 bytes.
- **Huella SHA-256 de los bytes originales:** `c4d78e481f80927d72886787e422ed02214ffb0d5739e67a25facd2c874f7532`.
- **Resolución fuente:** unos 90 m; **evaluación raster:** agregación determinista 3 × 3, aproximadamente 270 m. Es una máscara piloto, no replanteo cartográfico a precisión oficial.
- La fuente DSM representa la superficie terrestre, incluidos edificios, vegetación y otras estructuras: **no equivale a altimetría topográfica de terreno desnudo**. Citar Copernicus DEM mediante DOI [10.5270/ESA-c5d3d65](https://doi.org/10.5270/ESA-c5d3d65).

El TIFF original se conserva para reproducir el análisis; se verifican CRS EPSG:4326, presencia de banda única, cobertura de coordenadas, validez del rango de elevación, identificadores 9K, SHA y determinismo de la salida.

## 3. Algoritmo SIG

1. Seleccionar solo los **cinco fragmentos geométricos vinculados a C01/C02/C03**: no extrapolar a los otros 37 polígonos de 9K.
2. Recortar el raster fuente a una ventana que incluye cada polígono, reescalando a ~270 m y calculando elevación en cada celda.
3. Estimar pendiente local desde gradientes del DSM y distancias métricas por latitud. Excluir vecindades incompletas o no finitas.
4. Comparar el DEM continuo con el piso nominal de 9K (C01: 300–799 m; C02: ≥2500 m; C03: 1600–2499 m) y retener píxeles con **pendiente calculada no superior a 30°**. El límite de 30° es **hipótesis técnica conservadora para cribado de continuidad**, no umbral normativo para agricultura ni clase ecológica.
5. Poligonizar solo los píxeles compatibles, recortar por la geometría 9K y comprobar geometría válida, topología reproducible y ausencia de extensión hacia afuera.
6. Reportar la fracción de píxeles por fragmento y familia. **No utilizarla como superficie agrícola o fracción de cuenca** ni interpretar las manchas cartográficas desconectadas como barreras climáticas medidas.
7. Un fragmento del mismo piso puede presentar pendientes e insolación muy diferentes; **no se infiere igual temperatura, lluvia, humedad o incidencia de enfermedades**.

## 4. Resultados reales de cada sector

| Familia | Sector 9K | Cota mediana DSM | Pendiente p90 de píxeles evaluados | Fracción compatible | Partes separadas después del filtro |
|---|---|---:|---:|---:|---:|
| C01 (piedemonte) | S023 | **515,16 m** | 24,97° | **65,49 %** | **17** |
| C02 (alta montaña) | S006 | **3340,43 m** | 19,36° | **99,69 %** | **1** |
| C02 (alta montaña) | S007 | **3031,02 m** | 23,47° | **84,44 %** | **1** |
| C03 (ladera media) | S015 | **2309,66 m** | 36,28° | **56,10 %** | **3** |
| C03 (ladera media) | S016 | **2332,13 m** | 34,01° | **57,51 %** | **6** |

### Síntesis ponderada por píxeles del DSM agregado

| Familia | Sectores estudiados | Píxeles evaluados | Píxeles retenidos | Fracción compatible |
|---|---:|---:|---:|---:|
| **C01** | 1 | 3.190 | 2.089 | **65,486 %** |
| **C02** | 2 | 2.169 | 2.075 | **95,666 %** |
| **C03** | 2 | 944 | 534 | **56,568 %** |

Interpretación correcta: en C02 la máscara topográfica es menos fragmentada **dentro de los polígonos seleccionados**, pero nada de ello demuestra que la montaña alta tenga clima uniforme. C01 y C03 presentan más interrupciones físicas que deben investigarse con DEM más fino, cuencas y estaciones. Los gradientes DSM no se convierten en modelos de transferencia de anomalías por ladera.

## 5. Diseño explícito de transferencia de NOAA NMME sin fugas estadísticas

Los archivos NOAA NMME de 9K para octubre de 2026 tienen resolución **1° × 1°**, una anomalía de temperatura de conjunto multimodelo y otra anomalía de tasa de precipitación. Tres de las localidades representativas compartían el mismo centro de celda; por tanto, **no hay 42 realizaciones espaciales distintas ni 42 pronósticos independientes**.

La arquitectura de trabajo propuesta es **jerárquica, todavía sin ajuste entrenado**:

\[
X_{s,t}^{pron} = \mu_{s,m}^{local} + f_{s,m,h}(A_{g(s),t}^{NMME},Z_s,R_s,B_s)
\]

donde \(\mu_{s,m}^{local}\) sería la climatología independiente del sector \(s\) para el mes \(m\), \(A_{g(s),t}^{NMME}\) la anomalía de la celda gruesa \(g(s)\), y \(Z_s,R_s,B_s\) describirían altitud, relieve y cuenca. La función \(f\) **no está entrenada** ni calibrada en 9L. También falta demostrar compatibilidad entre la referencia de anomalía propia del NMME y la normal OAF 1996–2025.

Para un futuro ensayo se necesitarían emisiones numéricas NMME archivadas con fecha verdadera de inicialización, climatologías derivadas solo de datos disponibles hasta la emisión, observaciones locales independientes, validación cruzada espacial por cuencas y periodos totalmente posteriores. Se compararían contra climatología y persistencia para evitar una ganancia aparente debida a duplicar píxeles.

Los productos de 9L fijan **predicciones zonales generadas = 0**, **evaluación prospectiva validada = falsa**, **zonas homogéneas certificadas = 0**, **cuencas oficiales confirmadas = 0**. Se conserva como referencia primaria descriptiva 1996–2025, OMM 1991–2020 solo para comparabilidad y SENAMHI/ENFEN para observaciones y avisos institucionales.

## 5A. Comprobación institucional de unidades hidrográficas: intento registrado, sin inventar resultados

Se integró un procedimiento independiente, `modelos/consulta_cuencas_9l.py`, que intenta recuperar unidades hidrográficas mediante el servicio **EXTERNAS/Hidrografia/MapServer/6** atribuido a ANA y publicado por el Ministerio de Vivienda, Construcción y Saneamiento. Su consulta se limita a la envolvente de los núcleos (79,67°–79,24° O; 6,62°–6,05° S). La tarea de GitHub se ejecutó correctamente **en modo de registro de estado**, pero la consulta externa devolvió **error DNS (`Name or service not known`)** desde el entorno de ejecución. Por tanto **NO** se descargó ni comprobó ninguna geometría hidrográfica y se conserva **0 cuencas certificadas / 0 intersecciones**. El error no se interpreta como ausencia de cuencas en Lambayeque.

- [Registro de la consulta y error original](datos/relieve_9l/consulta_unidades_hidrograficas_9l.json).
- [GeoJSON vacío e identificado como no validado](datos/relieve_9l/intersecciones_cuencas_9l.geojson).
- [Workflow de comprobación de estado](.github/workflows/oaf_cuencas_9l.yml).
- [HydroBASINS, alternativa global de referencia cartográfica](https://www.hydrosheds.org/products/hydrobasins); también requiere cotejo con unidades hidrográficas ANA antes de asignar sectores por cuenca.

**Esta limitación impide afirmar la continuidad de una cuenca o fusionar sectores entre vertientes distintas.** Solo la topografía del DSM original sustenta el filtro espacial descrito en la fase.

## 6. Entregables

- [Copernicus GLO-90 original, sin reescribir](datos/relieve_9l/fuentes/copernicus_glo90_s07_w080.tif).
- [Polígonos 9L restringidos por relieve](datos/relieve_9l/nucleos_restringidos_relieve_9l.geojson).
- [Resultados de tres familias, cinco sectores, fuentes y SHA](datos/relieve_9l/estado_relieve_9l.json).
- [Motor SIG de relieve continuo](modelos/refinar_relieve_9l.py).
- [Pruebas de topología y fuentes](tests/test_relieve_9l.py).
- [GitHub Actions de reproducibilidad](.github/workflows/oaf_relieve_9l.yml).
- [Nuevo visor del relieve](modelos/visor_relieve_9l.js) integrado en la pestaña **Análisis de clima regional**, junto con el mapa altitudinal de 9K.

## 7. Pendientes comprobables (siguiente fase 9M)

Recuperar capa oficial de límites actualizados IGN/INEI y una capa de **unidades hidrográficas ANA**, con metadatos y licencia; cruzar ambos productos con los fragmentos y datos de ladera. Calcular estabilidad frente a cambios del umbral de pendiente y resolución agregada, y contrastar con observaciones meteorológicas de estaciones independientes. Solo después es defendible subdividir o fusionar zonas de predicción por cuenca o por régimen pluviométrico, con comparación prospectiva de NMME y otras fuentes climáticas. Para arándano y vid se requieren observaciones fenológicas y fitosanitarias de campo para transformar probabilidades meteorológicas en avisos agrícolas.
