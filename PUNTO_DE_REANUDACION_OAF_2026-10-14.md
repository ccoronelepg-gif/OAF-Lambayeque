# Punto de reanudación del OAF-Lambayeque — 14 de octubre de 2026

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.
**Sitio público:** https://ccoronelepg-gif.github.io/OAF-Lambayeque/
**Repositorio:** https://github.com/ccoronelepg-gif/OAF-Lambayeque

## Objetivo del proyecto
Desarrollar el Observatorio Agroclimático y Fitosanitario de Lambayeque como un **sistema predictivo con dos objetivos científicos principales**: **(1) anticipar posibles anomalías climáticas en Lambayeque, especialmente eventos y evolución de El Niño Costero, además de anomalías de lluvia, temperatura y humedad**, y **(2) predecir condiciones de riesgo de enfermedades agrícolas en arándano y vid**, integrando información climática, variables agronómicas y registros sanitarios de campo. El propósito es ofrecer predicciones anticipadas, probabilísticas, fechadas y verificables para mejorar la prevención y las decisiones de productores y profesionales. La vigilancia y el análisis histórico son la base, **no el resultado final**.


## Precisión estratégica final del autor (14/10/2026)

**Meta principal de todo el proyecto: PREDICCIÓN, no únicamente vigilancia o visualización.** El OAF deberá evolucionar hacia dos sistemas predictivos diferenciados pero relacionados:

1. **Predicción agroclimática:** estimar con anticipación la ocurrencia, intensificación o persistencia de anomalías de lluvia, temperatura y humedad en Lambayeque, prestando especial atención a **posibles episodios de El Niño Costero**. Para este fenómeno no basta procesar lluvia local: se necesitarán observaciones y predicciones oceánicas/atmosféricas, anomalía de TSM en Niño 1+2, índices y escenarios ENFEN, además de modelos de referencia. Distinguir pronósticos externos de predicciones originales del OAF. Empezar con modelos sencillos y avanzar a modelado probabilístico solo cuando existan datos adecuados.
2. **Predicción fitosanitaria:** estimar anticipadamente las condiciones favorables o, posteriormente, probabilidades calibradas de ocurrencia de enfermedades de **arándano y vid** con variables climáticas, fenología, datos de campo y modelos epidemiológicos validados localmente. Los primeros focos son Botrytis/antracnosis en arándano y oídio/mildiu en vid.

**Cadena de valor:** datos y monitoreo → pronóstico de anomalías climáticas → estimación de condiciones favorables para patógenos → predicción fitosanitaria calibrada → comunicación preventiva, con sello temporal y niveles explícitos de incertidumbre.

**Requisitos obligatorios antes de declarar éxito:** pronósticos emitidos antes del evento, comparación contra una referencia ingenua/institucional, evaluación temporal fuera de muestra, seguimiento de falsas alarmas, incertidumbre, verificación independiente y evidencia de campo cuando aplique. Los comunicados ENFEN continúan siendo el estado **oficial**, mientras que cualquier pronóstico propio sobre El Niño Costero debe identificarse como experimental hasta demostrar habilidad predictiva. No presentar el OAF como capaz de predecir El Niño o enfermedades antes de completar esta validación.

## Último avance: Fase 7B · ¿La humedad pronosticada se confirma? (15/10/2026)

**Objetivo:** evaluar científicamente la capacidad real del indicador HR >90 % durante ≥6 horas para anticipar episodios de humedad en Lambayeque, y evitar llamarlo «predicción de enfermedad» sin datos de infección por *Botrytis*.

**Benchmark histórico ejecutado con éxito:** Open-Meteo Previous Model Runs `relative_humidity_2m_previous_day1` (nominal 24 h antes) contrastado con HR horaria ERA5, enero–septiembre 2026, 273 jornadas y 6.552 horas coincidentes por localidad. Se evaluó matriz binaria de verdaderas coincidencias meteorológicas, falsas señales, omisiones y coincidencias negativas:
- **Chiclayo:** TP 7, FP 31, FN 5, TN 230, precisión positiva **18,4 %**.
- **Jayanca:** TP 16, FP 4, FN 18, TN 235, precisión positiva **80,0 %**.
- **Motupe:** TP 17, FP 111, FN 17, TN 128, precisión positiva **13,3 %**.
- **Olmos:** TP 27, FP 140, FN 10, TN 96, precisión positiva **16,2 %**.

