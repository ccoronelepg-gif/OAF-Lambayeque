# OAF-Lambayeque — Fase 6G: verificación prospectiva de emisiones meteorológicas

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Proyecto:** Observatorio Agroclimático y Fitosanitario de Lambayeque  
**Desarrollo inicial:** 15 de octubre de 2026 (UTC; primer archivo de predicción emitido el 14 de octubre, horario de Perú).  
**Estado:** verificación meteorológica prospectiva inicial. NO es alerta ni validación operativa.

## Propósito y distinción científica

El objetivo del OAF es desarrollar dos líneas científicas de predicción: **anomalías climáticas / El Niño Costero** y **riesgo futuro de enfermedades agrícolas de arándano y vid**. Para juzgar su utilidad no basta con mostrar datos recientes o realizar un backtest: debemos conservar cada predicción antes del día al que se refiere y evaluar su error cuando exista un dato de referencia independiente del momento de emisión.

Esta fase implementa infraestructura de evaluación **de los pronósticos externos de Open-Meteo**, no todavía de una predicción propia del OAF. Utiliza referencias de reanálisis y no instrumentos de campo.

## 1. Archivo de emisiones

- Archivos **inmutables por día de emisión** en [datos/pronosticos_emitidos/](datos/pronosticos_emitidos/), generados desde [modelo de archivo diario](modelos/archivar_pronosticos_prospectivos_6f.py).
- Primer archivo confirmado: [datos/pronosticos_emitidos/2026-10-14.json](datos/pronosticos_emitidos/2026-10-14.json), creado antes de los días válidos **15–21 de octubre 2026**.
- Cuatro localidades: **Chiclayo, Jayanca, Motupe, Olmos**.
- Cada archivo contiene emisión UTC, fecha y hora de consulta peruana, producto externo, unidad, coordenadas de celda y siete fechas futuras completas.
- Variables archivadas: temperatura media/máxima/mínima, precipitación, radiación solar, HR media, velocidad máxima del viento, DPV máximo, ET₀ diaria y duración de insolación.
- La fecha local de emisión, el horizonte de **días calendario** y la fecha válida se conservan para evitar comparación de pronósticos con periodos equivocados. La hora de emisión puede cambiar entre días: *D+1* no equivale siempre a 24 horas exactas.

## 2. Control de latencia de ERA5

Documentación del proveedor: [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api). Los productos ERA5 y ERA5-Land se actualizan normalmente **con unos cinco días de retraso**. Se adoptó un **margen prudente de siete días completos** desde la fecha meteorológica válida antes de permitir su evaluación.

El motor rechaza evaluaciones anticipadas. No utiliza la Forecast API con parámetros de pasado reciente para sustituir reanálisis aún no emitidos; tampoco registra como reales valores sintéticos.

**Primer día previsto por el OAF:** 15 de octubre de 2026.  
**Primera fecha de evaluación posible:** **22 de octubre de 2026** (sujeta a que efectivamente exista dato histórico válido).

Si el proveedor todavía no ofrece un valor válido, el día queda incompleto y no se utiliza. Si no hay ninguna fecha verificada, el JSON publica `estado="pendiente_reanalisis"` y la tabla CSV contiene solo encabezados; los errores no se representan como cero.

## 3. Variables y referencias utilizadas

| Variable | Campo de pronóstico (guardado previamente) | Referencia posterior | Unidad |
|---|---|---|---|
| Temperatura media diaria | `temperature_2m_mean` | **ERA5-Land** (`temperature_2m_mean`) | °C |
| Precipitación acumulada diaria | `precipitation_sum` | **ERA5** (`precipitation_sum`) | mm |
| Radiación solar global de onda corta | `shortwave_radiation_sum` | **ERA5** (`shortwave_radiation_sum`) | MJ/m² |

La comparación requiere que **las tres variables estén completas para la misma fecha y localidad**. No se imputan datos faltantes, ni se equipara radiación a UV o a PAR. Los errores de otros parámetros (DPV, ET₀, humedad, viento) podrán incorporarse cuando definamos referencias consistentes.

