# Fase 6B — Primer pronóstico oceánico experimental para Niño 1+2

**Observatorio Agroclimático y Fitosanitario de Lambayeque**  
**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Fecha del avance:** 14 de octubre de 2026 (Perú; la actualización de GitHub Actions figura en UTC)  
**Estado:** experimentación científica, NO sistema oficial ni alerta operativa.

## 1. Pregunta científica

¿Es posible anticipar **un mes** la anomalía de temperatura superficial del mar de la región **Niño 1+2**, usando únicamente las anomalías de meses previos, y obtener menos error que una predicción trivial de persistencia?

Esta es una tarea predictiva preliminar relacionada con **El Niño Costero**, pero NO una clasificación ni una predicción probada del evento El Niño Costero. Para predecir el fenómeno y sus impactos agrícolas necesitaremos posteriormente variables oceánico-atmosféricas adicionales y evaluación externa.

## 2. Fuente realmente procesada

**NOAA Climate Prediction Center**, archivo [sstoi.indices](https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices), serie mensual **OISST v2.1** de Niño 1+2, sector ecuatorial oriental **0–10° S, 90–80° O**.

- Primer mes en la serie utilizada: **1982-01**.
- Último mes observado incluido: **2026-09**.
- Producto oceánico: NOAA CPC **OISST**, con anomalías mensuales cuya climatología de referencia pública corresponde a 1991–2020.
- Datos descargados sin interpolación de meses, con control de continuidad, duplicados, rango y fecha de actualización.
- CSV trazable: [datos/noaa_nino12_oisst_mensual.csv](datos/noaa_nino12_oisst_mensual.csv).
- La serie está publicada en línea y se actualiza en el repositorio mediante un flujo de GitHub Actions que solo confirma datos si el proceso y las pruebas se completan sin errores.

### Diferencia fundamental con el ICEN de ENFEN

El **ICEN vigente** no se calcula directamente con esta serie OISST: ENFEN utiliza el producto **ERSSTv5** Niño 1+2 y un promedio móvil trimestral con metodología actualizada en 2024 y documentación operacional adicional en 2026. Por ello:

- **NO calculamos ICEN oficial ni clasificamos por umbrales históricos.**
- **NO atribuimos al OAF el estado ni la probabilidad institucional de El Niño Costero.**
- ENFEN conserva la autoridad de diagnóstico y alertas oficiales. Fuentes: [ICEN/IMARPE](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen), [Notas Técnicas ENFEN](https://enfen.imarpe.gob.pe/notas-tecnicas/), [Comunicados ENFEN](https://enfen.imarpe.gob.pe/downloads/comunicados/).

## 3. Método reproducible

La serie observada se escribe como y(t), anomalía SST Niño 1+2 en °C.

- **Referencia 1 — Persistencia:** estimar y(t+1) = y(t).
- **Referencia 2 — Anomalía cero:** estimar y(t+1) = 0 °C.
- **Modelo experimental — AR(1) por mínimos cuadrados ordinarios:** estimar y(t+1) = a + b × y(t), ajustando a y b exclusivamente con pares de meses anteriores y conocidos a la fecha de cada predicción.

**Evaluación retrospectiva expansiva (walk-forward):** cada predicción histórica se calculó con sus datos disponibles hasta ese origen; luego se comparó con el mes siguiente y se repitió el proceso. No se divide aleatoriamente la serie.

Limitación: el archivo NOAA incorpora revisiones y una climatología publicada posteriormente; una evaluación retrospectiva con la versión actualizada del índice **no equivale a haber archivado los pronósticos realmente emitidos en cada fecha histórica**.

## 4. Resultados reproducidos del archivo generado

| Indicador | Resultado |
|---|---:|
| Última anomalía NOAA (2026-09) | +4.69 °C |
| Horizonte siguiente | 2026-10 |
| Modelo AR(1), anomalía estimada | +4.35 °C |
| Persistencia, anomalía estimada | +4.69 °C |
| Orígenes retrospectivos evaluados | 200 |
| MAE AR(1), evaluación completa | 0.3749 °C |
| MAE persistencia, evaluación completa | 0.3797 °C |
| MAE AR(1), últimos 12 meses | 0.5818 °C |
| MAE persistencia, últimos 12 meses | 0.4708 °C |

Habilidad relativa global sobre persistencia (1 − MAE_AR1/MAE_persistencia): **1.26 %**. Aunque positiva, resulta pequeña.

Habilidad relativa en los últimos 12 meses: **-23.56 %**. El modelo empeoró respecto de persistencia en el periodo reciente.

Prueba exploratoria de robustez: 2000 remuestreos de bloques móviles de 12 meses, sobre errores pareados ya evaluados. Intervalo de mejora relativa aproximado (95 % de remuestreos): **-0.25 % a 5.36 %**.

**Conclusión técnica: el modelo AR(1) NO demuestra habilidad consistente frente a persistencia.** Este resultado se presenta como experimento educativo/investigativo y NO como una predicción climática fiable.

### Sobre los intervalos

El archivo incluye un rango experimental del percentil 10 al 90 de errores históricos aplicado a la proyección actual (**3.78 °C a 5.06 °C**). Es un **intervalo empírico retrospectivo no calibrado**; no afirmar cobertura futura del 80 %, ni usar como intervalo probabilístico oficial.

## 5. Archivos implementados

- [modelos/modelo_nino12_fase6b.py](modelos/modelo_nino12_fase6b.py): ingesta NOAA, controles, AR(1), baselines, walk-forward, remuestreo por bloques y pruebas sintéticas.
- [.github/workflows/oaf_nino12_fase6b.yml](.github/workflows/oaf_nino12_fase6b.yml): actualización mensual, con registro de éxito/error. Si no hay datos válidos no se sustituyen por ficticios.
- [datos/noaa_nino12_oisst_mensual.csv](datos/noaa_nino12_oisst_mensual.csv): datos históricos descargados.
- [datos/nino12_backtest_walkforward.csv](datos/nino12_backtest_walkforward.csv): 200 predicciones verificadas retrospectivamente, incluidos modelos de referencia.
- [datos/modelo_nino12_experimental.json](datos/modelo_nino12_experimental.json): resumen con estado experimental, serie reciente y métricas.
- [modelos/nino12_visor_v01.js](modelos/nino12_visor_v01.js): lectura segura del resultado en [Boletín de El Niño](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#nino).

## 6. Siguiente desarrollo científico

1. Incorporar **ERSSTv5 y la definición oficial actualizada de ICEN** para validar comparabilidad con ENFEN; no confundir este producto NOAA OISST con ICEN.
2. Conseguir pronósticos oceánico-atmosféricos emitidos y fechados (anomalías TSM, viento, presión, calor subsuperficial, ondas ecuatoriales), conservando series sin fuga temporal.
3. Mejorar la evaluación **prospectiva** y por periodos, incluyendo años con anomalías intensas y estaciones de transición.
4. Evaluar modelos estacionales/autorregresivos y modelos probabilísticos frente a persistencia y a pronósticos institucionales; **no incorporar complejidad injustificada si no mejora habilidad**.
5. Explorar después relaciones verificables entre anomalías Niño 1+2, lluvia/temperatura en Lambayeque y los modelos fitosanitarios de arándano y vid.

**Regla:** no convertir una anomalía SST pronosticada en aviso fitosanitario ni alerta oficial, ni declarar predicciones validadas sin evaluación independiente.
