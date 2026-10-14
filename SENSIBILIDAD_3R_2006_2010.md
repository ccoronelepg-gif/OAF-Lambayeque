# Fase 3R: sensibilidad geografica de CHIRPS 2006-2010

> Analisis exploratorio: la ubicacion real de las estaciones historicas NO se determina por menor error.
> Dos pares de metadatos por cada una de cinco estaciones; no afirmar traslados.

**Meses-estacion disponibles:** 284
**Comparaciones con las dos ubicaciones:** 284
**Rasters con fallo:** 0

## Diferencias multianuales

| Estacion | Meses | Meses mismo pixel | Diferencia CHIRPS (mm) | MAE original | MAE alternativo |
|---|---:|---:|---:|---:|---:|
| Cayaltí | 60 | 0 | -60.777 | 3.105 | 2.859 |
| Cueva Blanca | 59 | 0 | 493.42 | 26.472 | 23.235 |
| Jayanca (La Viña) | 59 | 59 | 0.0 | 7.959 | 7.959 |
| Lambayeque | 47 | 47 | 0.0 | 2.626 | 2.626 |
| Reque | 59 | 59 | 0.0 | 2.786 | 2.786 |

Fuente GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Datos instrumentales: registros históricos SENAMHI, solo meses completos.
Coordenadas: datos/catalogo_coordenadas_3r.csv (identidad no certificada).
PISCOp y ERA5 NO se recalcularon aquí; las diferencias son de CHIRPS.
