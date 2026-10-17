# Fase 8R — Evaluación predictiva retrospectiva y control de transferencia espacial de anomalías

**OAF-Lambayeque · octubre de 2026 · entorno experimental, no emisión de pronósticos operativos**

## 1. Objetivo y relación con las fases anteriores

La fase 8Q encontró grandes contrastes de temperatura histórica absoluta entre ambientes de los transectos V1 y V2 (hasta 8,06 °C entre sus cuatro puntos intermedios de V2), a la vez que las *anomalías térmicas mensuales* eran bastante semejantes dentro del mismo sistema de reanálisis.

**Hipótesis 8R:** una anomalía térmica del mes siguiente podría estimarse mejor combinando su información local pasada y la señal común regional del mes anterior. Esta es una hipótesis sobre series modeladas, **no una predicción del Niño Costero, ni una delimitación de zonas homogéneas, ni un modelo fitosanitario validado**.

Se implementó una comparación fuera del periodo de entrenamiento, reproducible y con una prueba adicional en la que se retiene un píxel térmico completo durante el ajuste de coeficientes.

## 2. Datos realmente utilizados

- **Fuente:** ERA5-Land, variable diaria `temperature_2m_mean`, obtenida anteriormente con Open-Meteo Historical Weather API y almacenada con fecha, URL, JSON original comprimido y SHA-256 en la fase 8Q.
- **Muestras:** los **10 puntos intermedios** de los transectos V1a, V1b y V2; sus series históricas cubren 1996–2025 con 360 meses agregados a partir de los días originales.
- **Control espacial:** los 10 puntos corresponden a **solo siete centros distintos de rejilla ERA5-Land**. Tres ubicaciones adicionales reutilizan celdas ya representadas; para entrenar, seleccionar y comparar el error principal, **se cuenta una sola vez cada centro de celda**. Las diez series se publican individualmente solo como desgloses descriptivos.
- **Variables:** temperatura histórica y anomalía de temperatura mensual. **No se utilizaron** precipitación, radiación, ENSO, viento, humedad, cuencas ni datos térmicos instrumentales SENAMHI como predictores; estos factores requieren fases posteriores.
- Las estimaciones climatológicas, valores objetivo y parámetros provienen del **mismo sistema de reanálisis**. Este diseño no estima precisión frente a sensores ni garantiza que siete rejillas próximas sean espacialmente independientes.

## 3. Separación estricta del tiempo

| Uso | Periodo | Regla |
|---|---|---|
| Normal térmica local para cada mes calendario | **1996–2010** | Usar exclusivamente los primeros 15 años; **prohibido normalizar con la serie completa 1996–2025** al evaluar 2016–2025 |
| Ajuste de coeficientes | **1997–2010** | Regresión sobre el objetivo de cada mes y predictores del mes anterior |
| Selección de una única estrategia entre las cuatro | **2011–2015** | Elegir menor RMSE validado; ninguna decisión depende del test |
| Evaluación reservada | **2016–2025** | 120 objetivos mensuales por celda × 7 celdas = **840 pruebas**; en cada paso, solo se usan datos del mes anterior para estimar el actual |

El OAF continúa usando 1996–2025 como **periodo descriptivo general del proyecto**; sin embargo, durante este backtest se requiere una **normal fija 1996–2010** para evitar que la climatología del futuro del test se infiltre en el entrenamiento.

**Nota temporal:** esto es una evaluación retrospectiva de predicciones *a un mes*, alimentadas en cada momento por la observación modelada real del mes anterior. No se trata de predicciones realmente emitidas en 2015, ni confirma que ERA5-Land esté disponible inmediatamente después de finalizar el mes. La latencia de datos y la disponibilidad en operación requieren otra evaluación.

## 4. Cuatro métodos comparados

1. **Climatología:** predice anomalía térmica = 0 °C, usando la normal local fija 1996–2010.
2. **Persistencia:** predice para el mes objetivo la anomalía observada en el mes anterior **en la misma ubicación**.
3. **Señal regional rezagada:** predice el promedio de las anomalías del mes anterior de **otras celdas térmicas distintas**. Excluye la celda del objetivo y no sobrerrepresenta puntos que comparten un mismo píxel.
4. **Modelo jerárquico lineal:** combina intercepto, rezago térmico local y señal regional rezagada. Sus coeficientes se estiman con una regresión ridge (penalización 1,0 en pendientes, intercepto sin penalizar) sobre el periodo de ajuste. **No emplea Tmedia del mes objetivo como predictor.**

Coeficientes calibrados exclusivamente con 1997–2010, congelados antes del test:

| Coeficiente | Valor |
|---|---:|
| Intercepto | 0,000242 |
| Anomalía térmica local de mes anterior | **0,757747** |
| Señal regional rezagada, excluyendo píxel objetivo | **0,123632** |

Estas cifras son parámetros del ensayo y no deben interpretarse como efectos físicos causales ni trasladarse a otras subregiones sin evaluación.

## 5. Resultado real de validación y de prueba reservada

### Periodo de selección 2011–2015, sin consultar el test

| Método | RMSE de validación |
|---|---:|
| Climatología | 0,645432 °C |
| Persistencia | 0,416145 °C |
| Señal regional rezagada | 0,441655 °C |
| **Modelo jerárquico** | **0,400824 °C** |

**Se eligió el modelo jerárquico exclusivamente por su RMSE de validación.**

### Periodo de prueba estrictamente retenido 2016–2025

| Método | RMSE | MAE |
|---|---:|---:|
| Climatología | 0,748643 °C | 0,567104 °C |
| Persistencia | 0,381327 °C | 0,299992 °C |
| Señal regional rezagada | 0,458211 °C | 0,355181 °C |
| **Modelo jerárquico seleccionado** | **0,363584 °C** | **0,284107 °C** |

