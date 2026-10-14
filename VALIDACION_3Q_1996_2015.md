# OAF-Lambayeque | Validacion CHIRPS, PISCOp y ERA5 1996-2015

> Exploratorio: coordenadas historicas de estaciones sin confirmar.
> CHIRPS y PISCOp usan mediciones pluviometricas y pueden depender de estaciones contrastadas.
> La evaluacion NO cubre 1996-2025 ni equivale a validacion independiente.

## Calidad y cobertura

- Meses-estacion SENAMHI completos: **1109**.
- Meses-estacion con los tres productos comparables: **1109**.
- Pares estimacion-observacion: **3327**.
- Cobertura sobre meses validos: **100.0 %**.
- Sin imputacion de datos faltantes como lluvia cero.

## Estadisticas de todos los meses 1996-2015

| Estacion | Producto | Meses | MAE mm/mes | RMSE mm/mes | Sesgo % | Pearson |
|---|---|---:|---:|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 235 | 3.712 | 8.21 | 22.56 | 0.9557 |
| Cayaltí | ERA5-Seamless | 235 | 15.613 | 40.465 | 248.89 | 0.831 |
| Cayaltí | PISCOp v3.0 | 235 | 1.824 | 6.035 | 11.82 | 0.9856 |
| Cueva Blanca | CHIRPS v3 | 218 | 30.502 | 52.386 | -27.73 | 0.7327 |
| Cueva Blanca | ERA5-Seamless | 218 | 131.025 | 325.5 | 183.11 | 0.5737 |
| Cueva Blanca | PISCOp v3.0 | 218 | 29.257 | 41.255 | -34.43 | 0.8063 |
| Jayanca (La Viña) | CHIRPS v3 | 219 | 9.154 | 29.508 | -30.02 | 0.9197 |
| Jayanca (La Viña) | ERA5-Seamless | 219 | 104.953 | 259.292 | 724.56 | 0.9385 |
| Jayanca (La Viña) | PISCOp v3.0 | 219 | 3.104 | 10.566 | -16.89 | 0.9886 |
| Lambayeque | CHIRPS v3 | 204 | 3.394 | 10.905 | 13.63 | 0.8834 |
| Lambayeque | ERA5-Seamless | 204 | 11.313 | 41.811 | 273.7 | 0.8839 |
| Lambayeque | PISCOp v3.0 | 204 | 1.038 | 2.649 | -4.87 | 0.9798 |
| Reque | CHIRPS v3 | 233 | 2.986 | 6.209 | 12.67 | 0.8875 |
| Reque | ERA5-Seamless | 233 | 7.757 | 26.838 | 221.78 | 0.8782 |
| Reque | PISCOp v3.0 | 233 | 1.023 | 2.45 | 3.98 | 0.975 |

## Sensibilidad: excluyendo 1998

| Estacion | Producto | Meses | MAE mm/mes | Sesgo % |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 223 | 3.394 | 25.65 |
| Cayaltí | ERA5-Seamless | 223 | 12.954 | 319.26 |
| Cayaltí | PISCOp v3.0 | 223 | 1.327 | 4.81 |
| Cueva Blanca | CHIRPS v3 | 206 | 28.052 | -33.81 |
| Cueva Blanca | ERA5-Seamless | 206 | 101.387 | 140.59 |
| Cueva Blanca | PISCOp v3.0 | 206 | 28.808 | -37.48 |
| Jayanca (La Viña) | CHIRPS v3 | 207 | 6.664 | -19.99 |
| Jayanca (La Viña) | ERA5-Seamless | 207 | 81.214 | 967.07 |
| Jayanca (La Viña) | PISCOp v3.0 | 207 | 2.643 | -23.27 |
| Lambayeque | CHIRPS v3 | 192 | 2.609 | -13.65 |
| Lambayeque | ERA5-Seamless | 192 | 6.861 | 231.14 |
| Lambayeque | PISCOp v3.0 | 192 | 0.913 | -9.08 |
| Reque | CHIRPS v3 | 221 | 2.7 | -1.06 |
| Reque | ERA5-Seamless | 221 | 5.402 | 202.62 |
| Reque | PISCOp v3.0 | 221 | 0.999 | 3.32 |

## Procedencia

CHIRPS v3 mensual GeoTIFF de Climate Hazards Center, píxel que contiene el punto provisional.
SENAMHI: registros diarios descargados previamente, agregados solo con todos los días válidos.
PISCOp y ERA5: comparaciones guardadas en fase 3O para las mismas fechas.
Fuente CHIRPS: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
No usar como alerta fitosanitaria, pronóstico ni evidencia de precisión fuera de muestra.

Bloque 1996_2000: 300 meses-estacion, 0 incidencias.
Bloque 2001_2005: 289 meses-estacion, 0 incidencias.
Bloque 2006_2010: 284 meses-estacion, 0 incidencias.
Bloque 2011_2015: 236 meses-estacion, 0 incidencias.
