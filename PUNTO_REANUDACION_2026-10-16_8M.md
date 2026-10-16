# OAF-Lambayeque — Punto de continuación · 16/10/2026 · Fase 8M

## Estado general
La **Parte 8M** está implementada técnicamente y publicada como etapa **incremental, regional todavía en curso**, con estudio de sensibilidad de ERA5-Land a desplazamientos de los puntos OAF.

### Objetivo y diseño
- Chiclayo, Jayanca, Motupe, Olmos.
- Por localidad, **9 puntos** (centro + N, S, E, W, NE, NW, SE, SW) con desplazamientos de ±0,05° latitud/longitud.
- Periodo fijo: **1996–2025**, 30 años completos, tres bloques de diez años por localidad. **12 bloques fuente** para el estudio regional. No publicar resultados por localidad hasta que tenga sus tres bloques completos.
- Temperatura media diaria del aire a 2 m por Open-Meteo Historical Weather API, modelo `era5_land`, `cell_selection=land`, zona `America/Lima`, ajuste de elevación predeterminado. Cada JSON original archivado como `.json.gz` + `.meta.json` con URL UTC y SHA256.
- Normales y anomalías mensuales diferenciadas por coordenada sobre la base 1996–2025; comparar temperatura absoluta y anomalías frente al centro.
- NO son estaciones SENAMHI, datos de parcela, ni habilidad prospectiva 8E demostrada; NO son alertas de Niño Costero ni enfermedad.

### Resultado real verificado en primer corte
- **6 de 12 bloques** con respuestas completas archivadas: Chiclayo tres décadas, Jayanca tres décadas.
- **18 puntos completos** y **5.760 pares mensuales vecino–centro** entre Chiclayo y Jayanca, 360 meses por punto.
- Chiclayo: **5 de 8** vecinos seleccionaron celda diferente; máximo MAE de Tmedia por rumbo **0,59889 °C**; mayor |ΔT mensual| **1,12333 °C**; máximo MAE de Δ anomalía **0,11058 °C**.
- Jayanca: **5 de 8** vecinos cambiaron celda; máximo MAE de Tmedia por rumbo **0,63055 °C**; mayor |ΔT mensual| **1,47500 °C**; máximo MAE de Δ anomalía **0,11376 °C**.
- En puntos que mantienen la misma celda Open-Meteo también pueden aparecer diferencias pequeñas de Tmedia, porque la API ajusta por elevación: NO atribuir diferencias exclusivamente a cambio de píxel ni a altitud física sin aislamiento experimental.
- **Motupe y Olmos PENDIENTES**; el informe regional mantiene `resultados_disponibles=false` aunque permite mostrar localidades con 360 meses completos.

### Bloqueo y solución
Open-Meteo devolvió inicialmente **HTTP 429** después de varias solicitudes históricas amplias (9 puntos × década). Se implementaron:
- Respeto al límite: abortar ante HTTP 429, sin peticiones de reintento compulsivas.
- **Máximo dos solicitudes nuevas por ciclo**; archivar cada fuente válida con metadatos y SHA.
- Workflow GitHub Actions diario (aproximadamente 09:27 hora de Perú) y ante cambios de código; no descargar si las 12 fuentes ya están.
- Sin inventar observaciones y sin presentar resultados regionales hasta contar con los 12 bloques.
- `git pull --ff-only origin main` antes de cargar fuentes para evitar conflicto binario entre ejecuciones originadas por distintas confirmaciones.
- Pruebas sintéticas aisladas y verificación automática del JS/HTML.

### Archivos del proyecto
- `modelos/sensibilidad_vecindad_8m.py` — recuperación rate-limited, QA de días, constancia de coordenadas de celda y elevación API, 360 meses por localidad, auditoría respecto de 8L y métrica 8M.
- `tests/test_sensibilidad_vecindad_8m.py` — 9 pruebas de diseño, integridad, parciales sin falso resultado, publicación exclusiva de localidad completa y conjunto regional.
- `.github/workflows/oaf_sensibilidad_vecindad_8m.yml` — revisión diaria y autocaptura segura.
- `datos/fuentes_vecindad_8m/` — bloques originales `.json.gz`, `.meta.json` con SHA.
- `datos/sensibilidad_vecindad_8m/estado_8m.json`, `puntos_8m.csv`, `pares_mensuales_8m.csv` y `vista_8m.json`.
- `modelos/visor_vecindad_8m.js`, `index.html` — panel de ocho rumbos, tabla y gráfico de diferencias anuales en sección **Verificación de datos**.
- `FASE_8M_SENSIBILIDAD_VECINDAD.md` — informe científico con datos iniciales y vínculos Open-Meteo/Copernicus.

### Integración y QA
La ejecución exitosa con resultados de dos localidades es:
https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38982675161

### Siguiente paso inmediato
**Completar automáticamente Motupe y Olmos** cuando el proveedor permita descargar los seis bloques faltantes; verificar que se obtienen los 36 puntos y 11.520 pares mensuales de vecinos, actualizar el informe científico y el panel 8M. Una vez completo, considerar fase **8N** para aislar el efecto de `elevation=nan` frente a elevación predeterminada y medir sesgos atribuibles al procedimiento de downscaling, siempre con pruebas temporales y sin inventar sensores reales.

Mantener los ejes ENSO/El Niño Costero, radiación, anomalías meteorológicas y fitosanidad arándano/vid. Climatología pública 1996–2025, OMM 1991–2020 comparativa. Usuario prefiere avance ejecutivo sin cuestionarios ni tareas manuales.
