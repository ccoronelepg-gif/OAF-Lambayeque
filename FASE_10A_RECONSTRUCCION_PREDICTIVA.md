# Fase 10A — Reconstrucción y auditoría territorial de predicciones (17/10/2026)

## Resultado comprobado
Se leyó íntegramente el archivo original `datos/generalizacion_9x/predicciones_sector_bloque_9x.csv`, **11.700 filas**, cinco modelos y **39 sectores × 60 meses** (enero 2021 a diciembre 2025). Sus **2.340 pares sector–mes** tienen los cinco modelos, sin duplicados, observaciones divergentes ni valores inválidos. Las métricas recalculadas reproducen las informadas en 9X.

| Modelo | MAE mm | RMSE mm | Sesgo mm |
| --- | ---: | ---: | ---: |
| Random Forest | 17,1634 | 39,0143 | -11,9889 |
| GCN (grafo) | 18,6207 | 41,4780 | -11,3100 |
| Climatología por piso | 20,3708 | 39,9676 | -2,0955 |
| Persistencia anual | 21,8341 | 47,2184 | -1,7163 |
| Climatología global | 24,3027 | 45,0520 | -1,6765 |

**29 de 39 sectores:** RF tiene menor MAE que GCN. **21 de 39:** RF tiene menor MAE que la climatología por piso. **14 de 39:** RF tiene el menor MAE de los tres modelos comparados. No es válido inferir superioridad uniforme desde el MAE agregado.

**Año 2023 (todos los sectores):** la climatología por piso presenta **29,0583 mm de MAE**, frente a **31,6858 mm de GCN** y **31,7230 mm de RF**. En montaña media, RF tiene MAE **46,6867 mm**, frente a **39,7768 mm** de la climatología por piso. Esto exige valorar extremos/anos anómalos por separado.

Los bloques geográficos 0–4 arrojan MAE RF de **31,3140; 10,0148; 13,1888; 4,4696; 14,2713 mm** respectivamente. Son distribuciones heterogéneas con distintos regímenes de lluvia, no un ranking de dificultad geográfica demostrado.

## Limitaciones y medidas de seguridad
1. **No hay instantáneas 'as-issued'.** CHIRPS v3 FINAL y las geometrías son retrospectivas. La última versión del mes anterior no siempre está disponible al comienzo del mes objetivo: CHIRPS v3 Final suele publicarse en la tercera semana del mes siguiente. No inventar `fecha_emision`. Véase [Climate Hazards Center](https://www.chc.ucsb.edu/data/chirps3).
2. **No se pueden aplicar intervalos conformales 9Y como validados.** La matriz 9X archivada solo incluye 2021–2025. En el diseño original 2016–2020 se utilizó para selección de hiperparámetros y early stopping; reutilizarlo sin reacondicionar entrenamiento y separar una calibración independiente introduce sesgo.
3. **Los cinco bloques de holdout no son pisos ecológicos certificados.** Hay al menos un sector categorizado `cota_negativa_revisar`; los polígonos fueron construidos retrospectivamente.
4. **No hay contraste instrumental independiente ni evaluación prospectiva**; CHIRPS contiene pluviómetros. Las cifras de habilidad relativas a CHIRPS no deben presentarse como exactitud de campo.
5. **No activar alertas de lluvia, El Niño o enfermedades** ni declarar ganador *operativo*.

## Recursos reproducibles
- [Diagnóstico calculado directamente de 11.700 filas de 9X](datos/integracion_10a/diagnostico_reconciliado_10a.json).
- [Archivo de predicciones 9X](datos/generalizacion_9x/predicciones_sector_bloque_9x.csv).
- [Ficha de bloques espaciales 9X](datos/generalizacion_9x/bloques_geograficos_9x.json).
- [Panel experimental de evaluación territorial](evaluacion-territorial.html).
- Código y tests 10A disponibles en el paquete entregado en la conversación.

## Decisión para 10B
Recalcular predicciones con un calendario genuino de disponibilidades: entrenamiento 1997–2015, ajuste 2016–2018, calibración estrictamente externa 2019–2020 y prueba 2021–2025 **solo si se recuperan las versiones de entrada realmente disponibles**. Auditar extremos 2023/ENSO, sensibilidad por zona y estaciones no incorporadas en CHIRPS; no afirmar habilidad certificada hasta completar.
