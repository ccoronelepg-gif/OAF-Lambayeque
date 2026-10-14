# OAF-Lambayeque — Estado del proyecto y punto de reanudación

**Fecha de cierre:** 11 de octubre de 2026 (Perú)  
**Estado:** Fase 1, integración histórica concluida; próximo paso: comparación observaciones SENAMHI–PISCOp–ERA5 en coordenadas coincidentes.  
**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque (OAF-Lambayeque).

## Objetivo y alcance

Construir un observatorio regional para Lambayeque con análisis histórico, seguimiento y futura predicción de lluvias, eventos asociados a El Niño y un módulo inicial de riesgos fitosanitarios del **arándano** utilizando registros sanitarios reales. Otros cultivos podrán agregarse posteriormente. La referencia climatológica principal es **1996–2025** (30 años); el periodo 1991–2020 puede emplearse como comparador internacional.

**Modo de colaboración acordado:** avanzar con el trabajo técnico del proyecto, presentar resultados y explicaciones claras; **no hacer preguntas de comprobación de conocimientos ni asignar ejercicios** al usuario.

## 1. Fuentes históricas y localidades iniciales

Primera red exploratoria: **Olmos, Chiclayo, Zaña e Incahuasi**. Estos son puntos de referencia, no estaciones instrumentales ni cobertura espacial completa de Lambayeque.

Se emplearon Open-Meteo Historical Weather (**ERA5-Seamless**) y un servicio de terceros de acceso a **PISCOp v3.0**. Se descubrió que solicitar ERA5-Land directamente devolvía precipitación diaria nula en una consulta inicial, por lo que se usó ERA5-Seamless para las extracciones históricas; las fuentes y variables deben verificarse por separado.

**Precipitación media anual PISCOp, 1996–2025, mm/año:**

| Localidad | Media |
| --- | ---: |
| Chiclayo | 59,15 |
| Zaña | 57,41 |
| Olmos | 267,61 |
| Incahuasi | 642,06 |

**Anomalías de precipitación 2023 vs. 1996–2025, PISCOp:**
Olmos +346,99 % (1 196,16 mm en 2023); Chiclayo +333,85 % (256,61 mm); Zaña +281,83 % (219,20 mm); Incahuasi +78,28 % (1 144,65 mm). La referencia incluye 2023 y no es un pronóstico.

## 2. Hallazgos del contraste de productos en Olmos

Para 1996–2025, ERA5-Seamless estimó una media anual de **1 016,15 mm/año** y PISCOp **267,61 mm/año**. Diferencia media: **748,54 mm/año**. En 1998, ERA5-Seamless estimó **5 005,50 mm** y PISCOp **1 453,68 mm** en el punto Olmos.

Correlación anual ERA5 vs. PISCOp en Olmos: Pearson **0,847** (30 años); Pearson **0,743** excluyendo temporalmente 1998; Spearman **0,781**. Correlación alta no implica acuerdo en cantidades ni exactitud frente a pluviómetros.

La auditoría espacial de Open-Meteo en Olmos para 1998 devolvió para **land** y **nearest** el mismo centro de celda (-6,0; -79,7), 5,288 km del punto solicitado, y los mismos **5 005,5 mm**. El método de selección no explicó la discrepancia en esa consulta.

## 3. Estaciones instrumentales SENAMHI incorporadas

Se recibieron archivos TXT originales de **Jayanca (La Viña), Cayaltí, Reque, Lambayeque y Cueva Blanca**, seis columnas diarias aparentes (año, mes, día, precipitación, temperatura máxima y mínima), con **-99,9** como código de dato ausente a tratar como NaN, verificando la ficha técnica para las unidades/definiciones.

Se informó de **116 293 filas originales** en los cinco archivos y se consolidó una rejilla analítica de **54 790 filas** (5 estaciones × 10 958 días entre 1996 y 2025), sin interpretar los días no observados como lluvia cero. Hay **11 años de precipitación completa simultánea** informados: 1996–2003, 2009, 2010, 2012. Los archivos recibidos terminan en 2014–2015; no contienen mediciones de 2017, 2023 o 2025. Se necesitan datos instrumentales nuevos para esos años.

**Lluvia observada en 1998**, con los 365 días disponibles en las cinco estaciones:

| Estación | Acumulado anual (mm) |
| --- | ---: |
| Jayanca (La Viña) | 1 428,00 |
| Cueva Blanca | 969,20 |
| Cayaltí | 558,50 |
| Lambayeque | 279,61 |
| Reque | 232,82 |

