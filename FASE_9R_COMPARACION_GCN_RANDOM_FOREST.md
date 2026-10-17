# Fase 9R — Comparación de redes neuronales convolucionales de grafos (GCN) y Random Forest para lluvia regional

**OAF-Lambayeque — 17 de octubre de 2026.** Estudio experimental con datos abiertos reales CHIRPS v3 final 1996–2025. **No es una validación operativa ex ante de pronósticos emitidos en 1997–2025**; los productos de precipitación final y los sectores exploratorios se compilaron retrospectivamente.

## Pregunta científica

¿Predice mejor la lluvia del **mes siguiente** la arquitectura **Graph Convolutional Network (GCN)**, que comparte información entre sectores físicamente relacionados, o el método **Random Forest**, entrenado con datos de los sectores de manera independiente? El mismo ensayo compara ambos con la **climatología mensual de entrenamiento**, para evitar declarar útil una IA que no mejore una regla sencilla. A diferencia de una CNN 1D, una GCN propaga representaciones según los enlaces de un **grafo territorial**.

## Procedencia y serie real

Fuentes: **CHIRPS v3 FINAL mensual**, 360 meses entre 1996-01 y 2025-12; 108 meses en [9O](datos/homogeneidad_9o/fuentes_chirps_9o.json), 12 en [9P](datos/continuidad_9p/fuentes_adicionales_chirps_9p.json) y 240 en [9Q](datos/recuperacion_9q/fuentes_chirps_9q.json). Todos tienen URL de origen y SHA-256 del GeoTIFF. Se utilizan 42 contornos exploratorios de 9K, pero el entrenamiento excluye los sectores sin **360 valores mensuales CHIRPS terrestres válidos**. No se imputan las tres áreas sin píxeles propios.

**CHIRPS v3 NO es una red de 39 pluviómetros independientes**: combina satélites y observaciones de estaciones, con autocorrelación espacial y posible dependencia de datos incorporados al propio producto. Referencia: [CHC/UCSB, CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3).

## Diseño experimental y separación estricta de años

| Uso | Periodo | Meses disponibles |
|---|---|---:|
| Entrenamiento de modelos y climatología mensual | **1997-01 a 2015-12** | **228** |
| Selección de parámetros y parada de entrenamiento | **2016-01 a 2020-12** | **60** |
| Evaluación final reservada | **2021-01 a 2025-12** | **60** |

1996 se conserva íntegro como año antecedente para disponer de rezagos de **12 meses** al inicio de 1997. Los meses de prueba no participan en el ajuste de normalización, climatología ni selección de hiperparámetros. Para predecir el objetivo mensual `t` se proporcionan solo las lluvias de **t-1, t-2, t-3, t-6 y t-12**, el promedio de los tres meses anteriores, seno y coseno del mes objetivo, y las coordenadas/altitud **físicas estáticas** del sector. No entran variables meteorológicas contemporáneas del propio mes objetivo, ni normales retrospectivas 1996–2025 como predictores (pues introducirían información del periodo de prueba). No se usa el resultado de la agrupación 9Q para construir las conexiones del grafo, porque esas agrupaciones sí fueron inferidas a partir de la totalidad de los datos históricos.

**Límite temporal imprescindible:** en fechas históricas reales, la edición CHIRPS v3 final del mes `t-1` puede no haber existido cuando se hubiera emitido un pronóstico para el mes `t`. El ensayo reconstruye condiciones con productos finales actuales; **no certifica un archivo de vintage as-issued** ni habilidad operativa 2026. Igualmente, los contornos físicos 9K fueron generados después del periodo de prueba, lo que implica un componente espacial retrospectivo. Estas limitaciones impiden proclamar una predicción prospectiva comprobada aunque el corte temporal de entrenamiento sea estricto.

## Topología del grafo, evitando fugas de precipitación

Los nodos son sectores con historia completa de CHIRPS y las aristas están predeterminadas únicamente por:

- La misma banda altitudinal física preliminar (no piso ecológico legal).
- Intersección de un código hidrográfico de la capa **ANA/IDEP referencial**.
- Distancia entre polígonos ≤ **0,14 grados** en coordenadas geográficas (aproximación para el grafo, no métrica legal).
- Se excluye la cota DEM negativa de enlazado.
- Autoenlaces y normalización simétrica de matriz de adyacencia `D^-1/2 (A+I) D^-1/2`.

La topología **no usa** correlaciones CHIRPS ni datos del periodo de prueba para crear enlaces. No se calculan coordenadas oficiales de microcuencas ni se certifica su vigencia.

## Modelos y comparación

**Random Forest:** `RandomForestRegressor` de scikit-learn, 240 árboles, profundidad máxima 15, `max_features=0.85`, `random_state=20261017` y elección del tamaño mínimo de hoja entre 3 y 8 a partir del error en la validación 2016–2020. Recibe las mismas once variables por muestra que la GCN, sin matriz de aristas.

