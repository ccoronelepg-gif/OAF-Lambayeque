# OAF-Lambayeque — Punto de reanudación Fase 8Q · octubre 2026

## Resultado real de la fase
La parte **8Q** quedó implementada, con tres transectos de puntos V1/V2; **10 ubicaciones DEM intermedias** seleccionadas sobre un muestreo conceptual, sin fingir rutas topográficas ni continuidad de polígonos.

Se recuperaron y archivaron **6/6 fuentes históricas reales**: modelos ERA5-Land para Tmean/Tmax/Tmin y ERA5 para precipitación/humedad/radiación durante 1996–2025, agrupados en 1996–2005, 2006–2015 y 2016–2025, para **10 puntos con 360 meses cada uno**. El proveedor no es una red instrumental de SENAMHI.

### Hallazgos físicos y térmicos
- Segmento V1a: extremos originales DEM 521–307 m, intermedios 611, 212, 696 y **1120 m**. Medias térmicas de 30 años entre **19,0854 y 22,0676 °C**, amplitud **2,9822 °C**.
- Segmento V1b: extremos DEM 212–307 m, intermedios 526 y 271 m. Tmedia de **21,7073 a 22,0021 °C**, amplitud **0,2948 °C**.
- Segmento V2: extremos DEM 2978–3236 m, intermedios **2186, 2717, 3839, 3546 m**. Tmedia de **7,2269 a 15,2893 °C**, amplitud **8,0624 °C**.
- **No proclamar homogeneidad de temperaturas absolutas**, ni interpretar la diferencia como efecto físico exclusivo de elevación: Open-Meteo ajusta según elevación y selección de celda; DEM del proveedor no son parcelas.

### Auditoría de celdas y coherencia temporal
- 10 intermedios × 2 modelos → **20 registros de coordenadas de celda** verificadas frente a JSON originales; centros estables por década.
- **4 de los 10** reutilizan el mismo centro ERA5-Land de otro testigo dentro de su transecto; **7 de los 10** el mismo centro ERA5.
- Especialmente V2: los cuatro puntos comparten la **misma celda ERA5** de lluvia/humedad/radiación; precipitación media 1419,53 mm/año idéntica por origen de dato, **NO prueba homogeneidad de lluvia real**.
- Se calcularon **13 pares de anomalías históricas mensuales**, con normales propias de cada localidad y mes calendario sobre 1996–2025. Correlaciones de Tmedia:
  - V1a: 0,93603–0,99998, MAE de diferencias de anomalías 0,00344–0,22296 °C.
  - V1b: correlación 0,96507, MAE 0,15014 °C.
  - V2: 0,93823–0,99998, MAE de diferencias de anomalías 0,00280–0,14820 °C.
  - **2 de 13 pares** comparten la misma celda de ERA5-Land, **9 de 13** la misma celda ERA5 de lluvia; la correlación de lluvias en esos pares NO equivale a evidencia independiente.
  - Aun en píxeles de temperatura ERA5-Land distintos, V2 muestra alta covariación (0,93823–0,98773), que podría orientar un modelo jerárquico de anomalía regional + climatología/corrección local.
- **La correlación histórica del reanálisis NO demuestra habilidad de predicción futura, independencia ni homogeneidad agrícola de un polígono**. SENAMHI de temperatura, estaciones independientes, cuencas, orientación, cobertura de suelo y límites INEI/IGN siguen pendientes.
- Zonas homogéneas certificadas: **0**; pronósticos zonales validados: **0**.

### Archivos ya en el repo
- `modelos/transectos_continuidad_8q.py`: diseño, adquisiciones, SHA, normas, anomalías y auditoría de pixel.
- `tests/test_transectos_continuidad_8q.py`: diez pruebas aisladas de continuidad DEM, corrupción de fuente, correlación y anomalía propia.
- `.github/workflows/oaf_transectos_8q.yml`: auditoría y recuperación solo faltantes diaria (a día 17 UTC), con controles del portal.
- `datos/transectos_8q/estado_transectos_8q.json`: fuente de verdad en vivo.
- `datos/transectos_8q/muestras_intermedias_8q.csv`: 10 ubicaciones.
- `datos/transectos_8q/comparacion_climatica_8q.csv`: Tmean/lluvia/RH/radiación 10 puntos y 30 años.
- `datos/transectos_8q/centros_modelados_8q.csv`: coordenadas proveedor ERA5Land/ERA5.
- `datos/transectos_8q/coherencia_anomalias_8q.csv`: 13 correlaciones de anomalía temporal, MAE, identidad de pixel.
- `datos/transectos_8q/fuentes`: seis respuestas originales comprimidas con SHA/URL/fecha.
- `index.html` y `modelos/visor_transectos_8q.js`: sección nueva 8Q con mapa de transectos, tabla de temperatura y coherencia mensual en https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.
- `FASE_8Q_TRANSECTOS_CONTINUIDAD.md`: informe científico completo de limitaciones y resultados.

### Próxima fase 8R
1. Avanzar la densificación de las **62 nuevas climatologías de 8P**, contrastar coherencia temporal de anomalías regionales con fuentes independientes y bloques espaciales.
2. Obtener oficialmente **límites INEI/IGN, máscara tierra/agua y cuencas y pendientes/orientación**; no permitir un solo polígono con múltiples pisos heterogéneos.
3. Analizar **habilidad de anomalía OOS**, sin fuga temporal, por piso/ámbito y modelo jerárquico: señal común + climatología local, comparar persistencia y normal mensual con 1996–2025; usar información SENAMHI donde esté realmente disponible y ENFEN para El Niño.
4. Desacoplar downscaling proveedor (elevation=nan vs default), y comparar lluvia con CHIRPS y estaciones reales SENAMHI, separando celdas ERA5 compartidas.
5. Solo delinear candidatos a unidades agroclimáticas **contiguas** respaldadas por gradiente topográfico, clima multivariable y validación espacial independiente, sin alertas fitosanitarias arándano/vid sin datos reales de campo.

Usuario prefiere continuidad ejecutiva sin preguntas ni tareas manuales; conservar todo en GitHub main.
