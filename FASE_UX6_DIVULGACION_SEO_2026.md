# Fase UX-6 — Divulgación agroclimática y descubrimiento SEO
**Fecha:** 21 de octubre de 2026  
**Proyecto:** OAF-Lambayeque · Observatorio Agroclimático y Fitosanitario  
**Ámbito:** interfaz pública, explicación de datos y buscadores. No cambia modelos, series, polígonos ni evaluaciones de IA.

## Objetivo
Facilitar el uso de OAF-Lambayeque como plataforma de divulgación: productores y estudiantes deben poder entender qué representa cada variable, distinguir procedencia de datos y acceder a documentos de trazabilidad sin confundir modelos experimentales con avisos oficiales.

## Entregables realizados
1. `guia-lectura-agroclimatica.html`: nueva página independiente, con título, descripción, canonical, metadatos Open Graph, datos estructurados Article, índice temático y explicación interactiva de tipos de gráficos. Explica temperatura, lluvia, humedad relativa, VPD, viento, radiación, pronósticos externos, reanálisis, anomalías, condiciones para sanidad y limitaciones.
2. `index.html`: enlace visible a la guía desde la portada; título y metadescripción específicos para Lambayeque y la interpretación agrícola, conservando las seis rutas y todos los dashboards.
3. `assets/oaf-divulgacion-2026.css`: estilos responsivos de la invitación a la guía, sin sobrescribir los estilos de mapas ni de series meteorológicas.
4. `sitemap.xml`: nueve URLs completas que corresponden a páginas públicas independientes, sin inventar rutas `#` como páginas separadas.
5. `tests/test_divulgacion_seo_2026.py`: pruebas automatizadas para integridad de la guía, enlaces locales, título/canonical, procedencia y sitemap.
6. `.github/workflows/oaf_ux_integrity_2026.yml`: ejecuta el nuevo contrato al cambiar los archivos de divulgación.

## Precauciones científicas
- Open-Meteo, CHIRPS, ERA5 y otros productos externos se identifican como tales: no son mediciones instrumentales en parcela.
- Análisis propios y modelos predictivos del OAF siguen siendo experimentales cuando no se ha demostrado habilidad operativa.
- Un dashboard de condiciones favorables a una enfermedad no confirma presencia de patógeno ni justifica tratamientos automáticamente.
- Las zonas y paisajes experimentales de OAF no son delimitaciones oficiales MINAM.
- La guía contiene solamente ejemplos numéricos expresamente hipotéticos; no se publican valores meteorológicos falsos o sin fecha.

## Validación
El workflow UX vigente incluye pruebas de regresión de rutas, IDs originales, visores JS, fuentes, ausencia de gráficos inventados y prueba específica SEO de los archivos nuevos. La ejecución de GitHub Pages y el índice de Google son procesos distintos; el éxito del despliegue no prueba indexación ni posicionamiento.

## Acciones externas pendientes
1. Añadir la propiedad `https://ccoronelepg-gif.github.io/OAF-Lambayeque/` en Google Search Console, si el servicio admite la verificación de ese prefijo por el mecanismo disponible al propietario.
2. Inspeccionar la portada y la guía, y registrar `https://ccoronelepg-gif.github.io/OAF-Lambayeque/sitemap.xml` en Sitemaps.
3. Medir resultados reales: páginas indexadas, consultas de búsqueda, impresiones, CTR y clics orgánicos. No inventar métricas sin acceso a Search Console.
4. Seguir creando páginas de divulgación independientes con contenido útil y no duplicado, enlazadas desde la portada, y mantener todos los metadatos científicos de cada dashboard.

**Nota sobre robots.txt:** en una URL de GitHub Pages con subruta de proyecto, un robots.txt dentro de `/OAF-Lambayeque/` no equivale al archivo robots.txt en la raíz del host `ccoronelepg-gif.github.io`. Por eso no se ha publicado un robots.txt engañoso dentro del proyecto.

## Enlaces
- Sitio: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
- Guía: https://ccoronelepg-gif.github.io/OAF-Lambayeque/guia-lectura-agroclimatica.html
- Sitemap: https://ccoronelepg-gif.github.io/OAF-Lambayeque/sitemap.xml
- Repositorio: https://github.com/ccoronelepg-gif/OAF-Lambayeque
