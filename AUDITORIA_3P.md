# OAF-Lambayeque: Fase 3P — Auditoría espacial y modelos ERA5

> **Exploratorio**: los metadatos geográficos de las estaciones son provisionales.
> No declarar este contraste como calibración operativa ni validación general 1996–2025.

## Diseño

Se consultaron por separado ERA5-Seamless, ERA5 y ERA5-Land en el API de Open-Meteo.
Los criterios `nearest` y `land` se prueban en 1998; en 2000 se usa `nearest`.
Se muestran las coordenadas efectivamente devueltas por el API y su distancia al punto solicitado.
La distancia espacial NO demuestra por sí misma la causa de los sesgos.

**Consultas completas: 30 / 45; incidencias: 15.**

## Acumulados y distancias

| Estación | Año | Celda | Modelo | Observado (mm) | Estimado (mm) | Sesgo (%) | Distancia (km) |
|---|---:|---|---|---:|---:|---:|---:|
| Jayanca (La Viña) | 1998 | nearest | era5_seamless | 1428.0 | 7601.4 | 432.31 | 3.372 |
| Jayanca (La Viña) | 1998 | nearest | era5 | 1428.0 | 7601.4 | 432.31 | 8.624 |
| Jayanca (La Viña) | 1998 | land | era5_seamless | 1428.0 | 7601.4 | 432.31 | 3.372 |
| Jayanca (La Viña) | 1998 | land | era5 | 1428.0 | 7601.4 | 432.31 | 8.624 |
| Jayanca (La Viña) | 2000 | nearest | era5_seamless | 58.4 | 1414.2 | 2321.58 | 3.372 |
| Jayanca (La Viña) | 2000 | nearest | era5 | 58.4 | 1414.2 | 2321.58 | 8.624 |
| Cayaltí | 1998 | nearest | era5_seamless | 558.5 | 1335.6 | 139.14 | 5.612 |
| Cayaltí | 1998 | nearest | era5 | 558.5 | 1335.6 | 139.14 | 14.235 |
| Cayaltí | 1998 | land | era5_seamless | 558.5 | 1335.6 | 139.14 | 5.612 |
| Cayaltí | 1998 | land | era5 | 558.5 | 1335.6 | 139.14 | 14.235 |
| Cayaltí | 2000 | nearest | era5_seamless | 49.38 | 184.9 | 274.44 | 5.612 |
| Cayaltí | 2000 | nearest | era5 | 49.38 | 184.9 | 274.44 | 14.235 |
| Reque | 1998 | nearest | era5_seamless | 232.82 | 846.4 | 263.54 | 4.212 |
| Reque | 1998 | nearest | era5 | 232.82 | 846.4 | 263.54 | 15.792 |
| Reque | 1998 | land | era5_seamless | 232.82 | 846.4 | 263.54 | 4.212 |
| Reque | 1998 | land | era5 | 232.82 | 846.4 | 263.54 | 15.792 |
| Reque | 2000 | nearest | era5_seamless | 18.1 | 89.8 | 396.13 | 4.212 |
| Reque | 2000 | nearest | era5 | 18.1 | 89.8 | 396.13 | 15.792 |
| Lambayeque | 1998 | nearest | era5_seamless | 279.61 | 1270.2 | 354.28 | 3.67 |
| Lambayeque | 1998 | nearest | era5 | 279.61 | 1270.2 | 354.28 | 10.166 |
| Lambayeque | 1998 | land | era5_seamless | 279.61 | 1270.2 | 354.28 | 3.67 |
| Lambayeque | 1998 | land | era5 | 279.61 | 1270.2 | 354.28 | 10.166 |
| Lambayeque | 2000 | nearest | era5_seamless | 20.41 | 127.8 | 526.16 | 3.67 |
| Lambayeque | 2000 | nearest | era5 | 20.41 | 127.8 | 526.16 | 10.166 |
| Cueva Blanca | 1998 | nearest | era5_seamless | 969.2 | 8447.7 | 771.62 | 3.516 |
| Cueva Blanca | 1998 | nearest | era5 | 969.2 | 8447.7 | 771.62 | 16.902 |
| Cueva Blanca | 1998 | land | era5_seamless | 969.2 | 8447.7 | 771.62 | 3.516 |
| Cueva Blanca | 1998 | land | era5 | 969.2 | 8447.7 | 771.62 | 16.902 |
| Cueva Blanca | 2000 | nearest | era5_seamless | 813.9 | 2281.3 | 180.29 | 3.516 |
| Cueva Blanca | 2000 | nearest | era5 | 813.9 | 2281.3 | 180.29 | 16.902 |

## Incidencias de consulta

- {'estacion': 'Jayanca (La Viña)', 'ano': 1998, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Jayanca (La Viña)', 'ano': 1998, 'seleccion': 'land', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Jayanca (La Viña)', 'ano': 2000, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cayaltí', 'ano': 1998, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cayaltí', 'ano': 1998, 'seleccion': 'land', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cayaltí', 'ano': 2000, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Reque', 'ano': 1998, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Reque', 'ano': 1998, 'seleccion': 'land', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Reque', 'ano': 2000, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Lambayeque', 'ano': 1998, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Lambayeque', 'ano': 1998, 'seleccion': 'land', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Lambayeque', 'ano': 2000, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cueva Blanca', 'ano': 1998, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cueva Blanca', 'ano': 1998, 'seleccion': 'land', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}
- {'estacion': 'Cueva Blanca', 'ano': 2000, 'seleccion': 'nearest', 'modelo': 'era5_land', 'error': 'RuntimeError: Precipitacion negativa o ausente en un dia'}

## Interpretacion y fuentes

- Los modelos representan resoluciones y superficies de grid distintas; 1998 es un año extremo y no debe usarse aisladamente.
- Open-Meteo: https://open-meteo.com/en/docs/historical-weather-api
- CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3 (producto futuro, NO calculado aún).
- PISCOp v3: https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru
- SENAMHI: datos históricos de estaciones suministrados por el usuario.
