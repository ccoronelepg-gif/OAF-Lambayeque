# OAF-Lambayeque | Protocolo de validación externa y trazabilidad instrumental

**Fecha:** 2026-10-14  
**Ámbito:** cinco estaciones instrumentales con registros recibidos y tres productos estimados PISCOp v3.0, CHIRPS v3 y ERA5-Seamless.

## Estado de la evidencia

Se ha verificado retrospectivamente **1 109 meses-estación** de SENAMHI y **3 327 pares observación-producto** entre 1996 y 2015. Estos números describen coincidencia histórica, **no independencia estadística ni verificación instrumental para 2016–2025**.

La matriz `datos/trazabilidad_independencia_3t.csv` contiene las 15 combinaciones estación/producto con condición **no verificada**. Ninguna se debe reclasificar como independiente únicamente por una alta correlación, un MAE bajo, la distancia a otra estación o el hecho de que una estación tenga un código similar.

### Evidencia que falta para cada estación

- Código oficial asociado exactamente al TXT histórico y sus eventuales códigos anteriores.
- Nombre histórico, clase de estación, sistema de coordenadas, latitud, longitud, altitud y precisión.
- Fecha de instalación, intervalos de observación, cambios de ubicación e instrumento, alteraciones de horarios y homogeneización.
- Procedencia de datos originales (SENAMHI), control de calidad e interpretación de `-99.9` y otros valores ausentes.
- Disponibilidad real y condiciones de uso de registros 2016–2025. La ausencia de esos años en el TXT recibido no prueba el cierre de la estación.

**Atención especial:** La Viña / Jayanca, Cayaltí y Cueva Blanca tienen metadatos publicados potencialmente discordantes. No asumir equivalencia entre estación automática, convencional o pluviométrica solo por el nombre; no adoptar las coordenadas con menor MAE como prueba.

### Evidencia necesaria sobre participación en los productos

Para cada modelo y combinación estación/año:

1. Solicitar la lista de pluviómetros que aportaron datos o estadísticas climatológicas a la versión EXACTA del producto.
2. Documentar la procedencia, versión de datos, fechas y criterio de exclusión cuando se usen estaciones de evaluación.
3. Comprobar si hubo estaciones aguas arriba de la climatología/ajuste de sesgos; estar fuera de la interpolación diaria no implica independencia de todas las etapas.
4. Cuando se disponga de los datos y especificaciones apropiadas, realizar un conjunto de prueba con instrumentos excluidos de construcción y calibración para ese intervalo, idealmente de diferentes pisos altitudinales.
5. Para análisis predictivo posterior: dejar fuera periodos futuros durante el ajuste y calibración del modelo. Esta separación temporal **no elimina** la posible dependencia ya incorporada en los productos originales.

**Importante:** No se dispone todavía de una lista auditada de pertenencia de estos cinco pluviómetros a PISCOp v3 o CHIRPS v3. **0 de 15 combinaciones externas comprobadas** expresa falta de documentación; no demuestra que las 15 sean dependientes.

## Diseño de evaluación externa cuando lleguen nuevos datos

- Conservar copias inalteradas y registrar fuente, licencia, fecha y versión de cada archivo.
- Verificar identidad del instrumento y calidad de la serie diaria, convertir códigos de ausencia a NA, comprobar duplicados y calendario.
- Agregar lluvia diaria a meses solo si **todos los días exigidos por la definición de medición** tienen registros válidos; no sustituir ausencia por 0 mm.
- Muestrear cada producto en el punto o píxel correcto, documentando resolución, coordenada consultada, coordenada de celda, altitud, unidades y zona horaria/periodo.
- Emparejar únicamente meses completos y exactamente coincidentes para todas las fuentes a comparar.
- Estimar MAE, RMSE, sesgo y correlación, estratificando por costa/valle/sierra, años con El Niño y meses lluviosos; acompañar cada cifra de tamaño muestral.
- Indicar el grado de independencia **por estación y por periodo**, no por producto globalmente.
- Reportar posibles diferencias entre valores medidos y estimados y las limitaciones de representatividad de píxel.

## Requisitos mínimos antes de publicar como 'validación independiente'

**No publicado hasta cumplir todos los requisitos pertinentes:**

- [ ] Identidad y ubicación instrumental confirmadas para el periodo de estudio.
- [ ] Documentación de no participación de las estaciones en los insumos de construcción del producto evaluado.
- [ ] Solapamiento real de fechas con datos fiables, suficiente muestra y cobertura de estaciones.
- [ ] Procedimiento reproducible, con scripts y metadatos completos.
- [ ] Atribución de las fuentes, restricciones de uso y limitaciones explícitas.

## Solicitud y descarga oficial

**Solicitud preparada, no enviada:** `SOLICITUD_DATOS_SENAMHI_3R.md`.  
SENAMHI dispone de descarga de archivos meteorológicos diarios, con registro previo y contraseña personal; debe gestionarla el investigador autorizado: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos

**Documentación técnica revisada:**

- SENAMHI PISCOp v3.0 (28 de mayo de 2026): https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru
- CHIRPS3, artículo científico de 11 de abril de 2026: https://www.nature.com/articles/s41597-026-07096-4
- Bitácora y metadatos geográficos anteriores: `METADATOS_3R.md`, `ESTADO_PROYECTO.md`

## Próxima etapa

Obtener las fichas y los registros autorizados disponibles de 2016–2025; asociar códigos originales a posiciones históricas; documentar si cada estación fue o no usada por los productos; construir entonces una **validación externa verificable**, no solo retrospectiva.
