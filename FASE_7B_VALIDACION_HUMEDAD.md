# OAF-Lambayeque — Fase 7B: verificación del indicador meteorológico de humedad para Botrytis de arándano

**Autor:** Carlos E. Coronel García, Ingeniero Agrónomo.  
**Fecha de ejecución:** 15/10/2026 UTC.  
**Estado:** evaluación de capacidad para predecir **humedad atmosférica prolongada**, NO validación epidemiológica o diagnóstico de Botrytis.

## 1. Pregunta científica

¿El indicador experimental de Fase 7A (humedad relativa a 2 m **superior a 90 % durante seis o más horas seguidas**) realmente anticipa los días en que ocurren esas condiciones meteorológicas? ¿Con qué frecuencia genera falsas señales u omite episodios? La pregunta es necesaria **antes** de usar el indicador como componente de cualquier modelo fitosanitario en Lambayeque.

La presencia de *Botrytis cinerea* e infección del arándano depende de más factores que HR pronosticada: humectación efectiva de pétalos/tejidos, etapa fenológica, patógeno y condiciones del cultivo. [UF/IFAS, Botrytis Blossom Blight of Southern Highbush Blueberry](https://ask.ifas.ufl.edu/publication/PP119) y [UF/IFAS Blueberry IPM Guide](https://ask.ifas.ufl.edu/publication/HS380). La [Universidad de Maine](https://extension.umaine.edu/blueberries/resources/212-botrytis-blight-control-for-wild-blueberries/) explica la dependencia de infección floral con horas reales de humectación y temperatura; esos umbrales no se pueden aplicar automáticamente a HR del aire de una cuadrícula.

## 2. Evaluación retrospectiva, utilizando fuentes reales

- **Fuente del pronóstico anterior al evento:** [Open-Meteo Previous Model Runs API](https://open-meteo.com/en/docs/previous-runs-api), `relative_humidity_2m_previous_day1`, horizonte nominal 24 h antes de la validez de cada hora.
- **Referencia de comparación posterior:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), **ERA5** `relative_humidity_2m` horaria, en la misma fecha y zona horaria `America/Lima`. ERA5 es reanálisis, NO una estación meteorológica del SENAMHI ni un sensor agrícola.
- **Periodo completamente transcurrido:** 2026-01-01 a 2026-09-30; **273 días × cuatro localidades = 1.092 jornadas** y **6.552 horas alineadas por localidad**. Criterio de HR predefinido por el ensayo original, sin modificarlo o calibrarlo con este conjunto de prueba.
- Un episodio se detecta cuando se completa la sexta hora consecutiva con HR >90 %. La secuencia puede atravesar medianoche; el día se etiqueta positivo si durante él se alcanza la sexta hora o continúa ese tramo. Días incompletos se excluyen; las fechas se emparejan exactamente, no por posición.
- Se registran verdaderos positivos (señal en pronóstico y ERA5), falsos positivos (solo en pronóstico), falsos negativos (solo ERA5) y verdaderos negativos (ninguno). **Esta tabla NO se refiere a presencia/ausencia de Botrytis**.

### Resultados reales de la primera evaluación

| Localidad | Días | Pronóstico + | ERA5 + | Coincidencias positivas | Falsas señales | Omisiones | Coincidencias negativas | Precisión positiva | Sensibilidad |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Chiclayo | 273 | 38 | 12 | 7 | 31 | 5 | 230 | 18.4 % | 58.3 % |
| Jayanca | 273 | 20 | 34 | 16 | 4 | 18 | 235 | 80.0 % | 47.1 % |
| Motupe | 273 | 128 | 34 | 17 | 111 | 17 | 128 | 13.3 % | 50.0 % |
| Olmos | 273 | 167 | 37 | 27 | 140 | 10 | 96 | 16.2 % | 73.0 % |

**Interpretación:** frente al reanálisis ERA5, la señal HR >90 % y ≥6 h presentó demasiadas detecciones positivas no corroboradas en Motupe (111) y Olmos (140). Jayanca mostró mayor precisión positiva, pero omitió 18 días con esa condición. Chiclayo tuvo pocos días positivos reales, por lo que es crucial no interpretar la exactitud global sin observar la matriz completa.

La cifra «precisión positiva» es la fracción de señales meteorológicas positivas pronosticadas corroboradas por ERA5; «sensibilidad» es la fracción de señales meteorológicas positivas de ERA5 identificadas por el pronóstico. **Ninguna es probabilidad de enfermedad ni tasa de infección.**

**Limitación geográfica adicional:** las celdas originales de pronóstico son más pequeñas que las celdas ERA5; por ejemplo Motupe devuelve cuadrícula aproximada **-6.151142, -79.69925**, frente a **-6.25, -79.75** en ERA5. La diferencia espacial puede influir en falsos positivos y errores. Hay que considerar este sesgo antes de atribuir toda discrepancia al pronóstico.

**Conclusión técnica:** no está justificado publicar el indicador como alerta de Botrytis o estimador de infección en ningún distrito. Primero debe mejorar la representatividad y demostrar capacidad para pronosticar el ambiente del cultivo y la enfermedad observada.

## 3. Verificación prospectiva de las propias emisiones del OAF

Para no depender únicamente de archivos reconstruidos, la Fase 7A guarda cada emisión horaria **antes de los días pronosticados**. Un segundo motor Fase 7B compara esas emisiones con ERA5 **solamente después de siete días de margen de publicación**.

- Primera emisión conservada: [15/10/2026](datos/patrones_botrytis_emitidos/2026-10-15.json).
- Pronósticos futuros de esa emisión: **16–22 octubre de 2026**.
- Primer día que puede verificarse: **2026-10-23**, sujeto a disponibilidad de ERA5.
- Primera ejecución real: **28 jornadas por sitio-horizonte archivadas; 0 elegibles; 0 verificadas**, estado **`pendiente_reanalisis`**. No hay aciertos ni falsos positivos prospectivos todavía.

El proceso evita cualquier comparación contra un valor histórico que todavía no exista; un conteo cero al inicio **no significa «sin humedad» ni «sin enfermedad»**.

## 4. Código y resultados auditables

- [Motor retrospectivo Python](modelos/validar_indicador_humedad_botrytis_7b.py).
- [JSON de matriz y métricas](datos/botrytis_indicador_7b_backtest.json).
- [CSV con las 1.092 jornadas clasificadas](datos/botrytis_indicador_7b_diario.csv).
- [Automatización y pruebas de regresión](.github/workflows/oaf_botrytis_7b_backtest.yml).
- [Verificador prospectivo Python](modelos/verificar_patrones_botrytis_emitidos_7b.py).
- [Workflow diario de verificación con demora](.github/workflows/oaf_botrytis_7b_prospectivo.yml).
- [Estado actual prospectivo JSON](datos/botrytis_humedad_7b_prospectivo.json).
- [Registro CSV prospectivo](datos/botrytis_humedad_7b_prospectivo.csv).
- [Visor en Cultivos → Predicción](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#riesgos): etiqueta claramente «evaluación meteorológica», no «precisión de Botrytis».

Ambas ejecuciones iniciales GitHub Actions terminaron en **success**, con autopruebas de episodios cruzando medianoche, horas faltantes y ausencia legítima de datos maduros.

## 5. Qué falta para una verdadera predicción de Botrytis — Fase 7C

La siguiente etapa debe utilizar registros de **parcelas reales** y no confundir reanálisis con mediciones instrumentales. Ya existe una [plantilla vacía con 25 variables](datos/plantilla_monitoreo_botrytis_arandano.csv), sin inventar observaciones.

Como mínimo se deben estudiar:
1. **Parcela, variedad, floración y tejidos expuestos**, manejo del riego y ventilación; la fenología cambia la susceptibilidad.
2. **Humectación foliar verdadera** mediante sensor o medición in situ, con hora y posición dentro del dosel; junto con temperatura, HR y, cuando sea posible, radiación y DPV de microclima.
3. **Presencia, incidencia y severidad diagnosticadas**, número de plantas/floraciones evaluadas y registro de fechas con resultados positivos y negativos, utilizando criterios comparables.
4. **Representatividad** espacial entre cuadrícula meteorológica y parcela; estratificar por estación/fenología y evitar que datos de la misma parcela/episodio se filtren entre entrenamiento y evaluación.
5. **Comparación de modelos:** referencia simple, criterio de HR, HR + lluvia/temperatura y modelos con humectación medida; evaluar precisión, sensibilidad, especificidad y calibración si posteriormente se generan probabilidades, siempre con validación por fecha y parcela.

Hasta entonces, la señal HR prolongada es **solo un antecedente meteorológico de investigación**, no una recomendación de fungicidas o alerta sanitaria.

**Principio de transparencia:** exhibir también falsos positivos, omisiones, periodos sin datos y limitaciones geográficas. Mantener diferenciadas las predicciones oceánicas de El Niño Costero, las anomalías agroclimáticas y las condiciones fitosanitarias del arándano.