**GCN:** red PyTorch con dos transformaciones convolucionales espaciales sobre la matriz de adyacencia normalizada, conexión residual de variables del nodo, 40 neuronas ocultas, *dropout* 0,13, AdamW y pérdida Huber sobre `log1p(lluvia)`. Selecciona la mejor época hasta un máximo de 180 mediante validación 2016–2020 y parada temprana de 25 épocas sin mejora. No requiere PyTorch Geometric porque la convolución de Kipf y Welling se implementa explícitamente mediante multiplicación matriz-vecindad y capas neuronales. Referencia: [Kipf y Welling (ICLR 2017)](https://arxiv.org/abs/1609.02907).

**Climatología histórica:** media de la lluvia por sector y mes calendario, estimada **solo con 1997–2015**. Es el control contra el cual se comparan ambos modelos.

En todas las evaluaciones las predicciones se transforman a mm y se restringen a valores no negativos. **Indicadores:** MAE (menor es mejor), RMSE (penaliza errores graves), sesgo, mejora porcentual de MAE frente a climatología, precisión/exhaustividad/F1 de anomalías altas (sobre el percentil 80 de lluvia por sector y mes, calculado únicamente con el periodo de entrenamiento), y métricas de 2021, 2022, 2023, 2024 y 2025 por separado.

Además se publican los errores por **piso altitudinal preliminar**, por las **siete agrupaciones propuestas en 9Q**, y la sensibilidad del diferencial de MAE al excluir uno de los cinco años de prueba cada vez. Los grupos 9Q sirven solamente para presentar resultados después de entrenar: **no intervienen como características ni aristas del modelo**.

## Evidencia cuantitativa y trazabilidad

Resultados generados mediante el workflow y los modelos incluidos en este repositorio:

- [Métricas GCN vs Random Forest vs climatología y cortes por piso](datos/validacion_predictiva_9r/comparacion_modelos_9r.json).
- [Predicciones mensuales 2021–2025 junto a CHIRPS observado](datos/validacion_predictiva_9r/predicciones_prueba_2021_2025_9r.csv).
- [Código entrenable con fuente CHIRPS y grafo estático](modelos/comparacion_gcn_rf_9r.py).
- [Pruebas de ventanas temporales, física, métricas y navegación](tests/test_comparacion_gcn_rf_9r.py).
- [Workflow CI de cálculo de modelos y evidencias](.github/workflows/oaf_prediccion_gcn_rf_9r.yml).
- [Dashboard interactivo](modelos/visor_comparacion_9r.js) en **Análisis de clima regional**.

La ventaja o desventaja de un modelo solamente se confirma después de publicar valores de prueba reales; jamás se presupone que una GCN superará a Random Forest. El baseline también puede superar a ambos.

## Resultados reales obtenidos con datos CHIRPS (auditoría 9R)

Se entrenaron ambos modelos sobre **39 de los 42 sectores** (S028, S032 y S034 no disponen de 360 valores sectoriales CHIRPS válidos), con **46 aristas físicas estáticas** en la GCN. El conjunto de prueba es **2021-01 a 2025-12**: 60 meses × 39 sectores = **2340 predicciones sector-mes** comparables. La métrica de referencia es el **MAE en mm mensuales (menor es mejor)**.

| Método | MAE (mm) | RMSE (mm) | Sesgo medio (mm) | Skill MAE vs climatología |
|---|---:|---:|---:|---:|
| **Climatología mensual del entrenamiento** | **14,2957** | **30,6393** | −0,0589 | 0 % |
| **Random Forest** | **15,5397** | **34,3094** | −8,4337 | **−8,702 %** |
| **GCN de dos capas** | **18,4682** | **39,6384** | −6,2141 | **−29,187 %** |

**Ganador entre los dos métodos de IA: Random Forest. Ganador general: la climatología mensual histórica.** La GCN obtuvo MAE aproximadamente **2,93 mm** más alto que Random Forest. Esto NO permite concluir que todas las arquitecturas GCN sean peores en cualquier periodo o con mejores predictores; sólo aplica al protocolo preespecificado y las fuentes disponibles.

### Desagregación por pisos físicos preliminares

| Piso de 9K | N.º sectores | Climatología MAE | Random Forest MAE | GCN MAE |
|---|---:|---:|---:|---:|
| Costa baja, 0–99 m | 4 | 5,1239 | **3,9605** | 4,8934 |
| Valle bajo, 100–299 m | 6 | **9,7580** | 9,8810 | 12,3506 |
| Piedemonte, 300–799 m | 11 | **12,5809** | 13,0466 | 15,5825 |
| Ladera baja, 800–1599 m | 6 | **12,1502** | 13,7201 | 15,6958 |
| Ladera media, 1600–2499 m | 8 | **21,8805** | 24,3652 | 30,9741 |
| Montaña alta, ≥2500 m | 3 | **29,0929** | 35,4076 | 36,1313 |
| Cota DEM negativa: revisar | 1 | 4,8734 | **3,9435** | 4,8139 |

**Interpretación:** la climatología sigue siendo el menor error en cinco de las seis franjas principales, especialmente en montaña. En costa baja Random Forest logra menor MAE. El sector de cota negativa no debe asignarse directamente a un ecosistema productivo ni considerarse validación agrícola.

### Sensibilidad entre años y precipitación excepcionalmente alta

| Año de prueba | Climatología MAE | Random Forest MAE | GCN MAE |
|---|---:|---:|---:|
| 2021 | **11,5963** | 13,1004 | 20,2167 |
| 2022 | **12,1021** | 12,3926 | 14,8172 |
| 2023 | **24,8143** | 30,9409 | 32,3255 |
| 2024 | 15,7262 | **10,0285** | 12,1702 |
| 2025 | **7,2394** | 11,2362 | 12,8114 |

En 2023 todos los métodos fueron considerablemente menos precisos; el RF subestimó precipitación en promedio (**sesgo −23,976 mm/mes**) y la GCN también (**−22,621 mm/mes**). Los modelos NO deben usarse todavía para alarmas tempranas de extremos.

Se definieron meses de lluvia anormalmente alta mediante el **percentil 80 por sector y mes calendario exclusivamente en el entrenamiento**. En las 2340 combinaciones sector-mes hubo **688 casos positivos**. El RF identificó correctamente **157** (precisión **0,4337**, exhaustividad **0,2282**, F1 **0,2990**). La GCN detectó **109** (precisión **0,2839**, exhaustividad **0,1584**, F1 **0,2034**). La climatología detectó **167** (precisión **0,3443**, exhaustividad **0,2427**, F1 **0,2847**). Ningún modelo tiene rendimiento suficientemente confiable para avisos de riesgo a nivel de productor.

Los resultados y la desagregación por las **siete parejas cartográficas 9Q** están en [comparacion_modelos_9r.json](datos/validacion_predictiva_9r/comparacion_modelos_9r.json), junto con la serie de predicciones [2021–2025](datos/validacion_predictiva_9r/predicciones_prueba_2021_2025_9r.csv).

### Implicación para el desarrollo del OAF

En lugar de reemplazar la climatología por una IA sin ventaja robusta, **mantener el baseline climático como método de referencia**. El próximo experimento debería enriquecer Random Forest y la GCN con señales realmente disponibles antes del mes de pronóstico: índices oceánicos ENSO publicados con fecha, temperaturas previas, humedad y radiación anteriores, topografía/exposición de laderas y estado del suelo, además de corregir la dependencia por píxeles y sesgos de precipitación extrema. Para comparar arquitecturas en términos de generalización se necesitan más bloques históricos fuera de muestra, evaluación por evento y estaciones meteorológicas independientes. No publicar un pronóstico 2026 como verificado utilizando retrospectivamente CHIRPS final de los años 2021–2025.

## Limitaciones para la futura predicción agroclimática y fitosanitaria

El resultado mide acierto al **reconstruir lluvia CHIRPS v3 final** desde meses retrospectivos anteriores, no al predecir pluviómetros independientes de Lambayeque. La asociación espacial entre nodos puede reforzar errores satelitales compartidos; tampoco demuestra por sí sola que dos sectores sean microclimáticamente homogéneos. El estudio aún no utiliza señales futuras verificadas de **ENFEN, océano Niño 1+2, presión, humedad y radiación atmosférica** como pronósticos emitidos antes de su fecha de validez. Estas podrían añadirse solamente con fechas de emisión y un protocolo de validación prospectiva.

No se derivan alertas de enfermedades de **arándano** o **vid** sin registros de campo, fenología y condiciones favorables respaldadas científicamente. **0 zonas oficialmente certificadas**, **0 pronósticos ex ante institucionalmente validados** y **0 alertas fitosanitarias nuevas** resultan de esta fase.

## Siguiente fase: 9S

Profundizar la comparación del mejor modelo frente a los extremos asociados a **El Niño Costero**, evaluar errores por subcuenca y elevación en años atípicos, e incorporar variables predictoras oceánicas atmosféricas que estuvieran realmente disponibles *antes del mes pronosticado*. Contrastar contra estaciones SENAMHI con identidades y periodos confirmados. Para uso real, congelar las emisiones de pronósticos e iniciar verificación prospectiva con latencia de los datos observados.

**Lema:** Datos abiertos y ciencia climática al servicio del campo.
