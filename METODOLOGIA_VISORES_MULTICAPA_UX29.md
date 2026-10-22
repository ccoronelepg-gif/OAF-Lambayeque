# OAF-Lambayeque · UX29 · Visores SIG multicapa y diagnóstico del territorio

**Fecha:** 22 de octubre de 2026  
**Secciones:** `Análisis de la región → Territorio y riesgos climáticos` y `Predicciones y anomalías → Escenarios de riesgo agroclimático`.  
**Diseño:** distribución funcional inspirada por el patrón genérico de un SIG web (árbol de capas, mapa y panel de diagnóstico), sin replicar código, imágenes o elementos propietarios de SIGRID.

## 1. Visor de territorio y riesgos

Conserva y reordena los controles que ya existen en OAF (UX24–UX28) en tres columnas:

- **CAPAS (izquierda):** susceptibilidad de inundaciones por lluvias, El Niño y movimientos en masa, inventarios georreferenciados, provincias/distritos/cuencas, superficie agrícola MINAM 2018, redes viales MTC y servicios de emergencias IGN/IDEP. Sus imágenes y registros se solicitan a los servicios cartográficos oficiales de origen. En esta versión se permite elegir un mapa raster base y superponer diferentes capas vectoriales y temáticas; dos raster de susceptibilidad superpuestos requieren considerar que sus colores pueden ocultarse parcialmente.
- **MAPA (centro):** contorno regional referencial de Lambayeque y todos los elementos geográficos habilitados, con herramientas de acercar, alejar y restablecer la extensión. Los mapas oficiales pueden tener desfases de vigencia. El mapa **no es un sistema de rutas de evacuación ni certifica transitabilidad**.
- **DIAGNÓSTICO (derecha):** interpretación que se actualiza al alternar capas y ámbito geográfico. Las fichas de puntos procedentes de los geoservicios se muestran al seleccionar sus marcadores. Se distingue riesgo, susceptibilidad, exposición y disponibilidad de datos.

Mantiene los identificadores y enlaces del portal para que la PWA y los accesos históricos funcionen.

## 2. Visor de escenarios agroclimáticos

La segunda subpestaña incorpora un visor independiente:

| Capa | Naturaleza | Fuente |
|---|---|---|
| Lluvia pronosticada a 3 o 7 días para Chiclayo, Jayanca, Motupe y Olmos | Pronóstico meteorológico externo **puntual**, sin interpolación espacial | Open-Meteo, variable diaria `precipitation_sum` |
| Susceptibilidad regional a inundaciones por lluvia fuerte | Raster histórico de predisposición física, **no predicción a una fecha** | CENEPRED/SIGRID, capa `5090024`, estudio 2021 |
| Susceptibilidad a inundaciones históricas asociadas a El Niño | Raster histórico | CENEPRED/SIGRID `5090023` |
| Susceptibilidad a movimientos en masa por lluvias fuertes | Raster histórico | CENEPRED/SIGRID `5090022` |
| Unidades hidrográficas | Polígonos obtenidos como GeoJSON desde el servidor (si está disponible) | ANA/IDEP, `FeatureServer/7` |
| Red vial nacional, departamental y vecinal | Imagen de capas oficiales, recortada al mapa regional | MTC/IDEP `MapServer/8,9,10` |
| Superficie agrícola (2018) | Imagen histórica de superficie agrícola, no cultivos específicos | MINAM `ServicioGeoINEA/MapServer/1` |

API meteorológica solicitada para cada localidad:

`https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...&daily=precipitation_sum,precipitation_probability_max&timezone=America/Lima&forecast_days=7`

Coordenadas de referencia:
- Chiclayo: -6.7714, -79.8409
- Jayanca: -6.39278, -79.8228
- Motupe: -6.15083, -79.7142
- Olmos: -5.98825, -79.74723

Las coordenadas son puntos de consulta meteorológica usados anteriormente por OAF; **no constituyen estaciones pluviométricas in situ**. Las series son pronósticos del proveedor y pueden cambiar al actualizarse.

### Umbrales ajustables

El usuario puede elegir un **umbral descriptivo** de precipitación acumulada (20, 40, 70 o 100 mm) y un horizonte de 3 o 7 días. Este umbral se utiliza **únicamente para clasificar visualmente los cuatro totales de lluvia mostrados**. **No es un umbral oficial de SENAMHI ni una probabilidad de crecida, huayco o inundación.** La lectura diagnóstica explicita este carácter hipotético.

### Incremento de caudales: restricción clave

Un pronóstico de lluvia y un mapa de susceptibilidad **no predicen automáticamente caudal, nivel de río, crecida, tiempo de traslado del pico, extensión ni profundidad de inundación**. Los modelos hidrológicos requieren precipitación por cuenca, observaciones de caudal/nivel, distribución de suelo, pendiente, infiltración y calibración. Las áreas inundables y la afectación de cultivos además requieren hidrodinámica, modelos de elevación y verificación espacial.

Por ello UX29 **no fabrica incrementos de caudal (m³/s)** ni dibuja polígonos de inundación futura. Muestra zonas susceptibles oficiales y lluvia pronosticada por localidades como **señales para orientar vigilancia y posterior investigación**. El panel de diagnóstico cambia con la selección del horizonte, el umbral, las capas y la localidad; explica las limitaciones y remite a SENAMHI, CENEPRED y fuentes OAF para consultas especializadas.

### Evaluación siguiente

1. Integrar datos históricos/operativos de caudal de estaciones ANA/SENAMHI con ubicación y periodo auditado.
2. Calibrar un modelo lluvia-escorrentía para las cuencas Chancay-Lambayeque, La Leche/Motupe y Zaña, empleando precipitación areal y observaciones de caudal suficientes.
3. Validar, con eventos independientes, los pronósticos hidrológicos y su incertidumbre; solo entonces generar escenarios de nivel, desbordamiento e inundación para áreas específicas.
4. Incorporar límites oficiales y polígonos de exposición agrícola con método de intersección reproducible.

## 3. Fuentes y trazabilidad

- CENEPRED/SIGRID: https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer
- Leyendas CENEPRED: https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/legend
- Escenarios oficiales CENEPRED: https://sigrid.cenepred.gob.pe/sigridv3/escenarios
- Metadatos ANA/IDEP: https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/FeatureServer/7
- Red vial MTC/IDEP: https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/MTC/MapServer
- Superficie agrícola MINAM: https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer
- Pronóstico externo: https://open-meteo.com/en/docs
- SENAMHI: https://www.senamhi.gob.pe/
- Análisis OAF ya existente: `assets/oaf-ux14-reorganizacion.js`, `assets/oaf-ux15-rf-salidas.js`, `assets/oaf-ux9-estructura.js`.

## 4. Revisión técnica y de usabilidad

- El visor del territorio reutiliza los módulos ya existentes, moviendo sus elementos DOM a una nueva distribución; no altera sus eventos ni fuentes.
- El visor predictivo es independiente y solicita datos meteorológicos solo al abrir la subpestaña.
- Diseño adaptable a móviles: árbol de capas vertical desplazable, mapa central y diagnóstico debajo.
- Los controles de zoom modifican el `viewBox` del SVG y no calculan métricas de ruta.
- En caso de error de CORS o indisponibilidad de un geoservicio se muestra una descripción de la limitación y enlaces a la fuente institucional.
- **Pendiente antes de validación operativa:** pruebas visuales reales en navegador, tiempos de carga, políticas CORS de los geoservicios, clasificación de riesgo/fecha y compatibilidad con caché PWA.
