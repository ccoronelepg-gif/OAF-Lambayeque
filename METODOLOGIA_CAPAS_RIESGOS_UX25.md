# OAF-Lambayeque · Integración de geocapas de peligros (UX25)

**Corte de implementación:** 22 de octubre de 2026  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos  
**Estado:** integración de geoservicios públicos para visualización; disponibilidad final dependiente del proveedor externo.

## Fuentes e identificadores verificables

| Institución / servicio | Identificador | Tipo de información | Fecha de referencia |
|---|---|---|---|
| CENEPRED/SIGRID — S05CP MapServer | 5090024 | Susceptibilidad a inundaciones por lluvias fuertes (raster) | Informe CENEPRED 2021 |
| CENEPRED/SIGRID — S05CP MapServer | 5090023 | Susceptibilidad a inundaciones asociadas a El Niño (raster) | Informe CENEPRED 2021 |
| CENEPRED/SIGRID — S05CP MapServer | 5010502 | Susceptibilidad regional a inundación, fuente INGEMMET (raster) | Metadatos del servicio |
| CENEPRED/SIGRID — S05CP MapServer | 5090022 | Susceptibilidad a movimientos en masa por lluvias fuertes (raster) | Metadatos del servicio |
| MINAM — caracterizacion_territorio_riesgo_desastres MapServer | 3 | Puntos críticos por inundaciones (puntos) | Fechas por registro, según fuente |
| CENEPRED/SIGRID — S05CP MapServer | 5020500 | Zonas críticas geológicas, fuente INGEMMET (puntos) | Inventario actualizado a 2022 |
| INGEMMET — Informe Técnico A7456 | Inventario 2023 | 172 zonas críticas documentadas en Lambayeque | 11/12/2023 |

Enlaces técnicos:

- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend
- https://geoservidorperu.minam.gob.pe/arcgis/rest/services/hiroambienplanificacion/caracterizacion_territorio_riesgo_desastres/MapServer/3
- https://www.gob.pe/institucion/ingemmet/noticias/879706-lambayeque-ingemmet-identifica-172-zonas-criticas-ante-el-fenomeno-el-nino
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22715 (fichas ANA 2026 como consulta complementaria; no son una geocapa incluida en el visor)

## Procedimiento geoespacial

1. Cargar la geometría del contorno referencial de Lambayeque conservada previamente en `datos/zonificacion_8n/limite_lambayeque_referencial.geojson`. El contorno es simplificado y de fuente secundaria: **no es límite oficial certificado**.
2. Calcular la extensión en coordenadas geográficas EPSG:4326 para la imagen del visor.
3. Solicitar las capas raster directamente al servicio ArcGIS REST MapServer/export, mediante `bbox`, `bboxSR=4326`, `imageSR=4326`, `layers=show:<ID>`, `transparent=true` y `f=image`.
4. Solicitar puntos de inventario mediante ArcGIS REST `/query`, con ventana geográfica, `outSR=4326` y `f=geojson`. Los datos pueden ser parciales si el servidor limita la cantidad de registros, y la carga puede fallar por CORS, cambios de servidor o cortes de red.
5. Superponer únicamente geometrías entregadas por las fuentes. El código no convierte un conteo histórico en coordenadas ni extrapola áreas de inundación.
6. Mostrar fallos de carga y vínculos a los visores originales si la red o el proveedor no responden.

## Interpretación y límites

- **Susceptibilidad no es probabilidad cuantificada ni pronóstico operativo de inundación.** Las categorías muy alta, alta, media y baja proceden de la leyenda del servidor CENEPRED; deben leerse en la fuente original.
- Un punto de inventario y un raster de susceptibilidad no son equivalentes: pueden diferir espacialmente, temporalmente y en metodología. Los registros no deben sumarse directamente con las 172 zonas críticas del informe A7456.
- La visualización no permite identificar automáticamente parcelas seguras, cuantificar daños, ni producir mapas de inundación para un episodio futuro sin modelamiento hidráulico validado.
- La geocapa se solicita al proveedor al usar el navegador. La comprobación técnica del registro y el despliegue de código GitHub no garantizan que una respuesta REST externa esté disponible en todo momento.

## Próximos pasos propuestos

- Verificar desde navegadores de escritorio y dispositivos móviles que las imágenes raster y las consultas GeoJSON se carguen con CORS y sin bloqueo del servidor.
- Incorporar el inventario 2026 de ANA mediante una fuente geográfica descargable y trazable si está públicamente disponible.
- Añadir hidrografía oficial, filtros por cuenca/provincia, polígono oficial y leyenda raster completa.
- Integrar cartografía confiable de infraestructura y cultivos, con métricas de exposición y metodología reproducible.
