# Fase 9Y — Incertidumbre temporal y criterio de publicación (17/10/2026)

## Propósito
Después de 9X (transferencia a cinco bloques geográficos sin entrenamiento local), evaluar la **fiabilidad de las predicciones de precipitación** de Random Forest, GCN y climatología, sin confundir exactitud retrospectiva con habilidad operativa.

## Diseño de evaluación
- Unidad de análisis: pronóstico fechado por sector, piso ecológico, modelo y horizonte temporal. Registrar siempre emisión, fecha objetivo, origen y versión de datos. No combinar horizontes ni precipitación diaria/mensual.
- Separación estricta temporal: entrenar el predictor sin información del futuro; usar exclusivamente **2016–2020** para calibrar incertidumbre de predicciones generadas fuera de muestra, y **2021–2025** como prueba temporal. Si la matriz de predicciones 9X no contiene esas columnas o una predicción genuinamente anterior al dato observado, informar «no evaluable».
- Comparar con climatología del mismo sector y mes, calculada solo con datos accesibles hasta el corte correspondiente. No elegir el modelo por error calculado sobre el conjunto de entrenamiento.
- Por combinación modelo × piso ecológico × horizonte: intervalo conformal de residuos absolutos y cobertura observada; MAE, RMSE y sesgo en mm; resultados anuales separados, con evaluación expresa de 2023 y años ENSO. Presentar n, vacíos, cobertura y tamaño del intervalo.
- Separar la **generalización geográfica** de la validación temporal; cinco bloques geográficos de 9X no equivalen automáticamente a cinco pisos ecológicos. Evitar extrapolación de una estación a un bloque entero.
- Etiquetar validaciones contra CHIRPS/ERA5 como contrastes de rejilla, **no validaciones instrumentales independientes**. Exigir series de estación realmente no usadas por el producto predictor para cerrar esa brecha.

## Criterio de publicación
**NO activar alertas automáticas de El Niño, eventos extremos ni enfermedades** con resultados 9X/9Y por sí solos. Mostrar como «experimental» o «sin evidencia suficiente» cualquier predicción sin validación prospectiva e instrumental. Una cobertura nominal del 90 % no garantiza el 90 % bajo dependencia temporal, sesgo sistemático o cambio de régimen ENSO.

## Artefacto de evaluación
El módulo local `evaluacion_incertidumbre_9y.py` (entregado como descarga junto a esta fase) acepta un CSV con `fecha,sector,piso,modelo,observado_mm,pronosticado_mm` y produce JSON con indicadores por piso y año; **no usa datos ficticios ni activa alertas**. Requiere al menos 24 pares de calibración por combinación modelo y piso, umbral exploratorio que debe endurecerse con autocorrelación y eventos efectivos.

## Puertas para 9Z
1. Auditar el inventario de predicciones 9X, distinguiendo hindcasts, forecasts y fechas de emisión.
2. Ejecutar calibración contra predicciones fuera de muestra y comparador climatológico idénticamente fechado.
3. Obtener datos independientes por valle/sector y por pisos altoandinos donde falten estaciones.
4. Someter a revisión la tasa de eventos extremos omitidos y el comportamiento en episodios ENSO antes de uso para productores.

**Estado:** protocolo y evaluador de incertidumbre listos; **no se reclaman coberturas, MAE ni un modelo ganador calculados a partir de observaciones que no fueron suministradas en un CSV válido.**
