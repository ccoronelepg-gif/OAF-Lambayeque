# Fase 9Q — Precipitación CHIRPS completa 1996–2025, pisos altitudinales y agrupaciones hidroclimáticas exploratorias

**OAF-Lambayeque — 17/10/2026. Fase ejecutada y reproducible.** El observatorio conserva una regionalización experimental, no delimitaciones oficiales ni pronósticos zonales verificados.

## 1. Recuperación completa de 30 años CHIRPS v3 final

El inventario inicial incluía 108 meses CHIRPS v3 FINAL LATAM archivados en 9O y 12 meses GLOBAL USGS archivados en 9P. **9Q recuperó los 240 meses faltantes**, sumando **360 meses de 360**, con **30 años completos 1996–2025**. Se auditaron 240 nuevas huellas SHA-256, URL de origen, integridad geográfica, extracción por 42 polígonos y por 81 testigos; **0 meses faltantes y 0 errores de descarga finales**. Los archivos nuevos se conservaron mediante confirmaciones por lotes de 24 meses en GitHub. La reproducción no requiere que los 5,3 GB aproximados de TIFF globales originales formen parte del repositorio, porque se preservaron URL y SHA-256; una repetición posterior deberá comprobar la identidad exacta.

La fuente es [USGS/FEWS NET, CHIRPS v3 FINAL mensual global](https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/global/monthly/chirps/final/downloads/monthly/), con equivalente regional [UCSB/CHC CHIRPS v3 FINAL LATAM](https://www.chc.ucsb.edu/data/chirps3). Su equivalencia espacial en el área de estudio se verificó contra 1996-01 y 2025-12; todos los nuevos archivos respetan resolución nativa 0,05° y grilla de referencia. La fuente se genera mediante observaciones satelitales y de estaciones, por lo que **la serie completa no significa disponer de 30 años instrumentales independientes por sector**.

Datos publicados: [fuentes_chirps_9q.json](datos/recuperacion_9q/fuentes_chirps_9q.json), [sectores_mensuales_9q.csv](datos/recuperacion_9q/sectores_mensuales_9q.csv) y [testigos_mensuales_9q.csv](datos/recuperacion_9q/testigos_mensuales_9q.csv). Se conservan intactos los originales de 9O/9P.

## 2. ¿Cómo cambian los indicadores entre los pisos altitudinales?

Los 42 polígonos de la fase 9K se agruparon inicialmente en **siete clases de altitud DEM**; seis corresponden a rangos no negativos y una separa el terreno DSM con cota negativa para revisión. **No equivalen automáticamente a ecorregiones, ecosistemas o pisos ecológicos oficiales.** La clasificación climática oficial [SENAMHI, Climas del Perú (2020)](https://www.gob.pe/institucion/senamhi/informes-publicaciones/2158106-climas-del-peru-mapa-de-clasificacion-climatica) integra además precipitación, temperatura, humedad y otros condicionantes regionales.

Los resultados históricos sobre sectores con píxeles CHIRPS terrestres válidos y testigos de reanálisis ERA5/ERA5-Land son:

| Clase de altitud | Sectores originales | Con lluvia CHIRPS | Lluvia anual mediana de sectores (mm/año) | Temperatura ERA5-Land promedio (°C) | Humedad ERA5 promedio (%) |
|---|---:|---:|---:|---:|---:|
| Planicie litoral 0–99 m | 4 | 4 | **50,19** | 22,23 | 73,99 |
| Valle bajo 100–299 m | 6 | 6 | **154,84** | 22,04 | 75,40 |
| Piedemonte 300–799 m | 14 | 11 | **193,36** | 20,60 | 76,82 |
| Ladera baja 800–1599 m | 6 | 6 | **223,90** | 17,92 | 77,86 |
| Ladera media 1600–2499 m | 8 | 8 | **520,29** | 15,93 | 78,00 |
| Montaña alta ≥2500 m | 3 | 3 | **791,62** | 11,53 | 75,90 |
| Cota negativa DSM: revisar | 1 | 1 | 51,58 | No disponible | No disponible |

**No sumar** los sectores como hectáreas: la lluvia es la mediana entre medias sectoriales (ponderación igual por sector) y no un promedio de superficie cultivada. Las temperaturas y humedad son **promedios de testigos de reanálisis asociados**, no estaciones independientes. La radiación de onda corta ERA5 se presenta en el archivo [comparacion_pisos_9q.csv](datos/recuperacion_9q/comparacion_pisos_9q.csv), conservando la unidad original acumulada mensual y sin convertirla en radiación recibida por cada parcela. Los sectores S028, S032 y S034 siguen sin centros de píxel terrestre válidos dentro de sus polígonos originales; no se reemplazaron con ceros ni con lluvia del sector vecino.

La muestra revela un gradiente histórico de mayor lluvia y menor temperatura en los pisos altos; **no es una ley monótona para cada ladera**. En piedemonte, por ejemplo, los sectores evaluables abarcan entre **106,29 y 379,49 mm/año**. La orientación, la exposición, la cuenca y la localización pueden cambiar considerablemente el microclima dentro de un mismo piso.

## 3. Agrupación por similitud multivariable y cuenca

El módulo [agrupar_pisos_9q.py](modelos/agrupar_pisos_9q.py) evalúa pares de sectores con la misma clase de altitud, al menos un código hidrográfico común en ANA/IDEP, proximidad espacial, **cero píxeles CHIRPS compartidos** y al menos 10 años completos. Además requiere simultáneamente:
- Correlación de anomalías mensuales de precipitación CHIRPS (`log1p`, estacionalidad retirada) ≥ **0,80**, que se mantenga ≥0,70 al excluir las décadas predefinidas.
- Diferencia relativa de lluvia media ≤ **25 %**, temperatura ERA5-Land ≤ **2 °C**, humedad relativa ERA5 ≤ **12 puntos** y radiación ERA5 ≤ **25 %**.
- Testigos climáticos asociados a **ambos** sectores. Cuando faltan testigos o datos espaciales, el sector se mantiene separado.
- Formación de grupos evitando unir transitivamente A y C solo porque ambos son parecidos a B (condición por todas las parejas del grupo).

**Resultado del método:** se analizaron **46 pares cercanos con misma clase altitudinal y unidades hidrográficas compartidas**; **12 parejas** cumplen simultáneamente los filtros numéricos; el algoritmo produce **siete agrupaciones cartográficas propuestas** de dos sectores cada una:

| Grupo experimental | Piso físico | Sectores |
|---|---|---|
| Q01 | Montaña alta ≥2500 m | **S006 + S007** |
| Q02 | Ladera media 1600–2499 m | **S015 + S016** |
| Q03 | Ladera media 1600–2499 m | **S017 + S018** |
| Q04 | Piedemonte 300–799 m | **S023 + S029** |
| Q05 | Piedemonte 300–799 m | **S024 + S027** |
| Q06 | Piedemonte 300–799 m | **S030 + S031** |
| Q07 | Valle bajo 100–299 m | **S040 + S042** |

Se trata de **hipótesis de similitud climática retrospectiva** y no una decisión de fusionar administrativamente los 42 sectores ni establecer límites agrícolas. Las diferencias entre observaciones CHIRPS y reanálisis, la disponibilidad de estaciones meteorológicas independientes y las condiciones intraparcela siguen pendientes de contraste externo. Una coincidencia de testigos simulados puede compartir procesos de interpolación; los filtros son umbrales exploratorios de trabajo, no criterios normativos validados por SENAMHI.

Archivo cartográfico: [agrupaciones_exploratorias_9q.geojson](datos/recuperacion_9q/agrupaciones_exploratorias_9q.geojson). Comparación de las 46 parejas: [pares_hidroclimaticos_9q.csv](datos/recuperacion_9q/pares_hidroclimaticos_9q.csv). Informe integral con referencias, límites y métricas: [diagnostico_pisos_y_agrupaciones_9q.json](datos/recuperacion_9q/diagnostico_pisos_y_agrupaciones_9q.json).

## 4. Transparencia y trazabilidad

Los procedimientos y descargas se reproducen mediante [recuperar_chirps_9q.py](modelos/recuperar_chirps_9q.py), [agrupar_pisos_9q.py](modelos/agrupar_pisos_9q.py), [pruebas SIG/climáticas](tests/test_agrupacion_9q.py) y [GitHub Actions 9Q](.github/workflows/oaf_agrupaciones_9q.yml). La pestaña **Análisis de clima regional** incluye el módulo interactivo «¿Qué pisos y sectores tienen condiciones climáticas similares?» con selector de lluvia, temperatura, humedad y radiación, tabla por piso y agrupaciones exploratorias.

**Criterios de honestidad científica:** CHIRPS es una grilla híbrida satélite-pluviómetros; ERA5 y ERA5-Land son reanálisis. Se conservan **0 zonas homogéneas instrumentales certificadas, 0 modelos zonales prospectivamente verificados y 0 alertas fitosanitarias derivadas**. No hay aprobación de intervención contra enfermedades de arándano ni vid basada exclusivamente en estas correlaciones. Las unidades hidrográficas son intersecciones referenciales procedentes de una capa ANA/IDEP cuya vigencia legal aún debe cotejarse.

## 5. Próxima fase 9R

El siguiente trabajo científico defendible será validar las siete agrupaciones candidatas con pluviómetros y estaciones SENAMHI de ubicación confirmada, probar la sensibilidad a la resolución de rejilla, delimitar mejor la exposición de laderas y evaluar anomalías 1996–2025 con referencias congeladas. Solo entonces se podrá estudiar transferencia predictiva NMME/ENSO por zona con datos estrictamente anteriores a la fecha de pronóstico, y asociar meteorología a enfermedad real en arándano y vid a partir de observaciones de campo.

**Lema OAF:** «Datos abiertos y ciencia climática al servicio del campo».
