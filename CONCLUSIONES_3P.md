# Fase 3P — Conclusiones verificadas y límites

**Fecha:** 14 de octubre de 2026 · **OAF-Lambayeque, versión web v0.6**

## Evidencia nueva

La auditoría `scripts/auditoria_3p_era5.py` consultó Open-Meteo para cinco estaciones, años 1998/2000 y modelos ERA5-Seamless, ERA5 y ERA5-Land. Se obtuvieron **30 de 45 consultas anuales previstas**. Las 15 fallidas corresponden a ERA5-Land: la precipitación diaria no permitió formar un acumulado anual completo. Una comprobación adicional para **1–10 de febrero de 1998**, en Jayanca y Cueva Blanca, comprobó que ERA5-Land devolvía **10/10 valores diarios nulos y 240/240 valores horarios nulos en cada estación**, mientras ERA5 y ERA5-Seamless ofrecían 10/10 días y 240/240 horas con datos. Esto caracteriza la respuesta del servicio para la consulta realizada, **no prueba ausencia de datos en el archivo oficial ECMWF**. **No deben reemplazarse faltantes por lluvia cero.**

La comparación mensual del archivo `datos/auditoria_3p_mensual.csv` estableció:

1. **180/180** pares de acumulados mensuales comparables de ERA5-Seamless y ERA5 fueron **numéricamente idénticos** en las coordenadas/fechas solicitadas (1998: land y nearest; 2000: nearest).
2. **60/60** pares mensuales comparables de ERA5-Seamless en 1998 fueron idénticos entre selección de celda `nearest` y `land`.
3. Las coordenadas del centro de celda **declaradas por la API difieren** entre ERA5-Seamless y ERA5, a pesar de los valores mensuales iguales. Por tanto, **no usar las coordenadas de respuesta por sí solas como demostración del grid de precipitación efectivamente aplicado**.
4. Las **sobreestimaciones de ERA5-Seamless no se limitan a 1998**: en el diagnóstico estacional derivado de los datos multianuales, los sesgos acumulados enero–abril **excluyendo 1998** continúan siendo positivos en las cinco estaciones. Las diferencias relativas deben interpretarse junto con valores absolutos y precipitación instrumental observada.
5. Las distancias y coordenadas históricas exactas de algunas estaciones aún no están confirmadas; comparar puntos mal ubicados puede aumentar sesgos aparentes, especialmente cerca de costa y gradientes altitudinales.

## Qué NO se puede concluir

- No hemos probado que el método `land` o `nearest` cause el sesgo. De hecho, en 1998 dieron resultados idénticos en el conjunto examinado.
- No hemos evaluado la precisión de ERA5-Land porque las series diarias disponibles en las 15 consultas no superaron el control de integridad.
- El contraste PISCOp-SENAMHI puede tener **dependencia de las estaciones** al ser PISCOp un producto mezclado/interpolado con observaciones; no se trata de validación fuera de muestra.
- Dos años para la auditoría de modelos no son suficientes para declarar exactitud de una climatología de 30 años.

## Documentos y datos de soporte

- `AUDITORIA_3P.md`: 30 acumulados anuales con celdas y distancias.
- `datos/auditoria_3p_celdas_modelos.csv`: salida anual de ERA5 y ubicación devuelta.
- `datos/auditoria_3p_mensual.csv`: 360 filas de lluvia mensual comparada, 30 casos completos × 12 meses.
- `datos/estado_3p.json`: 15 incidencias de ERA5-Land.
- `DIAGNOSTICO_ESTACIONAL_3P.md`: análisis por calendario con/sin 1998 derivado de 2 218 pares.
- `datos/diagnostico_estacional_3p.csv`: indicadores estacionales por estación y producto.
- `METADATOS_GEOGRAFICOS_3P.md`: distintas coordenadas reportadas y discrepancias.
- `DIAGNOSTICO_ERA5_LAND_3P.md`: verificación puntual complementaria de nulos diarios/horarios, cuando termine su ejecución.

## Referencias oficiales

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): ERA5, ERA5-Land, ERA5-Seamless y métodos de selección de celdas.
- [PISCOp v3.0, SENAMHI (2026)](https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru).
- [CHIRPS v3, Climate Hazards Center](https://www.chc.ucsb.edu/data/chirps3): producto de 0,05°, 1981–actualidad.

**Detalle metodológico importante para la etapa CHIRPS:** usar preferentemente el **producto mensual final** de CHIRPS v3 para el contraste mensual; el producto diario `DAILY_RNL` reparte los totales pentadales usando ERA5 y, por ello, no es una serie diaria completamente independiente de ERA5. El producto satelital `DAILY_SAT` usa IMERG para ese reparto.

## Próxima fase propuesta: 3Q, CHIRPS v3 y sensibilidad espacial

1. Identificar archivos mensuales `CHIRPS/v3.0/monthly/latam/tifs/` de los mismos meses SENAMHI (1996–2015); extraer píxel de cada estación de forma reproducible, anotando ubicación/resolución de celda y datos faltantes.
2. Calcular MAE, RMSE y sesgo CHIRPS frente a SENAMHI en los mismos **1 109 meses-estación**; contrastar PISCOp y ERA5 sobre exactamente los mismos meses.
3. Comprobar si cambiar entre candidatos documentales de coordenadas instrumentales modifica la celda o las estimaciones.
4. Solo después evaluar capacidad espacial fuera de muestra y añadir un panel fitosanitario relacionado con arándano.

**Regla permanente:** todo dato del observatorio debe figurar como observado, estimado, calculado o pronosticado; no confundir variables ni indicar alerta operativa sin validación.
