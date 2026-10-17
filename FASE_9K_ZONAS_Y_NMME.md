# Fase 9K — Agrupación de sectores por pisos altitudinales, continuidad y similitud climática; NOAA NMME numérico

**OAF-Lambayeque · Fecha:** 17 de octubre de 2026 · **Tipo:** sistema experimental SIG y archivo de anomalías estacionales, **sin** zonificación climatológica o pronóstico agrícola operativo validado.

## 1. Objetivo y cambio frente a 9J

Construir un primer mapa de **polígonos de influencia geográfica del muestreo** con altitudes y núcleos de semejanza climática; respetar el contraste entre costa, valle, piedemonte y ambientes andinos. **Agrupar piezas solo dentro de un mismo piso físico**, sin suponer que toda la superficie tiene la altitud medida en un centro. Además, incorporar **datos numéricos reales de pronóstico NOAA NMME** como información de gran escala, **sin** extenderlos ficticiamente a pisos de menor tamaño que la celda de 1°.

## 2. Insumos verificados y su representatividad

- **420 nodos geográficos con elevación** ya obtenida del Copernicus DEM GLO-90 mediante [Open-Meteo Elevation API](https://open-meteo.com/en/docs/elevation-api), archivo `datos/muestreo_8o/nodos_dem_8o.csv`. El DEM tiene una resolución fuente aproximada de 90 m, pero **420 puntos NO equivalen a una cuadrícula regional de elevación de 90 m**.
- **81 perfiles completos 1996–2025**, incluyendo temperatura a 2 m de ERA5-Land y lluvia, HR y radiación de ERA5, conservados de las fases 8O–8P. Son datos retrospectivos de modelo, no sensores de parcelas; muchas consultas reutilizan el mismo píxel de reanálisis.
- **51 pares de testigos** que satisfacen el filtro preliminar de vecindad 8P (distancia, altura y diferencias climáticas); **45** reutilizan una celda en al menos uno de los modelos y **6** poseen centros diferentes en ambos. Uno de esos seis enlaces cruza un piso altitudinal: **no se fusiona** por ese motivo.
- **Polígono regional referencial simplificado** de la fase 8N; su fuente secundaria no está validada como límite oficial actualizado. El IGN/INEI sigue siendo necesario para delimitar legalmente polígonos, cuencas, distritos o áreas agrícolas.

### Los pisos de muestreo (no clasificaciones normativas nacionales)

| Piso físico experimental | Altitud DEM de un punto | Nodos |
|---|---:|---:|
| Planicie costera | 0–99 m | **161** |
| Valle bajo | 100–299 m | **121** |
| Piedemonte | 300–799 m | **64** |
| Ladera baja | 800–1.599 m | **30** |
| Ladera media | 1.600–2.499 m | **11** |
| Montaña alta | ≥2.500 m | **23** |
| Cota DEM negativa: revisión | Por debajo de 0 m | **10** |
| **Total** | Centros DEM | **420** |

No inferir **proporción del territorio** de la proporción de nodos; el diseño del muestreo es deliberadamente más denso en zonas de pendiente y gradiente.

## 3. Método SIG reproducible y prudente

El motor `modelos/sectores_altitudinales_9k.py` realiza:

1. Leer de forma determinista los 420 centros, 81 perfiles y enlaces climáticos. Validar sus IDs, altitudes y conteos. Calcular SHA-256 de cada tabla y del límite simplificado.
2. Proyectar a **UTM 17S (EPSG:32717)** para calcular distancia y polígonos de Voronoi asociados a los centros DEM. Limitar cada celda al polígono regional referencial y un **radio gráfico máximo de 5,5 km**, para evitar áreas gigantes en la periferia. Reproyectar a WGS84 (GeoJSON) y recortar otra vez para evitar imprecisiones del borde.
3. Vincular tentativamente un punto DEM con un **testigo climático de su mismo piso**, siempre que esté a **12 km o menos** y tenga un desnivel DEM de **180 m o menos**. Cotas ≤5 m no reciben asociación de perfil en este cribado conservador. Sin testigo elegible, queda marcado expresamente **solo_muestreo_altitudinal**.
4. Construir familias de afinidad climática mediante enlaces 8P que consultan **dos celdas ERA5 diferentes y dos celdas ERA5-Land diferentes**, sin sobrepasar los filtros de distancia climática, desnivel y proximidad. Prohibir mezclar pisos físicos; el parecido producido al consultar la misma celda del modelo no cuenta como enlace multicelda.
5. Agrupar y disolver por **piso físico + familia de similitud**, manteniendo partes geográficas desconectadas separadas. Una pieza requiere al menos dos testigos distintos de la familia para marcarse como `hipotesis_nucleo_conectado`; las demás son solo áreas de influencia de la muestra.
6. Publicar geometrías, tablas y metadatos reproducibles mediante pruebas de topología, nodos, fuentes, distancia y prohibición de habilidad predictiva no medida.

**Importante:** unir polígonos a partir del muestreo es un instrumento de visualización y planificación; **no** es un mapa ráster de pisos altitudinales absolutos de cada píxel, delimitación de cuencas, ni conclusión de homogeneidad de toda la superficie incluida.

### Resultado SIG real de 9K

- **42 piezas cartográficas experimentales**, con registro GeoJSON individual de ID S001–S042, piso, testigos próximos y condición científica.
- **286 nodos** logran asociarse a un testigo climático cercano y del mismo piso, pero **134 nodos permanecen sin testigo elegible**; no se imputa clima a ellos.
- **Tres familias exploratorias de enlaces climáticos entre celdas diferentes**. Solo **5 enlaces** están dentro de su mismo piso físico: las tres familias nunca se fusionan a través de un umbral altitudinal.
- **Tres piezas** cumplen adicionalmente el rótulo gráfico de `hipotesis_nucleo_conectado`; no demuestra continuidad meteorológica en todas sus hectáreas.

| Familia | Piso del DEM | Testigos climáticos ya descargados | Enlaces de dos celdas diferentes |
|---|---|---|---:|
| C01 | 300–799 m (piedemonte) | M0163, M0224 | 1 |
| C02 | ≥2.500 m (montaña alta) | M0234, M0282, M0308 | 2 |
| C03 | 1.600–2.499 m (ladera media) | M0280, M0288, M0333 | 2 |

Cada familia es una hipótesis **interna a un piso** que conviene estudiar con un DEM continuo, transectos y estaciones reales. La 8Q ya mostró que dos extremos montañosos climáticamente parecidos pueden esconder cambios abruptos entre ellos: esta limitación sigue vigente.

**No se han certificado zonas homogéneas (0), parcelas agrícolas (0), microclimas para arándano/vid (0), ni modelos predictivos por polígono (0).**

## 4. Integración genuina de NOAA NMME estacional

Fuente primaria oficial: [NOAA/CPC — NMME](https://www.cpc.ncep.noaa.gov/products/NMME/data.html), [guía del sistema](https://www.cpc.ncep.noaa.gov/products/NMME/users_guide.html). Se ha recuperado el directorio público de inicialización de **octubre de 2026**, con subcarpeta [ENSMEAN/2026100800](https://ftp.cpc.ncep.noaa.gov/NMME/realtime_anom/ENSMEAN/2026100800/).

Se descargaron, conservaron como **copias NetCDF comprimidas sin alterar sus bytes internos**, comprobaron con SHA-256 y extrajeron sus ejes/dimensiones de dos archivos **NOAA NMME**:

| Archivo | Variable original | Unidades originales | Resolución |
|---|---|---|---|
| `NMME.tmp2m.202610.ENSMEAN.anom.nc` | Anomalía mensual de temperatura media 2 m del conjunto multimodelo | **K** (incremento equivalente numéricamente en °C) | **1° × 1°** |
| `NMME.prate.202610.ENSMEAN.anom.nc` | Anomalía mensual de tasa de precipitación del conjunto multimodelo | **mm/s** (NO mm por mes) | **1° × 1°** |

Ambos contienen variable 3D `target × lat × lon` con **12 posiciones** en el eje temporal, cuyo atributo `months since 1960-01-02 21:00:00` ha sido verificado contra la secuencia 2026-10 a 2027-09. En ambos campos, **octubre 2026 a junio 2027** contienen señales numéricas; **julio–septiembre de 2027** son campos con cero en toda la malla: se consideran **probable relleno y se convierten a ausencia (`null`) en el producto del OAF**, nunca a una predicción de anomalía exactamente cero. Octubre 2026 es intramensual y no se incluye en las predicciones anteriores a inicio del mes.

**Solo se utilizan numéricamente para mostrar una señal atmosférica regional, no para inferir habilidad propia de OAF.** En temperatura, un incremento expresado en K puede presentarse como diferencia en °C. En precipitación se conserva la tasa original en mm/s; si se representa en mm/día, se multiplica explícitamente por **86 400 segundos/día**, sin fingir un acumulado mensual.

### La resolución NOAA impide una diferenciación física directa por pisos

El muestreo sobre cuatro localidades devuelve **solo dos centros de celdas NOAA**:
- Chiclayo: **7° S, 80° O** (en el archivo: lat = −7, lon = 280° E).
- Jayanca, Motupe y Olmos: **6° S, 80° O** (lat = −6, lon = 280° E), la **misma celda en estas tres localidades**.

Estas dos celdas no resuelven las transiciones costeras, piedemontes ni cumbres. Es **científicamente incorrecto** generar «42 pronósticos NMME distintos» a partir de solo dos celdas. Se debe estudiar más adelante una **transferencia jerárquica**: señal oceánica/atmosférica regional + climatología local por altitud, con corrección estadística entrenada solo con datos anteriores al evento y validación espacial y temporal estricta. Ningún ajuste o downscaling fue entrenado aquí.

Las anomalías NOAA pueden usar climatologías propias de los sistemas participantes y **no se han recalculado** a las normales OAF 1996–2025 ni a las comparables OMM 1991–2020. Tampoco deben confundirse con ICEN oficial ENFEN o un pronóstico propio de Niño Costero. No existe todavía MAE, RMSE, fiabilidad de riesgo por piso ni eficacia de una predicción de cultivo, pues los eventos futuros deben verificarse después.

## 5. Entregables reales

- [GeoJSON de 42 sectores experimentales](datos/sectores_agroclimaticos_9k/sectores_muestreo_9k.geojson).
- [Estado SIG y familias de similitud](datos/sectores_agroclimaticos_9k/estado_sectores_9k.json).
- [Inventario de asignaciones de 420 nodos](datos/sectores_agroclimaticos_9k/asignacion_nodos_9k.csv).
- [Inventario NOAA NMME](datos/sectores_agroclimaticos_9k/inventario_nmme_9k.json), con origen, unidad, fecha objetivo, valores numéricos, huellas, ausencias y celdas comunes.
- [Dos NetCDF NOAA preservados comprimidos](datos/sectores_agroclimaticos_9k/fuentes_netcdf_gzip/), sin modificación de datos científicos.
- [Modelo SIG 9K](modelos/sectores_altitudinales_9k.py) y [lector NOAA](modelos/inspeccion_nmme_9k.py), reproducibles y auditables con `--check`.
- [Pruebas de geometría y fuentes](tests/test_sectores_altitudinales_9k.py).
- [Automatización GitHub Actions](.github/workflows/oaf_sectores_nmme_9k.yml) con dependencias de SIG y lectura NetCDF.
- [Mapa público interactivo 9K](modelos/visor_sectores_9k.js) y [estilos](assets/oaf-sectores-9k.css) añadidos a **Análisis de clima regional**. El portal conserva todas las secciones históricas y modelos no vinculados a esta etapa.

## 6. Siguiente etapa recomendada — Fase 9L

Afinar polígonos con **DEM ráster continuo** y topología real de divisorias, vertientes hidrográficas y pendientes; reemplazar el límite regional histórico por IGN/INEI. Calcular climatologías densas e independientes para cada sector y comprobar su estabilidad al variar el tamaño de celda, los criterios de fusión y los años de referencia. Preparar y evaluar un método jerárquico de corrección altitudinal que separe forzamiento NMME de base local sin transferir falsamente una anomalía de 1° a parcelas. Posteriormente, contrastar predicciones realmente emitidas contra estaciones SENAMHI y eventos ENSO validados antes de usar el resultado en decisiones fitosanitarias de arándano y vid.
