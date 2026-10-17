# Fase 9M — Sensibilidad de sectores agroclimáticos y agrupación por unidades hidrográficas

**OAF-Lambayeque — 17 de octubre de 2026.** Trabajo reproducible de cartografía, **no zonificación validada de parcelas ni habilidad de predicción demostrada**.

## 1. Pregunta científica y cobertura

Las fases 9K y 9L construyeron 42 sectores cartográficos de muestreo y comprobaron la continuidad de 5 sectores prioritarios, respectivamente. Se necesitaba examinar cuánto cambia cada límite cuando varían la pendiente y la resolución del DEM, y cruzar los sectores con una fuente institucional de cuencas para no unir indebidamente laderas de unidades de drenaje diferentes.

**9M evalúa 42 sectores en su inventario, pero el análisis de pendiente y exposición llega a 35**: 26 con cobertura completa y 9 parcial dentro de **UNA** tesela Copernicus GLO-90 S07 W080 (lat -7 a -6°, lon -80 a -79°). Los **7 restantes están fuera de esa tesela**. La capa hidrográfica, distinta del raster, cubre los 42 sectores de 9K. Nunca fusionar estas dos coberturas y afirmar que se examinó el relieve de toda Lambayeque.

### Distribución por estrato entre los 35 evaluados

| Estrato DEM del nodo | Sectores con análisis 9M |
|---|---:|
| Planicie muy baja 0–99 m | 1 |
| Valle 100–299 m | 6 |
| Piedemonte 300–799 m | 11 |
| Ladera baja 800–1599 m | 6 |
| Ladera media 1600–2499 m | 8 |
| Montaña alta ≥2500 m | 3 |
| **Total** | **35** |

Los puntos DEM negativos y los sectores no cubiertos no reciben diagnóstico físico extrapolado.

## 2. Comparación real de relieve, pendientes y orientación

