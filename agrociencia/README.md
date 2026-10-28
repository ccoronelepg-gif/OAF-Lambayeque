# AgroCiencia Aplicada · Versión 1.6 (28 octubre 2026)

## Propósito
Herramienta consultiva de agronomía, manejo integrado, morfología de insectos, fitopatología agrícola y análisis meteorológico. Mantiene siete cultivos: mango, palto, arándano, vid, banano, café y maracuyá.

## Nuevo módulo: carrusel científico anatómico

- 11 registros fotográficos / taxonómicos del catálogo vigente.
- 71 vistas por registro: 16 referencias fotográficas **no embebidas** en el ZIP (enlazadas externamente), 54 esquemas vectoriales **originales** con estructura aislada y 1 enlace a imagen científica externa que no se reproduce por licencia.
- Fotografías reales de *Drosophila suzukii* (macho, ala, cabeza, oviscapto y SEM) de UF/IFAS con atribución explícita a Martin Hauser (California Department of Food and Agriculture). **Se enlazan desde el sitio de origen; no se copia ni redistribuye su archivo**.
- Imagen específica de cabeza de *Ceratitis capitata* (Daniel Feliciano, Wikimedia Commons). Otros registros conservan las fotografías de la versión 1.5.
- Vistas aisladas de antena, ala/élitro, cabeza, rostro, tórax, abdomen, patas y ovipositor; por estadio se excluyen órganos propios del adulto que no corresponde representar en huevos y larvas.
- Cada vista indica si es fotografía real, imagen externa no reproducida o esquema vectorial. Los esquemas muestran **morfología general, no patrones taxonómicos exactos**; no poseen escala métrica ni sirven para diagnóstico. Los dibujos vectoriales tienen código fuente en `atlas_anatomico_v16.json`.
- Carrusel con flechas y selección numérica, manejo de teclado, mensajes ante fallo de imágenes remotas, referencias individuales e indicaciones de limitación por fotografía.
- Se mantienen las herramientas de clima, MIP y fitopatología, el logo original de OAF y la información de contacto ya publicada.

## Fuentes de referencia científica

1. EPPO (2011). PM 7/104: *Ceratitis capitata*, EPPO Bulletin 41:340–346. https://doi.org/10.1111/j.1365-2338.2011.02519.x
2. Reyna-Rivera E. et al. (2026). Fruit fly species associated with orchards in Luya, Amazonas, Peru. Frontiers in Insect Science. https://doi.org/10.3389/finsc.2026.1789891
3. UF/IFAS (Mann & Stelinski). *Drosophila suzukii*: fotografías de cabeza, ala y oviscapto. https://ask.ifas.ufl.edu/publication/IN887
4. UC IPM. *Scirtothrips perseae*. https://ipm.ucanr.edu/agriculture/avocado/avocado-thrips/
5. UC IPM. *Planococcus ficus*. https://ipm.ucanr.edu/agriculture/grape/vine-mealybug/
6. ICAR–NBAIR. *Cosmopolites sordidus*, ficha morfológica. https://databases.nbair.res.in/weevils_new/notories_detail.php?id=3
7. Johnson et al. (2020). *Hypothenemus hampei*, microscopía de anatomía externa, Fig. 4. Insects 11(12), 882. https://doi.org/10.3390/insects11120882
8. Cornell / EPPO: identificación de *D. suzukii* (sexo, mancha en ala, oviscapto). https://fruit.cornell.edu/spottedwing/identification/ ; https://gd.eppo.int/taxon/DROSSU/datasheet
9. Área de Conservación Guanacaste. *Dione juno*, referencia de especie. https://www.acguanacaste.ac.cr/galeria/fotografias/programa-de-educacion-biologica/1215-i-dione-juno-i-nymphalidae

## Advertencias y límites

- **No se ha efectuado diagnóstico** de muestras de campo ni verificación de presencia actual por cultivo o zona peruana.
- El material sobre trips del palto es evidencia técnica de un organismo descrito fuera del Perú; su inclusión no afirma presencia en Perú.
- *A. fraterculus* es un complejo taxonómico; el patrón alar por sí solo puede ser insuficiente para separar morfotipos; consultar acúleo y/o evidencia molecular adecuada.
- Los materiales de EPPO indican que la identificación morfológica confiable de *C. capitata* se realiza en adultos; huevos y larvas requieren métodos de confirmación apropiados.
- Los esquemas propios son **conceptuales y anatómicos**, no reconstrucciones exactas ni micrografías; se etiquetan con claridad en la interfaz. No deben imprimirse como claves de especie.
- Los recursos fotográficos remotos requieren conexión a internet; si fallan, usar los enlaces originales. No se ha certificado cada recurso remoto en la web pública.

## Archivos

- `index.html`: web modular lista para GitHub Pages con CSS/JS externos.
- `AgroCiencia_Aplicada_v1_6_autonomo.html`: web autónoma (HTML, CSS, JavaScript y hero integrados; imágenes remotas con referencias).
- `atlas_anatomico_v16.json`: manifiesto con vistas, ilustraciones SVG y fuentes.
- `anatomia-v16.js`: controlador del carrusel y datos SVG.
- `anatomia-v16.css`: interfaz responsive y contrastes.
- `tests_v16_resultados.json`: resultados de pruebas locales con Playwright (no sustituye auditoría de imágenes remotas).
- `build_anatomy.py` y `apply_v16.py`: fuentes reproducibles para nuevos esquemas y empaquetado.

## Desarrollo / despliegue

El archivo `index.html` usa rutas relativas (CSS y JS). El HTML autónomo permite subir un solo archivo `index.html` para una página estática de GitHub Pages, sustituyendo `index.html` por el HTML autónomo completo. Asegurarse de mantener el enlace y la atribución de todas las fotografías de terceros. Mantener OAF-Lambayeque como repositorio independiente del módulo, si se crea el nuevo repo.