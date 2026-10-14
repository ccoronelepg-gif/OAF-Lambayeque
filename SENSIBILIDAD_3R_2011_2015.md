# Fase 3R: sensibilidad geografica de CHIRPS 2011-2015

> Analisis exploratorio: la ubicacion real de las estaciones historicas NO se determina por menor error.
> Dos pares de metadatos por cada una de cinco estaciones; no afirmar traslados.

**Meses-estacion disponibles:** 236
**Comparaciones con las dos ubicaciones:** 236
**Rasters con fallo:** 0

## Diferencias multianuales

| Estacion | Meses | Meses mismo pixel | Diferencia CHIRPS (mm) | MAE original | MAE alternativo |
|---|---:|---:|---:|---:|---:|
| Cayaltí | 55 | 0 | -34.695 | 3.533 | 3.41 |
| Cueva Blanca | 39 | 0 | 273.6 | 43.243 | 40.244 |
| Jayanca (La Viña) | 42 | 42 | 0.0 | 7.428 | 7.428 |
| Lambayeque | 43 | 43 | 0.0 | 2.816 | 2.816 |
| Reque | 57 | 57 | 0.0 | 2.94 | 2.94 |

Fuente GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Datos instrumentales: registros históricos SENAMHI, solo meses completos.
Coordenadas: datos/catalogo_coordenadas_3r.csv (identidad no certificada).
PISCOp y ERA5 NO se recalcularon aquí; las diferencias son de CHIRPS.
