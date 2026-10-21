# Fase 10P: dos gráficos comparativos y ajuste reproducible RF — 21/10/2026

## Organización de Predicciones y Anomalías

1. Se conserva la cartografía interactiva de 42 geometrías 9K con selector de pisos de relieve al inicio del bloque de análisis propio.
2. **Gráfico único semanal** en `oaf-ux14-weekchart`: misma fecha local para la referencia de **Open-Meteo** y el candidato **Random Forest 10O**, con selector de localidad y variable (lluvia o temperatura máxima). Si no hay coincidencia exacta de fecha o datos, no se corre la serie arbitrariamente: los puntos faltantes no se interpolan. Se muestra diferencia absoluta media entre las dos predicciones **sin denominarla error**. **OpenWeather no está integrado** porque necesita una clave API particular; no corresponde renombrar a Open-Meteo como OpenWeather.
3. **Gráfico único mensual** en `oaf-ux14-monthchart`, con selección de vista:
   - Evaluación retrospectiva **2021–2025** de los cinco paisajes experimentales de OAF: lluvias observadas CHIRPS, modelo RF 10K y climatología sectorial.
   - Proyección **noviembre 2026–abril 2027** por localidad: RF candidato 10O y climatología de referencia calculada con ERA5 1996–2020 para el mismo mes y localidad. No se presenta como medición observada o validación a seis meses.
4. El **bloque independiente de meses siguientes** presenta seis tarjetas con precipitación y temperatura media por cada localidad: Chiclayo, Jayanca, Motupe y Olmos. No dibuja un gráfico redundante.
5. Ambos horizontes conservan metadatos, diferencias de fuente, pruebas temporales, carácter experimental y acceso al archivo técnico.

## Cambios del algoritmo RF original del OAF

Archivo fuente: `modelos/pronostico_rf_experimental_ux15.py`. El flujo de `.github/workflows/oaf_rf_experimental_ux15.yml` vuelve a entrenar un candidato en GitHub Actions con datasets históricos ERA5 disponibles.

- Se incorporaron cuatro variables indicadoras de localidad en ambos modelos para diferenciar Chiclayo, Jayanca, Motupe y Olmos.
- Se corrigió la comparación diaria frente a una referencia de climatología **local por mes**, estimada sin usar el año de prueba 2025; no se evalúa exclusivamente contra una mediana global.
- Para el RF mensual se separó entrenamiento hasta 2018, selección de parámetros y ponderación RF/climatología usando solo 2019–2020, evaluación retenida 2021–2025, y reentrenamiento con datos existentes para generar las salidas futuras.
- Selección: número de árboles 160/200, profundidad máxima 8/10/14, hojas mínimas 12/7/4, y pesos RF candidatos 0,2/0,4/0,6/0,8/1. La referencia local y su MAE se muestran separadamente. No se seleccionó ningún parámetro usando etiquetas del test 2021–2025.
- Un peso RF de 1 significa que la mezcla seleccionada NO corrige con climatología. La climatología continúa como línea de referencia, no salida del RF.

## Resultados verificados en la ejecución del 21/10/2026

| Variable y periodo | MAE RF previo | MAE RF ajustado | MAE climatología local | Interpretación |
|---|---:|---:|---:|---|
| Lluvia diaria, prueba 2025 | 2,33 mm/día (modelo con indicador local previo al nuevo baseline) | 2,33 mm/día | 3,06 mm/día | RF mejora referencia estacional en evaluación retrospectiva de 1 paso |
| T. máxima diaria, prueba 2025 | 0,83 °C | 0,83 °C | 1,00 °C | RF mejora referencia estacional en evaluación retrospectiva de 1 paso |
| Lluvia mensual, prueba 2021–2025 | 46,93 mm/mes | **44,09 mm/mes** | **42,49 mm/mes** | Mejora RF respecto a su versión anterior, pero todavía NO supera a la climatología local |
| T. media mensual, prueba 2021–2025 | 0,46 °C | 0,47 °C | 0,76 °C | La variante RF es ligeramente peor que la anterior para temperatura, aunque mejor que climatología |

La configuración elegida con validación 2019–2020 fue **160 árboles, profundidad 8, hojas mínimas 12**, con **peso RF 1,0** para lluvia. Estos valores son de evaluación retrospectiva con rezagos reales, **no** prueban destreza de secuencias autoregresivas a 7 días ni 6 meses. Un modelo para intensidades extremas de El Niño requerirá más años Niño significativos, predictores oceánicos *disponibles antes de la fecha de emisión*, validación as-issued y observaciones instrumentales independientes.

## Integridad

La validación del flujo revisa estados experimentales, continuidad de fechas diarias, las cuatro localidades, seis meses de salidas, unidades, peso RF y periodos de selección; el historial se conserva en JSON. No se activan alertas públicas ni se certifican probabilidades. El gráfico semanal NO es una comparación con lluvia efectivamente medida; comparar dos pronósticos y obtener una diferencia pequeña no prueba cuál acierta más.

## Enlaces
- [Portal Predicciones y Anomalías](https://ccoronelepg-gif.github.io/OAF-Lambayeque/#autor)
- [Resultados RF candidato del día](datos/rf_experimental_ux15.json)
- [Script Python RF](modelos/pronostico_rf_experimental_ux15.py)
- [Fuente ERA5 / API histórica Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)
- [Metadatos 10K](datos/ecopaisajes_10k/evaluacion_ecoclimatica_10k.json)
