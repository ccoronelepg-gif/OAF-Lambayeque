# Plan de evolución UX/UI del OAF-Lambayeque — octubre de 2026

## Auditoría previa y contrato de conservación

Inventario real de `main`: **799 archivos**, aproximadamente **34,6 MB** de contenido científico y web: 123 programas Python, 46 JavaScript, 143 CSV, 190 JSON, 95 archivos comprimidos, 81 workflows, 109 Markdown, 2 HTML y 4 CSS. El sitio usa **cinco rutas principales existentes**, **463 IDs públicos sin duplicados** y **45 scripts externos** en `index.html`. El inventario de los 463 IDs y de la secuencia de scripts quedó congelado en [datos/ux_2026/auditoria_base_2026.json](datos/ux_2026/auditoria_base_2026.json). **No modificar archivos originales ni resultados científicos** en las mejoras de interfaz.

| Recurso auditado | Situación previa | Decisión |
|---|---|---|
| Inicio | Hero con fotos agrícolas, selector de 4 ciudades, 7 variables actuales externas, un texto de interpretación; resumen de fuentes; sin home fitosanitaria, ENFEN ni mapa | Conservar e incrementar; métricas cada una con fuente y fecha |
| Análisis de clima regional | API Open-Meteo y series 7 días, dashboards, anomalías, CHIRPS, clima regional, mapa DEM de 420 puntos, tres estaciones identificadas | Priorizar una vista simple de 4 gráficos y reutilizar el **único** mapa; preservar todas las analíticas |
| Monitoreo del Niño | ENFEN + modelos históricos NOAA/OAF, dashboard oceánico | Resumen ENFEN separado estrictamente del análisis OAF; **estado ENFEN actual sin boletín confirmado** según `datos/estado_enfen_3z.json` |
| Sanidad vegetal | Botrytis/arandano, oídio/vid, enfermedades, modelo horario termométrico de origen UC IPM | Resumen sin porcentajes ni diagnósticos; enlace a controles vigentes |
| Investigación y datos | Gran cantidad de bloques, tablas, archivos y documentación auditables | Índice expandible de 4 grupos y una entrada «vista técnica» al contenido **existente sin recortes** |
| Interactividad | Navegación por hash con JS inline, cambios de lugar implementados por módulos diferentes, mapa SVG basado en puntos DEM y scripts independientes | Mantener hashes, IDs y rutas; añadir coordinación ligera y menú accesible |
| Transparencia | Fuentes institucionales y muchas advertencias científicas; ENFEN no actualizado oficialmente en registro del OAF | Leyenda global de cinco niveles + tarjeta de fuentes, provenance por variable y límites visibles |

### Criterios permanentes

- Contrato: **ninguno de los 463 IDs antiguos puede desaparecer**; ninguna de las 45 rutas de scripts existentes puede desaparecer ni cambiar de orden relativo.
- Mantener los cinco `section[data-page]` y las rutas `#dashboard`, `#control`, `#riesgos`, `#prediccion`, los enlaces directos a IDs y los `details` originales.
- No alterar matrices científicas, scripts Python, modelos históricos ni umbrales científicos. Usar Open-Meteo como proveedor **externo**, CHIRPS y ERA5 como **estimaciones/reanálisis**, no estación.
- Jamás inferir ENFEN si su archivo institucional carece de estado verificado. No usar «IA» como etiqueta de un predictor sin contraste adecuado.
- Estaciones Virrey, Puchaca y El Espinal: documentos SENAMHI identifican los nombres; ubicaciones y alturas históricas tienen discrepancias. No marcar una ubicación como validada en precisión parcelaria.
- Todas las fases de UX se basan en HTML, CSS y JavaScript del navegador, sin dependencias pesadas, cookies ni necesidad de servidor distinto de GitHub Pages.

## Secuencia de implementación y aceptación

### UX-1 · Arquitectura, accesibilidad y trazabilidad
Selector **Vista rápida | Vista técnica**, menú compacto en móvil, localidad persistente visible, leyenda de confianza a mano. Garantía de retorno a secciones científicas y de hash. **Prueba:** sin scripts/IDs antiguos borrados; 5 rutas funcionales.

### UX-2 · Inicio orientado al productor
Hero exacto, selector territorial inmediatamente debajo, siete tarjetas con valor, unidad, fecha/hora y **fuente por tarjeta**. Microlectura «¿Cómo está el clima?» expresada como referencias de modelo y límites. Resumen fitosanitario arándano/vid, ENFEN/anomalías, fuente institucional no verificada si procede. **Prueba:** sin valores inventados, estados insuficientes cuando las APIs fallan.

### UX-3 · Mapa, previsión interpretativa y tecnología visible
Trasladar el mapa DEM auditado sin duplicar su ID, añadir selección de localidad y ficha del punto; cuatro gráficos independientes de 7 días (temperatura, lluvia, HR, radiación) mediante consulta real, con unidad y leyenda. Añadir Novedades verificables, fuentes y flujo `API → QA → Python → modelos experimentales → interpretación`. **Prueba:** el DEM conserva exactamente 420 puntos y el mapa funciona también en móvil.

### UX-4 · Investigación por familias, interfaz de profundidad
Cuatro grupos expandibles: Clima regional, Océano y El Niño, Sanidad vegetal, Validación científica; accesos a módulos originales y páginas existentes. Vista técnica permite explorar todo el archivo. Títulos amigables; códigos de fase únicamente como metadatos, documentación o nombres de archivo. **Prueba:** todos los paneles originales y los 45 scripts conservados.

### UX-5 · Control responsive, calidad y publicación
Usabilidad táctil, contraste, tablas con alternativa/card si aplicable, jerarquía móvil, carga de fotos, pruebas de sintaxis, test DOM ID y compatibilidad, auditoría de fuentes, GitHub Actions; después verificar estado **success** del despliegue Pages. **Prueba:** se pasa QA integral y se documentan límites no resueltos.

## Límites de verificación

GitHub Actions confirma integridad, sintaxis y estructura y GitHub Pages confirma publicación, pero **no sustituye** una prueba visual en Android real ni acredita respuestas continuas de APIs externas. La API ENFEN puede mantenerse sin información verificada por fallo de consulta institucional; la web no debe fabricar un boletín. Las categorías de anomalía (P10/P90) se exponen como escala educativa sin asignar una categoría actual cuando no existe una comparación temporal-local validada.

## Entregables

Versiones incrementales de `index.html`, CSS y JS nuevos en `assets/` y tests en `tests/`, con commits auditables y documentación técnica. Todas las referencias de fases permanecen en los documentos originales.
