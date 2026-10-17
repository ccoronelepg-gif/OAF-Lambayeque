# Fase 10B · Calibración temporal e incertidumbre bajo años anómalos (17/10/2026)

## Evidencia ejecutada
Se recuperaron **11.700 registros** archivados de 9X (39 sectores × 60 meses × cinco métodos). Sin reentrenar los modelos, se calcularon errores absolutos para **2021–2022** (24 meses, 936 registros/modelo), el radio por sector/modelo de orden **23 de 24** para intervalo nominal al **90 %**, y cobertura posterior en **2023–2025** (36 meses, 1.404 registros/modelo). Precipitación predicha/observada en mm CHIRPS v3 FINAL; intervalos inferiores truncados en cero. No hay inferencia causal ni garantía conformal si falla la intercambiabilidad.

| Modelo | Cobertura 2023–2025 | Ancho medio (mm) | MAE (mm) |
|---|---:|---:|---:|
| Random Forest | 90,60 % | 66,54 | 18,4295 |
| GCN | 90,95 % | 82,01 | 19,4458 |
| Climatología por piso | 90,10 % | 79,09 | 21,5017 |
| Persistencia anual | 80,63 % | 59,95 | 25,7050 |
| Climatología global | 91,81 % | 99,08 | 24,6522 |

**Solo 2023:** cobertura RF **80,13 %**, GCN **82,26 %**, climatología por piso **85,68 %**, inferior al 90 % en los tres casos. Los sesgos globales negativos RF/GCN muestran subestimación sistemática de lluvias.

**Lluvias mensuales ≥100 mm, 2023–2025:** 91 pares sector-mes superaron el umbral observacional; la predicción puntual de RF también alcanzó ≥100 mm en **15**, GCN en **4** y climatología por piso en **17**. Se evaluaron también umbrales 50/150 mm. Estas cifras describen la sensibilidad de una regla simple sobre un regresor, NO habilidades de un clasificador entrenado para extremos ni umbrales oficiales de emergencias.

## Auditoría crucial de disponibilidad
La [documentación oficial CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) indica que **CHIRPS v3 Preliminary** tiene aproximadamente dos días de desfase desde cada pentada y **CHIRPS v3 Final** suele publicarse durante la tercera semana del mes siguiente. Por tanto, una emisión el día 1 del mes objetivo no puede usar el valor FINAL del mes inmediatamente anterior. Una variable rezagada **dos meses** resulta más compatible con la latencia típica, pero **no certifica** fecha efectiva, revisiones ni versión original del dato.

Además, **CHIRPS v3 FINAL fue retroprocesado históricamente**, así que disponer hoy de observaciones de 2021–2024 no prueba que esa versión estuviera accesible en dichos años. El OAF no conservó instantáneas as-issued de esas entradas. En la **fase 10B no se reentrenó** RF/GCN con lag2 ni se reconstruyeron falsamente fechas de pronóstico; los resultados cuantifican exclusivamente confiabilidad retrospectiva en CHIRPS final revisado.

## Condiciones de interpretabilidad
- Calibración: 2021–2022; prueba posterior: 2023–2025; **no evaluar calibración sobre los mismos residuos 2021–2022**.
- El 90 % es solo nivel nominal de construcción. Dependencia temporal/espacial y cambios de régimen (ej. 2023) impiden considerarlo una garantía universal.
- No extrapolar sectores exploratorios a pisos certificados o predios individuales.
- CHIRPS incorpora pluviómetros; falta validación independiente de SENAMHI y prospectiva.
- No se emiten alertas automáticas de lluvia, ENSO, enfermedades de arándano o vid. **No hay modelo operativo ganador.**

## Archivos reproducibles
[Resultado íntegro 10B](datos/calibracion_10b/evaluacion_temporal_10b.json) · [Motor Python](modelos/calibracion_temporal_10b.py) · [Pruebas automáticas](.github/workflows/oaf_10b_evaluacion.yml) · [Visualización experimental](evaluacion-temporal.html).

## Puerta 10C
Se requieren versiones observacionales verdaderamente disponibles en emisión (o un ensayo prospectivo), una comparación de datos con lags 2+ que **reentrene** los modelos y separe tuning/calibración, validación instrumental independiente y evaluación de extremos según eventos/sectores antes de usar el sistema para decisiones productivas.
