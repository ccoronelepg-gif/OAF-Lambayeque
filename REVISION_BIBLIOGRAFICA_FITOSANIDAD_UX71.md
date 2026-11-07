# OAF Lambayeque | Validación científica y bibliográfica, fase UX71
**Corte:** 6 de noviembre de 2026  
**Origen:** `datos/sanidad_agroexportadora_2026.json`, `datos/validacion_cientifica_fitosanidad_ux70.json`, `datos/fitosanitario_modelos_ux69.json`.  
**Producto:** [matriz de validación estructurada](datos/bibliografia_validada_fitosanidad_ux71.json), con trazabilidad por ID de cada ficha.

## 1. Propósito y límites de la validación

Se revisaron **las 23 asociaciones cultivo–plaga/enfermedad de los seis cultivos publicados**, y las fuentes específicas usadas para cada una. Se seleccionaron **35 referencias** de SENASA, INIA, repositorios universitarios, UC IPM y revistas indexadas, incluidas publicaciones de 2023–2026. Las fuentes más antiguas se conservan cuando son documentos originales relevantes, no porque cumplan un requisito de actualidad. Las referencias fueron contrastadas mediante su página editorial, resumen, DOI o metadatos publicados; **no se han leído íntegramente todos los textos ni auditado los especímenes de herbario/colecciones**. No se ha revisado independientemente el texto completo de cada informe PDF. Por tanto esto es **validación documental de pertinencia** y no una revisión sistemática PRISMA o confirmación de laboratorio.

Una publicación que acredita un organismo sobre un hospedante en una región distinta de Lambayeque **no demuestra ocurrencia regional**, mucho menos riesgo actual a nivel de distrito/parcela. Dos pares tienen evidencia relacionada con Lambayeque: **moscas de la fruta en mango como grupo**, documentadas por SENASA, y **Fusarium spp. de muestras de maracuyá**, investigadas por UNPRG. Esa evidencia es específica al alcance descrito, no a todos los organismos ni a cada distrito.

### Inventario comprobado

| Elemento | Cantidad | Significado |
|---|---:|---|
| Cultivos principales de Sanidad | 6 | Mango, vid, arándano, palto, maracuyá y banano |
| Fichas originales | 23 | 12 fichas de plagas y 11 de enfermedades |
| Fuentes bibliográficas seleccionadas | 35 | Mezcla deliberada de artículos, tesis, guías y fuentes oficiales: **no** 35 ensayos locales |
| Asociación con evidencia de grupo regional SENASA | 1 | Mango / moscas de la fruta, no identificación específica de todas las capturas |
| Estudios con muestras de Lambayeque | 1 | Maracuyá / Fusarium, tesis UNPRG |
| Evidencia del hospedante en otras regiones del Perú | 9 | No equivale a registro en Lambayeque |
| Evidencia solo internacional en esta selección | 10 | Transposición requiere verificación |
| Evidencia nacional general, sin localidad | 1 | Guía técnica, no vigilancia local |
| Evidencia directa insuficiente para la ficha actual | 1 | Palto / queresas y ácaros agrupados |
| Riesgos fitosanitarios localmente calibrados | 0 | Ninguna de las 23 fichas dispone de modelo regional validado |
| Productos con registro/etiqueta confirmada en el archivo | 0 de 31 | No se ha autorizado ninguno por esta auditoría |

*Estas categorías miden procedencia y pertinencia documental, no calidad Q1/Q2, eficacia comercial, daño regional ni nivel de riesgo.*

## 2. Matriz íntegra de correspondencia bibliográfica (23 fichas)

