# Fase 10I — Random Forest EXCLUSIVO para predicción de lluvia

**OAF-Lambayeque · Objetivo operativo futuro: lluvia mensual; estado actual: investigación retrospectiva.**

## 1. Separación obligatoria de módulos

**Algoritmo predictivo del autor:** entrenar y publicar **solo Random Forest para lluvia**. Este algoritmo no clasificará plagas, enfermedades, infecciones, patógenos ni recomendará tratamientos agrícolas.

**Productos físicos de la lluvia:** predicción de lluvia mensual en **mm** y probabilidad de que un mes supere el **percentil 90 de precipitación de su sector** (P90 de CHIRPS calculado solo sobre 1997–2015). Los umbrales P90 no son alertas oficiales ni pronósticos del fenómeno El Niño costero.

**Humedad para consulta fitosanitaria:** la humedad relativa mensual y la temperatura de rocío son variables atmosféricas predictoras de precipitación y pueden mostrarse en una sección descriptiva. El **número de horas con humedad relativa alta** requiere datos **horarios**, no se obtiene sumando ni convirtiendo milímetros de lluvia mensual. La **duración de humectación foliar** requiere datos horarios y un método físico o empírico validado para el cultivo, o sensores de hoja; no equivale a horas con HR superior a un umbral. La futura consulta de humedad NO forma parte de la predicción fitosanitaria de este Random Forest.

