# OAF-Lambayeque · Corrección UX32 de capas geológicas, hidrografía y exposición agrícola

**Fecha:** 22 de octubre de 2026.  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos.  
**Motivo:** las casillas de inundación fluvial, pluvial, erosión, cuencas, ríos y quebradas no producían información visible en el mapa; también había dos cruces agrícolas funcionalmente idénticos.

## 1. Diagnóstico de origen

- Se usaba para **cuencas** la ruta `INFORMACION_COMPLEMENTARIA/MapServer`, que carece de la capa **6030100**. El servicio correcto que sí publica **Cuencas (6030100)** es `sigrid/Informacion_Complementaria/MapServer`. Ambas variantes de URL aparecen en SIGRID, pero no publican exactamente el mismo conjunto de capas.
- La **Red hidrográfica IGN 1:100 000 (6030200)** tiene una restricción de visualización por escala (entre 1:250 000 y 1:50 001). En la vista regional del OAF no se mostraba; aunque la casilla estuviera marcada, la exportación del mapa podía ser transparente.
- Los **puntos INGEMMET 2017 (6010100)** dependen de GeoJSON obtenido desde un servicio público externo. Un error de red o restricciones CORS pueden dejar el visor sin puntos interactivos. Se añadió una vía alternativa de **imagen ArcGIS export** con `layerDefs` para mostrar directamente las categorías de interés en el servidor oficial, sin inventar coordenadas.
- **Exposición agrícola a inundaciones** y **Áreas agrícolas en zona susceptible** activaban exactamente la misma combinación de mapas y duplicaban opciones; se unificaron.

## 2. Correcciones aplicadas

| Grupo | Antes | Ahora |
|---|---|---|
| Cuencas ANA | servicio SIGRID sin capa 6030100 | servicio oficial `sigrid/Informacion_Complementaria/MapServer/6030100` |
| Ríos y drenajes IGN | imagen sujeta a escala que no aparecía en vista regional | consulta vectorial GeoJSON de ríos/acequias; líneas SVG azules visibles a escala regional y con zoom |
| Quebradas IGN | repetía toda la red hidrográfica | consulta independiente `tipo IN ('Q','Q1','QB','QQ','QI','QS')`, líneas diferenciadas en azul claro discontinuo |
| Inundación fluvial | dependencia única de GeoJSON | puntos interactivos si se reciben + exportación filtrada `tipo_pel = 'Inundación fluvial'` cuando no se reciben |
| Inundación pluvial | dependencia única de GeoJSON | puntos interactivos + imagen filtrada por `Inundación pluvial` y `Precipitación pluvial` |
| Erosión fluvial | dependencia única de GeoJSON | puntos interactivos + imagen filtrada por `Erosión fluvial` |
| Flujos de detritos | dependencia única de GeoJSON | puntos interactivos + imagen filtrada por `Flujo de detritos y lodo` / `Flujos` |
| Agricultura | dos casillas duplicadas | una sola casilla **Superposición agrícola y susceptibilidad a inundaciones** |

Al consultar ríos y quebradas se hacen **dos solicitudes separadas**, con `resultRecordCount=2000` por clase y mensaje visible si hay truncamiento. Un inventario obtenido parcialmente **no se presenta como total regional**.

## 3. Fuentes verificadas

- **INGEMMET/SIGRID (puntos FENC 2017, ID 6010100):** https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6010100
  - `tipo_pel` incluye «Inundación fluvial», «Inundación pluvial», «Precipitación pluvial», «Erosión fluvial» y «Flujo de detritos y lodo».
  - Geometría: puntos. **No equivale a polígonos de inundación**.
- **ANA/SIGRID (cuencas, ID 6030100):** https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6030100
  - Geometría: polígonos de unidades hidrográficas, fuente ANA.
- **IGN/SIGRID (hidrografía 1:100 000, ID 6030200):** https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6030200
  - `tipo` permite diferenciar «R» (ríos) de «Q» (quebradas). Los trazos descargados en GeoJSON se dibujan por separado.
- **MINAM (superficie agrícola 2018):** https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer/1
- **CENEPRED/SIGRID (susceptibilidad regional):** https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/5010502

## 4. Semántica del visor

Cada casilla explica en el panel **Diagnóstico del territorio** el fenómeno, la fuente y su alcance. El mapa tiene un mensaje de carga para ríos, quebradas y puntos INGEMMET.

**Precauciones:**
- Una marca activa no garantiza que el proveedor remoto esté disponible; el estado del visor debe informar fallos o consultas parciales.
- El dibujo de quebradas por GeoJSON depende del servidor SIGRID y puede fallar por CORS, límites de registros o problemas de red. El OAF no genera ríos/quebradas ficticios como sustituto.
- La exportación de puntos como imagen del MapServer sirve para visualización; sin respuesta GeoJSON no habrá fichas individuales seleccionables.
- La intersección agrícola es visual y **no representa hectáreas inundadas** ni cuantificación de exposición por parcela.
- Al hacer zoom, los mapas ArcGIS exportados conservan los filtros mediante el parámetro `layerDefs`.
- La consulta hidrológica respeta una escala general de precisión IGN 1:100 000; acercar el visor no incrementa la precisión del dato fuente.

## 5. Validación pendiente

Las rutas de geoservicios, capas y sus campos se verificaron en los catálogos REST publicados, y la sintaxis del JavaScript se comprobó sobre el repositorio. **Todavía se necesita una prueba visual real en el navegador y en la PWA**, porque la carga efectiva depende de respuestas HTTP/CORS y de GitHub Pages. Cuando las consultas fallen, el visor conserva explicaciones y vínculos institucionales en lugar de inventar geometrías.
