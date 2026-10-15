# PLAN MAESTRO OAF-Lambayeque 2.0
## Del análisis retrospectivo a la vigilancia y predicción agroclimática y fitosanitaria

**Aprobación de orientación:** 14/10/2026.  
**Responsable y autor:** ING. AGRÓNOMO CARLOS ENRIQUE CORONEL GARCÍA.  
**Región de trabajo:** Lambayeque, Perú, con contexto oceanográfico del Pacífico oriental y regional del norte peruano.  
**Situación:** Plan aprobado y módulos experimentales 6A–6C implementados; **todavía no existe predicción OAF operativa, validada prospectivamente, ni alertas propias**. No declarar que el OAF anticipó un fenómeno por consultar informes publicados.

## 1. Misión renovada

> Desarrollar un **observatorio regional predictivo** con dos capacidades científicas complementarias: **anticipar anomalías climáticas y posibles episodios o evolución de El Niño Costero**, y **predecir el riesgo de enfermedades agrícolas en arándano y vid**, mediante análisis de datos climáticos y oceánico-atmosféricos, modelos probabilísticos, registros fitosanitarios de campo, trazabilidad, pronósticos fechados y validación independiente. La vigilancia y los estudios retrospectivos son medios para alcanzar esa finalidad, no el objetivo final.

La salida inicial de un módulo no validado se etiqueta **experimental / no operativo**. Las alertas meteorológicas y clasificaciones de El Niño Costero **oficiales** corresponden a ENFEN y SENAMHI: el OAF las reproduce con fuente, fecha y validez, no las suplanta.


### Precisión de objetivos predictivos: dos líneas obligatorias

**Línea A — anomalías climáticas y El Niño Costero:** no limitarse a mostrar boletines. El proyecto debe estudiar señales precursoras, predicciones oceánicas/atmosféricas fechadas y evolución de anomalías de TSM (región Niño 1+2), junto con lluvia y temperatura de Lambayeque. El modelado predictivo de El Niño debe tener horizonte y evento bien definidos (p. ej., evolución de un índice o probabilidad de cruzar un umbral oficial); la clasificación ENFEN conserva su autoridad institucional. No intentar inferir la génesis de El Niño a partir de la precipitación local. Archivar pronósticos emitidos antes del resultado y comparar contra modelos de referencia y escenarios institucionales, sin confundir predicción externa con habilidad propia.

**Línea B — enfermedades en arándano y vid:** utilizar pronósticos de condiciones agroclimáticas y datos fitosanitarios para modelos específicos por patógeno, con evaluación independiente. La predicción validada de enfermedades exige historial de presencia/incidencia y de microclima real, no solo rangos bibliográficos. Resultados experimentales se distinguen claramente de advertencias operativas.

**Ambas líneas deben converger en el portal:** dato observado/estimado → escenario o pronóstico fechado → riesgo condicional por cultivo → evaluación posterior del acierto. Todos los resultados incluyen fuente, horizonte, localización, incertidumbre y estado de validación.

## 2. Preguntas que debe responder el sistema

1. **Estado oceánico:** ¿qué declara oficialmente ENFEN sobre El Niño Costero (región Niño 1+2) y cuáles son los escenarios/probabilidades con fecha de emisión?
2. **Condición observada reciente:** ¿cuándo y dónde se han observado o estimado anomalías de lluvia, temperatura y humedad? Distinguir siempre dato de pluviómetro de estimación satelital y su incertidumbre.
3. **Pronóstico:** ¿cuál es la probabilidad de un evento de lluvia/temperatura en 1–7 días, 2–6 semanas o 1–6 meses, según la fuente y su capacidad verificada?
4. **Implicaciones para los cultivos:** ¿hay condiciones meteorológicas favorables para el desarrollo de patógenos y plagas del arándano y de la vid, y las observaciones de campo confirman eventos de enfermedad?
5. **Desempeño:** ¿qué proporción de pronósticos históricos emitidos por adelantado acertó, cuál fue su incertidumbre y cuándo falló?

**No se pretende pronosticar la génesis de El Niño Costero únicamente a partir de cinco pluviómetros**. El componente oceánico tendrá como referencia la clasificación oficial; el valor añadido del OAF es el análisis de exposición y riesgo agrícola en Lambayeque.

## 3. Dos relojes de datos, dos criterios de calidad

