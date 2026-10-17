# Fase 8T — ¿Aporta Niño 1+2 a la predicción de anomalías térmicas mensuales de Lambayeque?

**OAF-Lambayeque · Ejecución auditada 17 de octubre de 2026 · reanálisis climático 1996–2025**

## 1. Propósito

La fase 8S obtuvo una mejoría histórica modesta, aproximadamente 4,28 % en RMSE frente a persistencia, al combinar la anomalía térmica del mes anterior de cada sitio con la señal previa de otros píxeles. La fase **8T** examina, sin suponer el resultado favorable, si **añadir la anomalía de temperatura superficial del mar Niño 1+2** aporta una mejora *adicional* frente a ese modelo térmico.

**La pregunta no es** si existe El Niño Costero o si ENFEN debería emitir una alerta. Tampoco se estima lluvia ni incidencia de enfermedades de arándano o vid: el objetivo continúa siendo la **anomalía de temperatura del aire del mes siguiente**, reconstruida en ERA5-Land.

## 2. Evidencia oceánica original

Se recuperó la serie mensual pública de [NOAA Climate Prediction Center, archivo `sstoi.indices`](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices), con las columnas `YR MON NINO1+2 ANOM NINO3 ANOM NINO4 ANOM NINO3.4 ANOM`. La columna empleada es **`NINO1+2 ANOM`** (región 0–10°S, 90–80°O). No debe confundirse con el **Índice Costero El Niño (ICEN)** utilizado en distintos contextos por instituciones peruanas.

La consulta quedó congelada en el repositorio:

- **Fecha UTC de consulta:** 2026-10-17 03:29:47.
- **SHA-256 de la respuesta original:** `4cf4938114c9f6130566d76ef280cddb3e601444d26d47237a9d2348628e5317`.
- **Cobertura para este estudio:** 360 meses de enero de 1996 a diciembre de 2025.
- [Fuente comprimida original](datos/oceano_8t/noaa_cpc_sstoi_indices.txt.gz) y [metadatos verificables](datos/oceano_8t/noaa_cpc_sstoi_indices.meta.json).

**Limitación crítica de reproducibilidad histórica:** se trata de una *versión actual de una serie histórica revisable*. Aunque durante el backtest se utilice exclusivamente el valor de Niño 1+2 correspondiente a **dos meses antes del objetivo**, su versión publicada en 2026 **no demuestra que ese valor exacto, con esa climatología de referencia y sin revisiones posteriores, estuviera disponible en la fecha histórica de la predicción**. El resultado es un contraste retrospectivo *pseudo-prospectivo*, **no un experimento de versiones de datos disponibles en tiempo real**. No autoriza pronósticos operativos ni probabilidades ENFEN.

## 3. Protocolo predictivo y protección contra fugas de datos

El experimento hereda, sin redefinir las fechas tras examinar resultados, las **cinco particiones temporales y cuatro bandas latitudinales** de 8S. Solo utiliza **65 testigos** de la última muestra regional completa verificada, correspondientes a **50 centros térmicos ERA5-Land diferentes**, después de excluir dos puntos con DEM ≤5 m pendientes de revisión costera.

**Métodos definidos previamente:**

1. **Base 8S:** regresión ridge con intercepto + anomalía térmica propia del mes anterior + anomalía media del mes anterior de otros píxeles térmicos distintos.
2. **Base + Niño 1+2:** igual regresión ridge, con un cuarto predictor: **anomalía SST Niño 1+2 del mes objetivo menos dos meses**. Se usa `t−2`, no `t` y no una previsión oceánica futura.

Para cada corte, ambos modelos se ajustan solo con sus años de entrenamiento y **se selecciona el modelo de menor RMSE durante la validación previa al test**. El resultado de cada prueba reservada se publica íntegro, incluyendo **los errores de la variante oceánica aun si no fue seleccionada**.

La prueba espacial retiene una de cuatro bandas completas al ajustar los coeficientes y seleccionar el modelo, y la excluye también de las anomalías regionales previas utilizadas en entrenamiento. Se permite expresamente disponer de la climatología propia previa y la anomalía de `t−1` de la celda retenida: **no es extrapolación a una ubicación sin historial local**.

## 4. Resultados calculados, test histórico 2012–2025

Se evaluaron **8.400 pares mes-centro de celda** sin solapamiento entre periodos de prueba tanto en el contraste temporal como en el control de bloque espacial.

| Evaluación | RMSE base 8S sin océano | RMSE estrategia seleccionada en validación | Variación relativa respecto a 8S |
|---|---:|---:|---:|
| Cinco cortes temporales | **0,448275 °C** | 0,448468 °C | **−0,0431 %** (empeora) |
| Cuatro franjas espaciales retenidas × cinco cortes | 0,448167 °C | **0,448123 °C** | **+0,0098 %** (mejora prácticamente nula) |

En el control espacial, la persistencia por sí sola obtuvo **0,468228 °C**. La estrategia preseleccionada por validación —oceánica cuando mejoraba la validación, base cuando no— superó la persistencia un **4,2938 % en RMSE**. Esta cifra es casi la misma que el resultado 8S **sin Niño 1+2** (4,2845 %).

### Qué pasó en cada ventana temporal

| Prueba reservada | Modelo elegido *antes* del test | RMSE 8S (°C) | RMSE variante con Niño 1+2 (°C) |
|---|---|---:|---:|
| 2012–2014 | 8S sin océano | 0,467761 | 0,467160 |
| 2015–2017 | 8S + Niño 1+2 | 0,416788 | 0,417769 |
| 2018–2020 | 8S sin océano | 0,403200 | 0,404362 |
| 2021–2022 | 8S sin océano | 0,446455 | 0,447304 |
| 2023–2025 | 8S + Niño 1+2 | 0,499807 | 0,499793 |

