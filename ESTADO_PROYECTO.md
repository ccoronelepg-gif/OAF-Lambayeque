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
