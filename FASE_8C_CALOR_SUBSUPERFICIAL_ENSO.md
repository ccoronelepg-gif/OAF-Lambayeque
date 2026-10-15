# OAF-Lambayeque · Fase 8C: T300 del Pacífico ecuatorial y predictores atmosféricos retrasados

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Ejecución con datos reales:** 15/10/2026 UTC.  
**Estado:** investigación retrospectiva; **no es predicción prospectiva validada, ICEN oficial ni alerta ENFEN**.

## 1. Objetivo científico y pregunta de trabajo

La Fase 8B demostró que agregar contemporáneamente SOI y vientos del Pacífico al modelo lineal de temperatura superficial del mar (TSM) Niño 1+2 **empeoraba** su desempeño. Una hipótesis física alternativa es que la **energía térmica de los primeros 300 metros del Pacífico** y el desfase de los índices atmosféricos puedan aportar información sobre la evolución posterior de la TSM. Esta fase no presupone que funcionen: pone a prueba tres modelos definidos de antemano y conserva sus errores.

El OAF persigue por separado: (a) predecir anomalías y estudiar El Niño Costero y sus repercusiones agroclimáticas en Lambayeque, y (b) desarrollar modelos fitosanitarios de arándano y vid basados en **datos reales de campo**, pendientes de recopilación. El indicador atmosférico para Botrytis no es aún un pronóstico validado de enfermedad.

## 2. Fuente científica nueva: NOAA/PMEL T300

