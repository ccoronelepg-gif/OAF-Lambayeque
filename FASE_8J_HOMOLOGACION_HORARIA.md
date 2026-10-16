# Parte 8J — Homologación horaria, representatividad espacial e incertidumbre descriptiva

**Fecha:** 16/10/2026.  
**Proyecto:** Observatorio Agroclimático y Fitosanitario OAF-Lambayeque.  
**Responsable:** Ing. Agrónomo Carlos Enrique Coronel García.  
**Estado:** código operativo de control y auditoría publicado; **sin series horarias instrumentales SENAMHI autorizadas incorporadas**.

## 1. Resultado observado, no simulado

En la primera ejecución del motor `modelos/homologar_temperatura_horaria_8j.py` se comprobó:

| Indicador | Resultado real |
|---|---:|
| Archivos horarios instrumentales autorizados y efectivamente incorporados | **0** |
| Estaciones con temperatura horaria comprobable | **0** |
| Meses con 24 horas diarias válidas y calendario mensual completo | **0** |
| Comparaciones descriptivas instrumento–ERA5-Land | **0** |
| MAE, RMSE y sesgo estación–reanálisis | **No evaluables** |
| Intervalos predictivos calibrados del OAF | **No disponibles** |
| Habilidad prospectiva del modelo 8E | **No demostrada** |

Los datos históricos SENAMHI guardados con anterioridad son de **precipitación**; no se han reclasificado como temperatura. Los resultados sintéticos de las 15 pruebas son exclusivamente instrumentos de comprobación del software y **no** se publican como ciencia observacional.

## 2. Evidencia y fuentes institucionales

