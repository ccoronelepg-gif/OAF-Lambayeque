# OAF-Lambayeque 2.0 — Protocolo de calidad, estados y comunicación del riesgo

## Estado inicial

Este protocolo entra en vigor con la reorganización del proyecto. **No existen todavía alertas predictivas propias validadas ni un servicio operativo OAF.** Los avisos oficiales de SENAMHI y el estado de El Niño Costero de ENFEN tienen autoría institucional; el OAF podrá enlazarlos y resumirlos con fecha y versión, nunca atribuirse su emisión.

## 1. Tipos de datos, etiquetas obligatorias

| Clase | Qué significa | Uso admisible |
|---|---|---|
| `OBSERVADO_INSTRUMENTAL` | Estación meteorológica con procedencia y periodo medido | Validación local solo con controles de calidad, códigos y continuidad |
| `OBSERVADO_DOCUMENTAL` | Acumulado/cifra extraída de boletín oficial | Visualización del mes documentado; no reconstruir serie diaria |
| `ESTIMADO_SATELITAL` | IMERG, CHIRPS u otro producto gridded | Monitoreo con escala y sesgos indicados; no adjudicar a pluviómetro |
| `REANALISIS` | Reconstrucción climática histórica mediante modelo/asimilación | Contexto retrospectivo; no es pronóstico emitido antes del evento |
| `PRONOSTICO_METEOROLOGICO` | Predicción emitida para un horizonte futuro | Pronóstico identificando fuente, fecha de emisión, plazo y desempeño |
| `ESTADO_OFICIAL_ENSO` | Estado/clasificación comunicada por ENFEN | Resumen fechado con URL; no inventar índice/alerta del OAF |
| `RIESGO_FITOSANITARIO_EXPERIMENTAL` | Condiciones meteorológicas favorables sin validar daño en campo | Divulgación técnica exploratoria, sin aconsejar aplicaciones |
| `RIESGO_FITOSANITARIO_VALIDADO` | Modelo con evidencia sanitaria y evaluación fuera de muestra | Solo si se superan controles de validación acordados |

## 2. Calidad y actualización

Cada registro público **deberá** incluir la fuente con enlace o identificador, versión, variable y unidad, huella/fecha de consulta, inicio-fin del intervalo de observación o pronóstico, cobertura, celda/coordenadas cuando corresponda y estado de control.

Estados permitidos:
- **verificado**: fuente, periodo, unidades, QA y cálculo rastreables; identidad instrumental adicional cuando se atribuya a estación.
- **provisional**: fuente identificada pero se encuentra pendiente un control científico (p. ej. coordenadas históricas, calidad de estación, validación de satélite).
- **desactualizado**: superó latencia recomendada, la actualización esperada no llegó o la vigencia del comunicado terminó; se conserva con fecha visible y sin presentarlo como actual.
- **no_disponible**: descarga fallida, servicio caído, falta la variable o la ventana; no generar valor.
- **descartado**: calidad insuficiente, periodo inválido, falta de unidades, duplicados irreconciliables, fuente no autorizada.

La cadencia diaria/semanal es **objetivo operativo**, no promesa de datos disponibles. En cada extracción, los errores quedan visibles en el registro técnico; nunca rellenar los huecos «porque falta poco para completar».

## 3. Definición de eventos futuros

Un pronóstico probabilístico necesita:
- Variable objetivo comprobable: ejemplo precipitación diaria observada > umbral local documentado, máxima de temperatura > percentil acordado o casos incidentes de enfermedad según protocolo.
- Horizonte de emisión (p. ej. 24–72 h, 1–7 días, 2–6 semanas) y fecha de corte del entrenamiento.
- Baseline o modelo de referencia: climatología de fuente comparable, persistencia o pronóstico institucional.
- Probabilidad calibrada frente a observaciones **posteriores**, con Brier Score, fiabilidad y evaluación de falsos positivos/omisiones.
- Etiqueta «experimental» hasta superar el umbral de calidad acordado científicamente; no fijar umbrales arbitrarios en la web como alertas.

NO usar los umbrales descriptivos de fase 3S (1, 20 y 50 mm **mensuales**) como desencadenantes de alertas de lluvia diaria.

## 4. Criterio de no alerta

**No emitir una alerta propia OAF** cuando ocurra cualquiera de los siguientes:
- Fuente principal no disponible/desactualizada o zona sin respaldo espacial comprobado.
- Solo hay una estimación retrospectiva o un reanálisis, no una predicción emitida antes del periodo.
- No se dispone de horizonte, probabilidad calibrada, incertidumbre y validación prospectiva.
- En sanidad vegetal: no hay observaciones de incidencia/severidad y confirmación del fenómeno para el cultivo/área.
- Existe conflicto de fuente o estaciones históricas confundidas con otras del mismo nombre.

En esos casos, mostrar «Información experimental insuficiente» y, si corresponde, **enlace al aviso institucional** emitido por SENAMHI o comunicado ENFEN con su fecha, no reformularlo como alerta propia.

## 5. Regla para faltantes (no imputación)

- En análisis anuales: 12/12 meses completos y 365/366 días válidos por estación. Un año incompleto **no tiene** total anual observado calculable.
- En vigilancia en curso: utilizar días/pentadas/ventanas válidas sin esperar el fin de año; no sustituir horas/días ausentes por 0 ni extrapolar una ventana incompleta como total.
- Distinguir **«Traza»** de cero y de datos ausentes.
- Las estimaciones de satélite o reanálisis pueden tener series completas propias; cada una es un **producto estimado** y su normal se etiqueta por fuente, sin decir que son años completos de estación SENAMHI.

## 6. Riesgo fitosanitario — arándano

Etapa experimental: índices de condiciones ambientales potencialmente favorables a **Botrytis cinerea** (temperatura, humedad, humectación y fenología cuando exista), **sin afirmar infección o brote real**. No recomendar fungicidas, dosis, intervalos ni decisiones de manejo basadas solamente en el índice.

Se exige dataset de campo con fecha, coordenada/sector protegido, fase fenológica, variedad, incidencia, severidad, condiciones de manejo y diagnóstico para calibrar modelo de enfermedad. Los datos de productores no se expondrán sin autorización, y las ubicaciones sensibles podrán generalizarse.

## 7. Auditoría del observatorio público

Todo módulo debe mostrar: **última fecha de datos**, **periodo observado/estimado o emitido**, fuente/versión, tiempo de vigencia, etiqueta de incertidumbre, área representada y, cuando corresponda, botón hacia comunicado institucional original.

**Estado actual (14/10/2026):** se reorganizaron misión y procedimientos; todavía no se ha iniciado el nuevo pipeline de vigilancia 3Z ni existe modelo predictivo fitosanitario propio validado. Los análisis retrospectivos y boletines previos se conservan.
