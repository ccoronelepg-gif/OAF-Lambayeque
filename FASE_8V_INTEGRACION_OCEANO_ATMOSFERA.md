# Fase 8V — Integración histórica océano-atmósfera, Lambayeque

**OAF-Lambayeque. Periodo 1996–2025. Investigación retrospectiva, NO alertas operativas.**

## Base integrada real, sin mezclar observación y modelo

Se implementó `modelos/integracion_oceano_atmosfera_8v.py`. Utiliza exclusivamente archivos ya archivados y auditables:

- Viento ERA5 a 10 m, seis sitios terrestres/marinos de ensayo: `datos/meteorologia_8u/vientos_mensuales_8u.csv`.
- Temperatura y anomalías SST **regionales** de Niño1+2 y Niño3.4 NOAA CPC: `datos/oceanografia_8u/tsm_nino12_mensual_8u.csv`.
- Corrientes **geostróficas**, no la corriente marina total, NOAA/AOML 2017–2025: `datos/corrientes_8u/corrientes_geostroficas_2017_2025.csv`.
- Temperatura del aire ERA5-Land, lluvia y radiación ERA5 acumuladas por mes: `datos/lambayeque_mensual_era5_8d.csv`. Se filtran únicamente los 360 meses 1996–2025, ignorando los meses de 2026 presentes en origen.

**Salidas reproducibles:**

- `datos/integracion_8v/matriz_terrestre_8v.csv`: **1440 meses-sitio**, cuatro localidades Chiclayo, Jayanca, Motupe y Olmos con temperatura, precipitación, radiación, velocidad/vectores aproximados del viento, SST de índices regionales y rezagos Niño1+2 t−1, t−2 y t−3. El primer trimestre carece de algunos rezagos porque el archivo de entrada comienza en enero 1996; se dejan en blanco.
- `datos/integracion_8v/matriz_marina_8v.csv`: **720 meses-sitio** con dos celdas ERA5 de viento marino, SST de los índices NOAA regionales y corrientes geostróficas cuando haya meses completos a partir de 2017. Las celdas de viento y corriente son próximas pero **NO están colocalizadas**. Los puntos oceánicos aún necesitan control independiente de máscara oceánica.
- `datos/integracion_8v/estado_integracion_8v.json`: número comprobado de meses disponibles, restricciones metodológicas y **SHA-256 de los cuatro CSV originales y de los resultados**.

La matriz no interpreta Niño1+2 como TSM de una playa, ni le asigna la identidad del ICEN oficial de ENFEN. No presenta la dirección meteorológica de viento como rumbo de una corriente. NOAA contiene versiones revisadas retrospectivamente y **no representa en forma exacta los datos disponibles en el momento de cada pronóstico histórico**.

## Control de calidad

El motor rechaza meses o celdas meteorológicas duplicados, faltantes para variables obligatorias, meses de viento sin todos los días, rangos no finitos o físicamente inverosímiles y metadatos que indiquen fuentes mal etiquetadas. No rellena meses parciales de corrientes, ni inventa el periodo 1996–2016. Una lectura ausente de corrientes no inutiliza la matriz terrestre: queda vacía y queda registrada.

Reproducción: `python modelos/integracion_oceano_atmosfera_8v.py`, `python modelos/integracion_oceano_atmosfera_8v.py --check`. La segunda orden contrasta byte a byte los archivos con fuentes actuales. Las seis pruebas sintéticas están en `tests/test_integracion_oceano_atmosfera_8v.py`, y la tarea de GitHub Actions en `.github/workflows/oaf_integracion_oceano_atmosfera_8v.yml`.

## Próximo paso — 8W

Evaluar objetivos de lluvia y temperaturas extremas por localidad y, posteriormente, por zonas altitudinales y topoclimáticas: climatologías **calculadas solo con cada corte de entrenamiento**, validación de origen móvil y espacial, umbrales locales de precipitación, prueba de referencias de climatología/persistencia y evaluación de errores y probabilidades calibradas. Contrastar con estaciones oficiales SENAMHI; no calcular alertas de enfermedades de arándano/vid sin evaluaciones sanitarias de campo.

**Límites:** viento y meteorología son reanálisis, corrientes NOAA/AOML son geostróficas y no todas las corrientes, SST NOAA CPC es regional, los 1440 meses-sitio comparten información y autocorrelación. Ningún resultado 8V equivale a una alerta predictiva validada o demuestra causalidad.

**Fuentes:** [Copernicus/ERA5](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels), [NOAA Niño1+2/3.4](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices), [NOAA AOML/CoastWatch](https://coastwatch.pfeg.noaa.gov/erddap/griddap/miamicurrents.html), [ICEN oficial y metodología](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen).
