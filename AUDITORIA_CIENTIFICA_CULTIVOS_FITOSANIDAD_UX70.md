# Auditoría científica de cultivos, plagas y enfermedades priorizados — OAF Lambayeque (UX70)

**Corte documental: 6 de noviembre de 2026.**  
**Alcance:** revisión de los **seis cultivos y 23 fichas del apartado «Cultivos y Sanidad»**, con contraste del catálogo experimental de «Escenarios de riesgo agroclimático» que contiene además café. **No modifica el contenido visible, no amplía el visor ni habilita nuevos modelos predictivos.**

## Conclusión ejecutiva

- El catálogo principal conserva **6 cultivos, 23 fichas (12 de plagas y 11 de enfermedades)**. La plataforma de escenarios incorpora **café como 7.º cultivo**, pero este no figura entre las 23 fichas: ambos inventarios todavía no son equivalentes.
- La revisión bibliográfica respalda la pertinencia de las principales asociaciones hospedante–organismo. **No se ha demostrado incidencia actual por provincia/distrito de Lambayeque para las 23 fichas**, ni existe calibración epidemiológica regional para convertirlas en categorías de riesgo.
- **31 de 31 fichas de productos** registradas en el catálogo tienen `ficha_confirmada=false`. El programa no debe decir que están autorizados sin verificar **SIGIA/SENASA** y la etiqueta exacta cultivo–especie–formulación–vigencia.
- Se identifican problemas de **agrupación taxonómica, referencias no específicas al organismo y condiciones epidemiológicas no medidas**. Las correcciones quedan especificadas en el registro JSON, sin modificar aún las fichas publicadas.
- Los indicadores de *Botrytis cinerea* (arándano) y *Ceratitis capitata* (mango) son **exploratorios**. Su existencia no justifica tratarlos como índices validados de infección o infestación.

## Metodología de evaluación y límites

Se contrastaron los nombres de los organismos, su asociación con el cultivo, la escala geográfica de las fuentes, los factores ambientales requeridos y la posibilidad de construir modelos mediante documentos oficiales de SENASA/INIA, literatura científica, guías técnicas revisadas y publicaciones indexadas. Se priorizaron trabajos recientes (2020–2026), conservando fuentes históricas cuando son la referencia original para un parámetro fisiológico.

**Niveles que NO deben confundirse:** (1) asociación biológica publicada; (2) evidencia en Perú; (3) registro específico en Lambayeque; (4) modelo calibrado localmente. Tener nivel (1) no demuestra (3) ni (4). Los enlaces son evidencia documental, no pruebas de presencia actual. Esta entrega tampoco constituye auditoría legal de registros de plaguicidas.

## Matriz completa de las 23 fichas

