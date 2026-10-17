# OAF-Lambayeque — punto de reanudación fase 9A (17 octubre 2026)

## Estado real, código ejecutado
- Motor Python: modelos/sensibilidad_humedad_vpd_9a.py; 8 tests sin fuga: tests/test_sensibilidad_humedad_vpd_9a.py. Workflow .github/workflows/oaf_sensibilidad_humedad_vpd_9a.yml. Último run VALIDADO exitosamente: https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39007456165 (tests, recomputación en ERA5, comparación 8W exacta y revisión JS/DOM).
- Datos publicados: datos/benchmark_9a/pronosticos_pareados_9a.csv (17280 pronósticos modelo-fecha), datos/benchmark_9a/eventos_p90_pareados_9a.csv (1440 probabilidades P90 retrospectivas), datos/benchmark_9a/estado_benchmark_9a.json con estadísticas/estabilidad/errores 2017/2023/fuentes SHA.
- Se amplía el modelo 8W local + viento + SST Niño 1+2/3.4 usando RH y VPD ERA5 de 1996-2025 de 4 localidades, 1440 meses-sitio, y se comparan 4 alternativas: base, base + RH, base + VPD, base + RH/VPD. Exactamente mismos train/test 2011–2013,2014–2016,2017–2019,2020–2022,2023–2025 y h=1,2,3 meses. Dos objetivos: T aire °C y lluvia ERA5 mm. Normalización de climatologías y Ridge alpha=15 entrenados SOLO con etiquetas anteriores al bloque; RH/VPD solo de fecha origen t, nunca mes objetivo t+h. Se verifica reproducción exacta del modelo base 8W dentro del redondeo y parejas sitio-fecha.
- Resultados agregados: con RH+VPD mejora MAE vs base solamente 5/12 combinaciones temperatura y 6/12 precipitación. Con RH sola 6/12 temperatura y 6/12 lluvia. Con VPD sola 5/12 temperatura y 6/12 lluvia.
- Estabilidad RH+VPD en >=3/5 cortes: temperatura 6/12, lluvia 5/12. En >=4/5: temperatura 2/12, lluvia 1/12. No seleccionar por promedios sin revisar cortes.
- PM para lluvia extrema enero–abril: eventos > P90 calculados SOLO en train por mes calendario, regresión logística; RH+VPD mejora Brier en solo 1/12 combinaciones localidad/horizonte. Olmos h1 base Brier .07386706 vs .07338589 +RH+VPD (mejora 0.6514%); 11/12 empeora, no activar.
- T+lluvia h1 MAE base y +RH/VPD: Chiclayo T .430439 -> .427934 °C; Jayanca .378756 -> .378033°C; Motupe .336764 -> .338335°C; Olmos .333740 -> .330774°C. Lluvia: Chiclayo 10.018625 -> 10.258646 mm; Jayanca 36.796392 -> 38.560249; Motupe 45.689133 -> 46.603207; Olmos 36.638134 -> 36.576657. Resultados no monotónicos.
- Eventos 2017/2023 enero–abril auditados con MAE/RMSE, 4 meses por año, no demostración de ENSO. El Niño 1997–98 en training de todos los folds: NO existe holdout para ese fenómeno.
- Frontend integrado index.html panel #oaf-benchmark-9a y modelos/visor_benchmark_9a.js con filtros localidad/horizonte/objetivo, MAE/RMSE, gráfica 5 cortes y comparativa Brier P90. Informe completo: FASE_9A_BENCHMARK_HUMEDAD_VPD.md.

## Fuentes y limitaciones
- RH y VPD meteorológicos ERA5 de Open-Meteo, no sensores SENAMHI ni humedad del dosel de arándano/vid. VPD es media del máximo diario, no VPD promedio horario. ERA5 y NOAA SST revisados retrospectivamente no disponen de versiones archivadas a la fecha de supuesta emisión.
- Cuatro ubicaciones de modelo NO equivalen a muestreo completo de pisos de Lambayeque; continua pendiente SIG/cuencas y homogeneidad topoclimática e instrumental.
- PM2.5/PM10 CAMS disponibles SOLO 2023-2025 en 8X: 144 meses-sitio con Motupe/Olmos series idénticas. No hay PM histórico 1996-2025, por lo que NO se incluye en modelo 9A.
- NASA MERRA-2 en 8Z solo fórmulas físicas y metadatos CMR 1998/2025 verificados, no series NetCDF procesadas. No atribuir validación PM histórica 30 años.
- Ningún riesgo fitosanitario arándano/vid ni alerta a productores hasta contrastar SENAMHI y evaluaciones de campo.

## Próximo paso: 9B
Evaluar incertidumbre por remuestreo en bloques anuales con diferencias de pérdida pareadas y corrección de multiplicidad, sensibilidad de resultados a pocos años ENSO y definición de información disponible en fecha emisión; ampliar a zonas realmente homogéneas con altitud, cuenca, topografía y estaciones. Priorizar una prueba conservadora para 1997–98 con años train anteriores si histórico suficiente, no falsa habilidad fuera de muestra. Mantener página con visualizaciones claras y estado no-operativo.
