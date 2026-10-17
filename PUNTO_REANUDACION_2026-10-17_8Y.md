# OAF-Lambayeque: Punto de reanudación fase 8Y (17 octubre 2026)

## Trabajo realmente implementado
- Motor: modelos/diagnostico_particulas_8y.py. Pruebas: tests/test_diagnostico_particulas_8y.py. Automatización: .github/workflows/oaf_diagnostico_particulas_8y.yml.
- Informe: FASE_8Y_AEROSOLES_Y_CLIMA.md y catálogo oficial fuentes datos/diagnostico_pm_8y/catalogo_fuentes_aerosoles_8y.json.
- Resultados auditados: datos/diagnostico_pm_8y/estado_diagnostico_pm_8y.json. Analiza PM2.5 y PM10 modelados CAMS Global frente a cinco variables: viento ERA5 a 10m, precipitación ERA5, temperatura ERA5-Land, radiación ERA5 y anomalía regional SST Niño1+2 NOAA.
- Tres análisis: coeficiente Pearson bruto, coeficiente tras retirar medias de mes calendario, estabilidad exploratoria del signo al excluir sucesivamente 2023/2024/2025. Exigir >=24 meses emparejados. No inferencia causal, no p-values, no pronósticos, no ECA.
- Identificación de series PM exactamente idénticas entre localidades y ajuste de número de series modeladas distintas; Motupe/Olmos habían mostrado mismas series 2025 pese a centros de malla reportados diferentes.
- Frontend: index.html #oaf-diagnostico-8y, JS modelos/visor_diagnostico_pm_8y.js; selector localidad/PM; tabla con correlación bruta, sin estación, meses y prueba de estabilidad, gráfico SVG.
- Documentación oficial verificada: CAMS EAC4 2003-2025 (~80km, 0.75° ADS) y NASA MERRA-2 M2T1NXAER desde 1980 (0.5°×0.625°), PM derivado con recetas NASA; NO extraídos ni validados en esta fase.

## Estado especial de 2023/2024
- Inicialmente 8X PM tenía 48 registros meses-localidad de 2025 (4 sitios×12 meses), 0/40 asociaciones por requerir >=24 meses.
- Job previo 8X run 39005204096 había DESCARGADO 2023/2024 pero falló al hacer git pull --rebase porque el estado JSON había cambiado en main: no afirmar esos datos publicados.
- Se corrigió la automatización 8X para versionar SOLO fuentes gzip+meta, restaurar derivados, sincronizar con main, reconstruir CSV/JSON y recién publicar. El nuevo run de 8X quedó en https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39005843128. Revisar estado final y luego la nueva ejecución 8Y de las correlaciones.
- Leer datos/aire_8x/estado_aire_8x.json y datos/diagnostico_pm_8y/estado_diagnostico_pm_8y.json antes de afirmar conteos actualizados. Si 8X exitoso y 8Y no se actualizó, revisar disparador por cambio CSV/JSON o rerun GitHub Actions con permisos apropiados.

## Próxima fase 8Z
Priorizar piloto NASA MERRA-2 1996-2025 para aerosoles/PM2.5/PM10 con conversión de kg/m³ a µg/m³ siguiendo fórmula NASA y QA espacial/temporal; comparar con CAMS EAC4 2003-2025 e instrumentos acreditados. Recuperar humedad relativa ERA5 y VPD si se va a analizar PM-clima fitosanitario; NO confundir humedad atmosférica con microclima de dosel. Revalidar celdas, pisos altitudinales y muestreo en Sierra Lambayeque. No activar alertas PM, ENFEN El Niño Costero ni Botrytis/vid sin validación prospectiva e instrumental.