Fuente: **Copernicus DEM GLO-90 DSM** archivado íntegramente en 9L. Se mantiene SHA-256 original `c4d78e481f80927d72886787e422ed02214ffb0d5739e67a25facd2c874f7532`; no se generan alturas sintéticas. Es un **Digital Surface Model**, que puede incluir vegetación e infraestructura. [Ficha Copernicus](https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM); [estructura de teselas](https://copernicus-dem-90m.s3.amazonaws.com/readme.html).

Para cada polígono, el motor:
1. Calcula **qué fracción del polígono está dentro de la tesela**, marcando `completa`, `parcial` o `fuera_de_tesela`.
2. Lee elevación válida por píxel con escalas de agregado **3× (~270 m)** y **5× (~450 m)**, conservando la clase física del píxel, no solo la altura de un único punto.
3. Deriva pendiente local de gradientes del DSM; compara umbrales **≤20°, ≤30° y ≤40°**. Son parámetros de *sensibilidad*, no recomendaciones agrícolas, ni umbrales normativos.
4. Calcula **orientación de descenso de la superficie (aspect)** y la resume en N/E/S/O, excluyendo laderas casi planas (pendiente inferior a 2°). La orientación **no mide viento, radiación, humedad o dirección real de escorrentía en una red hidrográfica**.
5. Poligoniza los píxeles que coinciden con el piso y pendiente ≤30° a ~270 m y los recorta al contorno experimental 9K.
6. Conserva resultado tabular para los 42 sectores, incluidos explícitamente los 7 sin cobertura, sin rellenar ausencias.

### ¿Son estables los límites ante un cambio de resolución?

La diferencia absoluta entre fracciones de píxeles aceptados con pendiente ≤30° entre las resoluciones ~270 m y ~450 m es:

| Estadístico | Diferencia de fracción | En puntos porcentuales |
|---|---:|---:|
| Mínimo entre sectores examinados | **0,00054** | **0,054 p.p.** |
| Mediana entre sectores examinados | **0,01915** | **1,915 p.p.** |
| Máximo entre sectores examinados | **0,17957** | **17,957 p.p.** |

**Interpretación:** una mediana pequeña no garantiza estabilidad de todos los polígonos: existe al menos un sector muy sensible a la resolución. Estos valores son descriptivos de la **máscara de relieve**, no errores de temperatura o precipitación ni estabilidad real de microclimas.

Hay sectores con asignación de piso poco representativa de su superficie raster. Por ejemplo, S009 y S010 pertenecen nominalmente a `montana_baja` (800–1599 m), pero dentro de la tesela presentan cotas medianas continuas aproximadas de **467,74 y 470,66 m**, y fracciones aceptadas de apenas **17,70 % y 13,42 %** en el filtro nominal de ≤30°. Esa discrepancia obliga a **revisar la clasificación por nodo y subdividir según DEM continuo** antes de agruparlos como montaña baja. No representa una falla o corrección instrumental medida en terreno.

## 3. Fuente de unidades hidrográficas ANA/IDEP comprobada

La consulta anterior a un servidor de Vivienda (9L) había fallado por DNS. Para 9M se identificó y descargó un recurso **realmente existente**, publicado por el geoportal institucional IDEP:

**[INSTITUCIONALES / ANA_WMS / FeatureServer / 7 — Unidades Hidrográficas](https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/FeatureServer/7)**. El servicio documenta `NIVEL1` a `NIVEL7`, `CODIGO`, `NOMBRE`, y acepta salida GeoJSON. La descarga se restringió a la envolvente departamental de la malla de estudio y se guardó comprimida con el JSON exacto.

- **17 geometrías institucionales devueltas** en la envolvente de consulta.
- **91 intersecciones** con los 42 polígonos originales 9K (umbral de cruce >0,01 km²).
- **42/42 sectores 9K** intersectan al menos una geometría del servicio.
- Ejemplos presentes en las intersecciones: **Cuenca Olmos**, **Cuenca Motupe**, **Cuenca Chancay-Lambayeque**, intercuencas numeradas y otras unidades de distintos niveles.
- SHA-256 de respuesta original: `ed20eddd32f4ec945dd1dbc792134cfcaca28dededde693eb60b7f4e73320867`.
- El programa comprueba que las unidades tengan geometría, identificador e intersección relevante; si el servidor no funciona se publica estado de **no disponibilidad**, no ausencia de cuencas.

**Importante:** una capa recuperada en IDEP atribuida a ANA **no equivale a cotejo independiente de vigencia legal, escala, límites ni coincidencia de predios**. El OAF mantiene **0 cuencas operativamente certificadas**; la cartografía es una capa institucional *de referencia* cuya versión se debe corroborar.

## 4. Agrupación física explícita: piso + código de unidad + familia climática

El módulo `agrupar_hidrofisicos_9m.py` cruza las intersecciones de ANA/IDEP con la clase altitudinal y, si existe, el núcleo climático previo **C01, C02 o C03**. Se agrupa y disuelve únicamente cuando coincide la clase y el código hidrográfico, sin unir partes no contiguas.

Para no contar dos veces superficies de niveles jerárquicos superpuestos, el procedimiento **prioriza códigos hidrográficos más específicos** (longitud del identificador) y sustrae el área ya atribuida dentro del sector. Ese criterio es **metodológico y de visualización**, no representa una decisión normativa de jerarquía de cuencas. Se publican grupos de planificación sin atribuir a ellos uniformidad de lluvia, temperatura o incidencia fitosanitaria.

Resultados de la ejecución de agrupación:

- **107 fragmentos hidrofísicos exploratorios**, con procedencia, piso, código, superficie aproximada y sectores originales.
- **2 fragmentos** están conectados a piezas de **dos o más sectores 9K**; los otros no acreditan fusión de zonas completas.
- **0 zonas climáticas homogéneas validadas**, **0 cuencas operativas certificadas** y **0 predicciones zonales con habilidad demostrada**.

La agrupación puede mostrar *fragmentación*, no necesariamente reducción del número de polígonos: 42 sectores originales cruzados por límites de cuenca generan más fragmentos. Este es un resultado científico legítimo, no un fracaso del algoritmo.

## 5. Transparencia, reproducciones y descargas

- [Informe de sensibilidad real y coberturas](datos/sensibilidad_9m/estado_relieve_9m.json).
- [42 filas con estabilidad por sector](datos/sensibilidad_9m/sensibilidad_42_sectores_9m.csv).
- [Máscaras de polígonos sobre la tesela del DEM](datos/sensibilidad_9m/sectores_filtrados_tesela_9m.geojson).
- [Estado de adquisición de ANA/IDEP](datos/sensibilidad_9m/estado_cuencas_ana_9m.json).
- [Archivo fuente original ANA comprimido](datos/sensibilidad_9m/fuentes/idep_ana_unidades_hidrograficas_9m.geojson.gz).
- [Intersecciones de ANA con sectores 9K](datos/sensibilidad_9m/cruces_hidrograficos_9m.geojson).
- [Mapa de agrupaciones por piso y código](datos/sensibilidad_9m/grupos_hidrofisicos_9m.geojson) y [metadatos](datos/sensibilidad_9m/estado_grupos_9m.json).
- [Modelo físico y sensibilidad](modelos/sensibilidad_relieve_9m.py), [lector ANA](modelos/zonas_hidrograficas_9m.py), [agrupación con desduplicación](modelos/agrupar_hidrofisicos_9m.py).
- [Workflow automatizado](.github/workflows/oaf_zonas_9m.yml) y [tests SIG](tests/test_zonas_9m.py), [tests de agrupación](tests/test_agrupacion_9m.py).
- [Mapa y tablas interactivos](modelos/visor_zonas_9m.js) integrados en **Análisis de clima regional**.

Las capas 8O–9L, los originales de ERA5, ERA5-Land, GLO-90, CHIRPS y NOAA NMME, y las cinco rutas permanecen intactos.

## 6. Qué se necesita antes de pronósticos zonales

El objetivo final es predecir anomalías por unidades razonablemente similares sin mezclar costa con alta montaña ni cuencas con drenajes diferentes. Faltan:

- Las **otras teselas DEM GLO-90** necesarias para cubrir los 7 sectores excluidos y porciones faltantes de los 9 parcialmente cubiertos, con teselas y SHA verificables. No existen resultados físicos fuera de S07 W080 en 9M.
- Evaluar consistencia espacial a resolución más fina y calidad del DSM, elevación, pendiente, orientación, vertientes y drenajes; verificar la capa institucional con ANA/IGN/INEI y contrastar índices de cuenca de distintas jerarquías.
- Recalcular y contrastar perfiles climáticos 1996–2025 por subregión realmente delimitada, comprobar estabilidad ante cambios de pesos/umbral y **validar con estaciones instrumentales independientes**.
- Diseñar transferencia de la señal NMME de 1° a zonas (si ofrece habilidad y existe calibración estadística externa), siempre congelando fecha de emisión, horizonte y comparación fuera de muestra.
- Solo después incorporar evidencia de fenología y presencia de enfermedades de vid y arándano para convertir señales meteorológicas verificadas en vigilancia fitosanitaria fiable.

**Siguiente fase 9N:** cerrar cobertura DEM multipieza y revisar la agrupación hidro-altitudinal con datos de precipitación de resolución adecuada y contraste instrumental independiente. No activar avisos agronómicos basados en grupos cartográficos preliminares.
