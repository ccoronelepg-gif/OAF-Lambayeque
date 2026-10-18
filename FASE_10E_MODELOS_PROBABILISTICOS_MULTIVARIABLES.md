# Fase 10E — Dos líneas de información y modelos probabilísticos multivariables del autor

**Fecha de ejecución:** 17 de octubre de 2026  
**Objetivo:** distinguir rigurosamente entre **información institucional de terceros** y **algoritmos experimentales entrenados por el autor** en el OAF-Lambayeque.

## I. Arquitectura pública del observatorio

**A. Fuentes oficiales e institucionales**: se mantienen enlaces, fechas, emisores, datos, pronósticos y avisos de organismos como SENAMHI y ENFEN, y conjuntos de datos abiertos NOAA/Copernicus/CHIRPS. Los productos NOAA/Copernicus/CHIRPS **son fuentes de datos**, no necesariamente alertas oficiales peruanas.

**B. Modelos del autor — investigación experimental**: resultados de algoritmos RF/GCN entrenados por el desarrollador, con especie, localidad, horizonte, variable objetivo, periodo entrenamiento/calibración/prueba, métricas probabilísticas y advertencias. Separar claramente **(i) lluvia intensa**, **(ii) anomalías y escenarios de El Niño costero y El Niño global**, **(iii) condiciones predisponentes a enfermedades de arándano/vid**. Ninguna de las tres metas se resuelve automáticamente con el mismo modelo: lluvia, temperatura del mar y enfermedades son **etiquetas diferentes**. Sin registros fitosanitarios de campo no se dispone de modelo validado de infección.

## II. Alcance efectivo de los datos multivariables

Se auditaron los archivos del proyecto:
- `datos/integracion_8v/matriz_terrestre_8v.csv`: **4 localidades × 360 meses (1996–2025)**, datos ERA5/ERA5-Land para precipitación, temperatura, radiación, vientos y anomalías NOAA Niño 1+2 / Niño 3.4.
- `datos/humedad_8z/humedad_vpd_mensual_8z.csv`: humedad relativa y déficit de presión de vapor, misma resolución nominal de cuatro localidades.
- `datos/integracion_8v/matriz_marina_8v.csv`: viento marino de dos puntos de muestreo, **no colocados** en la misma celda que cada localidad.
- `datos/noaa_cpc_predictores_atmosfericos_8b.csv`: índice SOI y alisios orientales.
- `datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv`: **solo 2017–2025**, componentes geostróficas y puntos no colocados con fuentes terrestres. **Se incluyen en inventario pero NO como predictoras**: rellenar 1996–2016 sería invención de datos.
- `datos/validacion_9w/matriz_sectores_chirps_9w.csv`: 39 sectores CHIRPS, pero **no coincide espacialmente con el conjunto multivariable**. La evaluación de 39 sectores en fases 9X–10D no se mezcla con el nuevo benchmark de cuatro localidades.

En el CSV 8V constan **11 meses-localidad con precipitación de reanálisis ≥1000 mm y etiqueta de revisión**. El código no los elimina silenciosamente; verifica el número de valores marcados y cuántos afectan la prueba.