El archivo de Cueva Blanca presentaba las temperaturas marcadas como ausentes; no emplearlas para análisis térmicos.

**Atención metodológica:** no comparar pluviómetros de Jayanca con estimaciones PISCOp correspondientes a Olmos. Buscar y verificar la ubicación y elevación históricas de cada estación; metadatos geográficos identificados hasta ahora son **preliminares**, con discrepancias entre documentos. Usar una comparación espacial y temporal homogénea; documentar que estaciones utilizadas en PISCOp podrían comprometer la independencia de su validación.

## 4. Herramientas y productos construidos

Trabajo local en Windows + VS Code/Jupyter: proyecto `Proyecto_Agricultura_IA`, cuaderno `OAF_Lambayeque_Fase1.ipynb`, subcarpetas propuestas `01_Datos`, `02_Notebooks`, `03_Graficos`, `04_Modelos`, `05_Resultados`, `06_Web`. El usuario habilitó el guardado automático en VS Code o recibió instrucciones para ello; **guardar localmente NO publica automáticamente en GitHub**.

**Repositorio público:** https://github.com/ccoronelepg-gif/OAF-Lambayeque  
**Portal GitHub Pages:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/  
**Versión:** prototipo web histórico **v0.3**. Se cargó `index.html` y GitHub Actions confirmó despliegue Pages exitoso para el commit `6bad4e097805dfca2e5b4637aa4343d94e7dbaec` (run `38204198432`). GitHub Pages no contiene todavía un módulo predictivo validado. La disponibilidad desde un navegador concreto del usuario puede requerir confirmación adicional; el despliegue terminó exitosamente.

Los archivos meteorológicos locales y los datos completos **NO deben asumirse sincronizados con GitHub** ni subirse íntegramente al sitio público sin evaluar atribución, licencias, privacidad y volumen.

## 5. Punto exacto para continuar

**Siguiente fase: 3N — Comparación instrumentada de SENAMHI–PISCOp–ERA5.**

1. Confirmar el código, latitud, longitud, altitud y posibles reubicaciones de las cinco estaciones usando metadatos oficiales fiables, sin inventarlos.
2. Consultar series mensuales de **PISCOp** y series de lluvia **ERA5-Seamless** para cada una de las cinco estaciones, en las mismas coordenadas y periodos de observación.
3. Emparejar por estación y mes, distinguiendo meses completos de parciales. No tratar acumulados incompletos como totales reales.
4. Calcular sesgo, MAE, RMSE, correlaciones y gráficos, junto con auditoría específica de 1998. Evaluar restricciones de independencia de la validación de PISCOp.
5. Incorporar más registros SENAMHI recientes cuando estén disponibles, y posteriormente CHIRPS/indicadores de El Niño, modelos de pronóstico y riesgo fitosanitario de arándano.

**Criterio:** no atribuir capacidad predictiva ni exactitud comprobada a los productos históricos antes de validarlos. Publicar versiones sucesivas del observatorio en la misma dirección de GitHub Pages.

_Esta bitácora guarda las decisiones y resultados reportados a lo largo de las sesiones; los archivos de origen y las salidas científicas se conservan separadamente._


## Actualización 12/10/2026 — Fase 3N, primer contraste observado de 1998

Se volvió a comprobar directamente la precipitación diaria de los cinco archivos originales: los 365 días de 1998 están completos. Se incorporó `datos/senamhi_mensual_1998.csv` (60 filas; 5 estaciones x 12 meses) al repositorio.

**Hallazgo de georreferenciación:** las coordenadas de Cueva Blanca en el visor inicial eran incorrectas: para el estudio usar aproximadamente -6.1313, -79.4045, 3300 m según documentación SENAMHI, sujeto a confirmar el emplazamiento en 1998. Se corrigieron provisionalmente las coordenadas documentales de las cinco estaciones en el sitio. Deben mantenerse avisos sobre cambios de ubicación y metadatos históricos.

**Extracción real completada** mediante GitHub Actions, ejecutando `scripts/validacion_3n_1998.py`: 10 de 10 comparaciones SENAMHI-PISCOp y SENAMHI-ERA5-Seamless (12 meses íntegros de 1998), sin incidencias de API. Datos guardados en `VALIDACION_3N.md`, `datos/comparacion_3n_1998.csv`, `datos/metricas_3n_1998.csv` y `datos/estado_3n_1998.json`.