| N.º | Cultivo | Ficha en OAF | Agente(s) citados | Identificación | Ámbito de la evidencia | Prioridad de revisión |
|---:|---|---|---|---|---|---|
| 1 | Mango | Moscas de la fruta | Ceratitis capitata y Anastrepha spp. | Identificación incompleta / agrupada | SENASA Lambayeque | muy alta |
| 2 | Mango | Cochinillas o queresas | Diversas especies de hemípteros | Identificación incompleta / agrupada | Sin identificación local | media |
| 3 | Mango | Antracnosis | Colletotrichum spp. | Identificación incompleta / agrupada | Publicaciones externas | alta |
| 4 | Vid | Cochinilla harinosa de la vid | Planococcus ficus y Pseudococcus spp. | Identificación incompleta / agrupada | Guías científicas externas | alta |
| 5 | Vid | Trips y ácaros | Diversos Thysanoptera y Acari | Identificación incompleta / agrupada | Guías científicas externas | media |
| 6 | Vid | Oídio | Erysiphe necator | Identificación definida | Guías científicas externas | muy alta |
| 7 | Vid | Botrytis del racimo | Botrytis cinerea | Identificación definida | Guías científicas externas | alta |
| 8 | Arándano | Trips | Frankliniella spp. y Thrips spp. | Identificación incompleta / agrupada | INIA Huaral | media |
| 9 | Arándano | Mosca blanca y cochinillas | Bemisia tabaci y pseudocóccidos | Identificación incompleta / agrupada | INIA Huaral | media |
| 10 | Arándano | Moho gris | Botrytis cinerea | Identificación definida | INIA Perú + guías externas | muy alta |
| 11 | Arándano | Pudrición radicular | Phytophthora cinnamomi | Oomiceto identificado | INIA Huaral | alta |
| 12 | Palto | Trips | Diversas especies de trips | Identificación incompleta / agrupada | Guías científicas externas | media |
| 13 | Palto | Queresas y ácaros | Hemípteros fitófagos y ácaros | Identificación incompleta / agrupada | Guías científicas externas | media |
| 14 | Palto | Tristeza / pudrición de raíces | Phytophthora cinnamomi | Oomiceto identificado | SENASA Perú (otro departamento) | muy alta |
| 15 | Palto | Muerte regresiva | Lasiodiplodia theobromae (según diagnóstico) | Identificación incompleta / agrupada | Estudio científico Perú | alta |
| 16 | Maracuyá | Mosca del ovario | Dasiops spp. | Identificación incompleta / agrupada | Estudios Perú; hospedante a precisar | alta |
| 17 | Maracuyá | Gusano defoliador | Dione juno y Agraulis spp. | Identificación incompleta / agrupada | Publicaciones externas | media |
| 18 | Maracuyá | Antracnosis | Colletotrichum spp. | Identificación incompleta / agrupada | Revisión secundaria externa | alta |
| 19 | Maracuyá | Marchitez / secadera | Fusarium spp. (confirmar aislamiento) | Identificación incompleta / agrupada | Investigación con muestras de Lambayeque | muy alta |
| 20 | Banano y plátano | Picudo negro | Cosmopolites sordidus | Identificación definida | SENASA San Martín | alta |
| 21 | Banano y plátano | Nematodos fitoparásitos | Radopholus similis y otros nematodos | Identificación incompleta / agrupada | Guía SENASA Perú | alta |
| 22 | Banano y plátano | Fusariosis Raza 4 Tropical | Fusarium oxysporum f. sp. cubense R4T | R4T, control oficial | Cuarentena Perú (Piura) | critica bioseguridad |
| 23 | Banano y plátano | Sigatoka negra | Pseudocercospora fijiensis | Identificación definida | Investigación Latinoamérica | muy alta |

**Interpretación:** «Identificación incompleta / agrupada» no invalida la existencia de la plaga: significa que la ficha no contiene una especie aislada con la precisión necesaria para un modelo de temperatura, infección, fenología o umbral de acción. «INIA Huaral», «SENASA San Martín» o «Literatura externa» tampoco significan detección en Lambayeque.

## Observaciones por cultivo

### Mango (*Mangifera indica*)

Separar *C. capitata* y *Anastrepha* spp. (SENASA MTD); las cochinillas no están identificadas a especie en la ficha. La antracnosis puede ser causada por múltiples especies de *Colletotrichum*: la referencia SENASA sobre mosca de fruta usada como fuente principal no demuestra antracnosis. Un estudio de 2026 aporta evidencia del complejo en mango, pero no acredita una detección en Lambayeque.

- **Moscas de la fruta — Ceratitis capitata y Anastrepha spp.:** Separar Ceratitis capitata de Anastrepha spp.; capturas MTD SENASA, identificación taxonómica y estado de frutos. El modelo térmico brasileño solo refiere a C. capitata.
- **Cochinillas o queresas — Diversas especies de hemípteros:** Identificar cochinilla/queresa a familia y especie y sustituir la referencia primaria: la nota SENASA adjunta se centra en moscas de la fruta.
- **Antracnosis — Colletotrichum spp.:** Colletotrichum spp. requiere identificación (complejos de especies) y datos de mojado de flores/frutos; reemplazar fuente principal no específica sobre mosca de fruta.