**No es validación fitopatológica:** los aciertos/falsos se refieren al patrón de humedad del aire de cuadrícula frente a ERA5, nunca a infecciones. No se dispone de humectación foliar medida ni registros de incidencia o diagnóstico de parcelas. Además, las resoluciones de cuadrícula de pronóstico y ERA5 difieren. Publicar ambas incertidumbres.

**Fase 7B prospectiva real:** se implementó verificador automático diario de las emisiones inmutables del OAF. Emisión inicial guardada 15/10/2026 para jornadas 16–22/10/2026; **28 jornadas-localidad archivadas, 0 maduras, 0 verificadas**, estado `pendiente_reanalisis`. Primera verificación posible **23/10/2026**, margen de siete días, si ERA5 tiene datos reales disponibles. No inventar resultados futuros.

**Implementado y archivado:** `FASE_7B_VALIDACION_HUMEDAD.md`, `modelos/validar_indicador_humedad_botrytis_7b.py`, `modelos/verificar_patrones_botrytis_emitidos_7b.py`, sus dos workflows GitHub Actions, `datos/botrytis_indicador_7b_backtest.json`, `datos/botrytis_indicador_7b_diario.csv`, `datos/botrytis_humedad_7b_prospectivo.json` y `datos/botrytis_humedad_7b_prospectivo.csv`. Nuevo panel desplegable Fase 7B en la sección Cultivos → Predicción, con lector `modelos/visor_validacion_humedad_botrytis_7b.js`.

**Preservación del sitio:** cinco pestañas, recuadro verde inicial exclusivamente título «Observatorio Agroclimático y Fitosanitario» y fotos arándano/vid; presentación autor en primera persona bajo el recuadro; nueve enfermedades; módulos climáticos y ENFEN separados, sin alertas propias inventadas.

**Siguiente paso Fase 7C:** preparar captura y validación de datos fitopatológicos de campo reales (parcela, variedad, floración, incidencia y severidad de Botrytis, confirmación diagnóstica) con HR/temperatura en dosel y humectación foliar instrumentada. Comparar su capacidad pronóstica para infección con modelo meteorológico básico, sin fuga temporal y con suficientes casos positivos/negativos. Mantener línea ENSO/El Niño Costero predictiva independiente.

## Último avance realizado: Fase 7A · Botrytis de arándano (15/10/2026)

**Nuevo módulo de arándano efectivamente integrado en el portal:** dentro de Cultivos → Predicción (ruta `#riesgos`), se presenta un análisis horario experimental de siete días completos de HR >90 % durante al menos seis horas consecutivas, que puede atravesar medianoche. Se complementa con lluvia, radiación (W/m² convertida a MJ/m² diarios), temperatura y DPV, en cuatro localidades de Lambayeque. Hay opción de identificar floración, pero la fenología *no* está certificada por el modelo. Se muestran solo patrones de humedad, **no probabilidades, alertas, diagnósticos ni tratamientos**.

**Sustento:** UC IPM documenta esas condiciones de humedad como favorables a *Botrytis* en general; la guía de arándano UF/IFAS destaca la floración y humectación prolongada. HR del aire a 2 m NO equivale a humectación foliar en flores. El criterio no fue calibrado para Lambayeque.

**Implementación verificada:** `modelos/botrytis_arandano_humedad_7a.js`, `modelos/botrytis_arandano_humedad_7a.py`, `.github/workflows/oaf_botrytis_arandano_7a.yml`; GitHub Actions pasó autopruebas, consulta real a Open-Meteo y archivo horario de cuatro localidades. Cotejo entre ambos lenguajes superó las verificaciones de episodios, duración, días, lluvia, radiación y DPV usando los datos del primer archivo.

**Primera emisión real 15/10/2026:** `datos/patrones_botrytis_emitidos/2026-10-15.json`, con pronósticos de 16–22 octubre (168 horas × 4 localidades). Episodios esperados según criterio atmosférico: Motupe **2**, Jayanca **0**, Olmos **3**, Chiclayo **0**. No son brotes ni infecciones.

