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

## Fase 3T — robustez temporal y preparación de validación independiente · 14/10/2026

**Avance efectivamente ejecutado y verificado:** 1 109 meses-estación SENAMHI completos; 3 327 pares observación-estimación; 92 combinaciones estación-año con al menos 9 meses válidos para los tres productos. Comparación pareada de MAE entre PISCOp y CHIRPS y exploración por remuestreo de años (2 000 repeticiones, semilla fija). Los resultados son retrospectivos y no prueban independencia externa.

**Años evaluables con menor MAE PISCOp / CHIRPS:** Jayanca **18/0**, Cayaltí **19/1**, Reque **20/0**, Lambayeque **16/0**, Cueva Blanca **9/9**; global **82/10 de 92 casos estación-año**. Los años con solo 9–11 meses son evaluables para error mensual, NO para acumulados anuales completos. En Cueva Blanca el rango exploratorio remuestreado de diferencia media de MAE CHIRPS–PISCOp es **[-2,956; +6,569] mm/mes** y atraviesa cero. No inferir precisión espacial independiente ni superioridad universal.

**La independencia externa todavía está pendiente:** 0 de 15 parejas estación-producto tienen prueba documentada suficiente de no participación en insumos de PISCOp, CHIRPS o ERA5, lo cual NO indica que todas participaran. Coordenadas/códigos y periodos originales de estaciones aún no certificados; nuevas observaciones SENAMHI 2016–2025 aún no recibidas.

**Artefactos:** `AUDITORIA_3T.md`, `PROTOCOLO_3T_VALIDACION_EXTERNA.md`, `scripts/auditoria_3t_robustez.py`, `datos/mae_estacion_anio_3t.csv`, `datos/comparacion_anual_piscop_chirps_3t.csv`, `datos/resumen_robustez_3t.csv`, `datos/trazabilidad_independencia_3t.csv`, `datos/estado_3t.json`. GitHub Actions `OAF 3T robustez temporal y trazabilidad` ejecutó los cálculos exitosamente.

**Portal:** código de la versión **v1.3** en `index.html` contiene `#independencia3t`, con selección de estación, años comparados y rango de remuestreo; pendiente confirmar último despliegue GitHub Pages. Se preservaron el autor profesional y el teléfono de contacto solicitados.

**Siguiente trabajo (Fase 3U):** documentar/obtener fichas SENAMHI con código y georreferencia de cada TXT, verificar participación en productos mediante autores/catálogos, conseguir series diarias 2016–2025 por acceso personal autorizado. Solo entonces presentar verificación independiente y eventualmente pasar a modelos agroclimáticos o riesgo fitosanitario de arándano con datos de campo. Evitar la clasificación operativa sin evidencia.

**Norma de trabajo:** seguir secuencia sin cuestionarios ni ejercicios; distinción entre dato observado, estimado y pronosticado.

## Fase 3U — importación SENAMHI 2016–2025: infraestructura y control · 14/10/2026

**Etapa de software completada:** se incorporó un programa Python para integrar en disco local y con trazabilidad archivos TXT diarios originales de SENAMHI, sin publicar automáticamente los datos, `scripts/importar_senamhi_3u.py`. Usa las seis columnas oficiales (año, mes, día, precipitación, Tmax, Tmin), audita fechas, duplicados, códigos de ausentes (incluyendo `-99.9`), valores inválidos y extremos que requieren revisión, y solo calcula la lluvia acumulada mensual si el mes está completo. Conservar **0 mm real** como lluvia cero y datos faltantes como **nulos**. Genera huella SHA256 e informe de calidad por estación en `datos/_privados/3u/`.

**Pruebas y seguridad:** `tests/test_importar_senamhi_3u.py` con **7 pruebas sintéticas**, sin pretender que sean observaciones; pipeline GitHub Actions `.github/workflows/pruebas_3u.yml`. Se creó `.gitignore` que excluye archivos de SENAMHI originales, datos privados, resultados locales y credenciales (`datos/_privados/`, `datos/senamhi_originales/`, `datos/ingesta_3u/`, `.env`). El uso forzado de `git add -f` sigue siendo peligroso; debe evitarse al gestionar datos bajo licencia.

