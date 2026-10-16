# Punto de reanudación OAF-Lambayeque — 16 de octubre de 2026 · Fase 8H

**Estado actual:** Fase **8H terminada técnicamente**: auditoría documental e instrumental, georreferenciación provisional y diseño de calibración de incertidumbre. La validación instrumental de temperatura sigue **pendiente de datos SENAMHI térmicos reales**. No se calculó ni se publicó precisión ficticia.

## Archivos nuevos
- `datos/catalogo_instrumental_candidato_8h.csv`: cinco estaciones históricas de lluvia, coordenadas consultadas y alternativas provisionales, sin certificar identificación instrumental.
- `modelos/auditoria_instrumental_8h.py`: control de datos instrumentales, cobertura, localización, metadatos, estado 8G y esquema preparatorio de cuantiles conformales con guardas temporales.
- `tests/test_auditoria_instrumental_8h.py`: 11 pruebas incluyendo serie incompleta, coordenada inválida, confusión lluvia/temperatura, fuga temporal y observaciones disponibles prematuramente (datos sintéticos solo aislados).
- `.github/workflows/oaf_auditoria_8h.yml`: auditoría automática mensual y al actualizar fuentes; también valida el visor JavaScript y el DOM.
- `datos/auditoria_instrumental_8h/estado_8h.json`: estado de cobertura, preparación, requisitos y trazabilidad SHA256.
- `datos/auditoria_instrumental_8h/estaciones_8h.csv`: inventario de estaciones y distancias orientativas sin adjudicar identidad.
- `modelos/visor_auditoria_instrumental_8h.js`: módulo de consulta pública en `index.html`, pestaña Verificación de datos.
- `FASE_8H_AUDITORIA_INSTRUMENTAL.md`: fuentes SENAMHI, OMM OSCAR, Copernicus ERA5-Land, resultados científicos y próximos pasos.

## Hallazgos reales verificados
- Las series históricas SENAMHI recibidas son de **precipitación total mensual (mm), no Tmedia/Tmax/Tmin**. Por tanto no pueden verificar el modelo térmico 8E.
- **1.109 meses-estación completos de lluvia**, cinco estaciones, **79 estaciones-año completos** en 1996–2015, último año completo común 2012.
- Distribución mensual: Jayanca (La Viña) 219; Cayaltí 235; Reque 233; Lambayeque 204; Cueva Blanca 218.
- Metadatos instrumentales histórico-geográficos y equivalencias de nombres sin certificar; distancias al punto OAF solo **orientativas**.
- **0 estaciones aptas para verificación instrumental de temperatura**, 0 comparaciones instrumentales térmicas.
- 8G conserva 8 pronósticos realmente anteriores al mes objetivo y 4 estimaciones intramensuales sin contrastes posteriores todavía elegibles.
- **Intervalos 90 % NO calibrados; radio, cobertura y habilidad prospectiva pendientes.** La función de cuantiles implementada es solo un preparativo que exige emisiones premes y observaciones publicadas al menos el día 10 del siguiente mes y antes de la nueva emisión, mínimo programático 36 errores.
- Primera ejecución y última auditoría CI tras actualizar pruebas y visor completadas con **success**: https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/38974266103

## Prioridad para próxima fase 8I
1. Obtener de SENAMHI series instrumentales de temperatura (Tmax, Tmin, de preferencia Tmedia diaria u horaria) para estaciones verificadas, con códigos oficiales, lat/lon/altitud, historial de movimiento, fechas, horario y control de calidad.
2. Diseñar importación segura y con fechas de publicación, sin rellenos. No equiparar automáticamente promedio de Tmax/Tmin al promedio temporal de ERA5-Land.
3. Establecer pares mes–estación–grilla verdaderamente comparables y evaluar sesgos instrumentales vs reanálisis, separándolo de habilidad prospectiva del modelo.
4. Mantener sin alterar emisiones fechadas 8E y evaluación 8G.
5. Continúa fitosanidad arándano/vid, ENFEN y predicción de anomalías ENSO como líneas independientes.
6. Toda la información metodológica extensa permanece en **Verificación de datos**, la portada se mantiene breve.

El usuario desea que avancemos de forma ejecutiva y sin preguntas de comprobación. No afirmar que hay alertas OAF validadas sin evidencia.
