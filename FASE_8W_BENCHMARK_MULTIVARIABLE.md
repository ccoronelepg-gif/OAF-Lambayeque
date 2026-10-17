# OAF-Lambayeque — Fase 8W: evaluación predictiva retrospectiva multivariable

**Fecha de desarrollo: octubre de 2026.**  
**Tipo de resultado: HINDCAST experimental en reanálisis; NO pronóstico climático emitido en el pasado y NO sistema operativo de alertas.**

## 1. Pregunta investigada

¿El viento atmosférico y la temperatura superficial del mar de regiones Niño 1+2 / Niño 3.4 añaden información predictiva útil sobre el clima local en Lambayeque a horizontes de uno, dos y tres meses? ¿Qué ocurre si se agregan, por separado y solo durante su periodo conocido, corrientes oceánicas geostróficas modeladas?

Objetivos observados **dentro de los reanálisis**: temperatura media mensual del aire (ERA5-Land) y precipitación mensual acumulada (ERA5), archivadas en la Fase 8V para cuatro referencias: Chiclayo, Jayanca, Motupe y Olmos. Son centros de celdas modelo; no son parcelas, estaciones oficiales SENAMHI, ni zonas topoclimáticas homogéneas certificadas. Los índices NOAA SST tienen revisiones históricas ex post, no se dispone de "vintage" congelado a la fecha del supuesto pronóstico.

## 2. Diseño preespecificado

- Entrada: [matriz terrestre 8V](datos/integracion_8v/matriz_terrestre_8v.csv) con 1.440 meses-localidad en 1996–2025 y [matriz marina 8V](datos/integracion_8v/matriz_marina_8v.csv) con corrientes geostróficas 2017–2025 solamente.
- Cinco cortes retrospectivos **sin barajar meses**: pruebas 2011–2013, 2014–2016, 2017–2019, 2020–2022 y 2023–2025. Entrenar respectivamente hasta diciembre de 2010, 2013, 2016, 2019 y 2022. La etiqueta (mes objetivo) de entrenamiento es anterior al primer mes objetivo del corte siguiente.
- Horizonte: mes objetivo `t+h` con `h=1,2,3`. Predictores hasta fin del mes de origen `t`. Se trata de archivo de meses completos; **no equivale a un pronóstico disponible al inicio del mes t+1**, debido al cierre, publicación y posible revisión de fuentes.
- Climatología por mes calendario aprendida **solo del entrenamiento de cada corte**. Estandarización de predictores y regularización fijada sin consultar datos de prueba.
- Se comparan climatología y persistencia contra regresión Ridge regularizada local; después se agregan velocidad/componentes u/v de viento y finalmente anomalías SST Niño 1+2 y Niño 3.4 de los meses t y t−1. La representación de precipitación en regresión usa `log1p(mm)`; los errores se vuelven a medir en **mm reales de reanálisis**.
- Para evento probabilístico, se evalúa superación de percentil **P90 de precipitación por mes calendario enero–abril** estimado **solo con el periodo de entrenamiento**, excluyendo meses en que el P90 estimado es cero. Se usa regresión logística regularizada y una referencia climatológica suavizada. Se compara **Brier score** y Brier Skill; NO es alerta de inundación ni umbral de daño agrícola.
- Los resultados completos son **21.600 pares modelo–mes–objetivo** continuos, **2.880 pares probabilísticos** de eventos, y **1.728 registros del subexperimento de corrientes**. Tales registros comparten años y localidades: **NO son observaciones estadísticamente independientes**.
- Para explorar corrientes solo se considera entrenamiento **2017–2022** y prueba **2023–2025**. Se comparan variantes con y sin u/v geostróficos AOML dentro del MISMO periodo corto, evitando falsear un histórico 1996–2025. Las dos celdas marinas no están colocalizadas con los vientos.

El principio de particiones temporales respeta [TimeSeriesSplit de scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html), pero está implementado con reglas de origen y objetivos explícitas sin depender de esa biblioteca. [ECMWF/WMO](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification) señalan la necesidad de verificar la habilidad de hindcasts y contar con métricas objetivas para interpretar productos predictivos.

## 3. Hallazgos originales del archivo de resultados

Los resultados exactos se guardan en [estado del experimento](datos/benchmark_8w/estado_benchmark_8w.json), [predicciones continuas](datos/benchmark_8w/predicciones_mensuales_8w.csv), [probabilidades de enero–abril](datos/benchmark_8w/probabilidades_lluvia_p90_8w.csv) y [sensibilidad con corrientes](datos/benchmark_8w/sensibilidad_corrientes_8w.csv).

**MAE a 1 mes, cuatro ejemplos sobre 180 meses objetivo por localidad (2011–2025):**

