# Fase 10K — Optimización geográfica Random Forest y dashboard de paisajes ecoclimáticos

**OAF-Lambayeque · Ejecución verificable 17 de octubre de 2026**

## 1. Objetivo y alcance del concepto «ecorregión»

Se conservan **39 sectores con series históricas CHIRPS 1996–2025**. La capa experimental 9K contiene 42 polígonos; **S028, S032 y S034 no tienen celdas CHIRPS suficientes** y quedan excluidos del cálculo de aptitud predictiva, nunca imputados.

Se establecen **cinco paisajes ecoclimáticos operativos**, determinados por un mapeo explícito de los siete pisos 9K:

| Paisaje OAF (NO ecorregión oficial) | Pisos asignados | Sectores con CHIRPS | Elevaciones preliminares |
|---|---|---:|---|
| Costa árida y valles bajos | Cota negativa (revisar), llanura costera, valle bajo | 11 | aprox. −2 a 293 m |
| Piedemonte y transición de bosque seco | Piedemonte | 11 | 304 a 785 m |
| Vertientes andinas bajas | Montaña baja | 6 | 801 a 1594 m |
| Vertientes andinas medias | Montaña media | 8 | 1665 a 2447 m |
| Alturas y cumbres andinas | Montaña alta | 3 | 2501 a 3839 m |

**Importante:** «transición de bosque seco», «costa árida» y «vertiente andina» son interpretaciones descriptivas generales. **No se han intersectado con polígonos oficiales del MINAM**, por lo que no deben exhibirse como límites homologados de las ecorregiones «bosque seco ecuatorial», «desierto del Pacífico» o «serranía esteparia». La futura homologación debe realizarse mediante intersección geométrica y superposición de fuentes autorizadas.

