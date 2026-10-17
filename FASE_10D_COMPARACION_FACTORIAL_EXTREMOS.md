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

## Criterio de paso a fase 10E
La siguiente etapa deberá validar científicamente el tratamiento de extremos con umbrales hidrometeorológicos contextualizados por sector, incorporar datos instrumentales externos, formar un registro real de emisiones con fecha, y explorar modelos de clasificación extremo/normal con validación temporal-espacial estricta. Mantener **cero alertas automáticas** mientras falten pruebas operativas y de campo.