| Localidad/objetivo | Ridge local | Ridge local + viento + SST | Ganancia MAE |
|---|---:|---:|---:|
| Motupe, temperatura media | 0,341520 °C | 0,336764 °C | +1,4 % |
| Olmos, temperatura media | 0,331983 °C | 0,333740 °C | −0,5 % |
| Motupe, lluvia mensual | 47,548796 mm | 45,689133 mm | +3,9 % |
| Jayanca, lluvia mensual | 39,534967 mm | 36,796392 mm | +6,9 % |
| Chiclayo, lluvia mensual | 10,444918 mm | 10,018625 mm | +4,1 % |

**Conjunto de combinaciones:** añadir viento y SST reduce MAE frente al modelo local en **11/12** combinaciones de temperatura y **11/12** de precipitación al agrupar todos los cortes, pero esa ventaja agregada NO fue constante durante los cinco ensayos.

En concreto, la variante con viento y SST mejora MAE en **al menos tres de cinco cortes** en **9/12** combinaciones de temperatura y **11/12** de lluvia. Solo en **4/12** de temperatura y **6/12** de precipitación mejora **al menos cuatro de cinco cortes**. De manera ilustrativa, en Motupe a un mes el porcentaje de mejora térmica por corte fue **+0,303 %, −4,631 %, +9,123 %, +3,177 %, −0,908 %**. Así que un porcentaje agregado positivo NO constituye habilidad consistentemente superior.

**Evento probabilístico de lluvia:** la variante completa mejora el Brier frente a la climatología de eventos en **8 de 12** combinaciones de localidad–horizonte. En Motupe a un mes, Brier climatología **0,07965204** y viento+SST **0,06547514**, para **5 eventos sobre 60 meses evaluados**; muestra escasa para extrapolar fiabilidad probabilística.

**Corrientes geostróficas:** agregar componentes u/v de NOAA/AOML en el ensayo 2017–2025 reduce MAE en solo **8/24** combinaciones, y reduce RMSE en solo **4/24**. Este ensayo corto y con rejillas no colocalizadas **NO proporciona evidencia suficiente para incluir corrientes como predictor operativo**. La presencia de corrientes sigue siendo importante en el mecanismo físico y se estudiará con productos oceanográficos mejor alineados y periodos más extensos, sin confundir ausencia de mejoría en esta versión con ausencia de influencia oceánica.

## 4. Advertencias sobre lluvia extrema

La fase 8V detectó **11 meses-localidad** ERA5 de precipitación ≥1.000 mm que requieren control instrumental; Motupe marzo 1998 **2.913,8 mm del reanálisis**, NO pluviómetro. En este ensayo, **1997–1998 está en entrenamiento para todos los cortes de prueba**; por tanto, **NO se ha demostrado habilidad fuera de muestra para un episodio equivalente a 1997–1998**. Los errores medios pueden ocultar el mal desempeño ante extremos poco frecuentes. Antes de avisos agrícolas, se necesitan estaciones oficiales y contraste con registros históricos de inundaciones, cuencas y precipitación.

## 5. Qué se publicó en el proyecto

Motor determinista: [`modelos/benchmark_multivariable_8w.py`](modelos/benchmark_multivariable_8w.py). Pruebas sintéticas: [`tests/test_benchmark_multivariable_8w.py`](tests/test_benchmark_multivariable_8w.py). Automatización de GitHub: [`oaf_benchmark_multivariable_8w.yml`](.github/workflows/oaf_benchmark_multivariable_8w.yml). Las pruebas sintéticas confirman lógica y ausencia de filtración de objetivos futuros para ejemplos controlados, pero NO validan modelos con datos instrumentales independientes. El panel de Verificación contiene filtros de localidad, horizonte y objetivo con MAE, RMSE, Brier y sensibilidad de corrientes: [portal OAF](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

## 6. Dictamen del experimento

**Estado: benchmark técnico exploratorio reproducible, no sistema predictivo operativo.** La evidencia favorece estudiar señales oceánicas y atmosféricas para mejorar el pronóstico de clima terrestre, pero no justifica emitir alertas a productores. Los promedios positivos conviven con resultados contradictorios por período, producto oceánico, sitio y variable. Es especialmente importante no tratar los cuatro centros de modelo como muestras independientes de toda la región, ni las anomalías SST de Niño1+2 como ICEN oficial, ni los océanos/superficie como una misma variable.

**La etapa 8X** debe aumentar el rigor con pruebas de estabilidad por temporadas y años extremos, referencias locales adicionales, visualización de errores grandes, subzonas realmente validadas por SIG y estaciones SENAMHI; solo después podrá evaluarse un producto con protocolos prospectivos y riesgo agrícola diferenciado. Para arándano y vid seguirán pendientes evaluaciones fitosanitarias de campo antes de probabilidades de enfermedad.

*Documento técnico redactado desde archivos del OAF. No constituye asesoría para gestión de inundaciones o aplicaciones fitosanitarias.*
