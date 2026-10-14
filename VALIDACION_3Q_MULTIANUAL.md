# Fase 3Q — Comparacion CHIRPS, PISCOp y ERA5, 1996–2000

> **Exploratoria.** Metadatos instrumentales geograficos preliminares.
> CHIRPS y PISCOp incluyen pluviómetros y no constituyen muestras independientes.
> Los meses incompletos se excluyen; no se convierten faltantes en 0 mm.

## Cobertura

- Meses raster descargados para 1996,1997,1999,2000: 48.
- Meses raster 1998 reutilizados y auditados: 12.
- Meses-estacion SENAMHI completos en el bloque: 300.
- Meses-estacion con las tres estimaciones validas: 300.
- Pares estacion-mes-producto: 900.
- Incidencias: 0.

## Comparacion equitativa: mismos meses para tres productos

| Estacion | Producto | Meses | MAE (mm/mes) | RMSE (mm/mes) | Sesgo total (%) | Pearson |
|---|---|---:|---:|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 60 | 5.178 | 12.999 | 7.01 | 0.97 |
| Cayaltí | ERA5-Seamless | 60 | 22.452 | 66.399 | 152.76 | 0.8573 |
| Cayaltí | PISCOp v3.0 | 60 | 4.006 | 11.164 | 5.71 | 0.9868 |
| Cueva Blanca | CHIRPS v3 | 60 | 32.409 | 72.387 | -3.24 | 0.8108 |
| Cueva Blanca | ERA5-Seamless | 60 | 223.31 | 542.01 | 337.91 | 0.6501 |
| Cueva Blanca | PISCOp v3.0 | 60 | 30.752 | 42.359 | -23.57 | 0.8113 |
| Jayanca (La Viña) | CHIRPS v3 | 60 | 13.915 | 47.422 | -36.75 | 0.951 |
| Jayanca (La Viña) | ERA5-Seamless | 60 | 178.518 | 437.779 | 608.83 | 0.9639 |
| Jayanca (La Viña) | PISCOp v3.0 | 60 | 4.078 | 12.802 | -11.67 | 0.9959 |
| Lambayeque | CHIRPS v3 | 60 | 5.039 | 18.24 | 37.96 | 0.949 |
| Lambayeque | ERA5-Seamless | 60 | 22.109 | 74.236 | 317.43 | 0.9283 |
| Lambayeque | PISCOp v3.0 | 60 | 1.28 | 3.423 | -4.39 | 0.9877 |
| Reque | CHIRPS v3 | 60 | 4.028 | 9.133 | 25.18 | 0.9498 |
| Reque | ERA5-Seamless | 60 | 15.398 | 50.139 | 258.85 | 0.9124 |
| Reque | PISCOp v3.0 | 60 | 1.138 | 2.657 | 3.92 | 0.9908 |

## Sin El Niño extraordinario de 1998 (estrato 1996–2000 excluyendo 1998)

| Estacion | Producto | Meses | MAE (mm/mes) | Sesgo total (%) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 48 | 4.069 | -13.79 |
| Cayaltí | ERA5-Seamless | 48 | 11.812 | 179.18 |
| Cayaltí | PISCOp v3.0 | 48 | 2.244 | -27.36 |
| Cueva Blanca | CHIRPS v3 | 48 | 22.371 | -23.53 |
| Cueva Blanca | ERA5-Seamless | 48 | 119.185 | 190.36 |
| Cueva Blanca | PISCOp v3.0 | 48 | 29.199 | -34.22 |
| Jayanca (La Viña) | CHIRPS v3 | 48 | 4.369 | -13.64 |
| Jayanca (La Viña) | ERA5-Seamless | 48 | 94.535 | 1370.36 |
| Jayanca (La Viña) | PISCOp v3.0 | 48 | 2.333 | -22.33 |
| Lambayeque | CHIRPS v3 | 48 | 2.314 | -21.3 |
| Lambayeque | ERA5-Seamless | 48 | 6.999 | 237.5 |
| Lambayeque | PISCOp v3.0 | 48 | 0.843 | -20.59 |
| Reque | CHIRPS v3 | 48 | 2.969 | -12.15 |
| Reque | ERA5-Seamless | 48 | 6.465 | 248.78 |
| Reque | PISCOp v3.0 | 48 | 1.053 | 0.68 |

## Método y procedencia

Se usaron mapas mensuales GeoTIFF CHIRPS v3 del Climate Hazards Center, coordenadas y píxel que contiene la estación.
La tabla multianual de SENAMHI–PISCOp–ERA5 procede de la Fase 3O y conserva meses completos.
Se reutilizan los 12 raster/píxeles 1998 auditados en Fase 3Q piloto.
Los datos no demuestran generalización espacial, causalidad del error ERA5 ni habilidad de pronóstico.
Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Documentación: https://www.chc.ucsb.edu/data/chirps3
