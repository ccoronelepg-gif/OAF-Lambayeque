# OAF-Lambayeque · UX30 — Visor territorial único con multicapas y diagnóstico

**Fecha:** 22 de octubre de 2026.  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos.  
**Cambios:** mantener visible solamente el visor geográfico con árbol de capas, mapa, filtros por provincia/distrito y diagnóstico. Trasladar las fuentes y metodología al apartado «Metadatos y trazabilidad». La sección de «Escenarios de riesgo agroclimático» conserva su propio visor y no se ha convertido en una predicción hidráulica sin validación.

## Categorías del árbol de capas y su procedencia

| Grupo | Capa visible | Fuente / tipo | Qué representa |
|---|---|---|---|
| Base | Mapa base y contorno regional | OAF, límite referencial simplificado | Referencia geográfica, no límite legal |
| Base | Imagen satelital | Esri World Imagery, MapServer/export | Mosaico satelital; la fecha y resolución varían por sector |
| Base | Límite departamental | SIGRID/INEI (2013), `6020100` | Polígono político |
| Base | Límites provinciales | SIGRID/INEI (2013), `6020200` | Polígonos políticos |
| Base | Límites distritales | SIGRID/INEI (2018), `6020300` | Polígonos políticos |
| Peligro | Susceptibilidad a inundaciones por lluvias fuertes | CENEPRED, `S05CP/MapServer/5090024` | Ráster de susceptibilidad con referencia 2021; no es inundación actual |
| Peligro | Susceptibilidad a inundaciones asociadas a El Niño | CENEPRED, `S05CP/MapServer/5090023` | Ráster de susceptibilidad con referencia 2021; no es alerta vigente |
| Peligro | Susceptibilidad a movimientos en masa por lluvias fuertes | CENEPRED, `S05CP/MapServer/5090022` | Ráster de susceptibilidad con referencia 2021; no identifica movimientos activos |
| Peligro | Inundación fluvial histórica | INGEMMET FENC 2017, `Informacion_Complementaria/MapServer/6010100` | Puntos tipo «Inundación fluvial» |
| Peligro | Inundación pluvial histórica | INGEMMET FENC 2017, capa `6010100` | Puntos tipo «Inundación pluvial» y «Precipitación pluvial» |
| Peligro | Flujos de detritos / quebradas | INGEMMET FENC 2017, capa `6010100` | Puntos documentales |
| Peligro | Erosión fluvial | INGEMMET FENC 2017, capa `6010100` | Puntos documentales |
| Peligro | Puntos críticos por inundación | MINAM, infraestructura de riesgos, `MapServer/3` | Inventario de puntos |
| Peligro | Zonas críticas geológicas | Retirada del árbol del visor UX60 | No se muestra en esta interfaz por decisión de diseño |
| Hidrografía | Cuencas ANA | ANA/GeoIDEP, `INSTITUCIONALES/ANA_WMS/MapServer/7,8` | Unidades hidrográficas poligonales; servicio espacial 3857, exportado a 4326 en el visor |
| Hidrografía | Ríos y drenajes | SIGRID/IGN, `Informacion_Complementaria/MapServer/6030200` | Red hidrográfica 1:100 000 |
| Hidrografía | Quebradas y cauces menores | SIGRID/IGN, `6030200` | Red hidrográfica (incluye quebradas y acequias) |
| Vías | Nacional, departamental, vecinal | MTC/IDEP, `MapServer/10,9,8` | Ejes de carreteras y caminos |
| Emergencia | Hospitales y centros o puestos de salud | IGN/IDEP, `INFRAESTRUCTURA_SOCIAL/FeatureServer/2` | Puntos referenciales |
| Emergencia | Policía / comisarías | IGN/IDEP, `FeatureServer/0` | Puntos referenciales |
| Emergencia | Compañías de bomberos | IGN/IDEP, `FeatureServer/3` | Puntos referenciales |
| Agricultura | Superficie agrícola | MINAM, `ServicioGeoINEA/MapServer/1` | Referencia cartográfica agrícola 2018 |
| Agricultura | Exposición agrícola e inundación | MINAM + IGNEMMET/SIGRID | **Coincidencia visual** entre capas, sin intersección vectorial cuantificada |
| Agricultura | Polígonos de susceptibilidad fluvial | Retirada del árbol UX60 | Se evita duplicar la capa regional CENEPRED y presentar una fuente antigua a escala 1:1 000 000 |
| Clima | Sequía/déficit hídrico y calor anómalo | Información explicativa y enlaces a SENAMHI | **Sin geometrías activas en esta fase**, por falta de capa regional auditada |

Fuentes institucionales principales:

