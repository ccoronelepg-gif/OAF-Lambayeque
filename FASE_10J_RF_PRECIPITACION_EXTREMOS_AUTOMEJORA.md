# Fase 10J — Random Forest de lluvia mensual, lluvias intensas y actualización futura controlada

**OAF-Lambayeque · 17 de octubre de 2026 · investigación retrospectiva sin alertas operativas.**

## Propósito científico

Este módulo tiene como **única familia predictiva de IA Random Forest**. Sus tres objetivos son estrictamente meteorológicos:

- **Precipitación mensual**: estimación en milímetros por sector agroclimático.
- **Mes con precipitación elevada**: probabilidad de lluvia mensual CHIRPS mayor o igual al **P90 histórico del sector**.
- **Mes con precipitación excepcional relativa**: probabilidad de lluvia mensual CHIRPS mayor o igual al **P95 histórico del sector**.

**P90 y P95 no son umbrales meteorológicos de alerta SENAMHI**, ni equivalen a una lluvia torrencial horaria, un desastre o al fenómeno El Niño costero. El módulo **NO predice enfermedades ni infecciones**. Las posibles horas con humedad elevada se estudian posteriormente con datos **horarios** y, para la humectación foliar, sensores o modelos físicos específicos; nunca se obtienen artificialmente a partir de mm mensuales.

## Datos utilizados y trazabilidad

Se integran los archivos ya auditados del OAF-Lambayeque para 39 sectores, 1996–2025, siempre con rezagos ≥2 meses:

| Categoría | Información disponible y utilizada | Precauciones |
|---|---|---|
| Lluvia | CHIRPS v3 Final mensual en polígonos experimentales 9K, rezagos t−2,t−3,t−4,t−6,t−12, estacionalidad, vecindad | Revisiones ex post; CHIRPS Final se publica después del mes objetivo |
| Océano | SST Niño 1+2 y Niño 3.4, SOI, vientos alisios | Indices regionales; no son SST de cada finca |
| Viento marino | Dos puntos marinos, Pimentel y norte Lambayeque | Señal regional, no registros anemométricos de finca |
| Aire y energía | NASA POWER/MERRA-2 temperatura, RH, viento, presión superficial y temperatura de rocío; radiación SRB/CERES | Solo 7 grupos meteorológicos aproximados para 39 sectores; radiación cambia de producto alrededor de 2001 |
| Derivadas físicas | Diferencia temperatura–rocío y déficit de presión de vapor (VPD), de las variables de t−2 | Son indicadores del aire, no horas de hoja mojada |
| Corrientes marinas | Archivo parcial 2017–2025 | **Excluidas** por no existir historia comparable 1997–2015 |
| Humedad del suelo, sensores de hojas y datos de finca | Sin serie completa confiable por sector | **No imputados**, no empleados |

Se incluyen **cuatro experimentos RF**: lluvia sola (L), lluvia+océano/viento (LO), lluvia+atmósfera NASA (LA) y lluvia+océano+atmósfera (LOA). La agrupación se contrasta tanto para cantidad en mm como para P90 y P95.

## Corrección conservadora y prevención de sobreajuste

En lugar de imponer predicciones RF incluso si la climatología es mejor:

1. Se calcula una **climatología mensual de precipitación por sector** a partir exclusivamente de 1997–2015 (normal fija del experimento).
2. RF Regresor aprende el **residuo de lluvia** respecto a esa normal. La estimación mensual es `max(0, climatología + peso × residuo_RF)`.
3. RF Clasificador aprende probabilidades de eventos ≥P90 y ≥P95, definidos por umbrales de cada sector calculados **solo en 1997–2015**. La probabilidad final es `(1−peso)×climatología_evento + peso×probabilidad_RF`, acotada a [0,1].
4. Los pesos permitidos son 0, 0,2, 0,4, 0,6, 0,8 y 1, seleccionados **únicamente en validación 2016–2018** sobre sectores de entrenamiento. **Peso cero significa que el modelo se abstiene de corregir la climatología**.
5. Se seleccionan por separado pesos y configuración de regresión (MAE) y de clasificación P90/P95 (Brier), no se extrapola automáticamente un único ganador a tres tareas.
6. Se calibran bandas **exploratorias** de error de lluvia con los residuos absolutos de **2019–2020**, exclusivamente para el área de prueba, sin emplear los años 2021–2025 para escoger amplitud. La cobertura nominal 90 % no está garantizada bajo dependencia temporal/espacial y extremos.
7. Los años **2021–2025** se usan solo para evaluación retrospectiva. Dado que en fases previas ya fueron examinados, esta prueba no se puede considerar genuinamente ciega respecto de toda la investigación.

