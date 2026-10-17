# OAF-Lambayeque — Fase 9A: impacto predictivo de humedad relativa y VPD

**Fecha del experimento:** octubre de 2026. **Dictamen:** benchmark retrospectivo reproducible, **sin justificación científica para activar automáticamente RH/VPD en alertas ni pronósticos operativos**.

## Pregunta concreta

¿Agregar humedad relativa (RH) y déficit de presión de vapor (VPD) aporta habilidad fuera de muestra para estimar temperatura del aire y precipitación mensual, o para detectar superaciones del P90 en enero–abril, frente al modelo original de OAF-Lambayeque (Fase 8W) que ya utiliza variables locales, viento y SST Niño 1+2/Niño 3.4?

## Diseño, cobertura y controles

- **Región:** Chiclayo, Jayanca, Motupe y Olmos, cuatro **referencias de celdas reanálisis**, no conjunto representativo de todos los pisos altitudinales de Lambayeque ni estaciones SENAMHI verificadas.
- **Clima histórico:** 1996–2025 (ERA5/ERA5-Land); RH y VPD diarios del histórico [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api), convertidos a 1.440 registros mensuales, cuatro referencias × 360 meses. La variable VPD aquí es la **media mensual del máximo diario**, no VPD horario promedio, ni dato del dosel.
- **Prueba temporal:** 5 bloques de 36 meses — 2011–2013, 2014–2016, 2017–2019, 2020–2022, 2023–2025. El entrenamiento acaba siempre al inicio del bloque; los objetivos de prueba jamás ajustan medias climatológicas, escalados ni Ridge. RH y VPD son **del mes origen** `t`, no del mes objetivo `t+h`, para horizontes **h=1,2,3 meses**.
- **Comparador idéntico 8W:** `local_viento_sst` frente a tres modelos anidados: +RH, +VPD, +RH/VPD. Coeficientes de regresión Ridge con el **mismo alpha 15**; transformación `log1p` de la precipitación en training, evaluando MAE/RMSE en mm. Se exige que la predicción de base 9A reproduzca dentro del redondeo la predicción **ya archivada de 8W** para cada localidad, fecha objetivo y horizonte (comprobación automática).
- **Evento:** lluvia enero–abril superior al percentil P90 mensual local **ajustado solo en training**, usando logística regularizada con entrenamiento pasado y Brier en las fechas de prueba. No calibración prospectiva. Para el evento P90 se compara +RH/VPD frente al modelo 8W original, exactamente con mismas etiquetas y umbrales. La estación lluviosa se considera por separado para error continuo 2017 y 2023 (4 meses cada año).
- **Fuentes y versiones:** metadatos SHA-256 del propio repositorio y de entrada 8V, humedad 8Z y 8W; índices oceánicos NOAA revisados, reanálisis ERA5 retrospectivos **no “vintage” disponible en fecha de emisión**. Un mes origen completo puede publicarse después de empezar el mes objetivo. Por tanto, **no constituye pronóstico real generado con información conocida a tiempo**.

### Implementación ejecutada

- Motor: [`modelos/sensibilidad_humedad_vpd_9a.py`](modelos/sensibilidad_humedad_vpd_9a.py)
- 8 tests sintéticos de fuga de futuro, reglas temporales, productos y tramos extremos: [`tests/test_sensibilidad_humedad_vpd_9a.py`](tests/test_sensibilidad_humedad_vpd_9a.py).
- Workflow GitHub Actions: [`oaf_sensibilidad_humedad_vpd_9a.yml`](.github/workflows/oaf_sensibilidad_humedad_vpd_9a.yml). Ejecuta tests + datos reales + validación contra 8W + revisión de gráfico y actualización de repositorio.
- [Matriz de **17.280 pares modelo–fecha–objetivo**](datos/benchmark_9a/pronosticos_pareados_9a.csv), [**1.440 predicciones probabilísticas** de lluvia P90](datos/benchmark_9a/eventos_p90_pareados_9a.csv) y [estado con MAE, RMSE, Brier, cortes, sensibilidad extrema y SHA](datos/benchmark_9a/estado_benchmark_9a.json). Los registros son predicciones múltiples sobre una muestra **altamente autocorrelacionada**, no 17.280 observaciones independientes.

## Resultados agregados objetivos

### Temperatura y precipitación mensual

De 12 combinaciones de 4 localidades × 3 horizontes para temperatura:
- **+RH:** mejora MAE respecto de 8W en **6/12**.
- **+VPD:** mejora en **5/12**.
- **+RH+VPD:** mejora en **5/12**.

De 12 combinaciones de lluvia:
- **+RH:** mejora en **6/12**.
- **+VPD:** mejora en **6/12**.
- **+RH+VPD:** mejora en **6/12**.

En valores directos a **h=1** (MAE del modelo 8W vs modelo +RH+VPD):