[NOAA/PMEL, Upper Ocean Heat Content and ENSO](https://www.pmel.noaa.gov/elnino/upper-ocean-heat-content-and-enso/) explica el papel del intercambio térmico subsuperficial en la dinámica ENSO; el centro publica **T300**, temperatura media de los primeros **0–300 m** en una franja **5°N–5°S, 120°E–80°O**, reconstruida con el sistema oceánico **GODAS** y reportada en anomalías respecto a **1981–2010**.

**Archivo original verificado:** [NOAA/PMEL t300.dat](https://www.pmel.noaa.gov/tao/wwv/data/t300.dat); columnas `AAAAMM`, temperatura media 0–300 m en °C y anomalía T300 en °C. El código comprueba meses únicos y consecutivos desde 1980-01, magnitudes admisibles, notación científica con valores negativos y límites de cobertura.

**Último dato real disponible en esta ejecución:** **2026-08**, con una anomalía T300 de **+1,320 °C** en los primeros 300 metros. **Esto no es la temperatura superficial ni una medición del litoral peruano**; tampoco implica por sí solo una categoría de El Niño Costero.

Los objetivos siguen siendo las anomalías mensuales de TSM Niño 1+2 **NOAA NCEI ERSSTv5**, con referencia 1991–2020 reconstruida por el OAF. **Las bases de referencia 1981–2010 (T300) y 1991–2020 (TSM) son distintas**; no deben restarse ni interpretarse como valores intercambiables. Sus unidades son °C pero representan fenómenos y regiones diferentes. El ICEN institucional corresponde únicamente a ENFEN según su [Nota Técnica 01-2024](https://enfen.imarpe.gob.pe/notas-tecnicas/) e información oficial [IMARPE/SIOFEN](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen).

## 3. Diseño temporal y modelos predefinidos

**Objetivo:** anomalía ERSSTv5 Niño 1+2 a horizontes de 1, 2 o 3 meses, evaluada contra tres variantes entrenadas de manera idéntica.

**Modelos:**

- **A. Persistencia:** anomalía mensual de TSM Niño 1+2 en mes de origen t, sin corrección.
- **B. TSM + tendencia:** regresión Ridge con SST del mes t y t−1. Misma regularización fija `alpha = 20`, intercepto no penalizado.
- **C. TSM + tendencia + T300:** misma regresión más anomalía GODAS T300 del **mes t−1** (no del mes t).
- **D. TSM + tendencia + T300 + atmósfera:** como C, más SOI y anomalías del viento a 850 hPa de NOAA CPC Pacífico central y oriental del **mes t−1**, correspondientes a la Fase 8B.

**Corte independiente y congelado para todos los horizontes:** entrenamiento solamente con ejemplos cuyo **mes de resultado conocido sea hasta diciembre de 2022**. Se fijan medias, escalas y coeficientes antes de examinar el conjunto **de enero de 2023 en adelante**, sin volver a entrenar con las etiquetas del periodo de prueba. Los horizontes h=2/3 requieren especialmente separar por **mes objetivo** y no únicamente por mes de predictores, para impedir que se incluyan etiquetas posteriores a 2022.

**Muestras comparables:** todos los modelos se evalúan en el mismo conjunto de fechas con TSM y T300 t−1, SOI y vientos t−1 completos, más objetivo t+h realmente observado. No se rellenan nulos con ceros y no se utiliza información futura en las columnas predictoras con fecha posterior a t.

**Precaución de disponibilidad real:** el que una variable se asigne al mes t **no implica que estuviera publicada antes del día 1 del mes t+1**. Aunque T300, SOI y vientos usan t−1, la TSM del mes t normalmente necesita procesamiento tras el cierre mensual. En consecuencia, una proyección a horizonte uno realizada tras ese cierre puede ser una **estimación intramensual del mes t+1**. Estas pruebas históricas tampoco conservan versiones *vintage* de lo que NOAA efectivamente publicaba en cada fecha pasada. El control de emisión real permanece en la **Fase 8A** y sus archivos con hora UTC.

## 4. Resultado del experimento independiente con NOAA real

El workflow GitHub Actions concluyó sus autopruebas, descarga PMEL y ensayo estadístico **sin errores**.

| Horizonte | Ejemplos entrenamiento | Meses prueba 2023–2026 | MAE persistencia (°C) | MAE TSM+tendencia (°C) | MAE TSM+T300 (°C) | MAE TSM+T300+atmósfera (°C) | Mejora T300 vs tendencia | Intervalo exploratorio de mejora 95 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 514 | 44 | 0.4378 | 0.4500 | 0.4168 | 0.4917 | 7.38 % | -4.75 % a 12.63 % |
| 2 | 513 | 43 | 0.7132 | 0.6951 | 0.6519 | 0.7782 | 6.21 % | -7.19 % a 10.31 % |
| 3 | 512 | 42 | 0.9280 | 0.8780 | 0.8285 | 0.9345 | 5.64 % | -6.56 % a 10.75 % |

La prueba t+h llega hasta septiembre de 2026, porque este era el último mes completo de anomalía ERSSTv5 reconstruida disponible en el archivo del OAF.

**Interpretación:**
- Con T300 y sin atmósfera adicional, el error medio bajó frente al modelo B en los tres horizontes: **7,38 %** a h=1, **6,21 %** a h=2 y **5,64 %** a h=3.
- El modelo D (que también agrega SOI y vientos retrasados) **empeoró** el MAE frente a B, en los tres horizontes.
- Para C, los tres **intervalos exploratorios de remuestreo por bloques de seis meses cruzan el cero**, de modo que el beneficio sobre B **no está demostrado de forma estable**. Estos intervalos son descriptivos y no sustituyen un análisis estadístico calibrado ni un ensayo prospectivo en tiempo real.
- **No está justificado sustituir el archivo de emisiones realmente prospectivas de la Fase 8A**, ni convertir este resultado de T300 en una alerta, probabilidad de ENFEN o predicción regional de inundación.
- El nombre «prueba independiente» describe la separación temporal de entrenamiento/test dentro del **archivo retrospectivo actual**, no una comprobación con predicciones realmente emitidas antes de cada evento.

## 5. Reproducción y trazabilidad

- [Código Python Fase 8C](modelos/benchmark_calor_subsuperficial_8c.py): análisis de series mensuales PMEL, integración con SOI/vientos y SST y regresión Ridge, prueba 2023+ y remuestreo emparejado.
- [Workflow GitHub Actions](.github/workflows/oaf_benchmark_calor_subsuperficial_8c.yml): autopruebas y descarga de NOAA/PMEL con publicador Git de resultados únicamente cuando todo finaliza correctamente.
- [Serie T300 NOAA/PMEL archivada](datos/noaa_pmel_t300_8c.csv), con meses, temperatura 0–300 m y anomalía.
- [Informe JSON con métricas y limitaciones](datos/benchmark_subsuperficial_8c.json).
- [129 resultados individuales de prueba temporal](datos/benchmark_subsuperficial_8c_test.csv), tres horizontes con 44, 43 y 42 meses respectivamente.
- [Visor experimental en el Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino), sin cambios a la portada autorizada ni a otras pestañas.

## 6. Decisión científica y futura Fase 8D

**Estado al terminar 8C:** se ha encontrado una **señal positiva preliminar de T300**, pero no una ventaja suficientemente robusta y comprobada en emisiones futuras. Mantener el modelo 8A congelado como registro de referencia y el 8C como experimento de comparación sin emisión operativa.

**Próxima línea propuesta, 8D:**
1. Capturar emisiones de un eventual modelo C con fecha exacta y fuente T300 disponible **antes de emitir**, sin reescribir las de 8A. Probarlo durante meses suficientes frente a persistencia.
2. Contrastar T300 de la cuenca completa con señales específicas del sector oriental (NOAA/PMEL T300 East) y física de ondas Kelvin, únicamente si hay datos y periodo de prueba independientes, y sin elegir retrospectivamente «ganadores».
3. Estudiar explícitamente la relación entre anomalías Niño 1+2 y **precipitación, temperatura y radiación solar regionales de Lambayeque**, usando como climatología regional **1996–2025** y el periodo OMM **1991–2020** para comparabilidad. Añadir humedad, DPV y vientos cuando existan registros confiables de disponibilidad histórica.
4. Comparar la habilidad para detectar **anomalías locales** contra climatología y persistencia con fechas de emisión, validación por estaciones SENAMHI u otra referencia independiente, y sin extrapolar una relación estadística a pronósticos de enfermedad.
5. Mantener visibles los comunicados y el **ICEN oficial ENFEN** como contexto diagnóstico institucional, nunca como salidas oficiales del modelo OAF.

**Conclusión:** la Fase 8C integra por primera vez la física subsuperficial del Pacífico a las pruebas científicas del OAF. Una mejora aparente, por interesante que sea, debe someterse a registros prospectivos y más eventos ENSO antes de convertirse en una predicción utilizable.
