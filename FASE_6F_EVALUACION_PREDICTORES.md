# OAF-Lambayeque — Fase 6F: ¿la radiación, la humedad y el viento mejoran la predicción meteorológica?

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque  
**Estado científico:** experimento retrospectivo de corrección de temperatura; **no** modelo operacional de El Niño Costero ni predicción de enfermedades confirmadas.

## Pregunta verificable

¿Añadir tres variables meteorológicas pronosticadas **antes del evento** (radiación solar global, humedad relativa y velocidad del viento) reduce el error de temperatura pronosticada a 24 horas frente a un modelo básico?

Esta es una fase preparatoria dentro de dos objetivos del OAF: (1) predicción de anomalías climáticas, incluido El Niño Costero a través de modelos oceánico-atmosféricos diferenciados, y (2) predicción fitosanitaria de arándano y vid, posteriormente validada con microclima y observaciones sanitarias de campo.

## Diseño sin filtración temporal directa

**Predictores:** [Open-Meteo Previous Model Runs API](https://open-meteo.com/en/docs/previous-runs-api), campos horarios **`_previous_day1`**, archivados con horizonte nominal de 24 horas antes de cada hora válida: `temperature_2m_previous_day1`, `shortwave_radiation_previous_day1`, `relative_humidity_2m_previous_day1` y `wind_speed_10m_previous_day1`.

**Referencia para verificación:** temperatura a 2 m del **reanálisis ERA5-Land** de la [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), alineada por la misma hora local America/Lima. **No son observaciones de termómetros SENAMHI**; la validación instrumental es pendiente.

**Localidades aproximadas:** Chiclayo, Jayanca, Motupe y Olmos. Las cuadrículas de pronóstico y ERA5-Land pueden no coincidir exactamente; se conservan las coordenadas devueltas para auditarlo.

**Separación predefinida:**
- Entrenamiento: enero 2024–diciembre 2025.
- Prueba temporal separada: enero–septiembre de 2026.
- Sin búsqueda ni selección de hiperparámetros según el conjunto de 2026. `alpha=20` fijo en los dos modelos y estandarización ajustada únicamente en el entrenamiento.
- Se descartan horas con valores ausentes o fuera de rangos plausibles: no se imputan ceros ni se rellenan con datos simulados.

## Tres estrategias comparables

**A. Pronóstico original**: temperatura `temperature_2m_previous_day1` publicada por el modelo externo, sin modificación.

**B. Corrección básica**: regresión Ridge (penalización 20, intercepto sin penalizar), usando temperatura pronosticada y componentes de seno/coseno de hora del día y fecha dentro del año. La predicción corregida puede diferir de la A porque aprende sesgos entre pronósticos y ERA5-Land.

**C. Corrección ampliada**: mismo método y variables B más **radiación solar, humedad relativa y viento pronosticados** con desplazamiento de 24 horas. No se incorporan valores observados después de la hora de emisión.

### Qué significa la comparación

Se calculan MAE (error absoluto medio), RMSE y sesgo para A, B y C en las mismas horas de 2026. La mejora de C frente a B se expresa como:

`mejora_relativa = 1 - MAE_C / MAE_B`.

Se acompaña de una prueba **descriptiva** de estabilidad, remuestreando errores emparejados en bloques de 14 días y obteniendo un intervalo exploratorio 95 %. Este intervalo NO reemplaza la validación prospectiva, la evaluación regional con estaciones independientes ni la comprobación en diferentes años ENSO.

**Un resultado positivo en alguna localidad no demuestra que la radiación cause la mejora** (colinealidad con nubosidad, hora, temperatura y humedad). Un modelo ampliado puede incluso resultar peor por sobreajuste o cambios de régimen meteorológico. En ese caso no se debe adoptar automáticamente.

## Estado de comprobación de fuentes

Se verificó una muestra real **1–5 de julio de 2025** para Motupe con **120/120 horas disponibles** por cada predictor (temperatura, radiación, humedad y viento) en Previous Runs, coincidentes temporalmente con 120 horas de temperatura ERA5-Land. El control automático terminó en estado *success*; esta prueba es una **verificación de cobertura y unidades, no de precisión predictiva**.

## Implementación y reproducibilidad

- [Motor de prueba](modelos/benchmark_radiacion_6f.py): Python 3.11 con biblioteca estándar. Incluye solución de regresión Ridge, división temporal y remuestreo por bloques.
- [Prueba de API histórica](tests/probe_prevruns_6f.py).
- [Ejecución verificable de GitHub Actions](.github/workflows/oaf_benchmark_radiacion_6f.yml).
- [Resumen estructurado del benchmark](datos/benchmark_variables_6f.json), publicado solo si todas las fuentes y pruebas pasan.
- [Errores por mes y localidad](datos/benchmark_variables_6f_mes.csv), publicado al completar la evaluación.
- [Panel del observatorio](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), en apartado plegable Fase 6F.

La evaluación no debe considerarse completada únicamente por la existencia del código o del panel; su resultado estará sujeto a la ejecución automática y la lectura de los CSV/JSON generados.

## Límites para enfermedades y El Niño Costero

- El análisis tiene como objetivo **temperatura meteorológica a 24 horas**, no presencia o incidencia de *Botrytis cinerea* en arándano, oídio de vid ni ningún patógeno confirmado.
- La radiación, el viento y la humedad son covariables candidatas que **podrían** contribuir a estudiar el secado superficial o las condiciones del dosel, pero no equivalen a una medida real de humectación foliar ni justifican tratamiento fitosanitario.
- La evolución de El Niño Costero requiere modelos oceánicos y atmosféricos de mayor escala, series Niño 1+2, ICEN y fuentes institucionales ENFEN; el resultado de un benchmark de temperatura regional no valida esa línea.
- La evaluación con ERA5-Land puede reflejar similitud entre modelos y no precisión frente a instrumentos de campo. Hay que contrastar con estaciones SENAMHI y sensores agrícolas para usos operativos.

## Próximos pasos

Después del resultado con datos reales: comparar el desempeño por localidad, estación, precipitación y rangos de radiación; verificar si la radiación mejora de forma estable respecto del modelo B y del pronóstico original; conservar emisiones diarias fechadas para auditoría prospectiva; comenzar diseño de estudio de humectación foliar y sanidad de arándano.

**Principio del OAF:** publicar errores y limitaciones aunque un modelo más complejo obtenga peores resultados que el básico.

## Primer procesamiento con datos reales: hallazgos

En la primera ejecución GitHub Actions, el programa concluyó íntegramente los cálculos con **17.105 horas de entrenamiento y 6.552 horas del periodo de prueba por localidad**. El envío automático del JSON falló por una actualización simultánea del repositorio (error Git `non-fast-forward`); los errores numéricos abajo proceden del registro de ejecución real. La publicación del JSON y CSV se repetirá tras corregir el flujo de envío.

| Localidad | MAE externo original | MAE corrección básica | MAE con radiación + HR + viento | Diferencia ampliado vs básico |
|---|---:|---:|---:|---:|
| Chiclayo | 0,9180 °C | 0,8463 °C | 0,7959 °C | **+5,95 %** |
| Jayanca | 1,0659 °C | 0,7424 °C | 0,9234 °C | **−24,38 %** |
| Motupe | 1,2410 °C | 1,5424 °C | 1,5749 °C | **−2,11 %** |
| Olmos | 1,7102 °C | 1,7432 °C | 1,6566 °C | **+4,97 %** |

**Interpretación:** la combinación ampliada mejoró Chiclayo y Olmos respecto del modelo básico, pero **empeoró Jayanca y Motupe**. En Motupe el pronóstico original fue mejor que ambos modelos de corrección. Estas variaciones son comparaciones en una **misma prueba temporal retrospectiva** contra ERA5-Land. No implican validez prospectiva ni permiten determinar el aporte causal individual de la radiación. Los intervalos por bloques estarán en el JSON completo si concluye su publicación.

## Nuevo archivo prospectivo antes del evento

Se implementó un archivo automático diario de los pronósticos meteorológicos externos de **siete jornadas futuras completas** para cuatro localidades. La primera emisión comprobada fue el **14 de octubre de 2026 en horario de Perú**, registrada antes del periodo previsto **15–21 de octubre**.

- Script: [archivar_pronosticos_prospectivos_6f.py](modelos/archivar_pronosticos_prospectivos_6f.py).
- Flujo diario: [oaf_archivo_prospectivo_6f.yml](.github/workflows/oaf_archivo_prospectivo_6f.yml).
- Primera emisión real: [2026-10-14.json](datos/pronosticos_emitidos/2026-10-14.json).
- La instantánea almacena hora UTC exacta, fecha local, localidad y coordenadas de celda, origen Open-Meteo, unidades y diez variables: temperatura media/máxima/mínima, lluvia, radiación global, HR media, viento máximo, DPV máximo, ET₀ y duración de insolación.
- Este archivo contiene **pronósticos externos**, NO predicciones propias de El Niño Costero o infección. Un archivo emitido en el futuro no debe sobrescribir la primera emisión de su fecha; el script impide tal sustitución.

Este método servirá de base para verificar errores en predicciones nuevas, pero **todavía no confirma aciertos** sobre jornadas aún futuras. Faltan confrontaciones con observaciones instrumentales y registros fitosanitarios.
