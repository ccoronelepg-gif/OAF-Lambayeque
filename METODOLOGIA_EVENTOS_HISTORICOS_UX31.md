# OAF-Lambayeque · UX31 — capas históricas: inundaciones, erosión, sequía y calor

**Fecha de implementación:** 22 de octubre de 2026.  
**Lugar en la web:** Análisis de la región → Territorio y riesgos climáticos → Peligros y susceptibilidad.

## 1. Inventario geológico INGEMMET 2017

**Fuente:** `https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6010100`

Capa ArcGIS REST `Puntos de control geológico`, fuente INGEMMET 2017, ámbito FENC 2017. Geometría: puntos EPSG:4326. Contiene `nom_dep`, `tipo_pel`, `fecha_doc`, `fuente`, `url` y `objectid`. El portal solicita las observaciones correspondientes a Lambayeque, clasifica `tipo_pel` y permite tres casillas independientes:

- **Inundación fluvial:** `tipo_pel` igual o equivalente a «Inundación fluvial».
- **Inundación pluvial:** incluye «Inundación pluvial» y «Precipitación pluvial».
- **Erosión fluvial:** `tipo_pel` «Erosión fluvial».

Se incluye también «flujos de detritos» cuando existan observaciones con esa clasificación. **Los puntos no delimitan la superficie inundada y no deben extrapolarse a todo el distrito.** Los conteos del visor son de registros recibidos, no totales oficiales exhaustivos.

Informe complementario INGEMMET:
https://sigrid.cenepred.gob.pe/docs/PARA%20PUBLICAR/INGEMMET/Informe_tecnico_A6766_Evaluacion_geologica_de_las_zonas_afectadas_por_el_nino_costero_Lambayeque_Cajamarca_2017.pdf

## 2. Emergencias de sequía INDECI (2003–2020)

**Fuente:** `https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/6040000`

Esta capa oficial tiene geometría de puntos y atribuciones `nom_dep`, `nom_prov`, `nom_dist`, `fecha`, `fenomeno`, `descrip` y `fuente`. El servicio documenta registros de emergencias desde 2003 hasta 2020. Se consultan los registros del departamento filtrando posibles grafías de «sequía» y se comprueba el fenómeno normalizado para evitar mezclar inundaciones u otros desastres.

**Interpretación:** el marcador representa el punto de ubicación archivado por INDECI para una emergencia reportada; **no es** la ubicación de una estación SPI ni el centro o extensión de un polígono de sequía. Tampoco representa la sequía vigente en 2026. Cuando la respuesta sea vacía o el proveedor falle, no se crean registros sintéticos.

Para análisis espacial continuo de sequía, SENAMHI publica el índice SPI basado en PISCO:
https://www.senamhi.gob.pe/main.php?dp=lambayeque&p=sequias

Como antecedente regional verificable, el boletín SPI de noviembre de 2024 identifica condiciones normales a secas en sectores de la sierra norte, incluidos sectores de Lambayeque, **sin atribuir un valor específico a distritos o parcelas**:
https://www.senamhi.gob.pe/load/file/02243SENA-68.pdf

## 3. Calor histórico SENAMHI

**Punto histórico incorporado (GeoJSON):** `datos/riesgos_ux31/calor_historico_senamhi_lambayeque.geojson`

Estación **Jayanca–La Viña**: el boletín de SENAMHI de marzo de 2024 documentó 37,8 °C el **18 de marzo de 2024** y una anomalía media mensual de temperaturas máximas de **+2,9 °C**. Son dos magnitudes diferentes (máxima diaria y anomalía mensual).

- Boletín SENAMHI: https://www.senamhi.gob.pe/load/file/02221SENA-134.pdf
- Reporte histórico con coordenadas de estación Jayanca: https://www.senamhi.gob.pe/load/file/02245SENA-5.pdf
- Coordenadas utilizadas: **longitud −79.779°, latitud −6.322°**, según este reporte.

**Área histórica de referencia:** WMS de SENAMHI IDESEP `Frecuencia Olas de Calor · Verano`, servicio:
`https://idesep.senamhi.gob.pe/geoserver/g_01_06/wms`, capa:
`g_01_06:01_06_001_03_001_512_0000_00_00`.

Catálogo oficial:
https://idesep.senamhi.gob.pe/portalidesep/wms.do

La capa se solicita como WMS 1.1.1, EPSG:4326, imagen transparente. **La extensión de color del WMS muestra una frecuencia histórica estacional según los metadatos del producto, no las áreas alcanzadas por la anomalía de marzo de 2024.** La interpretación depende de la simbología del proveedor; no se extraen valores numéricos de píxeles de imagen.

El servicio WMS puede no responder por mantenimiento, restricciones de acceso o cambios de URL. En ese caso permanece el punto histórico con respaldo documental, si el sitio puede descargar su GeoJSON.

## 4. Interacción con filtros y mapa

Los registros puntuales usan exactamente las coordenadas publicadas o incorporadas de fuentes documentales, se muestran solamente si el usuario activa su casilla, y se ocultan fuera de los polígonos elegidos por provincia, distrito o cuenca cuando esos filtros están disponibles.

La ficha del **Diagnóstico del territorio** muestra el tipo de evento, fecha/período, fuente original y explicación de su alcance. Los símbolos ajustan el radio visual durante el zoom de mapa. Las imágenes WMS y ArcGIS se pueden solicitar para la extensión visible a mayor detalle tras hacer zoom.

## 5. Distinciones científicas

- **Puntos de emergencia ≠ área afectada**.
- **Inventario histórico ≠ predicción futura**.
- **Frecuencia histórica de olas de calor ≠ anomalía de un episodio puntual**.
- **Sequía meteorológica SPI ≠ emergencia de sequía registrada por INDECI**.
- Se respeta la temporalidad de cada archivo: INGEMMET 2017; INDECI 2003–2020; SENAMHI marzo 2024 y WMS estacional.
- No se atribuye a un departamento entero la medición de una estación ni se inventan polígonos de sequía sin geometría oficial.

## 6. Control de calidad pendiente

Se verificó el esquema publicado de las capas SIGRID/INDECI y los datos bibliográficos del SENAMHI. Está pendiente probar **en un navegador real** la consulta GeoJSON, la respuesta CORS, disponibilidad del WMS y coincidencia de símbolos con el mapa, especialmente cuando la PWA utiliza caché. Si el servicio devuelve error o ningún registro, la interfaz informa esa situación, en lugar de dibujar puntos no comprobados.
