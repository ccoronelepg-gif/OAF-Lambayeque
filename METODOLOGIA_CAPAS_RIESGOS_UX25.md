# OAF-Lambayeque · Integración de geocapas de peligros (UX25)

**Corte de implementación:** 22 de octubre de 2026  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos  
**Estado:** integración de geoservicios públicos para visualización; disponibilidad final dependiente del proveedor externo.

## Fuentes e identificadores verificables

| Institución / servicio | Identificador | Tipo de información | Fecha de referencia |
|---|---|---|---|
| CENEPRED/SIGRID — S05CP MapServer | 5090024 | Susceptibilidad a inundaciones por lluvias fuertes (raster) | Informe CENEPRED 2021 |
| CENEPRED/SIGRID — S05CP MapServer | 5090023 | Susceptibilidad a inundaciones asociadas a El Niño (raster) | Informe CENEPRED 2021 |
| CENEPRED/SIGRID — S05CP MapServer | 5010502 | Capa regional antigua, retirada del árbol activo UX60 | No se utiliza |
| CENEPRED/SIGRID — S05CP MapServer | 5090022 | Susceptibilidad a movimientos en masa por lluvias fuertes (raster) | Metadatos del servicio |
| MINAM — caracterizacion_territorio_riesgo_desastres MapServer | 3 | Puntos críticos por inundaciones (puntos) | Fechas por registro, según fuente |
| CENEPRED/SIGRID — S05CP MapServer | 5020500 | Zonas críticas geológicas, fuente INGEMMET (puntos) | Capa retirada del visor UX60 a solicitud de diseño |

Enlaces técnicos:

- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend
- https://geoservidorperu.minam.gob.pe/arcgis/rest/services/hiroambienplanificacion/caracterizacion_territorio_riesgo_desastres/MapServer/3
- https://www.gob.pe/institucion/ingemmet/noticias/879706-lambayeque-ingemmet-identifica-172-zonas-criticas-ante-el-fenomeno-el-nino
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22169 (estudio nacional CENEPRED 2026 actualizado con Informe Técnico N.º 69-2026/SENAMHI-DMA-SPC; incluye SHAPE descargable)
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22910 (escenario CENEPRED de lluvias octubre–diciembre 2026, basado en el Informe Técnico N.º 12-2026/SENAMHI-DMA-SVC; incluye mapa y SHAPE)
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22600 (fichas técnicas referenciales ANA 2026 para puntos críticos de Lambayeque; consulta documental, no capa vectorial validada)

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


## Actualización de capas y fuentes · UX60 (03/11/2026)

- La capa activa de susceptibilidad a inundaciones por lluvias fuertes es `5090024`; la capa para inundaciones asociadas a El Niño es `5090023`; la capa de movimientos en masa por lluvias fuertes es `5090022`. Las tres se consumen desde `S05CP/MapServer` y su cartografía tiene referencia del estudio CENEPRED 2021. La leyenda oficial clasifica susceptibilidad muy alta, alta, media y baja.
- Se retira la capa `5010502` del árbol por ser una capa regional anterior que no estaba resolviendo correctamente el caso de uso; no se debe presentar como información más reciente.
- Se retiran del árbol los puntos de zonas críticas geológicas `5020500` y los polígonos fluviales INGEMMET `MapServer/0`, evitando duplicaciones y capas que no aportan una geometría fiable en el visor actual.
- El visor incorpora la imagen satelital Esri World Imagery como referencia visual. Es un mosaico con fechas y resoluciones heterogéneas; no equivale a una imagen tomada en una fecha única ni a cartografía catastral.
- Se encontró el estudio nacional CENEPRED 2026 sobre inundaciones y movimientos en masa asociados a El Niño, actualizado con el Informe Técnico N.º 69-2026/SENAMHI-DMA-SPC. La ficha ofrece mapa, Excel y SHAPE. El SHAPE se enlaza para consulta, pero no se integra como geometría hasta validar CRS, campos, cobertura de Lambayeque y topología.
- La ANA ha publicado fichas técnicas referenciales 2026 de puntos críticos en Lambayeque. Son documentos técnicos de puntos propuestos para intervenciones preventivas; no se transforman en coordenadas inventadas ni se dibujan sin una fuente espacial validada.
- Las unidades hidrográficas se consultan desde ANA/GeoIDEP `INSTITUCIONALES/ANA_WMS/MapServer/7,8`, `Feature Layer` poligonal con referencia espacial 3857. El servicio ArcGIS exporta la imagen a la extensión geográfica del visor.

- Descarga directa del SHAPE CENEPRED OND 2026: https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_trimestral/101_shape.zip
