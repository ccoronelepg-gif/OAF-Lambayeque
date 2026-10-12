# Fase 3N — Comparación de precipitación en estaciones de Lambayeque (1998)

> **EXPLORATORIO.** Las coordenadas documentales son preliminares y su
> correspondencia con emplazamientos históricos todavía requiere confirmación.
> PISCOp puede haber integrado estas observaciones en la producción del
> conjunto de datos; su contraste no equivale a validación independiente.

Se han comparado acumulados mensuales de 12 meses íntegros de 1998.
Sesgo = estimado - observado. MAE/RMSE calculados sobre **meses**.

Comparaciones obtenidas: **10/10**.

| Estación | Producto | Observado anual (mm) | Estimado anual (mm) | Sesgo mensual (mm) | MAE mensual (mm) | RMSE mensual (mm) | r Pearson |
|---|---|---:|---:|---:|---:|---:|---:|
| Jayanca (La Viña) | PISCOp v3.0 | 1428.0 | 1296.71 | -10.941 | 11.057 | 22.627 | 0.9979 |
| Jayanca (La Viña) | ERA5-Seamless | 1428.0 | 7603.9 | 514.658 | 514.658 | 928.088 | 0.9781 |
| Cayaltí | PISCOp v3.0 | 558.5 | 685.56 | 10.588 | 11.053 | 22.681 | 0.9928 |
| Cayaltí | ERA5-Seamless | 558.5 | 1335.6 | 64.758 | 65.01 | 141.701 | 0.8413 |
| Reque | PISCOp v3.0 | 232.82 | 245.46 | 1.054 | 1.477 | 2.721 | 0.9981 |
| Reque | ERA5-Seamless | 232.82 | 846.4 | 51.132 | 51.132 | 108.893 | 0.9372 |
| Lambayeque | PISCOp v3.0 | 279.61 | 288.23 | 0.718 | 3.029 | 6.649 | 0.9887 |
| Lambayeque | ERA5-Seamless | 279.61 | 1270.2 | 82.549 | 82.549 | 163.82 | 0.9372 |
| Cueva Blanca | PISCOp v3.0 | 969.2 | 1044.23 | 6.253 | 36.963 | 49.802 | 0.9015 |
| Cueva Blanca | ERA5-Seamless | 969.2 | 8451.4 | 623.517 | 640.117 | 1150.625 | 0.7657 |

## Procedencia y advertencias
- Observaciones: agregados mensuales calculados de cinco archivos TXT SENAMHI aportados al estudio.
- PISCOp: servicio externo https://fluviotech.com/meteodata/pisco/api/docs/
- ERA5-Seamless: https://open-meteo.com/en/docs/historical-weather-api
- Los productos se extraen para las mismas coordenadas solicitadas, pero **sus celdas espaciales son diferentes**.
- Los extremos climáticos no deben explicarse solo por una correlación; verificar cobertura, metodología y estación.
- No considerar esta primera muestra de un año como demostración de precisión histórica general.
- No extrapolar resultados observados a parcelas de arándano sin validación en campo.

## Metadatos espaciales empleados

| Estación | Latitud | Longitud | Procedencia preliminar |
|---|---:|---:|---|
| Jayanca (La Viña) | -6.322 | -79.779 | SENAMHI informe de Jayanca 2017 |
| Cayaltí | -6.88079444 | -79.54701389 | SENAMHI ficha Cayalti 000320 |
| Reque | -6.88613 | -79.8355 | ANA citada en repositorio Universidad Ricardo Palma |
| Lambayeque | -6.73152778 | -79.90983611 | Ficha SENAMHI reproducida en documento historico; confirmar |
| Cueva Blanca | -6.1313 | -79.4045 | SENAMHI informe norte 2020: ~-6.13,-79.40, 3300 m |
