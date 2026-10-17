# Fase 9X — Generalización espacial de Random Forest y convolución de grafos para precipitación

**OAF-Lambayeque · 17 de octubre de 2026.** Ensayo experimental ejecutado sobre CHIRPS v3 **final** 1996–2025. **No es predicción prospectiva certificada ni pronóstico fitosanitario operativo**.

## 1. Pregunta científica

La comparación anterior 9R/9W entrenó y evaluó los mismos **39 sectores** en años distintos. En ese diseño temporal, el MAE 2021–2025 fue **14,30 mm para la climatología histórica, 15,54 mm para Random Forest y 18,47 mm para GCN**. La referencia climatológica superó a ambas IA.

**9X responde una pregunta distinta:** ¿qué método puede estimar lluvia mensual **en otros sectores físicos que nunca estuvieron en su entrenamiento**, cuando el sector nuevo sí dispone de lluvia histórica rezagada? Es una forma limitada de transferencia espacial *inductiva*. No se entrena sobre los resultados de la zona de prueba y no se utiliza el futuro como predictor, pero se necesita el dato CHIRPS del mes anterior **del propio sector de prueba** y otros meses rezagados. Por eso **NO se demuestra extrapolación a una parcela sin estaciones o sin antecedentes de lluvia**.

## 2. Fuente real y protección de series

El archivo [matriz_sectores_chirps_9w.csv](datos/validacion_9w/matriz_sectores_chirps_9w.csv), derivado de **108 meses 9O + 12 meses 9P + 240 meses 9Q = 360** por sector, fue sometido al puente de auditoría 9W. Contiene **39 sectores × 360 meses = 14.040 valores sector-mes** que se corresponden con los originales CHIRPS v3 final, con fuentes identificadas por URL y SHA-256. Se excluyen **S028, S032 y S034** porque no tienen un píxel terrestre CHIRPS válido con centro dentro del polígono; no se completan valores a partir de vecinos.

El ensayo usa la **misma lluvia del producto final retrospectivo** como variable objetivo y, cuando se predice cada mes de prueba, las lluvias anteriores del sector como predictores. La lluvia CHIRPS combina estimación satelital y estaciones: la validación frente a esta rejilla **no reemplaza los pluviómetros independientes SENAMHI**. La geometría de 9K y las revisiones finales CHIRPS se compilaron después del periodo de prueba, por lo que no se garantiza disponibilidad real en cada fecha de emisión histórica.

## 3. Protocolo estricto de partición y entrenamiento

Los 39 sectores se separaron en **cinco bloques geográficos** mediante agrupamiento k-means de los centroides de polígonos, con semilla fija 20261017 y **sin utilizar lluvia para asignar bloques**. Se comprueba la identidad de las celdas CHIRPS de 0,05° que caen dentro de cada sector y se rechaza la prueba si dos bloques comparten exactamente una celda de lluvia. El resultado esperado es **cero celdas compartidas entre bloques**. No obstante, evitar la misma celda no elimina autocorrelaciones atmosféricas, diferencias de cuenca ni dependencia de estaciones incorporadas al producto.

Para cada bloque, los modelos usan exclusivamente **sectores externos a ese bloque** para ajustar pesos y árboles y para decidir sus hiperparámetros o parada temprana:

| Rol | Fecha | Sectores |
|---|---|---|
| Entrenamiento | **1997-01 a 2015-12** | Solo los otros cuatro bloques |
| Validación para parámetros/parada | **2016-01 a 2020-12** | Solo los otros cuatro bloques |
| Prueba final espacial y temporal | **2021-01 a 2025-12** | Únicamente el bloque reservado |

Los meses de 1996 permiten construir rezagos de 12 meses al iniciar 1997. Se ajustan escalas **solo con entrenamiento** y se preservan para transformar los sectores de prueba. Los lags `t-1, t-2, t-3, t-6, t-12`, el promedio previo de tres meses, seno/coseno del mes y elevación/ubicación SIG se conocen sin usar lluvia futura. Para comparabilidad, Random Forest y GCN reciben además exactamente los mismos **tres rezagos medios de sus vecinos disponibles y un grado del grafo**, calculados dentro del subgrafo de entrenamiento y, por separado, dentro del bloque de prueba. Si un nodo carece de vecinos, esos tres valores son sus propios rezagos. Las aristas obedecen la proximidad, altitud y unidad hidrológica **físicas** de 9K, no correlaciones calculadas con lluvia de años reservados.

