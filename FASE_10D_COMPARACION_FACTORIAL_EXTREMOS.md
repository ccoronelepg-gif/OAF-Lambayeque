# Fase 10D — Comparación factorial controlada de rezagos y sensibilidad a lluvias extremas

**Proyecto:** OAF-Lambayeque · **Fecha:** 17/10/2026 · **Estado:** experimento auditable, sin permisos de alerta.

## Pregunta, diseño y contraste
En 9X frente a 10C, al retirar la precipitación del mes t−1 también se modificó el periodo de selección de hiperparámetros; el contraste inicial no permitía atribuir causalmente toda la diferencia de MAE a los rezagos.

**10D reentrena ambos brazos bajo un protocolo idéntico en una sola ejecución:**

- **Brazo L1:** CHIRPS mensual t−1, t−2, t−3, t−6 y t−12 + media t−1:t−3.
- **Brazo L2:** CHIRPS mensual t−2, t−3, t−4, t−6 y t−12 + media t−2:t−4.
- **Entrenamiento:** 1997–2015. **Selección / parada anticipada:** 2016–2018.
- **Calibración independiente de umbrales:** 2019–2020.
- **Prueba estricta posterior:** 2021–2025.
- **Espacio:** 39 sectores preliminares y cinco bloques reservados, SIN incluir etiquetas objetivo de sectores reservados en el ajuste GCN/RF. Se permite su precipitación histórica rezagada para inferencia.
- **Modelos:** Random Forest, Graph Convolutional Network (GCN) y climatología por piso exploratorio; mismos predictores exógenos, grafo, candidatos de hiperparámetros, semilla y partición.
- **Estimando:** cambio de MAE emparejado `L2 − L1` en los mismos sectores y meses (menor que cero favorece a L2), por modelo, año, piso y régimen climático retrospectivo. Intervalos *exploratorios* mediante 3.125 combinaciones de cinco bloques espaciales.

## Evaluación específica de eventos extremos
El umbral observado se examina separadamente para **50, 100 y 150 mm/mes** (exploratorios, NO oficiales). Se publica matriz de confusión (TP, FP, FN, TN), sensibilidad, precisión, índice CSI, F2 y tasa de falsas alarmas. El error medio en mm NO sustituye la habilidad para detectar eventos extremos.

Se contrastan dos reglas:
1. **Regla puntual original:** evento señalado cuando el pronóstico de lluvia alcanza el mismo umbral.
2. **Regla reajustada solo en calibración 2019–2020:** elegir en una cuadrícula de cortes de 0–200 mm cada 5 mm el mayor F2 con tasa de falsos positivos de calibración <=25 %. Solo se admite con **10 o más eventos de calibración**. Si no, `INSUFICIENTES_EVENTOS_CALIBRACION`; no se informa falsa exactitud. Se informa la tasa real de falsas alarmas de prueba, que puede superar el 25 % de calibración.

Las reglas calibradas se evalúan sobre 2021–2025 **sin reoptimizar** usando información del periodo de prueba. La calibración por sectores de prueba no representa extrapolación a una localidad desconocida sin historia local.

## Estratificación retrospectiva por NOAA
Se anexa un extracto auditado del [índice RONI (CPC/NOAA; ERSSTv6)](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/) de 2021–2025, asociado al **mes central** de cada temporada DJF/…/NDJ. Valores >=+0,5, <=−0,5 y entre ambos se utilizan como **estratos descriptivos** cálido, frío y neutro; NO constituyen la clasificación oficial de episodios de Niño costero ni reemplazan los comunicados ENFEN. Los valores RONI históricos pueden revisarse. Al ser una media **centrada**, RONI **no se incluye como predictor en emisión**: introducirla en el modelo sería fuga de información temporal.

