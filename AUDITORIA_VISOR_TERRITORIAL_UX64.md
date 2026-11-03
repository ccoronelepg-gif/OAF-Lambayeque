# Auditoría del visor territorial · UX64

**Fecha:** 03/11/2026  
**Repositorio:** https://github.com/ccoronelepg-gif/OAF-Lambayeque  
**Portal:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/

## Correcciones aplicadas

1. **Ruta canónica SIGRID/CENEPRED.** Se sustituyó la ruta anterior `/sigrid/Informacion_Complementaria/MapServer` por la ruta oficial publicada `/INFORMACION_COMPLEMENTARIA/MapServer` en los módulos UX30, UX33 y UX35. La corrección cubre límites INEI, red hidrográfica IGN, puntos geológicos INGEMMET FENC 2017 y emergencias históricas INDECI 2003–2020.
2. **Caché de PWA.** El service worker ahora busca primero los recursos precargados del shell con `ignoreSearch:true`, para que los parámetros `?v=` usados por el HTML no impidan recuperar recursos sin conexión. La actualización de red continúa activa.
3. **Versionado.** Los módulos territoriales UX30/UX33/UX35 y las cachés PWA se actualizaron a UX64.
4. **Prueba de regresión.** Se incorporó `tests/auditoria_ux64_sigrid.cjs`, que valida metadatos de seis capas y la estructura de respuesta de consultas para puntos históricos, ríos, distritos y emergencias.

## Fuentes oficiales contrastadas

- CENEPRED/SIGRID, capas ráster 2021: inundación por lluvias fuertes (5090024), inundación asociada a eventos El Niño (5090023) y movimientos en masa (5090022): https://sig.cenepred.gob.pe/sigrid/rest/services/S05CP/MapServer/layers
- CENEPRED/SIGRID, catálogo de información complementaria: https://sig.cenepred.gob.pe/sigrid/rest/services/INFORMACION_COMPLEMENTARIA/MapServer/layers
- ANA/GeoIDEP, unidades hidrográficas, capa 8 (Feature Layer poligonal): https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/ANA_WMS/MapServer/8
- IGN/IDEP, infraestructura social: comisarías (0), salud (2) y bomberos (3): https://www.idep.gob.pe/geoportal/rest/services/INSTITUCIONALES/INFRAESTRUCTURA_SOCIAL/FeatureServer

## Comprobaciones realizadas en esta revisión

- Sintaxis JavaScript: correcta en UX30, UX33, UX35, `sw.js` y el nuevo script de auditoría.
- Consistencia de rutas: no quedan referencias a la ruta antigua en los módulos territoriales revisados.
- Versionado HTML: UX30, UX33 y UX35 referencian UX64.
- PWA: cachés RELEASE/STATIC UX64 y búsqueda de recursos precargados independiente de `?v=`.
- Catálogos oficiales: se verificó que los identificadores y tipos de las capas CENEPRED, ANA e infraestructura social corresponden a las descripciones publicadas por los organismos.

## Pendiente antes de declarar estable

**El visor todavía no debe etiquetarse como estable.** En este entorno no se pudo ejecutar un navegador real contra GitHub Pages ni lanzar la prueba de consultas desde Node con acceso de red. Por tanto, quedan pendientes:

1. Ejecutar `node tests/auditoria_ux64_sigrid.cjs` desde un entorno con acceso a Internet y revisar los conteos/errores devueltos por cada geoservicio.
2. Abrir el portal publicado y comprobar visualmente cada capa activada por separado y en combinación: límites, satélite Esri, CENEPRED, INGEMMET, ANA, ríos/quebradas, MTC y servicios de emergencia.
3. Comprobar filtros de provincia/distrito/cuenca, selección de puntos, zoom, arrastre y gestos táctiles.
4. Repetir la comprobación en móvil y verificar instalación, actualización y uso sin conexión de la PWA.
5. Confirmar que las capas se ajustan a la extensión regional y no quedan desplazadas por diferencias de CRS o deformación de escala.

Las capas de susceptibilidad continúan siendo cartografía de predisposición, no pronósticos de inundación ni modelos hidráulicos. Los inventarios de 2017 y 2003–2020 son históricos. No se deben interpretar como peligros activos o riesgo cero.

**Criterio de cierre:** declarar estabilidad únicamente después de completar los cinco puntos pendientes y conservar evidencia de las respuestas de servicios y capturas de navegador.
