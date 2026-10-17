# OAF-Lambayeque — Punto de reanudación fase 8U, 17 de octubre de 2026

## Meta y hallazgos 8U

Objetivo vigente: anticipar anomalías agroclimáticas, El Niño Costero y eventual riesgo fitosanitario para arándano/vid según **zonas físicas realmente semejantes**, sin confundir pisos altitudinales, celdas de reanálisis o asociaciones históricas con fronteras homogéneas agrícolas.

### Viento en cuatro localidades, climatología real de reanálisis
`modelos/viento_oceano_8u.py`, `.github/workflows/oaf_viento_oceano_8u.yml`, `datos/viento_8u/estado_factores_8u.json` y `viento_mensual_8u.csv`: tres archivos ERA5 originales comprimidos por década **1996–2025**, fechas locales/días completos/SHA-256, 360 meses por cada una de Chiclayo, Jayanca, Motupe, Olmos (1.440 meses–localidad). Velocidad 10m media **3,138 / 2,410 / 1,890 / 1,393 m/s**, respectivamente. Son **vientos modelados, NO anemómetros SENAMHI**. Dirección meteorológica es **desde dónde sopla**, componentes zonal u/meridional v aproximadas a partir de medias diarias y direcciones dominantes.

### Relación descriptiva con Niño1+2
`modelos/relacion_viento_sst_8u.py`, `tests/test_relacion_viento_sst_8u.py`, `datos/viento_8u/correlaciones_viento_sst_8u.json` y .csv: sobre **358 meses emparejados**, resta media calendario 1996–2025 propia del viento por punto y compara índice NOAA Niño 1+2 revisado de **dos meses antes**. Correlación r entre SST y velocidad viento: Chiclayo **+0,172522**, Jayanca **+0,217735**, Motupe **+0,157064**, Olmos **+0,194071**. Con componente zonal atmosférica: Chiclayo **−0,604520**, Jayanca **−0,396361**, Motupe **−0,385576**, Olmos **−0,311165**. Asociación descriptiva, sin incertidumbre autocorrelación/ajuste por otros factores, **NO CAUSAL NI PREDICTIVA**. No son corrientes oceánicas u/v.

### Temperatura del mar y corrientes: primer producto modelado real archivado
`modelos/instantanea_marina_8u.py`, `tests/test_instantanea_marina_8u.py`, `.github/workflows/oaf_corrientes_marinas_8u.yml` y `datos/marino_8u/`: primer **snapshot verificable de 72 horas** Open-Meteo Marine / SMOC Météo-France tomado **2026-10-17T03:51:48Z**, con 3 celdas marinas al oeste de Lambayeque, periodo local **16–18 octubre 2026**, sin poder llamar las 72 h “pronóstico emitido antes del periodo”, ya que incluye horas pasadas.
- Archivo original comprimido y metadatos `datos/marino_8u/fuentes/ocean_forecast_2026-10-17.json.gz` y `.meta.json`, SHA-256 respuesta original `1459507b8405ea5d9dab9a2b1e42622e38a0a81a1dfc13bdb9bd0729559c693e`. Estado `datos/marino_8u/estado_marino_8u.json`.
- Latitudes solicitadas -6,1/-6,5/-6,9, longitud -80,7° (tres puntos mar abiertos). Centros reales devueltos se archivan, **no son boyas**.
- Norte: SST media **26,0569°C**, velocidad corriente **0,1701 m/s**, u **−0,0998 m/s** (oeste), v **+0,1316 m/s** (norte).
- Centro: SST **25,5903°C**, corriente **0,1636 m/s**, u **−0,1033**, v **+0,1193 m/s**.
- Sur: SST **24,9319°C**, corriente **0,1782 m/s**, u **−0,1346**, v **+0,0624 m/s**.
- Diferencia SST N–S **1,125°C** en esa instantánea modelada; NO representa una anomalía climática Niño o una diferencia sistemática 30 años.
- **Importante:** Marine API devolvió rapidez de corrientes en **km/h** pese a `velocity_unit=ms`; se detectó la unidad en `hourly_units` y se convirtió explícitamente ÷3,6 a m/s; tests comprobaron conversión. Rumbo de corriente indica **HACIA dónde fluye**, distinto del viento meteorológico que indica DESDE dónde sopla.
- **NO existe serie de corrientes 1996–2025 validada**, ni habilidad predictiva oceanográfica, ni in situ. Costa es difícil para el modelo; tres celdas no caracterizan Corriente de Humboldt. Producto NASA OSCAR v2 y Copernicus GLOBAL_MULTIYEAR_PHY_001_030 aún pendientes de obtener/QA y credenciales posibles. Antiguo NOAA ERDDAP `jplOscar` pese al título 1992–presente solo contiene 2011-12 a 2014-09, **no sirve** como 1996–2025.
- NOAA Niño1+2 de CPC es SST índice de región amplia revisada, no la SST costera. `datos/sst_costera_8u/estado_sst_8u.json` de piloto NOAA OISST había **0/6 bloques obtenidos** en último control; comprobar estado real antes de afirmar datos.

