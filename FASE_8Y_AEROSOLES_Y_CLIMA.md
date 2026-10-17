# OAF-Lambayeque — Fase 8Y: partículas y relaciones agroclimáticas

**Fecha técnica:** 17 de octubre de 2026 · **Naturaleza:** investigación retrospectiva, análisis de modelo atmosférico, NO vigilancia instrumental ni pronóstico operacional.

## Pregunta

¿En qué medida las concentraciones mensuales modeladas de **PM₂.₅ y PM₁₀** describen la variabilidad asociada con viento atmosférico, lluvia, temperatura del aire, radiación y temperatura superficial marina regional en Chiclayo, Jayanca, Motupe y Olmos? ¿Se mantiene una asociación al retirar el ciclo estacional? ¿Podemos obtener productos de aerosoles con una cobertura equivalente a la climatología **1996–2025** del OAF?

Los resultados NO prueban que El Niño cause contaminación específica, que las partículas causen enfermedad vegetal, ni que permita pronosticar anomalías agroclimáticas. PM₂.₅ y PM₁₀ NO son concentraciones de esporas fúngicas ni variables fitopatológicas directas.

## 1. Estado de la serie 8X y recuperación

Se constató que la automatización de 8X recuperó **2023 y 2024** desde la fuente CAMS Global/Open-Meteo, pero un conflicto al sincronizar el CSV/JSON con otros cambios de GitHub impidió su publicación completa (run [39005204096](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39005204096)). Esta incidencia se corrigió en el flujo [`oaf_particulas_aire_8x.yml`](.github/workflows/oaf_particulas_aire_8x.yml): primero se versionan las fuentes originales por sitio/año, se sincroniza con `main`, se reconstruyen desde las fuentes las tablas y el estado, y después se publican. **No afirmar 144 registros archivados hasta que `datos/aire_8x/estado_aire_8x.json` lo confirme.**

El archivo `datos/aire_8x/estado_aire_8x.json` es la única referencia vigente de la cobertura realmente archivada. Los archivos originales comprimidos tienen SHA-256 y coordenadas reales devueltas por el proveedor; no son mediciones de estaciones.

## 2. Nuevo diagnóstico reproducible

Se implementó [`modelos/diagnostico_particulas_8y.py`](modelos/diagnostico_particulas_8y.py), con [pruebas independientes](tests/test_diagnostico_particulas_8y.py) y una automatización [8Y](.github/workflows/oaf_diagnostico_particulas_8y.yml) que se reejecuta cuando las series de 8X cambian.

Se relacionan, **solo en meses que están realmente disponibles**, PM₂.₅ y PM₁₀ con cinco variables: viento 10 m, precipitación mensual, temperatura del aire, radiación corta y anomalía del índice Niño 1+2. Diez pares de variables × cuatro ubicaciones = **40 combinaciones candidatas**.

Para cada combinación:
1. Comprobar que al menos **24 meses reales emparejados** tengan ambas variables válidas. Ausencia de medición = correlación no disponible, NUNCA cero inventado.
2. Calcular correlación Pearson **bruta** mensual de 2023–2025. No interpretarla causalmente.
3. Retirar el **promedio de cada mes calendario** (ciclo estacional) de ambos campos y recalcular Pearson. Esta referencia descriptiva utiliza la muestra completa 2023–2025 y **no puede reutilizarse como normal predictiva de training**.
4. Repetir de forma ilustrativa excluyendo por separado 2023, 2024 y 2025 cuando el resto tenga al menos 24 meses, identificando si el **signo** de la asociación se conserva. Solo tres años, autocorrelación temporal y múltiples hipótesis: sin pruebas p-valores ni intervalos de confianza calibrados.
5. Detectar automáticamente series PM enteramente **idénticas entre sitios**: aunque el proveedor devuelva centros de celda distintos, coincidencias Motupe–Olmos no justifican contar la misma señal atmosférica dos veces como replicación independiente.

Salida: [estado_diagnostico_pm_8y.json](datos/diagnostico_pm_8y/estado_diagnostico_pm_8y.json). En el dashboard de la sección Verificación, panel **Fase 8Y**, se muestran por sitio y PM ambas correlaciones, cantidad de meses, estabilidad exploratoria y advertencias de duplicación. Si no hay al menos 24 meses emparejados, **la interfaz no inventa una correlación**.

La variable humedad relativa es científicamente prioritaria, pero **todavía no hay una matriz mensual de humedad homologada con PM**; se debe recuperar ERA5 horaria/diaria con QA de unidades, zonas y fechas antes de incorporar humedad al análisis. En el catálogo de Open-Meteo Historical Weather se documenta `relative_humidity_2m`. No confundir humedad de un píxel con humedad del dosel del cultivo.

## 3. Fuentes científicas históricas para ampliar PM

| Fuente | Periodo documentado | Alcance y condición |
|---|---|---|
| [ECMWF/CAMS EAC4](https://www.ecmwf.int/en/research/climate-reanalysis/cams-reanalysis) | **2003–2025** | Reanálisis global ~80 km, disponible en ADS, NO descargado/validado en OAF. No cubre 1996–2002. |
| [NASA MERRA-2 M2T1NXAER](https://access.earthdata.nasa.gov/collections/C1276812830-GES_DISC) | **Desde 1980** | Reanálisis aerosol ~0,5° × 0,625°, candidato para 1996–2025. PM₂.₅/PM₁₀ total requiere **derivar** composición con recetas oficiales, no equivale a sensor. No descargado/validado. |
| [CAMS Global via Open-Meteo](https://open-meteo.com/en/docs/air-quality-api) | Piloto 2023–2025 | Producto de modelo accesible de forma directa, pero no homogéneo con una normal de 30 años. |

Inventario machine-readable: [catálogo de aerosoles 8Y](datos/diagnostico_pm_8y/catalogo_fuentes_aerosoles_8y.json). El historial científico CAMS EAC4 hasta diciembre 2025 fue comunicado por ECMWF en junio 2026. Comprobar licencias, ADS/Earthdata y características de cada producto antes de descarga.

## 4. Uso agronómico futuro y límites

Estudiar con datos de campo si el polvo se deposita sobre hojas y frutos y si influye en microclima, radiación incidente, calidad comercial u otros factores agronómicos. No inferir incidencia de *Botrytis* u oídio por PM₂.₅/PM₁₀; se necesitará monitoreo de patógenos, inóculo, cultivo, estadio fenológico y condiciones de dosel. Las correlaciones no reemplazan experimentos ni observaciones instrumentales.

La legislación peruana ECA Aire (D. S. 003-2017-MINAM) requiere datos y procedimientos de evaluación normativos, que **no equivalen a promedios CAMS**. El proyecto mantiene deshabilitadas afirmaciones de cumplimiento ECA, alertas fitosanitarias y predicciones por PM.

## 5. Resultado científico / criterio de activación

**Se autoriza exclusivamente la exploración retrospectiva.** Antes de incluir PM como predictor en modelos 1996–2025 habrá que obtener una fuente histórica realmente continua (MERRA-2 u otro producto verificado), demostrar consistencia temporal, caracterizar celdas/topografía, validar frente a estaciones y medir la mejora predictiva fuera de muestra con referencias simples y particiones sin fuga futura.

La **fase 8Z** debe priorizar un piloto reproducible de adquisición MERRA-2 de baja área y periodo controlado (y posible comparación EAC4), cuantificar sesgos entre productos, y considerar humedad/deficiencia de presión de vapor como covariables meteorológicas con trazabilidad real. No atribuir el comportamiento de una celda a toda la región ni presentar alertas prematuras.
