# OAF-Lambayeque · UX33: reparación vectorial, nombres y contraste

**Fecha:** 22 de octubre de 2026.  
**Sección:** Análisis de la región → Territorio y riesgos climáticos.  
**Objetivo:** remediar capas sin visualización en inundación fluvial/pluvial, erosión, ríos/quebradas, límites distritales y mejorar la lectura del territorio agrícola.

## 1. Fuentes y endpoints consultados

| Tema | Fuente | Servicio y capa | Tipo |
|---|---|---|---|
| Puntos geológicos por inundación fluvial, pluvial, erosión y flujos | INGEMMET / SIGRID | `sigrid/Informacion_Complementaria/MapServer/6010100` | Puntos 2017 con `tipo_pel` |
| Red hidrográfica | IGN / SIGRID | `sigrid/Informacion_Complementaria/MapServer/6030200` | Polilíneas `tipo`, `r_q_text`, `nombre` |
| Límites distritales | SERFOR/INEI | `Visor/Limites_Politicos_Administrativos/MapServer/2` | Polígonos `NOMBDIST`, `NOMBPROV` |
| Alternativa de límites distritales | INEI / SIGRID | `sigrid/Informacion_Complementaria/MapServer/6020300` | Polígonos `nombdist`, `nombprov` |
| Superficie agrícola | MINAM | `ServicioGeoINEA/MapServer/1` | Polígonos con `CATEGORIA`, `NOMBDIST` |

Links técnicos:

- https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6010100
- https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6030200
- https://sig.cenepred.gob.pe/sigrid/rest/services/sigrid/Informacion_Complementaria/MapServer/6020300
- https://geo.serfor.gob.pe/geoservicios/rest/services/Visor/Limites_Politicos_Administrativos/MapServer/2
- https://geoservidorperu.minam.gob.pe/arcgis/rest/services/ServicioGeoINEA/MapServer/1

## 2. Correcciones técnicas y visuales

- **Capas históricas:** la consulta GeoJSON ahora utiliza el servicio SIGRID que publica efectivamente el identificador 6010100. Se recupera geometría verdadera y se separa por el atributo `tipo_pel`. Los resultados son antecedentes documentados de 2017, no inundaciones activas.
- **Hidrografía:** consultas vectoriales independientes para ríos (`R`, `RN`, `RI`, `RS`, `AC`) y quebradas (`Q`, `Q1`, `QB`, `QQ`, `QI`, `QS`), con trayectorias SVG de distinta apariencia y nombres de `r_q_text` o `nombre` cuando constan en la fuente. La descarga de geometrías no depende del rango de escala configurado para la representación raster original, cuyo `Min Scale` es 250 000.
- **Distritos:** se consultan polígonos oficiales sin depender del umbral de escala que impide mostrar la imagen del MapServer a una extensión regional. Los límites usan línea violeta discontinua y los nombres se obtienen exclusivamente de `NOMBDIST`; los nombres provinciales se obtienen de `NOMBPROV`.
- **Puntos:** se dibujan símbolos seleccionables; si la fuente no contiene localidad, se usa el **tipo de peligro y fecha**, nunca un nombre inventado.
- **Etiquetas en el mapa:** visibles por defecto, alternables con la casilla *Mostrar nombres*. Se priorizan nombres de provincias/distritos, ríos y quebradas y registros individuales sin amontonarlos; aparecen más rótulos conforme aumenta el zoom. Su tamaño visual se adapta al acercamiento.
- **Agricultura:** se mantiene la cartografía original MINAM, pero se aplica un filtro SVG de color naranja oscuro (sin alterar coordenadas o geometrías) con opacidad alta y leyenda. Cuando el servicio devuelve etiquetas como `CATEGORIA` o `NOMBDIST`, estas pueden aparecer sobre polígonos por selección y escala. La superposición con susceptibilidad sigue siendo **visual, no un cálculo de hectáreas afectadas**.
- **Respaldo:** si fallan los servicios vectoriales, se intenta presentar la exportación de imagen oficial MapServer. En este caso no hay acceso individual a atributos ni etiquetas geográficas verificadas; el estado de consulta debe explicar la limitación.

## 3. Alcance y pruebas

La geografía no se genera sintéticamente: se carga desde fuentes oficiales en el navegador. Un proveedor con bloqueo de red, CORS o límites de peticiones puede ocasionar resultados parciales o indisponibles, lo cual se señala en pantalla. Las clasificaciones, mapas y nombres conservan su fecha y escala originales.

Los archivos HTML, JS y CSS pueden validarse estáticamente en GitHub. **El despliegue de GitHub Pages y la disponibilidad de cada petición externa todavía requieren una prueba funcional en Chrome o Safari de escritorio/móvil.**