**Reducción relativa del RMSE** en este conjunto histórico reservado:
- **51,43 % frente a climatología**, calculado como `1 − RMSE(modelo)/RMSE(climatología)`.
- **4,65 % frente a persistencia**, por la misma fórmula.

La evaluación corresponde a **840 predicciones retrospectivas de 7 centros de celda distintos**. El CSV público también contiene **1.200 registros de 10 puntos**, identificando su celda de origen; los registros adicionales no deben interpretarse como información espacial independiente.

Las reducciones observadas son **descriptivas del test** y deben confirmarse estadísticamente con bloques temporales y nuevas regiones independientes. La aparente ventaja frente a climatología puede depender del periodo base corto 1996–2010 frente a tendencias posteriores; por ello es crucial mantener persistencia como referencia.

## 6. Control adicional de transferencia espacial de coeficientes

Se realizó un ensayo de **dejar una celda térmica fuera por vez** entre las siete:

1. Se separa una celda completa de ERA5-Land como objetivo de transferencia.
2. Se recalculan los predictores regionales del resto **excluyendo esa celda** de los promedios en ajuste y validación.
3. Los coeficientes se entrenan con las otras seis celdas utilizando 1997–2010 y se elige el método con 2011–2015 exclusivamente sobre esas seis.
4. Se evalúa en **2016–2025 sobre la celda retenida**, utilizando su propia climatología histórica de 1996–2010 y su observación del mes anterior, ambos supuestos explícitos.
5. Se repite para las siete celdas; se promedian los errores sobre 840 objetivos retenidos de una celda por turno.

| Diagnóstico espacial | RMSE combinado |
|---|---:|
| Modelo seleccionado sin ajustar sobre la celda retenida | **0,363771 °C** |
| Persistencia sobre las mismas celdas y meses | **0,381327 °C** |
| Climatología sobre las mismas celdas y meses | 0,748643 °C |

La reducción del RMSE frente a persistencia en esa transferencia parcial es **4,60 %**. En los siete pliegues resultó seleccionado el método jerárquico.

**Limitación crítica:** este control prueba transferencia de coeficientes **entre los siete píxeles cercanos de la misma fuente ERA5-Land**, no extrapolación a sitios sin climatología local previa ni independencia de sensores. Las estaciones reales, la separación espacial por cuencas y los periodos posteriores de emisión real son indispensables para evaluar la transferibilidad hacia todo Lambayeque.

## 7. ¿Qué cambia para la estrategia OAF-Lambayeque?

Estos resultados apoyan continuar investigando un sistema **jerárquico**:

- **Capa común:** caracterizar una señal de anomalía regional/subregional que pueda compartir parte del movimiento mensual.
- **Capa local:** conservar normales térmicas independientes por sitio/celda, elevación, orientación, valle/piedemonte/montaña y eventual ajuste instrumental.
- **Validación:** contrastar si el modelo local+regional supera persistencia y climatología en cada subregión, en registros posteriores a la emisión y en estaciones independientes. No asumir que los siete píxeles representan todos los pisos climáticos de Lambayeque.
- **Extensiones:** lluvia, humedad, radiación y viento necesitarán pruebas de origen/píxel y modelos específicos; una misma celda ERA5 de lluvia en cuatro puntos del V2 no prueba homogeneidad hídrica.

**No se activan** pronósticos operativos zonales, alertas de ENFEN, predicciones de enfermedad de arándano o vid ni polígonos homogéneos por este experimento. No existe aquí una validación SENAMHI externa.

## 8. Archivos y reproducción

- [Motor Python de evaluación 8R](modelos/validacion_anomalias_8r.py), biblioteca estándar, pruebas de fechas, SHA fuente, píxeles, validación y ridge.
- [Pruebas sintéticas aisladas de fugas temporales y espaciales](tests/test_validacion_anomalias_8r.py); jamás utilizadas como fuente de resultados meteorológicos.
- [Workflow 8R](.github/workflows/oaf_validacion_8r.yml), que ejecuta tests, recalcula desde los archivos ERA5-Land originales auditados en 8Q y compara dos ejecuciones idénticas.
- [Reporte JSON validado](datos/validacion_predictiva_8r/estado_validacion_8r.json), métricas por los cuatro modelos, centro de celda y pliegue espacial.
- [CSV de 1.200 estimaciones históricas reservadas](datos/validacion_predictiva_8r/predicciones_retrospectivas_8r.csv).
- [Visor de predicción experimental](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones) en el módulo **8R**, con comparación de RMSE de validación y prueba, 10 sitios y transferencia espacial.

## 9. Próximo nivel de rigor: fase 8S

Ampliar la evaluación desde 7 celdas térmicas de 8Q hacia las climatologías regionales 8P hasta cubrir los **81 testigos previstos**, sin contar píxeles repetidos. Introducir validación espacial verdaderamente separada (por cuenca/piso y distancia), periodos de evaluación deslizantes y emisiones mensuales archivadas antes del mes objetivo. Buscar termómetros oficiales SENAMHI y estaciones de campo para verificar sesgos y habilidad instrumental. Posteriormente integrar señales ENSO/ENFEN de forma informativa sin presentarse como predicciones oficiales.

**Estado de fase 8R:** experimento retrospectivo reproducible exitoso frente a ERA5-Land. **Validación operativa/instrumental, pronóstico ENSO y zonas homogéneas certificadas: ninguno.**

## Referencias

- [Copernicus ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
- Muñoz-Sabater et al. (2021), [ERA5-Land: a state-of-the-art global reanalysis dataset for land applications](https://doi.org/10.5194/essd-13-4349-2021).
