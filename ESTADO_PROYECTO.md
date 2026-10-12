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
