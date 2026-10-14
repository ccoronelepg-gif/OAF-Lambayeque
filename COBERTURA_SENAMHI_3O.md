# OAF-Lambayeque | Auditoría de cobertura instrumental — Fase 3O

**Corte de la documentación:** octubre de 2026. **Periodo analizado:** enero de 1996–diciembre de 2015, restringido a los archivos SENAMHI históricos recibidos.

## Criterio de calidad aplicado

Un mes se declara **completo** si aparecen todos los días del mes calendario y **todos** poseen una precipitación diaria no negativa válida. El código de ausencia `-99.9` se convierte en faltante, **no en 0 mm**. Se invalida el total de un mes parcial aunque sus días observados sumen una cantidad de lluvia.

| Estación | Meses con registros | Meses completos | Meses incompletos | Años totalmente completos |
|:---|---:|---:|---:|---:|
| Jayanca (La Viña) | 223 | 219 | 4 | 15 |
| Cayaltí | 238 | 235 | 3 | 17 |
| Reque | 238 | 233 | 5 | 15 |
| Lambayeque | 223 | 204 | 19 | 15 |
| Cueva Blanca | 222 | 218 | 4 | 17 |
| **Total (mes-estación)** | **1 144** | **1 109** | **35** | — |

El intervalo de referencia 1996–2015 representa **1 200 posibles meses-estación** (20 años × 12 meses × 5 estaciones): **1 109** tienen lluvia completa, **35** contienen al menos una omisión y **56** no aparecen en los archivos recibidos. Por ello, la cobertura de meses completos respecto de esas 1 200 combinaciones es **92,42 %**. Esta cifra no representa la cobertura 1996–2025 (30 años) del proyecto.

**Años simultáneos completos de las cinco estaciones:** **1996–2003, 2009, 2010 y 2012** (11 años). El resto solo puede contrastarse por estación y mes con cobertura completa; no generar totales anuales a partir de meses incompletos.

## Comportamiento especial de la lluvia observada en 1998

La tabla compara el acumulado anual de **1998** contra la **mediana de los otros años completamente observados** en la estación (solo aquellos con 12 meses completos).

| Estación | Lluvia 1998 (mm) | Mediana otros años completos (mm) | Razón 1998/mediana |
|:---|---:|---:|---:|
| Jayanca (La Viña) | 1 428,00 | 68,85 | 20,7 veces |
| Cayaltí | 558,50 | 48,21 | 11,6 veces |
| Reque | 232,82 | 22,33 | 10,4 veces |
| Lambayeque | 279,61 | 35,08 | 8,0 veces |
| Cueva Blanca | 969,20 | 791,35 | 1,2 veces |

La mediana se calcula sobre conjuntos de años válidos de tamaño diferente entre estaciones; no sustituye una normal climatológica formal de 30 años. La diferencia entre costa y sierra es descriptiva y requiere confirmar los metadatos geográficos originales de cada estación.

## Procedencia y limitaciones

- Archivos diarios originales TXT de SENAMHI aportados por el investigador para **Jayanca, Cayaltí, Reque, Lambayeque y Cueva Blanca**. Los últimos registros de estos archivos corresponden a 2014 o 2015.
- Agregación mensual reproducible: `scripts/preparar_observaciones_3o.py` (en caso de incorporarse al repositorio) y salida `datos/senamhi_mensual_completo_1996_2015.csv`.
- Las series de lluvia por sí solas **no permiten cuantificar la precisión de PISCOp o ERA5** hasta alinear sus estimaciones en las mismas ubicaciones y meses.
- La ubicación instrumental exacta y las posibles reubicaciones históricas siguen pendientes de verificación documental oficial.
- No usar la muestra histórica para anunciar alertas operativas de cultivos, pronóstico o calibración independiente de PISCOp.
