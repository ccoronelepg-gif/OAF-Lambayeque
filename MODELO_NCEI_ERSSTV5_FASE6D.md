# Fase 6D — Reconstrucción reciente NOAA NCEI ERSSTv5 Niño 1+2 y experimentos a 1–3 meses

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Proyecto:** OAF-Lambayeque  
**Fecha de elaboración:** 14 de octubre de 2026 (Perú; ejecuciones automáticas fechadas en UTC).  
**Estado:** experimental; no es ICEN oficial, pronóstico operacional del ENFEN ni alerta fitosanitaria.

## Objetivo científico

Continuar el desarrollo de herramientas predictivas para anomalías de temperatura superficial del mar (TSM) en Niño 1+2 y, posteriormente, relacionar las anomalías de El Niño Costero con riesgos agroclimáticos y enfermedades del arándano y la vid.

La fase 6C utilizó ERSSTv5 publicado por CPC, pero esa descarga finalizaba en junio de 2026. La fase 6D encontró una descarga distinta del **mismo conjunto de datos ERSSTv5** en NOAA NCEI, actualizada hasta **2026-09**. La nueva serie requiere una **corrección explícita de la climatología** antes de ser comparable con el ICEN.

## Fuente y columnas de datos

- Anomalías ERSSTv5 de [NOAA NCEI](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat).
- [Readme de NOAA NCEI](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/Readme) confirma que las columnas son año, mes, Niño 3, Niño 4, Niño 3.4 y **Niño 1+2 en la sexta columna**, con anomalías calculadas frente a **1971–2000**.
- [NOAA CPC ERSSTv5 1991–2020](https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii), utilizado en Fase 6C y guardado como archivo histórico de comparación.
- Definición del ICEN por [IMARPE / ENFEN](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen): promedio móvil trimestral de anomalías Niño 1+2 basadas en ERSSTv5 y climatología 1991–2020. La publicación oficial y clasificación pertenecen a ENFEN.

**Nunca confundir la serie NOAA NCEI sin recalcular con la serie ICEN.**

## Método de conversión de referencia

Se convierte cada anomalía mensual NOAA NCEI basada en 1971–2000 a una anomalía referenciada a 1991–2020:

**Anomalía reajustada(mes) = anomalía original(mes) − promedio de anomalías originales del mismo mes calendario durante 1991–2020.**

El cálculo exige los 30 años completos por mes (enero de 1991, enero de 1992, …, enero de 2020, etc.) y rechaza duplicados o saltos de meses. Así evitamos tratar una diferencia en climatologías como un cambio físico del océano.

La transformación es **un cálculo independiente del OAF** sobre un archivo NOAA revisado; puede diferir ligeramente del CPC oficial por revisiones/ajustes de producto. No se atribuye al OAF la elaboración de ERSSTv5 original.

## Control cruzado con NOAA CPC

| Métrica | Resultado |
|---|---:|
| Último mes disponible NCEI | 2026-09 |
| Última anomalía mensual reajustada | +4.389 °C |
| Meses comunes con el archivo CPC anterior | 918 |
| Último mes comparable | 2026-06 |
| Diferencia absoluta media en toda la parte común | 0.0410 °C |
| Diferencia absoluta media últimos 24 meses comunes | 0.0397 °C |
| Máxima diferencia absoluta últimos 24 meses comunes | 0.1127 °C |

Los límites de plausibilidad preestablecidos para permitir exponer las estimaciones experimentales fueron: MAE de productos últimos 24 meses no superior a **0,4 °C** y diferencia absoluta máxima no superior a **0,75 °C**. Son **controles de coherencia permisivos, no pruebas de equivalencia metrológica ni de validación de pronósticos**. Se superaron.

## Predicción de anomalía oceánica a 1–3 meses

Se reutilizó el modelo AR(1) univariado de 6C, entrenado únicamente con meses anteriores a cada origen en una validación retrospectiva expansiva (*walk-forward*). Se comparó con la persistencia del último valor y la referencia de anomalía cero.

| Horizonte | Mes estimado | Estimación AR(1) | MAE histórico AR(1) | MAE histórico persistencia | MAE últimos 12 AR(1) | MAE últimos 12 persistencia |
|---|---|---:|---:|---:|---:|---:|
| 1 mes | 2026-10 | 4.054 °C | 0.3336 °C | 0.3375 °C | 0.5438 °C | 0.4404 °C |
| 2 meses | 2026-11 | 3.744 °C | 0.4869 °C | 0.5105 °C | 0.9647 °C | 0.8199 °C |
| 3 meses | 2026-12 | 3.456 °C | 0.6141 °C | 0.6670 °C | 1.2949 °C | 1.1619 °C |

El último valor observado reajustado fue 4.389 °C. Persistencia supondría ese mismo valor para cada uno de los tres horizontes.

**Resultado crucial:** el AR(1) tiene un error histórico ligeramente menor en el conjunto completo, pero **en los doce orígenes recientes evaluados su error es mayor a los tres horizontes**. Por ello el indicador `mejora_consistente_demostrada` está desactivado y **no se dispone de validación prospectiva**. Un gráfico de tendencia o una cifra calculada no demuestra que un pronóstico sea confiable.

No inferir a partir de esta serie la clasificación oficial del El Niño Costero, el riesgo de inundaciones, la severidad regional de sequías, ni la incidencia de plagas o enfermedades.

## Archivos del repositorio

- [Código y pruebas sintéticas Python](modelos/modelo_ncei_ersstv5_fase6d.py).
- [GitHub Actions de actualización mensual](.github/workflows/oaf_ncei_ersstv5_fase6d.yml).
- [Serie NCEI reajustada 1991–2020](datos/noaa_ncei_ersstv5_nino12_rebase_1991_2020.csv).
- [Predicciones retrospectivas de tres horizontes](datos/ncei_ersstv5_backtest_1a3m.csv).
- [Resumen de resultado y metadatos de procedencia](datos/modelo_ersstv5_ncei_6d.json).
- [Visor web del OAF](modelos/ncei_visor_6d.js).

## Siguientes pruebas necesarias

1. **Recopilar archivos de pronósticos emitidos realmente antes de cada mes**, para verificar sin sesgo de revisiones en origen o climatología reconstruida con información futura.
2. Comparar contra previsiones dinámicas y multimodelo de ENFEN y otros servicios especializados, con horizonte equivalente, evitando confundir productos oceánicos diferentes.
3. Añadir predictores de vientos, presión atmosférica y contenido térmico subsuperficial y evaluar si aportan habilidad adicional sobre persistencia.
4. Relacionar Niño 1+2 y las anomalías climáticas regionales de Lambayeque, pero **validar separadamente** la capacidad de pronosticar lluvias y temperaturas.
5. Conectar esa previsión a los modelos fitosanitarios de arándano y vid solo cuando las variables meteorológicas y los registros sanitarios de campo permitan validación independiente.

**Política permanente:** los resultados experimentales se publican con fuente, fecha, referencia climática, horizonte, error y estado de verificación. Nunca como alertas ENFEN, recomendaciones de tratamiento o probabilidades de enfermedad sin sustento.