### Vid (*Vitis vinifera*)

*E. necator* es el oídio y corresponde al catálogo. *Plasmopara viticola* (mildiu) figura como pendiente en el módulo C, **pero no está entre las cuatro fichas priorizadas** de vid: esa discrepancia se debe corregir antes de implementar un modelo. Para *Botrytis* del racimo, UC IPM requiere humedad libre y fenología; no aplicar el proxy de arándano. Separar trips y ácaros en la vigilancia.

- **Cochinilla harinosa de la vid — Planococcus ficus y Pseudococcus spp.:** Separar Planococcus ficus de Pseudococcus spp.; identificación taxonómica, inspección de racimos/corteza y hormigas.
- **Trips y ácaros — Diversos Thysanoptera y Acari:** No usar un único modelo para trips y ácaros; confirmar especie y diferenciar umbrales y enemigos naturales.
- **Oídio — Erysiphe necator:** Índice de oídio exige fenología y condiciones de infección primaria; no inferirlo solo con HR o lluvia.
- **Botrytis del racimo — Botrytis cinerea:** Necesita duración de humectación real del racimo, temperatura y etapa de floración/envero; no transferir proxy de arándano.

### Arándano (*Vaccinium* spp.)

La ficha se apoya principalmente en INIA Huaral (2020), que menciona los organismos, pero no demuestra incidencia en Lambayeque. El criterio HR ambiental >90 % durante seis horas para *Botrytis* solo mide favorabilidad del aire; no son seis horas de mojado foliar. *Phytophthora cinnamomi* es un oomiceto y requiere datos de drenaje/sustrato.

- **Trips — Frankliniella spp. y Thrips spp.:** Confirmar Frankliniella y Thrips a especie y fenología; la fuente INIA es Huaral, no validación Lambayeque.
- **Mosca blanca y cochinillas — Bemisia tabaci y pseudocóccidos:** Separar Bemisia tabaci de pseudocóccidos y su vigilancia; no agrupar en un modelo térmico.
- **Moho gris — Botrytis cinerea:** El criterio HR aire >90 % por 6 h es proxy experimental, no humedad foliar medida ni riesgo de infección validado; registrar floración y tejidos mojados.
- **Pudrición radicular — Phytophthora cinnamomi:** Phytophthora es oomiceto, no hongo verdadero; requiere humedad/saturación y drenaje del sustrato y diagnóstico radicular.

### Palto (*Persea americana*)

SENASA respalda *Phytophthora cinnamomi* y su vínculo con saturación del suelo, pero la nota se refiere a Moquegua; no prueba incidencia local. Un estudio indexado peruano de 2026 demuestra **diversas especies de *Lasiodiplodia*** en enfermedades de palto; atribuir toda muerte regresiva a *L. theobromae* sería una simplificación. En trips, queresas y ácaros falta identificación regional.

- **Trips — Diversas especies de trips:** Identificar trips regionales antes de adoptar parámetros de Scirtothrips perseae de California; validar especies presentes en Perú.
- **Queresas y ácaros — Hemípteros fitófagos y ácaros:** Separar queresas de ácaros e identificar especies; no hay una única respuesta térmica para ambos.
- **Tristeza / pudrición de raíces — Phytophthora cinnamomi:** Faltan humedad y drenaje del suelo, estado sanitario de raíces y datos locales de riego; Phytophthora cinnamomi es oomiceto.
- **Muerte regresiva — Lasiodiplodia theobromae (según diagnóstico):** Estudio peruano 2026 identifica varias especies Lasiodiplodia; no atribuir toda muerte regresiva a L. theobromae sin aislamiento/diagnóstico.

### Maracuyá (*Passiflora edulis*)