**Documentación:** `FASE_7A_BOTRYTIS_ARANDANO.md`, y `datos/plantilla_monitoreo_botrytis_arandano.csv` (25 columnas únicamente; no existen registros sanitarios de campo). La investigación del modelo térmico de oídio de vid continúa intacta, así como la comparación climática, ENFEN y verificación prospectiva 6G.

**Condición de preservación:** en recuadro verde de Inicio SOLO título Observatorio Agroclimático y Fitosanitario y dos fotos, bajo este la presentación en primera persona firmada Carlos E. Coronel García, Ingeniero Agrónomo. Cinco pestañas principales y nueve enfermedades en ficha.

**Siguiente Fase 7B:** empezar validación con datos reales y observaciones regionales de HR dentro del dosel, humectación foliar medida, fase de floración, incidencia/severidad confirmada de Botrytis. Comparar señales pronosticadas y observaciones sin fuga temporal, antes de producir cualquier probabilidad fitosanitaria. Mantener línea Niño Costero (ICEN/TSM) y anomalías climáticas en paralelo.

## Último avance: Fase 6G — Verificación prospectiva de pronósticos archivados (15/10/2026 UTC)

**Cierre confirmado Fase 6F:** el benchmark de radiación/humedad/viento terminó correctamente, con [JSON](datos/benchmark_variables_6f.json) y [CSV de errores mensuales](datos/benchmark_variables_6f_mes.csv) finalmente publicados. Cada localidad tuvo 6.552 horas de prueba enero–septiembre 2026. En relación con el modelo básico, los intervalos de mejora mediante remuestreo por bloques incluyeron 0 para Chiclayo (−2,73 % a +15,33 %) y Motupe (−5,48 % a +1,86 %); fueron negativos en Jayanca (−42,69 % a −9,52 %) y positivos en Olmos (+1,65 % a +10,14 %). No suponer causalidad ni generalizar la mejora de Olmos a toda Lambayeque.

**Fase 6G efectivamente ejecutada:** el OAF implementó la evaluación diaria de pronósticos externos conservados antes del evento, verificando pronóstico D+1...D+7 por localidad y variable frente a ERA5-Land (temperatura) y ERA5 (radiación y precipitación). Se impone retraso mínimo de 7 días por disponibilidad científica de reanálisis (~5 días). Calcula MAE, RMSE y sesgo sin imputaciones. Los datos de referencia no son estaciones SENAMHI.

**Primera ejecución REAL:** GitHub Actions exitoso, JSON `datos/evaluacion_prospectiva_6g.json` con estado `pendiente_reanalisis`, **28 jornadas archivadas, 0 verificables y 0 verificadas**. Primera fecha válida 15/10/2026; primera fecha elegible para evaluación 22/10/2026, siempre sujeto a disponibilidad. Archivo `datos/evaluacion_prospectiva_6g.csv` únicamente con encabezados. Ningún porcentaje de acierto fue inventado.

**Archivos guardados:** `modelos/verificar_pronosticos_emitidos_6g.py`, `.github/workflows/oaf_verificacion_6g.yml`, `modelos/verificacion_prospectiva_visor_6g.js`, `FASE_6G_VERIFICACION_PROSPECTIVA.md`. La web incorpora una sección desplegable Fase 6G en «Datos climatológicos».

**Estado del portal preservado:** cinco pestañas; dentro del recuadro verde solo título «Observatorio Agroclimático y Fitosanitario» y dos fotografías; debajo, descripción del proyecto en primera persona firmada por Carlos E. Coronel García, Ingeniero Agrónomo; enfermedades de arándano y vid y modelos oceánicos ENFEN diferenciados.

**Siguiente prioridad:** al cerrar las fechas previstas, contrastar error frente al reanálisis y luego a estaciones instrumentales SENAMHI/parcelas. Comparar sistemáticamente horizontes y eventos anómalos, estudiar señales radiativas/DPV/humectación foliar y comenzar validación biológica de Botrytis del arándano. Continuar modelos de Niño Costero con fuentes ICEN y predictores oceánico-atmosféricos diferenciados.

## Avance más reciente: Fase 6F · Valor predictivo de la radiación y covariables (14/10/2026)

**Pregunta prioritaria:** ¿la radiación solar, la humedad relativa y el viento realmente mejoran la predicción, frente al pronóstico original y un modelo sencillo, o generan sobreajuste?

