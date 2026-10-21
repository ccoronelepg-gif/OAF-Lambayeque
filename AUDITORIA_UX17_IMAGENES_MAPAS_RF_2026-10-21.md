# Auditoría UX17 OAF-Lambayeque — 21 de octubre de 2026

## Fotografías: correcciones reales

La presentación de fotografías fitosanitarias y envases pasa a object-fit: contain. Ya no se recortan los lados para llenar una tarjeta. En portada se conserva la fotografía completa, con fondo suavemente difuminado para equilibrar distintas relaciones de aspecto. Se corrigieron las miniaturas cargadas al cambiar filtros y los mensajes de error. Si una foto externa falla se muestra un SVG local rotulado como ilustración no diagnóstica, manteniendo el enlace a la fuente primaria.

Además, tres fotografías documentadas con licencia abierta fueron descargadas al repositorio y ya no dependen de servidores externos:
- Ceratitis capitata, fotografía de Daniel Feliciano, CC BY-SA 4.0, assets/fotos_cc/ceratitis_capitata_cc_by_sa.jpg. Fuente: https://commons.wikimedia.org/wiki/File:Ceratitis_capitata_-_adult.jpg
- Oídio de vid Erysiphe necator, Oliver Macdonald, CC BY-SA 3.0, assets/fotos_cc/oidio_vid_cc_by_sa.jpg. Fuente: https://commons.wikimedia.org/wiki/File:UncinulaNecatorOnGrapes.jpg
- Picudo negro de banano Cosmopolites sordidus, Obsidian Soul, CC0, assets/fotos_cc/picudo_banano_cc0.jpg. Fuente: https://commons.wikimedia.org/wiki/File:Cosmopolites_sordidus,_banana_weevil_(Mindanao,_Philippines)_01.jpg

Las demás imágenes externas pueden continuar bloqueadas por terceros; el fallback no se hace pasar por fotografía real. No se copiaron al repositorio envases comerciales sin permiso de reproducción.

## Mapas interactivos

- Fase 9K: 42 sectores experimentales, siete pisos altitudinales con colores distintos; leyenda interactiva, filtro de piso, transparencia ajustable y restablecimiento.
- Fase 10K: 39 sectores, cinco paisajes con paleta contrastada. Capas: paisaje, lluvia observada, lluvia RF, MAE RF y eventos P90. Escalas temáticas diferenciadas, valores extremos en leyenda, transparencia de polígonos, límites conmutables y centrado. No son ecorregiones oficiales MINAM ni avisos meteorológicos.

## Algoritmos RF: evaluación sin sobrepromesas

Modelo de investigación: modelos/pronostico_rf_experimental_ux15.py. Datos públicos: datos/rf_experimental_ux15.json.

Se añadió una comprobación realmente recursiva de lluvia mensual a seis meses, con modelo congelado entrenado hasta 2020 y diez orígenes (enero/julio 2021–2025) por cada localidad. No se incorporaron observaciones futuras a los retardos simulados. El usuario sigue viendo RF y climatología por separado, junto con la antelación real desde el último mes completo ERA5.

| Evaluación retrospectiva | RF MAE | Climatología MAE | Resultado |
|---|---:|---:|---|
| Día siguiente, lluvia 2025 | 2,33 mm/día | 3,06 mm/día | Mejor RF en evaluación a un paso |
| Día siguiente, Tmax 2025 | 0,83 °C | 1,00 °C | Mejor RF en evaluación a un paso |
| Mes siguiente, lluvia 2021–2025 | 44,09 mm | 42,49 mm | Mejor climatología |
| Paso recursivo 1 | 27,36 mm | 22,53 mm | Mejor climatología |
| Paso recursivo 2 | 44,96 mm | 54,72 mm | Mejor RF |
| Paso recursivo 3 | 110,50 mm | 61,32 mm | Mejor climatología |
| Paso recursivo 4 | 99,92 mm | 81,92 mm | Mejor climatología |
| Paso recursivo 5 | 15,33 mm | 12,77 mm | Mejor climatología |
| Paso recursivo 6 | 24,18 mm | 21,70 mm | Mejor climatología |

La optimización anterior redujo MAE de lluvia mensual RF de 46,93 a 44,09 mm/mes, pero el modelo todavía no supera la climatología mensual local ni muestra habilidad estable a seis meses. No se promueve su uso operativo ni se activan alertas. La serie Nov 2026–Abr 2027 parte de septiembre como último mes completo observado, por lo que abril representa el séptimo paso: fuera del diagnóstico de seis meses. Se requiere validación prospectiva as-issued, estaciones independientes, incertidumbre cuantificada y series de episodios Niño.

## Pruebas, archivos y límites

- CSS y scripts: assets/oaf-ux17-fotos-mapas.css y assets/oaf-ux17-imagenes-mapas.js.
- Mapas de paisajes: ecorregiones-clima-10k.html.
- Datos y crédito fotográfico: datos/galeria_sanidad_2026.json.
- Pruebas automatizadas: tests/test_ux17_fotos_mapa_rf.py y .github/workflows/oaf_ux17_integridad_visual.yml.
- Modelo: modelos/pronostico_rf_experimental_ux15.py y su JSON de resultados.
- Los archivos GitHub y sus pruebas no equivalen a una certificación visual en todos los navegadores. Las imágenes externas de otros orígenes pueden sufrir 403, 404 o cambios de URL.

Web: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
