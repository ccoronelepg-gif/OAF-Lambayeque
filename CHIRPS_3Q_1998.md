# Fase 3Q — CHIRPS v3 mensual: piloto 1998

> ESTUDIO EXPLORATORIO. Las estaciones pueden contribuir a CHIRPS; la coincidencia no equivale a validacion independiente.
> Coordenadas instrumentales historicas aun preliminares.

**Rasters mensuales validos: 12/12. Pares estacion-mes: 60/60.**

Fuente oficial: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/
Metodo: pixel que contiene la coordenada preliminar SENAMHI, sin interpolar. Se conserva georreferenciacion de pixel, resolucion y URL fuente.
No se completan artificialmente meses o pixeles faltantes.
PISCOp y ERA5 de 1998 provienen de la fase 3N.

## Indicadores por estacion

| Estacion | Meses | SENAMHI anual mm | CHIRPS anual mm | Sesgo anual % | MAE mensual mm | RMSE mensual mm |
|---|---:|---:|---:|---:|---:|---:|
| Jayanca (La Viña) | 12 | 1428.0 | 826.757 | -42.1 | 52.099 | 104.729 |
| Cayaltí | 12 | 558.5 | 657.559 | 17.74 | 9.616 | 26.406 |
| Reque | 12 | 232.82 | 331.993 | 42.6 | 8.264 | 15.501 |
| Lambayeque | 12 | 279.61 | 462.126 | 65.28 | 15.941 | 39.627 |
| Cueva Blanca | 12 | 969.2 | 1515.965 | 56.41 | 72.559 | 149.578 |

## Reglas de interpretacion

- Es un piloto limitado a 1998, no una evaluacion multianual del periodo 1996–2025.
- Para contrastes multianuales usar exactamente los mismos meses de observacion valida.
- CHIRPS v3 incorpora estaciones de lluvia; evaluar dependencia y generalizacion fuera de muestra.
- No inferir alertas sanitarias sin registros locales de enfermedades de arandano.
