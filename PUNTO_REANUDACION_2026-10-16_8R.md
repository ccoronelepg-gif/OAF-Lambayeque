# OAF-Lambayeque — Punto de reanudación Fase 8R (octubre de 2026)

## Estado real
**Fase 8R implementada y CI superado** en https://github.com/ccoronelepg-gif/OAF-Lambayeque. Módulo 8R incorporado a https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.

### Insumos heredados de 8Q
- 10 puntos DEM de transectos V1a, V1b, V2, temperaturas diarias ERA5-Land de 1996-2025, fuentes JSON gz y SHA auditadas en `datos/transectos_8q/fuentes/`.
- Solo **7 centros de celda ERA5-Land únicos** entre los diez puntos (3 consultas repetidas). No son mediciones SENAMHI ni representan todo Lambayeque.
- Correlaciones térmicas históricas de anomalías 8Q descriptivas, **sin pronóstico independiente**.

### Motor predictivo 8R
Archivo `modelos/validacion_anomalias_8r.py`:
- Normal propia de cada sitio/mes calculada exclusivamente con **1996–2010** (15 años, necesaria para no infiltrar test).
- Ajuste de regresión ridge con anomalía del mes previo en el mismo sitio y señal regional mes previo; entrenamiento **1997–2010**.
- Señal regional promedia **solo otros centros ERA5-Land únicos**, excluyendo el píxel del objetivo y evitando doble peso.
- Comparación modelos: anomalía cero (climatología), persistencia, señal regional rezagada, regresión local+regional.
- **2011–2015** sirve para elegir una estrategia global, sin tocar test.
- Test reservado cronológicamente **2016–2025**, un mes adelante con observación de t−1; nunca información del mismo mes objetivo en sus predictores.
- Test en **7 celdas únicas × 120 meses = 840 predicciones**; CSV tiene **10 ubicaciones ×120=1200 filas** para diagnóstico individual, sin considerarlas 10 sensores o píxeles independientes.
- Regresión elegida por validación con coeficientes: intercepto ~0,000242; rezago local ~0,757747; rezago regional ~0,123632.
- Validación RMSE (2011–2015): clima 0,645432; persistencia 0,416145; regional 0,441655; jerárquico **0,400824** °C.
- **TEST 2016–2025**: clima RMSE **0,748643**, persistencia **0,381327**, regional **0,458211**, **jerárquico 0,363584 °C**. MAE jerárquico **0,284107 °C**.
- Skill RMSE jerárquico vs climatología **+51,43 %**, vs persistencia **+4,65 %**. **NO evaluar cifras como habilidad frente a estación de campo**; solo frente al ERA5-Land de mismo proveedor. Normal de calibración 1996–2010 puede empeorar baseline climática ante tendencia a largo plazo.
- Contraste de transferencia de coeficientes: *leave-one-temperature-pixel-out*, excluyendo por completo la celda retenida de señal regional del ajuste y validación de los seis píxeles restantes; cada celda se evalúa en 2016–2025 con su climatología local 1996–2010 y su observación t−1. RMSE de seleccionado **0,363771 °C**, persistencia **0,381327**, reducción **4,60 %**. Los 7 pliegues eligieron jerárquico.
- **Limitación:** retener un píxel cercano no es prueba de extrapolación sin clima histórico del nuevo sitio, ni validación instrumental externa, ni bloque regional/cuenca independiente.
- Pronósticos ENSO El Niño Costero verificados = 0; zonas agroclimáticas cartografiadas certificadas = 0; alertas fitosanitarias de arándano o vid validadas = 0; validación con SENAMHI = 0.
- No se activaron pronósticos en vivo, ni se tocaron módulos previos 8E/8G o boletines oficiales.

### Artefactos reales
- `modelos/validacion_anomalias_8r.py`: algoritmo, reproducible sin dependencias Python externas.
- `tests/test_validacion_anomalias_8r.py`: pruebas sintéticas aisladas de ausencia de fuga futura, calendario t−1, deduplicación de píxeles, regresión, control espacial.
- `.github/workflows/oaf_validacion_8r.yml`: CI y recomputación --check con auto commit cuando cambie la evidencia.
- `datos/validacion_predictiva_8r/estado_validacion_8r.json`: parámetros, cortes, errores, diagnóstico por localidad y 7 pliegues espaciales; fichero fuente de verdad.
- `datos/validacion_predictiva_8r/predicciones_retrospectivas_8r.csv`: 1.200 estimaciones y objetivos por mes 2016–2025.
- `FASE_8R_VALIDACION_PREDICTIVA.md`: metodología completa con comparaciones y límites.
- `index.html` y `modelos/visor_anomalias_8r.js`: panel 8R en #verificaciones, barras RMSE, detalle de sitios, control de transferencia espacial, advertencias de no operación.

### Próximo paso 8S recomendado
- Ampliar del puñado de celdas 8Q a la muestra climática regional de 8P hasta 81 testigos, **con deduplicación de celda y validación espacial por bloques de cuenca y altitud**.
- Obtener realmente SENAMHI estaciones con códigos/metadatos y temperaturas 1996–2025 y datos más recientes; NO asumir disponibilidad instrumental.
- Evaluar backtests rolling origin (varios cortes anuales); no probar sobre el test y escoger después, exigir predicción emitida antes de observar el mes si se va a publicar habilidad prospectiva.
- Separar reconstrucción de temperatura absoluta local de predicción de anomalías regionales; comprobar estabilidad y drift de la normal en diferentes pisos altitudinales.
- Contrastar dinámicas pluviales con CHIRPS y SENAMHI por celda, máscara tierra/mar, cuencas, orientación de ladera y cartografía oficial IGN/INEI.
- Examinar ENSO oceánico institucional de ENFEN/NOAA como factor **con su disponibilidad temporal real en el momento de predecir**, sin anticipación del futuro ni atribuir avisos oficiales a OAF.
- Cultivos arándano y vid: alertas de riesgo requieren evaluaciones reales de campo, microclima, fenología y patógenos, no extrapolación de un RMSE térmico.

No hacer cuestionarios al usuario, proseguir como trabajo técnico real, con cierres honestos de reproducibilidad.
