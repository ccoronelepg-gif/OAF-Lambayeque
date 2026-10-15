# Fase 8E — Primeras emisiones verdaderamente archivadas de temperatura regional en Lambayeque

**Proyecto:** Observatorio Agroclimático y Fitosanitario OAF-Lambayeque.  
**Autor:** Ing. Agrónomo Carlos Enrique Coronel García.  
**Primera ejecución real:** **15 de octubre de 2026, 01:41:18 (hora peruana)**.  
**Estado:** predicciones experimentales de temperatura **sin capacidad prospectiva verificada todavía**. La serie de referencia es ERA5-Land, NO una estación SENAMHI.

## 1. Objetivo

Avanzar desde la Fase 8D, que evaluó modelos históricos de temperatura, precipitación y radiación, hacia predicciones **genuinamente fechadas** de temperatura media mensual de cuatro localidades referenciales (Chiclayo, Jayanca, Motupe y Olmos). Guardar el resultado y sus datos antes de observar los meses futuros, para comparar después sus errores reales contra referencias sencillas.

La predicción de anomalías del Niño Costero y el desarrollo fitosanitario para **arándano y vid** siguen siendo líneas científicas del OAF, pero las emisiones de temperatura 8E **NO** constituyen alertas ENFEN/SENAMHI ni un modelo de enfermedad.

## 2. Modelo y fuentes disponibles a la emisión

**Predicción:** temperatura media mensual **a dos metros** de una cuadrícula climática de ERA5-Land (°C), y su anomalía respecto a la referencia 1996–2022.