### Completitud 8P y reevaluación 8S/8T
8P ahora completó **24/24 bloques** y **81/81 testigos** con 1996–2025. Tras exclusión precautoria de DEM≤5 m quedan 79 sitios admisibles, **55 píxeles ERA5-Land únicos**. Automatización actualizada:
- `.github/workflows/oaf_validacion_regional_8s.yml` ahora se dispara también al actualizar `datos/clima_contiguo_8p/estado_clima_8p.json`;
- `.github/workflows/oaf_nino12_oceanico_8t.yml` ahora se dispara al actualizar `datos/validacion_regional_8s/estado_validacion_8s.json`.
- 8S recalculado: 5 cortes y 4 bandas geográficas, **9.240** meses-píxel del backtest 2012–2025, RMSE retenido **0,439071°C** vs persistencia **0,459102°C**, skill ~4,363%.
- 8T recalculado: misma muestra 55 píxeles, RMSE sin indicador Niño1+2 **0,439071°C** vs preseleccionado (con SST cuando valida bien) **0,438524°C**, mejora incremental **0,1246%** muy pequeña; 3/5 cortes temporales y 9/20 espaciales seleccionaron la variante SST. No demuestra pronóstico del Niño Costero ni estaciones SENAMHI.
- Los resultados anteriores 8S/8T de 65 sitios/50 celdas eran otro corte histórico, no comparar como si mismo diseño.
- Zonas homogéneas SIG certificadas = **0**; alerta fitosanitaria arándano/vid validada = **0**; pronóstico El Niño Costero verificado prospectivo = **0**, estaciones termométricas SENAMHI independientes en los modelos = **0**.

### Reporte y portal
- Informe `FASE_8U_VIENTO_SST_CORRIENTES.md` describe fundamentos, datos obtenidos, control OISST/OSCAR, vientos ERA5, Niño1+2, snapshot marino, conclusiones, recomendaciones.
- `index.html`: panel #oaf-factors-8u; `modelos/visor_factores_8u.js` muestras viento, correlaciones y estado SST piloto, más `modelos/visor_marino_8u.js` (tabla adicional SST y componentes u/v) cargada al expandir panel. `.github/workflows/oaf_corrientes_marinas_8u.yml` prueba 6 casos de conversión/dirección y correlaciones, node --check JS, comprueba ids DOM y archiva snapshot diario modelado sin confundirlo con 30 años. Success run 39000757206 para integración y QA; comprobar último run si cambios.
- Sitio público: https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.
- Fuentes técnicas: https://open-meteo.com/en/docs/marine-weather-api; https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices; https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_FINAL_V2.0; https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description.

## Siguiente fase 8V
1. Integrar lluvia y extremos térmicos como **objetivos de predicción** que benefician a productores; umbrales de lluvia extrema por cada sitio definidos en training, clasificador prob. contra climatología/persistencia con Brier/ROC/PR y 5 cortes sin fugas, temporal y spatial por cuencas aún pendientes.
2. Completar verdadera serie histórica oceánica de SST costera 1996–2025 NOAA OISST con máscara mar y QA, y corrientes u/v NASA OSCAR/Copernicus Marine si hay acceso legítimo, con datos por profundidad, celdas, periodos y fuente original, sin confundir forecast 72h con 30y.
3. SENAMHI instrumental de temperatura/lluvia/viento de estaciones reales, cuencas, gradiente altitudinal, topografía, SENASA/ENFEN; no inventar series. Evaluar alertas Niño Costero solo después de definir eventos con boletines emitidos oportunamente y predictores disponibles a fecha de emisión.
4. Agregar humedad, radiación, viento y objetivo lluvia con QA diferente para cada modelo/latitud; revisar autocorrelación y pseudorreplicación, no asumir que la correlación fuerte de viento zonal con Niño1+2 es causal.
5. Para arándano/vid, exigir incidencia real de enfermedad, cultivo/fenología y microclima antes de modelos de riesgos fitosanitarios operativos.

El usuario prefiere avanzar implementando realmente en GitHub sin preguntas ni ejercicios.
