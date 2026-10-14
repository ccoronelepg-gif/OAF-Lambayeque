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
