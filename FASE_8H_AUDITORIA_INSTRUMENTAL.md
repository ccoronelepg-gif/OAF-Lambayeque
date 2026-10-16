# Fase 8H — Auditoría instrumental, georreferenciación y preparación de la incertidumbre

**OAF-Lambayeque · Fecha: 16/10/2026**  
**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque.  
**Autor:** Ing. Agrónomo Carlos Enrique Coronel García.  
**Estado:** auditoría de preparación comprobada automáticamente; **sin validación térmica instrumental ni intervalos predictivos operativos**.

## 1. Conclusión científica

Las primeras emisiones 8E pronostican **temperatura media mensual del aire a 2 m** para cuatro cuadrículas referenciales: Chiclayo, Jayanca, Motupe y Olmos. Por su parte, el archivo instrumental histórico disponible `datos/senamhi_mensual_completo_1996_2015.csv` contiene **precipitación total mensual (mm)** para cinco estaciones y **no contiene Tmax, Tmin ni Tmedia de estación**.

**No se pueden estimar errores temperatura ERA5-Land – estación SENAMHI a partir de los pluviómetros.** No se deduce una temperatura a partir de precipitación, ni se atribuye a datos meteorológicos de reanálisis la condición de una medición instrumental independiente. La fase 8H reconoce exactamente **cero** estaciones habilitadas en el repositorio para esa validación térmica, y **cero** contrastes instrumentalmente verificados.

La fase 8G conserva 8 pronósticos emitidos antes del mes objetivo y 4 estimaciones intramensuales. En el primer corte consultado, **ningún mes objetivo se había verificado todavía** contra ERA5-Land. Los intervalos de predicción al 90 % permanecen **no calibrados, no disponibles y no evaluables**.

## 2. Inventario real instrumental 1996–2015

La auditoría automática sobre las fuentes originales produce:

| Estación | Meses completos de lluvia | Años completos | Último año temporalmente completo | Coordenada usada en estudios históricos → referencia alternativa |
|---|---:|---:|---:|---|
| Jayanca (La Viña) | 219 | 15 | 2012 | Separación de 1,68 km |
| Cayaltí | 235 | 17 | 2013 | Separación de 2,41 km |
| Reque | 233 | 15 | 2013 | Separación de 0,04 km |
| Lambayeque | 204 | 15 | 2013 | Separación de 3,36 km |
| Cueva Blanca | 218 | 17 | 2013 | Referencia actual -6,13130; -79,40450; otra coordenada antigua descartada |

**Total: 1.109 meses-estación completos de lluvia y 79 estaciones-año completos.** Último año común completo entre las cinco estaciones: **2012**.

Cueva Blanca figura en documentación reciente de SENAMHI aproximadamente a 3.300 m s. n. m., condición que refuerza la necesidad de estudiar gradientes orográficos en lugar de extrapolar mediciones a valles agrícolas. Esta altitud **no prueba** continuidad instrumental ni la altitud de una estación en 1998.

Una diferencia entre las coordenadas publicadas **no prueba un traslado**; podrían ser problemas de geocodificación, diferentes instrumentos, periodos o referencias. Ni siquiera una distancia pequeña permite inferir igualdad de las series.

### Fuentes específicas para la georreferenciación

