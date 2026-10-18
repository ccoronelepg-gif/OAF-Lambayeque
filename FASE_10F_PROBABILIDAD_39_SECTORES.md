# Fase 10F — Evaluación probabilística espacial sobre 39 sectores CHIRPS

**Fecha:** 17 de octubre de 2026 · **Estado:** experimento retrospectivo; prohibido habilitar alertas automáticas.

## ¿Qué cambia respecto a 10E?

En 10E se entrenaron RF y GCN con temperatura, radiación, humedad, viento, lluvia, SST y SOI de **cuatro localidades**; la climatología superó a ambos modelos de IA en Brier global. No sería válido declarar que esa matriz multivariable representa 39 sectores.

En 10F se aprovecha el archivo científico `datos/validacion_9w/matriz_sectores_chirps_9w.csv` —**39 sectores × 360 meses = 14.040 registros** de lluvia CHIRPS v3 FINAL, con 1996–2025 completos— y se enlazan variables oceánicas **regionales** procedentes de NOAA/CPC y viento marino de dos puntos, compartidas por todos los sectores según el mes. Esta integración **no convierte** los índices Niño 1+2 y Niño 3.4 en mediciones de la temperatura costera local de cada polígono.

No se trasladan temperaturas, radiación, humedad ni viento terrestre de las cuatro localidades a los 39 sectores. Tampoco se imputan corrientes geostróficas de 2017–2025 a los periodos anteriores. Estos campos requieren extracción ERA5/ERA5-Land geográfica/temporal específica con metadatos por celda, huella SHA, control de altitud y contraste instrumental.

## Pregunta científica

¿Cuánto mejora una evaluación probabilística de **meses de precipitación alta relativa al sector** al agregar SST Niño1+2/Niño3.4, SOI, alisios y vientos marinos regionales a las lluvias pasadas?

**Objetivo:** variable binaria lluvia CHIRPS mensual ≥ percentil 90 **histórico de cada sector**, calculado exclusivamente sobre 1997–2015 (228 meses). Los sectores reservados necesitan historia previa para calcular su normal y climatología; esto no es una extrapolación a un lugar sin ningún dato climático previo. Los umbrales P90 no son oficiales ni equivalen a inundación o alerta ENSO.

## Comparaciones en la misma muestra
1. **RF_lluvia** (rezagos locales t−2, t−3, t−4, t−6, t−12, media t−2:t−4, estacionalidad, características espaciales y vecindad).
2. **GCN_lluvia**, grafo de sectores construido por relaciones espaciales.
3. **RF_lluvia_oceano** agrega regionales t−2: anomalías SST Niño1+2/Niño3.4, SOI, alisios centrales/orientales y viento del mar frente a Pimentel y norte de Lambayeque.
4. **GCN_lluvia_oceano** con los mismos predictores.
5. **Climatología sectorial estacional**, construida solo a partir de historia 1997–2015 del sector; comparación fundamental para verificar habilidad adicional.

**Ablación:** la comparación entre variantes solo lluvia vs lluvia+océano permite identificar si las covariables regionales aportan habilidad con estos datos, bajo el mismo calendario.

