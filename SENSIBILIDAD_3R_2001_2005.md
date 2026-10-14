# Fase 3R: sensibilidad geografica de CHIRPS 2001-2005

> Analisis exploratorio: la ubicacion real de las estaciones historicas NO se determina por menor error.
> Dos pares de metadatos por cada una de cinco estaciones; no afirmar traslados.

**Meses-estacion disponibles:** 289
**Comparaciones con las dos ubicaciones:** 289
**Rasters con fallo:** 0

## Diferencias multianuales

| Estacion | Meses | Meses mismo pixel | Diferencia CHIRPS (mm) | MAE original | MAE alternativo |
|---|---:|---:|---:|---:|---:|
| Cayaltí | 60 | 0 | -29.802 | 3.017 | 2.537 |
| Cueva Blanca | 60 | 0 | 519.39 | 24.275 | 18.903 |
| Jayanca (La Viña) | 58 | 58 | 0.0 | 6.695 | 6.695 |
| Lambayeque | 54 | 54 | 0.0 | 2.693 | 2.693 |
| Reque | 57 | 57 | 0.0 | 2.143 | 2.143 |

Fuente GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Datos instrumentales: registros históricos SENAMHI, solo meses completos.
Coordenadas: datos/catalogo_coordenadas_3r.csv (identidad no certificada).
PISCOp y ERA5 NO se recalcularon aquí; las diferencias son de CHIRPS.