El método oceánico solo fue elegido en **dos de cinco cortes temporales**. Dentro de los 20 controles de ventana y franja, se eligió en **ocho**. En 2015–2017 fue seleccionado según validación pero **empeoró** sobre 8S en la prueba reservada. No se debe elegir retrospectivamente el modelo que funcionó mejor en el test: hacerlo destruiría el carácter fuera de muestra del experimento.

### Comportamiento por elevación en controles con bandas retenidas

| Estrato DEM | RMSE estrategia preseleccionada (°C) | RMSE 8S sin índice oceánico (°C) | ¿Mejora? |
|---|---:|---:|---|
| Planicie costera (DEM >5 m) | 0,566022 | 0,566437 | Marginal |
| Valle bajo | 0,476069 | 0,476122 | Prácticamente igual |
| Piedemonte | 0,413775 | 0,413984 | Marginal |
| Montaña baja | 0,361358 | **0,361147** | No |
| Montaña media | 0,322474 | **0,321652** | No |
| Montaña alta | 0,332158 | **0,330746** | No |

No declarar mayor habilidad costera ni peor respuesta de montaña con estos pequeños contrastes: el muestreo, los píxeles de reanálisis y el número desigual de centros afectan el resultado.

## 5. Interpretación científica para el proyecto

**Resultado negativo o inconcluyente — científicamente útil:** el índice revisado de Niño 1+2 retrasado dos meses **no demostró una ventaja adicional consistente** para pronosticar un mes de anomalía térmica del aire en esta muestra y con el esquema lineal evaluado.

Esto **no prueba que El Niño Costero carezca de efectos climáticos**. La pregunta estudiada fue muy específica: una sola variable oceánica, un solo desfase temporal, un modelo lineal y un objetivo de temperatura media del aire. Para el objetivo central de OAF-Lambayeque —anticipar anomalías regionales asociadas al Niño Costero— será necesario evaluar por separado **precipitación, temperatura extrema, humedad, radiación y temporadas con eventos extraordinarios**, analizar múltiples rezagos con selección estricta dentro del entrenamiento, incorporar otros índices oceánico-atmosféricos disponibles históricamente y usar fuentes institucionales ENFEN, SENAMHI e IGP.

**No se ha medido habilidad para predecir el índice Niño 1+2 mismo, un fenómeno El Niño, su inicio, duración o intensidad.** El índice oceánico actúa aquí exclusivamente como *predictor* de anomalía térmica mensual de ERA5-Land.

## 6. Componente instrumental SENAMHI — estado real

Se verificaron fuentes públicas oficiales que permiten continuar la búsqueda instrumental, **sin asignar estaciones o temperaturas que no estén realmente obtenidas**:

- [SENAMHI: descarga de datos hidrometeorológicos](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos).
- [SENAMHI en el portal nacional de datos abiertos](https://www.datosabiertos.gob.pe/dataset/datos-hidrometeorol%C3%B3gicos-de-libre-acceso).
- [Datos abiertos de variables de estaciones automáticas de intercambio internacional](https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-0): metadatos con ubicación, departamento, altitud, fecha, hora, temperatura, humedad y precipitación, según su descripción pública.

**Estado en 8T: 0 nuevas series térmicas instrumentales SENAMHI verificadas en este backtest.** La disponibilidad de un catálogo no demuestra que una estación concreta de Lambayeque tenga cobertura temporal y comparabilidad suficiente para los 30 años 1996–2025.

## 7. Artefactos auditables

- [Motor reproducible NOAA y validación](modelos/contraste_oceanico_8t.py), con verificación de SHA, cobertura NOAA y cálculo de regresión independiente de cualquier mes futuro.
- [Pruebas automáticas](tests/test_contraste_oceanico_8t.py): formato NOAA, meses completos, ausencia de fuga, regresión de cuatro términos, criterio de comparación y prohibición de ocultar errores negativos.
- [Workflow de adquisición y contraste](.github/workflows/oaf_nino12_oceanico_8t.yml): descarga original una vez, nunca sobreescribe la versión congelada y solo recalcula cuando los insumos están íntegros.
- [Reporte con 5 ventanas y 20 ensayos de bloque](datos/validacion_oceanica_8t/estado_oceanico_8t.json).
- [Predicciones históricas con selección temporal](datos/validacion_oceanica_8t/predicciones_oceanicas_temporales_8t.csv).
- [Predicciones históricas con bloque espacial retenido](datos/validacion_oceanica_8t/predicciones_oceanicas_espaciales_8t.csv).
- [Nuevo panel 8T](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones): compara públicamente los resultados oceánicos y sin océano, aunque empeoren.

## 8. Continuación propuesta: fase 8U

La siguiente necesidad es **evaluar eventos agroclimáticos de importancia real**: primero lluvia y temperatura máxima/extrema por subregión; después contrastar si las señales Niño 1+2, Niño 3.4 o boletines ENFEN disponibles al emitir una alerta anticipan cambios mejor que referencias simples. La evaluación debe segmentarse por estación del año, zona agrícola y años de eventos, sin entrenamiento sobre datos posteriores. Avanzar simultáneamente hacia estaciones SENAMHI instrumentales reales y delimitar las cuencas y pisos físicos con información oficial. No elaborar mapas de riesgo de enfermedad para arándano/vid sin observaciones sanitarias de campo.

**Estado fase 8T:** contraste oceánico completado, resultado incremental casi nulo; estaciones térmicas SENAMHI independientes verificadas en modelo = **0**; habilidad ENFEN/El Niño Costero prospectiva = **no demostrada**; zonas agrícolas homogéneas certificadas = **0**.
