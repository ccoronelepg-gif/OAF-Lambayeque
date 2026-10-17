# Fase 8U — Vientos atmosféricos, temperatura superficial del mar y corrientes marinas de Lambayeque

**OAF-Lambayeque · periodo climático terrestre 1996–2025 · versión experimental de octubre de 2026.**

## 1. Propósito físico y agrícola

Las anomalías de temperatura y lluvia en Lambayeque no pueden estudiarse únicamente con un índice oceánico aislado. La circulación atmosférica, la TSM regional, los vientos sobre el mar, la transferencia de calor océano–atmósfera, la circulación marina y la topografía local actúan a distintas escalas. Las fases anteriores señalaron que modelos sencillos local+regional mejoran modestamente la persistencia para anomalías de temperatura del aire **dentro del reanálisis**; pero la variable Niño1+2 t−2 añadió mejora mínima o negativa en 8T. La fase 8U construye una base para estudiar nuevos mecanismos, sin inventar capacidad de predicción ni igualar estaciones y modelos.

**Tres conceptos diferentes:**

1. **Viento del aire**, ERA5 a 10 m: vector atmosférico, dirección meteorológica indica **de dónde procede** (FROM); la fuerza y persistencia de vientos cercanos a la costa pueden modificar condiciones marinas.
2. **TSM (SST)**: temperatura del agua superficial, °C, y anomalía respecto de la referencia propia del índice; el **Niño 1+2** es una región grande, no una estación frente a cada localidad.
3. **Corrientes marinas**: vector de velocidad del **agua**, m/s, dirección **hacia dónde se desplaza** (TO), con parte geostrófica, parte asociada al viento/Ekman, mareas y otras componentes. Viento del aire y corriente marina no son intercambiables ni tienen iguales direcciones por definición.

## 2. Viento ERA5 1996–2025 — resultados efectivamente recuperados

Tres archivos originales de datos diarios ERA5 1996–2005, 2006–2015 y 2016–2025, consultados mediante Open-Meteo Historical Weather, fueron archivados con URL exacta, marca temporal y huella SHA-256.

**Cobertura confirmada:** seis puntos de referencia (cuatro sobre territorio y dos sobre mar abierto de diseño), **360 meses completos por punto, 2.160 registros mensuales**, seis celdas ERA5 distintas.

| Punto de muestreo | Velocidad media del viento histórico 10m |
|---|---:|
| Chiclayo | 3,138 m/s |
| Jayanca | 2,410 m/s |
| Motupe | 1,890 m/s |
| Olmos | 1,393 m/s |
| Referencia marítima frente al sector de Pimentel (lat −6,8; lon −81,0) | 4,994 m/s |
| Referencia marítima norte (lat −5,9; lon −81,5) | 5,134 m/s |

Estos promedios se calcularon sobre **1996–2025** con el reanálisis, no proceden de anemómetros locales. El viento diario se descompone **aproximadamente** en componentes zonal (u, este) y meridional (v, norte): si la velocidad media del día es s y su dirección dominante meteorológica (FROM) es θ, entonces `u ≈ −s·sen(θ)`, `v ≈ −s·cos(θ)`. Esa operación **no sustituye promediar cada velocidad horaria verdadera**, especialmente cuando el viento rota durante el día. Los puntos de consulta marinos aún requieren máscara tierra-mar oficial para confirmación territorial y no representan fondeaderos, playas o boyas.

Datos: [archivo de estado y SHA](datos/meteorologia_8u/estado_viento_8u.json), [CSV mensual de seis puntos](datos/meteorologia_8u/vientos_mensuales_8u.csv), [motor de auditoría](modelos/vientos_atmosfericos_8u.py), [pruebas](tests/test_vientos_atmosfericos_8u.py) y [workflow](.github/workflows/oaf_vientos_8u.yml).

El módulo 8U previamente incorporado al observatorio también documenta cuatro localidades de viento por otra ruta y correlaciones **meramente descriptivas**, 1996–2025, entre sus anomalías de viento y SST Niño1+2 t−2. Una de las correlaciones publicadas (u aproximada Chiclayo frente al índice rezagado) es **r≈−0,402**. Eso no demuestra causalidad, transporte de calor ni habilidad predictiva: las normales descriptivas 1996–2025 contienen información posterior a fechas de prueba retrospectivas y **no se utilizarán como normales de entrenamiento sin recálculo por corte**.

## 3. Temperatura superficial del mar — dos escalas que no deben mezclarse

**Regional**: se reutilizó la respuesta NOAA CPC `sstoi.indices` congelada por la fase 8T. Su archivo original auditado tiene **360 meses 1996–2025**, y se extrajeron **TSM absoluta de Niño 1+2, anomalía Niño 1+2, SST Niño 3.4 y anomalía Niño 3.4**. Se conserva exactamente la respuesta original, sin simular TSM cerca del litoral. Su índice contiene revisiones retrospectivas y no equivale a versiones en tiempo real para cada fecha histórica de backtest, ni necesariamente a ICEN oficial de ENFEN.