| Estación | SENAMHI obs. 1998 (mm) | PISCOp (mm) | ERA5-Seamless (mm) |
| --- | ---: | ---: | ---: |
| Jayanca (La Viña) | 1428.00 | 1296.71 | 7603.90 |
| Cayaltí | 558.50 | 685.56 | 1335.60 |
| Reque | 232.82 | 245.46 | 846.40 |
| Lambayeque | 279.61 | 288.23 | 1270.20 |
| Cueva Blanca | 969.20 | 1044.23 | 8451.40 |

**Conclusión provisional:** PISCOp ajusta más estrechamente los acumulados observados de las cinco estaciones en este año; ERA5-Seamless los sobreestima fuertemente. Esta es una **comparación exploratoria de un solo año**, no validación independiente o prueba de exactitud general: PISCOp puede incorporar las mismas estaciones en su interpolación, y las coordenadas históricas necesitan corroboración. Confirmar también unidades, centro de píxel meteorológico y posibles sesgos del producto ERA5 en futuros pasos.

**Portal actualizado** a versión 0.4: añade cuadro de comparación de los tres productos en 1998, selector interactivo de estación, métricas MAE y correcciones cartográficas preliminares. Rama `main` commit `483219446a06aa8dfad498c22552a6360965f222`; comprobar conclusión de despliegue GitHub Pages antes de afirmar sitio actualizado públicamente.

**Punto siguiente:** ampliar contraste a varios años y mensualidad coincidente con cobertura de 100 %, evaluar estaciones de control realmente independientes, confirmar metadatos históricos y auditar causa del sesgo extraordinario de ERA5. Mantener instrucciones del usuario: sin preguntas ni ejercicios, trabajar y publicar avances.

---

## Fase 3O cerrada el 14 de octubre de 2026 — validación multianual

**Resultados instrumentales:** se auditaron cinco archivos TXT SENAMHI y obtuvieron **1 109 meses-estación completos** entre enero de 1996 y octubre de 2015: Jayanca 219, Cayaltí 235, Reque 233, Lambayeque 204, Cueva Blanca 218. Hay 35 meses con observaciones incompletas y 56 meses-estación sin registros dentro de las 1 200 combinaciones 1996–2015. Se mantienen **11 años anuales completos simultáneos**: 1996–2003, 2009, 2010, 2012. Los registros originales no cubren 2016–2025.

**Contraste completo PISCOp v3.0 y ERA5-Seamless:** se obtuvieron **2 218 pares mensuales** y **10/10 combinaciones estación × producto**, sin errores pendientes tras recuperar intervalos ERA5 mediante consultas bienales. Métrica MAE mensual (mm), usando exactamente los mismos meses completos por estación:

| Estación | Meses | MAE PISCOp | MAE ERA5-Seamless | Sesgo acumulado PISCOp | Sesgo acumulado ERA5 |
|---|---:|---:|---:|---:|---:|
| Jayanca | 219 | 3,104 | 104,953 | −16,89 % | +724,56 % |
| Cayaltí | 235 | 1,824 | 15,613 | +11,82 % | +248,89 % |
| Reque | 233 | 1,023 | 7,757 | +3,98 % | +221,78 % |
| Lambayeque | 204 | 1,038 | 11,313 | −4,87 % | +273,70 % |
| Cueva Blanca | 218 | 29,257 | 131,025 | −34,43 % | +183,11 % |

El signo de sesgo se define como **estimado menos observado**. MAE y RMSE por mes son métricas descriptivas del conjunto evaluado. Resultados separados por 1998 y sin 1998 en `datos/metricas_3o_multianual.csv`.

**Principales advertencias:**
- PISCOp es interpolación climatológica alimentada por estaciones; al compararlo con registros SENAMHI posiblemente empleados en su elaboración, **no se dispone de validación independiente**.
- Coordenadas documentales de las cinco estaciones son **provisionales**; recuperar códigos y fichas oficiales SENAMHI, verificar cambios históricos de ubicación/altitud antes de una validación publicable.
- Los acumulados inusualmente elevados de **ERA5-Seamless** requieren auditoría de fuente, celdas, variable/unidades, elevación y contraste con ERA5 puro / ERA5-Land y, cuando sea posible, CHIRPS.
- Para construir alertas y modelos fitosanitarios se necesitan registros de enfermedades del arándano y observaciones meteorológicas recientes.

