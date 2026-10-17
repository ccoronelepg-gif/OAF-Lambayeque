# Fase 9C · Resultados de validación robusta de eventos extremos y anomalías (17/10/2026)

**Dictamen científico: NO activar HR+VPD como sustituto del benchmark viento+SST.** El estudio es retrospectivo sobre reanálisis ERA5/ERA5-Land y SST NOAA históricamente revisadas. No es una prueba de calidad en tiempo real, ni una validación instrumental SENAMHI, ni una alerta ENFEN.

## 1. Resultados realmente calculados

Se analizaron **dos matrices existentes** del proyecto:
- `datos/benchmark_9a/pronosticos_pareados_9a.csv` (SHA del blob Git: `eead493f0cb2d23f2390ef210929792dfaa80510`): **17 280 predicciones** de cuatro variantes, **4 320 pares de referencia-vs-HR/VPD**, 24 combinaciones de localidad (4), horizonte (3) y objetivo (2). Cada combinación contiene 180 meses objetivo (2011-2025).
- `datos/benchmark_9a/eventos_p90_pareados_9a.csv` (SHA Git `7193075d5dfe8594a9b1ab9f4bfffbe7ac5d4e54`): **1 440 predicciones probabilísticas**, **720 pares** base-vs-HR/VPD, 12 combinaciones de localidad y horizonte, cada una con 60 meses enero–abril entre 2011 y 2025. P90 de precipitación determinado en entrenamiento, no en test.

Los resultados completos y precisos se publican en `datos/validacion_9c/resultados_9c.json`, incluido cada intervalo, conteo, diferencia MAE/Brier, exclusión 2017/2023, procedencia y advertencias.

| Comprobación | Resultado |
|---|---:|
| Comparaciones de MAE donde HR+VPD mejora | **11 de 24** (temperatura **5/12**, precipitación **6/12**) |
| Comparaciones de Brier P90 donde HR+VPD mejora | **1 de 12** |
| Intervalo 95 % de diferencia MAE positivo con bloque de 3 años (sin ajuste múltiple) | **1 de 24** |
| Intervalo 95 % de diferencia Brier positivo con bloque de 3 años | **0 de 12** |
| Intervalo de confianza familiar conservador con ajuste Bonferroni favorable | **0 de 36** |
| Comparaciones de P90 con al menos 20 eventos | **0 de 12** |

**Caso más favorable, todavía no robusto:** Jayanca, precipitación a 3 meses, MAE 8W **40,95358 mm**, RH+VPD **40,59878 mm**, diferencia **+0,35481 mm** (menor MAE es mejor). Intervalo exploratorio del 95 % con bloques de 3 años: **[+0,01353; +0,78215] mm**. Con bloques de 1 año: **[-0,01635; +0,86612] mm**. Tras control Bonferroni de 24 comparaciones: **[-0,08808; +1,01631] mm**. El resultado es pequeño, sensible al diseño de remuestreo y **no justifica selección del modelo**.

**Lluvia superior al P90 (enero–abril):** el único Brier medio favorable aparece en Olmos h=1: base **0,073867**, candidato **0,073386**, diferencia favorable **0,000481**; IC95 bloque de 3 años **[-0,000882; +0,001852]**, incluye cero. En Chiclayo hubo **7** eventos sobre 60 meses; Jayanca **4**; Motupe **5**; Olmos **5**. Los mismos meses se reevalúan a 3 horizontes: no sumar los positivos de las 12 combinaciones como eventos independientes.

## 2. Método y restricciones

