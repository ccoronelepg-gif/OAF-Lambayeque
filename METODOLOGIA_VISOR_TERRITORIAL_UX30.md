# OAF-Lambayeque · UX30 — Visor territorial único con multicapas y diagnóstico

**Fecha:** 22 de octubre de 2026.  
**Módulo:** Análisis de la región → Territorio y riesgos climáticos.  
**Cambios:** mantener visible solamente el visor geográfico con árbol de capas, mapa, filtros por provincia/distrito y diagnóstico. Trasladar las fuentes y metodología al apartado «Metadatos y trazabilidad». La sección de «Escenarios de riesgo agroclimático» conserva su propio visor y no se ha convertido en una predicción hidráulica sin validación.

## Categorías del árbol de capas y su procedencia

| Grupo | Capa visible | Fuente / tipo | Qué representa |
|---|---|---|---|
| Base | Mapa base y contorno regional | OAF, límite referencial simplificado | Referencia geográfica, no límite legal |
| Base | Límite departamental | SIGRID/INEI (2013), `6020100` | Polígono político |
| Base | Límites provinciales | SIGRID/INEI (2013), `6020200` | Polígonos políticos |
| Base | Límites distritales | SIGRID/INEI (2018), `6020300` | Polígonos políticos |
| Peligro | Susceptibilidad regional a inundaciones | INGEMMET en SIGRID, `S05CP/MapServer/5010502` | Raster de susceptibilidad, NO extensión de inundación pronosticada |
| Peligro | Movimientos en masa por lluvia fuerte | CENEPRED en SIGRID, `S05CP/MapServer/5090022` | Raster de susceptibilidad |
| Peligro | Inundación fluvial histórica | INGEMMET FENC 2017, `Informacion_Complementaria/MapServer/6010100` | Puntos tipo «Inundación fluvial» |
| Peligro | Inundación pluvial histórica | INGEMMET FENC 2017, capa `6010100` | Puntos tipo «Inundación pluvial» y «Precipitación pluvial» |
| Peligro | Flujos de detritos / quebradas | INGEMMET FENC 2017, capa `6010100` | Puntos documentales |
| Peligro | Erosión fluvial | INGEMMET FENC 2017, capa `6010100` | Puntos documentales |
| Peligro | Puntos críticos por inundación | MINAM, infraestructura de riesgos, `MapServer/3` | Inventario de puntos |
| Peligro | Zonas críticas geológicas | INGEMMET/SIGRID `S05CP/MapServer/5020500` | Inventario de puntos |
| Hidrografía | Cuencas ANA | SIGRID, `Informacion_Complementaria/MapServer/6030100` | Unidades hidrográficas nivel 4 |
| Hidrografía | Ríos y drenajes | SIGRID/IGN, `Informacion_Complementaria/MapServer/6030200` | Red hidrográfica 1:100 000 |
| Hidrografía | Quebradas y cauces menores | SIGRID/IGN, `6030200` | Red hidrográfica (incluye quebradas y acequias) |
| Vías | Nacional, departamental, vecinal | MTC/IDEP, `MapServer/10,9,8` | Ejes de carreteras y caminos |
| Emergencia | Hospitales y centros o puestos de salud | IGN/IDEP, `INFRAESTRUCTURA_SOCIAL/FeatureServer/2` | Puntos referenciales |
| Emergencia | Policía / comisarías | IGN/IDEP, `FeatureServer/0` | Puntos referenciales |
| Emergencia | Compañías de bomberos | IGN/IDEP, `FeatureServer/3` | Puntos referenciales |
| Agricultura | Superficie agrícola | MINAM, `ServicioGeoINEA/MapServer/1` | Referencia cartográfica agrícola 2018 |
| Agricultura | Exposición agrícola e inundación | MINAM + IGNEMMET/SIGRID | **Coincidencia visual** entre capas, sin intersección vectorial cuantificada |
| Agricultura | Polígonos de susceptibilidad fluvial | INGEMMET, `SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0` | Polígonos de predisposición fluvial a escala 1:1 000 000; no polígonos de área inundada futura |
| Clima | Sequía/déficit hídrico y calor anómalo | Información explicativa y enlaces a SENAMHI | **Sin geometrías activas en esta fase**, por falta de capa regional auditada |

Fuentes institucionales principales:

- https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer
- https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- https://geocatmin.ingemmet.gob.pe/arcgis/rest/services/SERV_SUSCEPTIBILIDAD_INUNDACION_FLUVIAL_MIL1/MapServer/0
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

Una ficha de lectura sencilla se incorpora **por cada casilla activada**, además de un diagnóstico del ámbito territorial según provincia, distrito y cuenca. También se señalan datos faltantes, diferencias de escala, inventarios históricos y la lectura de las superposiciones. Al seleccionar puntos históricos, el diagnóstico presenta el tipo de peligro y la fecha documental.

Importante:
- Un punto histórico no equivale a la extensión de un evento.
- Los polígonos de susceptibilidad no indican las hectáreas que se inundarán en fechas futuras.
- La combinación «agricultura + susceptibilidad» es una superposición visual. No representa un cálculo de área expuesta ni daños.
- **Sequía y calor:** la casilla activa la explicación y marca la falta de una capa regional auditada, no dibuja polígonos ficticios.
- El mapa político se muestra a partir de límites INEI/SIGRID. La geometría local OAF es referencial y no reemplaza cartografía legal/catastral.

## Pruebas pendientes y observaciones

- Confirmar el funcionamiento de carga del servidor de polígonos INGEMMET, que puede fallar por tiempo de respuesta o escala de caché. Cuando una imagen externa no responde, el panel indica la limitación.
- Comprobar desde navegadores de escritorio y móvil las políticas de acceso de servicios REST y la paginación de inventarios.
- Contrastar los límites y códigos políticos según la versión y fecha de cada capa oficial.
- Evaluar futuras capas verificadas de SPI, calor anómalo y estimación de exposición agrícola **sin mezclar señales de pronóstico con peligros históricos**.
- El árbol actual usa casillas independientes de selección multicapa. El visor no está destinado a evacuaciones ni a garantizar transitabilidad o disponibilidad de atención médica.
