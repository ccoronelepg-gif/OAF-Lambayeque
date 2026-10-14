# OAF-Lambayeque | Fase 3S: precisión según intensidad de lluvia

> Estudio exploratorio retrospectivo: no pronóstico, no alerta de lluvia y no riesgo fitosanitario.
> 1, 20 y 50 mm mensuales son umbrales descriptivos elegidos para este estudio, no oficiales.
> PISCOp y CHIRPS pueden usar estaciones SENAMHI; no es validación totalmente independiente.

## Cobertura instrumental 1996-2015

Se utilizaron 1 109 meses-estación completos y 3 327 estimaciones comparables.
El subgrupo de 50 mm o más está incluido dentro de los meses de 20 mm o más.

| Estación | Meses | Secos (<1 mm) | Bajos (1 a <20 mm) | Lluviosos (>=20 mm) | Intensos (>=50 mm) |
|---|---:|---:|---:|---:|---:|
| Cayaltí | 235 | 106 | 117 | 12 | 3 |
| Cueva Blanca | 218 | 10 | 44 | 164 | 110 |
| Jayanca (La Viña) | 219 | 125 | 70 | 24 | 16 |
| Lambayeque | 204 | 131 | 63 | 10 | 3 |
| Reque | 233 | 156 | 70 | 7 | 2 |

## MAE mensual en meses lluviosos >=20 mm, incluyendo 1998

| Estación | Producto | Meses lluviosos | MAE (mm) | Sesgo medio (mm) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 12 | 15.841 | 4.996 |
| Cayaltí | ERA5-Seamless | 12 | 102.753 | 99.935 |
| Cayaltí | PISCOp v3.0 | 12 | 18.209 | 8.709 |
| Cueva Blanca | CHIRPS v3 | 164 | 38.513 | -23.268 |
| Cueva Blanca | ERA5-Seamless | 164 | 170.271 | 158.934 |
| Cueva Blanca | PISCOp v3.0 | 164 | 37.353 | -29.086 |
| Jayanca (La Viña) | CHIRPS v3 | 24 | 57.404 | -56.039 |
| Jayanca (La Viña) | ERA5-Seamless | 24 | 512.083 | 505.583 |
| Jayanca (La Viña) | PISCOp v3.0 | 24 | 23.117 | -22.566 |
| Lambayeque | CHIRPS v3 | 10 | 30.679 | 3.59 |
| Lambayeque | ERA5-Seamless | 10 | 110.462 | 109.458 |
| Lambayeque | PISCOp v3.0 | 10 | 8.473 | -1.983 |
| Reque | CHIRPS v3 | 7 | 24.649 | -4.975 |
| Reque | ERA5-Seamless | 7 | 85.336 | 79.104 |
| Reque | PISCOp v3.0 | 7 | 6.294 | 0.046 |

## MAE mensual en meses lluviosos >=20 mm, sin 1998

| Estación | Producto | Meses lluviosos | MAE (mm) | Sesgo medio (mm) |
|---|---|---:|---:|---:|
| Cayaltí | CHIRPS v3 | 8 | 10.522 | -4.205 |
| Cayaltí | ERA5-Seamless | 8 | 59.666 | 55.439 |
| Cayaltí | PISCOp v3.0 | 8 | 11.363 | -2.887 |
| Cueva Blanca | CHIRPS v3 | 154 | 35.403 | -28.372 |
| Cueva Blanca | ERA5-Seamless | 154 | 131.539 | 120.634 |
| Cueva Blanca | PISCOp v3.0 | 154 | 36.946 | -31.499 |
| Jayanca (La Viña) | CHIRPS v3 | 20 | 38.182 | -36.878 |
| Jayanca (La Viña) | ERA5-Seamless | 20 | 315.84 | 308.04 |
| Jayanca (La Viña) | PISCOp v3.0 | 20 | 21.334 | -20.673 |
| Lambayeque | CHIRPS v3 | 7 | 19.093 | -19.093 |
| Lambayeque | ERA5-Seamless | 7 | 24.443 | 23.009 |
| Lambayeque | PISCOp v3.0 | 7 | 7.403 | -3.794 |
| Reque | CHIRPS v3 | 5 | 20.737 | -20.737 |
| Reque | ERA5-Seamless | 5 | 22.19 | 13.466 |
| Reque | PISCOp v3.0 | 5 | 6.63 | -1.103 |

## Clasificación histórica de meses >=20 y >=50 mm

Los archivos incluyen la tabla de verdaderos positivos, falsos positivos, verdaderos negativos y falsos negativos, precisión, sensibilidad, especificidad y F1.
Estas estadísticas miden concordancia RETROSPECTIVA, no capacidad de anticipación.
Cuando hay pocos meses intensos, la incertidumbre es alta y no corresponde generalizar.

## Estaciones climáticas

La partición diciembre–abril versus mayo–noviembre es solo una clasificación de calendario; no define la climatología de todos los pisos altitudinales.

## Trazabilidad

Base: datos/comparacion_3q_1996_2015.csv (series SENAMHI completas y productos históricos).
Productos: PISCOp v3.0, CHIRPS v3 y ERA5-Seamless. No se consultaron ni añadieron nuevos datos observados.
Código: scripts/analisis_3s_intensidad.py
Archivos: datos/cobertura_3s.csv; datos/metricas_intensidad_3s.csv; datos/metricas_estacionales_3s.csv; datos/clasificacion_mensual_3s.csv; datos/estado_3s.json.
Pendientes: metadatos oficiales de estaciones, series 2016–2025 y validación espacial independiente.
Los resultados no son recomendaciones operativas de control de enfermedades agrícolas.

