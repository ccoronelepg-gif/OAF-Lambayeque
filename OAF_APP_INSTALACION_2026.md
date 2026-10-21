# OAF-Lambayeque App 1.0 (PWA): versión móvil fiel al portal

**Fecha:** 21/10/2026  
**Aplicación instalable:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/  
**Código y datos:** el mismo repositorio GitHub Pages del sitio, no un clon con datos separados.

## Contenido idéntico a la web

La aplicación es una **Progressive Web App (PWA)** que abre directamente el `index.html` original del observatorio, sin eliminar ni reproducir parcialmente sus módulos. Por lo tanto mantiene las seis pestañas:

1. **Inicio:** portada, fuente ENFEN, probabilidades oceánicas fechadas, indicadores y enlaces de contexto.
2. **Clima Regional:** mapas, estaciones, pisos altitudinales, pronósticos externos y series históricas.
3. **Predicciones y Anomalías:** gráficas comparativas Open-Meteo / Random Forest, paisajes y salidas experimentales de 7 días y meses.
4. **Cultivos y Sanidad:** seis cultivos, fichas de organismos, imágenes documentadas, mecanismos de acción y MIP.
5. **Boletines oficiales:** evolución del Niño, ENFEN, SENAMHI, NOAA y fuentes verificadas.
6. **Metadatos y trazabilidad:** datasets, información instrumental, metodología, calidad y controles de modelos.

La interfaz móvil responsiva UX19 también se mantiene en la aplicación instalada. No se ha migrado a otra base de datos ni se han cambiado algoritmos de predicción, tablas o paneles.

## Instalar en Android

1. Desde **Chrome para Android**, abrir https://ccoronelepg-gif.github.io/OAF-Lambayeque/
2. Buscar la barra **«Instala OAF-Lambayeque en tu celular»**.
3. Pulsar **Instalar OAF** si Chrome ofrece la instalación; de lo contrario abrir el menú **⋮** y seleccionar **Instalar aplicación** o **Añadir a pantalla principal**.
4. Confirmar. Se mostrará el ícono **OAF** en la pantalla de aplicaciones. La aplicación abrirá el observatorio completo en ventana propia, sin barra de navegador, conservando los datos en línea.

La opción nativa de instalar depende de las políticas y compatibilidad del navegador; no se fuerza ni se simula una instalación exitosa.

## Instalar en iPhone

1. Abrir el enlace en **Safari**.
2. Tocar **Compartir** y **Añadir a pantalla de inicio**.
3. Confirmar con **Añadir**. Abrir el ícono OAF.

La interacción de instalación difiere de Android. La PWA no se presenta como aplicación App Store aprobada.

## Uso con y sin Internet

- **Con Internet:** los datos se consultan en la misma web; gráficos, modelos y las seis pestañas emplean las mismas fuentes que GitHub Pages.
- **Sin Internet:** se permite abrir la portada y recursos estáticos previamente guardados cuando están disponibles. Si no hay una pantalla local disponible, aparece `offline.html` con un aviso.
- **Nunca se cachean ni se publican como datos actuales** JSON/CSV/GeoJSON de pronósticos, boletines, estado ENFEN, datos de estaciones o modelos RF: necesitan conexión de red.
- La aplicación muestra un aviso cuando el teléfono informa que perdió la conexión. No se generan alertas locales falsas ni se solicitan permisos de GPS.
- La navegación online tiene prioridad sobre las copias locales; las imágenes y scripts estáticos se reutilizan con recarga de versiones controlada.
- **Actualizaciones:** al detectar una nueva versión del service worker, aparece un aviso para recargar a decisión del usuario. No se borra ni se interrumpe automáticamente una lectura técnica.

## Implementación

- `manifest.webmanifest`: nombre, descripción, idioma es-PE, ámbito GitHub Pages, modo standalone, cuatro accesos directos y PNG 192, 512, maskable, más SVG vectorial.
- `assets/oaf-app-icon.svg` y `assets/oaf-app-maskable.svg`: identidad de aplicación.
- `assets/oaf-app-icon-192.png`, `assets/oaf-app-icon-512.png`, `assets/oaf-app-maskable-512.png`, `assets/oaf-apple-touch-icon-180.png`: íconos reales rasterizados automáticamente por GitHub Actions.
- `assets/oaf-pwa.css`, `assets/oaf-pwa.js`: instalación opcional, aviso de red y actualización controlada.
- `sw.js`: cache local del armazón y archivos estáticos, sin interceptar servicios externos ni almacenar pronósticos o boletines vigentes.
- `offline.html`: explicación de conectividad y vigencia.
- `tests/test_pwa_ux20.cjs`, `tests/test_pwa_ux20_browser.cjs`: integridad del manifiesto y prueba móvil con Chromium.
- `.github/workflows/oaf_app_iconos_ux20.yml`: creación de íconos instalables.
- `.github/workflows/oaf_responsive_mobile_ux19.yml`: pruebas de instalación junto con las comprobaciones del diseño móvil.

## Alcance

Esta versión **sí es una aplicación web instalable**, no es aún un paquete **APK/AAB firmado** ni una publicación en **Google Play o App Store**. Para distribuir por tiendas se requiere empaquetar la PWA y cumplir con los requisitos de publicación de cada tienda, además de pruebas de calidad y privacidad.

**Límites científicos:** los modelos Random Forest son experimentales; instalar la aplicación no aumenta automáticamente su acierto ni convierte los boletines de ENFEN en avisos de emergencia propios.

## Verificación

Se preserva la estructura de seis pestañas del `index.html`. Los íconos PNG se verifican por su encabezado y tamaño. La instalación efectiva desde Chrome/Safari depende del dispositivo y navegador del usuario; una prueba de escritorio o commit exitoso no la certifica en todos los teléfonos.