### Habilidad y publicación

Para declarar que un RF supera la referencia deben comprobarse, como mínimo, MAE menor que climatología para mm, Brier inferior para P90 y P95, estabilidad entre años, resultados en 2023 y condiciones espaciales. Aunque supere estas métricas, **las fuentes CHIRPS Final y NASA actuales son archivos retrospectivos, no snapshots originales "as-issued"**. Hasta validar contra emisiones reales y estaciones independientes, el resultado solo puede ser un experimento reproducible, no alertas operativas.

Fuentes: [Climate Hazards Center CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) y [NASA POWER Monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/).

## Mejora automática futura — **candidatos, no despliegue ciego**

Se implementó [actualizacion_automatica_rf_10j.py](modelos/actualizacion_automatica_rf_10j.py) y [GitHub Actions](.github/workflows/oaf_10j_automejora.yml). El workflow corre el día **26 de cada mes** y cuando se cargan meses nuevos, pero **no supone** que CHIRPS Final está disponible en ese momento.

### Condiciones de aceptación de nuevos datos
Un mes nuevo debe entregarse como `datos/nuevos_meses_chirps_10j/lluvia_CHIRPS3_FINAL_YYYY_MM.csv` con exactamente 39 sectores y columnas:

`mes,sector,lluvia_mm,producto,url_fuente,fecha_publicacion_utc,sha256_fuente_original`

El validador exige ausencia de duplicados o faltantes, meses 2026+ consecutivos, valores numéricos finitos, URL atribuida a CHC/UCSB, referencia SHA-256 y fecha posterior al periodo. **Estos metadatos se declaran en el archivo: el workflow no prueba por sí solo la autenticidad del recurso externo**; ello requerirá descarga/verificación de la fuente.

### Acciones si los datos están completos

- Generar **una versión candidata RF de lluvia**, serializada como archivo interno `joblib` (usar solo artefactos confiables, pues no son formato seguro para archivos ajenos).
- Si aún no hay series nuevas de NOAA/NASA para los mismos meses, entrenar exclusivamente con lluvia histórica, **sin fingir que hay indicadores oceánicos recientes**.
- Con 12 o más meses nuevos, realizar una **prueba cronológica sombreada** sobre los últimos 12 meses sin utilizarlos para ajustar el modelo que se evalúa, frente a climatología. Registra MAE y Brier P90/P95. Con menos de 12, documentar «evidencia futura insuficiente».
- El modelo candidato puede actualizarse con nuevos datos, pero **no se promociona automáticamente como pronóstico público**. Los archivos de modelo van a artefactos privados de CI, y las alertas meteorológicas permanecen deshabilitadas.
- Para desplegar un modelo al productor se exigirán predicciones archivadas **antes de cada fenómeno**, series de observaciones independientes y una evaluación sin selección retrospectiva del periodo de prueba. Un algoritmo que empeore la climatología debe quedar en modo de investigación.

Enfermedades de arándano/vid y otros cultivos constituirán otro proyecto científico con **etiquetas reales de incidencia/severidad en campo**, independientes del RF de lluvia.

## Recursos

[Entrenamiento RF P90/P95](modelos/rf_lluvia_extremos_10j.py) · [Pruebas de integridad](tests/test_rf_lluvia_10j.py) · [CI de entrenamiento](.github/workflows/oaf_10j_entrenamiento.yml) · [Panel visual del experimento](evaluacion-rf-lluvias-10j.html) · [Datos de predicciones del ensayo](datos/rf_robusto_10j/predicciones_rf_tres_objetivos_10j.csv) · [Auditoría y selección](datos/rf_robusto_10j/auditoria_y_seleccion_10j.json) · [Estado de publicación](datos/rf_robusto_10j/estado_publicacion_10j.json) · [CI de automejora](.github/workflows/oaf_10j_automejora.yml).

**Toda predicción oficial y monitoreo institucional del ENSO permanece separado del proyecto experimental del autor.**

## Resultados obtenidos de la ejecución 10J — evidencia real, 17/10/2026

[GitHub Actions de entrenamiento](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39092829210) completó la ingesta histórica reutilizada, las ocho pruebas de integridad, el entrenamiento de cuatro familias Random Forest en cinco pliegues y la auditoría de 9.360 pronósticos sector-mes. En 2021–2025 hubo **2.340 casos sector-mes**, **247 positivos ≥P90** y **155 positivos ≥P95**. P95 sigue siendo un extremo estadístico mensual relativo al sector.

