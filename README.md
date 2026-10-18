# OAF-Lambayeque 2.0
### Observatorio Agroclimático y Fitosanitario de Lambayeque, Perú

**Autor:** ING. AGRÓNOMO CARLOS ENRIQUE CORONEL GARCÍA  
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/















## Fase 10M · Incorporación de pluviómetros SENAMHI (17/10/2026)

**Integración efectiva a la base observacional del OAF.** Se examinaron **2.956 registros** (1.441 anteriores y 1.515 de **50 nuevos CSV**: 32 de Cueva Blanca, 18 de Incahuasi). Se identificaron **303 claves repetidas** con **362 copias extras idénticas**, **cero contradicciones de precipitación** y quedaron **2.594 observaciones únicas** (**1.386 diarias + 1.208 horarias**) de 13 estaciones.

**Montaña:** Cueva Blanca (3.300 m) ofrece **26 meses completos** entre oct-2021 y sep-2026, e Incahuasi (3.052 m) **14 meses completos** entre feb-2024 y may-2026. **No son series mensuales continuas**. Se auditaron completos por día; los archivos declaran **«Datos sin control de calidad»**. No se ha comprobado su independencia frente a CHIRPS ni su autenticidad directamente desde SENAMHI. Por ello **aún no se introducen al entrenamiento RF ni se anuncian predicciones operativas**.

La **base diaria, horaria, CSV originales con huellas SHA-256, auditoría Excel y protocolo de importación** se almacenó en la **biblioteca personal persistente** bajo `/OAF-Lambayeque/SENAMHI/`. El repositorio incluye una **tabla pública de 48 meses-estación (43 completos)** y un manifiesto con los SHA-256 de los 50 CSV para futura georreferenciación/QC. No imputar meses ausentes ni convertir `T` o `S/D` en cero.

[**Panel de pluviómetros y meses observados**](observaciones-senamhi-10m.html) · [Informe 10M](FASE_10M_INTEGRACION_SENAMHI.md) · [CSV mensual para dashboard](datos/senamhi_estaciones_10m/resumen_mensual_senamhi_observado.csv) · [Manifiesto fuente SHA y auditoría](datos/senamhi_estaciones_10m/manifest_fuentes_10m.json) · [Verificador de integridad](modelos/auditar_integracion_senamhi_10m.py) · [Control automatizado](.github/workflows/oaf_10m_senamhi_fuentes.yml).

## Fase 10L · Mejora de las lluvias en vertientes medias y altas (17/10/2026)

La fase 10L se ejecutó sobre **11 sectores montañosos del OAF** (8 de vertientes medias y 3 de alturas), con **660 observaciones sector-mes de 2021–2025**, confrontadas directamente con el modelo Random Forest geográfico 10K y la climatología mensual de cada sector.

Se ensayaron **seis opciones RF**: aprendizaje regional ponderado por altitud, especialistas de montaña, objetivos de anomalía logarítmica/normalizada, y un brazo completo con variables oceánicas NOAA y atmosféricas NASA POWER, siempre con rezago mínimo de dos meses; se añadieron climatología, dispersión histórica, relieve y altitud DEM preliminar como características fijas. **Entrenamiento 1997–2015, selección exclusiva 2016–2018, calibración 2019–2020 y evaluación retrospectiva 2021–2025**. Las geometrías representan paisajes experimentales 9K, no polígonos oficiales de ecorregiones MINAM.

| Paisaje | MAE RF fase 10K | MAE estrategia 10L | MAE climatología |
|---|---:|---:|---:|
| Vertientes medias, 8 sectores | 33,3271 mm | **23,4626 mm** | **21,8805 mm** |
| Cumbres altas, 3 sectores | 52,2841 mm | **29,0930 mm** | **29,0930 mm** |
| **Montaña total** | 38,4972 mm | **24,9982 mm** | **23,8475 mm** |

**Interpretación obligatoria:** la reducción del MAE en las vertientes medias procede de variantes RF seleccionadas con validación temporal, aunque climatología todavía es superior. En **alta montaña los tres sectores pertenecen al mismo bloque espacial de prueba**: sin muestras independientes de cumbres para entrenar, la fase implementó **una abstención automática y uso de climatología**, que explica la caída de 52,28 a 29,09 mm. **No se ha validado un nuevo especialista Random Forest para cumbres**. En 2023 la estrategia todavía subestimó la lluvia media de montaña en **27,11 mm/mes**, con MAE 38,48 mm (climatología 36,79 mm). No declarar predicciones operativas, lluvias horarias intensas ni alertas de ENSO; tampoco se entrenaron modelos de enfermedades.

[**Dashboard de lluvia en vertientes medias y altas**](optimizacion-lluvia-montana-10l.html) · [Informe científico 10L](FASE_10L_OPTIMIZACION_MONTANAS.md) · [RF Python de alta montaña](modelos/optimizacion_montana_rf_10l.py) · [Evaluación por franja/año/sector](datos/montanas_10l/evaluacion_montanas_10l.json) · [CSV 660 pares de prueba](datos/montanas_10l/predicciones_lluvia_montanas_10l.csv) · [Mapa altitudinal GeoJSON](datos/montanas_10l/sectores_mejora_montana_10l.geojson) · [Entrenamiento y ocho tests exitosos](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39095822082) · [Auditoría de mapa y MAE](.github/workflows/oaf_10l_auditoria.yml).

## Fase 10K · Ecorregiones experimentales, Random Forest y dashboard cartográfico (17/10/2026)