**Estado científico realmente comprobado:** siguen disponibles los **1 109 meses-estación** históricos 1996–2015 y 3 327 pares de producto; se han incorporado **0 archivos diarios nuevos** de 2016–2025 y existen **0 meses-estación nuevos certificados**. Es una situación de recepción de archivos, **no** una afirmación de ausencia de lluvia ni inactividad instrumental. Tampoco están confirmados los códigos originales/emplazamientos ni la independencia de pluviómetros en PISCOp y CHIRPS.

**Fuentes:** servicio SENAMHI de descarga meteorológica diaria con registro y contraseña: https://www.gob.pe/es/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos. Se identificó una opción complementaria de datos abiertos de estaciones automáticas de intercambio internacional en el portal nacional, pero **no se verificó que contenga las cinco series concretas ni se importó**. Solicitud de datos y fichas SENAMHI `SOLICITUD_DATOS_SENAMHI_3R.md` redactada, todavía **no enviada**.

**Documentación de entrega:** `PROTOCOLO_3U_INGESTA_SENAMHI.md`, `datos/estado_3u.json`, importador, pruebas y protección de archivos. Se cargó en `index.html` la **versión v1.4** con un panel `#incorporacion3u` que muestra claramente los datos instrumentales históricos frente a la ausencia de registros nuevos y el estado de verificación. Confirmar ejecución exitosa de GitHub Pages antes de declarar su publicación. Se mantiene autor y número telefónico ya solicitados.

**Próximo trabajo 3V:** cotejo de fichas originales y nuevas observaciones 2016–2025 obtenidas autorizadamente, evaluar cobertura y calidad real de nuevos datos, revisar independencia de pluviómetros en los productos y ampliar validación regional solo si hay observaciones auténticas comparables. Luego continuar hacia modelos agroclimáticos y el módulo fitosanitario de arándano con observaciones sanitarias georreferenciadas. Sin ejercicios ni cuestionarios al usuario.

## Fase 3V — evaluación exploratoria NOAA y nuevas fuentes abiertas · 14/10/2026

**Nueva tarea ejecutada:** se investigaron inventarios de la red **NOAA GHCN-Daily** (`ghcnd-stations.txt`, `ghcnd-inventory.txt`) y el conjunto SENAMHI de estaciones automáticas de intercambio **GBON/RBON** en datosabiertos.gob.pe. Este último está documentado como fuente pública de registros horarios de temperatura, humedad relativa y precipitación, pero aún no se ha descargado, analizado ni demostrado que contenga las cinco estaciones históricas específicas del OAF.

**Inventario NOAA realmente ejecutado en GitHub Actions:** `scripts/inventario_3v_noaa.py`, `.github/workflows/inventario_3v_noaa.yml`, `datos/candidatos_3v_noaa.csv`, `datos/estado_3v_noaa.json`, `INVENTARIO_3V_NOAA.md`. Se buscaron estaciones de Perú a máximo **160 km de cualquiera de los cinco puntos OAF** (criterio geométrico; no significa pertenencia a Lambayeque). Se identificaron **4 candidatas** con rangos de inventario PRCP que solapan 2016–2025, se descargaron sus **4 archivos diarios reales** NOAA y se validaron registros de precipitación excluyendo faltantes `-9999` y valores con `Q_FLAG` de calidad.

**Cobertura NOAA 2016–2025:** estación de aeropuerto José A. Quiñones/Chiclayo, código **PEM00084452**: **263 días PRCP válidos, 0 meses completos**; aeropuerto Armando Revoredo/Cajamarca **PEM00084472**: **1 487 días válidos, 1 mes completo (2025)**; aeropuerto Carlos Martínez de Pinillos/Trujillo, La Libertad, **PEM00084501**: **159 días válidos, 0 meses completos**; aeropuerto Guillermo Concha Ibérico/Piura **PEM00084401**: **218 días válidos, 1 mes completo (2017)**. Total: **2 meses completos dispersos en cuatro candidatos**. Ninguno proporciona una serie anual ni decenal mensual continua para ampliar nuestra validación de Lambayeque. Los nombres de aeropuertos y departamentos se apoyan en fuentes oficiales del MTC; el código NOAA no demuestra identidad con los TXT históricos SENAMHI.

