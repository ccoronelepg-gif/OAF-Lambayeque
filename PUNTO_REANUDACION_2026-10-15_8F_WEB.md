# Punto de reanudación OAF-Lambayeque — 15 de octubre de 2026

## Estado y continuidad
- Proyecto: Observatorio Agroclimático y Fitosanitario OAF-Lambayeque, con identidad CECG.
- Última fase trabajada: **8F-Web — rediseño funcional y reorganización del portal**, posterior a la fase 8F de verificación prospectiva.
- **Siguiente fase solicitada, todavía pendiente: 8G**, evaluador automatizado de pronósticos en Python, con lectura del registro maestro, cálculo de MAE/RMSE/sesgo/cobertura, gráficos por localidad/modelo y garantía de que los pronósticos se verifican únicamente con observaciones posteriores.
- El usuario pidió **guardar este estado y continuar más tarde**. No iniciar la 8G sin nueva indicación.

## Portal y repositorio
- Repositorio: https://github.com/ccoronelepg-gif/OAF-Lambayeque
- Sitio público: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
- Rama: main.
- Último commit del rediseño verificado en la conversación: `3a08478ab3c00c03713fed972c8946cb6742e20e`. El despliegue de GitHub Pages de ese commit terminó con éxito, y también lo hicieron las pruebas automáticas de los flujos «OAF 2.0 verificar plan de vigilancia y alertas» y «OAF 3Z calidad de fuentes actuales».

## Cambios realizados durante 8F-Web
1. Incorporación de identidad CECG en la cabecera y favicon por `assets/logo-cecg.svg`.
2. Nuevo estilo responsivo profesional de ciencias agrarias/climatología en `assets/oaf-redesign-8f.css`; colores azul, verde, celeste y acentos cálidos.
3. Nuevo módulo `Dashboard` con gráficos SVG dinámicos de Open-Meteo (temperatura, humedad, precipitación, radiación, viento, DPV, ET₀) y filtros Chiclayo, Jayanca, Motupe y Olmos, en `assets/oaf-redesign-8f.js`.
4. Explorador de **anomalías históricas** desde `datos/lambayeque_mensual_era5_8d.csv`, referencia mensual 1996–2025. Para cada localidad se observaron 360 meses de base (1996-01 a 2025-12), sin duplicados; registros posteriores hasta septiembre de 2026. Son datos de reanálisis, no instrumentos SENAMHI.
5. Pestaña `Control fitosanitario` para nueve enfermedades de arándano y vid, con medidas culturales y ejemplos de productos químicos y biológicos enlazados a etiquetas SENASA y guías UC IPM/UF-IFAS/FRAC.
6. Reorganización del menú en siete secciones: Inicio, Monitoreo agroclimático, Sanidad fitosanitaria, Dashboard, Control fitosanitario, Boletines y El Niño, Verificación de datos.
7. Se trasladaron **11 visores y módulos de fases 6–8E** a Verificación de datos, preservando sus IDs, métodos, descargas y vínculos. También se preservaron la presentación y autoría originales en archivo técnico.
8. Se restauraron y ubicaron dentro de Verificación de datos las referencias antiguas `id="plan20"` y `id="monitoreo3z"` que requieren las pruebas CI.
9. Boletines: se añadió una referencia fechada de ENFEN separada del verificador automático; la alerta oficial jamás es atribuida al OAF.

## Criterios científicos vigentes y controles a revisar
- Climatología principal 1996–2025; referencia comparativa OMM 1991–2020 cuando exista cobertura.
- Cubrimiento: Chiclayo, Jayanca, Motupe y Olmos; fitosanidad de arándano y vid.
- No inventar datos ni imputar observaciones faltantes sin justificación.
- Diferenciar pronósticos meteorológicos externos, reanálisis ERA5-Land, observaciones SENAMHI y pronósticos OAF.
- La fase 8E archivó emisiones prospectivas, pero **no tiene todavía habilidad predictiva prospectiva demostrada**. No presentar probabilidades ni alertas fitosanitarias como validadas.
- **Pendiente una comprobación visual del isotipo** para asegurar que `assets/logo-cecg.svg` reproduce exactamente la imagen CECG enviada por el usuario. También es recomendable probar las nuevas interfaces en navegador, y revisar vigencia y alcance real de cada etiqueta SENASA (producto × cultivo × enfermedad, modo de uso, carencia) antes de publicitar productos como autorizados.
- Cualquier cambio debe conservar los controles QA, datos y resultados experimentales ya desarrollados.

## Al reanudar
1. Leer este documento y consultar el estado actual del repositorio.
2. Si el usuario solicita 8G, implementar el evaluador Python usando el archivo original de pronósticos 8E y las observaciones que estén publicadas, con evaluación temporal estricta, intervalos calibrados y métricas que no inventen habilidad.
3. Conservar toda documentación técnica en la sección Verificación de datos y mantener la portada accesible, sin redundancias.
