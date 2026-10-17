# Fase 9B — Validación robusta de anomalías y eventos extremos

**Fecha de preparación:** 17 de octubre de 2026. **Estado:** protocolo reproducible integrado al repositorio; evaluación empírica 9B pendiente de ejecutar sobre las predicciones retrospectivas originales de 9A. No se declara habilidad nueva ni cambio de modelo operacional.

## Punto de partida verificado en la fase 9A

La fase 9A comparó el modelo de referencia con viento + SST frente a extensiones con humedad relativa (HR), déficit de presión de vapor (VPD) y HR+VPD. Se reportaron 17 280 predicciones retrospectivas, 1 440 evaluaciones probabilísticas y cinco periodos. HR+VPD mejoró el MAE en **5/12 comparaciones de temperatura y 6/12 de precipitación**, pero el Brier de extremos en solo 1/12; en las otras 11/12 comparaciones de extremos se deterioró. Esos resultados **no acreditan mejora estadísticamente significativa**, no justifican sustituir la referencia y requieren auditar sus archivos y la definición de evento.

## Preguntas de investigación

1. ¿Las diferencias de habilidad entre la referencia y HR+VPD se mantienen al reagrupar datos por año de emisión y al excluir periodos particulares?
2. ¿La aparente mejora es diferente para eventos de lluvia intensa, temperatura anómala y eventos habituales?
3. ¿Cambian las conclusiones entre zonas del litoral, valles Motupe–Olmos y montaña al controlar relieve, altitud y cuenca?
4. ¿Las probabilidades de eventos extremos están calibradas y ofrecen ventaja sobre una climatología estimada *solo con el entrenamiento*?

## Diseño de evaluación

**Unidades y trazabilidad.** Usar únicamente parejas predicción–observación que correspondan al mismo objetivo, horizonte, fecha y localidad. Registrar fecha de emisión, fecha objetivo, versión y SHA de datos/modelo, fuente de observación, unidades, porcentaje de datos válidos, bandera de fuga temporal y tipo de producto (instrumento, reanálisis, satélite). Rechazar duplicados, ausencia de sellos temporales y predicciones que incorporen predictores posteriores al instante de emisión.

**Validación temporal.** Repetir la comparación con cortes *rolling-origin*: cada entrenamiento termina antes del primer dato validado. Agrupar diferencias de pérdida por mes objetivo y remuestrear **bloques de 12 meses** (más una sensibilidad a 6 meses); 2 000 réplicas como mínimo con semilla fija. Publicar intervalo percentil al 95 % de la ganancia frente a referencia: pérdida(ref) – pérdida(candidato); positivo favorece candidato. Realizar *leave-one-year-out* como diagnóstico de fragilidad, sin entrenar con el futuro. Mantener 1996–2025 como referencia descriptiva regional y OMM 1991–2020 para comparabilidad; la climatología para pronósticos debe estimarse exclusivamente con el periodo de entrenamiento.

**Extremos.** Estimar umbrales P90/P95 de lluvia y temperatura por estación del año, únicamente en entrenamiento. Para lluvia incluir frecuencias de días húmedos y magnitudes; no usar MAE como criterio único de episodios raros. Reportar Brier, Brier Skill Score frente a climatología, diagrama de fiabilidad, AUC si existen ambas clases, precisión, sensibilidad, falsas alarmas, número de casos y prevalencia. Si hay menos de 20 eventos positivos por comparación, rotular «muestra insuficiente» y no emitir conclusión robusta. Calcular intervalos por bloques y ajuste Benjamini–Hochberg para las familias de 12 pruebas; no confundir p-valores exploratorios con validación prospectiva.

**Estratificación climática.** Partir de los 69 puntos/6 bandas altitudinales preliminares de 8N y el posterior inventario DEM de 420 puntos descrito en el rediseño del portal. Conservarlos como **muestras preliminares**, no como zonas homogéneas comprobadas. Cruzar elevación, pendiente, orientación, cuenca, distancia a costa y series 1996–2025 de temperatura/lluvia/radiación/HR/viento. Estandarizar por variables, comprobar estabilidad de agrupamientos por años y vecindad espacial, exigir cobertura de observaciones y publicar tamaños y dispersión intrazona. No asignar pronósticos individuales a celdas no evaluadas.

## Regla de decisión

Mantener el modelo viento+SST como **referencia experimental**. Solo proponer HR/VPD como candidato específico de variable/horizonte/zona si (a) mejora el promedio de pérdida, (b) el IC de bloques de la diferencia excluye cero en dirección favorable, (c) sobrevive corrección por multiplicidad, (d) no degrada peligrosamente extremos ni calibración y (e) conserva coherencia en cortes temporales y evaluación prospectiva. **Ningún resultado 9B permite declarar alertas ENFEN, SENAMHI o sanitarias del OAF.**

## Recursos técnicos

- Script de evaluación: `modelos/validacion_robusta_9b.py`.
- Entrada canónica: CSV con columnas `fecha_objetivo,localidad,horizonte,variable,observado,pred_ref,pred_candidato`; opcionalmente `prob_ref,prob_candidato,evento,subzona,fecha_emision`. `evento` debe definirse con umbrales congelados fuera de prueba, no con cuantiles calculados en prueba.
- Salida: JSON con tamaños muestrales, MAE, diferencias, IC por bloques, puntuación de Brier si aplica y advertencias. Sin series reales emparejadas, **el script no inventa resultados**.
- Evaluación de software con datos sintéticos solo prueba el código; no prueba habilidad en Lambayeque.

## Presentación en el portal

Incluir en **Investigación y datos → Validación científica** las tablas de estabilidad, número de extremos, intervalos, origen de observaciones, controles de fuga y versión de datos. En **Análisis de clima regional**, mapas y zonas altitudinales mostrar leyenda bajo cada visualización y distinguir claramente «estratificación preliminar» de «zona validada». En **Monitoreo del Niño y anomalías climáticas**, mantener separadas salidas experimentales y boletines oficiales. En **Sanidad vegetal**, conservar distinción entre clima favorable y riesgo/enfermedad observada.

**Criterio de cierre de 9B:** resultados reales reproducibles sobre los archivos 9A, sin fuga temporal, con intervalos de confianza, comparación con climatología y diagnóstico geográfico; hasta entonces: fase metodológica implementada, resultados por verificar.

## Referencias metodológicas

- OMM, *Joint Working Group on Forecast Verification Research*: https://community.wmo.int/site/knowledge-hub/governance/research-board/scientific-steering-committee-ssc/joint-working-group-forecast-verification-research
- WMO Lead Centre for Sub-seasonal Prediction: https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification
- OMM, *Guidelines on the Definition and Characterization of Extreme Weather and Climate Events* (2023): https://digitallibrary.un.org/record/4012890

**Actualización tras fase 9C (17/10/2026):** se ejecutó la validación retrospectiva con 10 000 remuestreos anuales y 36 contrastes de error. Ninguna de las 36 comparaciones superó el control conservador de multiplicidad; los 12 conjuntos P90 tuvieron menos de 20 eventos. Ver [resultados completos de fase 9C](FASE_9C_RESULTADOS_VALIDACION.md) y [matriz estadística](datos/validacion_9c/resultados_9c.json).
