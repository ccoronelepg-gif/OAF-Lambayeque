# Reanudación OAF-Lambayeque: Fase 8X (octubre 2026)

## Ejecución real
- Material particulado PM2.5 y PM10 CAMS Global (Open-Meteo) integrado como variable ambiental modelada, NO instrumento o estación SENAMHI: motor modelos/particulas_aire_8x.py; pruebas tests/test_particulas_aire_8x.py; automatización .github/workflows/oaf_particulas_aire_8x.yml; resultados reales datos/aire_8x/ (fuentes gzip con URL y SHA, CSV mensual, estado).
- Año 2025 acreditado para Chiclayo/Jayanca/Motupe/Olmos con 48 registros mensuales y cobertura horaria completa; se inició recuperación adicional 2023-2024. Releer siempre datos/aire_8x/estado_aire_8x.json para el estado y periodos reales: NO afirmar cobertura 1996-2025.
- La comparación del año 2025 mostró series modeladas de PM idénticas entre Motupe y Olmos, aunque el proveedor devuelve centros de celda diferentes. Programa registra centros y detecta pares duplicados, sin atribuir independencia espacial.
- No comparar promedios CAMS globales mensuales con límites ECA legales como evaluación de cumplimiento. D.S. 003-2017-MINAM y observaciones certificadas requieren diseños instrumentales correctos.
- Auditoría de extremos climáticos históricos 2017/2023: modelos/auditoria_extremos_8x.py, tests/test_auditoria_extremos_8x.py y datos/extremos_8x/. Se generaron 480 grupos de error MAE estacional por localidad/modelo/objetivo/horizonte/año. Los valores son ERA5/ERA5-Land retrospectivos y el evento ENSO 1997-1998 estaba en entrenamiento, NO en test.
- Relaciones descriptivas PM y clima: modelos/relaciones_particulas_8x.py, tests/test_relaciones_particulas_8x.py, workflow oaf_relaciones_particulas_8x.yml. Solo cuando haya 24 meses emparejados de CAMS y ERA5, sin causalidad, significación ni habilidad futura demostrada.
- Frontend: index.html, panel oaf-aire-extremos-8x; JS modelos/visor_aire_extremos_8x.js, tabla 2017/2023 y gráfico PM mensual configurable por localidad/contaminante/año.
- Informe: FASE_8X_EXTREMOS_AIRE.md. Portal: https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.

## Próxima fase 8Y
Verificar disponibilidad exacta de PM 2023-2025, duplicación de series y posibles fuentes CAMS EAC4 2003-2025 antes de intentar 30 años. Contrastar con estaciones SENAMHI, topografía y observaciones de campo; evaluar PM como predictor únicamente mediante backtesting temporal independiente, contra climatología/persistencia, sin filtrar datos futuros. Mantener modelos ENFEN y sanidad arándano/vid como problemas separados. No afirmar pronóstico operativo ni recomendar tratamientos.
