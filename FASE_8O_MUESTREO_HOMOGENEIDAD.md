# Fase 8O — Muestreo detallado y búsqueda de ambientes agroclimáticamente homogéneos

**OAF-Lambayeque · 16–17 octubre de 2026 · periodo climático 1996–2025.**

## Alcance logrado

La fase 8N contenía **69 puntos DEM**, insuficientes para examinar suficientemente la heterogeneidad topográfica. La 8O diseñó una malla adaptativa de **420 puntos** dentro de un límite histórico referencial simplificado de Lambayeque: **293 nodos regulares separados 0,0625°** y **127 puntos adicionales** en torno a los **33 puntos** del inventario anterior que mostraron altura ≥300 m o diferencias de elevación superiores a 350 m dentro de ~21 km.

Se obtuvieron **420 elevaciones reales del Copernicus DEM GLO-90 a través de Open-Meteo Elevation API**, divididas en nueve lotes, cada uno con URL, huella SHA-256, fecha de consulta y respuesta original comprimida. No son sensores de temperatura ni verifican áreas cultivadas. La malla con distancias angulares desiguales solo es un muestreo, **no polígonos territoriales ni estimaciones de porcentaje de superficie**.

**Límite regional:** proviene de fuente secundaria `juaneladio/peru-geojson`; corresponde a una delimitación departamental simplificada y no está acreditada como límite oficial actualizado del INEI/IGN. Un futuro análisis por hectáreas deberá emplear una capa oficial proyectada y documentada. [INEI IDE](https://ide.inei.gob.pe/).

## Diseño de homogeneidad verdaderamente climática

Se eligieron **19 puntos piloto**, distribuidos mediante criterio determinista de separación geográfica máxima dentro de siete franjas físicas (tres testigos por cada una de las seis franjas sobre el nivel del mar y uno para cotas DEM negativas en el primer corte). Esta elección está destinada a cubrir la diversidad de ambientes, **no** a estimar áreas homogéneas por sí sola.

Para cada testigo se diseñó obtener **30 años completos de datos diarios 1996–2025** de:
- **ERA5-Land** vía Open-Meteo: temperatura media, máxima y mínima diarias a 2 metros.
- **ERA5** vía Open-Meteo: precipitación acumulada, humedad relativa media y radiación solar acumulada.
- **DEM GLO-90**: elevación de referencia y clases físicas, solo como variable auxiliar e identificador del muestreo.

Los modelos ERA5 y ERA5-Land **no tienen por qué devolver la misma celda o resolución**. Se conservan por separado los parámetros y respuestas originales del proveedor y se comprueba que las fechas locales coincidan, que haya 360 meses completos por testigo y que no existan valores no numéricos o físicamente incompatibles. Las respuestas se almacenan en seis lotes decenales por modelo, con huellas SHA-256 y metadatos de origen. La ausencia de un lote impide publicar grupos climáticos definitivos.

## Criterio multivariable experimental

Los perfiles de cada testigo contienen **12 normales mensuales calculadas exclusivamente sobre 1996–2025** para cinco indicadores:
- Temperatura media mensual;
- Amplitud térmica diaria media (Tmax menos Tmin);
- Precipitación mensual promedio entre los años;
- Humedad relativa media;
- Radiación solar mensual promedio.

Las cinco familias de variables se escalan por su desviación estándar espacial y estacional y se incorporan a un procedimiento jerárquico determinista de vinculación media, probando agrupaciones con **k entre 2 y 6** y seleccionando la de mayor coeficiente de silueta cuando no se producen grupos aislados de un solo punto.

**Limitación crítica:** un conglomerado obtenido de 19 testigos no es una región continua ni demuestra por sí solo condiciones homogéneas en todos los distritos. Se publica exclusivamente como **núcleo de semejanza climática exploratorio**. El nombre de los grupos no se asigna aún a productores, distritos, niveles de riesgo sanitario ni mapas de polígonos.

Para delimitar zonas agronómicas será necesario continuar con un muestreo climático denso entre los 420 nodos, validar estabilidad al variar periodos/pesos, incluir proximidad y conectividad geográfica, explorar transiciones entre cuencas, gradientes costeros y laderas, comprobar límites oficiales y contrastar con series independientes de SENAMHI y estaciones de campo.

## Estado de ejecución y honestidad de resultados

- DEM regional detallado: **420/420 elevaciones verificadas**.
- Testigos de clima multivariable: **19 seleccionados**.
- Evaluación de homogeneidad: solo será viable cuando estén archivadas las **seis fuentes históricas completas**, sin imputar muestras ni usar tests sintéticos como evidencia de campo.
- **Zonas homogéneas certificadas = 0**.
- **Pronósticos climáticos zonales prospectivamente validados = 0**.

La automatización respeta límites de solicitudes del proveedor y preserva respuestas originales sin descargar de nuevo fuentes ya verificadas. Los conjuntos climáticos, incluso cuando estén disponibles, serán **exploratorios**, no unidades agroclimáticas operativas.

## Archivos de reproducción

- `modelos/muestreo_homogeneidad_8o.py`: diseño determinista de malla, puntos de detalle, DEM y testigos piloto.
- `modelos/perfiles_climaticos_8o.py`: adquisición y comparación multivariable, normales, agrupamiento exploratorio.
- `datos/muestreo_8o/estado_muestreo_8o.json`, `diseno_malla_8o.csv`, `nodos_dem_8o.csv`, `testigos_climaticos_8o.csv`.
- `datos/muestreo_8o/fuentes_dem/`: datos originales y SHA de elevación.
- `datos/perfiles_climaticos_8o/estado_climatico_8o.json`, `grupos_testigos_8o.csv`, `normales_mensuales_testigos_8o.csv`.
- `tests/test_muestreo_homogeneidad_8o.py`, `tests/test_perfiles_climaticos_8o.py`: pruebas sintéticas temporales que nunca se mezclan con reanálisis real.
- `.github/workflows/oaf_muestreo_8o.yml` y `oaf_perfiles_climaticos_8o.yml`: descargas graduadas, controles automáticos y publicación de resultados trazables.
- `modelos/visor_homogeneidad_8o.js`, módulo «Verificación de datos» del [observatorio OAF](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones).

## Próximos controles para predicción de anomalías

La futura clasificación debe ser útil **para toda la región**, y no una extrapolación automática de Chiclayo/Jayanca/Motupe/Olmos. Tras disponer de zonas candidatas contiguas, las predicciones necesitarán una evaluación temporal estricta por zona climática, comparadores sencillos, incertidumbre espacial, y contraste con SENAMHI/mediciones de campo. A las alertas del Niño Costero debe seguir atribuyéndoseles el origen **ENFEN** o la institución correspondiente; no inferir probabilidad de enfermedad en arándano/vid sin observaciones de patógenos, cultivo y fenología.

## Referencias

- [Open-Meteo Elevation API — GLO-90](https://open-meteo.com/en/docs/elevation-api).
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
- [Copernicus ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land).
- Muñoz-Sabater et al. (2021), [ESSD, ERA5-Land](https://doi.org/10.5194/essd-13-4349-2021).
- [Geoportal de datos espaciales INEI](https://ide.inei.gob.pe/).
