# Fase 9U — Selección condicionada por evidencia (17/10/2026)

## Resultado verificable
Se revisó el repositorio y no está disponible `resultados/9t/metricas_por_sector.csv`; la fase 9T figura expresamente como **no ejecutada en sectores reales**. Tampoco se encontró benchmark GCN. Por ello **ningún modelo ha demostrado todavía mayor exactitud para estos sectores**.

## Decisión de ingeniería
Se conserva **Random Forest como candidato técnico provisional**, no como vencedor científico. Se implementó `modelos/seleccion_modelo_9u.py` para auditar y comparar predicciones de 9T en exactamente los mismos pares sector-mes, publicar tablas de MAE/RMSE y seleccionar solo si RF supera a climatología. En caso contrario, se conserva la climatología como referencia y se rechaza la promoción de RF. La elección definitiva frente a GCN queda abierta.

## Cómo ejecutar, sin inventar resultados
1. Recuperar matriz CHIRPS histórica verificada por sector, 1996-2025, desde 9Q, con sectores y geometrias originales. Comprobar origen y fechas de publicación de CHIRPS.
2. `python modelos/fase_9t_pipeline.py --input datos/sectores_mensuales.csv --out resultados/9t`
3. `python modelos/seleccion_modelo_9u.py --predicciones resultados/9t/predicciones_fuera_muestra.csv --salida resultados/9u`
4. Incorporar posteriormente RF espacial y GCN temporal con el mismo conjunto de sectores, mismo test 2022–2025 y evaluación robusta por bloques; no usar test para optimizar los hiperparámetros.

## Restricciones
- CHIRPS es estimación grillada; no observación SENAMHI independiente.
- Sin datos por sector no hay cifras MAE, aciertos porcentuales ni mapas verificables.
- Los 5 puntos de monitoreo reciente 3Z no son sustituto de la matriz de sectores 9Q.
- Sin estudio del grafo, GCN sigue no evaluada.
- No presentar modelo como operativo ni publicar alertas de producción o fitosanitarias.
- La siguiente fase 9V deberá localizar la base sectorial, realizar experimentos en datos reales y contrastar independencia y calibración.
