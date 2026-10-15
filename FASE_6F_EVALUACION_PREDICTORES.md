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
