# Parte 8L — Sensibilidad histórica a la selección de celda ERA5-Land

**Observatorio Agroclimático y Fitosanitario OAF-Lambayeque · 16/10/2026**  
**Alcance:** Chiclayo, Jayanca, Motupe y Olmos. Climatología reciente fija: **1996–2025**.  
**Estado:** comparación histórica completada con fuentes de reanálisis verificadas. **No constituye validación instrumental ni habilidad predictiva prospectiva.**

## 1. Pregunta e interpretación científica

Se estudia si el parámetro **`cell_selection=land` frente a `cell_selection=nearest`** de la API histórica Open-Meteo produce distintas temperaturas de ERA5-Land en los cuatro puntos OAF.

Open-Meteo explica que `land` prefiere celdas terrestres adecuadas considerando similitud de elevación (modelo digital de elevación 90 m), mientras `nearest` prefiere la celda geográficamente más cercana. La API puede ofrecer correcciones estadísticas de elevación y el campo `elevation` no identifica automáticamente la orografía de la cuadrícula oficial. Las coordenadas devueltas por la API pueden distar algunos kilómetros de las solicitadas.

**Fuente científica:** [Open-Meteo, Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).  
**Reanálisis original:** [ECMWF/Copernicus, ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land): aproximación de ~9 km de resolución nativa (CDS ofrece cuadrícula regular de 0,1°); no es observación directa de una estación SENAMHI.

## 2. Procedimiento reproducible

La aplicación [`modelos/sensibilidad_celdas_8l.py`](modelos/sensibilidad_celdas_8l.py) consultó la API Historical Weather con los mismos cuatro pares de coordenadas referenciales de 8D, variable diaria `temperature_2m_mean` de `models=era5_land`, `timezone=America/Lima`, y dos criterios: `cell_selection=land` y `cell_selection=nearest`.

Periodo original: **01/01/1996 al 31/12/2025**, dividido en tres periodos de diez años: 1996–2005, 2006–2015 y 2016–2025. Dos métodos × tres bloques = **seis respuestas con cuatro localidades cada una**.

Cada respuesta JSON cruda fue archivada comprimida con `gzip` en `datos/fuentes_celdas_8l/`, junto a fecha de consulta, URL exacta y SHA-256 del JSON descomprimido, controles de días presentes y calidad de los valores. **No se interpolaron días ausentes ni se incorporó temperatura instrumental ficticia**.

Para cada localidad y mes:
- Temperatura mensual por método = promedio aritmético de las temperaturas medias diarias recibidas en el mes.
- Diferencia absoluta con signo: `D = T(nearest) − T(land)`.
- Normal estacional por método: promedio de cada mes del calendario en los **30 años 1996–2025** (ejemplo, todos los eneros).
- Anomalía mensual por método: temperatura mensual menos normal estacional de ese método.
- Sensibilidad de anomalía = `A(nearest) − A(land)`.
- Se calcula la media de `|D|`, la raíz del promedio de `D²`, la diferencia máxima `|D|` y los meses con `|D| ≥ 0,5 °C` o `≥ 1,0 °C` como **indicadores descriptivos, no umbrales sanitarios ni de alerta**.

No se ha usado la serie climática 1996–2025 para entrenar nuevos modelos, ni se ha recalibrado 8E o 8G. El estudio 8D mantiene congeladas sus emisiones y datos originales.

## 3. Resultado observado

El contraste de los **1.440 pares mensuales** (4 localidades × 360 meses) produjo el resultado siguiente.

| Localidad | Pares mensuales | ¿La celda seleccionada fue distinta? | Media absoluta de diferencia | Máxima diferencia absoluta | Sensibilidad de anomalías |
|---|---:|---|---:|---:|---:|
| Chiclayo | 360 | No | 0,00000 °C | 0,00000 °C | 0,00000 °C |
| Jayanca | 360 | No | 0,00000 °C | 0,00000 °C | 0,00000 °C |
| Motupe | 360 | No | 0,00000 °C | 0,00000 °C | 0,00000 °C |
| Olmos | 360 | No | 0,00000 °C | 0,00000 °C | 0,00000 °C |

**Conclusión delimitada:** en estas cuatro coordenadas, el proveedor eligió el **mismo centro de celda** para `land` y `nearest` en los seis bloques consultados. Los valores de temperatura coincidieron hasta la precisión archivada y no se modificó ninguna anomalía por cambiar entre ambos selectores.

**Esto NO demuestra robustez frente a desplazamientos de posición, cambio de resolución, ajuste de elevación, clima litoral o heterogeneidad topográfica.** Ambos métodos pueden coincidir en un punto y diferir a pocos kilómetros. Tampoco demuestra exactitud frente a termómetros de estación ni validez de avisos OAF a productores.

Como auditoría independiente de consistencia documental, la Tmedia mensual de `land` recuperada en 8L también reprodujo, hasta la precisión archivada, los **360 meses de cada localidad del archivo histórico 8D** (MAE de diferencia 0,00000 °C). Esto refuerza la reproducibilidad de los valores con los parámetros actuales del proveedor, **pero no constituye recuperación certificada de la respuesta geográfica original de 8D**: no se archivó originalmente la coordenada de celda de las respuestas de 8D, y el proveedor puede revisar fuentes.

## 4. Productos de la fase

- [Motor Python para descargar/verificar y calcular](modelos/sensibilidad_celdas_8l.py).
- [Pruebas sintéticas aisladas](tests/test_sensibilidad_celdas_8l.py), incluido examen de 1.440 pares mensuales sin mezcla con observaciones.
- [Fuentes crudas comprimidas y metadatos](datos/fuentes_celdas_8l/): seis bloques históricos separados y archivos `.meta.json`.
- [Estado resumen](datos/sensibilidad_celdas_8l/estado_8l.json): cuatro localidades, indicadores, restricciones y huellas.
- [Datos por localidad/mes](datos/sensibilidad_celdas_8l/pares_mensuales_8l.csv): Tmedia por método, diferencias, anomalías con 30 años de base y columna de contraste documental 8D.
- [Visor web 8L](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones), módulo dentro de **Verificación de datos** con selección de localidad, indicadores y gráfico de diferencias anuales observadas en reanálisis.
- [Automatización](.github/workflows/oaf_sensibilidad_celdas_8l.yml): verificaciones offline, descarga de archivos faltantes solo con cobertura íntegra, comparación determinista y publicación únicamente cuando cambian salidas.

## 5. Trabajo siguiente — 8M

La ausencia de variación en `land/nearest` **para un mismo punto** orienta el próximo experimento a cambiar sistemáticamente las **coordenadas de consulta** en torno a los cuatro puntos OAF y evaluar la sensibilidad espacial en un entorno de varios kilómetros, con método/celda/coordenadas/altitud registrados y comparabilidad climática documentada.

Este futuro experimento no debe sustituir la adquisición de series térmicas **SENAMHI** ni de evaluaciones fitosanitarias de **arándano y vid**. Los modelos predictivos de anomalías asociadas a El Niño Costero permanecen **experimentales**, con alertas oficiales únicamente atribuidas a ENFEN/SENAMHI.
