# Validación 3O: precipitación multianual 1996–2015

> **RESULTADOS EXPLORATORIOS**. Los cálculos usan meses completos de cinco archivos
> históricos SENAMHI y ubicaciones documentales **preliminares**. PISCOp podría
> usar estaciones del SENAMHI en su interpolación: NO es validación independiente.

## Cobertura y procedimiento

- Meses-estación completos de lluvia instrumental: **1109**.
- Pares observación-estimación obtenidos: **2218**.
- Combinaciones estación × producto: **10/10**.
- Comparación mes a mes, solo coincidencias de fecha y posición solicitada.
- Las estadísticas separan todos los meses, el año 1998 y los otros años.
- El porcentaje es sesgo acumulado (suma estimada - suma observada) / suma observada.
- No existen datos SENAMHI disponibles posteriores a 2015 en los archivos cargados.

## Estadísticas por estación/producto (solo estrato **todos**)

| Estación | Producto | Meses | Obs. (mm) | Est. (mm) | Sesgo mes (mm) | MAE mes (mm) | RMSE mes (mm) | Sesgo total (%) | Pearson |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Jayanca (La Viña) | PISCOp v3.0 | 219 | 3148.9 | 2617.13 | -2.428 | 3.104 | 10.566 | -16.89 | 0.9886 |
| Jayanca (La Viña) | ERA5-Seamless | 219 | 3148.9 | 25964.6 | 104.181 | 104.953 | 259.292 | 724.56 | 0.9385 |
| Cayaltí | PISCOp v3.0 | 235 | 1429.53 | 1598.51 | 0.719 | 1.824 | 6.035 | 11.82 | 0.9856 |
| Cayaltí | ERA5-Seamless | 235 | 1429.53 | 4987.5 | 15.14 | 15.613 | 40.465 | 248.89 | 0.831 |
| Reque | PISCOp v3.0 | 233 | 740.06 | 769.55 | 0.127 | 1.023 | 2.45 | 3.98 | 0.975 |
| Reque | ERA5-Seamless | 233 | 740.06 | 2381.4 | 7.044 | 7.757 | 26.838 | 221.78 | 0.8782 |
| Lambayeque | PISCOp v3.0 | 204 | 808.93 | 769.5 | -0.193 | 1.038 | 2.649 | -4.87 | 0.9798 |
| Lambayeque | ERA5-Seamless | 204 | 808.93 | 3023.0 | 10.853 | 11.313 | 41.811 | 273.7 | 0.8839 |
| Cueva Blanca | PISCOp v3.0 | 218 | 14382.3 | 9429.84 | -22.718 | 29.257 | 41.255 | -34.43 | 0.8063 |
| Cueva Blanca | ERA5-Seamless | 218 | 14382.3 | 40718.3 | 120.807 | 131.025 | 325.5 | 183.11 | 0.5737 |

## Control de calidad y limitaciones

- Valores diarios ausentes se conservan como ausentes: no se asignan a precipitación 0.
- Meses con un día de observación ausente no se incluyen. ERA5 también requiere todos los días.
- La serie PISCOp se obtiene mediante API externa Fluviotech. Evitar inferir independencia estadística.
- El conjunto ERA5-Seamless de Open-Meteo es híbrido; no equipararlo automáticamente a ERA5-Land oficial.
- Las celdas y representatividad orográfica difieren entre fuentes y estación.
- Extremos como 1998 pueden dominar las métricas; por ello se informa estrato sin 1998.
- Correlación alta no equivale a ausencia de sesgo.

## Fuentes técnicas

- https://fluviotech.com/meteodata/pisco/api/docs/
- https://open-meteo.com/en/docs/historical-weather-api
- Archivos históricos SENAMHI TXT aportados por el investigador.