- https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer
- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer/8
- https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22169 (estudio nacional CENEPRED 2026 con SHAPE descargable; referencia documental, no capa vectorial cargada)
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22910 (escenario CENEPRED de lluvias octubre–diciembre 2026, basado en el Informe Técnico N.º 12-2026/SENAMHI-DMA-SVC; incluye mapa y SHAPE)
- https://sigrid.cenepred.gob.pe/sigridv3/documento/22600 (fichas técnicas ANA 2026 de puntos críticos en Lambayeque)
- https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer
- https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer
- https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer/1
- https://www.senamhi.gob.pe/site/vigilancia-climatica/

## Navegación de mapa y adaptación móvil

- **Zoom:** rueda del ratón centrada en el puntero, botones + y – y doble clic. Los controles restablecen el ámbito regional.
- **Pan:** arrastre del mapa con ratón o dedo. Permite ampliación táctil con dos dedos.
- **Puntos:** el radio y el ancho de contorno de los símbolos se recalculan al cambiar `viewBox` con relación a la escala de ampliación; los símbolos no se agrandan artificialmente al acercarse.
- **Proyección y escala:** se mantiene el visor regional en coordenadas geográficas de las capas originales, con corrección local de escala este-oeste para el dibujo. El SVG mantiene relación de aspecto y los raster oficiales se recortan en el contorno. La precisión aparente al acercarse no mejora la resolución original de las fuentes.
- **Móvil:** árbol desplazable independiente, mapa de ancho completo y diagnóstico debajo, con texto justificado.

## Diagnóstico dinámico

Una ficha de lectura compacta se incorpora **por cada casilla activada**, además de un diagnóstico del ámbito territorial según provincia, distrito y cuenca. Se señalan fechas, fuentes, limitaciones y errores de carga. Las capas de susceptibilidad ráster 5090024, 5090023 y 5090022 tienen referencia 2021; el estudio CENEPRED 2026 y las fichas ANA 2026 se enlazan como documentación complementaria hasta validar sus geometrías descargables.

Importante:
- Un punto histórico no equivale a la extensión de un evento.
- Los polígonos de susceptibilidad no indican las hectáreas que se inundarán en fechas futuras.
- La combinación «agricultura + susceptibilidad» es una superposición visual. No representa un cálculo de área expuesta ni daños.
- **Sequía y calor:** la casilla activa la explicación y marca la falta de una capa regional auditada, no dibuja polígonos ficticios.
- El mapa político se muestra a partir de límites INEI/SIGRID. La geometría local OAF es referencial y no reemplaza cartografía legal/catastral.

## Pruebas pendientes y observaciones

- Verificar en navegador la carga de Esri World Imagery, las tres capas ráster CENEPRED y las unidades hidrográficas ANA/GeoIDEP. La disponibilidad puede variar por CORS o interrupciones del proveedor.
- Comprobar desde navegadores de escritorio y móvil las políticas de acceso de servicios REST y la paginación de inventarios.
- Contrastar los límites y códigos políticos según la versión y fecha de cada capa oficial.
- Evaluar futuras capas verificadas de SPI, calor anómalo y estimación de exposición agrícola **sin mezclar señales de pronóstico con peligros históricos**.
- El árbol actual usa casillas independientes de selección multicapa. El visor no está destinado a evacuaciones ni a garantizar transitabilidad o disponibilidad de atención médica.


## Actualización UX60 · 3 de noviembre de 2026

- Se incorpora una casilla independiente para la imagen satelital Esri World Imagery. La imagen se solicita por extensión geográfica, se recorta al contorno regional referencial y se vuelve a solicitar al cambiar el zoom. La fecha de captura no es uniforme en todo el mosaico.
- La susceptibilidad regional antigua `5010502` y los polígonos fluviales de INGEMMET a escala 1:1 000 000 dejan de usarse como capas activas. El árbol utiliza las capas CENEPRED `5090024`, `5090023` y `5090022` con su fecha de referencia 2021.
- La capa de cuencas se cambia a ANA/GeoIDEP `MapServer/7,8`, confirmada como `Feature Layer` poligonal de unidades hidrográficas.
- Los puntos INGEMMET FENC 2017 se consultan con filtro de departamento Lambayeque antes de dibujarse. Se conservan como antecedentes documentales y no como áreas de inundación.
- El diagnóstico se compacta para evitar desbordes de texto. Se eliminan controles heredados vacíos y el panel «Selecciona un punto del mapa…».
- El estudio nacional CENEPRED 2026 (actualizado con Informe Técnico N.º 69-2026/SENAMHI-DMA-SPC) y las fichas ANA 2026 de Lambayeque se enlazan como referencias más recientes. No se dibujan todavía como geometrías nuevas: su SHAPE debe someterse a validación de proyección, atributos, cobertura y topología antes de publicar una capa.

- Descarga directa del SHAPE CENEPRED OND 2026: https://sigrid.cenepred.gob.pe/sigridv3/storage/escenario_trimestral/101_shape.zip
