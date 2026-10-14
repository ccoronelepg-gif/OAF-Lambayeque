# OAF-Lambayeque | Fase 3Z: primera extracción de CHIRPS v3 reciente

**No es un pronóstico meteorológico ni alerta.** CHIRPS combina información satelital y datos pluviométricos.
Cada valor corresponde a **precipitación mensual estimada de una celda de 0,05°**, consultada en las coordenadas OAF históricas provisionales, NO a medición de estación.

## Periodo y disponibilidad verificada

- Fecha de consulta UTC: 2026-10-14T23:06:12+00:00
- Ventana de 12 meses calendarios CERRADOS: 2025-10 a 2026-09.
- Meses con raster descargado y cinco valores revisados: **11**.
- Meses con raster no disponible/fallido: **1**.
- Último mes CHIRPS realmente accesible: **2026-08**.
- Estado de actualización: disponible_para_ventana_consultada.
- La clasificación final/preliminar exacta del archivo no se afirma hasta consultar su metadato oficial; puede revisarse posteriormente.

## Muestras de cinco puntos por mes

| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca |
|---|---:|---:|---:|---:|---:|
| 2025-10 | 5.103 | 5.247 | 0.000 | 0.000 | 56.923 |
| 2025-11 | 6.878 | 3.913 | 8.297 | 8.201 | 42.300 |
| 2025-12 | 0.000 | 0.000 | 0.000 | 0.000 | 3.089 |
| 2026-01 | 1.887 | 4.776 | 5.697 | 1.628 | 20.879 |
| 2026-02 | 36.929 | 41.169 | 15.482 | 18.676 | 150.912 |
| 2026-03 | 17.322 | 7.480 | 4.196 | 2.462 | 83.691 |
| 2026-04 | 33.522 | 18.887 | 6.974 | 3.525 | 222.854 |
| 2026-05 | 0.000 | 0.000 | 1.430 | 0.256 | 15.079 |
| 2026-06 | 0.000 | 0.140 | 0.000 | 0.106 | 0.000 |
| 2026-07 | 0.000 | 1.287 | 0.224 | 0.454 | 0.000 |
| 2026-08 | 2.376 | 1.269 | 1.497 | 2.211 | 9.385 |

## Meses no disponibles

- **2026-09**: FileNotFoundError: Archivo no publicado HTTP 404 (https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/chirps-v3.0.2026.09.tif)

## Condiciones científicas

- No se sustituyeron archivos no disponibles por cero ni por productos alternativos.
- Los cinco puntos son referenciales y pueden no coincidir con el emplazamiento instrumental histórico.
- La disponibilidad de un GeoTIFF no implica independencia respecto a pluviómetros SENAMHI.
- Estos valores no certifican años 2016–2025 de lluvia instrumental ni permiten por sí solos pronosticar El Niño Costero.
- El intervalo termina en el último mes calendario cerrado. No aparece un valor de mes en curso incompleto.
- Verificar la condición preliminar/final mediante metadatos de publicación; no inferirla del nombre del fichero.
- Un fichero puede sufrir revisiones; se registra SHA256, fecha y HTTP Last-Modified cuando exista.
- La agenda semanal automática actualiza datos, pero no garantiza puntualidad de publicación de la fuente.
- El estado oficial de El Niño Costero se obtiene de ENFEN, no se infiere de estos cinco píxeles.

## Fuentes y artefactos

- Proveedor: https://www.chc.ucsb.edu/data/chirps3
- Servidor oficial de GeoTIFF: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
- Serie CSV: datos/chirps_v3_reciente_3z.csv
- Auditoría de ficheros: datos/auditoria_rasters_chirps_3z.json
- Estado público: datos/estado_monitoreo_3z.json
- Script: scripts/monitoreo_chirps_reciente_3z.py

