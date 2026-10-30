# OAF UX51 — Implementación de recomendaciones de auditoría

**Fecha:** 29 de octubre de 2026  
**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque  
**Versión web/PWA:** UX51

## 1. Corrección del análisis parcelario

### INGEMMET
La capa 0 del servicio de susceptibilidad a inundación fluvial está publicada como **Feature Layer poligonal**. La aplicación ahora envía la geometría real de la parcela en WGS84, con geometryType=esriGeometryPolygon y spatialRel=esriSpatialRelIntersects; ya no utiliza únicamente la envolvente rectangular para seleccionar entidades.

La respuesta ArcGIS se normaliza desde anillos Esri a geometría GeoJSON. Se conservan anillos interiores y se contempla la transformación de Web Mercator a WGS84 cuando la respuesta lo requiera.

La estimación de superposición se calcula con una malla de 40 × 40 puntos interiores. Las hectáreas resultantes se identifican como **aproximadas**; no se presentan como una intersección topológica exacta.

### CENEPRED
Las capas 5090022 (movimientos en masa por lluvias fuertes) y 5090024 (inundaciones por lluvias fuertes) son **ráster**, no capas de polígonos vectoriales. Por ello, la consulta parcelaria ahora utiliza MapServer/identify con geometría multipunto y puntos muestreados dentro del polígono.

La interfaz muestra:
- Número de puntos con valores identificables y cobertura de respuesta.
- Distribución de categorías devueltas por el servicio.
- Porcentajes calculados sobre los puntos identificados, no hectáreas exactas.

Si no hay valores, el servicio falla o el navegador bloquea la petición, la interfaz no convierte el resultado en cero hectáreas ni en susceptibilidad baja.

## 2. Pronóstico agroclimático por coordenadas

El horizonte semanal de «Mi área productiva» conserva la consulta puntual Open-Meteo y amplía las variables diarias a:
- Precipitación acumulada.
- Temperatura máxima y mínima.
- Humedad relativa media.
- Radiación solar acumulada.
- Velocidad máxima del viento.
- Evapotranspiración de referencia FAO (ET₀).
- Déficit de presión de vapor máximo (DPV).

Se muestra la coordenada solicitada y, cuando el proveedor la informa, el centro de la celda meteorológica utilizada. Se advierte que el pronóstico es una salida de modelo y no una medición instrumental dentro del predio. Las variables no devueltas se muestran como ausentes, sin imputarlas.

## 3. Puerta de publicación del Random Forest

El backtest recursivo 2025 del archivo experimental contiene 52 orígenes por horizonte. En la comparación publicada:
- Lluvia: RF mejora la climatología en **2 de 7 horizontes**.
- Temperatura máxima: RF mejora la climatología en **0 de 7 horizontes**.

La gráfica semanal deja de presentar RF como una serie predictiva cuando no supera un criterio mínimo de habilidad (al menos 5/7 horizontes mejores y MAE medio inferior a la climatología). La salida se conserva en el panel de auditoría, con métricas para lluvia y temperatura.

Esta decisión no elimina el experimento ni certifica el modelo alternativo: evita presentar una serie experimental con desempeño insuficiente como pronóstico operativo. Se mantienen deshabilitadas las alertas automáticas.

## 4. PWA, caché y rendimiento

Se actualiza la versión de caché a UX51 para forzar la renovación de los módulos modificados. Se conserva la política:
- Shell, scripts y estilos estáticos: caché para disponibilidad de la aplicación.
- Pronósticos, avisos y datos científicos: consulta en red; no se reutilizan avisos antiguos como si fueran actuales.
- Imágenes de contenido: carga diferida ya aplicada; la portada mantiene carga prioritaria.
- Sin conexión: se puede recuperar la estructura de la aplicación, pero no se promete un pronóstico meteorológico actualizado.

La división adicional de los módulos GIS en paquetes bajo demanda queda como siguiente optimización; no se altera todavía porque los visores comparten dependencias de capas, puntos y estado territorial.

## 5. Pruebas incorporadas

- Regresión de geometrías GeoJSON, MultiPolygon y huecos.
- Orientación y conversión de anillos Esri.
- Construcción de consulta vectorial con polígono WGS84 real.
- Construcción de Identify multipunto para capas ráster CENEPRED.
- Clasificación y cobertura de valores ráster.
- Pronóstico puntual con tabla diaria de variables agroclimáticas.
- Puerta de habilidad del RF para lluvia y temperatura.
- Auditoría externa de metadatos, consulta vectorial e Identify multipunto.

La auditoría en vivo se conserva como artefacto de GitHub Actions. Un servicio que no responda se registra como no verificable; no se interpreta como ausencia de peligro.

## 6. Límites que permanecen

1. La capa INGEMMET es de escala 1:1 000 000; sirve como contexto regional, no como delimitación predial ni sustento de decisiones catastrales, seguros o licencias.
2. El porcentaje CENEPRED corresponde a puntos muestreados en una capa ráster. No equivale a una intersección exacta ni a hectáreas afectadas.
3. Las capas CENEPRED consultadas describen susceptibilidad cartográfica; no representan el peligro actual de un evento ni un pronóstico.
4. La consulta desde navegador puede verse afectada por CORS o indisponibilidad del servidor.
5. Open-Meteo representa una celda de modelo; no sustituye una estación meteorológica en la parcela.
6. Random Forest sigue siendo experimental. Para promoverlo se requieren predicciones archivadas antes del evento, evaluación prospectiva y observaciones independientes de SENAMHI o estaciones verificadas.

## 7. Fuentes técnicas

- CENEPRED SIGRID, servicio S05CP: https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- INGEMMET, susceptibilidad a inundación fluvial, capa 0: https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0
- Esri, operación Identify de MapServer: https://developers.arcgis.com/rest/services-reference/enterprise/identify-map-service-.htm
- Open-Meteo, documentación de pronóstico: https://open-meteo.com/en/docs
