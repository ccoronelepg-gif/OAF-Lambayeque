# OAF-Lambayeque — Punto de continuidad · 16/10/2026 · Fase 8J

## Avance
La **Parte 8J** está implementada y comprobada: sistema de homologación **horaria** de temperatura instrumental SENAMHI, conversión horaria a `America/Lima`, integridad de 24 observaciones por día y de todos los días de mes, cribado provisional geográfico/altitudinal, comparación descriptiva con reanálisis ERA5-Land 8D y visor público en pestaña **Verificación de datos**.

**No hay datos instrumentales horarios SENAMHI incorporados** al repositorio. Los reportes registran:
- 0 archivos fuente y estaciones horarias autorizadas.
- 0 meses horarios completos, 0 pares descriptivos estación–reanálisis.
- MAE/RMSE/sesgo nulos/no evaluables.
- Sin habilidad prospectiva demostrada para modelos 8E, sin calibración de intervalos 90 % y sin validación independiente.
- Históricos SENAMHI anteriores son de precipitación, no de Tmedia instrumental.
No confundir pruebas sintéticas aisladas de software con datos empíricos.

## Archivos de la fase 8J
- `datos/temperatura_horaria_8j/manifest.csv`, `PLANTILLA_HORAS.csv`, `README.md`: esquema y política de recepción, sin observaciones.
- `modelos/homologar_temperatura_horaria_8j.py`: motor Python de calidad horaria y espacial, sin imputaciones.
- `tests/test_homologar_temperatura_horaria_8j.py`: 15 pruebas aisladas (duplicados, UTC, calendarios, QA, altitud, distancia, permisos y SHA).
- `.github/workflows/oaf_homologacion_horaria_8j.yml`: auditoría GitHub Actions al actualizar archivos y programada día 22 de cada mes.
- `datos/homologacion_horaria_8j/estado_8j.json`, `comparaciones_horarias_8j.csv`: reportes reales, con valores no evaluables hasta recibir fuentes.
- `modelos/visor_homologacion_horaria_8j.js` e `index.html`: panel público científico en Verificación de datos, separado de 8H y 8I.
- `FASE_8J_HOMOLOGACION_HORARIA.md`: guía y fuentes WMO/SENAMHI/Copernicus.
- Flujo de CI verificado con éxito después de integración web: https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38978871058

## Reglas de ciencia aplicadas
- Fechas instrumentales explícitamente UTC y exactamente por hora; conversión local a Perú (UTC−05) antes de computar días.
- Días 24/24 horas y meses totalmente completos; sin completar datos ausentes. No estimar Tmedia desde Tmax/Tmin sin método homologado.
- Coordenadas/altitudes deben documentarse. Distancia <20 km y diferencia de altitud <200 m son **cribas administrativas**, NO pruebas suficientes de representatividad. Prohibidas correcciones genéricas automáticas por gradiente vertical.
- ERA5-Land 8D es **reanálisis**; comparar con instrumentos no equivale a evaluar habilidad pre-evento de las emisiones 8E. No publicitar alertas ENFEN/SENAMHI desde un modelo OAF aún experimental.
- Climatología histórica pública 1996–2025 y normal OMM 1991–2020 donde sea científicamente comparable.
- Fitosanidad arándano/vid y pronóstico de anomalías asociadas a El Niño Costero son líneas permanentes paralelas, con evaluación de campo e instituciones acreditadas.
- Mantener front-end amigable y desplazar detalle de metodología a **Verificación de datos**.

## Próxima Parte 8K sugerida
Desarrollar selección documental de estaciones termométricas SENAMHI y matriz estación–centro real de píxel ERA5-Land, con altitud, tipo de exposición, representatividad, fuentes y cobertura. Preparar procedimientos para obtener evidencia histórica térmica de SENAMHI y para medir sesgo espacial/estacional sin duplicar los portales de 8I/8J. No afirmar que datos 1996–2025 o series actuales SENAMHI ya se han obtenido si no están archivados.
