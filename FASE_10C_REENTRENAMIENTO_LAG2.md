# Fase 10C — Reentrenamiento con rezagos de precipitación y calibración independiente

**Fecha:** 17 de octubre de 2026 · **Estado:** motor/QA CI publicado; los valores de reentrenamiento corresponden exclusivamente a la ejecución de GitHub Actions y al JSON generado, nunca a cifras supuestas.

## Pregunta científica
¿Se mantiene la habilidad retrospectiva de la GCN y Random Forest al suprimir el valor CHIRPS v3 FINAL del mes inmediatamente anterior al mes pronosticado, que usualmente no está disponible durante la emisión al comienzo del mes?

Según el [Climate Hazards Center](https://www.chc.ucsb.edu/data/chirps3), CHIRPS v3 FINAL se publica generalmente en la **tercera semana del mes siguiente**. Los datos CHIRPS v3 FINAL archivados en este repositorio son versiones **reprocesadas retrospectivamente**, y NO demuestran qué versión estaba disponible en una fecha original de 2021–2025.

## Cambios implementados
1. Predictores de precipitación **t−2, t−3, t−4, t−6 y t−12**, en lugar de incluir t−1. La media móvil utiliza únicamente **t−4, t−3 y t−2**. Las tres variables territoriales, seno y coseno estacionales y características vecinales se conservan; los vecinos usan también solo rezagos admisibles.
2. **5 bloques espaciales excluidos del entrenamiento** con geometrías y centroides reproducibles de 9X. Ningún valor objetivo de los sectores reservados entra al ajuste de RF ni de GCN; se pueden emplear sus rezagos históricos (si se conocieran en el instante de predicción).
3. Entrenamiento: **enero 1997–diciembre 2015** (228 meses). Selección de hiperparámetros y parada anticipada: **enero 2016–diciembre 2018** (36 meses, solo sectores de entrenamiento). Calibración de intervalos en sectores reservados: **enero 2019–diciembre 2020** (24 meses). Prueba posterior: **enero 2021–diciembre 2025** (60 meses).
4. Calibración al 90 % **nominal**, usando el 23.º residuo absoluto ordenado de 24 (por sector y modelo); estimación de cobertura para 2021–2025 y especialmente 2023, por pisos altitudinales.
5. Comparación legítima de ambos diseños sobre el **mismo sector, mes, modelo y CHIRPS observado**: MAE lag t−1 de 9X frente a MAE lag t−2 de 10C. Calibraciones no son directamente comparables: 10B calibró 2021–2022; 10C calibra 2019–2020.
6. Reproducibilidad: validación SHA256 de la serie fuente 9W, de predicciones 10C y de los datos originales 9X, pruebas unitarias de ausencia de fuga de t−1, salidas CSV/JSON, ejecución CI de cinco bloques.

## Advertencias estructurales
- **No es una reconstitución as-issued:** aunque la selección t−2 respete la latencia típica, el archivo histórico CHIRPS v3 FINAL usado en los entrenamientos contiene revisiones y productos que no necesariamente existían en esas fechas. Una evaluación histórica verdaderamente operativa requiere vintages de archivo contemporáneos o un ensayo prospectivo desde 2026.
- La GCN **es convolución en grafos**, no CNN convencional bidimensional.
- Los sectores 9K son **zonas exploratorias** y los pisos no han obtenido certificación ecológica; existen cotas anómalas por revisar.
- Los intervalos no tienen garantía del 90 % bajo autocorrelación, dependencia espacial o alteraciones como El Niño 2023.
- El contraste es contra CHIRPS, que combina estaciones pluviométricas. **No se ha validado instrumentalmente** y **no se emitirán alertas automáticas**.
- La calificación como «mejor» de un modelo debe atender también errores en episodios extremos, sesgos y cobertura espacial, nunca solo al MAE agregado.

## Resultados y ejecución
**Resultados verificables solo cuando termine la ejecución automática.** La corrida genera:
- [Métricas completas 10C](datos/reentrenamiento_10c/evaluacion_lag2_10c.json).
- [Predicciones de calibración 2019–2020](datos/reentrenamiento_10c/predicciones_calibracion_lag2_10c.csv).
- [Predicciones de prueba 2021–2025](datos/reentrenamiento_10c/predicciones_prueba_lag2_10c.csv).
- [Bloques espaciales y selección por bloque](datos/reentrenamiento_10c/bloques_geograficos_10c.json).
- [Código](modelos/reentrenamiento_lag2_10c.py), [pruebas](tests/test_reentrenamiento_10c.py), [automatización](.github/workflows/oaf_10c_reentrenamiento.yml), [panel interactivo](evaluacion-lag2.html).

## Fase 10D
Evaluar calibración robusta según régimen (ENSO/costa/altitud), establecer base observacional independiente, incorporar pronósticos reales con sellos de tiempo, y distinguir condiciones necesarias para sistemas de alerta de arándano y vid de predicciones físicas de precipitación.
