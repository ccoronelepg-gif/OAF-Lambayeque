# Fase 10O · Extensión experimental Random Forest 7 días y 6 meses

**Fecha de implementación:** 21/10/2026. **Clasificación:** Investigación y mejora continua, NO servicio operativo de pronóstico.

## Cambios de interfaz

La portada conserva la imagen del observatorio y un único recuadro de seguimiento de El Niño Costero, con intensidades probabilísticas **oceánicas** de ENFEN fechadas y enlace al comunicado. No se interpretan como probabilidades de precipitación en Lambayeque.

En Predicciones y Anomalías los paneles de referencia externa Open-Meteo y los de la salida RF propia se identifican por separado. El futuro mensual se organiza desde noviembre de 2026 hasta abril de 2027. El tablero de cinco paisajes 10K usa los datos históricos sin superposición de mapas. Las comparaciones RF/GCN originales permanecen archivadas.

## Implementación RF 10O

Código: `modelos/pronostico_rf_experimental_ux15.py`. Flujo diario: `.github/workflows/oaf_rf_experimental_ux15.yml`. Publicación del resultado con fecha y estado: `datos/rf_experimental_ux15.json`.

El candidato 10O es una **nueva extensión entrenada de la familia Random Forest**, no la promoción de los pesos previos 10K/10J. Usa **ERA5 reanálisis**, consultado mediante la API histórica de Open-Meteo, y el CSV mensual de ERA5 archivado en el OAF. Variables: precipitación y temperatura; predictores temporales y rezagos conocidos antes del periodo objetivo.

- **Semanal:** RandomForestRegressor entrenado con días históricos 2021–2024, comprobación retrospectiva 2025, reentrenamiento con días existentes y proyección autorregresiva de siete días desde el último día disponible. Serie referencia externa Open-Meteo mostrada aparte. Se registra latencia ERA5 y fechas de emisión.
- **Mensual:** RandomForestRegressor para lluvia mensual y temperatura media, con datos históricos ERA5 1996–2025 y 2026 solo si existen meses completos. Entrenamiento anterior a 2021, prueba temporal 2021–2025 y proyección autorregresiva desde el último mes completo, empezando el calendario público en noviembre de 2026.
- **Control:** el proceso conserva métrica MAE temporal, marca temporal de datos, URLs de origen, alertas deshabilitadas y etiqueta de candidato. Si faltan archivos o falla el entrenamiento, el estado es `no_disponible` y **no se publica ningún número inventado**.

**Limitación fundamental:** la validación implementada es retrospectiva a un paso, con rezagos reales en el periodo de prueba. **NO prueba la habilidad de una predicción encadenada a 7 días o 6 meses**, ni representa evaluación as-issued. Faltan comparaciones prospectivas congeladas, evaluación instrumental independiente y comprobación de utilidad superior a climatología antes de emitir alertas. Las proyecciones pueden subestimar extremos y no deben decidir por sí solas riegos, fumigaciones o acciones de emergencia.

El estado inicial de RF 10O queda publicado como `pendiente_primera_ejecucion`. El flujo GitHub Actions tiene horario diario y disparador de cambios, pero la agenda no garantiza finalización o acceso continuo a la API externa.

## Contador público de visitas

`assets/oaf-ux15-contador.js` utiliza la API documentada de CounterAPI. Si el navegador bloquea la lectura CORS, intenta una consulta JSONP **de solo lectura**. Si ambas fallan, muestra indisponibilidad sin inventar visitas. Se trata de visualizaciones, no de usuarios únicos certificados.

## Correcciones visuales

- La imagen y tarjeta ENFEN comparten fila de dos columnas proporcionadas, sin tarjeta meteorológica redundante.
- Los porcentajes conservan fecha, comentario breve, organismo y enlace.
- El resumen de IA/RF ocupa el ancho del recuadro con justificación del párrafo.
- El estado del modelo se resume a una línea; metodología específica permanece en paneles.
- El dashboard 10K independiente ya no incorpora teselas OpenStreetMap que podían superponerse; se conserva el mapa vectorial GeoJSON con filtros y sus series.
- Clima Regional y Metadatos conservan el pronóstico externo, la trazabilidad instrumental y las fuentes archivadas.

## Pendientes verificables

1. Confirmar desde GitHub Actions el estado de la primera ejecución RF 10O, los datos almacenados y MAE calculado; si falla el proveedor externo, los recuadros permanecen vacíos con razón visible.
2. Evaluación prospectiva real de 7 días y por horizonte mensual, con versiones congeladas de datos e independencia instrumental.
3. Revisar en navegador real el mapa de cinco paisajes en móvil y escritorio, la respuesta CounterAPI y la publicación GitHub Pages.
4. Actualizar automáticamente la ficha probabilística ENFEN solo después de verificar un comunicado oficial nuevo y su tabla de categorías, sin reutilizar porcentajes de meses antiguos como actualidad.
