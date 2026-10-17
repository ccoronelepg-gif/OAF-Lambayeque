# Fase 9J — Auditoría de emisiones históricas (vintage) y puertas de validación prospectiva

**Corte reproducible:** 17 de octubre de 2026, zona `America/Lima`. **Objetivo:** separar las predicciones que fueron emitidas **antes del objetivo** de reanálisis, reconstrucciones históricas o estimaciones emitidas cuando el periodo ya estaba iniciado.

**Estado científico:** infraestructura 9J implementada; **cero** evaluaciones de habilidad prospectiva con datos de contraste temporalmente maduros. No se calcula MAE, RMSE, sesgo, probabilidad de enfermedad o capacidad operativa ante ausencia de referencia posterior.

## 1. Resultados de auditoría: líneas que no deben confundirse

### A. Pronósticos meteorológicos externos diarios

Archivos `datos/pronosticos_emitidos/2026-10-14.json` a `2026-10-17.json` guardados por el proceso 6F. **Cuatro emisiones** de Open-Meteo, **cuatro localidades (Chiclayo, Jayanca, Motupe y Olmos)** y **siete días futuros por localidad**: **112 registros localidad–día–emisión**. Estos registros pueden compartir una misma localidad-fecha válida; **no son 112 observaciones independientes**.

