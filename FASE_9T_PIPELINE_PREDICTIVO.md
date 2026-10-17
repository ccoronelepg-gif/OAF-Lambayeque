# Fase 9T — Implementación del benchmark temporal

> **Actualización verificable 9W (17/10/2026):** este texto registra el estado previo de búsqueda o de diseño metodológico y **ya no describe la disponibilidad actual de datos**. Existen 360 meses CHIRPS v3 final en 9O+9P+9Q, predicciones GCN y Random Forest realmente ejecutadas en 9R, y una segunda ejecución RF 9T/selección 9U sobre 39 sectores con enlace de procedencia comprobado en [FASE_9W_RECONCILIACION_PREDICTIVA.md](FASE_9W_RECONCILIACION_PREDICTIVA.md). El mejor MAE observado en 9R es de la climatología, no de IA. Estos ensayos son **retrospectivos y NO constituyen habilidad operativa validada**. Conservar las recomendaciones de validación espacial como tareas pendientes.


**Fecha:** 17/10/2026. **Estado:** código de benchmark incorporado; ejecución sobre matriz sectorial real **pendiente**.

Se comprobaron rutas del repositorio: existe `datos/chirps_v3_reciente_3z.csv` con cinco puntos de referencia y meses recientes. No se localizaron bajo los nombres comprobados las matrices sectoriales 9Q/9R ni las geometrías. Estas cinco estaciones referenciales NO equivalen a los sectores S001–S042 y no se utilizarán para simular resultados sectoriales.

## Implementado
- `modelos/fase_9t_pipeline.py`: valida formato, duplicados, lluvia ausente/negativa, período íntegro 1996–2025 y genera el SHA-256 del archivo original.
- Features exclusivamente con rezagos mensuales; comparación climatología mensual de entrenamiento, persistencia estacional y Random Forest determinista.
- Cortes 1996–2018 entrenamiento / 2019–2021 validación / 2022–2025 prueba.
- Exporta por sector, modelo y mes predicciones fuera de muestra, métricas MAE/RMSE/sesgo y manifiesto de procedencia.
- Rechaza datos incompletos; sin imputación ni falsos ceros. No publica habilidad ni porcentajes sin ejecución.

## Entrada exigida
CSV real con columnas `sector_id,mes,lluvia_mm`, una fila por sector/mes, fechas `YYYY-MM`, 360 meses consecutivos por sector en 1996–2025, valores CHIRPS verificados. La fase 9Q debe aportar además el identificador y la geometría de polígonos; después se crearán el grafo de vecindad y el benchmark GCN. Se debe conservar la ruta/versión original de CHIRPS y verificar si los rezagos estaban disponibles en la fecha de emisión.

## Ejecución
```bash
python -m pip install numpy pandas scikit-learn
python modelos/fase_9t_pipeline.py --input datos/sectores_mensuales.csv --out resultados/9t
```

## Limitaciones
Este primer benchmark opera por sector y no utiliza todavía vecinos, altitud, cuenca, SST ni redes neuronales: no constituye una comparación final equitativa entre RF y GCN. Random Forest es un primer control reproducible. Ni el código incorporado ni la serie reciente parcial permiten afirmar calidad prospectiva o validación instrumental.

## Próxima fase 9U
Identificar y vincular matriz real y geometrías de 9Q con hashes; definir adyacencia topográfica y distancias; implementar RF con vecinos rezagados y GCN temporal con exactamente los mismos cortes y variables, y ejecutar la comparación controlada con intervalos de incertidumbre.
