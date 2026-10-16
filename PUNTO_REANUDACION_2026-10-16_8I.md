# Punto de continuidad OAF-Lambayeque · 16/10/2026 · Fase 8I

## Estado de trabajo
**Parte 8I implementada:** importación controlada de temperaturas instrumentales SENAMHI, homologación diaria/mensual, contraste descriptivo con ERA5-Land y panel público dentro de **Verificación de datos**.

**HALLAZGO:** no se han cargado al repositorio archivos instrumentales Tmedia SENAMHI autorizados. El motor informa **0 archivos, 0 meses homologados, 0 pares estación–reanálisis, métricas nulas**. Esto es correcto y no debe reemplazarse por datos ficticios. Las cinco series SENAMHI previas son de **lluvia 1996–2015**, no temperatura. No declarar validación prospectiva del modelo 8E.

## Archivos de fase 8I
- `datos/temperatura_senamhi_8i/manifest.csv`: encabezados de metadatos y fuentes, vacío hasta recibir datos documentados.
- `datos/temperatura_senamhi_8i/PLANTILLA_DATOS_DIARIOS.csv`: solo encabezados diarios; no registros inventados.
- `datos/temperatura_senamhi_8i/README.md`: requisitos de autorización, procedencia y métodos de temperatura.
- `modelos/homologar_temperatura_senamhi_8i.py`: validación de origen SHA256, permisos, formatos, huso horario, integridad diaria, QA, códigos, geografía, meses completos y diferencias estación–ERA5-Land 8D.
- `tests/test_homologar_temperatura_8i.py`: catorce pruebas, incluidas pruebas sintéticas aisladas (no publicadas como evidencia).
- `.github/workflows/oaf_temperatura_instrumental_8i.yml`: CI con tests, verificación del visor y actualización mensual día 21 o al cambiar fuentes.
- `datos/homologacion_temperatura_8i/estado_8i.json` y `datos/homologacion_temperatura_8i/comparacion_mensual_8i.csv`: informes reales; 0 pares, nulos hasta recibir datos.
- `modelos/visor_homologacion_temperatura_8i.js` y `index.html`: visualización pública en acordeón 8I dentro de Verificación de datos.
- `FASE_8I_HOMOLOGACION_TEMPERATURA.md`: protocolo completo y fuentes institucionales.
- Primera CI automatizada de homologación: success. Segundo CI tras integrar panel web: **success**, ver https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38975904573

## Reglas científicas
1. **No** deducir Tmedia de lluvia, ni equiparar automáticamente media (Tmax+Tmin)/2 con Tmedia horaria de ERA5-Land.
2. Exigir **todos los días calendario** de Tmedia con QA aprobada, fecha y procedencia de publicación verificable, SHA, permisos adecuados para publicar datos derivados, método documentado, identificación de estación y geografía corroborada.
3. La criba espacial provisional de 20 km **no garantiza** representatividad, similar altitud ni independencia de producto. La correspondencia es descriptiva.
4. Separar **ERA5-Land reanálisis vs estación SENAMHI** de **error prospectivo del modelo OAF 8E**, que continúa en 8G. Nunca sobreescribir emisiones 8E.
5. Conservar climatología pública 1996–2025 y periodo OMM 1991–2020 cuando exista cobertura, sin recalibración con años futuros.
6. Fitosanidad arándano/vid, fenómeno El Niño Costero y modelos de anomalías climáticas continúan como trabajos paralelos independientes.
7. Revisar siempre registro y etiquetas SENASA actuales para recomendaciones de fungicidas; no inducir aplicaciones químicas desde anomalías sin diagnóstico de campo.

## Siguiente fase sugerida: 8J
Instrumentar la **homologación horaria de Tmedia**, enriquecimiento de metadatos espaciales y de altitud, identificación de estaciones SENAMHI disponibles y evaluación de dependencia reanálisis–instrumento. Diseño estadístico de sesgo y calibración temporal de intervalos solo cuando existan suficientes observaciones válidas. Mantener toda la documentación técnica en «Verificación de datos», no saturar inicio.

Usuario desea avance ejecutivo sin cuestionarios ni tareas manuales. No pedirle que ejecute código.
