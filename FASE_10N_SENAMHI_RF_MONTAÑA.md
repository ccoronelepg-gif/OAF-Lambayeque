# Fase 10N — Integración de los CSV SENAMHI y entrenamiento RF experimental

**18 de octubre de 2026 · OAF-Lambayeque · datos terrestres sin control instrumental formal.**

## Integración de base de datos

Se confirmaron las huellas SHA-256 de los **16 CSV más recientes, table (50)–(65).csv**, todos de **Cueva Blanca (código 153102)**, contra el manifiesto de fuente del consolidado SENAMHI 10M. La base **SQLite 10N descargable** contiene la integración 10M de **13 estaciones**, **1.386 registros diarios únicos**, **1.208 horarios únicos**, 303 claves duplicadas idénticas de estación-fecha/resolución (362 copias extra no repetidas en el consolidado), **cero valores de lluvia contradictorios**.

De las estaciones de alta montaña, SENAMHI/DRD aporta **40 meses con días completos y lluvia numérica**. La serie es *discontinua* — no equivale a 40 meses consecutivos:

| Estación | Código | Altitud | Sector 9K experimental (intersección punto-polígono) | Meses completos |
|---|---|---:|---|---:|
| **Incahuasi** | `000307` | 3.052 m | **S007**, montaña alta | **14** |
| **Cueva Blanca** | `153102` | 3.300 m | **S008**, montaña alta | **26** |

La geometría de S007/S008 procede del mapa de sectores experimental OAF-9K y **no es delimitación oficial de ecorregión**. Coordenadas calculadas a partir de la cabecera DMS de los archivos: Incahuasi lat. −6.233889, lon. −79.318056; Cueva Blanca lat. −6.131300, lon. −79.404500.

Archivos canónicos de investigación: `datos/senamhi_10n/meses_pluviometricos_completos_10n.csv` (40 meses). Los registros diarios completos, horarios, manifiestos de SHA, pérdidas de hora y conflictos se incluyen en el **paquete SQLite/ZIP entregado al usuario**; no se está afirmando certificación SENAMHI.

## Entrenamiento nuevo — objetivo exclusivamente precipitación

Se entrenó **RandomForestRegressor**, pero **como corrector de medición puntual terrestre frente a una normal sectorial CHIRPS 1997–2015**, no como sustituto del RF territorial 10L ni como modelo fitosanitario.

Predictores conocidos antes del mes objetivo: mes sin/cos, climatología mensual CHIRPS histórica del sector S007/S008, altitud, identificadores de sector. **No se introdujo la lluvia observada del propio mes objetivo** ni fuentes futuras como variables explicativas.

Separación temporal:

- **Entrenamiento 2021–2024:** 17 meses-terrestres.
- **Validación 2025:** 15 meses-terrestres, para elegir entre RF de varias profundidades/hojas y peso de corrección [0;0,25;0,5;0,75;1].
- **Prueba 2026:** 8 meses-terrestres, reservados fuera del entrenamiento y validación.

Una vez escogidos hiperparámetros, se reentrenó el candidato con 2021–2025 y se verificó frente a los 8 meses de 2026. **La prueba de 2026 es retrospectiva:** no existe copia fechada de emisiones `as-issued`.

| Evaluación | MAE candidato RF | MAE normal CHIRPS del sector |
|---|---:|---:|
| **Validación 2025 (15)** | 55,9538 mm | 55,9538 mm |
| **Prueba 2026 (8)** | 63,5568 mm | 63,5568 mm |
| Incahuasi 2026 (4) | 68,5157 mm | 68,5157 mm |
| Cueva Blanca 2026 (4) | 58,5979 mm | 58,5979 mm |

**Resultado:** la validación seleccionó `peso_RF = 0`. Los árboles fueron entrenados y conservados como artefacto, pero **el ajuste RF no mejoró el error y la salida queda igual a climatología**. No se debe declarar mayor exactitud ni actualizar el pronóstico regional. Tampoco se justifica reportar «RF entrenado con 40 nuevos meses» como una validación robusta: solo 32 fueron usados en entrenamiento/ajuste y 8 quedaron para prueba.

## Advertencias que restringen la publicación

- Los archivos SENAMHI aportados indican expresamente **«Datos sin control de calidad»**. La completitud diaria de un mes no equivale a calibración instrumental ni validación oficial.
- Un pluviómetro mide precipitación **puntual**, mientras la climatología CHIRPS usada como referencia representa un **promedio espacial del sector experimental**.
- CHIRPS puede incorporar pluviómetros en su generación; no hemos comprobado si alguno de estos dos fue utilizado para construir la serie satelital del producto.
- Sólo dos estaciones de alta montaña en zonas S007/S008; no constituyen validación representativa de las demás cumbres o vertientes medias.
- 17 registros iniciales, meses no contiguos y 8 registros de prueba 2026 no permiten afirmar habilidad significativa.
- La familia principal del OAF continúa siendo Random Forest de precipitación; el futuro modelado de enfermedades requiere **otro algoritmo y evaluaciones reales de campo**. El ajuste 10N no predice horas de hoja mojada ni enfermedades.

## Entregables verificables

- [CSV de 40 meses completos y localización 9K](datos/senamhi_10n/meses_pluviometricos_completos_10n.csv)
- [Código de entrenamiento de corrector RF de estación](modelos/entrenar_rf_estaciones_senamhi_10n.py)
- [Métricas de entrenamiento y prueba](datos/senamhi_10n/evaluacion_rf_estacion_10n.json)
- [Predicciones comparativas mensuales](datos/senamhi_10n/evaluacion_mensual_rf_estacion_10n.csv)
- [Visor de estaciones y evaluación](verificacion-estaciones-senamhi-10n.html)
- [GitHub Actions de entrenamiento](.github/workflows/oaf_10n_senamhi_rf.yml)
- [Dashboard regional de montaña 10L](optimizacion-lluvia-montana-10l.html)

El siguiente paso, **antes de promover un algoritmo mejorado**, es obtener más años/estaciones de montaña, QC instrumental y correspondencia exacta pluviómetro–CHIRPS, continuar dejando algunas estaciones fuera del entrenamiento y conservar el mecanismo de prueba `as-issued`. 
