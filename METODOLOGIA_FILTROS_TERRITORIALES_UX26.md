# OAF-Lambayeque · UX26 — filtros territoriales y superficie agrícola

**Corte:** 22 de octubre de 2026.  
**Alcance:** visor `Análisis de la región → Territorio y riesgos climáticos`.  
**Estado:** código de consulta y visualización integrado al sitio y a la PWA; carga efectiva sujeta a accesibilidad de geoservicios oficiales y políticas CORS.

## Capas geoespaciales empleadas

| Dato | Institución | Servicio / capa | Campos de filtrado |
|---|---|---|---|
| Provincias | SERFOR/INEI | `Visor/Limites_Politicos_Administrativos/MapServer/1` | `IDDPTO=14`, `IDPROV`, `NOMBPROV` |
| Distritos | SERFOR/INEI | `Visor/Limites_Politicos_Administrativos/MapServer/2` | `IDDPTO=14`, `IDPROV`, `IDDIST`, `NOMBDIST` |
| Unidades hidrográficas | ANA, publicada en IDEP | `INSTITUCIONALES/ANA_WMS/FeatureServer/7` | `CODIGO`, `NOMBRE`, intersección con envolvente regional |
| Superficie agrícola nacional | MINAM | `ServicioGeoINEA/MapServer/1` | cartografía pública de superficie agrícola, referencia 2018 |

Enlaces de consulta:
- https://geo.serfor.gob.pe/geoservicios/rest/services/Visor/Limites_Politicos_Administrativos/MapServer/1
- https://geo.serfor.gob.pe/geoservicios/rest/services/Visor/Limites_Politicos_Administrativos/MapServer/2
- https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/FeatureServer/7
- https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer/1
- https://github.com/ccoronelepg-gif/OAF-Lambayeque/blob/main/METODOLOGIA_CAPAS_RIESGOS_UX25.md

## Comportamiento del visor

1. Consulta geocapas oficiales en formato GeoJSON desde ArcGIS REST; solicita coordenadas EPSG:4326 y simplificación de aproximadamente 0,001° **solo para lectura regional**, no para catastro ni medición parcelaria.
2. El filtro de distrito se actualiza según la provincia seleccionada. El filtro de cuenca o unidad hidrográfica ANA se puede combinar espacialmente con la división política.
3. Superpone contornos seleccionados, recorta visualmente las imágenes de susceptibilidad y de superficie agrícola y oculta puntos de inventarios fuera de los polígonos elegidos.
4. Presenta recuentos de **puntos cargados por las consultas web** que caen dentro del filtro, sin confundirlos con total de puntos críticos verificados para el departamento.
5. Se puede alternar una capa visual de superficie agrícola MINAM (2018). Se mantiene en estado inactivo hasta que el usuario la active.
6. Cuando un proveedor bloquea CORS, no responde o limita resultados, la interfaz informa la falta de datos y ofrece el acceso a su geoservicio.

## Límites científicos y estadísticos

- El cruce **visual** entre superficie agrícola y susceptibilidad no es una estimación de hectáreas afectadas, severidad de daños ni probabilidad de inundación. Para métricas de exposición hay que trabajar con geometrías vectoriales completas y una metodología reproducible de intersección espacial.
- Los límites simplificados pueden excluir o incluir puntos situados cerca de sus bordes. El filtro no debe utilizarse para decisiones catastrales, parcelarias o delimitaciones legales.
- Una unidad hidrográfica ANA puede extenderse fuera de Lambayeque. Su selección refleja una intersección geográfica; no necesariamente una cuenca completa situada dentro de la región.
- La capa de superficie agrícola nacional de referencia 2018 no identifica qué cultivo ocupa actualmente cada parcela ni cuantifica la superficie cosechada.
- Las colecciones de puntos descargadas pueden estar limitadas por el máximo de registros o disponibilidad del proveedor. Por ello los conteos del visor son **conteos de registros cargados**, no totales oficiales.
- La implementación se verificó en GitHub (estructura, sintaxis) pero es necesario realizar pruebas de cargas de imagen, CORS, geocapas y rendimiento en navegadores reales antes de considerarla validada operativamente.

## Validación siguiente

- Probar desde navegadores de escritorio y móviles la consulta en los tres geoservicios, el rendimiento y los cambios de selección.
- Verificar códigos de provincia y distrito, extensiones hidrográficas y bordes de polígonos frente a SIG institucional.
- Descargar una versión aprobada y reproducible de geometrías de exposición agrícola; calcular intersecciones vectoriales con escalas y errores documentados.
- Incorporar hidrografía, líneas de quebradas, drenajes y posibles escenarios hidráulicos, siempre con trazabilidad.
