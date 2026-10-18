# Fase 10H — Entrenamiento terminado: Random Forest frente a GCN, precipitación y océano + atmósfera NASA POWER

**OAF-Lambayeque · octubre de 2026 · Auditoría reproducible, no alerta operativa.**

## Resultado que corresponde publicar

La fase 10H **recuperó y auditó efectivamente 14.040 filas sector-mes** de datos públicos de NASA POWER, además de los archivos CHIRPS v3 FINAL y de los predictores oceanoatmosféricos regionales de la fase 10F. Se terminaron los reentrenamientos Random Forest y Graph Convolutional Network (GCN), con cinco bloques espaciales y 4.680 probabilidades retrospectivas de prueba.

La [ingesta NASA](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39085555539) y el [reentrenamiento y las seis pruebas](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39085711303) están finalizados correctamente en GitHub Actions. CSV, hashes SHA-256, parámetros y evaluaciones quedan archivados.

### ¿Cuál es mejor entre las dos redes y bosques?

**Random Forest, para el objetivo y los factores efectivamente evaluados.** La evaluación usa **2.340 casos sector-mes** de 2021–2025 (39 sectores × 60 meses), de ellos **247 positivos** al superar el percentil 90 de CHIRPS de cada sector calculado SOLO con entrenamiento 1997–2015.

| Método | Brier ↓ | PR-AUC ↑ | ROC-AUC ↑ |
|---|---:|---:|---:|
| **Climatología sectorial estacional** | **0,062884** | **0,60414** | **0,93172** |
| RF: CHIRPS + océano regional (fase 10F) | 0,069247 | 0,43511 | 0,90520 |
| **RF: CHIRPS + océano + NASA POWER (10H)** | **0,072036** | **0,39737** | **0,89277** |
| GCN: CHIRPS + océano + NASA POWER (10H) | 0,077423 | 0,35626 | 0,86583 |
| GCN: CHIRPS + océano (fase 10F) | 0,078348 | 0,35446 | 0,86646 |

**Decisión reproducible:**
1. Entre los dos algoritmos de IA que usan **todos los factores de 10H**, Random Forest obtiene **mejor Brier, PR-AUC y ROC-AUC** que GCN.
2. Entre todas las variantes de IA ensayadas, el **RF con lluvia y océano (10F) es más preciso** en Brier global que el RF con las variables NASA POWER añadidas. La inclusión de NASA **empeoró el Brier de RF +0,002789** frente a 10F, mientras GCN mejoró marginalmente **−0,000925**. Más covariables no implican más habilidad.
3. La **climatología sectorial estacional** obtiene el menor Brier global y la mayor PR-AUC de los métodos. Por eso **no se ha demostrado un modelo de IA superior a la línea base**.
4. Se permite mostrar **Random Forest como mejor IA experimental entre RF y GCN bajo estos datos**, no como único pronosticador superior a toda alternativa ni como alerta válida del Niño o enfermedades agrícolas.

## ¿Se sostiene la ventaja de RF todos los años?

Delta de Brier **RF NASA menos GCN NASA**: **−0,005387** (negativo favorece RF).

| Año | Brier RF NASA | Brier GCN NASA | Ventaja |
|---|---:|---:|---|
| 2021 | 0,053971 | **0,049689** | GCN |
| 2022 | 0,067478 | **0,061013** | GCN |
| 2023 | **0,138358** | 0,153523 | RF |
| 2024 | **0,035775** | 0,045194 | RF |
| 2025 | **0,064599** | 0,077697 | RF |

**Intervalo de remuestreo exploratorio 95 % por cinco años: [−0,013189; +0,002415]**, incluye cero. No permite afirmar con significación robusta que RF gana siempre. El remuestreo por **siete grupos espaciales gruesos** arroja [−0,007116; −0,000484], pero el número de grupos es pequeño, no son necesariamente meteorológicamente independientes ni compensa la dependencia temporal, por lo que **no es una prueba confirmatoria**. La mejora en 2023 es relevante pero no autoriza una alerta El Niño.

La [auditoría emparejada con diferencias por año, pliegue, piso y grupo NASA](datos/modelos_multivariables_10h/auditoria_comparacion_10h.json) permite consultar ambos resultados.

## Datos físicos que entran al modelo

**Precipitación (variable de pronóstico y predictores de meses anteriores):**
- CHIRPS v3 FINAL, lluvia de los 39 sectores (1996–2025).
- Umbrales P90 por sector calculados exclusivamente durante 1997–2015.
- Variables explicativas lluvia mensual rezagada **dos o más meses**, estacionalidad y características estáticas geográficas y de grafo.

