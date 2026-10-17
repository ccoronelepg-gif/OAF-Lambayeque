# Fase 8N — Prezonificación altitudinal y diseño de zonas agroclimáticas homogéneas

**OAF-Lambayeque · 16/10/2026 · planificación técnica para predicción regional.**

## Objetivo

Ampliar el proyecto más allá de las cuatro localidades piloto Chiclayo, Jayanca, Motupe y Olmos. Lambayeque incluye planicies litorales, valles agrícolas, piedemontes, laderas y cabeceras andinas. Es **científicamente incorrecto extrapolar una temperatura y un modelo único** a todos esos ambientes. La homogeneidad requiere semejanza conjunta de temperatura, amplitud térmica, precipitación/estacionalidad, humedad, radiación, evapotranspiración, exposición y relieve; la elevación **sola** no garantiza similitud climática.

La etapa 8N crea primero una **malla de muestreo altitudinal y geográfico verificable**. Los estratos de esta fase son **candidatos de diseño**, no zonas homogéneas ya demostradas, ni validación de pronósticos, ni riesgo fitosanitario operativo.

## 1. Cartografía territorial: advertencia sobre límites

La malla se recorta con un límite **histórico y simplificado** de Lambayeque (código UBIGEO 14), extraído de una colección pública secundaria: [juaneladio/peru-geojson — cartografía departamental](https://github.com/juaneladio/peru-geojson/blob/master/peru_departamental_simple.geojson). Solo se incorporó el polígono de Lambayeque, guardando la procedencia y el SHA del archivo fuente. Es **una delimitación referencial para planificar el muestreo**, NO una certificación de límites administrativos vigentes, predios, distritos o una capa de área real verificable.

Para elevar el rigor debe obtenerse y contrastarse el límite departamental más reciente de la [Infraestructura de Datos Espaciales del INEI](https://ide.inei.gob.pe/) o del [Instituto Geográfico Nacional](https://portalgeo.idep.gob.pe/). El INEI publica cartografía departamental actualizada al 2023; el archivo público secundario no sustituye dicha fuente.

## 2. Datos del terreno realmente adquiridos

Se generó una cuadrícula determinista con centros separados **0,125°** de latitud/longitud, filtrados por pertenencia a la superficie regional. Produjo **69 nodos** de referencia (no polígonos, ni totalidad de las hectáreas). Se solicitó la elevación para cada uno con la [Open-Meteo Elevation API](https://open-meteo.com/en/docs/elevation-api), que proporciona elevación estimada de un DEM. Dos lotes se archivaron junto con URL, hora UTC, datos JSON originales comprimidos y SHA-256. **El DEM no es medición de temperatura ni cota topográfica oficial de parcela**.

Al primer corte se obtuvieron **69/69 elevaciones válidas**, con valores desde **−2 hasta 3.236 m**. Dos valores negativos del DEM se conservaron y marcaron para revisión, en lugar de sustituirlos por cero. En entornos próximos a la costa pequeñas elevaciones negativas de un DEM no implican error por sí solas; exigen comprobar datum, topografía y resolución.

### Estratos altitudinales de muestreo, no zonas homogéneas confirmadas

| Estrato provisional | Regla de altitud del DEM | Puntos de la muestra |
|---|---|---:|
| Planicie muy baja | 0–99 m | 35 |
| Planicie y valle bajo | 100–299 m | 18 |
| Piedemonte | 300–799 m | 6 |
| Ladera baja | 800–1.599 m | 3 |
| Ladera media | 1.600–2.499 m | 4 |
| Zona alta andina | ≥ 2.500 m | 1 |
| Cotas DEM negativas, revisión | -2 a -1 m | 2 |

**Los umbrales son decisiones prácticas preliminares de muestreo, NO pisos ecológicos legalmente establecidos ni categorías de la OMM/INEI.** Tampoco representan el porcentaje territorial de cada zona: las celdas muestreadas son puntos, el borde regional es simplificado, el terreno varía dentro de la celda y las montañas están insuficientemente representadas.

## 3. Cómo construiremos las zonas verdaderamente homogéneas

Se aplicará la siguiente metodología antes de emitir una predicción por zona:

**Paso A — Consolidación SIG:** límite IGN/INEI verificable, DEM de resolución apropiada y ubicación de estaciones de SENAMHI con metadatos confirmados; aumentar la densidad de muestreo en laderas y cabeceras, priorizando la topografía abrupta y el bosque seco. Distinguir distancia real al mar, orientación de ladera, cuenca, pendiente, coordenada de celda del proveedor y altitud DEM de estación.

**Paso B — Variables meteorológicas comparables:** para cada nodo espacial, adquirir series históricas **1996–2025** de T2m media, Tmax, Tmin, precipitación, humedad relativa, radiación global y variables derivadas como ET0/VPD cuando sus definiciones sean comparables; conservar metadatos del reanálisis, unidades, método de agregación, resolución, cobertura y diferencias entre fuentes. La normal OMM **1991–2020** permanecerá como control científico de comparabilidad cuando exista.

**Paso C — Agrupación por homogeneidad:** comparar los perfiles estacionales y anomalías, amplitud térmica, humedad, concentración de precipitación, radiación y altitud con variables estandarizadas y pesos justificados. Construir clústeres climáticos contiguos o polígonos de subregión, evitando dividir una misma celda reanalizada artificialmente en múltiples observaciones independientes. El número de clústeres debe seleccionarse con estabilidad ante cambios de muestreo, sensibilidad a variables y validación espacial por bloques, no con un número arbitrario de pisos.

**Paso D — Detección de transiciones:** comprobar áreas de gradiente térmico/altitudinal abrupto, efectos de costa, corredor de valle y cabeceras de cuenca. Conservar explícita la incertidumbre y las celdas de transición. Requerir un mínimo de estaciones instrumentales independientes y varios nodos por estrato; una región alta representada por un solo nodo **no puede declararse homogénea**.

**Paso E — Predicción por zona:** una vez evaluada la zonificación histórica, preparar predicciones de anomalías por agrupación agroclimática, comparando modelo local, persistencia, climatología y predicción regional. La validación exige ventanas temporales posteriores al entrenamiento, partición geográfica por bloques, datos observados independientes y congelación de emisiones previas a los eventos. Los resultados experimentales solo se publicarán como tales. No activar alertas agrícolas hasta que la verificación de campo y calidad instrumental permita respaldarlas.

**Paso F — Fitopatología y Niño Costero:** para arándano y vid, combinar las anomalías por zona con fenología, microclima y observaciones de campo de plagas/enfermedades. Para Niño Costero, priorizar comunicación institucional ENFEN y fuentes oceánicas; no equiparar anomalía térmica local con una clasificación oficial ENFEN ni inferir brote sin evaluación.

## 4. Archivos y procesos realmente implementados

- [Polígono regional referencial](datos/zonificacion_8n/limite_lambayeque_referencial.geojson).
- [Programa Python para crear malla y comprobar DEM](modelos/zonificacion_preliminar_8n.py).
- [Pruebas de calidad](tests/test_zonificacion_8n.py), con DEM sintético en directorios temporales exclusivamente (no publicado como dato).
- [Workflow regional](.github/workflows/oaf_zonificacion_8n.yml), que consulta elevaciones faltantes, verifica SHA, recalcula tablas deterministas y publica el estado.
- [Estado del proyecto, limitaciones y distribución altitudinal](datos/zonificacion_8n/estado_8n.json).
- [Coordenadas y altitud de la muestra](datos/zonificacion_8n/nodos_altitudinales_8n.csv).
- [Malla geográfica (sin valores imputados)](datos/zonificacion_8n/malla_geografica_8n.csv).
- [Panel de zonificación](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones), con mapa de nodos, filtros por piso y explicación de límites.

## 5. Estado científico y próxima etapa

**Cumplido en 8N:** primer atlas regional altitudinal reproducible: **69 nodos, 69 elevaciones DEM descargadas, siete estados físicos incluyendo el DEM negativo; 0 zonas climáticas confirmadas, 0 pronósticos zonales certificados.** No se modificó ninguna predicción original 8E ni la evaluación prospectiva 8G.

**Parte 8O propuesta:** densificar malla andina y completar la extracción climática regional 1996–2025 para cada nodo representativo; construir indicadores de similitud multivariable, contrastar zonas estacionales y definir la primera agrupación de **ambientes climáticos relativamente homogéneos** con incertidumbre explícita. Integrar el análisis de elevación con `elevation=nan` frente al ajuste predeterminado en un ensayo separado para no atribuir causalidad sin control.

## Referencias científicas

- Open-Meteo: [Elevation API](https://open-meteo.com/en/docs/elevation-api), [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), modelo digital 90 m y downscaling que puede desactivarse con `elevation=nan`.
- Copernicus/ECMWF: [ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- Muñoz-Sabater et al. (2021), [ERA5-Land: a state-of-the-art global reanalysis dataset for land applications](https://doi.org/10.5194/essd-13-4349-2021).
- [INEI — Infraestructura de Datos Espaciales](https://ide.inei.gob.pe/), capa de límites departamentales.
- [IGN — IDEP](https://portalgeo.idep.gob.pe/), límites departamentales y cartografía.
