# Fase 3Q — Comparacion CHIRPS, PISCOp y ERA5, 2011–2015

> **Exploratoria.** Metadatos instrumentales geograficos preliminares.
> CHIRPS y PISCOp incluyen pluviómetros y no constituyen muestras independientes.
> Los meses incompletos se excluyen; no se convierten faltantes en 0 mm.

## Cobertura

- Meses raster descargados en el bloque: 58.
- Meses raster 1998 reutilizados y auditados: 0.
- Meses-estacion SENAMHI completos en el bloque: 236.
- Meses-estacion con las tres estimaciones validas: 236.
- Pares estacion-mes-producto: 708.
- Incidencias: 0.

## Comparacion equitativa: mismos meses para tres productos

| Estacion | Producto | Meses | MAE (mm/mes) | RMSE (mm/mes) | Sesgo total (%) | Pearson |
|---|---|---:|---:|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 55 | 3.533 | 5.986 | 20.72 | 0.6679 |
| Cayaltí | ERA5-Seamless | 55 | 12.509 | 24.655 | 311.62 | 0.8011 |
| Cayaltí | PISCOp v3.0 | 55 | 0.791 | 1.519 | 11.27 | 0.9861 |
| Cueva Blanca | CHIRPS v3 | 39 | 43.243 | 60.319 | -50.32 | 0.6803 |
| Cueva Blanca | ERA5-Seamless | 39 | 84.3 | 148.292 | 93.19 | 0.7762 |
| Cueva Blanca | PISCOp v3.0 | 39 | 35.126 | 46.723 | -44.84 | 0.8865 |
| Jayanca (La Viña) | CHIRPS v3 | 42 | 7.428 | 17.964 | -21.7 | 0.6699 |
| Jayanca (La Viña) | ERA5-Seamless | 42 | 74.531 | 121.606 | 978.22 | 0.8341 |
| Jayanca (La Viña) | PISCOp v3.0 | 42 | 2.888 | 10.984 | -27.63 | 0.9144 |
| Lambayeque | CHIRPS v3 | 43 | 2.816 | 5.475 | 3.38 | 0.6377 |
| Lambayeque | ERA5-Seamless | 43 | 5.548 | 9.151 | 200.24 | 0.8099 |
| Lambayeque | PISCOp v3.0 | 43 | 1.246 | 2.97 | 17.06 | 0.9332 |
| Reque | CHIRPS v3 | 57 | 2.94 | 5.535 | -18.62 | 0.5351 |
| Reque | ERA5-Seamless | 57 | 4.199 | 7.73 | 104.79 | 0.7936 |
| Reque | PISCOp v3.0 | 57 | 0.974 | 2.132 | 3.18 | 0.9546 |

## Estrato sin 1998 (equivale al bloque completo si no incluye 1998)

| Estacion | Producto | Meses | MAE (mm/mes) | Sesgo total (%) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 55 | 3.533 | 20.72 |
| Cayaltí | ERA5-Seamless | 55 | 12.509 | 311.62 |
| Cayaltí | PISCOp v3.0 | 55 | 0.791 | 11.27 |
| Cueva Blanca | CHIRPS v3 | 39 | 43.243 | -50.32 |
| Cueva Blanca | ERA5-Seamless | 39 | 84.3 | 93.19 |
| Cueva Blanca | PISCOp v3.0 | 39 | 35.126 | -44.84 |
| Jayanca (La Viña) | CHIRPS v3 | 42 | 7.428 | -21.7 |
| Jayanca (La Viña) | ERA5-Seamless | 42 | 74.531 | 978.22 |
| Jayanca (La Viña) | PISCOp v3.0 | 42 | 2.888 | -27.63 |
| Lambayeque | CHIRPS v3 | 43 | 2.816 | 3.38 |
| Lambayeque | ERA5-Seamless | 43 | 5.548 | 200.24 |
| Lambayeque | PISCOp v3.0 | 43 | 1.246 | 17.06 |
| Reque | CHIRPS v3 | 57 | 2.94 | -18.62 |
| Reque | ERA5-Seamless | 57 | 4.199 | 104.79 |
| Reque | PISCOp v3.0 | 57 | 0.974 | 3.18 |

## Método y procedencia

Se usaron mapas mensuales GeoTIFF CHIRPS v3 del Climate Hazards Center, coordenadas y píxel que contiene la estación.
La tabla multianual de SENAMHI–PISCOp–ERA5 procede de la Fase 3O y conserva meses completos.
Se reutilizan los 12 raster/píxeles 1998 auditados en Fase 3Q piloto.
Los datos no demuestran generalización espacial, causalidad del error ERA5 ni habilidad de pronóstico.
Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Documentación: https://www.chc.ucsb.edu/data/chirps3
