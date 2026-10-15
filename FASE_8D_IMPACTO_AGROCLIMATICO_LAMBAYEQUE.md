# Fase 8D — ¿Aportan Niño 1+2 y T300 capacidad para anticipar el clima de Lambayeque?

**Autor:** Ing. Agrónomo Carlos Enrique Coronel García.  
**Fecha de ejecución:** 15 de octubre de 2026.  
**Proyecto:** Observatorio Agroclimático y Fitosanitario OAF-Lambayeque.  
**Clasificación científica:** **estudio retrospectivo experimental**, sin predicción regional operativa validada.

## 1. Objetivo e hipótesis

La meta del OAF es doble: anticipar anomalías climáticas y la evolución de eventos relacionados con El Niño Costero, y desarrollar capacidades de predicción de enfermedades agrícolas en arándano y vid. Mientras se buscan **observaciones fitosanitarias reales** para Botrytis, se analiza si el conocimiento oceánico ayuda a **predecir con anticipación la temperatura, precipitación y radiación solar regionales**, y no solamente a explicar su comportamiento después de observarlo.

**Hipótesis predefinida:** ¿añadir anomalías mensuales de TSM Niño 1+2 al historial del clima local y después incorporar T300 del océano subsuperficial reduce el MAE de condiciones regionales futuras, frente a climatología, persistencia y una regresión local sencilla?

### Fuentes públicas, verificadas

