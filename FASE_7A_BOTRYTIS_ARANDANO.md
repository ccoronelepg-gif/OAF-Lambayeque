# Fase 7A — Primera detección experimental de condiciones ambientales relacionadas con Botrytis en arándano

**Proyecto:** Observatorio Agroclimático y Fitosanitario OAF-Lambayeque  
**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo  
**Fecha del primer registro:** 15 de octubre de 2026 (hora peruana).  
**Estado:** observación de **condiciones meteorológicas pronosticadas**, sin diagnóstico ni predicción calibrada de incidencia.

## Finalidad dentro del proyecto

El OAF pretende (1) anticipar anomalías climáticas, especialmente episodios vinculados a El Niño Costero, y (2) anticipar condiciones que favorezcan enfermedades agrícolas. La primera línea fitosanitaria prioritaria es **Botrytis en arándano**; la vid continúa en paralelo con su módulo experimental de oídio.

Esta fase establece un **indicador reproducible de humedad atmosférica prolongada** y archiva sus emisiones antes de las fechas previstas. NO puede afirmar infección, enfermedad presente, probabilidad porcentual, incidencia esperada ni recomendación de tratamiento.

## Evidencia y límites de transferencia

- [UC IPM: Botrytis blight / gray mold](https://ipm.ucanr.edu/home-and-landscape/botrytis-blight-or-gray-mold/): describe que una humedad relativa superior a aproximadamente **90 % durante seis o más horas continuas**, o plantas mojadas durante periodos comparables, puede favorecer procesos de infección por *Botrytis* en general. **La publicación no constituye un modelo calibrado de Botrytis de arándano en Lambayeque**.
- [UF/IFAS: Florida Blueberry Integrated Pest Management Guide](https://ask.ifas.ufl.edu/publication/HS380): durante la floración del arándano, las corolas senescentes y periodos extensos de humectación con humedad alta favorecen el tizón floral. Esta guía recalca el papel del estado fenológico y la humectación real, por lo que el indicador atmosférico del OAF NO equivale a riesgo epidemiológico completo.
- [Open-Meteo Forecast API](https://open-meteo.com/en/docs): proporciona pronósticos horarios modelados a 2 m; no son mediciones en el interior del cultivo, ni detecciones micológicas.

**No confundir:** HR elevada en la atmósfera no significa hojas mojadas; radiación solar alta o DPV bajo tampoco equivale directamente a duración de humectación foliar. Una etiqueta de condición meteorológica **no significa presencia de inóculo ni infección**.

## Algoritmo transparente

Se solicitan **ocho días**, zona horaria `America/Lima`, se descarta el día actual y se evalúan **siete días completos × 24 horas = 168 horas** para cada localidad referencial: Motupe, Jayanca, Olmos y Chiclayo.

Variables horarias de Open-Meteo:

| Variable | Unidad | Utilización |
|---|---|---|
| `relative_humidity_2m` | % | Se registra cada hora con **HR estrictamente superior a 90 %** y tramos continuos de **seis horas o más** |
| `temperature_2m` | °C | Contexto ambiental y control de integridad de los datos; sin umbral de infección inventado |
| `precipitation` | mm por hora | Suma diaria, indicador meteorológico complementario |
| `shortwave_radiation` | W/m² (media horaria) | Suma de energía solar diaria con conversión **W/m² × 0,0036 = MJ/m² para una hora**; **no** índice de infección |
| `vapour_pressure_deficit` | kPa | Promedio diario exploratorio del DPV; **no** prueba de secado real de pétalos u hojas |

La serie se valida hora a hora: marcas horarias completas, 24 horas por día, ninguna marca repetida, valores numéricos finitos, temperatura y HR en límites físicos plausibles, sin lluvia, radiación o DPV negativos. **Si falta una hora, se rechaza la evaluación: no se imputa ni se muestran resultados simulados.**

La secuencia continua **no se reinicia automáticamente a medianoche**. Un periodo de más de seis horas se cuenta una sola vez hasta que descienda la HR por debajo del criterio. Si persiste después de medianoche, el resumen diario puede señalar ambas fechas como expuestas al mismo periodo; el número de episodios no se duplica.

Se presentan cantidad de episodios, mayor duración, días con horas dentro de episodios prolongados, HR alta por día, lluvia, radiación y DPV. **No se asignan categorías «riesgo bajo/medio/alto» ni porcentajes epidemiológicos**.

## Primera emisión real archivada: 15/10/2026

La ejecución programada en GitHub Actions **terminó correctamente** con datos horarios reales de Open-Meteo. Se guardó el archivo original con sello temporal UTC y 168 horas pronosticadas por cada localidad para el periodo **16–22 de octubre de 2026**.

| Localidad | Episodios previstos HR >90 % ≥6 h | Duración mayor | Días con horas de episodio |
|---|---:|---:|---:|
| Motupe | **2** | 9 h | 2 |
| Jayanca | **0** | 4 h | 0 |
| Olmos | **3** | 7 h | 3 |
| Chiclayo | **0** | 0 h | 0 |

El valor «0» señala que **el pronóstico atmosférico no identificó ese patrón horario**; no prueba ausencia de *Botrytis* ni ausencia de humedad foliar en parcelas agrícolas.

Fuente y fecha exacta: [datos/patrones_botrytis_emitidos/2026-10-15.json](datos/patrones_botrytis_emitidos/2026-10-15.json). Los resultados pueden diferir de consultas posteriores por actualizaciones de pronósticos. **Las predicciones originales permanecen fechadas**, para permitir verificación prospectiva posterior.

## Pruebas de software ejecutadas

1. **Pruebas de lógica con series sintéticas**: secuencia de diez horas, ausencia de episodio, secuencia que atraviesa medianoche y rechazo de horas faltantes.
2. **Prueba real de contrato de API** en Motupe: cinco variables, 168 horas futuras y unidades admitidas; pasó el flujo GitHub Actions.
3. **Descarga y archivo completo** para las cuatro localidades, con fecha y datos horarios: pasó el flujo GitHub Actions.
4. **Comparación Python–JavaScript sobre cada archivo horario real**: las dos implementaciones coincidieron en seis conjuntos de resultados por localidad: episodios, máximo continuo, días, lluvia, radiación y DPV.

Las pruebas verifican **consistencia del software y disponibilidad del proveedor**, no capacidad para pronosticar infecciones de arándano.

## Archivos implementados

- [Motor web JavaScript](modelos/botrytis_arandano_humedad_7a.js), dentro de [Cultivos → Predicción fitosanitaria](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos).
- [Motor reproducible Python](modelos/botrytis_arandano_humedad_7a.py), que realiza autopruebas, consulta en vivo y archiva emisiones inmutables por fecha.
- [Programación diaria GitHub Actions](.github/workflows/oaf_botrytis_arandano_7a.yml): pruebas sintéticas, API real, archivo de cuatro localidades. Solo guarda archivos tras éxito completo.
- [Primera emisión y variables horarias](datos/patrones_botrytis_emitidos/2026-10-15.json).
- [Plantilla vacía para registros de campo](datos/plantilla_monitoreo_botrytis_arandano.csv), con columnas de parcela, variedad, fenología, humectación medida, daño, diagnóstico y observador. **Contiene únicamente encabezados, sin registros inventados**.

## Diseño de validación biológica — siguiente etapa 7B

Para pasar de señal meteorológica a **predicción de infección o daño**, se necesitan datos suficientes de campo y validación independiente:

1. Registrar **parcela, coordenadas correctas de Lambayeque, fecha, variedad, fase de floración y manejo cultural**, con trazabilidad de cada observación.
2. Medir **humectación foliar verdadera** y temperatura/humedad **dentro del dosel**, con registros temporales compatibles con la predicción horaria.
3. Diagnosticar y cuantificar **incidencia o severidad de *Botrytis cinerea*** con protocolo consistente; registrar y, donde corresponda, confirmar el agente causal. Diferenciar brotes verdaderos de otras causas de necrosis floral.
4. Vincular cada evaluación sanitaria a los pronósticos emitidos **antes del evento**; no utilizar condiciones futuras ya observadas como predictores.
5. Evaluar modelos básicos versus alternativas con radiación, DPV, lluvia, fenología, humectación y temperatura, con separación espacial/temporal rigurosa y métricas de calibración, sensibilidad y errores.
6. Solo publicar **probabilidades fitosanitarias** después de obtener datos de incidencia representativos y verificar el modelo fuera de muestra. No recomendar fungicidas ni mezclas sin confirmación diagnóstica y evaluación agronómica.

**Conclusión:** el módulo cumple su función como primera herramienta de anticipación de **condiciones meteorológicas**, con límites transparentes. Queda pendiente comprobar si esas condiciones pronosticadas se relacionan con enfermedades observadas del arándano en Lambayeque.