**Implementado y verificado en la API:** se recuperaron exitosamente 120/120 horas de predictores archivados 24 horas antes para Motupe (temperatura, radiación, humedad y viento) y 120 horas coincidentes de referencia ERA5-Land. Esto permite un experimento que respeta mejor la cronología de emisión de pronósticos.

**Código en GitHub:** `modelos/benchmark_radiacion_6f.py` (entrenamiento 2024–2025, prueba temporal aislada enero–septiembre 2026, cuatro localidades, regresión Ridge con/sin covariables; MAE/RMSE y remuestreo en bloques), `.github/workflows/oaf_benchmark_radiacion_6f.yml`, `tests/probe_prevruns_6f.py`, `modelos/benchmark_visor_6f.js`, `FASE_6F_EVALUACION_PREDICTORES.md`. El panel desplegable está en Datos climatológicos.

**Precisión:** únicamente inferimos temperatura futura contra reanálisis ERA5-Land, no El Niño Costero ni enfermedades. Las mejoras retrospectivas, si aparecen, NO se interpretan como validación operativa ni como causalidad de la radiación. Si una localidad o variable carece de cobertura, no se publicarán cifras fabricadas.

**Continuación:** revisar GitHub Actions del benchmark y los resultados `datos/benchmark_variables_6f.json` y `datos/benchmark_variables_6f_mes.csv` cuando estén realmente generados; documentar si el modelo ampliado supera o no al básico en cada localidad. Después programar archivo de pronósticos emitidos prospectivamente, validación contra sensores SENAMHI y mediciones de humectación para Botrytis del arándano.

### Evaluación real y archivo prospectivo (continuación 6F)

El benchmark completó cálculos de 17.105 h de entrenamiento y 6.552 h de prueba por localidad. MAE básico → MAE con radiación/HR/viento: **Chiclayo 0,8463 → 0,7959 °C (mejora 5,95 %)**; **Jayanca 0,7424 → 0,9234 °C (empeora 24,38 %)**; **Motupe 1,5424 → 1,5749 °C (empeora 2,11 %)**; **Olmos 1,7432 → 1,6566 °C (mejora 4,97 %)**. Son valores de registros GitHub Actions completos del cálculo; el primer `git push` del JSON falló porque la rama avanzó concurrentemente y se ajustará el flujo. No proclamar ventaja regional estable ni validación prospectiva.

Se creó con éxito el **archivo prospectivo diario**, primera emisión local 14 de octubre 2026 para los siete días siguientes y las cuatro localidades, en `datos/pronosticos_emitidos/2026-10-14.json`. Archiva Open-Meteo como pronóstico **externo** con fecha/hora, diez variables (incluida radiación), localidades, fuente y unidades. Workflow `.github/workflows/oaf_archivo_prospectivo_6f.yml` y script `modelos/archivar_pronosticos_prospectivos_6f.py` verificaron la primera emisión. La evaluación de acierto queda pendiente de que transcurran las fechas previstas.

## Avance más reciente: Fase 6E — radiación solar y nuevas variables (14/10/2026)

**Nueva instrucción y alcance del autor:** incorporar nuevas variables predictoras, **especialmente la radiación solar**, tanto para el análisis agroclimático y de anomalías regionales como para estudiar su posible utilidad en modelos fitosanitarios de arándano y vid. Mantener la línea ENSO con predictores oceánico-atmosféricos por separado.