**Productos guardados:**
- Portal web **v0.5**: https://ccoronelepg-gif.github.io/OAF-Lambayeque/ (sección Contraste meteorológico multianual).
- Informe estadístico: [VALIDACION_3O.md](VALIDACION_3O.md).
- Auditoría cobertura: [COBERTURA_SENAMHI_3O.md](COBERTURA_SENAMHI_3O.md).
- Insumo mensual: [datos/senamhi_mensual_completo_1996_2015.csv](datos/senamhi_mensual_completo_1996_2015.csv).
- Métricas: [datos/metricas_3o_multianual.csv](datos/metricas_3o_multianual.csv).
- Pares: [datos/comparacion_3o_multianual.csv](datos/comparacion_3o_multianual.csv).
- Código reproducible: [scripts/validacion_3o_multianual.py](scripts/validacion_3o_multianual.py).
- Flujo automático: [.github/workflows/validacion_3o.yml](.github/workflows/validacion_3o.yml).

**Próxima fase 3P:** auditar diferencias de ERA5-Seamless y su representatividad espacial, comprobar metadatos oficiales y, si se dispone de redes independientes, realizar validación externa fuera de muestra; después ampliar cobertura territorial y evaluación del riesgo fitosanitario del arándano.

**Modo de trabajo acordado:** seguir desarrollando el proyecto sin preguntas ni ejercicios de comprobación al usuario.

## Actualización 14/10/2026 — Fase 3P (auditoría modelos y celdas)

**Estado: fase 3P concluida con limitaciones de la fuente ERA5-Land; siguiente fase 3Q, CHIRPS v3 mensual y sensibilidad de coordenadas.**

**Portal:** v0.6 con visor interactivo de modelos/celdas, misma URL pública https://ccoronelepg-gif.github.io/OAF-Lambayeque/.

**Evidencia calculada y conservada en GitHub:**
- Se recuperaron **30 de 45** combinaciones estación/año/modelo/selección previstas para 1998 y 2000. Las **15 no válidas** corresponden a ERA5-Land. No se imputaron como cero.
- En **180 de 180 pares mensuales comparables** los valores de precipitación ERA5-Seamless y ERA5 fueron idénticos, aunque las coordenadas declaradas de las celdas difirieron.
- En **60 de 60 pares mensuales** de 1998, las opciones Open-Meteo `land` y `nearest` dieron los mismos totales para ERA5-Seamless. **No se demuestra que cambiar la celda explique el sesgo.**
- Diagnóstico puntual 1–10 febrero 1998, Jayanca/Cueva Blanca: respuesta ERA5-Land **10/10 días y 240/240 horas nulos por estación**; ERA5 y Seamless íntegros. Esto es un resultado de esa configuración API, **no concluye que ECMWF carezca de los datos oficiales**.
- A partir de **2 218 pares** previos se calcularon **60 filas** de indicadores estacionales por estaciones, producto, estrato con/sin 1998, estación temporal enero–abril y mayo–diciembre. Excluyendo 1998 persiste sesgo positivo de ERA5-Seamless en enero–abril de las cinco estaciones.
- Discrepancias entre coordenadas actualmente utilizadas y metadatos alternativos: Jayanca ~1,68 km; Cayaltí ~2,41 km; Reque ~0,04 km; Lambayeque ~3,36 km. Verificar códigos y posibles traslados, no corregir sin reconsultar.
- Cueva Blanca ~(-6.131, -79.405), 3300 m, respaldada por boletín SENAMHI 2024, pero continuidad histórica exacta no corroborada.

**Archivos principales:** [CONCLUSIONES_3P.md](CONCLUSIONES_3P.md), [AUDITORIA_3P.md](AUDITORIA_3P.md), [DIAGNOSTICO_ESTACIONAL_3P.md](DIAGNOSTICO_ESTACIONAL_3P.md), [DIAGNOSTICO_ERA5_LAND_3P.md](DIAGNOSTICO_ERA5_LAND_3P.md), [METADATOS_GEOGRAFICOS_3P.md](METADATOS_GEOGRAFICOS_3P.md), y series CSV en `datos/`.

**Siguiente fase 3Q:** extraer **CHIRPS v3 mensual final** para los 1 109 meses-estación completos SENAMHI (1996–2015), auditar posiciones exactas y compararlo en los mismos meses con PISCOp y ERA5. CHIRPS v3 incorpora estaciones en su elaboración. Evitar considerar el producto diario CHIRPS `rnl` independiente de ERA5, ya que lo utiliza para desagregar totales pentadales. Priorizar el producto mensual final y documentación de fuente.

**Regla permanente del usuario:** desarrollar directamente el proyecto; no pedir ejercicios ni pruebas de comprensión.

## Actualización 14/10/2026 — cierre 3P y piloto CHIRPS v3 (3Q)

