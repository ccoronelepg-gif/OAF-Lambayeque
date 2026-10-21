# OAF-Lambayeque · Adaptación a celulares UX19

Fecha: 21 de octubre de 2026.

## Objetivo

Que las seis pestañas principales del Observatorio Agroclimático y Fitosanitario sean utilizables en teléfonos pequeños, teléfonos medianos y tabletas sin ocultar información científica, cifras o procedencia de datos.

## Ajustes incorporados

**Menú y encabezado.** A anchuras de 700 píxeles o menos se muestra el botón táctil de menú (alto mínimo 44 px). Las seis pestañas se abren en un menú desplegable de una o dos columnas; al seleccionar una se cierra el menú, conservando el enrutamiento por anclas. Permanecen los botones Vista rápida y Vista técnica. Encabezado fijo con contexto regional visible sin cubrir el contenido.

**Inicio.** Fotografía completa y tarjeta ENFEN dispuestas verticalmente en móviles; proporción fotográfica 16:9. Las probabilidades del Niño Costero mantienen sus fuentes y distinción entre intensidad oceánica y efectos sobre precipitaciones.

**Clima Regional.** Paneles en una columna, mapas escalables, leyendas que se ajustan de línea, filtros táctiles sin controles cortados y tablas meteorológicas desplazables.

**Cultivos y Sanidad.** Fotografías reales o respaldos ilustrativos completos con `object-fit: contain`, fichas y cuadros sin superposiciones y selectores de cultivo, plaga, enfermedad y localidad ocupando todo el ancho móvil. La corrección anterior de cuatro imágenes locales se mantiene.

**Predicciones y Anomalías.** Se conservan los dos gráficos RF / Open-Meteo y las comparaciones de climatología. En teléfonos, los gráficos grandes se pueden desplazar horizontalmente sin reducir los rótulos a tamaños ilegibles. Selector de localidad y variable en una columna. Las seis fichas mensuales se reorganizan en dos columnas o una para pantallas muy estrechas. No se modifica el modelo ni se inventa un pronóstico.

**Boletines y Metadatos.** Tablas científicas de cuatro o más columnas se mantienen completas dentro de un contenedor de desplazamiento horizontal. Los bloques de fuentes y documentos se presentan en una columna.

**Mapa de paisajes 10K.** Vista de una columna bajo 760 px; el contenedor cartográfico responde al ancho del teléfono, mantiene filtros de cinco paisajes y leyendas cromáticas y recalcula el tamaño Leaflet al cambiar el tamaño/orientación. Los polígonos siguen siendo exploratorios y no ecorregiones oficiales.

## Archivos

- `assets/oaf-responsive-celulares-ux19.css`: última hoja de estilos, gana prioridad sobre estilos heredados de fases anteriores.
- `assets/oaf-responsive-celulares-ux19.js`: accesibilidad de navegación, desplazamiento táctil de gráficas/tablas y módulos cargados dinámicamente.
- `index.html`: incorpora ambos recursos con versión anticaché.
- `ecorregiones-clima-10k.html`: comportamiento móvil del visor independiente.
- `tests/test_movil_ux19.js`: prueba estática sin dependencias de seis pestañas, mapas, selectores y llaves CSS.
- `tests/test_movil_ux19_browser.cjs`: prueba con Chromium en tamaños 320, 375, 390, 430 y 768 px.
- `.github/workflows/oaf_responsive_mobile_ux19.yml`: prueba de navegador y capturas en GitHub Actions, bajo el artefacto `oaf-mobile-ux19-screenshots`.
- `.github/workflows/oaf_ux17_integridad_visual.yml`: añade el control estático de UX19 a las pruebas generales.

## Cómo verificar

1. Abrir desde el celular https://ccoronelepg-gif.github.io/OAF-Lambayeque/
2. Usar **☰ Menú** y alternar entre Clima Regional, Cultivos y Sanidad, Predicciones y Anomalías, Boletines y Metadatos.
3. En gráficos de siete días o mensuales, deslizar dentro del gráfico hacia los lados (no toda la página). Las etiquetas y leyendas deben permanecer disponibles.
4. Revisar las cuatro fotografías del repositorio en Cultivos y Sanidad, tanto vertical como horizontal.
5. Abrir https://ccoronelepg-gif.github.io/OAF-Lambayeque/ecorregiones-clima-10k.html y girar el celular para comprobar que el mapa reajusta su superficie.
6. Si se conserva una versión antigua de la página, recargar o abrir en pestaña privada.

**Verificación honesta:** se comprobó estáticamente la estructura del CSS/JS, su inclusión en HTML y las seis pestañas. El flujo Chromium permite pruebas reales y conserva capturas; no afirmar que cada navegador o dispositivo fue inspeccionado visualmente antes de contar con sus resultados.