### Elección estricta con validación 2016–2018

La mejor familia para **cada objetivo por cada bloque** resultó ser **lluvia histórica**, sin imponer variables atmosféricas adicionales. La corrección RF se parametrizó en esa misma validación. Los resultados de 2021–2025 de los modelos seleccionados (no elegidos viendo el test) fueron:

| Métrica de lluvia | Random Forest seleccionado | Climatología sectorial |
|---|---:|---:|
| MAE de precipitación mensual (mm) ↓ | 21,07159 | **14,29568** |
| RMSE de precipitación RF (mm) ↓ | 46,18250 | — |
| Brier de evento mensual ≥P90 ↓ | **0,0628431** | 0,0628840 |
| PR-AUC ≥P90 ↑ | 0,57223 | **0,60414** |
| Brier de evento mensual ≥P95 ↓ | 0,0471307 | **0,0469958** |
| Cobertura de banda empírica RF 90 % | 86,75 % | No aplica |
| Amplitud media de esa banda | 64,5767 mm | No aplica |

**Decisión científica:** RF no supera a climatología en MAE ni en Brier P95. En P90 la ventaja RF frente a la referencia es **−0,0000409 de Brier**, muy pequeña y con PR-AUC inferior. En la [auditoría emparejada recalculada desde el CSV completo](datos/rf_robusto_10j/comparacion_pareada_incertidumbre_10j.json), el intervalo de remuestreo exploratorio por cinco años para delta Brier (RF−climatología) fue **[−0,0108325; +0,0115818]**; por cinco bloques espaciales **[−0,0044275; +0,0024729]**. Ambos incluyen el cero. Estos intervalos no autorizan inferencia confirmatoria.

**Para 2023:** MAE RF **29,2415 mm** frente a climatología **24,8143 mm**; Brier ≥P90 RF **0,1220652** frente a climatología **0,1365946**; Brier ≥P95 RF **0,0989872** frente a climatología **0,1161087**. En ese episodio la habilidad probabilística RF fue mejor, pero siguió siendo peor su estimación en mm. La **cobertura empírica de la banda de lluvia cayó a 80,77 %**, por debajo de su nivel de referencia 90 %. No usar esta banda como garantía de riesgo extremo.

### Ablación física y efecto de imponer todos los factores

Los ensayos RF de todas las variables siguen disponibles para estudiar las contribuciones físicas, pero agregar factores que no mejoran validación debe poder recibir **peso cero**. Entre las cuatro familias, la variante lluvia+océano tuvo la mejor Brier P90 del test histórico, y lluvia+atmósfera el mejor Brier P95 del test. **Estas observaciones del test no reemplazan la elección preestablecida de 2016–2018**. Para lluvia en milímetros, ninguna variante seleccionada superó a climatología.

**Conclusión de publicación:** publicar la metodología, predicciones históricas, fuentes, desempeño por 2023 y territorios y límites de incertidumbre en la sección **«Investigación del autor»**. No emitir por ahora avisos automáticos, pronósticos oficiales, predicciones prospectivas o modelos fitosanitarios. El algoritmo puede mejorarse mediante futuras observaciones verificadas sin sustituir de inmediato un modelo evaluado.

### Automatización y artefacto reutilizable

- [Workflow automático mensual validado](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39093176254): ocho pruebas de integridad exitosas; **no había nuevos archivos 2026 en staging**, por lo que no se fabricó ni entrenó ficticiamente un candidato.
- [Código de fuente nueva y reentrenamiento](modelos/actualizacion_automatica_rf_10j.py): exige 39 sectores por mes, calendario completo, URL de origen, SHA y fecha; si falta información NOAA/NASA reciente, solo permite el brazo lluvia. Al actualizar, guarda candidato interno sin permiso de promoción automática.
- [Exportador del modelo entrenado](modelos/exportar_candidato_rf_10j.py) y [módulo de inferencia de lluvia](modelos/inferencia_rf_lluvia_10j.py): admiten un paquete de modelos RF con histórico hasta 2025, pesos fijos de validación y pronósticos solo cuando existan entradas hasta t−2. El modelo final reentrenado con toda la historia **no debe heredar como propias las métricas del ensayo original de cinco folds**. Sus pesos se guardan en artefactos CI, no como alerta pública.

