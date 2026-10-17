# OAF-Lambayeque — Rediseño público centrado en productores e investigación
**Fecha:** 17 de octubre de 2026 · **Estado:** implementado en `index.html`; validación automática de estructura, fuentes y JavaScript. El despliegue público depende de GitHub Pages.

## Objetivo del rediseño
Disminuir la complejidad visible sin perder ninguno de los trabajos técnicos acumulados hasta 9A. Separar **monitoreo y consulta agrícola** de **explicación académica y reproducibilidad**, distinguiendo mediciones reales de estaciones, modelos externos, reanálisis, análisis retrospectivos OAF e información oficial de ENFEN/SENAMHI.

## Navegación: cinco pestañas
1. **Inicio** — 6 indicadores agrometeorológicos en primer lugar (temperatura, lluvia, humedad relativa, déficit de presión de vapor, viento y radiación solar, con localidad seleccionable entre Chiclayo, Jayanca, Motupe y Olmos). Después: resumen narrativo corto de fuentes y fortalezas, situación ambiental/novedades verificadas desde JSON, autoría y alcance. Fuente meteorológica actual: Open-Meteo (producto externo, NO sensor).
2. **Análisis de clima regional** — clima reciente, pronóstico a 7 días, anomalías respecto a 1996–2025, dashboard con selector de variables, series históricas, mapa de **420 puntos DEM verificados** con filtro altitudinal, muestreo y zonificación 8M–8S, PM CAMS 8X–8Y, humedad/VPD 8Z. Las leyendas bajo cada gráfico diferencian datos, eje, interpretación y límites. El contorno geográfico está expresamente etiquetado como **referencial no oficial**; los estratos son puntos de muestreo, NO zonas agrícolas certificadas.
3. **Monitoreo del Niño y anomalías climáticas** — archivo ENFEN y estado de verificación, índice SST NOAA Niño 1+2 distinto de ICEN oficial, modelos oceanográficos experimentales, datos de viento, SST, corrientes e integración océano-atmósfera 8T–8V. Enlace al análisis de anomalías continentales de clima.
4. **Sanidad vegetal** — dos subpestañas. **Cultivos: arándano y vid**, con la biblioteca de 9 enfermedades, condiciones favorables y manejo integrado con referencias y registro SENASA; **Modelos predictivos de enfermedades**, con indicadores meteorológicos experimentales de Botrytis de arándano y oídio de vid y advertencias de ausencia de validación epidemiológica.
5. **Investigación y datos** — se conservaron los restantes paneles técnicos y documentación (8W, 9A, verificación SENAMHI, archivos oceánicos y climáticos) para profesionales e investigadores, descargables CSV/JSON, métodos de entrenamiento, indicadores MAE/RMSE/Brier, fuentes SHA-256 y limitaciones.

## Cambios técnicos y preservación de funcionalidad
- HTML reordenado **sin eliminar IDs críticos** de módulos y scripts históricos, navegación reducida de 7 a 5 secciones `data-page`, manteniendo enlaces internos heredados `#dashboard` → clima, `#control` → cultivos, `#riesgos` → modelos fitosanitarios, y enlaces profundos `#oaf-...` → pestaña que realmente aloja el panel, desplegándolo automáticamente.
- Archivo `assets/oaf-redesign-8f.js`: consulta Open-Meteo incluye viento y VPD; el selector de localidad del inicio comparte estado con el dashboard y, cuando corresponde, la consulta meteorológica regional. Si la API falla, los seis indicadores muestran **—**, no cifras ficticias.
- Archivo `assets/oaf-arquitectura-2026.js`: dibuja SVG de los **420 nodos DEM** reales de `datos/muestreo_8o/nodos_dem_8o.csv` y contorno regional referencial `datos/zonificacion_8n/limite_lambayeque_referencial.geojson`. Filtros de rangos 0–99, 100–299, 300–799, 800–1599, 1600–2499 y ≥2500 m. Leyenda y nota con restricciones. Los indicadores de noticias se leen directamente de los últimos archivos de estado publicitados:
    - `datos/estado_monitoreo_3z.json` para CHIRPS, últimos rasters realmente verificados y fecha de proceso.
    - `datos/estado_enfen_3z.json` para ENFEN. Ante última consulta fallida, **no afirmar estado oficial**, remitir a ENFEN.
    - `datos/aire_8x/estado_aire_8x.json` para cobertura PM, modelo CAMS y series duplicadas.
    - `datos/benchmark_9a/estado_benchmark_9a.json` para número de cortes, evaluaciones y límites de habilidad predictiva.
- **Descripción de procedencia** en Inicio: ERA5/ERA5-Land ECMWF, NOAA, CHIRPS, CAMS, Open-Meteo, boletines ENFEN/SENAMHI, bibliografía científica y SENASA. Las fuentes poseen documentación metodológica reconocida, **pero los resultados OAF no son validados automáticamente por usar esos insumos**.
- Leyendas añadidas al dashboard de 7 días, anomalias históricas y 12 módulos regionales/oceánicos/ambientales trasladados. Anotaciones recomiendan no interpretar píxeles como parcelas, ni grupos como polígonos validados, ni correlaciones como causalidad.
- Se revisó texto potencialmente obsoleto del aviso ENFEN: el comunicado N.º 17-2026 se presenta como **referencia histórica identificada al 15 de octubre**, no como el último comunicado confirmado de hoy.

## Control de calidad
`python -m unittest discover -s tests -p 'test_redisenio_oaf_2026.py' -v`: ocho pruebas que verifican el orden y número de pestañas, distribución de todos los módulos críticos, dos subpestañas de cultivos, permanencia de fuentes y descargas, 420 puntos DEM, seis indicadores de Inicio y enlaces anteriores.

`node --check assets/oaf-arquitectura-2026.js` y `node --check assets/oaf-redesign-8f.js`; asimismo se conserva `modelos/visor_benchmark_9a.js` validado.

CI: [OAF Web - Redisenio cientifico 2026](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/workflows/oaf_redisenio_web_2026.yml).

## Límites que no deben omitirse
- No convertir los productos modelados en supuestas mediciones de estaciones SENAMHI ni de hojas/frutos.
- No declarar zonas agroclimáticas homogéneas **certificadas**: hay muestreo DEM y reanálisis, pendiente de contraste instrumentado y cartografía administrativa oficial.
- No etiquetar PM CAMS como cumplimiento ECA ni como variable ya validada para 1996–2025.
- No atribuir un estado actual a ENFEN mientras el monitor automatizado no pueda confirmarlo; remitir a documentos emitidos oficialmente.
- No afirmar que el OAF ya anticipa la presencia o probabilidad de Botrytis u oídio sin datos de campo, fenología y validación.
- No equiparar el pronóstico externo de 7 días con los modelos de IA propios ni con sus hindcasts 8W/9A.

## Siguiente evolución
Mejorar progresivamente accesibilidad del mapa con versión tabular; validar el sitio visualmente en móviles y navegadores; agregar un buscador de variables dentro de Investigación y Datos; y continuar posteriormente fase 9B de incertidumbre predictiva, manteniendo el rediseño público estable.
