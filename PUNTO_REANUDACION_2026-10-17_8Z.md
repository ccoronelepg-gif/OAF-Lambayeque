# OAF-Lambayeque — Punto de reanudación Fase 8Z, 17 octubre 2026

## Resultados efectivamente publicados
- 8X CAMS Global PM2.5 y PM10, 2023-2025: 144 meses-sitio, 36 meses por Chiclayo/Jayanca/Motupe/Olmos. Motupe y Olmos comparten serie PM idéntica 36 meses pese a diferentes centros reportados: no considerar independencia espacial. Archivo y estado en datos/aire_8x/, workflow 8X completado con éxito.
- RH y VPD ERA5 1996-2025 completo: 1440 meses-sitio, 360 por cuatro localidades, originales diarios comprimidos con SHA y CSV mensual en datos/humedad_8z/. Las dos variables son RH media diaria (%) y déficit presión vapor máximo diario (kPa). El VPD mensual reportado es media de máximos diarios y máximo de máximos diarios, no promedio horario. Workflow .github/workflows/oaf_humedad_agroclimatica_8z.yml SUCCESS, run 39006648617.
- PM CAMS vs RH/VPD ERA5: 16 comparaciones retrospectivas de 36 meses coincidentes (2023-2025), 16/16 evaluables con al menos 24 meses. Datos/relaciones_pm_humedad_8z/estado_relacion_pm_humedad_8z.json. Chiclayo PM25 vs RH r bruto +0.233255 y desestacionalizado +0.00797; PM25 vs VPD r bruto -0.373253 y desestacionalizado -0.184673. Cambia al excluir años, SIN significación causal/predictiva. Workflow .github/workflows/oaf_relacion_pm_humedad_8z.yml SUCCESS run 39006883872 (con comprobación DOM y sintaxis JS).
- NASA MERRA-2 verificación CMR de cuatro granulos 1998-03-15 y 2025-07-15, colecciones M2T1NXAER (superficial PM25) y M2I3NVAER (3D PM10). Fuente documentada: https://gmao.gsfc.nasa.gov/gmao-products/merra-2/faq_merra-2/ . Formula PM25 seco = DUSMASS25+OCSMASS+BCSMASS+SSSMASS25+SO4SMASS*(132.14/96.06), kg/m3->ug/m3 1e9. PM10 NECESITA mezcla 3D nivel 72 y AIRDENS, fórmula NASA. Solo se verificaron metadatos, NO series PM NASA NetCDF descargadas. Estado datos/merra2_8z/estado_piloto_merra2_8z.json, pruebas y workflow run 39006623834 SUCCESS.
- Actualización de diagnóstico 8Y: paso de 48 a 144 meses CAMS PM y de 0/40 a 40/40 asociaciones descriptivas consideradas elegibles, NO robustez ni inferencia causal. Última corrida 39006848896 SUCCESS.
- Portal: index.html, #oaf-8z-humedad y modelos/visor_humedad_merra_8z.js, consulta de RH/VPD 30 años, NASA CMR y PM vs humedad. Documento FASE_8Z_HUMEDAD_AEROSOLES_MERRA2.md.

## Limitaciones indispensables
- Reanálisis ERA5 y modelos CAMS/NASA NO son estaciones meteorológicas SENAMHI ni sensores de PM; no hacen cumplimiento ECA MINAM.
- Humedad atmosférica 2m no humedad de hojas/dosel; ningún valor por sí solo valida Botrytis ni oídio en arándano/vid.
- No confundir índice SST Niño1+2 con ICEN ENFEN, ni corrientes geostróficas con corrientes totales.
- No se dispone aún de PM MERRA2 calculados 1996-2025: pruebas sintéticas de fórmula + catálogo de granulos NO son dataset aerosol procesado.
- Las localidades solo son referencias ERA5 y no zonas agroclimáticas homogéneas SIG/instrumentalmente certificadas.

## Siguiente fase 9A
Agregar RH/VPD a benchmark clima 8W y medir incremento fuera de muestra con mismos folds 2011-2013/2014-2016/2017-2019/2020-2022/2023-2025 y 1,2,3 meses. Evitar fuga de datos y recalcular entrenamiento estrictamente anterior a test. Estratificar sensibilidad en temporada lluviosa y extremos 2017/2023; contrastar con SENAMHI. Preparar descarga autenticada con subsetting NASA MERRA2 y recetas oficiales PM25/PM10, sin inventar valores cuando autenticación falte. Continuar por zonas homogéneas de altitud y cultivos arándano/vid, con datos fitosanitarios de campo.
