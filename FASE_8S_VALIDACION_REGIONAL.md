# Fase 8S: validación regional de anomalías térmicas con retención espacial

**OAF-Lambayeque · periodo de origen 1996–2025 · evaluación retrospectiva, no operacional.**

## Propósito y fuentes
Se amplió la evaluación de fase 8R, que solo cubría siete centros ERA5-Land, hacia los testigos regionales disponibles en fases 8O y 8P. Los datos originales son respuestas históricas de Open-Meteo para **ERA5-Land**; se leen los JSON comprimidos archivados junto a su hash y metadatos, y se recalculan los promedios mensuales. **No son estaciones SENAMHI.**

Al momento del experimento existían **67 testigos con 360 meses completos**. Se excluyeron preventivamente dos con DEM ≤5 m, pendientes de cartografía tierra/mar. Los **65 testigos analizados representaron 50 centros térmicos distintos**, pues 15 consultas repetían un centro. Las 50 celdas cuentan una vez en la evaluación principal: no equivalen a 50 mediciones independientes de campo. Esta es una muestra regional de diseño, no una distribución proporcional por superficie agrícola.

## Validación cronológica rigurosa: cinco cortes
Cada anomalía se calcula usando **la normal mensual del propio sitio computada hasta el fin del entrenamiento del corte**, sin usar años posteriores. Se ajustan cuatro estrategias candidatas: anomalía cero (climatología), persistencia t−1, anomalía regional t−1 de otras celdas únicas y regresión ridge local+regional t−1. Se elige la estrategia con menor RMSE de validación, antes del periodo de prueba.

| Corte | Ajuste | Selección | Prueba |
|---|---|---|---|
| 1 | 1997–2008 | 2009–2011 | 2012–2014 |
| 2 | 1997–2011 | 2012–2014 | 2015–2017 |
| 3 | 1997–2014 | 2015–2017 | 2018–2020 |
| 4 | 1997–2017 | 2018–2020 | 2021–2022 |
| 5 | 1997–2020 | 2021–2022 | 2023–2025 |

La normal utiliza datos desde 1996 hasta el fin del ajuste en cada corte. Se evita superposición entre periodos de prueba: cada mes de 2012–2025 aparece una sola vez en el agregado. La prueba permite conocer el reanálisis mensual del mes anterior **t−1**, pero no el valor del objetivo **t**; el acceso operacional a ERA5-Land puede tener otra latencia. Ningún corte constituye un pronóstico realmente emitido en ese año.

## Control de transferencia geográfica
Se distribuyeron los **50 centros** en **cuatro franjas latitudinales balanceadas**, construidas por coordenadas del centro de rejilla (no límites de cuenca, ecosistema, altitud o cartografía INEI/IGN). En cada corte se retuvo una franja completa, se reentrenaron los coeficientes con las otras y la selección se hizo sin la franja retenida. Los predictores regionales usados durante entrenamiento y validación también excluyen por completo las celdas de la franja reservada. Después se evalúa la franja retenida en los meses de prueba, **permitiendo explícitamente su climatología propia del periodo de entrenamiento y su observación t−1**. Por tanto, **NO evalúa transferencia a una ubicación sin registros previos**.

## Resultados reales de la ejecución inicial

Se evaluaron **8.400 anomalías mensuales retrospectivas** (50 centros × 168 meses de prueba) tanto en el diseño temporal como en el control espacial.

| Evaluación | RMSE seleccionado | RMSE persistencia | RMSE climatología | Reducción relativa del RMSE frente a persistencia |
|---|---:|---:|---:|---:|
| Cinco cortes temporales | **0,448275 °C** | 0,468228 °C | 0,878651 °C | **4,2614 %** |
| Cinco cortes y franjas retenidas | **0,448167 °C** | 0,468228 °C | 0,878651 °C | **4,2845 %** |

Los cinco cortes seleccionaron previamente el modelo jerárquico y obtuvieron las siguientes comparaciones RMSE (modelo vs persistencia): 2012–2014 **0,467761 vs 0,495672** °C; 2015–2017 **0,416788 vs 0,428646** °C; 2018–2020 **0,403200 vs 0,424201** °C; 2021–2022 **0,446455 vs 0,471317** °C; 2023–2025 **0,499807 vs 0,515401** °C.