**Fuentes públicas oficiales:**
- [CHIRPS v3, UCSB Climate Hazards Center](https://www.chc.ucsb.edu/data/chirps3), datos v3 Final publicados normalmente en la tercera semana del mes siguiente.
- [ERA5, ECMWF/Copernicus](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5), reanálisis atmosférico.
- [NOAA/CPC ENSO](https://www.cpc.ncep.noaa.gov/), series del Pacífico tropical.
- [ENFEN](https://enfen.imarpe.gob.pe/), vigilancia oficial del Niño costero y global; [SENAMHI](https://www.senamhi.gob.pe/), pronósticos/avisos meteorológicos peruanos.

## III. Modelo probabilístico experimental

**Objetivo único de esta fase:** estimar la probabilidad de que la precipitación **mensual de ERA5 supere el percentil 90 histórico de la localidad**. El percentil se aprende solo en entrenamiento 1997–2015, no del periodo de prueba. Es un indicador estadístico de mes lluvioso para cada localidad, NO un umbral de desastre ni una definición operativa de evento El Niño costero.

**Predictores con rezago de 2 meses o más:** lluvia acumulada de 2, 3, 6 y 12 meses atrás; lluvia media t−2:t−4; temperatura aire, radiación solar, rapidez/componentes del viento, humedad, VPD, temperatura de la superficie oceánica representada por anomalías Niño 1+2 / Niño 3.4, SOI y alisios del Pacífico oriental, más viento marino y atributos estáticos espaciales. Los índices SST NOAA no equivalen a SST costera in situ. No se incluyó lluvia, temperatura, radiación o viento del mismo mes que se pretende predecir. Sin datos homologados, no se incorporan corrientes, presión atmosférica, nubosidad o humedad foliar como si estuvieran medidas.

**Modelos:**
- `RF_multivariable` contra `GCN_multivariable` con las mismas covariables; RF incorpora rezagos vecinales, GCN propaga información mediante un **grafo de cuatro nodos** basado en vecindad geográfica. No es una CNN 2D sobre píxeles.
- `RF_solo_lluvia` y `GCN_solo_lluvia` como ablación para probar si las variables oceanoatmosféricas aportan una mejora.
- `climatologia_local_estacional`: frecuencia de excedencia mensual por localidad estimada **solo** del conjunto entrenamiento; sirve como línea base simple.

**Calendario estrictamente temporal:** train 1997–2015, selección de parámetros 2016–2018, calibración Platt 2019–2020 y evaluación 2021–2025. El corte de probabilidad para una regla exploratoria se selecciona en 2019–2020, nunca usando etiquetas de prueba.

**Métricas apropiadas:** Brier (cuanto menor, mejor), log loss, PR-AUC, ROC-AUC, sensibilidad, precisión, tasa de falsos positivos, desglose por localidad y año 2023. Clasificar aciertos por exactitud binaria solamente puede ser engañoso con eventos poco frecuentes.

## IV. Selección del modelo para la web

Un **modelo se puede destacar para consulta científica** solo si mejora el Brier respecto de la climatología y supera su PR-AUC con un mínimo de 15 eventos positivos en prueba. En caso contrario, el software se abstiene. El modelo publicado como destacado será **solamente una referencia experimental en cuatro localidades**, no el «mejor de todo Lambayeque» ni un algoritmo habilitado para emitir avisos. El resultado de la ejecución se publicará en el informe JSON y en la sección **Modelos del autor**.

**Ningún algoritmo queda autorizado** para avisos de lluvia, El Niño/La Niña o enfermedades agrícolas hasta validación prospectiva as-issued, contraste con estaciones independientes y comprobación de costo de falsas alarmas. Las series históricas de ERA5, CHIRPS y NOAA revisadas retrospectivamente no equivalen a datos que efectivamente estaban disponibles en fechas pasadas.

## V. Proyecciones fitosanitarias y oceánicas pendientes

- **Enfermedades de arándano y vid:** en adelante alimentar con temperatura, RH/VPD, radiación, lluvia, duración de humectación foliar y **registros de severidad/incidencia en campo por fecha y lote**. Sin etiología/confirmación de diagnóstico no se puede entrenar un clasificador de infecciones reales. Por ahora, solo predisposición agroclimática y antecedentes científicos.
- **Niño costero/global:** objetivo específico sobre anomalía SST Niño 1+2, condiciones atmosféricas y eventual transición oficial; no reutilizar directamente las etiquetas de lluvia intensa como etiquetas de Niño. ENFEN conserva primacía para la condición oficial del evento.
- **Corrientes/cizalladura/upwelling/presión/nubosidad:** recuperar datos temporales y espacialmente compatibles antes de incorporarlos a un modelo de riesgo ENSO/lluvia con trazabilidad y sin imputaciones espurias.

## VI. Archivos ejecutables

[Motor y configuración](modelos/probabilidad_multivariable_10e.py) · [Tests de QA](tests/test_probabilidad_10e.py) · [CI verificable](.github/workflows/oaf_10e_probabilidad.yml) · [Métricas JSON al finalizar ejecución](datos/probabilidades_10e/evaluacion_probabilistica_10e.json) · [Probabilidades retrospectivas](datos/probabilidades_10e/predicciones_probabilisticas_10e.csv).

Los textos del portal diferencian **fuente oficial** y **modelo experimental entrenado por el autor**, sin atribuirse aprobación institucional ni certificación externa.

## VII. Resultados de la evaluación reproducida (ejecución 10E)

[GitHub Actions verificado](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39081906133) ejecutó satisfactoriamente **siete pruebas**, entrenó dos RF y dos GCN con distintas familias de covariables y creó el informe y las 1.200 predicciones retrospectivas (cuatro localidades × 60 meses de test × cinco métodos). La clase positiva se definió con el percentil 90 local estimado solo a partir de 1997–2015.

| Modelo | Brier ↓ | PR-AUC ↑ | ROC-AUC ↑ | 2023 Brier ↓ |
|---|---:|---:|---:|---:|
| Climatología local estacional | **0,077467** | **0,59098** | **0,92421** | 0,128617 |
| Random Forest multivariable | 0,088183 | 0,57437 | 0,90048 | **0,114716** |
| Random Forest solo lluvia | 0,105151 | 0,53832 | 0,86206 | 0,163238 |
| GCN solo lluvia | 0,106848 | 0,39052 | 0,86032 | 0,167921 |
| GCN multivariable | 0,111878 | 0,37560 | 0,86063 | 0,181137 |

Prueba 2021–2025: **240 casos localidad-mes; 30 positivos (12,5 %)**; 2023: 48 casos, 10 positivos.

**El mejor de los modelos de IA** según Brier, PR-AUC y ROC-AUC de este benchmark es **Random Forest multivariable**, y utilizar covariables océano-atmósfera se asocia a menor Brier para RF que usar solo lluvia. Pero **la climatología estacional local obtiene menor Brier y mayor PR-AUC que cualquier algoritmo de IA**. La decisión codificada es, por tanto, `modelo_destacado_experimental_si_supera_climatologia: null`: **no hay modelo elegido para publicación como pronóstico validado**. Se puede visualizar RF multivariable como el modelo de IA con mejor resultado descriptivo, con el contraste completo y sin avisos.

Umbrales de evento de lluvia mensual ≥P90 (mm), obtenidos solamente en train: **Chiclayo 32,61; Jayanca 237,03; Motupe 287,25; Olmos 229,12**. La marcada heterogeneidad refleja diferencias de series ERA5 y no define umbrales reglamentarios de riesgo. En el archivo existen 11 observaciones de lluvia modelada ≥1000 mm marcadas para revisión (ninguna corresponde a 2021–2025); su influencia sobre entrenamiento merece análisis robusto posterior.

En prueba, usando cortes probabilísticos fijados solo con 2019–2020:
- **RF multivariable:** 13 detecciones correctas, 17 omisiones, 15 falsas alarmas; sensibilidad 43,33 %, precisión 46,43 %.
- **GCN multivariable:** 15 detecciones, 15 omisiones, 29 falsas alarmas; sensibilidad 50 %, precisión 34,09 %.
- **Climatología estacional:** 24 detecciones, 6 omisiones, 21 falsas alarmas; sensibilidad 80 %, precisión 53,33 %.

La prueba es sobre una etiqueta **percentil-90 local ERA5**; no comparar esas tasas con los 137 casos CHIRPS de la fase 10D ni presentar ambos como el mismo evento.

### Análisis de incertidumbre emparejado (cinco años)
[Auditoría complementaria de diferencias Brier](datos/probabilidades_10e/auditoria_incertidumbre_10e.json): RF multivariable menos GCN multivariable **−0,023695**, intervalo exploratorio con bloques anuales **[−0,052118; +0,002957]**. El intervalo incluye cero; **no se demuestra con significación confirmatoria una ventaja temporalmente robusta**. RF multivariable menos climatología local **+0,010716**, intervalo anual **[−0,011460; +0,047987]**; tampoco permite concluir superioridad a la referencia.

**Conclusión científica:** RF es el candidato de IA a seguir investigando para estas cuatro localidades, pero no ha superado el modelo sencillo de referencia. La web debe permitir evaluar las cinco alternativas, su sensibilidad ante extremos, sus variables de entrada y sus limitaciones. La GCN conserva un lugar comparativo, no de despliegue.

