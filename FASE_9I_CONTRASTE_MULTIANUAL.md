# Fase 9I — Ampliación temporal CHIRPS v3 y comparación mensual en ventanas comunes

**Fecha de ejecución:** 17 de octubre de 2026. **Estado:** completada la descarga exploratoria de cinco años adicionales y publicada la comparación reproducible de seis años en total. **No** certifica habilidad predictiva ni independencia de CHIRPS.

## 1. Pregunta y decisiones anteriores al contraste

¿Las diferencias entre registros de Virrey, Puchaca y El Espinal frente a CHIRPS v3 y ERA5 atmosférico persisten cuando se sale del episodio extraordinario de 1998 y ambos productos se contrastan en idénticos meses instrumentales?

Se seleccionaron **1996, 1998, 2002, 2007, 2011 y 2013 antes de extraer los nuevos TIFF**; se mantuvo 1998 ya extraído en 9H, sin descargarlo ni contarlo dos veces. Estos años separados no constituyen una climatología continua ni una muestra aleatoria de 1996–2025. Se retienen **ambas referencias espaciales 9G** de cada estación, aunque arrojen errores diferentes.

## 2. Fuentes, documentos originales y método

- **Observaciones de estación:** archivos de 9D y 9F; solo meses con **100 % de los días válidos**. No se rellenan registros. Aún faltan convención del día pluviométrico, licencia y metadatos históricos instrumentales.
- **CHIRPS v3 mensual 0,05°:** Climate Hazards Center (UCSB), GeoTIFF LATAM con CRS EPSG:4326 y una banda. Se extrajeron **60 de 60** TIFF mensuales nuevos (1996, 2002, 2007, 2011 y 2013); cada URL, mes, SHA-256 y tamaño está registrado en `datos/validacion_estaciones_9i/fuentes_chirps_ampliacion_9i.json`. **0 errores de descarga** en esta ejecución; no se reetiquetan versiones ni se declara categoría final/preliminar por ráster sin confirmación específica.
- **ERA5 atmosférico (aprox. 0,25°):** se reutilizaron pares reales de la fase 9H, extraídos vía Open-Meteo con modelo `era5`. No se mezclaron con ERA5-Land ni se estimaron temperaturas faltantes.
- **Emparejamiento:** estación, escenario documental y mes exacto. Para cada año se computó MAE, RMSE y sesgo **solamente sobre intersecciones**; se exige coherencia del dato observado utilizado por ambas comparaciones. Un cambio de escenario no equivale a observación independiente.
- **Operacionalidad:** no se usaron pronósticos con fecha histórica de emisión; por tanto **ningún** MAE mide anticipación real. CHIRPS puede incluir estaciones pluviométricas y no se ha verificado su independencia en estas tres series.