**Ejecutado en GitHub y publicado en código:**
- En **Datos climatológicos** se presentan radiación actual de onda corta (W/m²), radiación diaria acumulada (MJ/m²), viento actual y máximo diario (km/h), humedad relativa actual y media diaria (%), DPV actual y máximo (kPa), ET₀ FAO diaria (mm), presión superficial actual (hPa) e insolación diaria (h).
- Se amplió **Anomalías climáticas** con radiación acumulada prevista para siete días, radiación histórica P90 de acumulados equivalentes y clasificación respecto de P10/P90, conservando periodo **1996–2025** y ventana estacional ±15 días.
- **Verificación externa real:** GitHub Actions confirmó variables y unidades para Motupe y Chiclayo. El primer test detectó que el archivo ERA5-Land no entregaba radiación para octubre 2019 (0 de 31 días), mientras ERA5 sí entregaba 31 de 31. Se corrigió el módulo para usar **ERA5 como referencia de radiación y precipitación**, y ERA5-Land para temperatura.
- Se mantuvieron controles para rechazar datos faltantes; pruebas sintéticas de temperatura/lluvia/radiación pasaron. La verificación de toda la cobertura 1996–2025 **se ejecutó con éxito en GitHub Actions**, comprobando 10.958 de 10.958 registros numéricos en ERA5 radiación, ERA5 lluvia y ERA5-Land temperatura para Motupe; esto no certifica exactitud instrumental.
- Se documentó metodología y futuras fuentes (humectación foliar medida, sensores de suelo, PAR, UV, viento zonal del Pacífico, SOI) en `VARIABLES_AGROCLIMATICAS_FASE6E.md`.
- Código actualizado: `index.html`, `modelos/anomalias_climaticas_v01.js`; pruebas `tests/test_variables_agroclimaticas_6e.py`, flujo `.github/workflows/oaf_variables_6e_check.yml`.
- **No se modificó** la portada: recuadro verde solo con título Observatorio Agroclimático y Fitosanitario y fotografías; descripción en primera persona del autor debajo y firma Carlos E. Coronel García, Ingeniero Agrónomo. Cinco pestañas intactas.

**Siguiente tarea:** confirmar que el periodo 1996–2025 ofrece cobertura diaria suficiente con ERA5 para radiación; guardar fechas/horizontes de pronósticos; estudiar sesgos entre modelos y observación real; recopilar duración de humectación foliar y observaciones sanitarias. No tratar radiación/HR/DPV como diagnóstico de infección ni como pronóstico ENSO por sí solos.

## Avance más reciente: Fase 6D completada (14/10/2026, Perú)

**Meta permanente del proyecto:** predecir futuras anomalías climáticas, especialmente El Niño Costero, y anticipar enfermedades en arándano y vid con datos y validación prospectiva, no solo vigilar series.

**Hallazgo y solución de disponibilidad:** el archivo NOAA CPC ERSSTv5 usado antes permanecía en junio 2026. Se encontró una fuente NOAA NCEI ERSSTv5 distinta, actualizada a septiembre de 2026, con anomalías de Niño 1+2 en la sexta columna y climatología original 1971–2000. Se aplicó **reajuste mensual propio a 1991–2020**, con control estricto 30 años completos, meses continuos, datos numéricos, comparación con ERSSTv5 CPC y auditoría de procedencia.

**Resultados observados y cálculos derivados:** septiembre 2026 +4,389 °C (ERSSTv5 NOAA NCEI reajustado por OAF). Contraste con CPC: MAE interproducto últimos 24 meses coincidentes 0,0397 °C; NO mide desempeño de pronósticos. Modelo experimental AR(1) octubre 2026 +4,054 °C, noviembre +3,744 °C, diciembre +3,456 °C, frente a persistencia +4,389 °C. A 1/2/3 meses el AR(1) tiene un error mayor en los últimos 12 meses evaluados. NO se considera habilidad prospectiva demostrada, NO es ICEN oficial, NO predice una categoría ENFEN ni riesgo directo de enfermedades.

**Entregables implementados:**
- `modelos/modelo_ncei_ersstv5_fase6d.py`: ingesta, normalización climática, backtests y pruebas de calidad.
- `.github/workflows/oaf_ncei_ersstv5_fase6d.yml`: ejecución automática mensual confirmada como exitosa en GitHub Actions.
- `datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv`: serie histórica reajustada.
- `datos/ncei_ersstv5_backtest_1a3m.csv` y `datos/modelo_ersstv5_ncei_6d.json`: predicciones retrospectivas y métricas.
- `modelos/ncei_visor_6d.js`: panel web que impide mostrar resultados sin datos y vigencia.
- `MODELO_NCEI_ERSSTV5_FASE6D.md`: metodología, incertidumbres, limitaciones y siguientes pasos.

**Interfaz:** la pestaña «Boletín de El Niño» incluye un panel plegable 6D actualizado además del panel 6C histórico. Se mantienen las cinco pestañas y el recuadro verde con SOLO el título y dos fotos; bajo el recuadro la descripción en primera persona y firma «Carlos E. Coronel García, Ingeniero Agrónomo».

