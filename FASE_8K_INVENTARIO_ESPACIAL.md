# OAF-Lambayeque · Parte 8K — correspondencia geográfica y estaciones termométricas candidatas

**Fecha: 16 de octubre de 2026.** Área de estudio: Chiclayo, Jayanca, Motupe y Olmos. Responsable técnico del proyecto: Ing. Agrónomo Carlos Enrique Coronel García.

## Objetivo y distinción indispensable

La fase 8K diferencia **cuatro geometrías/documentos**: (i) referencia geográfica de las cuatro localidades OAF solicitadas a Open-Meteo en 8D; (ii) nodo puramente matemático de la cuadrícula regular 0,1°; (iii) latitud/longitud de celda que el proveedor realmente devuelve en **una nueva** consulta histórica ERA5-Land hecha en 8K; (iv) localización, código, altitud, periodo y emplazamiento **instrumental** oficialmente acreditados por SENAMHI.

**IMPORTANTE:** el script 8D no archivó las coordenadas de celda de las respuestas históricas originales. Por tanto, repetir en 8K la selección `models=era5_land, cell_selection=land` identifica **la celda elegida en la consulta nueva**, pero **no certifica que el producto de 1996–2026 archivado en 8D provenga del mismo píxel**. Atribuir automáticamente el mismo píxel o la misma orografía a la estación instrumental sería una afirmación no demostrada.

La fuente Copernicus Climate Data Store describe ERA5-Land en una cuadrícula geográfica regular de **0,1° × 0,1°** (resolución nativa de ~9 km). La API Historical Weather de Open-Meteo puede seleccionar el píxel preferido sobre tierra considerando topografía y devolver coordenadas de celda diferentes de las solicitadas. Su campo `elevation` es la altitud usada/referida por la API para selección o corrección de elevación; **NO es prueba suficiente de la orografía original de ERA5-Land ni de la altitud exacta del sensor SENAMHI.**