### Diagnóstico por ambiente altitudinal
Los estratos son **clases físicas de muestreo por elevación DEM**, no zonas agroclimáticas confirmadas.

| Estrato físico | RMSE modelo, validación por bloque | RMSE persistencia | Variación relativa RMSE |
|---|---:|---:|---:|
| Planicie costera >5 m y <100 m | 0,566437 °C | 0,583587 °C | +2,94 % |
| Valle bajo 100–299 m | 0,476122 °C | 0,497628 °C | +4,32 % |
| Piedemonte 300–799 m | 0,413984 °C | 0,434353 °C | +4,69 % |
| Montaña baja 800–1.599 m | 0,361147 °C | 0,381327 °C | +5,29 % |
| Montaña media 1.600–2.499 m | 0,321652 °C | 0,348482 °C | +7,70 % |
| Alta montaña desde 2.500 m | 0,330746 °C | 0,361974 °C | +8,63 % |

La variación de resultados por estrato puede reflejar tanto diferencias físicas reales como características del reanálisis y tamaño desigual de muestra. No constituye prueba estadística suficiente de habilidad específica para todos los sectores productivos a esas altitudes. **El modelo combinado supera la persistencia en el agregado experimental; la ventaja es moderada y aún no está verificada instrumentalmente.**

## Limitaciones científicas y próximos pasos
- Fuente única: **ERA5-Land**, usada tanto como predictor como referencia objetivo. Celdas distintas de la misma reanálisis pueden compartir errores y dependencia espacial.
- Los testigos no representan proporcionalmente todas las zonas agrícolas de Lambayeque, y las cuatro franjas retenidas no son cuencas ni polígonos homogéneos.
- Una mejora de aproximadamente 4 % respecto de persistencia puede desaparecer al incorporar estaciones reales, periodos más recientes, años extremos o otras áreas espaciales.
- Se necesita evaluación con **SENAMHI** (códigos de estación, metadatos, medidas y cobertura oficial confirmada), cartografía **INEI/IGN**, máscara tierra/agua, orientación y cuencas, pruebas de incertidumbre y emisiones anteriores a cada fecha objetivo.
- Las temperaturas locales de los pisos altitudinales no deben unificarse; el hallazgo se refiere a **anomalías mensuales**, no a temperaturas absolutas idénticas.
- No se han incorporado en 8S variables predictoras ENSO/ENFEN, lluvia, humedad, radiación ni riesgos de patógenos en arándano y vid. Ninguna alerta operativa o zona homogénea queda certificada.

## Trazabilidad y reproducción
- [Motor 8S Python](modelos/validacion_regional_8s.py): lectura diaria de fuentes originales 8O/8P con hash, agregación mensual, deduplicación de celda, comparación cronológica, entrenamiento y retención geográfica.
- [Pruebas automatizadas](tests/test_validacion_regional_8s.py): 11 casos aislados, sin descargar datos externos, incluyendo ausencia de fuga al variar meses posteriores y ausencia de superposición de los meses del test.
- [Workflow de evaluación 8S](.github/workflows/oaf_validacion_regional_8s.yml): controla reproducibilidad y archiva artefactos.
- [Reporte verificable y métricas](datos/validacion_regional_8s/estado_validacion_8s.json).
- [Predicciones retrospectivas por corte temporal](datos/validacion_regional_8s/predicciones_temporales_8s.csv).
- [Predicciones con bloque geográfico retenido](datos/validacion_regional_8s/predicciones_bloques_8s.csv).
- [Observatorio OAF-Lambayeque](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

**Estado final científico:** backtest regional reproducible sobre reanálisis, **0 validaciones instrumentales SENAMHI**, **0 pronósticos regionales prospectivos demostrados**, **0 delimitaciones de zonas agrícolas homogéneas acreditadas**.

## Fase 8T propuesta
Completar la muestra de 81 testigos 8P; repetir los cinco cortes y controles por bloques espaciales/cadenas hidrográficas una vez verificadas cuencas; estudiar teleconexiones ENSO (fuentes ENFEN/SENAMHI/NOAA con disponibilidad temporal histórica) y predictores de radiación y lluvia *con versiones archivadas y sin anticipar información del mes objetivo*. En paralelo, buscar series de estaciones SENAMHI para confrontar errores del reanálisis, calibración local e independencia instrumental.