Una tesis UNPRG (2025) procesó muestras de cinco sectores de Lambayeque y reportó aislamientos de *Fusarium* con patogenicidad, incluido *F. solani*: evidencia local de alta utilidad, pero aún no autoriza un índice climático. *Dasiops* spp. es real en pasifloráceas; el estudio de correlación de Oxapampa es en granadilla, no extrapolable a maracuyá de Lambayeque. Distinguir antracnosis (*Colletotrichum* spp.) y la identidad taxonómica del agente de secadera.

- **Mosca del ovario — Dasiops spp.:** Confirmar Dasiops inedulis u otra especie y revisar botón floral/ovario; el trabajo climático de Oxapampa trata granadilla, no maracuyá en Lambayeque.
- **Gusano defoliador — Dione juno y Agraulis spp.:** Dione juno y Agraulis spp. requieren identificación por larva/adulto; no inventar dinámica poblacional regional.
- **Antracnosis — Colletotrichum spp.:** Colletotrichum spp. es complejo; requiere diagnóstico y datos de mojado antes de parametrizar antracnosis.
- **Marchitez / secadera — Fusarium spp. (confirmar aislamiento):** La tesis UNPRG describe Fusarium solani FmOlmt5 en muestras de Lambayeque; distinguir del agente de marchitez Fusarium oxysporum f.sp. passiflorae. Confirmar aislamiento y pruebas de patogenicidad.

### Banano y plátano (*Musa* spp.)

Picudo negro y nematodos son plagas documentadas, pero los documentos utilizados no demuestran por sí solos ocurrencia en Lambayeque. Foc R4T está sujeto a control oficial y fue reportado inicialmente en Piura; no se puede declarar presencia en un distrito sin SENASA. La Sigatoka negra (*P. fijiensis*) tiene modelos publicados que usan lluvia, T, HR y humedad foliar: transferirlos requiere validación con hojas observadas.

- **Picudo negro — Cosmopolites sordidus:** Muestrear rizomas/pseudotallo y trampas; fuente original SENASA documenta San Martín, no ocurrencia en Lambayeque.
- **Nematodos fitoparásitos — Radopholus similis y otros nematodos:** Diferenciar Radopholus similis de otros nematodos con muestras de raíces/suelo y laboratorio; no usar temperatura sola.
- **Fusariosis Raza 4 Tropical — Fusarium oxysporum f. sp. cubense R4T:** Foc R4T es enfermedad cuarentenaria: confirmar diagnóstico oficial y medidas SENASA. La denominación Fusarium odoratissimum existe, pero su adopción taxonómica es debatida; mantener nomenclatura oficial R4T.
- **Sigatoka negra — Pseudocercospora fijiensis:** Modelo específico necesita duración de humedad foliar, lluvia, temperatura, radiación, susceptibilidad varietal y datos de infección; no basta HR media.

## Café: extensión científica, no uno de los seis cultivos del inventario principal

El catálogo del visor C presenta café, mientras «Cultivos y Sanidad» solo registra los seis cultivos previos. El interés científico de **roya (*Hemileia vastatrix*)** y **minador (*Leucoptera coffeella*)** está respaldado por investigaciones; no son fichas de los 23 registros. La roya necesita agua libre/humectación, temperatura, variedad, sombra e inóculo. El minador requiere identificación, muestreos de minas activas y enemigos naturales. No se habilita ni extrapola un modelo durante esta auditoría.

## Desajustes y correcciones necesarias antes de calcular riesgo

