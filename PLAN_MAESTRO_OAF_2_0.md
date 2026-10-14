# PLAN MAESTRO OAF-Lambayeque 2.0
## Del análisis retrospectivo a la vigilancia y predicción agroclimática y fitosanitaria

**Aprobación de orientación:** 14/10/2026.  
**Responsable y autor:** ING. AGRÓNOMO CARLOS ENRIQUE CORONEL GARCÍA.  
**Región de trabajo:** Lambayeque, Perú, con contexto oceanográfico del Pacífico oriental y regional del norte peruano.  
**Situación:** Plan de reorganización aprobado; **los módulos predictivos y las alertas propias aún no se han desarrollado ni validado**. No declarar que el OAF anticipó un fenómeno por consultar informes publicados.

## 1. Misión renovada

> Desarrollar un sistema regional de **vigilancia, predicción probabilística y alerta temprana experimental** de anomalías agroclimáticas y condiciones de riesgo fitosanitario en Lambayeque, integrando observaciones oficiales, información oceánica, satélites, pronósticos meteorológicos y registros agronómicos de campo, con trazabilidad, actualización reciente y evaluación independiente.

La salida inicial de un módulo no validado se etiqueta **experimental / no operativo**. Las alertas meteorológicas y clasificaciones de El Niño Costero **oficiales** corresponden a ENFEN y SENAMHI: el OAF las reproduce con fuente, fecha y validez, no las suplanta.

## 2. Preguntas que debe responder el sistema

1. **Estado oceánico:** ¿qué declara oficialmente ENFEN sobre El Niño Costero (región Niño 1+2) y cuáles son los escenarios/probabilidades con fecha de emisión?
2. **Condición observada reciente:** ¿cuándo y dónde se han observado o estimado anomalías de lluvia, temperatura y humedad? Distinguir siempre dato de pluviómetro de estimación satelital y su incertidumbre.
3. **Pronóstico:** ¿cuál es la probabilidad de un evento de lluvia/temperatura en 1–7 días, 2–6 semanas o 1–6 meses, según la fuente y su capacidad verificada?
4. **Implicaciones para los cultivos:** ¿hay condiciones meteorológicas favorables para el desarrollo de patógenos y plagas del arándano, y las observaciones de campo confirman eventos de enfermedad?
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
| **M1 — Vigilancia oceánica** | Escenarios ENSO | ENFEN (comunicados/ICEN Niño 1+2), SST/índices con procedencia | Estado oficial con fecha, evolución e incertidumbre | Fuente vigente verificable y sin inferencia del OAF sobre estado ENFEN |
| **M2 — Vigilancia agroclimática** | Anomalías regionales | SENAMHI, CHIRPS v3 preliminar/final, NASA IMERG V07, metadatos geográficos | Lluvia y temperatura recientes, anomalías/percentiles por área | Validación espacial, fechas, píxeles y calidad suficientes |
| **M3 — Pronóstico meteorológico** | Predicción prospectiva | Fuentes oficiales de pronósticos con fecha de emisión, ensembles cuando existan | Probabilidades de excedencia por horizonte (1–7 días; subseasonal y estacional) | Evaluación retrospectiva *sin filtración temporal* y control prospectivo; no usar reanálisis como pronóstico |
| **M4 — Riesgo fitosanitario** | Arándano, posteriormente otros cultivos | Meteorología, fenología, variedad, humectación, registros de incidencia/severidad | Condiciones favorables a Botrytis; después probabilidad de enfermedad calibrada | Suficientes observaciones independientes de campo y validación fuera de muestra |
| **M5 — Comunicación** | Transparencia y decisiones | Resultados M0–M4 | Panel, mapas, fechas, límites de incertidumbre y avisos **oficiales** | Auditoría de mensajes; alertas *propias* solo tras validación y reglas aprobadas |

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
