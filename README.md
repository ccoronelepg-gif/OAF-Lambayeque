# OAF-Lambayeque 2.0
### Observatorio Agroclimático y Fitosanitario de Lambayeque, Perú

**Autor:** ING. AGRÓNOMO CARLOS ENRIQUE CORONEL GARCÍA  
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/


## Actualización del portal · 14/10/2026

La página pública [OAF-Lambayeque 2.2](https://ccoronelepg-gif.github.io/OAF-Lambayeque/) incorpora:

- Biblioteca consultable para **arándano y vid**, con nueve enfermedades, variables meteorológicas, rangos publicados, nivel de respaldo y enlaces directos a estudios y guías técnicas.
- Módulo visible de **boletines ENFEN** con comunicado N.º 17-2026 (verificado al 14/10/2026), acceso a archivos institucionales y al registro de monitoreo automatizado con sus limitaciones.
- Consulta horaria experimental para **Jayanca, Motupe, Olmos y Chiclayo**, con años completos 2023–2025, usando ERA5-Land (temperatura/HR) y ERA5 (precipitación) a través de Open-Meteo, exportación CSV y tratamiento explícito de fallos y datos faltantes.
- Conservación de todas las secciones de validación, CHIRPS, SENAMHI y datos históricos existentes.

Los índices no son alertas operativas ni permiten diagnosticar enfermedades. El navegador necesita acceso a la API de terceros para obtener datos horarios.

## Interfaz pública simplificada · 14/10/2026

**Sitio:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/

La portada se reorganizó en cinco pestañas exclusivas:
1. Cultivos y condiciones de riesgo de patologías: tabla de tres columnas (enfermedad, condiciones climáticas y cultivo), con nueve patologías y fuentes.
2. Boletines de El Niño: enlaces ENFEN/SENAMHI, consulta al registro institucional y estado de verificación sin suponer alerta vigente.
3. Datos climáticos: consulta modelada de tiempo reciente y pronóstico externo a siete días para cuatro localidades, más última disponibilidad CHIRPS.
4. Riesgo de presencia de enfermedades: estado de los modelos, requisitos y advertencia de que no existen alertas OAF operativas.
5. Verificaciones de datos: resumen de calidad, cobertura histórica y enlace al portal anterior conservado en [archivo-analisis-historico.html](archivo-analisis-historico.html).

El nuevo diseño reduce información redundante; la página histórica de 2026 se mantiene íntegra. Las imágenes públicas proceden de Wikimedia Commons (Scott Bauer/USDA y Panelxf, CC0/dominio público). Las cifras de estado de fuente se cargan desde los JSON mantenidos en este repositorio. El pronóstico de Open-Meteo **no es un modelo predictivo propio del OAF**.

## Interfaz OAF actualizada · 14/10/2026

La navegación pública se ordena de izquierda a derecha en cinco secciones:

1. **Inicio:** propósito del proyecto, fuentes utilizadas, evaluación de calidad, modelos científicos y validación futura.
2. **Datos climatológicos:** meteorología modelada reciente, perspectiva a siete días de Open-Meteo, disponibilidad de precipitación CHIRPS y distinción de predicciones propias en desarrollo.
3. **Cultivos y riesgo de enfermedades:** tabla compacta de tres columnas con las nueve enfermedades de arándano y vid, bibliografía científica y resumen de modelos experimentales sin alertas operativas.
4. **Boletín de El Niño:** comunicados de ENFEN y avisos SENAMHI; el estado se publica únicamente si es verificable.
5. **Verificación de datos:** cobertura y control de calidad, archivo original íntegro en [archivo-analisis-historico.html](archivo-analisis-historico.html).

La web preserva los enlaces directos anteriores a `#cultivos` y redirige la pestaña antigua `#riesgos` a esa sección, sin duplicación de información.

## Fase 5 · Primer indicador térmico experimental (14/10/2026)

En [Cultivos → Predicción fitosanitaria](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos) se incorporó la consulta de pronóstico horario externo para Motupe, Jayanca, Olmos y Chiclayo, y una evaluación **exploratoria** del patrón térmico asociado con la fase conidial del oídio de la vid (*Erysiphe necator*) según UC IPM. Procesa siete jornadas futuras completas, cuenta horas continuas dentro del intervalo favorable y detecta secuencias de tres días consecutivos. Un vacío de datos hace no evaluable la jornada.

**No es una predicción validada de presencia de enfermedad ni un índice completo de UC IPM:** se usan temperaturas a 2 m, no datos del dosel, y se desconoce la infección primaria. No se recomienda tratamiento fitosanitario. La API externa se consulta cuando el visitante abre el módulo y su disponibilidad no está garantizada.

La implementación reproducible está en [modelos/oidio_vid_indicador_termico.py](modelos/oidio_vid_indicador_termico.py), con cuatro escenarios sintéticos de prueba. [Método, limitaciones y plan de validación](MODELO_TERMICO_OIDIO_VID_FASE5.md).

## Prioridad científica: dos sistemas de predicción (precisión del autor, 14/10/2026)

**No se trata solo de monitorear ni de reunir boletines.** La finalidad del proyecto es investigar, construir y evaluar dos tipos de predicción:

- **Anomalías agroclimáticas y El Niño Costero:** probabilidades o escenarios futuros de lluvia, temperatura y humedad anómalas, junto con evolución oceánica/atmosférica ligada a El Niño Costero y su posible impacto regional. El estado oficial pertenece a ENFEN; todo pronóstico OAF debe validarse y distinguirse de escenarios ajenos.
- **Enfermedades de arándano y vid:** modelos separados por patógeno y cultivo que incorporen pronósticos meteorológicos, microclima, fenología y observación sanitaria. No se equipara clima favorable a diagnóstico ni a probabilidad calibrada.

**Condición para publicación de pronósticos OAF:** guardar predicciones con fecha anterior al evento, medir habilidad frente a referencias, errores e incertidumbre, y no declarar operatividad hasta contar con validación externa o prospectiva suficiente.

## Fase 6A · Comparación predictiva de anomalías climáticas (14/10/2026)

En [Datos climatológicos del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), el nuevo módulo experimental compara temperaturas medias y lluvias previstas para 7 jornadas futuras con una referencia por época del año del periodo **1996–2025**. Para temperatura se identifican días previstos por encima de P90 o por debajo de P10 histórico; para precipitación se contrasta la suma de 7 días con el P90 de acumulados históricos equivalentes. Los datos históricos se consultan bajo demanda como reanálisis ERA5-Land (temperatura) y ERA5 (precipitación); el pronóstico es **externo de Open-Meteo**, no un modelo meteorológico propio. La comparación no equivale a probabilidad calibrada ni a alerta oficial.

- Código probado con datos sintéticos: [modelos/anomalias_climaticas_v01.js](modelos/anomalias_climaticas_v01.js).
- Método científico y limitaciones: [MODELO_ANOMALIAS_FASE6A.md](MODELO_ANOMALIAS_FASE6A.md).
- Diez verificaciones de lógica superadas: señales normales/cálidas/lluviosas, referencia de 30 años y umbrales mínimos de 25/24 años, registros faltantes, cambio de año y bisiestos. **No constituyen validación con observaciones meteorológicas reales**.
- El apartado **Boletín de El Niño** incluye una hoja de ruta predictiva específica Niño 1+2/ICEN. No se afirma que el OAF prediga ya El Niño Costero; ese modelo y su validación siguen pendientes.

**Próxima prioridad:** construir una serie oceánico-atmosférica verificable de Niño 1+2 e ICEN y un primer modelo base de predicción frente a persistencia y escenarios institucionales; en paralelo validar indicadores fitosanitarios con observaciones de campo.

## Fase 6B · Primera predicción oceánica experimental Niño 1+2 (14/10/2026)

**Objetivo de investigación:** anticipar una anomalía mensual oceánica Niño 1+2, como paso hacia un sistema de predicción de posibles episodios de El Niño Costero, y evaluar objetivamente si un modelo propio supera la persistencia. **No se afirma que este primer modelo prediga El Niño Costero o sea el índice ICEN oficial.**

- **Fuente real descargada:** [NOAA CPC OISST v2.1 Niño 1+2](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices), serie continua desde enero de 1982 hasta septiembre de 2026. Se distinguen en todo momento NOAA OISST y el **ICEN/ERSSTv5 oficial de ENFEN**.
- **Última anomalía NOAA:** septiembre de 2026, **+4,69 °C**.
- **Modelo de anomalía a un mes (octubre de 2026):** AR(1) experimental **+4,35 °C**; persistencia **+4,69 °C**. No son probabilidades, clasificaciones ENFEN ni avisos climáticos para Lambayeque.
- **Walk-forward con 200 pronósticos retrospectivos (2010–2026):** MAE AR(1) **0,3749 °C**, persistencia **0,3797 °C**; diferencia favorable **~1,26 %**, demasiado reducida para proclamar habilidad consolidada.
- **Últimos 12 meses:** MAE AR(1) **0,5818 °C** frente a **0,4708 °C** de persistencia (el AR1 empeora un **23,56 %**). El intervalo exploratorio del remuestreo por bloques incluye cero: NO se ha demostrado mejor desempeño robusto.
- **Archivos y método:** [MODELO_NINO12_FASE6B.md](MODELO_NINO12_FASE6B.md), [Python](modelos/modelo_nino12_fase6b.py), [workflow automático de GitHub Actions](.github/workflows/oaf_nino12_fase6b.yml), [serie NOAA](datos/noaa_nino12_oisst_mensual.csv), [evaluación mensual](datos/nino12_backtest_walkforward.csv), [salida JSON](datos/modelo_nino12_experimental.json).
- **Página:** [Boletín de El Niño → evaluación oceánica experimental](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino). Se conserva la fuente y estado oficial ENFEN por separado.

**Siguiente fase:** incorporar la serie ERSSTv5/ICEN conforme a la definición oficial actualizada, variables de viento y océano subsuperficial, y un conjunto histórico de pronósticos fechados para evaluación prospectiva. Persistencia seguirá siendo el modelo de referencia que debe superarse; ninguna alerta OAF se emitirá hasta validar los modelos.

## Fase 6C · ERSSTv5 Niño 1+2 y comprobación documental (14/10/2026)

La nueva sección plegable en [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino) incorpora una serie real **ERSSTv5 NOAA 1950-01 a 2026-06** y la evaluación histórica de modelos AR(1) a **1, 2 y 3 meses** frente a persistencia, además de un promedio móvil de tres meses **indicativo, no ICEN oficial**.

- **Control de vigencia:** el archivo ERSSTv5 NOAA tiene **4 meses de desfase respecto de octubre 2026**. Se guardan históricos y evaluaciones; **se bloquean todas las proyecciones actuales** (`prediccion_actual_disponible=false`), sin sustituir los últimos meses por datos OISST.
- **Backtest retrospectivo:** 197, 196 y 195 predicciones verificadas respectivamente. MAE AR(1) = **0,3449 / 0,4952 / 0,6183 °C** a 1/2/3 meses y MAE persistencia = **0,3546 / 0,5282 / 0,6823 °C**. Las mejoras globales NO prueban validez prospectiva; a uno y dos meses el AR(1) empeora en los últimos 12 meses.
- **Control institucional externo, no validación operativa:** se contrastaron ICEN publicados por SENAMHI de febrero, marzo, abril y mayo de 2026 con promedios trimestrales indicativos ERSSTv5 del OAF. Diferencia absoluta media de **0,0075 °C** en esos cuatro registros. Fuentes de SENAMHI enlazadas en el informe.
- **Documentos:** [MODELO_ERSSTV5_FASE6C.md](MODELO_ERSSTV5_FASE6C.md), [código Python](modelos/modelo_ersstv5_nino12_fase6c.py), [contraste institucional CSV](datos/contraste_icen_publicado_2026.csv) y [datos/modelo_ersstv5_nino12_6c.json](datos/modelo_ersstv5_nino12_6c.json).
- **Próximo paso Fase 6D:** localizar ERSSTv5/ICEN actuales de fuente institucional, ampliar contraste de meses y probar ERSSTv6 como producto distinto; iniciar evaluación de predicciones emitidas y archivadas realmente antes de cada evento.

## Fase 6D · Fuente NOAA NCEI ERSSTv5 recuperada y predicción experimental (14/10/2026)

**Resuelto el desfase de datos sin confundir índices.** NOAA NCEI mantiene una serie ERSSTv5 Niño 1+2 actualizada a **septiembre de 2026**, pero sus anomalías están calculadas frente a **1971–2000**. El OAF toma la **sexta columna** (Niño 1+2), calcula mes a mes la media de anomalías durante 1991–2020 y la resta para crear una serie de anomalías **reajustada por el OAF a 1991–2020**. Esta serie es *derivada*, **no un ICEN oficial**.

- Última anomalía mensual derivada: **+4,389 °C, septiembre de 2026**.
- Comparación interna con el archivo CPC ERSSTv5: 918 meses comunes; **MAE entre productos últimos 24 meses comunes: 0,0397 °C**. El control de procedencia pasó. No confundir este MAE de comparación entre fuentes con error predictivo.
- Modelo experimental AR(1) a uno, dos y tres meses: **+4,054 °C (octubre), +3,744 °C (noviembre) y +3,456 °C (diciembre de 2026)**. Referencia trivial de persistencia: **+4,389 °C** en los tres horizontes.
- Aunque el error histórico medio del AR(1) es ligeramente menor que el de persistencia, **el AR(1) es peor en los últimos doce meses a los tres horizontes**; ninguna estimación es considerada una predicción validada de El Niño Costero, lluvia regional o enfermedad agrícola.
- [Informe Fase 6D](MODELO_NCEI_ERSSTV5_FASE6D.md), [motor Python](modelos/modelo_ncei_ersstv5_fase6d.py), [fuente reajustada CSV](datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv), [evaluación walk-forward CSV](datos/ncei_ersstv5_backtest_1a3m.csv), [salida JSON](datos/modelo_ersstv5_ncei_6d.json), [flujo GitHub Actions](.github/workflows/oaf_ncei_ersstv5_fase6d.yml).
- Nuevo panel plegable en [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino). Conserva aparte el panel Fase 6C con su fuente CPC de junio 2026, identificada como histórica y desactualizada.

**Próximo avance recomendado — Fase 6E:** añadir predictores oceánico-atmosféricos de fuentes públicas, generar pronósticos verdaderamente fechados y compararlos prospectivamente con persistencia y modelos de referencia institucional. Sin esta evaluación **no existe predicción OAF operativa**.

## Fase 6E · Nuevas variables agroclimáticas: radiación solar y microclima (14/10/2026)

Se amplió [Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima) con variables **modeladas y pronosticadas por Open-Meteo** para Chiclayo, Jayanca, Motupe y Olmos:

- **Radiación solar global de onda corta:** `shortwave_radiation` actual (W/m²) y `shortwave_radiation_sum` diario (MJ/m²). No confundir con PAR, UV ni sensor en dosel.
- **Déficit de presión de vapor (DPV):** actual y máximo diario (kPa).
- **Viento a 10 m:** actual y máximo diario (km/h).
- **Humedad relativa:** actual y promedio diario (%).
- **ET₀ FAO:** evapotranspiración de referencia diaria (mm), no evapotranspiración real del cultivo.
- **Presión atmosférica superficial:** actual (hPa), no índice SOI.
- **Insolación estimada:** horas diarias de brillo solar, distintas del acumulado de energía.
- Temperatura, precipitación y probabilidad de precipitación se mantienen.

**Análisis de anomalías solares:** el indicador 1996–2025 ahora compara la radiación prevista acumulada en siete días con valores estacionales históricos (ventana ±15 días, P10/P90, ≥25 años válidos). Fuente de **radiación y lluvia: ERA5**, temperatura **ERA5-Land**, según comprobación de disponibilidad con GitHub Actions. Una ausencia de radiación deja su comparación **no evaluable**, sin fabricar ceros ni impedir interpretar separadamente temperatura/lluvia.

**Control con datos reales:** dos localidades pasaron comprobación de variables, formatos y unidades de pronóstico; en octubre de 2019 se encontraron 31/31 valores radiativos con ERA5 y 0/31 con ERA5-Land. El ensayo completo para Motupe confirmó **10.958/10.958 días numéricos de radiación ERA5, lluvia ERA5 y temperatura ERA5-Land durante 1996–2025**. Se corrigió y verificó la fuente histórica usada por el indicador. Ver [metodología y catálogo de variables de Fase 6E](VARIABLES_AGROCLIMATICAS_FASE6E.md) y [pruebas de consulta](tests/test_variables_agroclimaticas_6e.py).

**El próximo uso predictivo no será automático:** radiación, DPV, viento y humedad servirán como covariables candidatas solo después de evaluar errores y utilidad real. La humedad relativa **no sustituye** la duración medida de humectación foliar requerida para modelos de Botrytis. Las variables de meteorología local tampoco sustituyen señales oceánicas/atmosféricas de El Niño Costero.

## Fase 6F · Evaluación del valor predictivo de la radiación (14/10/2026)

Se creó un experimento cuantitativo para comprobar **si incorporar radiación solar, humedad relativa y viento mejora o empeora** el pronóstico de temperatura. A diferencia de una simple regresión sobre observaciones del mismo día, utiliza **predictores de pronósticos archivados con 24 horas de antelación** de Open-Meteo (Previous Runs API); la variable objetivo es temperatura reanalizada por ERA5-Land.

- Tres alternativas comparadas: (A) pronóstico anterior sin corregir, (B) corrección Ridge básica con temperatura y componentes horarios/estacionales, (C) mismo modelo Ridge más radiación, humedad y viento. Regularización fija y normalización aprendida exclusivamente del entrenamiento.
- Entrenamiento 2024–2025; evaluación temporal aislada enero–septiembre 2026; Chiclayo, Jayanca, Motupe y Olmos. Métricas MAE, RMSE, sesgo y remuestreo temporal en bloques; publicar honestamente resultados mejores o peores.
- Prueba de API real en Motupe: **120 horas archivadas para cada predictor y 120 horas equivalentes de referencia**, coincidentes; GitHub Actions lo confirmó.
- Código [benchmark_radiacion_6f.py](modelos/benchmark_radiacion_6f.py), [metodología](FASE_6F_EVALUACION_PREDICTORES.md), [flujo de evaluación](.github/workflows/oaf_benchmark_radiacion_6f.yml) y panel plegable en [Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima).
- Archivos de salida cuando la evaluación termine correctamente: [benchmark_variables_6f.json](datos/benchmark_variables_6f.json) y [errores mensuales](datos/benchmark_variables_6f_mes.csv).
- Este experimento **no constituye aún predicción validada de El Niño Costero ni enfermedades**, y su referencia ERA5-Land es reanálisis, no medición SENAMHI. Los modelos fitosanitarios requieren datos de campo adicionales.

## Fase 6F — Hallazgos iniciales y archivo prospectivo (14/10/2026)

La comparación con pronósticos efectivamente emitidos **24 horas antes** encontró que agregar radiación, humedad y viento disminuyó el MAE de temperatura corregida frente al modelo básico en **Chiclayo (5,95 %) y Olmos (4,97 %)**, pero lo aumentó en **Jayanca (24,38 %) y Motupe (2,11 %)**. Se entrenó con 2024–2025 y se evaluaron 6.552 horas por localidad de enero–septiembre 2026; la referencia es ERA5-Land reanalizado, no sensores SENAMHI. El pipeline generó métricas, pero el primer envío de archivos falló por cambios concurrentes en Git; se corrigió su proceso de publicación. Las variaciones no validan modelos operativos ni atribuyen causalidad a una variable específica.

También quedó registrada **la primera emisión prospectiva real**, correspondiente al 14/10/2026 en Perú, con pronósticos externos del 15 al 21 de octubre para las cuatro localidades: [consultar JSON emitido](datos/pronosticos_emitidos/2026-10-14.json). Incluye temperatura, precipitación, radiación, humedad, viento, DPV y ET₀ con fecha y unidades; permitirá verificar errores una vez sucedan las jornadas previstas. [Método y resultados de Fase 6F](FASE_6F_EVALUACION_PREDICTORES.md).

## Fase 6G · Verificación de pronósticos emitidos antes del evento (15/10/2026)

El OAF ya no solo archiva pronósticos: se implementó una **verificación prospectiva automatizada por fecha de emisión, localidad y horizonte**. Se comprueba temperatura media, precipitación y radiación solar pronosticadas para los siguientes 7 días frente a reanálisis **ERA5-Land (temperatura) y ERA5 (lluvia y radiación)**, con un margen de siete días después de la jornada válida por el retraso de publicación de aproximadamente cinco días.

- El primer pronóstico conservado se emitió el **14/10/2026 en horario Perú** y cubre del 15 al 21 de octubre para Chiclayo, Jayanca, Motupe y Olmos.
- [Estado actual de la evaluación prospectiva](datos/evaluacion_prospectiva_6g.json): **pendiente de reanálisis; 0 de 28 jornadas disponibles**, primera fecha posible de verificación **22/10/2026**. No se declaran aciertos, errores cero ni predicciones verificadas hasta obtener datos.
- [Motor de verificación](modelos/verificar_pronosticos_emitidos_6g.py), [proceso diario](.github/workflows/oaf_verificacion_6g.yml), [CSV auditable](datos/evaluacion_prospectiva_6g.csv) y [metodología](FASE_6G_VERIFICACION_PROSPECTIVA.md).
- Nuevo apartado plegable **Fase 6G** en [Datos climatológicos del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), con futura consulta de MAE, RMSE y sesgo por variable, localidad y horizonte.

**Corrección final de Fase 6F:** el último GitHub Actions terminó exitosamente y publicó [benchmark_variables_6f.json](datos/benchmark_variables_6f.json) y [errores mensuales](datos/benchmark_variables_6f_mes.csv). Los intervalos exploratorios de mejora ampliado vs básico por bloques fueron: Chiclayo **−2,73 % a +15,33 %**, Jayanca **−42,69 % a −9,52 %**, Motupe **−5,48 % a +1,86 %**, Olmos **+1,65 % a +10,14 %**. Solo Olmos presentó mejora positiva en ambos extremos de ese intervalo exploratorio. Un intervalo descriptivo y ERA5-Land como referencia NO equivalen a validación operativa.

## Misión

Construir un observatorio cuyo **objetivo principal es predecir**, de manera progresiva y científicamente verificable, **(1) posibles anomalías climáticas en Lambayeque, incluidos episodios y evolución de El Niño Costero**, y **(2) condiciones de riesgo y, tras validación, posible ocurrencia de enfermedades agrícolas en arándano y vid**. Integra observaciones, pronósticos oceánico-atmosféricos, bibliografía científica, datos fitosanitarios y evaluación independiente. Los gráficos, boletines y datos históricos sirven para desarrollar y evaluar esas capacidades predictivas.

**Estado actual:** la nueva arquitectura está **planificada**, no constituye aún un sistema de predicción propio validado, ni emite alertas climáticas o fitosanitarias operativas.

## Cuatro fases prioritarias

| Fase | Objetivo | Estado |
|---|---|---|
| **3Z** | Modernizar fuentes oficiales, monitoreo reciente y trazabilidad ENFEN/SENAMHI/satélites | **En progreso · CHIRPS v3 integrado** |
| **4A** | Modelos de anomalías y pronósticos probabilísticos meteorológicos | Pendiente |
| **4B** | Riesgo fitosanitario de arándano basado en condiciones y observaciones de campo | Pendiente |
| **4C** | Evaluación prospectiva, validación independiente y comunicación de alertas | Pendiente |

Plan detallado: [PLAN_MAESTRO_OAF_2_0.md](PLAN_MAESTRO_OAF_2_0.md).  
Protocolo de estados y alertas: [PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md](PROTOCOLO_ESTADOS_Y_ALERTAS_OAF_2_0.md).  
Catálogo de fuentes priorizadas: [datos/catalogo_fuentes_operativas_3z.csv](datos/catalogo_fuentes_operativas_3z.csv).  
Plan de fases legible por máquinas: [datos/plan_operativo_oaf_2_0.json](datos/plan_operativo_oaf_2_0.json).

## Fase 3Z — primera fuente reciente en producción de datos (14/10/2026)

**CHIRPS v3:** se descargaron y verificaron archivos GeoTIFF mensuales de octubre de 2025 a agosto de 2026 (11 meses, 55 estimaciones de píxel para cinco puntos referenciales del OAF). **Septiembre de 2026 todavía no estaba publicado** en la URL de consulta y quedó como faltante. Se preservaron el SHA-256 de los rasters, la fecha UTC de consulta, ubicación exacta de la celda, resoluciones y URLs. CHIRPS es una **estimación espacial mezclada satélite/pluviómetros**, no una observación SENAMHI ni un pronóstico.

**ENFEN:** está preparado el sistema semanal de verificación de comunicados, pero el servidor ENFEN no resolvió DNS durante la primera ejecución en GitHub Actions. La aplicación muestra `no_verificado` y enlaza directamente a [comunicados ENFEN](https://enfen.imarpe.gob.pe/comunicados/); **no inventa** un estado actual ni emite alertas propias.

**Automatización:** dos GitHub Actions los lunes para CHIRPS y ENFEN; el resultado del último monitoreo se expone en el [panel 3Z del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#monitoreo3z). La actualización depende de la disponibilidad de las fuentes y los despliegues de GitHub Pages, no es un servicio garantizado en tiempo real.

Archivos: [monitoreo CHIRPS](MONITOREO_CHIRPS_RECIENTE_3Z.md), [CSV reciente](datos/chirps_v3_reciente_3z.csv), [auditoría](datos/auditoria_rasters_chirps_3z.json), [estado CHIRPS](datos/estado_monitoreo_3z.json), [informe ENFEN](MONITOREO_ENFEN_3Z.md) y [estado ENFEN](datos/estado_enfen_3z.json).

## Datos y transparencia científica

- El observatorio conserva las fases históricas **3N–3Y** y todos sus datos originales y cálculos reproducibles.
- Base SENAMHI aportada: **1 109 meses-estación observados completos, 1996–2015**; 79 combinaciones estación-año completas y último año completo común **2012**. Se requieren fichas instrumentales adicionales para confirmar códigos y emplazamientos históricos.
- Se analizaron retrospectivamente PISCOp v3, CHIRPS v3 y ERA5-Seamless sobre meses completos históricos; no está demostrada independencia externa en los 15 pares estación-producto.
- Los valores mensuales publicados en boletines DZ2 de 2024–2025 se conservan por separado como evidencia documental preliminar, sin transformarlos en series diarias completas.
- **No se imputan días/meses faltantes ni se publica un acumulado anual observado de años incompletos.** La vigilancia de un día o semana recientes **sí puede realizarse** con datos realmente disponibles y de calidad verificada, sin esperar que termine el año.
- CHIRPS, IMERG y otros gridded son **estimaciones**, los modelos pronosticados son **pronósticos** y los pluviómetros son **observaciones instrumentales**: nunca se confunden.
- Las alertas oficiales sobre El Niño Costero corresponden a **ENFEN** y los avisos meteorológicos oficiales a **SENAMHI**. El OAF enlazará esas fuentes fechadas y evitará emitir alertas propias hasta demostrar validez.

Política histórica: [CRITERIO_COBERTURA_OFICIAL.md](CRITERIO_COBERTURA_OFICIAL.md).  
Resultados de cobertura: [RESULTADO_COBERTURA_OFICIAL.md](RESULTADO_COBERTURA_OFICIAL.md).  
Bitácora técnica completa: [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md).

## Fuentes institucionales a integrar en Fase 3Z

- **ENFEN** — https://enfen.imarpe.gob.pe/comunicados/
- **SENAMHI** — https://www.senamhi.gob.pe/
- **CHIRPS v3 (Climate Hazards Center)** — https://www.chc.ucsb.edu/data/chirps3
- **NASA GPM / IMERG** — https://gpm.nasa.gov/data/imerg
- **ECMWF** — https://www.ecmwf.int/en/forecasts

Estas fuentes tienen estados distintos: **CHIRPS v3 mensual ya está conectado**, con una actualización semanal programada y extracción real comprobada hasta agosto de 2026. La consulta ENFEN está implementada, pero su última ejecución **no pudo resolver el servidor institucional**, de modo que se muestra como no verificada y requiere revisar directamente el comunicado oficial. Las demás fuentes recientes aún no están integradas; no se deben anunciar como activas.

## Herramientas

Python, análisis estadístico, GitHub Actions, sensores remotos y SIG, con énfasis en **bajo presupuesto**, control de calidad, accesibilidad pública y aplicaciones en sanidad vegetal. La precisión dependerá de la calidad de los datos, no de presentar un modelo complejo.

---
*Proyecto científico en desarrollo. Ninguna visualización experimental sustituye los comunicados ENFEN, avisos SENAMHI ni el diagnóstico agronómico en campo.*