### A. Climatología y evaluación retrospectiva
- Acumulados **anuales observados** solo con 12 meses completos y 365/366 días válidos por estación, conforme a `CRITERIO_COBERTURA_OFICIAL.md`.
- En los TXT históricos recibidos: 1 109 meses-estación completos 1996–2015; 79 combinaciones estación-año completas; **último año completo común de las cinco estaciones: 2012**; Cayaltí, Reque, Lambayeque y Cueva Blanca individualmente hasta 2013; Jayanca hasta 2012.
- La correspondencia instrumental histórica exacta sigue **pendiente**. No divulgar «validación independiente» de PISCOp/CHIRPS sin documentar las estaciones utilizadas en su construcción.
- Para climatologías de 30 años: **1996–2025 como periodo objetivo** si existen 30 años completos del mismo producto o de una serie instrumental verificable; **1991–2020 como referencia normal OMM de comparabilidad**, cuando sea aplicable. Etiquetar cada normal como *producto gridded*, *serie de estación* o *referencia estándar*; jamás fusionarlas silenciosamente.
- Si un producto de referencia carece de una porción, calcular únicamente sobre **años completos disponibles**, mostrando claramente el periodo real y el número de años: no llamarlo «normal de 30 años».
- Los datos 2024–2025 extraídos de boletines DZ2 son evidencia documental incompleta, no sustitutos de series instrumentales completas.

### B. Vigilancia y predicción actual
- Se admiten **observaciones válidas recientes del día/semana en curso**, sin exigir que el año actual haya terminado. Esto es indispensable para vigilar cambios rápidos.
- No se acepta un acumulado diario de una estación si faltan las horas/días exigidos por su especificación. En precipitación satelital se permite una cobertura definida por producto y ventana de agregación solo con control explícito y *bandera de calidad*: **no rellenar periodos ausentes**.
- Cada medición/estimación/pronóstico conserva `periodo_inicio`, `periodo_fin`, `fecha_emision`, `fecha_consulta`, `fuente`, `producto_version`, `unidad`, `cobertura`, `estado_QA`, `latitud_longitud/celda`, y `incertidumbre` cuando corresponda.
- **Desactualizado/no disponible** es un resultado válido; nunca sustituir por el último valor y presentarlo como observado ahora.
- Una estimación satelital **no es observación instrumental**; un pronóstico **no es un dato observado**.

## 4. Arquitectura de módulos

| Módulo | Responsable científico | Entrada principal | Primera salida esperada | Condición para declarar operativo |
|---|---|---|---|---|
| **M0 — Trazabilidad** | Calidad de datos y fuentes | Metadatos y controles por estación/producto | Registro auditable: confiable, provisional, no disponible, desactualizado | Control de fuentes y pruebas automáticas |
| **M1 — Vigilancia y predicción de El Niño Costero** | Anomalías océano-atmosféricas y pronósticos ENSO | ENFEN (estado e ICEN), TSM/anomalías Niño 1+2, información atmosférica, pronósticos oceánicos emitidos y archivados con fecha | Estado oficial diferenciado de perspectivas externas y **probabilidad experimental OAF** de evolución/eventos con horizonte explícito | Verificación del estado oficial y habilidad predictiva propia demostrada fuera de muestra frente a referencias; sin atribuirse autoridad ENFEN |
| **M2 — Vigilancia agroclimática** | Anomalías regionales | SENAMHI, CHIRPS v3 preliminar/final, NASA IMERG V07, metadatos geográficos | Lluvia y temperatura recientes, anomalías/percentiles por área | Validación espacial, fechas, píxeles y calidad suficientes |
| **M3 — Pronóstico meteorológico** | Predicción prospectiva | Fuentes oficiales de pronósticos con fecha de emisión, ensembles cuando existan | Probabilidades de excedencia por horizonte (1–7 días; subseasonal y estacional) | Evaluación retrospectiva *sin filtración temporal* y control prospectivo; no usar reanálisis como pronóstico |
| **M4 — Predicción fitosanitaria** | **Arándano y vid** desde el diseño | Meteorología pronosticada y observada, fenología, variedad, humectación, manejo e incidencia/severidad confirmada | Ventanas meteorológicas favorables para Botrytis/antracnosis en arándano y oídio/mildiu en vid; luego probabilidades calibradas por enfermedad | Registros de campo suficientes, evaluación independiente prospectiva y validación fuera de muestra, sin confundir condiciones favorables con diagnóstico |
| **M5 — Comunicación** | Transparencia y decisiones | Resultados M0–M4 | Panel, mapas, fechas, límites de incertidumbre y avisos **oficiales** | Auditoría de mensajes; alertas *propias* solo tras validación y reglas aprobadas |