- [SENAMHI, datos de estaciones](https://www.gob.pe/institucion/senamhi/pages/9313-conocer-los-datos-hidrometeorologicos-del-peru): estaciones automáticas con reportes horarios y estaciones convencionales con frecuencias propias. La presencia de reportes horarios no demuestra disponibilidad pública de un registro histórico horario continuo por estación.
- [SENAMHI, descarga de datos meteorológicos](https://www.gob.pe/es/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos): acceso a datos diarios históricos sujeto a registro. El portal OAF no asume que esos archivos sean horarios ni que estén automáticamente licenciados para redistribución.
- [OMM, Guide to Instruments and Methods of Observation (WMO-No. 8)](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/instruments-and-methods-of-observation-programme-imop/guide-instruments-and-methods-of-observation-wmo-no-8): condiciones de emplazamiento, exposición y métodos de observación.
- [OMM, Siting Classification](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/instruments-and-methods-of-observation-programme-imop/siting-classification): el emplazamiento afecta la representatividad instrumental.
- [Copernicus / ECMWF, ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land): temperatura horaria del aire a 2 m calculada en grilla de reanálisis, **no** medida directa de los sensores SENAMHI.
- Muñoz-Sabater et al. (2021), *ERA5-Land: a state-of-the-art global reanalysis dataset for land applications*, Earth System Science Data 13, 4349–4383, DOI [10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021).

## 3. Definición de homologación horaria

La plantilla `datos/temperatura_horaria_8j/PLANTILLA_HORAS.csv` exige cuatro campos: `codigo_estacion`, `instante_utc`, `temperatura_2m_c` y `calidad`. El manifiesto `datos/temperatura_horaria_8j/manifest.csv` exige la identificación documental del instrumento, geografía, altitud, procedencia, fecha de publicación y SHA-256 del archivo.

Las marcas UTC deben incluir **zona UTC explícita** y minuto/segundo 00. El motor las transforma a `America/Lima` para agrupar por día civil peruano. Ejemplo ilustrativo de alineación temporal: **05:00 UTC = 00:00 en Perú**, sin transformar los valores de temperatura. Esta conversión permite evitar que las últimas cinco horas UTC de un día se atribuyan al día equivocado para un registro peruano.

**Reglas de control:**

1. La fecha observacional debe preceder a la fecha de publicación documental. Duplicados horarios, zona horaria ausente/incorrecta o muestreo desplazado se rechazan.
2. Se aceptan para el cálculo solo muestras con QA `aprobado`, temperatura finita y límites físicos de plausibilidad, sin sustituir ausencias, ceros ni banderas por temperaturas inventadas.
3. Un día exige **24 instantes horarios en el calendario local** con QA aprobado y temperatura presente; un mes requiere **todos los días completos**. Si falta una hora, no se publica la media del mes como completa.
4. El promedio mensual es el promedio de las 24 temperaturas horarias por día completo a lo largo de todo el mes, sin interpolación ni reemplazos.
5. La estación y la cuadrícula pueden representar exposiciones diferentes. El sistema aplica una criba **administrativa provisional** de distancia ≤20 km desde el punto OAF y diferencia absoluta de altitud estación–grilla ≤200 m, exigiendo metadatos documentados. **Son límites de revisión de calidad, no garantías científicas de equivalencia**.
6. Ni la altura de la celda ni la del instrumento se suponen por proximidad; deben figurar como números trazables junto con una URL fuente. Se desactiva cualquier supuesta corrección automática por gradiente térmico vertical sin datos empíricos y método explícito.
7. La grilla OAF referencial usada en el modelo no es necesariamente el centro de píxel real; confirmar las coordenadas/celdas del producto para una validación exhaustiva posterior.
8. Los reportes se clasifican expresamente como **comparaciones descriptivas preliminares**, incluso cuando hay pares, y no afirman independencia, verificación operativa o habilidad del modelo de pronóstico térmico 8E.

## 4. Archivos construidos

- `modelos/homologar_temperatura_horaria_8j.py`: motor y reglas documentales/horarias/espaciales.
- `tests/test_homologar_temperatura_horaria_8j.py`: **15 pruebas aisladas**, incluyendo un mes sintético con 744 horas, un día con una hora faltante, fecha/UTC incorrectos, duplicados, QA rechazado, altura/cobertura y SHA inválidos.
- `datos/temperatura_horaria_8j/manifest.csv` y `PLANTILLA_HORAS.csv`: estructuras vacías para recibir datos auténticos si la licencia lo permite.
- `datos/temperatura_horaria_8j/README.md`: requisitos de procedencia, privacidad/redistribución y formato.
- `datos/homologacion_horaria_8j/estado_8j.json`: estado y métricas nulas cuando no hay observaciones.
- `datos/homologacion_horaria_8j/comparaciones_horarias_8j.csv`: CSV descriptivo de meses (en la primera publicación, solo encabezados).
- `modelos/visor_homologacion_horaria_8j.js`: componente público en **Verificación de datos**, evita graficar falsos errores.
- `.github/workflows/oaf_homologacion_horaria_8j.yml`: ejecución de pruebas y actualización de reportes los días 22 del mes, tras fases 8H/8I.

## 5. Incertidumbre y etapas futuras

Esta fase **no calibra intervalos 90 %**: no hay observaciones instrumentales horarias utilizables ni suficientes errores prospectivos históricos para caracterizar estabilidad temporal. Tampoco modifica los modelos 8E/8G ni los límites de entrenamiento originales.

**Parte 8K propuesta:** preparar un inventario y algoritmo de selección de estaciones termométricas SENAMHI por metadatos corroborados, y un procedimiento de comparabilidad **celda ERA5-Land real–instrumento** con altitud efectiva, período, método diario/horario y análisis de sesgos estacionales. El paso a verificación prospectiva y riesgo fitosanitario operativo requiere primero observaciones reales, fenología y evaluaciones sanitarias del arándano y la vid.

Se mantiene la climatología pública del OAF de **1996–2025**, la normal OMM **1991–2020** cuando corresponda y la separación científica entre pronósticos térmicos, anomalías oceánicas y enfermedad agrícola.