| Nº | Cultivo | Ficha OAF | Organismo(s) declarados | Procedencia de evidencia | Fuentes específicas |
|---:|---|---|---|---|---|
| 1 | Mango | Moscas de la fruta | Ceratitis capitata y Anastrepha spp. | SENASA Lambayeque; grupo | [SENASA-MANGO-2025](#ref-senasa-mango-2025), [SENASA-MANGO-2021](#ref-senasa-mango-2021), [RICALDE-2012](#ref-ricalde-2012) |
| 2 | Mango | Cochinillas o queresas | Diversas especies de hemípteros | Literatura/guía externa | [MANGO-SCALE-2023](#ref-mango-scale-2023) |
| 3 | Mango | Antracnosis | Colletotrichum spp. | Perú, otro ámbito | [MANGO-ANTH-PERU-2023](#ref-mango-anth-peru-2023), [MANGO-ANTH-2025](#ref-mango-anth-2025) |
| 4 | Vid | Cochinilla harinosa de la vid | Planococcus ficus y Pseudococcus spp. | Literatura/guía externa | [GRAPE-MEALY-2024](#ref-grape-mealy-2024), [GRAPE-PSEUD](#ref-grape-pseud) |
| 5 | Vid | Trips y ácaros | Diversos Thysanoptera y Acari | Literatura/guía externa | [GRAPE-THRIPS](#ref-grape-thrips), [GRAPE-MITES](#ref-grape-mites) |
| 6 | Vid | Oídio | Erysiphe necator | Literatura/guía externa | [GRAPE-PM](#ref-grape-pm), [GRAPE-PM-MODEL](#ref-grape-pm-model) |
| 7 | Vid | Botrytis del racimo | Botrytis cinerea | Literatura/guía externa | [GRAPE-BOT](#ref-grape-bot) |
| 8 | Arándano | Trips | Frankliniella spp. y Thrips spp. | Perú, otro ámbito | [INIA-BLUEBERRY-2020](#ref-inia-blueberry-2020) |
| 9 | Arándano | Mosca blanca y cochinillas | Bemisia tabaci y pseudocóccidos | Perú, otro ámbito | [INIA-BLUEBERRY-2020](#ref-inia-blueberry-2020) |
| 10 | Arándano | Moho gris | Botrytis cinerea | Perú, otro ámbito | [INIA-BLUEBERRY-2020](#ref-inia-blueberry-2020), [BOT-GENERAL](#ref-bot-general), [BOT-REVIEW-2024](#ref-bot-review-2024) |
| 11 | Arándano | Pudrición radicular | Phytophthora cinnamomi | Perú, otro ámbito | [INIA-BLUEBERRY-2020](#ref-inia-blueberry-2020), [AVOCADO-PHYTO](#ref-avocado-phyto) |
| 12 | Palto | Trips | Diversas especies de trips | Literatura/guía externa | [AVOCADO-THRIPS](#ref-avocado-thrips) |
| 13 | Palto | Queresas y ácaros | Hemípteros fitófagos y ácaros | Evidencia directa insuficiente | [AVOCADO-PERSEA](#ref-avocado-persea) |
| 14 | Palto | Tristeza / pudrición de raíces | Phytophthora cinnamomi | Literatura/guía externa | [AVOCADO-PHYTO](#ref-avocado-phyto) |
| 15 | Palto | Muerte regresiva | Lasiodiplodia theobromae (según diagnóstico) | Perú, otro ámbito | [AVOCADO-LASIO-2026](#ref-avocado-lasio-2026) |
| 16 | Maracuyá | Mosca del ovario | Dasiops spp. | Perú, otro ámbito | [DASIOPS-MARACUYA-2026](#ref-dasiops-maracuya-2026), [DASIOPS-GRANADILLA-2022](#ref-dasiops-granadilla-2022) |
| 17 | Maracuyá | Gusano defoliador | Dione juno y Agraulis spp. | Guía técnica Perú | [MARACUYA-INIA](#ref-maracuya-inia) |
| 18 | Maracuyá | Antracnosis | Colletotrichum spp. | Literatura/guía externa | [MARACUYA-ANTH-2025](#ref-maracuya-anth-2025), [MARACUYA-REVIEW-2023](#ref-maracuya-review-2023) |
| 19 | Maracuyá | Marchitez / secadera | Fusarium spp. (confirmar aislamiento) | Tesis UNPRG; muestras | [MARACUYA-FUS-2025](#ref-maracuya-fus-2025) |
| 20 | Banano | Picudo negro | Cosmopolites sordidus | Perú, otro ámbito | [BANANA-PICUDO](#ref-banana-picudo) |
| 21 | Banano | Nematodos fitoparásitos | Radopholus similis y otros nematodos | Literatura/guía externa | [BANANA-NEMA-2024](#ref-banana-nema-2024) |
| 22 | Banano | Fusariosis Raza 4 Tropical | Fusarium oxysporum f. sp. cubense R4T | Perú, otro ámbito | [BANANA-TR4-EPPO](#ref-banana-tr4-eppo), [BANANA-TR4-SENASA](#ref-banana-tr4-senasa) |
| 23 | Banano | Sigatoka negra | Pseudocercospora fijiensis | Literatura/guía externa | [SIGATOKA-2025](#ref-sigatoka-2025), [SIGATOKA-2023](#ref-sigatoka-2023) |

## 3. Interpretación crítica por cultivo

### Mango

- **Moscas de la fruta:** SENASA informó el trabajo de control en Motupe, Jayanca, Olmos y Zaña (2025), pero no atribuye los conteos a una sola especie. Mantener la ficha como grupo y separar *Ceratitis capitata* de *Anastrepha* spp. para cualquier ecuación. El estudio de Ricalde et al. (2012) es de poblaciones de Brasil, no Lambayeque.
- **Antracnosis:** sustituir las noticias sobre mosca de la fruta, que son fuentes no pertinentes al patógeno, por el primer registro peruano de *Colletotrichum asianum* sobre mango (2023, Amazonas) y el estudio 2025 del complejo de *Colletotrichum* en mango. No convertir estudios de otros territorios en detecciones de Lambayeque.
- **Queresas y cochinillas:** hay publicaciones de la queresa blanca *Aulacaspis tubercularis* sobre mango en África, pero esa especie no está identificada en las fichas de Lambayeque. Conservar el nivel de grupo y requerir identificación taxonómica antes de recomendar umbrales.

### Vid

- **Cochinillas:** UC IPM diferencia *Planococcus ficus* de *Pseudococcus* spp. y no son intercambiables en monitoreo/modelado.
- **Trips y ácaros:** son órdenes/grupos diferentes. Sus muestreos, enemigos naturales y factores de riesgo deben tratarse por separado.
- **Oídio:** *Erysiphe necator* es el organismo correcto en la web. El antiguo modelo de UC IPM está archivado y exige validación local; se requieren temperatura horaria en la zona del racimo y fenología. *Plasmopara viticola*, presente como pendiente de módulo C, no figura entre las 23 fichas.
- **Botrytis del racimo:** humedad libre, temperatura y floración/envero; el proxy >90 % HR del aire de arándano no es un modelo de racimos.

### Arándano

- **Plagas:** el informe INIA 2020 de Huaral enumera trips, mosca blanca y pseudocóccidos; no sustenta especies aisladas ni incidencias de Lambayeque. Deben separarse *Bemisia* y cochinillas.
- **Moho gris:** *Botrytis cinerea* está documentado. La regla experimental HR del aire >90% durante ≥6 h procede de una guía general y no mide humedad foliar de flores o frutos; sin observaciones locales no es probabilidad de infección.
- **Pudrición de raíz:** *Phytophthora cinnamomi* es un oomiceto. La guía de palto se usa como referencia ecobiológica del suelo y no como evidencia de eficacia de un modelo para arándano.

### Palto

- **Trips:** la guía UC IPM es para *Scirtothrips perseae* en California; no autoriza llamarlo especie confirmada en Perú. La ficha actual solo indica 'diversas especies'.
- **Queresas/ácaros:** solo se documentó específicamente un ejemplo de ácaro de palto en la revisión; ninguna especie de queresa fue confirmada. No debe etiquetarse el conjunto como especie ya validada.
- **Pudrición radical:** *Phytophthora cinnamomi*, oomiceto, requiere humedad y drenaje del suelo, riego y diagnóstico de raíces; no sirve un indicador basado solo en HR 2 m.
- **Muerte regresiva:** Llanos et al. (2026) estudiaron múltiples especies de *Lasiodiplodia* en pudrición peduncular y cancro de ramas del palto peruano. El hallazgo no significa que todos los síntomas de muerte regresiva sean *L. theobromae*.

### Maracuyá

- **Mosca del botón floral:** la evidencia en *Passiflora edulis* procede de una tesis peruana en Lima (Rojas Meza, 2026, ensayos 2024). El estudio de Orihuela et al. (2022) se realizó en **granadilla** (*Passiflora ligularis*) en Oxapampa; su relación entre HR e incidencia no se transfiere a maracuyá de Lambayeque.
- **Defoliadores:** la guía técnica del INIA enumera *Dione juno* y *Agraulis* sp. como hospedantes de maracuyá; se revisó la ficha bibliográfica y su extracto indexado, no una auditoría entomológica completa del PDF.
- **Antracnosis:** reemplazar la revisión nutricional de maracuyá como fuente directa del patógeno por el estudio de *Colletotrichum* en *P. edulis* en China (2025), identificando que se trata de evidencia extranjera y de varias especies.
- **Secadera:** la tesis UNPRG 2025 trabajó con **30 muestras de tejido sintomático de cinco sectores**, con *Fusarium* en 22 muestras y aislado *F. solani* FmOlmt5. **22/30 no es incidencia de parcelas ni porcentaje regional de plantas afectadas.** Se requieren muestreos epidemiológicos para convertir esa evidencia en mapas.

### Banano

- **Picudo negro:** *Cosmopolites sordidus* está documentado por SENASA en San Martín, pero la cita no confirma su frecuencia en Lambayeque.
- **Nematodos:** la revisión sistemática 2024 identifica *Radopholus similis* y otros géneros; necesitan diagnóstico y densidad por unidad de raíces/suelo, no solo temperatura.
- **Foc R4T:** EPPO/SENASA documentan detección inicial oficial peruana en **Piura 2021** y situación bajo control. No inferir presencia en cada distrito de Lambayeque por clima. Priorizar bioseguridad y diagnóstico SENASA.
- **Sigatoka negra:** *Pseudocercospora fijiensis* está descrita por artículos 2023–2025, pero se requieren mediciones foliares y calibración específica. Un modelo de Antillas Francesas no es validado automáticamente en Lambayeque.

## 4. Extensión de café: validación documental independiente

El café figura en el visor experimental, pero **no forma parte de los 23 registros principales**. Se corroboró la relación *Hemileia vastatrix*–café mediante revisión de 2024 con DOI 10.32604/phyton.2024.049612 y la importancia de *Leucoptera coffeella* por revisión sistemática de junio de 2026 con DOI 10.3390/insects17060636. Ninguna valida ocurrencia en los puntos de Lambayeque ni un modelo de riesgo regional; se requiere decidir primero si café se añade formalmente a Cultivos y Sanidad, además de precisar la geografía cafetalera priorizada.

## 5. Correcciones que deben realizarse antes de aprobar las fichas para producción

1. Reemplazar en mango las referencias a moscas de la fruta usadas indebidamente en queresas y antracnosis por fuentes que traten el organismo correspondiente.
2. Separar asociaciones por especie/género: moscas de fruta, cochinillas de vid, trips y ácaros, mosca blanca y cochinillas, defoliadores de maracuyá.
3. Corregir la ficha de maracuyá para que el artículo *Dasiops* de Oxapampa quede marcado como **granadilla**, no evidencia primaria del cultivo maracuyá. Añadir la tesis de *Dasiops inedulis* en maracuyá de Lima, indicando escala.
4. Incorporar la tesis local de Fusarium como evidencia específica con su correcta interpretación; prohibir que el 73,33 % de **muestras seleccionadas** se interprete como prevalencia regional.
5. Aclarar que *Phytophthora cinnamomi* es oomiceto; reemplazar dependencia de HR 2m por mediciones de suelo.
6. Ampliar a *Lasiodiplodia* spp. en el diagnóstico diferencial de palto, evitando asignar todos los cancros y pudriciones a *L. theobromae*.
7. Distinguir entre oídio de vid y mildiu, y conservar el primero como organismo priorizado ya en producción.
8. Verificar Foc R4T por SENASA y mantener procedimientos de bioseguridad, no pronóstico de presencia por clima.
9. No habilitar categorías de riesgo para ninguno de los 23 organismos sin presencia, fenología, variables ambientales adecuadas y calibración local.
10. Verificar **cada registro de productos** en SIGIA SENASA por formulación, cultivo, blanco, uso y vigencia; los 31 del catálogo tienen `ficha_confirmada=false`.

## 6. Corrección bibliográfica especialmente relevante: *Ceratitis capitata*

En el artículo original de Ricalde et al. (2012), `DOI 10.1673/031.012.3301`, el resumen de Petrolina informa base térmica **8,47 °C** con **341 grados-día**, pero el texto de resultados vinculado a Tabla 4 indica **9,1 °C** con los mismos **341 grados-día**. La discrepancia está en la propia publicación. Por ello no corresponde declarar validado un umbral puntual para Lambayeque.

El indicador experimental UX69 actualmente usa 9,1 °C, señalado como provisional. Antes de corregirlo técnicamente se debe revisar la tabla y los materiales de la revista, correr una prueba de sensibilidad entre ambos valores y contrastarlos con observaciones de desarrollo local. **En esta fase no se altera el algoritmo ni se inventa una solución a la contradicción.**

## 7. Definición operativa de validación científica

**Aprobación bibliográfica limitada** significa que existe una referencia que respalda la asociación biológica al nivel documentado (especie, género o grupo), con identificación de año, fuente, lugar y limitación. No significa:
- confirmar el organismo en el mapa de Lambayeque;
- validar un modelo predictivo de enfermedad o infestación;
- demostrar infección actual ni necesidad de aplicar un plaguicida;
- validar el registro SENASA de un insumo comercial.

Para permitir un modelo fitosanitario regional se exigirán **seis condiciones verificables**: identidad taxonómica; evidencia de presencia en zonas objetivo; fenología del hospedante; medición de variables causales; parametrización contrastada; validación prospectiva independiente. Si falta una, se mantiene el estado «No validado para predicción regional».

## 8. Referencias bibliográficas verificadas por título, URL o DOI

Las citas siguientes **no implican revisión del texto completo**; se indica si son artículos científicos, guías institucionales o informes técnicos. Cuando no existe DOI publicado en la ficha, no se inventa.

<a id="ref-senasa-mango-2025"></a>
**SENASA-MANGO-2025** · SENASA (2025). [Nota oficial: Lambayeque intensifica lucha contra mosca de fruta en mango](https://www.gob.pe/institucion/senasa/noticias/1230976-lambayeque-intensifica-lucha-contra-la-mosca-de-la-fruta-para-proteger-la-competitividad-del-mango). *oficial regional*. Alcance: Confirma importancia del grupo en Motupe/Jayanca/Olmos/Zaña; no separa abundancias de Ceratitis y Anastrepha.

<a id="ref-senasa-mango-2021"></a>
**SENASA-MANGO-2021** · SENASA (2021). [Acciones de control integrado de mosca de fruta en cosecha de mango, Lambayeque](https://www.senasa.gob.pe/senasacontigo/lambayeque-acciones-de-control-integrado-de-moscas-de-la-fruta-contribuye-con-la-sanidad-en-la-cosecha-de-mango/). *oficial regional*. Alcance: Control y trampas; las cifras son históricas, no estado 2026.

<a id="ref-ricalde-2012"></a>
**RICALDE-2012** · Ricalde et al. (2012). [Temperature-dependent development and survival of Brazilian populations of Ceratitis capitata](https://doi.org/10.1673/031.012.3301). DOI: `10.1673/031.012.3301`. *articulo original laboratorio*. Alcance: Petrolina: resumen 8,47 °C/341 GD; cuerpo de resultados 9,1 °C/341 GD, discrepancia interna sin resolver; laboratorio Brasil.

<a id="ref-mango-scale-2023"></a>
**MANGO-SCALE-2023** · Dako (2023). [White Mango Scale (Aulacaspis tubercularis) infestation on mango: distinct scenarios in Ethiopia and Kenya](https://doi.org/10.1016/j.heliyon.2023.e19054). DOI: `10.1016/j.heliyon.2023.e19054`. *articulo original extranjero*. Alcance: Valida hospedante–queresa ejemplar; no prueba A. tubercularis en Lambayeque.

<a id="ref-mango-anth-peru-2023"></a>
**MANGO-ANTH-PERU-2023** · Vilcarromero-Ramos et al. (2023). [First Report of Anthracnose Caused by Colletotrichum asianum on Mango in Peru](https://doi.org/10.1094/PDIS-10-22-2357-PDN). DOI: `10.1094/PDIS-10-22-2357-PDN`. *articulo original peru*. Alcance: Reporte en Amazonas, no Lambayeque; no define todas las especies presentes.

<a id="ref-mango-anth-2025"></a>
**MANGO-ANTH-2025** · Nguyen et al. (2025). [Identification, characterization and pathogenicity of C. asianum, C. fructicola and C. laticiphilum in mango Vietnam](https://doi.org/10.1139/cjm-2025-0069). DOI: `10.1139/cjm-2025-0069`. *articulo original extranjero*. Alcance: Complejo de especies; Vietnam, no Perú.

<a id="ref-grape-mealy-2024"></a>
**GRAPE-MEALY-2024** · UC IPM (2024). [Vine Mealybug — Planococcus ficus](https://ipm.ucanr.edu/agriculture/grape/vine-mealybug/). *guia tecnica especializada*. Alcance: Planococcus ficus; requiere identificación local.

<a id="ref-grape-pseud"></a>
**GRAPE-PSEUD** · UC IPM (2015). [Mealybugs (Pseudococcus) in grape](https://ipm.ucanr.edu/agriculture/grape/mealybugs-pseudococcus/). *guia tecnica especializada*. Alcance: Especies distintas de Planococcus ficus, con ciclos diferentes.

<a id="ref-grape-thrips"></a>
**GRAPE-THRIPS** · UC IPM (2015). [Thrips on grape](https://ipm.ucanr.edu/agriculture/grape/thrips/). *guia tecnica especializada*. Alcance: Drepanothrips reuteri y Frankliniella occidentalis en California; no supone ocurrencia en Lambayeque.

<a id="ref-grape-mites"></a>
**GRAPE-MITES** · UC IPM (2016). [Identifying Spider Mites and Their Damage in Grape](https://ipm.ucanr.edu/agriculture/grape/invertebratesidentifying-spider-mites-and-their-damage/). *guia tecnica especializada*. Alcance: Diferenciar ácaros foliares, no agrupar con trips.

<a id="ref-grape-pm"></a>
**GRAPE-PM** · UC IPM (s. f.). [Powdery mildew of grape — Erysiphe necator](https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/). *guia tecnica especializada*. Alcance: Modelo requiere fenología, condiciones de infección y temperatura horaria.

<a id="ref-grape-pm-model"></a>
**GRAPE-PM-MODEL** · UC IPM archivo (s. f.). [Disease model of grape powdery mildew (archived)](https://ipm.ucanr.edu/DISEASE/DATABASE/grapepowderymildew.html). *guia historica archivada*. Alcance: El sitio avisa que es contenido archivado; no trasladar índices sin validación local.

<a id="ref-grape-bot"></a>
**GRAPE-BOT** · UC IPM (s. f.). [Botrytis Bunch Rot in Grape](https://ipm.ucanr.edu/agriculture/grape/botrytis-bunch-rot/). *guia tecnica especializada*. Alcance: Requiere agua libre en racimos y fenología; clima 2 m no da infección.

<a id="ref-inia-blueberry-2020"></a>
**INIA-BLUEBERRY-2020** · Velásquez Ochoa y Meza / INIA (2020). [Desarrollo de alternativas de MIP para arándano en Huaral](https://repositorio.inia.gob.pe/items/70ccf99b-a81b-4782-b2c6-07c4c7dabb25). *informe institucional peru*. Alcance: Documento de Huaral; resumen lista trips, Bemisia, pseudocóccidos, Botrytis, Phytophthora; no demuestra incidencia Lambayeque.

<a id="ref-bot-general"></a>
**BOT-GENERAL** · UC IPM (s. f.). [Botrytis blight or gray mold](https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/). *guia tecnica general*. Alcance: HR >90 % ≥6 h y/o mojado; no umbral clínicamente calibrado para arándano peruano.

<a id="ref-bot-review-2024"></a>
**BOT-REVIEW-2024** · Revisión en Food Microbiology (2024). [Botrytis fruit rot management: What have we achieved so far?](https://doi.org/10.1016/j.fm.2024.104564). DOI: `10.1016/j.fm.2024.104564`. *revision cientifica*. Alcance: Manejo y diagnóstico global, no parámetros de incidencia local.

<a id="ref-avocado-phyto"></a>
**AVOCADO-PHYTO** · UC IPM (s. f.). [Phytophthora Root Rot / Avocado](https://ipm.ucanr.edu/agriculture/avocado/phytophthora-root-rot/). *guia tecnica especializada*. Alcance: P. cinnamomi = oomiceto; humedad y drenaje del suelo determinantes.

<a id="ref-avocado-thrips"></a>
**AVOCADO-THRIPS** · UC IPM (2016). [Avocado Thrips — Scirtothrips perseae](https://ipm.ucanr.edu/agriculture/avocado/avocado-thrips/). *guia tecnica especializada*. Alcance: Espécimen guía de California; no valida presencia peruana.

<a id="ref-avocado-persea"></a>
**AVOCADO-PERSEA** · UC IPM (s. f.). [Persea Mite / Avocado](https://ipm.ucanr.edu/agriculture/avocado/persea-mite/). *guia tecnica especializada*. Alcance: Ácaros tienen diagnóstico diferente de queresas; identificar especie Perú.

<a id="ref-avocado-lasio-2026"></a>
**AVOCADO-LASIO-2026** · Llanos et al. (2026). [Identification, Distribution, and Pathogenicity of Lasiodiplodia Species Causing Avocado Stem-End Rot in Peru](https://doi.org/10.1094/PDIS-08-25-1691-RE). DOI: `10.1094/PDIS-08-25-1691-RE`. *articulo original peru*. Alcance: Aislamientos de 7 regiones; varias especies de Lasiodiplodia, confirma pudrición peduncular y cancro de ramas, no todos los casos de muerte regresiva.

<a id="ref-maracuya-inia"></a>
**MARACUYA-INIA** · INIA Perú (s. f.). [Guía técnica: el cultivo de maracuyá, sección plagas](https://repositorio.inia.gob.pe/bitstreams/c335afc1-2062-4ee4-8e84-4d958539d7c6/download). *guia institucional peru*. Alcance: Extracto indexado menciona Dione juno y Agraulis sp.; revisar edición y diagnóstico, no se evaluó el PDF completo en esta fase.

<a id="ref-maracuya-review-2023"></a>
**MARACUYA-REVIEW-2023** · Campos-Rodríguez et al. (2023). [Maracuyá: composición nutricional, bioactivos, biocontrol y fertilización orgánica](https://doi.org/10.17268/sci.agropecu.2023.040). DOI: `10.17268/sci.agropecu.2023.040`. *revision cientifica indirecta*. Alcance: No es estudio primario de infección/antracnosis/Fusarium o Dasiops en Lambayeque.

<a id="ref-dasiops-granadilla-2022"></a>
**DASIOPS-GRANADILLA-2022** · Orihuela et al. (2022). [Dasiops sp. in flower buds of Passiflora ligularis in Oxapampa](https://doi.org/10.24039/rtb20222021341). DOI: `10.24039/rtb20222021341`. *articulo original hospedante diferente*. Alcance: El hospedante del trabajo es GRANADILLA, no maracuyá; su correlación humedad–incidencia no se puede transferir.

<a id="ref-dasiops-maracuya-2026"></a>
**DASIOPS-MARACUYA-2026** · Rojas Meza / Universidad San Pedro (2026). [Dasiops inedulis en botón floral de maracuyá, ensayo en INIA La Molina](https://repositorio.usanpedro.edu.pe/items/dfd465f8-2c2a-489d-96f8-7e84bb90c3be). *tesis peru*. Alcance: Estudio experimental 2024 en Lima, depositado 2026; no detección Lambayeque.

<a id="ref-maracuya-anth-2025"></a>
**MARACUYA-ANTH-2025** · Zhao et al. (2025). [Identification and characterization of Colletotrichum species associated with anthracnose of passion fruit in China](https://doi.org/10.1080/07060661.2025.2505482). DOI: `10.1080/07060661.2025.2505482`. *articulo original extranjero*. Alcance: Passiflora edulis con múltiples especies; estudio Guangxi, no localidad Perú.

<a id="ref-maracuya-fus-2025"></a>
**MARACUYA-FUS-2025** · Tesen Elorreaga / UNPRG (2025). [Evaluación de tolerancia de Passiflora frente Fusarium spp., Lambayeque](https://repositorio.unprg.edu.pe/handle/20.500.12893/15980). *tesis muestras lambayeque*. Alcance: 22 de 30 MUESTRAS de tejidos afectados positivas, cinco sectores; NO prevalencia poblacional. F. solani cepa FmOlmt5 y pruebas de patogenicidad.

<a id="ref-banana-picudo"></a>
**BANANA-PICUDO** · SENASA (s. f.). [Monitoreo de parcelas de plátano en San Martín](https://www.senasa.gob.pe/senasacontigo/senasa-monitoreo-parcelas-de-platano-en-san-martin/). *nota oficial otra region*. Alcance: No demuestra ocurrencia en Lambayeque.

<a id="ref-banana-nema-2024"></a>
**BANANA-NEMA-2024** · Sousa et al. (2024). [Phytoparasitic Nematodes of Musa spp. with Emphasis on Genetic Resistance: a Systematic Review](https://doi.org/10.3390/plants13101299). DOI: `10.3390/plants13101299`. *revision sistematica*. Alcance: Radopholus similis, Helicotylenchus, Pratylenchus, Meloidogyne; identidad requiere laboratorio.

<a id="ref-banana-tr4-eppo"></a>
**BANANA-TR4-EPPO** · EPPO (2023). [Foc Tropical Race 4 distribution, Peru](https://gd.eppo.int/taxon/FUSAC4/distribution/PE). *registro fitosanitario oficial*. Alcance: Situación oficial de 2023: Perú, Piura (2021), restringida bajo control; no confirma presencia 2026 Lambayeque.

<a id="ref-banana-tr4-senasa"></a>
**BANANA-TR4-SENASA** · SENASA (2021). [Confirmación del brote Foc R4T en Piura](https://www.gob.pe/institucion/senasa/noticias/429832-senasa-confirma-brote-de-fusarium-raza-4-tropical-en-piura). *oficial peru*. Alcance: Lugar del reporte = Piura, no Lambayeque.

<a id="ref-sigatoka-2025"></a>
**SIGATOKA-2025** · de Jesus et al. (2025). [Pseudocercospora fijiensis and P. musae biology and epidemiology](https://doi.org/10.1016/j.fbr.2024.100408). DOI: `10.1016/j.fbr.2024.100408`. *revision cientifica*. Alcance: Revisión, sin calibración epidemiológica Lambayeque.

<a id="ref-sigatoka-2023"></a>
**SIGATOKA-2023** · Delatouche et al. (2023). [Dynamic of Pseudocercospora fijiensis: weather, fungicide and landscape effects](https://doi.org/10.1094/PHYTO-04-22-0132-R). DOI: `10.1094/PHYTO-04-22-0132-R`. *articulo original extranjero*. Alcance: Modelo en Antillas francesas; no transferir pesos a Lambayeque.

<a id="ref-coffee-rust-2024"></a>
**COFFEE-RUST-2024** · Salazar-Navarro et al. (2024). [Coffee Leaf Rust in Coffee Plants and Perspectives by the Disease Control](https://doi.org/10.32604/phyton.2024.049612). DOI: `10.32604/phyton.2024.049612`. *revision cientifica*. Alcance: Requiere agua libre en hoja; literatura externa.

<a id="ref-coffee-miner-2026"></a>
**COFFEE-MINER-2026** · Jean-Baptiste et al. (2026). [Systematic review of biocontrol, extracts and cover crops for Leucoptera coffeella](https://doi.org/10.3390/insects17060636). DOI: `10.3390/insects17060636`. *revision sistematica*. Alcance: Revisión 130 publicaciones examinadas, 28 incluidas; no calibra desarrollo local.

<a id="ref-senasa-sigia"></a>
**SENASA-SIGIA** · SENASA (s. f.). [SIGIA consulta de registros de plaguicidas por cultivo y plaga](https://servicios.senasa.gob.pe/SIGIAWeb/sigia_consulta_cultivo.html). *registro oficial*. Alcance: Consulta exacta de producto, cultivo, plaga, formulación y vigencia; no equivale a etiqueta aprobada.

## 9. Archivos y alcance técnico

- La **matriz independiente** se conserva en `datos/bibliografia_validada_fitosanidad_ux71.json`, con 23 registros enlazados a fuentes con IDs estables.
- El archivo principal `datos/sanidad_agroexportadora_2026.json` **no se ha modificado** en esta fase: evitar cambiar fichas de campo hasta aprobar la corrección de identidad, registros comerciales y niveles de evidencia.
- La salida está diseñada para alimentar luego fichas con etiquetas verificables: «Fuente científica internacional», «Fuente institucional Perú», «Evidencia de muestras Lambayeque», «Pendiente de identificación», «Sin validación local de riesgo».
