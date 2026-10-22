# OAF-Lambayeque · UX34 — Reparación de ríos y quebradas en el visor

**Fecha:** 22 de octubre de 2026.  
**Página:** Análisis de la región → Territorio y riesgos climáticos → Cuencas, ríos y drenajes.

## Incidencia

Al marcar las casillas «Ríos y drenajes IGN» y «Quebradas y cauces estacionales IGN», no se veían trazos. Los geoservicios oficiales contienen cartografía hidrográfica IGN, pero la vista regional es más pequeña que la escala mínima de visualización del MapServer y las consultas vectoriales únicas de gran tamaño pueden superar el tiempo de respuesta o los límites del proveedor.

## Cambios

1. **Consulta espacial por sectores:** división del recuadro regional del OAF en cuatro cuadrantes. Cada categoría hidrográfica consulta sus cuadrantes con hasta **180 entidades por consulta**, evitando descargar en una respuesta miles de trazos de toda Lambayeque. Dos solicitudes simultáneas por clase; conforme llega un sector se dibuja en SVG. Las respuestas se deduplican por `objectid`. Los conteos representan solo los registros recuperados, no un inventario completo.
2. **Dos formatos compatibles:** la consulta intenta primero ArcGIS REST `f=json`, con geometrías `paths`, transformadas a GeoJSON para el renderizado SVG. Si falla, prueba `f=geojson`. Usa siempre `inSR=4326`, `outSR=4326`, la extensión del mapa y los campos oficiales `tipo`, `nombre`, `r_q_text`, `objectid`.
3. **Ríos y quebradas separados:** código `R, RN, RI, RS, AC` para ríos/acequias; `Q, Q1, QB, QQ, QI, QS` para quebradas. Las líneas se dibujan azul sólido o azul discontinuo y se rotulan con el nombre oficial cuando existe.
4. **Fuente alternativa:** si ningún cuadrante responde, se consulta `Rios Quebradas` del geoservicio de OSINERGMIN `DSGN/CARTOG/MapServer/10`. Solo se consideran trazos cuyo `RASGO_PRIN`/`RASGO_SECU` permitan reconocer inequívocamente `río` o `quebrada`. Si se usa esta alternativa, el diagnóstico debe indicar que la fuente no es el servicio IGN/SIGRID inicial.
5. **Imagen cartográfica de emergencia:** si no se obtiene geometría vectorial, el visor puede intentar una exportación de la capa SIGRID a mayor resolución para superar la restricción de escala. Las imágenes no permiten inspeccionar individualmente el nombre de un tramo.
6. **Estado y recuperación:** se muestran los recuentos recuperados, los posibles datos parciales o fallos de servidor, y un control para volver a consultar. No se dibujan ríos artificiales.

## Fuentes oficiales

- IGN/SIGRID, Red hidrográfica 1:100 000, capa 6030200:  
  https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6030200
- OSINERGMIN, Ríos y quebradas, mapa institucional, capa 10:  
  https://gisem.osinergmin.gob.pe/serverdc/rest/services/DSGN/CARTOG/MapServer/10

## Limitaciones de uso

- La cartografía cartográfica IGN es referencial y no informa caudales actuales, desbordamientos, daños ni activaciones.
- Cuando un sector devuelve 180 elementos, el visor señala que la consulta **puede estar incompleta**; no extrapola el conteo al resto del departamento.
- El servicio alternativo OSINERGMIN utiliza su propia cobertura y fecha; debe contrastarse antes de tratar los trazos como equivalentes a IGN.
- La imagen de respaldo, cuando se solicita, podría continuar vacía si el servidor oficial está caído o limita la exportación.
- **Prueba pendiente:** la compatibilidad de CORS, la transferencia de las líneas y la legibilidad visual deben comprobarse en navegadores web y PWA reales. Una comprobación de sintaxis no confirma que la capa se haya descargado correctamente.

**Código:** `assets/oaf-ux33-geocapas-etiquetas.js`, `assets/oaf-ux33-geocapas-etiquetas.css`.
