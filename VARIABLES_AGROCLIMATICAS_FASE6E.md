# Fase 6E — Ampliación de variables agroclimáticas y fitosanitarias del OAF

**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque  
**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Fecha:** 14 de octubre de 2026 (Perú)  
**Objetivo del observatorio:** avanzar hacia predicciones verificables de (1) anomalías climáticas y evolución de El Niño Costero y (2) condiciones favorables y, tras validación, ocurrencia de enfermedades del arándano y la vid.

## Variables incorporadas al pronóstico diario

Los datos proceden de modelos meteorológicos externos servidos por Open-Meteo; no son mediciones dentro de una parcela. El portal consulta Chiclayo, Jayanca, Motupe y Olmos.

| Variable | Campo Open-Meteo | Unidad | Resolución mostrada | Aplicación agrícola |
|---|---|---|---|---|
| **Radiación solar global de onda corta** | `shortwave_radiation` (actual), `shortwave_radiation_sum` (diaria) | **W/m²** (actual) y **MJ/m²/día** (acumulado) | Instante actual del proveedor y cada día | Energía incidente, demanda evaporativa, balance hídrico, estudio de insolación y microclima |
| **Insolación estimada** | `sunshine_duration` | h/día, convirtiendo de segundos | Diaria | Duración de brillo solar; no confundir con energía acumulada |
| **Viento a 10 m** | `wind_speed_10m`, `wind_speed_10m_max` | km/h | Actual y máximo diario | Evaporación, dispersión potencial, ventilación y aplicación de productos (sin recomendación automática) |
| **Humedad relativa** | `relative_humidity_2m`, `relative_humidity_2m_mean` | % | Actual y media diaria | Ambiente propicio para procesos biológicos; **no equivale a horas de humectación foliar** |
| **Déficit de presión de vapor, DPV** | `vapour_pressure_deficit`, `vapour_pressure_deficit_max` | kPa | Actual y máximo diario | Demanda evaporativa del aire y estudio del estrés hídrico en cultivo |
| **ET₀ de referencia FAO** | `et0_fao_evapotranspiration` | mm/día | Diaria | Demanda evapotranspirativa de superficie de referencia; **no es consumo real de arándano ni vid** |
| **Presión atmosférica superficial** | `surface_pressure` | hPa | Actual | Seguimiento de dinámica local; **no es SOI**, que exige diferencias normalizadas de presión de estaciones específicas |
| **Temperatura y precipitación** | Campos ya existentes | °C y mm/día | Actual y diaria | Modelos térmicos, agua, extremos y enfermedades |
| **Probabilidad de precipitación del proveedor** | `precipitation_probability_max` | % | Máximo diario | Pronóstico EXTERNO y agregado, no probabilidad propia calibrada del OAF |

**Precisión:** radiación solar global de onda corta horizontal no es equivalente a radiación PAR, ultravioleta (UV), energía en la superficie de una hoja ni medición con piranómetro. Las horas de insolación tampoco son una conversión directa de radiación energética.

## Radiación incorporada al análisis de anomalías 1996–2025

- Pronóstico externo: siete días completos futuros, acumulados diarios `shortwave_radiation_sum` de Open-Meteo.
- Referencia: reanálisis **ERA5-Land** de 1996-01-01 a 2025-12-31, variable `shortwave_radiation_sum`, localidad de referencia.
- Comparación: sumar **siete días pronosticados** y comparar con acumulados de siete días del mismo periodo estacional (**±15 días**) de cada año.
- Se calculan **P10**, **mediana** y **P90** históricos. Se requieren **≥25 años** con al menos ocho ventanas de siete días completas dentro de la ventana estacional.
- Etiquetas: radiación prevista por encima de P90, por debajo de P10 o dentro de P10–P90. **No son probabilidades de eventos ni una alerta agrícola.**
- Si falta información histórica o futura, la radiación es **no evaluable**, sin forzar un resultado de cero ni ocultar el análisis independiente de lluvia y temperatura.

**Pruebas sintéticas de código aprobadas:** periodo 1996–2025 (10 958 días), cobertura completa de radiación, radiación alta >P90, radiación dentro del rango, dato futuro ausente, referencia radiativa ausente, invariancia de clasificación de temperatura y precipitación.

