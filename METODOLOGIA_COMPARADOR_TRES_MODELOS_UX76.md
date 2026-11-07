# OAF Lambayeque · UX76 · Tres referencias en web y aplicación PWA

**Implementación:** 7 de noviembre de 2026. Sitio y aplicación instalable usan los mismos recursos web; no existe una compilación móvil independiente.

## 1. Tres referencias visibles permanentemente

| Referencia | Qué representa | Pronóstico meteorológico futuro |
|---|---|---|
| **ERA5** (verde) | Climatología diaria 1996–2025 y mensual 1996–2020: media histórica para cada fecha/mes. ERA5 es **reanálisis retrospectivo** | **No**. Es un pronóstico estadístico de referencia o expectativa climatológica, no un modelo numérico futuro de ERA5 |
| **Open-Meteo** (azul) | Pronóstico diario actual; mensual procedente de ECMWF SEAS5 mediante Open-Meteo | **Sí**, con horizontes, resoluciones e incertidumbres de su proveedor |
| **Random Forest** (morado) | Pronóstico experimental OAF emitido por la versión RF incumbente | **Sí, experimental**: disponible solo para cuatro localidades regionales, sin validez parcelaria ni alertas |

Las tres aparecen en leyendas y tarjetas de la web y de su instalación PWA. Cuando un origen falla o la fecha no coincide con la emisión, se indica **sin dato** y no se inventan curvas. Los gráficos semanales son de **7 días**, los mensuales de **6 meses completos**.

## 2. ¿Cuál es el modelo más certero?

Se distingue entre **precisión retrospectiva** y **precisión prospectiva de emisiones originales**:

1. **Prueba retrospectiva 2025**: el ERA5 climatológico tiene menor MAE que el RF incumbente tanto en lluvia como Tmax; Open-Meteo no tiene pronósticos as-issued históricos archivados comparables para ese conjunto.
2. **Prueba retrospectiva 2026**: entre ERA5 climatológico y RF incumbente, el RF presentó menor MAE en ambas variables; Open-Meteo tampoco tiene el mismo historial de emisiones.
3. **Comparación triple prospectiva:** el flujo UX74/UX76 guarda RF y Open-Meteo tal como se emitieron, junto a la **climatología ERA5 congelada al emitir**, y los contrasta después contra ERA5 reanalizado, sin introducir información de días futuros. Se requieren **≥14 emisiones completas de siete días en la misma localidad y variable** para mostrar un **líder provisional** de los tres; antes se explica que no se puede elegir.

**No se afirma un ganador universal ni porcentajes de certeza inventados.** Los indicadores regionales no acreditan precisión de una finca. La referencia contra ERA5 posterior **no sustituye** observaciones independientes de estaciones SENAMHI.

## 3. Estado del entrenamiento UX75

El experimento multivariable directo UX75 utilizó 2024 para selección, 2025 y 2026 como pruebas independientes, y reentrenó el candidato final con ERA5 hasta **2026-10-31**. Su mejora en Tmax fue parcial: MAE **1,0787 → 1,0113 °C** (2025) y **1,3043 → 1,1088 °C** (2026), pero la climatología aún fue mejor en Tmax 2025. El candidato de lluvia **no** mejoró sistemáticamente. La interfaz por ahora continúa mostrando como RF el **incumbente**, no el nuevo candidato, ya que no se demostraron criterios suficientes de promoción. Informe detallado: `INFORME_REENTRENAMIENTO_RF_UX75.md`.

## 4. Arquitectura y verificación

- `assets/oaf-ux15-rf-salidas.js`: gráficos semanales y mensuales con las tres series fijas; referencias faltantes como NaN, nunca imputadas.
- `assets/oaf-ux76-ranking-modelos.js`: tarjetas y panel «cuál fue más certero», comparación retrospectiva reciente y triple provisional prospectiva por localidad.
- `assets/oaf-ux76-ranking-modelos.css`: diseño responsive.
- `scripts/seguimiento_rf_ux74.py`: congela los tres orígenes en el momento de emisión y verifica madurez; nunca usa emisiones emitidas como etiquetas de entrenamiento.
- `datos/seguimiento_rf_ux74/climatologia_diaria_era5_ux76.json`: cache científico de referencia fija 1996–2025, si descarga ERA5 se completó.
- `datos/seguimiento_rf_ux74/emisiones.json`: historial de predicciones y errores, con distinción de referencias.
- `index.html` y `sw.js`: instalación PWA con versión UX76 y precarga de recursos esenciales; archivos de pronósticos JSON consultados solo por red, para evitar datos caducados.
- `tests/oaf-smoke.mjs` y `tests/ux73_navegador.cjs`: regresión Node y Playwright.

## 5. Límites reconocidos

El histórico disponible en el momento de implementación contiene una sola fecha archivada sin verificación futura madura. **No hay todavía un «modelo más certero entre los tres» comprobado prospectivamente.** El panel lo indica de forma explícita y continuará evaluando al crecer el historial.

No se ha realizado calibración instrumental formal SENAMHI, ni validación de inundaciones o riesgo fitosanitario derivada del desempeño de estos tres.