| Localidad, objetivo | 8W (referencia) | + RH y VPD | Cambio en MAE |
|---|---:|---:|---:|
| Chiclayo temperatura | 0,430439 °C | 0,427934 °C | mejora 0,582 % |
| Jayanca temperatura | 0,378756 °C | 0,378033 °C | mejora 0,191 % |
| Motupe temperatura | 0,336764 °C | 0,338335 °C | empeora 0,467 % |
| Olmos temperatura | 0,333740 °C | 0,330774 °C | mejora 0,889 % |
| Chiclayo precipitación | 10,018625 mm | 10,258646 mm | empeora 2,396 % |
| Jayanca precipitación | 36,796392 mm | 38,560249 mm | empeora 4,794 % |
| Motupe precipitación | 45,689133 mm | 46,603207 mm | empeora 2,001 % |
| Olmos precipitación | 36,638134 mm | 36,576657 mm | mejora 0,168 % |

Las ventajas de temperatura normalmente quedan alrededor de 0–1 %, y en lluvia existen deterioros grandes y localizados. Esta evidencia **no permite elegir RH+VPD como reemplazo por defecto**. El desempeño depende del lugar, horizonte, estación y objetivo.

### Estabilidad entre cinco periodos

De 12 combinaciones por objetivo, la variante completa RH+VPD:
- mejora en **≥3 de los 5 bloques:** **6/12** de temperatura y **5/12** de precipitación.
- mejora en **≥4 de los 5 bloques:** **2/12** de temperatura y **1/12** de precipitación.

Solo 1/12 combinaciones de precipitación logra beneficios en al menos 4 cortes. Si seleccionáramos exclusivamente el promedio 2011–2025 sin revisar años, sobreestimaríamos la confiabilidad del modelo.

### Eventos de lluvia superior al P90: Brier Score

En 12 combinaciones de localidad × horizonte, **+RH+VPD mejora el Brier Score solo en 1/12**: Olmos con horizonte 1 mes, Brier 8W **0,07386706**, +RH+VPD **0,07338589** (mejora relativa 0,65 %). En los otros 11/12 **empeora**. Motupe horizonte 1 mes: **0,06547514** base frente a **0,06745484** ampliado.

Brier es error cuadrático de probabilidades frente a ocurrencia 0/1, y debe evaluarse junto con calibración, habilidad frente a climatología y muestras suficientemente grandes. Los métodos de verificación y sus límites están explicados por [ECMWF Forecast evaluation](https://www.ecmwf.int/en/research/modelling-and-prediction/forecast-evaluation), [ECMWF Forecast User Guide](https://confluence.ecmwf.int/pages/viewpage.action?pageId=363864334) y [WMO S2S Verification](https://confluence.ecmwf.int/spaces/WLS/pages/394992254/Verification).

**Dictamen para pronóstico de lluvia extrema:** la evidencia actual **desaconseja** activar +RH+VPD por defecto; conservar 8W como referencia experimental, sin alertas agrícolas ni sanitarias.

### Auditoría de episodios 2017/2023

Se archivaron errores MAE/RMSE por localidad, año, modelo, horizonte y objetivo, solo enero–abril (4 meses). Ejemplo de lluvia Motupe 2017 a 1 mes: 8W MAE **283,089991 mm**, +RH MAE **272,840344 mm** pero +RH+VPD **284,323735 mm**; en lluvia extraordinaria, ni siquiera los predictores añadidos se comportan uniformemente. Debe verificarse lluvia del reanálisis contra estaciones instrumentales y daños históricos.

El gran episodio **1997–1998 NO constituye holdout**, puesto que entra en entrenamiento de todos los cortes 9A. Una demostración seria de predicción de Niño Costero requerirá una evaluación independiente y diseño de ventanas que ensayen episodios intensos, sin fuga temporal ni datos revisados posteriores.

## Conclusión científica

El proyecto pasó de coleccionar variables a **medir si cada nueva variable realmente agrega habilidad predictiva**. El resultado de 9A es predominantemente negativo para extremos y no consistentemente positivo para temperatura o lluvia. No deben confundirse VPD de aire libre con humedad foliar o con condiciones epidemiológicas observadas de *Botrytis*, oídio o enfermedades de vid/arándano.

El módulo 9A de la [web del OAF](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones) permite filtrar por localidad/horizonte/objetivo, visualizar el cambio de MAE por cada uno de los cinco cortes, y cotejar temporada 2017–2023 y P90. La actualización del portal dependerá del despliegue de GitHub Pages.

### Propuesta fase 9B

Priorizar tres trabajos reales: **(i)** intervalos de incertidumbre de diferencias de error mediante remuestreo de bloques de años con pareado temporal y corrección de multiplicidad; **(ii)** evaluación independiente SENAMHI y episodios extremos por cuenca y pisos altitudinales homogéneos; **(iii)** ensayo con emisión auténticamente retrospectiva y variantes de desfase de fuentes para evitar que ERA5/NOAA revisados generen una ilusión de previsión anticipada. En paralelo, continuar adquisición de aerosoles MERRA-2 autenticada, sin inventar concentración PM ni tratamientos fitosanitarios.