- [Copernicus ECMWF ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- [Open-Meteo Historical Weather API — cell_selection, elevation y centro de celda devuelto](https://open-meteo.com/en/docs/historical-weather-api).
- [SENAMHI — catálogo institucional de estaciones en Lambayeque](https://www.senamhi.gob.pe/?dp=lambayeque&p=estaciones).
- [SENAMHI — catálogo/descarga de datos de estaciones](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos).
- [OMM — Guide to Instruments and Methods of Observation (WMO-No. 8)](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/instruments-and-methods-of-observation-programme-imop/guide-instruments-and-methods-of-observation-wmo-no-8).

## 1. Consulta geográfica nueva y reproducible

El archivo [`datos/metadatos_celdas_openmeteo_8k.csv`](datos/metadatos_celdas_openmeteo_8k.csv) documenta cuatro solicitudes y cuatro respuestas del proveedor con URL completa, fecha UTC, respuesta de latitud/longitud, elevación y SHA-256 de la respuesta JSON recuperada. Se usó un solo día (01/07/2020) de la API histórica, variable `temperature_2m_mean`, zona `America/Lima`, `models=era5_land` y `cell_selection=land`, el valor por defecto de selección utilizado en 8D.

| Localidad OAF | Solicitud (lat; lon) | Respuesta del proveedor 8K (lat; lon) | Distancia aproximada punto→celda |
|---|---|---|---:|
| Chiclayo | -6,77140 ; -79,84090 | -6,7999954 ; -79,7999950 | 5,524 km |
| Jayanca | -6,39278 ; -79,82280 | -6,4000015 ; -79,7999950 | 2,645 km |
| Motupe | -6,15083 ; -79,71420 | -6,1999970 ; -79,7000000 | 5,688 km |
| Olmos | -5,98825 ; -79,74723 | -6,0000000 ; -79,7000000 | 5,384 km |

Los valores de distancia son cálculos Haversine por el sistema OAF a partir de coordenadas del proveedor; **no son errores geográficos instrumentales ni evaluación de habilidad climática**. La respuesta también suministró una elevación de 34, 62, 132 y 177 m en ese orden; se guardó como `elevacion_respuesta_m` sin certificar que sea la altitud de la cuadrícula ERA5-Land o de una estación.

**Estado de certificación:** 4 respuestas nuevas del proveedor; **0 celdas originales del estudio 8D demostradas**; **0 estaciones con temperatura media instrumental comprobada**.

## 2. Inventario de estaciones: dos clases de evidencia que no deben confundirse

**A. Cinco estaciones de los archivos históricos instrumentales OAF**: Jayanca (La Viña), Cayaltí, Reque, Lambayeque y Cueva Blanca; 1.109 meses-estación completos de **lluvia** archivados entre 1996–2015. El documento 8H contiene dos coordenadas candidatas para algunas estaciones, con diferencias documentales. Sus datos **no pueden validar temperatura**.

**B. Ocho nombres de estaciones incluidos en una tabla de Tmax y Tmin de un boletín climático histórico de SENAMHI DZ2**: Jayanca, Olmos, Reque, Lambayeque, Cayaltí, Tongorrape, Sipán y Puchaca. Están documentados en [`datos/candidatas_termometricas_documentales_8k.csv`](datos/candidatas_termometricas_documentales_8k.csv), respaldado por [boletín SENAMHI DZ2](https://www.senamhi.gob.pe/load/file/03601SENA-102.pdf). La **mención de Tmax/Tmin agregadas en un boletín** respalda una búsqueda documental de fuentes térmicas, pero **no prueba disponibilidad de temperaturas diarias o horarias, continuidad 1996–2025, códigos de instrumento ni autorización de redistribución**. Los nombres compartidos entre A y B **no prueban identidad de archivos ni sensores**.

Todas las candidatas se encuentran en estado `elegible_validacion_instrumental=false`. El catálogo histórico de precipitación no representa toda la red SENAMHI de Lambayeque.

## 3. Procedimiento informático

- [`modelos/consultar_metadatos_openmeteo_8k.py`](modelos/consultar_metadatos_openmeteo_8k.py): consulta los cuatro puntos, valida coherencia de modelo, fecha, zona horaria y respuesta diaria; captura URL, hora de consulta y SHA-256 del JSON. No modifica las emisiones 8D ni inventa elevaciones. No repite consultas si la instantánea completa ya está archivada, salvo refresh explícito.
- [`modelos/auditoria_celdas_estaciones_8k.py`](modelos/auditoria_celdas_estaciones_8k.py): extrae por AST las cuatro coordenadas originales del código 8D; detecta cambios inesperados; revisa las cinco estaciones de lluvia de 8H y las ocho candidatas de boletín; admite metadatos proveedor nuevos con procedencia; calcula distancias geodésicas y variantes; **prohíbe marcar verificadas las celdas 8D originales a partir de una consulta 8K**.
- [`tests/test_auditoria_celdas_8k.py`](tests/test_auditoria_celdas_8k.py): pruebas locales con metadatos sintéticos en directorios temporales (no se publican como resultados de campo), validando las barreras físicas/documentales, ausencias y consistencia de la geometría.
- [`.github/workflows/oaf_geografia_8k.yml`](.github/workflows/oaf_geografia_8k.yml): pruebas, consulta de metadatos si todavía faltan, auditoría espacial, comprobación de panel web y actualización de resultados.

### Archivos científicos de salida

- [`datos/seleccion_espacial_8k/estado_8k.json`](datos/seleccion_espacial_8k/estado_8k.json): inventarios y controles, conteos reales y hashes.
- [`datos/seleccion_espacial_8k/localidades_celdas_8k.csv`](datos/seleccion_espacial_8k/localidades_celdas_8k.csv): localidad solicitada y coordenada realmente devuelta.
- [`datos/seleccion_espacial_8k/proximidad_estaciones_8k.csv`](datos/seleccion_espacial_8k/proximidad_estaciones_8k.csv): distancia de variantes históricas a cada localidad y respuesta 8K del proveedor, **no elegibilidad térmica**.
- [`datos/seleccion_espacial_8k/vista_8k.json`](datos/seleccion_espacial_8k/vista_8k.json): datos derivados destinados al módulo de **Verificación de datos**.

## 4. Próxima etapa

**Parte 8L — evaluación de cambio de celda, sensibilidad costera y orográfica y protocolo de obtención instrumental**: auditar si la consulta 8D original conservó alguna respuesta geográfica en resultados brutos o bitácoras anteriores, documentar comparación ERA5-Land sobre puntos exactos originales y centros de celda bajo parámetros y fechas trazables, recopilar fichas oficiales con códigos/categorías instrumentales de las candidatas SENAMHI y sus series térmicas *cuando sea posible legal y técnicamente*. No atribuir sesgo a altitud ni hacer correcciones adiabáticas automáticas sin prueba. Priorizar accesibilidad para productores, mantener modelos ENFEN/ENSO y arándano/vid como líneas paralelas.

**Regla permanente:** temperatura modelada ≠ temperatura instrumental. Una respuesta del proveedor no es la prueba definitiva de la celda histórica, y una mención de Tmax/Tmin no equivale a un registro mensual de temperatura media validado.