**Pacífico regional, también con rezago de al menos dos meses:**
- Anomalías SST en regiones Niño 1+2 y Niño 3.4 de NOAA.
- Índice SOI y alisios del Pacífico central y oriental.
- Viento marino en puntos de muestreo frente a Pimentel y el norte de Lambayeque.
- La **RONI centrada** se usa solo para clasificación retrospectiva, no para entrenar un predictor que conozca meses futuros.

**Atmósfera NASA POWER, rezago dos meses:**
- Temperatura media (T2M), humedad relativa (RH2M), viento a 10 m (WS10M), radiación solar descendente (ALLSKY_SFC_SW_DWN), presión superficial (PS) y temperatura de rocío (T2MDEW).
- Fuente NASA POWER mensual: meteorología **MERRA-2** y radiación de productos satelitales **SRB/CERES**. **No es el mismo producto que ERA5**, ni datos de estaciones.
- Solo **siete agrupaciones aproximadas de celda para 39 sectores**, con meteorología de ~0,5 × 0,625 grados y radiación frecuentemente más gruesa. Las observaciones no son espacialmente independientes. No representan condiciones exactas de fincas.
- **Advertencia de homogeneidad:** radiación SRB/CERES contiene cambios de origen alrededor de 2001; no se ha demostrado una serie radiométrica sin discontinuidades. Se archiva el origen de cada solicitud y su SHA.

**No se incluyeron como si existiesen:** corrientes geostróficas de 1996–2015 (archivo local solo disponible 2017–2025); nubosidad, déficit de presión de vapor, humedad foliar ni humedad de suelo **homologados para los 39 sectores**, o fenómenos de escala sinóptica que todavía requieran series verificables. No se justifica la frase «todos los factores meteorológicos que existen». **Se usaron los factores con historia y unidades auditadas disponibles.**

## Validez experimental y límites de publicación

- **Protocolo temporal común:** entrenamiento 1997–2015, selección de hiperparámetros 2016–2018, calibración de probabilidades 2019–2020 y prueba 2021–2025.
- **Protocolo espacial:** cinco bloques sin píxeles CHIRPS superpuestos. Pero algunos sectores de distintos bloques comparten celdas atmosféricas NASA/ERA5: no se puede declarar independencia total de covariables.
- **Objetivo de predicción:** probabilidad de superar la lluvia mensual **P90 de CHIRPS**, no su fecha/hora exacta, ni lluvia horaria torrencial, ni una declaración ENFEN.
- **Dato retrospectivo y fuga histórica:** NASA, NOAA y CHIRPS consultados después del evento pueden contener revisiones; no se conservaron **versiones originales as-issued**, por lo que estos son *hindcasts* retrospectivos, no simulaciones de emisión probadas.
- **No existe contraste con estaciones SENAMHI independientes**, instrumentación de campo, ni comparación prospectiva con avisos emitidos. No existe una medición de sensibilidad de falsas alarmas en aplicaciones reales a productores.
- **Enfermedades de arándano y vid:** requieren registros de infección, incidencia, patógenos y microclima de planta, no pueden inferirse directamente de la clasificación P90.
- **Niño costero y Niño global:** requieren etiquetas y objetivos específicos de Niño 1+2, Niño 3.4 y otras variables oceanoatmosféricas; la lluvia intensa no equivale a un episodio del fenómeno.

**Veredicto de publicación:** se puede publicar en la sección **«Modelos predictivos del autor — investigación experimental»** el resultado RF y la comparación íntegra con GCN y climatología, junto a incertidumbre, fuentes, código y limitaciones. **NO** se puede anunciar todavía como modelo **validado operacionalmente**, pronóstico meteorológico oficial, recomendación agronómica ni predicción confiable de El Niño costero.

## Productos y reproducción

[Panel público de resultados](evaluacion-modelos-atmosfericos-10h.html) · [Código RF/GCN](modelos/comparacion_rf_gcn_nasa_10h.py) · [Fuente NASA POWER](modelos/ingesta_nasa_power_10h.py) · [Pruebas automáticas](tests/test_nasa_multivariable_10h.py) · [Métricas reproducibles](datos/modelos_multivariables_10h/evaluacion_rf_gcn_nasa_10h.json) · [Predicciones históricas por sector](datos/modelos_multivariables_10h/probabilidades_rf_gcn_nasa_10h.csv) · [Auditoría comparativa](datos/modelos_multivariables_10h/auditoria_comparacion_10h.json) · [Metadatos NASA](datos/nasa_power_10h/auditoria_fuentes_10h.json).

**Siguiente control antes de activar avisos:** evaluación «as-issued» con datos disponibles en cada fecha, contraste contra estaciones independientes, inclusión de pronósticos de clima institucionales fechados, recalibración de eventos extremos por impacto agrícola, evaluación de costes de falsas alarmas y objetivos independientes ENSO/fitopatología.
