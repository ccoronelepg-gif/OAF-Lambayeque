# OAF-Lambayeque | Fase 3T: robustez temporal y protocolo de validacion independiente

> **Evaluación retrospectiva**, NO pronóstico ni validación independiente.
> PISCOp v3.0 y CHIRPS v3 mezclan datos de estaciones meteorológicas.
> Las ubicaciones históricas precisas de estaciones siguen pendientes de verificar.

## Auditoría realizada

- 1 109 meses-estación completos comparados con los mismos tres productos.
- 3 327 pares de estimación-observación, 1996–2015.
- Año evaluable: **al menos 9 meses observados completos** en cada estación.
- Comparación año por año del MAE (no usar valores anuales incompletos como lluvia total).
- Re-muestreo exploratorio por bloques anuales con 2 000 repeticiones y semilla fija.
- El intervalo de remuestreo refleja sensibilidad a los años observados, no independencia ni causalidad.

## Estabilidad de la diferencia de errores anuales (PISCOp frente a CHIRPS)

| Estación | Años evaluables | Meses | PISCOp mejor | CHIRPS mejor | Empates | Diferencia MAE CHIRPS − PISCOp (mm/mes) | Rango remuestreo 95 % |
|---|---:|---:|---:|---:|---:|---:|---|
| Cayaltí | 20 | 235 | 19 | 1 | 0 | 1.888 | [1.391; 2.318] |
| Cueva Blanca | 18 | 215 | 9 | 9 | 0 | 1.193 | [-2.956; 6.569] |
| Jayanca (La Viña) | 18 | 212 | 18 | 0 | 0 | 6.161 | [3.187; 11.055] |
| Lambayeque | 16 | 191 | 16 | 0 | 0 | 2.463 | [1.446; 4.063] |
| Reque | 20 | 233 | 20 | 0 | 0 | 1.963 | [1.404; 2.672] |

## ¿Qué no demuestra este ejercicio?

- Comparar distintos años NO elimina la dependencia de estaciones en la elaboración de CHIRPS o PISCOp.
- El intervalo es una exploración estadística por año, no un ensayo espacial fuera de muestra.
- No hay suficientes estaciones certificadas para extrapolar a parcelas agrícolas ni demostrar errores regionales.
- Pueden existir años incompletos y el mínimo de 9 meses es una regla de inclusión, NO un año de lluvia completa.
- Las muestras de Cueva Blanca y estaciones costeras tienen régimen climático y representatividad espacial distintos.

## Independencia externa: evaluación documental actual

**0 de 15 combinaciones estación-producto tienen independencia externa comprobada documentalmente**.
Esto NO significa que todas las estaciones estén incorporadas en cada producto; significa que aún no se ha acreditado si están o no.
Matriz: datos/trazabilidad_independencia_3t.csv.

## Requisitos para afirmar validación independiente

1. Identificar para cada serie instrumental original su código, tipo, ubicación y fechas de operación según SENAMHI.
2. Solicitar al equipo de PISCOp v3.0 y al CHC los inventarios de pluviómetros incorporados y el periodo de uso por estación.
3. Obtener estaciones excluidas de entrenamiento/calibración y cotejar las coordenadas correctas para el mismo periodo.
4. Repetir análisis con estaciones independientes por región/altitud, períodos coincidentes y métricas pareadas.
5. Incorporar 2016–2025 de estaciones certificadas si están disponibles; no inferir registros faltantes.
6. Publicar solo resultados debidamente identificados como retrospectivos, independientes comprobados o exploratorios.

## Fuentes metodológicas

- SENAMHI, PISCOp v3: https://www.gob.pe/institucion/senamhi/noticias/1398654-piscop-v3-0-la-nueva-referencia-de-datos-de-precipitacion-para-la-gestion-hidrica-y-el-monitoreo-climatico-en-el-peru
- CHIRPS3, artículo científico 2026: https://www.nature.com/articles/s41597-026-07096-4
- Descarga de datos SENAMHI con registro: https://www.gob.pe/9312-conocer-los-datos-hidrometeorologicos-del-peru-descargar-los-datos-meteorologicos
- Código de análisis: scripts/auditoria_3t_robustez.py
- Resultados: datos/mae_estacion_anio_3t.csv, datos/comparacion_anual_piscop_chirps_3t.csv, datos/resumen_robustez_3t.csv, datos/estado_3t.json.