**Fuentes institucionales de referencia:** [Mapa Nacional de Ecosistemas del Perú, MINAM](https://www.gob.pe/institucion/minam/informes-publicaciones/277146-mapa-nacional-de-ecosistemas-del-peru), aprobado mediante [R. M. 440-2018-MINAM](https://www.gob.pe/institucion/minam/normas-legales/235404-440-2018-minam), y el [SINIA](https://sinia.minam.gob.pe/mapas/mapa-nacional-ecosistemas-peru).

## 2. Nuevo entrenamiento y control de fuga

Se usó **exclusivamente Random Forest**. Dos brazos de entrada:

- **RF-eco lluvia:** precipitación histórica CHIRPS con rezagos desde t−2, temporada, relieve, atributos espaciales y categoría eco-climática codificada como cinco variables one-hot.
- **RF-eco multivariable:** mismas entradas más SST Niño1+2/Niño3.4, SOI, alisios, viento marino, temperatura, humedad, radiación, presión, viento NASA POWER y derivados de punto de rocío; todas las entradas temporales con lag ≥2 meses.

Para cada brazo se reentrenaron RF de **lluvia mensual mm**, **P90 relativo al sector** y **P95 relativo al sector**. Los umbrales de lluvia y la climatología se calculan con 1997–2015. Los pesos de combinación RF/climatología (0, 0.2, …, 1.0) y las hojas de los árboles se seleccionan solo con **2016–2018 sobre sectores de entrenamiento**, sin elegir el mejor resultado mirando 2021–2025. Las bandas exploratorias al 90 % usan **2019–2020 en sectores reservados**; la prueba principal es **2021–2025**, con cinco bloques geográficos CHIRPS. Como algunos sectores comparten celdas atmosféricas NASA, no se puede atribuir independencia total a los grupos.

**Ejecución de GitHub Actions:** [fase 10K, entrenamiento y ocho pruebas exitosas](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39094686704). Se publicaron **4.680 predicciones retrospectivas** (2.340 casos sector-mes × dos brazos) y **2.340 registros para el dashboard** de la familia seleccionada exclusivamente en validación.

## 3. Resultados globales 2021–2025

| Medida | RF con paisaje (selección validación) | Climatología |
|---|---:|---:|
| Precipitación media observada | 25,060 mm/mes | — |
| Precipitación media estimada | 29,909 mm/mes | 25,001 mm/mes |
| **MAE lluvia (menor mejor)** | 20,4298 mm | **14,2957 mm** |
| **Brier ≥P90 (menor mejor)** | **0,061688** | 0,062884 |
| **Brier ≥P95 (menor mejor)** | **0,046705** | 0,046996 |
| Sesgo medio RF | +4,8484 mm/mes | — |
| Cobertura empírica de banda «90 %» | 87,26 % | — |

El **MAE RF mejoró respecto a fase 10J (21,0716 → 20,4298 mm)**, pero sigue por detrás de la climatología (14,2957 mm). Las mejoras de Brier en P90 y P95 son pequeñas: **NO se ha probado una superioridad robusta**, y no se autoriza un pronóstico meteorológico operativo.

### ¿Qué aportaron las variables multivariables?

La variante RF con lluvia, geografía, océano y atmósfera produjo **MAE 14,2957 mm**, igual a climatología porque **el peso de RF en la salida mm fue seleccionado como cero en los cinco pliegues**. Esto significa **«el modelo no aportó corrección»**, NO una precisión de Random Forest demostrada por todas las covariables. Su Brier P90 fue 0,061766 y P95 0,046996, sin alcanzar una ventaja general robusta.

Los cinco pliegues seleccionaron el brazo **lluvia+paisaje** para los tres objetivos, basándose solo en validación 2016–2018. Los datos oceanoatmosféricos se conservaron para ablación y posibles revisiones futuras, no para forzar un brazo complejo con peor ajuste.

## 4. Cuadro comparativo de los cinco paisajes

Valores promediados por sector-mes, **sin ponderación por km²**. MAE en milímetros.

| Paisaje | Sectores | Lluvia observada mm/mes | Estimación RF mm/mes | MAE RF ↓ | MAE clima ↓ | Brier RF P90 ↓ |
|---|---:|---:|---:|---:|---:|---:|
| Costa árida y valles bajos | 11 | 9,049 | 8,080 | 8,5595 | **7,6288** | 0,079265 |
| Piedemonte / bosque seco (proxy) | 11 | 17,615 | 19,552 | 16,7707 | **12,5809** | 0,055513 |
| Vertientes andinas bajas | 6 | 20,435 | 20,957 | 15,7766 | **12,1502** | 0,053498 |
| Vertientes andinas medias | 8 | 45,427 | 56,361 | 33,3271 | **21,8805** | 0,055068 |
| Alturas y cumbres andinas | 3 | 66,008 | 95,285 | 52,2841 | **29,0930** | 0,053914 |

**Hallazgo:** error absoluto RF escala notablemente con la climatología húmeda en altura, pero **el MAE comparado no debe analizarse sin considerar las diferentes medias de precipitación ni que las áreas tienen pocos sectores y comparten muestras**. En alta montaña RF **sobreestima 29,3 mm/mes de media**, un problema prioritario. La cota negativa en S001 continúa en revisión.

### Análisis de 2023

En el año con episodios intensos, la lluvia observada global promedió **42,946 mm/mes**, RF estimó **29,993 mm/mes** y climatología **25,001 mm/mes**. MAE RF **28,8097 mm** frente a climatología **24,8143 mm**; **107 de los 468 sector-mes superaron P90**, y **75 superaron P95**. El Brier RF P90 2023 fue **0,122137** frente a climatología **0,136595**, mejora probabilística descriptiva, con sesgo RF de **−12,9536 mm**: en el año de lluvia anómala **subestima sistemáticamente en promedio**.

**Por paisaje en 2023:**

| Paisaje | Media observada mm | Media RF mm | MAE RF mm | MAE clima mm | Meses-sector ≥P90 |
|---|---:|---:|---:|---:|---:|
| Costa árida y valles | 22,012 | 9,007 | 16,6573 | 15,6321 | 39 |
| Piedemonte / transición | 37,740 | 19,327 | 26,8196 | 24,1733 | 30 |
| Vertientes bajas | 36,411 | 22,916 | 26,2604 | 20,8612 | 15 |
| Vertientes medias | 67,309 | 55,065 | 40,5985 | 34,5131 | 17 |
| Cumbres altas | 86,899 | 93,342 | 54,3273 | 42,8756 | 6 |

La **cobertura de la banda exploratoria 90 % cae a 81,2 % en 2023** (media 2021–2025: 87,26 %). No mostrar la banda como un intervalo garantizado de riesgo ni confundir «eventos P90 mensuales» con eventos extremos horarios, inundaciones o un aviso El Niño de ENFEN.

## 5. Dashboard público creado

[ecorregiones-clima-10k.html](ecorregiones-clima-10k.html) incluye:

1. **Mapa Leaflet georreferenciado** con 39 polígonos experimentales GeoJSON; interacción por clic, encuadre del paisaje y leyenda.
2. **Filtros de paisaje** (cinco), **periodo** (2021–2025 o cada año), **métrica cartográfica** (paisaje, lluvia observada, lluvia estimada RF, error MAE, eventos P90) y **sector**.
3. **Cuadro resumen territorial** actualizado según filtro: sectores, lluvia media observada, lluvia RF, MAE RF/climatología, Brier P90, número de eventos altos.
4. **Cuadro secundario de siete pisos** con error de predicción, lluvia y diferencias ecológicas.
5. **Serie mensual de lluvia CHIRPS, RF y climatología** por sector/año, con medias multianuales cuando se elige 2021–2025.
6. **Avisos permanentes de procedencia** que distinguen los paisajes exploratorios de ecorregiones oficiales MINAM y prohíben tratar el dashboard retrospectivo como pronóstico vigente.

El portal recupera sus datos directamente de los archivos publicados: [evaluación territorial](datos/ecopaisajes_10k/evaluacion_ecoclimatica_10k.json), [polígonos](datos/ecopaisajes_10k/paisajes_ecoclimaticos_10k.geojson), [series sector/mes](datos/ecopaisajes_10k/series_sector_mes_10k.json).

## 6. Próximas mejoras en la trayectoria científica

- Homologar cada polígono con el **Mapa Nacional de Ecosistemas del MINAM** mediante capas vectoriales oficiales y documentar porcentajes de intersección espacial; hasta entonces no llamar a los grupos «ecorregiones oficialmente delimitadas».
- Identificar y corregir sesgos de alta montaña, estudiar la estacionalidad lluvia-diciembre a abril y evaluar lluvia diaria intensa cuando se consiga una serie diaria georreferenciada con calidad suficiente.
- Mejorar el modelo usando **nuevos datos 2026+ genuinamente disponibles as-issued**, estabilidad por años y celdas NASA, y estaciones SENAMHI independientes antes de publicar pronósticos operativos.
- Mantener **Random Forest solo para precipitación**. Las enfermedades agrícolas quedarán exclusivamente para un algoritmo posterior con datos de incidencia y condiciones horarias de campo verificadas.

**Estado final 10K:** investigación geográfica y entrenamiento reproducibles, **SIN alertas operativas**.
