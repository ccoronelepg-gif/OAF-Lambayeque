# OAF-Lambayeque · Punto de reanudación 8T · octubre 2026

## Ejecución real y resultados

La fase **8T** se implementó directamente en el repositorio https://github.com/ccoronelepg-gif/OAF-Lambayeque y en el portal https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones.

**8T pregunta:** ¿añadir el índice histórico Niño 1+2 NOAA CPC a las anomalías térmicas previas locales y regionales mejora su predicción un mes por delante?

- Fuente oceánica **NOAA CPC** https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices; columna **`NINO1+2 ANOM`**, cobertura 1996–2025, **360 meses**. Respuesta original `datos/oceano_8t/noaa_cpc_sstoi_indices.txt.gz` y metadatos `datos/oceano_8t/noaa_cpc_sstoi_indices.meta.json` fijados por SHA-256.
- Archivo descargado 2026-10-17 03:29:47 UTC; SHA-256 original `4cf4938114c9f6130566d76ef280cddb3e601444d26d47237a9d2348628e5317`. **Serie histórica revisada hasta 2026, no vintages en tiempo real**. No se presenta como ICEN de ENFEN ni alerta oficial.
- El predictor oceánico se incluye con **dos meses de retraso t−2**, nunca del mes objetivo o siguiente. Se comparan dos modelos lineales ridge: (i) anomalías locales y regionales previas de 8S; (ii) lo mismo + índice Niño1+2 t−2. Ambos ajustados en training, seleccionados solo con validación anterior al test.
- Cinco ventanas rolling origin **2012–2025**, cuatro bandas geográficas retenidas, **65 testigos, 50 centros de ERA5-Land únicos, 8.400 predicciones retrospectivas** por tipo de evaluación.
- **Resultado 8T temporal:** baseline 8S RMSE **0,448275 °C** vs estrategia preseleccionada incluyendo cuando aplica Niño1+2 **0,448468 °C**, **empeora 0,0431 %**.
- **Resultado 8T espacial:** baseline 8S **0,448167 °C** vs estrategia preseleccionada **0,448123 °C**, **mejora solo 0,0098 %**, prácticamente nula. Persistencia 0,468228 °C, estrategia preseleccionada aún ≈4,2938 % mejor que persistencia.
- La variante oceánica se escogió en solo **2/5 ventanas cronológicas** y **8/20 ventanas espaciales**. En prueba 2015–2017 empeoró pese a ser elegida según validación. Comparación por estratos mostró efectos diminutos mixtos.
- **Conclusión:** incorporar únicamente Niño1+2 t−2 al modelo térmico existente NO DEMOSTRÓ ventaja incremental predictiva consistente; esto NO niega la influencia de El Niño Costero en otras variables, periodos, rezagos o eventos.
- **SENAMHI instrumental: 0 fuentes térmicas independientes integradas**; **predicción oficial Niño Costero o ENFEN: 0**; **zonas agroclimáticas agrícolas certificadas: 0**. Modelo objetivo sigue siendo temperatura del aire mensual de **ERA5-Land**, no la propia predicción del fenómeno oceánico ni enfermedad.
- **8P en progreso:** al último control **21 de 24 fuentes nuevas** archivadas, pero solo **67 testigos con 30 años completos** (tres grupos nuevos completos). Faltan tres bloques del cuarto grupo (14 testigos); futura finalización elevaría a 81 testigos, con cambio de cobertura y necesidad de recomputar 8S/8T. La automatización 8P sigue programada.

## Archivos

- `modelos/contraste_oceanico_8t.py`: fetch NOAA una vez, SHA-256 estricto, lectura de anomalía Niño1+2, selección de estrategia por validación, cinco cortes y cuatro franjas.
- `tests/test_contraste_oceanico_8t.py`: pruebas sintéticas de parsing NOAA, 360 meses, tiempo t−2 y resultados negativos no ocultos.
- `.github/workflows/oaf_nino12_oceanico_8t.yml`: CI, fetch NOAA, `--check`, comparación con 8O/8P, commit auditable y revisión de interfaz.
- `datos/oceano_8t/`: fuente original NOAA y metadatos.
- `datos/validacion_oceanica_8t/estado_oceanico_8t.json`, `predicciones_oceanicas_temporales_8t.csv`, `predicciones_oceanicas_espaciales_8t.csv`: resultados verdaderos y reproducibles.
- `FASE_8T_ENSO_OCEANICO.md`: informe metodológico completo con valores y límites.
- `modelos/visor_oceanico_8t.js` + `index.html`: panel 8T público en #verificaciones.

## Siguiente fase 8U

1. Priorizar la **predicción de anomalías relevantes al Niño Costero**: precipitación diaria/mensual, temperaturas máximas y eventos extremos, así como humedad/radiación en ambientes de Lambayeque. Evitar usar SST revisada en modelos operativos si no existe vintage real.
2. Probar fuentes oceánicas y atmosféricas históricas con disponibilidad temporal clara: Niño1+2, Niño3.4, ENFEN/ICEN de boletines originales emitidos en fechas pasadas, y posiblemente T300, validando entradas t−1/t−2/estacionales sin fuga.
3. Obtener series **SENAMHI instrumentales reales** y metadatos (nombre/código/latitud/longitud/altitud/cobertura/sensor/QA) por localidades y periodo; si no hay datos, mantener bloqueo de validez independiente.
4. Completar adquisición 8P restantes con el cron existente y recomputar 8S/8T cuando haya 81 testigos, registrando cambio de muestra.
5. Consolidar zonificación de pisos/climas con cartografía oficial INEI/IGN, máscara tierra/mar, cuencas, exposición, validación espacial y análisis del clima con otros reanálisis o estaciones. No crear zonas homogéneas certificadas ni alertas fitosanitarias de arándano y vid sin campo.

Se solicita continuar ejecutando en GitHub y publicar avances reales, sin cuestionarios al usuario y sin afirmaciones operativas prematuras.