**Limitaciones de independencia:** NOAA integra información de múltiples redes internacionales y fuentes originales, posiblemente estaciones nacionales SENAMHI o GSOD. Por tanto, estos cuatro registros NO se declaran independientes de PISCOp, CHIRPS o de los pluviómetros SENAMHI. La falta de observaciones NOAA completas no implica ausencia de lluvia o ausencia de datos originales en SENAMHI. La delimitación del departamento de Lambayeque no se evaluó mediante polígonos administrativos, por lo que Cajamarca, Piura y La Libertad se mantienen explícitamente diferenciadas.

**Fuentes oficiales y reproducibilidad:**
- NOAA GHCN-Daily: https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily
- Inventario NOAA: https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt y https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt
- GBON/RBON SENAMHI: https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio
- Contraste de geografía aeroportuaria: https://portal.mtc.gob.pe/transportes/aeronautica_civil/empresas_certificadas/Aerodromos.html
- Seguimiento de ingreso instrumental `datos/estado_3u.json`: se mantienen **0 archivos SENAMHI originales nuevos recibidos 2016–2025**.

**Portal:** sección exploratoria `#fuentes3v` añadida a `index.html` versión **v1.5**, conservando autor y teléfono. Esperar verificación de despliegue GitHub Pages antes de indicar publicación exitosa.

**Siguiente fase 3W:** investigar GBON/RBON SENAMHI (metadatos y cobertura horaria real sin suponer continuidad), cotejar con fichas instrumentales y verificar fuentes con registros agrarios regionales autorizados; ampliar 2016–2025 solo con estaciones originales completas y trazabilidad. Paralelamente se pueden seguir analizando productos PISCOp/CHIRPS 1996–2025, pero no presentar nuevos años como validados instrumentalmente sin registros.

## Fase 3W — auditoría GBON/RBON SENAMHI: resultado del CSV público · 14/10/2026

Se descargó y auditó directamente el conjunto de estaciones automáticas GBON/RBON de la Plataforma Nacional de Datos Abiertos, SENAMHI. La ficha del catálogo tiene modificación de **septiembre de 2025**, pero el archivo CSV realmente descargado contiene **408 960 filas**, **46 311 291 bytes**, con fechas de observación entre **2015-01-01 y 2024-04-30**, sin registros de 2025. Fuente: https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio

**Hallazgo crucial y comprobación cruzada:** el CSV contiene **cinco estaciones** (cada una con 81 792 filas), no cientos de miles de estaciones. El campo `ID` enumera **filas y NO es código de estación**. Las cinco son: **Matucana** y **Carania** (Lima/GBON); **Imata** y **San José de Uzuna** (Arequipa/RBON); y **Candarave** (Tacna/RBON). Se verificaron nombre, latitud, longitud, departamento y red en auditoría nacional. El punto más próximo al OAF es **Matucana a 651,75 km de Cayaltí**. No hay estaciones declaradas de **Lambayeque** ni dentro de 160 km de los cinco puntos de referencia de este archivo particular. Esto **NO significa que SENAMHI carezca de estaciones operativas en Lambayeque**; solo que NO se publican en el CSV GBON/RBON examinado.

**Procedimiento y artefactos verificados por GitHub Actions:**
- `scripts/comprobar_acceso_gbon_3w.py`, `datos/estado_3w_acceso.json`: disponibilidad HTTP y encabezado real de 16 campos.
- `scripts/auditar_gbon_rbon_3w.py`, `datos/estado_3w.json`, `datos/estaciones_gbon_rbon_3w.csv`, `AUDITORIA_3W_GBON_RBON.md`: auditoría de fechas y estaciones cercanas, con informe sin registros originales publicados.
- `scripts/inventario_nacional_gbon_3w.py`, `datos/inventario_nacional_gbon_3w.csv`, `datos/estado_geografia_3w.json`: auditoría nacional completa y comprobación del uso de `ID`.
- Workflow de GitHub Actions `OAF 3W auditoria horaria GBON RBON` y `OAF 3W geografia nacional GBON RBON` completados exitosamente después de corregir un cierre prematuro de lectura del CSV y el agrupamiento erróneo inicial por ID.
- Página actualizada en `index.html` versión **v1.6**, nuevo panel `#gbon3w`, conservando autor y teléfono; comprobar el último despliegue GitHub Pages antes de declararlo publicado.

