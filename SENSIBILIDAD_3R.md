# Fase 3R | Sensibilidad de CHIRPS v3 a coordenadas alternativas

> Analisis EXPLORATORIO. Las coordenadas alternativas NO se han validado como emplazamientos del mismo instrumento.
> Una discrepancia en las coordenadas de fuentes NO demuestra traslado de estación meteorológica.
> Solo se compara el producto CHIRPS mensual para 1998 y 2000; no se altera la serie instrumental SENAMHI.

## Método y controles

- GeoTIFF mensuales CHIRPS v3 de Climate Hazards Center, 0,05 grados.
- Dos coordenadas por estación: punto consultado en 3Q y candidato documental.
- Extracción del píxel contenedor sin interpolación.
- Datos CHIRPS 3Q originales se reprodujeron en 24 meses por cada estación.
- Comparación sobre meses con todos los días válidos SENAMHI.
- No se imputan datos faltantes ni se considera mejora por coincidencia como prueba de ubicación correcta.

## Sensibilidad anual

| Estación | Año | Distancia entre puntos km | Meses mismo píxel /12 | CHIRPS original mm | CHIRPS alternativo mm | Δ anual mm | MAE original | MAE alternativo |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Cayaltí | 1998 | 2.415 | 0/12 | 657.559 | 609.704 | -47.855 | 9.616 | 13.142 |
| Cayaltí | 2000 | 2.415 | 0/12 | 53.283 | 49.322 | -3.961 | 3.335 | 3.568 |
| Cueva Blanca | 1998 | 6.339 | 0/12 | 1515.965 | 1655.767 | 139.802 | 72.559 | 83.634 |
| Cueva Blanca | 2000 | 6.339 | 0/12 | 574.097 | 712.494 | 138.397 | 26.087 | 25.287 |
| Jayanca (La Viña) | 1998 | 1.683 | 12/12 | 826.757 | 826.757 | 0.0 | 52.099 | 52.099 |
| Jayanca (La Viña) | 2000 | 1.683 | 12/12 | 67.109 | 67.109 | 0.0 | 2.972 | 2.972 |
| Lambayeque | 1998 | 3.356 | 12/12 | 462.126 | 462.126 | 0.0 | 15.941 | 15.941 |
| Lambayeque | 2000 | 3.356 | 12/12 | 11.169 | 11.169 | 0.0 | 1.727 | 1.727 |
| Reque | 1998 | 0.042 | 12/12 | 331.993 | 331.993 | 0.0 | 8.264 | 8.264 |
| Reque | 2000 | 0.042 | 12/12 | 10.627 | 10.627 | 0.0 | 1.724 | 1.724 |

## Trazabilidad y límites

- Inventario de coordenadas y procedencias en datos/catalogo_coordenadas_3r.csv.
- Especial cuidado con Cueva Blanca: códigos y emplazamientos discordantes en fuentes; NO inferir equivalencia instrumental.
- Posibles cambios de celda en 0,05 grados no demuestran cambios meteorológicos a escala del pluviómetro.
- Código fuente y datos: scripts/sensibilidad_geografica_3r.py y datos/sensibilidad_3r_resumen.csv.
- Raster: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
- La ubicación exacta y código en la ficha original de descarga SENAMHI siguen pendientes de corroboración; no extrapolar a parcelas.