1. Parejas únicas por localidad, horizonte, objetivo, periodo, mes objetivo y resultado, comparando la base con la extensión HR+VPD; validación de etiquetas, modelos y umbrales de train.
2. MAE y Brier calculados sobre exactamente los mismos objetivos y observaciones. Diferencia positiva `error_base - error_candidato` representa mejora de RH+VPD.
3. Medias de diferencias de pérdida por **año calendario**, 15 años independientes en orden. Remuestreo *circular por bloques de 3 años*, con **10 000 réplicas**, semilla LCG reproducible 917, e intervalo percentil 95 %. Sensibilidad con bloques de un año y exclusión individual de 2017 y 2023.
4. Ajuste conservador de intervalos por **Bonferroni** al 95 % de cobertura familiar: 24 comparaciones MAE, 12 comparaciones Brier, por separado. No realizar inferencia causal ni dar significancia a diferencias mínimas con pocos bloques efectivamente independientes.
5. Se conserva la normal histórica **1996–2025** como descripción del territorio y **1991–2020** para comparabilidad OMM. Pero cualquier media, escala, umbral P90 o normal utilizada para entrenar una predicción debe depender únicamente de datos anteriores al fold de prueba.
6. No hay `vintage` confiable de todos los insumos meteorológicos/satelitales en el origen: los experimentos 9A/9C son **hindcasts retrospectivos**, no verdaderos pronósticos reemitidos con insumos disponibles en aquel instante.
7. La probabilidad de una clase extremadamente rara exige más eventos, examen de fiabilidad y contraste con climatología de entrenamiento; **este estudio no calcula un Brier Skill Score validado frente a una serie completa de probabilidades de climatología de entrenamiento**. No equiparar `P90` a una probabilidad observada fija de 10 % en cada fold.

## 3. Cobertura geográfica y pisos altitudinales

**No existen resultados de validación espacial regional completa para 9C.** Los 4 lugares (Chiclayo, Jayanca, Motupe, Olmos) corresponden a celdas de reanálisis, y la comparación entre esos puntos **no demuestra** zonas homogéneas ni pronósticos en otras altitudes. Los 420 puntos del DEM usados en el rediseño cartográfico son muestreo de relieve, no 420 estaciones meteorológicas verificadas.

Para una fase posterior: unir la malla DEM con límites de cuencas, topografía, distancia al litoral y cobertura de series climáticas; estimar similitud temporal a partir de 1996–2025 con control de dependencia espacial; validar grupos mediante estaciones SENAMHI y retención de zonas completas en test. Ninguna extrapolación a pisos montanos se considera validada.

## 4. Consecuencia práctica y estado de la web

El observatorio conserva el benchmark **8W viento+SST** como referencia de investigación, no como modelo operacional. Se añadió un panel interactivo en **Investigación y datos → Fase 9C** con localidad, variable, horizonte, barras de MAE, intervalo y leyenda científica, y referencia separada de Brier P90. Ninguna barra representa estado oficial o nivel de riesgo fitosanitario.

Los archivos 9C se reproducen con `python modelos/evaluacion_pareada_9c.py --verificar datos/validacion_9c/resultados_9c.json`; se rechazan pares duplicados, faltantes, cambios de etiqueta y umbrales inconsistentes. El workflow `.github/workflows/oaf_validacion_9c.yml` ejecuta comprobación de archivo y presencia del panel. Este dictamen se mantendrá mientras no se acumulen nuevos datos instrumentales y emisiones prospectivas.

## 5. Fuentes y metodología

- Datos 9A originales: [informe de la fase 9A](FASE_9A_BENCHMARK_HUMEDAD_VPD.md), [matriz base 9A](datos/benchmark_9a/pronosticos_pareados_9a.csv), [matriz de eventos 9A](datos/benchmark_9a/eventos_p90_pareados_9a.csv).
- [WMO Lead Centre / ECMWF: verificación de reforecasts, fiabilidad y bootstrap](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification).
- [WMO Lead Centre: Brier Score y Brier Skill Score](https://www.wmolc.org/contents/index/Verification%2BForecast).
- Las alertas de El Niño Costero pertenecen a [ENFEN](https://enfen.imarpe.gob.pe/comunicados/) y los avisos meteorológicos a [SENAMHI](https://www.senamhi.gob.pe/). Las observaciones de campo de arándano y vid siguen pendientes para predicción fitosanitaria.

## Siguiente fase 9D

Diseñar **evaluación de disponibilidad temporal real (vintage/latencia)** para predictores de viento, SST, humedad y reanálisis; extraer estaciones instrumentales cercanas con metadatos y calidad controlada; validar territorialmente subzonas altitudinales evitando fuga espacial. No forzar una predicción operativa donde hoy hay insuficiencia de evidencia.