Las [API horarias NASA POWER](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/) ofrecen HR, precipitación y otras variables horarias a su resolución original. La publicación [Suitability of relative humidity as an estimator of leaf wetness duration](https://doi.org/10.1016/j.agrformet.2007.09.011), *Agricultural and Forest Meteorology* (2008), diferencia la estimación de horas con hojas mojadas y la humedad ambiente; se debe validar según el dosel y cultivos, no declarar exactitud instrumental.

## 2. Variables multivariables disponibles, con procedencia y cobertura

El ensayo restringe todas las entradas dependientes del tiempo a **t−2 o más antiguas** en relación con el mes objetivo t.

| Dominio | Fuente y contenido | Tratamiento |
|---|---|---|
| Precipitación histórica | CHIRPS v3 FINAL, 39 sectores, 1996–2025 | Rezagos t−2, t−3, t−4, t−6, t−12, promedio rezagado |
| Temperatura oceánica tropical | Anomalías NOAA Niño 1+2 y Niño 3.4 | Indicador regional compartido t−2, NO SST medida en finca |
| Circulación oceano-atmosférica | SOI, alisios en Pacífico central/oriental | Indicador regional t−2 |
| Viento sobre océano | Pimentel y norte Lambayeque, fuentes archivadas | Señal regional t−2, NO viento de parcela |
| Temperatura/humedad de aire | NASA POWER T2M y RH2M | Muestra aproximada de grilla gruesa t−2 |
| Viento sobre superficie | NASA POWER WS10M | Señal de viento t−2 |
| Radiación de onda corta | NASA POWER ALLSKY_SFC_SW_DWN | Media diaria mensual, **kWh/m²/día**, t−2 |
| Presión de superficie | NASA POWER PS | kPa, t−2; NO presión reducida al nivel del mar |
| Punto de rocío | NASA POWER T2MDEW | °C, t−2 |
| Variables físicas derivadas | diferencia T−Td, VPD estimado de T/Td | Calculadas a partir de las mismas entradas t−2; **NO horas foliares** |
| Geografía/estacionalidad | Atributos sectoriales y vecindad CHIRPS 9K, sin solapamiento de píxel CHIRPS entre folds | Estáticos o conocidos antes del mes objetivo |
| Corrientes marinas | Archivo geostrófico disponible solo desde 2017 | No imputadas para 1997–2015, **EXCLUIDAS** |
| Humedad del suelo, nubosidad o dinámica sinóptica no homologada | No existe historia sectorial verificada compatible con la base | **EXCLUIDAS**, no inventadas |

NASA POWER se obtuvo para **siete grupos aproximados** de celdas meteorológicas, compartidos por 39 polígonos experimentales; no son 39 estaciones independientes. Su radiación de origen SRB/CERES presenta potenciales cambios de fuente que deben investigarse.

## 3. Entrenamiento — solo modelos Random Forest

| Experimento | Entrada | Salida RF regresión | Salida RF clasificación |
|---|---|---|---|
| L | lluvia CHIRPS histórica local | lluvia mensual mm | probabilidad de lluvia ≥P90 |
| LO | lluvia + índices océano / viento marino | lluvia mensual mm | probabilidad de lluvia ≥P90 |
| LA | lluvia + atmósfera NASA + VPD / depresión punto de rocío | lluvia mensual mm | probabilidad de lluvia ≥P90 |
| LOA | lluvia + océano + atmósfera y viento | lluvia mensual mm | probabilidad de lluvia ≥P90 |

**Mismos cortes temporales para todas las comparaciones:** entrenamiento **1997–2015**, selección de hiperparámetros en **2016–2018**, calibración de probabilidad por Platt **2019–2020** y prueba **2021–2025**. Cinco bloques geográficos de CHIRPS; la climatología sectorial mensual (media en mm y frecuencia suavizada P90, construida con 1997–2015) es una referencia obligatoria.

La regresión se selecciona por **MAE de validación**, distinguiendo salida de RF entrenado sobre lluvia mm o `log1p(mm)`. El clasificador por **Brier de validación** y calibración posterior en 2019–2020. Métricas de prueba: MAE, RMSE, sesgo, Brier, PR-AUC; evaluación separada 2023, pisos y bloques.

**Riesgo de selección del mejor brazo:** usar 2021–2025 para ordenar las cuatro configuraciones implica seleccionar retrospectivamente; no se puede presentar ese mismo periodo como nueva muestra de prueba completamente ciega del ganador. La prueba prospectiva as-issued y las observaciones independientes deben ocurrir posteriormente antes de habilitar avisos.

## 4. Reglas de publicación y decisión

El portal debe presentar las dos variables de precipitación y la comparación abierta de cuatro grupos físicos, junto con climatología. **Solo Random Forest se usa como familia predictiva en este módulo**. GCN permanece en el histórico metodológico como una comparación ya finalizada, sin ser algoritmo de predicción activo del portal.

No publicar como «mejor pronóstico validado» un modelo RF que no mejora la climatología en la métrica objetivo. Un modelo entrenado y documentado **sí puede publicarse como investigación experimental reproducible** si exhibe resultados, datos y controles de incertidumbre. Cualquier estimación futura de horas de humedad debe presentarse como un **producto meteorológico aparte**, con datos horarios y otra validación.

**Las predicciones oficiales de ENFEN/SENAMHI permanecen en la pestaña institucional**, independiente de estas investigaciones del autor. La lluvia alta P90 no determina por sí misma la ocurrencia de Niño costero ni una infección agrícola.

## 5. Archivos verificables
- [Código Python RF lluvia](modelos/random_forest_lluvia_multivariable_10i.py)
- [Tests de siete invariantes](tests/test_rf_solo_lluvia_10i.py)
- [Entrenamiento automatizado](.github/workflows/oaf_10i_rf_precipitacion.yml)
- [Comparador exclusivo de lluvias](random-forest-lluvias.html)
- [Evaluación CSV al terminar](datos/rf_precipitacion_10i/evaluacion_emparejada_10i.csv)
- [Informe JSON al terminar](datos/rf_precipitacion_10i/informe_rf_lluvia_10i.json)
- [Fuente NASA POWER 10H](datos/nasa_power_10h/auditoria_fuentes_10h.json)

## Próxima evaluación de validez antes de alertas
Recuperar estaciones pluviométricas SENAMHI externas, versiones históricas de emisiones y sus retrasos, y datos meteorológicos horarios si se implementa duración de condiciones húmedas; evaluar estratos altitudinales y un bloqueo que incluya celdas NASA compartidas; obtener un periodo de prueba prospectivo que no se utilice para elegir entre las cuatro configuraciones.
