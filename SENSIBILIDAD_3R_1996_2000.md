# Fase 3R: sensibilidad geografica de CHIRPS 1996-2000

> Analisis exploratorio: la ubicacion real de las estaciones historicas NO se determina por menor error.
> Dos pares de metadatos por cada una de cinco estaciones; no afirmar traslados.

**Meses-estacion disponibles:** 300
**Comparaciones con las dos ubicaciones:** 300
**Rasters con fallo:** 0

## Diferencias multianuales

| Estacion | Meses | Meses mismo pixel | Diferencia CHIRPS (mm) | MAE original | MAE alternativo |
|---|---:|---:|---:|---:|---:|
| Cayaltí | 60 | 0 | -70.44 | 5.178 | 5.777 |
| Cueva Blanca | 60 | 0 | 694.977 | 32.409 | 33.823 |
| Jayanca (La Viña) | 60 | 60 | 0.0 | 13.915 | 13.915 |
| Lambayeque | 60 | 60 | 0.0 | 5.039 | 5.039 |
| Reque | 60 | 60 | 0.0 | 4.028 | 4.028 |

Fuente GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Datos instrumentales: registros históricos SENAMHI, solo meses completos.
Coordenadas: datos/catalogo_coordenadas_3r.csv (identidad no certificada).
PISCOp y ERA5 NO se recalcularon aquí; las diferencias son de CHIRPS.
