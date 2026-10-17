# Fase 9W — Reconciliación del archivo CHIRPS y comparación reproducible de Random Forest, GCN y climatología

**OAF-Lambayeque · 17/10/2026 · evaluación retrospectiva, no pronóstico operativo.**

## 1. Hallazgo: existían dos estados documentales contradictorios

La **fase 9R sí ejecutó dos modelos sobre datos reales CHIRPS v3 final** y publicó 2340 objetivos sector-mes para 2021–2025 con 39 sectores: Random Forest y red convolucional de grafos (GCN, diferente de una CNN 2D clásica). Su comparación arrojó MAE climatología **14,2957 mm**, Random Forest **15,5397 mm** y GCN **18,4682 mm**. **Entre las dos IA gana RF; entre los tres métodos gana la climatología.**

Las notas de las fases 9S, 9T, 9U y 9V indican en algunos apartados que la matriz sectorial no se había encontrado o que ningún GCN se había entrenado. Esas afirmaciones **no describen el estado completo y actual del repositorio**: las fuentes existen en rutas concretas de las fases 9O, 9P, 9Q y 9R. El nuevo código no elimina documentos antiguos, sino que registra explícitamente su condición de notas metodológicas o diagnósticos previos desactualizados y los vincula a evidencia posterior.

## 2. Puente de procedencia exacta entre CHIRPS y benchmark 9R

El script [puente_validacion_9w.py](modelos/puente_validacion_9w.py) verifica las siguientes fuentes:

| Etapa | Fuente de meses CHIRPS final | Meses |
|---|---|---:|
| 9O | `datos/homogeneidad_9o/serie_sectores_chirps_9o.csv` | 108 |
| 9P | `datos/continuidad_9p/meses_adicionales_sectores_9p.csv` | 12 |
| 9Q | `datos/recuperacion_9q/sectores_mensuales_9q.csv` | 240 |
| **Total** | **1996-01 a 2025-12** | **360** |

Comprueba por cada mes **el SHA-256 original del TIFF**, 42 filas sectoriales sin duplicados, la ausencia explícita de tres sectores sin píxel CHIRPS (S028, S032 y S034), y los 360 meses de lluvia real no negativa para los **39 sectores restantes**. Los registros con coordenadas de polígonos de 9K mantienen sus propios hashes.

Se reconstruye la matriz `datos/validacion_9w/matriz_sectores_chirps_9w.csv` con **14 040 filas = 39 sectores × 360 meses**. Se verifican uno a uno los **2340 objetivos observados de 9R** contra la fuente CHIRPS original. La tolerancia de correspondencia es **0,001 mm**, necesaria para los redondeos de salida y el uso de `float32` en la ejecución original 9R; se reporta la desviación máxima real. Una diferencia superior invalida la auditoría y detiene el proceso; no se permite interpolación ni cambio de precipitación observada.

La documentación de origen y huellas está en [auditoria_puente_9w.json](datos/validacion_9w/auditoria_puente_9w.json). **Este cotejo de valores acredita procedencia histórica revisada, no prueba de disponibilidad de CHIRPS v3 en la fecha antigua de cada supuesto pronóstico.**

## 3. Dos protocolos, que NO deben mezclarse para declarar un ganador

**Protocolo A, 9R original.** Entrenamiento 1997–2015, validación 2016–2020 y prueba 2021–2025. Mismos 39 sectores. Arquitecturas **Random Forest (240 árboles)** y **GCN convolucional de grafos con PyTorch** frente a climatología mensual del entrenamiento. No es CNN de imágenes.

**Protocolo B, 9T–9U ejecutado ahora.** Entrenamiento hasta 2018, validación 2019–2021 y prueba 2022–2025. Usa exactamente los mismos 39 sectores y datos CHIRPS, pero otro diseño temporal e hiperparámetros de RF. Evalúa climatología, persistencia estacional y Random Forest con 250 árboles. La GCN **no fue reentrenada bajo el protocolo B**; el ranking GCN/RF válido continúa siendo el del protocolo A. El módulo 9U sólo puede seleccionar un RF si supera a su climatología **dentro del protocolo B**.

También se vuelven a calcular las métricas del 9R original **solo para los meses 2022–2025** como diagnóstico del cambio de periodo evaluado. No es un tercer ensayo independiente: esos meses ya estaban dentro del conjunto de prueba original.

**Nunca comparar sin más el MAE de RF 9T con GCN 9R para decidir superioridad**, porque los entrenamientos, parámetros y reglas de validación no son iguales, incluso cuando comparten años de prueba.

## 4. Errores, pisos altitudinales e incertidumbre por años

El módulo [evaluacion_bloques_9w.json](datos/validacion_9w/evaluacion_bloques_9w.json) publica MAE, RMSE, sesgo y mejora del MAE frente a climatología para cada modelo y cada diseño. Conserva [errores por piso](datos/validacion_9w/errores_pisos_9w.csv) y [errores por año](datos/validacion_9w/errores_anios_9w.csv) para evitar esconder los fallos sobre laderas de mayor lluvia.

Para cada pareja de modelos **del mismo protocolo** se calcula el diferencial emparejado de MAE, positivo cuando el primer modelo tiene más error. Se realiza un bootstrap **exacto por años completos**: los cinco años 2021–2025 permiten 5^5 = **3125 remuestras**, y los cuatro años 2022–2025 permiten 4^4 = **256 remuestras**. Se dan percentiles 2,5 y 97,5 % como intervalo descriptivo y proporción de muestras con diferencial positivo.