**Siguiente trabajo — Fase 6E:** probar predictores multivariables con datos realmente disponibles, priorizando SOI, viento zonal o calor subsuperficial si existen series trazables con fecha de disponibilidad. Evaluar por horizonte y frente a persistencia mediante walk-forward y, para resultados operativos, archivo prospectivo de emisiones. No afirmar resultados de El Niño Costero ni enfermedad agrícola antes de validarlos.

## Avance más reciente: Fase 6C · ERSSTv5 e ICEN (14/10/2026)

**Datos efectivamente descargados y procesados:** NOAA CPC ERSSTv5 Niño 1+2, anomalías mensuales desde enero de 1950 hasta junio de 2026. Esta versión NOAA presenta un desfase de **4 meses** a octubre de 2026, motivo por el cual **no se publican proyecciones vigentes** basadas en ella. El módulo conserva únicamente sus datos y evaluaciones históricas.

**Resultados:** 197, 196 y 195 pronósticos históricos walk-forward a horizontes de 1, 2 y 3 meses. MAE AR(1): **0,3449 / 0,4952 / 0,6183 °C**, MAE persistencia: **0,3546 / 0,5282 / 0,6823 °C**. En los últimos 12 meses, el AR(1) empeora a 1 y 2 meses y la mejora a 3 meses es mínima. Todas las etiquetas de habilidad prospectiva y demostrada siguen en falso.

**Contraste con fuente institucional:** un promedio trimestral centrado basado en ERSSTv5 del OAF se comparó con cuatro ICEN de SENAMHI–ENFEN publicados para febrero–mayo 2026. Diferencias OAF menos índice institucional: +0,017; +0,010; 0,000; +0,003 °C, respectivamente; media absoluta **0,0075 °C**. Solo control limitado de cómputo, no validación completa ni índice oficial.

**Archivos:** `MODELO_ERSSTV5_FASE6C.md`, `modelos/modelo_ersstv5_nino12_fase6c.py`, `.github/workflows/oaf_ersstv5_fase6c.yml`, `datos/modelo_ersstv5_nino12_6c.json`, `datos/noaa_ersstv5_nino12_mensual.csv`, `datos/contraste_icen_publicado_2026.csv`, `modelos/ersstv5_visor_v01.js`.

**Portal:** panel plegable de Fase 6C dentro de «Boletín de El Niño». Se mantienen las cinco pestañas. En el recuadro verde, únicamente título «Observatorio Agroclimático y Fitosanitario» y dos fotografías; abajo y fuera, descripción en primera persona y firma.

**Próximo trabajo Fase 6D:** localizar fuentes **vigentes** de ICEN/ERSSTv5 o registros institucionales y estudiar ERA6/ERSSTv6 como productos diferentes; ampliar controles documentales, recopilar pronósticos fechados para evaluación realmente prospectiva, y añadir señales atmosféricas para Niño Costero. No extrapolar automáticamente las anomalías oceánicas a incidencia de Botrytis u oídio.

## Último avance ejecutado: Fase 6B — modelo oceánico NOAA Niño 1+2 (14/10/2026)

**El trabajo efectivamente realizado:**
- Se implementó un modelo AR(1) un paso adelante sobre anomalía mensual SST Niño 1+2 de **NOAA CPC OISST v2.1** (NO es ICEN ENFEN), y se comparó contra **persistencia** y anomalía cero.
- GitHub Actions procesó exitosamente la serie NOAA, guardando datos 1982-01 a 2026-09, 200 pruebas walk-forward retrospectivas, métrica y salida JSON versionada. Archivos: `modelos/modelo_nino12_fase6b.py`, `.github/workflows/oaf_nino12_fase6b.yml`, `datos/noaa_nino12_oisst_mensual.csv`, `datos/nino12_backtest_walkforward.csv`, `datos/modelo_nino12_experimental.json`.
- Última anomalía NOAA real: **septiembre 2026, +4,69 °C**. Predicción AR(1) **octubre 2026, +4,35 °C**; persistencia **+4,69 °C**. Estas magnitudes **no equivalen al ICEN oficial** ni permiten afirmar pronóstico validado del evento El Niño Costero.
- Evaluación de 200 meses: MAE AR(1) **0,3749 °C**, persistencia **0,3797 °C** (mejora nominal ~1,26 %). Últimos 12 meses: MAE AR(1) **0,5818 °C**, persistencia **0,4708 °C** (**AR1 peor**). Prueba exploratoria de remuestreo por bloques 12 meses: intervalo de mejora relativa incluye cero, por lo que **no hay mejora robusta demostrada**.
- El módulo web **Boletín de El Niño** dispone de visor que consume solamente la salida JSON verificada y presenta errores/advertencias, nunca simulaciones. Código: `modelos/nino12_visor_v01.js`.
- Documento científico: `MODELO_NINO12_FASE6B.md`.
- Se ejecutó descarga y se confirmó la existencia de productos JSON/CSV reales en GitHub; no se ha inspeccionado manualmente el renderizado final desde un navegador de usuario.