1. **Inventario:** homologar si café se incorporará oficialmente como séptimo cultivo de «Cultivos y Sanidad», o mantenerlo expresamente como extensión experimental separada.
2. **Mango – mosca:** separar los modelos de *C. capitata* y *Anastrepha* spp.; solo el primero tiene el indicador térmico experimental UX69. Para riesgo real se necesita MTD/capturas, frutos y vigilancia. El modelo de Ricalde 2012 presenta **8,47 °C en el resumen y 9,1 °C en los resultados** para Petrolina; mantener advertencia de contradicción y revisar Tabla 4 antes de considerar definitivo un parámetro. Ninguno está validado en Lambayeque.
3. **Vid – enfermedad:** el inventario principal prioriza **oídio por *Erysiphe necator***; `Plasmopara viticola` figura en los pendientes del visor, pero **no** en las cuatro fichas de vid. No debe asignarse prioridad automáticamente a ese organismo sin una decisión explícita.
4. **Palto – muerte regresiva:** cambiar el criterio de diagnóstico para considerar *Lasiodiplodia* spp., porque la investigación peruana 2026 detecta distintas especies. *Phytophthora cinnamomi* debe describirse correctamente como oomiceto.
5. **Maracuyá – secadera:** integrar como referencia prioritaria la tesis UNPRG con muestras de Lambayeque, sin colapsar todas las secaderas en una única especie ni inventar porcentajes de riesgo. *Dasiops* debe especificar órgano dañado y especie cuando pueda confirmarse.
6. **Banano – Foc R4T:** separar de modelado climático y dar precedencia a vigilancia/confirmación oficial y bioseguridad; el hallazgo nacional en Piura no confirma presencia en otros departamentos.
7. **Fuentes no específicas:** reemplazar las páginas SENASA sobre mosca de fruta usadas como fuente principal de queresas o antracnosis de mango, por bibliografía relacionada directamente con la entidad.
8. **Productos:** no publicar registro SENASA como «confirmado» ni dosis/eficacia cuando el campo `ficha_confirmada` sea falso. Verificar especie objetivo y etiqueta en SIGIA.
9. **Datos agroclimáticos:** registrar humedad foliar real o un estimador validado para *Botrytis*, Sigatoka, roya y antracnosis; humedad relativa ambiental a 2 m no es equivalente. Para *Phytophthora* usar humedad y drenaje del suelo, no humedad foliar.

## Priorización para investigación/modelos, sin activar alarmas automáticas

| Orden sugerido | Organismo y cultivo | Motivo | Principal evidencia adicional que falta |
|---:|---|---|---|
| 1 | *C. capitata* – mango | Importancia económica y vigilancia regional SENASA | Capturas MTD, estado del hospedante y biofix térmico local |
| 2 | *Botrytis cinerea* – arándano | Modelo meteorológico exploratorio ya integrado | Humedad foliar medida, floración e incidencia por parcela |
| 3 | *Erysiphe necator* – vid | Modelo UC IPM publicado | Verificación de infección primaria, fenología y temperatura horaria |
| 4 | *Phytophthora cinnamomi* – palto | Enfermedad radicular documentada en Perú | Humedad del suelo, riego/drenaje y diagnóstico en raíces |
| 5 | *Fusarium* spp. – maracuyá | Evidencia académica con muestras de Lambayeque | Diagnóstico diferencial y evidencia de campo por localidad |
| 6 | *P. fijiensis* – banano | Modelo de infección foliar publicado en otros países | Humectación foliar, diagnóstico e identificación regional |
| Transversal | Foc R4T – banano | Bioseguridad y cuarentena | Confirmación oficial y protocolos SENASA; **no un índice climático** |
| Extensión | *H. vastatrix* – café | Relevancia potencial para ampliación agroecológica | Incorporación al inventario principal, datos de hoja/sombra e incidencia |

## Bibliografía y enlaces de contraste