**Fase 3P: auditoría de grillas y modelos meteorológicos.**
- Ejecutada en GitHub Actions: 30/45 consultas anuales completas a Open-Meteo. Las 15 no utilizables fueron de ERA5-Land por valores faltantes. Se registró un diagnóstico adicional de valores nulos diarios y horarios (no lluvia cero).
- Para esta muestra, 180/180 pares mensuales de ERA5-Seamless y ERA5 fueron numéricamente iguales pese a coordenadas de respuesta distintas; 60/60 pares de ERA5-Seamless para land y nearest durante 1998 también fueron iguales. NO está demostrada la causa física/geográfica del sesgo.
- El análisis estacional multianual, incluso excluyendo 1998, conserva sobreestimaciones en enero–abril para cinco estaciones. Ver `AUDITORIA_3P.md`, `CONCLUSIONES_3P.md`, `DIAGNOSTICO_ESTACIONAL_3P.md` y `METADATOS_GEOGRAFICOS_3P.md`.

**Fase 3Q: piloto CHIRPS v3 mensual de 1998.**
- Origen oficial: `https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/latam/tifs/`. Descargados y procesados los **12 mapas mensuales oficiales** mediante `scripts/validacion_3q_chirps_1998.py` en GitHub Actions. Extractor geográfico de píxel de 0,05° para cada una de las cinco ubicaciones preliminares.
- Completados **60/60** pares mensuales CHIRPS–SENAMHI, sin incidencias. En 1998, acumulados CHIRPS, en mm: Jayanca **826,757**, Cayaltí **657,559**, Reque **331,993**, Lambayeque **462,126**, Cueva Blanca **1515,965**. Sesgo porcentual anual respectivo: **−42,10 %, +17,74 %, +42,60 %, +65,28 %, +56,41 %**.
- Comparaciones anuales SENAMHI, PISCOp, CHIRPS y ERA5 disponibles en `CHIRPS_3Q_1998.md` y datos `datos/comparacion_3q_chirps_1998.csv`, `datos/metricas_3q_chirps_1998.csv`, `datos/chirps_3q_pixeles_1998.csv`, `datos/estado_3q_chirps.json`.
- El portal pasó a **v0.7** con panel interactivo CHIRPS 1998 y tabla de cuatro fuentes, condicionado a desplegarse correctamente en GitHub Pages.
- **Limitaciones:** un año extremo, ubicaciones históricas sin corroborar, CHIRPS y PISCOp pueden incorporar pluviómetros SENAMHI. Esta prueba NO evalúa capacidad predictiva, independencia ni precisión regional de 30 años.

**Próximo paso 3Q multianual:** ampliar CHIRPS v3 mensual a los **1109 meses-estación completos** de 1996–2015; procesar archivos por bloques anuales o por años con cobertura y guardar métricas comparables exactamente en las mismas fechas para CHIRPS, PISCOp y ERA5. Confirmar coordenadas instrumentales originales antes de interpretar gradientes espaciales. Después integrar análisis CHIRPS de 1996–2025 y, cuando existan observaciones fitosanitarias georreferenciadas, abordar el módulo inicial de arándano.

**Regla:** valores de estaciones faltantes son NaN, no precipitación cero; toda cifra del portal debe indicar observado/estimado/pronosticado y cobertura temporal.

## Cierre Fase 3Q: CHIRPS 1996–2015 · 14/10/2026

**Hito:** se completó una evaluación retrospectiva equitativa SENAMHI–PISCOp v3.0–CHIRPS v3–ERA5-Seamless para los **1 109 meses-estación completos** de cinco estaciones instrumentales SENAMHI, entre 1996 y 2015. Resultaron **3 327 pares estimación–observación**, con 100 % de cobertura de los meses **válidos**; ello equivale a 92,42 % de los 1 200 meses-estación calendario posibles para este intervalo, NO a 100 % de cobertura temporal total. Se excluyeron 35 meses incompletos y 56 sin registros, sin interpretarlos como lluvia cero. Se verificaron coherencia y fechas mediante script de consolidación.

**Fuentes:** CHIRPS v3 mensual LATAM GeoTIFF de Climate Hazards Center; PISCOp y ERA5 ya archivados de la Fase 3O; registros diarios SENAMHI agregados a meses completos. Extracción CHIRPS por píxel de 0,05° que contiene el punto documental preliminar de cada estación. Se reutilizó 1998 y se procesaron bloques 1996–2000, 2001–2005, 2006–2010 y 2011–2015; **sin fallos de descarga reportados**.