### Entregable 6A realizado (14/10/2026): anomalías agroclimáticas proyectadas

- Portal: indicador comparativo de temperatura media diaria pronosticada a 7 días contra P10/P90 de ERA5-Land estacional **1996–2025** (ventana ±15 días); lluvia pronosticada a 7 días contra distribución histórica estacional de acumulados 7 días de ERA5.
- Localidades referenciales: Chiclayo, Jayanca, Motupe y Olmos, **no estaciones instrumentales**.
- Datos y errores: la base se consulta bajo demanda; si faltan días o hay menos de 25 años aptos, no se genera señal. Cada fuente queda diferenciada. Ni las señales térmicas ni el umbral de precipitación son probabilidades calibradas o alertas.
- Pruebas: diez escenarios sintéticos de lógica satisfactorios; faltan pruebas contra datos reales, sesgos y despliegue público completo.
- Archivos: modelos/anomalias_climaticas_v01.js y MODELO_ANOMALIAS_FASE6A.md.

### Fase 6B — Próximo entregable: modelo experimental de Niño Costero

Definir un objetivo verificable relacionado con anomalía de TSM Niño 1+2 o evolución de ICEN usando **metodología oficial vigente ENFEN**, incluyendo actualización de 2024 y documentación de 2026. Ingestar series oceánicas oficiales y pronósticos fechados, construir primero pronóstico base de persistencia/estacionalidad y evaluar walk-forward contra referencias institucionales. NO inferir la clasificación oficial ni declarar capacidad predictiva en ausencia de habilidad demostrada. Separar esta predicción oceánica de la señal agroclimática local, investigando luego sus relaciones probabilísticas.


### Avance científico 6B realizado — modelo oceánico experimental Niño 1+2

- Se descargó y versionó la serie mensual **NOAA CPC OISST v2.1 Niño 1+2** de enero de 1982 a septiembre de 2026, desde su fuente original, sin imputación de meses.
- Se implementó pronóstico de anomalía a un mes con **AR(1) lineal** ajustado por origen temporal; referencias persistencia y climatología de anomalía cero; 200 verificaciones retrospectivas desde enero de 2010.
- Resultado inicial a octubre de 2026: AR1 +4,35 °C contra persistencia +4,69 °C, con última observación NOAA de septiembre de 2026 +4,69 °C. **No es diagnóstico oficial ENFEN ni predicción demostrada del evento El Niño Costero**.
- MAE global AR1 0,3749 °C y persistencia 0,3797 °C; MAE últimos 12 meses AR1 0,5818 °C y persistencia 0,4708 °C. No existe habilidad robusta demostrada; remuestreo por bloques incluye mejora nula/negativa.
- Ingesta automática/alerta de fallo de fuente, CSV, JSON, documentación y visor público guardados en el repositorio: `MODELO_NINO12_FASE6B.md`.
- **Próxima fase 6C:** integrar producto ERSSTv5 e índice oficial ICEN actualizado por ENFEN para evaluar la correspondencia con la serie NOAA; añadir pronósticos oceánico-atmosféricos fechados y comparar modelos con persistencia en horizonte 1–3 meses. No utilizar índices OISST como si fuesen ICEN ni extrapolar directamente a lluvia/enfermedad regional.

### Fase 6C realizada · Validación histórica con ERSSTv5 (14/10/2026)

- NOAA CPC ERSSTv5 Niño 1+2, base 1991–2020, con meses desde 1950-01 hasta 2026-06. La serie fue descargada y procesada en GitHub Actions; el desfase de cuatro meses frente a octubre de 2026 quedó identificado y bloqueó proyecciones prospectivas actuales.
- Se evaluaron 197, 196 y 195 orígenes de predicción a 1, 2 y 3 meses, mediante AR(1) frente a persistencia y anomalía cero, con método walk-forward y prueba exploratoria de errores por bloques. Ningún horizonte fue declarado validado prospectivamente.
- El promedio móvil ERSSTv5 indicativo fue contrastado con cuatro valores ICEN publicados por SENAMHI–ENFEN de febrero a mayo de 2026 (diferencia absoluta media 0,0075 °C); este control limitado **no** convierte la serie en índice oficial.
- Se integró un panel desplegable en «Boletín de El Niño», con aviso de desactualización y métricas de validación; intactos el título/fotografías del recuadro verde y las cinco pestañas.
- Ver [MODELO_ERSSTV5_FASE6C.md](MODELO_ERSSTV5_FASE6C.md) y [contraste institucional](datos/contraste_icen_publicado_2026.csv).

