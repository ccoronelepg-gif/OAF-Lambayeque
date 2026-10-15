# OAF-Lambayeque | Fase 6A: señales prospectivas de anomalías agroclimáticas

Autor: Carlos E. Coronel García, Ingeniero Agrónomo
Fecha: 14 de octubre de 2026
Estado: **experimental, no operativo**.

## Objetivo y naturaleza del resultado

El observatorio busca predecir (1) anomalías climáticas y episodios/evolución de El Niño Costero y (2) posibles riesgos fitosanitarios en arándano y vid. Esta etapa implementa una **comparación estadística entre el pronóstico meteorológico EXTERNO a 7 días y la climatología histórica 1996–2025**. No equivale a una predicción meteorológica propia ni a un índice validado de El Niño Costero.

## Fuentes abiertas
- Open-Meteo Forecast API: https://open-meteo.com/en/docs
  Variables diarias: temperatura media a 2 m y precipitación acumulada; horizonte 8 días (hoy y las 7 jornadas siguientes completas), America/Lima.
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api
  Temperatura diaria del reanálisis ERA5-Land y precipitación diaria ERA5 desde 1996-01-01 hasta 2025-12-31.
- Localidades referenciales: Chiclayo, Jayanca, Motupe y Olmos. Son puntos aproximados, no estaciones SENAMHI ni parcelas georreferenciadas.

La referencia principal del proyecto es 1996–2025, preservando 1991–2020 como referencia de comparabilidad según la OMM. Esta fase calcula únicamente con 1996–2025. El período representa 10.958 días calendario y 30 años potenciales (8 bisiestos).

## Método
1. Para cada día futuro seleccionar días históricos de 1996–2025 alrededor de la misma fecha de calendario dentro de **±15 días**, incluyendo correctamente el paso de diciembre a enero.
2. Con temperatura media diaria histórica válida, calcular media, percentil 10 (P10) y percentil 90 (P90). Exigir al menos 25 años con 15 o más días válidos dentro de la ventana. Se muestra la cantidad de años efectivamente aprovechados.
3. Comparar la temperatura prevista (dato externo) contra P10 y P90. Sobre P90 se etiqueta «señal cálida»; por debajo de P10, «señal fría». El valor pronosticado menos la media estacional de reanálisis es la anomalía térmica comparativa (°C).
4. Acumular la lluvia prevista durante 7 días futuros. Compararla contra la distribución de acumulados históricos de 7 días consecutivos, seleccionados por ventana de fecha estacional ±15 días. Exigir 25 años y por lo menos 8 ventanas semanales completas por año.
5. Si el acumulado previsto supera P90 (mayor que cero), mostrar «acumulado sobre P90». Si P90 es 0 mm, mostrarlo explícitamente y NO declararlo automáticamente un evento extremo.

**Un percentil histórico no es una probabilidad de pronóstico.** La comparación indica si el pronóstico está fuera de rangos históricos estacionales; no cuantifica la probabilidad de una enfermedad, un fenómeno de El Niño o un evento de lluvia extrema.

## Calidad y limitaciones científicas
- No se imputan días ausentes; se rechazan jornadas futuras incompletas y se exigen 25 años históricos válidos.
- Los datos ERA5 y ERA5-Land son reanálisis **modelados**, no lecturas instrumentales certificadas. Temperatura y precipitación proceden de celdas espaciales y resoluciones diferentes.
- Los pronósticos externos y reanálisis pueden tener sesgos sistemáticos distintos, capaces de producir falsas anomalías; el módulo es exploratorio hasta validar sesgos frente a SENAMHI y la habilidad de los pronósticos a cada horizonte.
- El indicador no estima incertidumbre predictiva, probabilidades calibradas, recurrencias ni severidad de enfermedades. No contiene un modelo causal de El Niño Costero.
- No sustituye las alertas oficiales meteorológicas de SENAMHI ni los comunicados ENFEN.
- Los datos se consultan bajo demanda y pueden no estar disponibles por cuotas, conexión o servicio; si falla, la interfaz debe señalar la falta en lugar de presentar una simulación.

## Línea predictiva separada: El Niño Costero

La predicción de El Niño Costero requerirá variables oceánico-atmosféricas y anomalías de TSM de la región Niño 1+2, además de series del **Índice Costero El Niño (ICEN)** y perspectivas oficiales fechadas.

Fuentes:
- https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen
- https://enfen.imarpe.gob.pe/notas-tecnicas/

**Atención metodológica:** la definición del ICEN fue actualizada en 2024 y ENFEN publicó documentación adicional en 2026. Los umbrales y criterios de episodios deben tomarse de las normas vigentes, no de una escala histórica desactualizada.

**Etapas siguientes:**
1. Integrar datos oceánicos históricos y pronósticos emitidos antes del evento.
2. Definir objetivos verificables para Niño Costero (p. ej., evolución o excedencia de anomalía TSM Niño 1+2 a 1–3 meses).
3. Evaluar una referencia simple de persistencia y luego modelos calibrados, con validación walk-forward y comparación contra pronósticos institucionales.
4. Publicar predicciones OAF únicamente tras demostrar capacidad predictiva independiente; el estado oficial seguirá siendo ENFEN.

## Reproducibilidad
Motor en JavaScript: [modelos/anomalias_climaticas_v01.js](modelos/anomalias_climaticas_v01.js). Las funciones separadas de preparación de series y comparación se pueden probar con datos sintéticos.

Pruebas desarrolladas: 10.958 fechas, 30 años elegibles, un día cálido frente a P90, un día sin anomalía, y lluvia pronosticada sobre P90; además se ampliarán pruebas de registros incompletos y fechas cercanas al inicio y cierre del año.

**Próxima prioridad:** revisar resultados contra series verificadas SENAMHI, conservar predicciones con fecha de emisión, cuantificar habilidad frente a un pronóstico base y construir la serie predictiva oceánica de Niño Costero. Posteriormente incorporar esas perspectivas a los modelos de Botrytis para arándano y oídio para vid.