**Siguiente trabajo: fase 6C (prioritario):** convertir las señales oceánicas en un modelo mejor informado, usando **ERSSTv5 e ICEN según ENFEN**, anomalías TSM Niño 1+2, vientos, señales subsuperficiales y posibles precursores, más evaluación estricta con pronósticos históricos fechados. Antes de agregar complejidad, determinar si hay mejora real contra persistencia y si se pueden producir horizontes 1–3 meses con incertidumbre verificable. Luego estudiar relación con anomalías de Lambayeque y enfermedades de arándano/vid.

**Regla permanente:** el proyecto busca predecir anomalías climáticas y enfermedades agrícolas, pero nunca presentará un valor de anomalía SST/indicador térmico como predicción operativa de El Niño Costero o de una infección agrícola sin validación.

## Último avance: Fase 6A (14/10/2026)

**Implementado y guardado en GitHub:**
- En «Datos climatológicos» hay un módulo experimental para comparar pronósticos externos de siete jornadas futuras con valores históricos por estación del año, usando como referencia **1996–2025** (reanalizados ERA5-Land: temperatura; ERA5: precipitación).
- Se clasifican temperaturas pronosticadas como relativamente cálidas (sobre P90), frías (bajo P10) o sin extremos, mostrando diferencia respecto a la media histórica. Para lluvias se compara el acumulado previsto de siete días con el P90 histórico estacional de acumulados de siete días.
- El cálculo se activa bajo demanda desde el navegador; NO informa riesgos porcentuales ni predice por sí solo El Niño Costero. Si falla la consulta a Open-Meteo, no inventa datos. Fuente y limitaciones explícitas.
- En «Boletín de El Niño» aparece la **línea predictiva oceánica por desarrollar**, vinculada al ICEN y a metodología oficial ENFEN actualizada en 2024/2026.
- **Código:** modelos/anomalias_climaticas_v01.js.
- **Documentación:** MODELO_ANOMALIAS_FASE6A.md.
- **Pruebas:** 10 pruebas sintéticas completadas (temperatura normal, anómala, lluvia >P90, transición de año, año bisiesto, 30 años elegibles, faltantes, 24 años rechazados, 25 años aceptados y 10.958 fechas históricas). Se ha verificado integridad estructural de la portada y cinco pestañas; el acceso real al proveedor y el despliegue de GitHub Pages NO han sido comprobados de extremo a extremo desde este entorno.
- **No alterar la presentación aprobada:** recuadro verde solo con título «Observatorio Agroclimático y Fitosanitario» y las fotografías; debajo y fuera, descripción en primera persona firmada «Carlos E. Coronel García, Ingeniero Agrónomo».

**Nuevo siguiente trabajo:** fase 6B, datos oceánicos y predicción preliminar de Niño Costero (anomalías TSM Niño 1+2, ICEN, índices atmosféricos, pronósticos externos archivados y modelo base de persistencia con evaluación walk-forward). En paralelo preparar validación de errores de las anomalías agroclimáticas e indicadores de enfermedades con datos de campo. No afirmar todavía predicción de El Niño o enfermedades validada.