**Siguiente fase 6D:** conseguir series ICEN/ERSSTv5 verificadas y vigentes para continuar una predicción actual y auditable; explorar ERSSTv6 como un producto alternativo **distinto**, introducir predictores atmosféricos y oceánicos, mantener métricas y pruebas prospectivas contra persistencia, y vincular después condiciones oceanográficas con el clima y enfermedades en Lambayeque.

### Fase 6D realizada: reconstrucción ERSSTv5 NOAA NCEI de referencia 1991–2020

- Fuente alternativa NOAA NCEI ERSSTv5 `ersst.v5.el_nino.dat` detectada con registros hasta septiembre 2026, con índice Niño 1+2 en sexta columna y climatología original 1971–2000.
- Se implementó la transformación por mes calendario de anomalías desde la referencia original a la base **1991–2020**, restando la media mensual 1991–2020 de la serie original. Resultado OAF DERIVADO, **no ICEN institucional**, con procedencia documentada.
- El contraste con los 918 meses comunes del archivo CPC ERSSTv5 mostró una diferencia absoluta media de 0,0397 °C en los últimos 24 meses coincidentes. Es un control de plausibilidad, no equivalencia de instrumentos ni validación predictiva.
- Se ejecutó y se guardó un backtest de AR(1) a 1/2/3 meses vs persistencia. Pronósticos experimentales octubre +4,054, noviembre +3,744, diciembre +3,456 °C, anclados en último mes septiembre 2026 de anomalía +4,389 °C. **El AR1 no supera a persistencia en los doce meses más recientes**; sin validación prospectiva ni alertas.
- Módulo adicional en pestaña Boletín de El Niño, plegable para conservar el diseño simplificado. Ver `MODELO_NCEI_ERSSTV5_FASE6D.md` y `datos/modelo_ersstv5_ncei_6d.json`.

**Fase 6E recomendada:** llevar un registro versionado de cada emisión mensual y su horizonte, incorporar variables climáticas atmosféricas (SOI, vientos, condiciones subsuperficiales) con origen temporal comprobado y evaluar capacidad predictiva fuera de muestra. Integrar después la predicción de anomalías regionales en Lambayeque y los modelos de riesgo fitosanitario de arándano y vid, evitando inferencias causales o sanitarias no justificadas.

### Fase 6E: ampliación de variables climáticas y registro de radiación solar (14/10/2026)

- Se integraron radiación solar global (W/m² instantáneo, MJ/m² por día), horas de insolación, DPV (kPa), viento (km/h), humedad relativa (%), ET₀ de referencia (mm) y presión atmosférica (hPa) a los datos externos disponibles en la pestaña Datos climatológicos.
- Se extendió el indicador de anomalías 1996–2025 a **radiación solar acumulada 7 días**, con percentiles P10/P90 y referencia estacional ±15 días; se exigen ≥25 años válidos y se muestran resultados **no evaluables** si falta radiación.
- Una prueba en API real identificó que **ERA5-Land no entregaba radiación histórica** para la muestra revisada (0/31 datos útiles); ERA5 entregó 31/31. Por ello la fuente definitiva es **ERA5 para radiación y lluvia, ERA5-Land para temperatura**. Los pronósticos provienen de Open-Meteo, no del OAF.
- Las variables no permiten inferir humectación foliar, enfermedad diagnosticada, riesgo calibrado ni predicción oficial de El Niño Costero.
- Se agregó [VARIABLES_AGROCLIMATICAS_FASE6E.md](VARIABLES_AGROCLIMATICAS_FASE6E.md) con fuentes, unidades, aplicación agronómica, control de calidad y nuevas variables candidatas.
- Continuar con validación de la radiación en series históricas completas y sensores de campo; después evaluar aportación incremental de covariables climáticas a modelos de enfermedad y de anomalías, evitando multicolinealidad y fuga de datos futuros.