**Resultados MAE mensual (mm) · PISCOp, CHIRPS, ERA5:** Jayanca **3,104; 9,154; 104,953** (219 meses); Cayaltí **1,824; 3,712; 15,613** (235); Reque **1,023; 2,986; 7,757** (233); Lambayeque **1,038; 3,394; 11,313** (204); Cueva Blanca **29,257; 30,502; 131,025** (218). PISCOp menor MAE en las cinco estaciones al incluir todos los meses. Al excluir 1998, CHIRPS menor MAE que PISCOp en Cueva Blanca: **28,052 frente a 28,808 mm/mes**; no equivale a superioridad general.

**Archivos de referencia:** `VALIDACION_3Q_1996_2015.md`, `datos/estado_3q_1996_2015.json`, `datos/comparacion_3q_1996_2015.csv`, `datos/metricas_3q_1996_2015.csv`, `scripts/consolidar_3q_1996_2015.py`, además de cuatro scripts/salidas por bloques y `scripts/validacion_3q_chirps_1998.py`. Sitio web actualizado a **v0.9** con explorador de productos, MAE, RMSE, sesgo porcentual y el estrato sin 1998. Verificar que GitHub Pages finalice el despliegue antes de declarar públicamente v0.9.

**Limitaciones científicas:**
- La muestra no cubre observaciones SENAMHI de 2016–2025; todavía no se ha validado el periodo climático completo **1996–2025**.
- La correspondencia espacial y continuidad histórica de los puntos instrumentales tiene coordenadas preliminares, especialmente para Cueva Blanca y pares alternativos de Jayanca, Cayaltí y Lambayeque.
- PISCOp y CHIRPS incorporan información de estaciones: la evaluación sobre estas estaciones puede ser parcialmente dependiente; no es una prueba independiente en parcelas agrícolas.
- No se ha identificado la causa física completa del fuerte sesgo ERA5 ni desarrollado pronóstico o alerta fitosanitaria validada.

**Siguiente fase 3R:** validar fichas oficiales y códigos de las cinco estaciones y analizar sensibilidad de píxeles a ubicaciones candidatas; buscar estaciones/registros independientes (especialmente 2016–2025) y comparar representatividad agroclimática por costa–valle–sierra; después expandir a series CHIRPS y PISCOp 1996–2025 y comenzar un módulo fitosanitario de arándano solo con observaciones de enfermedad en campo, ubicación y fechas reales. Mantener avances en GitHub, sin preguntas ni ejercicios para el usuario.

## Avance Fase 3R: sensibilidad geografica CHIRPS · 14/10/2026

Se procesó un experimento de **24 mapas mensuales de CHIRPS v3** (1998 y 2000), con **dos coordenadas documentales** de cada una de las cinco estaciones. Se obtuvieron **240 extracciones de píxel**, se corroboró que los resultados del punto previamente consultado reproducían CHIRPS v3 de la fase 3Q, y se generaron **10 comparaciones anuales completas**, **sin incidencias**. Las observaciones SENAMHI originales no se cambiaron.

**Resultado esencial:** coordenadas separadas hasta 3,356 km para Jayanca, Lambayeque y Reque estuvieron en **el mismo píxel CHIRPS** (0,05°), con diferencia anual **0 mm** en 1998 y 2000. Para **Cayaltí**, dos puntos separados **2,415 km** dieron distintos píxeles y cambios de **−47,855 mm (1998)** y **−3,961 mm (2000)**. Para **Cueva Blanca**, candidatos separados **6,339 km** dieron distintos píxeles y cambios **+139,802 mm (1998)** y **+138,397 mm (2000)**. En ambas estaciones la comparación se refiere a píxeles, NO a un traslado demostrado.

**Documentación:** `METADATOS_3R.md`, `SENSIBILIDAD_3R.md`, `datos/catalogo_coordenadas_3r.csv`, `datos/sensibilidad_3r_resumen.csv`, `datos/sensibilidad_3r_mensual.csv`, `datos/coordenadas_pixeles_3r_1998_2000.csv`, `datos/estado_3r.json`, `scripts/sensibilidad_geografica_3r.py`. GitHub Actions `OAF Fase 3R sensibilidad geográfica CHIRPS` ejecutó todos los controles con éxito.