- **[Open-Meteo Historical Weather](https://open-meteo.com/en/docs/historical-weather-api):** temperaturas medias diarias de **ERA5-Land** y precipitación y radiación corta diaria de **ERA5** desde 1996 hasta septiembre 2026. **Son reanálisis de celda**, no mediciones de estaciones **SENAMHI**, no sensores en dosel ni observaciones de lluvia instrumental en las parcelas.
- **[NOAA NCEI ERSSTv5 Niño 1+2](https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.el_nino.dat):** anomalías de temperatura superficial del mar, en referencia **1991–2020 recalculada por el OAF** según Fases 6D–8A. No representa el ICEN oficial publicado por ENFEN.
- **[NOAA/PMEL GODAS T300](https://www.pmel.noaa.gov/elnino/upper-ocean-heat-content-and-enso/):** anomalía mensual de temperatura media oceánica 0–300 m del Pacífico ecuatorial, referencia propia **1981–2010**. Se emplea el **mes anterior t−1**. No representa temperatura superficial del litoral lambayecano.

Cuatro puntos geográficos regionales **referenciales**: **Chiclayo, Jayanca, Motupe y Olmos**. Las celdas de ERA5 y ERA5-Land tienen distintas resoluciones y coordenadas ajustadas por el proveedor; los valores no deben extrapolarse directamente a una parcela agrícola concreta.

## 2. Climatología y separación temporal sin fuga de datos

Se preparó una serie mensual completa de **369 meses por localidad (enero 1996 a septiembre 2026)**, derivada de días completos y unidades explícitas:

- **Temperatura mensual (°C):** promedio de temperaturas medias diarias.
- **Precipitación mensual (mm):** suma de precipitaciones diarias.
- **Radiación mensual (MJ/m²):** suma de radiación solar global corta diaria; **no radiación ultravioleta ni PAR**.

**Dos climatologías separadas por principio:**

1. **Referencia pública descriptiva 1996–2025:** treinta años naturales completos, tal como establecimos para el observatorio. Las doce medias o acumulados mensuales se conservan en el JSON para explicar el contexto histórico.
2. **Referencia exclusiva del experimento, congelada 1996–2022:** veintisiete años, utilizada para calcular las **anomalías de entrenamiento y prueba**. Así las observaciones de **2023–2026** no influyen en el promedio climático que utiliza el ensayo. Usar directamente 1996–2025 para ajustar o transformar la prueba habría introducido parte de las fechas de evaluación en el cálculo de referencia.

No se computó la referencia **1991–2020** en este ensayo; se mantiene como periodo estándar OMM de futura comparación, pero **no se afirma que sus resultados ya estén calculados**.

## 3. Modelo y evaluación

Para cada variable, localidad y horizonte **h = 1, 2, 3 meses** se compararon cinco métodos sobre los mismos meses objetivo:
- **Climatología cero:** proyectar anomalía igual a cero (valor normal de referencia fija).
- **Persistencia local:** conservar la anomalía meteorológica local del mes de origen `t`.
- **Ridge local:** usar anomalía del mes de origen `t`.
- **Ridge local + Niño 1+2:** anomalía local en `t` y SST Niño 1+2 en `t`.
- **Ridge local + Niño 1+2 + T300:** anterior más anomalía T300 en `t−1`.

Regresión Ridge con **regularización fija alpha = 20**. Escalamiento y parámetros aprendidos **solo** del periodo de entrenamiento. Se excluyen los meses intermedios que producirían un objetivo después de 2022 pero un origen antes de 2023.

- **Entrenamiento:** resultados de mes objetivo **hasta diciembre de 2022**, sin acceder a objetivos posteriores.
- **Prueba aparte:** orígenes de enero 2023 en adelante, con objetivos que no sobrepasan septiembre de 2026; **44**, **43** y **42** pruebas a h=1, h=2 y h=3 respectivamente para cada localidad/variable.
- **Total auditado:** **1548 predicciones mensuales de evaluación** (4 localidades × 3 variables × 129 fechas-horizonte), más 1.476 valores mensuales meteorológicos completos almacenados.

El MAE y RMSE se computan respecto de la **anomalía de la variable en la referencia fija 1996–2022**, en su unidad natural. No comparar MAE en °C directamente con mm ni MJ/m².

**Importante sobre emisiones reales:** los predictores locales y la SST completos del mes `t` generalmente se conocen **después de cerrar t**. Por tanto, un valor calculado para `t+1` podrá ser una **estimación intramensual** si se publica cuando t+1 ya empezó. Además, archivos históricos ERA5 y NOAA pueden revisarse: este holdout no equivale a conservar pronósticos emitidos realmente antes del evento. El archivo oceánico prospectivo de Fase 8A se mantiene intacto.

## 4. Hallazgos para temperatura del aire

En las cuatro localidades el modelo **local + Niño 1+2 + T300** tuvo menor error en temperatura que el Ridge local **en cada uno de los tres horizontes**; las reducciones de MAE son señales retrospectivas, todavía sin validación instrumental independiente.

### Horizonte de tres meses

| Localidad | MAE local (°C) | MAE + Niño/T300 (°C) | Mejora relativa | Intervalo descriptivo de mejora, bloques 6 meses (95 %) |
|---|---:|---:|---:|---|
| Chiclayo | 1.139 | 1.054 | 7.5 % | -2.2 % a 13.6 % |
| Jayanca | 1.005 | 0.849 | 15.5 % | 6.6 % a 22.9 % |
| Motupe | 0.793 | 0.740 | 6.8 % | -15.7 % a 15.5 % |
| Olmos | 0.709 | 0.613 | 13.6 % | -9.8 % a 22.5 % |

**Lectura de estabilidad:** solamente **Jayanca, horizonte 3 meses**, tuvo un intervalo exploratorio de mejora totalmente positivo (aprox. **+6,6 % a +22,9 %**). Los otros once intervalos de temperatura entre localidades y horizontes incluyen cero, por lo que no demuestran mejora estable. Esta constatación es **exploratoria**, no una prueba formal corregida por múltiples comparaciones, y **no valida la predicción operativa para Jayanca**.

## 5. Lluvia y radiación solar: no activar el enfoque oceánico examinado

- **Precipitación mensual:** las doce comparaciones (4 localidades × 3 horizontes) del modelo con SST+T300 **empeoraron el MAE frente al Ridge local**. También quedaron peor que la **climatología cero** en este periodo de prueba. Los doce intervalos descriptivos del beneficio frente al Ridge local fueron completamente **negativos** bajo el remuestreo temporal elegido. Esto no autoriza predecir sequía/inundación a partir del nuevo modelo.
- **Radiación solar global:** las doce comparaciones oceánicas ampliadas también tuvieron **MAE mayor que el Ridge local**. Algunos intervalos fueron negativos por completo; otros incluyeron cero, sin señal de ventaja consistente. La radiación sigue siendo variable prioritaria del OAF, pero el predictor oceánico definido aquí no aporta precisión verificable sobre las alternativas sencillas.

**Conclusión:** los resultados de temperatura aportan una hipótesis de investigación, pero los de lluvia y radiación impiden promocionar el modelo 8D completo como herramienta predictiva regional.

## 6. Prueba de estabilidad y límites

Se realizó un **remuestreo descriptivo por bloques contiguos de seis meses (2.000 réplicas y semillas reproducibles)** para cada combinación localidad × variable × horizonte. El cálculo conserva el emparejamiento de errores del modelo local y oceánico para las mismas fechas.

- [Informe de estabilidad](datos/robustez_impacto_regional_8d.json).
- Estos **no son intervalos de confianza formalmente calibrados**, ni garantizan estabilidad ante un fenómeno ENSO extremo o un cambio de régimen. Las múltiples comparaciones y la duración limitada de prueba requieren replicación con nuevos años.

La relación estadística océano–clima **no es causalidad** demostrada, no infiere incidencia de Botrytis, ni una categoría de El Niño Costero. El uso de datos NOAA observados del mes de origen incluye riesgo de disponibilidad retrospectiva (*vintage bias*).

## 7. Artefactos técnicos ya ejecutados

- [Motor de evaluación regional](modelos/benchmark_impacto_regional_8d.py): descarga multisitio Open-Meteo, contraste de unidades y fechas completas, climatologías y evaluación.
- [Workflow de ejecución](.github/workflows/oaf_impacto_regional_8d.yml): comprobación sintética y evaluación ERA5. Se ajustó el proveedor a **consulta multicoordenada** al detectar un límite de solicitudes y se conservó rechazo completo de fechas/variables inválidas. Ejecución final **success**.
- [Serie de las cuatro localidades en CSV](datos/lambayeque_mensual_era5_8d.csv).
- [Métricas por sitio, variable y horizonte](datos/benchmark_impacto_lambayeque_8d.json).
- [1548 predicciones de prueba con observaciones y errores](datos/benchmark_impacto_lambayeque_8d_prueba.csv).
- [Motor de remuestreo temporal](modelos/robustez_impacto_regional_8d.py), [workflow](.github/workflows/oaf_robustez_impacto_8d.yml) y [JSON de intervalos](datos/robustez_impacto_regional_8d.json). Automatización inicial **success**.
- [Panel de consulta en Datos climatológicos](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#clima), con filtros localidad, temperatura/lluvia/radiación y horizonte.
- Este trabajo **no ha modificado** las emisiones selladas oceánicas de Fase 8A, las evaluaciones de 8B/8C ni los modelos fitosanitarios 7A–7C.

## 8. Futuro trabajo (Fase 8E)

1. Investigar la predicción de **temperatura local** con emisión verdaderamente **prospectiva**, registrando fecha y variables disponibles antes de predecir, empezando por las localidades con señal favorable. Confirmar habilidad durante varios ciclos e impactos ENSO diferentes.
2. Comparar cada estimación contra **estaciones SENAMHI y sensores regionales** con control de calidad, representatividad de celda, localidades y periodos. No tratar ERA5 como verdad instrumental.
3. Para la **lluvia**, evaluar modelos adecuados para distribución sesgada y muchos ceros: pronóstico de ocurrencia y magnitud por separado, precipitación CHIRPS u otra observación independiente, y métricas por temporada lluviosa; predefinir los modelos sin escoger uno retrospectivamente entre decenas.
4. Para **radiación**, probar nubosidad y señales locales, incluyendo observación de estación o satélite y errores por estación del año, sin atribuir a Niño 1+2 una mejora que el benchmark no detectó.
5. Estudiar señales ENFEN/ICEN como **contexto oficial** y experimentos de dependencia temporal, sin declarar pronósticos o alertas ENFEN desde un modelo del OAF.
6. Mantener **1996–2025** como normal regional descriptiva de 30 años y publicar, cuando se calcule correctamente, la referencia **1991–2020** como comparación OMM.
7. Retomar validación biológica de Botrytis y enfermedades de vid cuando existan **evaluaciones fitosanitarias reales y datos de microclima**. No confundir meteorología favorable con infección.

**Decisión científica al terminar 8D:** se conserva la variante regional como experimento transparente, sin recomendaciones agrícolas automáticas. La señal de temperatura merece vigilancia y comprobación verdaderamente prospectiva; la lluvia y la radiación requieren modelos y validaciones diferentes.