Documentación de origen: [CHIRPS v3 – UCSB](https://www.chc.ucsb.edu/data/chirps3); [diagnósticos y estaciones integradas en CHIRPS](https://www.chc.ucsb.edu/data/chirps3/diagnostics); [ERA5-Land, convenciones de acumulación – ECMWF](https://confluence.ecmwf.int/spaces/CKB/pages/140385202/ERA5-Land+data+documentation).

## 3. Cobertura auditada

| Año | Meses-estación distintos emparejados (máx. 36/año) | Registros con dos escenarios | Meses con las 3 estaciones |
|---|---:|---:|---:|
| 1996 | 36 | 72 | 12 |
| 1998 | 36 | 72 | 12 |
| 2002 | 35 | 70 | 11 |
| 2007 | 34 | 68 | 10 |
| 2011 | 36 | 72 | 12 |
| 2013 | 36 | 72 | 12 |
| **Total** | **213** | **426** | **69 meses-año** |

**72 parejas heredadas de 9H + 354 nuevas = 426 parejas escenario-mes para cada producto al restringirse a los años seleccionados.** Son **213 meses-estación únicos**, no 426 observaciones independientes. Una estación puede tener un año parcial aun si la descarga CHIRPS cubre los 12 archivos anuales.

## 4. Resultados: MAE mensual en los mismos meses para ambos productos

Resultados agregados **descriptivos** para 1996, 1998, 2002, 2007, 2011 y 2013, sin convertir años incompletos en completos. Se reporta MAE sobre los mismos meses, expresado en **mm por mes**; el cálculo anual y su agregación ponderada por número de meses están reproducidos en los resultados de la fase.

| Estación | Escenario | Meses comunes | MAE CHIRPS v3 | MAE ERA5 atmosférico |
|---|---|---:|---:|---:|
| El Espinal | Doc. 1 | 71 | **23,59** | 67,83 |
| El Espinal | Doc. 2 | 71 | **23,59** | 67,83 |
| Puchaca | Doc. 1 | 70 | **22,62** | 124,19 |
| Puchaca | Doc. 2 | 70 | **24,37** | 197,25 |
| Virrey | Doc. 1 | 72 | 37,82 | **25,96** |
| Virrey | Doc. 2 | 72 | 37,82 | **25,96** |

**Lectura científica:** CHIRPS presenta menor MAE en El Espinal y Puchaca en estos seis años, mientras que ERA5 atmosférico presenta menor MAE en Virrey. La divergencia de Puchaca entre celdas ERA5 es considerable: la elección posterior del escenario «más favorable» sesgaría las conclusiones. Dos escenarios idénticos en celda **no** son replicaciones. No se deben presentar las cifras como habilidad futura ni declarar un producto universalmente superior en Lambayeque.

## 5. Control de incertidumbre y límites de inferencia

1. **Dependencia instrumental:** CHIRPS integra pluviómetros; todavía no se determinó si las series analizadas ingresaron a sus archivos de estaciones. Su error aparente puede beneficiarse de circularidad.
2. **Soporte espacial:** un píxel representa una zona, un pluviómetro representa un punto. Topografía y exposición pueden diferir; Puchaca tiene altitudes documentales contradictorias.
3. **Representatividad:** seis años discontinuos dentro de 1996–2013 no bastan para medir la variabilidad histórica completa 1996–2025 ni probar fiabilidad en 2017, eventos más recientes o condiciones futuras.
4. **Convenciones y QC:** horas de observación, calidad homogeneizada, cambio de sensores y ubicación histórica continúan sin acreditación.
5. **Comparación honesta:** ERA5 atmosférico no es ERA5-Land. La extracción de temperaturas ERA5-Land continúa pendiente; ningún campo se rellenó ni se presentó como cero.
6. **Aplicación agronómica:** no transferir MAE de lluvia directamente a probabilidades de presencia de plagas o enfermedades de arándano y vid. Las alertas oficiales ENFEN/SENAMHI y los resultados experimentales permanecen diferenciados.

## 6. Reproducibilidad y productos entregados

- [Extractor CHIRPS multianual](modelos/contraste_multianual_chirps_9i.py): años predefinidos, TIFF reales, huellas y extracción de celdas, `--check` sin Internet.
- [Análisis emparejado](modelos/analisis_multianual_9i.py): genera el JSON con cobertura y métricas comparables, con modo `--check`.
- [CSV de los 354 pares CHIRPS nuevos](datos/validacion_estaciones_9i/pares_chirps_ampliacion_9i.csv).
- [Manifiesto de 60 archivos reales](datos/validacion_estaciones_9i/fuentes_chirps_ampliacion_9i.json).
- [Diagnóstico 9I](datos/validacion_estaciones_9i/diagnostico_multianual_9i.json) con 426 pares por producto restringidos a estos años y 213 meses-estación únicos.
- [Visor interactivo](modelos/visor_contraste_9i.js), incorporado en **Análisis de clima regional**.
- [Workflow científico 9I](.github/workflows/oaf_contraste_multianual_9i.yml), comprobaciones y publicación automática.

## 7. Próxima fase propuesta: 9J

Construir una prueba verdaderamente **prospectiva** con pronósticos archivados (emisión, horizonte, versión y fecha válida), reservar intervalos futuros fuera del entrenamiento y evaluar anomalías por zonas agroclimáticas homogéneas. Añadir controles de independencia de CHIRPS con los listados UCSB, recuperar temperatura ERA5-Land por modalidad compatible y certificar metadatos históricos de estaciones antes de comunicar habilidad operativa. Preservar como normal científica principal 1996–2025 y referencia OMM 1991–2020, sin fingir que estas tres series instrumentales ya cubren íntegramente dichas normales.