Este cálculo **no ofrece intervalos de confianza espaciales independientes**: los 39 sectores se correlacionan espacialmente y las predicciones fueron evaluadas en los mismos sectores usados para entrenar. El número efectivo de bloques es solo cuatro o cinco años, de manera que intervalos amplios son esperables. Tampoco demuestra generalización a sectores geográficos nunca vistos.

## 5. Resultado consolidado (según archivos ejecutados)

Se recomienda interpretar primero **los benchmarks por separado**. El 9R original favorece la climatología (14,30 mm) sobre RF (15,54 mm) y GCN (18,47 mm) en 2021–2025. En el protocolo alternativo 9T de 2022–2025, la climatología obtuvo **14,8293 mm** y RF **16,2716 mm** de MAE. En ambos casos, **no se ha demostrado mejora global del aprendizaje automático frente a la referencia climatológica**.

Las diferencias temporales, CIs emparejados y resultados desagregados por piso se reportan directamente desde la ejecución reproducible del 9W, no se inventan ni se seleccionan retrospectivamente para proclamar un modelo mejor.

## 5A. Resultados del remuestreo anual y diagnóstico de robustez

El puente 9W verificó **14 040 filas** (39 sectores × 360 meses), los **2340 objetivos 9R** y una deriva máxima de representación numérica de **0,00011 mm**, dentro del límite de 0,001 mm fijado para las conversiones a float32. El CI confirmó la reproducción íntegra de estos datos.

| Protocolo / años de prueba | Climatología MAE | Random Forest MAE | GCN MAE | Persistencia MAE |
|---|---:|---:|---:|---:|
| 9R: 2021–2025 | **14,29568** | 15,53971 | 18,46820 | No se calculó |
| 9R: 2022–2025 (subconjunto de los mismos modelos) | **14,97053** | 16,14954 | 18,03108 | No se calculó |
| 9T: modelos entrenados hasta 2018, prueba 2022–2025 | **14,82932** | 16,27165 | No reentrenada | 22,61547 |

Los valores son MAE de lluvia mensual en milímetros sobre **39 sectores**, no porcentajes de clasificación. La prueba 9T contiene **1872 comparaciones por modelo**. Aunque RF 9T tiene MAE superior a climatología, su RMSE fue ligeramente inferior (**31,71264** frente a **32,04035 mm**), lo que sugiere comportamientos diferentes en errores extremos; esto no basta para seleccionar RF cuando el criterio principal preespecificado es MAE.

**Contrastes emparejados dentro del protocolo 9R original, remuestreo exacto de cinco años (3125 combinaciones):**

| Diferencial de MAE | Estimación (mm) | Intervalo percentil 95 % por años completos (mm) | Interpretación |
|---|---:|---:|---|
| RF menos climatología | **+1,24403** | **[−2,56120; +4,42268]** | Contiene cero; diferencia incierta |
| GCN menos climatología | **+4,17252** | **[+0,09517; +7,56704]** | GCN tiende a mayor error |
| GCN menos RF | **+2,92849** | **[+1,61231; +5,06973]** | GCN muestra mayor MAE en los años examinados |

Estas bandas solo reflejan **variabilidad entre años** y no capturan dependencia espacial, revisiones retrospectivas de CHIRPS ni incertidumbre de nuevos sectores. No se deben leer como cobertura probabilística de un pronóstico futuro. En el protocolo 9T, el diferencial RF − climatología fue **+1,44232 mm**, con intervalo de cuatro años **[−1,78013; +4,56272] mm**; su ventaja o desventaja no es concluyente con esa muestra.

**Decisión 9U ejecutada sobre la matriz real 9W:** `RF_NO_SUPERA_CLIMATOLOGIA`. Como estrategia pública prudente, mantener la climatología histórica como referencia, estudiar RF para ciertos pisos o magnitudes de lluvia y no promover GCN hasta contar con pruebas de transferencia espacial, predictores con vintage real y estaciones independientes.

## 6. Publicación, pruebas e integridad

Archivos generados: matriz 39×360; manifiesto SHA; tres protocolos de evaluación; predicciones 9T de validación/prueba; decisión 9U; métricas por piso y año. Su ejecución está automatizada en [GitHub Actions](.github/workflows/oaf_evidencia_predictiva_9w.yml), con [tests de protección](tests/test_puente_predictivo_9w.py), y el módulo [visor_evidencia_9w.js](modelos/visor_evidencia_9w.js) se publica en **Análisis de clima regional**.

**Límites no negociables:** los productos CHIRPS son satélite/pluviómetros grillados y no observaciones de estaciones SENAMHI independientes; los polígonos y CHIRPS v3 final fueron compilados después de 2025; el tiempo real de disponibilidad de predictores históricos no ha sido certificado; no existe evaluación de transferencia a nuevas zonas, ensayo prospectivo 2026 ni habilidad de alertas fitosanitarias validada. **0 zonas operativas certificadas y 0 alertas emitidas a partir de 9W.**

## 7. Próxima fase 9X

Diseñar y ejecutar la **prueba de generalización espacial** dejando sectores o bloques hidrográficos completos fuera del entrenamiento (no solo meses futuros). Comprobar el sesgo de la red GCN con y sin vecinos; evitar que sus nodos conozcan objetivos en zonas reservadas. Reentrenar, dentro de exactamente los mismos cortes y grupos, climatología, persistencia, Random Forest espacial y GCN (una CNN convencional solo si tiene un tensor espacial regular válido). Incorporar **estaciones SENAMHI independientes con metadatos acreditados** y evaluación de episodios extremos; no promover ningún modelo sin superar esos controles. Solo tras habilidad histórica fuera de muestra y evidencia de disponibilidad as-issued se podrán plantear pronósticos operativos responsables.

**Lema:** «Datos abiertos y ciencia climática al servicio del campo».