[Temperatura marina Niño 1+2/3.4 archivada](datos/oceanografia_8u/tsm_nino12_mensual_8u.csv) · [catalogación de fuentes](datos/oceanografia_8u/estado_oceanografia_8u.json).

**Más cercana a la costa**: el proyecto cuenta también con un experimento de [NOAA OISST v2.1 de 0,25°](datos/sst_costera_8u/estado_sst_8u.json) en puntos oceánicos de ensayo. La recuperación es incremental y **no debe declararse completa mientras existan días ausentes**: en una década oceánica se detectaron **511 días faltantes**, suficientes para invalidar una climatología diaria continua. OISST es análisis de satélite y otras fuentes, no termómetro costero instrumental, y necesita máscara océano/tierra. En las predicciones conservar separados SST de celda local, índice Niño1+2 y registros instrumentales.

## 4. Corrientes marinas — evidencia disponible y sus límites temporales

**A. Instantánea marina física modelada**: la fase 8U archiva además **72 horas** de corriente y temperatura marina modeladas por Open-Meteo Marine/Météo-France para **tres puntos de mar abierto**, con componentes u/v obtenidas de la dirección de flujo **hacia** la que se mueve el agua, no dirección meteorológica de procedencia. Ver [estado y fecha de la instantánea](datos/marino_8u/estado_marino_8u.json). Es una salida del modelo oceanográfico de corto horizonte, **no** una normal 1996–2025, ni una boya validada, ni una predicción ENSO.