## Validación y protección
- Cinco bloques geográficos derivados de centroides y píxeles CHIRPS no compartidos, conservados desde 10C. No se permite entrenamiento de pesos usando etiquetas del sector de prueba.
- **Entrenamiento 1997–2015**, tuning 2016–2018 (exclusivamente sectores de entrenamiento), calibración Platt sobre registros históricos 2019–2020 del sector reservado y prueba futura 2021–2025.
- **Brier Score** (menor es mejor), PR-AUC (mayor es mejor), ROC-AUC, logloss, desgloses por pisos y bloques, años y régimen RONI retrospectivo.
- **RONI centrado no se usa como predictor**, sino como estrato retrospectivo; no equivale a situación oficial de El Niño costero (ENFEN).
- La calibración 2019–2020 del propio sector reservado requiere observaciones pasadas; se debe distinguir de transferir un modelo a una zona sin historial.
- No se cuenta con datos CHIRPS v3 Final «as-issued». El producto retrospectivo actual puede contener revisiones que no existían en emisión (véase [CHC/UCSB](https://www.chc.ucsb.edu/data/chirps3)).
- Las clases P90 son eventos **relativos a precipitación mensual CHIRPS**, no episodios extremos independientes ni umbrales de impacto agrícola. No sustituye datos pluviométricos SENAMHI.
- Los estratos ecológicos siguen siendo exploratorios, especialmente `cota_negativa_revisar`.

## Auditoría de datos preejecución
Los 39 sectores contienen 360 registros cada uno. Con el P90 calculado únicamente sobre 1997–2015, durante 2021–2025 hay **247 casos sector-mes positivos de 2.340**. Los datos regionales NOAA SST Niño1+2/Niño3.4 archivados para cuatro localidades coinciden exactamente por mes (0 divergencias), por lo que solo se emplea una serie *regional compartida*, no una supuesta observación independiente para cada sector.

## Decisión del modelo
La prueba nombra un **candidato experimental** solo si el modelo probabilístico logra simultáneamente:
- Brier menor y PR-AUC mayor que la climatología sectorial estacional.
- Al menos 15 casos positivos en prueba.
Si no, se abstiene de señalar una IA como superior. En cualquier caso, **modelo_operativo_ganador=null**, **alertas_habilitadas=false** y ninguna afirmación de predicción ENSO/fitosanitaria certificada.

**Modelos desarrollados/entrenados por el autor** no significa avisos emitidos, revisados o validados oficialmente por ENFEN/SENAMHI. El OAF diferencia en el menú «Información y avisos oficiales» y «Modelos del autor — experimental».

## Recursos reproducibles
- [Python y predictores](modelos/probabilidad_39_sectores_10f.py)
- [Pruebas de no fuga y procedencia](tests/test_probabilidad_10f.py)
- [CI de cinco bloques](.github/workflows/oaf_10f_39_sectores.yml)
- [Resultados completos, cuando termine la corrida](datos/extension_10f/evaluacion_39_sectores_10f.json)
- [CSV de probabilidades por sector](datos/extension_10f/probabilidades_39_sectores_10f.csv)
- [Visor por modelo y piso](evaluacion-sectores-10f.html)

## Resultados verificados · CI 10F concluida

[Ejecutar la auditoría / ver la corrida](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39083056802): siete pruebas de integridad exitosas, entrenamiento de cinco bloques y guardado en GitHub de **11.700 probabilidades retrospectivas**. Muestra de evaluación: **39 sectores × 60 meses = 2.340 objetivos**, **247** con precipitación ≥P90 del sector (10,56 %).

| Modelo | Brier ↓ | PR-AUC ↑ | ROC-AUC ↑ |
|---|---:|---:|---:|
| Climatología sectorial estacional | **0,062884** | **0,60414** | **0,93172** |
| RF lluvia + señales oceánicas regionales | 0,069247 | 0,43511 | 0,90520 |
| RF lluvia | 0,074842 | 0,44542 | 0,88586 |
| GCN lluvia + océano | 0,078348 | 0,35446 | 0,86646 |
| GCN lluvia | 0,084757 | 0,29251 | 0,84332 |

**Mejor IA por Brier en la muestra:** RF con señales oceánicas. La incorporación de regionales redujo Brier **0,005595** en RF y **0,006408** en GCN. En RF oceánico la PR-AUC **bajó** de 0,44542 a 0,43511 respecto a RF solo lluvia: no afirmar que mejoraron *todas* las métricas. La climatología obtuvo mejor Brier y PR-AUC globales; por eso `modelo_ia_destacado_si_supera_climatologia = null`, `modelo_operativo_ganador = null` y `alertas_habilitadas = false`.

### Episodios de 2023

En **2023**, 107 de los 468 objetivos sector-mes fueron ≥P90 del sector. Brier 2023: **RF + océano 0,121150**, **climatología 0,136595**, **GCN + océano 0,149943**, RF solo lluvia 0,169208 y GCN solo lluvia 0,165520. En ese año particular RF + océano obtuvo menor Brier que la climatología; no prueba superioridad en los cinco años.

Para RF + océano, la diferencia de Brier respecto a la climatología fue **+0,020618** en 2021, **+0,020588** en 2022, **−0,015444** en 2023, **+0,003248** en 2024 y **+0,002805** en 2025 (negativo favorece RF); la mejora **no es estable** temporalmente.

### Heterogeneidad ecológica

Los pisos muestran comportamientos distintos. En **montaña alta**, por ejemplo, GCN + océano obtuvo Brier 0,062627 y RF + océano 0,065048, frente a climatología 0,056546; allí la climatología conserva mejor Brier que ambos. En **montaña media**, RF + océano 0,062839 y GCN + océano 0,064398, frente a climatología **0,056669**. No seleccionar globalmente RF para todo piso por el solo menor Brier entre IA.

### Estratificación retrospectiva RONI

Los 312 casos sector-mes clasificados descriptivamente RONI cálido en 2021–2025 contienen solo **4 eventos ≥P90**: una muestra insuficiente para evaluar de forma sólida la habilidad sobre el fenómeno El Niño costero. RONI global cálido no representa necesariamente la lluvia excepcional del primer trimestre 2023, que ocurrió antes de la consolidación del índice RONI cálido. Este índice **no se empleó como predictor** ni reemplaza a ENFEN.

**Interpretación:** en 10F los algoritmos entrenados por el autor se mantienen como *investigación experimental*; las salidas son **probabilidades de lluvia mensual relativa por sector** frente a CHIRPS v3 FINAL retroprocesado, no probabilidades oficiales de El Niño, pronósticos operativos actuales ni diagnósticos de infección de arándano/vid.

## Fase 10G
Extraer de ERA5/ERA5-Land, en puntos o rejillas con soporte espacial adecuadamente declarado, temperatura, radiación solar, humedad, presión atmosférica, viento y humedad del suelo para cada sector; verificar temporalidad de cada versión, no interpolar sin fundamento; luego comparar nuevos modelos con exactamente las mismas particiones y contra climatología. ENSO/El Niño costero y enfermedades de vid/arándano exigirán **modelos objetivo separados**, entradas fechadas y validación independiente de incidencia y vigilancia institucional.