## Disponibilidad y límites
El [Climate Hazards Center de UCSB](https://www.chc.ucsb.edu/data/chirps3) documenta que CHIRPS v3 FINAL generalmente se publica durante la tercera semana del mes siguiente; su historia CHIRPS v3 FINAL está retroprocesada. Ambas ramas de 10D utilizan CHIRPS v3 FINAL histórico compilado después de las fechas evaluadas, no **vintages as-issued**. El brazo L1 t−1 no constituye un predictor operacional disponible al comenzar el mes. El contraste es un experimento retrospectivo y no acredita pronósticos operativos.

- No se han certificado pisos altitudinales homogéneos ni resuelto la cota negativa.
- CHIRPS incorpora estaciones; no existe validación instrumental independiente ni evaluación prospectiva en 2026.
- GCN no equivale a CNN bidimensional de imágenes.
- Cinco bloques no aseguran independencia espacial ni intervalos de confianza confirmatorios.
- La sensibilidad y F2 de umbrales exploratorios no autorizan alertas agroclimáticas, ENSO ni de enfermedades de arándano/vid.

## Artefactos
[Comparador interactivo](evaluacion-extremos.html) · [Python controlado](modelos/experimento_factorial_10d.py) · [Pruebas de integridad](tests/test_factorial_10d.py) · [RONI fuente NOAA](datos/experimentos_10d/roni_noaa_2021_2025.json) · [Predicciones de ambos brazos](datos/experimentos_10d/predicciones_factorial_10d.csv) · [Métricas y matrices de confusión](datos/experimentos_10d/evaluacion_controlada_10d.json) · [GitHub Actions](.github/workflows/oaf_10d_factorial.yml).

## Resultados ejecutados y verificaciones (GitHub Actions)

La [corrida 10D](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39080924683) completó **ocho pruebas unitarias**, entrenó ambos brazos de RF y GCN, verificó matrices emparejadas, SHA, ausencia de alertas y publicó **5.616 registros de calibración** y **14.040 registros de prueba** (39 sectores × [24+60] meses × tres modelos × dos brazos).

### Error histórico bajo el mismo periodo de ajuste

| Modelo | MAE L1 (mm) | MAE L2 (mm) | Cambio L2−L1 (mm) |
|---|---:|---:|---:|
| Random Forest | 17,0241 | 18,1443 | +1,1202 |
| GCN | 18,7739 | 17,6452 | −1,1287 |
| Climatología por piso | 20,3708 | 20,3708 | 0,0000 |

El **bootstrap exploratorio igualmente ponderado por cinco bloques** obtiene para `MAE L2−L1`:
- Random Forest **+0,9766 mm**, rango exploratorio 95 % **[+0,4137; +1,4447] mm**.
- GCN **−0,7592 mm**, rango exploratorio 95 % **[−2,7164; +0,8257] mm**. Incluye cero, por lo que no se confirma ventaja generalizable en todos los bloques.

### Umbral exploratorio de precipitación mensual ≥100 mm
En los **2.340 pares sector-mes de prueba** se observaron **137 pares con lluvia ≥100 mm**. Los siguientes resultados usan solo el brazo L2:

| Modelo | Regla de pronóstico puntual ≥100 mm: TP/FN/FP | Corte calibrado 2019–2020 (mm) | Regla calibrada: TP/FN/FP | Sensibilidad calibrada | Precisión calibrada |
|---|---|---:|---|---:|---:|
| Random Forest | 13 / 124 / 22 | 30 | 113 / 24 / 205 | 82,48 % | 35,53 % |
| GCN | 32 / 105 / 28 | 20 | 123 / 14 / 438 | 89,78 % | 21,93 % |
| Climatología por piso | 34 / 103 / 36 | 45 | 106 / 31 / 314 | 77,37 % | 25,24 % |

**No ocultar falsas alarmas:** la sensibilidad mayor de GCN requiere 438 falsas alarmas a escala sector-mes. Un criterio F2 premia la sensibilidad y puede ser inadecuado para avisos costosos al agricultor. Ningún corte calibrado es un umbral oficial fitosanitario o hidrometeorológico.

### Análisis altitudinal y oceánico
La GCN con rezagos L2 tiene MAE de **4,24 mm** en llanura costera, **14,32 mm** en piedemonte, **30,09 mm** en montaña media y **38,45 mm** en montaña alta. En montaña media la climatología por piso obtuvo **25,39 mm**, de modo que NO se recomienda extrapolar el menor MAE global de GCN como una mejora en todo piso.

Estratificación RONI retrospectiva para GCN L2: **14,73 mm** (RONI cálido, n=312), **17,11 mm** (frío, n=1.677) y **22,80 mm** (neutro, n=351). Estas diferencias descriptivas están afectadas por periodos, composición de sectores y régimen meteorológico; **no prueban que el índice RONI cause cambios en el error**, ni equivalen a validación de El Niño costero.

**Resultado metodológico:** ahora sí es posible aislar el efecto de cambiar la configuración de rezagos bajo el mismo protocolo de entrenamiento y validación *retrospectivo*. Persisten las restricciones por ausencia de datos CHIRPS as-issued y contraste de estaciones independientes. El estado permanece **experimental**, con **cero alertas y cero modelos operativos certificados**.

## Criterio de paso a fase 10E
La siguiente etapa deberá validar científicamente el tratamiento de extremos con umbrales hidrometeorológicos contextualizados por sector, incorporar datos instrumentales externos, formar un registro real de emisiones con fecha, y explorar modelos de clasificación extremo/normal con validación temporal-espacial estricta. Mantener **cero alertas automáticas** mientras falten pruebas operativas y de campo.