## Estado del portal
- Cinco secciones principales en este orden: **Inicio**, **Datos climatológicos**, **Cultivos y riesgo de enfermedades**, **Boletín de El Niño**, **Verificación de datos**.
- Portada: dentro del recuadro verde, **solo** «Observatorio Agroclimático y Fitosanitario» y las fotografías de arándano y vid. Debajo y fuera del recuadro, descripción del proyecto **en primera persona por el autor**, seguida de **Carlos E. Coronel García — Ingeniero Agrónomo**. No introducir más texto en el recuadro verde.
- La sección «Cultivos y riesgo de enfermedades» conserva una tabla compacta con **enfermedad, condiciones climáticas y cultivo**, respaldada por fuentes, y una subpestaña diferenciada de **Predicción del riesgo**.
- En el «Boletín de El Niño» se enlazan documentos oficiales ENFEN y SENAMHI, sin inferir automáticamente la alerta vigente. Si la consulta institucional falla, se señala que el estado no está verificado.
- En «Datos climatológicos» se ofrecen consultas meteorológicas externas y su evolución pronosticada; las predicciones propias se señalan como «en desarrollo».
- En «Verificación de datos» permanecen fuentes, trazabilidad, calidad y acceso al portal histórico archivado en `archivo-analisis-historico.html`.
- Evitar sobrecargar la portada y preservar sus cinco pestañas, fotografías y navegación.

## Cultivos, enfermedades y enfoque
- Cultivos prioritarios: **arándano y vid**.
- Biblioteca científica inicial: 5 enfermedades de arándano (Botrytis, antracnosis, mancha diana, oídio y Phytophthora) y 4 de vid (oídio, mildiu, podredumbre gris y podredumbre negra).
- Distinguir condiciones climáticas favorables, riesgo estimado y presencia confirmada. Los umbrales publicados fuera de Lambayeque **no son reglas operativas validadas localmente**.
- Mantener referencia climática principal 1996–2025 cuando haya cobertura completa, y 1991–2020 para comparabilidad con la normal OMM. No interpolar faltantes sin documentarlo.
- Fuentes: SENAMHI (observaciones), CHIRPS (estimaciones satelitales), ERA5/ERA5-Land (reanálisis), NASA POWER cuando resulte útil, ENFEN (comunicados oficiales); identificar siempre el producto y la fecha.

## Último avance técnico: fase 5
- Se incorporó en la subpestaña Predicción un **indicador térmico experimental** para oídio de la vid (`Erysiphe necator`) con pronóstico horario externo Open-Meteo para Motupe, Jayanca, Olmos y Chiclayo.
- Referencia UC IPM: **después de infección primaria**, tres días consecutivos con al menos seis horas continuas por día entre 70–85 °F (aprox. 21,1–29,4 °C) en el dosel. El portal calcula **solo el patrón térmico**, usando temperatura pronosticada a 2 m; **no reproduce el índice completo**, no estima probabilidad de enfermedad ni diagnostica infecciones.
- Se probaron 4 escenarios sintéticos: tres días favorables consecutivos, días separados, hora faltante y ausencia de condiciones favorables. Las pruebas lógicas pasaron. La disponibilidad real de la API no ha sido verificada en este entorno.
- Código: `modelos/oidio_vid_indicador_termico.py`.
- Documentación: `MODELO_TERMICO_OIDIO_VID_FASE5.md`.
- Mantener avisos de que los resultados experimentales no recomiendan fungicidas ni sustituyen monitoreo del cultivo.

## Próximos trabajos acordados
1. **Abrir la línea predictiva agroclimática**: definir anomalías objetivo (lluvia, temperatura, humedad y evolución de El Niño Costero), escalas temporales y métricas; catalogar TSM Niño 1+2, escenarios ENFEN y pronósticos oceánico-atmosféricos fechados.
2. Verificar la consulta horaria de la web y conservar instantáneas de pronósticos por fecha de emisión, plazo y localidad para futura evaluación sin fuga temporal.
3. **Continuar la línea predictiva fitosanitaria**: validar el indicador térmico de oídio en vid y trabajar en Botrytis de arándano con datos fiables de humectación foliar y registros de campo.
4. Implementar evaluación retrospectiva y prospectiva frente a referencias simples u oficiales, cuantificar habilidad, falsos avisos e incertidumbre, y registrar datos faltantes.
5. Evolucionar ambas líneas hacia predicciones útiles **solo si alcanzan validación independiente**; mantener diferenciados comunicados oficiales ENFEN, pronósticos externos, modelos propios experimentales y enfermedades diagnosticadas.

**Criterio permanente:** no inventar mediciones, cifras de riesgo, predicciones o validaciones. Presentar resultados confirmados y las incertidumbres.
