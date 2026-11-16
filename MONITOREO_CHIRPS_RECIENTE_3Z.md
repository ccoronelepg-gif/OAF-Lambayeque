# OAF-Lambayeque | Fase 3Z: primera extracción de CHIRPS v3 reciente

**No es un pronóstico meteorológico ni alerta.** CHIRPS combina información satelital y datos pluviométricos.
Cada valor corresponde a **precipitación mensual estimada de una celda de 0,05°**, consultada en las coordenadas OAF históricas provisionales, NO a medición de estación.

## Periodo y disponibilidad verificada

- Fecha de consulta UTC: 2026-11-16T23:44:37+00:00
- Ventana de 12 meses calendarios CERRADOS: 2025-11 a 2026-10.
- Meses con raster descargado y cinco valores revisados: **12**.
- Meses con raster no disponible/fallido: **0**.
- Último mes CHIRPS realmente accesible: **2026-10**.
- Estado de actualización: disponible_para_ventana_consultada.
- La clasificación final/preliminar exacta del archivo no se afirma hasta consultar su metadato oficial; puede revisarse posteriormente.

## Muestras de cinco puntos por mes

| Mes | Jayanca | Cayaltí | Reque | Lambayeque | Cueva Blanca |
|---|---:|---:|---:|---:|---:|
| 2025-11 | 5.312 | 2.586 | 6.844 | 6.878 | 51.263 |
| 2025-12 | 0.000 | 0.000 | 0.000 | 0.000 | 3.110 |
| 2026-01 | 1.852 | 4.695 | 5.619 | 1.600 | 18.557 |
| 2026-02 | 31.528 | 42.785 | 13.868 | 16.768 | 122.729 |
| 2026-03 | 15.726 | 5.247 | 2.534 | 1.008 | 84.072 |
| 2026-04 | 26.913 | 16.191 | 6.072 | 2.276 | 181.427 |
| 2026-05 | 0.000 | 0.000 | 1.401 | 0.252 | 14.863 |
| 2026-06 | 0.000 | 0.140 | 0.000 | 0.107 | 0.000 |
| 2026-07 | 0.000 | 1.299 | 0.225 | 0.458 | 0.000 |
| 2026-08 | 2.394 | 1.275 | 1.525 | 2.281 | 9.419 |
| 2026-09 | 0.000 | 0.000 | 0.000 | 0.000 | 13.067 |
| 2026-10 | 0.000 | 0.000 | 0.000 | 0.000 | 9.584 |

## Meses no disponibles

No se encontraron faltantes en los doce meses cerrados consultados.

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