**Límites científicos:** los 408 960 registros no dan cobertura a Lambayeque para ampliar la validación 2016–2025. **No** se han incorporado nuevas observaciones instrumentales de precipitación verificadas al OAF; siguen los **1 109 meses-estación** históricos completos 1996–2015. No se ha validado independencia de PISCOp/CHIRPS. La fecha de modificación del catálogo no equivale a fecha final de observaciones.

**Siguiente etapa 3X:** pasar de catálogos nacionales poco representativos a acceso oficial local SENAMHI (Dirección Zonal 2, Lambayeque) y fuentes sectoriales agrarias con identidad y calidad documental, gestionar solicitud ya preparada `SOLICITUD_DATOS_SENAMHI_3R.md` de fichas y series 2016–2025. Hasta obtener datos auténticos comparables, se puede desarrollar el módulo climático estimado, etiquetándolo como estimación NO validada instrumentalmente para esos años. No enviar solicitudes institucionales ni incluir credenciales/datos personales por cuenta del usuario.

## Fase 3X — fuentes instrumentales locales SENAMHI DZ2 · 14/10/2026

**Hallazgo público verificable:** el mapa de descarga histórica de SENAMHI de Lambayeque enumera por nombre REQUE, CAYALTI, CUEVA BLANCA, JAYANCA (LA VIÑA) y LAMBAYEQUE: https://www.senamhi.gob.pe/mapas/descarga-datos/map_hist_data.php?dp=lambayeque. Esto confirma la existencia de una vía oficial de consulta para las cinco denominaciones; **no prueba continuidad de código/emplazamiento ni disponibilidad de todos los días entre 2016 y 2025**.

**Segunda fuente local:** boletines climáticos DZ2 publicados mediante SENAMHI y gob.pe. Se catalogaron **10 enlaces institucionales** y transcribieron **15 observaciones estación-mes** de **julio 2024, octubre 2024 y febrero 2025** para las cinco denominaciones. Los boletines de SENAMHI son fuentes documentales de acumulados observados, pero NO sustituyen las series TXT diarias. Entre esos 15 registros hay **14 valores numéricos y una anotación no numérica "Traza"** (Cayaltí, octubre 2024), que se conserva como texto y NO se convierte en cero. La revisión visual página por página de los PDFs oficiales, el código instrumental y la identidad histórica siguen pendientes. No sumar estos meses como si fueran una serie 2016–2025 continua.

