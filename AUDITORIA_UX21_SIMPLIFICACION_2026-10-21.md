# OAF-Lambayeque · UX21: simplificación editorial de la web y la aplicación
Fecha: 21 de octubre de 2026.

## Correcciones solicitadas
1. Se quitaron de la cabecera los botones «Vista rápida» / «Vista técnica» y el rótulo «Localidad consultada / Cambiar zona». Los filtros locales de los módulos permanecen operativos, y la navegación de seis pestañas también.
2. Las interpretaciones se resaltan en negrita y cursiva; se corrigieron la interpretación del Niño Costero y los avisos explicativos existentes y dinámicos. La interpretación oceánica ICEN mantiene su fecha y sentido científico, sin confundir intensidad de El Niño con probabilidad de lluvias en Lambayeque.
3. «Consejo práctico» aparece en negrita. Se quitó la nota repetida sobre «Lectura orientativa elaborada por OAF...» del panel meteorológico, sin borrar las referencias instrumentales en Metadatos.
4. La sección **Ciencia de datos y agricultura de agroexportación en Lambayeque** ahora concentra: objetivo de la plataforma, fuentes verificables (ENFEN, SENAMHI, NOAA, CHIRPS, ERA5/Copernicus, Open-Meteo y CAMS), procesamiento original con Python, SIG y Random Forest, alcance experimental, límites de las predicciones y acceso a metodología. Se eliminaron de Inicio las tarjetas duplicadas de presentación y fuentes.
5. Se archivó en Metadatos el bloque duplicado de Inicio «Evolución histórica y predicciones / ¿Cómo está cambiando el clima?». No se borraron las series científicas originales.
6. En Predicciones y Anomalías se retiró la cuadrícula redundante «Predicción de noviembre de 2026 a abril de 2027, por localidad». Los mismos resultados están disponibles en el único gráfico mensual, que abre **Noviembre 2026–abril 2027** como opción preseleccionada. Continúan los filtros de localidad, variable y la opción retrospectiva por paisaje.
7. Se detallaron los objetivos, uso correcto e incertidumbre de las secciones predictivas (mapa, comparación de siete días y horizonte mensual), sin anunciar que el Random Forest sea operacional o esté validado a varios meses.
8. En cada ficha de Cultivos y Sanidad se conserva **un único enlace «Fuente fitosanitaria»**. Ya no aparecen enlaces múltiples titulados «Investigación complementaria»; las referencias completas permanecen en el archivo de datos de origen.

## Coherencia web / app
La PWA OAF App mantiene el mismo `index.html` y los mismos scripts del portal público, por lo tanto estos cambios se aplican a escritorio, teléfonos Android y iPhone. La versión de scripts se actualizó en `index.html` para evitar caché antiguo. El `sw.js` pasó a la versión de caché 3 para ofrecer actualización del contenido al abrir la aplicación. El usuario conserva su instalación y podrá actualizarla desde el aviso de la PWA.

## Código
- `index.html`: cabecera simple y presentación centralizada.
- `assets/oaf-ux-shell-2026.js`: conserva menú y localidad funcionales sin depender del antiguo conmutador.
- `assets/oaf-ux9-estructura.js`: elimina de Inicio la duplicación histórica y la mantiene en el archivo de Metadatos.
- `assets/oaf-ux9-lectura-clima.js`: resalta el consejo práctico y suprime el pie repetido de fuentes.
- `assets/oaf-ux14-reorganizacion.js`: amplía el texto explicativo de IA/RF y reduce los enlaces redundantes ENFEN.
- `assets/oaf-ux15-rf-salidas.js`: selecciona futuro por defecto y elimina la cuadrícula mensual.
- `assets/oaf-ux11-sanidad.js`: un enlace principal por organismo.
- `assets/oaf-ux21-lectura-limpia.css` y `assets/oaf-ux21-editorial.js`: estilos interpretativos y soporte de módulos dinámicos.
- `sw.js`: renovación de caché para la app instalable.

## Verificación
Se incorporaron `tests/test_ux21_limpieza.cjs` y `tests/test_ux21_browser.cjs` al flujo `.github/workflows/oaf_responsive_mobile_ux19.yml`. El último flujo comprobó correctamente en Chromium (390px y 1366px) ausencia de los elementos retirados, vista mensual preseleccionada, una fuente por ficha sanitaria, texto ENFEN en cursiva y navegación móvil. Las pruebas existentes de cinco tamaños móviles, PWA y pantalla sin conexión también terminaron correctamente.

Portal web e instalable: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
