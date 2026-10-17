# OAF-Lambayeque · Punto de reanudación Fase 8V, 17 octubre de 2026 (UTC)

## Logrado y efectivamente publicado en repositorio GitHub

La fase 8V no es una propuesta: hay código, pruebas, workflow y **salidas reales publicadas**.

- Código: `modelos/integracion_oceano_atmosfera_8v.py` (validación 1996–2025, trazabilidad y lag Niño1+2 de 1/2/3 meses, sin imputación).
- Dataset terrestre: `datos/integracion_8v/matriz_terrestre_8v.csv` — 4 localidades Chiclayo/Jayanca/Motupe/Olmos × 360 meses = **1440 registros**. Meteorología ERA5/ERA5-Land, viento ERA5, SST Niño1+2/Niño3.4 NOAA CPC revisados, no ICEN ENFEN ni SST de playa.
- Dataset marino: `datos/integracion_8v/matriz_marina_8v.csv` — 2 celdas de viento ERA5 marino × 360 meses = **720 registros**, corriente geostrófica NOAA/AOML **solo 216 registros completos (2017–2025)** en dos puntos marinos próximos pero NO colocalizados; los 504 restantes sin corriente permanecen vacíos. No confundir viento atmosférico y corriente marina, ni geostrófica con corriente total.
- Estado y SHA: `datos/integracion_8v/estado_integracion_8v.json` contiene SHA-256 de las 4 fuentes CSV y 2 matrices resultantes, cobertura y limitaciones.
- Extremos modelados: **11 meses-localidad** con precipitación ERA5 ≥1000 mm mensuales marcados para revisión instrumental; máximo ERA5 en Motupe marzo 1998 **2913,8 mm**, pendiente contraste SENAMHI. **NO afirmar que estación registró esa cifra**.
- Test: `tests/test_integracion_oceano_atmosfera_8v.py`, **7 pruebas sintéticas** (cobertura, idempotencia, lags, faltantes de viento y clima, duplicados, lluvia extrema sin descartar). Automatización `.github/workflows/oaf_integracion_oceano_atmosfera_8v.yml`, resultado de generación real en [Actions](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39003458908) **success**, nueva ejecución con verificación web pendiente de comprobar en su run correspondiente.
- Portal: gráfico SVG interactivo con filtros de localidad (4), variable (7), ventana temporal; panel `#oaf-integracion-8v` insertado en `index.html` dentro de página [Verificaciones](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones), motor `modelos/visor_integracion_8v.js`. No presenta anomalías como pronóstico.

## Precauciones permanentes

El periodo 1996–2025 es referencia **descriptiva**, nunca una normal aprendida sobre años posteriores de prueba. Entrenar modelos con cortes temporales y normales estimadas solo dentro de training. Viento u/v aproximado proviene de velocidades medias y dirección dominante diaria ERA5, NO vectores horarios exactos. NOAA SST índices grandes y revisados no son mediciones de TSM en Puerto Eten/Pimentel/Olmos. Corrientes geostróficas 2017–2025 NO pueden imputarse a 1996–2016. Zonas homogéneas SIG certificadas = 0; estaciones terrestres SENAMHI independientes para skill predictivo = 0; alerta predictiva El Niño Costero o riesgo fitosanitario validado = 0. No confundir un backtest en reanálisis con predicción prospectiva real.

## Próxima fase 8W — Objetivos agronómicos y backtesting preespecificado

En vez de asumir que SST/corrientes mejoran siempre el pronóstico, estudiar por localidad y zona física la habilidad para:
1. anomalías de temperatura media y extremos cálidos/fríos;
2. lluvia mensual superior a umbrales por mes/estación, con datos modelados y contraste SENAMHI;
3. errores por temporada y 1997–1998/2017/2023 como episodios de estrés climático, sin usar esos años simultáneamente en entrenamiento y prueba;
4. comparadores climatología/persistencia y variantes viento+Niño1+2 (+corrientes solo en subperiodo 2017–2025), con 5+ cortes cronológicos, umbrales y escalado solo del entrenamiento;
5. métricas MAE/RMSE y para eventos Brier score, calibración, sensibilidad/especificidad, precisión/recobrado y PR-AUC cuando proceda.

Se requiere trabajar todavía en delimitación de zonas homogéneas mediante SIG, estaciones SENAMHI y observaciones de enfermedades de arándano y vid para validar realmente pronósticos por zona o fitosanitarios.

**Evitar cuestionarios o ejercicios al usuario; avanzar implementando realmente y reportar resultados comprobables.**
