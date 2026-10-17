# OAF-Lambayeque — Punto de continuación · 16/10/2026 · Fase 8M

## Estado general
La **Parte 8M** está implementada, comprobada y **COMPLETA para las cuatro localidades**, con estudio de sensibilidad de ERA5-Land a desplazamientos de los puntos OAF.

### Objetivo y diseño
- Chiclayo, Jayanca, Motupe, Olmos.
- Por localidad, **9 puntos** (centro + N, S, E, W, NE, NW, SE, SW) con desplazamientos de ±0,05° latitud/longitud.
- Periodo fijo: **1996–2025**, 30 años completos, tres bloques de diez años por localidad. **12 bloques fuente** para el estudio regional. No publicar resultados por localidad hasta que tenga sus tres bloques completos.
- Temperatura media diaria del aire a 2 m por Open-Meteo Historical Weather API, modelo `era5_land`, `cell_selection=land`, zona `America/Lima`, ajuste de elevación predeterminado. Cada JSON original archivado como `.json.gz` + `.meta.json` con URL UTC y SHA256.
- Normales y anomalías mensuales diferenciadas por coordenada sobre la base 1996–2025; comparar temperatura absoluta y anomalías frente al centro.
- NO son estaciones SENAMHI, datos de parcela, ni habilidad prospectiva 8E demostrada; NO son alertas de Niño Costero ni enfermedad.

### Resultado real final verificado (16/10/2026)
- **12 de 12 bloques históricos** originales archivados con URLs, fecha UTC y SHA-256 (tres por cada localidad).
- **36 puntos completos y 11.520 pares mensuales vecino–centro**, 2.880 comparaciones y 360 meses por localidad; `resultados_disponibles=true` indica completitud del **reanálisis histórico**, NO validación con instrumentos.
- En Chiclayo, Jayanca, Motupe y Olmos, **5 de 8** posiciones vecinas cambiaron centro de celda API.
- Chiclayo: máximo MAE temperatura por rumbo **0,59889 °C**; máximo |ΔT mensual| **1,12333 °C**; máximo MAE diferencias de anomalías **0,11058 °C**.
- Jayanca: **0,63055 °C**; **1,47500 °C**; **0,11376 °C**.
- Motupe: **0,91775 °C**; **1,46129 °C**; **0,10007 °C**.
- Olmos: **2,04997 °C**; **2,52000 °C**; **0,13105 °C**. Dirección occidental Olmos: ΔTmedia promedio ≈ **−2,04997 °C**; elevación reportada por API 554 m contra 177 m en el centro. **NO atribuir la diferencia exclusivamente a altitud/celda**, pues el proveedor también aplica ajuste de elevación.
- **Ninguno** de los contrastes constituye medición SENAMHI, diagnóstico fitosanitario ni capacidad prospectiva 8E/8G verificada.

### Bloqueo y solución
Open-Meteo devolvió inicialmente **HTTP 429** después de varias solicitudes históricas amplias (9 puntos × década). Se implementaron:
- Respeto al límite: abortar ante HTTP 429, sin peticiones de reintento compulsivas.
- **Máximo dos solicitudes nuevas por ciclo**; archivar cada fuente válida con metadatos y SHA.
- Workflow GitHub Actions **mensual** (día 25) y ante cambios de código; ya están los 12 bloques y no se vuelven a descargar fuentes válidas.
- Sin inventar observaciones; el estudio regional ya cuenta con los 12 bloques y fue cerrado con verificación automática.
- `git pull --ff-only origin main` antes de cargar fuentes para evitar conflicto binario entre ejecuciones originadas por distintas confirmaciones.
- Pruebas sintéticas aisladas y verificación automática del JS/HTML.

### Archivos del proyecto
- `modelos/sensibilidad_vecindad_8m.py` — recuperación rate-limited, QA de días, constancia de coordenadas de celda y elevación API, 360 meses por localidad, auditoría respecto de 8L y métrica 8M.
- `tests/test_sensibilidad_vecindad_8m.py` — 9 pruebas de diseño, integridad, parciales sin falso resultado, publicación exclusiva de localidad completa y conjunto regional.
- `.github/workflows/oaf_sensibilidad_vecindad_8m.yml` — auditoría mensual de las fuentes inmutables y cambios de código.
- `datos/fuentes_vecindad_8m/` — bloques originales `.json.gz`, `.meta.json` con SHA.
- `datos/sensibilidad_vecindad_8m/estado_8m.json`, `puntos_8m.csv`, `pares_mensuales_8m.csv` y `vista_8m.json`.
- `modelos/visor_vecindad_8m.js`, `index.html` — panel de ocho rumbos, tabla y gráfico de diferencias anuales en sección **Verificación de datos**.
- `FASE_8M_SENSIBILIDAD_VECINDAD.md` — informe científico completo para las cuatro localidades, con fuentes Open-Meteo/Copernicus.

### Integración y QA
Las ejecuciones sucesivas de GitHub Actions que completaron Motupe y Olmos terminaron con éxito:
- Motupe completado: https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38991508069
- Olmos completado (primer JSON malformado fue rechazado; después se recuperaron los bloques íntegros): https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38991654608

### Siguiente etapa propuesta: 8N
Aislar el efecto de downscaling de elevación del proveedor mediante un nuevo experimento reproducible, por ejemplo `elevation=nan` frente al ajuste predeterminado, con bloques climáticos completos y salvaguardas de cobertura y procedencia. Proseguir la búsqueda de datos termométricos **instrumentales** SENAMHI independientes, monitoreo ENSO/El Niño Costero con ENFEN e investigación sanitaria de arándano y vid.


Mantener los ejes ENSO/El Niño Costero, radiación, anomalías meteorológicas y fitosanidad arándano/vid. Climatología pública 1996–2025, OMM 1991–2020 comparativa. Usuario prefiere avance ejecutivo sin cuestionarios ni tareas manuales.