- **Fase 6F, primer benchmark real:** el modelo que incorpora radiación/HR/viento mejoró MAE frente a corrección básica en Chiclayo (+5,95 %) y Olmos (+4,97 %), empeoró en Jayanca (−24,38 %) y Motupe (−2,11 %), con 6.552 h de prueba por sitio (2026) y ERA5-Land como referencia reanalizada. No atribuir causalidad ni capacidad operativa. Consultar `FASE_6F_EVALUACION_PREDICTORES.md`.
- **Primera verificación prospectiva iniciada:** archivo real fechado `datos/pronosticos_emitidos/2026-10-14.json` para jornadas futuras 15–21 octubre 2026; 4 localidades y variables meteorológicas, con actualización automatizada. Falta comprobar predicciones contra observaciones al cierre de cada horizonte.

### Fase 6F · Validar aporte de radiación, humedad y viento (14/10/2026)

- Se puso en marcha una comparación rigurosa de predictores *realmente pronosticados antes de la hora objetivo*, usando el archivo Open-Meteo Previous Runs con desplazamiento de 24 horas y temperatura verificadora ERA5-Land.
- Se diseñaron A) pronóstico externo original, B) Ridge básico con temperatura y estacionalidad, y C) Ridge ampliado con radiación, humedad y viento. Entrenamiento hasta diciembre 2025; evaluación temporal separada enero–septiembre 2026; cuatro localidades regionales.
- Se verificó por GitHub Actions la existencia de 120 horas archivadas y referencia horaria para Motupe. Se implementó pipeline de evaluación completa, informe metodológico y visor seguro de datos, sin exponer resultados antes de procesarse.
- Las métricas permiten detectar si agregar covariables empeora la habilidad, y no solo destacar mejores valores. La verificación ERA5-Land no sustituye sensores locales SENAMHI.
- Antes de llamar operativo al modelo será necesario archivar fechas de emisión en tiempo real, validar con observaciones regionales, medir estabilidad fuera de muestra, y extender la línea a enfermedades solamente con registros fitosanitarios confirmados.

### Fase 6G realizada: verificación de emisiones archivadas sin usar información futura

- El proceso `oaf_verificacion_6g.yml` se ejecuta diariamente: lee instantáneas inmutables de pronóstico emitido, verifica su cronología y fecha de emisión, y solo compara fechas transcurridas con una tolerancia de **siete días** para la llegada de reanálisis.
- Variables evaluadas: temperatura media diaria (ERA5-Land), lluvia diaria (ERA5) y radiación solar diaria acumulada (ERA5), por Chiclayo, Jayanca, Motupe y Olmos, y horizontes D+1..D+7. Se calculan MAE, RMSE, sesgo y n verificadas sin rellenar faltantes.
- Primer estado publicado el 15/10/2026: **28 jornadas pronosticadas, ninguna aún elegible para verificarse**. Primera evaluación posible 22/10/2026. Este diseño impide presentar errores de referencia ficticios cuando el evento todavía no ocurrió.
- Se añadió al portal una sección Fase 6G dentro de «Datos climatológicos», con informe `FASE_6G_VERIFICACION_PROSPECTIVA.md` y datos públicos `datos/evaluacion_prospectiva_6g.json`.
- El benchmark Fase 6F publicó finalmente sus resultados completos: las mejoras con radiación/HR/viento fueron heterogéneas y solo en Olmos el intervalo exploratorio del beneficio fue completamente positivo. Este hecho no implica causalidad ni validez operativa.

**Trabajo científico pendiente:** acumular emisiones prospectivas durante varios meses, comprobar sesgos contra estaciones SENAMHI, evaluar la precisión de anomalías de lluvia y radiación por horizonte y comparar modelos propios con referencias simples. Los modelos de El Niño Costero y enfermedades agrícolas continúan siendo líneas diferenciadas sujetas a validación.

### Fase 7A completada — primera señal meteorológica para Botrytis del arándano (15/10/2026)

