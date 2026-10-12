# Estado de avance — OAF-Lambayeque

Registro de continuidad del proyecto (11 de octubre de 2026).

## Objetivo
Desarrollar el Observatorio Agroclimático y Fitosanitario de Lambayeque, Perú, con análisis meteorológico regional, precipitaciones y eventos El Niño, comparación de fuentes, pronósticos y un futuro módulo de riesgo fitosanitario del **arándano** usando datos reales de campo.

## Decisiones de trabajo
- Periodo climatológico principal: **1996–2025**.
- Fuentes climáticas trabajadas: **ERA5-Seamless** (Open-Meteo) y **PISCOp v3.0** (consultado por servicio de terceros).
- Puntos exploratorios iniciales: **Olmos, Chiclayo, Zaña e Incahuasi**. Son puntos de análisis, no equivalen a estaciones meteorológicas ni representan por sí solos todo el departamento.
- Comparar estimaciones de rejilla con observaciones SENAMHI antes de declarar precisión, sesgos corregidos o construir alertas operativas.
- Los archivos originales de estaciones se conservan sin modificar; los códigos de ausencia de datos, como `-99.9`, se tratan como faltantes.
- **Preferencia de trabajo del proyecto:** continuar directamente los avances técnicos, **sin preguntas ni ejercicios** para el usuario.

## Análisis completados
1. Descargas y análisis históricos ERA5-Seamless de Olmos 1996–2025 y serie regional 2023.
2. Comparación ERA5–PISCOp para Olmos 1996–2025. Promedio anual: ERA5 1 016,15 mm; PISCOp 267,61 mm. Correlaciones entre productos: Pearson 0,847; Pearson sin 1998 0,743; Spearman 0,781. **Estas correlaciones NO son una validación contra estaciones.**
3. Series mensuales PISCOp 1996–2025 para cuatro localidades iniciales; anomalías de precipitación en 2023 respecto a 1996–2025.
4. Recepción y procesamiento de cinco archivos de estaciones SENAMHI: **Jayanca, Cayaltí, Reque, Lambayeque y Cueva Blanca**. Auditoría inicial de cobertura diaria y datos faltantes. Estas descargas terminan entre 2014 y 2015 y no permiten comprobar directamente 2017, 2023 o 2025.
5. Análisis preliminar de lluvia observada en 1998 en las cinco estaciones; pendientes de verificación final los metadatos históricos exactos de ubicación y altitud.
6. Página web **v0.3**: archivo `index.html` subido a la rama `main`; GitHub Pages configurado. El flujo «pages build and deployment» finalizó con conclusión `success` (ejecución 38204198432).

## Web
- Repositorio: https://github.com/ccoronelepg-gif/OAF-Lambayeque
- Dirección de GitHub Pages: https://ccoronelepg-gif.github.io/OAF-Lambayeque/
- El sitio es actualmente un **prototipo histórico**, no un servicio de pronóstico operativo ni una alerta fitosanitaria validada.
- Al actualizar la web, conservar la misma URL y distinguir claramente datos observados, estimados y pronosticados.

## Siguiente etapa acordada
**Validación espacial y estadística de precipitación SENAMHI–PISCOp–ERA5**. Primero corroborar coordenadas y metadatos de las cinco estaciones; después extraer PISCOp y ERA5 en cada ubicación real, emparejar por fecha y evaluar solo periodos con observaciones válidas. Calcular sesgo, MAE, RMSE, correlación y cobertura; diferenciar validación dependiente cuando PISCOp haya utilizado estaciones en su construcción. Ampliar posteriormente registros recientes y cobertura espacial departamental; luego pronósticos y módulo fitosanitario de arándano.

## Entorno local
Se trabaja con VS Code/Jupyter dentro del proyecto `Proyecto_Agricultura_IA`, incluyendo `OAF_Lambayeque_Fase1.ipynb`, carpetas de datos, gráficos, modelos y resultados. El usuario solicitó y recibió orientación para habilitar **Auto Save** en VS Code (`afterDelay` = 1000 ms); este ajuste local no reemplaza la sincronización con GitHub.
