# OAF-Lambayeque — Diagnóstico estacional de errores (Fase 3P)

**Cálculo a partir de la validación multianual 3O**, sin realizar descargas ni inventar observaciones. Fecha: 14/10/2026.

## Por qué se calculó

Comprobar si las sobreestimaciones de ERA5-Seamless se limitan al evento extremo de **1998** o también aparecen en otros años; dividir el calendario en **enero–abril** y **mayo–diciembre**, sin afirmar que sean periodos pluviométricos universales en todos los pisos altitudinales.

Se utilizaron **2 218 pares mensuales** de datos originales ya registrados en `datos/comparacion_3o_multianual.csv`. Los estratos son: todos, solo 1998, y sin 1998. No se añaden ni se imputan meses SENAMHI ausentes. Son coordenadas provisionales y no es validación independiente de PISCOp.

## Enero–abril, excluyendo completamente 1998

| Estación | Meses emparejados por producto | MAE PISCOp (mm/mes) | MAE ERA5-Seamless (mm/mes) | Sesgo porcentual PISCOp | Sesgo porcentual ERA5 |
|---|---:|---:|---:|---:|---:|
| Jayanca (La Viña) | 71 | 6.1 | 188.7 | -22.6 % | 955.2 % |
| Cayaltí | 75 | 2.76 | 33.11 | 11.6 % | 404.8 % |
| Reque | 74 | 1.84 | 13.34 | 12.1 % | 282.5 % |
| Lambayeque | 67 | 1.8 | 15.91 | -9.3 % | 261 % |
| Cueva Blanca | 69 | 42.37 | 239.53 | -30.6 % | 217.4 % |

**Hallazgo verificable:** incluso al retirar **1998** por completo, ERA5-Seamless mantiene sobreestimaciones positivas en el estrato de **enero–abril** para las cinco estaciones de la muestra. La magnitud del sesgo porcentual varía mucho según el régimen pluviométrico; los porcentajes con acumulados instrumentales bajos pueden resultar muy grandes y NO equivalen a la diferencia típica mensual.

## Método

- MAE mensual = media de `abs(estimado - observado)` en los meses emparejados.
- RMSE mensual = raíz de la media de los cuadrados de los errores mensuales.
- Sesgo acumulado (%) = 100 × (suma de estimaciones - suma de observaciones) / suma de observaciones del mismo estrato.
- El estrato `sin_1998` excluye las observaciones de todos los meses de 1998 en ambos productos.
- Los periodos `ene_abr` y `may_dic` son divisiones de calendario para un examen diagnóstico; no se trata de una clasificación agroclimática local validada.
- El CSV adjunto contiene **60 filas** (5 estaciones × 2 productos × 3 estratos × 2 periodos), cada una con cobertura, sumas, sesgo, MAE y RMSE.

## Lectura prudente

No se ha establecido que la selección de celda sea la causa de la diferencia: por ahora esta auditoría solo demuestra que el sesgo se mantiene fuera del año extremo. La causa física y espacial se evalúa en la auditoría de modelos de la fase 3P. Una buena concordancia de PISCOp con pluviómetros potencialmente incluidos en su construcción no demuestra habilidad predictiva en parcelas sin estaciones.

**Procedencia:** `datos/comparacion_3o_multianual.csv` publicado en este mismo repositorio. Véase también `VALIDACION_3O.md` y `METADATOS_GEOGRAFICOS_3P.md`.