**Fase ejecutada con ocho pruebas exitosas** y **4.680 estimaciones retrospectivas** de lluvia mensual en 39 sectores. Se definieron **cinco paisajes ecoclimáticos operativos**, como agrupación trazable de los **siete pisos altitudinales experimentales 9K**: costa árida/valles (11 sectores), piedemonte/transición bosque seco (11), vertientes bajas (6), medias (8) y cumbres altas (3). **Estos polígonos NO son ecorregiones oficialmente delimitadas por MINAM**: requieren futura homologación con su [Mapa Nacional de Ecosistemas del Perú](https://www.gob.pe/institucion/minam/informes-publicaciones/277146-mapa-nacional-de-ecosistemas-del-peru).

Se reentrenaron **solo Random Forest** con variables de lluvia/localización del paisaje frente a lluvia+océano+NASA+paisaje, usando cinco bloques CHIRPS, entrenamiento 1997–2015, selección 2016–2018, calibración 2019–2020 y prueba 2021–2025. Para mm, P90 y P95 los cinco pliegues seleccionaron la opción RF lluvia + ecopaisaje (sin imponer innecesariamente otros factores). **MAE RF global 20,4298 mm** (mejora respecto a 10J: 21,0716), pero climatología logra **14,2957 mm**. Brier P90 RF **0,061688** vs clima **0,062884** y P95 RF **0,046705** vs clima **0,046996**: mejoras pequeñas no acreditan habilidad operativa.

**El año 2023** tuvo 107 eventos sector-mes ≥P90; lluvia media observada 42,946 mm frente a 29,993 mm estimados con RF, **sesgo de −12,954 mm**, MAE RF 28,8097 vs clima 24,8143 mm y banda de incertidumbre 90 % que cubrió solo **81,20 %**. En alta montaña el MAE RF fue **52,28 mm** frente a 29,09 climatológico, por lo que la discriminación geográfica es clave.

[**Dashboard interactivo de ecorregiones y predicción de lluvias**](ecorregiones-clima-10k.html) ofrece **mapa Leaflet de 39 polígonos**, filtros de cinco paisajes, periodo, color de lluvia observada/estimada/error/eventos P90, selección sectorial, serie mensual y cuadro resumen por paisaje y piso. Los mapas son experimentales y muestran evaluación histórica, **NO pronóstico de 2026** ni alerta por El Niño costero. [Informe científico](FASE_10K_ECOPAISAJES_RF.md) · [Informe JSON por paisaje](datos/ecopaisajes_10k/evaluacion_ecoclimatica_10k.json) · [Capa GeoJSON](datos/ecopaisajes_10k/paisajes_ecoclimaticos_10k.geojson) · [Series JSON](datos/ecopaisajes_10k/series_sector_mes_10k.json) · [Código entrenamiento](modelos/rf_ecopaisajes_10k.py) · [Pruebas](tests/test_rf_ecopaisajes_10k.py) · [CI 10K exitosa](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39094686704).

## Fase 10J · RF conservador para precipitación y extremos P90/P95 con automejora (17/10/2026)

**Nuevo entrenamiento ejecutado y verificado:** cinco pliegues espaciales, **39 sectores × 60 meses = 2.340 casos históricos**, cuatro familias de covariables, **9.360 filas de estimaciones**. Objetivos únicos: **lluvia mensual (mm)**, **probabilidad de lluvia elevada ≥P90 local** y **probabilidad de lluvia excepcional ≥P95 local**. Se utilizan únicamente modelos **Random Forest**; las futuras enfermedades de cultivos se analizarán de forma separada con observaciones reales de campo, sin usar este modelo como clasificador de patógenos.

La nueva arquitectura usa **climatología de 1997–2015 como referencia** y RF como corrector cuyo peso puede ser cero si empeora la validación. Se fijan hiperparámetros y ponderaciones solo con 2016–2018, se construyen bandas empíricas con 2019–2020 y se evalúa retrospectivamente en 2021–2025. Las series atmosféricas NASA POWER/NOAA y precipitación CHIRPS incluyen revisiones y no constituyen datos originales *as-issued*. Los cinco bloques CHIRPS tampoco representan validación independiente de las celdas meteorológicas NASA compartidas.

**Resultados de la selección fijada en validación (misma familia lluvia histórica en los cinco pliegues):**

| Indicador | RF (10J) | Climatología |
|---|---:|---:|
| MAE lluvia mensual mm, menor mejor | 21,07159 | **14,29568** |
| Brier ≥P90, menor mejor | **0,0628431** | 0,0628840 |
| Brier ≥P95, menor mejor | 0,0471307 | **0,0469958** |

La mejora del Brier P90 es **muy pequeña** y no prueba superioridad robusta. Las bandas empíricas al 90 % tuvieron **86,75 %** de cobertura total y **80,77 %** en 2023 (no cumplen cobertura nominal en ese año). El RF de mm tiene un MAE superior a climatología. En consecuencia **no hay pronósticos operativos ni alertas activadas** y el proyecto publica el benchmark como investigación transparente.

**Automejora futura:** [GitHub Actions mensual](.github/workflows/oaf_10j_automejora.yml) revisa cada día 26 si existen nuevos archivos CHIRPS v3 Final completos por 39 sectores en `datos/nuevos_meses_chirps_10j/`. Si los hay, [genera un RF candidato](modelos/actualizacion_automatica_rf_10j.py) con trazabilidad, prueba retrospectiva reciente si se dispone de 12 o más meses nuevos y almacena el modelo internamente. **Sin nuevos datos no reentrena ni inventa valores**; sin covariables actualizadas de NASA/NOAA la versión futura identifica explícitamente su entrada como solo lluvia. Ningún candidato se promueve automáticamente a avisos públicos: se requieren pronósticos archivados antes del evento, estaciones independientes y revisión científica.

[**Visor sectorial nuevo**](evaluacion-rf-lluvias-10j.html) · [Informe metodológico](FASE_10J_RF_PRECIPITACION_EXTREMOS_AUTOMEJORA.md) · [Código de RF mm/P90/P95](modelos/rf_lluvia_extremos_10j.py) · [Evaluación JSON real](datos/rf_robusto_10j/auditoria_y_seleccion_10j.json) · [CSV de 9.360 estimaciones](datos/rf_robusto_10j/predicciones_rf_tres_objetivos_10j.csv) · [Estado de publicación](datos/rf_robusto_10j/estado_publicacion_10j.json) · [Fuente adicional de incertidumbre](datos/rf_robusto_10j/comparacion_pareada_incertidumbre_10j.json) · [CI de entrenamiento exitosa](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39092829210) · [CI de automejora exitosa (sin nuevos meses aún)](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39093176254) · [Modelo candidato RF exportado con SHA](datos/rf_robusto_10j/manifest_modelo_candidato_10j.json) · [Artefacto entrenado e inferencia verificada](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39093778424) · [Métricas y bandas de incertidumbre pareadas](datos/rf_robusto_10j/comparacion_pareada_incertidumbre_10j.json).

## Fase 10I · Random Forest exclusivo para precipitaciones, sin enfermedades (17/10/2026)

**Entrenamiento comprobado de un único algoritmo predictivo: Random Forest.** RF tiene dos tareas meteorológicas: predicción de **lluvia mensual CHIRPS en mm** y probabilidad de que el mes supere el **P90 de lluvia histórico del sector**. No predice infecciones ni enfermedades. El módulo de consulta futura de horas de humedad necesita series horarias; la lluvia mensual no determina cuánto tiempo está mojada la hoja.

Cuatro grupos físicos de predictores con rezagos t−2+: lluvia CHIRPS histórica, NOAA SST Niño 1+2/3.4, SOI, alisios y viento marino regional; NASA POWER temperatura, RH, viento, radiación solar, presión y temperatura de rocío, más VPD y diferencia T−Td calculados a partir de esos registros. Los 39 sectores comparten siete grupos NASA aproximados (no estaciones independientes). No se imputaron corrientes marinas históricas ni humedad foliar. Entrenamiento 1997–2015, ajuste 2016–2018, calibración 2019–2020, prueba 2021–2025.

| Familia RF | MAE mensual mm ↓ | Brier probabilidad P90 ↓ |
|---|---:|---:|
| **Solo lluvia histórica** | **18,0442** | 0,075266 |
| **Lluvia + océano/viento** | 18,4406 | **0,068131** |
| Lluvia + atmósfera NASA | 19,3196 | 0,070902 |
| Lluvia + océano + atmósfera NASA | 18,5796 | 0,071832 |
| **Climatología sectorial (referencia)** | **14,2957** | **0,062884** |

**Hallazgo:** la mejor variante RF para estimar mm usa lluvia histórica, mientras la mejor probabilidad P90 retrospectiva RF utiliza océano. **Ninguna supera a la climatología** en estas métricas principales. Una selección de familias por bloque usando solo ajuste 2016–2018 eligió lluvia histórica en todos los bloques para clasificación, cuyo Brier en test fue **0,075266** (climatología 0,062884). En 2023 lluvia+océano redujo Brier a 0,121486 frente a climatología 0,136595, aunque en MAE fue peor (30,1755 vs. 24,8143 mm). No publicar todavía alertas, predicción oficial El Niño, diagnósticos de enfermedades ni habilidad de emisión prospectiva. GCN solo se conserva como experimento comparativo histórico.

[**Panel principal RF de lluvia**](random-forest-lluvias.html) · [Informe RF 10I](FASE_10I_RF_SOLO_LLUVIA.md) · [Programa del entrenamiento](modelos/random_forest_lluvia_multivariable_10i.py) · [Métricas auditadas](datos/rf_precipitacion_10i/informe_rf_lluvia_10i.json) · [9.360 predicciones CSV](datos/rf_precipitacion_10i/evaluacion_emparejada_10i.csv) · [Selección por validación](datos/rf_precipitacion_10i/seleccion_solo_validacion_10i.json) · [Utilidad separada horas de RH con datos horarios](modelos/horas_humedad_horarias_10i.py) · [GitHub Actions exitoso](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39091613534).

## Fase 10H · Random Forest vs GCN: entrenamiento completado con NASA, CHIRPS y océano (17/10/2026)

**Entrenamiento y pruebas realmente ejecutados.** Se recuperó un histórico completo de **39 sectores × 360 meses = 14.040 filas** de NASA POWER (1996–2025) y se entrenaron cinco bloques espaciales de Random Forest y Graph Convolutional Network. Los modelos usan precipitaciones CHIRPS rezagadas, índices oceánicos NOAA (anomalías Niño 1+2 y Niño 3.4, SOI, alisios y viento marino) y seis campos físicos NASA (temperatura, humedad, viento, radiación, presión superficial y temperatura de rocío), todos con **rezagos de al menos dos meses**. La nueva evaluación tiene **2.340 casos de prueba 2021–2025, 247 lluviosos ≥P90 por sector**, y 4.680 probabilidades almacenadas.

| Evaluación | Brier ↓ | PR-AUC ↑ |
|---|---:|---:|
| Climatología sectorial estacional | **0,062884** | **0,60414** |
| Random Forest lluvia + océano (10F) | 0,069247 | 0,43511 |
| **Random Forest lluvia + océano + atmósfera NASA (10H)** | **0,072036** | **0,39737** |
| **GCN lluvia + océano + atmósfera NASA (10H)** | 0,077423 | 0,35626 |

**Conclusión:** entre las dos IA con todos los factores disponibles, **Random Forest obtuvo mejores resultados**. Pero incluir meteorología NASA POWER no mejoró RF frente al modelo con lluvia + océano, y **ninguna IA superó a la climatología** globalmente. El intervalo exploratorio de la diferencia de Brier RF−GCN por cinco años fue **[−0,013189; +0,002415]**, que incluye cero. Por ello el modelo recomendado es **RF como candidato de investigación**, no un algoritmo validado para alertas o pronóstico meteorológico operativo.

**Cobertura y límites:** NASA POWER solo generó **siete agrupaciones gruesas de muestreo para 39 sectores**. Los reanálisis NASA/MERRA-2 y los datos satelitales de radiación SRB/CERES son ex post, y la fuente de radiación cambia cerca de 2001. CHIRPS Final también fue revisado retrospectivamente. Faltan predicciones reales *as-issued* y validación con estaciones SENAMHI independientes. Las etiquetas P90 de lluvia **NO equivalen a El Niño costero ni diagnósticos de enfermedades de arándano/vid**; esos proyectos necesitarán objetivos y registros propios.

[Comparador en línea cuando GitHub Pages lo despliegue](evaluacion-modelos-atmosfericos-10h.html) · [Informe y ficha científica](FASE_10H_COMPARACION_MULTIVARIABLE.md) · [CSV de 4.680 probabilidades](datos/modelos_multivariables_10h/probabilidades_rf_gcn_nasa_10h.csv) · [Métricas JSON](datos/modelos_multivariables_10h/evaluacion_rf_gcn_nasa_10h.json) · [Incertidumbre emparejada](datos/modelos_multivariables_10h/auditoria_comparacion_10h.json) · [Fuentes NASA POWER](datos/nasa_power_10h/auditoria_fuentes_10h.json) · [Código RF/GCN](modelos/comparacion_rf_gcn_nasa_10h.py) · [CI de ingesta](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39085555539) · [CI de entrenamiento](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39085711303).

## Fase 10G · Control espacial de siete variables ERA5 en 39 sectores (17/10/2026)

El observatorio incorporó [control de procedencia atmosférica](verificacion-atmosferica.html) para consultar **ERA5 histórico 0,25°** (Open-Meteo/ECMWF) de forma trazable en **un punto interior de cada uno de los 39 polígonos experimentales**. Variables: temperatura, radiación de onda corta, humedad relativa, viento a 10 m, nubosidad, presión media al nivel del mar y déficit de presión de vapor. La API devuelve coordenadas de celdas reales, que no necesariamente coinciden con centros de parcelas o medias de cada polígono.

**Piloto real de 2023:** 468 registros mensuales (39 sectores × 12 meses), **17 celdas ERA5 distintas** y **32 sectores en celdas compartidas**. Por tanto, no existen 39 observaciones espaciales independientes de esas siete variables a esta resolución. Se conserva la cota negativa del sector S001 para revisión. [Auditoría del piloto](datos/atmosfera_sectorial_10g/piloto_era5_2023_10g.json) · [Puntos de muestreo](datos/atmosfera_sectorial_10g/puntos_y_advertencias_10g.json) · [GitHub Actions del piloto exitoso](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39084097579).

**Extensión 1996–2025:** el motor automatizado comprueba 360 meses por sector (14.040 filas), siete variables, unidades originales, coincidencia temporal, duplicados de celda y SHA. La publicación de [matriz](datos/atmosfera_sectorial_10g/muestra_era5_mensual_10g.csv) y [auditoría completa](datos/atmosfera_sectorial_10g/auditoria_atmosfera_10g.json) queda condicionada a pasar todos los controles. [Código de extracción](modelos/ingesta_era5_39_sectores_10g.py) · [Workflow](.github/workflows/oaf_10g_completo.yml).

**Reevaluación predictiva:** la [ablación RF/GCN con ERA5](modelos/comparacion_atmosferica_rf_gcn_10g.py) contrasta las mismas 2.340 etiquetas de 10F con siete variables ERA5 de t−2, solo cuando exista la matriz completa. [Pruebas de comparación](tests/test_comparacion_atmosferica_10g.py) · [Workflow predictivo](.github/workflows/oaf_10g_comparacion_rf_gcn.yml). **No hay mejoras demostradas por el mero hecho de incorporar variables; son reanálisis ex post y NO estaciones instrumentales, y las alertas siguen inactivas.**

[Informe metodológico y cautelas](FASE_10G_INGESTA_ATMOSFERICA_SECTORES.md).

## Fase 10F · Probabilidad de lluvia alta en 39 sectores (17/10/2026)

**Fase ejecutada y verificada:** cinco modelos probabilísticos en 39 sectores, **2.340 objetivos sector-mes** de prueba 2021–2025 y **247 eventos de precipitación ≥P90 histórico sectorial**. Se mantienen cinco bloques geográficos y ventanas independientes: entrenamiento 1997–2015, ajuste 2016–2018, calibración 2019–2020 y prueba 2021–2025.

**Brier Score global, menor es mejor:** climatología sectorial **0,062884** (PR-AUC 0,60414), RF lluvia + señales oceánicas **0,069247** (PR-AUC 0,43511), RF solo lluvia 0,074842, GCN lluvia + océano 0,078348, GCN solo lluvia 0,084757. **RF con océano es el mejor modelo de IA de esta prueba por Brier, pero NO supera a la climatología ni queda aprobado operativamente.** En 2023 RF + océano alcanzó Brier 0,121150 frente a climatología 0,136595; esta mejora no se mantiene todos los años.

**Advertencia territorial:** los 39 sectores tienen CHIRPS, y el modelo recibe indicadores oceánicos **regionales compartidos** (anomalías Niño1+2/Niño3.4, SOI, alisios y vientos marinos) con rezago ≥2 meses. La temperatura, radiación, humedad, VPD y viento local siguen homologados solo en cuatro localidades; NO se fabricaron datos de esas variables para los 39 sectores. No se usaron corrientes geostróficas incompletas. CHIRPS Final es retrospectivo, faltan archivos *as-issued* y estación instrumental independiente, y **no se activan alertas** de lluvia, Niño o enfermedades.

[Explorador por piso](evaluacion-sectores-10f.html) · [Informe científico 10F](FASE_10F_PROBABILIDAD_39_SECTORES.md) · [Métricas JSON](datos/extension_10f/evaluacion_39_sectores_10f.json) · [11.700 probabilidades CSV](datos/extension_10f/probabilidades_39_sectores_10f.csv) · [Código](modelos/probabilidad_39_sectores_10f.py) · [Pruebas](tests/test_probabilidad_10f.py) · [CI concluida](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39083056802).

## Fase 10E · Fuentes oficiales separadas y predicciones probabilísticas del autor (17/10/2026)

El sitio distingue explícitamente **[Información y avisos oficiales](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino)**, donde se identifica el emisor institucional SENAMHI/ENFEN, de **[Modelos experimentales desarrollados por el autor](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#autor)**, donde se muestran los algoritmos y sus verificaciones sin atribuirles respaldo oficial. El módulo del autor distingue lluvia intensa, escenarios ENSO/El Niño costero y factores para enfermedades de arándano y vid; solo el primero fue objeto de un **nuevo benchmark probabilístico** en 10E.

El ensayo utilizó ERA5/ERA5-Land, radiación, temperatura, viento (tierra/mar), humedad/VPD y anomalías NOAA Niño 1+2/3.4 más SOI/alisios en **cuatro localidades (Chiclayo, Jayanca, Motupe, Olmos)** con entradas t−2+, entrenamiento **1997–2015**, ajuste **2016–2018**, calibración **2019–2020** y prueba **2021–2025**. Se analizaron **240 casos de prueba**, 30 de ellos con lluvia ERA5 por encima del percentil 90 aprendido en entrenamiento.

**Brier Score (menor es mejor):** climatología local **0,077467**, **Random Forest multivariable 0,088183**, GCN multivariable **0,111878**. Entre los algoritmos de IA, RF obtiene mejor Brier y PR-AUC que GCN; pero **no supera la climatología**, por lo que **no se designa ganador operativo ni se habilitan avisos**. Los contrastes anuales pareados con solo cinco años son exploratorios y no prueban una diferencia robusta. Las corrientes geostróficas 2017–2025 no se imputaron a décadas anteriores; la matriz multivariable de cuatro localidades no se extrapola a los 39 sectores CHIRPS.

[Informe 10E](FASE_10E_MODELOS_PROBABILISTICOS_MULTIVARIABLES.md) · [Evaluación Brier/PR-AUC](datos/probabilidades_10e/evaluacion_probabilistica_10e.json) · [Auditoría de incertidumbre](datos/probabilidades_10e/auditoria_incertidumbre_10e.json) · [Probabilidades retrospectivas CSV](datos/probabilidades_10e/predicciones_probabilisticas_10e.csv) · [Motor RF-GCN](modelos/probabilidad_multivariable_10e.py) · [Tests](tests/test_probabilidad_10e.py) · [CI validada](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39081906133).

## Fase 10D · Prueba factorial de rezagos y sensibilidad a extremos (17/10/2026)

La evaluación de ambos diseños con **idénticas ventanas de entrenamiento 1997–2015, ajuste 2016–2018, calibración 2019–2020 y prueba 2021–2025** se ejecutó con éxito, con **5.616 predicciones de calibración y 14.040 predicciones de prueba** sobre 39 sectores y cinco bloques. MAE 2021–2025: **RF L1 17,0241 mm / L2 18,1443 mm**, **GCN L1 18,7739 mm / L2 17,6452 mm**; climatología por piso 20,3708 mm. El intervalo espacial exploratorio GCN L2−L1 **[−2,7164; +0,8257] mm** contiene cero, por lo que no confirma una ganancia homogénea.

Para **137 observaciones sector-mes con lluvia ≥100 mm**, la regla calibrada solo en 2019–2020 detectó **123 (GCN L2), 113 (RF L2) y 106 (climatología)**; simultáneamente produjo **438, 205 y 314 falsas alarmas**, respectivamente. Los umbrales son pruebas estadísticas, NO oficiales. La estratificación retrospectiva RONI del CPC/NOAA no sustituye el monitoreo ENFEN del Niño costero. **CHIRPS v3 Final se ha reprocesado históricamente; no existe validación as-issued ni instrumental, y siguen desactivadas las alertas automáticas.**

[Visor de eventos extremos](evaluacion-extremos.html) · [Informe 10D](FASE_10D_COMPARACION_FACTORIAL_EXTREMOS.md) · [Datos reales y métricas](datos/experimentos_10d/evaluacion_controlada_10d.json) · [Predicciones factoriales CSV](datos/experimentos_10d/predicciones_factorial_10d.csv) · [Programa Python](modelos/experimento_factorial_10d.py) · [Verificación CI satisfactoria](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39080924683).

## Fase 10C · Reentrenamiento con rezagos t−2 y calibración separada (17/10/2026)

Se reentrenaron **Random Forest y GCN** sobre cinco bloques geográficos de 39 sectores, utilizando solamente rezagos t−2, t−3, t−4, t−6, t−12 para pronósticos mensuales, ajuste de 2016–2018 y calibración independiente de 2019–2020. La prueba 2021–2025 produjo **MAE 18,1443 mm para RF y 17,6429 mm para GCN** (climatología por piso: 20,3708 mm). En 2023, la cobertura de intervalos nominales 90 % fue **85,04 % RF y 79,49 % GCN**. Los resultados usan CHIRPS v3 FINAL revisado: **NO son pruebas as-issued ni habilitan alertas**. El cambio respecto a 9X combina rezagos y una ventana distinta de selección de hiperparámetros.

[Panel 10C](evaluacion-lag2.html) · [Documento metodológico](FASE_10C_REENTRENAMIENTO_LAG2.md) · [Modelo reproducible](modelos/reentrenamiento_lag2_10c.py) · [Validación CI](.github/workflows/oaf_10c_reentrenamiento.yml) · [Resultados publicados](datos/reentrenamiento_10c/evaluacion_lag2_10c.json).

## Fase 10B · Incertidumbre y sensibilidad en años extremos (17/10/2026)

Se ejecutó una calibración conformal **retrospectiva**, empleando las 11.700 predicciones de 9X, calibración **2021–2022** y prueba posterior **2023–2025**, con radio de orden 23/24 por sector/modelo. En 2023, la cobertura observada cayó a **80,13 % en Random Forest**, **82,26 % en GCN** y **85,68 % en climatología por piso**, frente al 90 % nominal. Entre 91 observaciones sector-mes con precipitación mensual ≥100 mm durante 2023–2025, el pronóstico puntual también alcanzó ese umbral en 15 (RF), 4 (GCN) y 17 (climatología por piso). Son criterios exploratorios, no alertas oficiales. Las predicciones utilizan **CHIRPS v3 FINAL retroprocesado**, no un conjunto de versiones originales as-issued; no se reentrenaron todavía con rezagos operativos ni existe validación instrumental independiente. **Ningún modelo operativo está autorizado**.

[Visor de incertidumbre](evaluacion-temporal.html) · [Evidencia JSON](datos/calibracion_10b/evaluacion_temporal_10b.json) · [Informe 10B](FASE_10B_CALIBRACION_TEMPORAL.md) · [Código reproductor](modelos/calibracion_temporal_10b.py) · [QA 10B](.github/workflows/oaf_10b_evaluacion.yml).

## Evaluación territorial 10A · 17/10/2026
Se auditaron y reconciliaron **11.700 registros reales de CHIRPS v3 FINAL** (39 sectores × 60 meses × cinco modelos, prueba 2021–2025) contra la fase 9X. Random Forest tuvo MAE de **17,1634 mm**, GCN **18,6207 mm** y la climatología por piso **20,3708 mm**. **RF supera a GCN en 29/39 sectores, pero a la climatología solo en 21/39**; en 2023 la climatología por piso obtuvo menor MAE regional (29,0583 mm) que ambos modelos complejos. **No son predicciones operativas as-issued ni intervalos conformales calibrados; no se activaron alertas**. [Panel comparativo](evaluacion-territorial.html) · [Datos auditados](datos/integracion_10a/diagnostico_reconciliado_10a.json) · [Informe técnico](FASE_10A_RECONSTRUCCION_PREDICTIVA.md) · [Código replicable](modelos/auditoria_integrada_10a.py) · [Pruebas CI](.github/workflows/oaf_10a_auditoria.yml).

## Nueva experiencia UX · productor y ciencia técnica (17/10/2026)

Se implementó una interfaz por **Vista rápida/Vista técnica**, con navegación Android, localidad compartida Chiclayo/Jayanca/Motupe/Olmos, fuente y hora de validez por los siete indicadores del Inicio, cuatro gráficos independientes a siete días desde Open-Meteo, mapa DEM original de 420 puntos en portada, resumen de arándano/vid, estado oficial ENFEN solo si la verificación institucional aporta evidencia, e índice expandible de cuatro áreas científicas. El proyecto **conserva los 463 IDs y 45 scripts originales**, sus CSV/JSON y evaluaciones, verificables automáticamente.

**[Plan de implementación](PLAN_UX_OAF_2026.md)** · **[Entrega y limitaciones](ENTREGA_UX_OAF_OCTUBRE_2026.md)** · **[QA integral](.github/workflows/oaf_ux_integrity_2026.yml)** · **[Portal interactivo](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#inicio)**.

## Fase 9H · Contraste instrumental de CHIRPS y ERA5 (17/10/2026)

Se extrajeron valores **reales** de 12 GeoTIFF mensuales CHIRPS v3 de 1998 (72 parejas estación–píxel, **36 meses observacionales únicos**) y ERA5 atmosférico vía Open-Meteo 1996–2013 (1 276 parejas, **638 meses observacionales únicos**) para Virrey, Puchaca y El Espinal, evaluando **dos ubicaciones publicadas** por estación. Cada fuente conserva URL, SHA-256, fecha de consulta, centro de píxel, cobertura y error mensual. Se calculan MAE, RMSE y sesgo **solo en meses realmente pareados**; no son métricas de pronósticos OAF.

Puchaca es espacialmente sensible: las coordenadas alternativas devuelven **dos celdas ERA5 atmosféricas distintas** y el MAE mensual pasa de **93,06 a 155,15 mm**; CHIRPS también cambia de píxel aunque su MAE 1998 varía menos (**84,80 a 85,16 mm**). Esta diferencia no acredita un emplazamiento ni permite escoger a posteriori la mejor celda.

**No confundir productos:** ERA5 atmosférico (lluvia, ~0,25°) ≠ ERA5-Land (tierra, ~0,1°). La precipitación ERA5-Land no estuvo disponible directamente en la API histórica de Open-Meteo seleccionada; el intento complementario con temperaturas ERA5-Land sufrió **timeout**, por lo que **no se presentaron errores inexistentes**. CHIRPS combina pluviómetros, así que la independencia del contraste sigue sin demostrarse. Los archivos diarios originales no incluyen información suficiente para certificar el día pluviométrico o los cambios históricos del sensor.

[Informe 9H](FASE_9H_CONTRASTE_INSTRUMENTAL.md) · [CHIRPS y procedencia](datos/validacion_estaciones_9h/comparacion_observacional_9h.json) · [ERA5 y estado de temperaturas ERA5-Land](datos/validacion_estaciones_9h/contraste_era5_complementario_9h.json) · [QA 9H](.github/workflows/oaf_auditoria_9h.yml) · [Panel interactivo](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#oaf-9h-visor).

## Fase 9G · Sensibilidad geográfica instrumental (17/10/2026)

Las referencias documentales de Virrey, Puchaca y El Espinal tienen separación entre coordenadas alternativas de **1,531; 2,647; y 1,860 km**, respectivamente. Las alturas publicadas difieren **61, 445 y 38 m**; el caso Puchaca podría cambiar de franja exploratoria según qué cota histórica corresponda al instrumental. Estos valores no son distancias medidas de traslado, ni MAE/RMSE contra ERA5/CHIRPS: **los modelos grillados aún no se han extraído para estas candidatas**. [Auditoría reproducible 9G](datos/validacion_estaciones_9g/sensibilidad_geografica_9g.json) · [método](FASE_9G_SENSIBILIDAD_GEOGRAFICA.md).

## Identificación territorial: Virrey, Puchaca y El Espinal (17/10/2026)

Con información adicional del usuario y tres coincidencias exactas de día y precipitación máxima con **tablas oficiales SENAMHI**, se identificaron los originales: **00152107 = Virrey (código 152107; 330 mm el 10/02/2012)**, **00153114 = Puchaca (153114; 150,2 mm el 06/01/1998)** y **00000340 = El Espinal (000340; 107 mm el 20/02/1998)**. La identidad nominal supera la incertidumbre registrada en la etapa anterior.

Se recuperaron referencias geográficas institucionales de Virrey (Olmos), Puchaca (Incahuasi) y El Espinal (Oyotún). **Las fuentes no coinciden completamente en coordenadas ni en altitudes**; para Puchaca se publican 355, 500 y 800 m. Estas discrepancias se conservan en vez de elegir arbitrariamente una cota: la ubicación histórica del instrumento **aún no está certificada**.

Con datos observados completos y excluyendo 1997–1998 de la media anual descriptiva 1996–2013, la lluvia de 1998 fue aproximadamente **5,34 veces** la referencia de El Espinal (**15 años base**), **10,36 veces** en Puchaca (**9 años base**), y **10,34 veces** en Virrey (**16 años base**). Son razones exploratorias, **no una normal 1996–2025 ni validación predictiva**.

Recursos: [informe técnico](FASE_9F_IDENTIDAD_TERRITORIAL.md) · [inventario y hallazgos reproducibles](datos/validacion_estaciones_9f/identificacion_territorial_9f.json) · [script con SHA y coincidencias](modelos/identificacion_instrumental_9f.py) · [pruebas automáticas](.github/workflows/oaf_identificacion_9f.yml). En el portal, **Análisis de clima regional → Virrey, Puchaca y El Espinal: estaciones y territorio**. Los paneles de estaciones se colocaron correctamente dentro de esa pestaña, manteniendo la navegación desplegable y sin códigos de etapas en los títulos.

## Fase 9E · Contraste instrumental entre tres series (17/10/2026)

Se realizó un segundo control de 3 registros de estación aportados por usuario, usando solo meses con **100 % de días observados**. Sobre los 216 meses de 1996–2013, la precipitación estricta está disponible en **215 (00000340), 207 (00153114) y 216 (00152107)**. Los tres archivos tienen 1998 completo; 1983 solo está completo en 00153114 y 00152107.

**Correlaciones descriptivas de log(1+mm) mensuales, entre pares:** **0,81128**, **0,78934** y **0,87053** (n pareados 206, 215 y 207). Tales similitudes temporales no prueban que las estaciones estén cercanas, geográficamente localizadas, climáticamente homogéneas, ni que un modelo haya pronosticado las lluvias.

Durante 9E todavía no se había cotejado la identidad; la **etapa posterior de identificación territorial** corroboró nombres y códigos, aunque coordenadas históricas, altitudes y licencia no están conciliadas. El motor de comparación ERA5-Land/CHIRPS se entregó **con bloqueo deliberado** hasta disponer de fichas geográficas verificadas; **no hay sesgo/MAE estación-grilla calculados**. CHIRPS v3 incluye pluviómetros, por lo que hay que analizar la independencia del contraste si la propia estación fue asimilada en el producto.

Recursos: [informe y resultados 9E](FASE_9E_CONTRASTE_INSTRUMENTAL.md) · [matriz de comparación temporal JSON](datos/validacion_estaciones_9e/contraste_observacional_9e.json) · [fichas pendientes](datos/validacion_estaciones_9e/metadatos_identidad_9e.json) · [comparador geoespacial preparado](modelos/emparejamiento_reanalisis_9e.py). El público puede explorar las lluvias y correlaciones en **Análisis de clima regional → Comparación histórica de lluvias entre estaciones**, sin códigos de fase en los títulos.

## Fase 9D · Estaciones reales, trazabilidad y disponibilidad (17/10/2026)

Tres series diarias originales aportadas al OAF-Lambayeque se preservaron en [datos/estaciones_9d/originales/](datos/estaciones_9d/originales/) y se incorporaron a una ingesta reproducible con SHA-256, separación por variable de faltantes (-99.9), revisión de extremos y calendario diario sin duplicados.

**55 200 registros diarios**, **1 814 registros mensuales** con cobertura; los tres archivos tienen lluvia útil pero el código 00152107 carece de cualquier temperatura, y 00000340 no tiene lluvia registrada en 1983. La máxima lluvia diaria identificada, **330 mm en 00152107 el 10/02/2012**, permanece señalada para revisión y **no se ha eliminado**.

Para 1996–2013, meses válidos de precipitación (umbral interno de 90 % de días): 00000340 **215/216**, 00153114 **213/216** y 00152107 **216/216**. Las series llegan como máximo a julio de 2014: **no ofrecen una normal de 30 años 1996–2025**, ni han demostrado habilidad predictiva o verificación de 9A/9C. La identidad, nombres, latitud, longitud, altitud y licencia siguen sin corroboración; **no se asignan puntos inventados en mapas**.

**Publicados:** [informe y límites 9D](FASE_9D_ESTACIONES_REALES.md), [control de calidad y SHA](datos/estaciones_9d/auditoria_estaciones_9d.json), [mensuales auditados CSV](datos/estaciones_9d/series_mensuales_9d.csv), [motor Python](modelos/estaciones_instrumentales_9d.py), [automatización de auditoría](.github/workflows/oaf_estaciones_instrumentales_9d.yml). Dashboard en **Análisis de clima regional → Fase 9D** de la [web pública](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima).

## Fase 9C · Validación robusta con intervalos (17/10/2026)

Se recuperaron las matrices **reales, retrospectivas y reanalizadas** de 9A y se verificaron **4 320 parejas de predicción continua** y **720 parejas probabilísticas** comparando el benchmark 8W viento+SST frente a HR+VPD. Se calcularon MAE/Brier y 10 000 remuestreos en bloques circulares de tres años, análisis a un año, sensibilidad a 2017/2023 e intervalos exploratorios con ajuste conservador Bonferroni.

- HR+VPD mejora MAE en **11/24** combinaciones (temperatura 5/12, precipitación 6/12), y Brier extremo P90 en **1/12**.
- **0 de 36** resultados superan el ajuste conservador por comparaciones múltiples; **0 de 12** evaluaciones P90 tienen suficientes eventos (4–7 por localidad; horizontes repiten eventos).
- **No cambiar el modelo de referencia ni activar alertas.** Las celdas de reanálisis Chiclayo, Jayanca, Motupe y Olmos no representan todos los pisos altitudinales. Falta verificación instrumental SENAMHI y prospectiva con fechas originales.

**Recursos:** [informe 9C](FASE_9C_RESULTADOS_VALIDACION.md) · [matriz JSON](datos/validacion_9c/resultados_9c.json) · [motor Python de reproducción](modelos/evaluacion_pareada_9c.py) · [prueba automatizada](.github/workflows/oaf_validacion_9c.yml). El panel interactivo está en **Investigación y datos → Fase 9C** de la [web pública](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

## Rediseño de la web pública · 17/10/2026

La interfaz tiene **cinco pestañas para el público y los investigadores**, conservando los modelos, fuentes y series archivadas: (1) **Inicio** con seis indicadores agrometeorológicos modelados (temperatura, precipitación, humedad, VPD, viento y radiación), resumen breve de fuentes científicas y novedades verificadas; (2) **Análisis de clima regional** con dashboard, anomalías, mapa de 420 puntos DEM, pisos altitudinales y series históricas; (3) **Monitoreo del Niño y anomalías climáticas**, fuentes ENFEN/NOAA, viento, SST, corrientes y análisis experimentales; (4) **Sanidad vegetal** con subpestañas **Cultivos** (arándano y vid, enfermedades y manejo integrado) y **Modelos predictivos de enfermedades** (todavía experimentales); y (5) **Investigación y datos** para fuentes, validaciones, modelos y descargas reproducibles.

Los resultados científicos del OAF **no son automáticamente validados localmente por emplear fuentes de prestigio**. ERA5/ERA5-Land, NOAA, CHIRPS, CAMS y Open-Meteo tienen documentación de origen y metodología, pero predicciones de enfermedades, alertas ENSO y zonas homogéneas deben contar con su propia evaluación instrumental y de campo.

**[Descripción detallada del rediseño](REDISENO_WEB_OAF_OCTUBRE_2026.md)** · [Web OAF](https://ccoronelepg-gif.github.io/OAF-Lambayeque/) · [QA de la nueva arquitectura](.github/workflows/oaf_redisenio_web_2026.yml).

## Actualización del portal · 14/10/2026

La página pública [OAF-Lambayeque 2.2](https://ccoronelepg-gif.github.io/OAF-Lambayeque/) incorpora:

- Biblioteca consultable para **arándano y vid**, con nueve enfermedades, variables meteorológicas, rangos publicados, nivel de respaldo y enlaces directos a estudios y guías técnicas.
- Módulo visible de **boletines ENFEN** con comunicado N.º 17-2026 (verificado al 14/10/2026), acceso a archivos institucionales y al registro de monitoreo automatizado con sus limitaciones.
- Consulta horaria experimental para **Jayanca, Motupe, Olmos y Chiclayo**, con años completos 2023–2025, usando ERA5-Land (temperatura/HR) y ERA5 (precipitación) a través de Open-Meteo, exportación CSV y tratamiento explícito de fallos y datos faltantes.
- Conservación de todas las secciones de validación, CHIRPS, SENAMHI y datos históricos existentes.

Los índices no son alertas operativas ni permiten diagnosticar enfermedades. El navegador necesita acceso a la API de terceros para obtener datos horarios.

## Interfaz pública simplificada · 14/10/2026

**Sitio:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/

La portada se reorganizó en cinco pestañas exclusivas:
1. Cultivos y condiciones de riesgo de patologías: tabla de tres columnas (enfermedad, condiciones climáticas y cultivo), con nueve patologías y fuentes.
2. Boletines de El Niño: enlaces ENFEN/SENAMHI, consulta al registro institucional y estado de verificación sin suponer alerta vigente.
3. Datos climáticos: consulta modelada de tiempo reciente y pronóstico externo a siete días para cuatro localidades, más última disponibilidad CHIRPS.
4. Riesgo de presencia de enfermedades: estado de los modelos, requisitos y advertencia de que no existen alertas OAF operativas.
5. Verificaciones de datos: resumen de calidad, cobertura histórica y enlace al portal anterior conservado en [archivo-analisis-historico.html](archivo-analisis-historico.html).

El nuevo diseño reduce información redundante; la página histórica de 2026 se mantiene íntegra. Las imágenes públicas proceden de Wikimedia Commons (Scott Bauer/USDA y Panelxf, CC0/dominio público). Las cifras de estado de fuente se cargan desde los JSON mantenidos en este repositorio. El pronóstico de Open-Meteo **no es un modelo predictivo propio del OAF**.

## Interfaz OAF actualizada · 14/10/2026

La navegación pública se ordena de izquierda a derecha en cinco secciones:

1. **Inicio:** propósito del proyecto, fuentes utilizadas, evaluación de calidad, modelos científicos y validación futura.
2. **Datos climatológicos:** meteorología modelada reciente, perspectiva a siete días de Open-Meteo, disponibilidad de precipitación CHIRPS y distinción de predicciones propias en desarrollo.
3. **Cultivos y riesgo de enfermedades:** tabla compacta de tres columnas con las nueve enfermedades de arándano y vid, bibliografía científica y resumen de modelos experimentales sin alertas operativas.
4. **Boletín de El Niño:** comunicados de ENFEN y avisos SENAMHI; el estado se publica únicamente si es verificable.
5. **Verificación de datos:** cobertura y control de calidad, archivo original íntegro en [archivo-analisis-historico.html](archivo-analisis-historico.html).

La web preserva los enlaces directos anteriores a `#cultivos` y redirige la pestaña antigua `#riesgos` a esa sección, sin duplicación de información.

## Fase 5 · Primer indicador térmico experimental (14/10/2026)

En [Cultivos → Predicción fitosanitaria](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos) se incorporó la consulta de pronóstico horario externo para Motupe, Jayanca, Olmos y Chiclayo, y una evaluación **exploratoria** del patrón térmico asociado con la fase conidial del oídio de la vid (*Erysiphe necator*) según UC IPM. Procesa siete jornadas futuras completas, cuenta horas continuas dentro del intervalo favorable y detecta secuencias de tres días consecutivos. Un vacío de datos hace no evaluable la jornada.

**No es una predicción validada de presencia de enfermedad ni un índice completo de UC IPM:** se usan temperaturas a 2 m, no datos del dosel, y se desconoce la infección primaria. No se recomienda tratamiento fitosanitario. La API externa se consulta cuando el visitante abre el módulo y su disponibilidad no está garantizada.

La implementación reproducible está en [modelos/oidio_vid_indicador_termico.py](modelos/oidio_vid_indicador_termico.py), con cuatro escenarios sintéticos de prueba. [Método, limitaciones y plan de validación](MODELO_TERMICO_OIDIO_VID_FASE5.md).

## Prioridad científica: dos sistemas de predicción (precisión del autor, 14/10/2026)

**No se trata solo de monitorear ni de reunir boletines.** La finalidad del proyecto es investigar, construir y evaluar dos tipos de predicción:

- **Anomalías agroclimáticas y El Niño Costero:** probabilidades o escenarios futuros de lluvia, temperatura y humedad anómalas, junto con evolución oceánica/atmosférica ligada a El Niño Costero y su posible impacto regional. El estado oficial pertenece a ENFEN; todo pronóstico OAF debe validarse y distinguirse de escenarios ajenos.
- **Enfermedades de arándano y vid:** modelos separados por patógeno y cultivo que incorporen pronósticos meteorológicos, microclima, fenología y observación sanitaria. No se equipara clima favorable a diagnóstico ni a probabilidad calibrada.

**Condición para publicación de pronósticos OAF:** guardar predicciones con fecha anterior al evento, medir habilidad frente a referencias, errores e incertidumbre, y no declarar operatividad hasta contar con validación externa o prospectiva suficiente.

## Fase 6A · Comparación predictiva de anomalías climáticas (14/10/2026)

En [Datos climatológicos del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), el nuevo módulo experimental compara temperaturas medias y lluvias previstas para 7 jornadas futuras con una referencia por época del año del periodo **1996–2025**. Para temperatura se identifican días previstos por encima de P90 o por debajo de P10 histórico; para precipitación se contrasta la suma de 7 días con el P90 de acumulados históricos equivalentes. Los datos históricos se consultan bajo demanda como reanálisis ERA5-Land (temperatura) y ERA5 (precipitación); el pronóstico es **externo de Open-Meteo**, no un modelo meteorológico propio. La comparación no equivale a probabilidad calibrada ni a alerta oficial.

- Código probado con datos sintéticos: [modelos/anomalias_climaticas_v01.js](modelos/anomalias_climaticas_v01.js).
- Método científico y limitaciones: [MODELO_ANOMALIAS_FASE6A.md](MODELO_ANOMALIAS_FASE6A.md).
- Diez verificaciones de lógica superadas: señales normales/cálidas/lluviosas, referencia de 30 años y umbrales mínimos de 25/24 años, registros faltantes, cambio de año y bisiestos. **No constituyen validación con observaciones meteorológicas reales**.
- El apartado **Boletín de El Niño** incluye una hoja de ruta predictiva específica Niño 1+2/ICEN. No se afirma que el OAF prediga ya El Niño Costero; ese modelo y su validación siguen pendientes.

**Próxima prioridad:** construir una serie oceánico-atmosférica verificable de Niño 1+2 e ICEN y un primer modelo base de predicción frente a persistencia y escenarios institucionales; en paralelo validar indicadores fitosanitarios con observaciones de campo.

## Fase 6B · Primera predicción oceánica experimental Niño 1+2 (14/10/2026)

**Objetivo de investigación:** anticipar una anomalía mensual oceánica Niño 1+2, como paso hacia un sistema de predicción de posibles episodios de El Niño Costero, y evaluar objetivamente si un modelo propio supera la persistencia. **No se afirma que este primer modelo prediga El Niño Costero o sea el índice ICEN oficial.**

- **Fuente real descargada:** [NOAA CPC OISST v2.1 Niño 1+2](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices), serie continua desde enero de 1982 hasta septiembre de 2026. Se distinguen en todo momento NOAA OISST y el **ICEN/ERSSTv5 oficial de ENFEN**.
- **Última anomalía NOAA:** septiembre de 2026, **+4,69 °C**.
- **Modelo de anomalía a un mes (octubre de 2026):** AR(1) experimental **+4,35 °C**; persistencia **+4,69 °C**. No son probabilidades, clasificaciones ENFEN ni avisos climáticos para Lambayeque.
- **Walk-forward con 200 pronósticos retrospectivos (2010–2026):** MAE AR(1) **0,3749 °C**, persistencia **0,3797 °C**; diferencia favorable **~1,26 %**, demasiado reducida para proclamar habilidad consolidada.
- **Últimos 12 meses:** MAE AR(1) **0,5818 °C** frente a **0,4708 °C** de persistencia (el AR1 empeora un **23,56 %**). El intervalo exploratorio del remuestreo por bloques incluye cero: NO se ha demostrado mejor desempeño robusto.
- **Archivos y método:** [MODELO_NINO12_FASE6B.md](MODELO_NINO12_FASE6B.md), [Python](modelos/modelo_nino12_fase6b.py), [workflow automático de GitHub Actions](.github/workflows/oaf_nino12_fase6b.yml), [serie NOAA](datos/noaa_nino12_oisst_mensual.csv), [evaluación mensual](datos/nino12_backtest_walkforward.csv), [salida JSON](datos/modelo_nino12_experimental.json).
- **Página:** [Boletín de El Niño → evaluación oceánica experimental](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino). Se conserva la fuente y estado oficial ENFEN por separado.

**Siguiente fase:** incorporar la serie ERSSTv5/ICEN conforme a la definición oficial actualizada, variables de viento y océano subsuperficial, y un conjunto histórico de pronósticos fechados para evaluación prospectiva. Persistencia seguirá siendo el modelo de referencia que debe superarse; ninguna alerta OAF se emitirá hasta validar los modelos.

## Fase 6C · ERSSTv5 Niño 1+2 y comprobación documental (14/10/2026)

La nueva sección plegable en [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino) incorpora una serie real **ERSSTv5 NOAA 1950-01 a 2026-06** y la evaluación histórica de modelos AR(1) a **1, 2 y 3 meses** frente a persistencia, además de un promedio móvil de tres meses **indicativo, no ICEN oficial**.

- **Control de vigencia:** el archivo ERSSTv5 NOAA tiene **4 meses de desfase respecto de octubre 2026**. Se guardan históricos y evaluaciones; **se bloquean todas las proyecciones actuales** (`prediccion_actual_disponible=false`), sin sustituir los últimos meses por datos OISST.
- **Backtest retrospectivo:** 197, 196 y 195 predicciones verificadas respectivamente. MAE AR(1) = **0,3449 / 0,4952 / 0,6183 °C** a 1/2/3 meses y MAE persistencia = **0,3546 / 0,5282 / 0,6823 °C**. Las mejoras globales NO prueban validez prospectiva; a uno y dos meses el AR(1) empeora en los últimos 12 meses.
- **Control institucional externo, no validación operativa:** se contrastaron ICEN publicados por SENAMHI de febrero, marzo, abril y mayo de 2026 con promedios trimestrales indicativos ERSSTv5 del OAF. Diferencia absoluta media de **0,0075 °C** en esos cuatro registros. Fuentes de SENAMHI enlazadas en el informe.
- **Documentos:** [MODELO_ERSSTV5_FASE6C.md](MODELO_ERSSTV5_FASE6C.md), [código Python](modelos/modelo_ersstv5_nino12_fase6c.py), [contraste institucional CSV](datos/contraste_icen_publicado_2026.csv) y [datos/modelo_ersstv5_nino12_6c.json](datos/modelo_ersstv5_nino12_6c.json).
- **Próximo paso Fase 6D:** localizar ERSSTv5/ICEN actuales de fuente institucional, ampliar contraste de meses y probar ERSSTv6 como producto distinto; iniciar evaluación de predicciones emitidas y archivadas realmente antes de cada evento.

## Fase 6D · Fuente NOAA NCEI ERSSTv5 recuperada y predicción experimental (14/10/2026)

**Resuelto el desfase de datos sin confundir índices.** NOAA NCEI mantiene una serie ERSSTv5 Niño 1+2 actualizada a **septiembre de 2026**, pero sus anomalías están calculadas frente a **1971–2000**. El OAF toma la **sexta columna** (Niño 1+2), calcula mes a mes la media de anomalías durante 1991–2020 y la resta para crear una serie de anomalías **reajustada por el OAF a 1991–2020**. Esta serie es *derivada*, **no un ICEN oficial**.

- Última anomalía mensual derivada: **+4,389 °C, septiembre de 2026**.
- Comparación interna con el archivo CPC ERSSTv5: 918 meses comunes; **MAE entre productos últimos 24 meses comunes: 0,0397 °C**. El control de procedencia pasó. No confundir este MAE de comparación entre fuentes con error predictivo.
- Modelo experimental AR(1) a uno, dos y tres meses: **+4,054 °C (octubre), +3,744 °C (noviembre) y +3,456 °C (diciembre de 2026)**. Referencia trivial de persistencia: **+4,389 °C** en los tres horizontes.
- Aunque el error histórico medio del AR(1) es ligeramente menor que el de persistencia, **el AR(1) es peor en los últimos doce meses a los tres horizontes**; ninguna estimación es considerada una predicción validada de El Niño Costero, lluvia regional o enfermedad agrícola.
- [Informe Fase 6D](MODELO_NCEI_ERSSTV5_FASE6D.md), [motor Python](modelos/modelo_ncei_ersstv5_fase6d.py), [fuente reajustada CSV](datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv), [evaluación walk-forward CSV](datos/ncei_ersstv5_backtest_1a3m.csv), [salida JSON](datos/modelo_ersstv5_ncei_6d.json), [flujo GitHub Actions](.github/workflows/oaf_ncei_ersstv5_fase6d.yml).
- Nuevo panel plegable en [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino). Conserva aparte el panel Fase 6C con su fuente CPC de junio 2026, identificada como histórica y desactualizada.

**Próximo avance recomendado — Fase 6E:** añadir predictores oceánico-atmosféricos de fuentes públicas, generar pronósticos verdaderamente fechados y compararlos prospectivamente con persistencia y modelos de referencia institucional. Sin esta evaluación **no existe predicción OAF operativa**.

## Fase 6E · Nuevas variables agroclimáticas: radiación solar y microclima (14/10/2026)

Se amplió [Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima) con variables **modeladas y pronosticadas por Open-Meteo** para Chiclayo, Jayanca, Motupe y Olmos:

- **Radiación solar global de onda corta:** `shortwave_radiation` actual (W/m²) y `shortwave_radiation_sum` diario (MJ/m²). No confundir con PAR, UV ni sensor en dosel.
- **Déficit de presión de vapor (DPV):** actual y máximo diario (kPa).
- **Viento a 10 m:** actual y máximo diario (km/h).
- **Humedad relativa:** actual y promedio diario (%).
- **ET₀ FAO:** evapotranspiración de referencia diaria (mm), no evapotranspiración real del cultivo.
- **Presión atmosférica superficial:** actual (hPa), no índice SOI.
- **Insolación estimada:** horas diarias de brillo solar, distintas del acumulado de energía.
- Temperatura, precipitación y probabilidad de precipitación se mantienen.

**Análisis de anomalías solares:** el indicador 1996–2025 ahora compara la radiación prevista acumulada en siete días con valores estacionales históricos (ventana ±15 días, P10/P90, ≥25 años válidos). Fuente de **radiación y lluvia: ERA5**, temperatura **ERA5-Land**, según comprobación de disponibilidad con GitHub Actions. Una ausencia de radiación deja su comparación **no evaluable**, sin fabricar ceros ni impedir interpretar separadamente temperatura/lluvia.

**Control con datos reales:** dos localidades pasaron comprobación de variables, formatos y unidades de pronóstico; en octubre de 2019 se encontraron 31/31 valores radiativos con ERA5 y 0/31 con ERA5-Land. El ensayo completo para Motupe confirmó **10.958/10.958 días numéricos de radiación ERA5, lluvia ERA5 y temperatura ERA5-Land durante 1996–2025**. Se corrigió y verificó la fuente histórica usada por el indicador. Ver [metodología y catálogo de variables de Fase 6E](VARIABLES_AGROCLIMATICAS_FASE6E.md) y [pruebas de consulta](tests/test_variables_agroclimaticas_6e.py).

**El próximo uso predictivo no será automático:** radiación, DPV, viento y humedad servirán como covariables candidatas solo después de evaluar errores y utilidad real. La humedad relativa **no sustituye** la duración medida de humectación foliar requerida para modelos de Botrytis. Las variables de meteorología local tampoco sustituyen señales oceánicas/atmosféricas de El Niño Costero.

## Fase 6F · Evaluación del valor predictivo de la radiación (14/10/2026)

Se creó un experimento cuantitativo para comprobar **si incorporar radiación solar, humedad relativa y viento mejora o empeora** el pronóstico de temperatura. A diferencia de una simple regresión sobre observaciones del mismo día, utiliza **predictores de pronósticos archivados con 24 horas de antelación** de Open-Meteo (Previous Runs API); la variable objetivo es temperatura reanalizada por ERA5-Land.

- Tres alternativas comparadas: (A) pronóstico anterior sin corregir, (B) corrección Ridge básica con temperatura y componentes horarios/estacionales, (C) mismo modelo Ridge más radiación, humedad y viento. Regularización fija y normalización aprendida exclusivamente del entrenamiento.
- Entrenamiento 2024–2025; evaluación temporal aislada enero–septiembre 2026; Chiclayo, Jayanca, Motupe y Olmos. Métricas MAE, RMSE, sesgo y remuestreo temporal en bloques; publicar honestamente resultados mejores o peores.
- Prueba de API real en Motupe: **120 horas archivadas para cada predictor y 120 horas equivalentes de referencia**, coincidentes; GitHub Actions lo confirmó.
- Código [benchmark_radiacion_6f.py](modelos/benchmark_radiacion_6f.py), [metodología](FASE_6F_EVALUACION_PREDICTORES.md), [flujo de evaluación](.github/workflows/oaf_benchmark_radiacion_6f.yml) y panel plegable en [Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima).
- Archivos de salida cuando la evaluación termine correctamente: [benchmark_variables_6f.json](datos/benchmark_variables_6f.json) y [errores mensuales](datos/benchmark_variables_6f_mes.csv).
- Este experimento **no constituye aún predicción validada de El Niño Costero ni enfermedades**, y su referencia ERA5-Land es reanálisis, no medición SENAMHI. Los modelos fitosanitarios requieren datos de campo adicionales.

## Fase 6F — Hallazgos iniciales y archivo prospectivo (14/10/2026)

La comparación con pronósticos efectivamente emitidos **24 horas antes** encontró que agregar radiación, humedad y viento disminuyó el MAE de temperatura corregida frente al modelo básico en **Chiclayo (5,95 %) y Olmos (4,97 %)**, pero lo aumentó en **Jayanca (24,38 %) y Motupe (2,11 %)**. Se entrenó con 2024–2025 y se evaluaron 6.552 horas por localidad de enero–septiembre 2026; la referencia es ERA5-Land reanalizado, no sensores SENAMHI. El pipeline generó métricas, pero el primer envío de archivos falló por cambios concurrentes en Git; se corrigió su proceso de publicación. Las variaciones no validan modelos operativos ni atribuyen causalidad a una variable específica.

También quedó registrada **la primera emisión prospectiva real**, correspondiente al 14/10/2026 en Perú, con pronósticos externos del 15 al 21 de octubre para las cuatro localidades: [consultar JSON emitido](datos/pronosticos_emitidos/2026-10-14.json). Incluye temperatura, precipitación, radiación, humedad, viento, DPV y ET₀ con fecha y unidades; permitirá verificar errores una vez sucedan las jornadas previstas. [Método y resultados de Fase 6F](FASE_6F_EVALUACION_PREDICTORES.md).

## Fase 6G · Verificación de pronósticos emitidos antes del evento (15/10/2026)

El OAF ya no solo archiva pronósticos: se implementó una **verificación prospectiva automatizada por fecha de emisión, localidad y horizonte**. Se comprueba temperatura media, precipitación y radiación solar pronosticadas para los siguientes 7 días frente a reanálisis **ERA5-Land (temperatura) y ERA5 (lluvia y radiación)**, con un margen de siete días después de la jornada válida por el retraso de publicación de aproximadamente cinco días.

- El primer pronóstico conservado se emitió el **14/10/2026 en horario Perú** y cubre del 15 al 21 de octubre para Chiclayo, Jayanca, Motupe y Olmos.
- [Estado actual de la evaluación prospectiva](datos/evaluacion_prospectiva_6g.json): **pendiente de reanálisis; 0 de 28 jornadas disponibles**, primera fecha posible de verificación **22/10/2026**. No se declaran aciertos, errores cero ni predicciones verificadas hasta obtener datos.
- [Motor de verificación](modelos/verificar_pronosticos_emitidos_6g.py), [proceso diario](.github/workflows/oaf_verificacion_6g.yml), [CSV auditable](datos/evaluacion_prospectiva_6g.csv) y [metodología](FASE_6G_VERIFICACION_PROSPECTIVA.md).
- Nuevo apartado plegable **Fase 6G** en [Datos climatológicos del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), con futura consulta de MAE, RMSE y sesgo por variable, localidad y horizonte.

**Corrección final de Fase 6F:** el último GitHub Actions terminó exitosamente y publicó [benchmark_variables_6f.json](datos/benchmark_variables_6f.json) y [errores mensuales](datos/benchmark_variables_6f_mes.csv). Los intervalos exploratorios de mejora ampliado vs básico por bloques fueron: Chiclayo **−2,73 % a +15,33 %**, Jayanca **−42,69 % a −9,52 %**, Motupe **−5,48 % a +1,86 %**, Olmos **+1,65 % a +10,14 %**. Solo Olmos presentó mejora positiva en ambos extremos de ese intervalo exploratorio. Un intervalo descriptivo y ERA5-Land como referencia NO equivalen a validación operativa.

## Fase 7A · Primer indicador fitosanitario para Botrytis de arándano (15/10/2026)

Se implementó en [Cultivos → Predicción fitosanitaria](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos) un **indicador exploratorio de periodos atmosféricos prolongados de humedad** relacionados con condiciones que pueden favorecer *Botrytis cinerea*. El objetivo del OAF sigue siendo predecir anomalías climáticas / Niño Costero y riesgos de enfermedades de arándano y vid **con validación científica futura**, sin confundir una señal del clima con infección real.

- **Fundamento externo:** UC IPM describe HR superior a aproximadamente 90 % durante ≥6 horas continuas como contexto que puede favorecer *Botrytis* en general; UF/IFAS destaca floración y humectación prolongada en el arándano. Este criterio **no está validado para los cultivos de Lambayeque**.
- Se analizan siete días completos de pronósticos **horarios externos Open-Meteo**, en Motupe, Jayanca, Olmos y Chiclayo, usando temperatura, HR, lluvia, **radiación solar** y DPV, sin convertirlos en porcentaje de enfermedad ni alerta fitosanitaria. Episodios pueden cruzar medianoche; datos faltantes hacen que el análisis no sea evaluable.
- **Primera emisión efectivamente archivada, 15/10/2026**, para jornadas 16–22/10/2026: **Motupe 2**, **Jayanca 0**, **Olmos 3** y **Chiclayo 0** episodios previstos de HR >90 % por al menos 6 h. Los ceros no equivalen a ausencia de enfermedad.
- La automatización Python/GitHub Actions pasó autopruebas y verificación en vivo. El motor JavaScript y Python coincidieron por localidad al reprocesar el archivo horario, incluidos lluvia, radiación y DPV.
- [Informe Fase 7A](FASE_7A_BOTRYTIS_ARANDANO.md), [motor Python](modelos/botrytis_arandano_humedad_7a.py), [motor web](modelos/botrytis_arandano_humedad_7a.js), [workflow diario](.github/workflows/oaf_botrytis_arandano_7a.yml), [archivo de pronósticos horarios](datos/patrones_botrytis_emitidos/2026-10-15.json), [plantilla vacía de campo](datos/plantilla_monitoreo_botrytis_arandano.csv).

**Próxima etapa 7B:** obtener observaciones de humectación foliar, fenología, temperatura y humedad en el dosel y diagnóstico de *Botrytis* del arándano para estudiar sensibilidad y capacidad predictiva; antes de contar con datos sanitarios reales, este módulo sigue siendo **una comparación de condiciones meteorológicas previstas**, no un modelo de presencia de enfermedad.

## Fase 7B · Validación de señales de humedad del arándano (15/10/2026)

Se realizó y publicó la primera evaluación cuantitativa real de **episodios de humedad atmosférica que podrían favorecer Botrytis**, sin convertirlos en predicciones de infección. Se comparó el pronóstico archivado a horizonte 24 h de Open-Meteo con humedad horaria reanalizada **ERA5** durante **enero–septiembre de 2026 (273 días y 6.552 horas alineadas por localidad)**, preservando el criterio HR >90 % y seis horas continuas de la Fase 7A.

| Localidad | Coincidencias positivas | Falsas señales frente a ERA5 | Omisiones | Precisión positiva |
|---|---:|---:|---:|---:|
| Chiclayo | 7 | 31 | 5 | 18,4 % |
| Jayanca | 16 | 4 | 18 | 80,0 % |
| Motupe | 17 | 111 | 17 | 13,3 % |
| Olmos | 27 | 140 | 10 | 16,2 % |

**Conclusión:** el indicador meteorológico no está preparado para alertar por Botrytis. Hubo muchas falsas señales meteorológicas respecto de ERA5 en Motupe y Olmos. Los resultados difieren entre cuadrículas de distinta resolución; ERA5 NO son sensores del dosel ni datos micológicos. La precisión positiva citada **NO es probabilidad de enfermedad**.

Se implementó además una verificación **prospectiva** independiente de los pronósticos realmente archivados por el OAF: primer pronóstico emitido 15/10/2026 para 16–22/10; **28 jornadas-localidad guardadas**, 0 elegibles/verificadas al ejecutar 15/10 y **primera fecha de comparación posible 23/10/2026** por demora de siete días para disponibilidad ERA5. Todos los ceros de esta inicialización significan datos todavía pendientes, no ausencia de enfermedad.

**Recursos:** [informe técnico Fase 7B](FASE_7B_VALIDACION_HUMEDAD.md), [backtest JSON](datos/botrytis_indicador_7b_backtest.json), [series diarias](datos/botrytis_indicador_7b_diario.csv), [evaluación prospectiva actual](datos/botrytis_humedad_7b_prospectivo.json), [motor de comparación histórica](modelos/validar_indicador_humedad_botrytis_7b.py), [motor de verificación prospectiva](modelos/verificar_patrones_botrytis_emitidos_7b.py) y [panel en Cultivos y riesgo de enfermedades](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos).

**Siguiente Fase 7C:** diseñar y validar registros sanitarios de parcelas de arándano, sensores de humectación foliar, temperatura/HR en dosel y fenología; contrastar la señal horaria con incidencia y diagnóstico de *Botrytis*, con evaluación espacial y temporal independiente. Mientras falten datos reales de infección, no se puede estimar riesgo porcentual ni recomendar fungicidas.

## Fase 7C · Preparación de validación sanitaria de Botrytis en parcelas reales (15/10/2026)

La plataforma ya dispone de la estructura y controles necesarios para empezar, cuando haya observaciones reales, la **evaluación biológica** de *Botrytis cinerea* en arándano: [protocolo 7C](FASE_7C_PROTOCOLO_CAMPO_BOTRYTIS.md), [ficha fitosanitaria de 20 campos](datos/plantilla_7c_monitoreo_botrytis.csv), [ficha horaria de microclima de 12 campos](datos/plantilla_7c_microclima_horario.csv), [validador Python](modelos/validar_campo_botrytis_7c.py), [pruebas de GitHub Actions](.github/workflows/oaf_botrytis_7c_calidad_campo.yml) y [estado público actual](datos/estado_campo_botrytis_7c.json).

- **Monitoreo de campo:** variedad, fenología y floración, unidad muestreada, denominador y unidades sintomáticas; diagnóstico `sin_analisis` / `sospechoso` / `compatible_laboratorio` / `confirmado_botrytis_cinerea` / `descartado`. La confirmación de especie se trata conservadoramente y requiere método molecular específico; síntomas compatibles **no se convierten automáticamente** en incidencia confirmada.
- **Microclima medido:** temperatura/HR en dosel y sensor de humectación foliar binario, con identificación del equipo, altura, hora local Perú UTC−05 y estado de calibración; radiación y lluvia opcionales. Un dato de humectación ausente no significa hoja seca.
- **Privacidad:** futuros datos reales permanecen en `datos/_privados/botrytis_7c/`, excluido de Git. El visor presenta solo estado agregado, sin parcelas identificables.
- **Pruebas 7C pasaron en GitHub Actions:** validación de formato, límites de conteos, métodos de diagnóstico, duplicados, hora con huso y privacidad mediante **datos sintéticos temporales para autopruebas**.
- **Estado real confirmado:** `sin_datos_campo`; no existen en el proyecto observaciones de parcela, cifras de incidencia confirmada, un modelo entrenado de infección ni probabilidades validadas. Tener un validador no equivale a haber validado la enfermedad.

El nuevo panel Fase 7C aparece en [Cultivos y riesgo de enfermedades](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos). Se mantienen las cinco pestañas, la portada y la línea científica independiente de El Niño Costero.

**Próxima prioridad 7D:** emparejar en entorno privado fecha/parcela/fenología con pronósticos archivados ANTES del evento, revisar representatividad espacial y disponibilidad real de sensores y diagnóstico; evaluar capacidad de anticipar incidencia solo tras reunir casos y controles suficientes.

## Fase 8A · Predicciones oceánicas prospectivas mientras se buscan datos fitosanitarios (15/10/2026)

Continúan **dos líneas de trabajo en paralelo**: (1) recopilación y posterior validación de evaluaciones reales de Botrytis en arándano y vid; (2) desarrollo y evaluación prospectiva de predicciones de anomalías climáticas y El Niño Costero. No se suspendió el desarrollo climático por falta de registros fitosanitarios.

Se implementó **un archivo irreversible por mes de origen** de pronósticos experimentales de anomalía oceánica Niño 1+2, NOAA NCEI ERSSTv5 reajustado por OAF a climatología 1991–2020. Registra SHA-256 de datos/modelo, hora de emisión, mes objetivo, AR(1) y referencia de persistencia. **Distingue expresamente emisión intramensual frente a un pronóstico emitido antes del inicio del mes**, y no utiliza observaciones futuras para calificar sus resultados.

- **Primera emisión real, 15/10/2026:** septiembre +4,38867 °C observado como origen; predicción AR(1) para octubre **+4,054 °C (intramensual)**, noviembre **+3,744 °C (antes del mes)** y diciembre **+3,456 °C (antes del mes)**; referencia de persistencia +4,389 °C en todos los horizontes.
- **Aciertos aún no conocidos:** inicialmente 3 estimaciones guardadas, 0 verificadas. Primer control posible de octubre desde **10/11/2026** y únicamente si NOAA ya publicó ese valor. La verificación conserva la cautela ante revisiones retrospectivas de ERSSTv5.
- [Emisión original con sello](datos/pronosticos_oceanicos_emitidos/2026-09.json), [resumen de verificación](datos/verificacion_oceanica_8a.json), [código](modelos/auditoria_oceanica_8a.py), [automatización mensual](.github/workflows/oaf_auditoria_oceanica_8a.yml), [informe metodológico](FASE_8A_AUDITORIA_PROSPECTIVA_ENSO.md) y [apartado en Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino).
- **No** se atribuye habilidad predictiva demostrada al AR(1) ni se equipara anomalía Niño 1+2 derivada a **ICEN oficial ENFEN**, predicción de lluvia o incidencia de enfermedades.

**Fase 8B recomendada:** añadir señales de viento zonal del Pacífico, SOI/presión y calor subsuperficial con fechas auditables para comprobar mejora real sobre persistencia en 1–3 meses; continuar validaciones meteorológicas regionales con radiación y predicciones climáticas 1996–2025.

## Fase 8B · Experimento oceánico-atmosférico NOAA CPC 1–3 meses (15/10/2026)

Se completó la primera comparación de **vientos y presión del Pacífico tropical** como predictores de anomalía Niño 1+2, manteniendo la línea de El Niño Costero en paralelo a la búsqueda de registros reales de enfermedades en arándano y vid.

- **NOAA CPC oficial:** [SOI](https://www.cpc.ncep.noaa.gov/data/indices/soi), [alisios central 850 hPa](https://www.cpc.ncep.noaa.gov/data/indices/cpac850) y [alisios oriental 850 hPa](https://www.cpc.ncep.noaa.gov/data/indices/epac850), junto con TSM Niño 1+2 NOAA NCEI ERSSTv5 reajustada a 1991–2020 por el OAF. Se verificaron **573 meses de información coincidente (1979-01 a 2026-09)**.
- Se comparó **persistencia**, un modelo **TSM sola** y otro **TSM + SOI + dos índices de viento**, los dos últimos mediante Ridge con el mismo `alpha=20`. Walk-forward desde 2010, entrenamiento expansivo que nunca usa resultados posteriores al mes origen, y 1, 2, 3 meses de horizonte.
- **Resultado histórico:** MAE solo TSM frente a TSM + atmósfera: **h1 0,3351 → 0,3537 °C**; **h2 0,4871 → 0,5084 °C**; **h3 0,6121 → 0,6322 °C**. **Agregar estas tres variables empeoró el MAE en los tres horizontes.** En los 12 meses más recientes el modelo ampliado también resultó peor. No sustituir las emisiones oceánicas de Fase 8A.
- **Auditoría:** [método y conclusiones 8B](FASE_8B_PREDICTORES_ATMOSFERICOS_ENSO.md), [datos NOAA atmosféricos](datos/noaa_cpc_predictores_atmosfericos_8b.csv), [JSON de métricas](datos/benchmark_atmosferico_8b.json), [597 predicciones retrospectivas](datos/benchmark_atmosferico_8b_fold.csv), [motor](modelos/benchmark_atmosferico_8b.py), [GitHub Actions](.github/workflows/oaf_benchmark_atmosferico_8b.yml) y [panel Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino).
- **Límites:** archivos históricos CPC pueden contener revisiones (no son versiones fechadas originales); no hay habilidad prospectiva demostrada, el ICEN oficial pertenece a ENFEN, ni es predicción de lluvia o incidencia agrícola. La Fase 8A mantiene su archivo prospectivo sellado y sus controles de evaluación posteriores.

**Próximo paso 8C:** estudiar hipótesis limitadas de desfases de SOI/vientos, contenido de calor oceánico subsuperficial disponible e impacto regional sobre lluvia, temperatura y radiación de Lambayeque (1996–2025), evitando ajustes retrospectivos oportunistas.

## Fase 8C · Calor subsuperficial T300 y SOI/vientos desfasados (15/10/2026)

Se continuó la línea de investigación de **anomalías oceánicas / El Niño Costero** durante la recopilación pendiente de evaluaciones fitosanitarias reales de arándano/vid. Se incorporó una nueva fuente: [temperatura promedio del océano de 0–300 m, T300, NOAA/PMEL-GODAS](https://www.pmel.noaa.gov/tao/wwv/data/t300.dat), para la banda ecuatorial 5°N–5°S, 120°E–80°O. La **anomalía T300 usa base 1981–2010**; la anomalía SST Niño 1+2 NOAA NCEI del OAF usa **1991–2020**. No son medidas idénticas.

Se enfrentaron **persistencia**, un modelo **SST t y t−1**, uno con **T300 t−1** y otro con **T300 t−1 + SOI/vientos t−1**. Todos los modelos Ridge tuvieron regularización fija `alpha=20` y se entrenaron únicamente con meses objetivo **hasta diciembre 2022**. Periodo de prueba aislado: **enero 2023 a septiembre 2026** (44, 43 y 42 orígenes según horizonte h1/h2/h3). No se usaron objetivos de ese periodo para reajustar los parámetros.

| Horizonte | MAE TSM+tendencia | MAE +T300 | MAE +T300+atmósfera |
|---|---:|---:|---:|
| 1 mes | 0,4500 °C | **0,4168 °C** | 0,4917 °C |
| 2 meses | 0,6951 °C | **0,6519 °C** | 0,7782 °C |
| 3 meses | 0,8780 °C | **0,8285 °C** | 0,9345 °C |

**Resultado:** T300 redujo el MAE **7,38 %, 6,21 % y 5,64 %** frente a TSM+tendencia, pero los intervalos exploratorios por bloques cruzaron cero en los tres horizontes; la ganancia **no está demostrada de forma robusta**. Añadir SOI y vientos empeoró de nuevo. Ningún modelo de 8C se promovió a predicción o alerta operativa ni se modificaron las emisiones fechadas de la Fase 8A.

**Implementación auditada:** [informe Fase 8C](FASE_8C_CALOR_SUBSUPERFICIAL_ENSO.md), [motor Python](modelos/benchmark_calor_subsuperficial_8c.py), [workflow de GitHub](.github/workflows/oaf_benchmark_calor_subsuperficial_8c.yml), [serie real T300](datos/noaa_pmel_t300_8c.csv), [informe JSON](datos/benchmark_subsuperficial_8c.json), [129 resultados mensuales](datos/benchmark_subsuperficial_8c_test.csv) y [visualización en Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino). La fuente PMEL llega hasta agosto 2026; el mes t−1 permite emparejarla con el origen SST septiembre 2026, pero no garantiza disponibilidad de la versión histórica exacta al emitir un pronóstico.

**Siguiente etapa 8D:** evaluar relaciones entre Niño 1+2/T300 y anomalías **de temperatura, lluvia y radiación solar en Lambayeque**, con referencia regional 1996–2025 (y OMM 1991–2020). Asimismo diseñar una futura emisión prospectiva de T300 con control estricto de datos disponibles y evaluación frente a persistencia. Mantener ENFEN/ICEN oficial claramente diferenciado.

## Fase 8D · Niño 1+2 y T300 frente al clima regional de Lambayeque (15/10/2026)

Se implementó el primer estudio conjunto de **anomalías de temperatura, lluvia y radiación solar** en **Chiclayo, Jayanca, Motupe y Olmos**, para comprobar si la información Niño 1+2 y T300 aporta capacidad predictiva de condiciones agroclimáticas regionales. Las fuentes meteorológicas son **ERA5-Land (temperatura) y ERA5 (lluvia y radiación)** de Open-Meteo: **reanálisis, no estaciones instrumentales SENAMHI**.

- **Climatología descriptiva:** 1996–2025 completos (30 años). **Normal congelada para el entrenamiento y prueba:** 1996–2022, evitando filtrar los datos posteriores al promedio del periodo de test. Serie mensual descargada y comprobada: 369 meses/localidad, enero 1996–septiembre 2026.
- **Modelos comparados:** climatología cero, persistencia local, Ridge local `alpha=20`, Ridge local+Niño 1+2, Ridge local+Niño 1+2+T300 del mes previo. Entrenamiento con objetivos hasta diciembre 2022 y prueba sobre **44, 43 y 42 meses** a horizontes 1, 2, 3 desde 2023, con **1.548 filas** emparejadas en total.
- **Temperatura, horizonte 3:** modelo local MAE frente a modelo +Niño/T300: **Chiclayo 1,1386→1,0537 °C (7,5 % mejor)**; **Jayanca 1,0053→0,8491 (15,5 %)**; **Motupe 0,7935→0,7396 (6,8 %)**; **Olmos 0,7092→0,6131 (13,6 %)**. También disminuyó en horizontes 1 y 2 para las cuatro localidades.
- **Lluvia y radiación:** añadir Niño 1+2/T300 **empeoró el error frente a Ridge local en las 12 comparaciones por variable**. Para lluvia, incluso la referencia de climatología fue mejor en todas las localidades/horizontes probados. No activar pronósticos de precipitación ni radiación con este modelo.
- **Comprobación de estabilidad adicional:** 2.000 remuestreos emparejados de bloques de seis meses. Solo **Jayanca / temperatura / 3 meses** presentó intervalo exploratorio positivo (**+6,61 % a +22,90 %**); las otras 11 pruebas de temperatura incluyeron cero. No representa significación corregida ni validación prospectiva.
- **Limitación temporal:** la anomalía observada Niño 1+2 del mes t se publica tras el cierre de t; h=1 puede ser **estimación intramensual** y no predicción de mes completo realizada antes de iniciarse. Las fuentes históricas pueden revisarse; NO se han emitido pronósticos operativos regionales del OAF.

**Recursos reales verificados:** [informe Fase 8D](FASE_8D_IMPACTO_AGROCLIMATICO_LAMBAYEQUE.md), [serie mensual regional](datos/lambayeque_mensual_era5_8d.csv), [métricas por región/horizonte](datos/benchmark_impacto_lambayeque_8d.json), [1.548 predicciones retrospectivas](datos/benchmark_impacto_lambayeque_8d_prueba.csv), [intervalos de estabilidad](datos/robustez_impacto_regional_8d.json), [motor](modelos/benchmark_impacto_regional_8d.py), [pruebas de robustez](modelos/robustez_impacto_regional_8d.py) y [panel en Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima). Workflows completos con **success** tras optimizar a llamadas multicoordenada para evitar límite 429.

**Próxima Fase 8E:** emitir y evaluar prospectivamente una variante de temperatura solo con predictores efectivamente disponibles y sello temporal, comprobarla con estaciones SENAMHI; estudiar modelos diferenciados de lluvia y radiación con observaciones independientes. Preservar archivo oceánico 8A y señales oficiales ENFEN separadas; fitosanidad 7C continúa a la espera de registros sanitarios reales.

## Fase 8E · Primera emisión regional prospectiva de temperatura (15/10/2026)

Tras el análisis retrospectivo 8D de temperatura, lluvia y radiación de Lambayeque, el OAF ya **emitió y archivó su primera predicción experimental de temperatura mensual regional**, sin modificar la historia ni afirmar habilidad operativa. Se conservan dos líneas separadas: investigación océano/clima y validación fitosanitaria de arándano/vid pendiente de observaciones de campo.

- **Primera emisión real y congelada:** `datos/pronosticos_temperatura_regional_8e/2026-09.json`, emitida **15/10/2026 01:41:18 hora Perú**, sobre cuatro localidades referenciales: Chiclayo, Jayanca, Motupe y Olmos. Entrenamiento de ambos modelos exclusivamente hasta **2022-12** y anomalías locales con normal fija **1996–2022**; la referencia descriptiva regional continúa siendo 1996–2025.
- **Fuentes existentes:** temperatura ERA5-Land de septiembre 2026, SST Niño 1+2 NOAA NCEI (anomalía septiembre **+4,38867 °C**, base 1991–2020 reconstruida por OAF), y PMEL GODAS T300 agosto **+1,320034 °C**, base 1981–2010. Los datos reanalizados NO son mediciones SENAMHI ni el ICEN/alerta ENFEN.
- **12 estimaciones de temperatura del aire a 2 m (°C) archivadas:** 4 de octubre **intramensuales**, y 8 de noviembre/diciembre **emitidas antes del inicio del mes**. El modelo oceánico (local+Niño1+2+T300) predijo **noviembre/diciembre**: Chiclayo **24,35 / 25,61 °C**; Jayanca **24,83 / 25,89 °C**; Motupe **24,00 / 24,98 °C**; Olmos **24,22 / 25,18 °C**. Se conserva la alternativa **solo local** para comparar desempeño futuro.
- **Integridad del archivo:** hora UTC/Perú, pronósticos originales inmutables, hash SHA-256 de código y tres CSV de fuente, referencia/climatología, predictores del origen y controles para no emitir si TSM/T300/ERA5-Land no están publicados.
- **Verificación automática:** [workflow 8E](.github/workflows/oaf_temperatura_regional_8e.yml) pasó autopruebas, emisión y resumen real; programa comprobaciones los días 12, 19 y 26 de cada mes. La referencia será **ERA5-Land mensual** reanalizada, contrastada **no antes del día 10 del mes posterior** al objetivo y solo con cobertura diaria completa. **Estado inicial: 12 emitidas, 8 anteriores al mes, 0 comparadas; primera verificación posible desde 10/11/2026.**
- [Informe Fase 8E](FASE_8E_PRONOSTICOS_TEMPERATURA_PROSPECTIVOS.md), [motor Python](modelos/pronostico_temperatura_regional_8e.py), [estado en JSON](datos/verificacion_temperatura_regional_8e.json), [CSV inicialmente vacío](datos/verificacion_temperatura_regional_8e.csv) y [panel interactivo en Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima).
- **Lluvia y radiación:** los modelos ENSO/T300 de Fase 8D no demostraron mejorar el MAE frente a referencias sencillas. Por ello 8E **NO publica predicciones nuevas de estas variables ni alertas de inundación**; se propone modelarlas con estrategias diferentes y evaluación independiente.

**Próxima Fase 8F:** buscar y validar registros instrumentales SENAMHI para corroborar las anomalías del reanálisis y preparar modelos específicos de lluvia/nubosidad/radiación; continuar acumulando pronósticos realmente emitidos, sin prometer capacidad prospectiva demostrada por una sola emisión. ENFEN y SENAMHI conservan exclusividad de comunicados oficiales.

## Misión

Construir un observatorio cuyo **objetivo principal es predecir**, de manera progresiva y científicamente verificable, **(1) posibles anomalías climáticas en Lambayeque, incluidos episodios y evolución de El Niño Costero**, y **(2) condiciones de riesgo y, tras validación, posible ocurrencia de enfermedades agrícolas en arándano y vid**. Integra observaciones, pronósticos oceánico-atmosféricos, bibliografía científica, datos fitosanitarios y evaluación independiente. Los gráficos, boletines y datos históricos sirven para desarrollar y evaluar esas capacidades predictivas.

**Estado actual:** la nueva arquitectura está **planificada**, no constituye aún un sistema de predicción propio validado, ni emite alertas climáticas o fitosanitarias operativas.

## Cuatro fases prioritarias

| Fase | Objetivo | Estado |
|---|---|---|
| **3Z** | Modernizar fuentes oficiales, monitoreo reciente y trazabilidad ENFEN/SENAMHI/satélites | **En progreso · CHIRPS v3 integrado** |
| **4A** | Modelos de anomalías y pronósticos probabilísticos meteorológicos | Pendiente |
| **4B** | Riesgo fitosanitario de arándano basado en condiciones y observaciones de campo | Pendiente |
| **4C** | Evaluación prospectiva, validación independiente y comunicación de alertas | Pendiente |

Plan detallado: [PLAN_MAESTRO_OAF_2_0.md](PLAN_MAESTRO_OAF_2_0.md).  
Protocolo de estados y alertas: [PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md](PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md).  
Catálogo de fuentes priorizadas: [datos/catalogo_fuentes_operativas_3z.csv](datos/catalogo_fuentes_operativas_3z.csv).  
Plan de fases legible por máquinas: [datos/plan_operativo_oaf_2_0.json](datos/plan_operativo_oaf_2_0.json).

## Fase 3Z — primera fuente reciente en producción de datos (14/10/2026)

**CHIRPS v3:** se descargaron y verificaron archivos GeoTIFF mensuales de octubre de 2025 a agosto de 2026 (11 meses, 55 estimaciones de píxel para cinco puntos referenciales del OAF). **Septiembre de 2026 todavía no estaba publicado** en la URL de consulta y quedó como faltante. Se preservaron el SHA-256 de los rasters, la fecha UTC de consulta, ubicación exacta de la celda, resoluciones y URLs. CHIRPS es una **estimación espacial mezclada satélite/pluviómetros**, no una observación SENAMHI ni un pronóstico.

**ENFEN:** está preparado el sistema semanal de verificación de comunicados, pero el servidor ENFEN no resolvió DNS durante la primera ejecución en GitHub Actions. La aplicación muestra `no_verificado` y enlaza directamente a [comunicados ENFEN](https://enfen.imarpe.gob.pe/comunicados/); **no inventa** un estado actual ni emite alertas propias.

**Automatización:** dos GitHub Actions los lunes para CHIRPS y ENFEN; el resultado del último monitoreo se expone en el [panel 3Z del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#monitoreo3z). La actualización depende de la disponibilidad de las fuentes y los despliegues de GitHub Pages, no es un servicio garantizado en tiempo real.

Archivos: [monitoreo CHIRPS](MONITOREO_CHIRPS_RECIENTE_3Z.md), [CSV reciente](datos/chirps_v3_reciente_3z.csv), [auditoría](datos/auditoria_rasters_chirps_3z.json), [estado CHIRPS](datos/estado_monitoreo_3z.json), [informe ENFEN](MONITOREO_ENFEN_3Z.md) y [estado ENFEN](datos/estado_enfen_3z.json).

## Datos y transparencia científica

- El observatorio conserva las fases históricas **3N–3Y** y todos sus datos originales y cálculos reproducibles.
- Base SENAMHI aportada: **1 109 meses-estación observados completos, 1996–2015**; 79 combinaciones estación-año completas y último año completo común **2012**. Se requieren fichas instrumentales adicionales para confirmar códigos y emplazamientos históricos.
- Se analizaron retrospectivamente PISCOp v3, CHIRPS v3 y ERA5-Seamless sobre meses completos históricos; no está demostrada independencia externa en los 15 pares estación-producto.
- Los valores mensuales publicados en boletines DZ2 de 2024–2025 se conservan por separado como evidencia documental preliminar, sin transformarlos en series diarias completas.
- **No se imputan días/meses faltantes ni se publica un acumulado anual observado de años incompletos.** La vigilancia de un día o semana recientes **sí puede realizarse** con datos realmente disponibles y de calidad verificada, sin esperar que termine el año.
- CHIRPS, IMERG y otros gridded son **estimaciones**, los modelos pronosticados son **pronósticos** y los pluviómetros son **observaciones instrumentales**: nunca se confunden.
- Las alertas oficiales sobre El Niño Costero corresponden a **ENFEN** y los avisos meteorológicos oficiales a **SENAMHI**. El OAF enlazará esas fuentes fechadas y evitará emitir alertas propias hasta demostrar validez.

Política histórica: [CRITERIO_COBERTURA_OFICIAL.md](CRITERIO_COBERTURA_OFICIAL.md).  
Resultados de cobertura: [RESULTADO_COBERTURA_OFICIAL.md](RESULTADO_COBERTURA_OFICIAL.md).  
Bitácora técnica completa: [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md).

## Fuentes institucionales a integrar en Fase 3Z

- **ENFEN** — https://enfen.imarpe.gob.pe/comunicados/
- **SENAMHI** — https://www.senamhi.gob.pe/
- **CHIRPS v3 (Climate Hazards Center)** — https://www.chc.ucsb.edu/data/chirps3
- **NASA GPM / IMERG** — https://gpm.nasa.gov/data/imerg
- **ECMWF** — https://www.ecmwf.int/en/forecasts

Estas fuentes tienen estados distintos: **CHIRPS v3 mensual ya está conectado**, con una actualización semanal programada y extracción real comprobada hasta agosto de 2026. La consulta ENFEN está implementada, pero su última ejecución **no pudo resolver el servidor institucional**, de modo que se muestra como no verificada y requiere revisar directamente el comunicado oficial. Las demás fuentes recientes aún no están integradas; no se deben anunciar como activas.

## Herramientas

Python, análisis estadístico, GitHub Actions, sensores remotos y SIG, con énfasis en **bajo presupuesto**, control de calidad, accesibilidad pública y aplicaciones en sanidad vegetal. La precisión dependerá de la calidad de los datos, no de presentar un modelo complejo.

---
*Proyecto científico en desarrollo. Ninguna visualización experimental sustituye los comunicados ENFEN, avisos SENAMHI ni el diagnóstico agronómico en campo.*
