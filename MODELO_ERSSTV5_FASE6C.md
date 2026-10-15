# OAF-Lambayeque — Fase 6C: ERSSTv5 Niño 1+2 y validación de modelos a 1–3 meses

**Fecha:** 14/10/2026, hora peruana; los archivos de GitHub Actions se procesaron el 15/10/2026 UTC.  
**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Estado:** investigación histórica reproducible, **NO pronóstico operativo ni índice ICEN oficial**.

## 1. Propósito científico

El objetivo del OAF es anticipar tanto anomalías climáticas, especialmente las relacionadas con El Niño Costero, como condiciones de riesgo fitosanitario en arándano y vid. La Fase 6C estudia si un modelo univariado **AR(1)** puede anticipar anomalías mensuales en la región oceánica Niño 1+2, y si mejora la predicción ingenua de **persistencia** a horizontes de 1, 2 y 3 meses.

## 2. Fuentes verificadas y vigencia

1. **NOAA CPC ERSSTv5 Niño 1+2** (anomalías base 1991–2020): https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii
2. **Producto NOAA CPC OISST v2.1**, incluido en la fase 6B: https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices
3. **Definición institucional de ICEN:** https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen
4. **Definición y avisos:** https://enfen.imarpe.gob.pe/notas-tecnicas/
5. **Informe SENAMHI–ENFEN 06-2026** para contraste documental: https://www.gob.pe/institucion/senamhi/informes-publicaciones/8419259-informe-tecnico-senamhi-enfen-n-06-2026

La fuente NOAA ERSSTv5 disponible en esta ejecución **termina en 2026-06**: tiene **4 meses de retraso** a octubre de 2026. El sistema dejó `prediccion_actual_disponible=false` y anuló las estimaciones prospectivas, manteniendo solo resultados históricos y métricas de evaluación. **No se publica pronóstico de julio, agosto o septiembre como si fuera un pronóstico vigente de octubre o de los meses siguientes.**

NOAA OISST sí contiene meses posteriores, pero **no sustituye a ERSSTv5 ni al ICEN institucional**. La diferencia media absoluta entre anomalías OISST y ERSSTv5 durante los **534 meses comunes** fue **0.2171 °C**. Esta cifra describe *diferencia entre productos*, NO error de pronóstico ni precisión instrumental.

## 3. Reproducción matemática ilustrativa del promedio trimestral

Se calcula una media móvil centrada en el segundo de tres meses consecutivos de anomalías **ERSSTv5 Niño 1+2** (base 1991–2020). Esta operación aproxima el componente matemático básico del ICEN, **pero no reproduce necesariamente toda la metodología y proceso de publicación del ENFEN**.

**Control documental puntual:** el promedio ilustrativo centrado en **2026-05** es **+1.983 °C**. El informe SENAMHI–ENFEN N.º 06-2026, de 21/07/2026, reporta **ICEN centrado en mayo 2026 = +1,98 °C** y anomalía mensual de junio **+2,82 °C**. Nuestro archivo ERSSTv5 registra para junio **+2.82 °C**. La coincidencia a dos decimales en este punto es un control favorable de transcripción/cálculo, **no validación integral de la serie, umbrales o pronósticos**.

## 4. Modelos y protocolo

- Persistencia a h meses: anomalía prevista y(t+h) = y(t).
- Modelo AR(1) ajustado mediante mínimos cuadrados con los datos disponibles al origen t: y(t+1) = a + b × y(t), iterado h veces.
- Climatología cero: y(t+h) = 0, como referencia secundaria.
- Evaluación **expanding-window walk-forward**, con orígenes desde enero de 2010, y serie NOAA actualizada. Para cada origen, se entrenó solo con meses anteriores a ese objetivo.
- Métricas: MAE y RMSE (°C), mejora relativa del MAE frente a persistencia, métrica de los 12 meses más recientes y remuestreo de errores emparejados en bloques móviles de 12 meses.
- Los registros más recientes pueden cambiar si NOAA revisa sus datos. El backtest con la versión histórica disponible **no equivale a tener instantáneas archivadas en tiempo real**.

## 5. Resultados históricos de ERSSTv5

| Horizonte | Folds | MAE AR(1) | MAE persistencia | Mejora relativa global | MAE AR(1), últimos 12 | MAE persistencia, últimos 12 |
|---|---:|---:|---:|---:|---:|---:|
| 1 mes | 197 | 0.3449 °C | 0.3546 °C | 2.74 % | 0.4230 °C | 0.3875 °C |
| 2 meses | 196 | 0.4952 °C | 0.5282 °C | 6.25 % | 0.6574 °C | 0.6208 °C |
| 3 meses | 195 | 0.6183 °C | 0.6823 °C | 9.38 % | 0.7898 °C | 0.7917 °C |

A uno y dos meses, el modelo AR(1) fue **peor** que persistencia durante los últimos doce meses evaluados. A tres meses, la mejora reciente fue de solo **0.24 %**, demasiado marginal para declarar una ventaja confiable. Aunque las mejoras globales son positivas, **ningún horizonte dispone todavía de validación prospectiva ni demuestra capacidad predictiva operativa**.

## 6. Implementación, control y transparencia

- Script: [modelos/modelo_ersstv5_nino12_fase6c.py](modelos/modelo_ersstv5_nino12_fase6c.py)
- Actualización mensual: [.github/workflows/oaf_ersstv5_fase6c.yml](.github/workflows/oaf_ersstv5_fase6c.yml)
- Serie ERSSTv5: [datos/noaa_ersstv5_nino12_mensual.csv](datos/noaa_ersstv5_nino12_mensual.csv)
- Promedios trimestrales **indicativos**: [datos/nino12_ersstv5_promedio_trimestral_experimental.csv](datos/nino12_ersstv5_promedio_trimestral_experimental.csv)
- Predicciones retrospectivas: [datos/ersstv5_nino12_walkforward_1a3m.csv](datos/ersstv5_nino12_walkforward_1a3m.csv)
- Resumen auditable: [datos/modelo_ersstv5_nino12_6c.json](datos/modelo_ersstv5_nino12_6c.json)
- Visor web con bloqueo de pronósticos desactualizados: [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino)

Los scripts se ejecutaron correctamente en GitHub Actions tras ajustar el control de vigencia: primero el sistema **rechazó** publicar un pronóstico con fuente desactualizada; después el sistema **aceptó publicar únicamente el análisis histórico** y dejó bloqueadas las proyecciones vigentes.

## 7. Próxima fase sugerida: 6D

1. Investigar una **fuente actualizada y archivada** del mismo producto ERSSTv5 o datos institucionales recientes ICEN con licencia y trazabilidad. Mientras no exista, no reconstruir un ICEN «actual» con OISST.
2. Contrastar la serie indicativa del promedio trimestral con **múltiples** valores institucionales, no solo mayo 2026, para estudiar diferencias y revisiones.
3. Comparar con NOAA ERSSTv6 (si dispone de series actualizadas), **etiquetándolo como un producto distinto**.
4. Implementar evaluaciones prospectivas de modelos a horizontes 1–3 meses, contrastando persistencia y pronósticos oceánico-atmosféricos dinámicos.
5. Relacionar las señales Niño 1+2 con datos regionales de Lambayeque mediante estadística válida; solo después trasladarlas a modelos de riesgo fitosanitario de arándano y vid.

**Regla científica:** ninguna anomalía oceánica mensual, promedio ilustrativo ni predicción AR(1) sustituye un pronóstico ENFEN, demuestra presencia de enfermedad o constituye una alerta OAF operativa.
