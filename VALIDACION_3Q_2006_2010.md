# Fase 3Q — Comparacion CHIRPS, PISCOp y ERA5, 2006–2010

> **Exploratoria.** Metadatos instrumentales geograficos preliminares.
> CHIRPS y PISCOp incluyen pluviómetros y no constituyen muestras independientes.
> Los meses incompletos se excluyen; no se convierten faltantes en 0 mm.

## Cobertura

- Meses raster descargados en el bloque: 60.
- Meses raster 1998 reutilizados y auditados: 0.
- Meses-estacion SENAMHI completos en el bloque: 284.
- Meses-estacion con las tres estimaciones validas: 284.
- Pares estacion-mes-producto: 852.
- Incidencias: 0.

## Comparacion equitativa: mismos meses para tres productos

| Estacion | Producto | Meses | MAE (mm/mes) | RMSE (mm/mes) | Sesgo total (%) | Pearson |
|---|---|---:|---:|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 60 | 3.105 | 4.888 | 58.07 | 0.7933 |
| Cayaltí | ERA5-Seamless | 60 | 15.226 | 28.488 | 425.22 | 0.6681 |
| Cayaltí | PISCOp v3.0 | 60 | 1.174 | 2.265 | 21.38 | 0.9785 |
| Cueva Blanca | CHIRPS v3 | 59 | 26.472 | 36.416 | -29.0 | 0.8916 |
| Cueva Blanca | ERA5-Seamless | 59 | 96.7 | 159.053 | 119.38 | 0.7992 |
| Cueva Blanca | PISCOp v3.0 | 59 | 28.935 | 42.758 | -35.3 | 0.8549 |
| Jayanca (La Viña) | CHIRPS v3 | 59 | 7.959 | 18.949 | -13.17 | 0.591 |
| Jayanca (La Viña) | ERA5-Seamless | 59 | 79.534 | 129.445 | 820.34 | 0.591 |
| Jayanca (La Viña) | PISCOp v3.0 | 59 | 2.856 | 10.455 | -23.2 | 0.9176 |
| Lambayeque | CHIRPS v3 | 47 | 2.626 | 5.02 | -1.06 | 0.3444 |
| Lambayeque | ERA5-Seamless | 47 | 8.837 | 16.766 | 372.67 | 0.7816 |
| Lambayeque | PISCOp v3.0 | 47 | 0.609 | 1.222 | -4.42 | 0.9778 |
| Reque | CHIRPS v3 | 59 | 2.786 | 4.531 | -15.24 | 0.231 |
| Reque | ERA5-Seamless | 59 | 5.67 | 10.694 | 203.0 | 0.6893 |
| Reque | PISCOp v3.0 | 59 | 0.922 | 1.714 | -16.32 | 0.9331 |

## Estrato sin 1998 (equivale al bloque completo si no incluye 1998)

| Estacion | Producto | Meses | MAE (mm/mes) | Sesgo total (%) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 60 | 3.105 | 58.07 |
| Cayaltí | ERA5-Seamless | 60 | 15.226 | 425.22 |
| Cayaltí | PISCOp v3.0 | 60 | 1.174 | 21.38 |
| Cueva Blanca | CHIRPS v3 | 59 | 26.472 | -29.0 |
| Cueva Blanca | ERA5-Seamless | 59 | 96.7 | 119.38 |
| Cueva Blanca | PISCOp v3.0 | 59 | 28.935 | -35.3 |
| Jayanca (La Viña) | CHIRPS v3 | 59 | 7.959 | -13.17 |
| Jayanca (La Viña) | ERA5-Seamless | 59 | 79.534 | 820.34 |
| Jayanca (La Viña) | PISCOp v3.0 | 59 | 2.856 | -23.2 |
| Lambayeque | CHIRPS v3 | 47 | 2.626 | -1.06 |
| Lambayeque | ERA5-Seamless | 47 | 8.837 | 372.67 |
| Lambayeque | PISCOp v3.0 | 47 | 0.609 | -4.42 |
| Reque | CHIRPS v3 | 59 | 2.786 | -15.24 |
| Reque | ERA5-Seamless | 59 | 5.67 | 203.0 |
| Reque | PISCOp v3.0 | 59 | 0.922 | -16.32 |

## Método y procedencia

Se usaron mapas mensuales GeoTIFF CHIRPS v3 del Climate Hazards Center, coordenadas y píxel que contiene la estación.
La tabla multianual de SENAMHI–PISCOp–ERA5 procede de la Fase 3O y conserva meses completos.
Se reutilizan los 12 raster/píxeles 1998 auditados en Fase 3Q piloto.
Los datos no demuestran generalización espacial, causalidad del error ERA5 ni habilidad de pronóstico.
Fuente: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Documentación: https://www.chc.ucsb.edu/data/chirps3
