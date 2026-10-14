# Fase 3Q — Comparacion CHIRPS, PISCOp y ERA5, 2001–2005

> **Exploratoria.** Metadatos instrumentales geograficos preliminares.
> CHIRPS y PISCOp incluyen pluviómetros y no constituyen muestras independientes.
> Los meses incompletos se excluyen; no se convierten faltantes en 0 mm.

## Cobertura

- Meses raster descargados en el bloque: 60.
- Meses raster 1998 reutilizados y auditados: 0.
- Meses-estacion SENAMHI completos en el bloque: 289.
- Meses-estacion con las tres estimaciones validas: 289.
- Pares estacion-mes-producto: 867.
- Incidencias: 0.

## Comparacion equitativa: mismos meses para tres productos

| Estacion | Producto | Meses | MAE (mm/mes) | RMSE (mm/mes) | Sesgo total (%) | Pearson |
|---|---|---:|---:|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 60 | 3.017 | 6.189 | 61.22 | 0.8342 |
| Cayaltí | ERA5-Seamless | 60 | 12.006 | 25.208 | 444.36 | 0.7913 |
| Cayaltí | PISCOp v3.0 | 60 | 1.238 | 3.283 | 32.69 | 0.9636 |
| Cueva Blanca | CHIRPS v3 | 60 | 24.275 | 32.589 | -33.81 | 0.8043 |
| Cueva Blanca | ERA5-Seamless | 60 | 102.863 | 228.05 | 168.75 | 0.6245 |
| Cueva Blanca | PISCOp v3.0 | 60 | 24.264 | 34.246 | -36.38 | 0.7796 |
| Jayanca (La Viña) | CHIRPS v3 | 58 | 6.695 | 19.034 | -30.28 | 0.8078 |
| Jayanca (La Viña) | ERA5-Seamless | 58 | 76.738 | 166.88 | 858.89 | 0.9149 |
| Jayanca (La Viña) | PISCOp v3.0 | 58 | 2.505 | 7.312 | -21.25 | 0.9919 |
| Lambayeque | CHIRPS v3 | 54 | 2.693 | 5.813 | -27.73 | 0.7692 |
| Lambayeque | ERA5-Seamless | 54 | 6.064 | 13.019 | 156.78 | 0.7346 |
| Lambayeque | PISCOp v3.0 | 54 | 0.976 | 2.272 | -21.43 | 0.9796 |
| Reque | CHIRPS v3 | 57 | 2.143 | 4.234 | 93.04 | 0.4472 |
| Reque | ERA5-Seamless | 57 | 5.434 | 10.953 | 388.19 | 0.4181 |
| Reque | PISCOp v3.0 | 57 | 1.057 | 3.087 | 49.67 | 0.7332 |

## Estrato sin 1998 (equivale al bloque completo si no incluye 1998)

| Estacion | Producto | Meses | MAE (mm/mes) | Sesgo total (%) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 60 | 3.017 | 61.22 |
| Cayaltí | ERA5-Seamless | 60 | 12.006 | 444.36 |
| Cayaltí | PISCOp v3.0 | 60 | 1.238 | 32.69 |
| Cueva Blanca | CHIRPS v3 | 60 | 24.275 | -33.81 |
| Cueva Blanca | ERA5-Seamless | 60 | 102.863 | 168.75 |
| Cueva Blanca | PISCOp v3.0 | 60 | 24.264 | -36.38 |
| Jayanca (La Viña) | CHIRPS v3 | 58 | 6.695 | -30.28 |
| Jayanca (La Viña) | ERA5-Seamless | 58 | 76.738 | 858.89 |
| Jayanca (La Viña) | PISCOp v3.0 | 58 | 2.505 | -21.25 |
| Lambayeque | CHIRPS v3 | 54 | 2.693 | -27.73 |
| Lambayeque | ERA5-Seamless | 54 | 6.064 | 156.78 |
| Lambayeque | PISCOp v3.0 | 54 | 0.976 | -21.43 |
| Reque | CHIRPS v3 | 57 | 2.143 | 93.04 |
| Reque | ERA5-Seamless | 57 | 5.434 | 388.19 |
| Reque | PISCOp v3.0 | 57 | 1.057 | 49.67 |

## Método y procedencia

Se usaron mapas mensuales GeoTIFF CHIRPS v3 del Climate Hazards Center, coordenadas y píxel que contiene la estación.
La tabla multianual de SENAMHI–PISCOp–ERA5 procede de la Fase 3O y conserva meses completos.
Se reutilizan los 12 raster/píxeles 1998 auditados en Fase 3Q piloto.
Los datos no demuestran generalización espacial, causalidad del error ERA5 ni habilidad de pronóstico.
Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Documentación: https://www.chc.ucsb.edu/data/chirps3
