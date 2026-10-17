# Fase 9S — Protocolo de validación espacial y temporal (17/10/2026)

## Estado
**Diseño metodológico documentado; experimentos NO ejecutados en esta fase.**
No declarar vencedor GCN o Random Forest, porcentajes de acierto, mapas de habilidad ni alertas sin archivos de predicción y observación reproducibles.

## Antecedente que debe cotejarse
La fase 9Q reportó 360/360 meses CHIRPS v3 1996–2025 y propuso 7 parejas: S006–S007, S015–S016, S017–S018, S023–S029, S024–S027, S030–S031 y S040–S042. Esos productos aún deben vincularse en este repositorio con rutas, hashes y polígonos/sectores. Las parejas **no** son fusiones aprobadas.

## Hipótesis
Una GCN espacio-temporal podría mejorar la lluvia mensual de un sector frente a Random Forest al utilizar vecindad topográfica/climática; la mejora debe verificarse en datos fuera de muestra y compararse con climatología, persistencia y un RF con variables vecinales. La mayor complejidad no implica mejor desempeño.

## Dataset auditable
Por cada (sector_id, fecha_mes) incluir:
- identificador estable del polígono y geometría georreferenciada; área, elevación mediana/rango, piso ecológico, pendiente y cuenca;
- precipitación mensual CHIRPS v3 y cobertura/calidad por píxel o polígono, con URL, versión y fecha;
- predictores publicados **antes del inicio del mes objetivo**: rezagos de lluvia, anomalías calculadas sobre SOLO entrenamiento, mes del año cíclico y, si son históricamente disponibles en el origen, SST Niño 1+2, variables atmosféricas y T300;
- metadatos de disponibilidad real y período completo. Nunca reemplazar ausencia por lluvia cero o usar lluvia del mes pronosticado como predictor.
Los años 1996–2025 completos se refieren al producto CHIRPS reportado, NO a observaciones instrumentales completas SENAMHI.

## Protocolo temporal
Primer ensayo: entrenar 1996–2018; seleccionar hiperparámetros 2019–2021 con validación temporal expansiva; bloquear 2022–2025 para prueba final. Además ejecutar varios cortes retrospectivos con entrenamiento expansivo y un embargo temporal suficiente para las ventanas de entrada. Ajustar normalizaciones, selección de variables, pesos y agrupaciones solo con el conjunto de entrenamiento respectivo. Para probar generalización geográfica, repetir dejando sectores o grupos completos fuera del ajuste, sin permitir que su lluvia objetivo entre por nodos vecinos en el mismo horizonte.

## Modelos comparables
1. Climatología por mes calculada del entrenamiento; persistencia estacional.
2. RF con lluvia rezagada, ventana 3/6/12 meses, altitud, estacionalidad, SST disponible, e información vecinal rezagada como contraste justo.
3. GCN temporal: 12 meses de historia por nodo; convolución en grafo de adyacencia fijo elaborado de polígonos, distancia topográfica, cuenca y *similitud climática calculada SOLO con entrenamiento*, seguida de encoder temporal y cabeza de regresión no negativa; incluir ablation sin aristas climáticas.
La GCN no debe acceder a nodos con objetivos futuros; cuantificar incertidumbre con conjunto/ensemble y calibración sobre validación, no sobre test.

## Agrupación de pisos ecológicos y sectores
Registrar pisos y zonas en el polígono original. Probar las siete parejas como candidatas. Para cada pareja comparar distancia/continuidad, gradiente altitudinal, régimen lluvioso, correlación y distancia de series mensuales **del período de entrenamiento**, pendientes y exposición El Niño. Ejecutar variantes con y sin fusión; no fusionar si oculta extremos locales o perjudica la habilidad de alguno de los sectores. Conservar mapeo de polígonos originales para desagregar el pronóstico.

## Métricas y decisión
Para todos los modelos, el mismo conjunto de sector-mes (sin exclusiones oportunistas):
- MAE, RMSE, sesgo en mm; también MAE durante meses lluviosos y meses extremos;
- error por piso, sector, época húmeda/seca y episodios El Niño;
- habilidad frente a climatología = 1 − MAE_modelo/MAE_climatología, con denominadores válidos;
- contraste emparejado de diferencias de error, bootstrap por bloques de años y corrección por multiplicidad en análisis exploratorios;
- si se generan intervalos, cobertura y anchura de intervalos; si se generan probabilidades de excedencia, Brier/calibración.
Solo seleccionar GCN si supera las referencias y RF con evidencia consistente en test temporal y evaluación espacial; si empata, priorizar RF por interpretación y costo. Si ninguno supera climatología, mostrar que **no existe mejora demostrada**.

## Productos exigidos antes de publicar habilidad predictiva
1. Manifiesto del dataset, hashes SHA-256, geometría, fuente/versión y fechas de descarga.
2. Archivo de divisiones train/validation/test; lista de predictores, disponibilidad y grafo.
3. Ficheros CSV de cada predicción fuera de muestra por sector y mes, incluyendo valor observado, fecha de emisión y versión del modelo.
4. Tabla de métricas por modelo, piso, sector y evento extremo, gráficos de residuales y ablations.
5. Verificación independiente instrumental con estaciones SENAMHI cuando su cobertura/metadata y dependencia respecto de CHIRPS se hayan acreditado.
6. Solo entonces, panel web con leyendas entendibles para productores, etiquetas EXPERIMENTAL/NO VALIDADO/VALIDADO, incertidumbre y fuente.

## Criterios de seguridad científica
No presentar CHIRPS/ERA5 como observaciones instrumentales. No completar faltantes sin evidencia. La predicción retrospectiva de CHIRPS no es pronóstico validado contra pluviómetros. No emitir alertas del OAF sobre daños, inundaciones o enfermedades agrícolas; mostrar avisos oficiales SENAMHI/ENFEN diferenciados.

## Siguiente fase 9T
Construir pipeline reproducible: localizar efectivamente la matriz 9Q y geometrías de sectores, auditoría de integridad, extracción de features sin fuga, benchmarks basales/RF, GCN, conjunto de pruebas fuera de muestra y reporte de incertidumbre. **No asignar métricas ficticias antes de ejecutarlo**.
