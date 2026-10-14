# OAF-Lambayeque | Sensibilidad geográfica multianual CHIRPS 1996–2015

> **Exploratorio**: no se ha confirmado la identidad ni continuidad instrumental entre coordenadas documentales.
> La mejor coincidencia estadística NO demuestra la ubicación verdadera de la estación.
> Los datos instrumentales de 2016–2025 no están incluidos.

## Auditoría de integridad

- Meses-estación completos de SENAMHI: **1109**.
- Extracciones de CHIRPS (dos coordenadas): **2218**.
- Reproducción de CHIRPS 3Q: **confirmada**.
- Reproducción del piloto 3R de 1998 y 2000: **confirmada**.
- Fallos de descarga en los bloques: **0**.

## Variación espacial y errores mensuales

| Estación | Meses | Meses mismo píxel | Distancia puntos (km) | Cambio acumulado CHIRPS (mm) | MAE coordenada 3Q | MAE alternativa |
|---|---:|---:|---:|---:|---:|---:|
| Cayaltí | 235 | 0 | 2.415 | -195.714 | 3.712 | 3.651 |
| Cueva Blanca | 218 | 0 | 6.339 | 1981.387 | 30.502 | 27.999 |
| Jayanca (La Viña) | 219 | 219 | 1.683 | 0.0 | 9.154 | 9.154 |
| Lambayeque | 204 | 204 | 3.356 | 0.0 | 3.394 | 3.394 |
| Reque | 233 | 233 | 0.042 | 0.0 | 2.986 | 2.986 |

## Sensibilidad excluyendo 1998

| Estación | Meses | Cambio acumulado CHIRPS (mm) | MAE original | MAE alternativa |
|---|---:|---:|---:|---:|
| Cayaltí | 223 | -147.858 | 3.394 | 3.14 |
| Cueva Blanca | 206 | 1841.585 | 28.052 | 24.759 |
| Jayanca (La Viña) | 207 | 0.0 | 6.664 | 6.664 |
| Lambayeque | 192 | 0.0 | 2.609 | 2.609 |
| Reque | 221 | 0.0 | 2.7 | 2.7 |

## Interpretación y límites

El efecto observado depende de la celda CHIRPS de 0,05 grados. No equivale a la magnitud de un error de GPS, ni permite deducir reubicaciones de instrumentos.
El punto de Cueva Blanca alternativo procede de un documento con código/ubicación discordantes; no atribuir sus valores a la serie histórica.
Un cambio de píxel con mayor MAE puede deberse a heterogeneidad espacial o dependencia de pluviómetros; no evaluar ubicación mediante el ajuste estadístico.
Las estaciones meteorológicas pueden haber intervenido en CHIRPS; no es una validación independiente.
Solo lluvia mensual; no construir pronósticos ni alertas fitosanitarias a partir de esta sensibilidad.

Datos: datos/sensibilidad_3r_1996_2015.csv y datos/metricas_sensibilidad_3r_1996_2015.csv.
Código reproducible: scripts/sensibilidad_3r_multianual.py y scripts/consolidar_sensibilidad_3r.py.
Fuente CHIRPS: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
