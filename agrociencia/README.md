# AgroCiencia Aplicada · Versión 1.5

Plataforma consultiva agrícola de tema oscuro, publicada de forma separada en `/agrociencia/` del repositorio OAF-Lambayeque.

## Cambios

- Portada de manejo sanitario y tecnología: fotografía real de un dron agrícola, autor Hugonurk (CC BY-SA 4.0), desde [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:DJI_0017_HJN.jpg); no se presenta como evidencia de detección de una enfermedad. La fotografía requiere conexión.
- Sección «Manejo integrado de plagas» con **10 fichas** en siete cultivos, organizadas mediante navegación por cultivo; sin buscador interno en este apartado. El catálogo incluye insectos, ácaros y nematodos, etiquetados por grupo taxonómico; no confundirlos a todos con insectos.
- Atlas «Morfología de insectos», con **11 registros** documentales para siete cultivos, filtro por cultivo, estadio, familia y término. Fotografías reales, autor, licencia, fuente, explicación de estructuras anatómicas; incorpora microfotografías SEM originales de *Hypothenemus hampei* con rótulos anatómicos (Johnson et al., 2020).
- Nueva sección «Fitopatología agrícola» con **18 fichas** de enfermedades agrupadas en los siete cultivos; **7 referencias fotográficas específicas**, otras fichas indican expresamente que no hay fotografía validada. Fotos con créditos, enlace y breve explicación del síntoma y órgano afectado.
- Se conserva OAF Lambayeque, contacto público y observatorio.

## Rigor y limitaciones

Las imágenes son de referencia científica, no determinan una especie por sí solas, no acreditan la presencia de una plaga en Perú, no prueban un diagnóstico de campo ni autorizan aplicación de productos. Las fotografías externas pueden requerir conexión o abrirse directamente en sus fuentes por restricciones editoriales. Los créditos, licencias y URL se consignan por registro en `scientific_catalogs.json`. La ausencia de una imagen específica nunca se sustituye por una especie diferente. Algunos registros corresponden a patógenos de importancia internacional y se deben contrastar con distribución y regulación de SENASA. Para el monitoreo climático se requiere verificar la disponibilidad de Open-Meteo.

## Estructura

- `index.html` más `styles.css`, `dark-overrides.css`, `scientific-next.css`, `catalogos-v15.css`, `data.js`, `morphology.js`, `catalogos-v15.js`, `app.js` para edición modular.
- `AgroCiencia_Aplicada_v1_5_autonomo.html`: versión con estilos, lógica, SVG OAF y recursos locales insertados; usa imágenes documentales externas y API meteorológica.
- `scientific_catalogs.json`: manifiesto de los 11 registros entomológicos y enfermedades adicionales.
- `tests/test_v15.py`: prueba automatizada de navegación y filtros en escritorio y móvil con datos meteorológicos simulados.

## Instalación de GitHub Pages

En el repositorio, colocar el contenido de `index.html` autónomo bajo `/agrociencia/index.html`. No sobrescribir `/index.html` del observatorio.