- Se extendió Cultivos → Predicción con una sección para arándano: búsqueda en pronósticos Open-Meteo de **periodos de HR >90 % durante ≥6 h consecutivas**. Ese criterio de UC IPM es general para *Botrytis*, no un modelo entrenado ni validado en arándanos de Lambayeque. UF/IFAS indica que floración y humectación prolongada son componentes de susceptibilidad.
- Se incluyen temperatura a 2 m, lluvia, **radiación solar**, DPV y duración de la HR elevada, con intervalos que cruzan medianoche y rechazo estricto de horas nulas. No se publica riesgo porcentual o recomendación de productos comerciales.
- Primera emisión archivada y verificable 15/10/2026 para 16–22/10/2026, con 168 horas por localidad: Motupe 2 periodos, Jayanca 0, Olmos 3, Chiclayo 0. Sin mediciones de enfermedad, los episodios solo indican condiciones de humedad atmosférica pronosticadas.
- **Código, API y archivo prospectivo** comprobados mediante GitHub Actions; JavaScript y Python coincidieron en seis magnitudes al reprocesar los archivos reales para las cuatro localidades. Ver `FASE_7A_BOTRYTIS_ARANDANO.md` y `datos/patrones_botrytis_emitidos/2026-10-15.json`.
- **Fase 7B:** recopilar observaciones reales de humectación foliar en arándano, fases fenológicas, HR y temperatura en dosel y enfermedades diagnosticadas, con cronología y ubicación verificables. Evaluar modelos fitosanitarios únicamente después de contar con suficientes casos y negativos, periodos y parcelas.

## 5. Hoja de ruta y entregables comprobables

### Fase 3Z — Modernizar fuentes y monitoreo reciente (prioridad inmediata)
**Producto:** catálogo versionado de fuentes con accesos, permisos, periodicidad, cobertura, zonas, unidad, versión y estado de conexión; ingesta **inicial de al menos un producto público** realmente disponible, con extracción fechada, calidad y procedencia; indicador ENFEN con fecha de comunicado; primeras visualizaciones de los cinco puntos preliminares y, cuando haya límites comprobados, mapas regionales.

**Orden de integración propuesto:**
1. **ENFEN**: índice/estado oficial y escenarios Niño 1+2, 3.4; conservar documento/fuente y fecha de emisión, sin fabricar probabilidades.
2. **CHIRPS v3 preliminar/final**: estimación satelital-estacional ajustada con pluviómetros; comparar el mismo periodo y revisar revisiones del producto.
3. **NASA GPM IMERG V07**: lluvia satelital de baja latencia; considerar credenciales NASA y conversión correcta entre tasa de precipitación y acumulado, intervalos y UTC.
4. **SENAMHI DZ2 y red instrumental**: fuente preferente para verificar lluvia local, con acceso autorizado y ficha de estación.
5. **Pronósticos institucionales**: fase siguiente; catalogar pero **no inferir** probabilidad de lluvia de un reanálisis.

**Criterio de cierre 3Z:** datos recientes con sello temporal y bandera de calidad **realmente descargados**, gráfico públicamente identificable como estimación/observación, trazabilidad de fallos y sin mensajes de alerta meteorológica propia. Si no hay datos accesibles, el módulo debe declarar «sin conexión/verificación», no mostrar simulaciones como reales.

### Fase 4A — Detección y predicción de riesgo agroclimático
- Primero definir eventos verificables: precipitación diaria por encima de un umbral **fijado con climatología válida local**, rachas secas, temperatura extrema. No adoptar 20/50 mm mensuales de 3S como umbrales de alerta.
- Construir referencia simple (climatología/persistencia o pronóstico institucional), luego regresión logística/árboles, solo después Random Forest/XGBoost si datos justifican su complejidad.
- Comparación objetiva a horizontes 1–7 días (si hay pronósticos históricos archivados con su fecha de emisión) y señales subseasonales/estacionales si hay producto pertinente. No hacer pasar hindcasts con información futura por pronósticos históricos emitidos.
- Evaluación **walk-forward** con ventanas temporales y, si hay estaciones independientes suficientes, exclusión espacial; Brier Score y fiabilidad de probabilidades, POD, tasa de falsas alarmas, precisión-recall, y errores en cantidades. Escenarios probabilísticos y límites de confianza.
- Estratificar costa, valles y zonas de mayor altitud sin confundir pertenencia regional; excluir zonas sin estaciones locales comprobadas de afirmaciones categóricas.
- **Condición de cierre:** modelo con habilidad demostrada respecto de referencias; si no la tiene, solo mostrar el pronóstico de la institución fuente y explicar limitaciones.

