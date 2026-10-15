# OAF-Lambayeque — Fase 8B: predictores atmosféricos NOAA para anomalías Niño 1+2

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Fecha de ejecución:** 15 de octubre de 2026 (UTC; hora peruana UTC−05).  
**Estado:** experimento retrospectivo reproducible; **no** predicción validada de El Niño Costero, **no** ICEN institucional ni alerta ENFEN.

## 1. Objetivo y decisión

Comprobar mediante errores históricos reales si sumar indicadores atmosféricos (**Índice de Oscilación del Sur, SOI; anomalías de vientos alisios a 850 hPa del Pacífico central y oriental**) mejora la predicción de la **anomalía mensual de TSM Niño 1+2** de NOAA NCEI ERSSTv5 con referencia reajustada por OAF a 1991–2020.

**Decisión después de ejecutar el experimento:** **NO adoptar el modelo ampliado para alertas ni sustituir la referencia oceánica**. El modelo con tres covariables atmosféricas empeoró el MAE frente a uno que usa únicamente la temperatura superficial del mar en los tres horizontes, tanto en la prueba histórica completa como en la revisión de los últimos doce meses. Tampoco existe validación prospectiva de esta nueva variante.

El propósito del OAF mantiene dos líneas paralelas: estudiar la anticipación de El Niño Costero y sus efectos agroclimáticos en Lambayeque, y recopilar datos de campo para validar modelos fitosanitarios de arándano y vid, particularmente *Botrytis*.

## 2. Fuentes verificadas y definición de variables