1. SENASA (2025). [Mosca de fruta en mango de Lambayeque](https://www.gob.pe/institucion/senasa/noticias/1230976-lambayeque-intensifica-lucha-contra-la-mosca-de-la-fruta-para-proteger-la-competitividad-del-mango).
2. SENASA MTD. [Consulta oficial por lugar de producción](https://cmtd.senasa.gob.pe/consulta-lp/mtd).
3. UC IPM. [Oídio de vid (*Erysiphe necator*)](https://ipm.ucanr.edu/agriculture/grape/powdery-mildew/).
4. UC IPM. [Podredumbre Botrytis en vid](https://ipm.ucanr.edu/agriculture/grape/botrytis-bunch-rot/).
5. UC IPM. [Cochinilla harinosa de la vid](https://ipm.ucanr.edu/agriculture/grape/vine-mealybug/).
6. INIA (2020). [Plagas y enfermedades del arándano investigadas en Huaral](https://repositorio.inia.gob.pe/items/70ccf99b-a81b-4782-b2c6-07c4c7dabb25).
7. UF/IFAS. [Guía MIP arándano, Botrytis y humectación](https://ask.ifas.ufl.edu/publication/HS380).
8. SENASA. [Pudrición de raíces de palto](https://www.senasa.gob.pe/senasacontigo/senasa-la-tristeza-del-palto-y-recomendaciones-para-su-control/).
9. UC IPM. [*Phytophthora cinnamomi* es oomiceto y requiere drenaje](https://ipm.ucanr.edu/agriculture/avocado/phytophthora-root-rot/).
10. Llanos et al. (2026). [*Lasiodiplodia* spp. en palto peruano; Plant Disease, DOI 10.1094/PDIS-08-25-1691-RE](https://pubmed.ncbi.nlm.nih.gov/41177999/).
11. Campos-Rodríguez et al. (2023). [Revisión fitosanitaria secundaria en maracuyá, DOI 10.17268/sci.agropecu.2023.040](https://www.scielo.org.pe/scielo.php?pid=S2077-99172023000400011&script=sci_arttext).
12. UNPRG (tesis). [*Fusarium* en maracuyá muestreado en Lambayeque](https://repositorio.unprg.edu.pe/handle/20.500.12893/15980).
13. UNFV (2022). [*Dasiops* en granadilla y factores climáticos; no maracuyá](https://revistas.unfv.edu.pe/rtb/article/view/1341).
14. Benavides et al. (2023). [Modelos de Sigatoka negra, banana, Costa Rica](https://revistas.tec.ac.cr/index.php/agroinn/article/view/6612).
15. EPPO. [Situación oficial Foc R4T en Perú](https://gd.eppo.int/taxon/FUSAC4/distribution/PE).
16. EFSA (2022). [Nombre Foc TR4 y controversia taxonómica con *F. odoratissimum*, DOI 10.2903/j.efsa.2022.7092](https://doi.org/10.2903/j.efsa.2022.7092).
17. Ricalde et al. (2012). [Parámetros térmicos *C. capitata*; DOI 10.1673/031.012.3301](https://academic.oup.com/jinsectscience/article/12/1/33/881238).
18. Coffee Leaf Rust (2021). [Epidemiología roya del café y agua libre](https://www.mdpi.com/2073-4395/11/12/2590).
19. Revisión 2026. [*Leucoptera coffeella* y MIP](https://pmc.ncbi.nlm.nih.gov/articles/PMC13301395/).

## Entregables y regla de gobernanza

- Registro estructurado por ficha: [`datos/validacion_cientifica_fitosanidad_ux70.json`](datos/validacion_cientifica_fitosanidad_ux70.json).
- Fuente de datos que se ha auditado sin editar: [`datos/sanidad_agroexportadora_2026.json`](datos/sanidad_agroexportadora_2026.json).
- Catálogo experimental de dos modelos: [`datos/fitosanitario_modelos_ux69.json`](datos/fitosanitario_modelos_ux69.json).

**Regla de activación:** una asociación científicamente documentada solo permite mantener una ficha informativa. Un índice de riesgo con categorías espaciales exige, por separado, (a) organismo identificado, (b) datos ambientales necesarios, (c) fenología, (d) evidencia local de ocurrencia, (e) validación temporal/espacial y (f) trazabilidad de versión. Si falta alguno, se muestra «pendiente de validación» y no se dibuja riesgo ficticio.
