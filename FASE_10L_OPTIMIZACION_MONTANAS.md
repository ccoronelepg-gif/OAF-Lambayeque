# Fase 10L — Mejora responsable del modelo de lluvia en vertientes medias y alturas andinas

**OAF-Lambayeque · Análisis experimental 1996–2025, fecha 17/10/2026.**

## Propósito

Mejorar la predicción de precipitación mensual en los once sectores de **vertientes andinas medias (8) y alta montaña (3)** del conjunto experimental OAF-9K. La variable objetivo es exclusivamente **lluvia CHIRPS mensual en milímetros**; las probabilidades de excedencia P90/P95 se conservan de la evaluación 10K **sin atribuir al entrenamiento 10L una mejora inexistente**. No se incluyen enfermedades, infecciones, incidencia fitosanitaria ni lluvia intensa horaria.

La capa 9K es exploratoria, no una cartografía oficial de ecorregiones MINAM. Los 11 sectores de montaña tienen cotas preliminares entre 1.665–3.839 metros, agrupados en dos bandas de paisaje. Las diferencias de error en milímetros se comparan con climatología de cada sector.

## Qué se mejora realmente

Antecedentes auditados fase 10K:

| Paisaje | Sectores | MAE Random Forest 10K | MAE climatología |
|---|---:|---:|---:|
| Vertientes medias | 8 | 33,3271 mm | **21,8805 mm** |
| Cumbres y alturas | 3 | 52,2841 mm | **29,0930 mm** |

La diferencia de error es crítica: Random Forest sobreestima de forma importante en altura, y no es prudente presentar el mismo grado de confianza que en la costa.

### Entradas físicas y arquitectura

Se conserva el histórico de lluvia **1996–2025**, modelos con rezagos **t−2 o anteriores** y la referencia sectorial fija 1997–2015. Se incorporan **solamente características conocidas antes de cada predicción**:

- Climatología de lluvia **por sector y mes**, calculada exclusivamente con 1997–2015.
- Desviación estándar climatológica mensual previa a 2016 y promedio histórico por sector.
- Elevación DEM preliminar y rango altitudinal de los nodos DEM del polígono.
- Piso medio/alto y vecindad física experimental 9K, con la salvedad de que los polígonos no están homologados a MINAM.
- Rezagos de lluvia CHIRPS t−2, t−3, t−4, t−6, t−12 y estacionalidad.
- Ablación opcional con variables oceánicas NOAA y atmosféricas NASA POWER, con t−2 o más, sin completar artificialmente series horarias ni corrientes sin historia verificada.

Se ensayan seis familias **exclusivamente Random Forest**:

| Familia | Cobertura de entrenamiento | Transformación |
|---|---|---|
| Global lluvia normalizada | Todos los sectores; mayor peso a medios/altos | Desviación en mm relativa a 20 + climatología |
| Global lluvia logarítmica | Todos los sectores; mayor peso a medios/altos | log(1 + observación) − log(1 + climatología) |
| Especialista montaña normalizada | Solo sectores medios/altos disponibles en entrenamiento | Desviación normalizada |
| Especialista montaña logarítmica | Solo sectores medios/altos disponibles en entrenamiento | Anomalía logarítmica |
| Global océano/atmósfera normalizada | Lluvia + indices oceánicos/viento + NASA POWER con rezagos | Desviación normalizada |
| Global océano/atmósfera logarítmica | La misma base multivariable | Anomalía logarítmica |

Los registros de montaña del conjunto de entrenamiento reciben mayor peso que los costeros cuando se estima el regresor global. Se asigna peso adicional a la temporada noviembre–abril como hipótesis experimental. **No se utiliza lluvia del mes objetivo ni del mes anterior**, por coherencia con el retraso de CHIRPS Final. Las variables de 2021–2025 no se utilizan para entrenar, seleccionar hiperparámetros ni ponderaciones.

### Decisión conservadora

El proceso elige familia y peso entre **0; 0,2; 0,4; 0,6; 0,8; 1,0** únicamente por MAE de validación 2016–2018 en sectores del conjunto de entrenamiento. Se compara explícitamente contra climatología por banda. Un peso cero significa **no usar RF**, sino la referencia climatológica del sector. No se considera una victoria de RF cuando el método mejor en realidad es climatología.

**Contingencia cartográfica identificada durante el primer ensayo:** los **tres sectores de cumbres** pueden quedar juntos en un mismo bloque geográfico de prueba, sin muestras independientes de alta montaña en los bloques de entrenamiento. El protocolo está preparado para **abstenerse y emitir la climatología** en esos casos, sin declarar entrenado/validado un especialista de alta montaña. La evaluación de las vertientes medias es separada.

Bandas de incertidumbre empíricas al 90 % calculadas con **2019–2020** en los sectores reservados; esta cifra no es garantía nominal debido a la dependencia espacial/temporal y cambios en el régimen de lluvia.

## Validación y límites

- Entrenamiento: **1997–2015**. Selección: **2016–2018**. Calibración: **2019–2020**. Prueba retrospectiva: **2021–2025**.
- El modelo nuevo se compara **en los mismos 660 casos sector-mes de prueba** con RF 10K y climatología.
- La evaluación de 2023 incluye sesgo de predicción y MAE desagregado en vertientes medias y alturas.
- No existe una verificación genuina de datos disponibles *as-issued* antes de cada predicción histórica; CHIRPS Final y NASA/NOAA se procesaron retrospectivamente.
- No hay estaciones meteorológicas SENAMHI independientes para certificar acierto en altura.
- Si el error baja porque se utiliza climatología, **atribuir la mejora al mecanismo de abstención**, no a un RF especialista validado.
- Las etiquetas de «ecorregión» son agrupaciones experimentales del observatorio, no límites oficiales.

La literatura científica indica que la complejidad topográfica y la ausencia de pluviómetros afectan a las estimaciones por satélite. Referencias: [Validación CHIRPS en Andes centrales argentinos, Rivera, Marianetti y Hinrichs (2018)](https://doi.org/10.1016/j.atmosres.2018.06.023), [Validation of CHIRPS in coastal complex terrain (2023)](https://doi.org/10.1016/j.cscee.2023.100452) y [Validación con pluviómetros andinos — NASA TRMM](https://ntrs.nasa.gov/citations/20150011095). Estos estudios orientan el protocolo; **no son evidencia directa de que nuestro modelo 10L ya haya sido validado**.

## Resultados, gráficos y reproducibilidad

- [Dashboard interactivo de mejora montañosa](optimizacion-lluvia-montana-10l.html): mapa filtrable, dos bandas, sectores, años, serie CHIRPS/RF nuevo/RF 10K/climatología y cuadros comparativos.
- [Entrenamiento y selección](modelos/optimizacion_montana_rf_10l.py)
- [Tests](tests/test_optimizacion_montana_10l.py)
- [Flujo de ejecución automática](.github/workflows/oaf_10l_montanas.yml)
- [Evaluación computada de montaña 10L](datos/montanas_10l/evaluacion_montanas_10l.json)
- [CSV de 660 pronósticos históricos comparados](datos/montanas_10l/predicciones_lluvia_montanas_10l.csv)
- [Mapa GeoJSON de 39 sectores con 11 objetivos](datos/montanas_10l/sectores_mejora_montana_10l.geojson)
- [Series mensuales del dashboard](datos/montanas_10l/series_montana_10l.json)

**No habilitar predicciones actuales ni alertas por lluvia fuerte con estos ensayos.** La siguiente validación independiente debe incluir estaciones de montaña, metadatos de resolución de CHIRPS y archivo de pronósticos emitidos antes del fenómeno.