**B. Historia parcial geostrófica NOAA/AOML**: se implementó una segunda vía independiente usando [NOAA CoastWatch, `miamicurrents`](https://coastwatch.pfeg.noaa.gov/erddap/griddap/miamicurrents.html), cuyas variables originales `u_current` y `v_current` miden componente este/norte de **corriente geostrófica** en m/s. El servicio declara cobertura aproximada desde julio de **2016**; por tanto, no hay base para afirmar una historia 1996–2025. Se recuperaron y verificaron los **cuatro subconjuntos previstos** de **2017–2025** para **dos puntos marítimos**, con **3.287 días por punto, 6.574 registros diarios válidos en total y 216 promedios mensuales** (108 por sitio). Los archivos originales de NOAA/AOML se conservaron con metadatos y huella SHA-256. La primera fuente 2017–2020 para el punto al oeste de Pimentel conserva SHA original `3038574fb51b301c8888acf3d723a9cd18a5d665fce6987827cd20aeccdc8994`. Durante las consultas hubo alguna respuesta HTTP 403, pero los reintentos posteriores permitieron completar el subconjunto **2017–2025**; **esto no completa 1996–2025**.

| Punto de ensayo | Periodo íntegro | Componente geostrófica media u (hacia este) | Componente geostrófica media v (hacia norte) |
|---|---|---:|---:|
| Frente al sector de Pimentel (−6,7; −81,1) | 2017–2025 | **−0,0480 m/s** | **+0,0908 m/s** |
| Norte de Lambayeque (−5,9; −81,5) | 2017–2025 | **+0,0668 m/s** | **+0,0120 m/s** |

Los promedios son de las componentes de **la corriente geostrófica modelada**, no el transporte total paralelo a la costa, ni una estimación de corriente litoral en la playa. **No se imputó ningún día**.

[Estado real de cobertura](datos/corrientes_8u/estado_corrientes_8u.json) · [CSV mensual de vectores, solamente meses reales](datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv) · [script de consulta/QA](modelos/corrientes_geostroficas_8u.py).

**C. Productos para completar la historia física**: [NASA/PO.DAAC OSCAR v2 final](https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0) ofrece vectores oceánicos basados en datos satelitales y dinámica geostrófica/Ekman; [Copernicus Marine reanálisis global](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description) ofrece componentes oceanográficas y temperatura por niveles desde 1993. Su acceso y extracción por coordenadas/localización para toda la costa y el periodo 1996–2025 **no están verificados ni integrados aquí**. El producto OSCAR antiguo que aparece en ciertos formularios NOAA `jplOscar`, pese a su título amplio, declara en sus metadatos solo 2011–2014, por lo que fue descartado como fuente histórica continua.

## 4A. Relación descriptiva entre las tres variables (108 meses comunes, 2017–2025)

Con los dos subconjuntos históricos de corriente geostrófica ya completos para **2017–2025**, se emparejaron por mes los vectores geostróficos NOAA/AOML, las componentes aproximadas de viento atmosférico ERA5 de los dos sitios marítimos de referencia y la anomalía de SST regional Niño 1+2 del CPC NOAA **t−2**. Para cada serie se sustrajo su normal del mes calendario calculada sobre **2017–2025 (nueve años)**. Esos promedios utilizan los años posteriores de la ventana: están permitidos en un análisis de asociación descriptivo, **pero no deben emplearse para ajustar un backtest que pretenda evaluar predicciones pasadas**.

| Asociación entre anomalías mensuales | Sector oeste de Pimentel (108 meses) | Sector norte (108 meses) |
|---|---:|---:|
| Componente zonal del viento (u) vs corriente geostrófica (u) | **r = 0,25820** | **r = 0,04878** |
| Componente meridional del viento (v) vs corriente geostrófica (v) | r = 0,17916 | r = 0,08190 |
| Velocidad media del viento vs magnitud de corriente geostrófica | r = 0,22285 | r = 0,06039 |
| SST Niño 1+2 t−2 vs corriente este (u) | r = −0,08923 | r = 0,00582 |
| SST Niño 1+2 t−2 vs corriente norte (v) | r = 0,08461 | r = 0,05340 |

Interpretación: **no aparece una relación fuerte y uniforme** entre esas tres variables en ambos puntos y bajo estas definiciones. Los coeficientes no demuestran causalidad, que la corriente geostrófica responda instantáneamente al viento, que no exista corriente de Humboldt ni que Niño 1+2 no condicione el clima de Lambayeque. La dirección de la costa, Ekman/surgencia, resolución espacial, SST costera real, rezago variable, patrones de lluvia y covariabilidad remota quedan fuera de este contraste.

Cifras verificadas con [modelo descriptivo](modelos/relaciones_oceano_viento_8u.py), [pruebas](tests/test_relaciones_oceano_viento_8u.py), [resumen de 216 meses-punto y SHA de fuentes](datos/relaciones_fisicas_8u/estado_relaciones_8u.json) y [comparaciones tabulares](datos/relaciones_fisicas_8u/correlaciones_fisicas_8u.csv). **Modelos de pronóstico evaluados en esta subfase: cero.**

## 5. ¿Cómo debería estudiarse su efecto predictivo?

La estrategia futura es jerárquica y previa a la validación:

- **Respuesta agrícola en tierra:** probar por separado anomalía de temperatura máxima y mínima, precipitación, persistencia de sequía/lluvias y humedad relevante para arándano y vid. No deducir enfermedades de variables climáticas sin evidencia fitosanitaria de campo.
- **Predictores causales candidatos:** anomalías SST Niño1+2/Niño3.4 con versiones temporales precisas, TSM oceánica costera, velocidad y **componentes vectoriales** del viento costero, e intensidad/dirección de corrientes marinas u/v cuando se obtengan completas y comparables. La respuesta regional puede depender de viento paralelo a costa, surgencia, estratificación y teleconexiones, pero las relaciones necesitan contrastes independientes.
- **Control anti-filtración temporal:** separar entrenamiento y selección de ventanas test (como 8S/8T), usar solamente observaciones que habrían estado publicadas antes del pronóstico, no corregir a posteriori fechas faltantes, y comparar frente a climatología y persistencia.
- **Control espacial:** evitar píxeles repetidos de reanálisis y verificar cuencas, pisos, exposición de laderas, límites oficiales IGN/INEI y datos instrumentales SENAMHI/IMARPE.
- **Alertas oficiales:** priorizar ENFEN e instituciones responsables para comunicados sobre Niño Costero, sin etiquetar al OAF como emisor oficial.

La inclusión de estas variables en la base **no equivale a haber demostrado que mejoren predicciones**. El contraste incremental Niño1+2 t−2 de fase 8T tuvo habilidad adicional casi nula; las nuevas hipótesis todavía requieren ensayos fuera de muestra específicos sobre lluvias, extremos y eventos.

## 6. Estado científico actual

| Componente | Evidencia real | ¿Historia completa 1996–2025? | ¿Validación instrumental independiente? |
|---|---|---|---|
| Viento a 10 m (ERA5) | Seis referencias, 2.160 meses | Sí, solo reanálisis | No |
| SST regional Niño1+2/3.4 | NOAA CPC, 360 meses | Sí, índice amplio | No |
| SST más cercana a Lambayeque | OISST por dos celdas oceánicas | Incompleta y con días ausentes | No |
| Corriente modelada de corto horizonte | 72 horas, 3 puntos | No | No |
| Corriente geostrófica NOAA/AOML | 2 puntos × 108 meses de 2017–2025, 6.574 días-punto | No; falta 1996–2016 | No |
| OSCAR v2/Copernicus Marine | Productos identificados, archivos locales pendientes | Pendiente | No |

**Habilidad prospectiva de predecir Niño Costero oficialmente: no demostrada. Polígonos agroclimáticos homogéneos certificados: 0. Riesgos fitosanitarios de arándano/vid validados: 0.**

Las salidas iniciales de las fuentes pueden cambiar si se agregan descargas posteriores. Los archivos JSON de estado son la **fuente de verdad dinámica** del observatorio.

## 7. Próxima fase 8V

Consolidar una climatología oceánica costera 1996–2025 a partir de un producto NASA/Copernicus con acceso verificado y máscara oceánica; corregir cobertura parcial OISST sin interpolar días; enlazar vectores u/v históricos y viento con temperatura y lluvia regional. Implementar un **backtest de precipitación intensa, temperatura máxima y riesgos de extremos**, comparando (a) persistencia, (b) anomalías atmosféricas previas, (c) índices SST y (d) vientos/corrientes disponibles en el momento, con fechas y ventanas congeladas. Exigir evaluación de estabilidad por altitud/cuenca y datos instrumentales reales antes de alertas productivas.