**Verificación en vivo:** las pruebas de contrato de API están en [tests/test_variables_agroclimaticas_6e.py](tests/test_variables_agroclimaticas_6e.py) y el flujo [oaf_variables_6e_check.yml](.github/workflows/oaf_variables_6e_check.yml). Estas verificaciones comprueban existencia y unidades de variables pronosticadas y datos históricos; su resultado debe confirmarse mediante GitHub Actions.

## Variables prioritarias para fases siguientes (aún no integradas ni medidas)

| Área | Variable futura | Fuente candidata | Requisito antes de usar en modelos |
|---|---|---|---|
| Fitopatología / Botrytis | **Duración real de humectación foliar** | Sensor de hoja en arándano o algoritmo micrometeorológico validado | Medición simultánea de humedad/temperatura/rocío, evaluación de sesgo; jamás sustituir solo con HR |
| Fitopatología | Fenología, susceptibilidad, incidencia y severidad | Evaluación y diagnóstico agronómico de campo | Fechas, escala, lote, variedad y método de muestreo; diagnóstico |
| Fisiología / riego | Humedad y temperatura de suelo | Sensores o productos modelos validados | Profundidad, unidades, representatividad espacial |
| Fisiología | Radiación fotosintéticamente activa (PAR) y UV | Sensor o producto específico con trazabilidad | No inferir PAR/UV a partir de global horizontal sin calibración |
| Meteorología | Cobertura nubosa, punto de rocío, ráfagas | Open-Meteo/SENAMHI y validación | Guardar hora y escala: útil para estudio de rocío, viento y lluvia |
| Predicción ENSO | Temperatura superficial del mar Niño 1+2, ICEN | ERSSTv5/NOAA NCEI, ENFEN | ICEN oficial siempre desde ENFEN; no clasificarlo por reconstrucción propia |
| Predicción ENSO | Viento zonal del Pacífico, presión atmosférica/SOI | NOAA PSL, reanálisis, instituciones oficiales | Serie histórica con emisión temporal verificable; no mezclar presión superficial local con SOI |
| Predicción ENSO | Calor subsuperficial, profundidad termoclina | NOAA / GODAS, Argo u otras fuentes | Producto, fecha, validez, resolución y habilidad predictiva |

## Integración en la predicción

**Línea agroclimática:** temperatura + precipitación + **radiación** + viento + humedad + DPV + ET₀ para caracterización predictiva local. Las variables nuevas son *covariables candidatas*, no factores que se deban sumar indiscriminadamente: se validarán con series retrospectivas completas y contrastes de habilidad fuera de muestra. Diferenciar variables correlacionadas y evitar incluir variables del futuro real en las predicciones.

**Línea fitosanitaria:** radiación y déficit de presión de vapor pueden aportar información indirecta sobre secado foliar y microclima, pero **no prueban presencia de enfermedades**. Para *Botrytis cinerea*, oídio de vid y otras patologías se deben combinar pronósticos meteorológicos con fenología, humectación foliar y datos sanitarios confirmados.

**Línea El Niño Costero:** radiación local, ET₀ y DPV ayudan a estudiar los impactos agroclimáticos, pero **no sustituyen** los predictores oceánicos/atmosféricos ni el ICEN oficial. Se mantendrán modelos separados para anomalías regionales y evolución oceánica.

## Próximas decisiones técnicas

1. Comprobar el contrato real de Open-Meteo y el archivo ERA5-Land de radiación, registrar errores y unidades.
2. Archivar pronósticos emitidos con fecha, horizonte, localidad, variables y versión de fuente.
3. Contrastar la radiación modelada y otras variables con observaciones disponibles en Lambayeque.
4. Incorporar progresivamente variables adicionales **solo si** mejoran la capacidad predictiva medida frente a referencias simples y evitan fuga temporal.
5. Priorizar el modelado de humectación foliar y datos de campo para Botrytis de arándano, conservando la línea de El Niño Costero por separado.

**Regla invariable:** claridad de procedencia y unidades, no rellenar datos ausentes, no crear falsos porcentajes de enfermedad, no convertir señales exploratorias en alertas oficiales.