| Variable | Región / concepto | Archivo oficial |
|---|---|---|
| Objetivo: anomalía mensual de SST Niño 1+2 | 0–10°S, 90–80°O, reconstruida a 1991–2020 | [NOAA NCEI ERSSTv5](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat); archivo interno `datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv` |
| **SOI estandarizado** | Diferencia normalizada de presión entre Tahití y Darwin, valor mensual | [NOAA CPC SOI](https://www.cpc.ncep.noaa.gov/data/indices/soi), sección `STANDARDIZED DATA` |
| **Anomalía de vientos alisios del Pacífico central** | Capa 850 hPa, 175°O–140°O, 5°N–5°S | [NOAA CPC cpac850](https://www.cpc.ncep.noaa.gov/data/indices/cpac850), sección `ANOMALY` |
| **Anomalía de vientos alisios del Pacífico oriental** | Capa 850 hPa, 135°O–120°O, 5°N–5°S | [NOAA CPC epac850](https://www.cpc.ncep.noaa.gov/data/indices/epac850), sección `ANOMALY` |

La existencia y estructura de estos archivos NOAA se verificó en consultas reales; el motor interpreta correctamente los `-999.9` como **datos ausentes**, incluso cuando aparecen concatenados al número anterior, y nunca los convierte en valores reales. La serie instrumental local de radiación solar **no sustituye** los vientos de la atmósfera tropical, ni viceversa.

Archivo procesado de covariables [CSV atmosférico NOAA](datos/noaa_cpc_predictores_atmosfericos_8b.csv): **573 meses coincidentes (enero 1979–septiembre 2026)**. El SOI tiene historia más larga; los vientos limitan el inicio común a 1979. Para los intervalos de comparación se utilizan solo los meses de origen con todas las variables presentes.

**Advertencia sobre disponibilidad histórica:** estos son archivos institucionales retrospectivos actualizados, y no permiten reconstruir con garantía la *versión exacta* que se publicaba en cada fecha pasada. La evaluación temporal walk-forward **impide que los objetivos futuros entrenen en el modelo de cada fecha**, pero no elimina revisiones retrospectivas de fuentes (problema de `data vintage`); por ello, los resultados no demuestran habilidad de emisión real. La Fase 8A sí archivó una emisión previa para futuros ensayos prospectivos, que seguirá vigente y separada de este benchmark 8B.

## 3. Diseño de los tres modelos

Para cada mes de origen disponible, horizonte h=1, 2 y 3:

- **A: persistencia oceánica:** proyectar para el mes objetivo la anomalía Niño 1+2 del mes de origen sin cambios.
- **B: solo TSM:** regresión Ridge sobre anomalía Niño 1+2 en el mes de origen, penalización fija `alpha=20`, intercepto sin penalizar.
- **C: TSM + atmósfera:** la misma regresión Ridge y regularización fija, agregando SOI y anomalías cpac850 y epac850 observadas **en el mismo mes de origen**.

Se ajustan medias y desviaciones estándar de covariables exclusivamente en cada periodo de entrenamiento. La ventana de entrenamiento crece mes a mes y solo incluye ejemplos cuyo mes objetivo de entrenamiento es **anterior o igual** al mes de origen que se evalúa. No se utilizan etiquetas de meses futuros para predecir el mes h meses después de la fecha de origen. Los resultados presentados son errores en el mismo conjunto de orígenes por horizonte.

**Primer origen de evaluación:** 2010-01. **Mínimo de entrenamiento:** 120 ejemplos. El horizonte de 1 mes terminó en origen 2026-08, el de 2 meses en 2026-07, y el de 3 meses en 2026-06, porque sus resultados se conocen hasta septiembre de 2026.

**Precisión de comparación:** el modelo univariado B se construye aquí con **Ridge**, mientras que la Fase 6D empleaba otra formulación AR(1)/estimación de parámetros. Por eso pequeñas diferencias en el MAE entre Fase 6D y Fase 8B son esperables; el diseño B/C de 8B es una comparación de variables con el mismo método y conjunto de datos.

## 4. Resultados ejecutados en datos NOAA reales

Error absoluto medio (MAE) de anomalía objetivo; **menor MAE implica menor error**. Unidades °C.

| Horizonte (meses) | Orígenes evaluados | Persistencia MAE | Solo TSM MAE | TSM + atmósfera MAE | Mejora C frente a B | Mejora C vs B últimos 12 | Intervalo exploratorio de mejora de C vs B (bloques 12m, 95 %) |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 200 | 0.3375 | 0.3351 | 0.3537 | -5.55 % | -1.04 % | -12.48 % a 0.19 % |
| 2 | 199 | 0.5105 | 0.4871 | 0.5084 | -4.37 % | -3.72 % | -16.04 % a 5.29 % |
| 3 | 198 | 0.6670 | 0.6121 | 0.6322 | -3.28 % | -3.80 % | -13.97 % a 6.22 % |

**Interpretación científica:**
- **h=1:** C obtuvo MAE 0,3537 °C, superior a B (0,3351 °C) y a persistencia (0,3375 °C). No mejoró ninguna de ambas referencias.
- **h=2:** C obtuvo MAE 0,5084 °C, mayor que B (0,4871 °C), aunque ligeramente inferior a persistencia (0,5105 °C). Esto **no significa** que agregar atmósfera mejoró respecto del modelo base B.
- **h=3:** C obtuvo MAE 0,6322 °C, mayor que B (0,6121 °C), aunque inferior a persistencia (0,6670 °C).
- **Últimos doce meses:** C también empeoró MAE frente a B en los tres horizontes. Los intervalos descriptivos por bloques contienen cero; no demuestran mejora estable de la variante ampliada.

**Decisión:** para publicar predicciones, el módulo 8B quedará como ensayo comparativo transparente, no como motor operativo. Las emisiones 8A, ya congeladas, no se modificarán ni sustituirán retrospectivamente con el nuevo ajuste. Ningún valor de h=1,2,3 derivado del ensayo 8B constituye por sí solo una **emisión prospectiva**.

## 5. Código, verificación y publicación

- [Motor Python](modelos/benchmark_atmosferico_8b.py) (biblioteca estándar, descarga NOAA, controles de integridad, regresiones, walk-forward y estimación exploratoria por remuestreo de bloques mensuales).
- [GitHub Actions](.github/workflows/oaf_benchmark_atmosferico_8b.yml): autopruebas, descarga de tres fuentes NOAA, evaluación y publicación solo tras completar todo. **Ejecución inicial: success**.
- [NOAA CPC, serie conjunta CSV](datos/noaa_cpc_predictores_atmosfericos_8b.csv): últimos valores reales y meses históricos con cobertura.
- [Resultados y métricas estructurados JSON](datos/benchmark_atmosferico_8b.json).
- [597 predicciones retrospectivas individuales CSV](datos/benchmark_atmosferico_8b_fold.csv): mes origen, mes objetivo, valor observado y tres métodos, errores reproducibles.
- [Boletín de El Niño del observatorio](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino): nuevo panel plegable «Fase 8B · ¿El SOI y los vientos mejoran las predicciones?».

**Control de honestidad:** no convertir mejora histórica de un producto de NOAA respecto a otro en probabilidad de anomalía climática regional, ni declarar equivalencia con el ICEN oficial/alertas ENFEN. Conservar el historial 1996–2025 para futuros estudios agroclimáticos de Lambayeque.

## 6. Siguientes hipótesis — Fase 8C

La utilidad de los predictores físicos **puede depender de sus desfases temporales y no ser lineal**. La ausencia de mejora de este modelo lineal contemporáneo no refuta su relevancia científica. Una fase 8C deberá evaluar hipótesis previamente definidas, no seleccionar retrospectivamente combinaciones ganadoras entre cientos de variables:

1. **Desfases y tendencias:** SOI/vientos de meses anteriores y su tendencia, solo disponibles antes de la fecha real de emisión, manteniendo un conjunto independiente 2023–2026 o una prueba prospectiva.
2. **Calor subsuperficial del Pacífico ecuatorial:** identificar un archivo estable NOAA con cobertura histórica, unidades y fecha de publicación antes de incluirlo. *No se incorporó a 8B: no existe aún una serie verificada dentro del repositorio*.
3. **Robustez de validación:** comparar contra persistencia, B y pronósticos institucionales cuando proceda, controlar revisión de fuente, escenarios ENSO extremos y habilidad durante transiciones rápidas.
4. **Impactos regionales:** evaluar bajo control temporal Niño 1+2 ↔ precipitación, temperatura y **radiación solar** de Lambayeque (referencia 1996–2025), primero como análisis estadístico y sin inferir probabilidad operativa de lluvia/inundaciones.
5. **Vigilancia ENFEN:** seguir usando sus comunicaciones e ICEN publicados como fuente oficial contextual, no como datos de entrenamiento insertados con fecha retrospectiva ficticia.

**Conclusión:** la Fase 8B aporta una evaluación negativa pero científicamente útil. El avance real no consiste en acumular variables, sino en demostrar qué información ayuda a anticipar el clima de manera reproducible y cuál todavía no.