**Fuentes y fechas del primer origen septiembre 2026:**
- Temperatura regional mensual hasta **2026-09**, derivada de [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), modelo **ERA5-Land**. Los puntos son representativos de localidades, no de parcelas ni observaciones instrumentalmente verificadas.
- Anomalía de temperatura superficial del mar **Niño 1+2 hasta 2026-09** obtenida de [NOAA NCEI ERSSTv5](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat), recalculada en Fases 6D/8A al periodo 1991–2020 por el OAF. Para septiembre: **+4,38867 °C**. **No equivale al índice ICEN oficial de ENFEN**.
- **T300 de 2026-08**, anomalía de la temperatura oceánica media entre 0–300 m, fuente [NOAA/PMEL GODAS](https://www.pmel.noaa.gov/tao/wwv/data/t300.dat), **+1,320034 °C** con referencia diferente (1981–2010). T300 representa el mes anterior al origen, para reducir riesgo de utilizar datos todavía no publicados.
- Se archivaron hashes SHA-256 del modelo Python y de los tres archivos originales regional, Niño 1+2 y T300, para hacer comprobable qué datos sustentaron la emisión. Las predicciones se escriben **una sola vez** en `datos/pronosticos_temperatura_regional_8e/AAAA-MM.json`, por mes de origen, y no se sobrescriben.

**Modelo estadístico (sin retocar parámetros tras 2022):**
- **Referencia local:** Ridge `alpha=20`, predictor anomalía de la temperatura de la localidad en el mes `t`.
- **Modelo ampliado:** Ridge `alpha=20`, anomalía local en `t`, SST Niño 1+2 en `t`, y T300 en `t−1`.
- Para ambas alternativas, el resultado es una **anomalía predicha en °C** a la que se suma la **media normal histórica del mes objetivo**, calculada EXCLUSIVAMENTE a partir de **1996–2022**. No se utiliza 2023–2026 para calibrar coeficientes o fijar la climatología de prueba.
- La climatología histórica de **30 años 1996–2025** sigue siendo la referencia descriptiva aprobada para el OAF. No se utiliza para recalibrar esta primera emisión, pues incorpora años del periodo de prueba de la Fase 8D.
- Las ventanas h1/h2/h3 tienen su propio ajuste; solo entran resultados de entrenamiento cuyo **mes objetivo sea anterior o igual a diciembre 2022**. Se validó el esquema con datos sintéticos, sin publicarlos como hallazgos agrícolas.

## 3. Primera emisión: estimaciones para octubre–diciembre 2026

**Archivo original y hora exacta:** [2026-09.json](datos/pronosticos_temperatura_regional_8e/2026-09.json), UTC según su campo `emision_utc`, y hora de Perú `2026-10-15T01:41:18-05:00`.

| Localidad | Mes objetivo | Tipo de emisión | Modelo solo local (°C) | Modelo local + Niño1+2 + T300 (°C) | Normal fija 1996–2022 (°C) |
|---|---|---|---:|---:|---:|
| Chiclayo | 2026-10 | Intramensual | 23.66 | 23.98 | 19.22 |
| Chiclayo | 2026-11 | Anterior al mes | 23.92 | 24.35 | 20.13 |
| Chiclayo | 2026-12 | Anterior al mes | 25.17 | 25.61 | 21.94 |
| Jayanca | 2026-10 | Intramensual | 24.16 | 24.50 | 20.65 |
| Jayanca | 2026-11 | Anterior al mes | 24.38 | 24.83 | 21.38 |
| Jayanca | 2026-12 | Anterior al mes | 25.38 | 25.89 | 22.87 |
| Motupe | 2026-10 | Intramensual | 23.51 | 23.79 | 20.50 |
| Motupe | 2026-11 | Anterior al mes | 23.64 | 24.00 | 20.99 |
| Motupe | 2026-12 | Anterior al mes | 24.56 | 24.98 | 22.34 |
| Olmos | 2026-10 | Intramensual | 23.89 | 24.18 | 21.13 |
| Olmos | 2026-11 | Anterior al mes | 23.85 | 24.22 | 21.36 |
| Olmos | 2026-12 | Anterior al mes | 24.75 | 25.18 | 22.62 |

**Diferencia epistemológica esencial:**
- **Octubre 2026** es una **estimación intramensual**, porque se emitió el 15 de octubre. No debe contarse como un pronóstico de octubre previo al inicio de ese mes.
- **Noviembre y diciembre 2026** son **pronósticos almacenados antes del comienzo de esos meses**. Si la fuente observacional se vuelve disponible, permitirán evaluar genuinamente el error de las cifras que el modelo había publicado.
- Esta emisión contiene **4 estimaciones intramensuales y 8 pronósticos anteriores al mes objetivo**. No existen resultados posteriores al objetivo en su fecha de emisión.
- Se muestran siempre **ambos modelos**, incluso si en el futuro la versión Niño/T300 resulta peor que la referencia local.
- No se han construido intervalos predictivos calibrados ni se declara probabilidad de superar umbrales térmicos: la evaluación 8D fue inestable salvo una señal preliminar en Jayanca a tres meses.

## 4. Verificación verdaderamente posterior

Motor [modelos/pronostico_temperatura_regional_8e.py](modelos/pronostico_temperatura_regional_8e.py), con la ejecución de [GitHub Actions](.github/workflows/oaf_temperatura_regional_8e.yml). El flujo se programa los días **12, 19 y 26 de cada mes**, consulta las fuentes y realiza las siguientes operaciones:

1. **Emisión condicionada:** para un nuevo mes de origen, exige temperatura de ERA5-Land completa, anomalía Niño 1+2 del mismo mes y T300 del mes anterior efectivamente disponibles. Si NOAA/PMEL tiene retraso o falla la API, **no se inventa un nuevo pronóstico**. Las temperaturas de meses completados posteriores a septiembre se descargan en consulta multisitio si es necesario, con control de 24 h calendarias por día en las medias diarias del proveedor.
2. **No sobrescritura:** si ya hay emisión por el mes de origen, se conserva exactamente el JSON previo y no se vuelve a estimar retrospectivamente.
3. **Verificación temporal:** solo se consulta el dato del **mes objetivo completo** no antes del día **10 del mes siguiente** (mes objetivo octubre → primera fecha elegible 10 noviembre 2026), y únicamente si ERA5-Land tiene todos los días del mes. Open-Meteo informa que ERA5-Land tiene un retraso aproximado de varios días. Si faltan datos, se mantiene **pendiente**, nunca se sustituye por cero.
4. **Errores:** con datos reales disponibles se calcula la diferencia entre cada pronóstico archivado y la temperatura ERA5-Land mensual posterior. Se conserva el CSV por localidad, mes, horizonte y tipo de emisión.
5. **Evaluación correcta:** el MAE de la predicción genuina solo incluye emisiones **anteriores al mes objetivo**. Las estimaciones intramensuales se muestran por separado y NO se incorporan artificialmente a la habilidad de anticipación premes.
6. **Acumulación necesaria:** un trimestre por sí solo **no** constituye prueba científica de habilidad prospectiva. Mantener explícito el conteo de observaciones comparadas y el estado `habilidad_prospectiva_demostrada=false`.

**Resultado real de la primera ejecución:**

- Estado público: `esperando_cierre_y_reanalisis`.
- **1 emisión** con 12 pronósticos; 8 previos al inicio de su mes objetivo y 4 intramensuales.
- **0** observaciones posteriores verificadas; el CSV de evaluación contiene **solo encabezados**, sin fabricar aciertos.
- **Primera fecha posible de comprobación: 10/11/2026**, sujeto a disponibilidad posterior de temperatura ERA5-Land.

Archivos:
- [JSON de verificación](datos/verificacion_temperatura_regional_8e.json).
- [CSV de errores posteriores](datos/verificacion_temperatura_regional_8e.csv).
- [Emisión con fecha y variables](datos/pronosticos_temperatura_regional_8e/2026-09.json).
- [Código fuente reproducible](modelos/pronostico_temperatura_regional_8e.py).
- [Portal — Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), módulo «Fase 8E», con 12 temperaturas y su referencia local.

**Advertencias sobre verdad observada:** el contraste usa **reanálisis ERA5-Land**, no estaciones de medición SENAMHI; el proveedor puede revisar los registros anteriores. Para conseguir validación instrumental realmente independiente se necesitan series de estaciones meteorológicas de Lambayeque con controles de calidad y cobertura representativa.

## 5. Por qué lluvia y radiación siguen una línea separada

La Fase 8D obtuvo un MAE mayor al añadir Niño1+2/T300 para **precipitación y radiación solar** en las doce comparaciones localidad×horizonte. Por tanto **no se emiten falsas alertas futuras de lluvia ni radiación** con el modelo 8E.

Las próximas pruebas deberán usar modelos distintos:
- **Precipitación:** considerar por separado ocurrencia de lluvia y magnitud mensual, validación sobre estaciones SENAMHI y productos satelitales CHIRPS, base estacional 1996–2025 y atención a lluvias intensas con muestras suficientes.
- **Radiación:** evaluar previsores atmosféricos regionales, nubosidad y observación instrumental/satelital, diferenciando radiación global (MJ/m²), PAR y UV.
- **Ambos:** comparar contra climatología y modelos locales que fueron mejores en 8D, y no ajustar parámetros después de ver los resultados de meses usados para evaluación.

## 6. Siguiente fase propuesta: 8F

La Fase 8F debe concentrarse en **validación instrumental independiente**: identificación de estaciones SENAMHI comparables con puntos regionales, control de datos faltantes, registro de coordenadas y altitud y análisis de diferencia reanálisis–estación. Podrá incorporar modelos especializados para lluvia y radiación como líneas separadas, sin alterar emisiones prospectivas 8A/8E.

No se debe mezclar la verificación de temperatura regional con el progreso de la validación de *Botrytis* en arándano, que todavía requiere registros de campo, ni inferir a partir del calentamiento marino el pronóstico oficial ENFEN del **Niño Costero**.

**Resumen:** la Fase 8E aporta la primera predicción regional realmente archivada con origen, objetivos, hora y modelos comparables. La utilidad futura se decidirá **por sus errores prospectivos reales**, no por su atractivo estadístico o los resultados históricos de 8D.