- [SENAMHI, documento de red y estaciones meteorológicas](https://www.senamhi.gob.pe/load/file/01404SENA-1.pdf): referencias para Cayaltí, Reque y Jayanca.
- [SENAMHI, EMA La Viña](https://www.senamhi.gob.pe/load/file/00701SENA-313.pdf): la existencia de esta estación automática no demuestra equivalencia con la serie histórica denominada «Jayanca (La Viña)».
- [SENAMHI, boletín con Cueva Blanca](https://www.senamhi.gob.pe/load/file/03619SENA-31.pdf): altitud y referencia geográfica documental reciente; no certifica la ubicación histórica de 1996.
- [Auditoría de coordenadas de Fase 3P](METADATOS_GEOGRAFICOS_3P.md).

## 3. Qué comprueba exactamente el código

El módulo [`modelos/auditoria_instrumental_8h.py`](modelos/auditoria_instrumental_8h.py) realiza:

1. Lectura **sin sustituciones** del CSV SENAMHI y del inventario de coordenadas provisional.
2. Validación de campo `observado_mm`, unidades, valores finitos, días válidos, mes calendario y ausencia de duplicados.
3. Comparación cruzada con la auditoría documental de cobertura, incluyendo 1.109 meses y 79 estaciones-año, sin asumir continuidad reciente 2016–2025.
4. Distancia geográfica por Haversine de la coordenada consultada a cada una de las cuatro referencias OAF; la mínima es **orientativa, no crea ningún vínculo instrumental**.
5. Barreras explícitas para exigir identificador de estación, historial de emplazamiento e identidad con la serie antigua antes de declarar el punto apto para evaluación.
6. Detección inequívoca de que los datos disponibles contienen **lluvia, no temperatura**. Incluso al confirmar tres indicadores de metadatos, no puede pasar como estación térmica verificada.
7. Evaluación de la disponibilidad de los informes 8G sin fabricar nuevos contrastes.
8. Cálculo de SHA-256 de todos los archivos consultados para trazabilidad del resultado.
9. Emisión de dos archivos derivados, sin alterar datos o emisiones originales:
   - [`datos/auditoria_instrumental_8h/estado_8h.json`](datos/auditoria_instrumental_8h/estado_8h.json).
   - [`datos/auditoria_instrumental_8h/estaciones_8h.csv`](datos/auditoria_instrumental_8h/estaciones_8h.csv).

La calidad de la agregación mensual y la completitud de un archivo **no significan que SENAMHI haya certificado la serie para nuevos periodos**, ni que la estación se haya mantenido en el mismo lugar.

## 4. Preparación científica para incertidumbre de predicción

Por ahora se implementa **solo una función preparatoria** (`conformal_radius`) para estimar un radio de incertidumbre retrospectivo a partir de errores absolutos `|pronóstico − verificación|` de emisiones históricas.

La función establece las siguientes restricciones:

- Cada predicción de calibración debe haberse emitido **antes del inicio de su mes objetivo**.
- El resultado de referencia debe haber sido publicado **después de terminar el mes** y estar disponible **antes de la nueva emisión**.
- Se rechazan fechas sin zona horaria, meses objetivos duplicados y contrastes posteriores al origen que se desea pronosticar.
- Exige un mínimo programático preliminar de **36 errores válidos en meses distintos**, sin afirmar que 36 sea un tamaño científicamente suficiente para todas las regiones u horizontes.
- Se calcula el orden `k = ceil((n+1) × (1 − α))`, con `α = 0,10`; devuelve el error absoluto de orden `k`, si `k <= n`.
- Si la fuente es insuficiente o la comparación no está autorizada, retorna `null` o genera un error.

**Advertencia estadística imprescindible:** la justificación de cobertura finito-muestral de un intervalo conformal estándar supone condiciones de intercambiabilidad que **pueden no cumplirse** en series mensuales climáticas autocorrelacionadas, con cambio de régimen ENSO, dependencia entre estaciones y cambios de fuente. Un cuantíl de errores NO se publicará automáticamente como intervalo 90 % válido. Se requieren experimentos de cobertura por bloque temporal, localidades, horizontes, eventos extremos y años de prueba independientes. También se debe establecer la metodología cuando haya suficientes errores *verdaderamente prospectivos*.

**Estado presente:** `intervalos_prediccion_90_publicables=false`, `calibracion_temporal_realizada=false`, `radio_90_por_localidad_horizonte=null`.

## 5. Fuentes externas institucionales y científicas

- [SENAMHI: descarga de datos hidrometeorológicos](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos). El organismo publica observaciones de estaciones convencionales y automáticas; obtener datos por determinados canales puede requerir autenticación.
- [SENAMHI en gob.pe: consulta observacional](https://www.gob.pe/institucion/senamhi/pages/9313-conocer-los-datos-hidrometeorologicos-del-peru): distingue estación, elemento medido y frecuencia.
- [OMM/WMO: OSCAR/Surface](https://wmo.int/activities/global-observing-system-gos/global-observing-system-gos): repositorio oficial de metadatos de estaciones que participan del intercambio internacional. Las redes locales pueden necesitar consultar primero a SENAMHI para identificar códigos, instrumentos y continuidad.
- [OMM/WMO: WIGOS, documentos y metadatos](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-integrated-global-observing-system-wigos/key-wigos-publications): guía de metadatos y control de calidad observacional.
- [Copernicus/ECMWF: ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land): producto de reanálisis que combina información modelada y forzamiento atmosférico; **no mide directamente la temperatura de nuestras cinco estaciones**.
- Muñoz-Sabater et al. (2021), *ERA5-Land: a state-of-the-art global reanalysis dataset for land applications*, **Earth System Science Data**, 13, 4349–4383. [https://doi.org/10.5194/essd-13-4349-2021](https://doi.org/10.5194/essd-13-4349-2021).

## 6. Próximo avance requerido para validación térmica real

**Parte 8I propuesta — incorporación y homologación de observaciones térmicas reales:**

1. Adquirir estaciones SENAMHI con **temperatura máxima/mínima diaria** y preferentemente temperatura media observada o series horarias, con código oficial, fuente, fechas, horas y controles de ausencia.
2. Para cada estación, cotejar posición, altitud, historia del instrumento, WSI si existe, instrumento/método y posibles cambios.
3. Establecer reglas para el promedio térmico mensual: evitar equiparar automáticamente `(Tmax+Tmin)/2` con un promedio horario de ERA5-Land; el estimador debe documentarse y compararse apropiadamente.
4. Obtener pares completos estación–reanálisis para meses realmente coincidentes; documentar georreferenciación, diferencia de altitud y representatividad.
5. Separar validación retrospectiva del producto ERA5-Land de la **evaluación genuinamente prospectiva** del modelo 8E.
6. Diseñar estudio de incertidumbre temporal sin acceso a resultados futuros y sin anunciar precisión operativa a partir de un solo trimestre.

La investigación fitosanitaria de **arándano y vid** continúa como eje paralelo: requerirá observaciones de enfermedad y fenología en parcelas antes de entrenar un modelo de riesgo validado.
