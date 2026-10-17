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

## Primeros resultados del reentrenamiento (GitHub Actions)
La ejecución de entrenamiento sobre cinco bloques terminó y comunicó los siguientes valores retrospectivos sobre los **mismos 39 sectores × 60 meses (2021–2025)**:

| Modelo | MAE anterior 9X, mm | MAE nuevo 10C, mm | Diferencia, mm |
|---|---:|---:|---:|
| Random Forest | 17,1634 | 18,1443 | +0,9809 |
| GCN | 18,6207 | 17,6429 | −0,9778 |
| Climatología por piso | 20,3708 | 20,3708 | 0,0000 |

En **2023**, tras calibrar en 2019–2020, la cobertura observada de intervalos nominales 90 % fue **79,49 % para GCN**, **85,04 % para Random Forest** y **89,96 % para climatología por piso**. Ninguno de esos tres modelos alcanzó el 90 % ese año.

En **2021–2025**, sobre **137** observaciones sector-mes con lluvia ≥100 mm, la regla exploratoria sobre pronóstico puntual detectó **32** para GCN, **13** para Random Forest y **34** para climatología por piso. Las series vecinas no representan 137 fenómenos independientes.

**Advertencia de inferencia:** entre 9X y 10C cambian simultáneamente **las variables rezagadas y el periodo de selección de hiperparámetros** (9X 2016–2020 frente a 10C 2016–2018). Por ello, el contraste identifica el resultado de **dos diseños distintos**, no el efecto causal aislado de eliminar t−1. Una futura comparación factorial con idéntico periodo de tuning es necesaria.

**Estado de publicación: FINALIZADO.** Entrenamiento, seis pruebas, controles SHA y guardado del JSON/CSV en GitHub completados con éxito. La [ejecución publicada](https://github.com/ccoronelepg-gif/OAF-Lambayeque/actions/runs/39080124008) conservó todos los artefactos. La primera corrida había mostrado GCN=17,6452 mm y la ejecución final 17,6429 mm; se observa una diferencia numérica de 0,0023 mm entre entornos/corridas, por lo que conviene fijar versiones e imagen computacional para garantizar reproducción bit a bit.

**Incertidumbre espacial:** el remuestreo exploratorio de cinco bloques para la diferencia GCN menos RF en MAE tiene intervalo 95 % **[−1,0931; +0,2103] mm**, que incluye el cero. No se ha demostrado ventaja generalizable concluyente entre los modelos ni validez predictiva prospectiva.

## Resultados y ejecución
**Resultados verificados en GitHub Actions y publicados en el repositorio.** La corrida genera:
- [Métricas completas 10C](datos/reentrenamiento_10c/evaluacion_lag2_10c.json).
- [Predicciones de calibración 2019–2020](datos/reentrenamiento_10c/predicciones_calibracion_lag2_10c.csv).
- [Predicciones de prueba 2021–2025](datos/reentrenamiento_10c/predicciones_prueba_lag2_10c.csv).
- [Bloques espaciales y selección por bloque](datos/reentrenamiento_10c/bloques_geograficos_10c.json).
- [Código](modelos/reentrenamiento_lag2_10c.py), [pruebas](tests/test_reentrenamiento_10c.py), [automatización](.github/workflows/oaf_10c_reentrenamiento.yml), [panel interactivo](evaluacion-lag2.html).

## Fase 10D
Evaluar calibración robusta según régimen (ENSO/costa/altitud), establecer base observacional independiente, incorporar pronósticos reales con sellos de tiempo, y distinguir condiciones necesarias para sistemas de alerta de arándano y vid de predicciones físicas de precipitación.