| Emisión local | Commit histórico donde quedó guardado el archivo | Primer día objetivo | Primera comparación autorizable* |
|---|---|---|---|
| 14/10/2026 | [79e92c9](https://github.com/ccoronelepg-gif/OAF-Lambayeque/commit/79e92c9aac669e37599e868ff371aa67d9799ec5) | 15/10/2026 | 22/10/2026 |
| 15/10/2026 | [864d2bc](https://github.com/ccoronelepg-gif/OAF-Lambayeque/commit/864d2bc94ea653ad51ecb11001e9decdee80268d) | 16/10/2026 | 23/10/2026 |
| 16/10/2026 | [699bd04](https://github.com/ccoronelepg-gif/OAF-Lambayeque/commit/699bd04852dce39e79140c37afcced9c38aa71) | 17/10/2026 | 24/10/2026 |
| 17/10/2026 | [02445eb](https://github.com/ccoronelepg-gif/OAF-Lambayeque/commit/02445eb630eb77b4a1c4bb2b466230356c8b4a66) | 18/10/2026 | 25/10/2026 |

*Condición necesaria, no suficiente: después de siete días de resguardo conservador y solo si el reanálisis diario completo ya está disponible. El modelo exige contenido archivado en un commit anterior al **día objetivo en hora Perú**, revisa las fechas y compara **byte por byte** cada archivo con el contenido guardado en aquel commit. Los timestamps del commit son evidencia de trazabilidad del repositorio, no firma externa de un organismo de certificación.

En 17/10/2026 las cuatro emisiones son anteriores a sus objetivos, pero la **primera fecha de contraste sigue en el futuro**: las métricas deben seguir `null`, no cero.

### B. Modelos propios de temperatura regional

Emisión experimental **8E** del 15/10/2026, basada en ERA5-Land local, Niño 1+2 y T300: **12 predicciones** = cuatro localidades × tres horizontes. De esas, **8** pertenecen a **noviembre y diciembre** (antes de comenzar el mes objetivo) y **4** son estimaciones hechas **en octubre durante octubre**, que deben clasificarse como intramensuales, nunca contarse como pronósticos totalmente anticipatorios. La primera verificación posible de octubre comienza el **10/11/2026** y la primera **premensual** de noviembre comienza el **10/12/2026**, siempre condicionadas a la publicación real de todos los datos ERA5-Land necesarios. El libro 8G conserva **cero** comparaciones admisibles en el corte.

### C. Modelo propio experimental SST Niño 1+2

Emisión **8A** del 15/10/2026 (origen septiembre): **dos** predicciones premes para noviembre y diciembre de 2026 y **una** estimación intramensual para octubre. Su anomalía SST Niño 1+2 recalculada por OAF **no constituye el ICEN oficial de ENFEN**. La fecha de publicación de ERSSTv5 posterior condicionará cada verificación. No se declara ninguna habilidad de predicción del Niño Costero.

## 2. Reglas para evaluar un pronóstico de anomalías

1. **Verificación de emisión:** registrar `issue_time_utc`, `issue_time_local`, fecha y ventana objetivo, modelo o proveedor, versión, horizonte, horizonte cronológico, unidad, coordenada o celda, suma o promedio y huella digital del archivo **antes de conocer el objetivo**.
2. **Datos disponibles en emisión:** documentar fecha máxima real de disponibilidad de cada predictor. Entrenar y transformar únicamente con esa información; nunca retroceder datos corregidos en 2026 como si hubieran sido publicados en 2011.
3. **Observación posterior:** fijar evidencia, cobertura, fecha de consulta, fuente y versión de ERA5/ERA5-Land, CHIRPS, índices oceánicos o estaciones y evitar comparar un promedio de píxel con un pluviómetro individual como si fueran equivalentes.
4. **Prevalidez:** diferenciar antes del objetivo de «ya iniciado», excluir versiones corregidas retrospectivamente y nunca cambiar un valor original emitido.
5. **Evaluación por horizonte y territorio:** MAE, RMSE, sesgo; para eventos probabilísticos utilizar Brier y calibración solo cuando probabilidades fueron archivadas *ex ante*, con muestra suficiente y clases de evento previamente definidas.
6. **Puntos de corte de El Niño Costero:** una anomalía Niño 1+2 no es la misma variable que ICEN. Es necesario reproducir definición, ventana, norma y confirmación de ENFEN antes de calcular aciertos de un evento oficial.
7. **Riesgo agrícola:** condiciones meteorológicas favorables no equivalen a presencia real de *Botrytis*, oídio o plagas. No derivar una alerta fitosanitaria de estos contrastes sin observación de campo, biología y validación.

## 3. Inventario de fuentes estacionales en emisiones históricas verificables

La [NOAA/CPC NMME](https://www.cpc.ncep.noaa.gov/products/NMME/data.html) mantiene pronósticos estacionales y hindcasts; el [archivo de emisiones NMME](https://ftp.cpc.ncep.noaa.gov/NMME/archive/) documenta emisiones en tiempo real desde **agosto de 2011**. El proyecto distingue `forecast` emitido originalmente de `hindcast` reconstruido. Sus imágenes públicas no son por sí mismas series numéricas puntuales de Lambayeque; para incorporarlas se necesitan archivos numéricos oficiales, metadatos de inicialización, sistema/modelo, latitud/longitud, unidades, tiempo válido y versiones, más una copia verificable de sus datos. **En 9J no se extrajeron valores numéricos NMME, ni se computó habilidad con ellos**.

De forma complementaria, el catálogo [Copernicus C3S de estadísticas mensuales estacionales](https://www.ecmwf.int/en/forecasts/datasets/seasonal-forecast-monthly-statistics-single-levels) incluye tanto pronósticos en tiempo real como reforecast/hindcasts. No son intercambiables. Se incluyó únicamente como **fuente candidata documentada**.

## 4. Datos entregados y verificación

- `modelos/auditoria_vintage_9j.py`: lee 6F, 8E, 8A, 6G y 8G; comprueba fecha, tipo, unidades, horizonte, cobertura, y contenido en commit con `git show` (sin llamadas HTTP).
- `datos/auditoria_vintage_9j/manifiesto_fuentes_9j.json`: cuatro commits originales con timestamps y catálogo NMME/C3S; se compara contra el histórico.
- `datos/auditoria_vintage_9j/estado_prospectivo_9j.json`: salida con número de emisiones, primeras fechas elegibles, ausencia de contrastes maduros, métricas `null`, advertencias y citas de procedencia del archivo.
- `tests/test_auditoria_vintage_9j.py`: pruebas que comprueban 112 pronósticos externos, 8 predicciones OAF mensuales realmente previas, cuatro nowcasts térmicos, dos predicciones oceánicas premes y cero verificación ficticia.
- `modelos/visor_auditoria_9j.js` y `assets/oaf-auditoria-9j.css`: nuevo panel en **Verificaciones**, con estados, tabla de fechas y enlaces a commits originales.
- `.github/workflows/oaf_auditoria_vintage_9j.yml`: auditoría con Git de historia completa, pruebas 9J y UX y publicación **solo del informe reproducible**.

Los métodos observacionales 9D–9I, la regionalización altitudinal 8K–8R y las referencias 1996–2025 (descriptiva) / 1991–2020 (OMM) se conservan; **no se declara completada una normal instrumental a partir de estas tres estaciones**.

## 5. Próxima fase 9K

Crear ingestión reproducible de un subconjunto **numérico** de pronósticos NMME realmente emitidos (no retrospectivos), con metadatos originales. Comparar tiempo de inicialización y fecha válida y evaluar en células representativas de Lambayeque con verificación observacional madura, estratificación territorial y *baseline* de climatología/persistencia construidos sin fuga temporal. Paralelamente, mantener evaluaciones 6G y 8G cuando maduren las emisiones contemporáneas. Ningún resultado de 9J da lugar a alertas oficiales.
