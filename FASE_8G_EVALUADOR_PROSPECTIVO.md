# Fase 8G — Evaluador automatizado de pronósticos agroclimáticos

**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque (OAF-Lambayeque).  
**Responsable:** Ing. Agrónomo Carlos Enrique Coronel García.  
**Implementación:** 16 de octubre de 2026.  
**Clasificación:** investigación y auditoría prospectiva experimental, **no** sistema de alerta validado.

## 1. Objetivo y estado real

La fase 8G implementa en Python una **auditoría reproducible de emisiones inmutables de la fase 8E**. Verifica que cada predicción esté fechada, coteja su valor contra el archivo original y calcula errores **únicamente** cuando el motor 8E ya archivó una verificación posterior con reanálisis ERA5-Land.

**Resultado inicial observado al implementar:**

- Emisiones originales: **1**, fechada el **15/10/2026 (hora Perú)**.
- Registros originales: **12** (4 localidades × 3 meses objetivo).
- **8 pronósticos emitidos antes de empezar el mes**: noviembre/diciembre 2026.
- **4 estimaciones intramensuales**: octubre 2026, emitidas cuando octubre ya había comenzado.
- Comparaciones disponibles con mes completamente maduro y reanálisis: **0**.
- MAE, RMSE, sesgo, ventaja relativa y cobertura de intervalos: **no evaluables**. Ningún número se inventa.
- Primera fecha programada para intentar verificar octubre: **10/11/2026**, condicionada a que la fuente publique todos los días del mes. Las primeras verificaciones **premes** posibles llegarían desde diciembre 2026 (noviembre como objetivo).

El informe electrónico se genera a partir del último corte **registrado por 8E**; no implica que se haya consultado ERA5-Land de nuevo desde el evaluador.

## 2. Fuentes y naturaleza de cada dato

1. **Emisiones 8E originales e inmutables:** `datos/pronosticos_temperatura_regional_8e/AAAA-MM.json`. Cada fila contiene emisión, localidad, horizonte, modelo local, modelo Niño1+2/T300, climatología fija y persistencia.
2. **Contraste posterior del motor 8E:** `datos/verificacion_temperatura_regional_8e.csv`; valores **ERA5-Land derivados de Open-Meteo**, distintos de observaciones instrumentales SENAMHI y sujetos a revisiones posteriores.
3. **Estado, fecha de corte y conteos:** `datos/verificacion_temperatura_regional_8e.json`; el evaluador exige que coincidan con las filas realmente publicadas.
4. **Bibliografía de los predictores oceánicos:** NOAA NCEI ERSSTv5 Niño1+2 y NOAA/PMEL GODAS T300, descritos en las fases 8D y 8E. No confundir estos indicadores con el ICEN oficial de ENFEN.

Fuentes institucionales de consulta:

- [Copernicus/ECMWF — ERA5-Land](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means?tab=overview), DOI [10.24381/cds.68d2bb30](https://doi.org/10.24381/cds.68d2bb30).
- [NOAA CPC — Series e índices oceánicos](https://www.cpc.ncep.noaa.gov/data/indices/).
- [OMM — Guidelines on the Verification of Hydrological Forecasts (2025, WMO-No. 1364)](https://public.wmo.int/media/news/wmo-issues-guidelines-verification-of-hydrological-forecasts): principio de comparar pronósticos con verificaciones, exponer sesgo, precisión y limitaciones. La guía se especializa en hidrología y **no sustituye** un protocolo local de evaluación térmica.

## 3. Indicadores del sistema

Sea `fᵢ` un pronóstico archivado y `yᵢ` la temperatura mensual de referencia posterior, para `n` casos comparables.

**Error con signo (°C):**

`eᵢ = fᵢ − yᵢ`.

**Error absoluto medio (MAE):**

`MAE = (1/n) Σ |eᵢ|`.

**Raíz del error cuadrático medio (RMSE):**

`RMSE = √[(1/n) Σ(eᵢ²)]`.

**Sesgo:**

`Sesgo = (1/n) Σ eᵢ` (positivo: sobreestimación media; negativo: subestimación).

**Mejora de MAE al añadir Niño1+2/T300 respecto al modelo local:**

`100 × (1 − MAE_oceánico / MAE_local)`.

El cálculo es **nulo** si falta alguna observación del grupo o el denominador de comparación es cero.

Se computan los mismos índices para cuatro alternativas: Ridge **solo local**, Ridge **local+Niño1+2+T300**, **climatología fija de entrenamiento** y **persistencia**. Sus parámetros **no se recalibran** en 8G. Se calculan resultados separados por **localidad**, **horizonte 1/2/3**, **tipo de emisión** y totales descriptivos. Los totales combinados pueden tener dependencia temporal/espacial, por lo que no implican muestras estadísticamente independientes.

**Intervalos del 90 %:** 8E no archivó intervalos predictivos calibrados antes de emitir; por eso `intervalo_90_cobertura=null` y `n_intervalos_90_calibrados=0`. No se inventan bandas ni probabilidades a posteriori.

## 4. Reglas de admisión y prevención de fuga temporal

El programa `modelos/evaluador_prospectivo_8g.py` controla:

- Hora de emisión original **con zona horaria** y anterior o igual al corte del informe 8E.
- Mes objetivo = mes de origen + horizonte, localidad válida y emisión no duplicada.
- Clasificación temporal **real** tomando la fecha en `America/Lima` y el comienzo del mes objetivo, no una etiqueta arbitraria.
- Una observación de contraste solo es admisible desde el **día 10 del mes siguiente** al mes objetivo.
- Predicción reflejada en CSV **idéntica** (salvo precisión de redondeo) a la emisión inmutable. Comprueba también que el error sea la resta original menos contraste.
- No se acepta comparación duplicada, objetivo sin emisión, registros sin valor, dato no finito o conteos inconsistentes con el informe 8E.
- Nunca copia las estimaciones **intramensuales** al total de pronósticos **antes del mes**.
- Nunca confunde ERA5-Land con un termómetro SENAMHI o sensores intraparcelarios.
- Ni siquiera un MAE menor declara `habilidad_prospectiva_demostrada=true`: esto requeriría años comparables, incertidumbre, pruebas formales y validación independiente.

**Límite explícito:** el motor 8G audita lo publicado por 8E, no realiza una nueva consulta independiente al proveedor ni certifica instrumentalmente la verdad del reanálisis. Su integridad temporal depende también del riguroso control de días completos que ya realiza 8E.

## 5. Archivos producidos

- [Código fuente del evaluador](modelos/evaluador_prospectivo_8g.py).
- [Pruebas sintéticas aisladas](tests/test_evaluador_prospectivo_8g.py): fechas prematuras, modificaciones, duplicados, distinción intramensual/premes, muestras sin datos y casos sintéticos con resultados conocidos. **Las pruebas inventan valores solo en directorios temporales y nunca los publican como evidencia real.**
- [JSON de indicadores](datos/evaluacion_prospectiva_8g/metricas_8g.json): métricas y tamaños muestrales, cortes, estados de validez y SHA-256 de entradas y emisiones.
- [CSV por pronóstico](datos/evaluacion_prospectiva_8g/detalle_8g.csv): doce filas iniciales con predicción, estado de comprobación, fecha mínima, y celdas vacías para observación y error todavía no disponibles.
- [Panel público](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#verificaciones): acordeón «Fase 8G» dentro de **Verificación de datos**, con filtros, tabla y gráfico que solo se genera cuando hay datos reales contrastados.
- [Flujo de GitHub Actions](.github/workflows/oaf_evaluador_8g.yml): ejecuta pruebas y actualiza únicamente salidas derivadas los días **13, 20 y 27 de cada mes**, después de los intentos programados por 8E los días 12, 19 y 26.

El evaluador **no sobrescribe las emisiones originales ni ajusta los modelos**. Si la entrada no cambia, la salida permanece idéntica para evitar commits irrelevantes.

## 6. Cómo reproducirlo

Desde la raíz del repositorio, con Python 3.11:

```bash
python -m unittest discover -s tests -p 'test_evaluador_prospectivo_8g.py' -v
python modelos/evaluador_prospectivo_8g.py --run
python modelos/evaluador_prospectivo_8g.py --check
```

Los CSV y JSON se actualizan únicamente si cambian los contrastes válidos o su estado documental.

## 7. Siguiente fase científica

**8H — Auditoría de confiabilidad ampliada y preparación de validación independiente**. Priorizar series completas de estaciones SENAMHI comparables con los puntos de estudio, diferencias espaciales/reanálisis–instrumentos, corrección por dependencia temporal y determinación prospectiva y anterior al evento de bandas de incertidumbre basadas exclusivamente en errores históricos fuera de muestra. Mantener como línea separada la calibración agronómica y fitosanitaria con datos reales de arándano y vid.

No inferir, a partir de la predicción térmica, infecciones ni alertas de El Niño Costero sin validación adicional y fuentes oficiales.
