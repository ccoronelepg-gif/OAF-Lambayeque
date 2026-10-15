# OAF-Lambayeque — Fase 7C: protocolo y control de calidad de campo para Botrytis de arándano

**Responsable:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Fecha de implementación:** 15 de octubre de 2026 (UTC).  
**Resultado:** infraestructura de registro, validación y confidencialidad preparada; **SIN observaciones reales de campo y SIN modelo de enfermedad entrenado**.

## 1. Objetivo específico

Construir una base longitudinal y verificable que permita, cuando existan datos, relacionar **pronósticos meteorológicos emitidos antes de la fecha de evaluación** con humectación foliar, fenología y diagnósticos fitopatológicos obtenidos **en parcelas de arándano**. El OAF persigue anticipar tanto anomalías climáticas / El Niño Costero como enfermedades agrícolas; **son dos validaciones separadas**.

La evaluación histórica 7B mostró que el indicador horario HR >90 % durante ≥6 h, aunque conceptualmente relevante, genera falsas señales meteorológicas importantes para Motupe y Olmos frente a ERA5. Por eso la Fase 7C **no promueve automáticamente ese indicador a alerta de Botrytis**.

## 2. Fundamentación agrícola

- [UF/IFAS: Botrytis Blossom Blight of Southern Highbush Blueberry](https://ask.ifas.ufl.edu/publication/PP119): las corolas envejecidas son susceptibles a Botrytis y las condiciones de humedad prolongada favorecen el desarrollo, especialmente durante floración.
- [UF/IFAS: Florida Blueberry Integrated Pest Management Guide](https://ask.ifas.ufl.edu/publication/HS380): distingue el patógeno, las fases fenológicas y periodos de humectación extensa; la HR del aire **no es equivalente** a humedad efectiva en tejido.
- [SENASA Perú: vigilancia fitosanitaria en arándano de Lambayeque](https://www.senasa.gob.pe/senasacontigo/lambayeque-prospeccion-y-vigilancia-fitosanitaria-de-plantas-de-arandano/): antecedente institucional de vigilancia regional. La publicación no aporta una incidencia cuantitativa actual ni sustituye el diagnóstico de las parcelas del estudio.

**No se ha encontrado un umbral epidemiológico calibrado en arándano de Lambayeque que permita traducir el criterio HR >90 % × 6 h a una probabilidad de infección.** Ese criterio conserva su etiqueta de señal meteorológica exploratoria.

## 3. Dos instrumentos de registro preparados

### A. Ficha de evaluación fitosanitaria

Archivo CSV público **vacío**: [plantilla_7c_monitoreo_botrytis.csv](datos/plantilla_7c_monitoreo_botrytis.csv).

Tiene **20 campos**; para cada fecha de evaluación y parcela anónima recoge región/provincia/distrito, cultivar, fase fenológica, unidad de muestreo, número total de unidades evaluadas, unidades con síntomas, descripción, diagnóstico, método, fecha diagnóstica, riego por aspersión, fungicidas previos y códigos no personales de evidencia.

**Diccionario de criterios:**
- Fenología permitida: `vegetativo`, `prefloracion`, `floracion`, `cuajado`, `maduracion`, `cosecha`, `postcosecha`, `desconocida`.
- Unidad de muestreo: `flor`, `racimo_floral`, `fruto`, `planta`. Las unidades afectadas deben expresarse **en la misma unidad y denominador** que las evaluadas: **no dividir flores afectadas entre número de plantas**.
- Estados diagnósticos: `sin_analisis`, `sospechoso`, `compatible_laboratorio`, `confirmado_botrytis_cinerea`, `descartado`.
- Métodos: `ninguno`, `inspeccion_visual`, `microscopia`, `aislamiento_morfologia`, `pcr_especifica`, `secuenciacion`.
- **Regla de conservación científica:** para etiquetar específicamente `confirmado_botrytis_cinerea` el validador exige método molecular específico y fecha diagnóstica válida. Un hallazgo de síntomas, o microscopia sin confirmación específica, puede codificarse como sospechoso/compatible pero **no cuenta como especie confirmada**. Es una regla conservadora del proyecto, no una afirmación de que siempre se requiera PCR para manejo agronómico.
- Riego por aspersión últimos siete días y uso de fungicida últimos catorce días: `si`, `no` o `desconocido`. El dato desconocido **nunca se transforma en «no»**.

La incidencia de síntomas, cuando existan registros homogéneos, se distinguirá de la incidencia **confirmada** de Botrytis. Se evitará presentar resultados positivos/negativos como prevalencia regional sin diseño muestral representativo.

### B. Registro horario de microclima

Archivo CSV público **vacío**: [plantilla_7c_microclima_horario.csv](datos/plantilla_7c_microclima_horario.csv).

Tiene **12 campos**: identificador anónimo de lectura, fecha-hora local con UTC-05:00, parcela, sensor, tipo de sensor, altura, temperatura y HR del dosel, **humectación foliar binaria medida (1 mojado, 0 seco, vacío sin lectura)**, radiación y lluvia cuando existan, y estado de calibración.

- La fecha y hora debe seguir `AAAA-MM-DDTHH:00:00-05:00`; intervalos horarios sin zona horaria se rechazan.
- Para `humectacion_foliar_binaria`, el valor **0** significa que un sensor apto midió *seco*; el valor vacío significa **no observado**, nunca seco. Solo se registra como lectura calibrada si `control_calibracion=si`.
- Es obligatorio identificar tipo de sensor: `dosel_combinado`, `humectacion_hoja` o `estacion_meteorologica`. Una estación sin sensor foliar no puede reportar una medición foliar.
- La humedad a 2 m pronosticada y la HR del dosel no deben sustituirse por humectación foliar binaria.

## 4. Privacidad de parcelas y publicación segura

**No publicar coordenadas precisas, nombres de productores, teléfonos, imágenes identificables ni datos de parcelas sin autorización.** Se utilizan IDs como `P001` y los archivos reales residen **solo en el directorio local excluido de Git**:

`datos/_privados/botrytis_7c/monitoreo_botrytis.csv`  
`datos/_privados/botrytis_7c/microclima_horario.csv`

El archivo `.gitignore` ya excluye `datos/_privados/`. Un eventual vínculo geográfico con una cuadrícula meteorológica se establecerá en el entorno privado, verificando distancia y diferencia de resolución; nunca asignar automáticamente cualquier parcela de Lambayeque a Motupe, Jayanca u Olmos.

Los errores detallados del validador quedan en `reporte_qa_privado.json`, dentro del mismo directorio protegido. La salida pública únicamente presenta **estado agregado**; restringe los conteos si hay menos de cinco parcelas anónimas distintas, para reducir exposición de explotaciones pequeñas.

## 5. Motor de integridad y resultado realmente ejecutado

Código: [modelos/validar_campo_botrytis_7c.py](modelos/validar_campo_botrytis_7c.py).

Automatización GitHub Actions: [.github/workflows/oaf_botrytis_7c_calidad_campo.yml](.github/workflows/oaf_botrytis_7c_calidad_campo.yml).

Estado público: [datos/estado_campo_botrytis_7c.json](datos/estado_campo_botrytis_7c.json).

**Pruebas automatizadas aprobadas:** lectura de base vacía; registro sintomático con denominador válido; registro horario con humectación foliar; rechazo de síntomas mayores que unidades evaluadas; rechazo de especie confirmada únicamente por inspección; rechazo de horas sin offset local; duplicados; ocultación de agregados con pocas parcelas; verificación de que no exista pronóstico de enfermedad.

**Estado actual comprobado 15/10/2026:**
- `estado = sin_datos_campo`.
- `hay_registros_campo = false`.
- `n_errores_validacion = 0` **porque no hay archivos reales que evaluar**, no porque exista una base de calidad científica demostrada.
- `modelo_ajustado_con_datos_campo = false`, `probabilidad_infeccion_calibrada = false`, `alerta_fitosanitaria = false`.

**Nota:** los CSV públicos son plantillas de encabezados, no observaciones reales. Los datos sintéticos de las autopruebas son temporales, nunca se guardan como investigación agrícola.

## 6. Diseño de observación para futura validación (no ejecutado)

**Unidad de observación:** una parcela/cultivar y una evaluación fechada, con flores, racimos, frutos o plantas claramente definidos. Para tizón floral debe priorizarse floración y comparaciones de unidades florales consistentes. La periodicidad de monitoreo y tamaños muestrales deberán justificarse según variabilidad, presupuesto, frecuencia de floración y un piloto; no se afirma un tamaño mínimo científico universal sin estimación estadística previa.

**Separación temporal:** los pronósticos solo podrán utilizarse si fueron emitidos **antes** de la ventana causal/evaluación. La fecha de aparición de síntomas **no equivale necesariamente** a la fecha de infección; será necesario definir ventanas biológicas y periodos latentes apropiados con apoyo de patología de campo.

**Modelos candidatos, solo una vez haya datos reales:** (a) frecuencia histórica o regla sencilla, (b) HR/lluvia/temperatura previstas, (c) variables anteriores más radiación y DPV, (d) modelo con humectación foliar **verdaderamente medida o pronosticada mediante otro modelo validado**, fenología y manejo. Variables observadas después del evento **no pueden filtrarse** al predictor emitido.

**Validación rigurosa:** bloquear por parcela y por periodo, separar localidades cuando sea posible, comparar falsos positivos/negativos y calibración probabilística (Brier, curvas de confiabilidad) solo con suficientes casos realmente confirmados. Evaluar tanto casos positivos como negativos con seguimiento sistemático.

**Distinción crucial:** este módulo prepara la base y valida integridad; **NO predice todavía enfermedades**. Una futura herramienta fitosanitaria debe justificar precisión, error y decisiones prácticas, sin recomendar aplicaciones de fungicidas basadas solo en HR elevada.

## 7. Próxima Fase 7D

Crear un conjunto de emparejamiento **privado** y temporalmente seguro entre emisiones archivadas, lectura de humectación del dosel, evaluación sanitaria y diagnóstico posterior; emitir informes de cobertura y sesgo por fenología y localidad. Solo cuando existan datos suficientes y de calidad podrá calcularse un modelo de infección y validarlo en parcelas no vistas.

**Objetivo dual OAF conservado:** anticipación de El Niño Costero/anomalías agroclimáticas por un lado, e investigación de riesgo de enfermedades de arándano/vid por otro, siempre con fuente, fecha de emisión, horizonte y validación trazable.
