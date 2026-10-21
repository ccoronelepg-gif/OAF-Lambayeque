# Corrección de imágenes en Cultivos y Sanidad — 21/10/2026

## Error identificado y reparado

El visor `assets/oaf-galeria-mecanismos-2026.js` comprobaba fotografías con un validador que solo aceptaba URLs `https://`. Al convertir fotografías abiertas a copias del mismo repositorio (`assets/fotos_cc/*.jpg`), el visor las rechazaba y construía un elemento `figure` vacío. Se añadió validación específica de rutas locales seguras y, ahora, el mismo visor puede mostrar fotografías del repositorio y URL externas.

Se comprobó la creación de las 23 fotografías de organismos mediante simulación del visor con DOM aislado: las 23 entradas producen `<img>` y coinciden con la ruta registrada. Las cuatro fotografías locales se comprobaron como archivos JPEG existentes en GitHub.

## Fotografías reales locales que ahora se muestran

- `mango-plaga-1`: mosca de la fruta (*Ceratitis capitata*), crédito Daniel Feliciano / Wikimedia Commons, CC BY-SA 4.0.
- `vid-enfermedad-1`: oídio en uva, crédito Oliver Macdonald / Wikimedia Commons, CC BY-SA 3.0.
- `banano-plaga-1`: picudo negro (*Cosmopolites sordidus*), crédito Obsidian Soul / Wikimedia Commons, CC0.
- `banano-enfermedad-1`: síntomas compatibles con marchitez por *Fusarium* en banano, crédito Scot Nelson / Wikimedia Commons, CC0. La foto **no confirma Fusarium TR4**.

## Imágenes externas y manejo de errores

Las restantes fotografías proceden de sitios técnicos, autores y fabricantes externos y pueden dejar de cargar por URL caducada, restricciones de acceso o red. El visor ahora siempre presenta una imagen de respaldo local claramente rotulada, conserva el crédito y el vínculo a la documentación de origen y evita un espacio vacío. Los productos sin fotografía comercial verificada mantienen un dibujo genérico identificado como tal: no se suplanta el envase real.

Se mantuvo `object-fit: contain` para evitar recortes de las fotografías; el módulo reconstruye solo la fotografía cuando cambia el organismo seleccionado y evita recargarla innecesariamente.

## Controles

- Código: `assets/oaf-galeria-mecanismos-2026.js`.
- Datos y atribuciones: `datos/galeria_sanidad_2026.json`.
- Prueba sin dependencias: `tests/test_sanidad_imagenes_2026.js`.
- Workflow de integridad: `.github/workflows/oaf_ux17_integridad_visual.yml`.
- Versión de caché actualizada de `index.html` para que los navegadores utilicen la corrección.

**Límite de verificación:** la comprobación de rutas y módulos del repositorio no acredita que cada servidor externo vaya a servir su fotografía a cada navegador ni que GitHub Pages haya terminado su despliegue. La vista pública se debe revisar en navegador y actualizar con Ctrl+F5 si conserva caché.