**Hallazgos documentales:** SENAMHI publica coordenadas históricas de Jayanca (La Viña), Cayaltí y Reque. Otra ficha SENAMHI identifica EMA La Viña con distinta altitud, sin equivalencia instrumental demostrada. En el caso Cayaltí, un registro SENAMHI de estación convencional código 000320 describe otra posición y altitud que una tabla histórica SENAMHI. En Cueva Blanca existen documentos con códigos 106060 (INGEMMET/CENEPRED) y 153102 (reproducción de tabla ANA) y ubicaciones discordantes; no asignar uno de ellos al TXT original sin soporte.

**Sitio:** se añadió un módulo interactivo **v1.0** para elegir estación y año (1998 o 2000) y visualizar diferencia de píxel, MAE y precipitación anual en coordenadas candidatas. Verificar el workflow de GitHub Pages antes de declararlo desplegado.

**Pendiente dentro de 3R:** corroborar metadatos y códigos desde la ficha de cada archivo TXT SENAMHI, así como cambios de instrumento y emplazamientos en 1996–2015; explorar sensibilidad multianual de puntos donde cambian píxeles; obtener nuevas series instrumentales 2016–2025 y considerar validación independiente, sin adjudicar años faltantes como cero. El servicio de descarga de SENAMHI puede requerir inscripción personal y contraseña, y los archivos históricos recibidos solo alcanzan 2014/2015. La climatología del proyecto **1996–2025** sigue siendo un objetivo por validar, no un periodo instrumental ya corroborado.

**Preferencias:** avanzar directamente con el proyecto científico, sin cuestionarios ni ejercicios para el usuario.

## Cierre de sensibilidad multianual 3R · 14/10/2026

**Auditoría final completada:** Fase 3R amplió la comparación geográfica CHIRPS v3 a **1996–2015**, con cuatro bloques quinquenales, 5 estaciones SENAMHI, **1 109 meses-estación** con precipitación observada completa y **2 218 extracciones de píxel** (dos coordenadas por mes-estación). **No hubo fallos de descarga**. Los 1 109 valores CHIRPS de la posición usada en 3Q se reprodujeron exactamente dentro del criterio de redondeo; las 10 comparaciones del piloto 3R de 1998 y 2000 se reprodujeron también.

**Resultados comparativos** (la diferencia de CHIRPS corresponde al total de meses instrumentales disponibles, nunca a 20 años sin faltantes):
- **Jayanca (219 meses):** 219/219 pares en mismo píxel, cambio acumulado **0 mm**, MAE **9,154 → 9,154 mm/mes**.
- **Cayaltí (235 meses):** 0/235 pares en mismo píxel, cambio acumulado **−195,714 mm**, MAE **3,712 → 3,651 mm/mes**.
- **Reque (233 meses):** 233/233 mismos píxeles, cambio **0 mm**, MAE **2,986 → 2,986**.
- **Lambayeque (204 meses):** 204/204 mismos píxeles, cambio **0 mm**, MAE **3,394 → 3,394**.
- **Cueva Blanca (218 meses):** 0/218 mismos píxeles, cambio acumulado **+1 981,387 mm**, MAE **30,502 → 27,999 mm/mes**.
- **Sensibilidad sin 1998:** Cayaltí MAE **3,394 → 3,140** y Cueva Blanca **28,052 → 24,759 mm/mes**. Estas mejoras no demuestran que las coordenadas candidatas sean correctas.

**Archivos:** `SENSIBILIDAD_3R_MULTIANUAL.md`, `datos/estado_3r_1996_2015.json`, `datos/sensibilidad_3r_1996_2015.csv`, `datos/metricas_sensibilidad_3r_1996_2015.csv`, `scripts/sensibilidad_3r_multianual.py`, `scripts/consolidar_sensibilidad_3r.py`, más los cuatro bloques originales y sus controles en GitHub Actions.

**Portal:** código `index.html` actualizado para **v1.1** con módulo dinámico #sensibilidad3r20. Requiere confirmar despliegue GitHub Pages antes de anunciarlo operativo.

**Metadatos y nuevas series:** Se guardó el borrador **`SOLICITUD_DATOS_SENAMHI_3R.md`** dirigido a SENAMHI. NO se envió ninguna solicitud ni se ingresaron credenciales; requiere identidad/registro del investigador. Pedir fichas oficiales de los cinco TXT y registros disponibles para **2016–2025**, con código de estación, historial de emplazamientos y control de calidad. El enlace oficial de descarga diaria en gob.pe exige cuenta registrada y contraseña SENAMHI.

**Conclusión:** las ubicaciones candidatas de Cayaltí y Cueva Blanca afectan las estimaciones de CHIRPS; Jayanca, Reque y Lambayeque no cambian de píxel en el grid de 0,05° evaluado. La selección del punto definitivo NO puede resolverse con menor MAE. La identidad instrumental de las ubicaciones alternativas sigue sin demostrarse y las estimaciones 1996–2025 no son aún una validación instrumental completa.