Las redes GCN se entrenan únicamente sobre los nodos de los cuatro bloques de entrenamiento. En la inferencia se proporciona el subgrafo del bloque nuevo: **ningún objetivo ni etiqueta del bloque reservado se utiliza para entrenar, validar o ajustar parámetros**. Son GCN de grafos y NO redes convolucionales de imágenes 2D.

## 4. Métodos comparados y criterio principal

Se presentan cinco predictores: (a) climatología mensual **regional**, aprendida en otros sectores; (b) climatología mensual **por piso altitudinal** de sectores externos, con fallback a la regional cuando un piso no estuvo representado; (c) persistencia anual `t-12` del sector de prueba; (d) **Random Forest** de 160 árboles, profundidad máxima 15 y selección de hoja mínima 3 u 8 según MAE de validación; (e) **GCN** convolucional de grafos con dos capas, 32 unidades ocultas, dropout 0,13 y validación con parada temprana.

Los modelos puntúan exactamente **39 sectores × 60 meses = 2.340 casos sector-mes cada uno**, una sola vez por sector y con idéntico objetivo CHIRPS. Se calculan MAE, RMSE y sesgo mensual, desglosados por piso y año. El criterio principal para proponer algún modelo es el **MAE menor** frente a la climatología de su propio protocolo.

El ejercicio realiza además un bootstrap **sobre cinco bloques geográficos enteros**, 5^5 = 3125 combinaciones posibles, para el diferencial emparejado de MAE: primer método menos segundo (positivo significa peor). Esta medida representa solamente variabilidad descriptiva de los bloques de este protocolo, no intervalos de confianza instrumentales independientes ni pronósticos futuros.

## 5. Resultados del ensayo y su lectura

**Primera ejecución registrada:** MAE climatología regional **24,3027 mm**, climatología por piso **20,3708 mm**, persistencia anual **21,8341 mm**, Random Forest **17,1723 mm**, GCN **18,5370 mm**. La primera corrida de entrenamiento concluyó y calculó estas métricas; su flujo inicialmente falló después en la prueba de navegación porque el visor 9X todavía no estaba incorporado a aquel commit. El reporte estructurado en [evaluacion_bloques_espaciales_9x.json](datos/generalizacion_9x/evaluacion_bloques_espaciales_9x.json) prevalece cuando la auditoría completa se reproduzca y publique.

**Interpretación:** en esta prueba de **transferencia geográfica**, Random Forest mostró inicialmente menor MAE que GCN y que el baseline de piso. Esto **no contradice** que la climatología obtuviera mejor MAE en 9R: 9R y 9X responden preguntas distintas, porque 9R sí había entrenado con los mismos sectores y 9X excluye sectores completamente. Además, la climatología por piso de 9X tiene sectores nuevos donde su promedio histórico fue calculado sobre otras ubicaciones, por lo que su desempeño y significado cambian.

No se deben proclamar capacidades de pronóstico real al agricultor ni cambios operativos en el portal basados en estos datos. Los cinco pliegues son pocos para decidir capacidad generalizable a nuevas cuencas y pueden conservar correlaciones por sistemas meteorológicos comunes.

## 6. Resultados disponibles, trazabilidad y siguiente trabajo

- [Motor de evaluación espacial reproducible](modelos/generalizacion_espacial_9x.py).
- [Asignación a cinco bloques, hiperparámetros y exclusión de etiquetas](datos/generalizacion_9x/bloques_geograficos_9x.json).
- [Todas las predicciones sector-mes de prueba](datos/generalizacion_9x/predicciones_sector_bloque_9x.csv).
- [Indicadores por modelo, piso, año y bootstrap](datos/generalizacion_9x/evaluacion_bloques_espaciales_9x.json).
- [Pruebas de independencia de los conjuntos y honestidad científica](tests/test_generalizacion_9x.py).
- [GitHub Actions 9X](.github/workflows/oaf_generalizacion_9x.yml).
- [Visor gráfico del portal](modelos/visor_generalizacion_9x.js) bajo **Análisis de clima regional**.

La siguiente etapa científica debe evaluar especialmente lluvia intensa y episodios El Niño con un contraste espacial y temporal suficiente, incorporar estaciones independientes SENAMHI con fecha/ubicación y dependencia respecto de CHIRPS auditadas, y ensayar predictores oceánicos con vintage o fecha de disponibilidad real anterior al mes objetivo. La homogeneidad de siete pares del 9Q sigue siendo **hipótesis cartográfica**, no un hecho ambiental validado.

**Decisión vigente:** los resultados son únicamente retrospectivos. **0 zonas climáticas homogéneas certificadas, 0 modelos operativos habilitados, 0 alertas fitosanitarias emitidas**.

**Lema OAF:** «Datos abiertos y ciencia climática al servicio del campo».