**Ejemplo de nueva evidencia 2025:** el boletín climático oficial de febrero 2025 de SENAMHI DZ2 (https://www.senamhi.gob.pe/load/file/03601SENA-151.pdf) comunica precipitación observada mensual Jayanca **35,6 mm**, Cayaltí **19,62 mm**, Reque **10,91 mm**, Lambayeque **21,5 mm** y Cueva Blanca **282,3 mm**. Este descubrimiento muestra que la fuente GBON/RBON previamente descartada en fase 3W **NO describe toda la red de observación local de SENAMHI**. La correspondencia exacta con los instrumentos de nuestros cinco TXT históricos no ha sido acreditada.

**Archivos versionados en GitHub:** `datos/fuentes_dz2_3x.csv`, `datos/observaciones_publicadas_dz2_3x.csv`, `FUENTES_DZ2_3X.md`, `scripts/validar_fuentes_3x.py`, `datos/estado_3x.json`; workflow `.github/workflows/auditoria_3x.yml` superó la revisión estructural. Esta revisión comprueba formato, códigos de ausencia, URLs y conteos, **NO verifica visualmente los PDFs ni certifica identidad instrumental**.

**Solicitud técnica SENAMHI:** `SOLICITUD_DATOS_SENAMHI_3R.md` se amplió con evidencia documental 2025, petición de códigos, ficha histórica, reubicaciones y lluvia diaria 2016–2025. No se envió solicitud ni se accedió a cuentas SENAMHI. Portal DZ2 indica atención institucional en Chiclayo y teléfono **(074) 225589**, pero conviene confirmar sede vigente si se gestiona presencialmente.

**Página pública:** se actualizó `index.html` a **v1.7**, nueva sección `#fuentes3x`, conservando el nombre profesional del autor y su teléfono de contacto. Confirmar despliegue GitHub Pages antes de declararlo visible.

**Invariante de integridad:** los **1 109 meses-estación** históricos validados de 1996–2015 siguen sin alteraciones; **0 nuevos meses diarios certificados** 2016–2025. Los boletines son evidencia observada resumida, no prueba de independencia frente a PISCOp/CHIRPS/ERA5.

**Siguiente etapa 3Y:** ampliar con cautela el catálogo documental de boletines DZ2 por año/mes si se dispone de PDF y controles de transcripción; gestionar fichas y TXT diarios originales de SENAMHI; reconstruir la continuidad instrumental verificable, comparar estaciones y píxeles coincidentes sin reemplazar datos reales con grillas; comenzar modelos de riesgo sanitario solo con observaciones de campo fechadas y georreferenciadas. Continuar sin cuestionarios ni ejercicios.

## Fase 3Y — ampliación preliminar de boletines climáticos SENAMHI DZ2 · 14/10/2026

**Resultado científico-documental:** se identificó el compendio institucional que publica los **12 boletines climáticos mensuales del año 2025** de la Dirección Zonal 2 de SENAMHI: https://www.gob.pe/institucion/senamhi/informes-publicaciones/6490504-boletin-climatico-regional-dz2-2025. Su existencia NO garantiza una tabla completa ni una misma estación instrumental en todos los meses.

Se ampliaron los **3 meses documentales** iniciales de fase 3X con **4 meses adicionales** de tablas PP observada indexadas, con fuentes PDF específicas:
- **Septiembre 2024**: `03601SENA-146.pdf` (Jayanca 2,3; Cayaltí **Traza**; Reque 0; Lambayeque 0; Cueva Blanca 30,1 mm).
- **Enero 2025**: `03601SENA-150.pdf` (12,4; 19,0; 9,5; 4,5; 117,2 mm respectivamente).
- **Marzo 2025**: `03601SENA-152.pdf` (33,5; 6,55; 3,9; 11,2; 205,1 mm).
- **Junio 2025**: `03601SENA-155.pdf` (0; 1,4; 0,31; 0; 48,7 mm).
Los datos de **julio y octubre 2024 y febrero 2025** se conservaron idénticos desde fase 3X. Se registran ahora **7 meses documentales, 35 observaciones estación-mes, 33 valores numéricos, 2 Traza y 10 ceros reales**. El control Python comprueba 35 filas, consistencia de enlaces y meses, preservación de las 15 filas originales y distinción entre traza y cero. **Año 2025: 4/12 meses transcritos; 8 pendientes**. NO se completan faltantes con lluvia cero, interpolación o modelos.

**Limitación principal:** los nuevos valores provienen de tablas del texto indexado de los PDF originales; el entorno no pudo recuperar/renderizar todas las páginas PDF para cotejo visual, lo que permanece registrado explícitamente como **pendiente**. Esto permite un catálogo preliminar **no** una base instrumental certificada. El código histórico, coordenadas, posibles cambios de instrumento, horario de medición e independencia frente a PISCOp/CHIRPS siguen sin acreditarse. **0 nuevos meses diarios instrumentales certificados 2016–2025**; los **1 109 meses-estación 1996–2015** conservan su integridad.

**Reproducibilidad en GitHub:** `scripts/actualizar_boletines_3y.py`, `.github/workflows/ampliar_boletines_3y.yml`, `datos/observaciones_documentales_dz2_3y.csv`, `datos/matriz_boletines_2025_3y.csv`, `datos/estado_3y.json`, `BOLETINES_DZ2_3Y.md`. El programa se ejecutó en GitHub Actions con resultado correcto y datos cotejados estructuralmente contra los 15 anteriores.

**Observatorio público:** `index.html` actualizado a **v1.8**, nuevo módulo `#boletines3y` para explorar los meses documentados de 2024 y 2025, con enlaces a fuentes y advertencias de incertidumbre. **Comprobar el despliegue GitHub Pages** antes de declararlo finalizado. El autor y contacto permanecen sin alteraciones.

**Punto de continuidad:** seguir extrayendo solo tablas verificables de los **8 boletines restantes de 2025** (y eventualmente 2024) con revisión visual e identificación instrumental; en paralelo tramitar acceso autorizado a registros diarios completos SENAMHI. Solo entonces estudiar su emparejamiento con PISCOp, CHIRPS y ERA5, señalando debidamente la posible dependencia de pluviómetros. No iniciar predicciones ni alertas de enfermedades de arándano sin observaciones de campo georreferenciadas.