**Siguiente tarea (3S o continuación 3R):** cotejo oficial de códigos/cambios de estación, incorporar observaciones disponibles 2016–2025, realizar validación espacial con independencia y estratificación geográfica, y posteriormente construir modelos de riesgo fitosanitario de arándano con datos de sanidad georreferenciados reales.

**Regla de trabajo:** continuar sin cuestionarios ni ejercicios para el usuario; documentar límites y fuentes en web pública.

## Fase 3S — intensidad y estacionalidad de la lluvia · 14/10/2026

**Ejecución verificada en GitHub Actions:** se reutilizaron exactamente **1 109 meses-estación** con lluvia SENAMHI completa y **3 327 pares producto–observación** de 1996–2015 (cinco estaciones, tres productos PISCOp v3.0, CHIRPS v3 y ERA5-Seamless). Se clasificaron exclusivamente según **lluvia OBSERVADA por SENAMHI**: seco **<1 mm/mes**; bajo **1 a <20**; lluvioso **≥20**; intenso **≥50** como SUBGRUPO de lluviosos. Se calculó un segundo estrato excluyendo 1998, estacionalidad de calendario diciembre–abril y mayo–noviembre, MAE, RMSE, sesgo y correlación cuando existía número/variabilidad suficiente. Los umbrales son exploratorios, NO alertas oficiales ni umbrales fitosanitarios.

**Cobertura lluviosa ≥20 mm (sobre meses instrumentales completos):** Cueva Blanca **164/218**, Jayanca **24/219**, Cayaltí **12/235**, Lambayeque **10/204**, Reque **7/233**. Por ello no se debe generalizar la precisión regional con predominancia de meses secos.

**MAE mensual solo en meses observados ≥20 mm — PISCOp/CHIRPS/ERA5 (mm/mes):**
- Cayaltí: **18,209 / 15,841 / 102,753**, 12 meses; **CHIRPS** menor MAE en ese subconjunto, a diferencia de la conclusión sobre todos los meses.
- Cueva Blanca: **37,353 / 38,513 / 170,271**, 164 meses.
- Jayanca: **23,117 / 57,404 / 512,083**, 24 meses.
- Lambayeque: **8,473 / 30,679 / 110,462**, 10 meses.
- Reque: **6,294 / 24,649 / 85,336**, 7 meses.
- Sin 1998 y en meses ≥20 mm, CHIRPS supera ligeramente a PISCOp en Cayaltí (10,522 vs 11,363 mm/mes; 8 meses) y Cueva Blanca (35,403 vs 36,946; 154 meses). Los tamaños y coordenadas instrumentales no permiten declarar superioridad general.

**Clasificación retrospectiva ≥20 y ≥50 mm:** se calcularon VP, VN, FP, FN, precisión, sensibilidad, especificidad y F1, sin confundirse con predicción. Ejemplo: en Cueva Blanca ERA5 F1(≥20)=**0,9159**, aunque su MAE en meses lluviosos es **170,271 mm/mes**: clasificar la presencia de un mes húmedo no equivale a estimar correctamente su precipitación. Se evita comparar F1 donde no hay positivos observados o denominador suficiente.

**Archivos:** `ANALISIS_3S.md`, `scripts/analisis_3s_intensidad.py`, `datos/estado_3s.json`, `datos/cobertura_3s.csv`, `datos/metricas_intensidad_3s.csv`, `datos/metricas_estacionales_3s.csv`, `datos/clasificacion_mensual_3s.csv`. El portal se actualizó en `index.html` a **v1.2**, sección `#intensidad3s`; **verificar el despliegue GitHub Pages antes de anunciarlo como publicado**. El nombre del autor y enlace de contacto previamente solicitados permanecen en cabecera, sección de autoría y pie de página.

**Pendientes científicos (3T):** falta confirmación oficial de identidad y reubicaciones históricas de las cinco estaciones, observaciones instrumentales 2016–2025, evaluación verdaderamente independiente y validación de representatividad por zonas de cultivo. Sin datos de vigilancia de enfermedades de arándano con fecha y localidad NO se puede presentar riesgo fitosanitario operativo. No imputar faltantes como cero. Mantener distinción histórico/estimado/pronosticado.

**Preferencia del usuario:** avanzar directamente en desarrollo, sin cuestionarios ni ejercicios.