### Fase 4B — Riesgo fitosanitario en arándano
- Primer foco: **Botrytis cinerea**. Variables potenciales: temperatura, humedad, duración de humectación foliar y episodios de lluvia; requieren medición/estimación con escala pertinente, además de fenología, variedad y manejo.
- Etapa 1: «condiciones meteorológicas potencialmente favorables», basadas en bibliografía científica y declaradas **experimentales**.
- Etapa 2: convenio/protocolo de campo: fecha, GPS de parcela con consentimiento, fenología, incidencia/severidad, muestreo, manejo y confirmación diagnóstica según el diseño.
- Etapa 3: clasificador/probabilidad de incidencia validado fuera de muestra, evitando fuga de parcelas próximas, ciclos y fechas.
- **Condición de cierre:** verificar que el índice mejora frente a una referencia y que existe un conjunto sanitario de campo independiente. Sin registros reales, prohibido afirmar «predicción de enfermedad» o riesgo cuantificado.

### Fase 4C — Evaluación continua y alertas
- Archivar cada pronóstico **antes de la fecha que pretende predecir**, luego cotejar la observación futura independiente. Medir estabilidad por temporada, fenómeno ENSO y zona.
- Calibrar incertidumbre, revisar sesgos y publicar versiones con fecha.
- **Primera comunicación pública:** reproducir avisos de SENAMHI/ENFEN con enlace y fecha, distinguiéndolos del análisis experimental OAF.
- Alertas propias y recomendaciones fitosanitarias personalizadas solo después de demostrar calidad, definir responsable, umbrales y proceso de revisión, y documentar mantenimiento.

## 6. Plan de bajo presupuesto y herramientas

- **Python**: pandas, numpy, requests, xarray/rasterio, scikit-learn; GitHub Actions para pipelines versionados (dentro de límites gratuitos/plan de cuenta).
- **SIG**: GeoPandas, QGIS, datos administrativos oficiales, altitud, celdas espaciales; prohibir asignar estaciones a Lambayeque por simple proximidad (lección fase 3V).
- **GitHub Pages**: visor público estático que lee solo datos ya verificados, sin credenciales ni claves en JavaScript.
- **Servicios externos**: respetar licencia, restricciones y formatos; credenciales, si fueran necesarias, en secretos privados, nunca en repositorio.
- **Adquisición mínima de datos fitosanitarios**: colaboración con empresa/productores; si hay recursos para sensores, priorizar calidad de humedad/humectación y temperatura en campo frente a complejidad algorítmica.

## 7. Estado real heredado de las fases anteriores

**CONSERVAR:** todas las fases 3N–3Y, archivos SENAMHI y PISCOp/CHIRPS/ERA5, sensibilidad a coordenadas, auditorías de independencia, herramientas Python y boletines documentales. No modificar mediciones históricas ni simular nuevos resultados.

**COMPROBADO:** 1 109 meses-estación completos 1996–2015; 3 327 pares de estimación-producto en 3Q, evaluación retrospectiva; 79 combinaciones estación-año completas; 11 años completos comunes, último **2012**. CHIRPS/PISCOp potencialmente no independientes de las cinco estaciones.

**PENDIENTE:** fichas y código instrumental histórico, series diarias SENAMHI posteriores, validación realmente independiente, resultados de campo de enfermedades del arándano; datos recientes del nuevo pipeline 3Z aún **no capturados**, mapas de predicción/alertas **no implementados**.

## 8. Próximo trabajo priorizado

1. Catalogar y verificar fuente por fuente (autoridad, actualización, unidad, latencia, cobertura real, licencia).
2. Elegir un **producto reciente efectivamente accesible** e implementar su extracción técnica con pruebas y manejo de fallos.
3. Construir un panel que distinga nítidamente **observado/estimado/pronosticado**, fecha de emisión, cobertura, versión y leyenda de incertidumbre.
4. Añadir contexto oficial ENFEN con fecha y URL, nunca presentar escenarios de un comunicado antiguo como vigentes sin nueva comprobación.
5. Conseguir datasets de incidencia/severidad con georreferenciación responsable para el proyecto de arándano.
6. Diseñar evaluación predictiva prospectiva; el OAF no emitirá alertas propias hasta completar la validación.

**Documento rector para fases futuras.** El estado de implementación se actualiza por archivos de auditoría; la hoja de ruta es una intención de trabajo, no una afirmación de módulos ya terminados.

## Fuentes de referencia para integración futura

- ENFEN, comunicados: https://enfen.imarpe.gob.pe/comunicados/
- SENAMHI, datos diarios autorizados: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos
- Climate Hazards Center, CHIRPS v3: https://www.chc.ucsb.edu/data/chirps3
- NASA GPM, IMERG y datos: https://gpm.nasa.gov/data/imerg
- NOAA / CHIRPS / productos históricos y sus auditorías: revisar archivos del repositorio OAF.
