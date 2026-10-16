# OAF-Lambayeque — Punto de reanudación 16/10/2026 · Fase 8L

## Parte 8L implementada y verificada

Fase 8L completa: **sensibilidad del reanálisis histórico ERA5-Land a los criterios de selección `cell_selection=land` vs `nearest` de Open-Meteo**, 1996–2025, en Chiclayo/Jayanca/Motupe/Olmos.

**Hallazgo REAL significativo:** los dos criterios devolvieron las **mismas celdas y temperaturas** para los cuatro puntos geográficos actuales. Se archivaron **6 respuestas originales de Open-Meteo** comprimidas, divididas en tres décadas × dos selectores; **1.440 pares mensuales** comparados con cobertura completa, 360 meses por localidad. En cada localidad, MAE entre criterios = 0,00000 °C, máximo delta = 0,00000 °C, MAE de diferencias de anomalía = 0,00000 °C y 0 celdas distintas. La nueva serie `land` también reproduce los valores mensuales archivados de 8D a la precisión almacenada (MAE 0,00000 °C), **sin demostrar haber recuperado la respuesta de metadatos de celda original de 8D**.

## Archivos

- `modelos/sensibilidad_celdas_8l.py`: motor descarga, integridad de respuestas, elaboración de normales mensuales con 30 años 1996–2025 y comparación land/nearest. Sin observar SENAMHI, sin reentrenamiento o afirmaciones predictivas.
- `tests/test_sensibilidad_celdas_8l.py`: 8 pruebas, fixtures sintéticas en directorios temporales; controles de días, SHA, archivos parciales y periodos de 10 años.
- `.github/workflows/oaf_sensibilidad_celdas_8l.yml`: CI registra seis fuentes y derivados, y verifica el panel. Primera ejecución con descarga completó con success, y la ejecución tras añadir HTML/JS también aprobó (run 38981559296).
- `datos/fuentes_celdas_8l/`: seis archivos `.json.gz` con respuestas de Open-Meteo y seis `.meta.json` URL/fecha/hash, sin recalcular ni sustituir fechas.
- `datos/sensibilidad_celdas_8l/estado_8l.json`: resumen real, métricas y trazabilidad.
- `datos/sensibilidad_celdas_8l/pares_mensuales_8l.csv`: 1.440 registros (Tmedias, anomalías mensuales y diferencias con referencia 8D).
- `modelos/visor_sensibilidad_celdas_8l.js` e `index.html`: panel 8L dentro de «Verificación de datos», tabla de cuatro localidades y gráfico anual de diferencias reales.
- `FASE_8L_SENSIBILIDAD_CELDAS.md`: metodología, datos, límites de interpretación y fuentes Open-Meteo / Copernicus ECMWF.

## Interpretación y limitaciones

Los selectores land y nearest pueden devolver exactamente la misma celda para una coordenada determinada; **cero diferencia aquí NO significa ausencia de sesgo espacial general**, particularmente costas, topografía y sitios rurales alejados del punto de referencia. Open-Meteo puede corregir valores por elevación: no atribuir diferencia observada a orografía de ERA5-Land sin aislar los factores. Ningún resultado de 8L valida temperatura real de estaciones SENAMHI, habilidad prospectiva de pronósticos 8E/8G, anomalías ENSO o riesgo fitosanitario operativo.

Climatología OAF pública **1996–2025**, comparativa OMM **1991–2020** cuando proceda. Fitosanidad arándano/vid y vigilancia El Niño Costero (ENFEN) son líneas de trabajo permanentes y diferenciadas.

## Próxima Parte 8M sugerida

**Sensibilidad espacial a desplazar los puntos de consulta** varios kilómetros alrededor de Chiclayo/Jayanca/Motupe/Olmos, especialmente direcciones costa/interior y relieve. Comparar centro de celda seleccionado, altitud API, temperaturas por métodos, anomalías 1996–2025 y proporción de puntos cuyo píxel cambia. Utilizar puntos declarados con diseño previo (no afirmar ubicación de parcelas productivas), horarios y fechas reproducibles, evitar comparaciones que mezclen ERA5 con ERA5-Land. El resultado puede seguir siendo exploratorio, sin comparación con sensores SENAMHI hasta tener series reales autorizadas.

**Instrucciones del usuario:** continuar de forma técnica y ejecutiva, sin preguntas ni tareas para el usuario; preservar repositorio, página y verificación científica.