**Limitación importante:** las referencias ERA5/ERA5-Land son reanálisis meteorológicos, no observaciones de estación SENAMHI ni microclima medido dentro de un cultivo. El error frente a ERA5 no garantiza el mismo error frente a la realidad local. También pueden existir diferencias espaciales entre las celdas del pronóstico y del reanálisis.

## 4. Errores y horizonte de evaluación

Para cada emisión, fecha válida, localidad, horizonte (D+1 a D+7) y variable:

`error = pronóstico_archivado − valor_del_reanálisis`

Agrupados por localidad + horizonte + variable, con **conteo explícito de días verificables**, el programa calcula:

- MAE: media del valor absoluto del error, en unidades de la variable.
- RMSE: raíz del promedio del error al cuadrado, en unidades de la variable.
- Sesgo: promedio del error con signo.
- Número de emisiones y jornadas efectivamente verificadas.

**No hay probabilidades calibradas ni tasas de acierto categóricas.** No se permite la comparación directa de MAE entre variables con unidades distintas.

Se debe ser especialmente prudente con métricas generadas a partir de pocos días: pueden aparecer en el visor como resultados exploratorios, pero no constituyen validación operativa. Faltan estaciones instrumentales independientes.

## 5. Implementación auditable

- [Motor Python](modelos/verificar_pronosticos_emitidos_6g.py): comprueba cronología de emisión y de fechas válidas, sellos temporales, completitud, unidades y límite de siete días; genera errores solo con datos reales disponibles.
- [Ejecución diaria GitHub Actions](.github/workflows/oaf_verificacion_6g.yml) después del horario habitual de la emisión del archivo.
- [Estado estructurado JSON](datos/evaluacion_prospectiva_6g.json): conserva información de disponibilidad, variables, fuentes, días maduros, días verificados y métricas.
- [Errores individuales CSV](datos/evaluacion_prospectiva_6g.csv): audita emisión, fecha, horizonte, localidad, valor previo, valor reanalizado y error.
- [Lector de resultados](modelos/verificacion_prospectiva_visor_6g.js): solo presenta métricas cuando la verificación es real y consistente; si no, informa la fecha desde la que será posible consultar.
- [Sección Datos climatológicos del portal](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima): apartado desplegable de la **Fase 6G**.

La primera ejecución técnica pasó las autopruebas determinísticas y el procesamiento del repositorio. Resultado de inicialización:

| Campo | Resultado |
|---|---|
| Fecha de generación UTC | 15/10/2026 |
| Estado | **pendiente_reanalisis** |
| Jornadas guardadas | **28** (4 localidades × 7 días) |
| Jornadas ya elegibles | **0** |
| Jornadas verificadas | **0** |
| Primera fecha elegible | **22/10/2026** |

El CSV está **vacío de registros de error** porque ningún día podía evaluarse todavía. Este comportamiento es deliberado y científicamente correcto.

## 6. Próximas fases científicas

1. Completar sucesivas verificaciones diarias y observar los errores por sitio, estación, variable y horizonte durante semanas y meses. No declarar habilidad por una muestra pequeña.
2. Validar contra estaciones **SENAMHI** y, de ser posible, sensores instrumentales locales para corregir sesgos del reanálisis. Esta etapa requerirá datos observados de calidad verificable.
3. Desarrollar predictores de **anomalías climáticas regionales** con referencia histórica 1996–2025 y comparar su desempeño prospectivo con pronósticos institucionales y persistencia.
4. Mantener por separado la línea oceánica Niño 1+2 / **ICEN institucional ENFEN**, sin derivar una alerta de El Niño Costero únicamente de la lluvia local.
5. Para **Botrytis en arándano**, registrar humectación foliar, fenología y observaciones fitosanitarias antes de intentar modelos probabilísticos. Para la vid, validar indicadores de oídio con temperatura dentro del dosel y datos sanitarios.

**Principio:** distinguir fuente, fecha real de emisión, periodo pronosticado y verificación posterior. Nunca sustituir una ausencia de dato por un número supuesto.
